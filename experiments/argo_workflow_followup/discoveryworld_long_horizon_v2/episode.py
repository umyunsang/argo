#!/usr/bin/env python3
"""Prospective DiscoveryWorld 1000-step determinism episode with flushed progress."""
from __future__ import annotations
import argparse,contextlib,hashlib,io,json,os,socket,subprocess,time
from pathlib import Path
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1");os.environ.setdefault("SDL_VIDEODRIVER","dummy");os.environ.setdefault("SDL_AUDIODRIVER","dummy")
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def emit(x):print(json.dumps(x,sort_keys=True),flush=True)
def block_network():
 def denied(*args,**kwargs):raise OSError("NETWORK_DISABLED_BY_LONG_HORIZON_V2")
 socket.create_connection=denied;original=socket.socket
 class NoNetworkSocket(original):
  def connect(self,address):raise OSError("NETWORK_DISABLED_BY_LONG_HORIZON_V2")
  def connect_ex(self,address):return 1
 socket.socket=NoNetworkSocket
def nested_keys(x):
 out=set()
 if isinstance(x,dict):
  for k,v in x.items():out.add(str(k));out.update(nested_keys(v))
 elif isinstance(x,list):
  for v in x:out.update(nested_keys(v))
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument("--scenario",required=True);p.add_argument("--difficulty",choices=["Normal"],required=True);p.add_argument("--seed",type=int,choices=[0,1,2,3,4],required=True);p.add_argument("--repeat",type=int,choices=[0,1],required=True);p.add_argument("--thread-id",type=int,required=True);a=p.parse_args();a.horizon=1000;block_network();captured=io.StringIO();started=time.monotonic()
 with contextlib.redirect_stdout(captured):
  import discoveryworld
  from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
  api=DiscoveryWorldAPI(threadID=a.thread_id);loaded=api.loadScenario(a.scenario,a.difficulty,a.seed,numUserAgents=1);obs=api.getAgentObservation(0)
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=Path(discoveryworld.__file__).resolve().parents[1],text=True).strip();hidden_names={"scoreCard","scoreNormalized","criticalQuestions","criticalHypotheses"};hidden=hidden_names & nested_keys(obs);chain=bytes(32);emit({"event":"loaded","scenario":a.scenario,"seed":a.seed,"horizon":a.horizon,"repeat":a.repeat,"commit":commit,"loaded":loaded,"elapsed_seconds":round(time.monotonic()-started,6)});action_ok=tick_ok=0;checkpoints={1,2,5,10,20,50,100,200,500,1000};directions=["north","east","south","west"]
 for step in range(1,a.horizon+1):
  action={"action":"ROTATE_DIRECTION","arg1":directions[(step-1)%4]};ar=api.performAgentAction(0,action);tr=api.tick();obs=api.getAgentObservation(0);hidden.update(hidden_names & nested_keys(obs));action_ok+=ar.get("success") is True;tick_ok+=tr.get("success") is True;chain=hashlib.sha256(chain+canonical({"step":step,"action":action,"action_result":ar,"tick_result":tr,"ui":obs["ui"]})).digest()
  if step in checkpoints or step==a.horizon:emit({"event":"progress","step":step,"chain_sha256":chain.hex(),"elapsed_seconds":round(time.monotonic()-started,6)})
 emit({"event":"complete","scenario":a.scenario,"seed":a.seed,"horizon":a.horizon,"repeat":a.repeat,"steps":a.horizon,"action_successes":action_ok,"tick_successes":tick_ok,"step_counter":api.getStepCounter(),"chain_sha256":chain.hex(),"hidden_keys_in_observation":sorted(hidden),"commit":commit,"vision_accessed":False,"captured_stdout_sha256":hashlib.sha256(captured.getvalue().encode()).hexdigest(),"elapsed_seconds":round(time.monotonic()-started,6),"model_calls":0,"spend_usd":0.0});return 0
if __name__=="__main__":raise SystemExit(main())
