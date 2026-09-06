#!/usr/bin/env python3
"""Register a fresh worker process group with the outer supervisor before exec."""
from __future__ import annotations
import json,os,sys
def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":")).encode()+b"\n"
def write_all(fd,data):
 view=memoryview(data)
 while view:
  n=os.write(fd,view)
  if n<=0:raise OSError("supervisor pipe")
  view=view[n:]
def main(argv=None):
 args=list(sys.argv[1:] if argv is None else argv)
 if len(args)<2:raise RuntimeError("GATE_ARGS")
 fd=int(args.pop(0));record={"schema_version":"argo-font-worker-pgid/v1","source":"gate","pid":os.getpid(),"pgid":os.getpgrp(),"sid":os.getsid(0)}
 if record["pid"]!=record["pgid"]:raise RuntimeError("GATE_PROCESS_GROUP")
 write_all(fd,canonical(record));os.close(fd);os.execve(args[0],args,dict(os.environ))
if __name__=="__main__":raise SystemExit(main())
