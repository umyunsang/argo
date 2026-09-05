#!/usr/bin/env python3
from analyze import summarize

def ep(s,c,correct,affected=True,tokens=10):return {"shape":s,"condition":c,"affected":affected,"usage":{"total_tokens":tokens},"score":{"fully_correct":correct,"stale_consistent":False,"overreaction":False}}
rows=[]
for i in range(16):rows += [ep(str(i),"C_BASE",False,i<8),ep(str(i),"C_TARGET",i<12,i<8,9)]
o=summarize(rows);assert o["target_wins"]==12 and o["ties"]==4 and o["base_wins"]==0 and o["two_sided_exact_p"]<0.05 and o["token_ratio"]==0.9
rows[1]["score"]["stale_consistent"]=True;o=summarize(rows);assert o["affected_target_stale"]==1
print("All checks passed.")
