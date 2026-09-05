#!/usr/bin/env python3
"""Failing-first tests for the routing-to-decision-sufficiency scorer."""
from __future__ import annotations

import copy
import unittest

from decision_sufficiency import evaluate


def gold() -> dict:
    return {
        "schema_version": "argo-decision-sufficiency-gold/v1",
        "decision_id": "decision:d1",
        "expected_route": ["decision:d1"],
        "required_evidence": [
            {"id": "evidence:e1", "version": "v2"},
            {"id": "evidence:e2", "version": "v1"},
        ],
        "revoked_evidence": [{"id": "evidence:e0", "version": "v1"}],
        "required_constraints": [{"id": "constraint:c1", "version": "v3"}],
        "required_alternatives": ["action:a", "action:b"],
        "expected_choice": "action:b",
    }


def packet() -> dict:
    return {
        "schema_version": "argo-decision-packet/v1",
        "decision_id": "decision:d1",
        "evidence": [
            {"id": "evidence:e1", "version": "v2", "status": "VALID"},
            {"id": "evidence:e2", "version": "v1", "status": "VALID"},
        ],
        "constraints": [
            {"id": "constraint:c1", "version": "v3", "applicable": True}
        ],
        "alternatives": ["action:a", "action:b"],
        "selected": "action:b",
        "missing_evidence": [],
        "unresolved_conflicts": [],
        "falsifier": "observable:q contradicts evidence:e1",
        "next_experiment": {
            "action": "measure:q",
            "observable": "q",
            "stop_rule": "stop after one valid measurement",
        },
        "accessed_hidden_oracle": False,
    }


class DecisionSufficiencyTests(unittest.TestCase):
    def test_complete_packet_passes_but_task_outcome_remains_separate(self) -> None:
        result = evaluate(gold(), packet(), ["decision:d1"], task_outcome=False)
        self.assertEqual(result["overall_verdict"], "PASS")
        self.assertFalse(result["confirmatory_success"])

    def test_exact_route_alone_is_not_sufficient(self) -> None:
        candidate = packet()
        candidate["evidence"] = []
        candidate["constraints"] = []
        candidate["alternatives"] = []
        candidate["falsifier"] = ""
        candidate["next_experiment"] = {}
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["route_verdict"], "PASS")
        self.assertEqual(result["overall_verdict"], "INCONCLUSIVE")
        self.assertFalse(result["confirmatory_success"])

    def test_stale_version_is_invalid(self) -> None:
        candidate = packet()
        candidate["evidence"][0]["version"] = "v1"
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["evidence_verdict"], "INVALID")
        self.assertFalse(result["confirmatory_success"])

    def test_overbroad_route_is_invalid_even_when_task_succeeds(self) -> None:
        result = evaluate(
            gold(), packet(), ["decision:d1", "decision:unaffected"], task_outcome=True
        )
        self.assertEqual(result["route_verdict"], "INVALID")
        self.assertFalse(result["confirmatory_success"])

    def test_hidden_oracle_access_invalidates(self) -> None:
        candidate = packet()
        candidate["accessed_hidden_oracle"] = True
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["overall_verdict"], "INVALID")
        self.assertFalse(result["confirmatory_success"])

    def test_wrong_choice_is_invalid(self) -> None:
        candidate = packet()
        candidate["selected"] = "action:a"
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["decision_verdict"], "INVALID")
        self.assertFalse(result["confirmatory_success"])

    def test_no_unique_choice_oracle_abstains(self) -> None:
        ambiguous = copy.deepcopy(gold())
        ambiguous["expected_choice"] = None
        result = evaluate(ambiguous, packet(), ["decision:d1"], task_outcome=True)
        self.assertEqual(result["decision_verdict"], "INCONCLUSIVE")
        self.assertFalse(result["confirmatory_success"])

    def test_valid_packet_and_task_outcome_form_confirmatory_success(self) -> None:
        result = evaluate(gold(), packet(), ["decision:d1"], task_outcome=True)
        self.assertEqual(result["overall_verdict"], "PASS")
        self.assertTrue(result["confirmatory_success"])

    def test_revoked_evidence_is_invalid(self) -> None:
        candidate = packet()
        candidate["evidence"].append(
            {"id": "evidence:e0", "version": "v1", "status": "VALID"}
        )
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["evidence_verdict"], "INVALID")

    def test_declared_gap_abstains(self) -> None:
        candidate = packet()
        candidate["unresolved_conflicts"] = ["evidence:e1 conflicts with evidence:e2"]
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["evidence_verdict"], "INCONCLUSIVE")
        self.assertFalse(result["confirmatory_success"])

    def test_wrong_constraint_version_is_invalid(self) -> None:
        candidate = packet()
        candidate["constraints"][0]["version"] = "v2"
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["evidence_verdict"], "INVALID")

    def test_duplicate_route_fails_closed(self) -> None:
        result = evaluate(
            gold(), packet(), ["decision:d1", "decision:d1"], task_outcome=True
        )
        self.assertEqual(result["overall_verdict"], "INVALID")

    def test_malformed_packet_fails_closed(self) -> None:
        candidate = packet()
        del candidate["schema_version"]
        result = evaluate(gold(), candidate, ["decision:d1"], task_outcome=True)
        self.assertEqual(result["overall_verdict"], "INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
