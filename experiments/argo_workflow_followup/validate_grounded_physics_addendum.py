#!/usr/bin/env python3
"""Validate the grounded-physics trace manuscript addendum."""
from __future__ import annotations

import hashlib
from pathlib import Path


def _matches(root: Path, relative: str, digest: str) -> bool:
    path = root / relative
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest


def validate(addendum: dict, repo_root: Path) -> dict:
    checks = {}
    checks["SCHEMA"] = addendum.get("schema_version") == "argo-manuscript-update-addendum/v1" and addendum.get("status") == "READY_FOR_OWNER_REVIEW_NOT_APPLIED"
    checks["PARENT_HASH"] = _matches(repo_root, addendum.get("parent_handoff", ""), addendum.get("parent_handoff_sha256", ""))
    ownership = addendum.get("ownership_boundary", {})
    checks["QMD_IDENTITY"] = _matches(repo_root, ownership.get("qmd", ""), ownership.get("observed_sha256", "")) and ownership.get("edited") is False and ownership.get("dated_exports_edited") is False
    evidence = addendum.get("new_evidence", {})
    checks["EVIDENCE_HASH"] = all(
        _matches(repo_root, evidence.get(path_key, ""), evidence.get(hash_key, ""))
        for path_key, hash_key in (
            ("literature_receipt", "literature_receipt_sha256"),
            ("source_audit", "source_audit_sha256"),
            ("frontier_receipt", "frontier_receipt_sha256"),
        )
    )
    limits = " ".join(addendum.get("mandatory_limits", [])).lower()
    checks["SCOPE_LIMITS"] = all(phrase in limits for phrase in (
        "0/15 direct source-path closure",
        "structural reconstructability result",
        "private transcripts",
        "separate objects",
    ))
    checks["FORBIDDEN_BOUNDARY"] = {
        "raw decision graph available", "15 false event summaries",
        "aggregate replay proves decision sufficiency", "scientific truth verified",
        "independent n=15", "typed policy or ARGO efficacy", "permission to execute",
    } <= set(addendum.get("forbidden_interpretations", []))
    checks["OWNER_GATE"] = len(addendum.get("citation_gate", [])) >= 4 and len(addendum.get("affected_surfaces", [])) >= 4 and addendum.get("model_calls") == 0 and addendum.get("spend_usd") == 0.0
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors}
