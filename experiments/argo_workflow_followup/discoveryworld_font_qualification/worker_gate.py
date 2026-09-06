#!/usr/bin/env python3
"""Register while contained, handshake, create a session, register again, then exec."""
from __future__ import annotations
import json,os,sys
def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":")).encode()+b"\n"
def write_all(fd,data):
 view=memoryview(data)
 while view:
  n=os.write(fd,view)
  if n<=0:raise OSError("supervisor pipe")
  view=view[n:]
def record(fd,phase):write_all(fd,canonical({"schema_version":"argo-font-worker-pgid/v2","phase":phase,"pid":os.getpid(),"pgid":os.getpgrp(),"sid":os.getsid(0)}))
def main(argv=None):
 args=list(sys.argv[1:] if argv is None else argv)
 if len(args)<4:raise RuntimeError("GATE_ARGS")
 registry_fd=int(args.pop(0));ack_fd=int(args.pop(0));controller_ack_fd=int(args.pop(0));record(registry_fd,"pre_session")
 if os.read(ack_fd,1)!=b"G":raise RuntimeError("GATE_ACK")
 os.setsid()
 if os.getpid()!=os.getpgrp() or os.getpid()!=os.getsid(0):raise RuntimeError("GATE_SESSION")
 record(registry_fd,"post_session")
 if os.read(controller_ack_fd,1)!=b"C":raise RuntimeError("CONTROLLER_ACK")
 os.close(registry_fd);os.close(ack_fd);os.close(controller_ack_fd);os.execve(args[0],args,dict(os.environ))
if __name__=="__main__":raise SystemExit(main())
