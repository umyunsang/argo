#!/usr/bin/env python3
"""Isolated stdlib bootstrap for sealed controller and worker stages."""
from __future__ import annotations
import hashlib,json,os,runpy,stat,sys
from pathlib import Path
def read_regular(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  st=os.fstat(fd)
  if not stat.S_ISREG(st.st_mode):raise RuntimeError("POSTRUN_NOT_REGULAR")
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def read_hash(path):return hashlib.sha256(read_regular(path)).hexdigest()
def verify_postrun_identity(role,root,args):
 try:
  index=args.index("--approval");approval_path=Path(args[index+1]);approval=json.loads(read_regular(approval_path));repo=Path(approval["engine_repo"]).resolve();expected_root=repo/"experiments/argo_workflow_followup/discoveryworld_font_qualification"
  if root!=expected_root or Path(__file__).resolve()!=root/"bootstrap.py" or read_hash(__file__)!=approval["bindings"]["bootstrap"]["sha256"]:return False
  keys=["runner","episode","font_registry","protocol","process_control","manifest","environment_manifest","environment_content","bootstrap","worker_gate","result_verifier"]+(["admission_consumer"] if role=="admission" else [])
  for key in keys:
   spec=approval["bindings"][key];path=repo/spec["path"]
   if read_hash(path)!=spec["sha256"]:return False
  return approval.get("run_id")=="dw-font-registry-qual-20260906-v1"
 except (OSError,KeyError,ValueError,IndexError,json.JSONDecodeError):return False
def main(argv=None):
 args=list(sys.argv[1:] if argv is None else argv)
 if not args or args[0] not in {"controller","worker","verifier","admission"}:raise RuntimeError("BOOTSTRAP_ROLE")
 role=args.pop(0)
 if role in {"controller","verifier","admission"}:
  root=Path(args.pop(0)).resolve();script=root/{"controller":"run.py","verifier":"verify_result.py","admission":"admit_result.py"}[role];paths=[root]
 else:
  bundle=Path(args.pop(0)).resolve();source=Path(args.pop(0)).resolve();site=Path(args.pop(0)).resolve();script=bundle/"episode.py";paths=[bundle,source,site]
 if not all(path.is_dir() for path in paths) or not script.is_file():raise RuntimeError("BOOTSTRAP_PATH")
 if role in {"verifier","admission"} and not verify_postrun_identity(role,root,args):raise RuntimeError("POSTRUN_IDENTITY")
 sys.path[:0]=[str(path) for path in paths];sys.argv=[str(script),*args];runpy.run_path(str(script),run_name="__main__");return 0
if __name__=="__main__":raise SystemExit(main())
