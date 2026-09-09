"""Prospective programme configuration; never labels planned campaigns as runs."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import digest, make_contract, utc_now, write_new
from .state import Store


def initialize(root: Path, model_pool: dict) -> dict:
    control = root / "control"
    programme_path = control / "programme.json"
    if programme_path.exists():
        raise ValueError("programme already initialized; budgets and clocks do not reset")
    now = datetime.now(timezone.utc)
    pool_digest = digest(model_pool)
    campaigns = []
    for stage, conditions in (("first_week", ("B", "P")), ("comparison", ("B", "H", "P"))):
        for continuity in (False, True):
            for domain in ("wine", "duckdb", "diffusion"):
                for condition in conditions:
                    campaign_id = f"{stage}-{domain}-{condition}-{'continuity' if continuity else 'normal'}"
                    campaigns.append({"id": campaign_id, "stage": stage, "domain": domain,
                                      "condition": condition, "continuity": continuity, "status": "PLANNED",
                                      "quality": "UNASSESSED", "superiority": "NOT_ASSESSED", "pi_acceptance": "PENDING"})
    programme = {"schema": "project-research-programme/v1", "created_at": utc_now(), "execution_resumed_at": now.isoformat(),
                 "first_real_experiment_due": (now + timedelta(hours=12)).isoformat(),
                 "first_report_due": (now + timedelta(days=7)).isoformat(),
                 "additional_budget_krw": 300000, "phase_budgets_krw": {"first_week": 150000, "comparison": 90000, "reserve": 60000},
                 "aggregate_limits": {"cpus": 4, "memory_mib": 4608}, "model_pool_digest": pool_digest,
                 "primary_outcome": "PI accepted project completion within resource limits", "campaigns": campaigns,
                 "native_construction_authorized": False, "study_unit": "coherent research project", "do_not_claim_sota": True,
                 "comparison_admission": "freeze selected P; independent final/future data; normal comparisons before continuity",
                 "prior_design": "paper/research/study-design-20260909/protocol-v2.json (preserved predecessor)",
                 "study_campaigns_completed": 0}
    control.mkdir(parents=True, mode=0o700)
    (root / "worker").mkdir(exist_ok=True, mode=0o700)
    (root / "evaluator").mkdir(exist_ok=True, mode=0o700)
    store = Store(control / "state.sqlite")
    write_new(control / "model-pool.json", model_pool)
    for campaign in campaigns:
        contract = make_contract(campaign["id"], campaign["domain"], campaign["condition"], campaign["continuity"], pool_digest)
        write_new(control / "contracts" / f"{campaign['id']}.json", contract)
        store.append(contract)
    for domain in ("wine", "duckdb", "diffusion"):
        contract = make_contract(f"development-{domain}", domain, "B", False, pool_digest)
        contract["constraints"].append("preparation development measurement, not an autonomous comparison campaign")
        store.append(contract)
        write_new(control / "contracts" / f"development-{domain}.json", contract)
    write_new(programme_path, programme)
    return programme


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-pool", type=Path, required=True)
    args = parser.parse_args()
    programme = initialize(args.root, json.loads(args.model_pool.read_text()))
    print(json.dumps({"created_at": programme["created_at"], "campaigns_planned": len(programme["campaigns"]), "campaigns_completed": 0}))


if __name__ == "__main__":
    main()
