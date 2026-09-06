#!/usr/bin/env python3
"""One no-scenario font-resolution qualification cell."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from font_registry import configure,load,validate_manifest
SAMPLES=["ARGO 0123","한글 ARGO"]
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def write_all(fd,data):
 view=memoryview(data)
 while view:
  count=os.write(fd,view)
  if count<=0:raise OSError("event write")
  view=view[count:]
def emit(fd,value):write_all(fd,canonical(value)+b"\n")
def style_path(sysfont,name,bold,italic):
 key="arial" if name.lower()=="arial" else "monospace";styles=sysfont.Sysfonts.get(key) or sysfont.Sysalias.get(key);return styles.get((bold,italic)) or styles.get((False,False))
def measure(pygame_module,call):
 font=pygame_module.font.SysFont(call["name"],call["size"],bold=call["bold"],italic=call["italic"]);rows=[]
 for sample in SAMPLES:
  surface=font.render(sample,True,(255,255,255));pixels=pygame_module.image.tostring(surface,"RGBA");rows.append({"sample":sample,"size":list(font.size(sample)),"metrics":font.metrics(sample),"render_rgba_sha256":hashlib.sha256(pixels).hexdigest()})
 path=Path(style_path(pygame_module.sysfont,call["name"],call["bold"],call["italic"]));return {"source":call["source"],"line":call["line"],"name":call["name"],"size":call["size"],"bold":call["bold"],"italic":call["italic"],"resolved_path":str(path),"font_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"samples":rows}
def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=["native","pinned"],required=True);p.add_argument("--manifest",type=Path,required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--event-fd",type=int,required=True);a=p.parse_args();manifest=load(a.manifest);check=validate_manifest(manifest,a.source)
 if not check["passed"]:raise RuntimeError("FONT_MANIFEST")
 import pygame,pygame.sysfont
 pygame.font.init();calls=[];original=subprocess.run
 def counted(*args,**kwargs):calls.append(list(args[0]));return original(*args,**kwargs)
 def denied(*args,**kwargs):calls.append(list(args[0]));raise RuntimeError("PINNED_SUBPROCESS_ATTEMPT")
 subprocess.run=counted if a.mode=="native" else denied
 try:
  if a.mode=="pinned":configure(pygame,manifest,a.source)
  rows=[measure(pygame,call) for call in manifest["calls"]]
  os_fork_denied=None
  if a.mode=="pinned":
   subprocess.run=original
   try:original(["/usr/bin/true"],check=True);os_fork_denied=False
   except OSError:os_fork_denied=True
 finally:subprocess.run=original
 emit(a.event_fd,{"schema_version":"argo-font-qualification-cell/v1","mode":a.mode,"calls":rows,"font_discovery_subprocesses":calls,"os_fork_denied":os_fork_denied,"scenario_loads":0,"agent_observations":0,"model_calls":0,"spend_usd":0.0});os.fsync(a.event_fd);return 0
if __name__=="__main__":raise SystemExit(main())
