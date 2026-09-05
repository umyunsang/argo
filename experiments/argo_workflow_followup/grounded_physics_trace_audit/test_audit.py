#!/usr/bin/env python3
"""Failing-first checks for the grounded-physics trace archive."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from audit import audit

ARCHIVE = ROOT / "paper/research/capsules/2026-09-05-grounded-physics-trace/paper_c_data_v1.zip"
MANIFEST = ROOT / "paper/research/capsules/2026-09-05-grounded-physics-trace/manifest.json"


class GroundedPhysicsTraceTests(unittest.TestCase):
    def test_current_archive_passes(self) -> None:
        self.assertTrue(audit(ARCHIVE, MANIFEST)["passed"])

    def test_internal_integrity_is_complete(self) -> None:
        finding = audit(ARCHIVE, MANIFEST)["findings"]
        self.assertEqual(finding["internal_sha256"], "125/125")
        self.assertEqual(finding["unsafe_paths"], 0)

    def test_aggregate_replay_surface_is_present(self) -> None:
        finding = audit(ARCHIVE, MANIFEST)["findings"]
        self.assertEqual(finding["anchors"], {"tracks": 7, "pass": 4, "caveat": 3})
        self.assertEqual(finding["catch_episodes"], 15)
        self.assertEqual(finding["sessions"], 47)
        self.assertEqual(finding["literature_events"], 2162)

    def test_episode_sources_are_not_directly_closed(self) -> None:
        finding = audit(ARCHIVE, MANIFEST)["findings"]
        self.assertEqual(finding["episode_rows"], 15)
        self.assertEqual(finding["episode_rows_with_direct_source_path"], 0)
        self.assertEqual(finding["episode_rows_without_direct_source_path"], 15)

    def test_raw_transcripts_are_withheld(self) -> None:
        finding = audit(ARCHIVE, MANIFEST)["findings"]
        self.assertFalse(finding["raw_transcripts_published"])
        self.assertFalse(finding["raw_decision_graph_admissible"])

    def test_episode_lane_counts_match(self) -> None:
        self.assertEqual(
            audit(ARCHIVE, MANIFEST)["findings"]["episode_lanes"],
            {"Adversarial review": 7, "Distributed grounding": 1, "Falsification": 4, "Within-session debug": 3},
        )

    def test_manifest_hash_mutation_fails(self) -> None:
        mutant = json.loads(MANIFEST.read_text())
        mutant["archive_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(mutant))
            result = audit(ARCHIVE, path)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["archive_hash"])

    def test_decision_is_narrow(self) -> None:
        self.assertEqual(
            audit(ARCHIVE, MANIFEST)["findings"]["decision"],
            "ADMIT_AGGREGATE_AND_CORRECTION_TAXONOMY__REJECT_RAW_DECISION_GRAPH",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
