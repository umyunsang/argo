#!/usr/bin/env python3
"""Approval-gated controller for fixed DiscoveryWorld long-horizon replay."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,time
from collections import defaultdict
from pathlib import Path

TASKS=[(family,scenario,"Normal",seed) for family,scenario in [("chemistry","Combinatorial Chemistry"),("archaeology","Archaeology Dating")] for seed in range(5)]
REPEATS=2
STEPS=1000
EPISODE_TIMEOUT_SECONDS=120
EXPECTED_COMMIT="fd591323920be0d3786ef350955de1945aa571e5"
EXPECTED_INTERPRETER="/Users/um-yunsang/.cache/argo-research/DiscoveryWorld/.venv/bin/python"
EXPECTED_INTERPRETER_SHA="68100c5188b837802c7ae52398389d121b1c063ed244dec11649775b539c3a30"

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sanitized_env():
 return {"HOME":"/tmp","PATH":"/usr/bin:/bin:/opt/homebrew/bin","PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def build_commands(interpreter,episode_path):
 commands=[]
 for task_index,(family,scenario,difficulty,seed) in enumerate(TASKS):
  for repeat in range(REPEATS):
   thread_id=810000+task_index*10+repeat
   commands.append([str(interpreter),str(Path(episode_path).resolve()),"--scenario",scenario,"--difficulty",difficulty,"--seed",str(seed),"--repeat",str(repeat),"--thread-id",str(thread_id),"--steps",str(STEPS)])
 return commands
def validate_approval(approval,runner_path,episode_path):
 checks={
  "SCHEMA":approval.get("schema_version")=="argo-discoveryworld-long-horizon-approval/v1",
  "STATUS":approval.get("status")=="APPROVED" and approval.get("approved_by")=="user",
  "SCOPE":approval.get("scope")=="exactly 20 zero-model deterministic replay episodes totaling 20000 steps",
  "IDENTITY":approval.get("runner_path")=="experiments/argo_workflow_followup/discoveryworld_long_horizon/run.py" and approval.get("runner_sha256")==sha(runner_path) and approval.get("episode_path")=="experiments/argo_workflow_followup/discoveryworld_long_horizon/episode.py" and approval.get("episode_sha256")==sha(episode_path),
  "ENVIRONMENT":approval.get("discoveryworld_commit")==EXPECTED_COMMIT and approval.get("interpreter")==EXPECTED_INTERPRETER and approval.get("interpreter_sha256")==EXPECTED_INTERPRETER_SHA,
  "GRID":approval.get("task_families")==2 and approval.get("seeds")==[0,1,2,3,4] and approval.get("repeats")==REPEATS and approval.get("steps_per_episode")==STEPS and approval.get("episodes")==20 and approval.get("total_steps")==20000,
  "TIME":approval.get("episode_timeout_seconds")==EPISODE_TIMEOUT_SECONDS and approval.get("max_subprocess_wait_seconds")==2400 and approval.get("concurrency")==1,
  "BOUNDARY":approval.get("docker_calls")==0 and approval.get("model_calls")==0 and approval.get("api_spend_usd")==0.0 and approval.get("scorecard_access") is False and approval.get("gold_generation") is False and approval.get("vision") is False,
 }
 errors=[k for k,v in checks.items() if not v];return {"approved":not errors,"checks":checks,"errors":errors}
def execute(command):
 started=time.monotonic()
 try:
  done=subprocess.run(command,text=True,capture_output=True,check=False,timeout=EPISODE_TIMEOUT_SECONDS,env=sanitized_env())
  return {"command":command,"exit_code":done.returncode,"timed_out":False,"stdout":done.stdout,"stderr":done.stderr,"duration_seconds":round(time.monotonic()-started,6)}
 except subprocess.TimeoutExpired as exc:
  return {"command":command,"exit_code":124,"timed_out":True,"stdout":exc.stdout or "","stderr":exc.stderr or "","duration_seconds":round(time.monotonic()-started,6)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();approval=json.loads(a.approval.read_text());check=validate_approval(approval,Path(__file__).resolve(),Path(__file__).with_name("episode.py"))
 if not check["approved"]:
  result={"schema_version":"argo-discoveryworld-long-horizon-result/v1","status":"BLOCKED_BEFORE_EPISODES","approval":check,"episodes_started":0,"steps_executed":0,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,indent=2,sort_keys=True));return 2
 raw=[];episodes=[]
 for command in build_commands(approval["interpreter"],Path(__file__).with_name("episode.py")):
  run=execute(command);raw.append(run);parsed={}
  if run["exit_code"]==0:
   try:parsed=json.loads(run["stdout"])
   except json.JSONDecodeError:parsed={}
  episodes.append({"run":{k:v for k,v in run.items() if k not in {"stdout"}},"result":parsed,"stdout_sha256":hashlib.sha256(run["stdout"].encode()).hexdigest()})
 groups=defaultdict(list)
 for row in episodes:
  value=row["result"]
  if value:groups[(value["scenario"],value["difficulty"],value["seed"])].append(value)
 pairs=[]
 for key in sorted(groups):
  values=sorted(groups[key],key=lambda x:x["repeat"]);fields=["chain_sha256","checkpoints","action_successes","tick_successes","step_counter","hidden_keys_in_observation","commit"]
  exact=len(values)==2 and all(values[0][field]==values[1][field] for field in fields)
  pairs.append({"scenario":key[0],"difficulty":key[1],"seed":key[2],"repeats":len(values),"exact":exact,"field_matches":{field:len(values)==2 and values[0][field]==values[1][field] for field in fields}})
 summary={"episodes_expected":20,"episodes_completed":sum(bool(x["result"]) for x in episodes),"steps_expected":20000,"action_successes":sum(x["result"].get("action_successes",0) for x in episodes),"tick_successes":sum(x["result"].get("tick_successes",0) for x in episodes),"pairs_expected":10,"pairs_exact":sum(x["exact"] for x in pairs),"hidden_key_episodes":sum(bool(x["result"].get("hidden_keys_in_observation")) for x in episodes),"commits_exact":sum(x["result"].get("commit")==EXPECTED_COMMIT for x in episodes),"task_families":2,"inference_units":2}
 passed=summary=={"episodes_expected":20,"episodes_completed":20,"steps_expected":20000,"action_successes":20000,"tick_successes":20000,"pairs_expected":10,"pairs_exact":10,"hidden_key_episodes":0,"commits_exact":20,"task_families":2,"inference_units":2}
 result={"schema_version":"argo-discoveryworld-long-horizon-result/v1","created_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),"status":"PASS" if passed else "FAIL","approval_sha256":sha(a.approval),"runner_sha256":sha(Path(__file__)),"episode_sha256":sha(Path(__file__).with_name("episode.py")),"summary":summary,"pairs":pairs,"episodes":episodes,"all_pass":passed,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"summary":summary},indent=2,sort_keys=True));return 0 if passed else 1
if __name__=="__main__":raise SystemExit(main())
