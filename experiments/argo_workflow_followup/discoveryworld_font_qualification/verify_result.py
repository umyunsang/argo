#!/usr/bin/env python3
"""Independent integrity verifier for one font qualification result."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from run import canonical,exclusive,sha,validate_approval
RUN_ID="dw-font-registry-qual-20260906-v1"
def verify(root,approval_path):
 root=Path(root);approval=json.loads(Path(approval_path).read_bytes());gate=validate_approval(approval,root);errors=[]
 if not gate["approved"]:errors.append("APPROVAL")
 try:manifest=json.loads((root/approval["bindings"]["manifest"]["path"]).read_bytes());paths={k:root/v for k,v in manifest["paths"].items()};result_bytes=paths["result"].read_bytes();result=json.loads(result_bytes);marker=json.loads(paths["marker"].read_bytes());lines=[json.loads(x) for x in paths["ledger"].read_bytes().splitlines()]
 except (OSError,KeyError,json.JSONDecodeError,TypeError) as exc:return {"verdict":"FAIL","errors":errors+["INPUT:"+type(exc).__name__]}
 if result.get("schema_version")!="argo-font-qualification-result/v1" or result.get("run_id")!=RUN_ID or result.get("status") not in {"PASS","INVALID"}:errors.append("RESULT")
 if marker.get("run_id")!=RUN_ID or marker.get("no_retry") is not True:errors.append("MARKER")
 previous=None
 for index,row in enumerate(lines):
  digest=row.get("record_sha256");body=dict(row);body.pop("record_sha256",None)
  if row.get("previous_sha256")!=previous or digest!=hashlib.sha256(canonical(body)).hexdigest():errors.append("LEDGER_CHAIN:"+str(index));break
  previous=digest
 events=[x.get("event") for x in lines]
 if events.count("header")!=1 or events.count("planned")!=2 or events.count("spawned")!=2 or events.count("finished")!=2 or events.count("finalized")!=1:errors.append("LEDGER_COUNTS")
 finals=[x for x in lines if x.get("event")=="finalized"]
 if len(finals)!=1 or finals[0].get("result_sha256")!=hashlib.sha256(result_bytes).hexdigest() or finals[0].get("status")!=result.get("status"):errors.append("FINALIZATION")
 if result.get("cells_planned")!=2 or result.get("scenario_loads")!=0 or result.get("agent_observations")!=0 or result.get("model_calls")!=0 or result.get("docker_calls")!=0 or result.get("spend_usd")!=0.0 or result.get("no_retry") is not True:errors.append("SCOPE")
 cells=result.get("cell_results",[])
 if result.get("status")=="PASS":
  if len(cells)!=2 or not all(x.get("validation",{}).get("passed") and not x.get("run",{}).get("unreaped") for x in cells) or not result.get("comparison",{}).get("passed") or result.get("comparison",{}).get("matched_calls")!=5 or result.get("font_pre_post_stable") is not True or result.get("source_pre_post_stable") is not True or result.get("sealed_runtime_postcheck") is not True or result.get("within_deadline") is not True:errors.append("PASS_CONDITIONS")
 return {"schema_version":"argo-font-qualification-verification/v1","run_id":RUN_ID,"verdict":"PASS" if not errors else "FAIL","controller_status":result.get("status"),"errors":errors,"result_sha256":hashlib.sha256(result_bytes).hexdigest(),"ledger_sha256":sha(paths["ledger"]),"marker_sha256":sha(paths["marker"]),"cells":len(cells)}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval=json.loads(a.approval.read_bytes());manifest=json.loads((root/approval["bindings"]["manifest"]["path"]).read_bytes());expected=root/manifest["paths"]["post_run_verification"]
 if a.out.resolve()!=expected.resolve() or a.out.exists():raise RuntimeError("OUTPUT")
 value=verify(root,a.approval);exclusive(a.out,canonical(value)+b"\n");print(json.dumps(value,indent=2));return 0 if value["verdict"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
