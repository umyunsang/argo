#!/usr/bin/env python3
"""Strict, condition-aware validation for font qualification events."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
HEX=re.compile(r"[0-9a-f]{64}")
TOP={"schema_version","mode","source_commit","source_tree","source_archive_sha256","pygame_sysfont_sha256","font_manifest_sha256","python_executable","pygame_sysfont_path","episode_path","episode_sha256","font_registry_path","font_registry_sha256","calls","font_discovery_subprocesses","os_fork_denied","scenario_loads","agent_observations","model_calls","spend_usd"}
CALL={"source","line","name","size","bold","italic","resolved_path","font_sha256","samples"};SAMPLE={"sample","size","metrics","render_rgba_sha256"}
def read_one(path,limit=2_000_000):
 data=Path(path).read_bytes()
 if len(data)>limit or not data.endswith(b"\n") or data.count(b"\n")!=1:return None,"EVENT_FRAMING"
 try:value=json.loads(data)
 except (UnicodeDecodeError,json.JSONDecodeError):return None,"EVENT_JSON"
 return value,None
def valid_metrics(value,n):return isinstance(value,list) and len(value)==n and all(item is None or isinstance(item,list) and len(item)==5 and all(isinstance(x,int) for x in item) for item in value)
def validate_event(path,mode,font_manifest,identity):
 value,error=read_one(path);errors=[] if error is None else [error]
 if value is None:return {"passed":False,"errors":errors}
 if set(value)!=TOP:errors.append("TOP_FIELDS")
 for key in ["source_commit","source_tree","source_archive_sha256","pygame_sysfont_sha256","font_manifest_sha256","python_executable","pygame_sysfont_path","episode_path","episode_sha256","font_registry_path","font_registry_sha256"]:
  if value.get(key)!=identity[key]:errors.append("IDENTITY:"+key)
 if value.get("schema_version")!="argo-font-qualification-cell/v1" or value.get("mode")!=mode:errors.append("MODE_OR_SCHEMA")
 if value.get("scenario_loads")!=0 or value.get("agent_observations")!=0 or value.get("model_calls")!=0 or value.get("spend_usd")!=0.0:errors.append("BUDGET_OR_SCOPE")
 calls=value.get("calls")
 if not isinstance(calls,list) or len(calls)!=5:errors.append("CALL_COUNT");calls=[]
 expected=font_manifest.get("calls",[])
 for index,row in enumerate(calls):
  if not isinstance(row,dict) or set(row)!=CALL:errors.append(f"CALL_FIELDS:{index}");continue
  if index>=len(expected):continue
  call=expected[index]
  for key in ["source","line","name","size","bold","italic"]:
   if row.get(key)!=call.get(key):errors.append(f"CALL_ID:{index}:{key}")
  if not isinstance(row.get("resolved_path"),str) or not HEX.fullmatch(str(row.get("font_sha256",""))):errors.append(f"CALL_PATH_HASH:{index}")
  samples=row.get("samples")
  if not isinstance(samples,list) or [x.get("sample") for x in samples if isinstance(x,dict)]!=["ARGO 0123","한글 ARGO"]:errors.append(f"SAMPLES:{index}");continue
  for j,item in enumerate(samples):
   if not isinstance(item,dict) or set(item)!=SAMPLE or not isinstance(item.get("size"),list) or len(item["size"])!=2 or not all(isinstance(x,int) for x in item["size"]) or not valid_metrics(item.get("metrics"),len(item.get("sample",""))) or not HEX.fullmatch(str(item.get("render_rgba_sha256",""))):errors.append(f"SAMPLE_SCHEMA:{index}:{j}")
 discovery=value.get("font_discovery_subprocesses")
 if mode=="native":
  if discovery!=[["/usr/X11/bin/fc-list",":","file","family","style"]] or value.get("os_fork_denied") is not None:errors.append("NATIVE_PROCESS")
 else:
  if discovery!=[] or value.get("os_fork_denied") is not True:errors.append("PINNED_PROCESS")
 return {"passed":not errors,"errors":errors,"value":value,"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}
def compare(native,pinned):
 errors=[];fields=["source","line","name","size","bold","italic","resolved_path","font_sha256","samples"]
 for i,(left,right) in enumerate(zip(native.get("calls",[]),pinned.get("calls",[]))):
  if {k:left.get(k) for k in fields}!={k:right.get(k) for k in fields}:errors.append("MISMATCH:"+str(i))
 if len(native.get("calls",[]))!=5 or len(pinned.get("calls",[]))!=5:errors.append("DENOMINATOR")
 return {"passed":not errors,"errors":errors,"matched_calls":5-len([e for e in errors if e.startswith("MISMATCH:")])}
