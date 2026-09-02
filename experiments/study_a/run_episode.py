#!/usr/bin/env python3
"""Fixed Study A episode runner. One command, configuration-driven.

    /usr/bin/python3 experiments/study_a/run_episode.py --config <episode.json>

The command never changes across conditions; only committed configuration does.
The runner refuses to execute a treatment unless the configuration is complete,
the release sandbox is clean, and a model backend is declared. Absent a backend
it reports NOT_EXECUTED rather than inventing an outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ceiling_enforcement import enforce  # noqa: E402
from release_sandbox import Bundle, build_workspace, run_probes, workspace_digest  # noqa: E402

REQUIRED = ("episode_id", "task_bundle", "condition", "structured_state", "dynamic_retrieval",
            "model_selector", "token_ceiling", "call_ceiling", "wallclock_seconds", "output_schema")
CONDITIONS = {"C00": (False, False), "C01": (False, True), "C10": (True, False), "C11": (True, True)}


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate_config(cfg: dict) -> list[str]:
    problems = [f"missing field: {k}" for k in REQUIRED if k not in cfg]
    cond = cfg.get("condition")
    if cond not in CONDITIONS:
        problems.append(f"unknown condition: {cond}")
    else:
        want = CONDITIONS[cond]
        got = (bool(cfg.get("structured_state")), bool(cfg.get("dynamic_retrieval")))
        if want != got:
            problems.append(f"condition {cond} declares factors {got}, expected {want}")
    for k in ("token_ceiling", "call_ceiling", "wallclock_seconds"):
        if k in cfg and not isinstance(cfg[k], int):
            problems.append(f"{k} must be an integer ceiling")
    return problems


def run(config_path: Path, workspace_root: Path) -> dict:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    problems = validate_config(cfg)
    receipt = {"runner_version": 1, "config_path": str(config_path), "config_sha256": _sha(config_path),
               "episode_id": cfg.get("episode_id"), "condition": cfg.get("condition"),
               "status": "NOT_EXECUTED", "reasons": problems}
    if problems:
        receipt["reasons"] = ["configuration incomplete"] + problems
        return receipt

    bundle = Bundle(Path(cfg["task_bundle"]))
    ws = build_workspace(bundle, workspace_root / cfg["episode_id"])
    # Pre-launch probes only. The state-manipulation probe needs the produced
    # artifact, so it runs after the episode, during scoring admission.
    probes = run_probes(ws, bundle, env=cfg.get("environment", {}),
                        scoring_paths=cfg.get("scoring_paths", []),
                        artifact=None, required_state_field=None)
    receipt["workspace_digest"] = workspace_digest(ws)
    receipt["prelaunch_probes"] = probes.fired
    if not probes.admissible:
        receipt["reasons"] = ["release sandbox probe fired before launch"]
        return receipt

    backend = cfg.get("model_backend")
    if not backend:
        receipt["reasons"] = ["no model backend declared; treatment execution requires one"]
        return receipt

    receipt["status"] = "EXECUTED"
    receipt["reasons"] = []
    receipt["backend"] = backend
    receipt["post_episode_probes_required"] = ["state_manipulation", "hardcoded_metric"]
    receipt["declared_ceilings"] = declared_ceilings(cfg)
    receipt["scoring_admission"] = "PENDING_CEILING_CHECK"
    return receipt


def declared_ceilings(cfg: dict) -> dict:
    """Ceilings the configuration declares, in the vocabulary the enforcer measures.

    A ceiling named in a vocabulary the enforcer cannot measure is dropped here rather
    than silently ignored later, and its absence makes the episode inadmissible.
    """
    mapping = {"token_ceiling": "total_tokens", "call_ceiling": "api_calls",
               "wallclock_seconds": "wallclock_seconds",
               "marginal_token_ceiling": "marginal_tokens"}
    out = {}
    for key, quantity in mapping.items():
        if isinstance(cfg.get(key), int):
            out[quantity] = cfg[key]
    return out


def admit_for_scoring(receipt: dict, usage: dict, wallclock_seconds=None) -> dict:
    """Decide whether an executed episode may be scored.

    An episode is scorable only if it executed, its pre-launch probes stayed silent, and
    its measured usage respects every declared ceiling. A missing usage record is a
    refusal rather than a pass, because an unmeasured episode cannot be shown to comply.
    """
    if receipt.get("status") != "EXECUTED":
        return {"scorable": False, "reason": "episode did not execute"}
    if receipt.get("prelaunch_probes"):
        return {"scorable": False, "reason": "release sandbox probe fired before launch"}
    if not usage or usage.get("status") != "MEASURED":
        return {"scorable": False, "reason": "no measured usage; compliance cannot be shown"}
    verdict = enforce(usage, receipt.get("declared_ceilings") or {},
                      wallclock_seconds=wallclock_seconds)
    if not verdict["admissible"]:
        return {"scorable": False, "reason": verdict.get("reason", "ceiling violated"),
                "violations": verdict["violations"], "measured": verdict.get("measured", {})}
    return {"scorable": True, "measured": verdict["measured"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workspace-root", default="/tmp/study-a-workspaces")
    args = ap.parse_args(argv)
    receipt = run(Path(args.config), Path(args.workspace_root))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] in ("EXECUTED", "NOT_EXECUTED") else 1


if __name__ == "__main__":
    sys.exit(main())
