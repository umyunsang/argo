"""Static, local byte-binding fixture for one selected public-ML artifact.

This module is an instrument only.  It neither selects by score nor reads hidden
scores.  A lock is checked again against caller-supplied bytes or a local file
before a mock receipt can be bound.  ``LockRegistry`` is process-local and is
not a trusted enforcement service or a durable publication mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import os
from pathlib import Path
import re
from typing import Literal


_SCHEMA_VERSION = "argo-public-ml-artifact-lock/v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ArtifactLock:
    """The immutable byte and protocol bindings for exactly one artifact."""

    schema_version: str
    lock_id: str
    study_id: str
    protocol_id: str
    protocol_sha256: str
    artifact_identity: str
    artifact_sha256: str
    artifact_size_bytes: int
    source_kind: Literal["bytes", "file"]
    declared_root: str | None = None
    relative_path: str | None = None


@dataclass(frozen=True)
class MockScoreReceipt:
    """Synthetic score metadata; this fixture never obtains a real score."""

    receipt_id: str
    lock_id: str
    study_id: str
    protocol_id: str
    protocol_sha256: str
    artifact_identity: str
    artifact_sha256: str
    artifact_size_bytes: int
    score: float | int


@dataclass(frozen=True)
class BoundMockScore:
    """A mock receipt after the supplied artifact has been re-verified."""

    lock: ArtifactLock
    receipt: MockScoreReceipt


def lock_artifact_bytes(
    *,
    lock_id: str,
    study_id: str,
    protocol_id: str,
    protocol_sha256: str,
    artifact_identity: str,
    artifact_bytes: bytes,
) -> ArtifactLock:
    """Create a lock from explicit selected bytes and a frozen protocol hash."""
    metadata = _validate_metadata(
        lock_id, study_id, protocol_id, protocol_sha256, artifact_identity
    )
    data = _require_bytes(artifact_bytes)
    return ArtifactLock(
        schema_version=_SCHEMA_VERSION,
        lock_id=metadata[0],
        study_id=metadata[1],
        protocol_id=metadata[2],
        protocol_sha256=metadata[3],
        artifact_identity=metadata[4],
        artifact_sha256=_sha256(data),
        artifact_size_bytes=len(data),
        source_kind="bytes",
    )


def lock_artifact_file(
    *,
    lock_id: str,
    study_id: str,
    protocol_id: str,
    protocol_sha256: str,
    artifact_identity: str,
    artifact_path: str | Path,
    declared_root: str | Path,
) -> ArtifactLock:
    """Create a lock from one regular, non-symlink file bounded by a local root.

    The path checks are deliberate local hygiene, not a race-free filesystem
    sandbox.  Verification always reads the file bytes again.
    """
    metadata = _validate_metadata(
        lock_id, study_id, protocol_id, protocol_sha256, artifact_identity
    )
    root, relative_path, data = _read_bounded_file(artifact_path, declared_root)
    return ArtifactLock(
        schema_version=_SCHEMA_VERSION,
        lock_id=metadata[0],
        study_id=metadata[1],
        protocol_id=metadata[2],
        protocol_sha256=metadata[3],
        artifact_identity=metadata[4],
        artifact_sha256=_sha256(data),
        artifact_size_bytes=len(data),
        source_kind="file",
        declared_root=str(root),
        relative_path=relative_path,
    )


def verify_lock(
    lock: ArtifactLock,
    *,
    artifact_bytes: bytes | None = None,
    declared_root: str | Path | None = None,
) -> ArtifactLock:
    """Re-derive artifact bytes and check every lock binding.

    Byte locks require ``artifact_bytes``.  File locks require the exact declared
    root recorded by the lock.  A lock record alone is therefore never accepted
    as proof of an artifact.
    """
    _validate_lock_shape(lock)
    if lock.source_kind == "bytes":
        if declared_root is not None:
            raise ValueError("byte locks do not accept a declared root")
        data = _require_bytes(artifact_bytes)
    else:
        if artifact_bytes is not None:
            raise ValueError("file locks do not accept explicit artifact bytes")
        if declared_root is None:
            raise ValueError("file locks require their declared root")
        root = _prepare_root(declared_root)
        if str(root) != lock.declared_root:
            raise ValueError("declared root does not match the locked root")
        _, relative_path, data = _read_bounded_file(lock.relative_path, root)
        if relative_path != lock.relative_path:
            raise ValueError("artifact path does not match the locked path")
    if _sha256(data) != lock.artifact_sha256 or len(data) != lock.artifact_size_bytes:
        raise ValueError("artifact bytes do not match the lock")
    return lock


class LockRegistry:
    """Small process-local no-replace publication fixture for tests."""

    def __init__(self) -> None:
        self._published: dict[str, ArtifactLock] = {}

    def publish(
        self,
        lock: ArtifactLock,
        *,
        artifact_bytes: bytes | None = None,
        declared_root: str | Path | None = None,
    ) -> ArtifactLock:
        """Verify then publish once; any repeated lock ID is rejected."""
        verified = verify_lock(
            lock, artifact_bytes=artifact_bytes, declared_root=declared_root
        )
        if verified.lock_id in self._published:
            raise ValueError("lock ID is already published")
        self._published[verified.lock_id] = verified
        return verified


def bind_mock_score(
    lock: ArtifactLock,
    receipt: MockScoreReceipt,
    *,
    artifact_bytes: bytes | None = None,
    declared_root: str | Path | None = None,
) -> BoundMockScore:
    """Bind synthetic score metadata only after exact byte and field checks."""
    verified = verify_lock(
        lock, artifact_bytes=artifact_bytes, declared_root=declared_root
    )
    _validate_receipt_shape(receipt)
    expected = (
        verified.lock_id,
        verified.study_id,
        verified.protocol_id,
        verified.protocol_sha256,
        verified.artifact_identity,
        verified.artifact_sha256,
        verified.artifact_size_bytes,
    )
    observed = (
        receipt.lock_id,
        receipt.study_id,
        receipt.protocol_id,
        receipt.protocol_sha256,
        receipt.artifact_identity,
        receipt.artifact_sha256,
        receipt.artifact_size_bytes,
    )
    if observed != expected:
        raise ValueError("mock score receipt does not match the artifact lock")
    return BoundMockScore(lock=verified, receipt=receipt)


def _validate_metadata(
    lock_id: str,
    study_id: str,
    protocol_id: str,
    protocol_sha256: str,
    artifact_identity: str,
) -> tuple[str, str, str, str, str]:
    return (
        _require_text(lock_id, "lock ID"),
        _require_text(study_id, "study ID"),
        _require_text(protocol_id, "protocol ID"),
        _require_sha256(protocol_sha256, "protocol SHA-256"),
        _require_text(artifact_identity, "artifact identity"),
    )


def _validate_lock_shape(lock: ArtifactLock) -> None:
    if not isinstance(lock, ArtifactLock):
        raise ValueError("lock must be an ArtifactLock")
    if lock.schema_version != _SCHEMA_VERSION:
        raise ValueError("unsupported lock schema")
    _validate_metadata(
        lock.lock_id,
        lock.study_id,
        lock.protocol_id,
        lock.protocol_sha256,
        lock.artifact_identity,
    )
    _require_sha256(lock.artifact_sha256, "artifact SHA-256")
    if isinstance(lock.artifact_size_bytes, bool) or not isinstance(
        lock.artifact_size_bytes, int
    ) or lock.artifact_size_bytes < 0:
        raise ValueError("artifact size must be a non-negative integer")
    if lock.source_kind == "bytes":
        if lock.declared_root is not None or lock.relative_path is not None:
            raise ValueError("byte lock must not contain file metadata")
    elif lock.source_kind == "file":
        if not isinstance(lock.declared_root, str) or not os.path.isabs(lock.declared_root):
            raise ValueError("file lock must contain an absolute declared root")
        _validate_relative_path(lock.relative_path)
    else:
        raise ValueError("unknown artifact source kind")


def _validate_receipt_shape(receipt: MockScoreReceipt) -> None:
    if not isinstance(receipt, MockScoreReceipt):
        raise ValueError("receipt must be a MockScoreReceipt")
    _validate_metadata(
        receipt.lock_id,
        receipt.study_id,
        receipt.protocol_id,
        receipt.protocol_sha256,
        receipt.artifact_identity,
    )
    _require_text(receipt.receipt_id, "receipt ID")
    _require_sha256(receipt.artifact_sha256, "receipt artifact SHA-256")
    if isinstance(receipt.artifact_size_bytes, bool) or not isinstance(
        receipt.artifact_size_bytes, int
    ) or receipt.artifact_size_bytes < 0:
        raise ValueError("receipt artifact size must be a non-negative integer")
    if isinstance(receipt.score, bool) or not isinstance(receipt.score, (int, float)):
        raise ValueError("mock score must be a finite number")
    if not math.isfinite(receipt.score):
        raise ValueError("mock score must be a finite number")


def _read_bounded_file(
    artifact_path: str | Path | None, declared_root: str | Path
) -> tuple[Path, str, bytes]:
    root = _prepare_root(declared_root)
    if artifact_path is None:
        raise ValueError("artifact path is required")
    try:
        supplied = Path(artifact_path)
    except TypeError as error:
        raise ValueError("artifact path must be path-like") from error
    candidate = supplied if supplied.is_absolute() else root / supplied
    candidate = Path(os.path.abspath(os.fspath(candidate)))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact path is outside the declared root") from error
    relative_text = _validate_relative_path(relative.as_posix())
    checked = root
    for component in Path(relative_text).parts:
        checked = checked / component
        if checked.is_symlink():
            raise ValueError("artifact path must not traverse a symlink")
    if not checked.exists() or not checked.is_file():
        raise ValueError("artifact path must name an existing regular file")
    return root, relative_text, checked.read_bytes()


def _prepare_root(declared_root: str | Path) -> Path:
    try:
        root = Path(declared_root)
    except TypeError as error:
        raise ValueError("declared root must be path-like") from error
    if not root.is_absolute():
        raise ValueError("declared root must be absolute")
    root = Path(os.path.abspath(os.fspath(root)))
    if root.is_symlink() or not root.exists() or not root.is_dir():
        raise ValueError("declared root must be an existing non-symlink directory")
    return root


def _validate_relative_path(value: str | None) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("file lock must contain a relative artifact path")
    path = Path(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("artifact path must be a normalized relative path")
    return value


def _require_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a non-empty trimmed string")
    return value


def _require_sha256(value: str, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase SHA-256 hex digest")
    return value


def _require_bytes(value: bytes | None) -> bytes:
    if not isinstance(value, bytes):
        raise ValueError("explicit artifact bytes are required")
    return value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
