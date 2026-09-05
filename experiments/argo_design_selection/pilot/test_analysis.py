#!/usr/bin/env python3
from analyze_pilot import analyze

def ep(task, condition, *, stale, correct, partial=False, tokens=10, exit_code=0, admissible=True, budget=False):
 return {"task_id":task,"condition":condition,"exit_code":exit_code,"timed_out":False,"duration_seconds":1,"usage":{"total_tokens":tokens},"score":{"admissible":admissible,"budget_violation":budget,"stale_consistent":stale,"correct":correct,"partial":partial,"critical_inspected":correct}}
rows=[]
for i in range(6):rows += [ep(str(i),"C_BASE",stale=True,correct=False),ep(str(i),"C_TARGET",stale=False,correct=True,tokens=12)]
o=analyze({"episodes":rows});assert o["primary_nonstale_delta"]["mean"]==1 and o["secondary_correct_delta"]["positive"]==6
rows[1]=ep("0","C_TARGET",stale=False,correct=True,exit_code=1);o=analyze({"episodes":rows});assert o["primary_nonstale_delta"]["values"][0]==0
try:analyze({"episodes":rows[:-1]});raise AssertionError("missing pair not caught")
except ValueError:pass
print("All checks passed.")
