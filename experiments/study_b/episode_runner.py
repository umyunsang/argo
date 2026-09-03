#!/usr/bin/env python3
"""Episode runner: one arm x one task x one seed = one model episode.

Invocation strictly separates harness configuration (system prompt + extensions + tool allowlists)
from task content (user turn).
Costs are parsed from the stream and summed; manipulation logs are verified per arm.

Counting basis: the extension's tool_call interceptor writes exactly one record per tool
invocation, so a receipt's tool_call_counts equals distinct toolCallIds. Raw transcript
tool_execution_* events over-count because each call streams many update records; dedupe
them by toolCallId to reproduce the receipt numbers exactly.

origin: model_call
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments/study_b/tasks"))
from study_b.harness.arms import ARMS  # noqa: E402
import oracle_t3, run_t3  # noqa: E402

MODEL = "anthropic/claude-haiku-4-5"
TIMEOUT_S = 1800

EXT_DIR = ROOT / "experiments/study_b/harness/extensions"
PROMPTS_DIR = ROOT / "experiments/study_b/harness/prompts"
CLEAN_AGENT_DIR = Path("/tmp/clean_agent_dir")


def ensure_clean_agent_dir() -> Path:
    CLEAN_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    auth_src = Path(os.path.expanduser("~/.prime/agent/auth.json"))
    if auth_src.is_file():
        shutil.copy2(auth_src, CLEAN_AGENT_DIR / "auth.json")
    return CLEAN_AGENT_DIR


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

    USAGE_PATTERNS = [
        re.compile(r'"?total_tokens"?\s*[:=]\s*(\d+)', re.I),
        re.compile(r'total\s*tokens?\s*[:\-]?\s*(\d[\d,]*)', re.I),
        re.compile(r' (\d[\d,]{4,})\s*tokens? ', re.I),
    ]
    COST_PATTERN = re.compile(r'\$\s*(\d+\.\d+)')

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


def parse_manipulation_log(workdir: Path, arm: str) -> dict:
    log_file = workdir / "manipulation_log.json"
    events = []
    if log_file.is_file():
        try:
            events = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    tool_counts = {}
    gate_blocks = 0
    decisions = 0
    thresholds = 0
    pivots = 0
    graph_nodes = 0

    for ev in events:
        t = ev.get("tool")
        if t:
            tool_counts[t] = tool_counts.get(t, 0) + 1
        e_type = ev.get("event")
        if e_type == "gate_blocked":
            gate_blocks += 1
        elif e_type == "decision_recorded":
            decisions += 1
        elif e_type == "threshold_registered":
            thresholds += 1
        elif e_type == "threshold_evaluated" and not ev.get("passed"):
            pivots += 1
        elif e_type == "graph_add":
            graph_nodes += 1

    # Check arm-specific manipulation rules
    passed = True
    reason = "manipulation_rules_satisfied"
    if arm == "B0":
        if tool_counts.get("ipython", 0) > 0:
            passed = False
            reason = f"B0 violation: ipython was called {tool_counts['ipython']} times"
    elif arm == "B2":
        if decisions < 1 or thresholds < 1:
            passed = False
            reason = f"B2 violation: required decision_record (got {decisions}) and threshold_register (got {thresholds})"

    return {
        "manipulation_check_passed": passed,
        "manipulation_check_detail": reason,
        "tool_call_counts": tool_counts,
        "gate_blocks": gate_blocks,
        "decisions_recorded": decisions,
        "thresholds_registered": thresholds,
        "pivots": pivots,
        "graph_nodes_added": graph_nodes,
    }


def run_episode(arm: str, task: str, seed: int, workdir: Path, oracle_dir: Path,
                dry_run: bool) -> dict:
    t0 = time.time()
    workdir.mkdir(parents=True, exist_ok=True)
    truth = run_t3.build_workspace(seed, workdir, oracle_dir)

    # 1.1 Prompt separation
    task_file = workdir / "TASK.md"
    task_text = task_file.read_text(encoding="utf-8")
    task_sha256 = hashlib.sha256(task_text.encode("utf-8")).hexdigest()

    sys_prompt_file = PROMPTS_DIR / f"{arm.lower()}_system_prompt.txt"
    sys_prompt = sys_prompt_file.read_text(encoding="utf-8").strip()

    # User turn message: task instructions + dry-run note
    user_message = task_text
    if dry_run:
        user_message += "\n\n[Note: This is a PIPELINE DRY RUN; exactly one attempt to write answers.json.]"

    # Tooling and extension configuration per arm
    clean_agent = ensure_clean_agent_dir()
    sess_dir = workdir / "_sess"
    sess_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "prime-agent", "-p", "--no-session", "--mode", "json",
        "--cwd", str(workdir),
        "--session-dir", str(sess_dir),
        "-nc", "-ns", "-np",
        "--model", MODEL,
        "--thinking", "low",
        "--system-prompt", sys_prompt,
    ]

    if arm == "B0":
        # 1.2 B0: no builtin tools (no ipython), load b0_tools.js
        cmd += ["--no-builtin-tools", "-e", str(EXT_DIR / "b0_tools.js")]
    elif arm == "B1":
        # 1.3 B1: keeps built-in ipython, load b0_tools.js for file tools
        cmd += ["-e", str(EXT_DIR / "b0_tools.js")]
    elif arm == "B2":
        # 1.4 B2: keeps built-in ipython + G/P/R/L extension with gate
        cmd += ["-e", str(EXT_DIR / "b2_harness.js")]

    cmd.append(user_message)

    env = dict(os.environ)
    env["PRIME_AGENT_CODING_AGENT_DIR"] = str(clean_agent)

    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                              timeout=TIMEOUT_S, check=False, env=env)
        transcript = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired as exc:
        transcript = (exc.stdout or "") + "\n" + (exc.stderr or "") + "\nTIMEOUT"

    tpath = workdir / "transcript.txt"
    tpath.write_text(transcript, encoding="utf-8", errors="replace")
    usage = parse_usage(transcript)
    manipulation = parse_manipulation_log(workdir, arm)

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
        "task_sha256": task_sha256,
        "system_prompt_path": str(sys_prompt_file.relative_to(ROOT)),
        "exit_ok": proc.returncode == 0 if 'proc' in dir() else False,
        "duration_s": round(time.time() - t0, 1),
        "answered": answered, "score": score,
        "transcript_path": str(tpath), **usage,
        "manipulation_check": manipulation,
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
    print(json.dumps({
        "arm": ep["arm"],
        "answered": ep["answered"],
        "score": ep["score"],
        "manipulation": ep["manipulation_check"]["manipulation_check_passed"],
        "manipulation_detail": ep["manipulation_check"]["manipulation_check_detail"],
        "total_tokens": ep["total_tokens"],
        "cost_usd": ep["cost_usd"],
        "evidence_level": ep["evidence_level"]
    }, indent=2))
