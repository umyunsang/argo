"""Recording executor for run_block tests. Never calls a model."""
import json
from pathlib import Path


def record(arm, task, seed, workdir, oracle_dir, dry_run):
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "fixture_marker.json").write_text(json.dumps({"arm": arm, "seed": seed}))
    import os
    if seed == int(os.environ.get("FIXTURE_CRASH_AT_SEED", "-1")):
        raise RuntimeError("fixture crash after spend")
    if seed == int(os.environ.get("FIXTURE_KILL_AT_SEED", "-1")):
        os._exit(137)  # hard kill: no interrupt handler can run
    return {"arm": arm, "task": task, "seed": seed, "answered": True,
            "total_tokens": 1000 + seed, "cost_usd": 0.01,
            "manipulation_check": {"manipulation_check_passed": True}}
