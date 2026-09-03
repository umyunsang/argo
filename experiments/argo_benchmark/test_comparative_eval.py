#!/usr/bin/env python3
"""Failing-first test suite for comparative_eval.py.

Only synthetic fixtures are referenced; no number here is evidence (RD-2026-09-03-80A).
"""
import sys
from pathlib import Path

# Add benchmark dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comparative_eval import (
    TASKS,
    ArmResult,
    compute_arm_metrics,
    verify_claims_against_receipt,
)

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def main() -> int:
    # 1. Benchmark tasks completeness
    check("three distinct R&D benchmark tasks declared", len(TASKS) == 3)
    check("each task has distinct domain and falsification threshold",
          len({t.domain for t in TASKS}) == 3 and all(t.falsification_threshold > 0 for t in TASKS))

    # 2. Claim verification against receipt
    receipt = {"brier_score": 0.1425, "accuracy": 0.884, "model_params": 125000}
    
    # Exact matching
    claims_exact = [{"metric": "brier_score", "value": 0.1425}, {"metric": "accuracy", "value": 0.884}]
    v, u = verify_claims_against_receipt(claims_exact, receipt)
    check("exact matching claims all verified", v == 2 and u == 0)

    # Within tolerance matching
    claims_tol = [{"metric": "brier_score", "value": 0.1430}]  # delta = 0.0005 <= 0.002
    v, u = verify_claims_against_receipt(claims_tol, receipt)
    check("within-tolerance claims verified", v == 1 and u == 0)

    # Outside tolerance matching (unsupported/hallucinated claim)
    claims_out = [{"metric": "brier_score", "value": 0.1600}]  # delta = 0.0175 > 0.002
    v, u = verify_claims_against_receipt(claims_out, receipt)
    check("outside-tolerance claims detected as unsupported", v == 0 and u == 1)

    # Unreported metric (fabricated metric name)
    claims_fab = [{"metric": "f1_score", "value": 0.95}]  # not in receipt
    v, u = verify_claims_against_receipt(claims_fab, receipt)
    check("fabricated metric names detected as unsupported", v == 0 and u == 1)

    # 3. Aggregate arm metrics computation
    res1 = ArmResult(
        arm_id="test_arm", task_id="RND-01", execution_success=True,
        iterations_taken=3, total_tokens=15000, cost_usd=0.045,
        reported_claims=[], verified_claims_count=8, unsupported_claims_count=2,
        claim_support_rate=0.8, falsification_detected=True, autonomous_pivot_success=True,
        execution_receipt_digest="sha1"
    )
    res2 = ArmResult(
        arm_id="test_arm", task_id="RND-02", execution_success=True,
        iterations_taken=4, total_tokens=25000, cost_usd=0.075,
        reported_claims=[], verified_claims_count=10, unsupported_claims_count=0,
        claim_support_rate=1.0, falsification_detected=False, autonomous_pivot_success=False,
        execution_receipt_digest="sha2"
    )
    agg = compute_arm_metrics([res1, res2])
    check("aggregated execution success rate is 1.0", agg["execution_success_rate"] == 1.0)
    check("aggregated total claims asserted is 20", agg["total_claims_asserted"] == 20)
    check("aggregated verified claims is 18", agg["total_claims_verified"] == 18)
    check("claim support rate is 0.9", agg["claim_support_rate"] == 0.9)
    check("hallucination rate is 0.1", agg["hallucination_rate"] == 0.1)
    check("mean tokens per task is 20000", agg["mean_tokens_per_task"] == 20000)
    check("mean cost is 0.06", agg["mean_cost_usd"] == 0.06)

    # Empty result guard
    check("empty results list returns empty dict without crash", compute_arm_metrics([]) == {})

    print(f"\n{len(FAILURES)} failing checks" if FAILURES else "\nAll 11 checks passed.")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
