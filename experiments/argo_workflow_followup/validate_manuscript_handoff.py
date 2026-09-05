#!/usr/bin/env python3
"""Validate the post-C64 workflow-frontier manuscript handoff."""
from __future__ import annotations

import hashlib
from pathlib import Path

REQUIRED_FORBIDDEN = {
    "independent real-world graph validation",
    "decision sufficiency or fresh-context handoff proven",
    "DiscoveryWorld benchmark score or pass",
    "ten independent tasks or n=10",
    "OS isolation certified",
    "typed policy causal efficacy",
}
EXPECTED_CLAIM_STATE = {
    "protocol_targeting": "mechanically exact within synthetic and same-project projected semantics",
    "historical_pipeline": "one semantic falsifier PASS",
    "OS_isolation": "FIXED_UNVALIDATED_RETRY_CONSUMED",
    "external_task_pack": "SCHEMA_PASS_NOT_GENERATED_NOT_ADMITTED",
    "confirmatory_efficacy": "NOT_ESTABLISHED",
    "fresh_context_behavior": "NOT_RUN",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matches(repo_root: Path, relative: str, digest: str) -> bool:
    path = repo_root / relative
    return path.is_file() and _sha256(path) == digest


def validate(handoff: dict, repo_root: Path) -> dict:
    checks = {}
    checks["SCHEMA"] = (
        handoff.get("schema_version") == "argo-manuscript-update-handoff/v2"
        and handoff.get("status") == "READY_FOR_MANUSCRIPT_OWNER_REVIEW_NOT_APPLIED"
    )
    ownership = handoff.get("ownership_boundary", {})
    qmd = repo_root / str(ownership.get("canonical_qmd", ""))
    checks["QMD_IDENTITY"] = (
        qmd.is_file()
        and _sha256(qmd) == ownership.get("observed_current_sha256")
        and ownership.get("edited_by_this_research_lane") is False
        and ownership.get("dated_exports_edited") is False
    )
    authority = handoff.get("authority", {})
    checks["AUTHORITY_HASH"] = (
        _matches(
            repo_root,
            authority.get("update_contract", ""),
            authority.get("update_contract_sha256", ""),
        )
        and _matches(
            repo_root,
            authority.get("prior_handoff", ""),
            authority.get("prior_handoff_sha256", ""),
        )
    )

    evidence_ok = True
    for update in handoff.get("evidence_updates", []):
        pairs = []
        if "receipt" in update:
            pairs.append((update["receipt"], update.get("sha256")))
        if "source_audit" in update:
            pairs.append((update["source_audit"], update.get("source_audit_sha256")))
        if "pack_validation" in update:
            pairs.append((update["pack_validation"], update.get("pack_validation_sha256")))
        evidence_ok &= bool(pairs) and all(
            _matches(repo_root, path, digest or "") for path, digest in pairs
        )
    checks["EVIDENCE_HASH"] = evidence_ok and len(handoff.get("evidence_updates", [])) == 4
    checks["MANDATORY_LIMITS"] = all(
        bool(update.get("allowed_claim")) and bool(update.get("mandatory_limit"))
        for update in handoff.get("evidence_updates", [])
    )

    measurement = handoff.get("measurement_repair", {})
    checks["MEASUREMENT_CONTRACT"] = _matches(
        repo_root, measurement.get("contract", ""), measurement.get("contract_sha256", "")
    )
    checks["CLAIM_STATE"] = handoff.get("current_claim_state") == EXPECTED_CLAIM_STATE
    checks["FORBIDDEN_BOUNDARY"] = REQUIRED_FORBIDDEN <= set(
        handoff.get("forbidden_interpretations", [])
    )
    checks["OWNER_PROCEDURE"] = (
        len(handoff.get("affected_manuscript_surfaces", [])) >= 5
        and len(handoff.get("owner_checks_before_citation", [])) >= 4
        and handoff.get("model_calls") == 0
        and handoff.get("spend_usd") == 0.0
    )
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors}
