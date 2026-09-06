#!/usr/bin/env python3
"""Strict validation for zero-task World initialization cells."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
HEX=re.compile(r"[0-9a-f]{64}");TOP={"schema_version","mode","source_commit","source_tree","source_archive_sha256","pygame_sysfont_sha256","font_manifest_sha256","episode_path","episode_sha256","font_registry_path","font_registry_sha256","python_executable","pygame_sysfont_path","projection","font_discovery_subprocesses","os_fork_denied","forbidden_calls","scenario_loads","tasks_created","agents_created","ticks","agent_observations","model_calls","spend_usd"};PROJECTION={"window_size","api","world","ui","font_calls"};API={"thread_id","world_is_none","num_user_agents","ui_count","steps","acted_count","task_progress_count"};WORLD={"size","grid_dimensions","grid_sha256","agents","task_count","step","world_history","teleport_locations","live_user_playing","random_seed","rng_is_none","uuid_existing","sprite_count","sprite_dimensions_sha256","object_property_count","object_properties_sha256","material_property_count","material_properties_sha256","object_errors","object_warnings","feed","feed_sha256","start_time_is_finite"};UI={"currentAgent","curSelectedInventoryIdx","showScoreToUser","lastActionMessage","messageQueueText","dialogToDisplay","inModal","inDiscoveryFeedModal","curSelectedArgument1Idx","curSelectedArgument2Idx","curSelectedArgument1Obj","curSelectedArgument2Obj","argObjectsList","lastDiscoveryFeedPostCount","extendedPlayEnabled"};REQUESTS=[["Arial",8,False,False],["monospace",10,False,False],["monospace",15,False,False],["monospace",15,True,False]]
def read_one(path,limit=4_000_000):
 data=Path(path).read_bytes()
 if len(data)>limit or not data.endswith(b"\n") or data.count(b"\n")!=1:return None,"EVENT_FRAMING"
 try:return json.loads(data),None
 except (UnicodeDecodeError,json.JSONDecodeError):return None,"EVENT_JSON"
def validate_event(path,mode,identity):
 value,error=read_one(path);errors=[] if error is None else [error]
 if value is None:return {"passed":False,"errors":errors}
 if set(value)!=TOP:errors.append("TOP_FIELDS")
 for key,expected in identity.items():
  if value.get(key)!=expected:errors.append("IDENTITY:"+key)
 if value.get("schema_version")!="argo-world-initialization-cell/v1" or value.get("mode")!=mode:errors.append("MODE_SCHEMA")
 if any(value.get(key)!=0 for key in ["scenario_loads","tasks_created","agents_created","ticks","agent_observations","model_calls"]) or value.get("spend_usd")!=0.0 or value.get("forbidden_calls")!=[]:errors.append("SCOPE")
 process=value.get("font_discovery_subprocesses")
 if mode=="native":
  if process!=[["/usr/X11/bin/fc-list",":","file","family","style"]] or value.get("os_fork_denied") is not None:errors.append("NATIVE_PROCESS")
 elif process!=[] or value.get("os_fork_denied") is not True:errors.append("PINNED_PROCESS")
 projection=value.get("projection",{})
 if not isinstance(projection,dict) or set(projection)!=PROJECTION:errors.append("PROJECTION_FIELDS");projection={}
 if set(projection.get("api",{}))!=API or set(projection.get("world",{}))!=WORLD or set(projection.get("ui",{}))!=UI:errors.append("COMPONENT_FIELDS")
 api=projection.get("api",{});world=projection.get("world",{})
 if api.get("thread_id")!=918273 or api.get("world_is_none") is not False or any(api.get(k)!=0 for k in ["num_user_agents","ui_count","steps","acted_count","task_progress_count"]):errors.append("API_INITIAL")
 if world.get("size")!=[32,32] or world.get("grid_dimensions")!=[32,32] or any(world.get(k)!=0 for k in ["agents","task_count","step","world_history","teleport_locations","uuid_existing"]) or world.get("live_user_playing") is not False or world.get("random_seed") is not None or world.get("rng_is_none") is not True or world.get("start_time_is_finite") is not True:errors.append("WORLD_INITIAL")
 for key in ["grid_sha256","sprite_dimensions_sha256","object_properties_sha256","material_properties_sha256","feed_sha256"]:
  if not HEX.fullmatch(str(world.get(key,""))):errors.append("WORLD_HASH:"+key)
 fonts=projection.get("font_calls",[])
 if not isinstance(fonts,list) or [x.get("request") for x in fonts if isinstance(x,dict)]!=REQUESTS or len(fonts)!=4 or any(set(x)!={"request","constructor_path","font_sha256"} or not isinstance(x["constructor_path"],str) or not HEX.fullmatch(str(x["font_sha256"])) for x in fonts if isinstance(x,dict)):errors.append("FONT_CALLS")
 return {"passed":not errors,"errors":errors,"value":value,"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}
def compare(native,pinned):
 errors=[]
 if native.get("projection")!=pinned.get("projection"):errors.append("PROJECTION_MISMATCH")
 return {"passed":not errors,"errors":errors,"matched_components":5 if not errors else 0,"matched_font_calls":4 if not errors else 0}
