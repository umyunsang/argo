"""ORX checkpoint recovery tests use an in-memory transport; no compute launch."""
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest

from orx_adapter import OrxAdapter, OrxError, RunReference


PROJECT = "11111111-1111-4111-8111-111111111111"
EXPERIMENT = "22222222-2222-4222-8222-222222222222"
RUN = "33333333-3333-4333-8333-333333333333"
COMMAND = "/opt/homebrew/bin/python3 runner.py"
COMMIT = "a" * 40


class FakeOrx(OrxAdapter):
    def __init__(self):
        super().__init__(PROJECT, COMMAND)
        self.history = []
        self.launches = 0
        self.lost_ack = False
        self.publish = True

    def reference(self, state="running"):
        return RunReference(PROJECT, EXPERIMENT, RUN, COMMIT, COMMAND, state, "b" * 64, 1, None)

    def runs(self, experiment_id):
        return list(self.history)

    def _verify_commit(self, experiment_id, expected):
        return None

    def _launch(self, experiment_id):
        self.launches += 1
        if self.publish:
            self.history.append(self.reference())
        if self.lost_ack:
            raise OrxError("LOST_ACK")
        return RUN


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name).resolve() / "control" / "intent.json"
        self.adapter = FakeOrx()

    def tearDown(self):
        self.temporary.cleanup()

    def call(self, permit=True):
        return self.adapter.attach_or_run(EXPERIMENT, COMMIT, self.path, permit_launch=permit)

    def test_default_is_read_only(self):
        self.assertEqual(self.call(False)["state"], "NOT_SUBMITTED")
        self.assertEqual(self.adapter.launches, 0)

    def test_resume_attaches_once_and_preserves_terminal_failure(self):
        self.assertEqual(self.call()["reference"]["status"], "running")
        self.adapter.history = [self.adapter.reference("failed")]
        self.assertEqual(self.call()["reference"]["status"], "failed")
        self.assertEqual(self.adapter.launches, 1)

    def test_lost_launch_ack_is_reconciled_without_duplicate(self):
        self.adapter.lost_ack = True
        self.assertEqual(self.call()["run_id"], RUN)
        self.call()
        self.assertEqual(self.adapter.launches, 1)

    def test_unknown_submission_blocks_a_new_process(self):
        self.adapter.publish = False
        self.adapter.lost_ack = True
        self.assertEqual(self.call()["state"], "UNKNOWN")
        fresh = FakeOrx()
        self.assertEqual(fresh.attach_or_run(EXPERIMENT, COMMIT, self.path, permit_launch=True)["state"], "UNKNOWN")
        self.assertEqual(fresh.launches, 0)

    def test_pending_intent_with_late_run_can_attach(self):
        self.adapter.publish = False
        self.call()
        self.adapter.history = [self.adapter.reference("done")]
        self.assertEqual(self.call()["reference"]["status"], "done")
        self.assertEqual(self.adapter.launches, 1)

    def test_changed_commit_cannot_reuse_checkpoint(self):
        self.call()
        with self.assertRaisesRegex(OrxError, "IDENTITY_CHANGED"):
            self.adapter.attach_or_run(EXPERIMENT, "c" * 40, self.path, permit_launch=True)

    def test_completed_run_with_lost_checkpoint_is_attached(self):
        self.adapter.history = [self.adapter.reference("done")]
        self.assertEqual(self.call()["run_id"], RUN)
        self.assertEqual(self.adapter.launches, 0)

    def test_mismatched_run_id_does_not_attach_unrelated_run(self):
        self.call()
        record = json.loads(self.path.read_text())
        record["run_id"] = "44444444-4444-4444-8444-444444444444"
        self.path.write_text(json.dumps(record))
        self.assertEqual(self.call()["state"], "UNKNOWN")
        self.assertEqual(self.adapter.launches, 1)

    def test_reject_remote_api_and_contract_change(self):
        with self.assertRaises(OrxError):
            OrxAdapter(PROJECT, COMMAND, base_url="https://example.com")
        adapter = OrxAdapter(PROJECT, COMMAND)
        adapter._get = lambda route: {"experiments": [{"id": EXPERIMENT, "projectId": PROJECT, "runCommand": "other"}]}
        with self.assertRaisesRegex(OrxError, "CONTRACT_MISMATCH"):
            adapter.verify_experiment(EXPERIMENT)

    def test_run_schema_validates_exact_commit_and_backend(self):
        adapter = OrxAdapter(PROJECT, COMMAND)
        def get(route):
            if route.endswith("experiments"):
                return {"experiments": [{"id": EXPERIMENT, "projectId": PROJECT, "runCommand": COMMAND}]}
            return {"runs": [{"id": RUN, "projectId": PROJECT, "experimentId": EXPERIMENT,
                              "command": COMMAND, "commitSha": COMMIT, "createdAt": 1,
                              "status": "done", "endedAt": 2,
                              "backend": {"kind": "local_job", "sourceDigest": "b" * 64}}]}
        adapter._get = get
        self.assertEqual(asdict(adapter.runs(EXPERIMENT)[0])["commit_sha"], COMMIT)


if __name__ == "__main__":
    unittest.main()
