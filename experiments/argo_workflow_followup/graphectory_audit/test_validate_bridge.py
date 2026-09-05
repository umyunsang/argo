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
from validate_bridge import validate

BRIDGE = ROOT / "paper/research/routing-decision-outcome-bridge-v1.json"


def mutate(fn) -> Path:
    obj = json.loads(BRIDGE.read_text())
    fn(obj)
    path = Path(tempfile.mkdtemp()) / "bridge.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return path


class BridgeTests(unittest.TestCase):
    def test_current_bridge_passes(self) -> None:
        result = validate(BRIDGE, ROOT)
        self.assertTrue(result["passed"], result["errors"])

    def test_route_cannot_substitute_for_sufficiency(self) -> None:
        path = mutate(lambda obj: obj["measured"].update({"canonical_packet_sufficiency_pass": 4}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_selected_statuses_cannot_be_called_full_re_evaluation(self) -> None:
        path = mutate(lambda obj: obj["measured"].update({"graphectory_selected_status_verified": 3972}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_decision_oracle_cannot_be_invented(self) -> None:
        path = mutate(lambda obj: obj["measured"].update({"correction_decision_oracles_added": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_six_rows_cannot_be_six_programmes(self) -> None:
        path = mutate(lambda obj: obj["measured"].update({"independent_external_programmes_added": 6}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_raw_archive_cannot_be_called_verified(self) -> None:
        path = mutate(lambda obj: obj["measured"].update({"full_raw_archive_verified": True}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_input_hash_is_bound(self) -> None:
        path = mutate(lambda obj: obj["inputs"]["graphectory_audit"].update({"sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_model_calls_must_remain_zero(self) -> None:
        path = mutate(lambda obj: obj.update({"model_calls": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
