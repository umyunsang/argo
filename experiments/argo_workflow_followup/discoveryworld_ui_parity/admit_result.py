#!/usr/bin/env python3
"""Final admission consumer for a controller PASS plus independent verifier PASS."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from verify_result import publish_receipt,read_nofollow,verify
def strict_loads(data):
 def pairs(values):
  result={}
  for key,value in values:
   if key in result:raise ValueError("duplicate key")
   result[key]=value
  return result
 return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda value:(_ for _ in ()).throw(ValueError("nonfinite")))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n"
def receipt_exact(recorded_bytes,rederived):return recorded_bytes==canonical(rederived)

def admit(root,approval_path,verification_path):
 root=Path(root);errors=[]
 try:approval=json.loads(read_nofollow(approval_path));recorded_bytes=read_nofollow(verification_path);recorded=strict_loads(recorded_bytes);rederived=verify(root,approval_path);manifest=json.loads(read_nofollow(root/approval["bindings"]["manifest"]["path"]));result=json.loads(read_nofollow(root/manifest["paths"]["result"]));expected_verification=(root/manifest["paths"]["post_run_verification"]).resolve()
 except (OSError,KeyError,ValueError,json.JSONDecodeError) as exc:return {"schema_version":"argo-ui-parity-admission/v1","execution_root_sha256":None,"authority_root_sha256":None,"verdict":"NOT_ADMITTED","errors":["READ:"+type(exc).__name__]}
 if Path(verification_path).resolve()!=expected_verification:errors.append("VERIFIER_RECEIPT_PATH")
 if not receipt_exact(recorded_bytes,rederived):errors.append("VERIFIER_RECEIPT_REDERIVATION")
 if rederived.get("verdict")!="PASS" or rederived.get("status")!="PASS":errors.append("VERIFIER_OR_CONTROLLER_NOT_PASS")
 if rederived.get("execution_root_sha256")!=approval.get("execution_root_sha256") or result.get("execution_root_sha256")!=approval.get("execution_root_sha256"):errors.append("EXECUTION_ROOT")
 return {"schema_version":"argo-ui-parity-admission/v1","execution_root_sha256":approval.get("execution_root_sha256"),"authority_root_sha256":approval.get("authority_root_sha256"),"verdict":"ADMITTED" if not errors else "NOT_ADMITTED","errors":errors,"result_sha256":rederived.get("result_sha256"),"ledger_sha256":rederived.get("ledger_sha256"),"verifier_receipt_sha256":hashlib.sha256(recorded_bytes).hexdigest()}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument("--approval",type=Path);p.add_argument("--verification",type=Path);p.add_argument("--out",type=Path);a=p.parse_args();approval=a.approval or a.root/"experiments/argo_workflow_followup/discoveryworld_ui_parity/approval-template.json";verification=a.verification or a.root/"paper/research/receipts/discoveryworld-ui-parity-v1-post-run-verification.json";value=admit(a.root,approval,verification)
 if a.out is not None:publish_receipt(a.out,value)
 print(json.dumps(value,indent=2,sort_keys=True));return 0 if value["verdict"]=="ADMITTED" else 1
if __name__=="__main__":raise SystemExit(main())
