#!/opt/homebrew/bin/python3
"""Native Prime Python entrypoint with project-wide trusted Store accounting.

Only the worker workspace and session artifacts are mounted. The global Store,
provider auth and controller configuration remain host-only. No ORX lifecycle is
implemented here: this launcher accounts only for persistent native REPL kernels.
"""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
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

REPOSITORY = Path(__file__).resolve().parents[2]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

from experiments.project_research.state import AdmissionError, Store


PRIVATE_ROOT = Path.home() / ".local/share/argo-project-research-20260909"
DOCKER = "/opt/homebrew/bin/docker"
FORBIDDEN = {"control", "custody", "evaluator", "credentials", "auth.json", ".prime",
             ".codex", ".claude", ".ssh", ".aws", "docker.sock"}


@dataclass(frozen=True)
class KernelConfig:
    path: Path
    campaign_id: str
    workspace: Path
    artifacts: Path
    control: Path
    image: str
    deadline: float
    cpus: float
    memory_mib: int
    lease_seconds: float


def safe_path(value: str, *, exists: bool = True) -> Path:
    path = Path(value)
    if not path.is_absolute() or path != path.resolve(strict=exists) or any(c in value for c in (",", "\0", "\r", "\n")):
        raise ValueError("noncanonical kernel path")
    return path


def safe_tree(path: Path) -> None:
    for directory, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            entry = Path(directory) / name
            info = entry.lstat()
            if (name in FORBIDDEN or stat.S_ISLNK(info.st_mode)
                    or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))
                    or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1)):
                raise ValueError("protected, linked or special worker mount member")


def load_config(value: str, *, allow_expired: bool = False) -> KernelConfig:
    path = safe_path(value)
    raw = json.loads(path.read_text())
    workspace = safe_path(raw["workspace"])
    artifacts = safe_path(raw["artifact_root"])
    control = safe_path(raw["control_dir"])
    roots = (workspace, artifacts, control)
    if (not all(root.is_relative_to(PRIVATE_ROOT.resolve()) and root.is_dir() for root in roots)
            or workspace.parent != artifacts.parent or len(set(roots)) != 3
            or not control.is_relative_to(PRIVATE_ROOT / "control")
            or not path.is_relative_to(control)
            or any(left.is_relative_to(right) for left in roots for right in roots if left != right)):
        raise ValueError("kernel requires disjoint workspace/artifact siblings and private control")
    if any(root.stat().st_uid != os.getuid() for root in roots) or os.getuid() == 0:
        raise ValueError("kernel must run with current nonroot ownership")
    if any(part in FORBIDDEN for root in (workspace, artifacts) for part in root.relative_to(PRIVATE_ROOT).parts):
        raise ValueError("protected parent in kernel mount")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", raw["image"]):
        raise ValueError("immutable kernel image required")
    deadline = raw["deadline_epoch"]
    cpus = raw.get("kernel_cpus", 0.5)
    memory = raw.get("kernel_memory_mib", 512)
    seconds = raw.get("kernel_lease_seconds", 900)
    if (any(type(number) not in (float, int) or not math.isfinite(number) or number <= 0 for number in (deadline, cpus, memory, seconds))
            or cpus > 1 or type(memory) is not int or memory > 1024 or seconds > 3600
            or (not allow_expired and deadline <= time.time() + 15)
            or not isinstance(raw["campaign_id"], str) or not raw["campaign_id"]):
        raise ValueError("kernel resource or campaign bound invalid")
    safe_tree(workspace)
    safe_tree(artifacts)
    return KernelConfig(path, raw["campaign_id"], workspace, artifacts, control, raw["image"],
                        float(deadline), float(cpus), memory, float(seconds))


def command(config: KernelConfig, name: str, arguments: list[str], environment: dict[str, str]) -> list[str]:
    if not (len(arguments) == 2 and arguments[0] == "-c" or arguments == ["-m", "rlm.repl"]):
        raise ValueError("only native readiness or REPL entrypoint is allowed")
    safe_tree(config.workspace)
    safe_tree(config.artifacts)
    forwarded = {"RLM_GLOBAL_HARNESS_STATE_DIR": str(config.artifacts / "global-harness")}
    for key in ("RLM_DEPTH", "RLM_MAX_DEPTH"):
        value = environment.get(key, "0" if key == "RLM_DEPTH" else "2")
        if not value.isdecimal() or not 0 <= int(value) <= 8:
            raise ValueError("invalid RLM depth")
        forwarded[key] = value
    for key in ("RLM_SESSION_DIR", "RLM_HARNESS_STATE_DIR"):
        if key in environment:
            path = safe_path(environment[key], exists=False)
            if not any(path.is_relative_to(root) for root in (config.workspace, config.artifacts)):
                raise ValueError("RLM state leaves allowed mounts")
            forwarded[key] = str(path)
    memory = str(config.memory_mib * 1024**2)
    result = [DOCKER, "run", "--rm", "--interactive", "--init", "--name", name,
              "--label", "argo.project-research=20260909", "--label", "argo.role=kernel",
              "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
              "--user", f"{os.getuid()}:{os.getgid()}", "--pids-limit", "128",
              "--cpus", str(config.cpus), "--memory", memory, "--memory-swap", memory,
              "--stop-timeout", "1", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=134217728,mode=1777",
              "--workdir", str(config.workspace), "--env", "HOME=/tmp",
              "--env", "XDG_CACHE_HOME=/tmp/.cache", "--env", "OMP_NUM_THREADS=1",
              "--env", "OPENBLAS_NUM_THREADS=1", "--env", "MKL_NUM_THREADS=1", "--entrypoint", "python"]
    for root in (config.workspace, config.artifacts):
        result.extend(["--mount", f"type=bind,src={root},dst={root}"])
    for key, value in sorted(forwarded.items()):
        result.extend(["--env", f"{key}={value}"])
    return result + [config.image, *arguments]


def _write(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("x") as output:
        json.dump(value, output, sort_keys=True, allow_nan=False)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.chmod(0o600)
    os.replace(temporary, path)


def absent(name: str) -> bool:
    result = subprocess.run([DOCKER, "ps", "--all", "--quiet", "--filter", f"name=^/{name}$"],
                            capture_output=True, text=True, timeout=10, check=False)
    return result.returncode == 0 and not result.stdout.strip()


def cleanup(name: str) -> bool:
    try:
        subprocess.run([DOCKER, "rm", "--force", name], capture_output=True, timeout=10, check=False)
        return absent(name)
    except (OSError, subprocess.SubprocessError):
        return False


def container_process_alive(name: str) -> bool:
    try:
        result = subprocess.run([DOCKER, "top", name], capture_output=True, text=True, timeout=10, check=False)
        return result.returncode == 0 and len(result.stdout.strip().splitlines()) > 1
    except (OSError, subprocess.SubprocessError):
        return True


def settle(config: KernelConfig, record: dict, removed: bool, reason: str) -> None:
    elapsed = max(0, time.time() - record["started_at"])
    cpu = elapsed * config.cpus if removed and elapsed <= record["reserved_seconds"] else None
    receipt = {"terminal": removed, "container_absent": removed, "reason": reason,
               "container": record["container"], "usage_basis": "allocated_wall_upper_bound",
               "measured_cpu_seconds": None, "allocated_cpu_seconds": cpu, "wall_seconds": elapsed}
    store = Store(PRIVATE_ROOT / "control" / "state.sqlite")
    try:
        store.settle_compute(record["lease_id"], cpu, receipt)
    except AdmissionError:
        matching = [row for row in store.snapshot()["compute"] if row["id"] == record["lease_id"]]
        if len(matching) != 1 or matching[0]["state"] != "SETTLED":
            raise
    _write(config.control / (record["lease_id"] + ".completion.json"), receipt)


def status(config: KernelConfig) -> dict:
    leases = Store(PRIVATE_ROOT / "control" / "state.sqlite").snapshot()["compute"]
    active = [row["id"] for row in leases if row["id"].startswith("kernel-") and row["state"] in ("ACTIVE", "UNKNOWN")]
    own = [lease for lease in active if (config.control / (lease + ".json")).exists()]
    return {"status": "CLEAR" if not own else "KERNELS_REQUIRE_RECONCILIATION", "kernel_leases": own, "global_kernel_leases": active}


def watchdog(config: KernelConfig, record_path: Path) -> int:
    record = json.loads(record_path.read_text())
    reason = "owner_exit"
    while time.time() < record["stop_at"]:
        try:
            os.kill(record["wrapper_pid"], 0)
        except ProcessLookupError:
            break
        time.sleep(0.2)
    else:
        reason = "kernel_lease_deadline"
        with contextlib.suppress(ProcessLookupError):
            os.kill(record["wrapper_pid"], signal.SIGTERM)
    removed = cleanup(record["container"])
    settle(config, record, removed, reason)
    return 0 if removed else 1


def execute(config: KernelConfig, arguments: list[str]) -> int:
    lease = "kernel-" + uuid.uuid4().hex
    name = "project-research-" + lease
    invocation = command(config, name, arguments, dict(os.environ))
    seconds = min(config.lease_seconds, config.deadline - time.time())
    if seconds <= 15:
        raise AdmissionError("no bounded kernel cleanup reserve remains")
    store = Store(PRIVATE_ROOT / "control" / "state.sqlite")
    store.admit_compute(lease, config.campaign_id, seconds, config.cpus, config.memory_mib, exclusive=False)
    record = {"lease_id": lease, "container": name, "wrapper_pid": os.getpid(),
              "started_at": time.time(), "reserved_seconds": seconds, "stop_at": time.time() + seconds - 10}
    path = config.control / (lease + ".json")
    _write(path, record)
    watcher = subprocess.Popen([sys.executable, "-m", "experiments.project_research.kernel_launcher",
                                "--config", str(config.path), "--watchdog", str(path)], cwd=REPOSITORY,
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               start_new_session=True)
    process = None
    reason = "completed"
    def interrupted(signum, frame):
        raise InterruptedError(signum)
    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        process = subprocess.Popen(invocation)
        last_pid_check = time.time()
        while process.poll() is None:
            if time.time() >= record["stop_at"]:
                reason = "kernel_lease_deadline"
                return 124
            # A -c readiness probe is short; if the container's process is gone but the CLI has not
            # returned (observed after a host network drop), the probe is stuck and must be retired.
            if arguments[0] == "-c" and time.time() - last_pid_check > 30:
                last_pid_check = time.time()
                if time.time() - record["started_at"] > 90 and not container_process_alive(name):
                    reason = "probe_orphaned"
                    return 125
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
            process.wait(timeout=5)
        removed = cleanup(name)
        settle(config, record, removed, reason)
        if removed:
            watcher.terminate()
            watcher.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", default=os.environ.get("ARGO_KERNEL_CONFIG"))
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--watchdog", type=Path)
    options, arguments = parser.parse_known_args()
    config = load_config(options.config, allow_expired=bool(options.status or options.watchdog))
    if options.status:
        print(json.dumps(status(config)))
        return 0
    if options.watchdog:
        return watchdog(config, options.watchdog)
    return execute(config, arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, AdmissionError, subprocess.SubprocessError) as error:
        print(f"project research kernel: {error}", file=sys.stderr)
        raise SystemExit(125)
