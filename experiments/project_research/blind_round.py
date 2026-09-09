"""Run one blinded supervisor round over two teams' assembled candidates using a fresh native session."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from .candidate_assembly import assemble
from .contracts import utc_now, write_new
from .dispatch import ROOT, SOURCE
from .review import CandidateSpec, build_blind_round
from .state import Store
from .team_runner import ROLE_ORDER, latest_candidate, session_paths

CONTROLLER = SOURCE / "campaign_controller.ts"
SUPERVISOR_PROMPT = """You are a fresh blinded supervisor. Your workspace contains exactly one packet.json and two anonymous candidate directories. You have no memory of prior rounds and no knowledge of which team, model or author produced either candidate; do not try to infer it.

Judge each candidate against the six fixed dimensions: correctness, reproducibility, research_logic, falsification_and_comparison, evidence_and_accounting, claim_scope. For every finding give artifact_id, sha256 and an L<n> or L<n>-L<m> line locator inside that artifact, the impact on the conclusion, the minimum fix, and how to recheck. Severity is Critical, Major, Minor or Style. AAA requires every dimension PASS with cited evidence and no unresolved Critical/Major. Do not award AAA for style; do not block AAA for taste.

Write one assessment JSON per candidate into your workspace as assessment-<candidate_id>.json with this shape:
{"candidate_id", "round_id", "supervisor_session_id", "layer", "session_attestation": {"fresh_session": true, "received_only_packet": true, "previous_scores_received": false}, "dimensions": {<name>: {"status": PASS|FAIL|UNCONFIRMED, "rationale", "evidence": [{"artifact_id","sha256","locator"}]}}, "findings": [{"finding_id","severity","evidence":[...],"impact","minimum_fix","recheck"}], "independent_reproduction_evidence": [{"artifact_id","sha256","locator"}]}
independent_reproduction_evidence must point at a candidate's reproduction receipt JSON if one exists. Then call finish with a conclusion that names which candidate you select as the branch to continue and why, listing every Critical/Major finding. You have no experiment tool; this is review only."""


def prepare_round(campaign_id: str, *, layer: str = "research_operations") -> dict:
    teams = ("team-1", "team-2")
    specs = []
    for team in teams:
        assembled = assemble(campaign_id, team)
        workspace = Path(assembled["workspace"])
        sessions = assembled["sessions"]
        artifacts = tuple(sorted(p.name for p in workspace.iterdir() if p.is_file() and p.suffix in (".md", ".json") and p.name not in ("assembled.json", "private-identity.json")))
        models = tuple(sorted({json.loads(p.read_text())["model_id"] for role in ROLE_ORDER for p in session_paths(campaign_id, team, role)[0].glob("candidate-*.json")}))
        specs.append(CandidateSpec(candidate_id=f"{campaign_id}/{team}", team_id=team, workspace=workspace, artifacts=artifacts,
                                   authors=tuple(sessions) or (team,), models=models or ("unknown",)))
    round_id = "round-" + uuid.uuid4().hex[:12]
    round_dir = ROOT / "control/reviews" / campaign_id / round_id
    result = build_blind_round(specs, round_dir, layer=layer, evidence_scope="development_research")
    Store(ROOT / "control/state.sqlite").event({"event": "blind_round_prepared", "project_id": campaign_id, "round_dir": str(round_dir),
                                               "supervisor_session_id": result["supervisor_session_id"], "teams": list(teams)})
    return {**result, "round_id": round_id}


def prepare_supervisor_session(campaign_id: str, round_info: dict) -> Path:
    """A sterile controller session whose workspace is a copy of the supervisor packet only."""
    supervisor_dir = Path(round_info["supervisor_dir"])
    base_cfg = json.loads((ROOT / "control/campaigns" / campaign_id / "team-1/research/config.json").read_text())
    session_id = round_info["supervisor_session_id"]
    base = ROOT / "sessions" / campaign_id / "supervisor" / session_id
    workspace, artifacts = base / "workspace", base / "artifacts"
    control = ROOT / "control/campaigns" / campaign_id / "supervisor" / session_id
    for path in (workspace, artifacts, control):
        path.mkdir(parents=True, exist_ok=False, mode=0o700)
    for item in supervisor_dir.rglob("*"):
        if item.is_file():
            target = workspace / item.relative_to(supervisor_dir)
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(item, target)
            target.chmod(0o600)
    (control / "task.md").write_text(SUPERVISOR_PROMPT + "\n")
    (control / "policy.md").write_text("Blinded supervisor: review only, no experiments, no model change.\n")
    cfg = {**base_cfg, "team_id": "supervisor", "role": "supervisor", "workspace": str(workspace), "artifact_root": str(artifacts),
           "control_dir": str(control), "session_id": session_id, "task_prompt": str(control / "task.md"), "policy_prompt": str(control / "policy.md"),
           "deadline_epoch": time.time() + 7200, "max_controller_turns": 24, "supervisor_round_dir": round_info["round_dir"]}
    write_new(control / "config.json", cfg)
    return control / "config.json"


def run_supervisor(config: Path, *, max_resumes: int = 4) -> dict:
    summary: dict = {}
    for attempt in range(max_resumes):
        proc = subprocess.run(["/opt/homebrew/bin/node", "--experimental-strip-types", str(CONTROLLER), str(config)],
                              stdout=subprocess.PIPE, stderr=open(config.parent / "supervisor-runner.log", "a"), text=True, cwd=str(SOURCE.parents[1]), timeout=7200)
        line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
        summary = json.loads(line)
        status = summary.get("status", "")
        if status in ("CONCLUSION_SUBMITTED", "INTERRUPTED_CHECKPOINT_RETAINED", "CONTROLLER_TURN_LIMIT"):
            return summary
        if status == "MODEL_REQUEST_FAILED":
            # Aborted/failed generation with settled accounting: resume the same transcript.
            time.sleep(5)
            continue
        if status.startswith("MODEL_") or status.startswith("PRIOR_MODEL"):
            subprocess.run([sys.executable, "-m", "experiments.project_research.campaign_bridge", "--config", str(config), "reconcile_subscription"],
                           input="{}", text=True, capture_output=True, cwd=str(SOURCE.parents[1]), timeout=600)
            time.sleep(5)
            continue
        if status in ("AWAITING_RESEARCH_DECISION", "YIELDED"):
            continue
        return summary
    return summary


def collect_assessments(config: Path) -> list[Path]:
    workspace = Path(json.loads(config.read_text())["workspace"])
    return sorted(p for p in workspace.glob("assessment-*.json") if re.fullmatch(r"assessment-candidate-[a-f0-9]{24}\.json", p.name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    info = prepare_round(args.campaign_id)
    config = prepare_supervisor_session(args.campaign_id, info)
    out = {"round": info, "supervisor_config": str(config)}
    if not args.prepare_only:
        out["summary"] = run_supervisor(config)
        out["assessments"] = [str(p) for p in collect_assessments(config)]
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
