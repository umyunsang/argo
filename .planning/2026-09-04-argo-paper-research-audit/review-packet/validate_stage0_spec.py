#!/usr/bin/env python3
"""Validate Stage 0 acceptance specification; this does not certify a runner."""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
REQUIRED_CATEGORIES={"seed_identity","task_identity","evaluator_state","environment_identity","arm_loader","single_factor_semantics","hard_ceiling","scorer_blinding","oracle_isolation","receipt_provenance","stale_run_detection","floor_ceiling","issue_classification"}
EVAL_ZERO={"S0-EVAL-CRASH","S0-EVAL-TIMEOUT","S0-EVAL-NONZERO","S0-EVAL-MISSING","S0-EVAL-PARSE"}
PROV_FIELDS={"origin","model_provider_revision","protocol_fingerprint","harness_commit","task_hash","command","environment_hash","transcript_paths","artifact_paths","started_at","finished_at","exit_state","usage"}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(o:dict)->list[str]:
 f=[];xs=o.get("fixtures",[]);ids=[x.get("fixture_id") for x in xs]
 if o.get("status")!="SPEC_ONLY_NOT_EXECUTABLE" or o.get("experiment_authorized") is not False:f.append("spec must remain non-executable and unauthorized")
 if len(ids)!=len(set(ids)):f.append("duplicate fixture IDs")
 cats={x.get("category") for x in xs}
 if cats!=REQUIRED_CATEGORIES:f.append("category closure mismatch")
 if o.get("fixture_count")!=len(xs):f.append("fixture count mismatch")
 for x in xs:
  if x.get("deterministic") is not True:f.append(f"fixture not deterministic: {x.get('fixture_id')}")
  if x.get("polarity")=="negative" and (not x.get("expected_code") or not x.get("expected_reason_contains")):f.append(f"negative fixture lacks exact code/reason: {x.get('fixture_id')}")
 by={x["fixture_id"]:x for x in xs}
 for fid in EVAL_ZERO:
  x=by.get(fid,{})
  if x.get("score")!=0 or x.get("inadmissible_execution") is not True:f.append(f"evaluator failure is not zero/inadmissible: {fid}")
 for fid in ("S0-CAP-TOKEN","S0-CAP-TOOL","S0-CAP-TIME","S0-CAP-COST"):
  if by.get(fid,{}).get("run_stopped") is not True:f.append(f"hard ceiling does not stop run: {fid}")
 if set(by.get("S0-PROV-OK",{}).get("required_fields",[]))!=PROV_FIELDS:f.append("full provenance field closure mismatch")
 if by.get("S0-RUN-DEAD",{}).get("expected_code")!="ORPHANED_NO_VERDICT":f.append("dead worker is not orphaned no-verdict")
 return f
def self_test(o:dict)->dict:
 out=[]
 def one(name,mut,expect):
  c=copy.deepcopy(o);mut(c);fs=validate(c);out.append({"name":name,"expected_reason":expect,"caught":any(expect in x for x in fs),"failures":fs})
 one("remove category",lambda x:x.update(fixtures=[f for f in x["fixtures"] if f["category"]!="seed_identity"],fixture_count=len([f for f in x["fixtures"] if f["category"]!="seed_identity"])),"category closure mismatch")
 one("crash scores one",lambda x:next(f for f in x["fixtures"] if f["fixture_id"]=="S0-EVAL-CRASH").update(score=1),"evaluator failure is not zero/inadmissible")
 one("missing reason",lambda x:next(f for f in x["fixtures"] if f["fixture_id"]=="S0-LOAD-HASH").update(expected_reason_contains=""),"negative fixture lacks exact code/reason")
 one("authorize spec",lambda x:x.update(experiment_authorized=True),"spec must remain non-executable and unauthorized")
 one("dead worker called running",lambda x:next(f for f in x["fixtures"] if f["fixture_id"]=="S0-RUN-DEAD").update(expected_code="RUNNING"),"dead worker is not orphaned no-verdict")
 return {"passed":all(x["caught"] for x in out),"fixtures":out}
def main()->int:
 start=time.perf_counter();sp=HERE/"stage0-certification-spec.json";o=json.loads(sp.read_text());fs=validate(o);m=self_test(o);code=0 if not fs and m["passed"] else 1;script=Path(__file__).resolve();r={"schema_version":"argo-stage0-spec-validation/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_zero_cost_meta_validator","command":f"{sys.executable} {script.name}","validator_script_sha256":sha(script),"spec_sha256":sha(sp),"runtime_seconds":time.perf_counter()-start,"exit_code":code,"spec_validation_passed":not fs,"mutation_tests":m,"failures":fs,"stage0_runner_certified":False,"experiment_authorized":False,"spend_usd":0.0};(HERE/"stage0-spec-validation-receipt.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n");print(json.dumps(r,ensure_ascii=False,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
