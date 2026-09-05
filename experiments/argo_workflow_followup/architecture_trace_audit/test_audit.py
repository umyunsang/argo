#!/usr/bin/env python3
"""Failing-first checks for the external real architecture trace."""
from __future__ import annotations

import copy
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from audit import audit

ARCHIVE = ROOT / "paper/research/capsules/2026-09-05-architecture-trace/source-bytes.zip"
MANIFEST = ROOT / "paper/research/capsules/2026-09-05-architecture-trace/manifest.json"


class ArchitectureTraceAuditTests(unittest.TestCase):
    def test_current_trace_capsule_passes(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertTrue(result["passed"], result)

    def test_csv_has_114_source_rows(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(result["findings"]["rows"], 114)
        self.assertEqual(result["findings"]["phase_rows"], {"1": 43, "1b": 21, "2": 32, "3": 18})

    def test_three_cross_scope_pairs_are_source_matched(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        pairs = result["findings"]["applicability_pairs"]
        self.assertEqual(len(pairs), 3)
        self.assertEqual([pair["old_id"] for pair in pairs], ["H7", "H23", "H21"])
        self.assertTrue(all(pair["phase1_outcome"] == "success" for pair in pairs))
        self.assertEqual([pair["phase2_outcome"] for pair in pairs], ["failure", "success", "success"])

    def test_scoped_revalidation_is_exact(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(result["replay"]["SCOPED_REVALIDATE"]["exact"], 3)
        self.assertEqual(result["replay"]["SCOPED_REVALIDATE"]["historical_over_revocation"], 0)

    def test_unscoped_reuse_selects_wrong_phase2_setting(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(result["replay"]["UNSCOPED_REUSE"]["correct_phase2_choices"], 0)
        self.assertEqual(result["replay"]["UNSCOPED_REUSE"]["under_revalidation"], 3)

    def test_global_reset_destroys_scoped_history(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(result["replay"]["GLOBAL_INVALIDATE"]["historical_over_revocation"], 3)

    def test_trace_is_not_outcome_reproduction(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertFalse(result["findings"]["training_code_present"])
        self.assertFalse(result["findings"]["per_hypothesis_git_history_present"])
        self.assertEqual(result["findings"]["inference_unit"], "one research programme")

    def test_manifest_member_mutation_fails(self) -> None:
        mutant = json.loads(MANIFEST.read_text())
        mutant["members"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(mutant))
            result = audit(ARCHIVE, path)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["member_hashes"])

    def test_decision_is_narrow(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(
            result["findings"]["decision"],
            "ADMIT_REAL_TRACE_RETROSPECTIVE_APPLICABILITY_REPLAY__BLOCK_OUTCOME_REPRODUCTION",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
