#!/usr/bin/env python3
"""Strict per-cell validator for DiscoveryWorld official/UI-only parity."""
from __future__ import annotations
import gzip,hashlib,json,re
from pathlib import Path
from state_projection import canonical_bytes
START_KEYS={"event","schema_version","run_id","cell_id","cell_nonce","scenario","difficulty","seed","mode","repeat","steps","thread_id","source_commit","source_tree","source_archive_sha256","adapter_sha256","state_projection_sha256","environment_content_sha256","bootstrap_sha256","interpreter_path","interpreter_prefix","sys_path","numpy_module_path","pygame_module_path","module_path","adapter_module_path","state_projection_module_path"}
OBS_KEYS={"event","cell_id","cell_nonce","observation_index","world_counter","ui_sha256","pre_state_sha256","pre_state","post_state_sha256","post_state","action_success","tick_success"}
COMPLETE_KEYS={"event","cell_id","cell_nonce","observations","transitions","action_successes","tick_successes","start_counter","end_counter","counter_delta","frame_directory","vision_generated","vision_consumed","model_calls","spend_usd"}
STATE_KEYS={"inModal","inDiscoveryFeedModal","dialog_present","dialog_text","dialog_options","message_queue","arg_object_uuids","arg1_index","arg2_index","arg1_uuid","arg2_uuid","object_to_show_uuid","task_progress","api_steps","world_counter"}
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def strict_loads(data):
 def reject(value):raise ValueError("non-finite JSON")
 return json.loads(data,parse_constant=reject)
def validate_cell(cell,run,event_path,ui_gzip_path,frame_manifest,*,source_commit,source_tree,source_archive_sha256,adapter_sha256,state_projection_sha256,environment_content_sha256,bootstrap_sha256,interpreter_path,site_packages,source_root,bundle_root):
 if run.get("timed_out") is True:return {"status":"timeout","errors":["TIMEOUT"]}
 if run.get("exit_code")!=0:return {"status":"crash","errors":["NONZERO_EXIT"]}
 errors=[]
 try:
  raw=Path(event_path).read_bytes();lines=raw.splitlines();events=[strict_loads(x) for x in lines]
  if any(canonical_bytes(event)!=line for event,line in zip(events,lines)):raise ValueError("noncanonical event")
 except Exception:return {"status":"malformed","errors":["EVENT_READ"]}
 if any(type(event) is not dict for event in events):return {"status":"malformed","errors":["EVENT_SCHEMA"]}
 if len(events)!=1003 or [events[0].get("event"),events[-1].get("event")]!=["start","complete"]:errors.append("EVENT_COUNT_ORDER")
 starts=[e for e in events if e.get("event")=="start"];obs=[e for e in events if e.get("event")=="observation"];completes=[e for e in events if e.get("event")=="complete"]
 if len(starts)!=1 or len(completes)!=1 or len(obs)!=1001:errors.append("EVENT_CARDINALITY")
 if errors:return {"status":"malformed","errors":errors}
 s=starts[0];c=completes[0]
 if set(s)!=START_KEYS or set(c)!=COMPLETE_KEYS or any(set(e)!=OBS_KEYS for e in obs):errors.append("EVENT_SCHEMA")
 expected_start={"schema_version":"argo-discoveryworld-ui-parity-worker/v1","run_id":"dw-ui-parity-20260906-v1","cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"scenario":cell["scenario"],"difficulty":cell["difficulty"],"seed":cell["seed"],"mode":cell["mode"],"repeat":cell["repeat"],"steps":1000,"thread_id":cell["thread_id"],"source_commit":source_commit,"source_tree":source_tree,"source_archive_sha256":source_archive_sha256,"adapter_sha256":adapter_sha256,"state_projection_sha256":state_projection_sha256,"environment_content_sha256":environment_content_sha256,"bootstrap_sha256":bootstrap_sha256,"interpreter_path":str(Path(interpreter_path).resolve())}
 if any(s.get(k)!=v for k,v in expected_start.items()) or Path(s.get("interpreter_prefix","")).resolve()!=Path(interpreter_path).resolve().parents[1] or [Path(value).resolve() for value in s.get("sys_path",[])[:3]]!=[Path(bundle_root).resolve(),Path(source_root).resolve(),Path(site_packages).resolve()] or not str(Path(s.get("numpy_module_path","")).resolve()).startswith(str(Path(site_packages).resolve())+"/") or not str(Path(s.get("pygame_module_path","")).resolve()).startswith(str(Path(site_packages).resolve())+"/") or Path(s.get("module_path","")).resolve()!=Path(source_root).resolve()/"discoveryworld"/"__init__.py" or Path(s.get("adapter_module_path","")).resolve()!=Path(bundle_root).resolve()/"adapter_v2.py" or Path(s.get("state_projection_module_path","")).resolve()!=Path(bundle_root).resolve()/"state_projection.py":errors.append("START_IDENTITY")
 if [e["observation_index"] for e in obs]!=list(range(1001)) or [e["world_counter"] for e in obs]!=list(range(1,1002)):errors.append("OBSERVATION_SEQUENCE")
 ui_hashes=[];post_hashes=[];pre_hashes=[]
 for i,e in enumerate(obs):
  if e["cell_id"]!=cell["cell_id"] or e["cell_nonce"]!=cell["cell_nonce"]:errors.append("OBS_IDENTITY");break
  if set(e["pre_state"])!=STATE_KEYS or e["pre_state"].get("api_steps")!=i or e["pre_state"].get("world_counter")!=i+1 or hashlib.sha256(canonical_bytes(e["pre_state"])).hexdigest()!=e["pre_state_sha256"]:errors.append("PRE_STATE_SCHEMA_HASH")
  if set(e["post_state"])!=STATE_KEYS or e["post_state"].get("api_steps")!=i+1 or e["post_state"].get("world_counter")!=i+1:errors.append("STATE_SCHEMA")
  if hashlib.sha256(canonical_bytes(e["post_state"])).hexdigest()!=e["post_state_sha256"]:errors.append("STATE_HASH")
  if i==0 and (e["action_success"] is not None or e["tick_success"] is not None):errors.append("STEP0_RESULT")
  if i>0 and (e["action_success"] is not True or e["tick_success"] is not True):errors.append("TRANSITION_RESULT")
  ui_hashes.append(e["ui_sha256"]);pre_hashes.append(e["pre_state_sha256"]);post_hashes.append(e["post_state_sha256"])
 try:
  with gzip.open(ui_gzip_path,"rb") as f:ui_lines=f.read().splitlines()
  ui_rows=[strict_loads(x) for x in ui_lines]
  if any(canonical_bytes(value)!=line for value,line in zip(ui_rows,ui_lines)):raise ValueError("noncanonical ui")
 except Exception:errors.append("UI_SIDECAR_READ");ui_rows=[]
 if len(ui_rows)!=1001 or any(type(x) is not dict or set(x)!={"observation_index","ui"} for x in ui_rows) or [x.get("observation_index") for x in ui_rows]!=list(range(1001)):errors.append("UI_SIDECAR_SEQUENCE")
 elif any(hashlib.sha256(canonical_bytes(x.get("ui"))).hexdigest()!=ui_hashes[i] for i,x in enumerate(ui_rows)):errors.append("UI_SIDECAR_HASH")
 expected_complete={"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"observations":1001,"transitions":1000,"action_successes":1000,"tick_successes":1000,"start_counter":1,"end_counter":1001,"counter_delta":1000,"vision_consumed":False,"model_calls":0,"spend_usd":0.0}
 if any(c.get(k)!=v for k,v in expected_complete.items()) or Path(c.get("frame_directory","")).resolve()!=Path(cell["workdir"]).resolve()/"frames":errors.append("COMPLETE_SCHEMA")
 if frame_manifest.get("count")!=len(frame_manifest.get("files",[])) or frame_manifest.get("bytes")!=sum(x.get("size",0) for x in frame_manifest.get("files",[])):errors.append("FRAME_MANIFEST")
 expected_frame_names={f"ui_agent_0_frame_{i}.png" for i in range(1,1002)}|{"ui_agent_0_current_viewport.png"}
 actual_frame_names={x.get("path") for x in frame_manifest.get("files",[])}
 if cell["mode"]=="official":
  if frame_manifest.get("count")!=1002 or actual_frame_names!=expected_frame_names or frame_manifest.get("bytes",0)>67108864 or c.get("vision_generated") is not True:errors.append("OFFICIAL_FRAME_CONTRACT")
 else:
  if frame_manifest.get("count")!=0 or frame_manifest.get("bytes")!=0 or c.get("vision_generated") is not False:errors.append("UI_ONLY_FRAME_CONTRACT")
 return {"status":"malformed" if errors else "valid_complete","errors":errors,"ui_hashes":ui_hashes,"pre_state_hashes":pre_hashes,"post_state_hashes":post_hashes,"event_sha256":file_sha(event_path),"ui_gzip_sha256":file_sha(ui_gzip_path)}
def compare_pair(a,b):
 if a.get("status")!="valid_complete" or b.get("status")!="valid_complete":return "UNOBSERVABLE"
 for key in ["ui_hashes","pre_state_hashes","post_state_hashes"]:
  if type(a.get(key)) is not list or type(b.get(key)) is not list or len(a[key])!=1001 or len(b[key])!=1001 or any(not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{64}",value) for value in a[key]+b[key]):return "UNOBSERVABLE"
 return "EXACT" if all(a[key]==b[key] for key in ["ui_hashes","pre_state_hashes","post_state_hashes"]) else "OBSERVED_MISMATCH"
