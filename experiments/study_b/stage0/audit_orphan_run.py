#!/usr/bin/env python3
"""Read-only audit of one local run directory without polling or waiting."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os
from pathlib import Path
import run_state
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def pid_exists(pid:int|None)->bool:
 if pid is None:return False
 try:os.kill(pid,0);return True
 except (OSError,ProcessLookupError):return False
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--run-dir",type=Path,required=True);ap.add_argument("--run-id",required=True);ap.add_argument("--registry-state",required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();pid_file=a.run_dir/"pid";log=a.run_dir/"log";exit_file=a.run_dir/"exit_code";pid=int(pid_file.read_text().strip()) if pid_file.is_file() and pid_file.read_text().strip().isdigit() else None;log_size=log.stat().st_size if log.is_file() else 0;exit_code=int(exit_file.read_text().strip()) if exit_file.is_file() else None;snap={"registry_state":a.registry_state,"pid_exists":pid_exists(pid),"registered_process_start":None,"observed_process_start":None,"heartbeat_age_s":None,"heartbeat_max_age_s":60,"log_size_before":log_size,"log_size_after":log_size,"exit_code":exit_code,"result_receipt_exists":exit_file.is_file() and log_size>0};result=run_state.classify(snap);inputs=[]
 for p in (pid_file,log,exit_file,a.run_dir/"run.sh"):
  inputs.append({"path":str(p),"exists":p.is_file(),"bytes":p.stat().st_size if p.is_file() else None,"sha256":sha(p) if p.is_file() else None})
 receipt={"schema_version":"argo-stale-run-audit/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_read_only_audit","run_id":a.run_id,"run_dir":str(a.run_dir),"pid":pid,"snapshot":snap,"classification":result,"inputs":inputs,"polled":False,"wait_called":False,"run_files_modified":False,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
