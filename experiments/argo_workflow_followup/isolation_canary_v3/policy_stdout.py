#!/usr/bin/env python3
"""Emit the isolation canary result on stdout; write only inside no host mount."""
from __future__ import annotations

import json
import os
import socket
from pathlib import Path


def readable(path: str) -> bool:
    try:
        Path(path).read_bytes()
        return True
    except (OSError, PermissionError):
        return False


def connectable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


forbidden_paths = [
    "/withheld/gold.json",
    "/repo/experiments/argo_workflow_followup/historical_multihop/withheld/gold.json",
    "/task/../withheld/gold.json",
    "/proc/1/root/withheld/gold.json",
]
secret_tokens = ("ANTHROPIC", "OPENAI", "GITHUB_TOKEN", "AWS_", "AZURE_", "GOOGLE_API")
secret_environment = sorted(key for key in os.environ if any(token in key.upper() for token in secret_tokens))
try:
    mountinfo = Path("/proc/self/mountinfo").read_text()
except OSError:
    mountinfo = ""
result = {
    "released_case_readable": readable("/task/case.json"),
    "forbidden_path_readable": {path: readable(path) for path in forbidden_paths},
    "oracle_readable": any(readable(path) for path in forbidden_paths),
    "external_network_reachable": connectable("1.1.1.1", 53),
    "loopback_service_reachable": connectable("127.0.0.1", 9),
    "secret_environment_keys": secret_environment,
    "withheld_mount_visible": "/withheld" in mountinfo or "historical_multihop/withheld" in mountinfo,
    "root_entries": sorted(path.name for path in Path("/").iterdir()),
    "open_fds": sorted(path.name for path in Path("/proc/self/fd").iterdir()),
}
print(json.dumps(result, sort_keys=True))
