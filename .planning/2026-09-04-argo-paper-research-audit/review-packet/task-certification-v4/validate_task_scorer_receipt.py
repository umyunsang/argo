#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,hashlib,json,tempfile
from pathlib import Path
class Violation(ValueError):pass
def req(x,msg):
 if not x:raise Violation(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def task_hash(row):return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def validate(r,verified,fixtures,benchmark,run_root,expected_digest):
 req(r.get("schema_version")=="argo-sab-task-scorer-certification/v1","SCHEMA")
 req(r.get("verified_split_sha256")==sha(verified),"VERIFIED_HASH")
 req(r.get("fixture_spec_sha256")==sha(fixtures),"FIXTURE_HASH")
 req(r.get("container_digest")==expected_digest,"CONTAINER_DIGEST")
 rows={int(x["instance_id"]):x for x in json.loads(Path(verified).read_text())};specs={x["task_id"]:x for x in json.loads(Path(fixtures).read_text())["tasks"]}
 tasks=r.get("tasks",[]);ids=[x.get("instance_id") for x in tasks];req(len(ids)==16 and len(set(ids))==16 and set(ids)==set(specs),"TASK_SET")
 passed=0
 for t in tasks:
  tid=t["instance_id"];row=rows[tid];spec=specs[tid];ev=Path(benchmark)/"eval_programs"/row["eval_script_name"]
  req(t["task_sha256"]==task_hash(row),f"TASK_HASH:{tid}");req(t["eval_script_sha256"]==sha(ev),f"EVAL_HASH:{tid}")
  gd=Path(benchmark)/"eval_programs/gold_results";req(t["gold_sha256"]=={g:sha(gd/g) for g in sorted(set(spec["outputs"].values()))},f"GOLD_HASH:{tid}")
  runs=t.get("runs",[]);req(len(runs)==6,f"RUN_COUNT:{tid}")
  for fixture,score in (("positive",1),("corrupt",0)):
   xs=[x for x in runs if x.get("fixture")==fixture];req(sorted(x.get("repeat") for x in xs)==[1,2,3],f"REPEATS:{tid}:{fixture}")
   req(all(x.get("expected_score")==score and x.get("score")==score and x.get("exit_code")==0 and x.get("timed_out") is False for x in xs),f"SCORE:{tid}:{fixture}")
   semantic={(x["exit_code"],x["timed_out"],x["score"],x["stdout"],x["stderr"],json.dumps(x["output_manifest"],sort_keys=True)) for x in xs};req(len(semantic)==1,f"NONDETERMINISTIC:{tid}:{fixture}")
   for x in xs:
    pred=Path(run_root)/f"task-{tid}"/f"{fixture}-{x['repeat']}"/"pred_results";actual=[{"path":str(p.relative_to(pred)),"size":p.stat().st_size,"sha256":sha(p)} for p in sorted(pred.rglob("*")) if p.is_file()];req(actual==x["output_manifest"],f"OUTPUT_BYTES:{tid}:{fixture}:{x['repeat']}")
  checks=t.get("checks",{});req(set(checks)=={"positive_three_pass","corrupt_three_fail","positive_deterministic","corrupt_deterministic"} and all(checks.values()),f"CHECKS:{tid}");req(t.get("scorer_certified") is True,f"TASK_CERT:{tid}");passed+=1
 req(r.get("scorer_certified_count")==passed==16,"COUNT");req(r.get("task_count")==16 and r.get("all_scorers_certified") is True,"SUMMARY")
 req(r.get("os_oracle_isolation_certified") is False and r.get("fully_certified_task_count")==0 and r.get("experiment_authorized") is False,"PREMATURE_ADMISSION")
 req(r.get("model_calls")==0 and r.get("spend_usd")==0.0,"SPEND")
 return {"passed":True,"task_count":16,"evaluator_runs":96,"output_byte_manifests_rederived":96,"container_digest":expected_digest}
def main():
 p=argparse.ArgumentParser();p.add_argument("--receipt",type=Path,required=True);p.add_argument("--verified",type=Path,required=True);p.add_argument("--fixtures",type=Path,required=True);p.add_argument("--benchmark",type=Path,required=True);p.add_argument("--run-root",type=Path,required=True);p.add_argument("--expected-digest",required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();r=json.loads(a.receipt.read_text());base=validate(r,a.verified,a.fixtures,a.benchmark,a.run_root,a.expected_digest)
 muts=[]
 def check(name,fn):
  q=copy.deepcopy(r);fn(q)
  try:validate(q,a.verified,a.fixtures,a.benchmark,a.run_root,a.expected_digest);caught=False
  except Violation:caught=True
  req(caught,"MUTATION_NOT_CAUGHT:"+name);muts.append({"mutation":name,"caught":True})
 check("positive_score_flip",lambda q:q["tasks"][0]["runs"][0].update(score=0))
 check("corrupt_score_flip",lambda q:next(x for x in q["tasks"][0]["runs"] if x["fixture"]=="corrupt").update(score=1))
 check("task_hash_flip",lambda q:q["tasks"][0].update(task_sha256="0"*64))
 check("container_digest_flip",lambda q:q.update(container_digest="sha256:"+"0"*64))
 check("premature_admission",lambda q:q.update(experiment_authorized=True))
 check("duplicate_task",lambda q:q["tasks"].__setitem__(1,copy.deepcopy(q["tasks"][0])))
 out={"schema_version":"argo-sab-task-scorer-validation/v1","source_receipt_sha256":sha(a.receipt),"validator_sha256":sha(Path(__file__)),"validation":base,"mutation_tests":muts,"mutation_pass_count":sum(x["caught"] for x in muts),"mutation_test_count":len(muts),"fully_certified_task_count":0,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out["validation"]|{"mutation_tests":f"{out['mutation_pass_count']}/{out['mutation_test_count']}"}))
if __name__=="__main__":main()
