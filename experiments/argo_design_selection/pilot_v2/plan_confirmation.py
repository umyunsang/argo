#!/usr/bin/env python3
"""Exact unconditional power scenarios for a paired binary sign/McNemar test."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def binom_pmf(k,n,p):return math.comb(n,k)*(p**k)*((1-p)**(n-k))
def two_sided_sign_p(w,d):
 if d==0:return 1.0
 obs=binom_pmf(w,d,0.5)
 return min(1.0,sum(binom_pmf(k,d,0.5) for k in range(d+1) if binom_pmf(k,d,0.5)<=obs+1e-15))
def power(n,p_discordance,p_target_win,alpha=0.05):
 out=0.0
 for d in range(n+1):
  pd=binom_pmf(d,n,p_discordance)
  out += pd*sum(binom_pmf(w,d,p_target_win) for w in range(d+1) if two_sided_sign_p(w,d)<=alpha)
 return out
def minimum_n(pd,pw,target=0.8,max_n=300):
 for n in range(4,max_n+1):
  if power(n,pd,pw)>=target:return n,power(n,pd,pw)
 return None,None
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();rows=[]
 for pd in (0.25,0.50,0.75):
  for pw in (0.65,0.75,0.90):
   n,p=minimum_n(pd,pw);rows.append({"discordance_rate":pd,"target_win_given_discordance":pw,"minimum_tasks_for_80pct":n,"achieved_power":round(p,6) if p else None,"episodes_at_one_rollout_two_conditions":2*n if n else None,"episodes_at_three_rollouts_two_conditions":6*n if n else None})
 obj={"schema_version":"argo-confirmation-power-scenarios/v1","test":"two-sided exact sign test over task-level paired discordances","alpha":0.05,"target_power":0.80,"selection_rule":"report all scenarios; never select one post-outcome","rows":rows,"confirmatory_authorization":False};a.out.write_text(json.dumps(obj,indent=2)+"\n");print(json.dumps(rows,indent=2))
if __name__=="__main__":main()
