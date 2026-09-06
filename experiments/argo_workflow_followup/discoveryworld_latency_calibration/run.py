#!/usr/bin/env python3
"""Approval-gated exploratory DiscoveryWorld latency calibration controller."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,time
from pathlib import Path
TASKS=[("chemistry","Combinatorial Chemistry","Normal"),("archaeology","Archaeology Dating","Normal")]
HORIZONS=[10,50,100]
REPEATS=2
TIMEOUT_SECONDS=60
EXPECTED_COMMIT="fd591323920be0d3786ef350955de1945aa571e5"
EXPECTED_INTERPRETER="/Users/um-yunsang/.cache/argo-research/DiscoveryWorld/.venv/bin/python"
EXPECTED_INTERPRETER_SHA="68100c5188b837802c7ae52398389d121b1c063ed244dec11649775b539c3a30"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sanitized_env():return {"HOME":"/tmp","PATH":"/usr/bin:/bin:/opt/homebrew/bin","PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def build_commands(interpreter,episode_path):
 out=[]
 for ti,(_,scenario,difficulty) in enumerate(TASKS):
  for horizon in HORIZONS:
   for repeat in range(REPEATS):out.append([str(interpreter),str(Path(episode_path).resolve()),"--scenario",scenario,"--difficulty",difficulty,"--horizon",str(horizon),"--repeat",str(repeat),"--thread-id",str(910000+ti*100+horizon+repeat)])
 return out
def parse_events(text):
 if isinstance(text,bytes):text=text.decode(errors="replace")
 out=[]
 for line in (text or "").splitlines():
  try:
   value=json.loads(line)
   if isinstance(value,dict):out.append(value)
  except json.JSONDecodeError:pass
 return out
def validate_approval(a,r,e):
 checks={"SCHEMA":a.get("schema_version")=="argo-discoveryworld-latency-calibration-approval/v1","STATUS":a.get("status")=="APPROVED" and a.get("approved_by")=="user","SCOPE":a.get("scope")=="exactly 12 exploratory zero-model latency episodes totaling 640 planned steps","IDENTITY":a.get("runner_path")=="experiments/argo_workflow_followup/discoveryworld_latency_calibration/run.py" and a.get("runner_sha256")==sha(r) and a.get("episode_path")=="experiments/argo_workflow_followup/discoveryworld_latency_calibration/episode.py" and a.get("episode_sha256")==sha(e),"ENVIRONMENT":a.get("interpreter")==EXPECTED_INTERPRETER and a.get("interpreter_sha256")==EXPECTED_INTERPRETER_SHA and a.get("discoveryworld_commit")==EXPECTED_COMMIT,"GRID":a.get("task_families")==2 and a.get("seed")==0 and a.get("horizons")==HORIZONS and a.get("repeats")==REPEATS and a.get("episodes")==12 and a.get("planned_steps")==640,"TIME":a.get("timeout_seconds")==TIMEOUT_SECONDS and a.get("max_subprocess_wait_seconds")==720 and a.get("concurrency")==1,"BOUNDARY":a.get("purpose")=="exploratory runtime calibration with partial progress, not determinism certification" and a.get("docker_calls")==0 and a.get("model_calls")==0 and a.get("scorecard_access") is False and a.get("gold_generation") is False and a.get("vision") is False and a.get("api_spend_usd")==0.0};errors=[k for k,v in checks.items() if not v];return {"approved":not errors,"checks":checks,"errors":errors}
def execute(command):
 started=time.monotonic()
 try:
  d=subprocess.run(command,text=True,capture_output=True,check=False,timeout=TIMEOUT_SECONDS,env=sanitized_env());return {"command":command,"exit_code":d.returncode,"timed_out":False,"stdout":d.stdout,"stderr":d.stderr,"duration_seconds":round(time.monotonic()-started,6)}
 except subprocess.TimeoutExpired as x:
  stdout=x.stdout.decode(errors="replace") if isinstance(x.stdout,bytes) else (x.stdout or "");stderr=x.stderr.decode(errors="replace") if isinstance(x.stderr,bytes) else (x.stderr or "");return {"command":command,"exit_code":124,"timed_out":True,"stdout":stdout,"stderr":stderr,"duration_seconds":round(time.monotonic()-started,6)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);x=p.parse_args();a=json.loads(x.approval.read_text());check=validate_approval(a,Path(__file__),Path(__file__).with_name("episode.py"))
 if not check["approved"]:
  r={"schema_version":"argo-discoveryworld-latency-calibration-result/v1","status":"BLOCKED_BEFORE_EPISODES","approval":check,"episodes_started":0,"planned_steps_started":0,"model_calls":0,"spend_usd":0.0};x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(r,indent=2,sort_keys=True));return 2
 rows=[]
 for command in build_commands(a["interpreter"],Path(__file__).with_name("episode.py")):
  run=execute(command);events=parse_events(run["stdout"]);complete=next((e for e in reversed(events) if e.get("event")=="complete"),None);progress=[e for e in events if e.get("event")=="progress"];rows.append({"run":{k:v for k,v in run.items() if k!="stdout"},"stdout_sha256":hashlib.sha256(run["stdout"].encode()).hexdigest(),"events":events,"complete":complete,"max_progress_step":max((e.get("step",0) for e in progress),default=0)})
 summary={"episodes_expected":12,"episodes_completed":sum(r["complete"] is not None for r in rows),"episodes_timed_out":sum(r["run"]["timed_out"] for r in rows),"episodes_with_partial_progress":sum(r["max_progress_step"]>0 and r["complete"] is None for r in rows),"planned_steps":640,"completed_steps":sum((r["complete"] or {}).get("steps",0) for r in rows),"max_partial_step":max((r["max_progress_step"] for r in rows),default=0),"task_families":2,"inference_units":2};r={"schema_version":"argo-discoveryworld-latency-calibration-result/v1","created_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),"status":"COMPLETE_EXPLORATORY_CALIBRATION","approval_sha256":sha(x.approval),"runner_sha256":sha(Path(__file__)),"episode_sha256":sha(Path(__file__).with_name("episode.py")),"summary":summary,"episodes":rows,"model_calls":0,"spend_usd":0.0};x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":r["status"],"summary":summary},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
