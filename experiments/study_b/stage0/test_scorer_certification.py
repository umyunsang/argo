#!/usr/bin/env python3
from __future__ import annotations
import copy
import scorer_certification as sc
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except sc.ScorerCertificationViolation as e:check(n,text in str(e),str(e))
def anchors():return {"fatal":[{"ordinal_score":0,"official_score":0,"inadmissible_execution":True} for _ in range(3)],"valid_wrong":[{"ordinal_score":1,"official_score":0,"inadmissible_execution":False} for _ in range(3)],"valid_correct":[{"ordinal_score":2,"official_score":1,"inadmissible_execution":False} for _ in range(3)]}
def main():
 a=anchors();check("three-state anchors pass",sc.validate_anchors(a)["passed"])
 crash=anchors();crash["fatal"][0]["ordinal_score"]=1;expect("fatal cannot score one",lambda:sc.validate_anchors(crash),"FATAL_STATE_SEMANTICS_INVALID")
 wrong=anchors();wrong["valid_wrong"][0]["inadmissible_execution"]=True;expect("valid wrong must remain admissible",lambda:sc.validate_anchors(wrong),"VALID_WRONG_STATE_SEMANTICS_INVALID")
 nondet=anchors();nondet["valid_correct"][2]["official_score"]=0.9;expect("scorer repeat drift fails",lambda:sc.validate_anchors(nondet),"SCORER_NONDETERMINISTIC: valid_correct")
 scores={f"G{g}C{c}F{f}":[0,0,1,1] for g in (0,1) for c in (0,1) for f in (0,1)}
 check("nondegenerate four-task pilot passes",sc.validate_development_distribution(scores)["passed"])
 floor=copy.deepcopy(scores);floor["G0C0F0"]=[0,0,0,0];expect("cell floor fails",lambda:sc.validate_development_distribution(floor),"UNINFORMATIVE_SCORE_FLOOR: G0C0F0")
 ceiling=copy.deepcopy(scores);ceiling["G1C1F1"]=[1,1,1,1];expect("cell ceiling fails",lambda:sc.validate_development_distribution(ceiling),"UNINFORMATIVE_SCORE_CEILING: G1C1F1")
 few={k:v[:3] for k,v in scores.items()};expect("fewer than four tasks fails",lambda:sc.validate_development_distribution(few),"DEVELOPMENT_TASK_COUNT_INSUFFICIENT")
 invalid=copy.deepcopy(scores);invalid["G0C0F0"][0]=1.2;expect("score range fails",lambda:sc.validate_development_distribution(invalid),"NORMALIZED_SCORE_OUT_OF_RANGE")
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
