#!/usr/bin/env python3
"""Fail-closed admission consumer for font qualification."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from run import canonical,exclusive
RUN_ID="dw-font-registry-qual-20260906-v1"
def decide(result,verification):
 errors=[]
 if result.get("run_id")!=RUN_ID or verification.get("run_id")!=RUN_ID:errors.append("RUN_ID")
 if result.get("status")!="PASS" or verification.get("verdict")!="PASS" or verification.get("controller_status")!="PASS":errors.append("VERIFIER_OR_CONTROLLER_NOT_PASS")
 return {"schema_version":"argo-font-qualification-admission/v1","run_id":RUN_ID,"verdict":"ADMITTED" if not errors else "NOT_ADMITTED","errors":errors,"result_sha256":hashlib.sha256(canonical(result)+b"\n").hexdigest(),"verification_sha256":hashlib.sha256(canonical(verification)+b"\n").hexdigest(),"scope":"host/runtime font-initialization compatibility only; not UI parity, task, determinism, or efficacy evidence"}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval=json.loads(a.approval.read_bytes());manifest=json.loads((root/approval["bindings"]["manifest"]["path"]).read_bytes());result=json.loads((root/manifest["paths"]["result"]).read_bytes());verification=json.loads((root/manifest["paths"]["post_run_verification"]).read_bytes());expected=root/manifest["paths"]["admission"]
 if a.out.resolve()!=expected.resolve() or a.out.exists():raise RuntimeError("OUTPUT")
 value=decide(result,verification);exclusive(a.out,canonical(value)+b"\n");print(json.dumps(value,indent=2));return 0 if value["verdict"]=="ADMITTED" else 1
if __name__=="__main__":raise SystemExit(main())
