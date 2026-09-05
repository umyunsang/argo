#!/usr/bin/env python3
"""Zero-cost non-isomorphic task pack for a future decision-sufficiency study.

Both conditions receive one prefetched record, one remaining record-read slot,
and byte-equal allocation files. The only declared difference is whether the
allocation policy selected a decision-relevant record or a deterministic decoy.
"""
from __future__ import annotations
import hashlib, json
from collections import defaultdict, deque
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from targeting import oracle_target  # noqa: E402

FAMILIES = ("single_withdrawal", "alternate_support", "multi_hop_withdrawal", "unrelated_withdrawal")


def _node(i, k): return {"id": i, "kind": k, "scope": "study"}
def _edge(i, s, t): return {"id": i, "source": s, "target": t, "relation": "depends_on", "scope": "study"}


def family(name: str) -> dict:
    common_records = {
        "R5": "Record R5. Formatting notes only; no claim about the active decision.",
        "R6": "Record R6. Storage notes only; no claim about the active decision.",
    }
    if name == "single_withdrawal":
        records = {**common_records,
            "R1": "Record R1. Earlier support for setting alpha. Current-status pointer: R3.",
            "R3": "Record R3. Setting alpha is withdrawn after a prospective failure.",
            "M": "Record M. Settled constraint: use setting alpha. Supported only by R1."}
        nodes=[_node("R1","source"),_node("R3","source"),_node("R5","source"),_node("R6","source"),_node("M","claim"),_node("D","decision"),_node("A","action")]
        edges=[_edge("e:R1-M","R1","M"),_edge("e:M-D","M","D"),_edge("e:D-A","D","A")]
        roots=["R1","R3","R5","R6"];removed=["e:R1-M"];target_record="R1";decoy="R5";critical="R3";truth={"constraint_status":"withdrawn","action":"recheck"};decision="D"
    elif name == "alternate_support":
        records = {**common_records,
            "R1": "Record R1. Earlier support for setting beta; this support was retired.",
            "R2": "Record R2. Independent current replication still supports setting beta.",
            "M": "Record M. Settled constraint: use setting beta. Supported by R1 and R2."}
        nodes=[_node("R1","source"),_node("R2","source"),_node("R5","source"),_node("R6","source"),_node("M","claim"),_node("D","decision"),_node("A","action")]
        edges=[_edge("e:R1-M","R1","M"),_edge("e:R2-M","R2","M"),_edge("e:M-D","M","D"),_edge("e:D-A","D","A")]
        roots=["R1","R2","R5","R6"];removed=["e:R1-M"];target_record="R2";decoy="R5";critical="R2";truth={"constraint_status":"valid","action":"proceed"};decision="D"
    elif name == "multi_hop_withdrawal":
        records = {**common_records,
            "R1": "Record R1. Measurement supports claim C. Current-status pointer: R4.",
            "R4": "Record R4. The measurement in R1 failed recalibration and is withdrawn.",
            "C": "Record C. Intermediate claim derived only from R1.",
            "M": "Record M. Constraint gamma is derived through claim C."}
        nodes=[_node("R1","source"),_node("R4","source"),_node("R5","source"),_node("R6","source"),_node("C","claim"),_node("M","claim"),_node("D","decision"),_node("A","action")]
        edges=[_edge("e:R1-C","R1","C"),_edge("e:C-M","C","M"),_edge("e:M-D","M","D"),_edge("e:D-A","D","A")]
        roots=["R1","R4","R5","R6"];removed=["e:R1-C"];target_record="R1";decoy="R6";critical="R4";truth={"constraint_status":"withdrawn","action":"recheck"};decision="D"
    elif name == "unrelated_withdrawal":
        records = {**common_records,
            "R1": "Record R1. Independent current evidence supports setting delta.",
            "R3": "Record R3. An unrelated logging recommendation was withdrawn.",
            "M": "Record M. Settled constraint: use setting delta. Supported by R1.",
            "U": "Record U. Logging recommendation supported by R3."}
        nodes=[_node("R1","source"),_node("R3","source"),_node("R5","source"),_node("R6","source"),_node("M","claim"),_node("D","decision"),_node("A","action"),_node("U","claim")]
        edges=[_edge("e:R1-M","R1","M"),_edge("e:M-D","M","D"),_edge("e:D-A","D","A"),_edge("e:R3-U","R3","U")]
        roots=["R1","R3","R5","R6"];removed=["e:R3-U"];target_record="R1";decoy="R5";critical="R1";truth={"constraint_status":"valid","action":"proceed"};decision="D"
    else: raise ValueError(name)
    graph={"schema_version":"argo-dependency-targeting-instance/v1","family":name,"instance_id":"task-"+name,"seed":None,"roots":roots,"nodes":nodes,"edges":edges,"event":{"removed_edge_ids":removed,"kind":"source_support_withdrawn"}}
    affected=sorted(oracle_target(graph));return {"name":name,"graph":graph,"records":records,"target_record":target_record,"decoy_record":decoy,"critical_record":critical,"truth":truth,"decision_node":decision,"oracle_affected":affected}


def signature(spec: dict) -> str:
    g=spec["graph"];payload={"kinds":sorted(n["kind"] for n in g["nodes"]),"edges":sorted((next(n["kind"] for n in g["nodes"] if n["id"]==e["source"]),next(n["kind"] for n in g["nodes"] if n["id"]==e["target"])) for e in g["edges"]),"removed_count":len(g["event"]["removed_edge_ids"]),"affected_count":len(spec["oracle_affected"])};return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def _allocation(record_id: str, content: str, length: int = 512) -> bytes:
    obj={"allocated_record":{"id":record_id,"content":content},"allocated_slots":1,"remaining_record_reads":1,"policy":"verification allocation","padding":""}
    raw0=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()
    if len(raw0)>length:raise ValueError("ALLOCATION_TOO_LONG")
    obj["padding"]="x"*(length-len(raw0))
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()
    if len(raw)!=length:raise ValueError("ALLOCATION_LENGTH")
    return raw


def build(name: str, condition: str, out: Path) -> dict:
    if condition not in ("C_BASE","C_TARGET"):raise ValueError(condition)
    s=family(name);out.mkdir(parents=True,exist_ok=True);rdir=out/"records";rdir.mkdir()
    for k,v in s["records"].items():(rdir/f"{k}.txt").write_text(v+"\n")
    index={"records":sorted(s["records"]),"provenance":"record bodies must be opened; no status is summarized","total_record_budget":2}
    (out/"index.json").write_text(json.dumps(index,sort_keys=True)+"\n")
    rid=s["target_record"] if condition=="C_TARGET" else s["decoy_record"]
    (out/"allocation.json").write_bytes(_allocation(rid,s["records"][rid]))
    (out/"budget.json").write_text(json.dumps({"total_verification_budget":2,"prefetched_records":[rid],"remaining_record_reads":1})+"\n")
    task=("Read index.json and allocation.json. One verification slot has already prefetched the allocated record; "
          "you may open one additional record. Decide whether the active settled constraint is valid or withdrawn. "
          "Use only read_index, read_allocation, read_record, and write_decision. Output the fixed decision schema.")
    (out/"TASK.md").write_text(task+"\n")
    return {"family":name,"condition":condition,"truth":s["truth"],"target_record":s["target_record"],"critical_record":s["critical_record"],"allocated_record":rid,"oracle_affected":s["oracle_affected"],"structural_signature":signature(s),"allocation_bytes":(out/"allocation.json").stat().st_size,"task_sha256":hashlib.sha256((task+"\n").encode()).hexdigest()}


def schedule():
    return [(name, cond) for i,name in enumerate(FAMILIES) for cond in (("C_BASE","C_TARGET") if i%2==0 else ("C_TARGET","C_BASE"))]
