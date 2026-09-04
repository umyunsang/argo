#!/usr/bin/env python3
"""Fail-closed validation for GCF configs; this module never launches a model."""
from __future__ import annotations
import hashlib, json
class TreatmentViolation(ValueError):pass
def require(ok:bool,message:str)->None:
 if not ok:raise TreatmentViolation(message)
def canonical_hash(value:dict)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def load_registry(manifest:dict)->dict:
 cells=manifest.get("cells",[]);expected={f"G{g}C{c}F{f}" for g in (0,1) for c in (0,1) for f in (0,1)}
 require(len(cells)==8 and {x.get("cell_id") for x in cells}==expected,"INCOMPLETE_FACTORIAL_REGISTRY")
 registry={};fixed_hash=None
 for cell in cells:
  rid=cell.get("runner_config_id");require(rid not in registry,f"DUPLICATE_RUNNER_CONFIG: {rid}")
  cfg=cell.get("runner_config",{});actual=canonical_hash(cfg);registered=cell.get("runner_config_sha256")
  require(actual==registered,f"RUNNER_CONFIG_HASH_MISMATCH: {rid} registered={registered} actual={actual}")
  expected_factors={k:cell.get(k) for k in ("G","C","F")}
  require(cfg.get("cell_id")==cell.get("cell_id") and cfg.get("factors")==expected_factors,f"RUNNER_FACTOR_MISMATCH: {rid}")
  current_fixed=canonical_hash(cfg.get("fixed",{}))
  if fixed_hash is None:fixed_hash=current_fixed
  require(current_fixed==fixed_hash,f"FIXED_SURFACE_MISMATCH: {rid} expected={fixed_hash} actual={current_fixed}")
  registry[rid]=cfg
 return registry
def select_config(registry:dict,config_id:str,scheduled_cell_id:str)->dict:
 require(config_id in registry,f"UNKNOWN_RUNNER_CONFIG: {config_id}")
 cfg=registry[config_id];require(cfg.get("cell_id")==scheduled_cell_id,f"RUNNER_FACTOR_MISMATCH: scheduled={scheduled_cell_id} loaded={cfg.get('cell_id')}")
 return cfg
def compare_to_full(registry:dict,config_id:str)->list[str]:
 require(config_id in registry,f"UNKNOWN_RUNNER_CONFIG: {config_id}");full=registry.get("runner:g1c1f1:v1");require(full is not None,"FULL_CONFIG_MISSING")
 cfg=registry[config_id];return [k for k in ("G","C","F") if cfg["factors"][k]!=full["factors"][k]]
def content_multiset_digest(records:list[bytes])->str:
 hashes=sorted(hashlib.sha256(x).hexdigest() for x in records);return hashlib.sha256(json.dumps(hashes,separators=(",", ":")).encode()).hexdigest()
def require_content_equivalence(left:list[bytes],right:list[bytes])->dict:
 a=content_multiset_digest(left);b=content_multiset_digest(right);require(a==b,f"ACCESSIBLE_CONTENT_MISMATCH: left={a} right={b}");return {"passed":True,"content_multiset_sha256":a,"record_count":len(left)}
def validate_candidate_independence(candidates:list[dict],critic_started_at:float)->dict:
 require(len(candidates)==2,"CANDIDATE_COUNT_MISMATCH: expected=2")
 ids=[x.get("candidate_id") for x in candidates];require(len(set(ids))==2,"CANDIDATE_ID_NOT_DISTINCT")
 contexts=[x.get("context_id") for x in candidates];require(None not in contexts and len(set(contexts))==2,"CANDIDATE_CONTEXT_NOT_INDEPENDENT")
 rollouts=[x.get("rollout_id") for x in candidates];require(None not in rollouts and len(set(rollouts))==2,"CANDIDATE_ROLLOUT_NOT_INDEPENDENT")
 transcripts=[x.get("transcript_sha256") for x in candidates];require(None not in transcripts and len(set(transcripts))==2,"CANDIDATE_TRANSCRIPT_NOT_DISTINCT")
 for x in candidates:
  require(not x.get("cross_reads"),f"CANDIDATE_CROSS_READ: {x.get('candidate_id')} -> {x.get('cross_reads')}")
  require(isinstance(x.get("frozen_at"),(int,float)) and x["frozen_at"]<=critic_started_at,f"CANDIDATE_NOT_FROZEN_BEFORE_CRITIC: {x.get('candidate_id')}")
 return {"passed":True,"candidate_ids":ids,"context_ids":contexts,"rollout_ids":rollouts,"transcript_sha256":transcripts,"critic_started_at":critic_started_at}
