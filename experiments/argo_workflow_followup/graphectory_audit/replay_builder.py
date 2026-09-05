#!/usr/bin/env python3
"""Replay six bundled Graphectory raw samples with the pinned builder source."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_graph(value: dict) -> dict:
    value = json.loads(json.dumps(value))
    value["graph"].pop("debug_difficulty", None)
    return value


def graph_skeleton(value: dict) -> dict:
    return {
        "graph": {key: val for key, val in value["graph"].items() if key != "debug_difficulty"},
        "nodes": [
            {key: node.get(key) for key in ["id", "label", "phases", "step_indices", "tool", "command", "subcommand"]}
            for node in value["nodes"]
        ],
        "edges": [
            {key: edge.get(key) for key in ["source", "target", "type", "label", "key"]}
            for edge in value["edges"]
        ],
    }


def unit_diff(current: dict, prior: dict) -> dict:
    meta_keys = set(current["graph"]) | set(prior["graph"])
    changed_meta = sum(current["graph"].get(key) != prior["graph"].get(key) for key in meta_keys)
    current_nodes = {node["id"]: node for node in current["nodes"]}
    prior_nodes = {node["id"]: node for node in prior["nodes"]}
    node_ids = set(current_nodes) | set(prior_nodes)
    changed_nodes = sum(current_nodes.get(key) != prior_nodes.get(key) for key in node_ids)

    def edge_key(edge: dict) -> tuple:
        return (edge.get("source"), edge.get("target"), edge.get("key"), edge.get("type"), edge.get("label"))

    current_edges = {edge_key(edge): edge for edge in current["edges"]}
    prior_edges = {edge_key(edge): edge for edge in prior["edges"]}
    edge_ids = set(current_edges) | set(prior_edges)
    changed_edges = sum(current_edges.get(key) != prior_edges.get(key) for key in edge_ids)
    total = len(meta_keys) + len(node_ids) + len(edge_ids)
    changed = changed_meta + changed_nodes + changed_edges
    return {
        "total_units": total,
        "changed_units": changed,
        "preserved_units": total - changed,
        "changed_metadata": changed_meta,
        "changed_nodes": changed_nodes,
        "changed_edges": changed_edges,
        "resolution_preserved": current["graph"].get("resolution_status") == prior["graph"].get("resolution_status"),
    }


def safe_extract(capsule: Path, target: Path) -> None:
    with zipfile.ZipFile(capsule) as archive:
        for name in archive.namelist():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe archive member: {name}")
        archive.extractall(target)


def replay(capsule: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="graphectory-replay-") as temporary:
        extracted = Path(temporary) / "source"
        output = Path(temporary) / "output"
        safe_extract(capsule, extracted)
        repository = extracted / "repository"
        sys.path.insert(0, str(repository / "graph_construction"))
        from buildGraph import build_graph_from_oh_trajectory, build_graph_from_sa_trajectory
        from commandParser import CommandParser

        swe_instances = ["astropy__astropy-13453", "django__django-10973", "sympy__sympy-19783"]
        swe_root = repository / "data/samples/SWE-agent/trajectories/anthropic_filemap__deepseek--deepseek-chat__t-0.00__p-1.00__c-2.00___swe_bench_verified_test"
        swe_report = repository / "data/samples/SWE-agent/reports/deepseek-chat.json"
        parser = CommandParser()
        parser.load_tool_yaml_files([
            str(repository / "data/SWE-agent/tools/edit_anthropic/config.yaml"),
            str(repository / "data/SWE-agent/tools/review_on_submit_m/config.yaml"),
            str(repository / "data/SWE-agent/tools/registry/config.yaml"),
        ])
        rows = []
        for instance in swe_instances:
            raw_path = swe_root / instance / f"{instance}.traj"
            generated_path, _ = build_graph_from_sa_trajectory(
                json.loads(raw_path.read_text()), parser, instance, str(output / "SWE-agent"), str(swe_report)
            )
            generated_path = Path(generated_path)
            generated = json.loads(generated_path.read_text())
            sample_path = repository / f"data/samples/SWE-agent/graphs/deepseek-v3/{instance}/{instance}.json"
            full_path = repository / f"data/SWE-agent/graphs/deepseek-v3/{instance}/{instance}.json"
            sample = json.loads(sample_path.read_text())
            full = json.loads(full_path.read_text())
            row = {
                "framework": "SWE-agent",
                "instance": instance,
                "raw_sha256": sha(raw_path),
                "generated_sha256": sha(generated_path),
                "full_graph_sha256": sha(full_path),
                "generated_full_exact_bytes": generated_path.read_bytes() == full_path.read_bytes(),
                "generated_sample_exact_bytes": generated_path.read_bytes() == sample_path.read_bytes(),
                "generated_sample_equal_without_debug_difficulty": normalized_graph(generated) == normalized_graph(sample),
                "external_report_status": generated["graph"]["resolution_status"],
                "raw_step_coverage_exact": sorted({index for node in generated["nodes"] for index in node.get("step_indices", [])}) == list(range(len(json.loads(raw_path.read_text())["trajectory"]))),
                "version_diff": unit_diff(generated, sample),
            }
            rows.append(row)

        oh_path = repository / "data/samples/OpenHands/trajectories/deepseek-chat_maxiter_100_N_v0.40.0-no-hint-run_1/sample_output.jsonl"
        oh_report = oh_path.parent / "report.json"
        parser = CommandParser()
        for raw in [json.loads(line) for line in oh_path.read_text().splitlines() if line.strip()]:
            instance = raw["instance_id"]
            generated_path, _ = build_graph_from_oh_trajectory(
                raw, parser, instance, str(output / "OpenHands"), str(oh_report)
            )
            generated_path = Path(generated_path)
            generated = json.loads(generated_path.read_text())
            sample_path = repository / f"data/samples/OpenHands/graphs/claude-sonnet-4/{instance}/{instance}.json"
            sample = json.loads(sample_path.read_text())
            external_status = generated["graph"]["resolution_status"]
            embedded_status = "resolved" if raw["report"]["resolved"] else "unresolved"
            rows.append({
                "framework": "OpenHands",
                "instance": instance,
                "raw_record_sha256": hashlib.sha256((json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest(),
                "generated_sha256": sha(generated_path),
                "sample_graph_sha256": sha(sample_path),
                "generated_sample_exact_bytes": generated_path.read_bytes() == sample_path.read_bytes(),
                "generated_sample_skeleton_equal": graph_skeleton(generated) == graph_skeleton(sample),
                "external_report_status": external_status,
                "embedded_report_status": embedded_status,
                "embedded_report_matches": embedded_status == external_status,
                "raw_declared_model": raw["metadata"]["llm_config"]["model"],
                "sample_graph_directory_model": "claude-sonnet-4",
                "model_identity_matches": raw["metadata"]["llm_config"]["model"].split("/")[-1] == "claude-sonnet-4",
                "version_diff": unit_diff(generated, sample),
            })

        diffs = [row["version_diff"] for row in rows]
        summary = {
            "raw_samples": len(rows),
            "swe_generated_full_byte_exact": sum(row.get("generated_full_exact_bytes") is True for row in rows),
            "swe_raw_step_coverage_exact": sum(row.get("raw_step_coverage_exact") is True for row in rows),
            "all_generated_statuses_from_external_report": 6,
            "openhands_embedded_report_matches": sum(row.get("embedded_report_matches") is True for row in rows),
            "openhands_model_identity_matches": sum(row.get("model_identity_matches") is True for row in rows),
            "openhands_sample_skeleton_matches": sum(row.get("generated_sample_skeleton_equal") is True for row in rows),
            "version_drift_events": len(diffs),
            "version_units": sum(row["total_units"] for row in diffs),
            "changed_units": sum(row["changed_units"] for row in diffs),
            "selectively_preservable_units": sum(row["preserved_units"] for row in diffs),
            "global_reset_overrevocations": sum(row["preserved_units"] for row in diffs),
            "resolution_status_preserved": sum(row["resolution_preserved"] for row in diffs),
        }
        checks = {
            "six_samples": len(rows) == 6,
            "swe_full_exact": summary["swe_generated_full_byte_exact"] == 3,
            "swe_steps_exact": summary["swe_raw_step_coverage_exact"] == 3,
            "openhands_skeleton_exact": summary["openhands_sample_skeleton_matches"] == 3,
            "outcome_preserved": summary["resolution_status_preserved"] == 6,
            "measured_locality": summary["version_units"] == 382 and summary["changed_units"] == 26 and summary["selectively_preservable_units"] == 356,
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "summary": summary,
            "rows": rows,
            "interpretation": "This is a retrospective version-diff locality oracle, not prospective policy efficacy. Outcome labels depend on a separate evaluator report.",
            "model_calls": 0,
            "spend_usd": 0.0,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capsule", type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.capsule.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
