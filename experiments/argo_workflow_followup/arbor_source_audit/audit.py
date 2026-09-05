#!/usr/bin/env python3
"""Audit the pinned Arbor code and bundled research-state artifacts."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

EXPECTED_COMMIT = "2f4e65410a5c21c9e55835a9a0d77ead21a64ffa"
EXPECTED_TREE = "967fd922021785d4ce192c66ee7aea42530c39ec"
TYPED_FIELDS = {"evidence_id", "version", "validity", "applicability", "dependency_edges"}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _node_schema(source: str) -> tuple[list[str], list[str]]:
    tree = ast.parse(source)
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == "Node")
    fields = []
    mutable = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            if not item.target.id.isupper():
                fields.append(item.target.id)
            elif (
                item.target.id == "MUTABLE_FIELDS"
                and isinstance(item.value, ast.Call)
                and item.value.args
            ):
                mutable = sorted(ast.literal_eval(item.value.args[0]))
        if isinstance(item, ast.Assign):
            targets = [target.id for target in item.targets if isinstance(target, ast.Name)]
            if "MUTABLE_FIELDS" in targets and isinstance(item.value, ast.Call) and item.value.args:
                mutable = sorted(ast.literal_eval(item.value.args[0]))
    return sorted(fields), mutable


def audit(archive_path: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    archive_bytes = archive_path.read_bytes()
    archive_hash_ok = _sha256(archive_bytes) == manifest.get("archive_sha256")
    member_checks = {}
    extracted = {}
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for record in manifest.get("members", []):
                try:
                    data = archive.read(record["path"])
                    extracted[record["path"]] = data
                    member_checks[record["path"]] = (
                        len(data) == record.get("bytes")
                        and _sha256(data) == record.get("sha256")
                    )
                except (KeyError, OSError, zipfile.BadZipFile):
                    member_checks[record.get("path", "<missing>")] = False
    except zipfile.BadZipFile:
        member_checks["<archive>"] = False

    demo_script = extracted.get("scripts/generate_demo_recording.py", b"").decode("utf-8", "replace")
    demo_tree = json.loads(extracted.get("src/cli/assets/demo_session/tree.json", b"{}"))
    demo_events = [
        line for line in extracted.get("src/cli/assets/demo_session/events.jsonl", b"").decode().splitlines()
        if line.strip()
    ]
    browse = extracted.get(
        "project_page/public/assets/demo/browsecomp/idea_tree.html", b""
    ).decode("utf-8", "replace")
    node_matches = re.findall(
        r"^\s*'([^']+)':\s*\{\s*\n\s*c:\[[^]]*],\s*s:'([^']+)'",
        browse,
        flags=re.MULTILINE,
    )
    status_counts = Counter(status for node_id, status in node_matches if node_id != "ROOT")
    narrative_match = re.search(r"(\d+) done · (\d+) merged · (\d+) pruned", browse)
    narrative_counts = (
        {
            "done": int(narrative_match.group(1)),
            "merged": int(narrative_match.group(2)),
            "pruned": int(narrative_match.group(3)),
        }
        if narrative_match
        else {}
    )
    observed_counts = dict(sorted(status_counts.items()))
    raw_reference = "docs/total_test/research_log/v3-withskill_20cycles"
    archived_paths = {record.get("path") for record in manifest.get("members", [])}
    raw_lineage_absent = raw_reference in browse and not any(
        str(path).startswith(raw_reference) for path in archived_paths
    )

    idea_source = extracted.get("src/coordinator/idea_tree.py", b"").decode("utf-8", "replace")
    node_fields, mutable_fields = _node_schema(idea_source)
    missing_typed = sorted(TYPED_FIELDS - set(node_fields))
    demo_synthetic = all(
        phrase in demo_script
        for phrase in ("illustrative sample", "scores are hand-authored", "synthetic numbers")
    )
    checks = {
        "archive_hash": archive_hash_ok,
        "member_hashes": len(member_checks) == 10 and all(member_checks.values()),
        "repository_identity": manifest.get("commit") == EXPECTED_COMMIT
        and manifest.get("tree") == EXPECTED_TREE,
        "license": manifest.get("license") == "Apache-2.0",
        "demo_disclosure_parsed": demo_synthetic,
        "browsecomp_tree_parsed": len(node_matches) == 10 and bool(narrative_counts),
        "node_schema_parsed": "hypothesis" in node_fields and "result" in node_fields,
    }
    independent = not demo_synthetic and not raw_lineage_absent and observed_counts == narrative_counts
    findings = {
        "bundled_demo_explicitly_synthetic": demo_synthetic,
        "bundled_demo_nodes": len(demo_tree.get("nodes", {})),
        "bundled_demo_events": len(demo_events),
        "browsecomp_embedded_nodes": len(node_matches),
        "browsecomp_embedded_nonroot_status_counts": observed_counts,
        "browsecomp_narrative_status_counts": narrative_counts,
        "browsecomp_status_mismatch": observed_counts != narrative_counts,
        "browsecomp_raw_reference": raw_reference,
        "browsecomp_raw_lineage_absent": raw_lineage_absent,
        "node_fields": node_fields,
        "mutable_fields": mutable_fields,
        "missing_typed_fields": missing_typed,
        "recursive_descendant_prune": (
            "for child_id in n.children_ids:" in idea_source
            and "_prune(child_id)" in idea_source
        ),
        "answer_bearing_fields_mutable": all(
            field in mutable_fields
            for field in ("hypothesis", "insight", "result", "score", "status")
        ),
        "independent_real_graph_admissible": independent,
        "decision": "VALID_STRONG_COMPARATOR_CODE_SOURCE__BLOCKED_INDEPENDENT_REAL_GRAPH",
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors, "findings": findings}
