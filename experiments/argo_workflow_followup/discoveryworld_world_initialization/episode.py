#!/usr/bin/env python3
"""Production-shape, zero-task DiscoveryWorld initialization qualification cell."""
from __future__ import annotations
import argparse,errno,hashlib,json,math,os,subprocess,sys
from pathlib import Path
import font_registry as font_registry_module
from font_registry import configure,load,validate_manifest
EXPECTED_FONT_REQUESTS=[("Arial",8,False,False),("monospace",10,False,False),("monospace",15,False,False),("monospace",15,True,False)]
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def emit(fd,value):
 data=canonical(value)+b"\n";view=memoryview(data)
 while view:
  n=os.write(fd,view)
  if n<=0:raise OSError("event write")
  view=view[n:]
def normalize(value):
 if value is None or isinstance(value,(bool,int,str)):return value
 if isinstance(value,float):
  if not math.isfinite(value):raise RuntimeError("NONFINITE")
  return value
 if isinstance(value,(list,tuple)):return [normalize(x) for x in value]
 if isinstance(value,set):return sorted((normalize(x) for x in value),key=lambda x:canonical(x))
 if isinstance(value,dict):return {str(getattr(k,"name",k)):normalize(v) for k,v in sorted(value.items(),key=lambda item:str(getattr(item[0],"name",item[0])))}
 if hasattr(value,"name") and isinstance(value.name,str):return value.name
 raise RuntimeError("UNSUPPORTED_PROJECTION:"+type(value).__name__)
def summarize(api,world,ui,font_calls):
 sprite_rows=[[name,*world.spriteLibrary.sprites[name].get_size()] for name in sorted(world.spriteLibrary.sprites)];grid_rows=[]
 for row in world.grid:grid_rows.append([{str(getattr(layer,"name",layer)):len(objects) for layer,objects in sorted(tile.items(),key=lambda x:str(getattr(x[0],"name",x[0])))} for tile in row])
 object_properties=normalize(world.objectMaker.objectProperties);material_properties=normalize(world.objectMaker.materialProperties);feed={"articles":normalize(world.discoveryFeed.articles),"updatePosts":normalize(world.discoveryFeed.updatePosts),"uniquePostIDs":world.discoveryFeed.uniquePostIDs};ui_state={key:normalize(getattr(ui,key)) for key in ["currentAgent","curSelectedInventoryIdx","showScoreToUser","lastActionMessage","messageQueueText","dialogToDisplay","inModal","inDiscoveryFeedModal","curSelectedArgument1Idx","curSelectedArgument2Idx","curSelectedArgument1Obj","curSelectedArgument2Obj","argObjectsList","lastDiscoveryFeedPostCount","extendedPlayEnabled"]}
 return {"window_size":list(api.window.get_size()),"api":{"thread_id":api.THREAD_ID,"world_is_none":api.world is None,"num_user_agents":api.numUserAgents,"ui_count":len(api.ui),"steps":api.steps,"acted_count":len(api.agentsThatHaveActedThisStep),"task_progress_count":len(api.taskProgress)},"world":{"size":[world.sizeX,world.sizeY],"grid_dimensions":[len(world.grid),len(world.grid[0])],"grid_sha256":digest(grid_rows),"agents":len(world.agents),"task_count":len(world.taskScorer.tasks),"step":world.step,"world_history":len(world.worldHistory),"teleport_locations":len(world.teleportLocations),"live_user_playing":world.liveUserPlaying,"random_seed":world.randomSeed,"rng_is_none":world.rng is None,"uuid_existing":len(world.uuidGenerator.existingUUIDs),"sprite_count":len(sprite_rows),"sprite_dimensions_sha256":digest(sprite_rows),"object_property_count":len(object_properties),"object_properties_sha256":digest(object_properties),"material_property_count":len(material_properties),"material_properties_sha256":digest(material_properties),"object_errors":normalize(world.objectMaker.errors),"object_warnings":normalize(world.objectMaker.warnings),"feed":feed,"feed_sha256":digest(feed),"start_time_is_finite":isinstance(world.startTime,float) and math.isfinite(world.startTime)},"ui":ui_state,"font_calls":font_calls}
def no_fork(run):
 try:run(["/usr/bin/true"],check=True);return False
 except OSError as exc:
  if exc.errno not in {errno.EPERM,errno.EACCES}:raise
  return True
def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=["native","pinned"],required=True);p.add_argument("--manifest",type=Path,required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--event-fd",type=int,required=True);p.add_argument("--source-commit",required=True);p.add_argument("--source-tree",required=True);p.add_argument("--source-archive-sha256",required=True);p.add_argument("--pygame-sysfont-sha256",required=True);p.add_argument("--font-manifest-sha256",required=True);p.add_argument("--episode-sha256",required=True);p.add_argument("--font-registry-sha256",required=True);a=p.parse_args();manifest=load(a.manifest)
 import pygame,pygame.sysfont
 check=validate_manifest(manifest,a.source,pygame_sysfont_path=pygame.sysfont.__file__)
 if not check["passed"]:raise RuntimeError("FONT_MANIFEST")
 if pygame.sysfont.is_init or pygame.sysfont.Sysfonts or pygame.sysfont.Sysalias or pygame.font.SysFont is not pygame.sysfont.SysFont:raise RuntimeError("WARM_OR_ALIASED_SYSFONT")
 if hashlib.sha256(Path(pygame.sysfont.__file__).read_bytes()).hexdigest()!=a.pygame_sysfont_sha256 or hashlib.sha256(a.manifest.read_bytes()).hexdigest()!=a.font_manifest_sha256 or hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=a.episode_sha256 or hashlib.sha256(Path(font_registry_module.__file__).read_bytes()).hexdigest()!=a.font_registry_sha256:raise RuntimeError("MODULE_IDENTITY")
 original_run=subprocess.run;discovery=[]
 def counted(*args,**kwargs):discovery.append(list(args[0]));return original_run(*args,**kwargs)
 def denied(*args,**kwargs):discovery.append(list(args[0]));raise RuntimeError("PINNED_SUBPROCESS_ATTEMPT")
 subprocess.run=counted if a.mode=="native" else denied
 try:
  if a.mode=="pinned":configure(pygame,manifest,a.source,validated=True)
  from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
  from discoveryworld.TaskScorer import TaskMaker,TaskScorer
  from discoveryworld.UserInterface import UserInterface
  from discoveryworld.World import World
  forbidden=[]
  def block(name):
   def inner(*args,**kwargs):forbidden.append(name);raise RuntimeError("FORBIDDEN_CALL:"+name)
   return inner
  DiscoveryWorldAPI.loadScenario=block("loadScenario");DiscoveryWorldAPI.getAgentObservation=block("getAgentObservation");DiscoveryWorldAPI.performAgentAction=block("performAgentAction");World.tick=block("World.tick");TaskMaker.makeTask=block("TaskMaker.makeTask");TaskScorer.addTask=block("TaskScorer.addTask")
  paths=[];requests=[];original_constructor=pygame.sysfont.font_constructor;original_sysfont=pygame.font.SysFont
  def constructor(fontpath,size,bold,italic):paths.append(str(Path(fontpath)));return original_constructor(fontpath,size,bold,italic)
  def observed(name,size,bold=False,italic=False,constructor=None):requests.append((name,size,bool(bold),bool(italic)));return original_sysfont(name,size,bold=bold,italic=italic,constructor=constructor)
  pygame.sysfont.font_constructor=constructor;pygame.font.SysFont=observed
  try:
   api=DiscoveryWorldAPI(threadID=918273);api.world=World(assetPath=None,filenameSpriteIndex="spriteIndex.json",dataPath=None,filenameObjectData="objects.tsv",filenameMaterialData="materials.tsv",filenameDiscoveryFeed="discoveryFeed.json");world=api.world;ui=UserInterface(api.window,world.spriteLibrary,showScoreToUser=False);projection=summarize(api,world,ui,[{"request":list(request),"constructor_path":path,"font_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()} for request,path in zip(requests,paths)])
  finally:pygame.font.SysFont=original_sysfont;pygame.sysfont.font_constructor=original_constructor
  if requests!=EXPECTED_FONT_REQUESTS or len(paths)!=4:raise RuntimeError("FONT_CALLS")
  subprocess.run=original_run;fork_denied=no_fork(original_run) if a.mode=="pinned" else None
  event={"schema_version":"argo-world-initialization-cell/v1","mode":a.mode,"source_commit":a.source_commit,"source_tree":a.source_tree,"source_archive_sha256":a.source_archive_sha256,"pygame_sysfont_sha256":a.pygame_sysfont_sha256,"font_manifest_sha256":a.font_manifest_sha256,"episode_path":str(Path(__file__).resolve()),"episode_sha256":a.episode_sha256,"font_registry_path":str(Path(font_registry_module.__file__).resolve()),"font_registry_sha256":a.font_registry_sha256,"python_executable":str(Path(sys.executable).resolve()),"pygame_sysfont_path":str(Path(pygame.sysfont.__file__).resolve()),"projection":projection,"font_discovery_subprocesses":discovery,"os_fork_denied":fork_denied,"forbidden_calls":forbidden,"scenario_loads":0,"tasks_created":0,"agents_created":0,"ticks":0,"agent_observations":0,"model_calls":0,"spend_usd":0.0};emit(a.event_fd,event);os.fsync(a.event_fd);return 0
 finally:subprocess.run=original_run;pygame.quit()
if __name__=="__main__":raise SystemExit(main())
