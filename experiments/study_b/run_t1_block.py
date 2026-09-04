#!/usr/bin/env python3
"""Idempotent block execution driver for T1' (ScienceAgentBench).

Executes (task, seed, arm) episodes with per-episode commit and ledger persistence.
Stops gracefully if remaining OAuth lifetime is under 30 minutes.
Follows instruction-0018 §4 / instruction-0019 §5 / instruction-0020 §8.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments/study_b"))
sys.path.insert(0, str(ROOT / "experiments/study_b/tasks"))

import episode_runner
import run_t1

BLOCK_DIR = ROOT / "experiments/study_b/block"
BLOCK_DIR.mkdir(parents=True, exist_ok=True)
SAB_DIR = Path.home() / ".cache/ScienceAgentBench"

TASKS = [5, 92]
ARMS = ["B0", "B1", "B2"]
TOTAL_PAIRS = 40  # 20 per task across 2 certified tasks

def check_auth_remaining_seconds() -> float:
    auth_file = Path.home() / ".prime/agent/auth.json"
    if not auth_file.is_file():
        return 0.0
    try:
        data = json.loads(auth_file.read_text())
        exp_ms = data.get("anthropic", {}).get("expires", 0)
        return max(0.0, (exp_ms - time.time() * 1000) / 1000)
    except Exception:
        return 0.0

def run_block():
    print(f"Starting T1' block execution across tasks {TASKS}...")
    completed_count = 0
    
    # 40 triples total: seed 0..19 for Task 5, seed 0..19 for Task 92
    for task_idx, tid in enumerate(TASKS):
        for s in range(20):
            seed_id = s
            # Check auth safety margin (need at least 15 min for a triple)
            rem_s = check_auth_remaining_seconds()
            if rem_s < 900:
                print(f"Auth expiration imminent ({rem_s:.0f}s remaining). Halting before new triple.")
                return completed_count
                
            print(f"\n=== Processing Triple: Task {tid}, Seed {seed_id} ===")
            triple_receipts = {}
            
            for arm in ARMS:
                rec_file = BLOCK_DIR / f"block_t1_task{tid}_s{seed_id}_{arm}.json"
                if rec_file.is_file():
                    print(f"  Arm {arm} already completed: {rec_file.name}")
                    triple_receipts[arm] = json.loads(rec_file.read_text())
                    continue
                    
                wdir = Path(f"/tmp/study_b_block_t1_{arm}_task{tid}_s{seed_id}")
                if wdir.exists():
                    import shutil
                    shutil.rmtree(wdir)
                wdir.mkdir(parents=True, exist_ok=True)
                
                print(f"  Running Arm {arm}...")
                task_meta = run_t1.setup_workspace(tid, SAB_DIR, wdir)
                
                # Execute episode
                # Extract prompts
                sys_prompt_file = ROOT / f"experiments/study_b/harness/prompts/{arm.lower()}_system_prompt.txt"
                sys_prompt = sys_prompt_file.read_text(encoding="utf-8").strip()
                user_msg = (wdir / "TASK.md").read_text(encoding="utf-8")
                
                clean_agent = episode_runner.ensure_clean_agent_dir()
                sess_dir = wdir / "_sess"
                sess_dir.mkdir(parents=True, exist_ok=True)
                
                cmd = [
                    "prime-agent", "-p", "--no-session", "--mode", "json",
                    "--cwd", str(wdir),
                    "--session-dir", str(sess_dir),
                    "-nc", "-ns", "-np",
                    "--model", "anthropic/claude-haiku-4-5",
                    "--thinking", "low",
                    "--system-prompt", sys_prompt,
                ]
                
                ext_dir = ROOT / "experiments/study_b/harness/extensions"
                if arm == "B0":
                    cmd += ["--no-builtin-tools", "-e", str(ext_dir / "b0_tools.js")]
                elif arm == "B1":
                    cmd += ["-e", str(ext_dir / "b0_tools.js")]
                elif arm == "B2":
                    cmd += ["-e", str(ext_dir / "b2_harness.js")]
                    
                cmd.append(user_msg)
                env = dict(os.environ)
                env["PRIME_AGENT_CODING_AGENT_DIR"] = str(clean_agent)
                
                t0 = time.time()
                try:
                    proc = subprocess.run(cmd, cwd=wdir, capture_output=True, text=True, timeout=1800, env=env)
                    transcript = proc.stdout + "\n" + proc.stderr
                except subprocess.TimeoutExpired as exc:
                    transcript = (exc.stdout or "") + "\n" + (exc.stderr or "") + "\nTIMEOUT"
                    
                duration_s = round(time.time() - t0, 1)
                (wdir / "transcript.txt").write_text(transcript, encoding="utf-8", errors="replace")
                
                usage = episode_runner.parse_usage(transcript)
                manipulation = episode_runner.parse_manipulation_log(wdir, arm)
                gold_leak = len(list(wdir.rglob("*gold*"))) > 0
                
                expected_out = wdir / task_meta["output_fname"]
                answered = expected_out.is_file()
                ordinal_score, eval_detail = run_t1.verify_output(tid, SAB_DIR, wdir)
                
                rec = {
                    "evidence_level": "CONFIRMATION_EPISODE",
                    "arm": arm,
                    "task": "T1'",
                    "instance_id": tid,
                    "seed": seed_id,
                    "benchmark": "ScienceAgentBench",
                    "benchmark_commit": "c26e151ed601ba109dc4d35e057ff8e73fec469d",
                    "cost_usd": usage["cost_usd"],
                    "total_tokens": usage["total_tokens"],
                    "duration_s": duration_s,
                    "answered": answered,
                    "ordinal_score": ordinal_score,
                    "score_pass": bool(ordinal_score == 2),
                    "eval_detail": eval_detail,
                    "manipulation_check_passed": manipulation["manipulation_check_passed"],
                    "manipulation_check_detail": manipulation["manipulation_check_detail"],
                    "gold_leak": gold_leak,
                    "tool_call_counts": manipulation["tool_call_counts"],
                    "decisions_recorded": manipulation.get("decisions_recorded", 0),
                    "thresholds_registered": manipulation.get("thresholds_registered", 0),
                    "pivots": manipulation.get("pivots", 0),
                    "graph_nodes_added": manipulation.get("graph_nodes_added", 0),
                    "gate_blocks": manipulation.get("gate_blocks", 0),
                    "workspace": str(wdir),
                    "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                
                rec_file.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
                triple_receipts[arm] = rec
                print(f"    Done: cost=${usage['cost_usd']:.4f}, score={ordinal_score}, manipulation={manipulation['manipulation_check_passed']}")
                
            completed_count += 1
            print(f"Triple {completed_count}/40 completed.")
            
    return completed_count

if __name__ == "__main__":
    run_block()
