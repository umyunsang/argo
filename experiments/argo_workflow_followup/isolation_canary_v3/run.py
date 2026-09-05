#!/usr/bin/env python3
"""Approval-gated stdout-only isolation canary with no writable host bind."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

IMAGE = "python@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534"
IMAGE_ID = "sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534"
TIMEOUT_SECONDS = 30
CPUS = 1
MEMORY_MB = 256
PIDS = 64
HOST_USER = "501:20"
HERE = Path(__file__).resolve().parent
WORKFLOW = HERE.parent
POLICY = HERE / "policy_stdout.py"
RELEASED = WORKFLOW / "historical_multihop/released"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_approval(approval: dict, runner_path: Path, policy_path: Path) -> dict:
    checks = {
        "SCHEMA": approval.get("schema_version") == "argo-isolation-canary-v3-approval/v1",
        "STATUS": approval.get("status") == "APPROVED" and approval.get("approved_by") == "user",
        "SCOPE": approval.get("scope") == "exactly one zero-model stdout-only Docker isolation canary",
        "RUNNER_IDENTITY": approval.get("runner_path") == "experiments/argo_workflow_followup/isolation_canary_v3/run.py" and approval.get("runner_sha256") == sha(runner_path),
        "POLICY_IDENTITY": approval.get("policy_path") == "experiments/argo_workflow_followup/isolation_canary_v3/policy_stdout.py" and approval.get("policy_sha256") == sha(policy_path),
        "IMAGE": approval.get("image") == IMAGE,
        "COUNT": approval.get("attempts") == 1,
        "TIMEOUT": approval.get("timeout_seconds") == TIMEOUT_SECONDS,
        "RESOURCES": approval.get("cpus") == CPUS and approval.get("memory_mb") == MEMORY_MB and approval.get("pids") == PIDS,
        "NETWORK": approval.get("network") == "none",
        "MOUNTS": approval.get("host_bind_mounts") == 2 and approval.get("writable_host_bind_mounts") == 0,
        "ZERO_MODEL_COST": approval.get("model_calls") == 0 and approval.get("api_spend_usd") == 0.0,
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"approved": not errors, "checks": checks, "errors": errors}


def resolved(path: Path) -> str:
    return str(path.resolve(strict=True))


def build_command(policy_path: Path, released_dir: Path) -> list[str]:
    return [
        "docker", "run", "--rm", "--pull", "never",
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--pids-limit", str(PIDS),
        "--memory", f"{MEMORY_MB}m", "--cpus", str(CPUS), "--user", HOST_USER,
        "--ulimit", "nofile=64:64", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--env", "HOME=/tmp", "--env", "PYTHONDONTWRITEBYTECODE=1",
        "--env", "PYTHONHASHSEED=0", "--env", "LC_ALL=C.UTF-8", "--env", "TZ=UTC",
        "--workdir", "/tmp",
        "--mount", f"type=bind,src={resolved(released_dir)},dst=/task,readonly",
        "--mount", f"type=bind,src={resolved(policy_path)},dst=/policy.py,readonly",
        IMAGE, "python", "/policy.py",
    ]


def execute(command: list[str]) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=TIMEOUT_SECONDS)
        return {"exit_code": completed.returncode, "timed_out": False, "stdout": completed.stdout, "stderr": completed.stderr, "duration_seconds": round(time.monotonic() - started, 6)}
    except subprocess.TimeoutExpired as exc:
        return {"exit_code": 124, "timed_out": True, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "duration_seconds": round(time.monotonic() - started, 6)}


def parse_canary(run: dict) -> dict:
    if run.get("exit_code") != 0 or run.get("timed_out") or not run.get("stdout", "").strip():
        return {}
    try:
        value = json.loads(run["stdout"])
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    approval = json.loads(args.approval.read_text())
    approval_check = validate_approval(approval, Path(__file__).resolve(), POLICY)
    if not approval_check["approved"]:
        result = {"schema_version": "argo-isolation-canary-v3-result/v1", "status": "BLOCKED_BEFORE_DOCKER", "approval": approval_check, "docker_calls": 0, "container_launch_attempts": 0, "model_calls": 0, "api_spend_usd": 0.0}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    image = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], text=True, capture_output=True, check=False, timeout=TIMEOUT_SECONDS)
    run = execute(build_command(POLICY, RELEASED))
    canary = parse_canary(run)
    checks = {
        "image_identity": image.returncode == 0 and image.stdout.strip() == IMAGE_ID,
        "one_container_exit_zero": run["exit_code"] == 0 and not run["timed_out"],
        "released_case_readable": canary.get("released_case_readable") is True,
        "oracle_not_readable": canary.get("oracle_readable") is False,
        "forbidden_paths_blocked": bool(canary) and not any(canary.get("forbidden_path_readable", {}).values()),
        "external_network_blocked": canary.get("external_network_reachable") is False,
        "loopback_service_absent": canary.get("loopback_service_reachable") is False,
        "no_secret_environment": canary.get("secret_environment_keys") == [],
        "withheld_mount_absent": canary.get("withheld_mount_visible") is False,
    }
    result = {
        "schema_version": "argo-isolation-canary-v3-result/v1",
        "created_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "approval_sha256": sha(args.approval),
        "runner_sha256": sha(Path(__file__).resolve()),
        "policy_sha256": sha(POLICY),
        "image": IMAGE,
        "image_id": image.stdout.strip(),
        "docker_binary": shutil.which("docker"),
        "host": {"python": platform.python_version(), "uid": os.getuid(), "gid": os.getgid()},
        "attempts": 1,
        "host_bind_mounts": 2,
        "writable_host_bind_mounts": 0,
        "timeout_seconds": TIMEOUT_SECONDS,
        "run": run,
        "canary": canary,
        "checks": checks,
        "all_pass": all(checks.values()),
        "model_calls": 0,
        "api_spend_usd": 0.0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2, sort_keys=True))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
