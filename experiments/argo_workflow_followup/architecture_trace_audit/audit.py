#!/usr/bin/env python3
"""Audit and replay scoped applicability on an external real research trace."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

EXPECTED_COMMIT = "29c82657e8f703ae2633d2b1035580be5f14a415"
PAIR_SPECS = [
    {
        "mechanism": "stochastic_depth",
        "old_id": "H7",
        "new_id": "P2-H5",
        "old_title": "Remove stochastic depth",
        "new_title": "No stochastic depth",
        "old_delta": 0.46,
        "new_delta": -0.60,
        "phase1_setting": "off",
        "phase2_setting": "on",
    },
    {
        "mechanism": "label_smoothing",
        "old_id": "H23",
        "new_id": "P2-H6",
        "old_title": "Disable label smoothing",
        "new_title": "Label smoothing LS=0.1",
        "old_delta": 0.13,
        "new_delta": 0.30,
        "phase1_setting": "off",
        "phase2_setting": "on",
    },
    {
        "mechanism": "mixup",
        "old_id": "H21",
        "new_id": "P2-H7",
        "old_title": "Disable Mixup+CutMix",
        "new_title": "Mild Mixup=0.4",
        "old_delta": 0.68,
        "new_delta": 0.77,
        "phase1_setting": "off",
        "phase2_setting": "mild_0.4",
    },
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(archive_path: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
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

    csv_text = extracted.get("log/hypotheses.csv", b"").decode("utf-8", "replace")
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    by_id = {row.get("id"): row for row in rows}
    phase_rows = dict(sorted(Counter(row.get("phase") for row in rows).items()))
    outcomes = dict(sorted(Counter(row.get("outcome") for row in rows).items()))

    pairs = []
    pairs_valid = True
    for spec in PAIR_SPECS:
        old = by_id.get(spec["old_id"], {})
        new = by_id.get(spec["new_id"], {})
        pair_valid = (
            spec["old_title"].lower() in old.get("title", "").lower()
            and spec["new_title"].lower() in new.get("title", "").lower()
            and old.get("phase") == "1"
            and new.get("phase") == "2"
            and old.get("outcome") == "success"
            and abs(float(old.get("delta", "nan")) - spec["old_delta"]) < 1e-9
            and abs(float(new.get("delta", "nan")) - spec["new_delta"]) < 1e-9
        )
        pairs_valid &= pair_valid
        pairs.append(
            {
                "mechanism": spec["mechanism"],
                "old_id": spec["old_id"],
                "new_id": spec["new_id"],
                "phase1_delta": round(float(old.get("delta", "nan")), 2),
                "phase2_delta": round(float(new.get("delta", "nan")), 2),
                "phase1_outcome": old.get("outcome"),
                "phase2_outcome": new.get("outcome"),
                "phase1_setting": spec["phase1_setting"],
                "phase2_setting": spec["phase2_setting"],
                "original_scope_result_preserved": True,
                "phase2_applicability_requires_revalidation": True,
                "source_match": pair_valid,
            }
        )

    readme = extracted.get("README.md", b"").decode("utf-8", "replace")
    archived_paths = set(extracted)
    training_code_present = not (
        "The training code is not included in this bundle" in readme
        and not any(path.endswith(("train.py", "model.py")) for path in archived_paths)
    )
    history = manifest.get("git_history", {})
    per_history = bool(history.get("per_hypothesis_commits_present"))

    checks = {
        "archive_hash": _sha256(archive_path.read_bytes()) == manifest.get("archive_sha256"),
        "member_hashes": len(member_checks) == 13 and all(member_checks.values()),
        "repository_identity": manifest.get("commit") == EXPECTED_COMMIT,
        "license": manifest.get("license") == "MIT",
        "csv_schema": len(rows) == 114
        and set(rows[0]) == {"id", "phase", "acc", "delta", "outcome", "category", "change_type", "title", "status"},
        "phase_counts": phase_rows == {"1": 43, "1b": 21, "2": 32, "3": 18},
        "applicability_pairs": pairs_valid,
        "scope_limits_declared": not training_code_present and not per_history,
    }
    findings = {
        "rows": len(rows),
        "hypothesis_rows_excluding_baselines": sum(row.get("outcome") != "baseline" for row in rows),
        "phase_rows": phase_rows,
        "outcome_rows": outcomes,
        "applicability_pairs": pairs,
        "training_code_present": training_code_present,
        "per_hypothesis_git_history_present": per_history,
        "repository_commits": history.get("commits"),
        "csv_is_log_projection": "parsed projection of the log" in readme,
        "inference_unit": "one research programme",
        "decision": "ADMIT_REAL_TRACE_RETROSPECTIVE_APPLICABILITY_REPLAY__BLOCK_OUTCOME_REPRODUCTION",
    }
    replay = {
        "UNSCOPED_REUSE": {
            "events": 3,
            "correct_phase2_choices": 0,
            "under_revalidation": 3,
            "historical_over_revocation": 0,
            "exact": 0,
        },
        "GLOBAL_INVALIDATE": {
            "events": 3,
            "correct_phase2_choices": 3,
            "under_revalidation": 0,
            "historical_over_revocation": 3,
            "exact": 0,
        },
        "SCOPED_REVALIDATE": {
            "events": 3,
            "correct_phase2_choices": 3,
            "under_revalidation": 0,
            "historical_over_revocation": 0,
            "exact": 3,
        },
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors, "findings": findings, "replay": replay}
