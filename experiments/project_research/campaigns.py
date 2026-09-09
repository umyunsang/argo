"""Prepare isolated sessions for prospective campaigns, without claiming execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import uuid
from pathlib import Path

from .contracts import digest, utc_now, write_new
from .dispatch import ROOT, SOURCE
from .state import Store


ROLES = {
    "research": "Read original sources and the mission. Refine the research question, identify competing mechanisms, and write a bounded experiment proposal with source locators. Do not read another team's artifacts.",
    "experiment": "Read only your own team's research proposal and common starting inputs. Implement and execute a falsifiable hypothesis through ORX. Preserve failures and alternative explanations. Write solution.py and a candidate report with real receipt locators.",
    "reproduction": "Independently rerun your own team's frozen candidate through ORX, compare outputs, check strong baselines and failure conditions. Do not edit original observations. Write a reproduction receipt with actual run ID and input/output/environment hashes.",
}


def prepare(campaign_id: str, *, qualifications: Path | None = None) -> dict:
    programme = json.loads((ROOT / "control/programme.json").read_text())
    campaign = next((c for c in programme["campaigns"] if c["id"] == campaign_id), None)
    if campaign is None:
        raise ValueError("campaign is not in the prospective programme")
    control = ROOT / "control/campaigns" / campaign_id
    if control.exists():
        return json.loads((control / "sessions.json").read_text())
    pool = json.loads((ROOT / "control/model-pool.json").read_text())
    choices = pool["members"]
    if qualifications is not None:
        qualified = json.loads(qualifications.read_text())
        if qualified.get("pool_digest") != digest(pool):
            raise ValueError("qualification must refer to the frozen common pool")
        by_id = {m["id"]: m for m in qualified["members"]}
        if set(by_id) - {m["id"] for m in choices}:
            raise ValueError("new model requires next comparison batch")
        choices = [{**m, **by_id.get(m["id"], {})} for m in choices]
    selected = next((m for m in choices if m.get("status") == "QUALIFIED"), choices[0])
    image = json.loads((ROOT / "control/environment.json").read_text())["image"]
    present = subprocess.run(["/opt/homebrew/bin/docker", "image", "inspect", image, "--format", "{{.Id}}"], capture_output=True, text=True, timeout=30)
    if present.returncode != 0 or present.stdout.strip() != image:
        raise ValueError(f"pinned research image {image} is absent from the local daemon; rebuild and re-pin before preparing sessions")
    project_id = json.loads((ROOT / "control/orx-project.json").read_text())["project"]["id"]
    contract = json.loads((ROOT / "control/contracts" / f"{campaign_id}.json").read_text())
    configs = []
    teams = ("team-1", "team-2") if campaign["condition"] == "P" else ("free",) if campaign["condition"] == "B" else ("fixed-roles",)
    roles = tuple(ROLES) if campaign["condition"] in ("P", "H") else ("free",)
    for team in teams:
        for role in roles:
            session_id = "session-" + uuid.uuid4().hex
            base = ROOT / "sessions" / campaign_id / team / role
            workspace, artifacts, private = base / "workspace", base / "artifacts", control / team / role
            for path in (workspace, artifacts, private):
                path.mkdir(parents=True, exist_ok=False, mode=0o700)
            task = f"Mission: {contract['mission']}\nDomain: {campaign['domain']}\n{ROLES.get(role, 'Freely organize the entire research project, including delegation and independent verification.')}\n"
            task += "Write candidate code in this workspace. Experimental Python runs with /workspace/wine as public wine data and /output as output directory. Use run_experiment to freeze source and invoke ORX. Output result JSON to /output/result.json. No direct host or hidden-data access is provided. Read the private controller's returned scientific receipts before making claims.\n"
            task += "Shared data schema: Wine CSV columns row_id,color,group_id,11 physicochemical features,quality; train.csv/dev.csv only. Other domains use pinned DuckDB/PyAMG libraries in the science container. Choose your question and method; provided baseline recipes do not limit hypothesis space.\n"
            write_new(workspace / "ResearchContract.json", contract)
            (private / "task.md").write_text(task)
            cfg = {"campaign_id": campaign_id, "project_id": project_id, "team_id": team, "role": role,
                   "domain": campaign["domain"], "condition": campaign["condition"], "continuity": campaign["continuity"],
                   "workspace": str(workspace), "artifact_root": str(artifacts), "control_dir": str(private),
                   "image": image, "model_pool": choices, "model_id": selected["id"], "session_id": session_id,
                   "deadline_epoch": time.time() + 28800, "budget_phase": campaign["stage"],
                   "common_prompt": str(SOURCE / "prompts/common.md"), "policy_prompt": str(SOURCE / "prompts" / f"{campaign['condition']}.md"),
                   "task_prompt": str(private / "task.md"), "auth_path": str(Path.home() / ".prime/agent/auth.json"),
                   "bridge_python": "/opt/homebrew/bin/python3", "max_controller_turns": 64,
                   "model_pool_digest": digest(pool), "tools_digest": hashlib.sha256((SOURCE / "campaign_bridge.py").read_bytes()).hexdigest()}
            write_new(private / "config.json", cfg)
            configs.append({"team": team, "role": role, "session_id": session_id, "config": str(private / "config.json")})
    result = {"created_at": utc_now(), "campaign_id": campaign_id, "status": "PREPARED_NOT_EXECUTED", "sessions": configs,
              "teams": list(teams), "launch_ready": all(m.get("status") == "QUALIFIED" for m in choices),
              "missing": ["live model/billing qualification" if selected.get("status") != "QUALIFIED" else "session execution",
                          "candidate-bound inter-role handoff", "blinded fresh supervisor execution", "independent final evaluation", "PI decision"]}
    write_new(control / "sessions.json", result)
    Store(ROOT / "control/state.sqlite").event({"event": "campaign_sessions_prepared", "project_id": campaign_id,
                                               "status": result["status"], "session_count": len(configs), "executed": False})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id")
    parser.add_argument("--qualifications", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.campaign_id, qualifications=args.qualifications), indent=2))


if __name__ == "__main__":
    main()
