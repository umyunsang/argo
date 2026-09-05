#!/usr/bin/env python3
"""Failing-first tests for canonical real decision packets."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from validate import simulate_withdrawals, validate_documents, validate_paths

CONTRACT_PATH = ROOT / "paper/research/real-decision-packet-contract-v1.json"
MANIFEST_PATH = HERE / "manifest.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text())
MANIFEST = json.loads(MANIFEST_PATH.read_text())


class RealDecisionPacketTests(unittest.TestCase):
    def test_valid_real_packets_reproduce_frozen_summary(self) -> None:
        result = validate_paths(CONTRACT_PATH, MANIFEST_PATH, ROOT)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["summary"], MANIFEST["expected_descriptive_summary"])

    def test_route_fidelity_does_not_equal_sufficiency(self) -> None:
        result = validate_documents(CONTRACT, MANIFEST, ROOT)
        self.assertEqual(result["summary"]["route_fidelity_pass"], 4)
        self.assertEqual(result["summary"]["sufficiency_pass"], 2)
        self.assertEqual(result["summary"]["sufficiency_inconclusive"], 2)

    def test_no_external_task_outcome_is_inferred(self) -> None:
        result = validate_documents(CONTRACT, MANIFEST, ROOT)
        self.assertEqual(result["summary"]["external_task_outcomes_measured"], 0)
        self.assertTrue(all(row["external_task_outcome"] == "NOT_MEASURED" for row in result["packets"].values()))

    def test_selective_withdrawal_is_exact_on_four_real_packets(self) -> None:
        replay = simulate_withdrawals(CONTRACT, MANIFEST)
        self.assertEqual(replay["events"], 4)
        self.assertEqual(replay["selective_exact"], 4)
        self.assertTrue(all(row["selective_affected"] == row["expected_affected"] for row in replay["trials"]))

    def test_global_reset_overrevokes_twelve_packets(self) -> None:
        self.assertEqual(simulate_withdrawals(CONTRACT, MANIFEST)["global_overrevocations"], 12)

    def test_external_nested_pairs_cannot_be_n3(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][0]["claims"]["inference_units"] = 3
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["external_trace"]["verdict"], "INVALID")

    def test_physics_aggregate_cannot_be_promoted_to_raw_graph(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][1]["selected_decision"] = "ADMIT_RAW_DECISION_GRAPH"
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["grounded_physics"]["verdict"], "INVALID")

    def test_discoveryworld_seed_rows_cannot_be_n10(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][2]["claims"]["inference_units"] = 10
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["discoveryworld"]["verdict"], "INVALID")

    def test_unapproved_canary_cannot_be_promoted(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][3]["selected_decision"] = "ISOLATION_PROVEN_RUN_TASKS"
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["isolation_canary"]["verdict"], "INVALID")

    def test_missing_route_is_inconclusive_not_pass(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][2]["routed_roles"].remove("source_audit")
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["discoveryworld"]["route_fidelity"], "INCONCLUSIVE")
        self.assertEqual(result["packets"]["discoveryworld"]["verdict"], "INCONCLUSIVE")

    def test_wrong_evidence_hash_is_invalid(self) -> None:
        mutant_contract = copy.deepcopy(CONTRACT)
        mutant_contract["packets"]["grounded_physics"]["evidence"]["audit"]["sha256"] = "0" * 64
        result = validate_documents(mutant_contract, MANIFEST, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["grounded_physics"]["route_fidelity"], "INVALID")

    def test_extra_wrong_route_is_invalid(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["packets"][0]["routed_roles"].append("audit")
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertEqual(result["packets"]["external_trace"]["route_fidelity"], "INVALID")

    def test_contract_hash_drift_fails_before_scoring(self) -> None:
        mutant = copy.deepcopy(MANIFEST)
        mutant["contract_sha256"] = "0" * 64
        result = validate_documents(CONTRACT, mutant, ROOT)
        self.assertFalse(result["passed"])
        self.assertIn("CONTRACT_IDENTITY", result["errors"])

    def test_missing_canonical_decision_node_is_invalid(self) -> None:
        mutant_contract = copy.deepcopy(CONTRACT)
        mutant_contract["packets"]["external_trace"]["graph_decision_id"] = "decision:does_not_exist"
        result = validate_documents(mutant_contract, MANIFEST, ROOT)
        self.assertFalse(result["passed"])
        self.assertIn("GRAPH_DECISION_ID", result["packets"]["external_trace"]["errors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
