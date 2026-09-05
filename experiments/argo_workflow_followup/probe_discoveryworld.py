#!/usr/bin/env python3
"""Zero-cost deterministic-boundary probe for a pinned DiscoveryWorld install."""
from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import io
import json
import os
import subprocess
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def nested_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(nested_keys(child))
    return keys


def image_hashes(data_url: str) -> dict:
    from PIL import Image

    raw = base64.b64decode(data_url.split(",", 1)[1])
    image = Image.open(io.BytesIO(raw)).convert("RGBA")
    return {
        "png_sha256": hashlib.sha256(raw).hexdigest(),
        "pixel_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
        "size": list(image.size),
        "mode": image.mode,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="Proteomics")
    parser.add_argument("--difficulty", default="Easy")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--thread-id", type=int, required=True)
    args = parser.parse_args()

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        import discoveryworld
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

        api = DiscoveryWorldAPI(threadID=args.thread_id)
        loaded = api.loadScenario(
            args.scenario, args.difficulty, args.seed, numUserAgents=1
        )
        observation_0 = api.getAgentObservation(0)
        directions = sorted(
            observation_0["ui"]["agentLocation"]["directions_you_can_move"]
        )
        if not directions:
            raise RuntimeError("NO_AVAILABLE_DIRECTION")
        action_result = api.performAgentAction(
            0, {"action": "MOVE_DIRECTION", "arg1": directions[0]}
        )
        tick_result = api.tick()
        observation_1 = api.getAgentObservation(0)
        scorecard = api.getTaskScorecard()

    package_root = Path(discoveryworld.__file__).resolve().parents[1]
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=package_root, text=True
    ).strip()
    hidden_names = {
        "scoreCard", "scoreNormalized", "criticalQuestions", "criticalHypotheses"
    }
    result = {
        "schema_version": "argo-discoveryworld-probe/v1",
        "commit": commit,
        "scenario": args.scenario,
        "difficulty": args.difficulty,
        "seed": args.seed,
        "loaded": loaded,
        "direction": directions[0],
        "action_result": action_result,
        "tick_result": tick_result,
        "step": api.getStepCounter(),
        "ui_0_sha256": canonical_hash(observation_0["ui"]),
        "ui_1_sha256": canonical_hash(observation_1["ui"]),
        "scorecard_sha256": canonical_hash(scorecard),
        "vision_0": {
            key: image_hashes(value)
            for key, value in sorted(observation_0["vision"].items())
        },
        "vision_1": {
            key: image_hashes(value)
            for key, value in sorted(observation_1["vision"].items())
        },
        "hidden_keys_in_observation": sorted(
            hidden_names & nested_keys(observation_1)
        ),
        "captured_runtime_stdout_sha256": hashlib.sha256(
            captured.getvalue().encode()
        ).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
