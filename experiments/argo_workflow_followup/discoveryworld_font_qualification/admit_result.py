#!/usr/bin/env python3
"""Fail-closed admission consumer for font qualification."""
from __future__ import annotations
import argparse,hashlib,json,os,stat
from pathlib import Path
from run import authority_root,canonical,execution_root,exclusive,validate_approval
RUN_ID="dw-font-registry-qual-20260906-v1";
def read_regular(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  if not stat.S_ISREG(os.fstat(fd).st_mode):raise RuntimeError("NOT_REGULAR")
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
VERIFICATION_FIELDS={"schema_version","run_id","verdict","controller_status","errors","result_sha256","ledger_sha256","marker_sha256","supervision_sha256","cells","execution_root_sha256","authority_root_sha256"}
def decide(result,verification,result_bytes,verification_bytes,approval_gate,expected_execution_root,expected_authority_root,current_ledger_sha256,current_marker_sha256,current_supervision_sha256):
 errors=[]
 if not approval_gate.get("approved"):errors.append("APPROVAL_NOT_VALID")
 if set(verification)!=VERIFICATION_FIELDS or verification.get("schema_version")!="argo-font-qualification-verification/v1":errors.append("VERIFICATION_SCHEMA")
 if result.get("run_id")!=RUN_ID or verification.get("run_id")!=RUN_ID:errors.append("RUN_ID")
 if result_bytes!=canonical(result)+b"\n" or verification_bytes!=canonical(verification)+b"\n":errors.append("NONCANONICAL_BYTES")
 if verification.get("result_sha256")!=hashlib.sha256(result_bytes).hexdigest():errors.append("RESULT_DRIFT")
 if verification.get("ledger_sha256")!=current_ledger_sha256 or verification.get("marker_sha256")!=current_marker_sha256 or verification.get("supervision_sha256")!=current_supervision_sha256:errors.append("LEDGER_MARKER_OR_SUPERVISION_DRIFT")
 if verification.get("execution_root_sha256")!=expected_execution_root or verification.get("authority_root_sha256")!=expected_authority_root:errors.append("ROOTS")
 if result.get("status")!="PASS" or verification.get("verdict")!="PASS" or verification.get("controller_status")!="PASS":errors.append("VERIFIER_OR_CONTROLLER_NOT_PASS")
 return {"schema_version":"argo-font-qualification-admission/v1","run_id":RUN_ID,"verdict":"ADMITTED" if not errors else "NOT_ADMITTED","errors":errors,"result_sha256":hashlib.sha256(result_bytes).hexdigest(),"verification_sha256":hashlib.sha256(verification_bytes).hexdigest(),"execution_root_sha256":expected_execution_root,"authority_root_sha256":expected_authority_root,"scope":"host/runtime font-initialization compatibility only; not UI parity, task, determinism, or efficacy evidence"}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval=json.loads(read_regular(a.approval));gate=validate_approval(approval,root);manifest=json.loads(read_regular(root/approval["bindings"]["manifest"]["path"]));result_bytes=read_regular(root/manifest["paths"]["result"]);verification_bytes=read_regular(root/manifest["paths"]["post_run_verification"]);result=json.loads(result_bytes);verification=json.loads(verification_bytes);proposal=json.loads(read_regular(root/approval["bindings"]["proposal"]["path"]));er=execution_root(approval);ar=authority_root(approval,proposal);expected=root/manifest["paths"]["admission"]
 if a.out.resolve()!=expected.resolve() or a.out.exists():raise RuntimeError("OUTPUT")
 value=decide(result,verification,result_bytes,verification_bytes,gate,er,ar,hashlib.sha256(read_regular(root/manifest["paths"]["ledger"])).hexdigest(),hashlib.sha256(read_regular(root/manifest["paths"]["marker"])).hexdigest(),hashlib.sha256(read_regular(root/manifest["paths"]["supervision"])).hexdigest());exclusive(a.out,canonical(value)+b"\n");print(json.dumps(value,indent=2));return 0 if value["verdict"]=="ADMITTED" else 1
if __name__=="__main__":raise SystemExit(main())
