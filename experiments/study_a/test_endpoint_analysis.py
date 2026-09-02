#!/usr/bin/env python3
"""Failing-first fixtures for the endpoint analysis.

Three kinds of check. Analytic cases whose components can be worked out by hand, guard
cases that must raise rather than report a clean zero, and one regression case that
reproduces the numbers already published in the verified-endpoint receipt from the
original verdict record. The last is an oracle produced before this code existed.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from endpoint_analysis import (  # noqa: E402
    allocation, analyse, coverage_by_episode, pearson, variance_components,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECORDED = ROOT / "paper/experiments/verified-endpoint-receipt.json"
ORIGINAL_VERDICTS = ROOT / "paper/experiments/study-a-variance-block-2026-09-02/element-verdicts.json"

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def rec(ep, element, verdict):
    return {"episode_id": ep, "element": element, "verdict": verdict}


def main() -> int:
    cov = coverage_by_episode([
        rec("T1__C00__r1", "a", "satisfied"),
        rec("T1__C00__r1", "b", "not_satisfied"),
        rec("T1__C00__r1", "c", "unclear"),
        rec("T1__C00__r1", "d", "unparsed"),
    ])
    check("coverage counts only satisfied", abs(cov["T1__C00__r1"] - 0.25) < 1e-12, str(cov))
    check("unclear does not count as met", cov["T1__C00__r1"] != 0.5)

    # Two tasks, two conditions, two repeats, all variation carried by task.
    rows = []
    for task, base in (("A", "satisfied"), ("B", "not_satisfied")):
        for cond in ("C00", "C11"):
            for r in (1, 2):
                rows.append(rec(f"{task}__{cond}__r{r}", "e", base))
    vc = variance_components(coverage_by_episode(rows))
    check("pure task variation gives a task share of one hundred percent",
          vc["shares_percent"]["task"] == 100.0, json.dumps(vc["shares_percent"]))
    check("pure task variation leaves no residual",
          vc["shares_percent"]["residual_repeat"] == 0.0)
    check("design is reported back", vc["design"] == {"tasks": 2, "conditions": 2, "repeats": 2})

    rows_c = []
    for task in ("A", "B"):
        for cond, v in (("C00", "satisfied"), ("C11", "not_satisfied")):
            for r in (1, 2):
                rows_c.append(rec(f"{task}__{cond}__r{r}", "e", v))
    vc_c = variance_components(coverage_by_episode(rows_c))
    check("pure condition variation gives a condition share of one hundred percent",
          vc_c["shares_percent"]["condition"] == 100.0, json.dumps(vc_c["shares_percent"]))

    alloc = allocation({"task": 0.0, "condition": 0.0, "task_x_condition": 0.0,
                        "residual_repeat": 0.02})
    one = alloc[0]
    expected_se = math.sqrt(0.02 / 48)
    check("standard error of a mean follows the components",
          abs(one["se_condition_mean"] - round(expected_se, 4)) < 1e-9, str(one))
    check("paired difference carries the square root of two",
          abs(one["se_paired_difference"] - round(math.sqrt(2) * expected_se, 4)) < 1e-4, str(one))
    check("the minimum detectable effect uses the difference, not the mean",
          abs(one["paired_mde_approx"] - round(2.8 * math.sqrt(2) * expected_se, 4)) < 1e-4,
          str(one))
    check("more repeats with fewer tasks does not change the standard error here",
          len({a["se_condition_mean"] for a in alloc}) == 1, str(alloc))

    check("perfect correlation is one", abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9)
    check("a constant vector correlates to zero rather than raising",
          pearson([1, 1, 1], [1, 2, 3]) == 0.0)

    # The message is asserted, not only that something raised: a wrong guard can still
    # raise for the wrong reason and would otherwise pass.
    for name, expect, rows_bad in (
        ("unbalanced design raises for imbalance", "unbalanced",
         [rec("A__C00__r1", "e", "satisfied"), rec("A__C00__r2", "e", "satisfied"),
          rec("A__C11__r1", "e", "satisfied")]),
        ("one observation per cell raises for the residual", "residual",
         [rec("A__C00__r1", "e", "satisfied"), rec("A__C11__r1", "e", "satisfied"),
          rec("B__C00__r1", "e", "satisfied"), rec("B__C11__r1", "e", "satisfied")]),
        ("unmatched identifiers raise for the identifiers", "no episode identifiers",
         [rec("junk", "e", "satisfied")]),
    ):
        message = ""
        try:
            variance_components(coverage_by_episode(rows_bad))
        except ValueError as exc:
            message = str(exc)
        check(name, expect in message, message or "nothing raised")

    if RECORDED.is_file() and ORIGINAL_VERDICTS.is_file():
        recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
        got = analyse(ORIGINAL_VERDICTS)
        check("reproduces the recorded variance shares",
              got["variance"]["shares_percent"] == recorded["verified_variance_shares_percent"],
              json.dumps(got["variance"]["shares_percent"]))
        rec_alloc = recorded["allocation_on_verified_endpoint"]
        check("reproduces the recorded standard error",
              all(abs(a["se_condition_mean"] - b["se_condition_mean"]) < 1e-9
                  for a, b in zip(got["allocation"], rec_alloc)))
        check("reproduces the recorded minimum detectable effect",
              all(abs(a["paired_mde_approx"] - b["paired_mde_approx"]) < 1e-9
                  for a, b in zip(got["allocation"], rec_alloc)),
              str([a["paired_mde_approx"] for a in got["allocation"]]))
        check("reproduces the recorded judgement count",
              got["element_judgements"] == recorded["element_judgements"])
    else:
        check("recorded receipt and original record are present for the regression check", False)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
