#!/usr/bin/env python3
"""Read-only host capability audit for the planned Linux oracle boundary."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, platform, shutil, subprocess, sys
from pathlib import Path
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();tools={x:shutil.which(x) for x in ("bwrap","strace","docker","podman","sandbox-exec")};docker={"attempted":False,"available":False,"exit_code":None,"output_sha256":None}
 if tools["docker"]:
  docker["attempted"]=True
  try:
   r=subprocess.run([tools["docker"],"info","--format","{{json .ServerVersion}}"],capture_output=True,text=True,timeout=10);text=r.stdout+r.stderr;docker.update(available=r.returncode==0,exit_code=r.returncode,output_sha256=hashlib.sha256(text.encode()).hexdigest())
  except subprocess.TimeoutExpired:docker.update(exit_code="TIMEOUT")
 host={"system":platform.system(),"machine":platform.machine(),"python":platform.python_version()};native_linux=host["system"]=="Linux" and host["machine"] in ("x86_64","amd64") and bool(tools["bwrap"]) and bool(tools["strace"]);container_linux=bool(docker["available"]);ready=native_linux or container_linux;receipt={"schema_version":"argo-isolation-capability-audit/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_read_only_host_audit","host":host,"tools":tools,"docker_server":docker,"target":"linux-x86_64 separate agent/scorer namespaces with file/network access logging","target_runtime_available":ready,"namespace_executed":False,"access_log_collected":False,"oracle_isolation_verified":False,"stage0_runner_certified":False,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps(receipt,ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
