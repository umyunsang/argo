#!/usr/bin/env python3
"""Condition-blind scorer payload and OS namespace/access-log validation."""
from __future__ import annotations
import hashlib,json,re
from pathlib import PurePosixPath
class BoundaryViolation(ValueError):pass
HEX64=re.compile(r"^[0-9a-f]{64}$");ATTEMPT=re.compile(r"^attempt-[0-9a-f]{16}$");CONDITION=re.compile(r"(?:^|[/_.-])(?:g[01]c[01]f[01]|b[012])(?:$|[/_.-])",re.I)
def require(ok:bool,msg:str)->None:
 if not ok:raise BoundaryViolation(msg)
def validate_scorer_payload(p:dict)->dict:
 allowed={"task_hash","attempt_id","output_files","scorer_hash","environment_hash"};extra=set(p)-allowed
 if extra:raise BoundaryViolation("SCORER_PAYLOAD_FORBIDDEN_FIELD: "+sorted(extra)[0])
 missing=allowed-set(p)
 if missing:raise BoundaryViolation("SCORER_PAYLOAD_MISSING_FIELD: "+sorted(missing)[0])
 for field in ("task_hash","scorer_hash","environment_hash"):require(isinstance(p[field],str) and bool(HEX64.fullmatch(p[field])),f"SCORER_PAYLOAD_HASH_INVALID: {field}")
 require(isinstance(p["attempt_id"],str) and bool(ATTEMPT.fullmatch(p["attempt_id"])),"SCORER_ATTEMPT_ID_NOT_OPAQUE")
 files=p["output_files"];require(isinstance(files,list) and bool(files),"SCORER_OUTPUT_FILES_MISSING")
 for rec in files:
  path=rec.get("path","");pp=PurePosixPath(path)
  require(not CONDITION.search(path),f"SCORER_PATH_CONDITION_LEAK: {path}")
  require(bool(path) and not pp.is_absolute() and ".." not in pp.parts and pp.parts[0]=="submission","SCORER_OUTPUT_PATH_NOT_NEUTRAL")
  require(isinstance(rec.get("sha256"),str) and bool(HEX64.fullmatch(rec["sha256"])),f"SCORER_OUTPUT_HASH_INVALID: {path}")
 return {"passed":True,"payload_sha256":scorer_payload_hash(p),"output_count":len(files)}
def scorer_payload_hash(p:dict)->str:return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def validate_namespace(m:dict)->dict:
 require(m.get("target_platform")=="linux-x86_64","ISOLATION_TARGET_PLATFORM_INVALID")
 require(isinstance(m.get("isolation_engine"),str) and bool(m["isolation_engine"]),"ISOLATION_ENGINE_MISSING")
 require(m.get("agent_network") is False,"AGENT_NETWORK_NOT_ISOLATED");require(m.get("scorer_network") is False,"SCORER_NETWORK_NOT_ISOLATED")
 oracle=set(m.get("oracle_source_ids",[]));agent=m.get("agent_mounts",[]);scorer=m.get("scorer_mounts",[]);require(bool(oracle),"ORACLE_SOURCE_IDS_MISSING")
 targets=set()
 for x in agent:
  require(x.get("source_id") not in oracle,f"ORACLE_MOUNT_EXPOSED: {x.get('source_id')} -> {x.get('target')}")
  require(x.get("role") in ("task_input","workspace","runtime","dependency"),f"AGENT_MOUNT_ROLE_INVALID: {x.get('role')}")
  require(x.get("target") not in targets,f"AGENT_MOUNT_TARGET_DUPLICATE: {x.get('target')}");targets.add(x.get("target"))
 roles={x.get("role"):x for x in scorer};require(set(roles)=={"scorer_code","gold","submission"},"SCORER_MOUNT_ROLE_SET_INVALID")
 require(roles["gold"].get("source_id") in oracle and roles["gold"].get("mode")=="ro","SCORER_GOLD_NOT_READ_ONLY")
 require(roles["scorer_code"].get("source_id") in oracle and roles["scorer_code"].get("mode")=="ro","SCORER_CODE_NOT_READ_ONLY")
 require(roles["submission"].get("mode")=="ro","SCORER_SUBMISSION_NOT_READ_ONLY")
 return {"passed":True,"agent_mount_count":len(agent),"scorer_mount_count":len(scorer),"oracle_source_ids":sorted(oracle)}
def validate_access_log(events:list,manifest:dict)->dict:
 require(isinstance(events,list) and bool(events),"OS_ACCESS_LOG_MISSING");validate_namespace(manifest);oracle=set(manifest["oracle_source_ids"]);allowed=[x["target"].rstrip("/") for x in manifest["agent_mounts"]]
 for e in events:
  actor=e.get("actor");kind=e.get("kind");target=str(e.get("target",""));source=e.get("resolved_source_id")
  require(actor in ("agent","scorer"),f"OS_ACCESS_ACTOR_INVALID: {actor}")
  if actor=="agent":
   if kind=="network":raise BoundaryViolation(f"AGENT_NETWORK_ACCESS_ATTEMPT: {target}")
   if source in oracle:raise BoundaryViolation(f"ORACLE_ACCESS_ATTEMPT: kind={kind} target={target} source={source}")
   if kind in ("file","symlink") and not any(target==x or target.startswith(x+"/") for x in allowed):raise BoundaryViolation(f"AGENT_PATH_OUTSIDE_MOUNTS: {target}")
 return {"passed":True,"event_count":len(events),"agent_event_count":sum(e.get("actor")=="agent" for e in events),"scorer_event_count":sum(e.get("actor")=="scorer" for e in events)}
