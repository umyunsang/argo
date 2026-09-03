#!/usr/bin/env python3
"""Failing-first tests for the T2 budget-completion adapter."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_t2

F = []
def check(n, ok, d=""):
    print(("PASS " if ok else "FAIL ") + n + (f" :: {d}" if not ok else ""))
    if not ok: F.append(n)

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        s = run_t2.check_preconditions(root / "absent")
        check("absent bundle directory is reported as not ready", s["ready"] is False)
        check("the reason names the absent directory", "absent" in s["reason"], s["reason"])

        part = root / "partial"; part.mkdir()
        (part / "T1-context-artifact").mkdir()
        s = run_t2.check_preconditions(part)
        check("a partial bundle set is not ready", s["ready"] is False)
        check("the missing tasks are listed by name",
              "T4-retrieval-scale" in s.get("missing", []), str(s))

        full = root / "full"; full.mkdir()
        for t in run_t2.BUNDLE_DIGESTS: (full / t).mkdir()
        check("a complete bundle set is ready", run_t2.check_preconditions(full)["ready"] is True)

    # budget completion is a competing event, never a dropped episode
    r = run_t2.score_completion({"cost_usd": 0.9, "answer_path": None, "exit_code": 1}, 0.5)
    check("an episode over ceiling with no answer is a competing event",
          r["outcome"] == "budget_exhausted" and r["competing_event"] is True and r["completed"] is False)
    r = run_t2.score_completion({"cost_usd": 0.2, "answer_path": "a.json", "exit_code": 0}, 0.5)
    check("an answered episode inside budget is completed",
          r["outcome"] == "completed" and r["completed"] is True)
    r = run_t2.score_completion({"cost_usd": 0.2, "answer_path": None, "exit_code": 2}, 0.5)
    check("a failure inside budget is distinguished from budget exhaustion",
          r["outcome"] == "failed_within_budget" and r["competing_event"] is False)
    r = run_t2.score_completion({"cost_usd": 0.9, "answer_path": "a.json", "exit_code": 0}, 0.5)
    check("an answered episode that also hit the ceiling still counts as completed",
          r["completed"] is True)

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
