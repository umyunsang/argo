#!/usr/bin/env python3
"""Failing-first fixtures for plan status.

The property that matters is that a blocked outcome is never reported as planable, and
that an inadmissible episode never informs a plan.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from plan_status import completion_outcome, quality_outcome  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def balanced_coverage():
    cov = {}
    for task in ("A", "B"):
        for cond in ("C00", "C01", "C10", "C11"):
            for rep in (1, 2):
                cov[f"{task}__{cond}__r{rep}"] = 0.6 if cond == "C00" else 0.8
    return cov


def main() -> int:
    cov = balanced_coverage()
    check("a complete design with labels is planable",
          quality_outcome(cov, 25, 25)["planable"] is True)

    r = quality_outcome(cov, 0, 25)
    check("missing labels block the plan", r["planable"] is False)
    check("the blocker names the external input",
          r["blocked_by"][0]["kind"] == "external input", str(r))
    check("the blocker states how many labels are missing",
          "0 of 25" in r["blocked_by"][0]["detail"])

    partial = {k: v for i, (k, v) in enumerate(cov.items()) if i != 0}
    r2 = quality_outcome(partial, 25, 25)
    check("an unbalanced design blocks the plan", r2["planable"] is False)
    check("the design blocker is labelled as design",
          r2["blocked_by"][0]["kind"] == "design", str(r2))

    r3 = quality_outcome(partial, 0, 25)
    check("both blockers are reported, not just the first", len(r3["blocked_by"]) == 2, str(r3))

    check("a receipt with no cost blocks completion planning",
          completion_outcome({"per_episode": []})["planable"] is False)
    check("the completion blocker is stated",
          "cost" in completion_outcome({"per_episode": []})["blocked_by"])

    good = {"per_episode": [{"cost_usd": 0.2} for _ in range(8)],
            "budget_completion": {"per_condition": {"C00": {"rate": 1.0}, "C11": {"rate": 0.75}}}}
    c = completion_outcome(good)
    check("completion is planable without a judge", c["planable"] is True, str(c))
    check("completion reports a block size", c["episodes"] > 0)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
