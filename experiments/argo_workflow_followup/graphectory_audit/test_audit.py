#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from audit import audit

CAPSULE = ROOT / "paper/research/capsules/2026-09-05-graphectory/source-bytes.zip"
MANIFEST = ROOT / "paper/research/capsules/2026-09-05-graphectory/manifest.json"


class GraphectoryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = audit(CAPSULE, MANIFEST)

    def test_capsule_passes(self) -> None:
        self.assertTrue(self.result["passed"], self.result)

    def test_repo_graph_inventory_matches_metrics(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["tracked_graph_paths"], 3972)
        self.assertEqual(f["metrics_rows"], 3972)
        self.assertTrue(f["graph_metric_path_identity"])

    def test_paper_repository_count_difference_is_preserved(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["paper_nonempty_trajectories"], 3973)
        self.assertEqual(f["repository_graph_count_difference"], -1)
        self.assertEqual(f["count_difference_collection"], "SWE-agent/deepseek-v3")

    def test_selected_graph_outcomes_match_metrics(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["selected_graphs"], 22)
        self.assertEqual(f["selected_graph_metric_status_matches"], 22)

    def test_external_report_is_required_for_sample_outcome(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["sample_external_report_matches"], "6/6")
        self.assertEqual(f["openhands_embedded_report_matches"], "1/3")

    def test_openhands_sample_model_identity_mismatch_is_preserved(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["openhands_raw_model_vs_graph_directory_mismatch"], "3/3")

    def test_static_graphs_do_not_contain_raw_tuple_text_fields(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["selected_graphs_with_raw_thought_observation_fields"], 0)
        self.assertEqual(f["selected_graphs"], 22)

    def test_resolution_distribution_is_not_binary_only(self) -> None:
        self.assertEqual(self.result["findings"]["resolution_counts"], {"resolved": 1915, "unresolved": 1929, "unsubmitted": 128})

    def test_builder_source_reads_separate_report(self) -> None:
        self.assertTrue(self.result["findings"]["builder_external_report_dependency"])

    def test_zenodo_archive_remains_unfetched(self) -> None:
        f = self.result["findings"]
        self.assertEqual(f["zenodo_archive_size"], 1446491536)
        self.assertFalse(f["zenodo_archive_downloaded"])

    def test_capsule_byte_mutation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.zip"
            data = bytearray(CAPSULE.read_bytes())
            data[len(data) // 2] ^= 1
            bad.write_bytes(data)
            self.assertFalse(audit(bad, MANIFEST)["passed"])

    def test_manifest_identity_mutation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "manifest.json"
            obj = json.loads(MANIFEST.read_text())
            obj["repository"]["commit"] = "0" * 40
            bad.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
            self.assertFalse(audit(CAPSULE, bad)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
