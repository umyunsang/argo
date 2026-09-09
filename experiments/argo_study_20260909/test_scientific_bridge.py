"""Synthetic admission, custody and lifecycle tests; no live ORX launches."""
from __future__ import annotations

import dataclasses
import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

import candidate_entry
import scientific_bridge as bridge
from scoring import canonical_config, content_sha256, file_sha256, fit

PARENT = "11111111-1111-1111-1111-111111111111"
PROJECT = "22222222-2222-2222-2222-222222222222"
IMAGE = os.environ.get("STUDY_TEST_IMAGE", "sha256:" + "a" * 64)


def public_metadata() -> dict:
    return {"target_column": "class", "feature_columns": ["x", "empty", "kind"], "numeric_columns": ["x", "empty"],
            "categorical_columns": ["kind"], "class_mapping": ["negative", "positive"], "classes": [0, 1],
            "row_counts": {"dev": 4, "test": 4}, "files_sha256": {}}


class FakeBackend:
    def __init__(self, statuses=None):
        self.calls = []
        self.statuses = list(statuses or [])

    def run(self, spec, source, event):
        self.calls.append((spec, source))
        number = len(self.calls)
        experiment_id = f"00000000-0000-0000-0000-{number:012d}"
        event({"phase": "RUNNING", "experiment_id": experiment_id, "run_id": experiment_id, "commit": "c" * 40})
        status = self.statuses.pop(0) if self.statuses else "VALID"
        if status == "RAISE":
            raise RuntimeError("simulated lost launch response")
        result = {"status": status, "experiment_id": experiment_id, "run_id": experiment_id, "commit": "c" * 40}
        if status == "VALID":
            result["balanced_accuracy"] = 0.91 if spec["kind"] == "final" else 0.75
        return result


class BridgeFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.episode = self.root / "episode"
        self.workspace = self.episode / "workspace"
        self.control = self.episode / "control"
        self.private = self.control / "scientific"
        self.custody = self.root / "synthetic-custody"
        self.repo = self.root / "project"
        for directory in (self.workspace, self.private, self.custody, self.repo, self.episode / "artifacts"):
            directory.mkdir(parents=True)
        self.kernel_path = self.control / "kernel.json"
        self.kernel_path.write_text("{}")
        self.cfg = bridge.EpisodeConfig(self.workspace, self.custody, public_metadata(), self.private, self.kernel_path,
                                        PROJECT, self.repo, IMAGE, time.time() + 3600, parent_experiment_id=PARENT)
        self.backend = FakeBackend()
        self.service = bridge.ScientificBridge(self.cfg, self.backend)
        (self.workspace / "solution.py").write_text("def fit(X, y, config):\n    return None\n")

    def tearDown(self):
        self.temporary.cleanup()

    def candidate(self, number=1, **kwargs):
        return self.service.run_candidate(config={"version": number}, hypothesis="Synthetic alternative", **kwargs)

    def test_initial_baseline_charged_and_parent_bound(self):
        result = self.service.initialize()
        self.assertEqual(result["feedback_slot"], 1)
        self.assertEqual(self.backend.calls[0][0]["parent_experiment_id"], PARENT)
        self.assertEqual(self.backend.calls[0][1], bridge.BASELINE_SOURCE)
        self.assertEqual(self.backend.calls[0][0]["config"]["model_parameters"]["n_estimators"], 100)

    def test_duplicate_request_reuses_identical_receipt(self):
        first = self.service.initialize()
        self.assertEqual(first, self.service.initialize())
        result = self.candidate()
        self.assertEqual(result, self.candidate())
        self.assertEqual(len(self.backend.calls), 2)
        self.assertEqual(self.service.list_results()["feedback_used"], 2)

    def test_observed_candidate_source_and_config_are_addressable_without_labels(self):
        base = self.service.initialize()
        source = self.service.read_candidate(base["candidate_id"], length=20)
        self.assertEqual(source["text"], bridge.BASELINE_SOURCE.decode()[:20])
        config = self.service.read_candidate(base["candidate_id"], kind="config")
        self.assertEqual(json.loads(config["text"])["model_parameters"]["n_estimators"], 100)
        self.assertEqual(self.service.list_results()["feedback_used"], 1)
        for args in [("../escape",), (base["candidate_id"], "labels"), (base["candidate_id"], "source", -1), (base["candidate_id"], "source", 0, 4001)]:
            with self.subTest(args=args), self.assertRaises(bridge.BridgeError):
                self.service.read_candidate(*args)
        (self.private / base["candidate_id"] / "solution.py").write_text("changed")
        with self.assertRaisesRegex(bridge.BridgeError, "CANDIDATE_SOURCE_CHANGED"):
            self.service.read_candidate(base["candidate_id"])

    def test_failures_consume_slots_and_thirteenth_is_refused(self):
        self.service.initialize()
        self.backend.statuses = ["AGENT_INVALID"] * 11
        for number in range(1, 12):
            self.assertEqual(self.candidate(number)["status"], "AGENT_INVALID")
        with self.assertRaisesRegex(bridge.BridgeError, "FEEDBACK_EXHAUSTED"):
            self.candidate(13)
        self.assertEqual(len(self.backend.calls), 12)

    def test_unknown_launch_stops_and_never_relaunches(self):
        self.service.initialize()
        self.backend.statuses = ["RAISE"]
        unknown = self.candidate()
        self.assertEqual(unknown["status"], "UNKNOWN")
        self.assertEqual(self.candidate(), unknown)
        with self.assertRaisesRegex(bridge.BridgeError, "UNKNOWN_RUN"):
            self.candidate(2)
        self.assertEqual(len(self.backend.calls), 2)

    def test_admitted_pending_intent_is_not_retried_after_restart(self):
        self.service.initialize()
        state = json.loads(self.service.state_path.read_text())
        state["candidates"][0].pop("receipt")
        state["candidates"][0]["status"] = "PENDING"
        bridge.atomic_json(self.service.state_path, state)
        restarted = bridge.ScientificBridge(self.cfg, self.backend)
        self.assertEqual(restarted.initialize()["status"], "UNKNOWN")
        with self.assertRaises(bridge.BridgeError):
            restarted.run_candidate(config={}, hypothesis="New")
        self.assertEqual(len(self.backend.calls), 1)

    def test_parent_must_have_been_observed_in_this_episode(self):
        base = self.service.initialize()
        result = self.candidate(parent_experiment_id=base["experiment_id"])
        self.assertEqual(self.backend.calls[1][0]["parent_experiment_id"], base["experiment_id"])
        self.assertEqual(self.backend.calls[1][0]["parent_commit"], base["commit"])
        self.candidate(2)
        self.assertEqual(self.backend.calls[2][0]["parent_experiment_id"], result["experiment_id"])
        with self.assertRaisesRegex(bridge.BridgeError, "PARENT_NOT_OBSERVED"):
            self.candidate(3, parent_experiment_id=PARENT)

    def test_one_verified_lock_closes_selection_and_final_score_is_withheld(self):
        base = self.service.initialize()
        chosen = self.candidate()
        self.service.lock_candidate(chosen["candidate_id"])
        with self.assertRaisesRegex(bridge.BridgeError, "FINAL_SELECTION_CLOSED"):
            self.service.lock_candidate(base["candidate_id"])
        with self.assertRaises(bridge.BridgeError):
            self.candidate(2)
        final = self.service.finalize()
        self.assertEqual(final, {"status": "FINAL_WITHHELD", "candidate_id": chosen["candidate_id"]})
        self.assertEqual(self.service.finalize(), final)
        self.assertEqual(len(self.backend.calls), 3)
        self.assertNotIn("0.91", json.dumps(self.service.list_results()))
        self.assertEqual(json.loads((self.private / "final-private-receipt.json").read_text())["balanced_accuracy"], 0.91)
        self.assertEqual(self.backend.calls[-1][0]["config"], self.backend.calls[1][0]["config"])
        self.assertEqual(self.backend.calls[-1][1], self.backend.calls[1][1])

    def test_default_finalization_does_not_select_last_candidate(self):
        base = self.service.initialize()
        self.candidate()
        final = self.service.finalize()
        self.assertEqual(final["candidate_id"], base["candidate_id"])

    def test_invalid_candidate_cannot_be_explicitly_locked(self):
        self.service.initialize()
        self.backend.statuses = ["AGENT_INVALID"]
        result = self.candidate()
        with self.assertRaisesRegex(bridge.BridgeError, "UNVERIFIED_FINAL"):
            self.service.lock_candidate(result["candidate_id"])

    def test_changed_locked_source_prevents_refit_and_keeps_spent_attempt(self):
        base = self.service.initialize()
        (self.private / base["candidate_id"] / "solution.py").write_text("changed")
        with self.assertRaisesRegex(bridge.BridgeError, "LOCKED_RECIPE_CHANGED"):
            self.service.finalize()
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(json.loads(self.service.state_path.read_text())["final_refits"], 1)

    def test_workspace_traversal_symlinks_and_hardlinks_rejected(self):
        self.service.initialize()
        outside = self.root / "private.py"
        outside.write_text("synthetic private sentinel")
        (self.workspace / "linked.py").symlink_to(outside)
        (self.workspace / "directory").symlink_to(self.root, target_is_directory=True)
        os.link(outside, self.workspace / "hard.py")
        for source in ("../private.py", str(outside), "linked.py", "directory/private.py", "hard.py"):
            with self.subTest(source=source), self.assertRaises(bridge.BridgeError):
                self.service.run_candidate(relative_source=source, hypothesis="Unsafe path")
        self.assertEqual(len(self.backend.calls), 1)

    def test_config_change_and_final_wall_reserve_are_enforced(self):
        self.service.initialize()
        changed = bridge.ScientificBridge(dataclasses.replace(self.cfg, image="sha256:" + "b" * 64), self.backend)
        with self.assertRaisesRegex(bridge.BridgeError, "EPISODE_CONFIG_CHANGED"):
            changed.list_results()
        with patch.object(bridge.time, "time", return_value=self.cfg.deadline_epoch - 599):
            with self.assertRaisesRegex(bridge.BridgeError, "FINAL_WALL_RESERVE"):
                self.candidate()

    def test_configuration_must_keep_private_custody_outside_worker_mounts(self):
        path = self.control / "episode.json"
        path.write_text(json.dumps(self.cfg.to_json()))
        loaded = bridge.load_episode_config(path, study_root=self.root)
        self.assertEqual(loaded, self.cfg)
        raw = self.cfg.to_json()
        raw["private_artifact_dir"] = str(self.episode / "artifacts")
        path.write_text(json.dumps(raw))
        with self.assertRaisesRegex(bridge.BridgeError, "ARTIFACT_CUSTODY_MUST_BE_PRIVATE"):
            bridge.load_episode_config(path, study_root=self.root)


class CandidateEntryTests(unittest.TestCase):
    def test_synthetic_baseline_artifact_contract_matches_canonical_oracle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            app, data, output, prediction = [root / name for name in ("app", "data", "fit", "predict")]
            for path in (app, data, output, prediction):
                path.mkdir()
            metadata = public_metadata()
            config = canonical_config(metadata)
            (app / "solution.py").write_bytes(bridge.BASELINE_SOURCE)
            (app / "public.json").write_text(json.dumps(metadata))
            (app / "config.json").write_text(json.dumps(config))
            frame = pd.DataFrame({"x": [0, 1, 2, 3, 4, 5], "empty": [np.nan] * 6, "kind": ["a", None, "NA", "b", "b", "b"]})
            labels = np.array([0, 0, 0, 1, 1, 1])
            train = frame.copy()
            train["class"] = labels
            train.to_csv(data / "train.csv", index=False)
            candidate_entry.run("fit", app, data, output)
            shutil.copyfile(output / "model.joblib", data / "model.joblib")
            frame.to_csv(data / "features.csv", index=False)
            candidate_entry.run("predict", app, data, prediction)
            predictions = json.loads((prediction / "predictions.json").read_text())
            np.testing.assert_array_equal(predictions, fit(frame, labels, config).predict(frame))


class EpisodeDispatchTests(unittest.TestCase):
    setUp = BridgeFixture.setUp
    tearDown = BridgeFixture.tearDown

    def snapshot(self):
        snapshot = self.root / "episode-snapshot"
        snapshot.mkdir()
        for name in bridge.RUNTIME_FILES:
            shutil.copyfile(Path(bridge.__file__).parent / name, snapshot / name)
        for name in ("controller.ts", "model_meter.ts"):
            (snapshot / name).write_text("// synthetic fixture only\n")
        config_path = self.control / "episode.json"
        config_path.write_text(json.dumps(self.cfg.to_json()))
        spec = {
            "schema": "study-node-spec/v1", "kind": "episode", "intent_id": "synthetic-episode",
            "episode_config": str(config_path), "episode_config_sha256": file_sha256(config_path),
            "runtime_sha256": {name: file_sha256(snapshot / name) for name in (*bridge.RUNTIME_FILES, "controller.ts", "model_meter.ts")},
        }
        (snapshot / "node-spec.json").write_text(json.dumps(spec))
        return snapshot, spec, config_path

    def test_only_valid_and_agent_invalid_are_propagated(self):
        snapshot, _, _ = self.snapshot()
        for status in ("VALID", "AGENT_INVALID", "UNKNOWN", "CONTROLLER_FAILED", "FINAL_WITHHELD", None):
            with self.subTest(status=status):
                summary = {"schema": "study-episode-summary/v1", "status": status}
                result = bridge.CommandResult(0, json.dumps(summary), "")
                with patch.object(bridge, "load_episode_config", return_value=self.cfg), patch.object(bridge, "command", return_value=result) as launch:
                    receipt = bridge.execute_spec(snapshot)
                self.assertEqual(receipt["status"], status if status in ("VALID", "AGENT_INVALID") else "UNKNOWN")
                self.assertEqual(receipt["episode_summary"], summary)
                launch.assert_called_once()

    def test_changed_controller_meter_or_python_runtime_prevents_launch(self):
        snapshot, _, _ = self.snapshot()
        for name in ("controller.ts", "model_meter.ts", "kernel_wrapper.py"):
            original = (snapshot / name).read_bytes()
            (snapshot / name).write_bytes(original + b"\nchanged fixture\n")
            with self.subTest(name=name), patch.object(bridge, "command") as launch, patch.object(bridge, "load_episode_config") as load:
                receipt = bridge.execute_spec(snapshot)
                self.assertEqual(receipt["status"], "UNKNOWN")
                self.assertEqual(receipt["reason"], "EPISODE_RUNTIME_CHANGED")
                launch.assert_not_called()
                load.assert_not_called()
            (snapshot / name).write_bytes(original)

    def test_external_host_config_requires_exact_bytes(self):
        snapshot, _, config_path = self.snapshot()
        config_path.write_text(json.dumps(self.cfg.to_json(), indent=2))
        with patch.object(bridge, "command") as launch, patch.object(bridge, "load_episode_config") as load:
            receipt = bridge.execute_spec(snapshot)
        self.assertEqual(receipt["status"], "UNKNOWN")
        self.assertEqual(receipt["reason"], "EPISODE_CONFIG_CHANGED")
        launch.assert_not_called()
        load.assert_not_called()

    def test_missing_required_runtime_hash_prevents_launch(self):
        snapshot, spec, _ = self.snapshot()
        del spec["runtime_sha256"]["model_meter.ts"]
        (snapshot / "node-spec.json").write_text(json.dumps(spec))
        with patch.object(bridge, "command") as launch:
            receipt = bridge.execute_spec(snapshot)
        self.assertEqual(receipt["status"], "UNKNOWN")
        self.assertEqual(receipt["reason"], "EPISODE_RUNTIME_MANIFEST_INCOMPLETE")
        launch.assert_not_called()

    def test_missing_config_hash_or_config_change_during_validation_prevents_launch(self):
        snapshot, spec, config_path = self.snapshot()
        bound_spec = json.loads(json.dumps(spec))
        del spec["episode_config_sha256"]
        (snapshot / "node-spec.json").write_text(json.dumps(spec))
        with patch.object(bridge, "command") as launch:
            self.assertEqual(bridge.execute_spec(snapshot)["reason"], "EPISODE_CONFIG_CHANGED")
            launch.assert_not_called()
        (snapshot / "node-spec.json").write_text(json.dumps(bound_spec))
        def change_config(path):
            config_path.write_text("changed synthetic fixture")
            return self.cfg
        with patch.object(bridge, "load_episode_config", side_effect=change_config), patch.object(bridge, "command") as launch:
            receipt = bridge.execute_spec(snapshot)
        self.assertEqual(receipt["status"], "UNKNOWN")
        self.assertEqual(receipt["reason"], "EPISODE_CONFIG_CHANGED")
        launch.assert_not_called()

    def test_malformed_summary_or_failed_process_cannot_be_valid(self):
        snapshot, _, _ = self.snapshot()
        valid = json.dumps({"schema": "study-episode-summary/v1", "status": "VALID"})
        for result in (bridge.CommandResult(1, valid, ""), bridge.CommandResult(0, "not json", ""), bridge.CommandResult(0, "[]", "")):
            with self.subTest(result=result), patch.object(bridge, "load_episode_config", return_value=self.cfg), patch.object(bridge, "command", return_value=result):
                receipt = bridge.execute_spec(snapshot)
                self.assertEqual(receipt["status"], "UNKNOWN")


class RunnerTests(unittest.TestCase):
    setUp = BridgeFixture.setUp
    tearDown = BridgeFixture.tearDown
    def snapshot(self, *, final=False):
        self.service.initialize()
        recipe = self.backend.calls[0][0]
        snapshot = self.root / "snapshot"
        snapshot.mkdir()
        for name in bridge.RUNTIME_FILES:
            shutil.copyfile(Path(bridge.__file__).parent / name, snapshot / name)
        for name, content in {
            "inner_train.csv": "x,empty,kind,class\n0,,a,0\n1,,b,1\n",
            "outer_train.csv": "x,empty,kind,class\n0,,a,0\n1,,b,1\n",
            "dev_X.csv": "x,empty,kind\n0,,a\n1,,b\n2,,a\n3,,b\n",
            "test_X.csv": "x,empty,kind\n0,,a\n1,,b\n2,,a\n3,,b\n",
            "dev_y.csv": "class\n0\n1\n0\n1\n", "test_y.csv": "class\n0\n1\n0\n1\n",
        }.items():
            (self.custody / name).write_text(content)
        metadata = self.cfg.metadata.copy()
        metadata["files_sha256"] = {path.name: file_sha256(path) for path in self.custody.iterdir()}
        spec = {**recipe, "kind": "final" if final else "candidate", "episode": {**self.cfg.to_json(), "metadata": metadata}}
        (snapshot / "node-spec.json").write_text(json.dumps(spec))
        (snapshot / "solution.py").write_bytes(bridge.BASELINE_SOURCE)
        (snapshot / "config.json").write_text(json.dumps(spec["config"]))
        (snapshot / "public.json").write_text(json.dumps(spec["public_schema"]))
        return snapshot, SimpleNamespace(image=IMAGE, deadline_epoch=self.cfg.deadline_epoch, max_cpu_seconds=7200,
                                         control_dir=self.control, docker="/docker", pids_limit=128)

    def test_fit_and_prediction_custody_separate_and_scorer_returns_only_scalar(self):
        snapshot, kernel = self.snapshot()
        calls = []
        def sandbox(config_path, app, output, inputs, stage, *, final):
            calls.append((stage, inputs, final, set(path.name for path in app.iterdir())))
            if stage == "fit":
                (output / "model.joblib").write_bytes(b"synthetic opaque pickle fixture")
            else:
                (output / "predictions.json").write_text("[0,1,0,1]")
        with patch.object(bridge, "load_kernel_config", return_value=kernel):
            result = bridge.execute_spec(snapshot, sandbox)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["balanced_accuracy"], 1)
        self.assertEqual(set(calls[0][1]), {"train.csv"})
        self.assertEqual(set(calls[1][1]), {"model.joblib", "features.csv"})
        self.assertFalse(any("scoring.py" in call[3] for call in calls))
        self.assertNotIn("labels", result)

    def test_invalid_vector_is_agent_failure_and_private_scorer_is_not_called(self):
        snapshot, kernel = self.snapshot()
        def sandbox(config_path, app, output, inputs, stage, *, final):
            (output / ("model.joblib" if stage == "fit" else "predictions.json")).write_bytes(b"opaque" if stage == "fit" else b"[0,99,0,1]")
        with patch.object(bridge, "load_kernel_config", return_value=kernel), patch.object(bridge, "score_private_labels", side_effect=AssertionError("private scorer reached")):
            result = bridge.execute_spec(snapshot, sandbox)
        self.assertEqual(result["status"], "AGENT_INVALID")

    def test_custody_hash_change_is_trusted_unknown_before_launch(self):
        snapshot, kernel = self.snapshot()
        (self.custody / "dev_X.csv").write_text("changed")
        with patch.object(bridge, "load_kernel_config", return_value=kernel), patch.object(bridge, "run_sandbox", side_effect=AssertionError("launch")) as sandbox:
            result = bridge.execute_spec(snapshot, sandbox)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["reason"], "CUSTODY_INPUT_CHANGED")

    def test_final_uses_outer_train_and_test_only(self):
        snapshot, kernel = self.snapshot(final=True)
        calls = []
        def sandbox(config_path, app, output, inputs, stage, *, final):
            calls.append((stage, inputs, final))
            (output / ("model.joblib" if stage == "fit" else "predictions.json")).write_bytes(b"opaque" if stage == "fit" else b"[0,1,0,1]")
        with patch.object(bridge, "load_kernel_config", return_value=kernel):
            result = bridge.execute_spec(snapshot, sandbox)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(calls[0][1]["train.csv"].name, "outer_train.csv")
        self.assertEqual(calls[1][1]["features.csv"].name, "test_X.csv")
        self.assertTrue(all(call[2] for call in calls))

    def test_docker_command_has_no_worker_private_labels_home_or_socket(self):
        snapshot, kernel = self.snapshot()
        output = self.private / "empty-output"
        output.mkdir()
        argv = bridge.docker_argv(kernel, "synthetic", snapshot, output, {"train.csv": self.custody / "inner_train.csv"}, "fit")
        joined = " ".join(argv)
        self.assertIn("--network none", joined)
        self.assertIn("--read-only", joined)
        self.assertIn("--memory-swap 4294967296", joined)
        self.assertIn("--cap-drop ALL", joined)
        self.assertNotIn("dev_y.csv", joined)
        self.assertNotIn("test_y.csv", joined)
        self.assertNotIn("docker.sock", joined)
        with self.assertRaises(bridge.BridgeError):
            bridge.docker_argv(kernel, "synthetic", snapshot, output, {"train.csv": self.custody / "inner_train.csv", "labels.csv": self.custody / "dev_y.csv"}, "fit")


class ORXParserTests(unittest.TestCase):
    def test_captured_create_and_status_surfaces_require_fixed_command(self):
        fixtures = Path(__file__).parents[1] / "argo_workflow_followup/public_ml_apparatus/house_price_runtime/orx_text_fixtures"
        created = (fixtures / "create-baseline.txt").read_text().replace("/usr/bin/python3 fixture.py", bridge.FIXED_COMMAND)
        title = bridge._fields(created)["title"]
        experiment, branch = bridge.parse_created(created, title)
        self.assertTrue(branch.startswith("orx/"))
        with self.assertRaises(bridge.BridgeError):
            bridge.parse_created(created.replace(bridge.FIXED_COMMAND, "python other.py"), title)
        status = (fixtures / "status-done.txt").read_text().replace("/usr/bin/python3 fixture.py", bridge.FIXED_COMMAND)
        experiment = bridge._fields(status)["id"]
        self.assertEqual(bridge.parse_status(status, experiment)["status"], "done")
        with self.assertRaises(bridge.BridgeError):
            bridge.parse_status(status, PARENT)


class ORXLifecycleTests(unittest.TestCase):
    setUp = BridgeFixture.setUp
    tearDown = BridgeFixture.tearDown

    def test_mocked_orx_commits_once_and_reconciles_status_transition_between_reads(self):
        self.service.initialize()
        spec, source = self.backend.calls[0]
        backend = bridge.ORXBackend(self.cfg)
        experiment = "33333333-3333-3333-3333-333333333333"
        run = "44444444-4444-4444-4444-444444444444"
        branch = "orx/synthetic"
        commit = "c" * 40
        title = "study-candidate-" + spec["intent_id"][:16]
        events, commands, git_commands = [], [], []
        launched = False
        running_status_reads = 0
        log_reads = 0
        def git(args, cwd=None):
            git_commands.append((args, cwd))
            if args == ["rev-parse", "--show-toplevel"]:
                return str(self.repo)
            if args[:2] == ["worktree", "add"]:
                Path(args[2]).mkdir()
            if args == ["rev-parse", "HEAD"]:
                return commit
            return ""
        def call(args, **kwargs):
            nonlocal launched, running_status_reads, log_reads
            commands.append(args)
            if args[0] == "create-experiment":
                return bridge.CommandResult(0, f"✓ Created local child experiment\n  id: {experiment}\n  title: {title}\n  command: {bridge.FIXED_COMMAND}\n  branch: {branch}\n", "")
            if args[:2] == ["exp", "status"]:
                observed_state = "running" if running_status_reads == 0 else "done"
                last = f"{run} ({observed_state}, commit {commit[:7]}, ran 1s, updated 1s)" if launched else "— (never run)"
                text = f"  id: {experiment}\n  command: {bridge.FIXED_COMMAND}\n  branch: {branch}\n  last run: {last}\n"
                if launched:
                    text += f"  commit: {commit}\n"
                    running_status_reads += 1
                return bridge.CommandResult(0, text, "")
            if args[0] == "runs":
                return bridge.CommandResult(0, f"{run}  done  {title}  {commit[:7]}  1s  1s\n" if launched else "No runs found.\n", "")
            if args[:2] == ["exp", "run"]:
                self.assertEqual(events[-1]["phase"], "LAUNCH_INTENT")
                self.assertIn(["--backend", "local"], [args[-2:]])
                self.assertNotIn("--force", args)
                launched = True
                return bridge.CommandResult(0, f"  run  {run}\n", "")
            if args[:2] == ["exp", "wait"]:
                return bridge.CommandResult(0, "done\n", "")
            if args[0] == "logs":
                log_reads += 1
                if log_reads == 1:
                    return bridge.CommandResult(0, "", "[local file] bytes 0–0 of 0\n")
                committed = json.loads((self.private / ("worktree-" + spec["intent_id"]) / "node-spec.json").read_text())
                receipt = {"status": "VALID", "balanced_accuracy": 0.65, "spec_sha256": content_sha256(committed), "intent_id": spec["intent_id"]}
                output = json.dumps(receipt) + "\n"
                return bridge.CommandResult(0, output, f"[local file] bytes 0–{len(output)} of {len(output)}\n")
            raise AssertionError(args)
        with patch.object(backend, "git", side_effect=git), patch.object(backend, "call", side_effect=call):
            result = backend.run(spec, source, events.append)
        self.assertEqual(result["balanced_accuracy"], 0.65)
        self.assertEqual(result["commit"], commit)
        self.assertEqual(sum(args[:2] == ["exp", "run"] for args in commands), 1)
        self.assertEqual(running_status_reads, 2)
        self.assertEqual(log_reads, 2)
        self.assertTrue(any(args[0] == "add" and "node-spec.json" in args for args, _ in git_commands))
        self.assertFalse(any(args[0] in {"push", "reset", "rebase", "merge"} for args, _ in git_commands))


@unittest.skipUnless(os.environ.get("STUDY_TEST_IMAGE"), "explicit immutable synthetic Docker image required")
class DockerSyntheticTests(unittest.TestCase):
    def test_real_container_fit_predict_and_shared_resource_release(self):
        bridge.STUDY_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="synthetic-bridge-", dir=bridge.STUDY_ROOT) as temporary:
            root = Path(temporary).resolve()
            workspace, artifacts, control = [root / name for name in ("workspace", "artifacts", "control")]
            for path in (workspace, artifacts, control):
                path.mkdir(mode=0o700)
            app, fit_output, predict_output = [control / name for name in ("app", "fit", "predict")]
            for path in (app, fit_output, predict_output):
                path.mkdir(mode=0o700)
            config_path = control / "kernel.json"
            config_path.write_text(json.dumps({"image": IMAGE, "workspace": str(workspace), "artifact_root": str(artifacts),
                                                "control_dir": str(control), "deadline_epoch": time.time() + 1800}))
            metadata = public_metadata()
            (app / "public.json").write_text(json.dumps(metadata))
            (app / "config.json").write_text(json.dumps(canonical_config(metadata)))
            (app / "solution.py").write_bytes(bridge.BASELINE_SOURCE)
            shutil.copyfile(Path(candidate_entry.__file__), app / "candidate_entry.py")
            train = control / "synthetic-train.csv"
            train.write_text("x,empty,kind,class\n0,,a,0\n1,,a,0\n2,,NA,0\n3,,b,1\n4,,b,1\n5,,b,1\n")
            features = control / "synthetic-features.csv"
            features.write_text("x,empty,kind\n0,,a\n5,,b\n")
            bridge.run_sandbox(config_path, app, fit_output, {"train.csv": train}, "fit", final=False)
            bridge.run_sandbox(config_path, app, predict_output, {"features.csv": features, "model.joblib": fit_output / "model.joblib"}, "predict", final=False)
            self.assertEqual(json.loads((predict_output / "predictions.json").read_text()), [0, 1])
            pool = json.loads((control / "resource-pool.json").read_text())
            self.assertEqual(pool["active"], {})
            self.assertEqual(len(pool["completed"]), 2)
            self.assertGreater(pool["conservative_cpu_seconds"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
