"""Synthetic qualification only. Set ARGO_KERNEL_TEST_IMAGE to an image ID."""
from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

import kernel_wrapper as wrapper


IMAGE = os.environ.get("ARGO_KERNEL_TEST_IMAGE", "sha256:" + "0" * 64)


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        parent = wrapper.STUDY_ROOT / "qualification"
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-", dir=parent)
        self.episode = Path(self.temporary.name)
        for name in ("workspace", "artifacts", "control"):
            (self.episode / name).mkdir(mode=0o700)
        self.raw = {"image": IMAGE, "workspace": str(self.episode / "workspace"),
                    "artifact_root": str(self.episode / "artifacts"),
                    "control_dir": str(self.episode / "control"),
                    "deadline_epoch": time.time() + 180, "max_cpu_seconds": 600}
        self.config_path = self.episode / "control/kernel.json"
        self.write_config()
        self.cfg = wrapper.load_config(self.config_path)

    def write_config(self) -> None:
        self.config_path.write_text(json.dumps(self.raw))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def environment(self) -> dict[str, str]:
        return {**os.environ, "ARGO_KERNEL_CONFIG": str(self.config_path),
                "RLM_SESSION_DIR": str(self.cfg.artifact_root / "session-a"),
                "RLM_HARNESS_STATE_DIR": str(self.cfg.artifact_root / "session-a/harness"),
                "RLM_GLOBAL_HARNESS_STATE_DIR": str(Path.home() / ".prime/agent/harness"),
                "ARGO_SECRET_PROBE": "synthetic-not-a-credential"}

    def pool(self) -> dict:
        return json.loads((self.cfg.control_dir / "resource-pool.json").read_text())


class PathAndBudgetTests(Fixture):
    def test_path_escape_and_unknown_config_are_rejected(self) -> None:
        for changed in ({"workspace": str(Path.home())}, {"extra_mounts": [str(Path.home())]},
                        {"image": "argo-study-kernel:20260909"}, {"episode_cpus": 3},
                        {"episode_memory_bytes": 9 * wrapper.GIB}, {"kernel_cpus": float("nan")}):
            with self.subTest(changed=changed):
                original = dict(self.raw)
                self.raw.update(changed)
                self.write_config()
                with self.assertRaises((ValueError, TypeError)):
                    wrapper.load_config(self.config_path)
                self.raw = original

    def test_mount_symlink_hardlink_and_hidden_label_rejected(self) -> None:
        sentinel = self.cfg.control_dir / "private.txt"
        sentinel.write_text("synthetic")
        target = self.cfg.workspace / "alias"
        target.symlink_to(sentinel)
        with self.assertRaises(ValueError):
            wrapper.validate_mount_tree(self.cfg.workspace)
        target.unlink()
        os.link(sentinel, target)
        with self.assertRaises(ValueError):
            wrapper.validate_mount_tree(self.cfg.workspace)
        target.unlink()
        (self.cfg.workspace / "dev_y.csv").write_text("synthetic")
        with self.assertRaises(ValueError):
            wrapper.validate_mount_tree(self.cfg.workspace)

    def test_only_two_mounts_allowlisted_environment(self) -> None:
        command = wrapper.docker_command(self.cfg, "synthetic-name", ["-m", "rlm.repl"], self.environment())
        self.assertEqual(command.count("--mount"), 2)
        self.assertNotIn("synthetic-not-a-credential", " ".join(command))
        self.assertNotIn(str(Path.home() / ".prime/agent/harness"), " ".join(command))
        with self.assertRaises(ValueError):
            wrapper.docker_command(self.cfg, "synthetic-name", ["-m", "rlm.repl"],
                                   {"RLM_SESSION_DIR": str(self.cfg.control_dir)})
        with self.assertRaises(ValueError):
            wrapper.docker_command(self.cfg, "synthetic-name", ["some.py"], {})

    def test_kernel_and_fit_share_cpu_memory_and_charge(self) -> None:
        kernel = wrapper.reserve_resources(self.cfg, "kernel", 0.5, 512 * 1024**2, kind="kernel")
        fit = wrapper.reserve_resources(self.cfg, "fit", 1.5, 4 * wrapper.GIB)
        with self.assertRaisesRegex(RuntimeError, "CPU"):
            wrapper.reserve_resources(self.cfg, "over", 0.1, 1)
        wrapper.release_resources(self.cfg, fit, measured_cpu_seconds=0.01)
        with self.assertRaisesRegex(RuntimeError, "memory"):
            wrapper.reserve_resources(self.cfg, "big", 0.5, 8 * wrapper.GIB)
        wrapper.release_resources(self.cfg, kernel)
        self.assertEqual(self.pool()["active"], {})
        self.assertGreater(self.pool()["conservative_cpu_seconds"], 0)
        self.assertEqual(self.pool()["completed"][0]["measured_cpu_seconds"], 0.01)

    def test_idle_kernels_are_not_training_jobs(self) -> None:
        leases = [wrapper.reserve_resources(self.cfg, f"kernel-{i}", 0.25, 128 * 1024**2, kind="kernel")
                  for i in range(3)]
        leases += [wrapper.reserve_resources(self.cfg, f"fit-{i}", 0.25, 128 * 1024**2) for i in range(2)]
        with self.assertRaisesRegex(RuntimeError, "two scientific"):
            wrapper.reserve_resources(self.cfg, "fit-2", 0.25, 128 * 1024**2)
        for lease in leases:
            wrapper.release_resources(self.cfg, lease)

    def test_deadline_and_cpu_time_are_shared(self) -> None:
        cfg = dataclasses.replace(self.cfg, deadline_epoch=time.time() - 1)
        with self.assertRaisesRegex(RuntimeError, "deadline"):
            wrapper.reserve_resources(cfg, "late", 0.5, 1)
        cfg = dataclasses.replace(self.cfg, max_cpu_seconds=0.01)
        lease = wrapper.reserve_resources(cfg, "brief", 0.5, 1)
        time.sleep(0.03)
        self.assertEqual(wrapper.remaining_seconds(cfg), 0)
        self.assertEqual(wrapper.remaining_cpu_seconds(cfg), 0)
        with self.assertRaisesRegex(RuntimeError, "allowance"):
            wrapper.reserve_resources(cfg, "later", 0.5, 1)
        wrapper.release_resources(cfg, lease)


class NativeProcess:
    def __init__(self, fixture: Fixture) -> None:
        self.process = subprocess.Popen([str(Path(wrapper.__file__).resolve()), "-m", "rlm.repl"],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, env=fixture.environment(),
                                        start_new_session=True)
        self.events: queue.Queue[str | None] = queue.Queue()
        def read() -> None:
            for line in self.process.stdout:
                self.events.put(line)
            self.events.put(None)
        threading.Thread(target=read, daemon=True).start()

    def read(self, timeout: float = 30) -> dict:
        line = self.events.get(timeout=timeout)
        if line is None:
            raise EOFError("native protocol closed")
        return json.loads(line)

    def send(self, request: dict) -> None:
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

    def done(self, request_id: str) -> list[dict]:
        events = []
        while True:
            event = self.read()
            events.append(event)
            if event.get("event") == "done" and event.get("id") == request_id:
                return events

    def execute(self, code: str, request_id: str = "cell") -> list[dict]:
        self.send({"type": "execute", "id": request_id, "code": code})
        return self.done(request_id)

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=20)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()


@unittest.skipUnless("ARGO_KERNEL_TEST_IMAGE" in os.environ, "explicit immutable test image required")
class NativeContainerTests(Fixture):
    def start(self) -> NativeProcess:
        native = NativeProcess(self)
        self.addCleanup(native.close)
        self.assertEqual(native.read()["protocol"], 3)
        return native

    def assert_cleaned(self, timeout: float = 15) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.pool()["active"]:
                break
            time.sleep(0.2)
        self.assertFalse(self.pool()["active"], self.pool())
        for record in self.cfg.control_dir.glob("argo-kernel-*.json"):
            obj = json.loads(record.read_text())
            if "container" in obj:
                result = subprocess.run([self.cfg.docker, "container", "ls", "--all", "--quiet",
                                         "--filter", f"name=^/{obj['container']}$"],
                                        capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), "")

    def test_import_check_and_mount_boundary(self) -> None:
        private = self.cfg.control_dir / "private.txt"
        private.write_text("synthetic")
        code = ("import os,pathlib,rlm,rlm.repl,dill,requests,httpx,yaml,tomli,dotenv,pandas,numpy,scipy,bs4,lxml,pydantic,tyro,sklearn; "
                "assert rlm.repl.PROTOCOL_VERSION==3; assert callable(rlm.run); "
                "assert callable(rlm.harness.create_memory); assert sklearn.__version__=='1.6.1'; "
                "assert pandas.__version__=='2.2.3'; assert os.getuid()!=0; "
                "assert 'ARGO_SECRET_PROBE' not in os.environ; "
                f"assert not pathlib.Path({str(private)!r}).exists(); "
                "assert not pathlib.Path('/var/run/docker.sock').exists(); "
                "assert 'CapEff:\\t0000000000000000' in pathlib.Path('/proc/self/status').read_text(); "
                "pathlib.Path('synthetic-output.txt').write_text('ok'); print('IMPORT_BOUNDARY_OK')")
        result = subprocess.run([str(Path(wrapper.__file__).resolve()), "-c", code],
                                capture_output=True, text=True, env=self.environment(), timeout=40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "IMPORT_BOUNDARY_OK")
        self.assertTrue((self.cfg.workspace / "synthetic-output.txt").exists())
        self.assert_cleaned()

    def test_native_protocol_persistence_bridge_and_snapshot(self) -> None:
        native = self.start()
        name = next(iter(self.pool()["active"].values()))["name"]
        inspected = json.loads(subprocess.run([self.cfg.docker, "inspect", name], capture_output=True,
                                              text=True, check=True).stdout)[0]
        self.assertEqual({item["Source"] for item in inspected["Mounts"]},
                         {str(self.cfg.workspace), str(self.cfg.artifact_root)})
        constraints = inspected["HostConfig"]
        self.assertEqual(constraints["NetworkMode"], "none")
        self.assertTrue(constraints["ReadonlyRootfs"])
        self.assertEqual(constraints["NanoCpus"], 500000000)
        self.assertEqual(constraints["Memory"], 512 * 1024**2)
        self.assertEqual(constraints["MemorySwap"], 512 * 1024**2)
        self.assertEqual(constraints["PidsLimit"], 128)
        self.assertIn("ALL", constraints["CapDrop"])
        self.assertIn("no-new-privileges", constraints["SecurityOpt"])
        network = native.execute("import socket\ns=socket.socket()\ns.settimeout(1)\nassert s.connect_ex(('1.1.1.1', 443)) != 0\ns.close()")
        self.assertEqual(network[-1]["status"], "ok")
        self.assertEqual(native.execute("x=40\nx+2")[-2]["text"], "42")
        self.assertEqual(native.execute("x+3")[-2]["text"], "43")
        native.send({"type": "execute", "id": "host", "code": "import rlm\nawait rlm.host_request('synthetic.ping', {'x': x})"})
        event = native.read()
        self.assertEqual(event["event"], "host_request")
        self.assertEqual(event["data"], {"type": "synthetic.ping", "x": 40})
        native.send({"type": "host_reply", "id": event["id"], "data": {"status": "ok", "result": {"pong": 42}}})
        self.assertEqual(native.done("host")[-1]["status"], "ok")
        snapshot = self.cfg.artifact_root / "synthetic.pkl"
        native.send({"type": "snapshot", "id": "save", "path": str(snapshot), "manifest_path": str(snapshot)+".json"})
        self.assertIn("x", native.done("save")[-1]["saved"])
        native.send({"type": "shutdown", "id": "shutdown"})
        self.assertEqual(native.done("shutdown")[-1]["status"], "ok")
        self.assertEqual(native.process.wait(timeout=20), 0)
        restored = self.start()
        restored.send({"type": "restore", "id": "restore", "path": str(snapshot)})
        self.assertIn("x", restored.done("restore")[-1]["restored"])
        self.assertEqual(restored.execute("x+4")[-2]["text"], "44")
        restored.send({"type": "shutdown", "id": "stop"})
        restored.done("stop")
        restored.process.wait(timeout=20)
        self.assert_cleaned()

    def test_native_interrupt_then_continue(self) -> None:
        native = self.start()
        native.send({"type": "execute", "id": "loop", "code": "import asyncio\nawait asyncio.sleep(999)"})
        native.send({"type": "interrupt", "id": "loop"})
        events = native.done("loop")
        self.assertTrue(any(event.get("ename") == "KeyboardInterrupt" for event in events))
        self.assertEqual(native.execute("6*7")[-2]["text"], "42")
        native.process.terminate()
        native.process.wait(timeout=20)
        self.assert_cleaned()

    def test_wrapper_sigkill_and_process_group_sigkill_cleanup(self) -> None:
        for kill_group in (False, True):
            with self.subTest(kill_group=kill_group):
                native = self.start()
                native.send({"type": "execute", "id": "loop", "code": "import time\nwhile True:\n time.sleep(0.1)"})
                if kill_group:
                    os.killpg(native.process.pid, signal.SIGKILL)
                else:
                    native.process.kill()
                native.process.wait(timeout=10)
                self.assert_cleaned()

    def test_absolute_deadline_stops_native_container(self) -> None:
        self.raw["deadline_epoch"] = time.time() + 4
        self.write_config()
        native = self.start()
        native.process.wait(timeout=15)
        self.assertIn(native.process.returncode, (124, 143))
        self.assert_cleaned()


if __name__ == "__main__":
    unittest.main(verbosity=2)
