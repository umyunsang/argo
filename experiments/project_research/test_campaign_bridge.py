"""Host bridge isolation/billing checks with no external request."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.project_research import campaign_bridge
from experiments.project_research.contracts import make_contract
from experiments.project_research.state import AdmissionError, Store


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.patcher = patch.object(campaign_bridge, "ROOT", self.root)
        self.patcher.start()
        self.store = Store(self.root / "control/state.sqlite")
        self.store.append(make_contract("campaign", "wine", "P", False, "pool"))
        self.workspace = self.root / "sessions/team1/workspace"
        self.workspace.mkdir(parents=True)
        self.cfg = {"campaign_id": "campaign", "team_id": "team1", "session_id": "s1", "model_id": "m", "image": "sha256:" + "0" * 64,
                    "auth_path": "unused-auth-path", "workspace": str(self.workspace), "deadline_epoch": time.time()+1000,
                    "model_pool": [{"id": "m", "provider": "openai-codex", "status": "QUALIFIED", "billing_mode": "subscription",
                                    "billing_authorized": True, "billing_upper_krw": 0, "billing_basis": "trusted entitlement"}]}

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def test_team_state_does_not_disclose_other_team(self):
        self.store.event({"project_id": "campaign", "team_id": "team2", "event": "secret-hypothesis"})
        self.store.event({"project_id": "campaign", "team_id": "team1", "event": "own-hypothesis"})
        result = campaign_bridge.execute(self.cfg, "read_state", {})
        self.assertNotIn("secret-hypothesis", json.dumps(result))
        self.assertIn("own-hypothesis", json.dumps(result))

    def test_unconfirmed_entitlement_prevents_dispatch(self):
        with patch.object(campaign_bridge, "codex_subscription_snapshot", return_value={"status": "UNKNOWN"}):
            result = campaign_bridge.execute(self.cfg, "reserve_model", {"request_id": "r", "model_id": "m", "upper_krw": 0})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.store.snapshot()["charges"], [])

    def test_post_entitlement_unknown_is_not_sdk_zero(self):
        with patch.object(campaign_bridge, "codex_subscription_snapshot", return_value={"status": "AVAILABLE_INCLUDED_ONLY"}):
            campaign_bridge.execute(self.cfg, "reserve_model", {"request_id": "r", "model_id": "m", "upper_krw": 0})
        with patch.object(campaign_bridge, "codex_subscription_snapshot", return_value={"status": "UNKNOWN"}):
            result = campaign_bridge.execute(self.cfg, "settle_model", {"request_id": "r", "usage": {"native": {"cost": {"total": 0}}}})
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(self.store.snapshot()["charges"][0]["actual"])

    def test_changed_source_cannot_launch_after_yield(self):
        (self.workspace / "solution.py").write_text("print('changed')")
        with patch.object(campaign_bridge, "dispatch") as dispatch:
            with self.assertRaises(AdmissionError):
                campaign_bridge.execute(self.cfg, "run_experiment", {"relative_source": "solution.py", "hypothesis": "x", "source_sha256": "0"*64})
            dispatch.assert_not_called()

    def test_fabricated_observation_cannot_trigger_continuity(self):
        with self.assertRaises(AdmissionError):
            campaign_bridge.execute(self.cfg, "checkpoint", {"first_hypothesis_observed": True, "observation_evidence": ["invented"]})

    def test_checkpoint_binds_receipt_hash_embedded_in_prose(self):
        self.store.event({"project_id": "campaign", "team_id": "team1", "event": "hypothesis_observation", "run_id": "run-1",
                          "experiment_id": "exp-1", "receipt_sha256": "a" * 64, "result_status": "EXECUTED_UNVALIDATED", "hypothesis": "h"})
        result = campaign_bridge.execute(self.cfg, "checkpoint", {"question": "q", "artifacts": [], "uncertainties": [], "confirmed_decisions": [],
                                                                    "first_hypothesis_observed": True, "observation_evidence": [f"ORX run run-1 receipt {'a' * 64} exit 0"]})
        self.assertEqual(result["status"], "CHECKPOINTED")
        with self.assertRaises(AdmissionError):
            campaign_bridge.execute(self.cfg, "checkpoint", {"question": "q", "artifacts": [], "uncertainties": [], "confirmed_decisions": [],
                                                            "first_hypothesis_observed": True, "observation_evidence": ["other-team-run"]})


if __name__ == "__main__":
    unittest.main()
