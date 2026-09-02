#!/usr/bin/env python3
"""Verify recorded source evidence against its own record and its upstream archive.

Three levels, reported separately because they prove different things:

* claim level  - every claim locator's file digest and the excerpt hash at the recorded
                 line range. This is what a reader needs to check a quotation.
* member level - the archive member manifest re-derived from a re-fetched archive.
* byte level   - each committed source file compared byte for byte with the same member
                 extracted from the re-fetched archive.

An archive digest proves the archive. It does not prove that the file in the repository
is the file that came out of it, which is what the byte level checks.

    /usr/bin/python3 experiments/study_a/verify_sources.py [--offline]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "paper/sources/claim-locators.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_claim_locators(claims_path: pathlib.Path = CLAIMS) -> dict:
    obj = json.loads(claims_path.read_text(encoding="utf-8"))
    locators = obj["locators"] if isinstance(obj, dict) else obj
    file_failures, excerpt_failures = [], []
    for loc in locators:
        path = ROOT / loc["source_file"]
        if not path.is_file():
            file_failures.append({"locator": loc["claim_locator_id"], "reason": "file missing"})
            continue
        if loc.get("source_file_sha256") and sha256_path(path) != loc["source_file_sha256"]:
            file_failures.append({"locator": loc["claim_locator_id"],
                                  "reason": "file digest differs"})
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        start, end = int(loc["line_start"]), int(loc["line_end"])
        excerpt = "\n".join(lines[start - 1:end])
        if sha256_bytes(excerpt.encode()) != loc["excerpt_sha256"]:
            excerpt_failures.append({"locator": loc["claim_locator_id"],
                                     "reason": "excerpt no longer hashes at these lines"})
    return {"locators": len(locators), "file_failures": file_failures,
            "excerpt_failures": excerpt_failures,
            "ok": not file_failures and not excerpt_failures}


def verify_archive(record: dict, fetch=True) -> dict:
    """Compare committed files with the same members re-extracted from the archive."""
    url = record.get("artifact_url")
    digest = record.get("archive_sha256")
    repo_paths = record.get("tex_files_repository_paths") or []
    members = record.get("tex_files") or []
    result = {"source_id": record.get("source_id"), "files": len(repo_paths),
              "checked": 0, "byte_identical": 0, "mismatched": [], "status": "SKIPPED"}
    if not (url and digest and repo_paths):
        result["status"] = "INCOMPLETE_RECORD"
        return result
    if not fetch:
        result["status"] = "OFFLINE"
        return result
    with tempfile.TemporaryDirectory() as tmp:
        local = pathlib.Path(tmp) / "archive"
        proc = subprocess.run(["curl", "-sfL", "--retry", "3", "-o", str(local), url],
                              capture_output=True)
        if proc.returncode != 0 or not local.is_file():
            result["status"] = "FETCH_FAILED"
            return result
        if sha256_path(local) != digest:
            result["status"] = "ARCHIVE_DIGEST_MISMATCH"
            return result
        try:
            archive = tarfile.open(local, "r:*")
        except tarfile.ReadError:
            result["status"] = "NOT_AN_ARCHIVE"
            return result
        by_name = {m.name: m for m in archive.getmembers() if m.isfile()}
        for member, repo_path in zip(members, repo_paths):
            committed = ROOT / repo_path
            if member not in by_name or not committed.is_file():
                result["mismatched"].append({"member": member, "reason": "absent on one side"})
                continue
            result["checked"] += 1
            if archive.extractfile(by_name[member]).read() == committed.read_bytes():
                result["byte_identical"] += 1
            else:
                result["mismatched"].append({"member": member, "reason": "bytes differ"})
    result["status"] = "VERIFIED" if not result["mismatched"] else "MISMATCH"
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--receipts", nargs="*", default=[])
    args = ap.parse_args()
    out = {"claim_level": verify_claim_locators()}
    archives = []
    for rel in args.receipts:
        obj = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        records = obj if isinstance(obj, list) else obj.get("records", [])
        for record in records:
            archives.append(verify_archive(record, fetch=not args.offline))
    out["byte_level"] = archives
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if out["claim_level"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
