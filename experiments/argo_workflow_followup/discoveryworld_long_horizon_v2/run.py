#!/usr/bin/env python3
"""Approval-gated prospective DiscoveryWorld 1000-step determinism controller."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,time
from collections import defaultdict
from pathlib import Path
TASKS=[(family,scenario,"Normal",seed) for family,scenario in [("chemistry","Combinatorial Chemistry"),("archaeology","Archaeology Dating")] for seed in range(5)]
REPEATS=2
STEPS=1000
TIMEOUT_SECONDS=180
EXPECTED_COMMIT="fd591323920be0d3786ef350955de1945aa571e5"
EXPECTED_INTERPRETER="/Users/um-yunsang/.cache/argo-research/DiscoveryWorld/.venv/bin/python"
EXPECTED_INTERPRETER_SHA="68100c5188b837802c7ae52398389d121b1c063ed244dec11649775b539c3a30"
EXPECTED_FAILURE_CLOSURE="8c0be6104e417d496feffb318551a0d45d230c5c2f9fdfdea45cfc0f9ee4a61e"
EXPECTED_CALIBRATION_CLOSURE="0007f00e8d5a30325528be714175cdd4d862902fc718ed1e4aad57ca05e16199"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sanitized_env():return {"HOME":"/tmp","PATH":"/usr/bin:/bin:/opt/homebrew/bin","PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def build_commands(interpreter,episode):
 out=[]
 for ti,(_,scenario,difficulty,seed) in enumerate(TASKS):
  for repeat in range(REPEATS):out.append([str(interpreter),str(Path(episode).resolve()),"--scenario",scenario,"--difficulty",difficulty,"--seed",str(seed),"--repeat",str(repeat),"--thread-id",str(1010000+ti*10+repeat)])
 return out
def parse_events(text):
 if isinstance(text,bytes):text=text.decode(errors="replace")
 out=[]
 for line in (text or "").splitlines():
  try:
   v=json.loads(line)
   if isinstance(v,dict):out.append(v)
  except json.JSONDecodeError:pass
 return out
def validate_approval(a,r,e):
 checks={"SCHEMA":a.get("schema_version")=="argo-discoveryworld-long-horizon-v2-approval/v1","STATUS":a.get("status")=="APPROVED" and a.get("approved_by")=="user","SCOPE":a.get("scope")=="exactly 20 prospective zero-model 1000-step determinism episodes totaling 20000 steps","IDENTITY":a.get("runner_path")=="experiments/argo_workflow_followup/discoveryworld_long_horizon_v2/run.py" and a.get("runner_sha256")==sha(r) and a.get("episode_path")=="experiments/argo_workflow_followup/discoveryworld_long_horizon_v2/episode.py" and a.get("episode_sha256")==sha(e),"ENVIRONMENT":a.get("interpreter")==EXPECTED_INTERPRETER and a.get("interpreter_sha256")==EXPECTED_INTERPRETER_SHA and a.get("discoveryworld_commit")==EXPECTED_COMMIT,"GRID":a.get("task_families")==2 and a.get("seeds")==[0,1,2,3,4] and a.get("repeats")==2 and a.get("steps_per_episode")==1000 and a.get("episodes")==20 and a.get("total_steps")==20000,"TIME":a.get("timeout_seconds")==180 and a.get("max_subprocess_wait_seconds")==3600 and a.get("concurrency")==1,"PRIOR":a.get("prior_failure_closure_sha256")==EXPECTED_FAILURE_CLOSURE and a.get("calibration_closure_sha256")==EXPECTED_CALIBRATION_CLOSURE,"BOUNDARY":a.get("docker_calls")==0 and a.get("model_calls")==0 and a.get("scorecard_access") is False and a.get("gold_generation") is False and a.get("vision") is False and a.get("task_completion_endpoint") is False and a.get("api_spend_usd")==0.0};errors=[k for k,v in checks.items() if not v];return {"approved":not errors,"checks":checks,"errors":errors}
def execute(command):
 started=time.monotonic()
 try:
  d=subprocess.run(command,text=True,capture_output=True,check=False,timeout=TIMEOUT_SECONDS,env=sanitized_env());return {"command":command,"exit_code":d.returncode,"timed_out":False,"stdout":d.stdout,"stderr":d.stderr,"duration_seconds":round(time.monotonic()-started,6)}
 except subprocess.TimeoutExpired as x:
  stdout=x.stdout.decode(errors="replace") if isinstance(x.stdout,bytes) else (x.stdout or "");stderr=x.stderr.decode(errors="replace") if isinstance(x.stderr,bytes) else (x.stderr or "");return {"command":command,"exit_code":124,"timed_out":True,"stdout":stdout,"stderr":stderr,"duration_seconds":round(time.monotonic()-started,6)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);x=p.parse_args();a=json.loads(x.approval.read_text());check=validate_approval(a,Path(__file__),Path(__file__).with_name("episode.py"))
 if not check["approved"]:
  r={"schema_version":"argo-discoveryworld-long-horizon-v2-result/v1","status":"BLOCKED_BEFORE_EPISODES","approval":check,"episodes_started":0,"steps_observed":0,"model_calls":0,"spend_usd":0.0};x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(r,indent=2,sort_keys=True));return 2
 rows=[]
 for command in build_commands(a["interpreter"],Path(__file__).with_name("episode.py")):
  run=execute(command);events=parse_events(run["stdout"]);complete=next((e for e in reversed(events) if e.get("event")=="complete"),None);progress=[e for e in events if e.get("event")=="progress"];rows.append({"run":{k:v for k,v in run.items() if k!="stdout"},"stdout_sha256":hashlib.sha256(run["stdout"].encode()).hexdigest(),"events":events,"complete":complete,"max_progress_step":max((e.get("step",0) for e in progress),default=0)})
 groups=defaultdict(list)
 for row in rows:
  c=row["complete"]
  if c:groups[(c["scenario"],c["seed"])].append(row)
 pairs=[]
 for key in sorted(groups):
  values=groups[key]
  def progress_map(row):return {e["step"]:e["chain_sha256"] for e in row["events"] if e.get("event")=="progress"}
  exact=len(values)==2 and values[0]["complete"]["chain_sha256"]==values[1]["complete"]["chain_sha256"] and progress_map(values[0])==progress_map(values[1])
  pairs.append({"scenario":key[0],"seed":key[1],"repeats":len(values),"exact":exact,"final_chain_match":len(values)==2 and values[0]["complete"]["chain_sha256"]==values[1]["complete"]["chain_sha256"],"checkpoint_chain_match":len(values)==2 and progress_map(values[0])==progress_map(values[1])})
 summary={"episodes_expected":20,"episodes_completed":sum(r["complete"] is not None for r in rows),"episodes_timed_out":sum(r["run"]["timed_out"] for r in rows),"episodes_with_partial_progress":sum(r["complete"] is None and r["max_progress_step"]>0 for r in rows),"steps_expected":20000,"completed_steps":sum((r["complete"] or {}).get("steps",0) for r in rows),"max_progress_step":max((r["max_progress_step"] for r in rows),default=0),"action_successes":sum((r["complete"] or {}).get("action_successes",0) for r in rows),"tick_successes":sum((r["complete"] or {}).get("tick_successes",0) for r in rows),"pairs_expected":10,"pairs_exact":sum(p["exact"] for p in pairs),"hidden_key_episodes":sum(bool((r["complete"] or {}).get("hidden_keys_in_observation")) for r in rows),"commits_exact":sum((r["complete"] or {}).get("commit")==EXPECTED_COMMIT for r in rows),"task_families":2,"inference_units":2}
 passed=summary=={"episodes_expected":20,"episodes_completed":20,"episodes_timed_out":0,"episodes_with_partial_progress":0,"steps_expected":20000,"completed_steps":20000,"max_progress_step":1000,"action_successes":20000,"tick_successes":20000,"pairs_expected":10,"pairs_exact":10,"hidden_key_episodes":0,"commits_exact":20,"task_families":2,"inference_units":2};r={"schema_version":"argo-discoveryworld-long-horizon-v2-result/v1","created_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),"status":"PASS" if passed else "FAIL","approval_sha256":sha(x.approval),"runner_sha256":sha(Path(__file__)),"episode_sha256":sha(Path(__file__).with_name("episode.py")),"summary":summary,"pairs":pairs,"episodes":rows,"all_pass":passed,"model_calls":0,"spend_usd":0.0};x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":r["status"],"summary":summary},indent=2,sort_keys=True));return 0 if passed else 1
if __name__=="__main__":raise SystemExit(main())
