#!/usr/bin/env python3
"""Deterministic development policies for evidence-invalidation manipulation."""
from __future__ import annotations
from collections import defaultdict,deque
DEPENDENCY_RELATIONS={"supports","informs_decision","governs_action","produces"}
class ContractViolation(ValueError):pass
def require(ok:bool,message:str)->None:
 if not ok:raise ContractViolation(message)
def validate_capsule(c:dict)->None:
 require(c.get("schema_version")=="argo-scientific-choice-capsule/v1","CAPSULE_SCHEMA")
 nodes=c.get("nodes",[]);ids=[x.get("id") for x in nodes];require(len(ids)==len(set(ids)) and all(ids),"CAPSULE_NODE_IDS")
 idset=set(ids)
 for e in c.get("dependency_edges",[]):require(e.get("source") in idset and e.get("target") in idset,"CAPSULE_DANGLING_EDGE")
 events=c.get("events",[]);require(events and all(x.get("source_id") in idset for x in events),"CAPSULE_EVENT_SOURCE")
 require(c.get("fixed_opportunities",{}).get("model_calls")==0,"CAPSULE_NOT_ZERO_COST")
def _base(c:dict)->dict:
 results=sorted(x["id"] for x in c["nodes"] if x["kind"]=="result")
 return {"requires_recheck":[],"stale_results":[],"preserved_results":results,"preserved_unaffected_results":results,"allowed_next_action":c["experiment_tree"]["active_next_action"]}
def typed_policy(c:dict,event:dict)->dict:
 validate_capsule(c);out=_base(c);adj=defaultdict(list)
 for e in c["dependency_edges"]:
  if e["relation"] in DEPENDENCY_RELATIONS:adj[e["source"]].append(e["target"])
 reached=set();q=deque([event["source_id"]])
 while q:
  cur=q.popleft()
  for nxt in sorted(adj[cur]):
   if nxt not in reached:reached.add(nxt);q.append(nxt)
 kinds={x["id"]:x["kind"] for x in c["nodes"]}
 out["requires_recheck"]=sorted(x for x in reached if kinds[x] in {"decision","action"})
 out["stale_results"]=sorted(x for x in reached if kinds[x]=="result")
 out["preserved_unaffected_results"]=sorted(set(out["preserved_results"])-set(out["stale_results"]))
 active=out["allowed_next_action"]
 if active in reached:
  decisions=sorted(x for x in reached if kinds[x]=="decision")
  require(bool(decisions),"AFFECTED_ACTION_WITHOUT_DECISION")
  out["allowed_next_action"]="recheck:"+decisions[0]
 return out
def result_tree_policy(c:dict,event:dict)->dict:
 validate_capsule(c);out=_base(c)
 # A result-driven tree has no source-to-decision transition. It records the
 # source event but cannot target a reopen without adding the tested mechanism.
 out["source_event_recorded"]=event["source_id"]
 return out
def comparable_view(out:dict)->dict:return {k:out[k] for k in ("requires_recheck","stale_results","preserved_results","preserved_unaffected_results","allowed_next_action")}
def evaluate(c:dict)->dict:
 validate_capsule(c);records=[];failures=[]
 for event in c["events"]:
  for name,fn in (("typed",typed_policy),("result_tree",result_tree_policy)):
   observed=fn(c,event);view=comparable_view(observed);expected=c["expected"][event["id"]][name];ok=view==expected
   records.append({"event_id":event["id"],"policy":name,"observed":observed,"expected":expected,"passed":ok})
   if not ok:failures.append(f"{event['id']}:{name}")
 relevant=next(x for x in records if x["event_id"]=="event:relevant" and x["policy"]=="typed")
 unrelated=next(x for x in records if x["event_id"]=="event:unrelated" and x["policy"]=="typed")
 manipulation=(relevant["observed"]["allowed_next_action"]!=unrelated["observed"]["allowed_next_action"] and bool(relevant["observed"]["requires_recheck"]) and not unrelated["observed"]["requires_recheck"])
 if not manipulation:failures.append("TYPED_POLICY_MANIPULATION_NOT_ACTIVE")
 return {"passed":not failures,"failures":failures,"records":records,"typed_policy_manipulation_active":manipulation,"efficacy_result":False}
