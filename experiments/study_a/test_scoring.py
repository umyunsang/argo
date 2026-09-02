#!/usr/bin/env python3
"""Failing-first fixtures for Study A scoring and judge calibration.

Each diagnostic must fire on a deliberately defective judge and stay silent on a
well-behaved one. Run: /usr/bin/python3 experiments/study_a/test_scoring.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring import DIMENSIONS, Episode, calibration_report, run_redlines, score_episode, Scored, state_use_report  # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append({"check": name, "passed": bool(cond), "detail": detail})


def human_anchor(seed=7, n=24):
    rng = random.Random(seed)
    return {f"t{i}": {d: rng.choice([1, 2, 3, 4, 5]) for d in DIMENSIONS} for i in range(n)}


def main() -> int:
    human = human_anchor()

    faithful = {i: {d: max(0, min(5, v + random.Random(stable_seed(i, d)).choice([-1, 0, 1])))
                    for d, v in dims.items()} for i, dims in human.items()}
    rep = calibration_report(faithful, human)
    check("faithful_judge_admissible", rep["admissible"], json.dumps(rep))

    harsh = {i: {d: max(0, v - 2) for d, v in dims.items()} for i, dims in human.items()}
    rep_h = calibration_report(harsh, human)
    check("severity_probe_fires", not rep_h["admissible"] and any("severity" in f for f in rep_h["failures"]),
          json.dumps(rep_h))

    halo = {i: {d: statistics_mean(dims) for d in DIMENSIONS} for i, dims in human.items()}
    rep_x = calibration_report(halo, human)
    check("halo_probe_fires", any("halo" in f for f in rep_x["failures"]), json.dumps(rep_x))

    noise = {i: {d: random.Random(stable_seed(i, d, "n")).choice([0, 5]) for d in DIMENSIONS}
             for i in human}
    rep_n = calibration_report(noise, human)
    check("agreement_floor_fires", any("agreement" in f for f in rep_n["failures"]), json.dumps(rep_n))

    clean = Episode("e1", "C10", "We compare two conditions with a held-out split and report paired intervals.")
    bad = Episode("e2", "C10", "Result: accuracy = 0.93 on dataset TBD, and no control was used.")
    check("redlines_silent_on_clean", run_redlines(clean.artifact_text) == [], str(run_redlines(clean.artifact_text)))
    fired = run_redlines(bad.artifact_text)
    check("redlines_fire_on_defective", {"fabricated_resource", "unexecuted_number", "missing_control"} <= set(fired),
          str(fired))

    s_bad = score_episode(bad, lambda d, t: 4)
    check("fatal_flaw_zeroes_dimension", s_bad.dimensions["resources"] == 0 and not s_bad.fatal_error_free,
          json.dumps(s_bad.dimensions))
    s_ok = score_episode(clean, lambda d, t: 4)
    check("clean_episode_is_fec", s_ok.fatal_error_free and s_ok.total == 24, json.dumps(s_ok.dimensions))

    calls = []
    score_episode(clean, lambda d, t: calls.append(d) or 3)
    check("one_call_per_dimension", calls == list(DIMENSIONS), str(calls))

    from scoring import state_use_report, structural_gaps  # noqa: E402
    scaffold = "x:\n" + "sampling_frame:\n"
    filled = "x: a\nsampling_frame: merged pull requests in three repositories\n"
    design_good = "We sample merged pull requests from three repositories."
    design_bad = "We sample whatever is convenient."
    good = state_use_report(filled, design_good, "sampling_frame", scaffold)
    bad_state = state_use_report(scaffold, design_good, "sampling_frame", scaffold)
    check("state_use_detects_consumption", good["consumed"] and good["carry_through_ratio"] > 0.3, json.dumps(good))
    check("state_use_detects_empty_scaffold", not bad_state["consumed"], json.dumps(bad_state))
    weak = state_use_report(filled, design_bad, "sampling_frame", scaffold)
    check("carry_through_separates_use_from_compliance", weak["consumed"] and weak["carry_through_ratio"] < good["carry_through_ratio"],
          json.dumps(weak))
    check("structural_gaps_flag_incomplete", "names_uncertainty" in structural_gaps("We will run an ablation on GAIA with a primary outcome and a stopping rule."),
          str(structural_gaps("We will run an ablation on GAIA with a primary outcome and a stopping rule.")))
    check("structural_gaps_silent_on_complete",
          structural_gaps("Ablation on GAIA, primary outcome accuracy, bootstrap confidence interval, stopping rule fixed.") == [],
          str(structural_gaps("Ablation on GAIA, primary outcome accuracy, bootstrap confidence interval, stopping rule fixed.")))

    # --- Added after a mutation audit: these three mutations previously survived. ---
    zeroed = Scored(episode_id="m1", redlines=[], dimensions={d: 0.0 for d in DIMENSIONS})
    check("zero_dimension_is_not_fatal_error_free", zeroed.fatal_error_free is False,
          "a dimension scored zero must not count as fatal-error-free")

    scored_ok = Scored(episode_id="m2", redlines=[], dimensions={d: 3.0 for d in DIMENSIONS})
    check("positive_dimensions_are_fatal_error_free", scored_ok.fatal_error_free is True,
          "all positive dimensions must pass")

    with_redline = Scored(episode_id="m3", redlines=["fabricated result"],
                          dimensions={d: 3.0 for d in DIMENSIONS})
    check("redline_blocks_fatal_error_free", with_redline.fatal_error_free is False,
          "a redline must block the endpoint even when every dimension is positive")

    rep_carry = state_use_report(
        state_text="sampling_frame: alpha alpha alpha beta",
        design_text="alpha beta",
        field="sampling_frame",
        scaffold_text="sampling_frame:",
    )
    check("carry_through_ratio_bounded_by_one", 0.0 <= rep_carry["carry_through_ratio"] <= 1.0,
          json.dumps(rep_carry))

    passed = sum(1 for r in R if r["passed"])

    print(json.dumps({"suite": "study_a_scoring", "checks": len(R), "passed": passed, "results": R},
                     indent=2, sort_keys=True))
    return 0 if passed == len(R) else 1


def stable_seed(*parts) -> int:
    """Process-independent seed; builtin hash() is salted and would make this gate flaky."""
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:4], "big")


def statistics_mean(d):
    return sum(d.values()) / len(d)


if __name__ == "__main__":
    sys.exit(main())
