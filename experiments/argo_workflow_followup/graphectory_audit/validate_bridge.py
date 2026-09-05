#!/usr/bin/env python3
"""Validate the cross-programme routing/decision/outcome category bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path, root: Path) -> dict:
    root = Path(root)
    bridge = json.loads(Path(path).read_text())
    errors: list[str] = []
    inputs = {}
    for name, spec in bridge.get("inputs", {}).items():
        source = root / spec.get("path", "")
        if not source.is_file() or sha(source) != spec.get("sha256"):
            errors.append(f"INPUT_IDENTITY:{name}")
        else:
            inputs[name] = json.loads(source.read_text())
    expected = None
    if {"real_decision_packets", "graphectory_audit", "graphectory_builder_replay", "graphectory_frontier_validation"}.issubset(inputs):
        packet_summary = inputs["real_decision_packets"]["replay"]["summary"]
        findings = inputs["graphectory_audit"]["audit"]["result"]["findings"]
        builder = inputs["graphectory_builder_replay"]["measured"]
        frontier = inputs["graphectory_frontier_validation"]["result"]
        if frontier.get("passed") is not True:
            errors.append("FRONTIER_NOT_VALID")
        expected = {
            "canonical_packet_route_pass": packet_summary["route_fidelity_pass"],
            "canonical_packet_sufficiency_pass": packet_summary["sufficiency_pass"],
            "canonical_packet_policy_decisions_correct": packet_summary["policy_decision_correct"],
            "canonical_packet_external_outcomes": packet_summary["external_task_outcomes_measured"],
            "graphectory_graph_metric_paths": findings["tracked_graph_paths"],
            "graphectory_selected_status_verified": findings["selected_graph_metric_status_matches"],
            "source_sample_external_report_matches": int(findings["sample_external_report_matches"].split("/")[0]),
            "source_sample_embedded_openhands_matches": builder["openhands_embedded_report_matches"],
            "source_sample_rows": builder["raw_samples"],
            "independent_external_programmes_added": inputs["graphectory_audit"]["independent_n"],
            "correction_decision_oracles_added": 0,
            "full_raw_archive_verified": findings["zenodo_archive_downloaded"],
        }
    if bridge.get("measured") != expected:
        errors.append("MEASURED_BINDING")
    surface_ids = {surface.get("id") for surface in bridge.get("surfaces", [])}
    if surface_ids != {"canonical_research_packets", "graphectory_recorded_corpus", "graphectory_source_samples"}:
        errors.append("SURFACES")
    required_limits = {
        "3972 independent research programmes",
        "six independent experiments",
        "independent re-evaluation of SWE-bench outcomes",
        "correction or reopening decision correctness",
        "ARGO policy efficacy",
        "full raw corpus verification",
    }
    if not required_limits.issubset(set(bridge.get("not_claimed", []))):
        errors.append("LIMITS")
    if bridge.get("model_calls") != 0 or bridge.get("spend_usd") != 0.0:
        errors.append("EXECUTION_SCOPE")
    return {"passed": not errors, "errors": errors, "measured": expected, "decision": bridge.get("decision")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = validate(args.bridge, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
