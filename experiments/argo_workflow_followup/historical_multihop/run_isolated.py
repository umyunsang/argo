#!/usr/bin/env python3
"""Run one historical multi-hop pipeline falsifier in an isolated container."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKFLOW = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WORKFLOW))

from decision_sufficiency import evaluate
from historical_multihop import verify_sources

IMAGE = "python@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534"
IMAGE_ID = "sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolved_mount(path: Path) -> str:
    """Return the daemon-visible physical path and fail before Docker if absent."""
    return str(path.resolve(strict=True))


def build_command(policy: Path, output_dir: Path) -> list[str]:
    return [
        "docker", "run", "--rm", "--pull", "never",
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--pids-limit", "64",
        "--memory", "256m", "--cpus", "1", "--user", "65534:65534",
        "--ulimit", "nofile=64:64",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--env", "HOME=/tmp", "--env", "PYTHONDONTWRITEBYTECODE=1",
        "--env", "PYTHONHASHSEED=0", "--env", "LC_ALL=C.UTF-8",
        "--env", "TZ=UTC", "--workdir", "/tmp",
        "--mount", f"type=bind,src={resolved_mount(HERE / 'released')},dst=/task,readonly",
        "--mount", f"type=bind,src={resolved_mount(policy)},dst=/policy.py,readonly",
        "--mount", f"type=bind,src={resolved_mount(output_dir)},dst=/output",
        IMAGE, "python", "/policy.py", "/task/case.json", "/output/response.json",
    ]


def run_policy(policy: Path, output_dir: Path) -> dict:
    output_dir.chmod(0o777)
    command = build_command(policy, output_dir)
    started = time.monotonic()
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    output = output_dir / "response.json"
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "duration_seconds": round(time.monotonic() - started, 6),
        "output_path": output,
        "output_exists": output.is_file(),
    }


def sanitized_command(command: list[str]) -> list[str]:
    return [
        item.replace(str(ROOT), "<REPO>").replace(str(Path(tempfile.gettempdir())), "<TMP>")
        for item in command
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    case_path = HERE / "released/case.json"
    gold_path = HERE / "withheld/gold.json"
    reference_policy = HERE / "policies/reference_policy.py"
    canary_policy = HERE / "policies/isolation_canary.py"
    case = json.loads(case_path.read_text())
    gold = json.loads(gold_path.read_text())

    inspect = subprocess.run(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
        text=True, capture_output=True, check=False,
    )
    source_verification = verify_sources(gold, ROOT)
    with tempfile.TemporaryDirectory(prefix="argo-multihop-") as temporary:
        temp = Path(temporary)
        reference_runs = []
        for index in range(2):
            output_dir = temp / f"reference-{index}"
            output_dir.mkdir()
            run = run_policy(reference_policy, output_dir)
            response = json.loads(run["output_path"].read_text()) if run["output_exists"] else {}
            route = response.pop("recheck_decision_ids", [])
            score = evaluate(
                gold,
                response,
                route,
                task_outcome=source_verification["all_pass"] and gold["task_outcome"],
            )
            reference_runs.append(
                {
                    "exit_code": run["exit_code"],
                    "duration_seconds": run["duration_seconds"],
                    "stdout": run["stdout"],
                    "stderr": run["stderr"],
                    "stdout_sha256": hashlib.sha256(run["stdout"].encode()).hexdigest(),
                    "stderr_sha256": hashlib.sha256(run["stderr"].encode()).hexdigest(),
                    "output_sha256": sha256(run["output_path"]) if run["output_exists"] else None,
                    "command": sanitized_command(run["command"]),
                    "score": score,
                }
            )

        canary_dir = temp / "canary"
        canary_dir.mkdir()
        canary_run = run_policy(canary_policy, canary_dir)
        canary = json.loads(canary_run["output_path"].read_text()) if canary_run["output_exists"] else {}

    canary_checks = {
        "container_exit_zero": canary_run["exit_code"] == 0,
        "released_case_readable": canary.get("released_case_readable") is True,
        "oracle_not_readable": canary.get("oracle_readable") is False,
        "every_forbidden_path_blocked": not any(canary.get("forbidden_path_readable", {}).values()),
        "external_network_blocked": canary.get("external_network_reachable") is False,
        "loopback_service_absent": canary.get("loopback_service_reachable") is False,
        "no_secret_environment": canary.get("secret_environment_keys") == [],
        "withheld_mount_absent": canary.get("withheld_mount_visible") is False,
    }
    reference_outputs = [run["output_sha256"] for run in reference_runs]
    reference_checks = {
        "image_identity": inspect.returncode == 0 and inspect.stdout.strip() == IMAGE_ID,
        "both_exits_zero": all(run["exit_code"] == 0 for run in reference_runs),
        "outputs_exact_across_replays": len(set(reference_outputs)) == 1 and None not in reference_outputs,
        "both_scores_pass": all(run["score"]["overall_verdict"] == "PASS" for run in reference_runs),
        "both_pipeline_success": all(run["score"]["confirmatory_success"] for run in reference_runs),
        "source_gold_rederived": source_verification["all_pass"],
    }
    docker_path = Path(shutil.which("docker") or "")
    result = {
        "schema_version": "argo-historical-multihop-isolation/v1",
        "created_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "case": str(case_path.relative_to(ROOT)),
        "case_sha256": sha256(case_path),
        "gold": str(gold_path.relative_to(ROOT)),
        "gold_sha256": sha256(gold_path),
        "image": IMAGE,
        "image_id": inspect.stdout.strip(),
        "docker_binary": str(docker_path),
        "docker_binary_sha256": sha256(docker_path) if docker_path.is_file() else None,
        "host_python": platform.python_version(),
        "source_verification": source_verification,
        "reference_runs": reference_runs,
        "reference_checks": reference_checks,
        "canary": canary,
        "canary_run": {
            "exit_code": canary_run["exit_code"],
            "stdout": canary_run["stdout"],
            "stderr": canary_run["stderr"],
            "command": sanitized_command(canary_run["command"]),
        },
        "canary_checks": canary_checks,
        "all_pass": all(reference_checks.values()) and all(canary_checks.values()),
        "scope": "one historical multi-hop pipeline falsifier; not policy efficacy or an independent task population",
        "model_calls": 0,
        "spend_usd": 0.0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "all_pass": result["all_pass"],
        "reference_checks": reference_checks,
        "canary_checks": canary_checks,
        "model_calls": 0,
        "spend_usd": 0.0,
    }, indent=2, sort_keys=True))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
