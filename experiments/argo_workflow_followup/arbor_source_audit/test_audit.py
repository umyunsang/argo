#!/usr/bin/env python3
"""Failing-first checks for the pinned Arbor artifact audit."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from audit import audit

ARCHIVE = ROOT / "paper/research/capsules/2026-09-05-arbor-source-audit/source-bytes.zip"
MANIFEST = ROOT / "paper/research/capsules/2026-09-05-arbor-source-audit/manifest.json"


class ArborSourceAuditTests(unittest.TestCase):
    def test_current_capsule_passes_identity_checks(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertTrue(result["passed"], result)

    def test_bundled_demo_is_classified_synthetic(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertTrue(result["findings"]["bundled_demo_explicitly_synthetic"])
        self.assertEqual(result["findings"]["bundled_demo_nodes"], 7)
        self.assertEqual(result["findings"]["bundled_demo_events"], 117)

    def test_browsecomp_html_status_mismatch_is_detected(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(
            result["findings"]["browsecomp_embedded_nonroot_status_counts"],
            {"done": 4, "merged": 1, "pruned": 4},
        )
        self.assertEqual(
            result["findings"]["browsecomp_narrative_status_counts"],
            {"done": 5, "merged": 1, "pruned": 3},
        )
        self.assertTrue(result["findings"]["browsecomp_status_mismatch"])

    def test_referenced_raw_browsecomp_run_is_absent(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertTrue(result["findings"]["browsecomp_raw_lineage_absent"])
        self.assertFalse(result["findings"]["independent_real_graph_admissible"])

    def test_tree_schema_has_no_typed_evidence_validity_fields(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(
            result["findings"]["missing_typed_fields"],
            ["applicability", "dependency_edges", "evidence_id", "validity", "version"],
        )
        self.assertIn("hypothesis", result["findings"]["node_fields"])
        self.assertIn("result", result["findings"]["mutable_fields"])
        self.assertTrue(result["findings"]["recursive_descendant_prune"])
        self.assertTrue(result["findings"]["answer_bearing_fields_mutable"])

    def test_manifest_hash_mutation_fails(self) -> None:
        mutant = json.loads(MANIFEST.read_text())
        mutant["members"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(mutant))
            result = audit(ARCHIVE, path)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["member_hashes"])

    def test_code_source_not_real_graph_source(self) -> None:
        result = audit(ARCHIVE, MANIFEST)
        self.assertEqual(
            result["findings"]["decision"],
            "VALID_STRONG_COMPARATOR_CODE_SOURCE__BLOCKED_INDEPENDENT_REAL_GRAPH",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
