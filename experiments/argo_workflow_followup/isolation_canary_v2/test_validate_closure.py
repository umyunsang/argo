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
from validate_closure import validate

CLOSURE = ROOT / "paper/research/receipts/isolation-canary-v2-closure-v1.json"


def mutate(fn) -> Path:
    obj = json.loads(CLOSURE.read_text())
    fn(obj)
    path = Path(tempfile.mkdtemp()) / "closure.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return path


class ClosureTests(unittest.TestCase):
    def test_current_closure_passes(self) -> None:
        result = validate(CLOSURE, ROOT)
        self.assertTrue(result["passed"], result["errors"])

    def test_approved_authorization_hash_is_bound(self) -> None:
        path = mutate(lambda obj: obj.update({"approved_authorization_sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_retry_cannot_be_reopened(self) -> None:
        path = mutate(lambda obj: obj["authorization"].update({"remaining_attempts": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_policy_episode_cannot_be_invented(self) -> None:
        path = mutate(lambda obj: obj["execution"].update({"policy_episodes": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_unobserved_check_cannot_be_called_failure(self) -> None:
        path = mutate(lambda obj: obj["observed_checks"].update({"external_network_blocked": "FAIL"}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_prelaunch_diagnosis_is_fixed(self) -> None:
        path = mutate(lambda obj: obj["diagnosis"].update({"code": "ISOLATION_FAILED"}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_result_hash_is_bound(self) -> None:
        path = mutate(lambda obj: obj.update({"result_sha256": "0" * 64}))
        self.assertFalse(validate(path, ROOT)["passed"])

    def test_model_calls_remain_zero(self) -> None:
        path = mutate(lambda obj: obj.update({"model_calls": 1}))
        self.assertFalse(validate(path, ROOT)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
