"""Trusted host tools for isolated Prime research sessions."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

from .contracts import canonical, utc_now, write_new
from .dispatch import FIXED_COMMAND, ROOT, dispatch
from .orx_adapter import OrxAdapter, RunReference
from .runner import DOCKER
from .model_billing import (anthropic_included_allocation, anthropic_subscription_snapshot,
                            codex_subscription_snapshot, included_subscription_allocation)


SUBSCRIPTION_PROVIDERS = ("openai-codex", "anthropic")


def subscription_route(provider: str):
    # Resolved at call time so test seams that patch module attributes remain effective.
    if provider == "anthropic":
        return anthropic_subscription_snapshot, anthropic_included_allocation
    return codex_subscription_snapshot, included_subscription_allocation
from .state import AdmissionError, Store


def original_reservation(receipt: dict) -> dict:
    """Each UNKNOWN settlement wraps the previous receipt; the admission-time reservation is the innermost one."""
    node = receipt
    while isinstance(node.get("reservation"), dict) and "before" not in node:
        node = node["reservation"]
    return node


def config(path: Path) -> dict:
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT / "control"):
        raise AdmissionError("private controller configuration required")
    cfg = json.loads(path.read_text())
    workspace = Path(cfg["workspace"])
    if workspace != workspace.resolve() or not workspace.is_relative_to(ROOT / "sessions"):
        raise AdmissionError("session workspace boundary")
    if cfg["condition"] not in ("B", "H", "P") or cfg["deadline_epoch"] <= time.time():
        raise AdmissionError("campaign condition or deadline")
    return cfg


def scope(cfg: dict, store: Store) -> dict:
    snapshot = store.snapshot()
    records = [r for r in snapshot["records"] if r["project_id"] == cfg["campaign_id"] and
               (r["type"] == "ResearchContract" or r.get("team_id") == cfg["team_id"])]
    events = [e for e in snapshot["events"] if e.get("project_id") == cfg["campaign_id"] and e.get("team_id") == cfg["team_id"]]
    return {"records": records, "events": events, "model_pool": cfg["model_pool"],
            "unknown_charges": sum(x["state"] == "UNKNOWN" for x in snapshot["charges"]),
            "spent_or_reserved_krw": sum(x["actual"] if x["actual"] is not None else x["reserved"] for x in snapshot["charges"])}


def execute(cfg: dict, action: str, args: dict) -> dict:
    store = Store(ROOT / "control/state.sqlite")
    project = cfg["campaign_id"]
    store.start_project(project)
    event = {"project_id": project, "team_id": cfg["team_id"], "session_id": cfg["session_id"], "model_id": cfg["model_id"]}
    if action == "read_state":
        return {"status": "READY", **scope(cfg, store)}
    if action == "reserve_model":
        model = next((x for x in cfg["model_pool"] if x["id"] == args["model_id"]), None)
        if not model or model.get("status") != "QUALIFIED" or model.get("billing_authorized") is not True or not model.get("billing_basis"):
            raise AdmissionError("model request and billing qualification missing")
        before = None
        if model["provider"] in SUBSCRIPTION_PROVIDERS and model.get("billing_mode") == "subscription":
            if args["upper_krw"] != 0:
                raise AdmissionError("included subscription uses checked entitlement, not guessed price")
            before = subscription_route(model["provider"])[0](Path(cfg["auth_path"]))
            if before.get("status") != "AVAILABLE_INCLUDED_ONLY":
                return {"status": "BLOCKED", "reason": "included entitlement unavailable or unconfirmed", "snapshot": before}
        elif model["provider"] == "openrouter" and model.get("billing_mode") == "paid":
            prompt = model["max_prompt_usd_per_million"]
            completion = model["max_completion_usd_per_million"]
            rate = model["accounting_rate_krw_per_usd"]
            upper = math.ceil((args["input_upper_tokens"] * prompt + args["output_limit"] * completion) / 1000000 * rate)
            if args["upper_krw"] != upper or args["output_limit"] != model["max_output_tokens"]:
                raise AdmissionError("derived provider reservation mismatch")
        else:
            raise AdmissionError("billing route unsupported")
        # Dead controller reservations are never silently released on a new session.
        for charge in store.snapshot()["charges"]:
            if charge["state"] == "RESERVED" and charge["receipt"]:
                owner = json.loads(charge["receipt"]).get("owner_pid")
                if type(owner) is int:
                    try:
                        os.kill(owner, 0)
                    except ProcessLookupError:
                        store.settle_charge(charge["id"], None, {"reason": "owner exited with unsettled request"})
        store.reserve_charge(args["request_id"], project, cfg.get("budget_phase", "first_week"), args["upper_krw"],
                             {"before": before, "model_id": model["id"], "provider": model["provider"], "session_id": cfg["session_id"], "owner_pid": args.get("owner_pid"), "billing_mode": model["billing_mode"]})
        store.event({**event, "event": "model_request_reserved", **args})
        return {"status": "RESERVED"}
    if action == "settle_model":
        # SDK cost estimates and zero-filled errors are not invoice evidence.
        actual = None
        charge = next((r for r in store.snapshot()["charges"] if r["id"] == args["request_id"]), None)
        if not charge or charge["project"] != project:
            raise AdmissionError("model settlement identity mismatch")
        if charge["state"] == "SETTLED":
            # Idempotent: a prior controller already settled this request against trusted evidence.
            return {"status": "SETTLED", "actual_krw": charge["actual"], "already_settled": True}
        reservation = json.loads(charge["receipt"]) if charge["receipt"] else {}
        entitlement = None
        if reservation.get("billing_mode") == "subscription":
            snapshot, allocate = subscription_route(reservation.get("provider", "openai-codex"))
            after = snapshot(Path(cfg["auth_path"]))
            entitlement = allocate(reservation.get("before") or {}, after, args.get("usage") or {})
            actual = entitlement["actual_krw"]
        elif args.get("provider_invoice") and isinstance(args.get("actual_krw"), int) and not isinstance(args["actual_krw"], bool):
            actual = args["actual_krw"]
        store.settle_charge(args["request_id"], actual, {"reservation": reservation, "usage": args.get("usage"), "provider_invoice": args.get("provider_invoice"), "subscription_entitlement": entitlement, "scope": "SDK cost ignored; raw paid invoice or trusted pre/post included-entitlement observations"})
        store.event({**event, "event": "model_request_settled", **args, "actual_krw": actual})
        return {"status": "SETTLED" if actual is not None else "UNKNOWN", "additional_dispatch": actual is not None}
    if action == "reconcile_subscription":
        # Post-hoc entitlement reconciliation: a fresh trusted snapshot with the cumulative extra-usage
        # counter still zero evidences that unknown subscription requests added no charge.
        settled = []
        for charge in store.snapshot()["charges"]:
            receipt = json.loads(charge["receipt"]) if charge["receipt"] else {}
            reservation = original_reservation(receipt)
            if charge["state"] != "UNKNOWN" or reservation.get("billing_mode") != "subscription" or reservation.get("provider") not in SUBSCRIPTION_PROVIDERS:
                continue
            snapshot, allocate = subscription_route(reservation["provider"])
            after = snapshot(Path(cfg["auth_path"]))
            entitlement = allocate(reservation.get("before") or {}, after, {"usage_status": "UNKNOWN"})
            if entitlement["actual_krw"] == 0:
                store.settle_charge(charge["id"], 0, {"reservation": reservation, "previous_settlement": receipt, "reconciliation": entitlement, "scope": "post-hoc entitlement; tokens unobserved"})
                settled.append(charge["id"])
        store.event({**event, "event": "subscription_reconciliation", "settled": settled})
        return {"status": "RECONCILED", "settled": settled}
    if action == "reconcile_compute":
        # A kernel lease left UNKNOWN by a watchdog that reached its deadline while the container was already
        # gone is bounded by its reservation: the container cannot have run longer than the lease window.
        settled = []
        for lease in store.snapshot()["compute"]:
            if lease["state"] != "UNKNOWN" or lease["project"] != project or not lease["id"].startswith("kernel-"):
                continue
            receipt = json.loads(lease["receipt"]) if lease["receipt"] else {}
            if receipt.get("terminal") is not True or receipt.get("container_absent") is not True:
                continue
            container = lease["id"].replace("kernel-", "project-research-kernel-")
            if subprocess.run([DOCKER, "ps", "-aq", "--filter", f"name=^{container}$"], capture_output=True, text=True, timeout=15).stdout.strip():
                continue
            store.settle_compute(lease["id"], float(lease["reserved"]), {**receipt, "reconciliation": "wall-bounded by reservation; container verified absent",
                                                                      "usage_basis": "reserved_upper_bound"})
            settled.append(lease["id"])
        store.event({**event, "event": "compute_reconciliation", "settled": settled})
        return {"status": "RECONCILED", "settled": settled}
    if action == "choose_model":
        allowed = {m["id"] for m in cfg["model_pool"] if m.get("status") == "QUALIFIED"}
        if args["model_id"] not in allowed or args["model_id"] in cfg.get("unavailable_models", []) or not args.get("reason"):
            raise AdmissionError("alternative model is unavailable or unqualified")
        store.event({**event, "event": "model_change_requested", "next_model": args["model_id"], "reason": args["reason"]})
        return {"status": "MODEL_CHANGE_REQUESTED", "model_id": args["model_id"], "new_session_required": True}
    if action == "run_experiment":
        path = Path(cfg["workspace"]) / args["relative_source"]
        if path != path.resolve() or not path.is_relative_to(Path(cfg["workspace"])) or path.suffix != ".py" or not path.is_file() or path.stat().st_nlink != 1:
            raise AdmissionError("candidate source must be one local regular Python file")
        source = path.read_bytes()
        if args.get("source_sha256") != hashlib.sha256(source).hexdigest():
            raise AdmissionError("candidate changed after controller yielded; new decision required")
        if len(source) > 262144 or not isinstance(args.get("hypothesis"), str) or not args["hypothesis"].strip():
            raise AdmissionError("bounded source and hypothesis required")
        intent_id = hashlib.sha256(source + canonical(args).encode()).hexdigest()
        intent_file = Path(cfg["control_dir"]) / "scientific-intents" / f"{intent_id}.json"
        if intent_file.exists():
            saved = json.loads(intent_file.read_text())
            if "orx" not in saved:
                return {"status": "UNKNOWN", "reason": "previous experiment submission requires reconciliation"}
            record = saved["orx"]
        else:
            seconds = min(600, int(cfg["deadline_epoch"] - time.time() - 30))
            if seconds < 30:
                raise AdmissionError("insufficient time for bounded experiment")
            write_new(intent_file, {"state": "SUBMITTING", "candidate_sha256": hashlib.sha256(source).hexdigest(), "hypothesis": args["hypothesis"]})
            spec = {"mode": "candidate", "project_id": project, "team_id": cfg["team_id"], "domain": cfg["domain"],
                    "worker_root": str(ROOT / "worker"), "image": cfg["image"], "timeout_seconds": seconds,
                    "arguments": [cfg["domain"]], "hypothesis": args["hypothesis"]}
            record = dispatch(spec, "candidate-" + intent_id[:16], candidate=source)
            intent_file.write_text(json.dumps({"state": "SUBMITTED", "orx": record}, indent=2) + "\n")
        adapter = OrxAdapter(cfg["project_id"], FIXED_COMMAND)
        identity = record["identity"]
        launch_intent_path = Path(record["intent_path"])
        while time.time() < cfg["deadline_epoch"]:
            record = adapter.attach_or_run(identity["experiment_id"], identity["commit_sha"], launch_intent_path)
            if record["state"] == "UNKNOWN":
                return {"status": "UNKNOWN", "reason": "ORX launch needs reconciliation"}
            ref = RunReference(**record["reference"])
            if ref.status in ("done", "failed", "cancelled"):
                raw = adapter.logs(ref)
                try:
                    result = json.loads(raw.decode().strip().splitlines()[-1])
                except (ValueError, IndexError):
                    return {"status": "FAILED", "run_id": ref.run_id, "reason": "missing structured result"}
                store.event({**event, "event": "hypothesis_observation", "run_id": ref.run_id, "experiment_id": ref.experiment_id,
                             "receipt_sha256": hashlib.sha256(raw).hexdigest(), "result_status": result.get("status"), "hypothesis": args["hypothesis"]})
                if result.get("status") == "BLOCKED" and result.get("scope") == "INFRASTRUCTURE_FAILURE":
                    # The runner refused to measure (for example a competing science container). The refusal is
                    # preserved under this decision; the team may resubmit the same source as a new decision.
                    retired = intent_file.with_name(intent_file.stem + f".deferred-{ref.run_id[:8]}.json")
                    intent_file.replace(retired)
                    store.event({**event, "event": "experiment_deferred_by_infrastructure", "run_id": ref.run_id,
                                 "experiment_id": ref.experiment_id, "reason": result.get("reason"), "retired_intent": str(retired)})
                    return {"status": "DEFERRED", "run_id": ref.run_id, "experiment_id": ref.experiment_id,
                            "receipt_sha256": hashlib.sha256(raw).hexdigest(), "reason": result.get("reason"),
                            "retry": "The measurement host refused this run before your code executed; call run_experiment again (unchanged source is fine). The refused run stays on record."}
                # The team receives its own run's outputs; the receipt file itself stays host-side.
                output_dir = Path(result["output_path"]) if isinstance(result.get("output_path"), str) else None
                artifacts = {}
                if output_dir and output_dir.is_dir():
                    for p in sorted(output_dir.iterdir()):
                        if p.is_file() and p.name not in ("receipt.json", "resource.json", "watchdog.json") and p.stat().st_size <= 262144:
                            artifacts[p.name] = p.read_text(errors="replace")
                return {"status": result.get("status", "UNKNOWN"), "run_id": ref.run_id, "experiment_id": ref.experiment_id,
                        "receipt_sha256": hashlib.sha256(raw).hexdigest(), "result": result.get("result"), "resources": result.get("resources"),
                        "exit_code": result.get("exit_code"), "output_files": result.get("output_files"), "artifacts": artifacts,
                        "validation_scope": "EXECUTED_UNVALIDATED means the code ran to completion in isolation; scientific claims still need your own verification and the separate review."}
            time.sleep(1)
        return {"status": "UNKNOWN", "reason": "deadline: reconcile existing ORX run; do not rerun"}
    if action == "checkpoint":
        state = scope(cfg, store)
        observed = [x for x in state["events"] if x.get("event") == "hypothesis_observation"]
        evidence_text = " ".join(str(x) for x in args.get("observation_evidence", []))
        bound = [x for x in observed if x["receipt_sha256"] in evidence_text or x["run_id"] in evidence_text]
        if args["first_hypothesis_observed"] and not bound:
            raise AdmissionError("checkpoint observation must bind a real team ORX receipt")
        runs = [{"experiment_id": x["experiment_id"], "run_id": x["run_id"], "status": x["result_status"]} for x in observed]
        rec = {"type": "Checkpoint", "id": "checkpoint-" + uuid.uuid4().hex, "project_id": project, "created_at": utc_now(),
               "team_id": cfg["team_id"], "model_id": cfg["model_id"], "session_id": cfg["session_id"],
               "tool_versions": {"image": cfg["image"]}, "budget": {"used_or_reserved_krw": state["spent_or_reserved_krw"], "unknown_count": state["unknown_charges"]},
               "orx_runs": runs, **{k: args[k] for k in ("question", "artifacts", "uncertainties", "confirmed_decisions", "first_hypothesis_observed", "observation_evidence")}}
        store.append(rec)
        return {"status": "CHECKPOINTED", "checkpoint_id": rec["id"], "continuity_trigger_ready": bool(cfg.get("continuity") and observed)}
    if action == "finish":
        if not args.get("conclusion") or not isinstance(args.get("claims"), list) or not isinstance(args.get("limitations"), list):
            raise AdmissionError("conclusion, claims and limitations required")
        result = {"at": utc_now(), "status": "CANDIDATE_SUBMITTED", "quality": "UNASSESSED", "superiority": "NOT_ASSESSED", "pi_acceptance": "PENDING", **event, **args}
        write_new(Path(cfg["control_dir"]) / ("candidate-" + uuid.uuid4().hex + ".json"), result)
        store.event({**event, "event": "candidate_submitted", "quality": "UNASSESSED"})
        return result
    raise AdmissionError("unknown host action")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("action")
    args = parser.parse_args()
    try:
        value = execute(config(args.config), args.action, json.load(sys.stdin))
    except (AdmissionError, ValueError, KeyError) as exc:
        value = {"status": "BLOCKED", "reason": str(exc)}
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
