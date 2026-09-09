#!/usr/bin/env python3
"""Validate the blocked protocol-fingerprint template without sealing it."""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[2]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def null_paths(value,path=""):
 out=[]
 if value is None:out.append(path)
 elif isinstance(value,dict):
  for k,v in value.items():out.extend(null_paths(v,f"{path}.{k}" if path else k))
 elif isinstance(value,list):
  for i,v in enumerate(value):out.extend(null_paths(v,f"{path}[{i}]"))
 return out
def validate(o:dict,schema:dict)->dict:
 f=[]
 missing=[k for k in schema["required"] if k not in o]
 extra=set(o)-set(schema["properties"])
 if missing:f.append("missing top-level fields: "+", ".join(missing))
 if extra:f.append("unexpected top-level fields: "+", ".join(sorted(extra)))
 for b in o.get("file_bindings",[]):
  p=REPO/b.get("path","");actual=sha(p) if p.is_file() else None
  if actual!=b.get("sha256"):f.append(f"file binding mismatch: {b.get('role')} path={b.get('path')} registered={b.get('sha256')} actual={actual}")
 unresolved=[p for p in null_paths(o) if p!="protocol_fingerprint"]
 readiness=[]
 if not o.get("stage0",{}).get("runner_certified"):readiness.append("stage0.runner_certified=false")
 if o.get("stage0",{}).get("certified_task_count",0)<16:readiness.append("stage0.certified_task_count<16")
 if not o.get("human_approval",{}).get("approved"):readiness.append("human_approval.approved=false")
 if o.get("human_approval",{}).get("decision") not in ("FULL","FALLBACK"):readiness.append("human_approval.decision is HOLD/unset")
 blockers=unresolved+readiness
 sealable=not f and not blockers
 if o.get("status")=="SEALED_APPROVED" and not sealable:f.append("sealed status declared while blockers remain")
 if o.get("protocol_fingerprint") and not sealable:f.append("fingerprint declared while protocol is incomplete")
 if o.get("human_approval",{}).get("approved") and (not o["human_approval"].get("record_path") or not o["human_approval"].get("record_sha256")):f.append("approval true without approval record identity")
 if o.get("stage0",{}).get("runner_certified") and not o["stage0"].get("clean_environment_execution_receipt_sha256"):f.append("runner certified without clean-environment Stage 0 receipt")
 if o.get("status")=="DRAFT_BLOCKED" and o.get("protocol_fingerprint") is not None:f.append("blocked draft must not carry protocol fingerprint")
 graph_binding=next((b for b in o.get("file_bindings",[]) if b.get("role")=="context_graph_overlay"),None)
 if not graph_binding:f.append("template does not bind context graph overlay")
 else:
  gp=REPO/graph_binding["path"]
  if gp.is_file():
   graph=json.loads(gp.read_text(encoding="utf-8"))
   forbidden=[]
   for n in graph.get("nodes",[]):
    if "fingerprint_template_sha256" in n or (n.get("id")=="artifact:protocol_fingerprint_template" and "artifact_hash" in n):forbidden.append(n.get("id"))
   if forbidden:f.append("mutual template-graph hash cycle: "+", ".join(forbidden))
 return {"valid_draft":not f,"protocol_sealable":sealable,"unresolved_fields":unresolved,"readiness_blockers":readiness,"failures":f}
def rehash_binding(o,role):
 b=next(x for x in o["file_bindings"] if x["role"]==role);b["sha256"]="0"*64
def self_test(o,schema):
 xs=[]
 def one(name,mut,expect):
  c=copy.deepcopy(o);mut(c);r=validate(c,schema);xs.append({"name":name,"expected_reason":expect,"caught":any(expect in x for x in r["failures"]),"failures":r["failures"]})
 one("stale file hash",lambda x:rehash_binding(x,"treatment_manifest"),"file binding mismatch")
 one("premature fingerprint",lambda x:x.update(protocol_fingerprint="a"*64),"fingerprint declared while protocol is incomplete")
 def fake_approval(x):x["human_approval"].update(approved=True,decision="FULL")
 one("approval without record",fake_approval,"approval true without approval record identity")
 one("runner certified without receipt",lambda x:x["stage0"].update(runner_certified=True),"runner certified without clean-environment Stage 0 receipt")
 one("sealed with blockers",lambda x:x.update(status="SEALED_APPROVED"),"sealed status declared while blockers remain")
 return {"passed":all(x["caught"] for x in xs),"fixtures":xs}
def main()->int:
 st=time.perf_counter();tp=HERE/"10-protocol-fingerprint-template.json";sp=HERE/"10-protocol-fingerprint-schema.json";o=json.loads(tp.read_text());schema=json.loads(sp.read_text());r=validate(o,schema);m=self_test(o,schema);ok=r["valid_draft"] and not r["protocol_sealable"] and m["passed"];code=0 if ok else 1;script=Path(__file__).resolve();receipt={"schema_version":"argo-protocol-fingerprint-template-validation/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_zero_cost_validator","command":f"{sys.executable} {script.name}","validator_script_sha256":sha(script),"schema_sha256":sha(sp),"template_sha256":sha(tp),"runtime_seconds":time.perf_counter()-st,"exit_code":code,"validation":r,"mutation_tests":m,"passed":ok,"protocol_sealable":False,"protocol_fingerprint":None,"experiment_authorized":False,"spend_usd":0.0};(HERE/"10-protocol-fingerprint-template-validation-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps(receipt,ensure_ascii=False,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
