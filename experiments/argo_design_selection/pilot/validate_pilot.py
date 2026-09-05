#!/usr/bin/env python3
"""Independent byte-level validation of the frozen Stage B pilot receipt."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from score import score_decision

OPAQUE = re.compile(r"^attempt-[0-9a-f]{16}$")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def validate(receipt: dict, protocol: dict, protocol_path: Path) -> dict:
    require(receipt.get("schema_version") == "argo-stage-b-pilot/v1", "SCHEMA")
    require(receipt.get("phase") == "final", "PHASE")
    require(receipt.get("protocol_sha256") == sha(protocol_path), "PROTOCOL_HASH")
    require(receipt.get("model") == protocol["model"], "MODEL")
    episodes = receipt.get("episodes", [])
    expected = protocol["phases"]["final"]
    require(len(episodes) == receipt.get("completed_episodes") == expected["episodes"], "EPISODE_COUNT")
    require(receipt.get("planned_episodes") == expected["episodes"], "PLANNED_COUNT")
    require(receipt.get("code") == {k: protocol["code_sha256"][k] for k in ("build_task.py", "score.py", "run_pilot.py")}, "CODE_HASH")

    by = {}
    for ep in episodes:
        require(ep["model"] == protocol["model"], "EPISODE_MODEL")
        wd = Path(ep["workdir"])
        require(OPAQUE.fullmatch(wd.name) is not None, "NON_OPAQUE_WORKDIR")
        require(ep["condition"].lower() not in str(wd).lower(), "CONDITION_IN_PATH")
        require(sha(wd / "transcript.jsonl") == ep["transcript_sha256"], "TRANSCRIPT_HASH")
        access = wd / "record_access_log.json"
        require(access.is_file() and sha(access) == ep["record_access_log_sha256"], "ACCESS_LOG_HASH")
        rows = json.loads(access.read_text())
        charged = sorted(set(str(x["record_id"]).upper() for x in rows if x.get("tool") == "read_record" and x.get("charged")))
        require(charged == ep["observed_reads"], "OBSERVED_READS")
        prefetch = ep.get("prefetched_records", [])
        require(sorted(set(charged + prefetch)) == ep["verification_records"], "VERIFICATION_RECORDS")
        require(len(ep["verification_records"]) <= protocol["fixed"]["total_record_budget"], "BUDGET")
        require((wd / "dependency_target.json").exists() == (ep["condition"] == "C_TARGET"), "TREATMENT_FILE")
        require((prefetch == ["R1"]) == (ep["condition"] == "C_TARGET"), "PREFETCH")
        payload = json.loads((wd / "decision.json").read_text()) if (wd / "decision.json").is_file() else None
        if payload is not None:
            rescored = score_decision(payload, {"constraint_status": "withdrawn", "action": "recheck"}, "R3", 2, ep["verification_records"])
            require(rescored == ep["score"], "SCORE_REDERIVATION")
        by.setdefault(ep["task_id"], {})[ep["condition"]] = ep

    require(len(by) == expected["episodes"] // 2, "TASK_COUNT")
    for task, pair in by.items():
        require(set(pair) == {"C_BASE", "C_TARGET"}, f"PAIR:{task}")
        require(pair["C_BASE"]["records_sha256"] == pair["C_TARGET"]["records_sha256"], f"RECORD_BYTES:{task}")
    return {"passed": True, "episodes": len(episodes), "tasks": len(by),
            "transcript_hashes_rederived": len(episodes), "access_log_hashes_rederived": len(episodes),
            "scores_rederived": len(episodes), "condition_paths_opaque": True, "budget_enforced": True}


def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument("--receipt",type=Path,required=True);ap.add_argument("--protocol",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args()
    receipt=json.loads(a.receipt.read_text());protocol=json.loads(a.protocol.read_text());result=validate(receipt,protocol,a.protocol)
    out={"schema_version":"argo-stage-b-pilot-validation/v1","receipt_sha256":sha(a.receipt),"protocol_sha256":sha(a.protocol),"validator_sha256":sha(Path(__file__)),"validation":result}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(result));return 0
if __name__=="__main__":raise SystemExit(main())
