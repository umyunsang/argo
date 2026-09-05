#!/usr/bin/env python3
"""Validate the consumed one-attempt isolation-canary v2 closure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path, root: Path) -> dict:
    root = Path(root)
    obj = json.loads(Path(path).read_text())
    errors: list[str] = []
    bindings = [
        ("PROPOSAL", "proposal", "proposal_sha256"),
        ("RUNNER", "runner", "runner_sha256"),
        ("APPROVED_AUTH", "approved_authorization", "approved_authorization_sha256"),
        ("CONSUMED_AUTH", "consumed_authorization", "consumed_authorization_sha256"),
        ("RESULT", "result", "result_sha256"),
    ]
    loaded = {}
    for name, path_key, hash_key in bindings:
        source = root / obj.get(path_key, "")
        if not source.is_file() or sha(source) != obj.get(hash_key):
            errors.append(f"IDENTITY:{name}")
        elif source.suffix == ".json":
            loaded[name] = json.loads(source.read_text())
    approved = loaded.get("APPROVED_AUTH", {})
    consumed = loaded.get("CONSUMED_AUTH", {})
    result = loaded.get("RESULT", {})
    if approved.get("status") != "APPROVED" or approved.get("approved_by") != "user" or approved.get("approval_message") != "zero-model Docker canary 1회 실행을 승인":
        errors.append("APPROVAL_AUTHORITY")
    if result.get("approval_sha256") != obj.get("approved_authorization_sha256"):
        errors.append("APPROVAL_RESULT_BINDING")
    if consumed.get("status") != "CONSUMED_FAIL_PRELAUNCH" or consumed.get("remaining_attempts") != 0 or consumed.get("retry_authorized") is not False:
        errors.append("CONSUMED_STATE")
    execution = obj.get("execution", {})
    expected_execution = {
        "docker_cli_invocations": 2,
        "image_inspections": 1,
        "container_launch_attempts": 1,
        "containers_started": 0,
        "policy_episodes": 0,
        "exit_code": 125,
        "timed_out": False,
    }
    for key, value in expected_execution.items():
        if execution.get(key) != value:
            errors.append(f"EXECUTION:{key}")
    if "invalid mount config" not in execution.get("stderr", "") or "/private/var/folders/" not in execution.get("stderr", ""):
        errors.append("PRELAUNCH_STDERR")
    if result:
        if result.get("attempts") != 1 or result.get("canary") != {} or result.get("run", {}).get("exit_code") != 125:
            errors.append("RAW_RESULT")
        if result.get("checks", {}).get("image_identity") is not True:
            errors.append("IMAGE_IDENTITY")
        if result.get("model_calls") != 0 or result.get("api_spend_usd") != 0.0:
            errors.append("RAW_EXECUTION_SCOPE")
    expected_checks = {"image_identity": "PASS", **{key: "NOT_OBSERVED" for key in ["forbidden_paths_blocked", "external_network_blocked", "loopback_service_absent", "no_secret_environment", "oracle_not_readable", "released_case_readable", "withheld_mount_absent"]}}
    if obj.get("observed_checks") != expected_checks:
        errors.append("OBSERVED_CHECK_SEMANTICS")
    authorization = obj.get("authorization", {})
    if authorization.get("attempts_consumed") != 1 or authorization.get("remaining_attempts") != 0 or authorization.get("retry_authorized") is not False:
        errors.append("RETRY_BOUNDARY")
    if obj.get("diagnosis", {}).get("code") != "OUTPUT_BIND_PATH_NOT_VISIBLE_TO_DOCKER_DAEMON":
        errors.append("DIAGNOSIS")
    required_limits = {"OS isolation failure", "OS isolation success", "policy episode", "task outcome", "model execution", "permission to retry"}
    if not required_limits.issubset(set(obj.get("not_claimed", []))):
        errors.append("LIMITS")
    if obj.get("status") != "CLOSED_FAIL_PRELAUNCH_NO_RETRY" or obj.get("model_calls") != 0 or obj.get("spend_usd") != 0.0:
        errors.append("CLOSURE_SCOPE")
    return {"passed": not errors, "errors": errors, "status": obj.get("status"), "attempts_remaining": authorization.get("remaining_attempts")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = validate(args.closure, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
