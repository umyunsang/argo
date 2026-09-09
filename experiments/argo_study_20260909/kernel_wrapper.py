#!/usr/bin/env python3
"""Research-local Docker interpreter for the unchanged Prime native kernel.

The host bridge may share reserve_resources/release_resources with fit jobs.
Control files are never mounted. CPU charges are conservative allocation-time
bounds, not measured utilization. No command is evaluated by a host shell.
"""
from __future__ import annotations

import contextlib
import dataclasses
import fcntl
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
import uuid


STUDY_ROOT = Path.home() / ".local/share/argo-study-20260909"
GIB = 1024**3
FORBIDDEN_NAMES = {
    "custody", "source", "sources", "auth.json", "credentials", "profile",
    "control", ".ssh", ".aws", ".prime", ".codex", "docker.sock",
    "dev_y.csv", "test_y.csv", "test_X.csv", "test", "test_data",
}


@dataclasses.dataclass(frozen=True)
class Config:
    image: str
    workspace: Path
    artifact_root: Path
    control_dir: Path
    deadline_epoch: float
    kernel_cpus: float = 0.5
    kernel_memory_bytes: int = 512 * 1024**2
    episode_cpus: float = 2.0
    episode_memory_bytes: int = 8 * GIB
    max_cpu_seconds: float = 7200.0
    pids_limit: int = 128
    docker: str = "/opt/homebrew/bin/docker"


def canonical_path(value: str, *, exists: bool = True) -> Path:
    path = Path(value)
    if not path.is_absolute() or any(c in value for c in (",", "\n", "\r", "\0")):
        raise ValueError("paths must be absolute and free of mount delimiters")
    if path != path.resolve(strict=exists):
        raise ValueError("symlinks and non-canonical paths are forbidden")
    return path


def _positive(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def load_config(path: str | Path) -> Config:
    config_path = canonical_path(str(path))
    raw = json.loads(config_path.read_text())
    allowed = {field.name for field in dataclasses.fields(Config)}
    if not isinstance(raw, dict) or set(raw) - allowed:
        raise ValueError("unknown kernel configuration fields")
    for name in ("workspace", "artifact_root", "control_dir"):
        raw[name] = canonical_path(raw[name])
    cfg = Config(**raw)
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", cfg.image):
        raise ValueError("an immutable local image ID is required")
    roots = (cfg.workspace, cfg.artifact_root, cfg.control_dir)
    episode = cfg.workspace.parent
    if not episode.is_relative_to(STUDY_ROOT.resolve()) or episode == STUDY_ROOT.resolve():
        raise ValueError("episode must be private and below the dedicated study root")
    if len({root.parent for root in roots}) != 1 or len(set(roots)) != 3:
        raise ValueError("workspace, artifacts and control must be distinct episode siblings")
    if roots != (episode / "workspace", episode / "artifacts", episode / "control"):
        raise ValueError("episode directories must be workspace, artifacts and control")
    if not config_path.is_relative_to(cfg.control_dir):
        raise ValueError("config must be inside the unmounted control directory")
    if any(part in FORBIDDEN_NAMES for part in episode.relative_to(STUDY_ROOT).parts):
        raise ValueError("episode path overlaps a protected study area")
    for root in roots:
        if not root.is_dir() or root.stat().st_uid != os.getuid():
            raise ValueError("episode paths must be current-user-owned directories")
    for name in ("deadline_epoch", "kernel_cpus", "kernel_memory_bytes", "episode_cpus",
                 "episode_memory_bytes", "max_cpu_seconds", "pids_limit"):
        _positive(getattr(cfg, name), name)
    if cfg.episode_cpus > 2 or cfg.episode_memory_bytes > 8 * GIB:
        raise ValueError("episode exceeds 2 CPU or 8 GiB ceiling")
    if cfg.kernel_cpus > cfg.episode_cpus or cfg.kernel_memory_bytes > cfg.episode_memory_bytes:
        raise ValueError("kernel allocation exceeds episode ceiling")
    if not 16 <= cfg.pids_limit <= 256 or not isinstance(cfg.pids_limit, int):
        raise ValueError("pids_limit must be an integer between 16 and 256")
    if not isinstance(cfg.kernel_memory_bytes, int) or not isinstance(cfg.episode_memory_bytes, int):
        raise ValueError("memory limits must be integer bytes")
    if os.getuid() == 0:
        raise ValueError("the host wrapper must run as a nonroot user")
    if not Path(cfg.docker).is_absolute() or not os.access(cfg.docker, os.X_OK):
        raise ValueError("docker must identify a local executable")
    return cfg


def validate_mount_tree(root: Path) -> None:
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            info = path.lstat()
            if name in FORBIDDEN_NAMES:
                raise ValueError(f"protected entry in public mount: {name}")
            if stat.S_ISLNK(info.st_mode) or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise ValueError("mount contains symlink or special file")
            if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
                raise ValueError("mount contains a hardlinked file")


def _atomic_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as out:
        json.dump(value, out, sort_keys=True, indent=2)
        out.write("\n")
    os.replace(temporary, path)


@contextlib.contextmanager
def _pool(cfg: Config):
    lock_path = cfg.control_dir / "resource-pool.lock"
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = cfg.control_dir / "resource-pool.json"
        data = json.loads(path.read_text()) if path.exists() else {
            "schema": "argo-study-resource-pool/v1", "active": {}, "completed": [],
            "conservative_cpu_seconds": 0.0,
            "limits": {"cpus": cfg.episode_cpus, "memory_bytes": cfg.episode_memory_bytes,
                       "max_cpu_seconds": cfg.max_cpu_seconds, "deadline_epoch": cfg.deadline_epoch},
        }
        expected = {"cpus": cfg.episode_cpus, "memory_bytes": cfg.episode_memory_bytes,
                    "max_cpu_seconds": cfg.max_cpu_seconds, "deadline_epoch": cfg.deadline_epoch}
        if data["limits"] != expected:
            raise ValueError("shared pool limits changed during the episode")
        yield data
        _atomic_json(path, data)


def reserve_resources(cfg: Config, name: str, cpus: float, memory_bytes: int,
                      *, kind: str = "fit", pid: int | None = None) -> str:
    """Admit one allocation or fail before launch; callers retry deliberately."""
    cpus = _positive(cpus, "cpus")
    _positive(memory_bytes, "memory_bytes")
    if not isinstance(memory_bytes, int) or kind not in {"kernel", "fit", "probe"}:
        raise ValueError("invalid resource allocation")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}", name):
        raise ValueError("resource name must be a safe identifier")
    now = time.time()
    with _pool(cfg) as data:
        active = list(data["active"].values())
        if now >= cfg.deadline_epoch:
            raise RuntimeError("episode deadline exhausted")
        if sum(item["cpus"] for item in active) + cpus > cfg.episode_cpus + 1e-9:
            raise RuntimeError("episode CPU slots exhausted")
        if sum(item["memory_bytes"] for item in active) + memory_bytes > cfg.episode_memory_bytes:
            raise RuntimeError("episode memory slots exhausted")
        if kind == "fit" and sum(item["kind"] == "fit" for item in active) >= 2:
            raise RuntimeError("two scientific jobs already active")
        consumed = data["conservative_cpu_seconds"] + sum(
            max(0, now - item["started_at"]) * item["cpus"] for item in active)
        if consumed >= cfg.max_cpu_seconds:
            raise RuntimeError("conservative episode CPU allowance exhausted")
        if any(item["name"] == name for item in active):
            raise RuntimeError("resource name already active")
        lease = uuid.uuid4().hex
        data["active"][lease] = {
            "name": name, "kind": kind, "pid": pid or os.getpid(),
            "cpus": cpus, "memory_bytes": memory_bytes, "started_at": now,
        }
    return lease


def release_resources(cfg: Config, lease: str, *, reason: str = "completed",
                      measured_cpu_seconds: float | None = None) -> None:
    """Release only after the identified process/container is confirmed stopped."""
    with _pool(cfg) as data:
        item = data["active"].pop(lease, None)
        if item is None:
            return
        stopped_at = time.time()
        charged = max(0, stopped_at - item["started_at"]) * item["cpus"]
        data["conservative_cpu_seconds"] += charged
        data["completed"].append({**item, "lease": lease, "stopped_at": stopped_at,
                                  "conservative_cpu_seconds": charged,
                                  "measured_cpu_seconds": measured_cpu_seconds, "reason": reason})


def remaining_seconds(cfg: Config) -> float:
    now = time.time()
    with _pool(cfg) as data:
        active = list(data["active"].values())
        cpus = sum(item["cpus"] for item in active)
        consumed = data["conservative_cpu_seconds"] + sum(
            max(0, now - item["started_at"]) * item["cpus"] for item in active)
        cpu_time = (cfg.max_cpu_seconds - consumed) / cpus if cpus else math.inf
        return max(0.0, min(cfg.deadline_epoch - now, cpu_time))


def remaining_cpu_seconds(cfg: Config) -> float:
    """Remaining conservative core-seconds, independent of current concurrency."""
    now = time.time()
    with _pool(cfg) as data:
        consumed = data["conservative_cpu_seconds"] + sum(
            max(0, now - item["started_at"]) * item["cpus"]
            for item in data["active"].values())
        return max(0.0, cfg.max_cpu_seconds - consumed)


def docker_command(cfg: Config, name: str, arguments: list[str], env: dict[str, str]) -> list[str]:
    if not (len(arguments) == 2 and arguments[0] == "-c" or arguments == ["-m", "rlm.repl"]):
        raise ValueError("only native -c readiness and -m rlm.repl entrypoints are supported")
    for root in (cfg.workspace, cfg.artifact_root):
        validate_mount_tree(root)
    forwarded = {}
    for key in ("RLM_DEPTH", "RLM_MAX_DEPTH"):
        value = env.get(key, "0" if key == "RLM_DEPTH" else "2")
        if not value.isdecimal() or not 0 <= int(value) <= 32:
            raise ValueError(f"invalid {key}")
        forwarded[key] = value
    for key in ("RLM_SESSION_DIR", "RLM_HARNESS_STATE_DIR"):
        if key in env:
            path = canonical_path(env[key], exists=False)
            if not any(path.is_relative_to(root) for root in (cfg.workspace, cfg.artifact_root)):
                raise ValueError(f"{key} leaves episode mounts")
            forwarded[key] = str(path)
    forwarded["RLM_GLOBAL_HARNESS_STATE_DIR"] = str(cfg.artifact_root / "global-harness")
    command = [cfg.docker, "run", "--rm", "--interactive", "--init", "--name", name,
               "--label", "argo.study=20260909", "--network", "none", "--read-only",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "--user", f"{os.getuid()}:{os.getgid()}", "--pids-limit", str(cfg.pids_limit),
               "--cpus", str(cfg.kernel_cpus), "--memory", str(cfg.kernel_memory_bytes),
               "--memory-swap", str(cfg.kernel_memory_bytes), "--stop-timeout", "1",
               "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=134217728,mode=1777",
               "--workdir", str(cfg.workspace), "--env", "HOME=/tmp",
               "--env", "XDG_CACHE_HOME=/tmp/.cache", "--entrypoint", "python"]
    for root in (cfg.workspace, cfg.artifact_root):
        command += ["--mount", f"type=bind,src={root},dst={root}"]
    for key, value in sorted(forwarded.items()):
        command += ["--env", f"{key}={value}"]
    return command + [cfg.image, *arguments]


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def _remove_container(cfg: Config, name: str) -> bool:
    try:
        subprocess.run([cfg.docker, "rm", "--force", name], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=10, check=False)
        result = subprocess.run([cfg.docker, "container", "ls", "--all", "--quiet",
                                 "--filter", f"name=^/{name}$"], capture_output=True,
                                text=True, timeout=10, check=False)
        return result.returncode == 0 and not result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False


def _watchdog(config_path: str, owner: int, name: str, lease: str) -> int:
    cfg = load_config(config_path)
    record_path = cfg.control_dir / f"{name}.json"
    reason = "owner_exit"
    while _alive(owner):
        if remaining_seconds(cfg) <= 0:
            reason = "episode_limit"
            break
        time.sleep(0.2)
    if reason == "episode_limit":
        with contextlib.suppress(ProcessLookupError):
            os.kill(owner, signal.SIGTERM)
    # The watchdog has a separate process group, so native killpg(SIGKILL)
    # cannot remove it together with the interpreter wrapper.
    if record_path.exists():
        record = json.loads(record_path.read_text())
        cli_pid = record.get("docker_cli_pid")
        if isinstance(cli_pid, int):
            with contextlib.suppress(ProcessLookupError):
                os.kill(cli_pid, signal.SIGKILL)
    removed = False
    for _ in range(3):
        removed = _remove_container(cfg, name)
        time.sleep(0.2)
    if removed:
        release_resources(cfg, lease, reason=reason)
    _atomic_json(cfg.control_dir / f"{name}.watchdog.json",
                 {"reason": reason, "container_removed": removed, "lease": lease})
    return 0 if removed else 1


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments[:1] == ["--watchdog"]:
        return _watchdog(arguments[1], int(arguments[2]), arguments[3], arguments[4])
    config_path = os.environ.get("ARGO_KERNEL_CONFIG")
    if not config_path:
        raise ValueError("ARGO_KERNEL_CONFIG is required")
    cfg = load_config(config_path)
    name = "argo-kernel-" + uuid.uuid4().hex
    command = docker_command(cfg, name, arguments, dict(os.environ))
    lease = reserve_resources(cfg, name, cfg.kernel_cpus, cfg.kernel_memory_bytes,
                              kind="probe" if arguments[0] == "-c" else "kernel")
    record_path = cfg.control_dir / f"{name}.json"
    _atomic_json(record_path, {"container": name, "wrapper_pid": os.getpid(), "lease": lease,
                              "image": cfg.image, "started_at": time.time()})
    watcher = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--watchdog",
                                config_path, str(os.getpid()), name, lease],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, start_new_session=True)
    process = None
    reason = "completed"
    def terminate(signum: int, frame: object) -> None:
        raise InterruptedError(signum)
    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, terminate)
    try:
        process = subprocess.Popen(command)
        record = json.loads(record_path.read_text())
        _atomic_json(record_path, {**record, "docker_cli_pid": process.pid})
        while process.poll() is None:
            if remaining_seconds(cfg) <= 0:
                reason = "episode_limit"
                return 124
            time.sleep(0.1)
        return process.returncode
    except InterruptedError:
        reason = "signal"
        return 143
    finally:
        for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            signal.signal(signum, signal.SIG_IGN)
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        removed = _remove_container(cfg, name)
        if removed:
            release_resources(cfg, lease, reason=reason)
        _atomic_json(cfg.control_dir / f"{name}.completion.json",
                     {"reason": reason, "container_removed": removed, "lease": lease})
        if removed:
            watcher.terminate()
            watcher.wait(timeout=5)
        # An unavailable Docker daemon keeps the lease reserved and leaves the
        # watchdog responsible for its own final UNKNOWN cleanup receipt.


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"kernel wrapper: {exc}", file=sys.stderr)
        sys.exit(125)
