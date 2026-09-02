#!/usr/bin/env python3
"""Study A instrument pilot: build one episode workspace and emit its fixed command.

The command is identical in every condition. Only committed configuration differs:
whether a released evidence pack is mounted (dynamic retrieval) and whether a
structured research-state scaffold is mounted (structured state).

    /usr/bin/python3 experiments/study_a/run_pilot.py --plan <plan.json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_sandbox import Bundle, build_workspace, run_probes, workspace_digest  # noqa: E402

CONDITIONS = {"C00": (False, False), "C01": (False, True), "C10": (True, False), "C11": (True, True)}
REQUIRED_STATE_FIELD = "sampling_frame"

SCAFFOLD = """# Research state (fill every field before writing the design)

decision_id:
question:
alternatives:            # at least two rejected alternatives
""" + REQUIRED_STATE_FIELD + """:   # the population and unit your comparison samples over
evidence_used:           # what you relied on, and what you could not verify
falsifier:               # the observation that would refute your design's premise
stopping_rule:           # when you would stop collecting
"""

BASE_PROMPT = """Read ./instructions.md in this directory and produce the complete experimental design it asks for.

Write the design to ./design.md. Do not print it to the terminal only; the file is the deliverable.
Do not report any numeric result: you are designing, not running.
"""

RETRIEVAL_PROMPT = """A released evidence pack is mounted at ./evidence. It contains excerpts from prior studies.
Consult it before deciding. Cite the file name of any excerpt you rely on.
Use only ./evidence. Do not search the network.
"""

STATE_PROMPT = """A research-state scaffold is mounted at ./state.md.
Fill every field in ./state.md first, then write ./design.md so that it follows the filled state.
Your design must explicitly reference the '""" + REQUIRED_STATE_FIELD + """' you recorded.
"""


def build_episode(plan: dict, out_root: Path) -> dict:
    condition = plan["condition"]
    structured, retrieval = CONDITIONS[condition]
    bundle = Bundle(Path(plan["task_bundle"]))
    ws = build_workspace(bundle, out_root / plan["episode_id"])
    if not retrieval and (ws / "evidence").exists():
        shutil.rmtree(ws / "evidence")
    if structured:
        (ws / "state.md").write_text(SCAFFOLD, encoding="utf-8")
    probes = run_probes(ws, bundle, env={}, scoring_paths=[], artifact=None, required_state_field=None)
    prompt = BASE_PROMPT + (RETRIEVAL_PROMPT if retrieval else "") + (STATE_PROMPT if structured else "")
    return {
        "episode_id": plan["episode_id"], "task_id": plan["task_id"], "condition": condition,
        "structured_state": structured, "dynamic_retrieval": retrieval,
        "workspace": str(ws), "workspace_digest": workspace_digest(ws),
        "prelaunch_probes": probes.fired, "admissible": probes.admissible,
        "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "evidence_files": sorted(p.name for p in (ws / "evidence").glob("*.txt")) if retrieval else [],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out-root", default="/tmp/study-a-pilot")
    args = ap.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    print(json.dumps(build_episode(plan, Path(args.out_root)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
