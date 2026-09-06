#!/usr/bin/env python3
"""One fixed-policy DiscoveryWorld determinism episode; no scorer or gold access."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import socket
import subprocess
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def block_network() -> None:
    def denied(*args, **kwargs):
        raise OSError("NETWORK_DISABLED_BY_LONG_HORIZON_PROBE")
    socket.create_connection = denied
    original = socket.socket
    class NoNetworkSocket(original):
        def connect(self, address):
            raise OSError("NETWORK_DISABLED_BY_LONG_HORIZON_PROBE")
        def connect_ex(self, address):
            return 1
    socket.socket = NoNetworkSocket


def nested_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key)); keys.update(nested_keys(child))
    elif isinstance(value, list):
        for child in value: keys.update(nested_keys(child))
    return keys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--difficulty", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--repeat", type=int, choices=[0, 1], required=True)
    parser.add_argument("--thread-id", type=int, required=True)
    parser.add_argument("--steps", type=int, choices=[1000], required=True)
    args = parser.parse_args()
    block_network()
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        import discoveryworld
        from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
        api = DiscoveryWorldAPI(threadID=args.thread_id)
        loaded = api.loadScenario(args.scenario, args.difficulty, args.seed, numUserAgents=1)
        chain = bytes(32)
        checkpoints = {}
        action_successes = 0
        tick_successes = 0
        hidden_names = {"scoreCard", "scoreNormalized", "criticalQuestions", "criticalHypotheses"}
        hidden_seen = set()
        checkpoint_steps = {0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000}
        observation = api.getAgentObservation(0)
        hidden_seen.update(hidden_names & nested_keys(observation))
        checkpoints["0"] = hashlib.sha256(canonical(observation["ui"])).hexdigest()
        directions = ["north", "east", "south", "west"]
        for step in range(1, args.steps + 1):
            action = {"action": "ROTATE_DIRECTION", "arg1": directions[(step - 1) % 4]}
            action_result = api.performAgentAction(0, action)
            tick_result = api.tick()
            observation = api.getAgentObservation(0)
            hidden_seen.update(hidden_names & nested_keys(observation))
            action_successes += action_result.get("success") is True
            tick_successes += tick_result.get("success") is True
            payload = {"step": step, "action": action, "action_result": action_result, "tick_result": tick_result, "ui": observation["ui"]}
            chain = hashlib.sha256(chain + canonical(payload)).digest()
            if step in checkpoint_steps: checkpoints[str(step)] = hashlib.sha256(canonical(observation["ui"])).hexdigest()
    package_root = Path(discoveryworld.__file__).resolve().parents[1]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=package_root, text=True).strip()
    result = {"schema_version":"argo-discoveryworld-long-horizon-episode/v1","commit":commit,"scenario":args.scenario,"difficulty":args.difficulty,"seed":args.seed,"repeat":args.repeat,"steps":args.steps,"loaded":loaded,"action_successes":action_successes,"tick_successes":tick_successes,"step_counter":api.getStepCounter(),"chain_sha256":chain.hex(),"checkpoints":checkpoints,"hidden_keys_in_observation":sorted(hidden_seen),"captured_stdout_sha256":hashlib.sha256(captured.getvalue().encode()).hexdigest(),"vision_accessed":False,"model_calls":0,"spend_usd":0.0}
    print(json.dumps(result, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
