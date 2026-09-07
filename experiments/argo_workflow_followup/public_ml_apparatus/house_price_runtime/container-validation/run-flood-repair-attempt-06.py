import json
from pathlib import Path
import subprocess
import sys
import time
base = Path(__file__).resolve().parent
stdout_path = base / "flood-repair-attempt-06.stdout"
stderr_path = base / "flood-repair-attempt-06.stderr"
receipt_path = base / "flood-repair-attempt-06.exit.json"
started = time.monotonic()
command = [sys.executable, "-m", "unittest", "-v", "test_container_runner.ContainerRunnerTests.test_unmounted_output_directory_extra_file_write_is_denied", "test_container_runner.ContainerRunnerTests.test_stdout_flood_truncates_without_echo_and_cleans_exact_container"]
try:
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(command, cwd=base.parent, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=30, check=False)
    receipt = {"exit_code": completed.returncode, "timed_out": False}
except subprocess.TimeoutExpired:
    receipt = {"exit_code": 124, "timed_out": True}
receipt["duration_seconds"] = time.monotonic() - started
receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
raise SystemExit(receipt["exit_code"])
