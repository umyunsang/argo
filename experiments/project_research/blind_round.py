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
from .review import CandidateSpec, ReviewError, assess, build_blind_round
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


def validate_assessments(config: Path) -> dict[str, dict]:
    """Run the fixed validator over the supervisor's files without editing or importing them."""
    round_dir = Path(json.loads(config.read_text())["supervisor_round_dir"])
    out: dict[str, dict] = {}
    for path in collect_assessments(config):
        try:
            out[path.name] = {"status": "VALID", "result": assess(json.loads(path.read_text()), round_dir / "supervisor")}
        except (ReviewError, ValueError, OSError) as exc:
            out[path.name] = {"status": "REJECTED", "reason": str(exc)}
    return out


def locator_diagnostics(config: Path) -> dict[str, list[str]]:
    """List every malformed or out-of-range evidence locator with the artifact's real line count."""
    cfg = json.loads(config.read_text())
    supervisor_dir = Path(cfg["supervisor_round_dir"]) / "supervisor"
    packet = json.loads((supervisor_dir / "packet.json").read_text())
    files = {a["artifact_id"]: a["file"] for c in packet["candidates"] for a in c["artifacts"]}
    lengths = {aid: len((supervisor_dir / f).read_text().splitlines()) for aid, f in files.items()}
    pattern = re.compile(r"^L([1-9][0-9]*)(?:-L([1-9][0-9]*))?$")
    out: dict[str, list[str]] = {}
    for path in collect_assessments(config):
        problems: list[str] = []

        def walk(node: object) -> None:
            if isinstance(node, dict):
                if "locator" in node and "artifact_id" in node:
                    aid, loc = str(node["artifact_id"]), str(node["locator"])
                    match = pattern.match(loc)
                    if aid not in lengths:
                        problems.append(f"{aid}: unknown artifact_id")
                    elif not match:
                        problems.append(f"{aid} locator {loc[:60]!r}: must be exactly L<n> or L<n>-L<m>")
                    else:
                        start, end = int(match[1]), int(match[2] or match[1])
                        if start > end or end > lengths[aid]:
                            problems.append(f"{aid} locator {loc}: artifact has {lengths[aid]} lines (valid range L1-L{lengths[aid]})")
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        try:
            walk(json.loads(path.read_text()))
        except ValueError as exc:
            problems.append(f"file is not valid JSON: {exc}")
        out[path.name] = sorted(set(problems))
    return out


def request_rework(config: Path) -> dict:
    """Return a schema rejection to the same fresh supervisor transcript; content stays the supervisor's."""
    validation = validate_assessments(config)
    rejected = {name: item["reason"] for name, item in validation.items() if item["status"] == "REJECTED"}
    diagnostics = locator_diagnostics(config)
    cfg = json.loads(config.read_text())
    if not rejected and len(validation) == 2:
        return {"status": "NO_REWORK_NEEDED", "validation": validation}
    control = config.parent
    state_path = control / "controller-state.json"
    state = json.loads(state_path.read_text())
    if state.get("rework") and state.get("status") != "CONCLUSION_SUBMITTED":
        # An earlier rework instruction is already in task.md; the session was interrupted before answering it.
        return {"status": "REWORK_PENDING_RESUME", "rework": state["rework"], "controller_status": state.get("status")}
    if state.get("status") != "CONCLUSION_SUBMITTED" or state.get("pending"):
        raise RuntimeError("rework requires a submitted, non-pending supervisor session")
    task_path = control / "task.md"
    task = task_path.read_text()
    rework_round = task.count("## Validator rejection") + 1
    lines = [f"- {name}: {reason}" for name, reason in sorted(rejected.items())]
    for name, problems in sorted(diagnostics.items()):
        lines.extend(f"  - {name}: {problem}" for problem in problems)
    if len(validation) < 2:
        lines.append(f"- only {len(validation)} of 2 assessment files exist; one file per candidate is required")
    task += (f"\n## Validator rejection {rework_round}\n"
             "The fixed assessment validator rejected your files. Only the schema is enforced; your scientific judgment is unchanged.\n"
             + "\n".join(lines) + "\n"
             "Rules: every evidence \"locator\" string must be exactly L<n> or L<n>-L<m> (1-based line numbers inside the cited artifact, m not beyond the artifact's last line) and nothing else; move explanations into rationale, impact, minimum_fix or recheck text. Each artifact_id/sha256 pair must match packet.json. "
             "Do not change dimension statuses, severities, findings or your selection unless the evidence requires it. Rewrite each assessment-<candidate_id>.json in place with the ipython tool, then call finish again with the same selection.\n")
    task_path.write_text(task)
    state["status"] = "ASSESSMENT_SCHEMA_REWORK"
    state["rework"] = {"round": rework_round, "rejected": rejected, "diagnostics": diagnostics, "at": utc_now()}
    tmp = state_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.chmod(0o600)
    tmp.replace(state_path)
    Store(ROOT / "control/state.sqlite").event({"event": "assessment_schema_rework_requested", "project_id": cfg["campaign_id"],
                                               "session_id": state["session_id"], "rework_round": rework_round, "rejected": rejected})
    return {"status": "REWORK_REQUESTED", "rework_round": rework_round, "rejected": rejected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id", nargs="?")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--rework-config", type=Path, help="existing supervisor config: validate, return rejections, resume the same session")
    args = parser.parse_args()
    if args.rework_config is not None:
        out = {"rework": request_rework(args.rework_config)}
        if out["rework"]["status"] in ("REWORK_REQUESTED", "REWORK_PENDING_RESUME"):
            out["summary"] = run_supervisor(args.rework_config)
            out["validation"] = validate_assessments(args.rework_config)
        print(json.dumps(out, indent=2))
        return
    if args.campaign_id is None:
        parser.error("campaign_id is required unless --rework-config is given")
    info = prepare_round(args.campaign_id)
    config = prepare_supervisor_session(args.campaign_id, info)
    out = {"round": info, "supervisor_config": str(config)}
    if not args.prepare_only:
        out["summary"] = run_supervisor(config)
        out["validation"] = validate_assessments(config)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
