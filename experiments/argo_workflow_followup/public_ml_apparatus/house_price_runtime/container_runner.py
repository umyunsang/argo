"""Fixed Docker boundary for arbitrary HousePrice generated solution code.

This module is trusted infrastructure.  It only receives a pre-opened/trusted
``RunnerConfig`` from the fixed ORX bridge; it has no model-derived Docker
arguments, mounts, image name, or command.  It is not an ORX supervisor.
"""

from __future__ import annotations

import argparse
import csv
import io
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import signal
import subprocess
import threading
import time
from typing import BinaryIO, Sequence
import uuid


DOCKER_EXECUTABLE = "/opt/homebrew/bin/docker"
IMAGE_DIGEST = "sha256:cd43d0d8edac942bd67cd097caf08edd2def45016bf011c1635849f15ebc7835"
CONTAINER_UID_GID = "65532:65532"
_CONTAINER_PREFIX = "argo-hp-r1-"
_RUN_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    DOCKER_ERROR = "DOCKER_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    LOG_LIMIT_EXCEEDED = "LOG_LIMIT_EXCEEDED"
    CLEANUP_UNCONFIRMED = "CLEANUP_UNCONFIRMED"


@dataclass(frozen=True)
class RunnerConfig:
    """Trusted request constructed by the root-owned fixed ORX bridge only."""

    run_id: str
    solution_path: Path
    train_path: Path
    features_path: Path
    output_parent: Path
    wall_seconds: int
    cpus: float
    memory_bytes: int
    pids_limit: int
    nofile: int
    tmpfs_bytes: int
    max_input_bytes: int
    max_output_bytes: int
    log_quarantine_bytes: int

    @property
    def container_name(self) -> str:
        return f"{_CONTAINER_PREFIX}{self.run_id}"


@dataclass(frozen=True)
class RunResult:
    status: RunStatus
    run_id: str
    predictions_path: Path | None = None
    predictions_sha256: str | None = None
    row_count: int | None = None
    docker_argv: tuple[str, ...] = ()
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    logs_truncated: bool = False

    def to_public_dict(self) -> dict[str, object]:
        """Only safe receipt fields.  No output rows, paths, or child diagnostics."""
        return {
            "status": self.status.value,
            "run_id": self.run_id,
            "predictions_sha256": self.predictions_sha256,
            "row_count": self.row_count,
            "stdout_bytes": self.stdout_bytes,
            "stderr_bytes": self.stderr_bytes,
            "logs_truncated": self.logs_truncated,
        }


@dataclass(frozen=True)
class _OpenedFile:
    path: Path
    digest: str
    size: int
    device: int
    inode: int
    mtime_ns: int
    payload: bytes | None = None


class _InputError(Exception):
    pass


class _PipeCounter:
    """Aggregate stdout/stderr cap with byte counts but no retained content."""

    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.stdout_bytes = 0
        self.stderr_bytes = 0
        self.flooded = threading.Event()
        self._lock = threading.Lock()

    def add(self, channel: str, size: int) -> bool:
        with self._lock:
            if channel == "stdout":
                self.stdout_bytes += size
            else:
                self.stderr_bytes += size
            if self.stdout_bytes + self.stderr_bytes > self.cap:
                self.flooded.set()
                return True
            return False


def _drain_bounded(stream: BinaryIO, counter: _PipeCounter, channel: str) -> None:
    """Drain without retaining child-controlled text; stop after aggregate cap."""
    try:
        while not counter.flooded.is_set():
            chunk = stream.read(1024)
            if not chunk:
                return
            if counter.add(channel, len(chunk)):
                return
    finally:
        stream.close()


def _sha256_from_fd(fd: int) -> str:
    digest = hashlib.sha256()
    while True:
        block = os.read(fd, 1024 * 1024)
        if not block:
            return digest.hexdigest()
        digest.update(block)


def _open_exact_regular(path: Path, max_bytes: int, *, capture_payload: bool = False) -> _OpenedFile:
    """Reject links/special files before opening and bind the opened byte identity."""
    if max_bytes <= 0:
        raise _InputError("input_cap")
    try:
        before = os.lstat(path)
    except OSError as error:
        raise _InputError("input_missing") from error
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise _InputError("input_type")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise _InputError("input_open") from error
    try:
        opened = os.fstat(fd)
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or
                opened.st_dev != before.st_dev or opened.st_ino != before.st_ino or
                opened.st_size != before.st_size or opened.st_size > max_bytes):
            raise _InputError("input_changed")
        digest = hashlib.sha256()
        chunks: list[bytes] | None = [] if capture_payload else None
        remaining = opened.st_size + 1
        while remaining:
            block = os.read(fd, min(1024 * 1024, remaining))
            if not block:
                break
            digest.update(block)
            if chunks is not None:
                chunks.append(block)
            remaining -= len(block)
        payload = b"".join(chunks) if chunks is not None else None
        if (remaining != 1 or (payload is not None and len(payload) != opened.st_size)):
            raise _InputError("input_short_read")
        after = os.fstat(fd)
        if (after.st_dev != opened.st_dev or after.st_ino != opened.st_ino or
                after.st_size != opened.st_size or after.st_mtime_ns != opened.st_mtime_ns):
            raise _InputError("input_changed_read")
        return _OpenedFile(
            path=path.absolute(), digest=digest.hexdigest(), size=opened.st_size,
            device=opened.st_dev, inode=opened.st_ino, mtime_ns=opened.st_mtime_ns,
            payload=payload,
        )
    finally:
        os.close(fd)


def _unchanged(opened: _OpenedFile) -> bool:
    try:
        current = os.lstat(opened.path)
    except OSError:
        return False
    if (not stat.S_ISREG(current.st_mode) or current.st_nlink != 1 or
            current.st_dev != opened.device or current.st_ino != opened.inode or
            current.st_size != opened.size or current.st_mtime_ns != opened.mtime_ns):
        return False
    try:
        return _open_exact_regular(opened.path, opened.size).digest == opened.digest
    except _InputError:
        return False


def _is_int(value: object, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def _is_finite_number(value: object, minimum: float, maximum: float) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value)) and minimum <= float(value) <= maximum


def _validate_config(config: RunnerConfig) -> None:
    try:
        parsed_run_id = uuid.UUID(config.run_id)
    except (AttributeError, ValueError):
        raise _InputError("run_id") from None
    if str(parsed_run_id) != config.run_id:
        raise _InputError("run_id")
    if not _is_int(config.wall_seconds, 1, 3600):
        raise _InputError("wall_seconds")
    if not _is_finite_number(config.cpus, 0.01, 8):
        raise _InputError("cpus")
    if not _is_int(config.memory_bytes, 16 * 1024 * 1024, 8 * 1024 * 1024 * 1024):
        raise _InputError("memory")
    if not _is_int(config.pids_limit, 1, 256) or not _is_int(config.nofile, 16, 4096):
        raise _InputError("process_limits")
    if not _is_int(config.tmpfs_bytes, 1024 * 1024, 1024 * 1024 * 1024):
        raise _InputError("tmpfs")
    if not _is_int(config.max_input_bytes, 1, 256 * 1024 * 1024):
        raise _InputError("input_size")
    if not _is_int(config.max_output_bytes, 1, 64 * 1024 * 1024):
        raise _InputError("output_size")
    if not _is_int(config.log_quarantine_bytes, 1, 64 * 1024 * 1024):
        raise _InputError("log_quarantine_size")


def _prepare_output(config: RunnerConfig) -> Path:
    """Create the one writable host file; the container never mounts its directory."""
    parent = config.output_parent.absolute()
    try:
        parent_info = os.lstat(parent)
    except OSError as error:
        raise _InputError("output_parent") from error
    if not stat.S_ISDIR(parent_info.st_mode) or stat.S_ISLNK(parent_info.st_mode):
        raise _InputError("output_parent")
    run_directory = parent / config.run_id
    try:
        run_directory.mkdir(mode=0o700)
        output = run_directory / "predictions.csv"
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_CLOEXEC", 0), 0o666)
        os.close(fd)
        os.chmod(output, 0o666)
    except OSError as error:
        raise _InputError("output_create") from error
    return output


def _docker_argv(config: RunnerConfig, entry_path: Path, output: Path) -> tuple[str, ...]:
    mounts = (
        (config.solution_path.absolute(), "/solution/solution.py", True),
        (config.train_path.absolute(), "/input/train.csv", True),
        (config.features_path.absolute(), "/input/features.csv", True),
        (entry_path.absolute(), "/trusted/container_entry.py", True),
        (output.absolute(), "/tmp/predictions.csv", False),
    )
    argv: list[str] = [
        DOCKER_EXECUTABLE, "run", "--rm", "--name", config.container_name,
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges=true", "--user", CONTAINER_UID_GID,
        "--pids-limit", str(config.pids_limit), "--cpus", str(config.cpus),
        "--memory", str(config.memory_bytes), "--memory-swap", str(config.memory_bytes),
        "--ulimit", f"nofile={config.nofile}:{config.nofile}",
        "--ulimit", f"fsize={config.max_output_bytes}:{config.max_output_bytes}",
        "--tmpfs", f"/tmp:rw,nosuid,nodev,noexec,size={config.tmpfs_bytes},mode=1777",
        "--log-driver", "local", "--log-opt", f"max-size={max(1, math.ceil(config.log_quarantine_bytes / 1024))}k",
        "--log-opt", "max-file=1", "--log-opt", "compress=false", "--workdir", "/tmp", "--stop-timeout", "1",
        "--env", f"ARGO_OUTPUT_BYTES={config.max_output_bytes}",
    ]
    for source, target, readonly in mounts:
        mount = f"type=bind,src={source},dst={target}"
        if readonly:
            mount += ",readonly"
        argv.extend(("--mount", mount))
    argv.extend((IMAGE_DIGEST, "python", "/trusted/container_entry.py"))
    return tuple(argv)


def _container_absent(name: str) -> bool:
    try:
        probe = subprocess.run(
            (DOCKER_EXECUTABLE, "container", "ls", "--all", "--filter", f"name=^/{name}$", "--format", "{{.ID}}"),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
        return probe.returncode == 0 and not probe.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return False


def _cleanup_container(name: str) -> bool:
    """Force-remove only this deterministic name, then prove absence to Docker."""
    try:
        subprocess.run(
            (DOCKER_EXECUTABLE, "rm", "--force", name), stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return _container_absent(name)


def _terminate_and_reap(process: subprocess.Popen[bytes] | None, name: str) -> bool:
    """Container removal is primary; direct client termination is bounded fallback."""
    cleanup_ok = _cleanup_container(name)
    if process is not None and process.poll() is None:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                process.terminate()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    cleanup_ok = False
    return cleanup_ok and _container_absent(name)


def _read_feature_ids(features: _OpenedFile) -> list[str] | None:
    if features.payload is None:
        return None
    try:
        reader = csv.reader(io.StringIO(features.payload.decode("utf-8"), newline=""))
        header = next(reader)
        if header.count("Id") != 1 or "SalePrice" in header:
            return None
        index = header.index("Id")
        rows = list(reader)
        if any(len(row) != len(header) for row in rows):
            return None
        return [row[index] for row in rows]
    except (UnicodeError, csv.Error, StopIteration):
        return None


def _verify_output(output: Path, expected_ids: list[str], max_output_bytes: int) -> tuple[str, str | None, int | None]:
    expected = output
    try:
        before = os.lstat(expected)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > max_output_bytes:
            return "invalid", None, None
        if before.st_size == 0:
            return "missing", None, None
        fd = os.open(expected, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(fd)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or
                    opened.st_dev != before.st_dev or opened.st_ino != before.st_ino or
                    opened.st_size != before.st_size):
                return "invalid", None, None
            chunks: list[bytes] = []
            remaining = opened.st_size + 1
            while remaining:
                chunk = os.read(fd, min(1024 * 1024, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
        finally:
            os.close(fd)
        if len(payload) != before.st_size:
            return "invalid", None, None
        reader = csv.reader(io.StringIO(payload.decode("utf-8"), newline=""))
        if next(reader) != ["Id", "SalePrice"]:
            return "invalid", None, None
        rows = list(reader)
        if len(rows) != len(expected_ids):
            return "invalid", None, None
        for row, expected_id in zip(rows, expected_ids, strict=True):
            if len(row) != 2 or row[0] != expected_id or not math.isfinite(float(row[1])):
                return "invalid", None, None
        return "ok", hashlib.sha256(payload).hexdigest(), len(rows)
    except (OSError, UnicodeError, ValueError, csv.Error, StopIteration):
        return "invalid", None, None

def run_fixed_solution(config: RunnerConfig) -> RunResult:
    """Run one pre-admitted immutable solution through one fixed Docker child.

    CPU quota throttles; ``wall_seconds`` terminates. The root-owned ORX bridge
    owns run admission and lifecycle beyond this single child.
    """
    argv: tuple[str, ...] = ()
    output: Path | None = None
    process: subprocess.Popen[bytes] | None = None
    drainers: list[threading.Thread] = []
    log_counter: _PipeCounter | None = None
    interrupted = threading.Event()
    previous_term: object | None = None

    def signal_interrupt(_: int, __: object) -> None:
        interrupted.set()

    def result(status: RunStatus, **kwargs: object) -> RunResult:
        if log_counter is not None:
            kwargs.setdefault("stdout_bytes", log_counter.stdout_bytes)
            kwargs.setdefault("stderr_bytes", log_counter.stderr_bytes)
            kwargs.setdefault("logs_truncated", log_counter.flooded.is_set())
        return RunResult(status, config.run_id, docker_argv=argv, **kwargs)

    try:
        if threading.current_thread() is threading.main_thread():
            previous_term = signal.signal(signal.SIGTERM, signal_interrupt)
        _validate_config(config)
        solution = _open_exact_regular(config.solution_path, config.max_input_bytes)
        train = _open_exact_regular(config.train_path, config.max_input_bytes)
        features = _open_exact_regular(config.features_path, config.max_input_bytes, capture_payload=True)
        entry = _open_exact_regular(Path(__file__).with_name("container_entry.py"), config.max_input_bytes)
        expected_ids = _read_feature_ids(features)
        if expected_ids is None:
            raise _InputError("features_schema")
        output = _prepare_output(config)
        argv = _docker_argv(config, entry.path, output)
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        assert process.stdout is not None and process.stderr is not None
        log_counter = _PipeCounter(config.log_quarantine_bytes)
        drainers = [
            threading.Thread(target=_drain_bounded, args=(process.stdout, log_counter, "stdout"), daemon=True),
            threading.Thread(target=_drain_bounded, args=(process.stderr, log_counter, "stderr"), daemon=True),
        ]
        for drainer in drainers:
            drainer.start()
        deadline = time.monotonic() + config.wall_seconds
        status: RunStatus | None = None
        while process.poll() is None:
            if interrupted.is_set():
                status = RunStatus.CANCELLED
                break
            if log_counter.flooded.is_set():
                status = RunStatus.LOG_LIMIT_EXCEEDED
                break
            if time.monotonic() >= deadline:
                status = RunStatus.TIMEOUT
                break
            time.sleep(0.02)
        if status is not None:
            cleanup_ok = _terminate_and_reap(process, config.container_name)
            for drainer in drainers:
                drainer.join(timeout=1)
            if not cleanup_ok:
                return result(RunStatus.CLEANUP_UNCONFIRMED)
            return result(status)

        exit_code = process.returncode
        cleanup_ok = _terminate_and_reap(process, config.container_name)
        for drainer in drainers:
            drainer.join(timeout=1)
        if not cleanup_ok:
            return result(RunStatus.CLEANUP_UNCONFIRMED)
        if log_counter.flooded.is_set():
            return result(RunStatus.LOG_LIMIT_EXCEEDED)
        if not all(_unchanged(item) for item in (solution, train, features, entry)):
            return result(RunStatus.INVALID_INPUT)
        assert output is not None
        check, digest, rows = _verify_output(output, expected_ids, config.max_output_bytes)
        if check == "missing" and exit_code != 0:
            return result(RunStatus.EXECUTION_FAILED)
        if check != "ok":
            return result(RunStatus.INVALID_OUTPUT)
        if exit_code != 0:
            return result(RunStatus.EXECUTION_FAILED)
        return result(RunStatus.SUCCESS, predictions_path=output, predictions_sha256=digest, row_count=rows)
    except _InputError:
        cleanup_ok = _terminate_and_reap(process, config.container_name)
        return result(RunStatus.INVALID_INPUT if cleanup_ok else RunStatus.CLEANUP_UNCONFIRMED)
    except KeyboardInterrupt:
        cleanup_ok = _terminate_and_reap(process, config.container_name)
        return result(RunStatus.CANCELLED if cleanup_ok else RunStatus.CLEANUP_UNCONFIRMED)
    except (OSError, subprocess.SubprocessError):
        cleanup_ok = _terminate_and_reap(process, config.container_name)
        return result(RunStatus.DOCKER_ERROR if cleanup_ok else RunStatus.CLEANUP_UNCONFIRMED)
    except Exception:
        cleanup_ok = _terminate_and_reap(process, config.container_name)
        return result(RunStatus.INTERNAL_ERROR if cleanup_ok else RunStatus.CLEANUP_UNCONFIRMED)
    finally:
        if previous_term is not None:
            signal.signal(signal.SIGTERM, previous_term)


def _config_from_trusted_request(path: Path) -> RunnerConfig:
    """CLI adapter for the root-owned fixed ORX request file, never model input."""
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    allowed = {field.name for field in RunnerConfig.__dataclass_fields__.values()}
    if set(raw) != allowed:
        raise ValueError("request_schema")
    return RunnerConfig(**{
        key: Path(value) if key.endswith("_path") or key == "output_parent" else value
        for key, value in raw.items()
    })


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Root-owned fixed ORX Docker child only")
    parser.add_argument("--trusted-orx-request", required=True, type=Path)
    arguments = parser.parse_args(argv)
    result = run_fixed_solution(_config_from_trusted_request(arguments.trusted_orx_request))
    print(json.dumps(result.to_public_dict(), sort_keys=True))
    return 0 if result.status is RunStatus.SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
