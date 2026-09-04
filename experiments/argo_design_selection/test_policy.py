#!/usr/bin/env python3
"""Failing-first checks for the scientific-choice manipulation instrument."""
from __future__ import annotations
import copy,json
from pathlib import Path
from policy import ContractViolation,evaluate,typed_policy
CAPSULE=Path(__file__).parent/"capsules/dependency_invalidation_v1.json"
F=[]
def check(name,ok,detail=""):
 print(("PASS " if ok else "FAIL ")+name+(" :: "+detail if detail and not ok else ""));F.append(name) if not ok else None
def main():
 c=json.loads(CAPSULE.read_text());base=evaluate(c);check("declared manipulation passes",base["passed"],str(base["failures"]));check("typed policy is active",base["typed_policy_manipulation_active"]);check("diagnostic is not efficacy",base["efficacy_result"] is False)
 r=next(x for x in c["events"] if x["id"]=="event:relevant");u=next(x for x in c["events"] if x["id"]=="event:unrelated")
 check("relevant source reopens d1",typed_policy(c,r)["allowed_next_action"]=="recheck:decision:d1");check("unrelated source preserves action",typed_policy(c,u)["allowed_next_action"]=="action:a1");check("result bytes are preserved",typed_policy(c,r)["preserved_results"]==["result:r1","result:r2"])
 broken=copy.deepcopy(c);broken["dependency_edges"]=[x for x in broken["dependency_edges"] if not (x["source"]=="source:s1" and x["target"]=="claim:c1")];check("missing dependency edge is caught",not evaluate(broken)["passed"])
 contaminated=copy.deepcopy(c);contaminated["dependency_edges"].append({"source":"source:s3","target":"claim:c2","relation":"supports"});check("unrelated dependency contamination is caught",not evaluate(contaminated)["passed"])
 dangling=copy.deepcopy(c);dangling["dependency_edges"].append({"source":"missing","target":"claim:c1","relation":"supports"})
 try:typed_policy(dangling,r);caught=False
 except ContractViolation:caught=True
 check("dangling edge fails closed",caught)
 a=evaluate(c);b=evaluate(copy.deepcopy(c));check("fresh-context replay deterministic",a==b)
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
