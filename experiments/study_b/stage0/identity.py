#!/usr/bin/env python3
"""Deterministic identity checks for future Stage 0 runner manifests."""
from __future__ import annotations
import hashlib

class IdentityViolation(ValueError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise IdentityViolation(message)

def validate_identity(manifest: dict, task_content: bytes) -> dict:
    task_id=manifest.get("task_id");rollout_id=manifest.get("rollout_id");seed=manifest.get("environment_seed")
    require(isinstance(task_id,str) and bool(task_id),"TASK_ID_MISSING")
    require(isinstance(rollout_id,str) and bool(rollout_id),"ROLLOUT_ID_MISSING")
    require(isinstance(seed,int) and not isinstance(seed,bool),"ENVIRONMENT_SEED_MISSING")
    actual=hashlib.sha256(task_content).hexdigest();registered=manifest.get("task_content_sha256")
    require(actual==registered,f"TASK_CONTENT_HASH_MISMATCH: task_id={task_id} registered={registered} actual={actual}")
    observed=manifest.get("observed_rng_seeds")
    require(isinstance(observed,dict) and bool(observed),"OBSERVED_RNG_SEEDS_MISSING")
    for name,value in sorted(observed.items()):
        require(value==seed,f"SEED_IDENTITY_MISMATCH: {name} expected={seed} observed={value}")
    supported=manifest.get("provider_seed_supported")
    model_seed=manifest.get("model_sampling_seed")
    require(isinstance(supported,bool),"PROVIDER_SEED_SUPPORT_UNDECLARED")
    if supported:
        require(model_seed==seed,f"MODEL_SEED_IDENTITY_MISMATCH: expected={seed} observed={model_seed}")
        randomness="SEEDED_PROVIDER_STOCHASTICITY"
    else:
        require(model_seed is None,"UNSUPPORTED_PROVIDER_SEED_CLAIM: model_sampling_seed must be null")
        randomness="UNSEEDED_PROVIDER_STOCHASTICITY"
    return {"passed":True,"task_id":task_id,"task_content_sha256":actual,"environment_seed":seed,"rollout_id":rollout_id,"model_randomness":randomness}

def validate_schedule(manifests: list[dict]) -> dict:
    seen=set();task_hashes={}
    for manifest in manifests:
        rid=manifest.get("rollout_id")
        require(rid not in seen,f"DUPLICATE_ROLLOUT_ID: {rid}")
        seen.add(rid)
        task_id=manifest.get("task_id");task_hash=manifest.get("task_content_sha256")
        if task_id in task_hashes:
            require(task_hashes[task_id]==task_hash,f"TASK_ID_COLLISION: {task_id}")
        else:task_hashes[task_id]=task_hash
    return {"passed":True,"rollout_count":len(manifests),"unique_rollout_count":len(seen),"unique_task_count":len(task_hashes)}

def audit_legacy_receipt(receipt: dict) -> dict:
    if "seed" in receipt and not receipt.get("observed_rng_seeds"):
        return {"status":"UNVERIFIED_ROLLOUT_LABEL_NOT_SEED","legacy_value":receipt.get("seed"),"reason":"receipt has a seed label but no observed_rng_seeds or provider-seed binding"}
    return {"status":"IDENTITY_NOT_ESTABLISHED","reason":"legacy receipt does not satisfy the Stage 0 identity manifest"}
