"""Root-only one-shot assessment; never a controller tool or native run lifecycle.

The root must collect the original outer terminal before calling this adapter.
It reopens the bound phase/ORX evidence but does not certify its own OS exit.
Final IDs are prior final-refit task inputs, not hidden labels. The durable
fence precedes hidden target reads and MAE, not trusted ID validation.
Only a trusted scorer process may call it with real references. Same-UID host
integrity and no malicious concurrent mutation remain explicit assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import phase_completion as completion
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.bridge import FixedNativePort, NativeObservation
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import RunControllerConfig
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import (
    FileBinding, grade_files, read_bound,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_completion import PhaseCompletionConfig
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity


@dataclass(frozen=True)
class FinalAssessmentConfig:
    phase: PhaseCompletionConfig
    final_completion: FileBinding
    task_manifest: FileBinding
    hidden_ids: FileBinding
    hidden_targets: FileBinding
    output_directory: DirectoryIdentity


@dataclass(frozen=True)
class FinalAssessmentResult:
    disposition: str
    reason: str
    admission: FileBinding | None
    publication: FileBinding | None


@dataclass(frozen=True)
class _Verified:
    completion_bytes: bytes
    task_bytes: bytes
    predictions: FileBinding


def assess_final(config: FinalAssessmentConfig) -> FinalAssessmentResult:
    try:
        _validate(config)
    except Exception:
        return _result("NOT_ADMITTED", "INVALID_INPUT")
    try:
        verified = _verify(config)
        descriptor = _open_directory(config.output_directory)
    except Exception:
        return _result("NOT_ADMITTED", "EVIDENCE_MISMATCH")
    admission: FileBinding | None = None
    try:
        if os.listdir(descriptor):
            return _result("NOT_ADMITTED", "ALREADY_ATTEMPTED")
        value = {
            "schema_version": "argo-house-price-hidden-assessment-admission/v1",
            "final_completion": _binding(config.final_completion),
            "task_manifest": _binding(config.task_manifest),
            "predictions": _binding(verified.predictions),
            "hidden_ids": _binding(config.hidden_ids),
            "hidden_targets": _binding(config.hidden_targets),
            "attempt": 1,
        }
        try:
            admission = _publish(descriptor, config.output_directory, "assessment-admission.json", _canonical(value))
        except FileExistsError:
            return _result("NOT_ADMITTED", "ALREADY_ATTEMPTED")
        graded = grade_files(verified.predictions, config.hidden_ids, config.hidden_targets, max_rows=292)
        if (type(graded.row_count) is not int or graded.row_count != 292 or
                not isinstance(graded.mae, Fraction) or graded.mae < 0 or
                graded.predictions_sha256 != verified.predictions.sha256 or
                graded.ids_sha256 != config.hidden_ids.sha256 or
                graded.targets_sha256 != config.hidden_targets.sha256):
            raise ValueError()
        _recheck(config, verified, admission)
        payload = _canonical({
            "schema_version": "argo-house-price-hidden-assessment/v1", "status": "CANDIDATE_UNACCEPTED",
            "admission": _binding(admission), **{key: item for key, item in value.items()
                if key not in {"schema_version", "attempt"}},
            "metric": {"name": "original-unit MAE", "numerator": str(graded.mae.numerator),
                       "denominator": str(graded.mae.denominator), "rows": graded.row_count},
            "scope": "one development programme; not comparative efficacy or Kaggle leaderboard",
            "returned_to_evaluated_controller": False,
        })
        publication = _publish(descriptor, config.output_directory, "hidden-assessment-candidate.json", payload)
        _recheck(config, verified, admission)
        read_bound(publication, 65536)
        return FinalAssessmentResult("CANDIDATE_READY", "VERIFIED", admission, publication)
    except Exception:
        return FinalAssessmentResult("UNKNOWN", "ASSESSMENT_INCOMPLETE", admission, None)
    finally:
        os.close(descriptor)


def _validate(config: FinalAssessmentConfig) -> None:
    if not isinstance(config, FinalAssessmentConfig):
        raise ValueError()
    completion._validate_input(config.phase)
    if (config.phase.context != "continuation" or
            config.final_completion.path != config.phase.completion_directory.path / "final-completion.json"):
        raise ValueError()
    for item, cap in ((config.final_completion, 65536), (config.task_manifest, 65536),
                      (config.hidden_ids, 262144), (config.hidden_targets, 262144)):
        completion._validate_binding_shape(item, cap)
    completion._validate_directory_shape(config.output_directory)


def _verify(config: FinalAssessmentConfig) -> _Verified:
    original = read_bound(config.final_completion, 65536)
    evidence = completion._verify(config.phase)
    expected, name = completion._publication_payload(config.phase, evidence)
    if name != "final-completion.json" or original != expected or evidence.final_lock is None:
        raise ValueError()
    lock = evidence.final_lock
    task_bytes = read_bound(config.task_manifest, 65536)
    task = completion._mapping(completion._gate_json(task_bytes))
    hidden = completion._mapping(completion._mapping(task.get("phase_input_files")).get("trusted_final_assessment"))
    counts = completion._mapping(task.get("counts"))
    if (config.task_manifest.sha256 != lock.task_sha256 or
            task.get("schema_version") != "argo-house-price-fixed-task/v1" or
            task.get("task_id") != "mlagentbench-house-price" or
            type(counts.get("hidden")) is not int or counts["hidden"] != 292 or
            set(hidden) != {"ids", "targets"}):
        raise ValueError()
    for key, item in (("ids", config.hidden_ids), ("targets", config.hidden_targets)):
        expected_file = completion._mapping(hidden[key])
        if (set(expected_file) != {"sha256", "bytes"} or
                type(expected_file.get("bytes")) is not int or
                expected_file != {"sha256": item.sha256, "bytes": item.bytes}):
            raise ValueError()

    bridge = completion.load_bridge_from_config(evidence.bridge_binding.path, evidence.bridge_binding.sha256)
    port = bridge.port
    if not isinstance(port, FixedNativePort):
        raise ValueError()
    if (config.output_directory.path != bridge.config.state_root.path.parent / "trusted-final-assessment" or
            port.config.final_inputs.get("ids") != config.hidden_ids or "targets" in port.config.final_inputs or
            type(port.config.final_rows) is not int or port.config.final_rows != 292):
        raise ValueError()
    process = RunControllerConfig.from_dict(completion._mapping(completion._gate_json(
        completion._read_binding(config.phase.process_config, 65536))))
    bridge_value = completion._mapping(completion._gate_json(read_bound(evidence.bridge_binding, 65536)))
    completion._verify_disjoint_roots(config.output_directory, process, evidence.gate,
                                      bridge_value, config.phase.current_session.path)
    for protected in (bridge.config.state_root.path, config.hidden_ids.path.parent,
                      config.hidden_targets.path.parent, config.final_completion.path.parent):
        if completion._overlaps(config.output_directory.path, protected):
            raise ValueError()
    _, bindings = bridge._state()
    finals = [item for item in bindings if item.phase == "final_refit"]
    if len(finals) != 1:
        raise ValueError()
    final = finals[0]
    for key, value in {
        "run_id": lock.run_id, "closure_sha256": lock.closure_sha256,
        "solution_sha256": lock.code_sha256, "execution_config_sha256": lock.execution_config_sha256,
        "task_sha256": lock.task_sha256, "environment_sha256": lock.environment_sha256,
        "protocol_sha256": lock.protocol_sha256,
    }.items():
        if getattr(final, key) != value:
            raise ValueError()
    observation = port.observe(final)
    if (not isinstance(observation, NativeObservation) or observation.status != "DONE" or
            observation.cancel_requested is not False or observation.run_id != final.run_id or
            observation.experiment_id != final.experiment_id or observation.native_commit != final.native_commit or
            observation.native_source_digest != final.native_source_digest):
        raise ValueError()
    predictions = port.final_artifact_binding(final, observation)
    if predictions.sha256 != lock.artifact_sha256:
        raise ValueError()
    read_bound(predictions, 1048576)
    if read_bound(config.final_completion, 65536) != original:
        raise ValueError()
    return _Verified(original, task_bytes, predictions)


def _recheck(config: FinalAssessmentConfig, original: _Verified, admission: FileBinding) -> None:
    if _verify(config) != original:
        raise ValueError()
    read_bound(original.predictions, 1048576)
    read_bound(config.hidden_ids, 262144)
    read_bound(config.hidden_targets, 262144)
    read_bound(admission, 65536)


def _open_directory(identity: DirectoryIdentity) -> int:
    descriptor = os.open(identity.path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in identity.path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        completion._assert_directory_fd(descriptor, identity)
        if os.fstat(descriptor).st_uid != os.geteuid():
            raise ValueError()
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _publish(descriptor: int, identity: DirectoryIdentity, name: str, data: bytes) -> FileBinding:
    if name not in {"assessment-admission.json", "hidden-assessment-candidate.json"} or not 0 < len(data) <= 65536:
        raise ValueError()
    check = _open_directory(identity)
    os.close(check)
    completion._assert_directory_fd(descriptor, identity)
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
        if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600 or
                info.st_nlink != 1 or info.st_size != len(data)):
            raise ValueError()
    finally:
        os.close(output)
    os.fsync(descriptor)
    binding = FileBinding(identity.path / name, hashlib.sha256(data).hexdigest(), len(data), info.st_mtime_ns)
    read_bound(binding, 65536)
    return binding


def _binding(item: FileBinding) -> dict[str, str | int]:
    return {"path": str(item.path), "sha256": item.sha256, "bytes": item.bytes, "mtime_ns_max": item.mtime_ns_max}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _result(disposition: str, reason: str) -> FinalAssessmentResult:
    return FinalAssessmentResult(disposition, reason, None, None)
