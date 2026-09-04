#!/usr/bin/env python3
"""Read-only field-coverage audit for legacy T3 and T1-prime receipts."""
from __future__ import annotations
import argparse, collections, datetime as dt, hashlib, json
from pathlib import Path
import receipt_provenance as prov
ROOT=Path(__file__).resolve().parents[3]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def t3_paths():
 out=list(sorted((ROOT/"paper/experiments/screening/stage1v4").glob("*T3*receipt.json")))
 for arm in ("B0","B1","B2"):out+=list(sorted((ROOT/f"paper/experiments/screening/block/{arm}_T3").glob("seed*-receipt.json")))
 return out
def summarize(name,paths):
 missing=collections.Counter();rows=[]
 for p in paths:
  o=json.loads(p.read_text(encoding="utf-8"));m=[x for x in prov.REQUIRED if x not in o or o[x] is None]
  for x in m:missing[x]+=1
  rows.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"missing_fields":m})
 return {"scope":name,"receipt_count":len(rows),"fully_conforming_count":sum(not x["missing_fields"] for x in rows),"missing_field_counts":dict(sorted(missing.items())),"input_manifest_sha256":hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",", ":")).encode()).hexdigest(),"inputs":rows}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();t3=summarize("T3",t3_paths());t1=summarize("T1prime",sorted((ROOT/"experiments/study_b/block").glob("*.json")));r={"schema_version":"argo-legacy-provenance-audit/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_read_only_audit","required_fields":list(prov.REQUIRED),"t3":t3,"t1prime":t1,"source_receipts_modified":False,"efficacy_re_admitted":False,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"T3":{"n":t3["receipt_count"],"conforming":t3["fully_conforming_count"],"missing":t3["missing_field_counts"]},"T1prime":{"n":t1["receipt_count"],"conforming":t1["fully_conforming_count"],"missing":t1["missing_field_counts"]}},ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
