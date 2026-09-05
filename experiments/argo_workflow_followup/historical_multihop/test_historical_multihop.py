#!/usr/bin/env python3
"""Failing-first tests for one real historical multi-hop replay."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKFLOW = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WORKFLOW))

from decision_sufficiency import evaluate
from historical_multihop import (
    build_reference_packet,
    derive_any_support,
    derive_typed,
    verify_sources,
)

CASE = json.loads((HERE / "released/case.json").read_text())
GOLD = json.loads((HERE / "withheld/gold.json").read_text())


class HistoricalMultiHopTests(unittest.TestCase):
    def test_released_case_has_no_hidden_verdict(self) -> None:
        released = json.dumps(CASE, sort_keys=True)
        for forbidden in (
            '"expected_choice"',
            '"source_authority"',
            '"historical_source_receipts"',
            "HOLD_C_AND_REDESIGN_OUTCOME_CONTRACT",
        ):
            self.assertNotIn(forbidden, released)

    def test_historical_source_bytes_rederive_gold(self) -> None:
        result = verify_sources(GOLD, ROOT)
        self.assertTrue(result["all_pass"], result)

    def test_gold_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(GOLD)
        mutant["expected_choice"] = "action:discard_all_b2_evidence"
        result = verify_sources(mutant, ROOT)
        self.assertFalse(result["all_pass"])
        self.assertFalse(result["checks"]["audit_decision_maps_to_expected_choice"])

    def test_typed_replay_changes_full_multihop_chain(self) -> None:
        replay = derive_typed(CASE)
        self.assertEqual(replay["affected_nodes"], GOLD["expected_replay"]["affected_nodes"])
        self.assertEqual(replay["unaffected_nodes"], GOLD["expected_replay"]["unaffected_nodes"])
        self.assertEqual(replay["after"], GOLD["expected_replay"]["after"])
        self.assertEqual(replay["selected"], GOLD["expected_choice"])
        self.assertGreaterEqual(replay["max_changed_path_edges"], 4)

    def test_any_support_baseline_is_decision_insufficient(self) -> None:
        replay = derive_any_support(CASE)
        self.assertEqual(replay["selected"], "action:promote_directly_to_confirmation")
        self.assertNotEqual(replay["selected"], GOLD["expected_choice"])

    def test_reference_packet_passes_all_separate_gates(self) -> None:
        packet = build_reference_packet(CASE, derive_typed(CASE))
        result = evaluate(
            GOLD,
            packet,
            GOLD["expected_route"],
            task_outcome=GOLD["task_outcome"],
        )
        self.assertEqual(result["route_verdict"], "PASS")
        self.assertEqual(result["evidence_verdict"], "PASS")
        self.assertEqual(result["decision_verdict"], "PASS")
        self.assertTrue(result["confirmatory_success"])

    def test_route_only_output_is_inconclusive(self) -> None:
        packet = build_reference_packet(CASE, derive_typed(CASE))
        packet["evidence"] = []
        packet["constraints"] = []
        result = evaluate(GOLD, packet, GOLD["expected_route"], task_outcome=True)
        self.assertEqual(result["route_verdict"], "PASS")
        self.assertEqual(result["overall_verdict"], "INCONCLUSIVE")
        self.assertFalse(result["confirmatory_success"])

    def test_global_reset_route_is_invalid(self) -> None:
        packet = build_reference_packet(CASE, derive_typed(CASE))
        result = evaluate(
            GOLD,
            packet,
            GOLD["expected_route"] + ["decision:b2_status_only_descriptive_retention"],
            task_outcome=True,
        )
        self.assertEqual(result["route_verdict"], "INVALID")
        self.assertFalse(result["confirmatory_success"])

    def test_hidden_oracle_access_is_invalid(self) -> None:
        packet = build_reference_packet(CASE, derive_typed(CASE))
        packet["accessed_hidden_oracle"] = True
        result = evaluate(GOLD, packet, GOLD["expected_route"], task_outcome=True)
        self.assertEqual(result["overall_verdict"], "INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
