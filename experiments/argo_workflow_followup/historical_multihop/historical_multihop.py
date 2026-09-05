#!/usr/bin/env python3
"""Typed replay for one byte-pinned historical ARGO research decision."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path


def _ordered(nodes: set[str]) -> list[str]:
    order = {"claim": 0, "decision": 1, "action": 2, "result": 3}
    return sorted(nodes, key=lambda node: (order.get(node.split(":", 1)[0], 9), node))


def _max_changed_path(case: dict, changed: set[str]) -> int:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in case["typed_edges"]:
        adjacency[edge["source"]].append(edge["target"])
    starts = [
        edge["source"]
        for edge in case["typed_edges"]
        if edge["source"] == "evidence:corrected_b2_protocol_audit"
    ]
    queue = deque((node, 0) for node in sorted(set(starts)))
    best: dict[str, int] = {node: 0 for node in starts}
    while queue:
        node, distance = queue.popleft()
        for child in adjacency[node]:
            candidate = distance + 1
            if candidate > best.get(child, -1):
                best[child] = candidate
                queue.append((child, candidate))
    return max((distance for node, distance in best.items() if node in changed), default=0)


def _after_state(case: dict, use_all_of: bool) -> tuple[dict, str]:
    state = dict(case["state_before"])
    state.update(case["correction_event"]["updates"])
    requirements = [bool(state[node]) for node in case["decision_rule"]["all_of"]]
    admitted = all(requirements) if use_all_of else any(requirements)
    selected = (
        case["decision_rule"]["if_true"]
        if admitted
        else case["decision_rule"]["if_false"]
    )
    state[case["decision_rule"]["decision_id"]] = (
        "PROMOTE_DIRECTLY" if admitted else "HOLD_AND_REDESIGN"
    )
    state.update(case["downstream_rule"][selected])
    return state, selected


def derive_typed(case: dict) -> dict:
    """Apply the frozen conjunctive validity/applicability decision rule."""
    after, selected = _after_state(case, use_all_of=True)
    before = case["state_before"]
    affected = {node for node, value in after.items() if before.get(node) != value}
    unaffected = {
        node
        for node in case["correction_event"]["unchanged"]
        if after.get(node) == before.get(node)
    }
    reported_after = {
        node: after[node]
        for node in (
            "decision:b2_causal_admission",
            "action:next_workflow_step",
            "result:workflow_branch",
        )
    }
    return {
        "affected_nodes": _ordered(affected),
        "unaffected_nodes": _ordered(unaffected),
        "after": reported_after,
        "selected": selected,
        "max_changed_path_edges": _max_changed_path(case, affected),
    }


def derive_any_support(case: dict) -> dict:
    """Deliberately coarse comparator that conflates required gates with alternatives."""
    after, selected = _after_state(case, use_all_of=False)
    return {
        "selected": selected,
        "decision": after[case["decision_rule"]["decision_id"]],
    }


def build_reference_packet(case: dict, replay: dict) -> dict:
    """Build a complete packet from released facts only for pipeline validation."""
    return {
        "schema_version": "argo-decision-packet/v1",
        "decision_id": case["decision_rule"]["decision_id"],
        "evidence": [
            {"id": item["id"], "version": item["version"], "status": "VALID"}
            for item in case["source_identities"]
        ],
        "constraints": [
            {
                "id": item["id"],
                "version": item["version"],
                "applicable": item["applicable"],
            }
            for item in case["current_constraints"]
        ],
        "alternatives": [item["id"] for item in case["alternatives"]],
        "selected": replay["selected"],
        "missing_evidence": [],
        "unresolved_conflicts": [],
        "falsifier": "A corrected endpoint passes only if the frozen scorer, action, access, and stratum semantics remain decision-valid.",
        "next_experiment": {
            "action": "construct an unambiguous stratified B3 contract",
            "observable": "affected-family resolution and unaffected-family no-harm",
            "stop_rule": "stop after the separately authorized eight development episodes",
        },
        "accessed_hidden_oracle": False,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(gold: dict, repo_root: Path) -> dict:
    """Re-derive the hidden choice and outcome from immutable historical receipts."""
    records = {item["role"]: item for item in gold["historical_source_receipts"]}
    loaded = {}
    hashes_match = True
    for role, record in records.items():
        path = repo_root / record["path"]
        hashes_match &= path.is_file() and _sha256(path) == record["sha256"]
        if path.is_file():
            loaded[role] = json.loads(path.read_text())

    audit = loaded.get("protocol_audit", {})
    rule = loaded.get("frozen_rule", {})
    downstream = loaded.get("downstream_outcome", {})
    decision_map = {
        "HOLD_C_AND_REDESIGN_OUTCOME_CONTRACT":
            "action:hold_confirmation_and_redesign_outcome_contract"
    }
    checks = {
        "source_hashes_match": hashes_match,
        "audit_marks_original_endpoint_invalid": audit.get("original_endpoint_status")
        == "INVALID_FOR_CAUSAL_DECISION; preserve unchanged",
        "audit_decision_maps_to_expected_choice": decision_map.get(audit.get("decision"))
        == gold.get("expected_choice"),
        "audit_preserves_descriptive_sensitivity": audit.get("status_only_sensitivity")
        == {
            "affected_families": 2,
            "affected_target_wins": 2,
            "affected_losses": 0,
            "unaffected_families": 2,
            "unaffected_no_harm": 2,
            "all_target_status_correct": 4,
            "all_base_status_correct": 2,
        },
        "frozen_rule_never_authorized_confirmation": rule.get("confirmation_c_authorized")
        is False,
        "downstream_b3_result_exists": downstream.get("decision")
        == gold.get("source_authority", {}).get("downstream_decision"),
        "downstream_still_did_not_authorize_c": downstream.get("C_authorized")
        is gold.get("source_authority", {}).get("downstream_C_authorized"),
        "gold_labels_pipeline_scope_only": "pipeline falsifier only"
        in str(gold.get("scope", "")),
    }
    return {"checks": checks, "all_pass": all(checks.values())}
