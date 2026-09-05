#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from validate_graphectory_addendum import validate

ADDENDUM = ROOT / "paper/research/manuscript-update-handoff-graphectory-addendum.json"


def mutate(fn) -> Path:
    obj = json.loads(ADDENDUM.read_text())
    fn(obj)
    path = Path(tempfile.mkdtemp()) / "addendum.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return path


class AddendumTests(unittest.TestCase):
    def test_current_addendum_passes(self) -> None:
        result = validate(ADDENDUM, ROOT)
        self.assertTrue(result["passed"], result["errors"])

    def test_parent_hash_is_bound(self) -> None:
        path = mutate(lambda obj: obj.update({"parent_handoff_sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_qmd_must_remain_unedited(self) -> None:
        path = mutate(lambda obj: obj["ownership_boundary"].update({"edited": True}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_paper_repository_difference_must_remain(self) -> None:
        path = mutate(lambda obj: obj["mandatory_limits"].remove("The 1,446,491,536-byte Zenodo raw archive was identified but not downloaded; full raw-corpus integrity is unverified."))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_source_hashes_are_bound(self) -> None:
        path = mutate(lambda obj: obj["new_evidence"].update({"source_audit_sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_static_graph_raw_content_cannot_be_promoted(self) -> None:
        path = mutate(lambda obj: obj["mandatory_limits"].remove("Static selected graph JSON contains command and summary fields but no complete raw thought/observation/response fields."))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_independent_n_cannot_be_inflated(self) -> None:
        path = mutate(lambda obj: obj["forbidden_interpretations"].remove("n=6 independent experiments"))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_addendum_cannot_authorize_execution(self) -> None:
        path = mutate(lambda obj: obj["forbidden_interpretations"].remove("permission to execute Docker, tasks, models, or OpenResearch"))
        self.assertFalse(validate(path, ROOT)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
