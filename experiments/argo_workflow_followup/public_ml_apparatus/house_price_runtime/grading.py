"""Trusted bounded grading I/O. This module grants no launch or hidden-reveal authority."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_scorer import (
    ArtifactInvalidError,
    ScorerContractError,
    ScorerLimits,
    score_prediction_csv,
)

MAX_ARTIFACT_BYTES = 1_048_576
MAX_REFERENCE_BYTES = 262_144
MAX_ROWS = 292
MAX_DEV_MAE = 10**12
SCORER_LIMITS = ScorerLimits(MAX_ARTIFACT_BYTES, MAX_ROWS, 128, 32, 32)


class GradingError(ValueError):
    """Safe enum text only, never a parser or filesystem exception payload."""


@dataclass(frozen=True)
class FileBinding:
    path: Path
    sha256: str
    bytes: int
    mtime_ns_max: int


@dataclass(frozen=True)
class GradedArtifact:
    mae: Fraction
    row_count: int
    predictions_sha256: str
    ids_sha256: str
    targets_sha256: str

    def public_metric(self) -> dict[str, str | int]:
        return {"mae": format_dev_mae(self.mae), "rows": self.row_count}


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read_bound(binding: FileBinding, max_bytes: int) -> bytes:
    if (not isinstance(binding, FileBinding) or not isinstance(binding.path, Path) or
            not binding.path.is_absolute() or ".." in binding.path.parts or
            not isinstance(binding.sha256, str) or
            re.fullmatch(r"[a-f0-9]{64}", binding.sha256) is None or
            type(binding.bytes) is not int or type(binding.mtime_ns_max) is not int or
            type(max_bytes) is not int or not 0 < binding.bytes <= max_bytes <= MAX_ARTIFACT_BYTES or
            binding.mtime_ns_max < 0):
        raise GradingError("FILE_CONTRACT")
    directories: list[int] = []
    try:
        parent_fd = os.open(binding.path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        directories.append(parent_fd)
        for part in binding.path.parts[1:-1]:
            parent_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            directories.append(parent_fd)
        fd = os.open(binding.path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or
                    before.st_size != binding.bytes or before.st_mtime_ns > binding.mtime_ns_max):
                raise GradingError("FILE_IDENTITY")
            data = stream.read(max_bytes+1)
            after = os.fstat(stream.fileno())
            current = os.stat(binding.path.name, dir_fd=parent_fd, follow_symlinks=False)
            if (_identity(before) != _identity(after) or _identity(after) != _identity(current) or
                    len(data) != binding.bytes or hashlib.sha256(data).hexdigest() != binding.sha256):
                raise GradingError("FILE_IDENTITY")
        return data
    except (OSError, ValueError):
        raise GradingError("FILE_IDENTITY") from None
    finally:
        for fd in reversed(directories):
            os.close(fd)


def _load_ids(data: bytes, max_rows: int) -> tuple[str, ...]:
    try:
        ids = json.loads(data)
    except (ValueError, UnicodeError):
        raise GradingError("REFERENCE_CONTRACT") from None
    if (not isinstance(ids, list) or not 0 < len(ids) <= max_rows or
            any(not isinstance(value, str) or re.fullmatch(r"[0-9]{1,32}", value) is None for value in ids) or
            len(set(ids)) != len(ids)):
        raise GradingError("REFERENCE_CONTRACT")
    return tuple(ids)


def _load_targets(data: bytes, ids: tuple[str, ...]) -> dict[str, Decimal]:
    try:
        reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True)
        if next(reader) != ["Id", "SalePrice"]:
            raise GradingError("REFERENCE_CONTRACT")
        result: dict[str, Decimal] = {}
        for index, row in enumerate(reader):
            if (index >= len(ids) or len(row) != 2 or row[0] != ids[index] or
                    re.fullmatch(r"[0-9]{1,16}(?:\.[0-9]{1,8})?", row[1]) is None):
                raise GradingError("REFERENCE_CONTRACT")
            value = Decimal(row[1])
            if not value.is_finite() or value <= 0:
                raise GradingError("REFERENCE_CONTRACT")
            result[row[0]] = value
        if len(result) != len(ids):
            raise GradingError("REFERENCE_CONTRACT")
        return result
    except (UnicodeError, csv.Error, StopIteration, InvalidOperation):
        raise GradingError("REFERENCE_CONTRACT") from None


def grade_files(predictions: FileBinding, ids: FileBinding, targets: FileBinding,
                *, max_rows: int) -> GradedArtifact:
    if type(max_rows) is not int or not 1 <= max_rows <= MAX_ROWS:
        raise GradingError("SCORER_CONTRACT")
    expected_ids = _load_ids(read_bound(ids, MAX_REFERENCE_BYTES), max_rows)
    references = _load_targets(read_bound(targets, MAX_REFERENCE_BYTES), expected_ids)
    data = read_bound(predictions, MAX_ARTIFACT_BYTES)
    try:
        result = score_prediction_csv(data, expected_ids, references, SCORER_LIMITS)
    except ArtifactInvalidError:
        raise GradingError("ARTIFACT_INVALID") from None
    except ScorerContractError:
        raise GradingError("SCORER_CONTRACT") from None
    return GradedArtifact(result.mae, result.row_count, predictions.sha256, ids.sha256, targets.sha256)


def format_dev_mae(value: Fraction) -> str:
    if not isinstance(value, Fraction) or not 0 <= value <= MAX_DEV_MAE:
        raise GradingError("PUBLIC_METRIC_RANGE")
    # Exact round-half-even to six decimal places, without Decimal context drift.
    scaled, remainder = divmod(value.numerator * 1_000_000, value.denominator)
    if 2*remainder > value.denominator or (2*remainder == value.denominator and scaled % 2):
        scaled += 1
    return f"{scaled // 1_000_000}.{scaled % 1_000_000:06d}"
