#!/usr/bin/env python3
import argparse,importlib.util,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--module",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();d=json.loads(a.input.read_text());s=importlib.util.spec_from_file_location("sb",a.module);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def req(x,msg):
 if not x:raise ValueError(msg)
ns=m.validate_namespace(d["manifest"]);clean=m.validate_access_log(d["clean_events"],d["manifest"]);caught=[]
for x in d["negative_events"]:
 try:m.validate_access_log(d["clean_events"]+[x["event"]],d["manifest"]);raise ValueError("NEGATIVE_NOT_CAUGHT:"+x["fixture"])
 except m.BoundaryViolation as e:req(x["expected_code"] in str(e),"WRONG_NEGATIVE_CODE:"+x["fixture"]+":"+str(e));caught.append({"fixture":x["fixture"],"code":x["expected_code"],"caught":True})
r=d["actual_probe_result"];req(r["boundary_pass"] is True,"PROBE_BOUNDARY_FAIL");req(r["allowed"]["success"] is True,"ALLOWED_READ_FAIL");req(r["direct"].get("errno")==2 and r["direct"]["success"] is False,"DIRECT_NOT_BLOCKED");req(r["symlink"].get("errno")==2 and r["symlink"]["success"] is False,"SYMLINK_NOT_BLOCKED");req(r["inherited_fds"]["oracle_fd_count"]==0,"ORACLE_FD_PRESENT");req(r["network_external"]["connect_ex"]==101 and r["network_loopback"]["connect_ex"]==111,"NETWORK_NOT_BLOCKED")
req(d["agent_image_digest"]==d["scorer_image_digest"],"AGENT_SCORER_IMAGE_MISMATCH");req(d["agent_container_id"]!=d["scorer_container_id"],"CONTAINER_ID_REUSED");req(d["agent_observer_pid_mode"]=="container:"+d["agent_container_id"],"AGENT_OBSERVER_WRONG_PID_NAMESPACE");req(d["scorer_observer_pid_mode"]=="container:"+d["scorer_container_id"],"SCORER_OBSERVER_WRONG_PID_NAMESPACE");req(d["scorer_eval_source_sha256"]==d["scorer_eval_copy_sha256"],"SCORER_CODE_COPY_MISMATCH")
at="".join(Path(x["path"]).read_text(errors="replace") for x in d["agent_trace_files"]);st="".join(Path(x["path"]).read_text(errors="replace") for x in d["scorer_trace_files"])
for required in ['"/workspace/allowed.txt", O_RDONLY|O_CLOEXEC) = 3','"/oracle/eval_programs/gold_results/ligand_fingerprint_gold.csv", O_RDONLY|O_CLOEXEC) = -1 ENOENT','"/workspace/oracle-link", O_RDONLY|O_CLOEXEC) = -1 ENOENT','inet_addr("1.1.1.1")','ENETUNREACH']:
 req(required in at,"AGENT_TRACE_MISSING:"+required)
for target in ['/scorer/eval_fingerprint.py>','/submission/ligand_fingerprint_pred.csv>','/gold/ligand_fingerprint_gold.csv>']:req(target in st,"SCORER_TRACE_MISSING:"+target)
log=json.loads(Path(d["scorer_log_path"]).read_text().splitlines()[-1]);req(log["exit_code"]==0 and log["stderr"]=="" and log["stdout"].startswith("(1,"),"SCORER_EXECUTION_FAIL")
out={"schema_version":"argo-actual-os-oracle-isolation/v1","namespace_validation":ns,"clean_access_validation":clean,"negative_fixtures":caught,"actual_agent_probe":"PASS","actual_scorer_probe":"PASS","agent_scorer_same_image":True,"agent_scorer_separate_containers":True,"agent_trace_count":len(d["agent_trace_files"]),"scorer_trace_count":len(d["scorer_trace_files"]),"runtime_policy_certified":True,"integrated_task_runner_certified":False,"fully_certified_task_count":0,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out))
