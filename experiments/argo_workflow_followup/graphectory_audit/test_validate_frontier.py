#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from validate_frontier import validate

RECEIPT = ROOT / "paper/research/graphectory-trace-audit.json"


def mutated(change) -> Path:
    obj = json.loads(RECEIPT.read_text())
    change(obj)
    directory = Path(tempfile.mkdtemp())
    path = directory / "receipt.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return path


class GraphectoryFrontierTests(unittest.TestCase):
    def test_current_frontier_passes(self) -> None:
        result = validate(RECEIPT, ROOT)
        self.assertTrue(result["passed"], result["errors"])

    def test_paper_repo_count_difference_cannot_be_erased(self) -> None:
        path = mutated(lambda obj: obj["audit"]["result"]["findings"].update({"repository_graph_count_difference": 0}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_version_changed_units_cannot_be_relabelled(self) -> None:
        path = mutated(lambda obj: obj["builder_replay"]["measured"].update({"changed_units": 0}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_nested_samples_cannot_be_n6(self) -> None:
        path = mutated(lambda obj: obj.update({"independent_n": 6}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_unfetched_raw_archive_cannot_be_claimed_fetched(self) -> None:
        path = mutated(lambda obj: obj["source"].update({"raw_archive_downloaded": True}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_static_graph_cannot_be_called_full_raw_tuple(self) -> None:
        path = mutated(lambda obj: obj["not_admitted"].remove("claim that static graph JSON contains complete thought/observation text"))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_model_identity_failure_cannot_be_erased(self) -> None:
        path = mutated(lambda obj: obj["builder_replay"]["measured"].update({"openhands_model_identity_matches": 3}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_builder_receipt_hash_is_bound(self) -> None:
        path = mutated(lambda obj: obj["builder_replay"].update({"receipt_sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_capsule_hash_is_bound(self) -> None:
        path = mutated(lambda obj: obj["capsule"].update({"sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_model_calls_must_remain_zero(self) -> None:
        path = mutated(lambda obj: obj.update({"model_calls": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
