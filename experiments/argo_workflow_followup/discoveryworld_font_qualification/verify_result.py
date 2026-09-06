#!/usr/bin/env python3
"""Independently rederive font qualification integrity from raw artifacts."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,tempfile
from pathlib import Path
from environment_manifest import verify_root
from protocol import compare,read_one,validate_event
from run import SOURCE_ARCHIVE,SOURCE_COMMIT,SOURCE_TREE,SYSFONT_SHA,authority_root,canonical,execution_root,exclusive,prepare_source,profile,runtime_paths,sha,stat_font,tree_digest,validate_approval
RUN_ID="dw-font-registry-qual-20260906-v1";RUN_FIELDS={"exit_code","timed_out","global_deadline","controller_signal","unreaped","pid","pgid","duration_seconds"};SUPERVISION_FIELDS={"schema_version","run_id","passed","controller_exit_code","timed_out","interrupted","unreaped","descendant_leak","worker_pgids","worker_pgid_sources","registry_errors","registry_eof","elapsed_seconds","ledger_spawned_pgids","pgid_registry_matches","controller_seal_removed","launch_monotonic","observed_completion_monotonic","deadline_seconds","marker_sha256","result_sha256"}
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
def regular(path):
 try:return not Path(path).is_symlink() and stat.S_ISREG(Path(path).stat().st_mode)
 except OSError:return False
def verify(root,approval_path):
 root=Path(root);approval_bytes=read_regular(approval_path);approval=json.loads(approval_bytes);gate=validate_approval(approval,root);errors=[]
 if not gate["approved"]:errors.append("APPROVAL")
 try:
  manifest=json.loads(read_regular(root/approval["bindings"]["manifest"]["path"]));font_manifest=json.loads(read_regular(root/approval["bindings"]["font_manifest"]["path"]));environment=json.loads(read_regular(root/approval["bindings"]["environment_content"]["path"]));proposal=json.loads(read_regular(root/approval["bindings"]["proposal"]["path"]));paths={k:root/v for k,v in manifest["paths"].items()};result_bytes=read_regular(paths["result"]);result=json.loads(result_bytes);marker_bytes=read_regular(paths["marker"]);marker=json.loads(marker_bytes);ledger_bytes=read_regular(paths["ledger"]);lines=[json.loads(x) for x in ledger_bytes.splitlines()];supervision_bytes=read_regular(paths["supervision"]);supervision=json.loads(supervision_bytes)
 except (OSError,KeyError,json.JSONDecodeError,TypeError) as exc:return {"verdict":"FAIL","errors":errors+["INPUT:"+type(exc).__name__]}
 try:runtime_paths(Path("/tmp/unused"),environment)
 except RuntimeError:errors.append("RUNTIME_DESTINATIONS")
 er=execution_root(approval);ar=authority_root(approval,proposal);approval_sha=hashlib.sha256(approval_bytes).hexdigest()
 if result_bytes!=canonical(result)+b"\n" or marker_bytes!=canonical(marker)+b"\n" or supervision_bytes!=canonical(supervision)+b"\n":errors.append("NONCANONICAL_INPUT")
 if result.get("schema_version")!="argo-font-qualification-result/v1" or result.get("run_id")!=RUN_ID or result.get("status") not in {"PASS","INVALID"}:errors.append("RESULT")
 if marker.get("schema_version")!="argo-font-qualification-marker/v1" or marker.get("run_id")!=RUN_ID or marker.get("no_retry") is not True or marker.get("approval_sha256")!=approval_sha or marker.get("execution_root_sha256")!=er or marker.get("authority_root_sha256")!=ar or marker.get("deadline_monotonic")!=marker.get("launch_monotonic",0)+120 or marker.get("environment_content_aggregate_sha256")!=environment.get("aggregate_sha256"):errors.append("MARKER")
 if result.get("approval_sha256")!=approval_sha or result.get("execution_root_sha256")!=er or result.get("authority_root_sha256")!=ar:errors.append("RESULT_ROOTS")
 if set(supervision)!=SUPERVISION_FIELDS or supervision.get("schema_version")!="argo-font-qualification-supervision/v1" or supervision.get("run_id")!=RUN_ID or supervision.get("passed") is not True or supervision.get("timed_out") is not False or supervision.get("interrupted") is not False or supervision.get("unreaped") is not False or supervision.get("descendant_leak") is not False or supervision.get("registry_errors")!=[] or supervision.get("registry_eof") is not True or supervision.get("pgid_registry_matches") is not True or supervision.get("controller_seal_removed") is not True or supervision.get("worker_pgids")!=supervision.get("ledger_spawned_pgids") or any(sources!={"controller","gate"} for sources in [set(x) for x in supervision.get("worker_pgid_sources",{}).values()]) or set(supervision.get("worker_pgid_sources",{}))!={str(x) for x in supervision.get("worker_pgids",[])} or not isinstance(supervision.get("elapsed_seconds"),(int,float)) or supervision.get("elapsed_seconds")>=120 or supervision.get("deadline_seconds")!=120 or supervision.get("launch_monotonic")!=marker.get("launch_monotonic") or supervision.get("marker_sha256")!=hashlib.sha256(marker_bytes).hexdigest() or supervision.get("result_sha256")!=hashlib.sha256(result_bytes).hexdigest():errors.append("SUPERVISION")
 if ledger_bytes!=b"".join(canonical(row)+b"\n" for row in lines):errors.append("LEDGER_NONCANONICAL")
 previous=None
 for index,row in enumerate(lines):
  digest=row.get("record_sha256");body=dict(row);body.pop("record_sha256",None)
  if row.get("previous_sha256")!=previous or digest!=hashlib.sha256(canonical(body)).hexdigest():errors.append("LEDGER_CHAIN:"+str(index));break
  previous=digest
 cells=result.get("cell_results",[]);expected_events=["header"]
 for cell in cells:expected_events += ["planned","spawned","finished"]
 expected_events += ["finalized"]
 if [x.get("event") for x in lines]!=expected_events:errors.append("LEDGER_ORDER")
 if not lines or any(row.get("run_id")!=RUN_ID for row in lines) or lines[0].get("timestamp")!=marker.get("consumed_at"):errors.append("LEDGER_HEADER")
 ledger_spawned=sorted(x.get("pgid") for x in lines if x.get("event")=="spawned")
 if supervision.get("worker_pgids")!=ledger_spawned or supervision.get("ledger_spawned_pgids")!=ledger_spawned:errors.append("SUPERVISION_LEDGER_PGIDS")
 if [x.get("cell_id") for x in lines if x.get("event")=="planned"]!=[x.get("cell_id") for x in cells] or [x.get("mode") for x in lines if x.get("event")=="planned"]!=[x.get("mode") for x in cells]:errors.append("LEDGER_CELLS")
 for cell in cells:
  spawned=[x for x in lines if x.get("event")=="spawned" and x.get("cell_id")==cell.get("cell_id")];finished=[x for x in lines if x.get("event")=="finished" and x.get("cell_id")==cell.get("cell_id")]
  if len(spawned)!=1 or spawned[0].get("pid")!=cell.get("run",{}).get("pid") or spawned[0].get("pgid")!=cell.get("run",{}).get("pgid"):errors.append("LEDGER_SPAWN:"+str(cell.get("cell_id")))
  if len(finished)!=1 or finished[0].get("mode")!=cell.get("mode") or finished[0].get("exit_code")!=cell.get("run",{}).get("exit_code") or finished[0].get("valid")!=cell.get("validation",{}).get("passed") or finished[0].get("errors")!=cell.get("validation",{}).get("errors") or finished[0].get("artifacts")!=cell.get("artifacts"):errors.append("LEDGER_FINISH:"+str(cell.get("cell_id")))
 finals=[x for x in lines if x.get("event")=="finalized"]
 if len(finals)!=1 or finals[0].get("result_sha256")!=hashlib.sha256(result_bytes).hexdigest() or finals[0].get("status")!=result.get("status") or finals[0].get("execution_root_sha256")!=er or finals[0].get("authority_root_sha256")!=ar:errors.append("FINALIZATION")
 parsed={};temp_roots=set();side_root=paths["sidecar_root"]
 for index,cell in enumerate(cells):
  mode=cell.get("mode");cell_id=cell.get("cell_id")
  if index>=2 or cell_id!=manifest["ordered_cells"][index]["cell_id"] or mode!=manifest["ordered_cells"][index]["mode"]:errors.append("CELL_ORDER:"+str(index));continue
  side=side_root/mode;event=side/"event.jsonl";stdout=side/"stdout.bin";stderr=side/"stderr.bin";profile_path=side/"profile.sb"
  if not all(regular(p) for p in [event,stdout,stderr,profile_path]):errors.append("SIDECAR_TYPE:"+mode);continue
  temp=Path(marker.get("sealed_temp_root",""));temp_roots.add(str(temp));bundle=temp/"bundle";base,site=runtime_paths(temp,environment);sealed_python=base/"bin/python3.11";sealed_sysfont=site/"pygame/sysfont.py";identity={"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"source_archive_sha256":SOURCE_ARCHIVE,"pygame_sysfont_sha256":SYSFONT_SHA,"font_manifest_sha256":approval["bindings"]["font_manifest"]["sha256"],"python_executable":str(sealed_python.resolve()),"pygame_sysfont_path":str(sealed_sysfont.resolve()),"episode_path":str((bundle/"episode.py").resolve()),"episode_sha256":approval["bindings"]["episode"]["sha256"],"font_registry_path":str((bundle/"font_registry.py").resolve()),"font_registry_sha256":approval["bindings"]["font_registry"]["sha256"]};derived=validate_event(event,mode,font_manifest,identity) if cell.get("run",{}).get("exit_code")==0 else {"passed":False,"errors":["PROCESS_OR_EVENT"]};artifacts={"event_sha256":sha(event),"stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),"profile_sha256":sha(profile_path)}
  if cell.get("validation")!=derived or cell.get("artifacts")!=artifacts:errors.append("CELL_DERIVATION:"+mode)
  if derived.get("passed") and (stdout.stat().st_size!=0 or stderr.stat().st_size!=0):errors.append("UNEXPECTED_OUTPUT:"+mode)
  if profile_path.read_text()!=profile(mode,temp/mode,sealed_python):errors.append("PROFILE:"+mode)
  if derived.get("passed"):parsed[mode]=derived["value"]
 if len(temp_roots)!=1:errors.append("TEMP_ROOTS")
 derived_comparison=compare(parsed["native"],parsed["pinned"]) if set(parsed)=={"native","pinned"} else {"passed":False,"errors":["MISSING_VALID_CELL"],"matched_calls":0}
 if result.get("comparison")!=derived_comparison:errors.append("COMPARISON")
 try:
  current_fonts=[stat_font(call["resolved_path"]) for call in font_manifest["calls"]]
  if result.get("font_before")!=result.get("font_after") or result.get("font_after")!=current_fonts:errors.append("FONT_PRE_POST")
 except (OSError,RuntimeError):errors.append("FONT_CURRENT")
 try:
  with tempfile.TemporaryDirectory(prefix="dw-font-verifier-source-") as td:source=prepare_source(Path(td));source_digest=tree_digest(source)
  if result.get("source_digest_before")!=source_digest or result.get("source_digest_after")!=source_digest or marker.get("source_digest")!=source_digest:errors.append("SOURCE_PRE_POST")
 except (OSError,RuntimeError):errors.append("SOURCE_CURRENT")
 if environment.get("aggregate_sha256")!=result.get("environment_content_aggregate_sha256") or not all(verify_root(spec) for spec in environment.get("roots",[])):errors.append("RUNTIME_CURRENT")
 scope_ok=result.get("cells_planned")==2 and result.get("cells_finished")==len(cells) and result.get("scenario_loads")==0 and result.get("agent_observations")==0 and result.get("model_calls")==0 and result.get("docker_calls")==0 and result.get("spend_usd")==0.0 and result.get("no_retry") is True
 if not scope_ok:errors.append("SCOPE")
 process_pass=all(set(cell.get("run",{}))==RUN_FIELDS and cell["run"].get("exit_code")==0 and cell["run"].get("timed_out") is False and cell["run"].get("global_deadline") is False and cell["run"].get("controller_signal") is None and cell["run"].get("unreaped") is False for cell in cells)
 derived_pass=len(cells)==2 and process_pass and set(parsed)=={"native","pinned"} and derived_comparison["passed"] and result.get("font_pre_post_stable") is True and result.get("source_pre_post_stable") is True and result.get("sealed_runtime_postcheck") is True and result.get("within_deadline") is True and isinstance(result.get("elapsed_seconds"),(int,float)) and result.get("elapsed_seconds")<105 and supervision.get("passed") is True
 if (result.get("status")=="PASS")!=derived_pass:errors.append("STATUS_DERIVATION")
 expected_exit=0 if result.get("status")=="PASS" else 1
 if supervision.get("controller_exit_code")!=expected_exit:errors.append("CONTROLLER_EXIT")
 return {"schema_version":"argo-font-qualification-verification/v1","run_id":RUN_ID,"verdict":"PASS" if not errors else "FAIL","controller_status":result.get("status"),"errors":errors,"result_sha256":hashlib.sha256(result_bytes).hexdigest(),"ledger_sha256":hashlib.sha256(ledger_bytes).hexdigest(),"marker_sha256":hashlib.sha256(marker_bytes).hexdigest(),"supervision_sha256":hashlib.sha256(supervision_bytes).hexdigest(),"cells":len(cells),"execution_root_sha256":er,"authority_root_sha256":ar}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval=json.loads(read_regular(a.approval));manifest=json.loads(read_regular(root/approval["bindings"]["manifest"]["path"]));expected=root/manifest["paths"]["post_run_verification"]
 if a.out.resolve()!=expected.resolve() or a.out.exists():raise RuntimeError("OUTPUT")
 value=verify(root,a.approval);exclusive(a.out,canonical(value)+b"\n");print(json.dumps(value,indent=2));return 0 if value["verdict"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
