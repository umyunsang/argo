#!/usr/bin/env python3
"""Read-only identity audit for legacy T3 and T1-prime receipts."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def outer_label(path:Path)->int|None:
 m=re.search(r"seed(\d+)",path.name) or re.search(r"_s(\d+)_",path.name)
 return int(m.group(1)) if m else None
def records(paths):
 out=[]
 for p in paths:
  obj=json.loads(p.read_text(encoding="utf-8"));episodes=obj.get("episodes") if isinstance(obj.get("episodes"),list) else [obj]
  for ep in episodes:out.append((p,ep))
 return out
def summarize(name,records_):
 rows=[]
 for p,ep in records_:
  rows.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"outer_label":outer_label(p),"inner_seed":ep.get("seed"),"task_hash":ep.get("task_sha256") or ep.get("task_content_sha256"),"has_observed_rng_seeds":bool(ep.get("observed_rng_seeds")),"has_model_sampling_seed":"model_sampling_seed" in ep})
 digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
 return {"name":name,"episode_count":len(rows),"outer_label_count":len({r["outer_label"] for r in rows if r["outer_label"] is not None}),"inner_seed_values":sorted({r["inner_seed"] for r in rows if r["inner_seed"] is not None}),"unique_task_hash_count":len({r["task_hash"] for r in rows if r["task_hash"]}),"outer_inner_mismatch_count":sum(r["outer_label"] is not None and r["inner_seed"] is not None and r["outer_label"]!=r["inner_seed"] for r in rows),"observed_rng_seed_count":sum(r["has_observed_rng_seeds"] for r in rows),"model_sampling_seed_field_count":sum(r["has_model_sampling_seed"] for r in rows),"input_manifest_sha256":digest,"inputs":rows}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args()
 t3=list(sorted((ROOT/"paper/experiments/screening/stage1v4").glob("*T3*receipt.json")))
 for arm in ("B0","B1","B2"):t3+=list(sorted((ROOT/f"paper/experiments/screening/block/{arm}_T3").glob("seed*-receipt.json")))
 t1=list(sorted((ROOT/"experiments/study_b/block").glob("*.json")))
 s3=summarize("T3",records(t3));s1=summarize("T1prime",records(t1))
 receipt={"schema_version":"argo-legacy-seed-identity-audit/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_read_only_audit","t3":s3,"t1prime":s1,"findings":[{"scope":"T3","status":"PSEUDOREPLICATION_SINGLE_INNER_SEED","reason":f"{s3['episode_count']} episodes expose inner seed values {s3['inner_seed_values']} and {s3['unique_task_hash_count']} unique task hash; outer filename labels mismatch {s3['outer_inner_mismatch_count']} episodes"},{"scope":"T1prime","status":"UNVERIFIED_ROLLOUT_LABEL_NOT_SEED","reason":f"{s1['episode_count']} episodes have {s1['observed_rng_seed_count']} observed RNG seed records, {s1['model_sampling_seed_field_count']} model seed fields, and {s1['unique_task_hash_count']} task hashes"}],"source_receipts_modified":False,"efficacy_admissible":False,"experiment_authorized":False,"spend_usd":0.0}
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"t3":{k:s3[k] for k in ("episode_count","outer_label_count","inner_seed_values","unique_task_hash_count","outer_inner_mismatch_count")},"t1prime":{k:s1[k] for k in ("episode_count","outer_label_count","observed_rng_seed_count","model_sampling_seed_field_count","unique_task_hash_count")}},ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
