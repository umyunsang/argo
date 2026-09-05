#!/usr/bin/env python3
"""Task-paired descriptive analysis for the Stage B development pilot."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, statistics
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def endpoint(ep: dict) -> dict:
    s = ep.get("score") or {}
    complete = (ep.get("exit_code") == 0 and not ep.get("timed_out") and
                s.get("admissible") is True and s.get("budget_violation") is False)
    return {
        "nonstale_itt": int(complete and s.get("stale_consistent") is False),
        "correct_itt": int(complete and s.get("correct") is True),
        "partial_itt": int(complete and s.get("partial") is True),
        "critical_inspected_itt": int(complete and s.get("critical_inspected") is True),
        "complete": complete,
        "tokens": int((ep.get("usage") or {}).get("total_tokens", 0)),
        "duration_seconds": float(ep.get("duration_seconds", 0)),
    }


def analyze(receipt: dict, expected_tasks: int = 6) -> dict:
    rows = receipt["episodes"]
    by = {}
    for ep in rows:
        by.setdefault(ep["task_id"], {})[ep["condition"]] = endpoint(ep)
    if len(by) != expected_tasks or any(set(v) != {"C_BASE", "C_TARGET"} for v in by.values()):
        raise ValueError("PAIR_SET_INVALID")
    pairs = []
    for task, cond in sorted(by.items()):
        base, target = cond["C_BASE"], cond["C_TARGET"]
        pairs.append({"task_id": task, "base": base, "target": target,
                      "nonstale_delta": target["nonstale_itt"] - base["nonstale_itt"],
                      "correct_delta": target["correct_itt"] - base["correct_itt"],
                      "token_delta": target["tokens"] - base["tokens"]})
    def summ(key):
        xs = [p[key] for p in pairs]
        return {"values": xs, "mean": statistics.mean(xs), "positive": sum(x > 0 for x in xs),
                "zero": sum(x == 0 for x in xs), "negative": sum(x < 0 for x in xs)}
    return {"tasks": len(pairs), "episodes": len(rows), "pairs": pairs,
            "primary_nonstale_delta": summ("nonstale_delta"),
            "secondary_correct_delta": summ("correct_delta"),
            "token_delta": summ("token_delta"),
            "scope": "exploratory development direction; no confirmatory p-value or population claim"}


def main() -> int:
    ap = argparse.ArgumentParser();ap.add_argument("--receipt",type=Path,required=True);ap.add_argument("--protocol",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args()
    r=json.loads(a.receipt.read_text());p=json.loads(a.protocol.read_text())
    if r.get("protocol_sha256") != sha(a.protocol) or r.get("phase") != "final":raise ValueError("PROTOCOL_BINDING_INVALID")
    out={"schema_version":"argo-stage-b-pilot-analysis/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"receipt_path":str(a.receipt.resolve()),"receipt_sha256":sha(a.receipt),"protocol_path":str(a.protocol.resolve()),"protocol_sha256":sha(a.protocol),"analysis":analyze(r,p["phases"]["final"]["episodes"]//2)}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out["analysis"]["primary_nonstale_delta"],indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
