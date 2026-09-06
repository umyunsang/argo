#!/usr/bin/env python3
"""Seal approved controller modules before importing or executing them."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,tempfile
from pathlib import Path
FILES={"runner":"run.py","lifecycle":"lifecycle.py","protocol":"protocol.py","episode":"episode.py","adapter":"adapter_v2.py","state_projection":"state_projection.py","schemas":"schemas.json","manifest":"manifest.json","environment_manifest_module":"environment_manifest.py","environment_content_manifest":"environment-content-manifest.json","bootstrap":"bootstrap.py"}
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def read_once(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  st=os.fstat(fd)
  if not stat.S_ISREG(st.st_mode):raise RuntimeError("NOT_REGULAR:"+str(path))
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def write_once(path,data,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 try:
  view=memoryview(data)
  while view:
   written=os.write(fd,view)
   if written<=0:raise OSError("short write")
   view=view[written:]
  os.fsync(fd)
 finally:os.close(fd)

def resolve(root,path):return Path(path) if Path(path).is_absolute() else Path(root)/path
def seal_controller(approval,approval_bytes,approval_path,root,destination):
 destination=Path(destination);destination.mkdir(mode=0o700);hashes={}
 launcher=approval.get("bindings",{}).get("launcher",{});self_bytes=read_once(__file__)
 if sha_bytes(self_bytes)!=launcher.get("sha256"):raise RuntimeError("LAUNCHER_IDENTITY")
 for key,name in FILES.items():
  spec=approval.get("bindings",{}).get(key,{});data=read_once(resolve(root,spec.get("path","")))
  if sha_bytes(data)!=spec.get("sha256"):raise RuntimeError("BINDING_DRIFT:"+key)
  target=destination/name;write_once(target,data,0o500 if name.endswith(".py") else 0o400);hashes[name]=spec["sha256"]
 approval_target=destination/"approval.json";write_once(approval_target,approval_bytes,0o400);hashes["approval.json"]=sha_bytes(approval_bytes)
 seal={"schema_version":"argo-ui-parity-controller-seal/v1","files":hashes,"original_approval_path":str(Path(approval_path).resolve())};seal_bytes=canonical(seal)+b"\n";write_once(destination/"seal.json",seal_bytes,0o400)
 fd=os.open(destination,os.O_RDONLY);os.fsync(fd);os.close(fd);destination.chmod(0o500);return sha_bytes(seal_bytes)
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();root=Path.cwd();approval_bytes=read_once(a.approval);approval=json.loads(approval_bytes)
 if root.resolve()!=Path(approval.get("engine_repo","/nonexistent")).resolve():raise RuntimeError("ENGINE_REPO_IDENTITY")
 if approval.get("status")!="APPROVED" or approval.get("approved_by")!="user":print(json.dumps({"status":"BLOCKED_BEFORE_CONSUMPTION","reason":"STATUS"},sort_keys=True));return 2
 destination=Path(tempfile.mkdtemp(prefix="dw-ui-controller-seal-"));seal_sha=seal_controller(approval,approval_bytes,a.approval,root,destination);env=dict(os.environ);env.update({"ARGO_UI_PARITY_CONTROLLER_SEAL":str(destination),"ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256":seal_sha});controller=approval["controller_interpreter"];argv=[controller,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(a.approval.resolve()),"--out",str(a.out.resolve())];os.execve(controller,argv,env)
if __name__=="__main__":raise SystemExit(main())
