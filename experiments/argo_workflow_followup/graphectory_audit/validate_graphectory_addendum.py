#!/usr/bin/env python3
"""Validate the owner-only Graphectory manuscript addendum."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path, root: Path) -> dict:
    root = Path(root)
    obj = json.loads(Path(path).read_text())
    errors: list[str] = []
    if obj.get("schema_version") != "argo-manuscript-update-addendum/v1" or obj.get("status") != "READY_FOR_OWNER_REVIEW_NOT_APPLIED":
        errors.append("SCHEMA_OR_STATUS")
    parent = root / obj.get("parent_handoff", "")
    if not parent.is_file() or sha(parent) != obj.get("parent_handoff_sha256"):
        errors.append("PARENT_IDENTITY")
    boundary = obj.get("ownership_boundary", {})
    if boundary.get("qmd") != "paper/manuscript/thesis-ko.qmd" or boundary.get("edited") is not False or boundary.get("dated_exports_edited") is not False:
        errors.append("OWNERSHIP_BOUNDARY")
    if not re.fullmatch(r"[0-9a-f]{64}", boundary.get("observed_sha256", "")):
        errors.append("OBSERVED_QMD_HASH")
    evidence = obj.get("new_evidence", {})
    for path_key, hash_key in [
        ("literature_receipt", "literature_receipt_sha256"),
        ("source_audit", "source_audit_sha256"),
        ("builder_replay", "builder_replay_sha256"),
        ("category_bridge", "category_bridge_sha256"),
        ("immutable_validation", "immutable_validation_sha256"),
    ]:
        source = root / evidence.get(path_key, "")
        if not source.is_file() or sha(source) != evidence.get(hash_key):
            errors.append(f"EVIDENCE_IDENTITY:{path_key}")
    if evidence.get("repository_commit") != "052079f71239f9f68c9af9849fef219c052c9dda" or evidence.get("repository_tree") != "294de524fdeedb39d6a18b6a60c212d4f401330a":
        errors.append("REPOSITORY_IDENTITY")
    required_limits = {
        "This is one external software-agent programme, not 3,972 or six independent research programmes.",
        "The six-row comparison is a retrospective version-diff locality oracle, not a prospective typed-policy or ARGO efficacy estimate.",
        "The 1,446,491,536-byte Zenodo raw archive was identified but not downloaded; full raw-corpus integrity is unverified.",
        "Static selected graph JSON contains command and summary fields but no complete raw thought/observation/response fields.",
        "OpenHands raw model identity versus sample graph directory is 0/3; do not make same-model or same-recipe sample/full comparisons.",
        "Graphectory supplies recorded terminal status but no correction/reopening choice oracle, so decision correctness remains open.",
    }
    if not required_limits.issubset(set(obj.get("mandatory_limits", []))):
        errors.append("MANDATORY_LIMITS")
    required_forbidden = {
        "n=3972 independent programmes",
        "n=6 independent experiments",
        "paper count exactly reproduced",
        "full raw archive verified",
        "static graphs contain full raw thoughts and observations",
        "OpenHands same-model sample/full comparison",
        "correction decision correctness measured",
        "typed policy or ARGO efficacy",
        "permission to execute Docker, tasks, models, or OpenResearch",
    }
    if not required_forbidden.issubset(set(obj.get("forbidden_interpretations", []))):
        errors.append("FORBIDDEN_INTERPRETATIONS")
    claims = " ".join(obj.get("allowed_claims", []))
    for token in ["3,972", "3,973", "498", "499", "6/6", "1/3", "26/382", "356"]:
        if token not in claims:
            errors.append(f"ALLOWED_CLAIM:{token}")
    if obj.get("model_calls") != 0 or obj.get("spend_usd") != 0.0:
        errors.append("EXECUTION_SCOPE")
    return {"passed": not errors, "errors": errors, "addendum_sha256": sha(Path(path)), "status": obj.get("status")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addendum", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = validate(args.addendum, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
