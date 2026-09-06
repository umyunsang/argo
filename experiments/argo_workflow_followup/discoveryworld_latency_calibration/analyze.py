#!/usr/bin/env python3
"""Deterministic analysis of the frozen exploratory latency calibration."""
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

def ols(xs,ys):
 mx=sum(xs)/len(xs);my=sum(ys)/len(ys);den=sum((x-mx)**2 for x in xs);slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den;return my-slope*mx,slope
def analyze(result):
 errors=[];episodes=result.get("episodes",[]);rows=[]
 if len(episodes)!=12:errors.append("EPISODE_COUNT")
 for episode in episodes:
  c=episode.get("complete")
  if not isinstance(c,dict):errors.append("MISSING_COMPLETE");continue
  loaded=next((x for x in episode.get("events",[]) if x.get("event")=="loaded"),None)
  if loaded is None:errors.append("MISSING_LOADED");continue
  rows.append({"scenario":c["scenario"],"horizon":c["horizon"],"repeat":c["repeat"],"load_seconds":loaded["elapsed_seconds"],"elapsed_seconds":c["elapsed_seconds"],"step_seconds":(c["elapsed_seconds"]-loaded["elapsed_seconds"])/c["steps"],"chain":c["chain_sha256"],"actions":c["action_successes"],"ticks":c["tick_successes"],"hidden":c["hidden_keys_in_observation"],"vision":c["vision_accessed"],"commit":c["commit"]})
 pairs=defaultdict(list)
 for r in rows:pairs[(r["scenario"],r["horizon"])].append(r)
 pair_exact=sum(len(v)==2 and len({x["chain"] for x in v})==1 for v in pairs.values())
 prefix=defaultdict(list)
 for episode in episodes:
  c=episode.get("complete") or {}
  for event in episode.get("events",[]):
   if event.get("event")=="progress":prefix[(c.get("scenario"),event["step"])].append(event["chain_sha256"])
 prefix_multi={k:v for k,v in prefix.items() if len(v)>=2};prefix_exact=sum(len(set(v))==1 for v in prefix_multi.values())
 latency={}
 for scenario in sorted({r["scenario"] for r in rows}):
  values=[r for r in rows if r["scenario"]==scenario];intercept,slope=ols([r["horizon"] for r in values],[r["elapsed_seconds"] for r in values]);median_load=statistics.median(r["load_seconds"] for r in values);median_step=statistics.median(r["step_seconds"] for r in values);latency[scenario]={"median_load_seconds":median_load,"median_seconds_per_step":median_step,"minimum_seconds_per_step":min(r["step_seconds"] for r in values),"maximum_seconds_per_step":max(r["step_seconds"] for r in values),"median_projected_1000_seconds":median_load+1000*median_step,"ols_intercept_seconds":intercept,"ols_seconds_per_step":slope,"ols_projected_1000_seconds":intercept+1000*slope}
 measured={"episodes_completed":len(rows),"completed_steps":sum(r["horizon"] for r in rows),"action_successes":sum(r["actions"] for r in rows),"tick_successes":sum(r["ticks"] for r in rows),"same_cell_chain_pairs_exact":f"{pair_exact}/{len(pairs)}","cross_horizon_prefix_groups_exact":f"{prefix_exact}/{len(prefix_multi)}","hidden_key_episodes":sum(bool(r["hidden"]) for r in rows),"vision_accessed_episodes":sum(bool(r["vision"]) for r in rows),"commits_exact":sum(r["commit"]=="fd591323920be0d3786ef350955de1945aa571e5" for r in rows),"maximum_observed_horizon":max((r["horizon"] for r in rows),default=0),"controller_wall_seconds":sum(e.get("run",{}).get("duration_seconds",0) for e in episodes)}
 expected={"episodes_completed":12,"completed_steps":640,"action_successes":640,"tick_successes":640,"same_cell_chain_pairs_exact":"6/6","cross_horizon_prefix_groups_exact":"14/14","hidden_key_episodes":0,"vision_accessed_episodes":0,"commits_exact":12,"maximum_observed_horizon":100}
 for k,v in expected.items():
  if measured.get(k)!=v:errors.append("MEASURED:"+k)
 if result.get("summary",{}).get("episodes_completed")!=12 or result.get("summary",{}).get("completed_steps")!=640:errors.append("RAW_SUMMARY")
 return {"passed":not errors,"errors":errors,"measured":measured,"latency_by_scenario":latency,"inference_units":2,"long_horizon_certified":False,"interpretation":"Exploratory seed-0 short-horizon replay is exact through 100 steps. Latency projections are planning evidence only and do not replace an observed 1000-step run.","model_calls":0,"spend_usd":0.0}
def main():
 p=argparse.ArgumentParser();p.add_argument("--result",type=Path,required=True);a=p.parse_args();r=analyze(json.loads(a.result.read_text()));print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
