"""Tests for the manipulation-check summarizer (instruction-0016a item 1)."""

import json
from pathlib import Path


from experiments.study_b.summarize_manipulation import (
    aggregate_receipts,
    episode_rule_check,
)


def make_receipt(arm, seed, passed=True, tools=None, decisions=0, thresholds=0):
    mc = {
        "manipulation_check_passed": passed,
        "tool_call_counts": tools if tools is not None else {"bash": 3},
        "decisions_recorded": decisions,
        "thresholds_registered": thresholds,
    }
    ep = {"arm": arm, "seed": seed, "manipulation_check": mc}
    return {"episodes": [ep]}


def test_rule_b0_ipython_violation():
    ok = episode_rule_check("B0", {"tool_call_counts": {"bash": 2}})
    bad = episode_rule_check("B0", {"tool_call_counts": {"ipython": 1}})
    assert ok["pass"] is True
    assert bad["pass"] is False and bad["rule"] == "B0_no_ipython_tool"


def test_rule_b2_decision_precedence():
    ok = episode_rule_check("B2", {"decisions_recorded": 1, "thresholds_registered": 1})
    bad_dec = episode_rule_check("B2", {"decisions_recorded": 0, "thresholds_registered": 2})
    bad_thr = episode_rule_check("B2", {"decisions_recorded": 2, "thresholds_registered": 0})
    assert ok["pass"] is True
    assert bad_dec["pass"] is False and bad_thr["pass"] is False
    assert bad_dec["rule"] == "B2_decision_node_precedence"


def test_b1_has_no_arm_rule():
    assert episode_rule_check("B1", {})[ "pass"] is True


def _write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_aggregate_clean_and_violating(tmp_path):
    clean = _write(tmp_path, "r1.json", make_receipt("B0", 0))
    b2_violating = _write(
        tmp_path, "r2.json",
        make_receipt("B2", 1, tools={"bash": 1}, decisions=0, thresholds=2))
    summary = aggregate_receipts([clean, b2_violating], root=tmp_path)
    assert summary["input_receipt_count"] == 2
    assert summary["episodes_total"] == 2
    assert summary["manipulation_check_passed_total"] == 2  # boolean field only
    assert summary["rule_violations_total"] == 1
    assert summary["excluded_episode_count"] == 1
    assert summary["excluded_episodes"][0]["arm"] == "B2"
    assert summary["all_passed"] is False
    assert summary["arm_aggregates"]["B0"]["rule_checks"]["B0_no_ipython_tool"] == {"pass": 1, "violations": 0}


def test_aggregate_all_clean(tmp_path):
    paths = [
        _write(tmp_path, "b0.json", make_receipt("B0", 0)),
        _write(tmp_path, "b1.json", make_receipt("B1", 0)),
        _write(tmp_path, "b2.json",
               make_receipt("B2", 0, tools={"read": 1}, decisions=2, thresholds=1)),
    ]
    summary = aggregate_receipts(paths, root=tmp_path)
    assert summary["all_passed"] is True
    assert summary["excluded_episode_count"] == 0


def test_output_receipt_does_not_claim_execution():
    # Single-run provenance binding cannot describe a 120-run aggregate; the
    # receipt must not assert execution at its own level.
    from experiments.study_b.summarize_manipulation import assemble_output, TASK, N_SEEDS
    out = assemble_output({"input_receipts": [], "input_receipt_count": 0,
                           "episodes_total": 0, "manipulation_check_passed_total": 0,
                           "rule_violations_total": 0, "excluded_episodes": [],
                           "excluded_episode_count": 0, "all_passed": False,
                           "arm_aggregates": {}},
                          Path("experiments/study_b/summarize_manipulation.py"))
    assert out["executed"] is False
    for marker in ("arms", "aggregate_metrics", "episodes", "tokens", "cost_usd"):
        assert marker not in out
    assert out["schema_version"] == "study-b-manipulation-summary/v1"
    assert out["task"] == "T3" and out["n_seeds"] == 40
    assert out["summarizer"]["script"].endswith("summarize_manipulation.py")
