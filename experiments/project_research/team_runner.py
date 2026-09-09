"""Sequential role handoff within one independent team; teams never see each other."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .contracts import utc_now, write_new
from .dispatch import ROOT
from .state import Store

ROLE_ORDER = ("research", "experiment", "reproduction")
CONTROLLER = Path(__file__).resolve().parent / "campaign_controller.ts"


def session_paths(campaign_id: str, team: str, role: str) -> tuple[Path, Path]:
    control = ROOT / "control/campaigns" / campaign_id / team / role
    workspace = ROOT / "sessions" / campaign_id / team / role / "workspace"
    return control, workspace


def latest_candidate(control: Path) -> dict | None:
    files = sorted(control.glob("candidate-*.json"), key=lambda p: p.stat().st_mtime)
    return json.loads(files[-1].read_text()) if files else None


def frozen_sources(campaign_id: str, team: str) -> dict[str, tuple[bytes, str]]:
    """Exact candidate bytes that ORX executed for this team, keyed by run ID."""
    snapshot = Store(ROOT / "control/state.sqlite").snapshot()
    runs = {e["run_id"] for e in snapshot["events"] if e.get("event") == "hypothesis_observation" and e.get("project_id") == campaign_id and e.get("team_id") == team}
    found: dict[str, tuple[bytes, str]] = {}
    for dispatch_dir in (ROOT / "control/dispatches").iterdir():
        launch = dispatch_dir / "launch.json"
        frozen = dispatch_dir / "frozen.json"
        if not launch.exists() or not frozen.exists():
            continue
        run_id = json.loads(launch.read_text()).get("run_id")
        if run_id not in runs:
            continue
        candidate = Path(json.loads(frozen.read_text())["worktree"]) / "candidate.py"
        if candidate.is_file():
            data = candidate.read_bytes()
            found[run_id] = (data, hashlib.sha256(data).hexdigest())
    return found


def handoff(campaign_id: str, team: str, source_role: str, target_role: str) -> dict:
    """Copy the source role's frozen conclusion and workspace sources into the target role's workspace."""
    source_control, source_workspace = session_paths(campaign_id, team, source_role)
    target_control, target_workspace = session_paths(campaign_id, team, target_role)
    candidate = latest_candidate(source_control)
    if candidate is None:
        raise RuntimeError(f"{source_role} has not submitted a conclusion; handoff blocked")
    inbox = target_workspace / f"inbox-from-{source_role}"
    inbox.mkdir(mode=0o700, exist_ok=True)
    manifest = {}
    for p in sorted(source_workspace.iterdir()):
        if p.is_file() and p.suffix in (".py", ".md", ".json", ".txt", ".csv") and p.stat().st_size <= 1048576 and not p.name.startswith("inbox-"):
            shutil.copyfile(p, inbox / p.name)
            manifest[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    # Workspace files can be rewritten after submission; the frozen ORX candidates are what actually ran.
    executed = inbox / "executed-candidates"
    executed.mkdir(mode=0o700, exist_ok=True)
    for run_id, (data, sha) in frozen_sources(campaign_id, team).items():
        name = f"candidate-{run_id[:8]}.py"
        (executed / name).write_bytes(data)
        manifest[f"executed-candidates/{name}"] = sha
    conclusion = {k: candidate[k] for k in ("conclusion", "claims", "limitations", "session_id", "model_id")}
    write_new(inbox / "conclusion.json", conclusion)
    manifest["conclusion.json"] = hashlib.sha256((inbox / "conclusion.json").read_bytes()).hexdigest()
    write_new(inbox / "manifest.json", {"source_role": source_role, "team": team, "campaign_id": campaign_id, "files": manifest, "at": utc_now()})
    task_path = target_control / "task.md"
    task = task_path.read_text()
    marker = f"\n## Handoff from {source_role}\n"
    if marker not in task:
        task += marker + f"Your team's {source_role} session concluded; its conclusion, claims, limitations and workspace files are in inbox-from-{source_role}/ in your workspace (see manifest.json for hashes). inbox-from-{source_role}/executed-candidates/ holds the exact source bytes ORX ran for each of your team's run IDs; prefer these over workspace copies. Build on it; do not rewrite its recorded observations. Record disagreements as evidence-backed findings.\n"
        task_path.write_text(task)
    Store(ROOT / "control/state.sqlite").event({"event": "role_handoff", "project_id": campaign_id, "team_id": team, "source_role": source_role,
                                               "target_role": target_role, "files": len(manifest), "conclusion_session": candidate["session_id"]})
    return {"status": "HANDED_OFF", "files": len(manifest), "inbox": str(inbox)}


def run_role(campaign_id: str, team: str, role: str, *, max_resumes: int = 6) -> dict:
    """Run one role's controller to a terminal status, resuming on recoverable host yields."""
    control, _ = session_paths(campaign_id, team, role)
    config = control / "config.json"
    log = control / "team-runner.log"
    summary: dict = {}
    for attempt in range(max_resumes):
        with log.open("a") as out:
            out.write(f"\n=== attempt {attempt} {utc_now()} ===\n")
            out.flush()
            proc = subprocess.run(["/opt/homebrew/bin/node", "--experimental-strip-types", str(CONTROLLER), str(config)],
                                  stdout=subprocess.PIPE, stderr=out, text=True, cwd=str(CONTROLLER.parents[2]), timeout=28800)
        line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
        summary = json.loads(line)
        status = summary.get("status", "")
        Store(ROOT / "control/state.sqlite").event({"event": "role_session_status", "project_id": campaign_id, "team_id": team, "role": role, "status": status, "turns": summary.get("turns")})
        if status in ("CONCLUSION_SUBMITTED", "MODEL_CHANGE_REQUESTED", "INTERRUPTED_CHECKPOINT_RETAINED", "CONTROLLER_TURN_LIMIT"):
            return summary
        if status in ("AWAITING_RESEARCH_DECISION", "RESEARCH_OBSERVED", "YIELDED"):
            continue
        if status == "MODEL_REQUEST_FAILED":
            time.sleep(5)
            continue
        if status.startswith("MODEL_") or status.startswith("PRIOR_MODEL"):
            # Charge/usage reconciliation; the bridge settles from a fresh trusted view, then we resume.
            subprocess.run([sys.executable, "-m", "experiments.project_research.campaign_bridge", "--config", str(config), "reconcile_subscription"],
                           input="{}", text=True, capture_output=True, cwd=str(CONTROLLER.parents[2]), timeout=600)
            time.sleep(5)
            continue
        return summary
    return summary


def run_team(campaign_id: str, team: str) -> dict:
    results = {}
    for index, role in enumerate(ROLE_ORDER):
        if index:
            handoff(campaign_id, team, ROLE_ORDER[index - 1], role)
        results[role] = run_role(campaign_id, team, role)
        if results[role].get("status") != "CONCLUSION_SUBMITTED":
            results["stopped_at"] = role
            break
    write_new(ROOT / "control/campaigns" / campaign_id / team / f"team-run-{int(time.time())}.json", results)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id")
    parser.add_argument("team")
    args = parser.parse_args()
    print(json.dumps({role: value.get("status") if isinstance(value, dict) else value for role, value in run_team(args.campaign_id, args.team).items()}))


if __name__ == "__main__":
    main()
