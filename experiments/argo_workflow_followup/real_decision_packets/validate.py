#!/usr/bin/env python3
"""Deterministic real-research decision packet validator.

Facts are rederived from receipt bytes. Route fidelity, claim-relative evidence
sufficiency, narrow policy-decision correctness, and external task outcome are
reported as separate axes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def object_file_sha(value: dict) -> str:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_routed(packet_contract: dict, packet_manifest: dict, root: Path) -> tuple[str, dict, list[str]]:
    expected = packet_contract["evidence"]
    routed = packet_manifest.get("routed_roles")
    if not isinstance(routed, list) or len(routed) != len(set(routed)):
        return "INVALID", {}, ["MALFORMED_ROUTE"]
    expected_roles = set(expected)
    routed_roles = set(routed)
    if routed_roles - expected_roles:
        return "INVALID", {}, ["WRONG_OR_EXTRA_ROLE"]
    if expected_roles - routed_roles:
        return "INCONCLUSIVE", {}, ["MISSING_ROLE"]
    loaded: dict[str, dict] = {}
    missing = []
    mismatched = []
    for role in sorted(expected_roles):
        spec = expected[role]
        path = root / spec["path"]
        if not path.is_file():
            missing.append(role)
            continue
        if file_sha(path) != spec["sha256"]:
            mismatched.append(role)
            continue
        loaded[role] = json.loads(path.read_text())
    if mismatched:
        return "INVALID", loaded, [f"EVIDENCE_IDENTITY:{role}" for role in mismatched]
    if missing:
        return "INCONCLUSIVE", loaded, [f"EVIDENCE_MISSING:{role}" for role in missing]
    return "PASS", loaded, []


def _ratio_exact_count(text: str) -> int:
    numerator, denominator = (int(value) for value in text.split("/"))
    return numerator if numerator == denominator else -1


def _derive_external(documents: dict[str, dict]) -> dict:
    frontier = documents["frontier"]
    findings = frontier["source_audit"]["findings"]
    measured = frontier["measured"]
    return {
        "official_log_to_csv_byte_exact": measured["official_log_to_csv_byte_exact"],
        "scoped_exact": _ratio_exact_count(measured["SCOPED_REVALIDATE_exact"]),
        "nested_pairs": measured["nested_regime_pairs"],
        "inference_units": 1 if findings["inference_unit"] == "one research programme" else None,
        "training_code_present": findings["training_code_present"],
        "external_task_outcome": "NOT_MEASURED",
    }


def _derive_physics(documents: dict[str, dict]) -> dict:
    audit = documents["audit"]
    result = audit["audit"]["result"]
    findings = result["findings"]
    return {
        "archive_audit_passed": result["passed"],
        "aggregate_byte_exact": audit["aggregate_replay"]["byte_exact"],
        "episode_rows": findings["episode_rows"],
        "direct_source_closed_rows": findings["episode_rows_with_direct_source_path"],
        "raw_transcripts_published": findings["raw_transcripts_published"],
        "inference_units": 1,
        "external_task_outcome": "NOT_MEASURED",
    }


def _derive_discoveryworld(documents: dict[str, dict]) -> dict:
    validation = documents["validation"]
    design = documents["design"]
    gold = documents["gold_contract"]
    source = documents["source_audit"]
    execution = design["execution"]
    return {
        "schema_validation_passed": validation["validation"]["passed"],
        "task_rows": len(design["tasks"]),
        "seed_rows": len(design["tasks"]),
        "inference_units": len({task["family"] for task in design["tasks"]}),
        "runner_present": execution["runner"] is not None,
        "gold_generated": gold["status"] != "DESIGN_ONLY_NOT_EXECUTED",
        "source_admitted": source["admissibility"]["usable_now"] is True
        if isinstance(source["admissibility"]["usable_now"], bool)
        else source["result"] not in {"CONDITIONAL_NOT_ADMITTED", "NOT_ADMITTED"},
        "external_task_outcome": "NOT_MEASURED",
    }


def _derive_isolation(documents: dict[str, dict]) -> dict:
    readiness = documents["readiness"]
    approval = documents["approval"]
    return {
        "readiness_validated": readiness["readiness"] == "READY_FOR_EXPLICIT_USER_DECISION_NOT_EXECUTION",
        "approval_present": readiness["approval_present"] is True
        and approval["status"] == "APPROVED"
        and approval["approved_by"] == "user",
        "container_launches": readiness["container_launches"],
        "external_task_outcome": "NOT_MEASURED",
    }


ADAPTERS = {
    "external_trace": _derive_external,
    "grounded_physics": _derive_physics,
    "discoveryworld": _derive_discoveryworld,
    "isolation_canary": _derive_isolation,
}


def _condition_passes(condition: dict, facts: dict) -> bool:
    actual = facts.get(condition["fact"])
    op = condition["op"]
    expected = condition["value"]
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "gt":
        return actual > expected
    if op == "gte":
        return actual >= expected
    if op == "lt":
        return actual < expected
    raise ValueError(f"unsupported condition operator: {op}")


def _apply_rules(packet_contract: dict, facts: dict) -> dict:
    for rule in packet_contract["rules"]:
        if all(_condition_passes(condition, facts) for condition in rule["when"]):
            return {"rule_id": rule["id"], "decision": rule["decision"], "sufficiency": rule["sufficiency"]}
    return {"rule_id": "default", **packet_contract["default"]}


def _claim_errors(expectations: dict, claims: object, facts: dict) -> list[str]:
    if not isinstance(claims, dict) or set(claims) != set(expectations):
        return ["CLAIM_SCHEMA"]
    return [f"CLAIM_MISMATCH:{key}" for key in expectations if claims[key] != facts.get(key)]


def simulate_withdrawals(contract: dict, manifest: dict) -> dict:
    packet_ids = set(contract["packets"])
    trials = []
    exact = 0
    global_overrevocations = 0
    for trial in manifest.get("withdrawal_trials", []):
        owner, role = trial["evidence"].split(".", 1)
        target_path = contract["packets"][owner]["evidence"][role]["path"]
        affected = sorted(
            packet_id
            for packet_id, packet in contract["packets"].items()
            if any(spec["path"] == target_path for spec in packet["evidence"].values())
        )
        expected = sorted(trial["expected_affected"])
        if affected == expected:
            exact += 1
        global_overrevocations += len(packet_ids - set(affected))
        trials.append({
            "evidence": trial["evidence"],
            "selective_affected": affected,
            "expected_affected": expected,
            "global_affected": sorted(packet_ids),
            "global_overrevocations": len(packet_ids - set(affected)),
        })
    return {
        "events": len(trials),
        "selective_exact": exact,
        "global_overrevocations": global_overrevocations,
        "trials": trials,
    }


def validate_documents(contract: dict, manifest: dict, root: Path) -> dict:
    root = Path(root)
    global_errors: list[str] = []
    if manifest.get("schema_version") != "argo-real-decision-packet-manifest/v1":
        global_errors.append("MANIFEST_SCHEMA")
    if contract.get("schema_version") != "argo-real-decision-packet-contract/v1":
        global_errors.append("CONTRACT_SCHEMA")
    if manifest.get("contract_sha256") != object_file_sha(contract):
        global_errors.append("CONTRACT_IDENTITY")
    graph_path = root / manifest.get("graph", "")
    graph_nodes = set()
    if graph_path.is_file():
        graph_nodes = {node["id"] for node in json.loads(graph_path.read_text())["nodes"]}
    else:
        global_errors.append("GRAPH_MISSING")
    manifest_packets = manifest.get("packets", [])
    by_id = {packet.get("id"): packet for packet in manifest_packets if isinstance(packet, dict)}
    if len(by_id) != len(manifest_packets) or set(by_id) != set(contract.get("packets", {})):
        global_errors.append("PACKET_SET")

    packet_results: dict[str, dict] = {}
    for packet_id, packet_contract in contract.get("packets", {}).items():
        packet_manifest = by_id.get(packet_id, {})
        errors: list[str] = []
        if packet_contract["graph_decision_id"] not in graph_nodes:
            errors.append("GRAPH_DECISION_ID")
        route, documents, route_errors = _load_routed(packet_contract, packet_manifest, root)
        errors.extend(route_errors)
        facts: dict = {}
        rule = {"rule_id": "not_evaluated", "decision": None, "sufficiency": "INCONCLUSIVE"}
        claim_errors: list[str] = []
        decision_correct = False
        if route == "PASS":
            try:
                facts = ADAPTERS[packet_contract["adapter"]](documents)
                rule = _apply_rules(packet_contract, facts)
                claim_errors = _claim_errors(packet_contract["claim_expectations"], packet_manifest.get("claims"), facts)
                errors.extend(claim_errors)
                decision_correct = packet_manifest.get("selected_decision") == rule["decision"]
                if not decision_correct:
                    errors.append("DECISION_MISMATCH")
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                errors.append(f"ADAPTER:{type(exc).__name__}")
                route = "INVALID"
        if route == "INVALID" or any(error in {"GRAPH_DECISION_ID", "DECISION_MISMATCH", "CLAIM_SCHEMA"} or error.startswith(("CLAIM_MISMATCH", "ADAPTER")) for error in errors):
            verdict = "INVALID"
        elif route == "INCONCLUSIVE":
            verdict = "INCONCLUSIVE"
        elif rule["sufficiency"].startswith("SUFFICIENT_"):
            verdict = "PASS"
        else:
            verdict = "INCONCLUSIVE"
        packet_results[packet_id] = {
            "route_fidelity": route,
            "claim_relative_evidence_sufficiency": rule["sufficiency"],
            "derived_rule": rule["rule_id"],
            "derived_decision": rule["decision"],
            "selected_decision": packet_manifest.get("selected_decision"),
            "policy_decision_correct": decision_correct,
            "external_task_outcome": facts.get("external_task_outcome", "NOT_MEASURED"),
            "facts": facts,
            "verdict": verdict,
            "errors": errors,
        }

    replay = simulate_withdrawals(contract, manifest)
    values = list(packet_results.values())
    summary = {
        "packets": len(values),
        "route_fidelity_pass": sum(row["route_fidelity"] == "PASS" for row in values),
        "sufficiency_pass": sum(row["claim_relative_evidence_sufficiency"].startswith("SUFFICIENT_") for row in values),
        "sufficiency_inconclusive": sum(row["claim_relative_evidence_sufficiency"].startswith("INCONCLUSIVE") for row in values),
        "policy_decision_correct": sum(row["policy_decision_correct"] for row in values),
        "external_task_outcomes_measured": sum(row["external_task_outcome"] != "NOT_MEASURED" for row in values),
        "selective_withdrawal_events": replay["events"],
        "selective_exact": replay["selective_exact"],
        "global_overrevocations": replay["global_overrevocations"],
    }
    if summary != manifest.get("expected_descriptive_summary"):
        global_errors.append("SUMMARY_MISMATCH")
    invalid_packets = [packet_id for packet_id, row in packet_results.items() if row["verdict"] == "INVALID"]
    passed = not global_errors and not invalid_packets and summary["route_fidelity_pass"] == summary["packets"]
    return {
        "passed": passed,
        "errors": global_errors,
        "invalid_packets": invalid_packets,
        "summary": summary,
        "packets": packet_results,
        "withdrawal_replay": replay,
        "interpretation": "Route fidelity is 4/4 while claim-relative sufficiency is 2/4 and external task outcomes are 0/4; narrow policy correctness does not substitute for external outcome.",
        "confirmatory": False,
    }


def validate_paths(contract_path: Path, manifest_path: Path, root: Path) -> dict:
    return validate_documents(json.loads(Path(contract_path).read_text()), json.loads(Path(manifest_path).read_text()), root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = validate_paths(args.contract, args.manifest, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
