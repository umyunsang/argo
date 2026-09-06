#!/usr/bin/env python3
"""Fail-closed admission consumer for font qualification."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from run import authority_root,canonical,execution_root,exclusive,validate_approval
RUN_ID="dw-font-registry-qual-20260906-v1";VERIFICATION_FIELDS={"schema_version","run_id","verdict","controller_status","errors","result_sha256","ledger_sha256","marker_sha256","cells","execution_root_sha256","authority_root_sha256"}
def decide(result,verification,result_bytes,verification_bytes,approval_gate,expected_execution_root,expected_authority_root):
 errors=[]
 if not approval_gate.get("approved"):errors.append("APPROVAL_NOT_VALID")
 if set(verification)!=VERIFICATION_FIELDS or verification.get("schema_version")!="argo-font-qualification-verification/v1":errors.append("VERIFICATION_SCHEMA")
 if result.get("run_id")!=RUN_ID or verification.get("run_id")!=RUN_ID:errors.append("RUN_ID")
 if result_bytes!=canonical(result)+b"\n" or verification_bytes!=canonical(verification)+b"\n":errors.append("NONCANONICAL_BYTES")
 if verification.get("result_sha256")!=hashlib.sha256(result_bytes).hexdigest():errors.append("RESULT_DRIFT")
 if verification.get("execution_root_sha256")!=expected_execution_root or verification.get("authority_root_sha256")!=expected_authority_root:errors.append("ROOTS")
 if result.get("status")!="PASS" or verification.get("verdict")!="PASS" or verification.get("controller_status")!="PASS":errors.append("VERIFIER_OR_CONTROLLER_NOT_PASS")
 return {"schema_version":"argo-font-qualification-admission/v1","run_id":RUN_ID,"verdict":"ADMITTED" if not errors else "NOT_ADMITTED","errors":errors,"result_sha256":hashlib.sha256(result_bytes).hexdigest(),"verification_sha256":hashlib.sha256(verification_bytes).hexdigest(),"execution_root_sha256":expected_execution_root,"authority_root_sha256":expected_authority_root,"scope":"host/runtime font-initialization compatibility only; not UI parity, task, determinism, or efficacy evidence"}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval=json.loads(a.approval.read_bytes());gate=validate_approval(approval,root);manifest=json.loads((root/approval["bindings"]["manifest"]["path"]).read_bytes());result_bytes=(root/manifest["paths"]["result"]).read_bytes();verification_bytes=(root/manifest["paths"]["post_run_verification"]).read_bytes();result=json.loads(result_bytes);verification=json.loads(verification_bytes);proposal=json.loads((root/approval["bindings"]["proposal"]["path"]).read_bytes());er=execution_root(approval);ar=authority_root(approval,proposal);expected=root/manifest["paths"]["admission"]
 if a.out.resolve()!=expected.resolve() or a.out.exists():raise RuntimeError("OUTPUT")
 value=decide(result,verification,result_bytes,verification_bytes,gate,er,ar);exclusive(a.out,canonical(value)+b"\n");print(json.dumps(value,indent=2));return 0 if value["verdict"]=="ADMITTED" else 1
if __name__=="__main__":raise SystemExit(main())
