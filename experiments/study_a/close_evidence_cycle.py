#!/usr/bin/env python3
"""Re-run byte-level source verification and re-anchor the receipt, but only on success.

The gate detects a stale byte-level result; it cannot close the window. This closes it
as part of the change that opened it.

The safety property is that re-anchoring is not an approval step. The recorded digest of
the evidence base is updated only when verification of every receipt succeeded. A failed
or partial run leaves the old anchor in place, so the gate keeps failing as stale rather
than being silenced by the very command meant to satisfy it.

    /usr/bin/python3 experiments/study_a/close_evidence_cycle.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verify_sources import verify_archive, verify_claim_locators  # noqa: E402

CLAIMS = ROOT / "paper/sources/claim-locators.json"
RECEIPT = ROOT / "paper/experiments/source-verification-receipt.json"
ACCEPTABLE = {"VERIFIED", "DIGEST_VERIFIED_NO_MEMBERS"}


def receipt_files() -> list[pathlib.Path]:
    return sorted((ROOT / "paper/sources").glob("*source-receipts*.json"))


def run(dry_run: bool = False) -> dict:
    claim = verify_claim_locators(CLAIMS)
    archives, unacceptable = [], []
    for path in receipt_files():
        obj = json.loads(path.read_text(encoding="utf-8"))
        for record in (obj if isinstance(obj, list) else obj.get("records", [])):
            result = verify_archive(record, fetch=True)
            archives.append(result)
            if result["status"] not in ACCEPTABLE or result["mismatched"]:
                unacceptable.append({"source_id": result.get("source_id"),
                                     "status": result["status"]})
    summary = {
        "claim_level_ok": claim["ok"],
        "archives": len(archives),
        "acceptable": len(archives) - len(unacceptable),
        "unacceptable": unacceptable,
        "files_compared": sum(a["checked"] for a in archives),
        "byte_identical": sum(a["byte_identical"] for a in archives),
        "mismatched": sum(len(a["mismatched"]) for a in archives),
    }
    summary["verification_passed"] = bool(
        claim["ok"] and not unacceptable and summary["mismatched"] == 0)

    if not summary["verification_passed"]:
        summary["anchor_updated"] = False
        summary["reason"] = "verification did not pass; the anchor is left stale on purpose"
        return summary
    if dry_run:
        summary["anchor_updated"] = False
        summary["reason"] = "dry run"
        return summary

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt.setdefault("full_coverage_run", {})
    receipt["full_coverage_run"].update({
        "claim_locators_sha256": hashlib.sha256(CLAIMS.read_bytes()).hexdigest(),
        "archives": summary["archives"],
        "files_compared": summary["files_compared"],
        "byte_identical": summary["byte_identical"],
        "mismatched": summary["mismatched"],
    })
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    summary["anchor_updated"] = True
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    result = run(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["verification_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
