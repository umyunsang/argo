#!/usr/bin/env python3
"""Failing-first tests for task, environment-seed, and rollout identity."""
from __future__ import annotations
import hashlib
import identity

F=[]
def check(name,ok,detail=""):
 print(("PASS " if ok else "FAIL ")+name+(f" :: {detail}" if not ok else ""))
 if not ok:F.append(name)
def expect_error(name,fn,text):
 try:fn();check(name,False,"no error")
 except identity.IdentityViolation as exc:check(name,text in str(exc),str(exc))
def main():
 task=b"sealed task bytes";digest=hashlib.sha256(task).hexdigest()
 valid={"task_id":"task-001","task_content_sha256":digest,"environment_seed":17,"rollout_id":"r0001","provider_seed_supported":True,"model_sampling_seed":17,"observed_rng_seeds":{"python":17,"numpy":17,"task":17}}
 result=identity.validate_identity(valid,task)
 check("supported provider identity passes",result["passed"] is True)
 expect_error("task hash mismatch is named",lambda:identity.validate_identity(valid,task+b"x"),"TASK_CONTENT_HASH_MISMATCH")
 bad_rng=dict(valid);bad_rng["observed_rng_seeds"]={"python":17,"numpy":18,"task":17}
 expect_error("inner seed mismatch is named",lambda:identity.validate_identity(bad_rng,task),"SEED_IDENTITY_MISMATCH: numpy expected=17 observed=18")
 unsupported=dict(valid);unsupported.update(provider_seed_supported=False,model_sampling_seed=None,rollout_id="r0002")
 result=identity.validate_identity(unsupported,task)
 check("unsupported provider is explicit",result["model_randomness"]=="UNSEEDED_PROVIDER_STOCHASTICITY",str(result))
 fake=dict(unsupported);fake["model_sampling_seed"]=17
 expect_error("unsupported provider cannot claim a model seed",lambda:identity.validate_identity(fake,task),"UNSUPPORTED_PROVIDER_SEED_CLAIM")
 wrong_model=dict(valid);wrong_model["model_sampling_seed"]=19
 expect_error("supported provider model seed must match",lambda:identity.validate_identity(wrong_model,task),"MODEL_SEED_IDENTITY_MISMATCH")
 schedule=[valid,unsupported]
 check("unique rollout schedule passes",identity.validate_schedule(schedule)["passed"] is True)
 duplicate=[valid,dict(valid)]
 expect_error("duplicate rollout IDs fail",lambda:identity.validate_schedule(duplicate),"DUPLICATE_ROLLOUT_ID: r0001")
 legacy={"task":"T1'","instance_id":5,"seed":7,"arm":"B0"}
 audit=identity.audit_legacy_receipt(legacy)
 check("legacy seed is not promoted",audit["status"]=="UNVERIFIED_ROLLOUT_LABEL_NOT_SEED",str(audit))
 check("legacy audit explains missing propagation", "observed_rng_seeds" in audit["reason"],str(audit))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
