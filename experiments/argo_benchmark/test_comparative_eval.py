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
    ABSORPTION_ENTRIES,
    ACCEPTANCE_RULE_FAMILIES,
    DesignSourceAbsorptionLedger,
    HARNESS_ENTRY_ID,
    LEDGER,
    TESTED,
    IMPLEMENTED_UNTESTED,
    DECLARED_ONLY,
    TEST_STATUSES,
    s1_case_anchors,
    s1_specification_mapping,
    compute_arm_metrics,
    verify_claims_against_receipt,
)

FAILURES = []
CHECKS_RUN = 0

# The counting convention this ledger must match: the absorption table covers
# every recorded system, the representative view drops the application-level
# instances of a published acceptance family another entry already represents,
# and the families are the distinct published gate categories.
THESIS_CONVENTION = {
    "absorption_table": 10,
    "frontier_systems": 9,
    "representative_view": 8,
    "acceptance_families": 6,
}


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS_RUN
    CHECKS_RUN += 1
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

    # 4. Design-source absorption ledger: canonical counts, derived not stored
    counts = LEDGER.counts()
    for key, expected in THESIS_CONVENTION.items():
        check(f"ledger count '{key}' matches the thesis counting convention",
              counts.get(key) == expected, f"got {counts.get(key)!r}, want {expected}")

    check("every count is derived from the one canonical entry list",
          counts["absorption_table"] == len(ABSORPTION_ENTRIES)
          and counts["representative_view"] == len([e for e in ABSORPTION_ENTRIES if e.representative]))
    check("counts are internally consistent (frontier systems + this harness = table)",
          counts["frontier_systems"] + 1 == counts["absorption_table"])

    # The two application-level instances of the published ACCEPTED family fold
    # into that family rather than carrying their own representative entry.
    collapsed = {e.id for e in LEDGER.collapsed_entries}
    check("exactly the accepted-family instances are folded out of the representative view",
          collapsed == {"the_ai_scientist", "mlagentbench"}, f"got {sorted(collapsed)}")
    accepted_reps = LEDGER.family_representatives()["ACCEPTED"]
    check("the folded entries' family keeps its own representatives",
          set(accepted_reps) == {"sol_pi", "openai_agents_api", "prime_agent"}, f"got {accepted_reps}")

    # Ledger invariants: uniqueness, vocabulary, non-empty absorption fields,
    # family coverage. validate() raises on any violation.
    try:
        LEDGER.validate()
        validated = True
        detail = ""
    except ValueError as exc:
        validated = False
        detail = str(exc)
    check("ledger self-validation passes on the canonical entries", validated, detail)
    check("absorption table covers this harness as well as the frontier systems",
          HARNESS_ENTRY_ID in {e.id for e in LEDGER.absorption_table}
          and HARNESS_ENTRY_ID not in {e.id for e in LEDGER.collapsed_entries})
    check("every entry records an absorbed element, a requirement and a site",
          all(e.absorbed_element.strip() and e.design_requirement.strip()
              and e.implementation_site.strip() for e in LEDGER))
    check("every test status is drawn from the declared vocabulary",
          all(e.test_status in TEST_STATUSES for e in LEDGER))
    check("every acceptance family is drawn from the declared vocabulary",
          all(e.acceptance_family in ACCEPTANCE_RULE_FAMILIES for e in LEDGER)
          and len(LEDGER.acceptance_families) == len(ACCEPTANCE_RULE_FAMILIES))
    check("a duplicate system identifier is rejected",
          _rejects_duplicate_entries())

    # TESTED is reserved for elements an executed run actually exercised, so at
    # least one entry must sit in each untested category and the tested entries
    # must name an exercised site.
    statuses = LEDGER.by_test_status()
    check("test status vocabulary covers the ledger",
          statuses[TESTED] and (statuses[IMPLEMENTED_UNTESTED] or statuses[DECLARED_ONLY]))
    check("tested entries only claim sites with an executed run behind them",
          all(entry.tested for entry in LEDGER if entry.test_status == TESTED)
          and all(not entry.tested for entry in LEDGER.untested()))

    # 5. S1 specification mapping: requirement records, not judgements
    anchors = s1_case_anchors(0.5183, 0.5406, 0.000117)
    check("S1 anchors report the frozen case inputs unchanged",
          anchors["naive_cv_mae"] == 0.5183 and anchors["group_isolated_cv_mae"] == 0.5406
          and anchors["holdout_mae_diff"] == 0.000117)
    check("S1 anchors report the grouped baselines unchanged",
          anchors["unified_baseline_mae"] == 0.5245
          and anchors["group_isolated_baseline_mae"] == 0.5179)
    check("S1 leakage magnitude is derived from the anchors, not restated",
          anchors["leakage_delta"] == anchors["group_isolated_cv_mae"] - anchors["naive_cv_mae"]
          and anchors["leakage_pct"] == round(
              anchors["leakage_delta"] / anchors["group_isolated_cv_mae"] * 100, 2))
    check("S1 anchors that no longer describe the case are rejected",
          _rejects_inconsistent_anchors())

    mapping = s1_specification_mapping(
        candidate_strategy="color_stratified_gbt",
        naive_cv_mae=0.5183,
        group_isolated_cv_mae=0.5406,
        holdout_mae_diff=0.000117,
    )
    check("every absorption entry receives one mapping record",
          len(mapping) == len(ABSORPTION_ENTRIES) and set(mapping) == set(e.id for e in ABSORPTION_ENTRIES))
    check("each record carries the published acceptance rule it was derived from",
          all(rec["published_acceptance_rule"] == LEDGER[sid].gate_mechanism
              for sid, rec in mapping.items()))
    check("each record carries the absorbed element, requirement and site",
          all(rec["absorbed_element"] == LEDGER[sid].absorbed_element
              and rec["design_requirement"] == LEDGER[sid].design_requirement
              and rec["implementation_site"] == LEDGER[sid].implementation_site
              for sid, rec in mapping.items()))
    check("each record reports the shared S1 anchors",
          all(rec["s1_anchors"] == anchors for rec in mapping.values()))
    check("this harness reports its own residual defect with the derived leakage magnitude",
          f"{anchors['leakage_pct']}%" in mapping[HARNESS_ENTRY_ID]["published_rule_consequence_under_s1"])
    check("records carry no verdict or gate-action vocabulary",
          not any(k in rec for rec in mapping.values()
                  for k in ("epistemic_verdict", "action", "accepted", "detected_leakage")))
    check("an unknown S1 candidate strategy is rejected", _rejects_unknown_strategy())

    print(f"\n{len(FAILURES)} failing checks" if FAILURES else f"\nAll {CHECKS_RUN} checks passed.")
    return 1 if FAILURES else 0


def _rejects_duplicate_entries() -> bool:
    try:
        DesignSourceAbsorptionLedger((ABSORPTION_ENTRIES[0], ABSORPTION_ENTRIES[0]))
    except ValueError:
        return True
    return False


def _rejects_inconsistent_anchors() -> bool:
    try:
        # Grouping must worsen the error; these anchors invert that relation.
        s1_case_anchors(0.5406, 0.5183, 0.000117)
    except ValueError:
        return True
    return False


def _rejects_unknown_strategy() -> bool:
    try:
        s1_specification_mapping("not_a_declared_strategy", 0.5183, 0.5406, 0.000117)
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())
