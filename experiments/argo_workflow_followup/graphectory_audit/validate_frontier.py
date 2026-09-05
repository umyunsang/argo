#!/usr/bin/env python3
"""Re-derive and validate the Graphectory frontier receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit import audit


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(receipt_path: Path, root: Path) -> dict:
    root = Path(root)
    receipt = json.loads(Path(receipt_path).read_text())
    errors: list[str] = []

    def bound(section: dict, path_key: str = "path", sha_key: str = "sha256") -> Path | None:
        path = root / section[path_key]
        if not path.is_file() or sha(path) != section[sha_key]:
            return None
        return path

    capsule = bound(receipt.get("capsule", {}))
    manifest = bound(receipt.get("capsule", {}), "manifest", "manifest_sha256")
    if capsule is None:
        errors.append("CAPSULE_IDENTITY")
    if manifest is None:
        errors.append("MANIFEST_IDENTITY")
    literature = receipt.get("literature", {})
    literature_path = root / literature.get("receipt", "")
    if not literature_path.is_file() or sha(literature_path) != literature.get("receipt_sha256"):
        errors.append("LITERATURE_IDENTITY")
    builder_ref = receipt.get("builder_replay", {})
    builder_path = root / builder_ref.get("receipt", "")
    builder = None
    if not builder_path.is_file() or sha(builder_path) != builder_ref.get("receipt_sha256"):
        errors.append("BUILDER_RECEIPT_IDENTITY")
    else:
        builder = json.loads(builder_path.read_text())
    audit_script = root / receipt.get("audit", {}).get("script", "")
    audit_test = root / receipt.get("audit", {}).get("test", "")
    if not audit_script.is_file() or sha(audit_script) != receipt["audit"].get("script_sha256"):
        errors.append("AUDIT_SCRIPT_IDENTITY")
    if not audit_test.is_file() or sha(audit_test) != receipt["audit"].get("test_sha256"):
        errors.append("AUDIT_TEST_IDENTITY")
    fresh = audit(capsule, manifest) if capsule and manifest else None
    if fresh != receipt.get("audit", {}).get("result"):
        errors.append("AUDIT_RESULT")
    expected_audit = {
        "tracked_graph_paths": 3972,
        "metrics_rows": 3972,
        "repository_graph_count_difference": -1,
        "count_difference_collection": "SWE-agent/deepseek-v3",
        "sample_external_report_matches": "6/6",
        "openhands_embedded_report_matches": "1/3",
        "openhands_raw_model_vs_graph_directory_mismatch": "3/3",
        "selected_graphs_with_raw_thought_observation_fields": 0,
        "zenodo_archive_downloaded": False,
    }
    findings = fresh.get("findings", {}) if fresh else {}
    for key, value in expected_audit.items():
        if findings.get(key) != value:
            errors.append(f"AUDIT_FACT:{key}")
    expected_builder = {
        "raw_samples": 6,
        "swe_generated_full_byte_exact": 3,
        "openhands_embedded_report_matches": 1,
        "openhands_model_identity_matches": 0,
        "version_units": 382,
        "changed_units": 26,
        "selectively_preservable_units": 356,
        "global_reset_overrevocations": 356,
        "resolution_status_preserved": 6,
    }
    measured = builder_ref.get("measured", {})
    if builder is None or builder.get("measured") != measured:
        errors.append("BUILDER_RESULT_BINDING")
    for key, value in expected_builder.items():
        if measured.get(key) != value:
            errors.append(f"BUILDER_FACT:{key}")
    if builder is not None:
        if builder.get("inference_unit") != "one external programme" or builder.get("independent_n") != 1:
            errors.append("BUILDER_INFERENCE_UNIT")
        runner = root / builder.get("runner", "")
        if not runner.is_file() or sha(runner) != builder.get("runner_sha256"):
            errors.append("REPLAY_RUNNER_IDENTITY")
        if builder.get("capsule_sha256") != receipt.get("capsule", {}).get("sha256"):
            errors.append("REPLAY_CAPSULE_BINDING")
        if builder.get("repaired", {}).get("result", {}).get("summary") != measured:
            errors.append("REPLAY_RESULT")
        if builder.get("failing_first", {}).get("summary", {}).get("swe_generated_full_byte_exact") != 0:
            errors.append("FAILING_FIRST")
    required_limits = {
        "research-state decision graph",
        "correction or reopening decision oracle",
        "claim that static graph JSON contains complete thought/observation text",
        "OpenHands sample/full model identity",
    }
    if not required_limits.issubset(set(receipt.get("not_admitted", []))):
        errors.append("LIMITS")
    if receipt.get("inference_unit") != "one external programme" or receipt.get("independent_n") != 1:
        errors.append("INFERENCE_UNIT")
    if receipt.get("source", {}).get("raw_archive_downloaded") is not False:
        errors.append("RAW_ARCHIVE_SCOPE")
    if receipt.get("model_calls") != 0 or receipt.get("spend_usd") != 0.0:
        errors.append("EXECUTION_SCOPE")
    return {
        "passed": not errors,
        "errors": errors,
        "fresh_audit_sha256": hashlib.sha256((json.dumps(fresh, ensure_ascii=False, sort_keys=True) + "\n").encode()).hexdigest() if fresh else None,
        "measured": expected_builder,
        "decision": receipt.get("decision"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = validate(args.receipt, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
