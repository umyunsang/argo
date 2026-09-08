from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import parse_session_usage
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance import (
    CombinationExpectation,
    assess_combination,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    CleanupReceipt,
    ControllerRunReceipt,
    InterpreterIdentity,
    PathIdentity,
    ProcessHandleReceipt,
    ResourceObservationReceipt,
    RunControllerCaps,
    RunControllerConfig,
    config_to_dict,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import ClosureError, SourceTree
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import UsageObserver, UsageObserverConfig

CONTEXT = "b" * 64
SESSION_ID = "11111111-1111-4111-8111-111111111111"
RUN_IDS = ("22222222-2222-4222-8222-222222222222", "33333333-3333-4333-8333-333333333333")
RESPONSE_IDS = ("a2-combination-response-0001", "a2-combination-response-0002")
TOOL_ID = "a2-combination-tool-0001"
FINAL_TEXT = "A2 synthetic combination frontend complete."
NORMAL_SHA = "dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21"
FAUX_SHA = "4c9b73b8d759fd0dd0061c84dd28a658452eaed6175fda4ba23ff4b60e6b09d6"


class CombinationAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="argo-a2-combination-accept-")
        self.root = Path(self.temp.name).resolve()
        os.chmod(self.root, 0o700)
        self.artifact = self.directory("artifact")
        self.session = self.directory("artifact/session")
        self.tmp = self.directory("artifact/tmp")
        self.profile = self.directory("profile")
        self.cwd = self.directory("cwd")
        self.gate_outcomes = self.directory("gate-outcomes")
        self.state_roots = tuple(self.directory(name) for name in ("source", "trusted", "bridge-state"))
        self.namespace = self.directory("namespace")
        self.frontend = self.directory("frontend")
        self.prime = Path("/opt/homebrew/lib/node_modules/prime-agent").resolve(strict=True)
        (self.state_roots[0] / "research.md").write_text("synthetic research\n", encoding="utf-8")
        self.research_sha = hashlib.sha256(b"synthetic research\n").hexdigest()
        self.normal_frontend = self.frontend / "controller-main.ts"
        normal_source = Path(__file__).with_name("controller-main.ts").read_bytes()
        self.normal_frontend.write_bytes(normal_source)
        os.chmod(self.normal_frontend, 0o600)
        self.synthetic_frontend_path = self.frontend / "a2-combination-frontend.ts"
        faux_source = Path(__file__).with_name("a2-frontend-probes").joinpath("a2-combination-frontend.ts").read_bytes()
        self.synthetic_frontend_path.write_bytes(faux_source)
        os.chmod(self.synthetic_frontend_path, 0o600)
        self.synthetic_frontend = self.binding(self.synthetic_frontend_path)
        self.assertEqual(self.synthetic_frontend.sha256, FAUX_SHA)
        self.process_exec = self.namespace / "process_exec.py"
        self.process_exec.write_bytes(Path(__file__).with_name("process_exec.py").read_bytes())
        os.chmod(self.process_exec, 0o600)
        self.node = self.file("node", b"node", 0o700)
        self.kernel_target = self.file("kernel-target", b"python", 0o700)
        self.pyvenv = self.file("pyvenv.cfg", b"home = synthetic\n", 0o600)
        self.task_prompt_text = "Use read_public_result once, then stop.\n"
        self.task_prompt = self.file(
            "frontend/task.md",
            self.task_prompt_text.encode("utf-8"),
            0o600,
        )
        self.deployment = self.file(
            "deployment.json",
            self.canonical(self.deployment_value()),
            0o600,
        )
        self.bridge_config = self.bound_data("bridge-config.json", self.bridge_config_value())
        self.normal_config = self.process_config(self.normal_frontend, NORMAL_SHA)
        self.synthetic_config = self.process_config(self.synthetic_frontend_path, FAUX_SHA)
        self.normal_config_binding = self.bound_data("normal-process-config.json", config_to_dict(self.normal_config))
        self.synthetic_config_binding = self.bound_data("synthetic-process-config.json", config_to_dict(self.synthetic_config))
        self.public_result = self.public_value()
        self.session_binding = self.write_session(self.session_records())
        self.process_receipt = self.write_process_receipt(0)
        self.metadata = self.write_metadata()
        self.gate_config = self.bound_data("frontend/gate-config.json", self.gate_config_value())
        self.latest_binding, self.latest, self.checkpoint = self.make_latest_gate()
        self.expectation = CombinationExpectation(
            controller_context_id=CONTEXT,
            normal_process_config=self.normal_config_binding,
            synthetic_process_config=self.synthetic_config_binding,
            process_receipt=self.process_receipt,
            gate_config=self.gate_config,
            metadata=self.metadata,
            current_session=self.session_binding,
            current_session_id=SESSION_ID,
            synthetic_frontend=self.synthetic_frontend,
            verified_dev_run_ids=RUN_IDS,
            research_sha256=self.research_sha,
            state_trees=tuple(self.tree(path) for path in self.state_roots),
            namespace_tree=self.tree(self.namespace),
            frontend_tree=self.tree(self.frontend),
            installed_prime_tree=self.tree(self.prime),
            elapsed_limit_seconds=20,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def directory(self, relative: str) -> Path:
        path = self.root / relative
        path.mkdir(parents=True, exist_ok=True)
        os.chmod(path, 0o700)
        return path

    def file(self, relative: str, data: bytes, mode: int) -> Path:
        path = self.root / relative
        path.write_bytes(data)
        os.chmod(path, mode)
        return path

    def binding(self, path: Path) -> FileBinding:
        data = path.read_bytes()
        info = path.stat()
        return FileBinding(path, hashlib.sha256(data).hexdigest(), len(data), info.st_mtime_ns)

    def bound_data(self, relative: str, value: object) -> FileBinding:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        return self.binding(self.file(relative, data, 0o600))

    def directory_identity(self, path: Path) -> DirectoryIdentity:
        info = path.stat()
        return DirectoryIdentity(path, info.st_dev, info.st_ino)

    def path_identity(self, path: Path, sha256: str | None = None) -> PathIdentity:
        info = path.stat()
        return PathIdentity(
            str(path), "regular_file", info.st_dev, info.st_ino, info.st_mode & 0o777,
            info.st_uid, info.st_size, info.st_mtime_ns,
            sha256 or hashlib.sha256(path.read_bytes()).hexdigest(),
        )

    def directory_path_identity(self, path: Path) -> PathIdentity:
        info = path.stat()
        return PathIdentity(
            str(path), "directory", info.st_dev, info.st_ino, info.st_mode & 0o777,
            info.st_uid, info.st_size, info.st_mtime_ns, None,
        )

    def tree(self, path: Path) -> SourceTree:
        info = path.stat()
        return SourceTree(str(path), info.st_dev, info.st_ino, "e" * 64, 1, 0, 0, 1, info.st_mtime_ns)

    def caps(self) -> RunControllerCaps:
        return RunControllerCaps(
            provider_timeout_ms=120000, provider_retries=0,
            phase_wall_seconds=3600, campaign_wall_seconds=10800,
            cpu_seconds_per_process=600, file_size_bytes=8388608,
            rss_trigger_bytes=2147483648, rss_sample_ms=250, v8_old_space_mib=1024,
            model_tokens_between_turns=120000, controller_turn_limit_per_phase=20,
            source_text_max_bytes=131072, autonomous_gate_retries=20,
            autonomous_gate_timeout_ms=30000, bridge_close_grace_ms=1000,
            artifact_aggregate_bytes=67108864, artifact_file_count=128,
            terminate_grace_seconds=2, kill_grace_seconds=2,
            observer_timeout_seconds=3, observer_output_bytes=8388608,
        )

    def file_seal(self, path: Path) -> dict[str, object]:
        binding = self.binding(path)
        return {
            "path": str(path),
            "sha256": binding.sha256,
            "bytes": binding.bytes,
            "mtime_ns_max": str(binding.mtime_ns_max),
        }

    def directory_seal(self, path: Path, empty: bool) -> dict[str, object]:
        info = path.stat()
        return {
            "path": str(path),
            "realpath": str(path),
            "device": str(info.st_dev),
            "inode": str(info.st_ino),
            "mtime_ns_max": str(info.st_mtime_ns),
            "mode_octal": "0700",
            "must_be_empty": empty,
        }

    def deployment_value(self) -> dict[str, object]:
        generic = self.file_seal(self.normal_frontend)
        assets = {
            "prime_entry": generic,
            "prime_closure_manifest": generic,
            "controller_main": self.file_seal(self.normal_frontend),
            "frontend_closure_manifest": generic,
            "extension": generic,
            "binding": generic,
            "settings": generic,
            "system_prompt": generic,
            "task_prompt": self.file_seal(self.task_prompt),
            "autonomous_gate": generic,
            "node_executable": self.file_seal(self.node),
            "kernel_interpreter": {
                "invocation_path": "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python",
                "invocation_link": {"device": "1", "inode": "1", "mtime_ns_max": "1", "link_target": "python"},
                "resolved_target": self.file_seal(self.kernel_target),
                "pyvenv_cfg": self.file_seal(self.pyvenv),
            },
        }
        environment = {
            "PRIME_AGENT_CODING_AGENT_DIR": str(self.profile),
            "PRIME_AGENT_KERNEL_PYTHON": "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python",
            "PRIME_AGENT_TELEMETRY": "0",
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
            "TMPDIR": str(self.tmp) + "/",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
        }
        limits = {
            "provider_timeout_ms": 120000, "provider_retries": 0,
            "phase_wall_seconds": 3600, "campaign_wall_seconds": 10800,
            "cpu_seconds_per_process": 600, "file_size_bytes": 8388608,
            "rss_trigger_bytes": 2147483648, "rss_sample_ms": 250,
            "v8_old_space_mib": 1024, "model_tokens_between_turns": 120000,
            "controller_turn_limit_per_phase": 20, "source_text_max_bytes": 131072,
            "bridge_close_grace_ms": 1000, "autonomous_max_continuations": 20,
            "autonomous_gate_retries": 20, "autonomous_gate_timeout_ms": 30000,
        }
        return {
            "schema_version": "argo-house-price-a2-controller-main-deployment/v1",
            "status": "TRUSTED_FIXED_DEPLOYMENT",
            "assets": assets,
            "directories": {
                "artifact_root": self.directory_seal(self.artifact, False),
                "cwd": self.directory_seal(self.cwd, False),
                "profile": self.directory_seal(self.profile, False),
                "session_dir": self.directory_seal(self.session, True),
                "temporary_dir": self.directory_seal(self.tmp, True),
            },
            "runtime": {
                "phase": "dev", "model": "openai-codex/gpt-5.6-sol", "thinking": "xhigh",
                "mode": "text", "print": True, "offline": True, "fresh_session": True,
                "tools": ["read_solution", "write_solution", "request_R1_run", "read_public_result", "read_dev_result", "lock_final_artifact"],
            },
            "environment": {"exact": environment, "home_must_be_unset": True, "forbidden_prefixes": ["PRIME_AGENT_INTERNAL_"]},
            "limits": limits,
        }

    def process_config(self, frontend: Path, frontend_sha: str) -> RunControllerConfig:
        target = self.path_identity(self.kernel_target)
        pyvenv = self.path_identity(self.pyvenv)
        interpreter = InterpreterIdentity(
            "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python", (), target,
            str(self.pyvenv), pyvenv,
        )
        environment = {
            "PRIME_AGENT_CODING_AGENT_DIR": str(self.profile),
            "PRIME_AGENT_KERNEL_PYTHON": "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python",
            "PRIME_AGENT_TELEMETRY": "0",
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
            "TMPDIR": str(self.tmp) + "/",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
        }
        return RunControllerConfig(
            python_executable=interpreter.invocation_path,
            interpreter_identity=interpreter,
            process_exec_path=str(self.process_exec),
            process_exec_identity=self.path_identity(self.process_exec),
            node_executable=str(self.node), node_identity=self.path_identity(self.node),
            frontend_path=str(frontend), frontend_identity=self.path_identity(frontend, frontend_sha),
            deployment_path=str(self.deployment), deployment_identity=self.path_identity(self.deployment),
            artifact_root=str(self.artifact), artifact_root_identity=self.directory_path_identity(self.artifact),
            temporary_dir=str(self.tmp), temporary_dir_identity=self.directory_path_identity(self.tmp),
            session_dir=str(self.session), session_dir_identity=self.directory_path_identity(self.session),
            profile_dir=str(self.profile), profile_dir_identity=self.directory_path_identity(self.profile),
            child_environment=environment, caps=self.caps(),
            campaign_started_monotonic_ns=10, synthetic_test_context=False,
        )

    def public_value(self) -> dict[str, object]:
        runs = []
        experiment_ids = (
            "44444444-4444-4444-8444-444444444444",
            "55555555-5555-4555-8555-555555555555",
        )
        for index, run_id in enumerate(RUN_IDS, 1):
            runs.append({
                "intent_sha256": str(index) * 64,
                "run_id": run_id,
                "experiment_id": experiment_ids[index - 1],
                "solution_sha256": str(index+5) * 64,
                "phase": "dev", "status": "DONE",
            })
        return {
            "phase": "development", "dev_attempts": 2, "final_attempts": 0,
            "remaining_dev_opportunities": 1, "runs": runs,
        }

    def session_records(self) -> list[dict[str, object]]:
        tool_text = json.dumps(self.public_result, separators=(",", ":"))
        usage1 = {"input": 100, "output": 10, "cacheRead": 20, "cacheWrite": 30, "totalTokens": 160}
        usage2 = {"input": 80, "output": 8, "cacheRead": 10, "cacheWrite": 20, "totalTokens": 118}
        return [
            {"type": "session", "version": 3, "id": SESSION_ID, "cwd": str(self.cwd), "rlmDepth": 0},
            {"type": "model_change", "id": "m", "parentId": None, "provider": "openai-codex", "modelId": "gpt-5.6-sol"},
            {"type": "message", "id": "u", "parentId": "m", "message": {
                "role": "user",
                "content": [{"type": "text", "text": self.task_prompt_text}],
                "timestamp": 122,
            }},
            {"type": "message", "id": "a1", "parentId": "u", "message": {
                "role": "assistant", "provider": "openai-codex", "model": "gpt-5.6-sol",
                "responseId": RESPONSE_IDS[0], "stopReason": "toolUse", "usage": usage1,
                "content": [{"type": "toolCall", "id": TOOL_ID, "name": "read_public_result", "arguments": {}}],
            }},
            {"type": "message", "id": "t", "parentId": "a1", "message": {
                "role": "toolResult", "toolCallId": TOOL_ID, "toolName": "read_public_result",
                "content": [{"type": "text", "text": tool_text}], "details": {"action": "read_public_result"},
                "isError": False, "timestamp": 123,
            }},
            {"type": "message", "id": "a2", "parentId": "t", "message": {
                "role": "assistant", "provider": "openai-codex", "model": "gpt-5.6-sol",
                "responseId": RESPONSE_IDS[1], "stopReason": "stop", "usage": usage2,
                "content": [{"type": "text", "text": FINAL_TEXT}],
            }},
        ]

    def write_session(self, records: list[dict[str, object]]) -> FileBinding:
        path = self.session / f"{SESSION_ID}.jsonl"
        data = b"".join(json.dumps(record, separators=(",", ":")).encode("utf-8") + b"\n" for record in records)
        path.write_bytes(data)
        os.chmod(path, 0o600)
        return self.binding(path)

    def write_process_receipt(self, returncode: object) -> FileBinding:
        (self.artifact / "stdout").write_text(FINAL_TEXT + "\n", encoding="utf-8")
        (self.artifact / "stderr").write_bytes(b"")
        caps = self.synthetic_config.caps
        handle = ProcessHandleReceipt(
            123, 123, "strong", str(self.artifact / "stdout"), str(self.artifact / "stderr"), 1,
            self.synthetic_config.process_exec_path, self.synthetic_config.frontend_path,
            self.synthetic_config.deployment_path, str(self.artifact), str(self.session),
            tuple(sorted(self.synthetic_config.child_environment)), "DEVNULL",
        )
        resources = ResourceObservationReceipt(
            caps.provider_timeout_ms, caps.provider_retries, caps.model_tokens_between_turns,
            caps.controller_turn_limit_per_phase, caps.source_text_max_bytes,
            caps.autonomous_gate_retries, caps.autonomous_gate_timeout_ms, caps.bridge_close_grace_ms,
            "sampled_trigger_not_hard_limit", caps.rss_trigger_bytes, caps.rss_sample_ms,
            1000, 0, None, None, 1, 11, 11, 0.0, 0.0, True, (), (), 5, 1000, 500,
            0, 0, caps.artifact_file_count, caps.artifact_aggregate_bytes, caps.file_size_bytes,
            caps.cpu_seconds_per_process, caps.phase_wall_seconds, caps.campaign_wall_seconds,
            caps.observer_output_bytes, "unknown_not_zero",
        )
        cleanup = CleanupReceipt(True, False, True, True, (), (), (123,), (), (), ())
        receipt = ControllerRunReceipt(
            "argo-house-price-a2-controller-process-receipt/v1",
            "0cfaeb57c18662f428cdb9fbdef842d55782624b9baaf9bbbbe98ebeb4412c20",
            "succeeded", "completed", returncode, 11, 1_000_000_011, 1.0,
            handle, resources, cleanup, (),
        )
        value = receipt.to_dict()
        value["returncode"] = returncode
        return self.bound_data("controller-process-receipt.json", value)

    def bridge_config_value(self) -> dict[str, object]:
        return {
            "schema_version": "mock-bridge/v1",
            "context_rights": {
                "context": "initial", "initial_context_id": CONTEXT,
                "controller_context_id": CONTEXT,
            },
        }

    def gate_config_value(self) -> dict[str, object]:
        return {
            "schema_version": "argo-house-price-a2-phase-gate-deployment/v1",
            "context": "initial",
            "bridge_config": {
                "path": str(self.bridge_config.path),
                "sha256": self.bridge_config.sha256,
                "bytes": self.bridge_config.bytes,
                "mtime_ns_max": self.bridge_config.mtime_ns_max,
            },
            "session_directory": asdict(self.directory_identity(self.session)) | {"path": str(self.session)},
            "cwd": str(self.cwd), "provider": "openai-codex", "model": "gpt-5.6-sol",
            "budget": 120000, "prior_session": None, "prior_session_id": None, "prior_cwd": None,
            "final_lock_path": str(self.root / "final-artifact-lock.json"),
            "gate_outcome_directory": asdict(self.directory_identity(self.gate_outcomes)) | {"path": str(self.gate_outcomes)},
            "expected_rows": 292,
        }

    def make_latest_gate(self):
        observer = UsageObserver(UsageObserverConfig(
            self.directory_identity(self.session), str(self.cwd), "openai-codex", "gpt-5.6-sol", 120000, (),
        ))
        observation = observer.observe()
        checkpoint = observer.export_checkpoint()
        research = {"ok": True, "result": {
            "path": "research.md", "content": "synthetic research\n", "sha256": self.research_sha,
        }}
        public = {"ok": True, "result": self.public_result}
        latest = {
            "schema_version": "argo-house-price-a2-phase-gate-outcome/v2",
            "context": "initial", "config_sha256": self.gate_config.sha256,
            "bridge_config_sha256": self.bridge_config.sha256,
            "decision": {
                "outcome": "READY_INITIAL_CHECKPOINT", "ready": True, "stop": True,
                "verified_dev_run_ids": list(RUN_IDS), "selected_final_run_id": None,
            },
            "usage": asdict(observation),
            "view_sha256": {
                "public": hashlib.sha256(self.canonical(public)).hexdigest(),
                "dev": "d" * 64,
                "research": hashlib.sha256(self.canonical(research)).hexdigest(),
            },
            "final_lock_sha256": None, "sequence": 1, "previous_outcome_sha256": None,
            "usage_checkpoint": checkpoint,
        }
        binding = self.bound_data("gate-outcomes/0001-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json", latest)
        return binding, latest, checkpoint

    def write_metadata(self) -> FileBinding:
        value = {
            "schema_version": "argo-house-price-a2-synthetic-provider-metadata/v1",
            "test_only": True, "provider": "openai-codex", "model": "gpt-5.6-sol",
            "response_ids": list(RESPONSE_IDS), "provider_call_count": 2, "contexts_observed": 2,
            "tool_names": ["read_solution", "write_solution", "request_R1_run", "read_public_result", "read_dev_result", "lock_final_artifact"],
            "tool_schema_sha256": "553e00b05207cc51eaf80d3d58ff480279319990ce620409ea52a1e4d281ad61",
            "final_text_sha256": hashlib.sha256(FINAL_TEXT.encode()).hexdigest(),
            "usage_authority": "NATIVE_SESSION_ONLY", "production_provider_factory": False,
        }
        return self.bound_data("artifact/a2-synthetic-provider-metadata.json", value)

    def canonical(self, value: object) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

    def assess(self, expectation=None, *, latest=None, tree_error=None):
        value = self.expectation if expectation is None else expectation
        latest_value = self.latest if latest is None else latest
        verify_effect = tree_error if tree_error is not None else lambda root, expected, limits: expected
        with patch(
            "experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance.verify_tree",
            side_effect=verify_effect,
        ) as verify, patch(
            "experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance._latest_gate",
            return_value=(self.latest_binding, latest_value, self.checkpoint),
        ):
            result = assess_combination(value)
        self.verify_calls = verify.call_count
        return result

    def test_positive_verifies_one_synthetic_combination(self) -> None:
        result = self.assess()
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.reason, "VERIFIED_SYNTHETIC_COMBINATION")
        self.assertEqual(result.campaign_tokens, 278)
        self.assertEqual(result.session_sha256, self.session_binding.sha256)
        self.assertEqual(result.native_gate_sha256, self.latest_binding.sha256)
        self.assertEqual(result.native_gate_binding, self.latest_binding)
        self.assertEqual(self.verify_calls, 6)

    def test_task_prompt_asset_change_and_foreign_gate_location_reject(self) -> None:
        self.task_prompt.write_text("changed prompt\n", encoding="utf-8")
        self.assertEqual(self.assess().reason, "SOURCE_MISMATCH")

        self.task_prompt.write_text(self.task_prompt_text, encoding="utf-8")
        foreign_gate = self.bound_data("foreign-gate-config.json", self.gate_config_value())
        expectation = replace(self.expectation, gate_config=foreign_gate)
        self.assertEqual(self.assess(expectation).reason, "SOURCE_MISMATCH")

    def test_wrong_bound_user_prompt_rejects_with_consistent_session_and_gate(self) -> None:
        records = self.session_records()
        records[2]["message"]["content"][0]["text"] = "UNEXPECTED_SYNTHETIC_USER_PROMPT"
        expectation = replace(self.expectation, current_session=self.write_session(records))
        self.latest_binding, self.latest, self.checkpoint = self.make_latest_gate()
        before = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        result = self.assess(expectation)
        after = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        self.assertEqual(result.status, "NOT_ADMITTED")
        self.assertEqual(result.reason, "TOOL_TRANSCRIPT_INVALID")
        self.assertEqual(before, after)

    def test_wrong_tool_id_and_extra_tool_call_reject(self) -> None:
        records = self.session_records()
        records[3]["message"]["content"][0]["id"] = "wrong-tool"
        expectation = replace(self.expectation, current_session=self.write_session(records))
        self.latest_binding, self.latest, self.checkpoint = self.make_latest_gate()
        self.assertEqual(self.assess(expectation).reason, "TOOL_TRANSCRIPT_INVALID")
        records = self.session_records()
        records[3]["message"]["content"].append({"type": "toolCall", "id": "extra", "name": "read_public_result", "arguments": {}})
        expectation = replace(self.expectation, current_session=self.write_session(records))
        self.latest_binding, self.latest, self.checkpoint = self.make_latest_gate()
        self.assertEqual(self.assess(expectation).reason, "TOOL_TRANSCRIPT_INVALID")

    def test_tool_result_wire_rejects_extra_key_bool_timestamp_and_envelope(self) -> None:
        mutations = ("extra", "bool_timestamp", "envelope")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                records = self.session_records()
                tool_result = records[4]["message"]
                if mutation == "extra":
                    tool_result["unexpected"] = True
                elif mutation == "bool_timestamp":
                    tool_result["timestamp"] = True
                else:
                    tool_result["content"][0]["text"] = json.dumps(
                        {"ok": True, "result": self.public_result},
                        separators=(",", ":"),
                    )
                expectation = replace(self.expectation, current_session=self.write_session(records))
                self.latest_binding, self.latest, self.checkpoint = self.make_latest_gate()
                self.assertEqual(self.assess(expectation).reason, "TOOL_TRANSCRIPT_INVALID")

    def test_missing_gate_rejects_without_manufacture(self) -> None:
        with patch(
            "experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance.verify_tree",
            side_effect=lambda root, expected, limits: expected,
        ), patch(
            "experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance._latest_gate",
            side_effect=ValueError("missing"),
        ):
            result = assess_combination(self.expectation)
        self.assertEqual(result.reason, "GATE_INVALID")
        self.assertIsNone(result.native_gate_sha256)
        self.assertIsNone(result.native_gate_binding)

    def test_false_process_exit_rejects(self) -> None:
        expectation = replace(self.expectation, process_receipt=self.write_process_receipt(False))
        self.assertEqual(self.assess(expectation).reason, "PROCESS_INVALID")

    def test_wrong_faux_config_normalization_rejects(self) -> None:
        changed = replace(self.synthetic_config, campaign_started_monotonic_ns=12)
        binding = self.bound_data("changed-synthetic-config.json", config_to_dict(changed))
        expectation = replace(self.expectation, synthetic_process_config=binding)
        self.assertEqual(self.assess(expectation).reason, "CONFIG_INVALID")

    def test_source_change_or_missing_proof_rejects(self) -> None:
        result = self.assess(tree_error=ClosureError())
        self.assertEqual(result.reason, "SOURCE_MISMATCH")
        bad_tree = replace(self.expectation.frontend_tree, tree_sha256="bad")
        self.assertEqual(self.assess(replace(self.expectation, frontend_tree=bad_tree)).reason, "CONFIG_INVALID")

    def test_incomplete_usage_and_cross_response_replay_reject(self) -> None:
        records = self.session_records()
        del records[3]["message"]["usage"]["cacheWrite"]
        expectation = replace(self.expectation, current_session=self.write_session(records))
        self.assertEqual(self.assess(expectation).reason, "USAGE_UNKNOWN")
        records = self.session_records()
        records[5]["message"]["responseId"] = RESPONSE_IDS[0]
        expectation = replace(self.expectation, current_session=self.write_session(records))
        self.assertEqual(self.assess(expectation).reason, "USAGE_UNKNOWN")

    def test_metadata_mismatch_rejects(self) -> None:
        original = json.loads(self.metadata.path.read_text())
        for field, value in (
            ("provider_call_count", 1),
            ("tool_schema_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                metadata = dict(original)
                metadata[field] = value
                self.metadata.path.write_text(
                    json.dumps(metadata, sort_keys=True, separators=(",", ":")),
                    encoding="ascii",
                )
                binding = self.binding(self.metadata.path)
                result = self.assess(replace(self.expectation, metadata=binding))
                self.assertEqual(result.reason, "METADATA_INVALID")
                self.assertEqual(result.campaign_tokens, 278)
                self.assertEqual(result.session_sha256, self.session_binding.sha256)
                self.assertEqual(result.native_gate_sha256, self.latest_binding.sha256)
                self.assertEqual(result.native_gate_binding, self.latest_binding)

    def test_output_aggregate_cap_rejects(self) -> None:
        (self.artifact / "aggregate.bin").write_bytes(b"x" * 1_048_000)
        result = self.assess()
        self.assertEqual(result.reason, "OUTPUT_LIMIT")
        self.assertEqual(result.native_gate_binding, self.latest_binding)

    def test_output_file_count_cap_rejects(self) -> None:
        for index in range(130):
            (self.artifact / f"extra-{index:03d}").write_bytes(b"x")
        self.assertEqual(self.assess().reason, "OUTPUT_LIMIT")


if __name__ == "__main__":
    unittest.main()
