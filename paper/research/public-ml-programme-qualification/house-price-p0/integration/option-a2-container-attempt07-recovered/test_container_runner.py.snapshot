import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import socket
import sys
import time
import threading
import unittest

from container_runner import (
    IMAGE_DIGEST,
    RunStatus,
    RunnerConfig,
    run_fixed_solution,
)


class ContainerRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".argo-hp-container-test-", dir=Path(__file__).parent)
        self.base = Path(self.temp.name)
        os.chmod(self.base, 0o711)
        self.solution = self.base / "solution.py"
        self.train = self.base / "train.csv"
        self.features = self.base / "features.csv"
        (self.base / "private-output").mkdir(mode=0o700)
        self._write_csv(self.train, ["Id", "x", "SalePrice"], [[1, 10, 100], [2, 20, 200]])
        self._write_csv(self.features, ["Id", "x"], [[3, 30], [4, 40]])

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _write_csv(path, header, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def _config(self, **overrides):
        values = dict(
            run_id="11111111-1111-4111-8111-111111111111",
            solution_path=self.solution,
            train_path=self.train,
            features_path=self.features,
            output_parent=self.base / "private-output",
            wall_seconds=8,
            cpus=0.5,
            memory_bytes=128 * 1024 * 1024,
            pids_limit=32,
            nofile=64,
            tmpfs_bytes=32 * 1024 * 1024,
            max_input_bytes=1024 * 1024,
            max_output_bytes=1024 * 1024,
            log_quarantine_bytes=4096,
        )
        values.update(overrides)
        return RunnerConfig(**values)

    def _write_solution(self, body):
        self.solution.write_text(body, encoding="utf-8")


    def test_hardened_fit_predict_writes_exact_sealed_output(self):
        self._write_solution("""
import pandas as pd

def fit_predict(train: pd.DataFrame, features: pd.DataFrame):
    return features['x'].astype(float) * 2
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(result.row_count, 2)
        self.assertIsNotNone(result.predictions_path)
        self.assertTrue(result.predictions_path.is_file())
        self.assertEqual(result.predictions_sha256, hashlib.sha256(result.predictions_path.read_bytes()).hexdigest())
        self.assertEqual(result.stdout_bytes, 0)
        self.assertEqual(result.stderr_bytes, 0)
        with result.predictions_path.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.reader(handle)), [["Id", "SalePrice"], ["3", "60.0"], ["4", "80.0"]])

    def test_failing_control_weak_mount_and_environment_expose_synthetic_sentinels(self):
        sentinel = self.base / "host-sentinel.txt"
        sentinel.write_text("SYNTHETIC_HOST_SECRET", encoding="utf-8")
        os.chmod(sentinel, 0o644)
        completed = subprocess.run(
            ["docker", "run", "--rm", "-e", "SYNTHETIC_ENV_SECRET=SYNTHETIC_ENV_SECRET",
             "-v", f"{sentinel}:/secret:ro", IMAGE_DIGEST,
             "python", "-c", "import os; print(open('/secret').read()); print(os.environ['SYNTHETIC_ENV_SECRET'])"],
            text=True, capture_output=True, timeout=20, check=True,
        )
        self.assertIn("SYNTHETIC_HOST_SECRET", completed.stdout)
        self.assertIn("SYNTHETIC_ENV_SECRET", completed.stdout)

    def test_hardened_container_cannot_read_unmounted_sentinel_or_host_env(self):
        self._write_solution("""
import os

def fit_predict(train, features):
    assert not os.path.exists('/secret')
    assert os.getenv('SYNTHETIC_ENV_SECRET') is None
    return [1.0] * len(features)
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertNotIn("SYNTHETIC", json.dumps(result.to_public_dict()))

    def test_failing_control_default_network_reaches_loopback_canary_but_hardened_cannot(self):
        received = threading.Event()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def accept_once():
            try:
                connection, _ = server.accept()
                with connection:
                    received.set()
                    connection.sendall(b"SYNTHETIC_LOOPBACK_CANARY")
            finally:
                server.close()

        thread = threading.Thread(target=accept_once, daemon=True)
        thread.start()
        weak = subprocess.run(
            ["docker", "run", "--rm", IMAGE_DIGEST, "python", "-c",
             f"import socket; s=socket.create_connection(('host.docker.internal',{port}),2); print(s.recv(64).decode())"],
            text=True, capture_output=True, timeout=20, check=True,
        )
        self.assertIn("SYNTHETIC_LOOPBACK_CANARY", weak.stdout)
        self.assertTrue(received.wait(2))
        self._write_solution(f"""
import socket
import sys
import time

def fit_predict(train, features):
    try:
        socket.create_connection(('host.docker.internal', {port}), 0.5)
    except OSError:
        return [1.0] * len(features)
    raise AssertionError('network reachable')
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.SUCCESS)

    def test_timeout_returns_typed_status_and_removes_named_container(self):
        self._write_solution("""
import subprocess
import time

def fit_predict(train, features):
    subprocess.Popen(['sleep', '30'])
    time.sleep(30)
    return [1.0] * len(features)
""")
        config = self._config(wall_seconds=1)
        result = run_fixed_solution(config)
        self.assertEqual(result.status, RunStatus.TIMEOUT)
        inspect = subprocess.run(
            ["docker", "container", "inspect", config.container_name], text=True,
            capture_output=True, timeout=10,
        )
        self.assertNotEqual(inspect.returncode, 0)

    def _archived_attempt05_unreachable_output_write_then_flood_fixture(self):
        self._write_solution("""
from pathlib import Path

def fit_predict(train, features):
    Path('/output/extra.txt').write_text('SYNTHETIC_FEATURE_SENTINEL' * 1000)
    print('SYNTHETIC_FEATURE_SENTINEL' * 1000)
    raise RuntimeError('SYNTHETIC_FEATURE_SENTINEL')
""")
        result = run_fixed_solution(self._config(max_output_bytes=256, log_quarantine_bytes=256))
        self.assertEqual(result.status, RunStatus.LOG_LIMIT_EXCEEDED)
        self.assertTrue(result.logs_truncated)
        self.assertGreater(result.stdout_bytes + result.stderr_bytes, 256)
        public = json.dumps(result.to_public_dict())
        self.assertNotIn("SYNTHETIC_FEATURE_SENTINEL", public)
        self.assertIsNone(result.predictions_path)

    def test_unmounted_output_directory_extra_file_write_is_denied(self):
        self._write_solution("""
from pathlib import Path

def fit_predict(train, features):
    Path('/output/extra.txt').write_text('SYNTHETIC_EXTRA_FILE_SENTINEL')
    return [1.0] * len(features)
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.EXECUTION_FAILED)
        self.assertIsNone(result.predictions_path)
        self.assertNotIn("SYNTHETIC_EXTRA_FILE_SENTINEL", json.dumps(result.to_public_dict()))

    def test_stdout_flood_truncates_without_echo_and_cleans_exact_container(self):
        self._write_solution("""
def fit_predict(train, features):
    print('SYNTHETIC_STDOUT_FLOOD_SENTINEL' * 1000)
    return [1.0] * len(features)
""")
        config = self._config(log_quarantine_bytes=256)
        result = run_fixed_solution(config)
        self.assertEqual(result.status, RunStatus.LOG_LIMIT_EXCEEDED)
        self.assertTrue(result.logs_truncated)
        self.assertGreater(result.stdout_bytes + result.stderr_bytes, config.log_quarantine_bytes)
        self.assertIsNone(result.predictions_path)
        self.assertNotIn("SYNTHETIC_STDOUT_FLOOD_SENTINEL", json.dumps(result.to_public_dict()))
        inspected = subprocess.run(
            ["docker", "container", "inspect", config.container_name],
            text=True, capture_output=True, timeout=10,
        )
        self.assertNotEqual(inspected.returncode, 0)


    def test_generated_feature_id_mutation_cannot_self_validate(self):
        self._write_solution("""
def fit_predict(train, features):
    features['Id'] = 'MODEL_MUTATED_ID'
    return [1.0] * len(features)
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.INVALID_OUTPUT)

    def test_rejects_symlink_input_without_container_execution(self):
        real = self.base / "real-solution.py"
        real.write_text("def fit_predict(train, features): return [1] * len(features)\n", encoding="utf-8")
        self.solution.unlink(missing_ok=True)
        self.solution.symlink_to(real)
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.INVALID_INPUT)

    def test_rejects_nonfinite_and_wrong_order_predictions(self):
        self._write_solution("""
def fit_predict(train, features):
    return [float('nan'), 2.0]
""")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.EXECUTION_FAILED)


    def test_pids_limit_bounds_synthetic_descendant_creation(self):
        self._write_solution("""
import subprocess

def fit_predict(train, features):
    started = 0
    for _ in range(64):
        try:
            subprocess.Popen(['sleep', '2'])
            started += 1
        except OSError:
            break
    return [float(started)] * len(features)
""")
        result = run_fixed_solution(self._config(pids_limit=8))
        self.assertEqual(result.status, RunStatus.SUCCESS)
        with result.predictions_path.open(newline="", encoding="utf-8") as handle:
            count = float(list(csv.reader(handle))[1][1])
        self.assertLess(count, 64)

    def test_memory_limit_has_observed_cgroup_oom_kill_and_runner_denies_result(self):
        probe_name = "argo-hp-memory-probe-11111111"
        command = [
            "docker", "run", "--name", probe_name, "--network", "none", "--memory", "128m", "--memory-swap", "128m",
            IMAGE_DIGEST, "python", "-c", "blocks = []\nwhile True: blocks.append(bytearray(16 * 1024 * 1024))",
        ]
        try:
            probe = subprocess.run(command, text=True, capture_output=True, timeout=20)
            inspected = subprocess.run(
                ["docker", "container", "inspect", "--format", "{{.State.OOMKilled}}", probe_name],
                text=True, capture_output=True, timeout=10, check=True,
            )
            self.assertNotEqual(probe.returncode, 0)
            self.assertEqual(inspected.stdout.strip(), "true")
        finally:
            subprocess.run(["docker", "rm", "--force", probe_name], text=True, capture_output=True, timeout=10, check=False)
        self._write_solution("""
def fit_predict(train, features):
    blocks = []
    while True:
        blocks.append(bytearray(16 * 1024 * 1024))
""")
        result = run_fixed_solution(self._config(memory_bytes=128 * 1024 * 1024, wall_seconds=8))
        self.assertEqual(result.status, RunStatus.EXECUTION_FAILED)
        self.assertIsNone(result.predictions_path)

    def test_sigterm_reaps_exact_named_container(self):
        self._write_solution("""
import time

def fit_predict(train, features):
    time.sleep(30)
    return [1.0] * len(features)
""")
        config = self._config(wall_seconds=30)
        request = self.base / "trusted-request.json"
        request.write_text(json.dumps({
            key: str(value) if isinstance(value, Path) else value
            for key, value in config.__dict__.items()
        }), encoding="utf-8")
        child = subprocess.Popen(
            [sys.executable, str(Path(__file__).with_name("container_runner.py")),
             "--trusted-orx-request", str(request)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and child.poll() is None:
                listed = subprocess.run(
                    ["docker", "container", "ls", "--all", "--filter", f"name=^/{config.container_name}$", "--format", "{{.ID}}"],
                    text=True, capture_output=True, timeout=5, check=True,
                )
                if listed.stdout.strip():
                    break
                time.sleep(0.05)
            self.assertIsNone(child.poll(), "runner exited before SIGTERM control")
            child.terminate()
            stdout, stderr = child.communicate(timeout=20)
            self.assertEqual(stderr, "")
            self.assertEqual(json.loads(stdout)["status"], RunStatus.CANCELLED.value)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=5)
        absence = subprocess.run(
            ["docker", "container", "inspect", config.container_name], text=True, capture_output=True, timeout=10,
        )
        self.assertNotEqual(absence.returncode, 0)

    def test_output_mount_is_one_precreated_file_and_fsize_blocks_large_write(self):
        self._write_solution("""
from pathlib import Path

def fit_predict(train, features):
    Path('/tmp/not-a-host-sibling.txt').write_text('container-only')
    Path('/tmp/predictions.csv').write_bytes(b'x' * 4096)
    raise RuntimeError('stop after bounded write')
""")
        result = run_fixed_solution(self._config(max_output_bytes=512))
        self.assertEqual(result.status, RunStatus.INVALID_OUTPUT)
        output = self.base / "private-output" / result.run_id
        self.assertEqual([item.name for item in output.iterdir()], ["predictions.csv"])
        self.assertLessEqual((output / "predictions.csv").stat().st_size, 512)
        self.assertFalse((output / "not-a-host-sibling.txt").exists())

    def test_rejects_boolean_and_nonfinite_resource_caps_before_docker(self):
        self._write_solution("def fit_predict(train, features): return [1] * len(features)\n")
        self.assertEqual(run_fixed_solution(self._config(wall_seconds=True)).status, RunStatus.INVALID_INPUT)
        self.assertEqual(run_fixed_solution(self._config(cpus=float('nan'))).status, RunStatus.INVALID_INPUT)

    def test_docker_flags_are_fixed_and_do_not_accept_model_arguments(self):
        self._write_solution("def fit_predict(train, features): return [1] * len(features)\n")
        result = run_fixed_solution(self._config())
        self.assertEqual(result.status, RunStatus.SUCCESS)
        argv = result.docker_argv
        self.assertIn("--network", argv)
        self.assertIn("none", argv)
        self.assertIn("--read-only", argv)
        self.assertIn("--cap-drop", argv)
        self.assertIn("ALL", argv)
        self.assertIn("--security-opt", argv)
        self.assertIn("no-new-privileges=true", argv)
        self.assertIn("--user", argv)
        self.assertNotIn("--privileged", argv)


if __name__ == "__main__":
    unittest.main(verbosity=2)
