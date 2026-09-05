#!/usr/bin/env python3
"""Pure command-construction tests; these do not launch Docker."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_isolated import IMAGE, build_command, resolved_mount


class IsolationCommandTests(unittest.TestCase):
    def test_temp_mount_uses_existing_physical_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="argo-mount-") as temporary:
            logical = Path(temporary)
            physical = Path(resolved_mount(logical))
            self.assertTrue(physical.is_absolute())
            self.assertTrue(physical.is_dir())
            command = build_command(HERE / "policies/reference_policy.py", logical)
            mounts = [command[index + 1] for index, item in enumerate(command) if item == "--mount"]
            self.assertIn(f"type=bind,src={physical},dst=/output", mounts)

    def test_only_released_policy_and_output_are_mounted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="argo-mount-") as temporary:
            command = build_command(
                HERE / "policies/reference_policy.py", Path(temporary)
            )
            mounts = [command[index + 1] for index, item in enumerate(command) if item == "--mount"]
            self.assertEqual(len(mounts), 3)
            self.assertEqual(
                {mount.split("dst=", 1)[1].split(",", 1)[0] for mount in mounts},
                {"/task", "/policy.py", "/output"},
            )
            self.assertFalse(any("withheld" in mount for mount in mounts))

    def test_security_flags_and_image_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="argo-mount-") as temporary:
            command = build_command(
                HERE / "policies/reference_policy.py", Path(temporary)
            )
            joined = " ".join(command)
            for required in (
                "--network none",
                "--read-only",
                "--cap-drop ALL",
                "--security-opt no-new-privileges",
                "--pull never",
                "--user 65534:65534",
            ):
                self.assertIn(required, joined)
            self.assertIn(IMAGE, command)

    def test_missing_mount_fails_before_docker(self) -> None:
        with self.assertRaises(FileNotFoundError):
            resolved_mount(HERE / "does-not-exist")


if __name__ == "__main__":
    unittest.main(verbosity=2)
