"""Container entrypoint emitting CPU and failure receipts for a real task."""
from __future__ import annotations

import json
import resource
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    spec = json.loads(Path("/app/node-spec.json").read_text())
    start = time.monotonic()
    command = ([sys.executable, "/app/candidate.py"] if spec.get("mode") == "candidate" else
               [sys.executable, "-m", "experiments.project_research.domains.cli", *spec["arguments"], "--output", "/output/result.json"])
    result = subprocess.run(command, check=False)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {"exit_code": result.returncode, "wall_seconds": time.monotonic() - start,
               "cpu_seconds": usage.ru_utime + usage.ru_stime, "max_rss_kib": usage.ru_maxrss,
               "command": command, "scope": "DEVELOPMENT_RESEARCH", "autonomous_campaign": spec.get("mode") == "candidate"}
    Path("/output/resource.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
