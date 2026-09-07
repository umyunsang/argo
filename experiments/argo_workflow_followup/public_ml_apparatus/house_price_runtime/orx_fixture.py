"""Inert bounded ORX lifecycle fixture. No model, data, network or child process."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import threading


def execute(configuration):
    if not isinstance(configuration, dict) or set(configuration) != {"mode", "nonce"}:
        raise ValueError("CONFIG")
    if configuration["mode"] not in {"success", "failure", "cancel"}:
        raise ValueError("CONFIG")
    if configuration["nonce"] != "house-price-orx-native-fixture-v1":
        raise ValueError("CONFIG")
    return {"schema_version":"argo-orx-native-fixture/v1", "mode":configuration["mode"],
            "fixture_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "config_sha256":hashlib.sha256(json.dumps(configuration,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "model_calls":0,"ML_fits":0,"hidden_scores":0}


def main():
    config = json.loads(Path("fixture-config.json").read_text())
    result = execute(config)
    print("ARGO_SYNTHETIC_START " + json.dumps(result,sort_keys=True), flush=True)
    if config["mode"] == "cancel":
        threading.Event().wait(20)
    print("ARGO_SYNTHETIC_END " + json.dumps({"mode":config["mode"],"ok":config["mode"]!="failure"},sort_keys=True),flush=True)
    return 3 if config["mode"]=="failure" else 0


if __name__ == "__main__":
    raise SystemExit(main())
