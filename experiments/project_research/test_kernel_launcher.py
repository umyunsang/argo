"""Kernel boundary/config tests; no real Docker or scientific compute."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from experiments.project_research import kernel_launcher as kernel


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.workspace = self.root / "team" / "workspace"
        self.artifacts = self.root / "team" / "artifacts"
        self.control = self.root / "control" / "team"
        for path in (self.workspace, self.artifacts, self.control):
            path.mkdir(parents=True)
        self.path = self.control / "config.json"
        self.value = {"campaign_id": "fixture", "workspace": str(self.workspace), "artifact_root": str(self.artifacts), "control_dir": str(self.control), "image": "sha256:" + "a" * 64, "deadline_epoch": time.time() + 120}
        self.path.write_text(json.dumps(self.value))
        self.root_patch = patch.object(kernel, "PRIVATE_ROOT", self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.temporary.cleanup()

    def test_command_has_only_two_binds_and_exact_resource_flags(self):
        config = kernel.load_config(str(self.path))
        args = kernel.command(config, "fixture", ["-m", "rlm.repl"], {})
        mounts = [args[i + 1] for i, value in enumerate(args) if value == "--mount"]
        self.assertEqual(len(mounts), 2)
        self.assertTrue(all(str(self.control) not in value for value in mounts))
        for option, value in (("--network", "none"), ("--cpus", "0.5"), ("--memory", "536870912"), ("--cap-drop", "ALL")):
            self.assertEqual(args[args.index(option) + 1], value)
        self.assertIn("--read-only", args)

    def test_reject_symlink_special_or_hidden_control(self):
        (self.workspace / "link").symlink_to(self.control)
        with self.assertRaises(ValueError):
            kernel.load_config(str(self.path))
        (self.workspace / "link").unlink()
        (self.workspace / "control").mkdir()
        with self.assertRaises(ValueError):
            kernel.load_config(str(self.path))

    def test_reject_state_escape_or_non_native_entrypoint(self):
        config = kernel.load_config(str(self.path))
        with self.assertRaises(ValueError):
            kernel.command(config, "fixture", ["-m", "rlm.repl"], {"RLM_SESSION_DIR": str(self.control)})
        with self.assertRaises(ValueError):
            kernel.command(config, "fixture", ["script.py"], {})

    def test_reject_nonfinite_or_expired_limits(self):
        for field, value in (("deadline_epoch", time.time() - 1), ("kernel_cpus", 4), ("kernel_lease_seconds", float("inf"))):
            with self.subTest(field=field):
                self.path.write_text(json.dumps({**self.value, field: value}))
                with self.assertRaises(ValueError):
                    kernel.load_config(str(self.path))

    def test_unknown_container_keeps_usage_unknown(self):
        config = kernel.load_config(str(self.path))
        record = {"lease_id": "kernel-fixture", "container": "fixture", "started_at": time.time(), "reserved_seconds": 60}
        with patch.object(kernel, "Store") as store:
            kernel.settle(config, record, False, "cleanup_unknown")
            self.assertIsNone(store.return_value.settle_compute.call_args.args[1])
            self.assertFalse(store.return_value.settle_compute.call_args.args[2]["container_absent"])


if __name__ == "__main__":
    unittest.main()
