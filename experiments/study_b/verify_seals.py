#!/usr/bin/env python3
"""Re-derive every Study B seal from current bytes and report mismatches."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def digest_check(check_id: str, root: Path, relpath: str, registered: str,
                 algorithm: str = "sha256") -> dict:
    path = root / relpath
    actual = None
    if path.is_file():
        actual = sha256(path) if algorithm == "sha256" else blob_sha1(path)
    matched = actual == registered
    reason = "matched"
    if not matched:
        reason = f"{relpath}: registered={registered} actual={actual}"
    return {
        "id": check_id,
        "path": relpath,
        "algorithm": algorithm,
        "registered": registered,
        "actual": actual,
        "matched": matched,
        "reason": reason,
    }


def verify(root: Path, protocol_path: Path) -> dict:
    cfg = json.loads(protocol_path.read_text(encoding="utf-8"))
    study = cfg["study_b"]
    checks = [
        digest_check("preregistration_v4", root, study["preregistration_path"],
                     study["preregistration_sha256"]),
        digest_check("analysis_spec_v4a", root, study["analysis_spec_path"],
                     study["analysis_spec_sha256"]),
        digest_check("analysis_script", root, study["analysis_script_path"],
                     study["analysis_script_sha256"]),
        digest_check("t1prime_addendum", root, study["t1prime_addendum_path"],
                     study["t1prime_addendum_sha256"]),
    ]
    arm_members = []
    for relpath, registered in sorted(study["arm_blob_hashes"].items()):
        full_rel = f"experiments/study_b/{relpath}"
        arm_members.append(digest_check(
            f"arm_blob:{relpath}", root, full_rel, registered, "git_blob_sha1"))
    arm_matched = all(x["matched"] for x in arm_members)
    arm_reason = "matched" if arm_matched else "; ".join(
        x["reason"] for x in arm_members if not x["matched"])
    checks.append({
        "id": "arm_blobs_16",
        "algorithm": "git_blob_sha1",
        "member_count": len(arm_members),
        "members": arm_members,
        "matched": arm_matched,
        "reason": arm_reason,
    })
    return {
        "schema_version": "study-b-seal-verification/v1",
        "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "protocol_path": str(protocol_path.relative_to(root)),
        "checks": checks,
        "passed": all(x["matched"] for x in checks),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--protocol", default=".orx/paper_protocol.json")
    parser.add_argument("--out")
    args = parser.parse_args()
    root = args.root.resolve()
    result = verify(root, root / args.protocol)
    if args.out:
        out = root / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
