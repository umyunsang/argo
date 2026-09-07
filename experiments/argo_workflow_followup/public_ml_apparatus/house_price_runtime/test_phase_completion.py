from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import ContextRights
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    RunControllerCaps,
    capture_path_identity,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion import (
    PhaseCompletionConfig,
    PhaseCompletionResult,
    complete_phase,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import decide_phase
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.trusted_io import FinalArtifactLock
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import (
    UsageObserver,
    UsageObserverConfig,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import parse_session_usage


def digest(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def binding(path: Path) -> FileBinding:
    path = path.resolve()
    info = path.stat()
    return FileBinding(path, digest(path.read_bytes()), info.st_size, info.st_mtime_ns)


def directory(path: Path) -> DirectoryIdentity:
    path = path.resolve()
    info = path.stat()
    return DirectoryIdentity(path, info.st_dev, info.st_ino)


def binding_dict(value: FileBinding) -> dict[str, object]:
    return {"path": str(value.path), "sha256": value.sha256, "bytes": value.bytes, "mtime_ns_max": value.mtime_ns_max}


def file_seal(path: Path) -> dict[str, object]:
    value = binding(path)
    return {"path": str(value.path), "sha256": value.sha256, "bytes": value.bytes, "mtime_ns_max": str(value.mtime_ns_max)}


def directory_seal(path: Path, empty: bool) -> dict[str, object]:
    value = directory(path)
    return {"path": str(value.path), "realpath": str(value.path), "device": str(value.device), "inode": str(value.inode),
            "mtime_ns_max": str(value.path.stat().st_mtime_ns), "mode_octal": "0700", "must_be_empty": empty}


def session_bytes(session_id: str, cwd: Path, response_id: str | None, tokens: int = 100) -> bytes:
    header = {"type": "session", "id": session_id, "cwd": str(cwd), "version": 3,
              "parentSession": None, "rlmDepth": 0}
    message = {"type": "message", "id": "entry-1", "parentId": None, "message": {
        "role": "assistant", "provider": "openai-codex", "model": "gpt-5.6-sol",
        "stopReason": "stop", "responseId": response_id,
        "usage": {"input": tokens, "output": 0, "cacheRead": 0, "cacheWrite": 0, "totalTokens": tokens},
    }}
    return (json.dumps(header, sort_keys=True, separators=(",", ":")) + "\n" +
            json.dumps(message, sort_keys=True, separators=(",", ":")) + "\n").encode()


class FakeTrustedIo:
    def __init__(self, lock: FinalArtifactLock | None):
        self.lock = lock

    def final_artifact_lock(self) -> FinalArtifactLock:
        if self.lock is None:
            raise ValueError("no lock")
        return self.lock


class FakeBridge:
    def __init__(self, state_root: DirectoryIdentity, rights: ContextRights,
                 public: dict[str, object], dev: dict[str, object], research: dict[str, object],
                 lock: FinalArtifactLock | None):
        self.responses = {"read_public_result": public, "read_dev_result": dev, "read_solution": research}
        self.calls: list[str] = []
        self.config = type("Config", (), {
            "state_root": state_root,
            "context_rights": rights,
            "task_sha256": digest("task"),
            "environment_sha256": digest("environment"),
            "protocol_sha256": digest("protocol"),
            "outer_training_manifest_sha256": digest("outer"),
            "hidden_features_manifest_sha256": digest("hidden"),
            "trusted_io": FakeTrustedIo(lock),
        })()

    def handle(self, request: dict[str, object]) -> dict[str, object]:
        action = request["action"]
        self.calls.append(action)
        return self.responses[action]


class CompletionFixture:
    def __init__(self, root: Path, *, context: str = "initial", ready: bool = True,
                 incomplete: bool = False, final_mismatch: bool = False, replay: bool = False,
                 current_tokens: int = 100):
        self.root = root.resolve()
        self.context = context
        self.ready = ready
        self.initial_id = digest("initial-context")
        self.controller_id = self.initial_id if context == "initial" else digest("continuation-context")
        self.next_id = digest("continuation-context") if context == "initial" else None
        self.paths = {}
        for name in ("artifact", "profile", "cwd", "outcomes", "completion", "bridge-state", "source"):
            path = self.root / name
            path.mkdir(mode=0o700)
            self.paths[name] = path.resolve()
        self.paths["session"] = self.paths["artifact"] / "session"
        self.paths["session"].mkdir(mode=0o700)
        self.paths["tmp"] = self.paths["artifact"] / "tmp"
        self.paths["tmp"].mkdir(mode=0o700)
        for name in ("frontend.mjs", "process-exec.py", "node", "python", "pyvenv.cfg", "asset"):
            path = self.root / name
            path.write_text(name + "\n")
            if name in {"node", "python"}:
                path.chmod(0o700)
            self.paths[name] = path.resolve()
        self.dev_ids = [str(uuid.UUID(int=101)), str(uuid.UUID(int=102))]
        if context == "continuation":
            self.dev_ids.append(str(uuid.UUID(int=103)))
        self.final_id = str(uuid.UUID(int=201))
        self.public, self.dev, self.research, self.lock = self._views(final_mismatch)
        self.bridge_config_path = self.root / "bridge-config.json"
        checkpoint = None
        if context == "continuation":
            checkpoint_file = self.root / "prior-handoff.json"
            checkpoint_file.write_text("{}")
            checkpoint = binding(checkpoint_file)
        rights = ContextRights(
            "argo-house-price-a2-context-rights/v1", self.controller_id, context,
            self.initial_id, checkpoint,
        )
        bridge_config = {
            "directories": {"source": {"path": str(self.paths["source"])}},
            "context_rights": {
                "schema_version": rights.schema_version, "controller_context_id": rights.controller_context_id,
                "context": rights.context, "initial_context_id": rights.initial_context_id,
                "checkpoint": None if rights.checkpoint is None else binding_dict(rights.checkpoint),
            },
        }
        self.bridge_config_path.write_text(json.dumps(bridge_config, sort_keys=True, separators=(",", ":")))
        self.bridge_binding = binding(self.bridge_config_path)
        self.bridge = FakeBridge(directory(self.paths["bridge-state"]), rights, self.public, self.dev,
                                 self.research, self.lock)
        if self.lock is not None:
            lock_path = self.paths["bridge-state"] / "final-artifact-lock.json"
            lock_path.write_text(json.dumps(asdict(self.lock), sort_keys=True, separators=(",", ":")))

        self.prior_session_binding = None
        self.prior_session_id = None
        self.prior_cwd = None
        prior_usage = ()
        if context == "continuation":
            prior_dir = self.root / "prior-session"
            prior_dir.mkdir(mode=0o700)
            self.prior_cwd = str(self.paths["cwd"])
            self.prior_session_id = str(uuid.UUID(int=301))
            prior_path = prior_dir / (self.prior_session_id + ".jsonl")
            prior_path.write_bytes(session_bytes(self.prior_session_id, self.paths["cwd"], "prior-response", 50))
            self.prior_session_binding = binding(prior_path)
            prior_usage = (parse_session_usage(prior_path.read_bytes(), self.prior_session_id,
                                               self.prior_cwd, "openai-codex", "gpt-5.6-sol"),)

        self.session_id = str(uuid.UUID(int=302 if context == "continuation" else 300))
        response_id = None if incomplete else "prior-response" if replay else "current-response"
        self.session_path = self.paths["session"] / (self.session_id + ".jsonl")
        self.session_path.write_bytes(session_bytes(self.session_id, self.paths["cwd"], response_id, current_tokens))
        self.session_binding = binding(self.session_path)
        self.session_usage = parse_session_usage(
            self.session_path.read_bytes(), self.session_id, str(self.paths["cwd"]), "openai-codex", "gpt-5.6-sol",
        )

        self.caps = RunControllerCaps(
            provider_timeout_ms=120000, provider_retries=0, phase_wall_seconds=3600,
            campaign_wall_seconds=10800, cpu_seconds_per_process=600, file_size_bytes=8388608,
            rss_trigger_bytes=2147483648, rss_sample_ms=250, v8_old_space_mib=1024,
            model_tokens_between_turns=120000, controller_turn_limit_per_phase=20,
            source_text_max_bytes=131072, autonomous_gate_retries=20, autonomous_gate_timeout_ms=30000,
            bridge_close_grace_ms=1000, artifact_aggregate_bytes=67108864, artifact_file_count=128,
            terminate_grace_seconds=1.0, kill_grace_seconds=1.0, observer_timeout_seconds=1.0,
            observer_output_bytes=8388608,
        )
        self.environment = {
            "PRIME_AGENT_CODING_AGENT_DIR": str(self.paths["profile"]),
            "PRIME_AGENT_KERNEL_PYTHON": str(self.paths["python"]), "PRIME_AGENT_TELEMETRY": "0",
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
            "TMPDIR": str(self.paths["tmp"]) + "/", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
        }
        self.deployment_path = self.root / "deployment.json"
        self._write_deployment()
        self.process_config_path = self.root / "process-config.json"
        self._write_process_config()
        self.process_config_binding = binding(self.process_config_path)
        self.process_receipt_path = self.root / "process-receipt.json"
        self._write_process_receipt()
        self.process_receipt_binding = binding(self.process_receipt_path)

        self.gate_config_path = self.root / "gate-config.json"
        self._write_gate_config()
        self.gate_binding = binding(self.gate_config_path)
        observer_config = UsageObserverConfig(
            directory(self.paths["session"]), str(self.paths["cwd"]), "openai-codex", "gpt-5.6-sol",
            120000, prior_usage,
        )
        observer = UsageObserver(observer_config)
        observation = observer.observe()
        decision = decide_phase(context, self.public, self.dev, self.research, observation, self.lock, 292)
        if not ready and not incomplete:
            decision = decide_phase(context, self.public, self.dev, self.research, observation, self.lock, 292)
        outcome = {
            "schema_version": "argo-house-price-a2-phase-gate-outcome/v2", "context": context,
            "config_sha256": self.gate_binding.sha256, "bridge_config_sha256": self.bridge_binding.sha256,
            "decision": asdict(decision), "usage": asdict(observation),
            "view_sha256": {
                "public": digest(json.dumps(self.public, sort_keys=True, separators=(",", ":"), ensure_ascii=True)),
                "dev": digest(json.dumps(self.dev, sort_keys=True, separators=(",", ":"), ensure_ascii=True)),
                "research": digest(json.dumps(self.research, sort_keys=True, separators=(",", ":"), ensure_ascii=True)),
            },
            "final_lock_sha256": None if self.lock is None else digest(json.dumps(asdict(self.lock), sort_keys=True, separators=(",", ":"))),
            "sequence": 1, "previous_outcome_sha256": None,
            "usage_checkpoint": observer.export_checkpoint(),
        }
        outcome_path = self.paths["outcomes"] / ("0001-" + "a" * 32 + ".json")
        outcome_path.write_text(json.dumps(outcome, sort_keys=True, separators=(",", ":")))
        outcome_path.chmod(0o600)
        self.outcome_path = outcome_path.resolve()
        self.config = PhaseCompletionConfig(
            context, self.initial_id, self.controller_id, self.next_id,
            self.gate_binding, self.process_config_binding, self.process_receipt_binding,
            self.session_binding, self.session_id, directory(self.paths["completion"]),
        )

    def _views(self, final_mismatch: bool):
        run_rows = []
        dev_results = []
        for index, run_id in enumerate(self.dev_ids):
            solution = digest(f"solution-{index}")
            run_rows.append({"intent_sha256": digest(f"intent-{index}"), "run_id": run_id,
                             "experiment_id": str(uuid.UUID(int=401 + index)), "solution_sha256": solution,
                             "phase": "dev", "status": "DONE"})
            dev_results.append({"run_id": run_id, "solution_sha256": solution, "valid": True,
                                "mae": f"{index + 1}.000000", "rows": 292})
        lock = None
        phase = "development"
        if self.context == "continuation":
            selected_solution = run_rows[-1]["solution_sha256"]
            artifact = digest("artifact")
            run_rows.append({"intent_sha256": digest("final-intent"), "run_id": self.final_id,
                             "experiment_id": str(uuid.UUID(int=499)), "solution_sha256": selected_solution,
                             "phase": "final_refit", "status": "DONE", "artifact_sha256": artifact})
            phase = "final_locked"
            lock = FinalArtifactLock(
                closure_sha256=digest("closure"), code_sha256=selected_solution,
                selection_receipt_sha256=digest("selection"), execution_identity_sha256=digest("execution"),
                execution_config_sha256=digest("config"), outer_training_manifest_sha256=digest("outer"),
                hidden_features_manifest_sha256=digest("hidden"), run_id=self.final_id,
                artifact_sha256=artifact, task_sha256=digest("wrong" if final_mismatch else "task"),
                environment_sha256=digest("environment"), protocol_sha256=digest("protocol"),
            )
        if not self.ready:
            run_rows = run_rows[:1]
            dev_results = dev_results[:1]
            phase = "development"
            lock = None
        public = {"ok": True, "result": {"phase": phase,
            "dev_attempts": len([row for row in run_rows if row["phase"] == "dev"]),
            "final_attempts": len([row for row in run_rows if row["phase"] == "final_refit"]),
            "remaining_dev_opportunities": max(0, 3 - len(dev_results)), "runs": run_rows}}
        dev = {"ok": True, "result": {"results": dev_results}}
        research_text = "saved research\n"
        research = {"ok": True, "result": {"path": "research.md", "content": research_text,
                                             "sha256": digest(research_text)}}
        return public, dev, research, lock

    def _write_deployment(self):
        asset = self.paths["asset"]
        assets = {name: file_seal(asset) for name in (
            "prime_entry", "prime_closure_manifest", "frontend_closure_manifest", "extension", "binding",
            "settings", "system_prompt", "task_prompt", "autonomous_gate",
        )}
        assets["controller_main"] = file_seal(self.paths["frontend.mjs"])
        assets["node_executable"] = file_seal(self.paths["node"])
        assets["kernel_interpreter"] = {
            "invocation_path": str(self.paths["python"]),
            "invocation_link": {"device": "1", "inode": "1", "mtime_ns_max": "1", "link_target": "python"},
            "resolved_target": file_seal(self.paths["python"]), "pyvenv_cfg": file_seal(self.paths["pyvenv.cfg"]),
        }
        limits = {name: getattr(self.caps, name) for name in (
            "provider_timeout_ms", "provider_retries", "phase_wall_seconds", "campaign_wall_seconds",
            "cpu_seconds_per_process", "file_size_bytes", "rss_trigger_bytes", "rss_sample_ms",
            "v8_old_space_mib", "model_tokens_between_turns", "controller_turn_limit_per_phase",
            "source_text_max_bytes", "bridge_close_grace_ms", "autonomous_gate_retries", "autonomous_gate_timeout_ms",
        )}
        limits["autonomous_max_continuations"] = 20
        value = {
            "schema_version": "argo-house-price-a2-controller-main-deployment/v1", "status": "TRUSTED_FIXED_DEPLOYMENT",
            "assets": assets,
            "directories": {
                "artifact_root": directory_seal(self.paths["artifact"], False),
                "cwd": directory_seal(self.paths["cwd"], False),
                "profile": directory_seal(self.paths["profile"], False),
                "session_dir": directory_seal(self.paths["session"], True),
                "temporary_dir": directory_seal(self.paths["tmp"], True),
            },
            "runtime": {"phase": "dev" if self.context == "initial" else "final_refit",
                        "model": "openai-codex/gpt-5.6-sol", "thinking": "xhigh", "mode": "text",
                        "print": True, "offline": True, "fresh_session": True,
                        "tools": ["read_solution", "write_solution", "request_R1_run", "read_public_result",
                                  "read_dev_result", "lock_final_artifact"]},
            "environment": {"exact": self.environment, "home_must_be_unset": True,
                            "forbidden_prefixes": ["PRIME_AGENT_INTERNAL_"]},
            "limits": limits,
        }
        self.deployment_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))

    def _write_process_config(self):
        def identity(path: Path, hashed: bool) -> dict[str, object]:
            return asdict(capture_path_identity(path, hash_file=hashed, max_file_bytes=1_048_576))
        python_identity = identity(self.paths["python"], True)
        value = {
            "python_executable": str(self.paths["python"]),
            "interpreter_identity": {"invocation_path": str(self.paths["python"]), "symlink_chain": [],
                                     "resolved_target": python_identity, "pyvenv_cfg_path": str(self.paths["pyvenv.cfg"]),
                                     "pyvenv_cfg": identity(self.paths["pyvenv.cfg"], True)},
            "process_exec_path": str(self.paths["process-exec.py"]),
            "process_exec_identity": identity(self.paths["process-exec.py"], True),
            "node_executable": str(self.paths["node"]), "node_identity": identity(self.paths["node"], True),
            "frontend_path": str(self.paths["frontend.mjs"]), "frontend_identity": identity(self.paths["frontend.mjs"], True),
            "deployment_path": str(self.deployment_path.resolve()), "deployment_identity": identity(self.deployment_path, True),
            "artifact_root": str(self.paths["artifact"]), "artifact_root_identity": identity(self.paths["artifact"], False),
            "temporary_dir": str(self.paths["tmp"]), "temporary_dir_identity": identity(self.paths["tmp"], False),
            "session_dir": str(self.paths["session"]), "session_dir_identity": identity(self.paths["session"], False),
            "profile_dir": str(self.paths["profile"]), "profile_dir_identity": identity(self.paths["profile"], False),
            "child_environment": self.environment, "caps": asdict(self.caps),
            "campaign_started_monotonic_ns": 1, "synthetic_test_context": False,
        }
        self.process_config_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))

    def _write_process_receipt(self):
        resources = {
            "provider_timeout_ms": self.caps.provider_timeout_ms, "provider_retries": 0,
            "model_tokens_between_turns": self.caps.model_tokens_between_turns,
            "controller_turn_limit_per_phase": self.caps.controller_turn_limit_per_phase,
            "source_text_max_bytes": self.caps.source_text_max_bytes,
            "autonomous_gate_retries": self.caps.autonomous_gate_retries,
            "autonomous_gate_timeout_ms": self.caps.autonomous_gate_timeout_ms,
            "bridge_close_grace_ms": self.caps.bridge_close_grace_ms,
            "rss_sampling_semantics": "sampled_trigger_not_hard_limit", "rss_trigger_bytes": self.caps.rss_trigger_bytes,
            "rss_sample_interval_ms": self.caps.rss_sample_ms, "peak_sampled_rss_bytes": 1,
            "rss_overshoot_bytes": 0, "rss_trigger_monotonic_ns": None,
            "rss_trigger_elapsed_from_first_sample_seconds": None, "sample_count": 2,
            "first_sample_monotonic_ns": 2, "last_sample_monotonic_ns": 100000002,
            "max_sample_gap_ms": 100.0, "observed_seconds": 0.1,
            "coverage_complete_for_observed_tree": True, "observer_errors": [], "census_errors": [],
            "census_file_count_peak": 2, "census_aggregate_bytes_peak": 100, "census_largest_file_bytes": 100,
            "file_count_overshoot": 0, "aggregate_bytes_overshoot": 0,
            "artifact_file_count_trigger": self.caps.artifact_file_count,
            "artifact_aggregate_bytes_trigger": self.caps.artifact_aggregate_bytes,
            "regular_file_rlimit_bytes": self.caps.file_size_bytes,
            "cpu_rlimit_seconds_per_process": self.caps.cpu_seconds_per_process,
            "phase_wall_seconds": self.caps.phase_wall_seconds,
            "campaign_wall_seconds": self.caps.campaign_wall_seconds,
            "observer_output_limit_bytes": self.caps.observer_output_bytes,
            "native_usage_missing_or_inflight_semantics": "unknown_not_zero",
        }
        cleanup = {"confirmed_for_tracked_processes": True, "claims_all_possible_descendants": False,
                   "unobserved_escape_possible": True, "root_process_reaped": True, "signals_sent": [],
                   "tracked_processes": [], "observed_process_groups": [], "escaped_observed_process_groups": [],
                   "alive_tracked_after_cleanup": [], "cleanup_errors": []}
        handle = {"pid": 99991, "root_pgid": 99991, "pid_start_identity": "start", "spawn_attempts": 1,
                  "stdout_path": str(self.paths["artifact"] / "controller.stdout"),
                  "stderr_path": str(self.paths["artifact"] / "controller.stderr"),
                  "process_exec_path": str(self.paths["process-exec.py"]),
                  "frontend_path": str(self.paths["frontend.mjs"]),
                  "deployment_path": str(self.deployment_path.resolve()), "artifact_root": str(self.paths["artifact"]),
                  "session_dir": str(self.paths["session"]), "child_environment_keys": sorted(self.environment),
                  "stdin_mode": "DEVNULL"}
        receipt = {"schema_version": "argo-house-price-a2-controller-process-receipt/v1",
                   "authority_contract_sha256": "0cfaeb57c18662f428cdb9fbdef842d55782624b9baaf9bbbbe98ebeb4412c20",
                   "status": "succeeded", "terminal_reason": "completed", "returncode": 0,
                   "started_monotonic_ns": 2, "ended_monotonic_ns": 100000002, "elapsed_seconds": 0.1,
                   "handle": handle, "resources": resources, "cleanup": cleanup, "limitations": []}
        self.process_receipt_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")))

    def _write_gate_config(self):
        value = {"schema_version": "argo-house-price-a2-phase-gate-deployment/v1", "context": self.context,
                 "bridge_config": binding_dict(self.bridge_binding),
                 "session_directory": {"path": str(self.paths["session"]),
                                       "device": directory(self.paths["session"]).device,
                                       "inode": directory(self.paths["session"]).inode},
                 "cwd": str(self.paths["cwd"]), "provider": "openai-codex", "model": "gpt-5.6-sol",
                 "budget": 120000,
                 "prior_session": None if self.prior_session_binding is None else binding_dict(self.prior_session_binding),
                 "prior_session_id": self.prior_session_id, "prior_cwd": self.prior_cwd,
                 "final_lock_path": str(self.paths["bridge-state"] / "final-artifact-lock.json"),
                 "gate_outcome_directory": {"path": str(self.paths["outcomes"]),
                                            "device": directory(self.paths["outcomes"]).device,
                                            "inode": directory(self.paths["outcomes"]).inode},
                 "expected_rows": 292}
        self.gate_config_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))

    def run(self) -> PhaseCompletionResult:
        with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion.load_bridge_from_config",
                   return_value=self.bridge):
            return complete_phase(self.config)


class PhaseCompletionTest(unittest.TestCase):
    def test_initial_publishes_exact_handoff_from_terminal_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            before = {str(path.relative_to(fixture.root)): digest(path.read_bytes())
                      for path in fixture.root.rglob("*") if path.is_file() and fixture.paths["completion"] not in path.parents}
            result = fixture.run()
            after = {str(path.relative_to(fixture.root)): digest(path.read_bytes())
                     for path in fixture.root.rglob("*") if path.is_file() and fixture.paths["completion"] not in path.parents}
            self.assertEqual(after, before)
            self.assertEqual(result.disposition, "INITIAL_HANDOFF_PUBLISHED")
            self.assertEqual(result.reason, "VERIFIED")
            self.assertEqual(result.current_tokens, 100)
            self.assertEqual(result.campaign_tokens, 100)
            value = json.loads(result.publication.path.read_text())
            self.assertEqual(set(value), {"schema_version", "initial_context_id", "next_context_id",
                "verified_dev_run_ids", "research_sha256", "prior_process_receipt", "prior_session",
                "prior_session_id", "prior_cwd", "provider", "model", "campaign_token_budget",
                "campaign_used_tokens"})
            self.assertEqual(value["verified_dev_run_ids"], sorted(fixture.dev_ids))
            self.assertEqual(fixture.bridge.calls, ["read_public_result", "read_dev_result", "read_solution"])

    def test_nonready_native_gate_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), ready=False)
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "NOT_READY"))
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_missing_actual_gate_and_active_gate_lock_are_evidence_mismatch(self):
        for mode in ("missing", "locked"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = CompletionFixture(Path(temporary))
                if mode == "missing":
                    fixture.outcome_path.unlink()
                else:
                    (fixture.paths["outcomes"] / ".gate-evaluation.lock").write_text("active")
                result = fixture.run()
                self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))

    def test_process_receipt_boolean_and_mismatched_path_do_not_prove_termination(self):
        for field in ("boolean", "path"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                fixture = CompletionFixture(Path(temporary))
                value = json.loads(fixture.process_receipt_path.read_text())
                if field == "boolean":
                    value["terminated"] = True
                else:
                    value["handle"]["frontend_path"] = str(fixture.paths["asset"])
                fixture.process_receipt_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
                fixture.config = PhaseCompletionConfig(**{**fixture.config.__dict__,
                    "process_receipt": binding(fixture.process_receipt_path)})
                result = fixture.run()
                self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))

    def test_process_config_environment_must_match_sealed_frontend_deployment(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            value = json.loads(fixture.process_config_path.read_text())
            value["child_environment"]["LANG"] = "C"
            fixture.process_config_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
            fixture.config = PhaseCompletionConfig(**{**fixture.config.__dict__,
                "process_config": binding(fixture.process_config_path)})
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_mutated_session_or_history_never_publishes(self):
        for field in ("session", "history"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                fixture = CompletionFixture(Path(temporary))
                if field == "session":
                    fixture.session_path.write_bytes(fixture.session_path.read_bytes() + b" ")
                    fixture.config = PhaseCompletionConfig(**{**fixture.config.__dict__,
                        "current_session": binding(fixture.session_path)})
                else:
                    value = json.loads(fixture.outcome_path.read_text())
                    value["previous_outcome_sha256"] = digest("foreign")
                    fixture.outcome_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
                    fixture.outcome_path.chmod(0o600)
                result = fixture.run()
                self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))

    def test_incomplete_current_session_maps_to_usage_unknown(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), incomplete=True)
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "USAGE_UNKNOWN"))
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_replayed_response_id_across_contexts_never_publishes(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), context="continuation", replay=True)
            result = fixture.run()
            self.assertEqual(result.disposition, "NOT_ADMITTED")
            self.assertIn(result.reason, {"USAGE_UNKNOWN", "EVIDENCE_MISMATCH"})
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_native_budget_stop_maps_to_budget_exhausted(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), current_tokens=120000)
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "BUDGET_EXHAUSTED"))
            self.assertIsNone(result.current_tokens)
            self.assertIsNone(result.campaign_tokens)
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_foreign_bridge_context_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            fixture.bridge.config.context_rights = ContextRights(
                "argo-house-price-a2-context-rights/v1", digest("foreign"), "initial", digest("foreign"), None)
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))

    def test_existing_name_is_publication_failed_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            target = fixture.paths["completion"] / "initial-handoff.json"
            target.write_bytes(b"held")
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "PUBLICATION_FAILED"))
            self.assertEqual(target.read_bytes(), b"held")

    def test_partial_publication_failure_returns_no_fabricated_binding_and_preserves_partial(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            def partial(descriptor, payload):
                os.write(descriptor, payload[:1])
                raise OSError("short write")
            with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion._write_all",
                       side_effect=partial):
                result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "PUBLICATION_FAILED"))
            self.assertIsNone(result.publication)
            self.assertEqual((fixture.paths["completion"] / "initial-handoff.json").read_bytes(), b"{")

    def test_continuation_publishes_exact_final_completion_without_hidden_score(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), context="continuation")
            result = fixture.run()
            self.assertEqual(result.disposition, "FINAL_COMPLETION_PUBLISHED")
            self.assertEqual(result.current_tokens, 100)
            self.assertEqual(result.campaign_tokens, 150)
            value = json.loads(result.publication.path.read_text())
            self.assertEqual(set(value), {"schema_version", "initial_context_id", "controller_context_id",
                "process_config", "process_receipt", "gate_config", "native_gate_outcome", "bridge_config",
                "current_session", "current_session_id", "prior_session", "prior_session_id", "cwd",
                "provider", "model", "campaign_token_budget", "current_used_tokens", "campaign_used_tokens",
                "verified_dev_run_ids", "research_sha256", "final_artifact_lock", "final_lock_sha256",
                "final_lock", "hidden_score_observed"})
            self.assertEqual(value["schema_version"], "argo-house-price-a2-final-completion/v1")
            self.assertIs(value["hidden_score_observed"], False)
            self.assertEqual(value["final_lock"], asdict(fixture.lock))
            self.assertEqual(value["verified_dev_run_ids"], sorted(fixture.dev_ids))

    def test_final_scientific_identity_mismatch_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary), context="continuation", final_mismatch=True)
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

    def test_invalid_config_returns_safe_result_but_base_exception_is_not_caught(self):
        result = complete_phase("not-config")
        self.assertEqual(result, PhaseCompletionResult(
            "argo-house-price-a2-phase-completion-result/v1", "NOT_ADMITTED", "INVALID_INPUT", None, None, None))
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion._verify",
                       side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    complete_phase(fixture.config)


    def test_false_returncode_cannot_publish_a_handoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = CompletionFixture(Path(temporary))
            receipt = json.loads(fixture.process_receipt_path.read_text())
            receipt["returncode"] = False
            fixture.process_receipt_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
            fixture.config = PhaseCompletionConfig(**{**fixture.config.__dict__,
                "process_receipt": binding(fixture.process_receipt_path)})
            result = fixture.run()
            self.assertEqual((result.disposition, result.reason), ("NOT_ADMITTED", "EVIDENCE_MISMATCH"))
            self.assertEqual(list(fixture.paths["completion"].iterdir()), [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
