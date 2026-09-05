#!/usr/bin/env python3
"""Failing-first tests for the exact one-launch isolation canary."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
WORKFLOW = HERE.parent
sys.path.insert(0, str(HERE))
from run import IMAGE, TIMEOUT_SECONDS, build_command, execute, validate_approval

RUNNER = HERE / "run.py"
TEMPLATE = json.loads((HERE / "approval-template.json").read_text())
POLICY = WORKFLOW / "historical_multihop/policies/isolation_canary.py"
RELEASED = WORKFLOW / "historical_multihop/released"


def runner_sha() -> str:
    return hashlib.sha256(RUNNER.read_bytes()).hexdigest()


def valid_approval() -> dict:
    approval = copy.deepcopy(TEMPLATE)
    approval.update({"status": "APPROVED", "approved_by": "user", "runner_sha256": runner_sha()})
    return approval


class IsolationCanaryV2Tests(unittest.TestCase):
    def test_unapproved_template_fails_closed(self) -> None:
        result = validate_approval(TEMPLATE, RUNNER)
        self.assertFalse(result["approved"])
        self.assertIn("STATUS", result["errors"])

    def test_exact_valid_approval_passes(self) -> None:
        self.assertTrue(validate_approval(valid_approval(), RUNNER)["approved"])

    def test_runner_hash_drift_fails(self) -> None:
        approval = valid_approval()
        approval["runner_sha256"] = "0" * 64
        result = validate_approval(approval, RUNNER)
        self.assertFalse(result["approved"])
        self.assertIn("RUNNER_IDENTITY", result["errors"])

    def test_command_has_fixed_security_and_resource_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command = build_command(POLICY, RELEASED, Path(temporary))
        joined = " ".join(command)
        for required in (
            "--pull never", "--network none", "--read-only", "--cap-drop ALL",
            "--security-opt no-new-privileges", "--pids-limit 64", "--memory 256m",
            "--cpus 1", "--user 501:20",
        ):
            self.assertIn(required, joined)
        self.assertIn(IMAGE, command)

    def test_mounts_expose_only_released_policy_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command = build_command(POLICY, RELEASED, Path(temporary))
        mounts = [command[index + 1] for index, item in enumerate(command) if item == "--mount"]
        self.assertEqual(len(mounts), 3)
        self.assertEqual({mount.split("dst=", 1)[1].split(",", 1)[0] for mount in mounts}, {"/task", "/policy.py", "/output"})
        self.assertFalse(any("withheld" in mount or "gold" in mount for mount in mounts))

    def test_timeout_is_exact(self) -> None:
        self.assertEqual(TIMEOUT_SECONDS, 30)
        self.assertEqual(valid_approval()["timeout_seconds"], 30)

    def test_timeout_is_fail_closed(self) -> None:
        with patch("run.subprocess.run", side_effect=subprocess.TimeoutExpired(["docker"], 30)):
            result = execute(["docker", "run"])
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["exit_code"], 124)


if __name__ == "__main__":
    unittest.main(verbosity=2)
