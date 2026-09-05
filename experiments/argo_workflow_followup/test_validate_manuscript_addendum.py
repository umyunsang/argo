#!/usr/bin/env python3
"""Failing-first checks for the external-trace manuscript addendum."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from validate_manuscript_addendum import validate

ADDENDUM = json.loads(
    (ROOT / "paper/research/manuscript-update-handoff-external-trace-addendum.json").read_text()
)


class ManuscriptAddendumTests(unittest.TestCase):
    def test_current_addendum_passes(self) -> None:
        self.assertTrue(validate(ADDENDUM, ROOT)["passed"])

    def test_nested_scope_limit_removal_fails(self) -> None:
        mutant = copy.deepcopy(ADDENDUM)
        mutant["mandatory_limits"] = [
            item for item in mutant["mandatory_limits"] if "nested" not in item
        ]
        result = validate(mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertIn("SCOPE_LIMITS", result["errors"])

    def test_source_hash_mutation_fails(self) -> None:
        mutant = copy.deepcopy(ADDENDUM)
        mutant["new_evidence"]["source_audit_sha256"] = "0" * 64
        result = validate(mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertIn("EVIDENCE_HASH", result["errors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
