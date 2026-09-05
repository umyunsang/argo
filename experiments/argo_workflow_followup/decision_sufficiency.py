#!/usr/bin/env python3
"""Deterministic scorer for routing and decision sufficiency.

The scorer keeps route fidelity, evidence sufficiency, decision correctness, and
end-to-end task outcome separate. It never treats a correct route or a completed
packet as proof that the downstream task succeeded.
"""
from __future__ import annotations

PASS = "PASS"
INVALID = "INVALID"
INCONCLUSIVE = "INCONCLUSIVE"


def _invalid_result(task_outcome: bool, reason: str) -> dict:
    return {
        "route_verdict": INVALID,
        "evidence_verdict": INVALID,
        "decision_verdict": INVALID,
        "overall_verdict": INVALID,
        "task_outcome": bool(task_outcome),
        "confirmatory_success": False,
        "route_over": [],
        "route_under": [],
        "reasons": [reason],
    }


def _index(items: object, field: str) -> dict[str, dict]:
    if not isinstance(items, list):
        raise ValueError(f"{field}_NOT_LIST")
    indexed: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError(f"{field}_ITEM_INVALID")
        item_id = item["id"]
        if not item_id or item_id in indexed:
            raise ValueError(f"{field}_ID_INVALID")
        indexed[item_id] = item
    return indexed


def _string_set(items: object, field: str) -> set[str]:
    if not isinstance(items, list) or not all(isinstance(item, str) and item for item in items):
        raise ValueError(f"{field}_INVALID")
    if len(items) != len(set(items)):
        raise ValueError(f"{field}_DUPLICATE")
    return set(items)


def _has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate(gold: dict, packet: dict, route: list[str], task_outcome: bool) -> dict:
    """Evaluate one hidden-gold decision packet without exposing the gold."""
    try:
        if gold.get("schema_version") != "argo-decision-sufficiency-gold/v1":
            return _invalid_result(task_outcome, "GOLD_SCHEMA")
        if packet.get("schema_version") != "argo-decision-packet/v1":
            return _invalid_result(task_outcome, "PACKET_SCHEMA")
        if packet.get("decision_id") != gold.get("decision_id"):
            return _invalid_result(task_outcome, "DECISION_ID")

        expected_route = _string_set(gold.get("expected_route"), "EXPECTED_ROUTE")
        actual_route = _string_set(route, "ROUTE")
        required_evidence = _index(gold.get("required_evidence"), "REQUIRED_EVIDENCE")
        revoked_evidence = _index(gold.get("revoked_evidence", []), "REVOKED_EVIDENCE")
        actual_evidence = _index(packet.get("evidence"), "EVIDENCE")
        required_constraints = _index(
            gold.get("required_constraints"), "REQUIRED_CONSTRAINTS"
        )
        actual_constraints = _index(packet.get("constraints"), "CONSTRAINTS")
        required_alternatives = _string_set(
            gold.get("required_alternatives"), "REQUIRED_ALTERNATIVES"
        )
        actual_alternatives = _string_set(packet.get("alternatives"), "ALTERNATIVES")
    except (AttributeError, TypeError, ValueError) as exc:
        return _invalid_result(task_outcome, str(exc))

    reasons: list[str] = []
    route_over = sorted(actual_route - expected_route)
    route_under = sorted(expected_route - actual_route)
    route_verdict = PASS if not route_over and not route_under else INVALID
    if route_over:
        reasons.append("ROUTE_OVER")
    if route_under:
        reasons.append("ROUTE_UNDER")

    evidence_invalid = False
    evidence_missing = False
    for evidence_id, required in required_evidence.items():
        actual = actual_evidence.get(evidence_id)
        if actual is None:
            evidence_missing = True
            reasons.append(f"EVIDENCE_MISSING:{evidence_id}")
            continue
        if actual.get("version") != required.get("version"):
            evidence_invalid = True
            reasons.append(f"EVIDENCE_VERSION:{evidence_id}")
        if actual.get("status") != "VALID":
            evidence_invalid = True
            reasons.append(f"EVIDENCE_STATUS:{evidence_id}")
    for evidence_id, revoked in revoked_evidence.items():
        actual = actual_evidence.get(evidence_id)
        if actual is not None and actual.get("version") == revoked.get("version"):
            evidence_invalid = True
            reasons.append(f"REVOKED_EVIDENCE:{evidence_id}")

    for constraint_id, required in required_constraints.items():
        actual = actual_constraints.get(constraint_id)
        if actual is None:
            evidence_missing = True
            reasons.append(f"CONSTRAINT_MISSING:{constraint_id}")
            continue
        if actual.get("version") != required.get("version"):
            evidence_invalid = True
            reasons.append(f"CONSTRAINT_VERSION:{constraint_id}")
        if actual.get("applicable") is not True:
            evidence_invalid = True
            reasons.append(f"CONSTRAINT_APPLICABILITY:{constraint_id}")

    missing_declared = packet.get("missing_evidence")
    conflicts = packet.get("unresolved_conflicts")
    if not isinstance(missing_declared, list) or not isinstance(conflicts, list):
        evidence_invalid = True
        reasons.append("GAP_LIST_SCHEMA")
    elif missing_declared or conflicts:
        evidence_missing = True
        reasons.append("DECLARED_GAP")

    if evidence_invalid:
        evidence_verdict = INVALID
    elif evidence_missing:
        evidence_verdict = INCONCLUSIVE
    else:
        evidence_verdict = PASS

    decision_invalid = False
    decision_missing = False
    if not required_alternatives <= actual_alternatives:
        decision_missing = True
        reasons.append("ALTERNATIVES_MISSING")
    selected = packet.get("selected")
    if not isinstance(selected, str) or not selected:
        decision_invalid = True
        reasons.append("SELECTION_INVALID")
    elif actual_alternatives and selected not in actual_alternatives:
        decision_invalid = True
        reasons.append("SELECTION_INVALID")
    expected_choice = gold.get("expected_choice")
    if expected_choice is None:
        decision_missing = True
        reasons.append("CHOICE_ORACLE_ABSENT")
    elif selected != expected_choice:
        decision_invalid = True
        reasons.append("CHOICE_INCORRECT")
    if not _has_text(packet.get("falsifier")):
        decision_missing = True
        reasons.append("FALSIFIER_MISSING")
    next_experiment = packet.get("next_experiment")
    if not isinstance(next_experiment, dict) or not all(
        _has_text(next_experiment.get(key)) for key in ("action", "observable", "stop_rule")
    ):
        decision_missing = True
        reasons.append("NEXT_EXPERIMENT_INCOMPLETE")

    if decision_invalid:
        decision_verdict = INVALID
    elif decision_missing:
        decision_verdict = INCONCLUSIVE
    else:
        decision_verdict = PASS

    if packet.get("accessed_hidden_oracle") is not False:
        reasons.append("HIDDEN_ORACLE_ACCESS")
        route_verdict = evidence_verdict = decision_verdict = INVALID

    verdicts = (route_verdict, evidence_verdict, decision_verdict)
    if INVALID in verdicts:
        overall_verdict = INVALID
    elif INCONCLUSIVE in verdicts:
        overall_verdict = INCONCLUSIVE
    else:
        overall_verdict = PASS

    return {
        "route_verdict": route_verdict,
        "evidence_verdict": evidence_verdict,
        "decision_verdict": decision_verdict,
        "overall_verdict": overall_verdict,
        "task_outcome": bool(task_outcome),
        "confirmatory_success": overall_verdict == PASS and bool(task_outcome),
        "route_over": route_over,
        "route_under": route_under,
        "reasons": sorted(set(reasons)),
    }
