#!/usr/bin/env python3
"""Audit a GCF treatment manifest without loading tools or launching a model."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from pathlib import Path
import treatment_loader as loader
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--manifest",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();obj=json.loads(a.manifest.read_text());reg=loader.load_registry(obj);rem={x:loader.compare_to_full(reg,x) for x in ("runner:g0c1f1:v1","runner:g1c0f1:v1","runner:g1c1f0:v1")};receipt={"schema_version":"argo-stage0-treatment-manifest-audit/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_no_execution_audit","manifest_path":str(a.manifest),"manifest_sha256":sha(a.manifest),"config_count":len(reg),"configs":[{"runner_config_id":k,"runner_config_sha256":loader.canonical_hash(v),"cell_id":v["cell_id"],"factors":v["factors"],"fixed_surface_sha256":loader.canonical_hash(v["fixed"])} for k,v in sorted(reg.items())],"removal_differences":rem,"schema_audit_passed":True,"actual_runner_integration_verified":False,"candidate_independence_executed":False,"accessible_content_equivalence_executed":False,"stage0_runner_certified":False,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"config_count":len(reg),"removals":rem,"stage0_runner_certified":False},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
