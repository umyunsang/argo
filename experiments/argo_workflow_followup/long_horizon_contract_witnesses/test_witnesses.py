"""Engineered contract examples only; no agent or benchmark evaluation."""
import copy
import json
from pathlib import Path
import unittest

from validator import validate

FIXTURES = Path(__file__).parent / "fixtures"
CATALOGUE = json.loads((FIXTURES / "catalogue.json").read_text())["cases"]
MALFORMED = json.loads((FIXTURES / "malformed.json").read_text())["cases"]
CASES = {case["id"]: case for case in CATALOGUE}


class ContractWitnessTests(unittest.TestCase):
    def check_case(self, name):
        case = CASES[name]
        before = copy.deepcopy(case["input"])
        self.assertEqual(validate(case["input"]), case["expected"])
        self.assertEqual(case["input"], before, "validator must not rewrite history")

    def test_bytes_recoverable_not_exposed(self):
        self.check_case("bytes_recoverable_not_exposed")

    def test_reachable_wrong_scope(self):
        self.check_case("reachable_wrong_scope")

    def test_cached_wrong_artifact_version(self):
        self.check_case("cached_wrong_artifact_version")

    def test_negative_unchanged_context(self):
        self.check_case("negative_unchanged_context")

    def test_negative_relevant_change(self):
        self.check_case("negative_relevant_change")

    def test_negative_irrelevant_change(self):
        self.check_case("negative_irrelevant_change")

    def test_historical_best_survives_correction(self):
        self.check_case("historical_best_survives_correction")

    def test_inferred_workspace_not_original(self):
        self.check_case("inferred_workspace_not_original")

    def test_legal_controls(self):
        for case in CATALOGUE:
            if case["category"] == "control":
                with self.subTest(case=case["id"]):
                    self.check_case(case["id"])

    def test_malformed_or_missing_evidence(self):
        for case in MALFORMED:
            with self.subTest(case=case["id"]):
                with self.assertRaises(ValueError):
                    validate(case["input"])


if __name__ == "__main__":
    unittest.main()
