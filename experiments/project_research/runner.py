"""Fixed ORX entrypoint. The committed node spec owns task variation."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

from experiments.project_research.contracts import digest, utc_now, write_new
from experiments.project_research.state import Store


PRIVATE_ROOT = Path.home() / ".local/share/argo-project-research-20260909"
DOCKER = "/opt/homebrew/bin/docker"


def safe_tree(path: Path) -> Path:
    if path != path.resolve() or not path.is_dir() or any(c in str(path) for c in (",", "\n", "\r")):
        raise ValueError("noncanonical mount")
    for entry in path.rglob("*"):
        if entry.is_symlink() or not (entry.is_file() or entry.is_dir()) or (entry.is_file() and entry.stat().st_nlink > 1):
            raise ValueError("unsafe mount member")
    return path


def absent(name: str) -> bool:
    check = subprocess.run([DOCKER, "ps", "-a", "-q", "--filter", f"name=^/{name}$"], capture_output=True, text=True, timeout=15)
    return check.returncode == 0 and not check.stdout.strip()


def cleanup(name: str) -> bool:
    try:
        subprocess.run([DOCKER, "rm", "-f", name], capture_output=True, timeout=15)
        return absent(name)
    except (OSError, subprocess.TimeoutExpired):
        return False


def background_activity() -> list[dict]:
    result = subprocess.run([DOCKER, "stats", "--no-stream", "--format", "{{json .}}"], capture_output=True, text=True, timeout=15, check=True)
    rows = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    for row in rows:
        usage = float(row["CPUPerc"].rstrip("%"))
        if not math.isfinite(usage) or usage > 1.0 or row["Name"].startswith(("project-research-", "argo-kernel-")):
            raise RuntimeError("competing compute observed; measurement deferred")
    return [{"name": row["Name"], "cpu_percent": row["CPUPerc"], "memory": row["MemUsage"]} for row in rows]


def valid_observation(scientific: object, resources: object, domain: str) -> bool:
    if not isinstance(scientific, dict) or not isinstance(resources, dict):
        return False
    if resources.get("exit_code") != 0:
        return False
    for key in ("cpu_seconds", "wall_seconds"):
        number = resources.get(key)
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number) or number < 0:
            return False
    return (scientific.get("schema_version") == "project-research-domain-result/v1"
            and scientific.get("domain") == domain and scientific.get("status") == "OBSERVATIONS_RECORDED"
            and scientific.get("development_only") is True and scientific.get("final_evaluation") is False
            and scientific.get("evidence_stage") == "DEVELOPMENT_BASELINE_HYPOTHESIS"
            and isinstance(scientific.get("result"), dict) and bool(scientific["result"])
            and scientific.get("environment", {}).get("matches_pins") is True
            and bool(scientific.get("code_sha256")))


def watchdog(owner: int, name: str, deadline: float, output: Path) -> int:
    reason = "deadline"
    while time.time() < deadline:
        try:
            os.kill(owner, 0)
        except ProcessLookupError:
            reason = "owner_exit"
            break
        time.sleep(0.25)
    removed = cleanup(name)
    output.write_text(json.dumps({"reason": reason, "container_absent": removed, "at": utc_now()}) + "\n")
    return 0 if removed else 1


def execute(snapshot: Path) -> dict:
    spec = json.loads((snapshot / "node-spec.json").read_text())
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", spec["image"]):
        raise ValueError("immutable image required")
    worker = safe_tree(Path(spec["worker_root"]))
    if worker != PRIVATE_ROOT / "worker" or spec["domain"] not in ("wine", "duckdb", "diffusion"):
        raise ValueError("public input boundary")
    if spec.get("mode", "development") not in ("development", "candidate"):
        raise ValueError("invalid execution mode")
    if not isinstance(spec["arguments"], list) or not all(isinstance(a, str) for a in spec["arguments"]):
        raise ValueError("argument list required")
    if not spec["arguments"] or spec["arguments"][0] != spec["domain"] or "--output" in spec["arguments"]:
        raise ValueError("invalid task arguments")
    seconds = spec.get("timeout_seconds", 600)
    if type(seconds) is not int or not 30 <= seconds <= 28800:
        raise ValueError("bounded task timeout required")
    task_id = uuid.uuid4().hex
    name = f"project-research-{task_id}"
    output = PRIVATE_ROOT / "runs" / task_id
    output.mkdir(parents=True, mode=0o700)
    store = Store(PRIVATE_ROOT / "control" / "state.sqlite")
    # External processes also matter for exclusive performance measurements.
    background_before = background_activity()
    store.admit_compute(task_id, spec["project_id"], seconds, 1, 2048, exclusive=True)
    command = [DOCKER, "run", "--rm", "--name", name, "--label", "argo.project-research=20260909",
               "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "--cpus", "1", "--memory", "2147483648", "--memory-swap", "2147483648", "--pids-limit", "128",
               "--user", f"{os.getuid()}:{os.getgid()}", "--tmpfs", "/tmp:rw,nosuid,nodev,size=536870912,mode=1777",
               "--env", "HOME=/tmp", "--env", "PYTHONDONTWRITEBYTECODE=1", "--env", "PYTHONPATH=/app",
               "--env", "OMP_NUM_THREADS=1", "--env", "OPENBLAS_NUM_THREADS=1", "--env", "MKL_NUM_THREADS=1",
               "--mount", f"type=bind,src={safe_tree(snapshot)},dst=/app,readonly",
               "--mount", f"type=bind,src={worker},dst=/workspace,readonly",
               "--mount", f"type=bind,src={output},dst=/output",
               "--workdir", "/app", "--entrypoint", "python", spec["image"],
               "-m", "experiments.project_research.container_task"]
    started = utc_now()
    timer = time.monotonic()
    watcher = subprocess.Popen([sys.executable, "-m", "experiments.project_research.runner", "--watchdog", str(os.getpid()), name,
                                str(time.time() + seconds - 2), str(output / "watchdog.json")],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
    exit_code = None
    error = None
    def interrupted(signum, frame):
        raise InterruptedError(signum)
    old = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        with (output / "stdout.txt").open("w") as out, (output / "stderr.txt").open("w") as err:
            result = subprocess.run(command, stdout=out, stderr=err, timeout=seconds - 5, check=False)
            exit_code = result.returncode
    except (OSError, subprocess.TimeoutExpired, InterruptedError) as exc:
        error = type(exc).__name__
    finally:
        for s, handler in old.items():
            signal.signal(s, handler)
        removed = cleanup(name)
        if removed:
            watcher.terminate()
            watcher.wait(timeout=5)
    wall = time.monotonic() - timer
    try:
        background_after = background_activity()
        quiet_samples = True
    except (RuntimeError, OSError, subprocess.SubprocessError):
        background_after = None
        quiet_samples = False
    resource_path = output / "resource.json"
    resources = json.loads(resource_path.read_text()) if resource_path.exists() else None
    result_path = output / "result.json"
    scientific = json.loads(result_path.read_text()) if result_path.exists() else None
    if not removed:
        status = "UNKNOWN"
    elif spec.get("mode") == "candidate" and exit_code == 0:
        # Candidate code owns its outputs; exit 0 evidences execution only, never validation.
        status = "EXECUTED_UNVALIDATED"
    else:
        status = "SUCCEEDED" if exit_code == 0 and valid_observation(scientific, resources, spec["domain"]) else "FAILED"
    receipt = {"schema": "project-research-run/v1", "id": task_id, "project_id": spec["project_id"], "domain": spec["domain"],
               "started_at": started, "ended_at": utc_now(), "status": status, "error": error, "exit_code": exit_code,
               "terminal": removed, "container_absent": removed, "image": spec["image"], "spec_digest": digest(spec),
               "command": command, "wall_seconds": wall, "resources": resources, "result": scientific,
               "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest() if result_path.exists() else None,
               "output_files": sorted(p.name for p in output.iterdir() if p.is_file() and p.name not in ("receipt.json",)),
               "stdout_tail": (output / "stdout.txt").read_text(errors="replace")[-4000:] if (output / "stdout.txt").exists() else None,
               "stderr_tail": (output / "stderr.txt").read_text(errors="replace")[-2000:] if (output / "stderr.txt").exists() else None,
               "output_path": str(output), "scope": "DEVELOPMENT_RESEARCH", "autonomous_campaign": spec.get("mode") == "candidate",
               "AAA": "UNASSESSED", "PI": "PENDING", "additional_charge_krw": 0,
               "scientific_validation": "DEVELOPMENT_OBSERVATIONS_ONLY" if status == "SUCCEEDED" else "NOT_ASSESSED",
               "background_before": background_before, "background_after": background_after,
               "timing_admissibility": "IDLE_SERVICE_SAMPLES_ONLY" if quiet_samples else "BACKGROUND_ACTIVITY_UNCONFIRMED",
               "timing_limit": "Before/after CPU samples are not continuous quiet-host proof; confirmatory timing remains pending.",
               "charge_basis": "local computation; no model, search, or paid service call in runner"}
    # Allocation time is a conservative CPU reservation charge, separately named.
    store.settle_compute(task_id, min(seconds, wall) if removed and wall <= seconds else None,
                         {"terminal": removed, "container_absent": removed, "cpu_accounting": "allocated_wall_upper_bound", "receipt": str(output / "receipt.json")})
    write_new(output / "receipt.json", receipt)
    store.event({"event": "development_research_result", "receipt": str(output / "receipt.json"), "id": task_id,
                 "project_id": spec["project_id"], "team_id": spec.get("team_id"), "domain": spec["domain"],
                 "status": status, "autonomous_campaign": spec.get("mode") == "candidate"})
    return receipt


def main() -> int:
    if sys.argv[1:2] == ["--watchdog"]:
        return watchdog(int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), Path(sys.argv[5]))
    try:
        receipt = execute(Path.cwd())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        spec = json.loads((Path.cwd() / "node-spec.json").read_text())
        receipt = {"schema": "project-research-run/v1", "project_id": spec["project_id"], "domain": spec["domain"],
                   "status": "BLOCKED", "scope": "INFRASTRUCTURE_FAILURE", "autonomous_campaign": False,
                   "error": type(exc).__name__, "reason": str(exc), "at": utc_now()}
        Store(PRIVATE_ROOT / "control/state.sqlite").event({"event": "run_precondition_failure", **receipt})
    print(json.dumps(receipt, sort_keys=True, allow_nan=False), flush=True)
    return 0 if receipt["status"] in ("SUCCEEDED", "EXECUTED_UNVALIDATED") else 1


if __name__ == "__main__":
    sys.exit(main())
