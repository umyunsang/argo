#!/usr/bin/env python3
"""Failing-first checks for the workflow-frontier manuscript handoff."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from validate_manuscript_handoff import validate

HANDOFF = json.loads(
    (ROOT / "paper/research/manuscript-update-handoff-workflow-frontier.json").read_text()
)


class ManuscriptHandoffTests(unittest.TestCase):
    def assertRejected(self, mutant: dict, error: str) -> None:
        result = validate(mutant, ROOT)
        self.assertFalse(result["passed"], result)
        self.assertIn(error, result["errors"])

    def test_current_handoff_passes(self) -> None:
        self.assertTrue(validate(HANDOFF, ROOT)["passed"])

    def test_qmd_identity_mismatch_fails(self) -> None:
        mutant = copy.deepcopy(HANDOFF)
        mutant["ownership_boundary"]["observed_current_sha256"] = "0" * 64
        self.assertRejected(mutant, "QMD_IDENTITY")

    def test_missing_scope_limit_fails(self) -> None:
        mutant = copy.deepcopy(HANDOFF)
        mutant["evidence_updates"][0]["mandatory_limit"] = ""
        self.assertRejected(mutant, "MANDATORY_LIMITS")

    def test_isolation_pass_claim_fails(self) -> None:
        mutant = copy.deepcopy(HANDOFF)
        mutant["current_claim_state"]["OS_isolation"] = "PASS"
        self.assertRejected(mutant, "CLAIM_STATE")

    def test_forbidden_boundary_removal_fails(self) -> None:
        mutant = copy.deepcopy(HANDOFF)
        mutant["forbidden_interpretations"].remove("typed policy causal efficacy")
        self.assertRejected(mutant, "FORBIDDEN_BOUNDARY")

    def test_evidence_hash_mutation_fails(self) -> None:
        mutant = copy.deepcopy(HANDOFF)
        mutant["evidence_updates"][1]["sha256"] = "f" * 64
        self.assertRejected(mutant, "EVIDENCE_HASH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
