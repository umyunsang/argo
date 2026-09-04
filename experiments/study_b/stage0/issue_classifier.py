#!/usr/bin/env python3
"""Condition-blind classification of agent, infrastructure, and protocol failures."""
from __future__ import annotations
class IssueClassificationViolation(ValueError):pass
ALLOWED={"event_id","phase","agent_exit_state","environment_health","neutral_control_status","external_service_status","agent_action_preceded_failure","contract_ambiguity","sealed_identity_mismatch","evidence_complete"}
def require(ok:bool,msg:str)->None:
 if not ok:raise IssueClassificationViolation(msg)
def classify(e:dict)->dict:
 extra=set(e)-ALLOWED
 if extra:raise IssueClassificationViolation("ISSUE_CLASSIFIER_FORBIDDEN_FIELD: "+sorted(extra)[0])
 missing=ALLOWED-set(e)
 if missing:raise IssueClassificationViolation("ISSUE_CLASSIFIER_MISSING_FIELD: "+sorted(missing)[0])
 require(e["environment_health"] in ("healthy","unhealthy","unknown"),"ISSUE_ENVIRONMENT_HEALTH_INVALID")
 require(e["neutral_control_status"] in ("pass","fail","not_run"),"ISSUE_CONTROL_STATUS_INVALID")
 require(e["external_service_status"] in ("available","unavailable","not_used","unknown"),"ISSUE_EXTERNAL_STATUS_INVALID")
 if e["contract_ambiguity"] is True or e["sealed_identity_mismatch"] is True:kind="PROTOCOL_DEFECT";reason="contract ambiguity or sealed identity mismatch"
 elif e["evidence_complete"] is not True:kind="UNRESOLVED";reason="condition-blind evidence is incomplete"
 elif e["environment_health"]=="unhealthy" or e["neutral_control_status"]=="fail" or e["external_service_status"]=="unavailable":kind="ENVIRONMENT_OR_INFRASTRUCTURE";reason="condition-independent environment/control/service failure"
 elif e["environment_health"]=="healthy" and e["neutral_control_status"]=="pass" and e["external_service_status"] in ("available","not_used") and e["agent_exit_state"]=="failed" and e["agent_action_preceded_failure"] is True:kind="AGENT_CAUSED_FAILURE";reason="healthy controls and failure follows agent action"
 else:kind="UNRESOLVED";reason="facts do not identify responsibility"
 retry=kind=="ENVIRONMENT_OR_INFRASTRUCTURE"
 return {"classification":kind,"reason":reason,"retry_allowed":retry,"max_retries":1 if retry else 0,"retain_original_in_reliability":True,"condition_blind":True}
