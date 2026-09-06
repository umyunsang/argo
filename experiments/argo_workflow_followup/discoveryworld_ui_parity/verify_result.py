#!/usr/bin/env python3
"""Independent post-run rederivation gate for UI-parity artifacts."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os
from pathlib import Path
from lifecycle import CELL_RESULT_KEYS,final_status,validate_ledger
from protocol import compare_pair,validate_cell
from run import execution_root_sha,validate_approval,validate_manifest
def read_nofollow(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def rederive_pairs(manifest,cells):
 mode=[{**pair,"status":compare_pair(cells.get(pair["official"],{}),cells.get(pair["ui_only"],{}))} for pair in manifest["mode_pairs"]];repeat=[{**pair,"status":compare_pair(cells.get(pair["left"],{}),cells.get(pair["right"],{}))} for pair in manifest["ui_repeat_pairs"]];return mode,repeat
def rederive_timing(pairs,cells):
 values=[]
 for pair in pairs:
  official=cells.get(pair["official"],{});ui=cells.get(pair["ui_only"],{});a=official.get("run",{}).get("duration_seconds");b=ui.get("run",{}).get("duration_seconds");observed=official.get("status")=="valid_complete" and ui.get("status")=="valid_complete" and isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool)
  values.append({**pair,"observed":observed,"official_seconds":a if observed else None,"ui_only_seconds":b if observed else None,"ui_minus_official_seconds":round(b-a,6) if observed else None,"ui_to_official_ratio":round(b/a,6) if observed and a>0 else None})
 return values
def validation_matches(cell_result,validation):
 return all(cell_result.get(key)==validation.get(key) for key in ["status","errors","ui_hashes","pre_state_hashes","post_state_hashes","event_sha256","ui_gzip_sha256"])
def verify(root,approval_path):
 root=Path(root);errors=[]
 try:
  approval_bytes=read_nofollow(approval_path);approval=json.loads(approval_bytes);manifest_path=root/approval["bindings"]["manifest"]["path"];manifest_bytes=read_nofollow(manifest_path);manifest=json.loads(manifest_bytes);result_path=root/manifest["paths"]["result"];ledger_path=root/manifest["paths"]["ledger"];marker_path=root/manifest["paths"]["marker"];result=json.loads(read_nofollow(result_path));ledger_bytes=read_nofollow(ledger_path);marker_bytes=read_nofollow(marker_path);marker=json.loads(marker_bytes)
 except (OSError,KeyError,json.JSONDecodeError) as exc:return {"schema_version":"argo-ui-parity-post-run-verification/v1","execution_root_sha256":None,"verdict":"NOT_PASS","passed":False,"errors":["READ:"+type(exc).__name__],"status":None,"cells":0,"mode_pairs":0,"ui_repeat_pairs":0,"result_sha256":None,"ledger_sha256":None}
 approval_check=validate_approval(approval,root);manifest_check=validate_manifest(manifest)
 if not approval_check["approved"]:errors.append("APPROVAL:"+",".join(approval_check["errors"]))
 if not manifest_check["passed"]:errors.append("MANIFEST_SCHEMA")
 manifest_sha=hashlib.sha256(manifest_bytes).hexdigest();approval_sha=hashlib.sha256(approval_bytes).hexdigest()
 if manifest_sha!=approval.get("bindings",{}).get("manifest",{}).get("sha256") or execution_root_sha(approval)!=approval.get("execution_root_sha256"):errors.append("APPROVED_ROOT")
 expected_marker={"run_id":approval.get("run_id"),"approval_sha256":approval_sha,"manifest_sha256":manifest_sha,"source_commit":approval.get("source_commit"),"source_tree":approval.get("source_tree"),"source_archive_sha256":approval.get("source_archive_sha256"),"execution_root_sha256":approval.get("execution_root_sha256")}
 if marker.get("schema_version")!="argo-ui-parity-marker/v1" or any(marker.get(key)!=value for key,value in expected_marker.items()) or json.dumps(marker,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n"!=marker_bytes:errors.append("MARKER_IDENTITY")
 try:
  environment=json.loads(read_nofollow(root/approval["bindings"]["environment_content_manifest"]["path"]));base=next(spec for spec in environment["roots"] if spec["name"]=="base_python");python_entry=next(entry for entry in base["entries"] if entry["path"]=="bin/python3.11");expected_interpreter_sha=python_entry["sha256"]
  if marker.get("sealed_interpreter_sha256")!=expected_interpreter_sha:errors.append("MARKER_INTERPRETER")
 except (OSError,KeyError,StopIteration,json.JSONDecodeError):expected_interpreter_sha=None;errors.append("ENVIRONMENT_ROOT")
 ledger=validate_ledger(ledger_path,manifest,allow_partial=result.get("status")=="INCOMPLETE",expected_header={"manifest_sha256":marker.get("manifest_sha256"),"approval_sha256":marker.get("approval_sha256"),"source_archive_sha256":marker.get("source_archive_sha256"),"preflight_identity_sha256":marker.get("preflight_identity_sha256"),"execution_root_sha256":marker.get("execution_root_sha256")},strict_sidecars=True,result_payload_path=result_path,artifact_root=root,ledger_bytes=ledger_bytes)
 if not ledger["passed"] or not ledger.get("finalized"):errors.append("LEDGER:"+",".join(ledger["errors"]+([] if ledger.get("finalized") else ["FINALIZED_REQUIRED"])))
 rederived={}
 for cell in manifest["ordered_cells"]:
  prior=result.get("cells",{}).get(cell["cell_id"])
  if prior is None:continue
  if not isinstance(prior,dict) or set(prior)!=CELL_RESULT_KEYS:errors.append("CELL_SCHEMA:"+cell["cell_id"]);continue
  if prior.get("status")!="valid_complete":rederived[cell["cell_id"]]=prior;continue
  try:
   event_path=root/cell["event_path"];events=read_nofollow(event_path).splitlines();start=json.loads(events[0]);bundle=Path(marker["sealed_bundle_path"]);source=Path(marker["sealed_source_path"]);site=Path(marker["sealed_site_packages_path"]);runtime_cell={**cell,"workdir":prior["runtime_workdir"]};frames=json.loads(read_nofollow(root/cell["frame_manifest_path"]));
   if frames!=prior.get("frame_manifest"):errors.append("FRAME_INLINE:"+cell["cell_id"])
   validation=validate_cell(runtime_cell,prior["run"],event_path,root/cell["ui_gzip_path"],frames,source_commit=approval["source_commit"],source_tree=approval["source_tree"],source_archive_sha256=approval["source_archive_sha256"],adapter_sha256=approval["bindings"]["adapter"]["sha256"],state_projection_sha256=approval["bindings"]["state_projection"]["sha256"],environment_content_sha256=approval["bindings"]["environment_content_manifest"]["sha256"],bootstrap_sha256=approval["bindings"]["bootstrap"]["sha256"],execution_root_sha256=approval["execution_root_sha256"],interpreter_sha256=expected_interpreter_sha,interpreter_path=marker["sealed_interpreter_path"],site_packages=site,source_root=source,bundle_root=bundle)
   if not validation_matches(prior,validation):errors.append("CELL:"+cell["cell_id"])
   rederived[cell["cell_id"]]={**prior,**validation}
  except (OSError,KeyError,IndexError,json.JSONDecodeError) as exc:errors.append("CELL_READ:"+cell["cell_id"]+":"+type(exc).__name__)
 mode,repeat=rederive_pairs(manifest,rederived);timing=rederive_timing(manifest["mode_pairs"],rederived)
 if timing!=result.get("timing_pairs"):errors.append("TIMING_REDERIVATION")
 if mode!=result.get("mode_pairs") or repeat!=result.get("ui_repeat_pairs"):errors.append("PAIR_REDERIVATION")
 statuses=[rederived[cell["cell_id"]]["status"] for cell in manifest["ordered_cells"] if cell["cell_id"] in rederived];computed=final_status(statuses,[pair["status"] for pair in mode+repeat],30)
 if result.get("summary",{}).get("controller_error") is not None:computed="INCOMPLETE" if len(statuses)<30 else "INVALID"
 if result.get("status")!=computed:errors.append("FINAL_STATUS")
 if result.get("execution_root_sha256")!=approval.get("execution_root_sha256"):errors.append("EXECUTION_ROOT")
 return {"schema_version":"argo-ui-parity-post-run-verification/v1","execution_root_sha256":result.get("execution_root_sha256"),"verdict":"PASS" if not errors else "NOT_PASS","passed":not errors,"errors":errors,"status":result.get("status"),"cells":len(rederived),"mode_pairs":len(mode),"ui_repeat_pairs":len(repeat),"result_sha256":hashlib.sha256(read_nofollow(result_path)).hexdigest(),"ledger_sha256":hashlib.sha256(ledger_bytes).hexdigest()}
def publish_receipt(path,value):
 path=Path(path);pending=path.with_name(path.name+".pending");data=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n";flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(pending,flags,0o600)
 try:
  view=memoryview(data)
  while view:
   written=os.write(fd,view)
   if written<=0:raise OSError("short verifier write")
   view=view[written:]
  os.fsync(fd)
 finally:os.close(fd)
 os.link(pending,path,follow_symlinks=False);directory=os.open(path.parent,os.O_RDONLY);os.fsync(directory);os.unlink(pending);os.fsync(directory);os.close(directory);return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument("--approval",type=Path);p.add_argument("--out",type=Path);a=p.parse_args();approval=a.approval or a.root/"experiments/argo_workflow_followup/discoveryworld_ui_parity/approval-template.json";value=verify(a.root,approval)
 if a.out is not None:publish_receipt(a.out,value)
 print(json.dumps(value,indent=2,sort_keys=True));return 0 if value["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
