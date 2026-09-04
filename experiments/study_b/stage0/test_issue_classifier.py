#!/usr/bin/env python3
from __future__ import annotations
import issue_classifier as ic
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except ic.IssueClassificationViolation as e:check(n,text in str(e),str(e))
def base():return {"event_id":"incident-001","phase":"execution","agent_exit_state":"failed","environment_health":"healthy","neutral_control_status":"pass","external_service_status":"available","agent_action_preceded_failure":True,"contract_ambiguity":False,"sealed_identity_mismatch":False,"evidence_complete":True}
def main():
 agent=ic.classify(base());check("agent failure is not retryable",agent["classification"]=="AGENT_CAUSED_FAILURE" and agent["retry_allowed"] is False,str(agent));check("original remains in reliability",agent["retain_original_in_reliability"] is True,str(agent))
 infra=base();infra.update(environment_health="unhealthy",neutral_control_status="fail");r=ic.classify(infra);check("infrastructure failure gets one retry",r["classification"]=="ENVIRONMENT_OR_INFRASTRUCTURE" and r["retry_allowed"] and r["max_retries"]==1,str(r))
 protocol=base();protocol["contract_ambiguity"]=True;r=ic.classify(protocol);check("protocol defect blocks",r["classification"]=="PROTOCOL_DEFECT" and r["retry_allowed"] is False,str(r))
 unresolved=base();unresolved["evidence_complete"]=False;check("incomplete evidence is unresolved",ic.classify(unresolved)["classification"]=="UNRESOLVED")
 leaked=base();leaked["cell_id"]="G1C1F1";expect("condition field is forbidden",lambda:ic.classify(leaked),"ISSUE_CLASSIFIER_FORBIDDEN_FIELD: cell_id")
 scored=base();scored["official_score"]=0;expect("official score is forbidden",lambda:ic.classify(scored),"ISSUE_CLASSIFIER_FORBIDDEN_FIELD: official_score")
 ambiguous=base();ambiguous.update(agent_action_preceded_failure=False,agent_exit_state="unknown");check("unclear healthy failure is unresolved",ic.classify(ambiguous)["classification"]=="UNRESOLVED")
 external=base();external["external_service_status"]="unavailable";check("external outage is infrastructure",ic.classify(external)["classification"]=="ENVIRONMENT_OR_INFRASTRUCTURE")
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
