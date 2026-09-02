#!/usr/bin/env python3
"""Failing-first fixtures for closing the evidence cycle.

The property that matters is negative: a failed verification must NOT update the anchor.
A command that re-anchors regardless would silence the very gate it exists to satisfy.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import close_evidence_cycle as cec  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def main() -> int:
    original_claims, original_archive, original_files = (
        cec.verify_claim_locators, cec.verify_archive, cec.receipt_files)
    try:
        cec.receipt_files = lambda: []

        cec.verify_claim_locators = lambda path: {"ok": False, "file_failures": ["L"],
                                                  "excerpt_failures": []}
        r = cec.run(dry_run=False)
        check("a failed claim level does not update the anchor", r["anchor_updated"] is False)
        check("the failure is stated as deliberate", "on purpose" in r.get("reason", ""))
        check("verification is reported as not passed", r["verification_passed"] is False)

        cec.verify_claim_locators = lambda path: {"ok": True, "file_failures": [],
                                                  "excerpt_failures": []}
        r2 = cec.run(dry_run=True)
        check("a dry run never updates the anchor", r2["anchor_updated"] is False)
        check("a dry run still reports the verification result",
              r2["verification_passed"] is True)

        cec.receipt_files = lambda: [pathlib.Path("dummy")]
        original_read = pathlib.Path.read_text

        def fake_read(self, *a, **k):
            if self.name == "dummy":
                return json.dumps([{"source_id": "S"}])
            return original_read(self, *a, **k)

        pathlib.Path.read_text = fake_read
        try:
            cec.verify_archive = lambda record, fetch=True: {
                "source_id": "S", "status": "MISMATCH", "checked": 1,
                "byte_identical": 0, "mismatched": [{"member": "m", "reason": "bytes differ"}]}
            r3 = cec.run(dry_run=False)
            check("a byte mismatch does not update the anchor", r3["anchor_updated"] is False)
            check("the offending source is named", r3["unacceptable"][0]["source_id"] == "S")

            cec.verify_archive = lambda record, fetch=True: {
                "source_id": "S", "status": "FETCH_FAILED", "checked": 0,
                "byte_identical": 0, "mismatched": []}
            r4 = cec.run(dry_run=False)
            check("a failed fetch is unacceptable rather than skipped",
                  r4["anchor_updated"] is False and r4["unacceptable"])

            cec.verify_archive = lambda record, fetch=True: {
                "source_id": "S", "status": "DIGEST_VERIFIED_NO_MEMBERS", "checked": 0,
                "byte_identical": 0, "mismatched": []}
            r5 = cec.run(dry_run=True)
            check("a pdf record with a verified digest is acceptable",
                  r5["verification_passed"] is True, json.dumps(r5))
        finally:
            pathlib.Path.read_text = original_read
    finally:
        cec.verify_claim_locators, cec.verify_archive, cec.receipt_files = (
            original_claims, original_archive, original_files)

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
