"""Dispatch-recovery regressions using local fixtures and mocked ORX/git only."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiments.project_research import dispatch as dispatch_module


class DispatchRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="project-dispatch-fixture-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.control = self.root / "control"
        self.control.mkdir()
        self.repository = self.root / "orx-project"
        self.repository.mkdir()
        self.project_id = "11111111-1111-4111-8111-111111111111"
        self.experiment_id = "22222222-2222-4222-8222-222222222222"
        self.commit = "a" * 40
        (self.control / "orx-project.json").write_text(json.dumps({
            "project": {"id": self.project_id, "path": str(self.repository)},
        }))
        source = self.root / "fixture-source"
        source.mkdir()
        for name in ("__init__.py", "contracts.py", "state.py", "runner.py", "container_task.py"):
            (source / name).write_text("# Fixture content; never executed.\n")
        (source / "domains").mkdir()
        (source / "domains" / "cli.py").write_text("# Fixture domain command; never executed.\n")
        (source / "domains" / "requirements.txt").write_text("# Fixture dependency manifest.\n")

        self.patch("ROOT", self.root)
        self.patch("SOURCE", source)
        self.git = self.patch("git")
        self.git.side_effect = self.fake_git
        self.run = self.patch("subprocess.run")
        self.run.return_value = subprocess.CompletedProcess(
            args=["mock-orx"], returncode=0,
            stdout=f"  id: {self.experiment_id}\n  branch: orx/fixture-node\n", stderr="",
        )
        self.adapter_type = self.patch("OrxAdapter")
        self.adapter = self.adapter_type.return_value
        self.adapter.executable = "/fixture/never-executed-orx"
        self.adapter.attach_or_run.return_value = {
            "state": "ATTACHED", "run_id": "33333333-3333-4333-8333-333333333333",
        }
        self.store_type = self.patch("Store")
        self.spec = {
            "project_id": "development-wine", "domain": "wine", "mode": "candidate",
            "decision_id": "fixture-decision", "hypothesis": "Fixture only; no research result.",
        }
        self.candidate = b"# Frozen fixture candidate; never executed.\n"

    def patch(self, target: str, *args):
        patcher = patch(f"experiments.project_research.dispatch.{target}", *args)
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def fake_git(self, repository: Path, *arguments: str) -> str:
        if arguments == ("remote",):
            return ""
        if arguments[:2] == ("worktree", "add"):
            Path(arguments[2]).mkdir(parents=True)
            return ""
        if arguments == ("rev-parse", "HEAD"):
            return self.commit
        if arguments[:2] == ("add", "--") or (arguments and arguments[0] == "-c"):
            return ""
        raise AssertionError(f"unexpected git operation in fixture: {arguments}")

    def request_directory(self) -> Path:
        directories = list((self.control / "dispatches").iterdir())
        self.assertEqual(len(directories), 1)
        return directories[0]

    def test_same_spec_and_source_retry_reuses_frozen_intent(self) -> None:
        first = dispatch_module.dispatch(self.spec, "fixture-first-call", candidate=self.candidate)
        request_dir = self.request_directory()
        frozen_before = (request_dir / "frozen.json").read_bytes()
        request_before = (request_dir / "request.json").read_bytes()
        intent_path = request_dir / "launch.json"
        intent_path.write_text(json.dumps({"state": "UNKNOWN", "run_id": first["run_id"]}))
        intent_before = intent_path.read_bytes()

        # A wording change on retry must not create another research decision.
        second = dispatch_module.dispatch(dict(self.spec), "fixture-retry-label", candidate=bytes(self.candidate))

        self.assertEqual(first["intent_path"], second["intent_path"])
        self.assertEqual(first["run_id"], second["run_id"])
        self.run.assert_called_once()
        self.assertIn("create-experiment", self.run.call_args.args[0])
        self.assertEqual(self.adapter.attach_or_run.call_count, 2)
        first_call, retry_call = self.adapter.attach_or_run.call_args_list
        self.assertEqual(first_call, retry_call)
        self.assertEqual(retry_call.args, (self.experiment_id, self.commit, request_dir / "launch.json"))
        self.assertEqual(retry_call.kwargs, {"permit_launch": True})
        self.assertEqual((request_dir / "frozen.json").read_bytes(), frozen_before)
        self.assertEqual((request_dir / "request.json").read_bytes(), request_before)
        self.assertEqual(intent_path.read_bytes(), intent_before)
        self.assertEqual(self.request_directory(), request_dir)
        self.assertEqual(sum(call.args[1:3] == ("worktree", "add") for call in self.git.call_args_list), 1)
        self.store_type.return_value.event.assert_called_once()

    def test_lost_launch_response_reuses_existing_frozen_identity(self) -> None:
        self.adapter.attach_or_run.side_effect = [
            TimeoutError("fixture response lost after submitting the existing node"),
            {"state": "ATTACHED", "run_id": "33333333-3333-4333-8333-333333333333"},
        ]
        with self.assertRaises(TimeoutError):
            dispatch_module.dispatch(self.spec, "fixture-lost-launch", candidate=self.candidate)
        request_dir = self.request_directory()
        self.assertTrue((request_dir / "frozen.json").is_file())

        resumed = dispatch_module.dispatch(self.spec, "fixture-resume-launch", candidate=self.candidate)

        self.assertEqual(resumed["state"], "ATTACHED")
        self.run.assert_called_once()
        original, resumed_call = self.adapter.attach_or_run.call_args_list
        self.assertEqual(original, resumed_call)
        self.assertEqual(resumed_call.args[2], request_dir / "launch.json")
        self.assertEqual(self.request_directory(), request_dir)

    def test_ambiguous_create_timeout_blocks_new_node_on_retry(self) -> None:
        self.run.side_effect = subprocess.TimeoutExpired(["mock-orx", "create-experiment"], 30)
        with self.assertRaises(subprocess.TimeoutExpired):
            dispatch_module.dispatch(self.spec, "fixture-create-timeout", candidate=self.candidate)
        request_dir = self.request_directory()
        request_before = (request_dir / "request.json").read_bytes()
        self.assertFalse((request_dir / "frozen.json").exists())

        with self.assertRaisesRegex(RuntimeError, "requires reconciliation; no automatic replacement"):
            dispatch_module.dispatch(self.spec, "fixture-create-retry", candidate=self.candidate)

        self.run.assert_called_once()
        self.adapter.attach_or_run.assert_not_called()
        self.adapter.verify_experiment.assert_not_called()
        self.assertEqual((request_dir / "request.json").read_bytes(), request_before)
        self.assertEqual(self.request_directory(), request_dir)

    def test_unparseable_successful_create_response_also_blocks_replacement(self) -> None:
        self.run.return_value = subprocess.CompletedProcess(
            args=["mock-orx"], returncode=0, stdout="fixture response without the created node ID\n", stderr="",
        )
        with self.assertRaises(KeyError):
            dispatch_module.dispatch(self.spec, "fixture-incomplete-response", candidate=self.candidate)
        request_dir = self.request_directory()
        self.assertTrue((request_dir / "create-output.txt").is_file())

        with self.assertRaisesRegex(RuntimeError, "requires reconciliation; no automatic replacement"):
            dispatch_module.dispatch(self.spec, "fixture-parse-retry", candidate=self.candidate)

        self.run.assert_called_once()
        self.adapter.attach_or_run.assert_not_called()
        self.assertFalse((request_dir / "frozen.json").exists())
        self.assertEqual(self.request_directory(), request_dir)


if __name__ == "__main__":
    unittest.main()
