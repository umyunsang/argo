#!/usr/bin/env python3
"""Pre-action reservation against hard token, tool, wall-time, and cost ceilings."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
class ResourceViolation(ValueError):pass
FIELDS=("tokens","tool_calls","wall_seconds","cost_usd")
CODES={"tokens":"TOKEN_CAP_EXCEEDED","tool_calls":"TOOL_CAP_EXCEEDED","wall_seconds":"TIME_CAP_EXCEEDED","cost_usd":"COST_CAP_EXCEEDED"}
def number(value,kind,field):
 if isinstance(value,bool):raise ResourceViolation(f"RESOURCE_{kind}_INVALID: {field}")
 try:x=Decimal(str(value))
 except (InvalidOperation,ValueError):raise ResourceViolation(f"RESOURCE_{kind}_INVALID: {field}")
 if x<0:raise ResourceViolation(f"RESOURCE_{kind}_INVALID: {field}")
 if field in ("tokens","tool_calls") and x!=x.to_integral_value():raise ResourceViolation(f"RESOURCE_{kind}_INVALID: {field}")
 return x
def show(x:Decimal)->str:
 return str(int(x)) if x==x.to_integral_value() else format(x,"f")
def reserve(used:dict,requested:dict,caps:dict)->dict:
 projected={};capvals={}
 for field in FIELDS:
  if field not in caps:raise ResourceViolation(f"RESOURCE_CAP_MISSING: {field}")
  u=number(used.get(field),"USAGE",field);r=number(requested.get(field),"REQUEST",field);c=number(caps[field],"CAP",field);p=u+r
  if p>c:raise ResourceViolation(f"{CODES[field]}: projected={show(p)} cap={show(c)}")
  projected[field]=p;capvals[field]=c
 return {"passed":True,"projected":{"tokens":int(projected["tokens"]),"tool_calls":int(projected["tool_calls"]),"wall_seconds":float(projected["wall_seconds"]),"cost_usd":float(projected["cost_usd"])},"remaining":{"tokens":int(capvals["tokens"]-projected["tokens"]),"tool_calls":int(capvals["tool_calls"]-projected["tool_calls"]),"wall_seconds":float(capvals["wall_seconds"]-projected["wall_seconds"]),"cost_usd":float(capvals["cost_usd"]-projected["cost_usd"])},"action_executed":False}
