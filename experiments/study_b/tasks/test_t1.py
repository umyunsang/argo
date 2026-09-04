#!/usr/bin/env python3
"""Tests for the T1' ScienceAgentBench adapter."""
import sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_t1

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    check("licence is recorded and permissive", run_t1.licence_ok()[0] is True)
    check("licence note names the licence", "MIT" in run_t1.licence_ok()[1])

    s = run_t1.check_preconditions(None)
    check("absent checkout is not ready", s["ready"] is False)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        part = root / "partial"; (part / "benchmark/eval_programs").mkdir(parents=True)
        s = run_t1.check_preconditions(part)
        check("an incomplete checkout is not ready", s["ready"] is False)

        full = root / "full"
        (full / "benchmark/eval_programs/gold_results").mkdir(parents=True)
        (full / "benchmark/datasets").mkdir(parents=True)
        s = run_t1.check_preconditions(full)
        check("a complete checkout is ready", s["ready"] is True)

        # Test workspace setup
        sab_dir = Path.home() / ".cache" / "ScienceAgentBench"
        if sab_dir.exists():
            ws_dir = root / "workspace_task1"
            meta = run_t1.setup_workspace(1, sab_dir, ws_dir)
            check("workspace created", ws_dir.exists())
            check("TASK.md created without gold answers", (ws_dir / "TASK.md").exists())
            check("dataset copied", (ws_dir / "benchmark/datasets/clintox/clintox_train.csv").exists())
            check("oracle isolation (no gold files in workspace)", not (ws_dir / "benchmark/eval_programs").exists())

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
