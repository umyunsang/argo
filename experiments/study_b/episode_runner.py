#!/usr/bin/env python3
"""Episode runner: one arm x one task x one seed = one model episode.

Invocation is the fixed, sealed form. Costs are parsed from the transcript and summed
into the receipt's provider usage log; the receipt only carries numbers that parser
actually saw. Nothing here is an estimate.

origin: model_call
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments/study_b/tasks"))
from study_b.harness.arms import ARMS  # noqa: E402
import oracle_t3, run_t3  # noqa: E402

MODEL = "anthropic/claude-haiku-4-5"
TIMEOUT_S = 1800

ARM_PROMPTS = {
    "B0": ("You are an agent with only four primitive tools: read a file, write a file, "
           "replace text in a file, and run a shell command. Work step by step from a fresh "
           "shell each time; keep your notes in a single plain text file."),
    "B1": ("You are an agent with a persistent Python interpreter. Keep intermediate objects "
           "in memory across steps. You may spawn recursive sub-questions as new short scripts."),
    "B2": ("You are an agent with a persistent Python interpreter. Treat your working state as a "
           "typed research graph: create gap, hypothesis, decision and experiment records before "
           "acting. Every decision record has six fields: question, alternatives, rationale, "
           "decision, expected effect and risk, falsifier. Register your success threshold before "
           "you run anything. After every run, compare the observed numbers against that "
           "threshold; if it is not met, change the approach once, within budget. Report only "
           "numbers that appear in your computation output."),
}

USAGE_PATTERNS = [
    re.compile(r'"?total_tokens"?\s*[:=]\s*(\d+)', re.I),
    re.compile(r'total\s*tokens?\s*[:\-]?\s*(\d[\d,]*)', re.I),
    re.compile(r'(\d[\d,]{4,})\s*tokens?', re.I),
]
COST_PATTERN = re.compile(r'\$\s*(\d+\.\d+)')


def parse_usage(transcript_text: str) -> dict:
    def _num(g):
        return int(g.replace(",", ""))

    json_tokens = 0
    json_cost = 0.0
    found_event = False
    for line in transcript_text.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") == "message_end":
            msg = ev.get("message") or {}
            if msg.get("role") == "assistant" and "usage" in msg:
                u = msg["usage"]
                json_tokens += int(u.get("totalTokens", 0))
                c = (u.get("cost") or {}).get("total", 0.0)
                json_cost += float(c)
                found_event = True

    if found_event:
        return {"total_tokens": json_tokens, "cost_usd": round(json_cost, 6)}

    total = sum(_num(m.group(1)) for m in USAGE_PATTERNS[0].finditer(transcript_text))
    if total == 0:
        for pat in USAGE_PATTERNS[1:]:
            vals = [_num(g) for g in pat.findall(transcript_text)]
            vals = [v for v in vals if 1000 <= v <= 5_000_000]
            if vals:
                total = max(vals)
                break
    costs = [float(x) for x in COST_PATTERN.findall(transcript_text) if 0.0005 < float(x) < 100]
    return {"total_tokens": total, "cost_usd": round(sum(costs), 6)}


def run_episode(arm: str, task: str, seed: int, workdir: Path, oracle_dir: Path,
                dry_run: bool) -> dict:
    cfg = ARMS[arm]
    t0 = time.time()
    workdir.mkdir(parents=True, exist_ok=True)
    truth = run_t3.build_workspace(seed, workdir, oracle_dir)

    prompt = ARM_PROMPTS[arm] + "\n\n" + (workdir / "TASK.md").read_text(encoding="utf-8")
    prompt += ("\n\nWhen done, write answers.json in the same directory with the keys named "
               "in the task. This run is a PIPELINE DRY RUN; one attempt only." if dry_run else "")
    cmd = ["prime-agent", "-p", "--no-session", "--mode", "json", "--cwd", str(workdir),
           "--model", MODEL, "--thinking", "low", prompt]
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                              timeout=TIMEOUT_S, check=False)
        transcript = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired as exc:
        transcript = (exc.stdout or "") + "\n" + (exc.stderr or "") + "\nTIMEOUT"

    tpath = workdir / "transcript.txt"
    tpath.write_text(transcript, encoding="utf-8", errors="replace")
    usage = parse_usage(transcript)
    answers_path = workdir / "answers.json"
    answered = answers_path.is_file()
    score = None
    if answered:
        try:
            score = run_t3.score(json.loads(answers_path.read_text(encoding="utf-8")), truth)
        except Exception as exc:
            score = {"error": str(exc), "pass": False}
    return {
        "arm": arm, "task": task, "seed": seed,
        "exit_ok": proc.returncode == 0 if 'proc' in dir() else False,
        "duration_s": round(time.time() - t0, 1),
        "answered": answered, "score": score,
        "transcript_path": str(tpath), **usage,
        "origin": "model_call",
        "evidence_level": "PIPELINE_DRY_RUN" if dry_run else "REPRODUCED_EXPERIMENT",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["B0", "B1", "B2"])
    ap.add_argument("--task", default="T3")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--oracle-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.task != "T3":
        print(json.dumps({"status": "REFUSED", "reason": "episode runner implements T3 only"}))
        sys.exit(2)
    ep = run_episode(a.arm, a.task, a.seed, Path(a.workdir), Path(a.oracle_dir), a.dry_run)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(ep, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: ep[k] for k in ("arm", "answered", "total_tokens", "cost_usd",
                                         "evidence_level")}, indent=2))
