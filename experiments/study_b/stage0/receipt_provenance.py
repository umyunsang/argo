#!/usr/bin/env python3
"""Fail-closed validation of model/verifier receipt provenance and referenced bytes."""
from __future__ import annotations
import datetime as dt, hashlib, re
from pathlib import Path
class ProvenanceViolation(ValueError):pass
REQUIRED=("origin","model_provider_revision","protocol_fingerprint","harness_commit","task_hash","command","environment_hash","transcript_paths","artifact_paths","started_at","finished_at","exit_state","usage")
HEX64=re.compile(r"^[0-9a-f]{64}$");HEX40=re.compile(r"^[0-9a-f]{40}$")
def require(ok:bool,msg:str)->None:
 if not ok:raise ProvenanceViolation(msg)
def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def check_paths(records:list,root:Path,kind:str)->int:
 require(isinstance(records,list) and bool(records),f"RECEIPT_{kind}_PATHS_MISSING")
 for rec in records:
  rel=rec.get("path") if isinstance(rec,dict) else None;require(isinstance(rel,str) and bool(rel),f"RECEIPT_{kind}_PATH_MISSING")
  p=(root/rel).resolve();require(p.is_relative_to(root.resolve()),f"RECEIPT_{kind}_PATH_ESCAPES_ROOT: {rel}")
  actual=digest(p) if p.is_file() else None;require(actual==rec.get("sha256"),f"RECEIPT_{kind}_IDENTITY_MISMATCH: {rel} registered={rec.get('sha256')} actual={actual}")
 return len(records)
def validate(receipt:dict,root:Path)->dict:
 for field in REQUIRED:require(field in receipt and receipt[field] is not None,f"RECEIPT_PROVENANCE_MISSING: {field}")
 require(receipt["origin"] in ("model_call","verifier","human"),f"RECEIPT_ORIGIN_INVALID: {receipt['origin']}")
 rev=receipt["model_provider_revision"];require(isinstance(rev,dict),"RECEIPT_PROVIDER_REVISION_MISSING")
 for field in ("model_id","api_revision","provider_revision"):require(isinstance(rev.get(field),str) and bool(rev[field]),f"RECEIPT_PROVIDER_REVISION_MISSING: {field}")
 require(bool(HEX64.fullmatch(str(receipt["protocol_fingerprint"]))),"RECEIPT_PROTOCOL_FINGERPRINT_INVALID")
 require(bool(HEX40.fullmatch(str(receipt["harness_commit"]))),"RECEIPT_HARNESS_COMMIT_INVALID")
 require(bool(HEX64.fullmatch(str(receipt["task_hash"]))),"RECEIPT_TASK_HASH_INVALID")
 require(bool(HEX64.fullmatch(str(receipt["environment_hash"]))),"RECEIPT_ENVIRONMENT_HASH_INVALID")
 cmd=receipt["command"];require(isinstance(cmd,list) and bool(cmd) and all(isinstance(x,str) and x for x in cmd),"RECEIPT_COMMAND_NOT_ARGV")
 try:start=dt.datetime.fromisoformat(receipt["started_at"]);finish=dt.datetime.fromisoformat(receipt["finished_at"])
 except (TypeError,ValueError) as exc:raise ProvenanceViolation(f"RECEIPT_TIMESTAMP_INVALID: {exc}") from exc
 require(start.tzinfo is not None and finish.tzinfo is not None,"RECEIPT_TIMESTAMP_TIMEZONE_MISSING")
 require(finish>=start,"RECEIPT_TIME_ORDER_INVALID")
 require(receipt["exit_state"] in ("success","agent_failure","infrastructure_failure","protocol_failure"),f"RECEIPT_EXIT_STATE_INVALID: {receipt['exit_state']}")
 usage=receipt["usage"];require(isinstance(usage,dict),"RECEIPT_USAGE_INVALID")
 for field in ("tokens","tool_calls","wall_seconds","cost_usd"):
  value=usage.get(field);require(isinstance(value,(int,float)) and not isinstance(value,bool) and value>=0,f"RECEIPT_USAGE_INVALID: {field}")
 nt=check_paths(receipt["transcript_paths"],root,"TRANSCRIPT");na=check_paths(receipt["artifact_paths"],root,"ARTIFACT")
 return {"passed":True,"transcript_count":nt,"artifact_count":na,"started_at":receipt["started_at"],"finished_at":receipt["finished_at"],"exit_state":receipt["exit_state"]}
