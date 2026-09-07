"""Pure verifier for one separately labeled A2 synthetic combination case."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Mapping

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import _valid_prior_process_receipt
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import (
    SessionUsage,
    UsageError,
    parse_session_usage,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    FROZEN_PRODUCTION_CAPS,
    PRODUCTION_ENV_KEYS,
    PRODUCTION_FIXED_ENV,
    RunControllerConfig,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion import (
    _latest_gate,
    _verify_process_receipt,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import (
    _gate_directory,
    _gate_file_binding,
    _gate_json,
    _gate_read,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import (
    ClosureError,
    ClosureLimits,
    SourceTree,
    verify_tree,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import (
    UsageObservation,
    UsageObserverConfig,
)

HEX64 = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
NORMAL_FRONTEND_SHA256 = "dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21"
PROCESS_EXEC_SHA256 = "c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840"
SYNTHETIC_FRONTEND_SHA256 = "4c9b73b8d759fd0dd0061c84dd28a658452eaed6175fda4ba23ff4b60e6b09d6"
EXPECTED_TOOL_SCHEMA_SHA256 = "553e00b05207cc51eaf80d3d58ff480279319990ce620409ea52a1e4d281ad61"
RESPONSE_IDS = ("a2-combination-response-0001", "a2-combination-response-0002")
TOOL_CALL_ID = "a2-combination-tool-0001"
FINAL_TEXT = "A2 synthetic combination frontend complete."
METADATA_NAME = "a2-synthetic-provider-metadata.json"
TOOLS = (
    "read_solution", "write_solution", "request_R1_run", "read_public_result",
    "read_dev_result", "lock_final_artifact",
)
DEPLOYMENT_ASSET_KEYS = {
    "prime_entry", "prime_closure_manifest", "controller_main", "frontend_closure_manifest",
    "extension", "binding", "settings", "system_prompt", "task_prompt", "autonomous_gate",
    "node_executable", "kernel_interpreter",
}
DEPLOYMENT_DIRECTORY_KEYS = {"artifact_root", "cwd", "profile", "session_dir", "temporary_dir"}
DEPLOYMENT_RUNTIME_KEYS = {"phase", "model", "thinking", "mode", "print", "offline", "fresh_session", "tools"}
DEPLOYMENT_ENVIRONMENT_KEYS = {"exact", "home_must_be_unset", "forbidden_prefixes"}
DEPLOYMENT_LIMIT_KEYS = {
    "provider_timeout_ms", "provider_retries", "phase_wall_seconds", "campaign_wall_seconds",
    "cpu_seconds_per_process", "file_size_bytes", "rss_trigger_bytes", "rss_sample_ms",
    "v8_old_space_mib", "model_tokens_between_turns", "controller_turn_limit_per_phase",
    "source_text_max_bytes", "bridge_close_grace_ms", "autonomous_max_continuations",
    "autonomous_gate_retries", "autonomous_gate_timeout_ms",
}
STATE_LIMITS = ClosureLimits(256, 8388608, 2097152, 8, 1024)
NAMESPACE_LIMITS = ClosureLimits(160, 8388608, 1048576, 8, 4096)
FRONTEND_LIMITS = ClosureLimits(160, 8388608, 1048576, 8, 4096)
PRIME_LIMITS = ClosureLimits(30000, 268435456, 67108864, 32, 4096)
INSTALLED_PRIME_ROOT = Path("/opt/homebrew/lib/node_modules/prime-agent")
REASONS = frozenset({
    "CONFIG_INVALID", "SOURCE_MISMATCH", "PROCESS_INVALID", "USAGE_UNKNOWN",
    "GATE_INVALID", "TOOL_TRANSCRIPT_INVALID", "METADATA_INVALID", "OUTPUT_LIMIT",
})


@dataclass(frozen=True)
class CombinationExpectation:
    controller_context_id: str
    normal_process_config: FileBinding
    synthetic_process_config: FileBinding
    process_receipt: FileBinding
    gate_config: FileBinding
    metadata: FileBinding
    current_session: FileBinding
    current_session_id: str
    synthetic_frontend: FileBinding
    verified_dev_run_ids: tuple[str, str]
    research_sha256: str
    state_trees: tuple[SourceTree, SourceTree, SourceTree]
    namespace_tree: SourceTree
    frontend_tree: SourceTree
    installed_prime_tree: SourceTree
    elapsed_limit_seconds: int


@dataclass(frozen=True)
class CombinationAssessment:
    status: str
    reason: str
    campaign_tokens: int | None
    session_sha256: str | None
    native_gate_sha256: str | None


class _Reject(ValueError):
    def __init__(self, reason: str):
        self.reason = reason if reason in REASONS else "CONFIG_INVALID"
        super().__init__(self.reason)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise _Reject("CONFIG_INVALID") from None


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise _Reject("CONFIG_INVALID")
        output[key] = value
    return output


def _reject_constant(_value: str) -> object:
    raise _Reject("CONFIG_INVALID")


def _json(data: bytes, reason: str) -> dict[str, object]:
    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=_object_pairs, parse_constant=_reject_constant,
        )
    except (ValueError, UnicodeError, RecursionError):
        raise _Reject(reason) from None
    if type(value) is not dict:
        raise _Reject(reason)
    return value


def _binding_shape(binding: FileBinding, cap: int) -> None:
    if (
        not isinstance(binding, FileBinding)
        or not isinstance(binding.path, Path)
        or not binding.path.is_absolute()
        or ".." in binding.path.parts
        or type(binding.sha256) is not str
        or HEX64.fullmatch(binding.sha256) is None
        or type(binding.bytes) is not int
        or not 0 <= binding.bytes <= cap
        or type(binding.mtime_ns_max) is not int
        or binding.mtime_ns_max < 0
    ):
        raise _Reject("CONFIG_INVALID")


def _read(binding: FileBinding, cap: int, reason: str, *, allow_empty: bool = False) -> bytes:
    _binding_shape(binding, cap)
    if binding.bytes == 0 and not allow_empty:
        raise _Reject(reason)
    try:
        return _gate_read(
            binding.path, cap, binding.sha256, binding.bytes, binding.mtime_ns_max,
        )
    except Exception:
        if allow_empty and binding.bytes == 0:
            return _read_zero_file(binding, cap, reason)
        raise _Reject(reason) from None


def _read_zero_file(binding: FileBinding, cap: int, reason: str) -> bytes:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        descriptor = os.open(binding.path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            data = stream.read(cap + 1)
            after = os.fstat(stream.fileno())
        named = binding.path.lstat()
    except OSError:
        raise _Reject(reason) from None
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or _identity(before) != _identity(after)
        or _identity(after) != _identity(named)
        or data != b""
        or binding.bytes != 0
        or binding.sha256 != hashlib.sha256(b"").hexdigest()
    ):
        raise _Reject(reason)
    return data


def _identity(info: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
        info.st_size, info.st_mtime_ns, info.st_ctime_ns,
    )


def _overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _path_within(path: Path, root: Path) -> bool:
    try:
        return path != root and root in path.parents
    except (OSError, RuntimeError):
        return False


def _validate_expectation(expectation: CombinationExpectation) -> tuple[SourceTree, ...]:
    if (
        not isinstance(expectation, CombinationExpectation)
        or type(expectation.controller_context_id) is not str
        or HEX64.fullmatch(expectation.controller_context_id) is None
        or type(expectation.current_session_id) is not str
        or UUID.fullmatch(expectation.current_session_id) is None
        or type(expectation.research_sha256) is not str
        or HEX64.fullmatch(expectation.research_sha256) is None
        or type(expectation.verified_dev_run_ids) is not tuple
        or len(expectation.verified_dev_run_ids) != 2
        or tuple(sorted(expectation.verified_dev_run_ids)) != expectation.verified_dev_run_ids
        or len(set(expectation.verified_dev_run_ids)) != 2
        or any(UUID.fullmatch(value) is None for value in expectation.verified_dev_run_ids)
        or type(expectation.elapsed_limit_seconds) is not int
        or expectation.elapsed_limit_seconds != 20
        or type(expectation.state_trees) is not tuple
        or len(expectation.state_trees) != 3
    ):
        raise _Reject("CONFIG_INVALID")
    for binding, cap in (
        (expectation.normal_process_config, 65536),
        (expectation.synthetic_process_config, 65536),
        (expectation.process_receipt, 1048576),
        (expectation.gate_config, 65536),
        (expectation.metadata, 4096),
        (expectation.current_session, 8388608),
        (expectation.synthetic_frontend, 1048576),
    ):
        _binding_shape(binding, cap)
    trees = expectation.state_trees + (
        expectation.namespace_tree, expectation.frontend_tree, expectation.installed_prime_tree,
    )
    if any(not isinstance(tree, SourceTree) or HEX64.fullmatch(tree.tree_sha256) is None for tree in trees):
        raise _Reject("CONFIG_INVALID")
    roots = tuple(Path(tree.root) for tree in trees)
    if Path(expectation.installed_prime_tree.root) != INSTALLED_PRIME_ROOT:
        raise _Reject("CONFIG_INVALID")
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            if _overlap(left, right):
                raise _Reject("CONFIG_INVALID")
    return trees


def _load_process_config(binding: FileBinding) -> RunControllerConfig:
    value = _json(_read(binding, 65536, "CONFIG_INVALID"), "CONFIG_INVALID")
    try:
        config = RunControllerConfig.from_dict(value)
    except Exception:
        raise _Reject("CONFIG_INVALID") from None
    if config.synthetic_test_context is not False:
        raise _Reject("CONFIG_INVALID")
    if (
        set(config.child_environment) != PRODUCTION_ENV_KEYS
        or any(config.child_environment.get(key) != value for key, value in PRODUCTION_FIXED_ENV.items())
        or config.child_environment.get("PRIME_AGENT_CODING_AGENT_DIR") != config.profile_dir
        or config.child_environment.get("PRIME_AGENT_KERNEL_PYTHON") != config.python_executable
        or config.child_environment.get("TMPDIR") != config.temporary_dir + "/"
        or config.python_executable != "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python"
    ):
        raise _Reject("CONFIG_INVALID")
    for key, value in FROZEN_PRODUCTION_CAPS.items():
        if getattr(config.caps, key) != value:
            raise _Reject("CONFIG_INVALID")
    if (
        config.caps.terminate_grace_seconds != 2
        or config.caps.kill_grace_seconds != 2
        or config.caps.observer_timeout_seconds != 3
    ):
        raise _Reject("CONFIG_INVALID")
    return config


def _load_configs(
    expectation: CombinationExpectation,
) -> tuple[RunControllerConfig, RunControllerConfig]:
    normal = _load_process_config(expectation.normal_process_config)
    synthetic = _load_process_config(expectation.synthetic_process_config)
    normal_value = asdict(normal)
    synthetic_value = asdict(synthetic)
    for key in ("frontend_path", "frontend_identity"):
        normal_value.pop(key)
        synthetic_value.pop(key)
    if (
        _canonical(normal_value) != _canonical(synthetic_value)
        or normal.frontend_path == synthetic.frontend_path
        or normal.frontend_identity.sha256 != NORMAL_FRONTEND_SHA256
        or synthetic.frontend_path != str(expectation.synthetic_frontend.path)
        or synthetic.frontend_identity.resolved_path != str(expectation.synthetic_frontend.path)
        or synthetic.frontend_identity.sha256 != expectation.synthetic_frontend.sha256
        or synthetic.frontend_identity.size != expectation.synthetic_frontend.bytes
        or synthetic.frontend_identity.mtime_ns_max != expectation.synthetic_frontend.mtime_ns_max
        or expectation.synthetic_frontend.path.name != "a2-combination-frontend.ts"
        or expectation.synthetic_frontend.sha256 != SYNTHETIC_FRONTEND_SHA256
        or normal.process_exec_identity.sha256 != PROCESS_EXEC_SHA256
        or synthetic.process_exec_identity.sha256 != PROCESS_EXEC_SHA256
        or not _path_within(Path(normal.frontend_path), Path(expectation.frontend_tree.root))
        or not _path_within(Path(synthetic.frontend_path), Path(expectation.frontend_tree.root))
        or not _path_within(Path(synthetic.process_exec_path), Path(expectation.namespace_tree.root))
    ):
        raise _Reject("CONFIG_INVALID")
    _read(expectation.synthetic_frontend, 1048576, "SOURCE_MISMATCH")
    for path, identity in (
        (Path(normal.frontend_path), normal.frontend_identity),
        (Path(synthetic.process_exec_path), synthetic.process_exec_identity),
    ):
        try:
            _gate_read(path, 1048576, identity.sha256, identity.size, identity.mtime_ns_max)
        except Exception:
            raise _Reject("SOURCE_MISMATCH") from None
    return normal, synthetic


def _verify_trees(
    expectation: CombinationExpectation,
    trees: tuple[SourceTree, ...],
    synthetic: RunControllerConfig,
) -> None:
    limits = (STATE_LIMITS, STATE_LIMITS, STATE_LIMITS, NAMESPACE_LIMITS, FRONTEND_LIMITS, PRIME_LIMITS)
    try:
        for tree, limit in zip(trees, limits):
            verify_tree(Path(tree.root), tree, limit)
    except Exception:
        raise _Reject("SOURCE_MISMATCH") from None
    protected = (
        expectation.normal_process_config.path,
        expectation.synthetic_process_config.path,
        expectation.process_receipt.path,
        expectation.metadata.path,
        expectation.current_session.path,
        Path(synthetic.artifact_root),
        Path(synthetic.profile_dir),
        Path(synthetic.session_dir),
        Path(synthetic.temporary_dir),
    )
    roots = tuple(Path(tree.root) for tree in trees)
    frontend_root = Path(expectation.frontend_tree.root)
    if expectation.gate_config.path != frontend_root / "gate-config.json":
        raise _Reject("SOURCE_MISMATCH")
    if any(
        _overlap(expectation.gate_config.path, root)
        for root in roots
        if root != frontend_root
    ):
        raise _Reject("SOURCE_MISMATCH")
    if any(any(_overlap(path, root) for root in roots) for path in protected):
        raise _Reject("SOURCE_MISMATCH")


def _task_prompt(
    expectation: CombinationExpectation,
    normal: RunControllerConfig,
    synthetic: RunControllerConfig,
) -> str:
    if (
        normal.deployment_path != synthetic.deployment_path
        or normal.deployment_identity != synthetic.deployment_identity
    ):
        raise _Reject("CONFIG_INVALID")
    identity = synthetic.deployment_identity
    try:
        deployment_bytes = _gate_read(
            Path(synthetic.deployment_path),
            65536,
            identity.sha256,
            identity.size,
            identity.mtime_ns_max,
        )
    except Exception:
        raise _Reject("CONFIG_INVALID") from None
    deployment = _json(deployment_bytes, "CONFIG_INVALID")
    if (
        set(deployment) != {"schema_version", "status", "assets", "directories", "runtime", "environment", "limits"}
        or deployment["schema_version"] != "argo-house-price-a2-controller-main-deployment/v1"
        or deployment["status"] != "TRUSTED_FIXED_DEPLOYMENT"
        or type(deployment["assets"]) is not dict
        or set(deployment["assets"]) != DEPLOYMENT_ASSET_KEYS
        or type(deployment["directories"]) is not dict
        or set(deployment["directories"]) != DEPLOYMENT_DIRECTORY_KEYS
        or type(deployment["runtime"]) is not dict
        or set(deployment["runtime"]) != DEPLOYMENT_RUNTIME_KEYS
        or type(deployment["environment"]) is not dict
        or set(deployment["environment"]) != DEPLOYMENT_ENVIRONMENT_KEYS
        or type(deployment["limits"]) is not dict
        or set(deployment["limits"]) != DEPLOYMENT_LIMIT_KEYS
    ):
        raise _Reject("CONFIG_INVALID")
    seal = deployment["assets"]["task_prompt"]
    if (
        type(seal) is not dict
        or set(seal) != {"path", "sha256", "bytes", "mtime_ns_max"}
        or type(seal["path"]) is not str
        or type(seal["sha256"]) is not str
        or HEX64.fullmatch(seal["sha256"]) is None
        or type(seal["bytes"]) is not int
        or not 0 < seal["bytes"] <= 131072
        or type(seal["mtime_ns_max"]) is not str
        or re.fullmatch(r"(?:0|[1-9][0-9]{0,18})", seal["mtime_ns_max"]) is None
    ):
        raise _Reject("CONFIG_INVALID")
    prompt_path = Path(seal["path"])
    if not _path_within(prompt_path, Path(expectation.frontend_tree.root)):
        raise _Reject("CONFIG_INVALID")
    try:
        data = _gate_read(
            prompt_path,
            131072,
            seal["sha256"],
            seal["bytes"],
            int(seal["mtime_ns_max"]),
        )
        text = data.decode("utf-8")
    except Exception:
        raise _Reject("SOURCE_MISMATCH") from None
    if not text.strip() or "\0" in text:
        raise _Reject("CONFIG_INVALID")
    return text


def _validate_public(value: object, expected_ids: tuple[str, str]) -> dict[str, object]:
    if type(value) is not dict or set(value) != {
        "phase", "dev_attempts", "final_attempts", "remaining_dev_opportunities", "runs",
    }:
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    runs = value["runs"]
    if (
        value["phase"] != "development"
        or type(value["dev_attempts"]) is not int
        or value["dev_attempts"] != 2
        or type(value["final_attempts"]) is not int
        or value["final_attempts"] != 0
        or type(value["remaining_dev_opportunities"]) is not int
        or value["remaining_dev_opportunities"] != 1
        or type(runs) is not list
        or len(runs) != 2
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    observed = []
    for run in runs:
        if type(run) is not dict or set(run) != {
            "intent_sha256", "run_id", "experiment_id", "solution_sha256", "phase", "status",
        }:
            raise _Reject("TOOL_TRANSCRIPT_INVALID")
        if (
            type(run["run_id"]) is not str
            or UUID.fullmatch(run["run_id"]) is None
            or type(run["experiment_id"]) is not str
            or UUID.fullmatch(run["experiment_id"]) is None
            or type(run["intent_sha256"]) is not str
            or HEX64.fullmatch(run["intent_sha256"]) is None
            or type(run["solution_sha256"]) is not str
            or HEX64.fullmatch(run["solution_sha256"]) is None
            or run["phase"] != "dev"
            or run["status"] != "DONE"
        ):
            raise _Reject("TOOL_TRANSCRIPT_INVALID")
        observed.append(run["run_id"])
    if tuple(sorted(observed)) != expected_ids:
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    return value


def _transcript(
    session: bytes,
    expected_ids: tuple[str, str],
    task_prompt: str,
) -> dict[str, object]:
    try:
        lines = session.splitlines()
        records = [_json(line, "TOOL_TRANSCRIPT_INVALID") for line in lines]
    except Exception:
        raise _Reject("TOOL_TRANSCRIPT_INVALID") from None
    messages = [record["message"] for record in records[1:] if record.get("type") == "message"]
    other_types = [record.get("type") for record in records[1:] if record.get("type") != "message"]
    if (
        len(messages) != 4
        or any(value not in {"model_change", "thinking_level_change", "service_tier_change"} for value in other_types)
        or len(other_types) != len(set(other_types))
        or any(type(message) is not dict for message in messages)
        or [message.get("role") for message in messages] != ["user", "assistant", "toolResult", "assistant"]
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    user = messages[0]
    if (
        set(user) != {"role", "content", "timestamp"}
        or user.get("role") != "user"
        or type(user.get("timestamp")) is not int
        or not 0 <= user["timestamp"] <= 2 ** 53 - 1
        or user.get("content") != [{"type": "text", "text": task_prompt}]
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    first = messages[1]
    tool_result = messages[2]
    final = messages[3]
    first_content = first.get("content")
    if type(first_content) is not list or len(first_content) != 1 or type(first_content[0]) is not dict:
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    tool_call = first_content[0]
    if (
        tool_call != {"type": "toolCall", "id": TOOL_CALL_ID, "name": "read_public_result", "arguments": {}}
        or first.get("responseId") != RESPONSE_IDS[0]
        or first.get("provider") != "openai-codex"
        or first.get("model") != "gpt-5.6-sol"
        or first.get("stopReason") not in {"stop", "toolUse"}
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    content = tool_result.get("content")
    timestamp = tool_result.get("timestamp")
    if (
        set(tool_result) != {
            "role", "toolCallId", "toolName", "content", "details", "isError", "timestamp",
        }
        or type(timestamp) is not int
        or not 0 <= timestamp <= 2 ** 53 - 1
        or tool_result.get("toolCallId") != TOOL_CALL_ID
        or tool_result.get("toolName") != "read_public_result"
        or tool_result.get("isError") is not False
        or tool_result.get("details") != {"action": "read_public_result"}
        or type(content) is not list
        or len(content) != 1
        or type(content[0]) is not dict
        or set(content[0]) != {"type", "text"}
        or content[0]["type"] != "text"
        or type(content[0]["text"]) is not str
        or len(content[0]["text"].encode("utf-8")) > 262144
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    public = _validate_public(
        _json(content[0]["text"].encode("utf-8"), "TOOL_TRANSCRIPT_INVALID"),
        expected_ids,
    )
    if (
        final.get("responseId") != RESPONSE_IDS[1]
        or final.get("provider") != "openai-codex"
        or final.get("model") != "gpt-5.6-sol"
        or final.get("stopReason") != "stop"
        or final.get("content") != [{"type": "text", "text": FINAL_TEXT}]
    ):
        raise _Reject("TOOL_TRANSCRIPT_INVALID")
    return public


def _usage(
    expectation: CombinationExpectation,
    synthetic: RunControllerConfig,
    gate: Mapping[str, object],
) -> tuple[SessionUsage, bytes]:
    session = _read(expectation.current_session, 8388608, "USAGE_UNKNOWN")
    if (
        expectation.current_session.path.name != expectation.current_session_id + ".jsonl"
        or expectation.current_session.path.parent != Path(synthetic.session_dir)
    ):
        raise _Reject("USAGE_UNKNOWN")
    try:
        usage = parse_session_usage(
            session,
            expectation.current_session_id,
            gate["cwd"],
            gate["provider"],
            gate["model"],
        )
    except Exception:
        raise _Reject("USAGE_UNKNOWN") from None
    if (
        not usage.complete
        or usage.assistant_messages != 2
        or usage.response_ids != RESPONSE_IDS
        or usage.total_tokens >= 120000
        or any(value <= 0 for value in (usage.input, usage.output, usage.cache_read, usage.cache_write))
    ):
        raise _Reject("USAGE_UNKNOWN")
    return usage, session


def _load_gate(
    expectation: CombinationExpectation,
    synthetic: RunControllerConfig,
) -> tuple[dict[str, object], object, bytes]:
    gate = _json(_read(expectation.gate_config, 65536, "GATE_INVALID"), "GATE_INVALID")
    required = {
        "schema_version", "context", "bridge_config", "session_directory", "cwd", "provider",
        "model", "budget", "prior_session", "prior_session_id", "prior_cwd", "final_lock_path",
        "gate_outcome_directory", "expected_rows",
    }
    if (
        set(gate) != required
        or gate["schema_version"] != "argo-house-price-a2-phase-gate-deployment/v1"
        or gate["context"] != "initial"
        or gate["provider"] != "openai-codex"
        or gate["model"] != "gpt-5.6-sol"
        or gate["budget"] != 120000
        or gate["expected_rows"] != 292
        or any(gate[key] is not None for key in ("prior_session", "prior_session_id", "prior_cwd"))
    ):
        raise _Reject("GATE_INVALID")
    try:
        session_directory = _gate_directory(gate["session_directory"])
        if (
            session_directory.path != Path(synthetic.session_dir)
            or (session_directory.device, session_directory.inode) != (
                synthetic.session_dir_identity.device, synthetic.session_dir_identity.inode,
            )
        ):
            raise _Reject("GATE_INVALID")
        bridge_path, bridge_bytes = _gate_file_binding(gate["bridge_config"], 65536)
    except Exception:
        raise _Reject("GATE_INVALID") from None
    bridge = _json(bridge_bytes, "GATE_INVALID")
    rights = bridge.get("context_rights")
    if (
        type(rights) is not dict
        or rights.get("context") != "initial"
        or rights.get("initial_context_id") != expectation.controller_context_id
        or rights.get("controller_context_id") != expectation.controller_context_id
    ):
        raise _Reject("GATE_INVALID")
    return gate, session_directory, bridge_path


def _research(expectation: CombinationExpectation) -> dict[str, object]:
    source_root = Path(expectation.state_trees[0].root)
    path = source_root / "research.md"
    try:
        info = path.lstat()
        data = _gate_read(path, 131072, expectation.research_sha256, info.st_size, info.st_mtime_ns)
        text = data.decode("utf-8")
    except Exception:
        raise _Reject("SOURCE_MISMATCH") from None
    if not text.strip() or "\0" in text:
        raise _Reject("SOURCE_MISMATCH")
    return {"ok": True, "result": {
        "path": "research.md", "content": text, "sha256": expectation.research_sha256,
    }}


def _gate(
    expectation: CombinationExpectation,
    gate: Mapping[str, object],
    session_directory: object,
    usage: SessionUsage,
    public: dict[str, object],
    research: dict[str, object],
) -> FileBinding:
    observer = UsageObserverConfig(
        session_directory,
        gate["cwd"], gate["provider"], gate["model"], 120000, (),
    )
    try:
        outcome_directory = _gate_directory(gate["gate_outcome_directory"])
        latest_binding, latest, checkpoint = _latest_gate(
            outcome_directory, expectation.gate_config.sha256, observer,
        )
    except Exception:
        raise _Reject("GATE_INVALID") from None
    expected_usage = UsageObservation(
        "WITHIN_BUDGET", None, True, usage.total_tokens, usage.total_tokens,
        usage.session_id, expectation.current_session.sha256, expectation.current_session.bytes,
    )
    expected_decision = {
        "outcome": "READY_INITIAL_CHECKPOINT",
        "ready": True,
        "stop": True,
        "verified_dev_run_ids": list(expectation.verified_dev_run_ids),
        "selected_final_run_id": None,
    }
    if (
        type(latest) is not dict
        or latest.get("schema_version") != "argo-house-price-a2-phase-gate-outcome/v2"
        or latest.get("context") != "initial"
        or latest.get("config_sha256") != expectation.gate_config.sha256
        or latest.get("bridge_config_sha256") != gate["bridge_config"]["sha256"]
        or latest.get("decision") != expected_decision
        or latest.get("usage") != asdict(expected_usage)
        or type(checkpoint) is not dict
        or checkpoint.get("observation") != asdict(expected_usage)
        or latest.get("final_lock_sha256") is not None
        or type(latest.get("sequence")) is not int
        or latest["sequence"] < 1
        or type(latest.get("view_sha256")) is not dict
        or set(latest["view_sha256"]) != {"public", "dev", "research"}
        or latest["view_sha256"]["public"] != hashlib.sha256(_canonical({"ok": True, "result": public})).hexdigest()
        or latest["view_sha256"]["research"] != hashlib.sha256(_canonical(research)).hexdigest()
        or HEX64.fullmatch(latest["view_sha256"]["dev"]) is None
    ):
        raise _Reject("GATE_INVALID")
    return latest_binding


def _metadata(expectation: CombinationExpectation, synthetic: RunControllerConfig) -> None:
    if (
        expectation.metadata.path != Path(synthetic.artifact_root) / METADATA_NAME
        or expectation.metadata.path.name != METADATA_NAME
    ):
        raise _Reject("METADATA_INVALID")
    try:
        info = expectation.metadata.path.lstat()
    except OSError:
        raise _Reject("METADATA_INVALID") from None
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
        raise _Reject("METADATA_INVALID")
    value = _json(_read(expectation.metadata, 4096, "METADATA_INVALID"), "METADATA_INVALID")
    expected = {
        "schema_version": "argo-house-price-a2-synthetic-provider-metadata/v1",
        "test_only": True,
        "provider": "openai-codex",
        "model": "gpt-5.6-sol",
        "response_ids": list(RESPONSE_IDS),
        "provider_call_count": 2,
        "contexts_observed": 2,
        "tool_names": list(TOOLS),
        "tool_schema_sha256": EXPECTED_TOOL_SCHEMA_SHA256,
        "final_text_sha256": hashlib.sha256(FINAL_TEXT.encode("utf-8")).hexdigest(),
        "usage_authority": "NATIVE_SESSION_ONLY",
        "production_provider_factory": False,
    }
    if value != expected:
        raise _Reject("METADATA_INVALID")


def _bounded_output(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > 1048576:
                raise _Reject("PROCESS_INVALID")
            data = stream.read(1048577)
            after = os.fstat(stream.fileno())
        named = path.lstat()
    except _Reject:
        raise
    except Exception:
        raise _Reject("PROCESS_INVALID") from None
    if (
        len(data) != before.st_size
        or _identity(before) != _identity(after)
        or _identity(after) != _identity(named)
    ):
        raise _Reject("PROCESS_INVALID")


def _process(
    expectation: CombinationExpectation,
    synthetic: RunControllerConfig,
) -> None:
    receipt = _json(_read(expectation.process_receipt, 1048576, "PROCESS_INVALID"), "PROCESS_INVALID")
    if (
        type(receipt.get("returncode")) is not int
        or receipt["returncode"] != 0
        or not _valid_prior_process_receipt(receipt, expectation.current_session.path)
    ):
        raise _Reject("PROCESS_INVALID")
    try:
        _verify_process_receipt(receipt, synthetic)
    except Exception:
        raise _Reject("PROCESS_INVALID") from None
    elapsed = receipt.get("elapsed_seconds")
    resources = receipt.get("resources")
    cleanup = receipt.get("cleanup")
    if (
        isinstance(elapsed, bool)
        or not isinstance(elapsed, (int, float))
        or not math.isfinite(float(elapsed))
        or not 0 <= elapsed < expectation.elapsed_limit_seconds
        or type(resources) is not dict
        or type(cleanup) is not dict
        or resources.get("rss_overshoot_bytes") != 0
        or resources.get("file_count_overshoot") != 0
        or resources.get("aggregate_bytes_overshoot") != 0
        or resources.get("observer_errors") != []
        or resources.get("census_errors") != []
        or cleanup.get("signals_sent") != []
    ):
        raise _Reject("PROCESS_INVALID")
    handle = receipt["handle"]
    _bounded_output(Path(handle["stdout_path"]))
    _bounded_output(Path(handle["stderr_path"]))


def _artifact_census(synthetic: RunControllerConfig) -> None:
    root = Path(synthetic.artifact_root)
    expected = synthetic.artifact_root_identity
    root_descriptor: int | None = None
    pending: list[int] = []
    try:
        root_descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        held_root = os.fstat(root_descriptor)
        named_root = root.lstat()
        for opened in (held_root, named_root):
            if (
                not stat.S_ISDIR(opened.st_mode)
                or stat.S_IMODE(opened.st_mode) != 0o700
                or opened.st_uid != os.getuid()
                or (opened.st_dev, opened.st_ino) != (expected.device, expected.inode)
            ):
                raise _Reject("OUTPUT_LIMIT")
        pending.append(os.dup(root_descriptor))
        files = 0
        directories = 0
        total = 0
        while pending:
            current = pending.pop()
            try:
                directories += 1
                if directories > 128:
                    raise _Reject("OUTPUT_LIMIT")
                with os.scandir(current) as entries:
                    for entry in entries:
                        info = entry.stat(follow_symlinks=False)
                        if stat.S_ISDIR(info.st_mode):
                            child = os.open(
                                entry.name,
                                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=current,
                            )
                            if _identity(os.fstat(child)) != _identity(info):
                                os.close(child)
                                raise _Reject("OUTPUT_LIMIT")
                            pending.append(child)
                        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                            files += 1
                            total += info.st_size
                            if files > 128 or total > 1048576:
                                raise _Reject("OUTPUT_LIMIT")
                        else:
                            raise _Reject("OUTPUT_LIMIT")
            finally:
                os.close(current)
        held_after = os.fstat(root_descriptor)
        named_after = root.lstat()
        if (
            (held_after.st_dev, held_after.st_ino) != (expected.device, expected.inode)
            or (named_after.st_dev, named_after.st_ino) != (expected.device, expected.inode)
        ):
            raise _Reject("OUTPUT_LIMIT")
    except _Reject:
        raise
    except Exception:
        raise _Reject("OUTPUT_LIMIT") from None
    finally:
        for descriptor in pending:
            os.close(descriptor)
        if root_descriptor is not None:
            os.close(root_descriptor)


def assess_combination(expectation: CombinationExpectation) -> CombinationAssessment:
    campaign_tokens: int | None = None
    session_sha256: str | None = None
    native_gate_sha256: str | None = None
    stage = "CONFIG_INVALID"
    try:
        trees = _validate_expectation(expectation)
        normal, synthetic = _load_configs(expectation)
        stage = "SOURCE_MISMATCH"
        _verify_trees(expectation, trees, synthetic)
        stage = "CONFIG_INVALID"
        task_prompt = _task_prompt(expectation, normal, synthetic)
        stage = "GATE_INVALID"
        gate, session_directory, _bridge_path = _load_gate(expectation, synthetic)
        stage = "USAGE_UNKNOWN"
        usage, session = _usage(expectation, synthetic, gate)
        campaign_tokens = usage.total_tokens
        session_sha256 = expectation.current_session.sha256
        stage = "TOOL_TRANSCRIPT_INVALID"
        public = _transcript(session, expectation.verified_dev_run_ids, task_prompt)
        stage = "PROCESS_INVALID"
        _process(expectation, synthetic)
        stage = "SOURCE_MISMATCH"
        research = _research(expectation)
        stage = "GATE_INVALID"
        latest = _gate(expectation, gate, session_directory, usage, public, research)
        native_gate_sha256 = latest.sha256
        stage = "METADATA_INVALID"
        _metadata(expectation, synthetic)
        stage = "OUTPUT_LIMIT"
        _artifact_census(synthetic)
        return CombinationAssessment(
            "PASS", "VERIFIED_SYNTHETIC_COMBINATION",
            campaign_tokens, session_sha256, native_gate_sha256,
        )
    except _Reject as error:
        return CombinationAssessment(
            "NOT_ADMITTED", error.reason,
            campaign_tokens, session_sha256, native_gate_sha256,
        )
    except Exception:
        return CombinationAssessment(
            "NOT_ADMITTED", stage if stage in REASONS else "CONFIG_INVALID",
            campaign_tokens, session_sha256, native_gate_sha256,
        )
