"""Provenance and create-only evidence for development domain commands."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from threadpoolctl import threadpool_info

EventSink = Callable[[dict[str, object]], None]
PINNED_VERSIONS = {
    "numpy": "1.26.4", "scipy": "1.14.1", "scikit-learn": "1.6.1",
    "joblib": "1.4.2", "threadpoolctl": "3.6.0", "duckdb": "1.4.5", "pyamg": "5.3.0",
}


class DomainError(ValueError):
    """A domain contract or reproducibility requirement was not satisfied."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def write_new(path: Path, data: bytes, mode: int = 0o600) -> None:
    path = Path(path)
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise DomainError("output parent must be an existing nonsymlink directory")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def read_regular(path: Path, max_bytes: int = 16 * 1024 * 1024) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= max_bytes:
            raise DomainError("input is not a bounded regular file")
        data = stream.read(max_bytes + 1)
        after = os.fstat(stream.fileno())
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise DomainError("input changed during read")
    return data


def environment() -> dict[str, object]:
    installed: dict[str, str | None] = {}
    for package in PINNED_VERSIONS:
        try:
            installed[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed[package] = None
    return {
        "python": sys.version, "platform": platform.platform(),
        "machine": platform.machine(), "packages": installed,
        "matches_pins": installed == PINNED_VERSIONS,
        "thread_environment": {
            name: os.environ.get(name) for name in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "PYTHONHASHSEED",
            )
        },
        "threadpools": threadpool_info(),
    }


def code_identity() -> dict[str, str]:
    root = Path(__file__).parent
    paths = sorted(root.glob("*.py")) + [root / "requirements.txt"]
    return {path.name: file_digest(path) for path in paths}


def provenance(domain: str, seed: int) -> dict[str, object]:
    return {
        "schema_version": "project-research-domain-result/v1",
        "domain": domain, "created_at": now(), "seed": seed,
        "evidence_stage": "DEVELOPMENT_BASELINE_HYPOTHESIS",
        "development_only": True, "autonomous_campaign": False,
        "final_evaluation": False, "aaa_assessment": "NOT_PERFORMED",
        "pi_completion": "NOT_ASSESSED", "environment": environment(),
        "code_sha256": code_identity(), "command": [sys.executable, *sys.argv],
        "accounting": {"model_calls": 0, "paid_tool_calls": 0,
                       "local_computation_cost_krw": None,
                       "cost_note": "Wall/CPU usage recorded; no monetary price assigned to local compute."},
    }


def emit(sink: EventSink | None, event: str, **fields: object) -> None:
    if sink is not None:
        sink({"at": now(), "event": event, **fields})
