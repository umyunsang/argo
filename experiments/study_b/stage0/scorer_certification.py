#!/usr/bin/env python3
"""Deterministic scorer-anchor and development floor/ceiling certification."""
from __future__ import annotations
import statistics
class ScorerCertificationViolation(ValueError):pass
def require(ok:bool,msg:str)->None:
 if not ok:raise ScorerCertificationViolation(msg)
def validate_anchors(a:dict)->dict:
 expected={"fatal","valid_wrong","valid_correct"};require(set(a)==expected,"SCORER_ANCHOR_SET_INVALID")
 for name in sorted(expected):
  runs=a[name];require(isinstance(runs,list) and len(runs)>=3,f"SCORER_REPEAT_COUNT_INSUFFICIENT: {name}")
  values=[x.get("official_score") for x in runs];require(len(set(values))==1,f"SCORER_NONDETERMINISTIC: {name} values={values}")
 for x in a["fatal"]:require(x.get("ordinal_score")==0 and x.get("official_score")==0 and x.get("inadmissible_execution") is True,"FATAL_STATE_SEMANTICS_INVALID")
 for x in a["valid_wrong"]:require(x.get("ordinal_score")==1 and x.get("official_score")==0 and x.get("inadmissible_execution") is False,"VALID_WRONG_STATE_SEMANTICS_INVALID")
 for x in a["valid_correct"]:require(x.get("ordinal_score")==2 and x.get("official_score")==1 and x.get("inadmissible_execution") is False,"VALID_CORRECT_STATE_SEMANTICS_INVALID")
 return {"passed":True,"repeat_count":min(len(v) for v in a.values()),"fatal_score":0,"valid_wrong_score":0,"valid_correct_score":1}
def validate_development_distribution(scores:dict,min_tasks:int=4)->dict:
 expected={f"G{g}C{c}F{f}" for g in (0,1) for c in (0,1) for f in (0,1)};require(set(scores)==expected,"DEVELOPMENT_CELL_SET_INVALID")
 summary={}
 for cell in sorted(expected):
  xs=scores[cell];require(len(xs)>=min_tasks,f"DEVELOPMENT_TASK_COUNT_INSUFFICIENT: {cell} observed={len(xs)} minimum={min_tasks}")
  for x in xs:require(isinstance(x,(int,float)) and not isinstance(x,bool) and 0<=x<=1,f"NORMALIZED_SCORE_OUT_OF_RANGE: {cell} value={x}")
  if all(x==0 for x in xs):raise ScorerCertificationViolation(f"UNINFORMATIVE_SCORE_FLOOR: {cell}")
  if all(x==1 for x in xs):raise ScorerCertificationViolation(f"UNINFORMATIVE_SCORE_CEILING: {cell}")
  summary[cell]={"n_tasks":len(xs),"mean":statistics.mean(xs),"min":min(xs),"max":max(xs),"floor_count":sum(x==0 for x in xs),"ceiling_count":sum(x==1 for x in xs)}
 return {"passed":True,"cells":summary,"inference_unit":"task","power_certified":False}
