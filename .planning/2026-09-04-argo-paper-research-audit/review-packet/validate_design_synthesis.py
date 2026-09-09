#!/usr/bin/env python3
"""Validate evidence binding and completeness of the integrated design synthesis."""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def locator_registry():
 ids=set(); files=[REPO/"paper/sources/claim-locators.json"]+sorted(HERE.glob("*-locators.json"))
 for p in files:
  if p.is_file():
   o=json.loads(p.read_text());
   for x in o.get("locators",[]):ids.add(x.get("claim_locator_id") or x.get("locator_id"))
 return ids
def validate(o:dict)->list[str]:
 f=[];cs=o.get("choices",[]);ids=[x.get("choice_id") for x in cs];locs=locator_registry()
 if o.get("status")!="DRAFT_NO_EXPERIMENT" or o.get("experiment_authorized") is not False:f.append("design synthesis must remain draft and unauthorized")
 if o.get("choice_count")!=15 or len(cs)!=15:f.append("design must contain exactly 15 choices")
 if len(ids)!=len(set(ids)):f.append("duplicate choice IDs")
 for c in cs:
  alts=c.get("alternatives",[]);selected=c.get("selected");sel=[a for a in alts if a.get("disposition")=="SELECTED"]
  if len(alts)<2:f.append(f"choice lacks competing alternatives: {c.get('choice_id')}")
  if len(sel)!=1 or sel[0].get("alternative_id")!=selected:f.append(f"selected alternative mismatch: {c.get('choice_id')}")
  for key in ("rationale","uncertainty","falsifier","implementation_acceptance"):
   if not c.get(key):f.append(f"choice missing {key}: {c.get('choice_id')}")
  if not c.get("evidence_locators") and not c.get("authority_refs"):f.append(f"choice lacks evidence: {c.get('choice_id')}")
  missing=set(c.get("evidence_locators",[]))-locs
  if missing:f.append(f"unknown evidence locator: {c.get('choice_id')} -> {sorted(missing)}")
  for a in c.get("authority_refs",[]):
   p=REPO/a.get("path","");lines=p.read_text(encoding="utf-8").splitlines() if p.is_file() else [];ex="\n".join(lines[a.get("line_start",0)-1:a.get("line_end",0)])
   if not p.is_file() or sha(p)!=a.get("sha256") or hashlib.sha256(ex.encode()).hexdigest()!=a.get("excerpt_sha256"):f.append(f"authority path/hash/span mismatch: {c.get('choice_id')}")
 return f
def self_test(o):
 xs=[]
 def one(name,mut,expect):
  c=copy.deepcopy(o);mut(c);fs=validate(c);xs.append({"name":name,"expected_reason":expect,"caught":any(expect in x for x in fs),"failures":fs})
 one("unknown locator",lambda x:x["choices"][0].update(evidence_locators=["locator:absent"]),"unknown evidence locator")
 one("single alternative",lambda x:x["choices"][0].update(alternatives=x["choices"][0]["alternatives"][:1]),"choice lacks competing alternatives")
 one("missing falsifier",lambda x:x["choices"][0].update(falsifier=""),"choice missing falsifier")
 one("selected mismatch",lambda x:x["choices"][0].update(selected="absent"),"selected alternative mismatch")
 one("premature authorization",lambda x:x.update(experiment_authorized=True),"design synthesis must remain draft and unauthorized")
 one("authority span mutation",lambda x:x["choices"][1]["authority_refs"][0].update(excerpt_sha256="0"*64),"authority path/hash/span mismatch")
 return {"passed":all(x["caught"] for x in xs),"fixtures":xs}
def main()->int:
 st=time.perf_counter();mp=HERE/"11-design-choice-matrix.json";dp=HERE/"11-integrated-experiment-design.md";o=json.loads(mp.read_text());fs=validate(o);m=self_test(o);doc=dp.read_text();required=("Stage 0","Stage R","Stage 1","Stage 2","Stage 3","G0C0F0","L1P1-L0P1","No best-of-k")
 miss=[x for x in required if x not in doc]
 if miss:fs.append("integrated design missing sections: "+", ".join(miss))
 code=0 if not fs and m["passed"] else 1;script=Path(__file__).resolve();r={"schema_version":"argo-integrated-design-validation/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_zero_cost_validator","command":f"{sys.executable} {script.name}","validator_script_sha256":sha(script),"matrix_sha256":sha(mp),"design_sha256":sha(dp),"runtime_seconds":time.perf_counter()-st,"exit_code":code,"choice_count":len(o.get("choices",[])),"source_locator_count":len(locator_registry()),"failures":fs,"mutation_tests":m,"passed":not fs and m["passed"],"experiment_authorized":False,"spend_usd":0.0};(HERE/"11-design-synthesis-validation-receipt.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n");print(json.dumps(r,ensure_ascii=False,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
