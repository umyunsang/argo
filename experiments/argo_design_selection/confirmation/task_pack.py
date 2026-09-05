#!/usr/bin/env python3
"""Disjoint 16-structure confirmation task pack. Zero model calls."""
from __future__ import annotations
import hashlib,itertools,json,math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
from targeting import oracle_target,policy_cascade  # noqa: E402
AFFECTED_SHAPES=("a_direct","a_chain2","a_chain3","a_fanout","a_parallel","a_uneven","a_diamond","a_shortcut")
UNAFFECTED_SHAPES=("u_direct2","u_direct3","u_alt_chain","u_two_chains","u_long_plus_direct","u_uneven_chains","u_same_source_paths","u_unrelated")
SHAPES=AFFECTED_SHAPES+UNAFFECTED_SHAPES

def node(i,k):return {"id":i,"kind":k,"scope":"confirmation"}
def edge(i,s,t):return {"id":i,"source":s,"target":t,"relation":"depends_on","scope":"confirmation"}
def graph(shape):
 E=[];claims=set();sources=set();ei=0
 def add(s,t):
  nonlocal ei;ei+=1;E.append(edge(f"e{ei}",s,t))
  if s.startswith("S"): sources.add(s)
  elif s not in ("D","A"): claims.add(s)
  if t not in ("D","A"): claims.add(t)
 def path(s,*xs):
  for a,b in zip((s,)+xs,xs):add(a,b)
 if shape=="a_direct":path("S1","M");add("M","C9")
 elif shape=="a_chain2":path("S1","C1","M");add("C1","D")
 elif shape=="a_chain3":path("S1","C1","C2","M")
 elif shape=="a_fanout":add("S1","C0");path("C0","C1","M");path("C0","C2","M")
 elif shape=="a_parallel":add("S1","C0");path("C0","C1","M");path("C0","C2","M");path("C0","C3","M")
 elif shape=="a_uneven":add("S1","C0");path("C0","C1","C3","M");path("C0","C2","M")
 elif shape=="a_diamond":add("S1","C0");add("C0","C1");add("C0","C2");add("C1","C3");add("C2","C3");add("C3","M")
 elif shape=="a_shortcut":add("S1","C0");path("C0","C1","C2","M");add("C0","C2")
 elif shape=="u_direct2":add("S1","M");add("S2","M");path("S2","C9","M")
 elif shape=="u_direct3":add("S1","M");add("S2","M");add("S3","M")
 elif shape=="u_alt_chain":add("S1","M");path("S2","C1","M")
 elif shape=="u_two_chains":path("S1","C1","M");path("S2","C2","M")
 elif shape=="u_long_plus_direct":path("S1","C1","C2","M");add("S2","M")
 elif shape=="u_uneven_chains":path("S1","C1","M");path("S2","C2","C3","M")
 elif shape=="u_same_source_paths":path("S1","C1","M");path("S1","C2","M")
 elif shape=="u_unrelated":path("S1","U","V");path("S2","C9","M")
 else:raise ValueError(shape)
 # Decision/action path is identical and semantically downstream.
 add("M","D");add("D","A");claims.discard("D");claims.discard("A")
 # Remove the first edge from S1. All A shapes have an articulation there;
 # U shapes retain a path to M.
 removed=next(e["id"] for e in E if e["source"]=="S1")
 ids_sources=sorted(sources|{"W","RZ"});nodes=[node(x,"source") for x in ids_sources]+[node(x,"claim") for x in sorted(claims)]+[node("D","decision"),node("A","action")]
 g={"schema_version":"argo-dependency-targeting-instance/v1","family":"confirmation","instance_id":shape,"seed":None,"roots":ids_sources,"nodes":nodes,"edges":E,"event":{"removed_edge_ids":[removed],"kind":"source_version_changed"}}
 affected="D" in oracle_target(g);assert affected==(shape in AFFECTED_SHAPES)
 surviving=sorted(s for s in sources if s!="S1")
 target="S1" if affected or shape=="u_same_source_paths" else surviving[0]
 return {"shape":shape,"graph":g,"affected":affected,"truth":{"constraint_status":"withdrawn" if affected else "valid","constraint_disposition":"do_not_apply" if affected else "apply","needs_more_verification":False},"target_record":target,"decoy_record":"RZ","critical_record":"W" if affected else target,"oracle_affected":sorted(oracle_target(g))}

def canonical_signature(spec):
 g=spec["graph"];kind={n["id"]:n["kind"] for n in g["nodes"]};groups={k:sorted(i for i,v in kind.items() if v==k) for k in set(kind.values())};keys=sorted(groups);best=None
 perms=[list(itertools.permutations(groups[k])) for k in keys]
 for combo in itertools.product(*perms):
  mapping={old:f"{k}{j}" for k,perm in zip(keys,combo) for j,old in enumerate(perm)};enc=(tuple(sorted((mapping[e["source"]],mapping[e["target"]],e["id"] in g["event"]["removed_edge_ids"]) for e in g["edges"])),mapping["D"] in {mapping[x] for x in oracle_target(g)})
  s=repr(enc)
  if best is None or s<best:best=s
 return hashlib.sha256(best.encode()).hexdigest()
def records(spec):
 shape=spec["shape"];setting="setting-"+hashlib.sha256(shape.encode()).hexdigest()[:6];r={"RZ":"Neutral allocation record. Formatting and storage notes only; no decision evidence.","M":f"Active constraint: use {setting}. Its support structure is shown in index.json.","W":f"Current status: the S1 support for {setting} is withdrawn after a prospective contradiction."}
 for n in spec["graph"]["nodes"]:
  if n["kind"]=="source" and n["id"] not in r:
   if n["id"]=="S1":r[n["id"]]=f"S1 evidence for {setting}. Current-status pointer: W."
   else:r[n["id"]]=f"{n['id']} is current independent evidence supporting {setting}."
 for n in spec["graph"]["nodes"]:
  if n["kind"]=="claim" and n["id"] not in r:r[n["id"]]=f"Intermediate research claim {n['id']} for {setting}."
 return r
def allocation(id,content,length=768):
 o={"allocated_record":{"id":id,"content":content},"allocated_slots":1,"remaining_record_reads":1,"policy":"verification allocation","padding":""};raw=(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode();assert len(raw)<=length;o["padding"]="x"*(length-len(raw));raw=(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode();assert len(raw)==length;return raw
def build(shape,condition,out):
 assert condition in ("C_BASE","C_TARGET");s=graph(shape);rs=records(s);out.mkdir(parents=True,exist_ok=True);rd=out/"records";rd.mkdir();[ (rd/f"{k}.txt").write_text(v+"\n") for k,v in rs.items() ];idx={"nodes":s["graph"]["nodes"],"edges":s["graph"]["edges"],"event":{"changed_source":"S1","detail":"status must be verified from records"},"total_record_budget":2};(out/"index.json").write_text(json.dumps(idx,sort_keys=True)+"\n");rid=s["target_record"] if condition=="C_TARGET" else s["decoy_record"];(out/"allocation.json").write_bytes(allocation(rid,rs[rid]));(out/"budget.json").write_text(json.dumps({"prefetched_records":[rid],"remaining_record_reads":1,"total_verification_budget":2})+"\n");task="Use the four research tools. Verify the active constraint under a total budget of two records (one allocated, one remaining). Return constraint_status valid/withdrawn/unverified, constraint_disposition apply/do_not_apply/undetermined, needs_more_verification, records_inspected, and reason.";(out/"TASK.md").write_text(task+"\n");return {**s,"condition":condition,"allocated_record":rid,"records":rs,"task_sha256":hashlib.sha256((task+"\n").encode()).hexdigest(),"signature":canonical_signature(s)}
def primary_schedule():return [(shape,cond) for i,shape in enumerate(SHAPES) for cond in (("C_BASE","C_TARGET") if i%2==0 else ("C_TARGET","C_BASE"))]
def replication_schedule():return [(shape,"C_TARGET" if cond=="C_BASE" else "C_BASE") for shape,cond in primary_schedule()]
