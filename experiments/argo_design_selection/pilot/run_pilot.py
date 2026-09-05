#!/usr/bin/env python3
"""Stage B pilot runner: budgeted-verification episodes on a pinned frontier model."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from build_task import build
from score import load_and_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL = "anthropic/claude-opus-4-6"
TIMEOUT_S = 600
SYSTEM_PROMPT = ("You are completing one inherited research-state decision. Follow the task file exactly, "
                 "respect the stated verification budget, and write the requested JSON file.")
CLEAN_AGENT_DIR = Path("/tmp/argo_pilot_agent_dir")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clean_agent_dir() -> Path:
    CLEAN_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    src = Path(os.path.expanduser("~/.prime/agent/auth.json"))
    if src.is_file():
        shutil.copy2(src, CLEAN_AGENT_DIR / "auth.json")
    return CLEAN_AGENT_DIR


def parse_usage(text: str) -> dict:
    tokens, cost, calls = 0, 0.0, 0
    for line in text.splitlines():
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
                tokens += int(u.get("totalTokens", 0))
                cost += float((u.get("cost") or {}).get("total", 0.0) or 0.0)
                calls += 1
    return {"total_tokens": tokens, "reported_cost_usd": round(cost, 6), "assistant_messages": calls}


def observed_reads(text: str) -> list:
    return sorted(set(m.group(1).upper() for m in re.finditer(r"records/([A-Za-z0-9_]+)\.txt", text)))


def run_one(seed: int, condition: str, rollout: int, outdir: Path) -> dict:
    wd = outdir / f"{seed:02d}_{condition}_r{rollout}"
    if wd.exists():
        shutil.rmtree(wd)
    meta = build(seed, condition, wd)
    task_text = (wd / "TASK.md").read_text(encoding="utf-8")
    sess = wd / "_sess"
    sess.mkdir(parents=True, exist_ok=True)
    cmd = ["prime-agent", "-p", "--no-session", "--mode", "json", "--cwd", str(wd),
           "--session-dir", str(sess), "-nc", "-ns", "-np", "--model", MODEL,
           "--thinking", "low", "--system-prompt", SYSTEM_PROMPT, task_text]
    env = dict(os.environ)
    env["PRIME_AGENT_CODING_AGENT_DIR"] = str(clean_agent_dir())
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=wd, capture_output=True, text=True,
                              timeout=TIMEOUT_S, check=False, env=env)
        transcript = proc.stdout + "\n" + proc.stderr
        exit_code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        transcript = (exc.stdout or "") + "\n" + (exc.stderr or "")
        exit_code, timed_out = None, True
    (wd / "transcript.jsonl").write_text(transcript, encoding="utf-8")
    usage = parse_usage(transcript)
    reads = observed_reads(transcript)
    verification_records = sorted(set(reads + meta.get("prefetched_records", [])))
    scored = load_and_score(wd, meta, observed_reads=verification_records)
    return {
        "episode_id": f"{meta['task_id']}|{condition}|r{rollout}",
        "task_id": meta["task_id"], "seed": seed, "condition": condition, "rollout": rollout,
        "model": MODEL, "exit_code": exit_code, "timed_out": timed_out,
        "duration_seconds": round(time.time() - t0, 3),
        "usage": usage, "observed_reads": reads,
        "prefetched_records": meta.get("prefetched_records", []),
        "verification_records": verification_records,
        "task_md_sha256": meta["task_md_sha256"], "records_sha256": meta["records_sha256"],
        "computed_target": meta["computed_target"], "score": scored,
        "workdir": str(wd), "transcript_sha256": sha(wd / "transcript.jsonl"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3])
    ap.add_argument("--rollouts", type=int, default=3)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    a.outdir.mkdir(parents=True, exist_ok=True)
    plan = [(s, c, r) for s in a.seeds for r in range(1, a.rollouts + 1) for c in ("C_BASE", "C_TARGET")]
    if a.limit:
        plan = plan[:a.limit]
    rows = []
    for i, (s, c, r) in enumerate(plan, 1):
        row = run_one(s, c, r, a.outdir)
        rows.append(row)
        print(json.dumps({"i": i, "of": len(plan), "episode": row["episode_id"],
                          "parsed": row["score"]["parsed"], "correct": row["score"].get("correct"),
                          "stale": row["score"].get("stale_consistent"),
                          "tokens": row["usage"]["total_tokens"]}), flush=True)
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        a.receipt.write_text(json.dumps({
            "schema_version": "argo-stage-b-pilot/v1",
            "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "model": MODEL, "approval": "paper/research/receipts/stage-b-pilot-approval.json",
            "planned_episodes": len(plan), "completed_episodes": len(rows),
            "code": {n: sha(HERE / n) for n in ("build_task.py", "score.py", "run_pilot.py")},
            "harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "episodes": rows,
            "scope": "development pilot; effect direction and variance only; not confirmatory",
        }, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
