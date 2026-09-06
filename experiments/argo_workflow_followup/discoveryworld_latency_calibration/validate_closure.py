#!/usr/bin/env python3
"""Validate the completed exploratory latency calibration closure."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate(path,root):
 root=Path(root);o=json.loads(Path(path).read_text());errors=[];loaded={}
 for name,pk,hk in [("proposal","proposal","proposal_sha256"),("runner","runner","runner_sha256"),("episode","episode","episode_sha256"),("approved","approved_authorization","approved_authorization_sha256"),("consumed","consumed_authorization","consumed_authorization_sha256"),("result","result","result_sha256"),("analysis","analysis","analysis_sha256")]:
  p=root/o.get(pk,"")
  if not p.is_file() or sha(p)!=o.get(hk):errors.append("IDENTITY:"+name)
  elif p.suffix==".json":loaded[name]=json.loads(p.read_text())
 approved=loaded.get("approved",{});consumed=loaded.get("consumed",{});result=loaded.get("result",{});analysis=loaded.get("analysis",{})
 if approved.get("status")!="APPROVED" or approved.get("approved_by")!="user" or approved.get("approval_message")!="승인할게 실험 진행해":errors.append("APPROVAL")
 if approved.get("approved_proposal_sha256")!=o.get("proposal_sha256") or result.get("approval_sha256")!=o.get("approved_authorization_sha256"):errors.append("APPROVAL_BINDING")
 if consumed.get("status")!="CONSUMED_COMPLETE_EXPLORATORY" or consumed.get("remaining_attempts")!=0 or consumed.get("retry_authorized") is not False:errors.append("CONSUMED_STATE")
 ex=o.get("execution",{});expected_ex={"controller_exit_code":0,"episodes_completed":12,"episodes_timed_out":0,"completed_steps":640,"action_successes":640,"tick_successes":640}
 for k,v in expected_ex.items():
  if ex.get(k)!=v:errors.append("EXECUTION:"+k)
 raw=result.get("summary",{})
 if result.get("status")!="COMPLETE_EXPLORATORY_CALIBRATION" or raw.get("episodes_completed")!=12 or raw.get("completed_steps")!=640 or raw.get("episodes_timed_out")!=0:errors.append("RAW_RESULT")
 analyzed=analysis.get("result_analysis",{})
 if analyzed.get("passed") is not True or analyzed.get("measured")!=o.get("measured") or analyzed.get("latency_by_scenario")!=o.get("latency_by_scenario"):errors.append("ANALYSIS_BINDING")
 m=o.get("measured",{});expected_m={"episodes_completed":12,"completed_steps":640,"action_successes":640,"tick_successes":640,"same_cell_chain_pairs_exact":"6/6","cross_horizon_prefix_groups_exact":"14/14","hidden_key_episodes":0,"vision_accessed_episodes":0,"commits_exact":12,"maximum_observed_horizon":100}
 for k,v in expected_m.items():
  if m.get(k)!=v:errors.append("MEASURED:"+k)
 if set(o.get("latency_by_scenario",{}))!={"Archaeology Dating","Combinatorial Chemistry"} or not all(v.get("median_projected_1000_seconds",0)>120 for v in o.get("latency_by_scenario",{}).values()):errors.append("LATENCY")
 auth=o.get("authorization",{})
 if auth.get("episodes_consumed")!=12 or auth.get("remaining_attempts")!=0 or auth.get("retry_authorized") is not False:errors.append("AUTHORITY")
 required={"observed 1000-step completion","seeds 1-4 determinism","long-horizon determinism","task completion or score","correction/handoff gold validity","behavioral TREE/TYPED comparison","model efficacy","OS-level task isolation"}
 if not required.issubset(set(o.get("scope_not_supported",[]))):errors.append("SCOPE_LIMITS")
 if o.get("status")!="CLOSED_COMPLETE_EXPLORATORY_NO_RETRY" or o.get("model_calls")!=0 or o.get("spend_usd")!=0.0:errors.append("CLOSURE_SCOPE")
 return {"passed":not errors,"errors":errors,"status":o.get("status"),"maximum_observed_horizon":m.get("maximum_observed_horizon"),"attempts_remaining":auth.get("remaining_attempts")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--closure",type=Path,required=True);p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args();r=validate(a.closure,a.root);print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
