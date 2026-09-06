#!/usr/bin/env python3
"""Validate the no-retry long-horizon runtime-feasibility closure."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate(path,root):
 root=Path(root);o=json.loads(Path(path).read_text());errors=[];loaded={}
 for name,pk,hk in [("proposal","proposal","proposal_sha256"),("runner","runner","runner_sha256"),("episode","episode","episode_sha256"),("approved","approved_authorization","approved_authorization_sha256"),("consumed","consumed_authorization","consumed_authorization_sha256"),("result","result","result_sha256")]:
  p=root/o.get(pk,"")
  if not p.is_file() or sha(p)!=o.get(hk):errors.append("IDENTITY:"+name)
  elif p.suffix==".json":loaded[name]=json.loads(p.read_text())
 approved=loaded.get("approved",{});consumed=loaded.get("consumed",{});result=loaded.get("result",{})
 if approved.get("status")!="APPROVED" or approved.get("approved_by")!="user" or approved.get("approval_message")!="승인":errors.append("APPROVAL")
 if approved.get("approved_proposal_sha256")!=o.get("proposal_sha256") or result.get("approval_sha256")!=o.get("approved_authorization_sha256"):errors.append("APPROVAL_BINDING")
 if consumed.get("status")!="CONSUMED_FAIL_RUNTIME_TIMEOUT" or consumed.get("remaining_attempts")!=0 or consumed.get("retry_authorized") is not False:errors.append("CONSUMED_STATE")
 ex=o.get("execution",{});expected={"controller_exit_code":1,"episode_subprocesses_started":20,"episode_subprocesses_timed_out":20,"episode_subprocesses_completed":0,"episode_receipts":0,"per_episode_timeout_seconds":120,"stderr_nonempty":0,"stdout_nonempty":0}
 for k,v in expected.items():
  if ex.get(k)!=v:errors.append("EXECUTION:"+k)
 episodes=result.get("episodes",[])
 if len(episodes)!=20 or any(e.get("run",{}).get("exit_code")!=124 or e.get("run",{}).get("timed_out") is not True or e.get("result")!={} for e in episodes):errors.append("RAW_EPISODES")
 expected_summary={"action_successes":0,"commits_exact":0,"episodes_completed":0,"episodes_expected":20,"hidden_key_episodes":0,"inference_units":2,"pairs_exact":0,"pairs_expected":10,"steps_expected":20000,"task_families":2,"tick_successes":0}
 if result.get("status")!="FAIL" or result.get("summary")!=expected_summary or o.get("raw_summary")!=expected_summary:errors.append("RAW_SUMMARY")
 if set(o.get("observed_semantics",{}).values())!={"NOT_OBSERVED"} or len(o.get("observed_semantics",{}))!=7:errors.append("OBSERVED_SEMANTICS")
 auth=o.get("authorization",{})
 if auth.get("subprocess_attempts_consumed")!=20 or auth.get("remaining_attempts")!=0 or auth.get("retry_authorized") is not False:errors.append("AUTHORITY")
 required_not={"DiscoveryWorld nondeterminism","DiscoveryWorld determinism","zero actual steps executed","task failure","task success","hidden-key absence","model behavior","permission to retry or shorten endpoint"}
 if not required_not.issubset(set(o.get("not_claimed",[]))):errors.append("NOT_CLAIMED")
 if "do not shorten, exclude, or retry these confirmatory-shaped episodes post hoc" not in o.get("next_requirements",[]):errors.append("NO_POSTHOC")
 if o.get("decision")!="REJECT_FROZEN_1000_STEP_120_SECOND_PROTOCOL_AS_RUNTIME_INFEASIBLE__NO_DETERMINISM_JUDGMENT" or o.get("status")!="CLOSED_FAIL_RUNTIME_FEASIBILITY_NO_RETRY":errors.append("DECISION")
 if o.get("model_calls")!=0 or o.get("spend_usd")!=0.0:errors.append("EXECUTION_SCOPE")
 return {"passed":not errors,"errors":errors,"status":o.get("status"),"timeouts":ex.get("episode_subprocesses_timed_out"),"attempts_remaining":auth.get("remaining_attempts")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--closure",type=Path,required=True);p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args();r=validate(a.closure,a.root);print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
