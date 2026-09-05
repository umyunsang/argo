#!/usr/bin/env python3
"""Audit a byte-capsuled Graphectory repository slice without model execution."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            keys.update(all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(all_keys(child))
    return keys


def report_status(report: dict, instance: str) -> str:
    if instance in report.get("resolved_ids", []):
        return "resolved"
    if instance in report.get("unresolved_ids", []):
        return "unresolved"
    return "unsubmitted"


def parse_tree(text: str) -> dict[str, dict]:
    records = {}
    for line in text.splitlines():
        left, path = line.split("\t", 1)
        mode, kind, oid, size = left.split()
        records[path] = {"mode": mode, "kind": kind, "oid": oid, "size": int(size)}
    return records


def audit(capsule_path: Path, manifest_path: Path) -> dict:
    capsule_path = Path(capsule_path)
    manifest_path = Path(manifest_path)
    errors: list[str] = []
    try:
        external_manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(external_manifest_bytes)
        with zipfile.ZipFile(capsule_path) as archive:
            bad_member = archive.testzip()
            names = archive.namelist()
            unsafe = [name for name in names if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts]
            members = {name: archive.read(name) for name in names}
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile, RuntimeError) as exc:
        return {"passed": False, "checks": {"archive_readable": False}, "findings": {}, "errors": [f"ARCHIVE:{type(exc).__name__}"]}

    expected_records = {row["path"]: row for row in manifest.get("members", [])}
    checks = {
        "archive_crc": bad_member is None,
        "safe_paths": not unsafe,
        "member_set": set(members) == set(expected_records) | {"manifest.json"},
        "manifest_identity": members.get("manifest.json") == external_manifest_bytes,
        "member_identity": all(
            path in members and len(members[path]) == row["size"] and digest(members[path]) == row["sha256"]
            for path, row in expected_records.items()
        ),
        "lfs_content_identity": all(
            "lfs_oid" not in row or (path in members and digest(members[path]) == row["lfs_oid"] and len(members[path]) == row["lfs_size"])
            for path, row in expected_records.items()
        ),
    }
    if not all(checks.values()):
        errors.extend(name for name, passed in checks.items() if not passed)

    try:
        tree = parse_tree(members["metadata/git-ls-tree.txt"].decode())
        graph_pattern = re.compile(r"^data/(OpenHands|SWE-agent)/graphs/([^/]+)/([^/]+)/\3\.json$")
        tracked_graphs = {path for path in tree if graph_pattern.match(path)}
        metric_members = sorted(
            name for name in members
            if re.match(r"^repository/data/(OpenHands|SWE-agent)/analysis/[^/]+/trajectory_metrics\.csv$", name)
        )
        metric_status: dict[str, str] = {}
        collection_counts: dict[str, dict] = {}
        for member in metric_members:
            match = re.match(r"^repository/data/(OpenHands|SWE-agent)/analysis/([^/]+)/trajectory_metrics\.csv$", member)
            assert match
            agent, model = match.groups()
            rows = list(csv.DictReader(io.StringIO(members[member].decode())))
            counts = Counter(row["resolution"] for row in rows)
            collection_counts[f"{agent}/{model}"] = {"rows": len(rows), **dict(sorted(counts.items()))}
            for row in rows:
                key = f"data/{agent}/graphs/{model}/{row['instance']}/{row['instance']}.json"
                if key in metric_status:
                    errors.append(f"DUPLICATE_METRIC:{key}")
                metric_status[key] = row["resolution"]
        graph_metric_identity = tracked_graphs == set(metric_status)
        selected_members = sorted(name for name in members if graph_pattern.match(name.removeprefix("repository/")))
        selected_matches = 0
        selected_with_raw = 0
        for member in selected_members:
            graph = json.loads(members[member])
            rel = member.removeprefix("repository/")
            path_match = graph_pattern.match(rel)
            assert path_match
            instance = path_match.group(3)
            if graph["graph"]["instance_name"] == instance and graph["graph"]["resolution_status"] == metric_status[rel]:
                selected_matches += 1
            if {"thought", "observation", "response"} & all_keys(graph):
                selected_with_raw += 1

        paper = members["literature/2608.17195.txt"].decode()
        paper_count_match = re.search(r"corpus contains ([0-9,]+) trajectories", paper)
        paper_count = int(paper_count_match.group(1).replace(",", "")) if paper_count_match else None
        paper_sa_match = re.search(r"SA DeepSeek-V3\s+([0-9]+)", paper)
        paper_sa_count = int(paper_sa_match.group(1)) if paper_sa_match else None
        repo_sa_count = collection_counts["SWE-agent/deepseek-v3"]["rows"]
        difference_collection = "SWE-agent/deepseek-v3" if paper_sa_count != repo_sa_count else None

        swe_report = json.loads(members["repository/data/samples/SWE-agent/reports/deepseek-chat.json"])
        swe_instances = ["astropy__astropy-13453", "django__django-10973", "sympy__sympy-19783"]
        swe_matches = 0
        swe_raw_without_resolution = 0
        for instance in swe_instances:
            graph_member = f"repository/data/samples/SWE-agent/graphs/deepseek-v3/{instance}/{instance}.json"
            raw_member = next(name for name in members if name.endswith(f"/{instance}/{instance}.traj"))
            graph = json.loads(members[graph_member])
            raw = json.loads(members[raw_member])
            swe_matches += graph["graph"]["resolution_status"] == report_status(swe_report, instance)
            swe_raw_without_resolution += "resolved" not in all_keys(raw)

        oh_raw_member = "repository/data/samples/OpenHands/trajectories/deepseek-chat_maxiter_100_N_v0.40.0-no-hint-run_1/sample_output.jsonl"
        oh_report_member = "repository/data/samples/OpenHands/trajectories/deepseek-chat_maxiter_100_N_v0.40.0-no-hint-run_1/report.json"
        oh_rows = [json.loads(line) for line in members[oh_raw_member].decode().splitlines() if line.strip()]
        oh_report = json.loads(members[oh_report_member])
        oh_external_matches = 0
        oh_embedded_matches = 0
        oh_model_mismatches = 0
        for row in oh_rows:
            instance = row["instance_id"]
            graph_member = f"repository/data/samples/OpenHands/graphs/claude-sonnet-4/{instance}/{instance}.json"
            graph_status = json.loads(members[graph_member])["graph"]["resolution_status"]
            oh_external_matches += graph_status == report_status(oh_report, instance)
            embedded = "resolved" if row["report"]["resolved"] else "unresolved"
            oh_embedded_matches += graph_status == embedded
            raw_model = row["metadata"]["llm_config"]["model"].split("/")[-1]
            oh_model_mismatches += raw_model != "claude-sonnet-4"

        builder = members["repository/graph_construction/buildGraph.py"].decode()
        builder_dep = all(token in builder for token in ["determine_resolution_status", "eval_report_path", "resolved_ids", "unresolved_ids"])
        zenodo = json.loads(members["zenodo/record-17364210.json"])
        zfile = zenodo["files"][0]
        resolution_counts = Counter(metric_status.values())
        findings = {
            "repository_commit": manifest["repository"]["commit"],
            "repository_tree": manifest["repository"]["tree"],
            "tracked_files": len(tree),
            "tracked_lfs_files": len(json.loads(members["metadata/git-lfs-files.json"])["files"]),
            "tracked_graph_paths": len(tracked_graphs),
            "metrics_files": len(metric_members),
            "metrics_rows": len(metric_status),
            "graph_metric_path_identity": graph_metric_identity,
            "collection_counts": collection_counts,
            "resolution_counts": dict(sorted(resolution_counts.items())),
            "selected_graphs": len(selected_members),
            "selected_graph_metric_status_matches": selected_matches,
            "selected_graphs_with_raw_thought_observation_fields": selected_with_raw,
            "paper_nonempty_trajectories": paper_count,
            "repository_graph_count_difference": len(tracked_graphs) - paper_count if paper_count is not None else None,
            "paper_swe_agent_deepseek_v3_count": paper_sa_count,
            "repository_swe_agent_deepseek_v3_count": repo_sa_count,
            "count_difference_collection": difference_collection,
            "sample_external_report_matches": f"{swe_matches + oh_external_matches}/6",
            "swe_raw_records_without_resolution_field": f"{swe_raw_without_resolution}/3",
            "openhands_embedded_report_matches": f"{oh_embedded_matches}/3",
            "openhands_raw_model_vs_graph_directory_mismatch": f"{oh_model_mismatches}/3",
            "builder_external_report_dependency": builder_dep,
            "zenodo_archive_size": zfile["size"],
            "zenodo_archive_recorded_checksum": zfile["checksum"],
            "zenodo_archive_downloaded": manifest["zenodo"]["downloaded"],
        }
        checks.update({
            "repo_identity": findings["repository_commit"] == "052079f71239f9f68c9af9849fef219c052c9dda" and findings["repository_tree"] == "294de524fdeedb39d6a18b6a60c212d4f401330a",
            "tracked_inventory": findings["tracked_files"] == 4123 and findings["tracked_lfs_files"] == 4006,
            "graph_metric_identity": graph_metric_identity and len(tracked_graphs) == len(metric_status),
            "selected_status_identity": selected_matches == len(selected_members),
            "sample_external_report_identity": swe_matches + oh_external_matches == 6,
            "builder_report_dependency": builder_dep,
            "paper_count_located": paper_count is not None and paper_sa_count is not None,
            "zenodo_metadata": zfile["key"] == "raw_trajectories.tar.gz" and zfile["size"] == manifest["zenodo"]["file_size"],
        })
        errors.extend(name for name, passed in checks.items() if not passed and name not in errors)
        return {"passed": not errors, "checks": checks, "findings": findings, "errors": errors}
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"AUDIT:{type(exc).__name__}")
        return {"passed": False, "checks": checks, "findings": {}, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capsule", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.capsule, args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
