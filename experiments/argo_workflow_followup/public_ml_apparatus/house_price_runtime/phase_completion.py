"""Verify one already-terminal A2 context and publish bounded root evidence.

This module never launches, cancels, scores, or calls a provider. It consumes the
actual root process/session/gate/Bridge evidence after the controller has returned.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Mapping

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import (
    _valid_prior_process_receipt,
    load_bridge_from_config,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import (
    CampaignUsage,
    SessionUsage,
    combine_usage,
    parse_session_usage,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    RunControllerConfig,
    _validate_identity,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import (
    GateConfigError,
    GateDecision,
    _gate_directory,
    _gate_file_binding,
    _gate_json,
    _gate_read,
    _read_gate_history,
    decide_phase,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.trusted_io import FinalArtifactLock
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import (
    UsageObservation,
    UsageObserverConfig,
)

HEX64 = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
RESULT_SCHEMA = "argo-house-price-a2-phase-completion-result/v1"
HANDOFF_SCHEMA = "argo-house-price-a2-handoff/v1"
FINAL_SCHEMA = "argo-house-price-a2-final-completion/v1"
GATE_SCHEMA = "argo-house-price-a2-phase-gate-deployment/v1"
GATE_OUTCOME_SCHEMA = "argo-house-price-a2-phase-gate-outcome/v2"
BUDGET = 120_000


@dataclass(frozen=True)
class PhaseCompletionConfig:
    context: str
    initial_context_id: str
    controller_context_id: str
    next_context_id: str | None
    gate_config: FileBinding
    process_config: FileBinding
    process_receipt: FileBinding
    current_session: FileBinding
    current_session_id: str
    completion_directory: DirectoryIdentity


@dataclass(frozen=True)
class PhaseCompletionResult:
    schema_version: str
    disposition: str
    reason: str
    publication: FileBinding | None
    current_tokens: int | None
    campaign_tokens: int | None


@dataclass(frozen=True)
class _Evidence:
    gate: Mapping[str, object]
    gate_binding: FileBinding
    process_binding: FileBinding
    receipt_binding: FileBinding
    session_binding: FileBinding
    bridge_binding: FileBinding
    latest_gate_binding: FileBinding
    current_usage: SessionUsage
    prior_usage: SessionUsage | None
    campaign_usage: CampaignUsage
    public: Mapping[str, object]
    dev: Mapping[str, object]
    research: Mapping[str, object]
    decision: GateDecision
    final_lock: FinalArtifactLock | None
    final_lock_binding: FileBinding | None


class _CompletionError(ValueError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class _PublicationError(RuntimeError):
    pass


def complete_phase(config: PhaseCompletionConfig) -> PhaseCompletionResult:
    try:
        _validate_input(config)
    except Exception:
        return _not_admitted("INVALID_INPUT")
    try:
        evidence = _verify(config)
    except _CompletionError as error:
        return _not_admitted(error.reason)
    except Exception:
        return _not_admitted("EVIDENCE_MISMATCH")
    try:
        payload, name = _publication_payload(config, evidence)
        binding = _publish(config.completion_directory, name, payload)
    except Exception:
        return _not_admitted("PUBLICATION_FAILED")
    disposition = "INITIAL_HANDOFF_PUBLISHED" if config.context == "initial" else "FINAL_COMPLETION_PUBLISHED"
    return PhaseCompletionResult(
        RESULT_SCHEMA, disposition, "VERIFIED", binding,
        evidence.current_usage.total_tokens, evidence.campaign_usage.total_tokens,
    )


def _not_admitted(reason: str) -> PhaseCompletionResult:
    if reason not in {
        "INVALID_INPUT", "EVIDENCE_MISMATCH", "NOT_READY", "USAGE_UNKNOWN",
        "BUDGET_EXHAUSTED", "PUBLICATION_FAILED",
    }:
        reason = "EVIDENCE_MISMATCH"
    return PhaseCompletionResult(RESULT_SCHEMA, "NOT_ADMITTED", reason, None, None, None)


def _validate_input(config: PhaseCompletionConfig) -> None:
    if (not isinstance(config, PhaseCompletionConfig) or config.context not in {"initial", "continuation"} or
            any(not isinstance(value, str) or HEX64.fullmatch(value) is None
                for value in (config.initial_context_id, config.controller_context_id)) or
            not isinstance(config.gate_config, FileBinding) or not isinstance(config.process_config, FileBinding) or
            not isinstance(config.process_receipt, FileBinding) or not isinstance(config.current_session, FileBinding) or
            not isinstance(config.completion_directory, DirectoryIdentity) or
            not isinstance(config.current_session_id, str) or UUID.fullmatch(config.current_session_id) is None):
        raise ValueError()
    if config.context == "initial":
        if (config.initial_context_id != config.controller_context_id or not isinstance(config.next_context_id, str) or
                HEX64.fullmatch(config.next_context_id) is None or config.next_context_id == config.initial_context_id):
            raise ValueError()
    elif (config.controller_context_id == config.initial_context_id or config.next_context_id is not None):
        raise ValueError()
    _validate_binding_shape(config.gate_config, 65_536)
    _validate_binding_shape(config.process_config, 65_536)
    _validate_binding_shape(config.process_receipt, 1_048_576)
    _validate_binding_shape(config.current_session, 8_388_608)
    _validate_directory_shape(config.completion_directory)


def _verify(config: PhaseCompletionConfig) -> _Evidence:
    gate_bytes = _read_binding(config.gate_config, 65_536)
    gate = _object(_gate_json(gate_bytes), {
        "schema_version", "context", "bridge_config", "session_directory", "cwd", "provider", "model",
        "budget", "prior_session", "prior_session_id", "prior_cwd", "final_lock_path",
        "gate_outcome_directory", "expected_rows",
    })
    if (gate["schema_version"] != GATE_SCHEMA or gate["context"] != config.context or
            gate["provider"] != "openai-codex" or gate["model"] != "gpt-5.6-sol" or
            gate["budget"] != BUDGET or gate["expected_rows"] != 292 or
            not isinstance(gate["cwd"], str) or not _canonical_directory_text(gate["cwd"])):
        raise _CompletionError("EVIDENCE_MISMATCH")
    session_directory = _gate_directory(gate["session_directory"])
    gate_outcome_directory = _gate_directory(gate["gate_outcome_directory"])
    completion = _verified_completion_directory(config.completion_directory)

    process_bytes = _read_binding(config.process_config, 65_536)
    process_value = _gate_json(process_bytes)
    process = RunControllerConfig.from_dict(_mapping(process_value))
    _verify_process_config(process, gate, session_directory)
    frontend = _read_frontend_deployment(process)
    _verify_frontend_deployment(frontend, process, gate)

    receipt_bytes = _read_binding(config.process_receipt, 1_048_576)
    receipt = _mapping(_gate_json(receipt_bytes))
    if (type(receipt.get("returncode")) is not int or receipt["returncode"] != 0 or
            not _valid_prior_process_receipt(receipt, config.current_session.path)):
        raise _CompletionError("EVIDENCE_MISMATCH")
    _verify_process_receipt(receipt, process)

    current_bytes = _read_binding(config.current_session, 8_388_608)
    if (config.current_session.path.name != config.current_session_id + ".jsonl" or
            config.current_session.path.parent != session_directory.path or
            config.current_session.path.parent != Path(process.session_dir)):
        raise _CompletionError("EVIDENCE_MISMATCH")
    current = parse_session_usage(
        current_bytes, config.current_session_id, gate["cwd"], gate["provider"], gate["model"],
    )
    prior, bridge_path, bridge_bytes = _gate_dependencies(gate, config.context)
    sessions = (() if prior is None else (prior,)) + (current,)
    combined = combine_usage(sessions, BUDGET)

    bridge = load_bridge_from_config(bridge_path, gate["bridge_config"]["sha256"])
    bridge_binding = _binding_from_mapping(gate["bridge_config"], 65_536)
    if _read_binding(bridge_binding, 65_536) != bridge_bytes:
        raise _CompletionError("EVIDENCE_MISMATCH")
    bridge_config_value = _mapping(_gate_json(bridge_bytes))
    _verify_context_rights(config, bridge, bridge_config_value)
    _verify_disjoint_roots(completion, process, gate, bridge_config_value, config.current_session.path)

    observer_config = UsageObserverConfig(
        session_directory, gate["cwd"], gate["provider"], gate["model"], BUDGET,
        () if prior is None else (prior,),
    )
    latest_binding, latest, latest_checkpoint = _latest_gate(
        gate_outcome_directory, config.gate_config.sha256, observer_config,
    )
    observation = _usage_observation(latest.get("usage"))
    _verify_gate_usage(observation, latest_checkpoint, config, current, combined)

    public = _mapping(bridge.handle({"action": "read_public_result", "arguments": {}}))
    dev = _mapping(bridge.handle({"action": "read_dev_result", "arguments": {}}))
    research = _mapping(bridge.handle({"action": "read_solution", "arguments": {"path": "research.md"}}))
    final_lock, final_binding = _read_final_lock(config, gate, bridge, public)
    decision = decide_phase(config.context, public, dev, research, observation, final_lock, 292)
    _verify_latest_gate(latest, config, bridge_binding.sha256, decision, public, dev, research, final_binding)
    _verify_ready(config.context, decision, current, combined)
    _verify_completion_directory_unchanged(completion)
    return _Evidence(
        gate, config.gate_config, config.process_config, config.process_receipt, config.current_session,
        bridge_binding, latest_binding, current, prior, combined, public, dev, research,
        decision, final_lock, final_binding,
    )


def _verify_ready(context: str, decision: GateDecision, current: SessionUsage, combined: CampaignUsage) -> None:
    if not current.complete or not current.response_ids or not combined.complete:
        raise _CompletionError("USAGE_UNKNOWN")
    if combined.total_tokens >= BUDGET:
        raise _CompletionError("BUDGET_EXHAUSTED")
    expected = "READY_INITIAL_CHECKPOINT" if context == "initial" else "READY_FINAL_LOCK"
    if not decision.ready or decision.outcome != expected:
        if decision.outcome == "STOP_USAGE_UNKNOWN":
            raise _CompletionError("USAGE_UNKNOWN")
        if decision.outcome == "STOP_BUDGET":
            raise _CompletionError("BUDGET_EXHAUSTED")
        raise _CompletionError("NOT_READY")


def _verify_process_config(process: RunControllerConfig, gate: Mapping[str, object],
                           session_directory: DirectoryIdentity) -> None:
    if process.synthetic_test_context is not False:
        raise _CompletionError("EVIDENCE_MISMATCH")
    if (process.session_dir != str(session_directory.path) or
            (process.session_dir_identity.device, process.session_dir_identity.inode) !=
            (session_directory.device, session_directory.inode)):
        raise _CompletionError("EVIDENCE_MISMATCH")
    try:
        _validate_identity(process.process_exec_path, process.process_exec_identity, executable=False, max_file_bytes=1_048_576)
        _validate_identity(process.frontend_path, process.frontend_identity, executable=False, max_file_bytes=1_048_576)
        _validate_identity(process.deployment_path, process.deployment_identity, executable=False, max_file_bytes=1_048_576)
    except ValueError:
        raise _CompletionError("EVIDENCE_MISMATCH") from None
    if dict(process.child_environment).get("PRIME_AGENT_TELEMETRY") != "0":
        raise _CompletionError("EVIDENCE_MISMATCH")


def _read_frontend_deployment(process: RunControllerConfig) -> Mapping[str, object]:
    identity = process.deployment_identity
    data = _gate_read(
        Path(process.deployment_path), 1_048_576, identity.sha256, identity.size, identity.mtime_ns_max,
    )
    return _mapping(_gate_json(data))


def _verify_frontend_deployment(frontend: Mapping[str, object], process: RunControllerConfig,
                                gate: Mapping[str, object]) -> None:
    _exact_keys(frontend, {"schema_version", "status", "assets", "directories", "runtime", "environment", "limits"})
    if (frontend["schema_version"] != "argo-house-price-a2-controller-main-deployment/v1" or
            frontend["status"] != "TRUSTED_FIXED_DEPLOYMENT"):
        raise _CompletionError("EVIDENCE_MISMATCH")
    assets = _mapping(frontend["assets"])
    directories = _mapping(frontend["directories"])
    runtime = _mapping(frontend["runtime"])
    environment = _mapping(frontend["environment"])
    controller_main = _mapping(assets.get("controller_main"))
    node = _mapping(assets.get("node_executable"))
    kernel = _mapping(assets.get("kernel_interpreter"))
    expected_phase = "dev" if gate["context"] == "initial" else "final_refit"
    if (not _file_seal_matches(controller_main, process.frontend_path, process.frontend_identity) or
            not _file_seal_matches(node, process.node_executable, process.node_identity) or
            kernel.get("invocation_path") != process.python_executable or
            runtime.get("model") != gate["provider"] + "/" + gate["model"] or
            runtime.get("phase") != expected_phase or
            runtime.get("mode") != "text" or runtime.get("print") is not True or
            runtime.get("offline") is not True or runtime.get("fresh_session") is not True):
        raise _CompletionError("EVIDENCE_MISMATCH")
    for key, path, identity in (
        ("artifact_root", process.artifact_root, process.artifact_root_identity),
        ("cwd", gate["cwd"], None),
        ("profile", process.profile_dir, process.profile_dir_identity),
        ("session_dir", process.session_dir, process.session_dir_identity),
        ("temporary_dir", process.temporary_dir, process.temporary_dir_identity),
    ):
        seal = _mapping(directories.get(key))
        if seal.get("path") != path:
            raise _CompletionError("EVIDENCE_MISMATCH")
        if identity is not None and (seal.get("device") != str(identity.device) or seal.get("inode") != str(identity.inode)):
            raise _CompletionError("EVIDENCE_MISMATCH")
    exact_environment = _mapping(environment.get("exact"))
    if exact_environment != dict(process.child_environment):
        raise _CompletionError("EVIDENCE_MISMATCH")
    limits = _mapping(frontend["limits"])
    for key in (
        "provider_timeout_ms", "provider_retries", "phase_wall_seconds", "campaign_wall_seconds",
        "cpu_seconds_per_process", "file_size_bytes", "rss_trigger_bytes", "rss_sample_ms",
        "v8_old_space_mib", "model_tokens_between_turns", "controller_turn_limit_per_phase",
        "source_text_max_bytes", "autonomous_gate_retries", "autonomous_gate_timeout_ms",
        "bridge_close_grace_ms",
    ):
        if limits.get(key) != getattr(process.caps, key):
            raise _CompletionError("EVIDENCE_MISMATCH")


def _verify_process_receipt(receipt: Mapping[str, object], process: RunControllerConfig) -> None:
    handle = _mapping(receipt.get("handle"))
    resources = _mapping(receipt.get("resources"))
    if (handle.get("process_exec_path") != process.process_exec_path or
            handle.get("frontend_path") != process.frontend_path or
            handle.get("deployment_path") != process.deployment_path or
            handle.get("artifact_root") != process.artifact_root or
            handle.get("session_dir") != process.session_dir or
            handle.get("child_environment_keys") != sorted(process.child_environment) or
            handle.get("stdin_mode") != "DEVNULL" or
            Path(handle.get("stdout_path", "")).parent != Path(process.artifact_root) or
            Path(handle.get("stderr_path", "")).parent != Path(process.artifact_root) or
            receipt.get("started_monotonic_ns", 0) < process.campaign_started_monotonic_ns):
        raise _CompletionError("EVIDENCE_MISMATCH")
    comparisons = {
        "provider_timeout_ms": process.caps.provider_timeout_ms,
        "provider_retries": process.caps.provider_retries,
        "model_tokens_between_turns": process.caps.model_tokens_between_turns,
        "controller_turn_limit_per_phase": process.caps.controller_turn_limit_per_phase,
        "source_text_max_bytes": process.caps.source_text_max_bytes,
        "autonomous_gate_retries": process.caps.autonomous_gate_retries,
        "autonomous_gate_timeout_ms": process.caps.autonomous_gate_timeout_ms,
        "bridge_close_grace_ms": process.caps.bridge_close_grace_ms,
        "rss_trigger_bytes": process.caps.rss_trigger_bytes,
        "rss_sample_interval_ms": process.caps.rss_sample_ms,
        "regular_file_rlimit_bytes": process.caps.file_size_bytes,
        "cpu_rlimit_seconds_per_process": process.caps.cpu_seconds_per_process,
        "phase_wall_seconds": process.caps.phase_wall_seconds,
        "campaign_wall_seconds": process.caps.campaign_wall_seconds,
        "observer_output_limit_bytes": process.caps.observer_output_bytes,
        "artifact_file_count_trigger": process.caps.artifact_file_count,
        "artifact_aggregate_bytes_trigger": process.caps.artifact_aggregate_bytes,
    }
    if any(resources.get(key) != value for key, value in comparisons.items()):
        raise _CompletionError("EVIDENCE_MISMATCH")


def _gate_dependencies(gate: Mapping[str, object], context: str) -> tuple[SessionUsage | None, Path, bytes]:
    bridge_path, bridge_bytes = _gate_file_binding(gate["bridge_config"], 65_536)
    if context == "initial":
        if any(gate[key] is not None for key in ("prior_session", "prior_session_id", "prior_cwd")):
            raise _CompletionError("EVIDENCE_MISMATCH")
        return None, bridge_path, bridge_bytes
    if (not isinstance(gate["prior_session_id"], str) or UUID.fullmatch(gate["prior_session_id"]) is None or
            not isinstance(gate["prior_cwd"], str)):
        raise _CompletionError("EVIDENCE_MISMATCH")
    prior_path, prior_bytes = _gate_file_binding(gate["prior_session"], 8_388_608)
    if prior_path.name != gate["prior_session_id"] + ".jsonl":
        raise _CompletionError("EVIDENCE_MISMATCH")
    prior = parse_session_usage(
        prior_bytes, gate["prior_session_id"], gate["prior_cwd"], gate["provider"], gate["model"],
    )
    if not prior.complete or not prior.response_ids:
        raise _CompletionError("USAGE_UNKNOWN")
    return prior, bridge_path, bridge_bytes


def _latest_gate(directory: DirectoryIdentity, config_sha256: str,
                 observer: UsageObserverConfig) -> tuple[FileBinding, Mapping[str, object], Mapping[str, object]]:
    descriptor = os.open(directory.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        _assert_directory_fd(descriptor, directory)
        try:
            os.stat(".gate-evaluation.lock", dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _CompletionError("EVIDENCE_MISMATCH")
        checkpoint, count, _, _ = _read_gate_history(descriptor, config_sha256, observer)
        if count < 1 or checkpoint is None:
            raise _CompletionError("EVIDENCE_MISMATCH")
        names = []
        with os.scandir(descriptor) as entries:
            for entry in entries:
                if entry.name == ".gate-evaluation.lock":
                    raise _CompletionError("EVIDENCE_MISMATCH")
                names.append(entry.name)
                if len(names) > 40:
                    raise _CompletionError("EVIDENCE_MISMATCH")
        names.sort()
        if len(names) != count:
            raise _CompletionError("EVIDENCE_MISMATCH")
        name = names[-1]
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
            raise _CompletionError("EVIDENCE_MISMATCH")
        record_identity = _stat_identity(info)
        binding = FileBinding(directory.path / name, "0" * 64, info.st_size, info.st_mtime_ns)
    finally:
        os.close(descriptor)
    data = _gate_read(binding.path, 16_384, None, binding.bytes, binding.mtime_ns_max)
    binding = FileBinding(binding.path, hashlib.sha256(data).hexdigest(), binding.bytes, binding.mtime_ns_max)
    reopened = _gate_read(binding.path, 16_384, binding.sha256, binding.bytes, binding.mtime_ns_max)
    latest = _mapping(_gate_json(reopened))
    second = os.open(directory.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        _assert_directory_fd(second, directory)
        named = os.stat(name, dir_fd=second, follow_symlinks=False)
        if _stat_identity(named) != record_identity:
            raise _CompletionError("EVIDENCE_MISMATCH")
        try:
            os.stat(".gate-evaluation.lock", dir_fd=second, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _CompletionError("EVIDENCE_MISMATCH")
    finally:
        os.close(second)
    if latest.get("usage_checkpoint") != checkpoint:
        raise _CompletionError("EVIDENCE_MISMATCH")
    return binding, latest, checkpoint


def _verify_gate_usage(observation: UsageObservation, checkpoint: Mapping[str, object],
                       config: PhaseCompletionConfig, current: SessionUsage,
                       combined: CampaignUsage) -> None:
    if (_mapping(checkpoint).get("observation") != asdict(observation) or
            observation.session_id != config.current_session_id or
            observation.session_sha256 != config.current_session.sha256 or
            observation.observed_bytes != config.current_session.bytes or
            observation.current_tokens != current.total_tokens or
            observation.total_tokens != combined.total_tokens):
        raise _CompletionError("EVIDENCE_MISMATCH")


def _verify_latest_gate(latest: Mapping[str, object], config: PhaseCompletionConfig,
                        bridge_config_sha256: str, decision: GateDecision, public: Mapping[str, object], dev: Mapping[str, object],
                        research: Mapping[str, object], final_lock_binding: FileBinding | None) -> None:
    _exact_keys(latest, {
        "schema_version", "context", "config_sha256", "bridge_config_sha256", "decision", "usage",
        "view_sha256", "final_lock_sha256", "sequence", "previous_outcome_sha256", "usage_checkpoint",
    })
    view_hashes = {
        name: hashlib.sha256(_canonical(value)).hexdigest()
        for name, value in (("public", public), ("dev", dev), ("research", research))
    }
    expected_lock = None if final_lock_binding is None else final_lock_binding.sha256
    if (latest["schema_version"] != GATE_OUTCOME_SCHEMA or latest["context"] != config.context or
            latest["config_sha256"] != config.gate_config.sha256 or
            latest["bridge_config_sha256"] != bridge_config_sha256 or
            _canonical(latest["decision"]) != _canonical(asdict(decision)) or
            latest["view_sha256"] != view_hashes or
            latest["final_lock_sha256"] != expected_lock):
        raise _CompletionError("EVIDENCE_MISMATCH")


def _read_final_lock(config: PhaseCompletionConfig, gate: Mapping[str, object], bridge: object,
                     public: Mapping[str, object]) -> tuple[FinalArtifactLock | None, FileBinding | None]:
    state_root = bridge.config.state_root.path
    expected_path = state_root / "final-artifact-lock.json"
    if not isinstance(gate["final_lock_path"], str) or Path(gate["final_lock_path"]) != expected_path:
        raise _CompletionError("EVIDENCE_MISMATCH")
    public_result = _mapping(public.get("result")) if public.get("ok") is True else {}
    if config.context == "initial":
        if public_result.get("phase") == "final_locked" or expected_path.exists():
            raise _CompletionError("EVIDENCE_MISMATCH")
        return None, None
    binding = _binding_for_path(expected_path, 16_384)
    data = _read_binding(binding, 16_384)
    value = _mapping(_gate_json(data))
    _exact_keys(value, {field.name for field in fields(FinalArtifactLock)})
    lock = FinalArtifactLock(**value)
    stored = bridge.config.trusted_io.final_artifact_lock()
    if lock != stored or data != _canonical(asdict(stored)):
        raise _CompletionError("EVIDENCE_MISMATCH")
    if (lock.task_sha256 != bridge.config.task_sha256 or
            lock.environment_sha256 != bridge.config.environment_sha256 or
            lock.protocol_sha256 != bridge.config.protocol_sha256 or
            lock.outer_training_manifest_sha256 != bridge.config.outer_training_manifest_sha256 or
            lock.hidden_features_manifest_sha256 != bridge.config.hidden_features_manifest_sha256):
        raise _CompletionError("EVIDENCE_MISMATCH")
    return lock, binding


def _verify_context_rights(config: PhaseCompletionConfig, bridge: object,
                           bridge_value: Mapping[str, object]) -> None:
    rights = bridge.config.context_rights
    expected = _mapping(bridge_value.get("context_rights"))
    if (rights.context != config.context or rights.initial_context_id != config.initial_context_id or
            rights.controller_context_id != config.controller_context_id or
            expected.get("context") != config.context or expected.get("initial_context_id") != config.initial_context_id or
            expected.get("controller_context_id") != config.controller_context_id):
        raise _CompletionError("EVIDENCE_MISMATCH")


def _verify_disjoint_roots(completion: DirectoryIdentity, process: RunControllerConfig,
                           gate: Mapping[str, object], bridge_value: Mapping[str, object], session: Path) -> None:
    directories = _mapping(bridge_value.get("directories"))
    source = Path(_mapping(directories.get("source")).get("path", ""))
    protected = {Path(process.artifact_root), Path(process.profile_dir), Path(process.session_dir), source, session.parent}
    for path in protected:
        if not path.is_absolute() or _overlaps(completion.path, path):
            raise _CompletionError("EVIDENCE_MISMATCH")
    outcome = Path(_mapping(gate["gate_outcome_directory"])["path"])
    if _overlaps(completion.path, outcome):
        raise _CompletionError("EVIDENCE_MISMATCH")


def _publication_payload(config: PhaseCompletionConfig, evidence: _Evidence) -> tuple[bytes, str]:
    dev_ids = sorted(evidence.decision.verified_dev_run_ids)
    research_result = _mapping(evidence.research.get("result"))
    research_sha = research_result.get("sha256")
    if not isinstance(research_sha, str) or HEX64.fullmatch(research_sha) is None:
        raise _CompletionError("EVIDENCE_MISMATCH")
    if config.context == "initial":
        value = {
            "schema_version": HANDOFF_SCHEMA,
            "initial_context_id": config.initial_context_id,
            "next_context_id": config.next_context_id,
            "verified_dev_run_ids": dev_ids,
            "research_sha256": research_sha,
            "prior_process_receipt": _binding_dict(evidence.receipt_binding),
            "prior_session": _binding_dict(evidence.session_binding),
            "prior_session_id": config.current_session_id,
            "prior_cwd": evidence.gate["cwd"],
            "provider": evidence.gate["provider"],
            "model": evidence.gate["model"],
            "campaign_token_budget": BUDGET,
            "campaign_used_tokens": evidence.campaign_usage.total_tokens,
        }
        return _canonical(value), "initial-handoff.json"
    if evidence.prior_usage is None or evidence.final_lock is None or evidence.final_lock_binding is None:
        raise _CompletionError("EVIDENCE_MISMATCH")
    value = {
        "schema_version": FINAL_SCHEMA,
        "initial_context_id": config.initial_context_id,
        "controller_context_id": config.controller_context_id,
        "process_config": _binding_dict(evidence.process_binding),
        "process_receipt": _binding_dict(evidence.receipt_binding),
        "gate_config": _binding_dict(evidence.gate_binding),
        "native_gate_outcome": _binding_dict(evidence.latest_gate_binding),
        "bridge_config": _binding_dict(evidence.bridge_binding),
        "current_session": _binding_dict(evidence.session_binding),
        "current_session_id": config.current_session_id,
        "prior_session": _binding_dict(_binding_from_mapping(evidence.gate["prior_session"], 8_388_608)),
        "prior_session_id": evidence.gate["prior_session_id"],
        "cwd": evidence.gate["cwd"],
        "provider": evidence.gate["provider"],
        "model": evidence.gate["model"],
        "campaign_token_budget": BUDGET,
        "current_used_tokens": evidence.current_usage.total_tokens,
        "campaign_used_tokens": evidence.campaign_usage.total_tokens,
        "verified_dev_run_ids": dev_ids,
        "research_sha256": research_sha,
        "final_artifact_lock": _binding_dict(evidence.final_lock_binding),
        "final_lock_sha256": evidence.final_lock_binding.sha256,
        "final_lock": asdict(evidence.final_lock),
        "hidden_score_observed": False,
    }
    return _canonical(value), "final-completion.json"


def _publish(directory: DirectoryIdentity, name: str, payload: bytes) -> FileBinding:
    if name not in {"initial-handoff.json", "final-completion.json"} or not 0 < len(payload) <= 65_536:
        raise _PublicationError()
    descriptor = os.open(directory.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    output: int | None = None
    try:
        _assert_directory_fd(descriptor, directory)
        output = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=descriptor)
        _write_all(output, payload)
        os.fsync(output)
        created = os.fstat(output)
        if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1 or created.st_size != len(payload):
            raise _PublicationError()
        os.close(output)
        output = None
        os.fsync(descriptor)
    except Exception:
        raise _PublicationError() from None
    finally:
        if output is not None:
            os.close(output)
        os.close(descriptor)
    binding = _binding_for_path(directory.path / name, 65_536)
    if _read_binding(binding, 65_536) != payload:
        raise _PublicationError()
    return binding


def _verified_completion_directory(identity: DirectoryIdentity) -> DirectoryIdentity:
    _validate_directory_shape(identity)
    descriptor = os.open(identity.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        _assert_directory_fd(descriptor, identity)
    finally:
        os.close(descriptor)
    return identity


def _verify_completion_directory_unchanged(identity: DirectoryIdentity) -> None:
    _verified_completion_directory(identity)


def _assert_directory_fd(descriptor: int, identity: DirectoryIdentity) -> None:
    opened = os.fstat(descriptor)
    named = identity.path.lstat()
    for item in (opened, named):
        if (not stat.S_ISDIR(item.st_mode) or stat.S_IMODE(item.st_mode) != 0o700 or
                (item.st_dev, item.st_ino) != (identity.device, identity.inode)):
            raise _CompletionError("EVIDENCE_MISMATCH")


def _validate_directory_shape(identity: DirectoryIdentity) -> None:
    if (not isinstance(identity, DirectoryIdentity) or not isinstance(identity.path, Path) or
            not identity.path.is_absolute() or ".." in identity.path.parts or
            type(identity.device) is not int or type(identity.inode) is not int or
            identity.device < 0 or identity.inode <= 0):
        raise ValueError()
    try:
        if identity.path.resolve(strict=True) != identity.path:
            raise ValueError()
    except (OSError, RuntimeError):
        raise ValueError() from None


def _validate_binding_shape(binding: FileBinding, cap: int) -> None:
    if (not isinstance(binding, FileBinding) or not isinstance(binding.path, Path) or
            not binding.path.is_absolute() or ".." in binding.path.parts or
            not isinstance(binding.sha256, str) or HEX64.fullmatch(binding.sha256) is None or
            type(binding.bytes) is not int or not 0 < binding.bytes <= cap or
            type(binding.mtime_ns_max) is not int or not 0 <= binding.mtime_ns_max <= 2 ** 63 - 1):
        raise ValueError()


def _read_binding(binding: FileBinding, cap: int) -> bytes:
    _validate_binding_shape(binding, cap)
    try:
        return _gate_read(binding.path, cap, binding.sha256, binding.bytes, binding.mtime_ns_max)
    except GateConfigError:
        raise _CompletionError("EVIDENCE_MISMATCH") from None


def _binding_from_mapping(value: object, cap: int) -> FileBinding:
    record = _mapping(value)
    _exact_keys(record, {"path", "sha256", "bytes", "mtime_ns_max"})
    if not isinstance(record["path"], str):
        raise _CompletionError("EVIDENCE_MISMATCH")
    binding = FileBinding(Path(record["path"]), record["sha256"], record["bytes"], record["mtime_ns_max"])
    _validate_binding_shape(binding, cap)
    return binding


def _binding_for_path(path: Path, cap: int) -> FileBinding:
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not 0 < info.st_size <= cap:
            raise OSError()
        data = _gate_read(path, cap, None, info.st_size, info.st_mtime_ns)
    except (OSError, GateConfigError):
        raise _CompletionError("EVIDENCE_MISMATCH") from None
    return FileBinding(path, hashlib.sha256(data).hexdigest(), len(data), info.st_mtime_ns)


def _file_seal_matches(seal: Mapping[str, object], path: str, identity: object) -> bool:
    return (seal.get("path") == path and seal.get("sha256") == identity.sha256 and
            seal.get("bytes") == identity.size and seal.get("mtime_ns_max") == str(identity.mtime_ns_max))


def _usage_observation(value: object) -> UsageObservation:
    record = _mapping(value)
    _exact_keys(record, {field.name for field in fields(UsageObservation)})
    try:
        return UsageObservation(**record)
    except TypeError:
        raise _CompletionError("EVIDENCE_MISMATCH") from None


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise _CompletionError("EVIDENCE_MISMATCH")
    return value


def _object(value: object, keys: set[str]) -> Mapping[str, object]:
    record = _mapping(value)
    _exact_keys(record, keys)
    return record


def _exact_keys(value: Mapping[str, object], keys: set[str]) -> None:
    if set(value) != keys:
        raise _CompletionError("EVIDENCE_MISMATCH")


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                          allow_nan=False).encode("ascii")
    except (ValueError, TypeError, UnicodeError):
        raise _CompletionError("EVIDENCE_MISMATCH") from None


def _canonical_directory_text(value: str) -> bool:
    try:
        path = Path(value)
        info = path.lstat()
        return (path.is_absolute() and ".." not in path.parts and path.resolve(strict=True) == path and
                stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode))
    except (OSError, RuntimeError):
        return False


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise _PublicationError()
        offset += written


def _binding_dict(binding: FileBinding) -> dict[str, object]:
    return {
        "path": str(binding.path), "sha256": binding.sha256,
        "bytes": binding.bytes, "mtime_ns_max": binding.mtime_ns_max,
    }
