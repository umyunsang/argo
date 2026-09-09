"""Negative contract/accounting fixtures; not research outcomes."""
import copy
import tempfile
import unittest
from pathlib import Path

from experiments.project_research.contracts import ContractError, make_contract, utc_now, validate_record
from experiments.project_research.state import AdmissionError, Store


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "state.sqlite")
        self.contract = make_contract("p", "wine", "P", True, "pool-hash")
        self.store.append(self.contract)

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_contract_cannot_reset_resources(self):
        self.store.admit_compute("first", "p", 30)
        self.store.append(self.contract)
        changed = copy.deepcopy(self.contract)
        changed["id"] = "new-contract"
        with self.assertRaises(AdmissionError):
            self.store.append(changed)
        with self.assertRaises(AdmissionError):
            self.store.admit_compute("next", "p", 30)

    def test_unknown_billing_blocks_dispatch_across_restart(self):
        self.store.reserve_charge("a", "p", "first_week", 1000)
        self.store.settle_charge("a", None, {"sent": True, "usage": "missing"})
        restarted = Store(self.store.path)
        with self.assertRaises(AdmissionError):
            restarted.reserve_charge("b", "p", "comparison", 1)
        self.assertIsNone(restarted.snapshot()["charges"][0]["actual"])
        restarted.settle_charge("a", 800, {"provider_invoice": "receipt-hash"})
        restarted.reserve_charge("b", "p", "comparison", 1)

    def test_reservations_count_toward_phase_and_total(self):
        self.store.reserve_charge("a", "p", "first_week", 150000)
        with self.assertRaises(AdmissionError):
            self.store.reserve_charge("b", "p", "first_week", 1)
        self.store.reserve_charge("c", "p", "comparison", 90000)
        self.store.reserve_charge("d", "p", "reserve", 60000)
        with self.assertRaises(AdmissionError):
            self.store.reserve_charge("e", "p", "reserve", 1)

    def test_invalid_numbers_rejected(self):
        for value in (True, -1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(AdmissionError):
                self.store.admit_compute("a", "p", value)
        invalid = copy.deepcopy(self.contract)
        invalid["resources"]["cpu_core_seconds"] = 28801
        with self.assertRaises(ContractError):
            validate_record(invalid)

    def test_global_memory_ceiling_across_projects(self):
        contract = make_contract("q", "duckdb", "B", False, "pool-hash")
        contract["resources"]["memory_mib"] = 4000
        self.store.append(contract)
        self.store.admit_compute("a", "p", 30, 1, 2000, exclusive=False)
        with self.assertRaises(AdmissionError):
            self.store.admit_compute("b", "q", 30, 1, 3000, exclusive=False)

    def test_unknown_container_keeps_capacity_and_blocks_restart(self):
        self.store.admit_compute("a", "p", 30)
        self.store.settle_compute("a", 2, {"terminal": True, "container_absent": False})
        self.assertIsNone(self.store.snapshot()["compute"][0]["used"])
        with self.assertRaises(AdmissionError):
            Store(self.store.path).admit_compute("b", "p", 30)

    def test_kernel_cannot_enter_active_exclusive_measurement(self):
        self.store.admit_compute("measurement", "p", 30, exclusive=True)
        with self.assertRaises(AdmissionError):
            self.store.admit_compute("kernel", "p", 30, .5, 512, exclusive=False)

    def test_settled_cpu_remains_charged(self):
        self.store.admit_compute("a", "p", 30)
        self.store.settle_compute("a", 15, {"terminal": True, "container_absent": True})
        self.store.admit_compute("b", "p", 30)
        self.assertEqual(self.store.snapshot()["compute"][0]["used"], 15)

    def checkpoint(self, observed=True):
        return {"type": "Checkpoint", "id": "ck", "project_id": "p", "created_at": utc_now(),
                "question": "Does it generalize?", "artifacts": ["sha256:artifact"], "uncertainties": ["new color"],
                "orx_runs": [{"experiment_id": "e", "run_id": "r", "status": "RUNNING"}],
                "tool_versions": {"tool": "sha256:t"}, "budget": {"unknown": False}, "model_id": "m1",
                "session_id": "s1", "confirmed_decisions": ["decision-1"], "first_hypothesis_observed": observed,
                "observation_evidence": ["receipt-hash"] if observed else []}

    def test_continuity_requires_observation_new_model_and_session(self):
        self.store.append(self.checkpoint())
        for model, session in (("m1", "s2"), ("m3", "s2"), ("m2", "s1")):
            with self.subTest(model=model, session=session), self.assertRaises(AdmissionError):
                self.store.resume("ck", model, session, ["m1", "m2"])
        resumed = self.store.resume("ck", "m2", "s2", ["m1", "m2"])
        self.assertEqual(resumed["checkpoint"]["orx_runs"][0]["run_id"], "r")
        self.assertEqual(resumed["orx_action"], "RECONCILE_EXISTING_RUNS")

    def test_unreached_trigger_is_preserved(self):
        self.store.append(self.checkpoint(False))
        with self.assertRaises(AdmissionError):
            self.store.resume("ck", "m2", "s2", ["m1", "m2"])
        self.assertFalse(self.store.snapshot()["records"][-1]["first_hypothesis_observed"])

    def test_record_tampering_rejected(self):
        self.store.append(self.checkpoint())
        tampered = self.checkpoint()
        tampered["question"] = "A different question"
        with self.assertRaises(AdmissionError):
            self.store.append(tampered)


if __name__ == "__main__":
    unittest.main()
