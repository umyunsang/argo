#!/usr/bin/env python3
"""Failing-first fixtures for reference-anchored scoring and selective evaluation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_anchor import (Element, SelectiveJudge, coverage,  # noqa: E402
                              minimum_calibration_size, wilson_upper)

R = []


def check(name, cond, detail=""):
    R.append({"check": name, "passed": bool(cond), "detail": detail})


def main() -> int:
    checklist = [Element("a", "names a paired design", [r"paired", r"within[- ]task"]),
                 Element("b", "states an equivalence plan", [r"equivalence", r"TOST"]),
                 Element("c", "states a power target", [r"power", r"minimum detectable"])]

    full = coverage("A paired design with an equivalence margin and a power target.", checklist)
    none = coverage("We will try some things and see.", checklist)
    part = coverage("A paired design, but nothing about the null.", checklist)
    check("coverage_full", full["coverage_ratio"] == 1.0, json.dumps(full))
    check("coverage_zero", none["coverage_ratio"] == 0.0, json.dumps(none))
    check("coverage_partial_lists_missed", part["missed"] == ["b", "c"], json.dumps(part))
    check("coverage_is_graded", none["coverage_ratio"] < part["coverage_ratio"] < full["coverage_ratio"])

    j = SelectiveJudge(risk_level=0.1)
    d = j.decide(0.99, "win")
    check("uncalibrated_judge_admits_nothing", not d["admitted"] and "uncalibrated" in d["reason"], json.dumps(d))

    empty = j.calibrate([])
    check("empty_calibration_refused", not empty["calibrated"], json.dumps(empty))

    small = [{"confidence": 0.9 + i * 0.001, "judge_verdict": "a", "anchor_verdict": "a"} for i in range(20)]
    noisy = [{"confidence": 0.3 + i * 0.001, "judge_verdict": "a", "anchor_verdict": "b"} for i in range(20)]
    rep_small = j.calibrate(small + noisy)
    check("undersized_calibration_refused_with_requirement",
          not rep_small["calibrated"] and rep_small["minimum_flawless_calibration_size"] == 25,
          json.dumps(rep_small))

    enough = [{"confidence": 0.9 + i * 0.001, "judge_verdict": "a", "anchor_verdict": "a"} for i in range(30)]
    rep = j.calibrate(enough + noisy)
    check("sufficient_calibration_certifies", rep["calibrated"] and rep["threshold"] >= 0.9, json.dumps(rep))
    check("high_confidence_admitted", j.decide(0.95, "a")["admitted"])
    low = j.decide(0.31, "a")
    check("low_confidence_abstains_and_escalates", not low["admitted"] and low.get("escalate") is True, json.dumps(low))

    check("bound_is_above_point_estimate", wilson_upper(0, 20, 0.05) > 0.0 and wilson_upper(0, 20, 0.05) > 0.1,
          str(round(wilson_upper(0, 20, 0.05), 4)))
    check("tighter_risk_needs_more_labels",
          minimum_calibration_size(0.05) > minimum_calibration_size(0.10) > minimum_calibration_size(0.20),
          f"{minimum_calibration_size(0.05)}/{minimum_calibration_size(0.10)}/{minimum_calibration_size(0.20)}")

    j2 = SelectiveJudge(risk_level=0.0)
    bad_only = j2.calibrate([{"confidence": 0.99, "judge_verdict": "a", "anchor_verdict": "b"}])
    check("impossible_risk_level_refused", not bad_only["calibrated"], json.dumps(bad_only))

    passed = sum(1 for r in R if r["passed"])
    print(json.dumps({"suite": "study_a_reference_anchor", "checks": len(R), "passed": passed, "results": R},
                     indent=2, sort_keys=True))
    return 0 if passed == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
