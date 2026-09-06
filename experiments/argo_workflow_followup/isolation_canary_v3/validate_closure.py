#!/usr/bin/env python3
"""Validate the consumed one-attempt v3 generic isolation canary closure."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate(path,root):
 root=Path(root);obj=json.loads(Path(path).read_text());errors=[];loaded={}
 for name,pk,hk in [("proposal","proposal","proposal_sha256"),("runner","runner","runner_sha256"),("policy","policy","policy_sha256"),("approved","approved_authorization","approved_authorization_sha256"),("consumed","consumed_authorization","consumed_authorization_sha256"),("result","result","result_sha256")]:
  source=root/obj.get(pk,"")
  if not source.is_file() or sha(source)!=obj.get(hk):errors.append("IDENTITY:"+name)
  elif source.suffix==".json":loaded[name]=json.loads(source.read_text())
 approved=loaded.get("approved",{});consumed=loaded.get("consumed",{});result=loaded.get("result",{})
 if approved.get("status")!="APPROVED" or approved.get("approved_by")!="user" or approved.get("approval_message")!="승인":errors.append("APPROVAL")
 if approved.get("approved_proposal_sha256")!=obj.get("proposal_sha256") or result.get("approval_sha256")!=obj.get("approved_authorization_sha256"):errors.append("APPROVAL_BINDING")
 if consumed.get("status")!="CONSUMED_PASS" or consumed.get("remaining_attempts")!=0 or consumed.get("retry_authorized") is not False:errors.append("CONSUMED_STATE")
 expected_checks={"external_network_blocked","forbidden_paths_blocked","image_identity","loopback_service_absent","no_secret_environment","one_container_exit_zero","oracle_not_readable","released_case_readable","withheld_mount_absent"}
 if set(obj.get("checks",{}))!=expected_checks or not all(obj.get("checks",{}).values()):errors.append("CHECKS")
 if result.get("checks")!=obj.get("checks") or result.get("status")!="PASS" or result.get("all_pass") is not True:errors.append("RAW_RESULT")
 execution=obj.get("execution",{})
 expected={"docker_cli_invocations":2,"container_launch_attempts":1,"containers_started":1,"policy_episodes":1,"exit_code":0,"timed_out":False,"host_bind_mounts":2,"writable_host_bind_mounts":0}
 for key,value in expected.items():
  if execution.get(key)!=value:errors.append("EXECUTION:"+key)
 canary=obj.get("canary",{})
 if canary.get("released_case_readable") is not True or canary.get("oracle_readable") is not False or any(canary.get("forbidden_path_readable",{}).values()) or canary.get("external_network_reachable") is not False or canary.get("loopback_service_reachable") is not False or canary.get("secret_environment_keys")!=[] or canary.get("withheld_mount_visible") is not False:errors.append("CANARY")
 auth=obj.get("authorization",{})
 if auth.get("attempts_consumed")!=1 or auth.get("remaining_attempts")!=0 or auth.get("retry_authorized") is not False:errors.append("AUTHORITY_CONSUMPTION")
 required={"DiscoveryWorld-specific runner isolation","1000-step replay determinism","procedural-score semantics","correction/handoff gold validity","integrated task runner","model behavior or efficacy","permission for another Docker launch, task generation, or model call"}
 if not required.issubset(set(obj.get("scope_not_supported",[]))):errors.append("SCOPE_LIMITS")
 if obj.get("status")!="CLOSED_PASS_EXACT_GENERIC_CANARY_NO_RETRY" or obj.get("model_calls")!=0 or obj.get("spend_usd")!=0.0:errors.append("CLOSURE_SCOPE")
 return {"passed":not errors,"errors":errors,"status":obj.get("status"),"checks_passed":sum(obj.get("checks",{}).values()),"attempts_remaining":auth.get("remaining_attempts")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--closure",type=Path,required=True);p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args();r=validate(a.closure,a.root);print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
