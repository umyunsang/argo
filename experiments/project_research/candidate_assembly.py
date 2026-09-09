"""Assemble each team's controller-verified artifacts into a candidate workspace for blind review."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .contracts import utc_now, write_new
from .dispatch import ROOT
from .state import Store
from .team_runner import ROLE_ORDER, latest_candidate, session_paths


IDENTITY_PATTERNS = (
    (re.compile(r"(?i)\bteam[-_ ]?[0-9]+\b"), "[TEAM]"),
    (re.compile(r"(?i)\b(?:anthropic/|openai-codex/)?(?:claude[-_ ]?(?:sonnet|opus|haiku)?[-_ ]?[0-9][\w.-]*|gpt[-_]?[0-9][\w.-]*|codex|anthropic|openai)\b"), "[MODEL]"),
    (re.compile(r"session-[a-f0-9]{32}"), "[SESSION]"),
)


def redact_identity(value):
    """Remove team/model/session identity from candidate text; scientific content is untouched."""
    if isinstance(value, dict):
        return {k: redact_identity(v) for k, v in value.items() if k not in ("team_id", "model_id", "session_id", "session", "sessions", "producer_session_ids", "reproducer_session_id")}
    if isinstance(value, list):
        return [redact_identity(v) for v in value]
    if isinstance(value, str):
        for pattern, replacement in IDENTITY_PATTERNS:
            value = pattern.sub(replacement, value)
        return value
    return value


def team_runs(campaign_id: str, team: str) -> list[dict]:
    snapshot = Store(ROOT / "control/state.sqlite").snapshot()
    seen: set[str] = set()
    runs = []
    for e in snapshot["events"]:
        if e.get("event") == "hypothesis_observation" and e.get("project_id") == campaign_id and e.get("team_id") == team and e["run_id"] not in seen:
            seen.add(e["run_id"])
            runs.append({"run_id": e["run_id"], "experiment_id": e["experiment_id"], "status": e["result_status"],
                         "receipt_sha256": e["receipt_sha256"], "session_id": e.get("session_id"), "hypothesis": e.get("hypothesis")})
    return runs


def find_output(run_id: str) -> Path | None:
    for dispatch_dir in (ROOT / "control/dispatches").iterdir():
        launch = dispatch_dir / "launch.json"
        if launch.exists() and json.loads(launch.read_text()).get("run_id") == run_id:
            frozen = json.loads((dispatch_dir / "frozen.json").read_text())
            spec_digest = frozen["spec_digest"]
            for run_dir in (ROOT / "runs").iterdir():
                receipt = run_dir / "receipt.json"
                if receipt.exists() and json.loads(receipt.read_text()).get("spec_digest") == spec_digest:
                    return run_dir
    return None


def assemble(campaign_id: str, team: str) -> dict:
    """Write a fresh candidate-workspace-<n>/ under the team's control dir with trusted receipts and role conclusions."""
    control = ROOT / "control/campaigns" / campaign_id / team
    existing = sorted(p for p in control.glob("candidate-workspace*") if p.is_dir())
    workspace = control / f"candidate-workspace-{len(existing) + 1}"
    workspace.mkdir(mode=0o700)
    report = ["# Candidate report", "", f"Campaign {campaign_id}.", ""]
    sessions = []
    for role in ROLE_ORDER:
        role_control, _ = session_paths(campaign_id, team, role)
        candidate = latest_candidate(role_control)
        if candidate is None:
            report += [f"## {role}", "", "No conclusion submitted.", ""]
            continue
        sessions.append(candidate["session_id"])
        report += [f"## {role} conclusion", "", redact_identity(candidate["conclusion"]), "", "### Claims", ""] + [f"- {redact_identity(c)}" for c in candidate["claims"]] + ["", "### Limitations", ""] + [f"- {redact_identity(l)}" for l in candidate["limitations"]] + [""]
    (workspace / "report.md").write_text("\n".join(report))
    # Private, identity-bearing mapping stays outside the reviewed artifact set.
    write_new(workspace / "private-identity.json", {"campaign_id": campaign_id, "team_id": team, "sessions": sessions})
    runs = team_runs(campaign_id, team)
    runs_doc = []
    for run in runs:
        out = find_output(run["run_id"])
        entry = dict(run)
        entry.pop("session_id", None)
        if out is not None:
            receipt = json.loads((out / "receipt.json").read_text())
            entry.update({"exit_code": receipt.get("exit_code"), "cpu_seconds": (receipt.get("resources") or {}).get("cpu_seconds"),
                          "image": receipt.get("image"), "result_sha256": receipt.get("result_sha256"), "spec_digest": receipt.get("spec_digest")})
            if (out / "result.json").exists():
                target = workspace / f"result-{run['run_id'][:8]}.json"
                target.write_text(json.dumps(redact_identity(json.loads((out / "result.json").read_text())), indent=2, ensure_ascii=False))
                entry["result_file"] = target.name
        runs_doc.append(entry)
    write_new(workspace / "orx-runs.json", {"campaign_id": campaign_id, "runs": [redact_identity(r) for r in runs_doc], "generated_at": utc_now()})
    # Controller-derived independent reproduction receipt: last role reran a frozen earlier-role candidate.
    repro_control, _ = session_paths(campaign_id, team, "reproduction")
    repro = latest_candidate(repro_control)
    repro_session = (repro or {}).get("session_id")
    repro_runs = [r for r in runs if r.get("session_id") == repro_session and r["status"] == "EXECUTED_UNVALIDATED"]
    producer_runs = [r for r in runs if r.get("session_id") != repro_session and r["status"] == "EXECUTED_UNVALIDATED"]
    by_run = {r["run_id"]: r for r in runs_doc}
    if repro and repro_runs and producer_runs:
        env = json.loads((ROOT / "control/environment.json").read_text())
        wine = json.loads((ROOT / "worker/wine/manifest.json").read_text())
        # Session identities are opaque tokens so the reviewer can check producer/reproducer distinctness without learning teams.
        opaque = {s: "session-" + hashlib.sha256((campaign_id + s).encode()).hexdigest()[:16] for s in {r["session_id"] for r in runs}}
        receipt = {"kind": "independent_reproduction", "status": "PASS" if all(by_run[r["run_id"]].get("exit_code") == 0 for r in repro_runs) else "FAIL",
                   "evidence_scope": "development_research", "producer_session_ids": sorted({opaque[r["session_id"]] for r in producer_runs}),
                   "reproducer_session_id": opaque[repro_session], "execution_id": repro_runs[-1]["run_id"],
                   "command": ["/opt/homebrew/bin/python3", "runner.py"], "exit_code": by_run[repro_runs[-1]["run_id"]].get("exit_code"),
                   "environment_sha256": env["image"].split(":", 1)[1], "input_sha256": [wine["files"]["train.csv"]["sha256"], wine["files"]["dev.csv"]["sha256"]],
                   "output_sha256": [by_run[r["run_id"]]["result_sha256"] for r in repro_runs if by_run[r["run_id"]].get("result_sha256")],
                   "scope": "Same-team fresh-session rerun of frozen candidate in the pinned image; the controller derived this receipt from ORX records, not from agent prose. It is not a cross-team or external replication."}
        write_new(workspace / "reproduction-receipt.json", receipt)
    (workspace / "assembled.json").write_text(json.dumps({"campaign_id": campaign_id, "runs": len(runs_doc), "at": utc_now()}, indent=2) + "\n")
    return {"workspace": str(workspace), "files": sorted(p.name for p in workspace.iterdir()), "sessions": sessions, "runs": len(runs_doc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id")
    parser.add_argument("team")
    args = parser.parse_args()
    print(json.dumps(assemble(args.campaign_id, args.team), indent=2))


if __name__ == "__main__":
    main()
