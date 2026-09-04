#!/usr/bin/env python3
"""Failing-first tests for pre-action resource ceiling enforcement."""
from __future__ import annotations
import resource_ceiling as cap
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except cap.ResourceViolation as e:check(n,text in str(e),str(e))
def main():
 limits={"tokens":1000,"tool_calls":10,"wall_seconds":60.0,"cost_usd":1.0};used={"tokens":900,"tool_calls":9,"wall_seconds":50.0,"cost_usd":0.9}
 check("equal-to-cap reservation passes",cap.reserve(used,{"tokens":100,"tool_calls":1,"wall_seconds":10.0,"cost_usd":0.1},limits)["passed"])
 expect("token overflow stops before action",lambda:cap.reserve(used,{"tokens":101,"tool_calls":0,"wall_seconds":0,"cost_usd":0},limits),"TOKEN_CAP_EXCEEDED: projected=1001 cap=1000")
 expect("tool overflow stops before action",lambda:cap.reserve(used,{"tokens":0,"tool_calls":2,"wall_seconds":0,"cost_usd":0},limits),"TOOL_CAP_EXCEEDED: projected=11 cap=10")
 expect("time overflow stops before action",lambda:cap.reserve(used,{"tokens":0,"tool_calls":0,"wall_seconds":10.1,"cost_usd":0},limits),"TIME_CAP_EXCEEDED")
 expect("cost overflow stops before action",lambda:cap.reserve(used,{"tokens":0,"tool_calls":0,"wall_seconds":0,"cost_usd":0.100001},limits),"COST_CAP_EXCEEDED")
 bad=dict(used);bad["tokens"]=-1;expect("negative usage fails",lambda:cap.reserve(bad,{"tokens":0,"tool_calls":0,"wall_seconds":0,"cost_usd":0},limits),"RESOURCE_USAGE_INVALID: tokens")
 missing=dict(limits);missing.pop("cost_usd");expect("missing cap fails",lambda:cap.reserve(used,{"tokens":0,"tool_calls":0,"wall_seconds":0,"cost_usd":0},missing),"RESOURCE_CAP_MISSING: cost_usd")
 result=cap.reserve({"tokens":0,"tool_calls":0,"wall_seconds":0,"cost_usd":0},{"tokens":10,"tool_calls":1,"wall_seconds":2,"cost_usd":0.01},limits);check("reservation returns projected usage",result["projected"]=={"tokens":10,"tool_calls":1,"wall_seconds":2.0,"cost_usd":0.01},str(result));check("reservation does not execute action",result["action_executed"] is False,str(result))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
