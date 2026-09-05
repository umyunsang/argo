#!/usr/bin/env python3
"""Failing-first tests for the source-only DiscoveryWorld pack design."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from validate_pack import validate

PACK = json.loads((HERE / "pack-design.json").read_text())


class DiscoveryWorldPackTests(unittest.TestCase):
    def assertRejected(self, mutant: dict, error: str) -> None:
        result = validate(mutant, ROOT)
        self.assertFalse(result["passed"], result)
        self.assertIn(error, result["errors"])

    def test_valid_design_passes_schema_only(self) -> None:
        result = validate(PACK, ROOT)
        self.assertTrue(result["passed"], result)

    def test_off_by_one_seed_manifest_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        for task in mutant["tasks"]:
            task["literal_api_seed"] += 1
        self.assertRejected(mutant, "TASK_MATRIX")

    def test_visual_path_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["observation_contract"]["vision_enabled"] = True
        self.assertRejected(mutant, "TEXT_ONLY")

    def test_llm_knowledge_judge_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["observation_contract"]["explanatory_knowledge_judge_enabled"] = True
        self.assertRejected(mutant, "NO_LLM_JUDGE")

    def test_seed_specific_gold_leak_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["tasks"][0]["expected_choice"] = "secret solution"
        self.assertRejected(mutant, "GOLD_LEAK")

    def test_seed_rows_cannot_be_inference_units(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["sampling"]["inference_unit"] = "seed_row"
        mutant["sampling"]["confirmatory_n"] = 10
        self.assertRejected(mutant, "PSEUDOREPLICATION")

    def test_old_record_must_remain_as_revoked(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["tasks"][0]["correction_event"]["retains_revoked_old_version"] = False
        self.assertRejected(mutant, "VERSION_HISTORY")

    def test_arm_information_must_match(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["event_contract"]["same_correction_bytes"] = False
        self.assertRejected(mutant, "ARM_IDENTITY")

    def test_runner_without_isolation_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["execution"]["runner"] = "run.py"
        self.assertRejected(mutant, "EXECUTION_GATE")

    def test_missing_cartesian_task_fails(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["tasks"].pop()
        mutant["sampling"]["task_rows"] = 9
        self.assertRejected(mutant, "TASK_MATRIX")

    def test_procedural_score_cannot_replace_primary(self) -> None:
        mutant = copy.deepcopy(PACK)
        mutant["endpoints"]["primary"] = "official scoreNormalized"
        self.assertRejected(mutant, "ENDPOINT")

    def test_gold_contract_contains_no_seed_solution(self) -> None:
        contract = json.loads((HERE / "gold-generation-contract.json").read_text())
        text = json.dumps(contract, sort_keys=True)
        self.assertNotIn("expected_choice", text)
        self.assertEqual(contract["status"], "DESIGN_ONLY_NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
