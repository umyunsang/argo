"""Read-only terminal/result conjunction for one synthetic A2 combination.

The root supplies OS wait/capture facts. This module never launches, retries,
cleans up, grades, or promotes a scientific run.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance import (
    CombinationAssessment, CombinationExpectation, assess_combination,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import _gate_json
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import (
    ClosureLimits, SourceTree, verify_tree,
)

CASE_SCHEMA = "argo-house-price-a2-synthetic-combination-case/v3"
CONFIG_SCHEMA = "argo-house-price-a2-combination-case-config/v2"
EXPECTATION_SCHEMA = "argo-house-price-a2-combination-expectation/v1"
SUCCESS = "VERIFIED_SYNTHETIC_COMBINATION"
EXPECTED_LIMITATIONS = (
    "Synthetic integration only; production main entry, fixed factory list and OAuth transport were not executed.",
    "Fake ORX/runner receipts are fabricated; no real model fit, task data or hidden score is observed.",
    "RSS/current-response usage and whole-case stage budgets are monitored, not hard aggregate limits.",
    "Source and cleanup proof use a root-private no-concurrent-same-UID-mutator TCB, not hostile-host isolation.",
)
HEX64 = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
TREE_LIMITS = ClosureLimits(160, 8388608, 1048576, 8, 4096)
PRIME_LIMITS = ClosureLimits(30000, 268435456, 67108864, 32, 4096)
FILE_CAPS = {
    "normal_process_config": 65536, "synthetic_process_config": 65536,
    "process_receipt": 1048576, "gate_config": 65536, "metadata": 4096,
    "current_session": 8388608, "synthetic_frontend": 1048576,
}
RESULT_KEYS = {"status", "stage", "reason", "receipt", "process_attempts", "controller_context_id"}
CASE_KEYS = {
    "schema_version", "case_id", "synthetic_only", "production_entry_executed", "actual_P0",
    "status", "stage", "reason", "context_id", "process_attempts", "source_bindings",
    "case_admission", "expectation", "latest_gate", "normal_process_config",
    "synthetic_process_config", "process_receipt", "gate_config", "metadata", "current_session",
    "current_session_id", "assessment", "elapsed_seconds", "cleanup_confirmed",
    "fixture_close_result", "limitations",
}
CONFIG_KEYS = {
    "schema_version", "case_root", "namespace_tree", "frontend_seed_tree", "installed_prime_tree",
    "expected_faux_frontend_sha256", "expected_fixture_module_sha256",
    "expected_acceptance_module_sha256", "protected_roots",
}


@dataclass(frozen=True)
class CombinationReadback:
    status: str
    reason: str
    case_receipt: FileBinding | None
    assessment: CombinationAssessment | None


class _Invalid(ValueError):
    pass


class _Unavailable(ValueError):
    pass


class _TerminalIncomplete(ValueError):
    pass


def _object(value: object, keys: set[str]) -> dict:
    if type(value) is not dict or set(value) != keys:
        raise _Invalid()
    return value


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def _hash(value: object) -> str:
    if type(value) is not str or HEX64.fullmatch(value) is None:
        raise _Invalid()
    return value


def _path(value: object) -> Path:
    if type(value) is not str:
        raise _Invalid()
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts or str(path) != value or len(value.encode()) > 4096:
        raise _Invalid()
    return path


def _integer(value: object, lower: int, upper: int) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise _Invalid()
    return value


def _binding(value: object, cap: int) -> FileBinding:
    row = _object(value, {"path", "sha256", "bytes", "mtime_ns_max"})
    return FileBinding(_path(row["path"]), _hash(row["sha256"]),
                       _integer(row["bytes"], 1, cap), _integer(row["mtime_ns_max"], 0, 2**63-1))


def _read(binding: FileBinding, cap: int, *, empty: bool = False) -> bytes:
    if type(binding) is not FileBinding or not isinstance(binding.path, Path):
        raise _Invalid()
    _path(str(binding.path)); _hash(binding.sha256)
    _integer(binding.bytes, 0 if empty else 1, cap)
    _integer(binding.mtime_ns_max, 0, 2**63-1)
    descriptors = []
    try:
        parent = os.open(binding.path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(parent)
        for part in binding.path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(parent)
        fd = os.open(binding.path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        descriptors.append(fd)
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != binding.bytes
                or before.st_mtime_ns > binding.mtime_ns_max):
            raise _Invalid()
        chunks = []
        remaining = binding.bytes
        while remaining:
            chunk = os.read(fd, min(65536, remaining))
            if not chunk:
                raise _Invalid()
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise _Invalid()
        data = b"".join(chunks)
        after = os.fstat(fd)
        named = os.stat(binding.path.name, dir_fd=parent, follow_symlinks=False)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if (identity(before) != identity(after) or identity(after) != identity(named)
                or hashlib.sha256(data).hexdigest() != binding.sha256):
            raise _Invalid()
        return data
    except OSError as error:
        if error.errno in (errno.ENOENT, errno.EACCES, errno.EPERM, errno.EIO, errno.ESTALE):
            raise _Unavailable() from None
        raise _Invalid() from None
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def _capture(binding: FileBinding, cap: int, *, empty: bool = False) -> bytes:
    try:
        return _read(binding, cap, empty=empty)
    except _Unavailable:
        raise _TerminalIncomplete() from None


def _tree(value: object) -> SourceTree:
    row = _object(value, {field.name for field in fields(SourceTree)})
    _path(row["root"]); _hash(row["tree_sha256"])
    _integer(row["root_device"], 0, 2**64-1); _integer(row["root_inode"], 1, 2**64-1)
    _integer(row["maximum_mtime_ns"], 0, 2**63-1)
    for name in ("file_count", "directory_count", "symlink_count"):
        _integer(row[name], 0, 30000)
    _integer(row["total_file_bytes"], 0, 268435456)
    return SourceTree(**row)


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _protected(config: dict, case: Path) -> None:
    roots = _object(config["protected_roots"], {"raw", "auth", "profile", "controller", "public"})
    descriptors = []
    try:
        for value in roots.values():
            row = _object(value, {"path", "device", "inode"})
            path = _path(row["path"])
            dev = _integer(row["device"], 0, 2**64-1)
            ino = _integer(row["inode"], 1, 2**64-1)
            if _overlaps(case, path) or path.resolve(strict=True) != path:
                raise _Invalid()
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(fd)
            for info in (os.fstat(fd), path.lstat()):
                if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or (info.st_dev, info.st_ino) != (dev, ino):
                    raise _Invalid()
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def _config(data: bytes) -> dict:
    row = _object(_gate_json(data), CONFIG_KEYS)
    if row["schema_version"] != CONFIG_SCHEMA:
        raise _Invalid()
    case = _path(row["case_root"])
    for name in ("expected_faux_frontend_sha256", "expected_fixture_module_sha256", "expected_acceptance_module_sha256"):
        _hash(row[name])
    trees = [_tree(row[name]) for name in ("namespace_tree", "frontend_seed_tree", "installed_prime_tree")]
    roots = [Path(tree.root) for tree in trees]
    if any(_overlaps(case, root) for root in roots):
        raise _Invalid()
    for index, left in enumerate(roots):
        if any(_overlaps(left, right) for right in roots[index+1:]):
            raise _Invalid()
    _protected(row, case)
    for tree, limit in zip(trees, (TREE_LIMITS, TREE_LIMITS, PRIME_LIMITS)):
        verify_tree(Path(tree.root), tree, limit)
    return row


def _expectation(value: object) -> CombinationExpectation:
    row = dict(_object(value, {field.name for field in fields(CombinationExpectation)} | {"schema_version"}))
    if row.pop("schema_version") != EXPECTATION_SCHEMA:
        raise _Invalid()
    for name, cap in FILE_CAPS.items():
        row[name] = _binding(row[name], cap)
    for name in ("namespace_tree", "frontend_tree", "installed_prime_tree"):
        row[name] = _tree(row[name])
    if type(row["state_trees"]) is not list or len(row["state_trees"]) != 3:
        raise _Invalid()
    row["state_trees"] = tuple(_tree(tree) for tree in row["state_trees"])
    ids = row["verified_dev_run_ids"]
    if (type(ids) is not list or len(ids) != 2 or any(type(i) is not str or UUID.fullmatch(i) is None for i in ids)
            or ids != sorted(set(ids))):
        raise _Invalid()
    row["verified_dev_run_ids"] = tuple(ids)
    _hash(row["controller_context_id"]); _hash(row["research_sha256"])
    if type(row["current_session_id"]) is not str or UUID.fullmatch(row["current_session_id"]) is None:
        raise _Invalid()
    if type(row["elapsed_limit_seconds"]) is not int or row["elapsed_limit_seconds"] != 20:
        raise _Invalid()
    return CombinationExpectation(**row)


def _assessment(value: object, gate: FileBinding) -> CombinationAssessment:
    row = dict(_object(value, {field.name for field in fields(CombinationAssessment)}))
    if row["status"] != "PASS" or row["reason"] != SUCCESS:
        raise _Invalid()
    _integer(row["campaign_tokens"], 1, 119999)
    _hash(row["session_sha256"]); _hash(row["native_gate_sha256"])
    row["native_gate_binding"] = _binding(row["native_gate_binding"], 16384)
    if row["native_gate_binding"] != gate or row["native_gate_sha256"] != gate.sha256:
        raise _Invalid()
    return CombinationAssessment(**row)


def _cleanup(value: object) -> None:
    row = _object(value, {"schema_version", "confirmed", "shutdown_completed", "serve_thread_stopped", "socket_closed",
                          "cleanup_thread_stopped", "timed_out", "error", "elapsed_seconds"})
    if (row["schema_version"] != "argo-house-price-a2-fixture-close/v1"
            or any(row[name] is not True for name in ("confirmed", "shutdown_completed", "serve_thread_stopped", "socket_closed", "cleanup_thread_stopped"))
            or row["timed_out"] is not False or row["error"] is not None
            or type(row["elapsed_seconds"]) is not float or not math.isfinite(row["elapsed_seconds"])
            or not 0 <= row["elapsed_seconds"] <= 2):
        raise _Invalid()


def _layout(expectation: CombinationExpectation, config: dict, case: Path) -> None:
    expected_paths = {
        "normal_process_config": case/"control/normal-process-config.json",
        "synthetic_process_config": case/"control/synthetic-process-config.json",
        "process_receipt": case/"evidence/controller-process-receipt.json",
        "gate_config": case/"frontend/gate-config.json",
        "metadata": case/"artifacts/a2-synthetic-provider-metadata.json",
        "current_session": case/"artifacts/session"/(expectation.current_session_id+".jsonl"),
        "synthetic_frontend": case/"frontend/a2-frontend-probes/a2-combination-frontend.ts",
    }
    if any(getattr(expectation, name).path != path for name, path in expected_paths.items()):
        raise _Invalid()
    if (expectation.namespace_tree != _tree(config["namespace_tree"])
            or expectation.installed_prime_tree != _tree(config["installed_prime_tree"])
            or expectation.synthetic_frontend.sha256 != config["expected_faux_frontend_sha256"]
            or Path(expectation.frontend_tree.root) != case/"frontend"
            or [Path(tree.root) for tree in expectation.state_trees] != [case/"fixture"/name for name in ("source", "trusted-state", "bridge-state")]):
        raise _Invalid()


def readback_combination(case_config: FileBinding, *, returncode: int | None,
                         stdout: FileBinding, stderr: FileBinding,
                         terminal_complete: bool) -> CombinationReadback:
    if terminal_complete is not True or returncode is None:
        return CombinationReadback("UNKNOWN", "TERMINAL_INCOMPLETE", None, None)
    if type(returncode) is not int or returncode != 0:
        return CombinationReadback("NOT_ADMITTED", "TERMINAL_REJECTED", None, None)
    reason = "TERMINAL_INVALID"
    receipt_binding = None
    case_fd = None
    try:
        terminal = _capture(stdout, 65536)
        _capture(stderr, 1048576, empty=True)
        result = _object(_gate_json(terminal), RESULT_KEYS)
        if (terminal != _canonical(result)+b"\n" or result["status"] != SUCCESS
                or result["stage"] != "COMPLETE" or result["reason"] != "VERIFIED"
                or type(result["process_attempts"]) is not int or result["process_attempts"] != 1):
            raise _Invalid()
        _hash(result["controller_context_id"])
        receipt_binding = _binding(result["receipt"], 65536)
        reason = "CONFIG_INVALID"
        config = _config(_read(case_config, 65536))
        case = _path(config["case_root"])
        if receipt_binding.path != case/"evidence/case-receipt.json" or any(case == item.path or case in item.path.parents for item in (case_config, stdout, stderr)):
            raise _Invalid()
        case_fd = os.open(case, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        case_info = os.fstat(case_fd)
        if not stat.S_ISDIR(case_info.st_mode) or case_info.st_uid != os.getuid() or stat.S_IMODE(case_info.st_mode) != 0o700:
            raise _Invalid()
        reason = "RECEIPT_INVALID"
        payload = _object(_gate_json(_read(receipt_binding, 65536)), CASE_KEYS)
        if (payload["schema_version"] != CASE_SCHEMA or payload["case_id"] != "A2-Faux-C1"
                or payload["synthetic_only"] is not True or payload["production_entry_executed"] is not False
                or payload["actual_P0"] is not False or payload["cleanup_confirmed"] is not True
                or (payload["status"], payload["stage"], payload["reason"]) != (SUCCESS, "COMPLETE", "VERIFIED")
                or type(payload["process_attempts"]) is not int or payload["process_attempts"] != 1
                or payload["context_id"] != result["controller_context_id"]
                or type(payload["elapsed_seconds"]) not in (int, float) or not math.isfinite(payload["elapsed_seconds"])
                or not 0 <= payload["elapsed_seconds"] < 180
                or _canonical(payload["source_bindings"]) != _canonical(config)
                or type(payload["limitations"]) is not list
                or payload["limitations"] != list(EXPECTED_LIMITATIONS)):
            raise _Invalid()
        _cleanup(payload["fixture_close_result"])
        expectation = _expectation(payload["expectation"])
        _layout(expectation, config, case)
        if (expectation.controller_context_id != result["controller_context_id"]
                or expectation.current_session_id != payload["current_session_id"]):
            raise _Invalid()
        for name in FILE_CAPS:
            if name in payload and _binding(payload[name], FILE_CAPS[name]) != getattr(expectation, name):
                raise _Invalid()
        admission = _binding(payload["case_admission"], 65536)
        latest = _binding(payload["latest_gate"], 16384)
        if (admission.path != case/"case-admission.json" or latest.path.parent != case/"gate-outcomes"
                or re.fullmatch(r"[0-9]{4}-[0-9a-f]{32}\.json", latest.path.name) is None):
            raise _Invalid()
        observed_admission = _object(_gate_json(_read(admission, 65536)), {"schema_version", "case_id", "synthetic_only", "actual_P0", "config"})
        expected_admission = {"schema_version":"argo-house-price-a2-synthetic-case-admission/v1", "case_id":"A2-Faux-C1", "synthetic_only":True, "actual_P0":False, "config":config}
        if _canonical(observed_admission) != _canonical(expected_admission):
            raise _Invalid()
        recorded = _assessment(payload["assessment"], latest)
        if recorded.session_sha256 != expectation.current_session.sha256:
            raise _Invalid()
        refs = [(case_config,65536,False), (stdout,65536,False), (stderr,1048576,True),
                (receipt_binding,65536,False), (admission,65536,False), (latest,16384,False)]
        refs += [(getattr(expectation,name),cap,False) for name,cap in FILE_CAPS.items()]
        gate_config = _gate_json(_read(expectation.gate_config,65536))
        bridge = _binding(gate_config["bridge_config"],65536)
        if bridge.path != case/"fixture/bridge-config.json":
            raise _Invalid()
        refs.append((bridge,65536,False))
        reason = "REFERENCE_MISMATCH"
        for binding, cap, empty in refs:
            if binding is stdout or binding is stderr:
                _capture(binding,cap,empty=empty)
            else:
                _read(binding,cap,empty=empty)
        reason = "ASSESSMENT_REJECTED"
        assessment = assess_combination(expectation)
        if type(assessment) is not CombinationAssessment or assessment != recorded:
            raise _Invalid()
        reason = "REFERENCE_MISMATCH"
        for binding, cap, empty in refs:
            if binding is stdout or binding is stderr:
                _capture(binding,cap,empty=empty)
            else:
                _read(binding,cap,empty=empty)
        _protected(config,case)
        for current in (os.fstat(case_fd),case.lstat()):
            if (not stat.S_ISDIR(current.st_mode) or current.st_uid != os.getuid()
                    or stat.S_IMODE(current.st_mode) != 0o700
                    or (current.st_dev,current.st_ino) != (case_info.st_dev,case_info.st_ino)):
                raise _Invalid()
        return CombinationReadback("PASS",SUCCESS,receipt_binding,assessment)
    except _TerminalIncomplete:
        return CombinationReadback("UNKNOWN","TERMINAL_INCOMPLETE",None,None)
    except Exception:
        return CombinationReadback("NOT_ADMITTED",reason,None,None)
    finally:
        if case_fd is not None:
            os.close(case_fd)
