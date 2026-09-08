"""Root-only original OS terminal/result conjunction; never grades or launches.

The root supplies PID/wait/capture facts from the original handle. Bound launch
and terminal files preserve those facts; this reader does not establish their
OS origin against a dishonest root. An acceptance file alone never overrides a
non-PASS return or an incomplete root command. References stay in the trusted
process and are not returned as rows, labels, predictions, or residuals.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import final_assessment as assessment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.final_assessment import FinalAssessmentConfig
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding, read_bound
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import _gate_json


@dataclass(frozen=True)
class AssessmentReadback:
    status: str
    reason: str
    candidate: FileBinding | None
    acceptance: FileBinding | None


class _Unavailable(ValueError):
    pass


def accept_assessment(config: FinalAssessmentConfig, *, launch: FileBinding, terminal: FileBinding,
                      stdout: FileBinding, stderr: FileBinding, pid: int | None,
                      returncode: int | None, terminal_complete: bool) -> AssessmentReadback:
    if terminal_complete is not True or returncode is None:
        return _result("UNKNOWN", "TERMINAL_INCOMPLETE")
    if type(returncode) is not int or returncode != 0 or type(pid) is not int or pid <= 0:
        return _result("NOT_ADMITTED", "TERMINAL_REJECTED")
    descriptor: int | None = None
    try:
        assessment._validate(config)
        terminal_bytes = _capture(terminal, 65536)
        stdout_bytes = _capture(stdout, 65536)
        _capture(stderr, 1048576, empty=True)
        launch_bytes = _capture(launch, 65536)
        admitted = _object(_gate_json(launch_bytes), {"schema_version", "config", "stdout", "stderr"})
        if (admitted["schema_version"] != "argo-house-price-assessment-outer-admission/v1" or
                _canonical(admitted["config"]) != _canonical(asdict(config))):
            raise ValueError()
        waited = _object(_gate_json(terminal_bytes), {
            "schema_version", "launch", "pid", "returncode", "terminal_complete", "stdout", "stderr"})
        expected_wait = {"schema_version": "argo-house-price-assessment-outer-terminal/v1",
            "launch": assessment._binding(launch), "pid": pid, "returncode": 0,
            "terminal_complete": True, "stdout": assessment._binding(stdout), "stderr": assessment._binding(stderr)}
        if _canonical(waited) != _canonical(expected_wait):
            raise ValueError()
        if len({item.path for item in (launch, terminal, stdout, stderr)}) != 4:
            raise ValueError()
        for item in (launch, terminal, stdout, stderr):
            if assessment.completion._overlaps(config.output_directory.path, item.path):
                raise ValueError()
        _capture_identity(stdout, admitted["stdout"])
        _capture_identity(stderr, admitted["stderr"])
        returned = _object(_gate_json(stdout_bytes), {"disposition", "reason", "admission", "publication"})
        if (stdout_bytes != _canonical(returned)+b"\n" or
                returned["disposition"] != "CANDIDATE_READY" or returned["reason"] != "VERIFIED"):
            raise ValueError()
        admission = _binding(returned["admission"])
        candidate = _binding(returned["publication"])
        if (admission.path != config.output_directory.path / "assessment-admission.json" or
                candidate.path != config.output_directory.path / "hidden-assessment-candidate.json"):
            raise ValueError()
        verified = assessment._verify(config)
        admission_bytes = read_bound(admission, 65536)
        provenance = {"final_completion": assessment._binding(config.final_completion),
            "task_manifest": assessment._binding(config.task_manifest),
            "predictions": assessment._binding(verified.predictions),
            "hidden_ids": assessment._binding(config.hidden_ids),
            "hidden_targets": assessment._binding(config.hidden_targets)}
        expected_admission = {"schema_version": "argo-house-price-hidden-assessment-admission/v1",
                              **provenance, "attempt": 1}
        if admission_bytes != _canonical(expected_admission):
            raise ValueError()
        candidate_bytes = read_bound(candidate, 65536)
        value = _object(_gate_json(candidate_bytes), {
            "schema_version", "status", "admission", *provenance,
            "metric", "scope", "returned_to_evaluated_controller"})
        metric = _object(value["metric"], {"name", "numerator", "denominator", "rows"})
        if (metric["name"] != "original-unit MAE" or type(metric["rows"]) is not int or metric["rows"] != 292 or
                type(metric["numerator"]) is not str or type(metric["denominator"]) is not str or
                re.fullmatch(r"(?:0|[1-9][0-9]{0,255})", metric["numerator"]) is None or
                re.fullmatch(r"[1-9][0-9]{0,255}", metric["denominator"]) is None):
            raise ValueError()
        expected_candidate = {"schema_version": "argo-house-price-hidden-assessment/v1",
            "status": "CANDIDATE_UNACCEPTED", "admission": assessment._binding(admission),
            **provenance, "metric": metric,
            "scope": "one development programme; not comparative efficacy or Kaggle leaderboard",
            "returned_to_evaluated_controller": False}
        if candidate_bytes != _canonical(expected_candidate):
            raise ValueError()
        assessment._recheck(config, verified, admission)
        # Check the original captures again; no newly recaptured digest is an entitlement.
        for item, cap, empty in ((launch, 65536, False), (terminal, 65536, False),
                                  (stdout, 65536, False), (stderr, 1048576, True)):
            _capture(item, cap, empty=empty)
        _capture_identity(stdout, admitted["stdout"])
        _capture_identity(stderr, admitted["stderr"])
        read_bound(candidate, 65536)
        descriptor = assessment._open_directory(config.output_directory)
        names = set(os.listdir(descriptor))
        if "assessment-acceptance.json" in names:
            return _result("NOT_ADMITTED", "ALREADY_ASSESSED")
        if names != {"assessment-admission.json", "hidden-assessment-candidate.json"}:
            raise ValueError()
        payload = _canonical({"schema_version": "argo-house-price-assessment-acceptance/v1",
            "status": "ACCEPTED_BY_ORIGINAL_TERMINAL_CONJUNCTION", "candidate": assessment._binding(candidate),
            "launch": assessment._binding(launch), "terminal": assessment._binding(terminal),
            "stdout": assessment._binding(stdout), "stderr": assessment._binding(stderr),
            "final_completion": assessment._binding(config.final_completion),
            "not_standalone_without_PASS_return": True})
        acceptance = _publish(descriptor, config.output_directory.path, payload)
        for item, cap, empty in ((launch, 65536, False), (terminal, 65536, False),
                                  (stdout, 65536, False), (stderr, 1048576, True)):
            _capture(item, cap, empty=empty)
        _capture_identity(stdout, admitted["stdout"])
        _capture_identity(stderr, admitted["stderr"])
        assessment._recheck(config, verified, admission)
        read_bound(candidate, 65536)
        read_bound(acceptance, 65536)
        assessment.completion._assert_directory_fd(descriptor, config.output_directory)
        return AssessmentReadback("PASS", "VERIFIED", candidate, acceptance)
    except _Unavailable:
        return _result("UNKNOWN", "TERMINAL_INCOMPLETE")
    except FileExistsError:
        return _result("NOT_ADMITTED", "ALREADY_ASSESSED")
    except Exception:
        return _result("NOT_ADMITTED", "EVIDENCE_MISMATCH")
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _object(value: object, keys: set[str]) -> dict[str, object]:
    if type(value) is not dict or set(value) != keys:
        raise ValueError()
    return value


def _binding(value: object) -> FileBinding:
    row = _object(value, {"path", "sha256", "bytes", "mtime_ns_max"})
    if type(row["path"]) is not str:
        raise ValueError()
    result = FileBinding(Path(row["path"]), row["sha256"], row["bytes"], row["mtime_ns_max"])
    assessment.completion._validate_binding_shape(result, 65536)
    return result


def _capture_identity(binding: FileBinding, value: object) -> None:
    row = _object(value, {"path", "device", "inode"})
    info = binding.path.lstat()
    if (row["path"] != str(binding.path) or type(row["device"]) is not int or type(row["inode"]) is not int or
            (info.st_dev, info.st_ino) != (row["device"], row["inode"]) or
            not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
        raise ValueError()


def _capture(binding: FileBinding, cap: int, *, empty: bool = False) -> bytes:
    if (type(binding) is not FileBinding or not isinstance(binding.path, Path) or
            not binding.path.is_absolute() or ".." in binding.path.parts or
            type(binding.sha256) is not str or re.fullmatch(r"[a-f0-9]{64}", binding.sha256) is None or
            type(binding.bytes) is not int or not (0 if empty else 1) <= binding.bytes <= cap or
            type(binding.mtime_ns_max) is not int or not 0 <= binding.mtime_ns_max <= 2**63-1):
        raise ValueError()
    descriptors = []
    try:
        parent = os.open(binding.path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(parent)
        for part in binding.path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(parent)
        descriptor = os.open(binding.path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != binding.bytes or
                before.st_mtime_ns > binding.mtime_ns_max):
            raise ValueError()
        chunks = []
        remaining = binding.bytes
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                raise ValueError()
            chunks.append(chunk); remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError()
        data = b"".join(chunks)
        after = os.fstat(descriptor)
        named = os.stat(binding.path.name, dir_fd=parent, follow_symlinks=False)
        def identity(item):
            return (item.st_dev, item.st_ino, item.st_mode, item.st_nlink,
                    item.st_size, item.st_mtime_ns, item.st_ctime_ns)
        if (identity(before) != identity(after) or identity(after) != identity(named) or
                hashlib.sha256(data).hexdigest() != binding.sha256):
            raise ValueError()
        return data
    except OSError as error:
        if error.errno in {errno.ENOENT, errno.EACCES, errno.EPERM, errno.EIO, errno.ESTALE}:
            raise _Unavailable() from None
        raise ValueError() from None
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _publish(descriptor: int, root: Path, data: bytes) -> FileBinding:
    name = "assessment-acceptance.json"
    if not 0 < len(data) <= 65536:
        raise ValueError()
    output = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=descriptor)
    try:
        remaining = memoryview(data)
        while remaining:
            count = os.write(output, remaining)
            if count <= 0:
                raise OSError()
            remaining = remaining[count:]
        os.fsync(output)
        info = os.fstat(output)
    finally:
        os.close(output)
    os.fsync(descriptor)
    result = FileBinding(root / name, hashlib.sha256(data).hexdigest(), len(data), info.st_mtime_ns)
    read_bound(result, 65536)
    return result


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False, default=_json_path).encode("ascii")


def _json_path(value: object) -> str:
    if not isinstance(value, Path):
        raise ValueError()
    return str(value)


def _result(status: str, reason: str) -> AssessmentReadback:
    return AssessmentReadback(status, reason, None, None)
