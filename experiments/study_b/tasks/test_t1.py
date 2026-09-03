#!/usr/bin/env python3
"""Failing-first tests for the T1 ResearchClawBench adapter."""
import sys, tempfile
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
    check("the adapter does not acquire data by itself",
          s["acquisition"] == "not attempted by this module")
    check("it tells the caller the acquisition command", "git clone" in s["next_step"])

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        part = root / "partial"; (part / "tasks").mkdir(parents=True)
        s = run_t1.check_preconditions(part)
        check("an incomplete checkout is not ready", s["ready"] is False)
        check("missing directories are named", "evaluation" in s.get("missing", []), str(s))

        full = root / "full"
        for d in run_t1.REQUIRED_DIRS: (full / d).mkdir(parents=True)
        for i in range(6): (full / "tasks" / f"task_{i}").mkdir()
        s = run_t1.check_preconditions(full)
        check("a complete, licensed checkout is ready", s["ready"] is True)
        check("the discovered task count is reported", s["discovered_task_count"] == 6, str(s))

        # a non-permissive licence must block even a complete checkout
        saved = run_t1.BENCH["licence"]
        run_t1.BENCH["licence"] = "CC BY-NC-ND-4.0"
        s = run_t1.check_preconditions(full)
        check("a non-permissive licence blocks a complete checkout", s["ready"] is False)
        check("the block names the licence problem", "not in the permissive set" in s.get("reason", ""), str(s))
        run_t1.BENCH["licence"] = saved

    tasks = [f"t{i}" for i in range(20)]
    a1 = run_t1.select_subset(tasks, 5, 7)
    check("subset selection is deterministic", a1 == run_t1.select_subset(tasks, 5, 7))
    check("a different seed selects a different subset", a1 != run_t1.select_subset(tasks, 5, 8))
    check("subset does not depend on input order",
          a1 == run_t1.select_subset(list(reversed(tasks)), 5, 7))
    try:
        run_t1.select_subset(tasks, 50, 7)
        check("asking for more tasks than exist is rejected", False, "no error")
    except run_t1.PreconditionUnmet as e:
        check("asking for more tasks than exist is rejected with the counts",
              "50" in str(e) and "20" in str(e), str(e))

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
