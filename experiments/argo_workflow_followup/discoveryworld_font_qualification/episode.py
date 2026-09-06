#!/usr/bin/env python3
"""One no-scenario font-resolution qualification cell."""
from __future__ import annotations
import argparse,errno,hashlib,json,os,subprocess,sys
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
 captured=[];sysfont=pygame_module.sysfont;original_constructor=sysfont.font_constructor
 def constructor(fontpath,size,bold,italic):captured.append(fontpath);return original_constructor(fontpath,size,bold,italic)
 sysfont.font_constructor=constructor
 try:font=pygame_module.font.SysFont(call["name"],call["size"],bold=call["bold"],italic=call["italic"])
 finally:sysfont.font_constructor=original_constructor
 if len(captured)!=1 or captured[0] is None:raise RuntimeError("FONT_CONSTRUCTOR_PATH")
 rows=[]
 for sample in SAMPLES:
  surface=font.render(sample,True,(255,255,255));pixels=pygame_module.image.tostring(surface,"RGBA");rows.append({"sample":sample,"size":list(font.size(sample)),"metrics":font.metrics(sample),"render_rgba_sha256":hashlib.sha256(pixels).hexdigest()})
 path=Path(captured[0]);declared=Path(style_path(pygame_module.sysfont,call["name"],call["bold"],call["italic"]))
 if path!=declared:raise RuntimeError("FONT_CONSTRUCTOR_DECLARATION_MISMATCH")
 return {"source":call["source"],"line":call["line"],"name":call["name"],"size":call["size"],"bold":call["bold"],"italic":call["italic"],"resolved_path":str(path),"font_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"samples":rows}
def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=["native","pinned"],required=True);p.add_argument("--manifest",type=Path,required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--event-fd",type=int,required=True);p.add_argument("--source-commit",required=True);p.add_argument("--source-tree",required=True);p.add_argument("--source-archive-sha256",required=True);p.add_argument("--pygame-sysfont-sha256",required=True);p.add_argument("--font-manifest-sha256",required=True);a=p.parse_args();manifest=load(a.manifest);check=validate_manifest(manifest,a.source)
 if not check["passed"]:raise RuntimeError("FONT_MANIFEST")
 import pygame,pygame.sysfont
 if pygame.sysfont.is_init or pygame.sysfont.Sysfonts or pygame.sysfont.Sysalias:raise RuntimeError("WARM_FONT_CACHE")
 if pygame.font.SysFont is not pygame.sysfont.SysFont:raise RuntimeError("SYSFONT_ALIAS_IDENTITY")
 if hashlib.sha256(Path(pygame.sysfont.__file__).read_bytes()).hexdigest()!=a.pygame_sysfont_sha256 or hashlib.sha256(a.manifest.read_bytes()).hexdigest()!=a.font_manifest_sha256:raise RuntimeError("MODULE_OR_MANIFEST_IDENTITY")
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
   except OSError as exc:
    if exc.errno not in {errno.EPERM,errno.EACCES}:raise
    os_fork_denied=True
 finally:subprocess.run=original
 emit(a.event_fd,{"schema_version":"argo-font-qualification-cell/v1","mode":a.mode,"source_commit":a.source_commit,"source_tree":a.source_tree,"source_archive_sha256":a.source_archive_sha256,"pygame_sysfont_sha256":a.pygame_sysfont_sha256,"font_manifest_sha256":a.font_manifest_sha256,"python_executable":str(Path(sys.executable).resolve()),"pygame_sysfont_path":str(Path(pygame.sysfont.__file__).resolve()),"calls":rows,"font_discovery_subprocesses":calls,"os_fork_denied":os_fork_denied,"scenario_loads":0,"agent_observations":0,"model_calls":0,"spend_usd":0.0});os.fsync(a.event_fd);return 0
if __name__=="__main__":raise SystemExit(main())
