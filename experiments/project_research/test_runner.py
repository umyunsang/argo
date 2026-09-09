"""Receipt integrity fixtures, with no real research execution."""
import unittest

from experiments.project_research.runner import valid_observation


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.resource = {"exit_code": 0, "cpu_seconds": 1.0, "wall_seconds": 2.0}
        self.receipt = {"schema_version": "project-research-domain-result/v1", "domain": "wine",
                        "status": "OBSERVATIONS_RECORDED", "development_only": True, "final_evaluation": False,
                        "evidence_stage": "DEVELOPMENT_BASELINE_HYPOTHESIS", "result": {"observations": []},
                        "environment": {"matches_pins": True}, "code_sha256": {"source.py": "sha"}}

    def test_zero_exit_and_truthy_json_not_enough(self):
        self.assertFalse(valid_observation({"hello": "world"}, self.resource, "wine"))
        self.assertFalse(valid_observation(self.receipt, {"exit_code": 0}, "wine"))

    def test_failed_or_wrong_domain_or_fixture_rejected(self):
        for key, value in (("status", "FAILED"), ("domain", "duckdb"), ("evidence_stage", "APPARATUS_ONLY"), ("final_evaluation", True)):
            receipt = {**self.receipt, key: value}
            self.assertFalse(valid_observation(receipt, self.resource, "wine"))

    def test_invalid_usage_rejected(self):
        for value in (-1, float("nan"), float("inf"), True):
            self.assertFalse(valid_observation(self.receipt, {**self.resource, "cpu_seconds": value}, "wine"))

    def test_observation_receipt_is_admissible_execution_not_aaa(self):
        self.assertTrue(valid_observation(self.receipt, self.resource, "wine"))


if __name__ == "__main__":
    unittest.main()
