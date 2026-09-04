#!/usr/bin/env python3
"""Failing-first tests for the non-executing GCF treatment manifest loader."""
from __future__ import annotations
import copy, hashlib, json, tempfile
from pathlib import Path
import treatment_loader as loader
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except loader.TreatmentViolation as e:check(n,text in str(e),str(e))
def cfg(g,c,f):
 x={"config_schema":"argo-gcf-runner-config/v1","cell_id":f"G{g}C{c}F{f}","factors":{"G":g,"C":c,"F":f},"fixed":{"model":"m","interface":"i","permissions":"p","retrieval":"r","environment":"e","budget":"b","scorer":"s","retry":"x","stop_authority":"h"}}
 return {"cell_id":x["cell_id"],"G":g,"C":c,"F":f,"runner_config_id":"runner:"+x["cell_id"].lower()+":v1","runner_config_sha256":loader.canonical_hash(x),"runner_config":x}
def manifest():return {"cells":[cfg(g,c,f) for g in (0,1) for c in (0,1) for f in (0,1)]}
def main():
 m=manifest();reg=loader.load_registry(m);check("eight config registry passes",len(reg)==8,str(reg))
 selected=loader.select_config(reg,"runner:g1c0f1:v1","G1C0F1");check("scheduled and loaded factors match",selected["factors"]=={"G":1,"C":0,"F":1})
 expect("unknown config fails",lambda:loader.select_config(reg,"runner:unknown:v1","G0C0F0"),"UNKNOWN_RUNNER_CONFIG")
 bad=manifest();bad["cells"][0]["runner_config"]["fixed"]["model"]="changed"
 expect("config hash mismatch fails",lambda:loader.load_registry(bad),"RUNNER_CONFIG_HASH_MISMATCH")
 dup=manifest();dup["cells"][1]["runner_config_id"]=dup["cells"][0]["runner_config_id"]
 expect("duplicate config id fails",lambda:loader.load_registry(dup),"DUPLICATE_RUNNER_CONFIG")
 drift=manifest();drift["cells"][1]["runner_config"]["fixed"]["budget"]="different";drift["cells"][1]["runner_config_sha256"]=loader.canonical_hash(drift["cells"][1]["runner_config"])
 expect("fixed surface drift fails",lambda:loader.load_registry(drift),"FIXED_SURFACE_MISMATCH")
 check("minus G is a single factor removal",loader.compare_to_full(reg,"runner:g0c1f1:v1")==["G"])
 check("minus C is a single factor removal",loader.compare_to_full(reg,"runner:g1c0f1:v1")==["C"])
 check("minus F is a single factor removal",loader.compare_to_full(reg,"runner:g1c1f0:v1")==["F"])
 check("factorial cell is comparison not removal",loader.compare_to_full(reg,"runner:g0c0f1:v1")==["G","C"])
 a=[b"source-a",b"source-b",b"decision-c"]
 check("content multiset ignores order",loader.require_content_equivalence(a,list(reversed(a)))["passed"])
 expect("content byte drift fails",lambda:loader.require_content_equivalence(a,[b"source-a",b"source-X",b"decision-c"]),"ACCESSIBLE_CONTENT_MISMATCH")
 independent=[{"candidate_id":"A","context_id":"ctx-a","rollout_id":"ra","transcript_sha256":"a"*64,"frozen_at":10,"cross_reads":[]},{"candidate_id":"B","context_id":"ctx-b","rollout_id":"rb","transcript_sha256":"b"*64,"frozen_at":11,"cross_reads":[]}]
 check("two independent candidates pass",loader.validate_candidate_independence(independent,critic_started_at=12)["passed"])
 same=copy.deepcopy(independent);same[1]["context_id"]="ctx-a"
 expect("shared candidate context fails",lambda:loader.validate_candidate_independence(same,12),"CANDIDATE_CONTEXT_NOT_INDEPENDENT")
 cross=copy.deepcopy(independent);cross[1]["cross_reads"]=["candidate:A"]
 expect("cross candidate read fails",lambda:loader.validate_candidate_independence(cross,12),"CANDIDATE_CROSS_READ")
 late=copy.deepcopy(independent);late[1]["frozen_at"]=13
 expect("critic before freeze fails",lambda:loader.validate_candidate_independence(late,12),"CANDIDATE_NOT_FROZEN_BEFORE_CRITIC")
 same_tx=copy.deepcopy(independent);same_tx[1]["transcript_sha256"]="a"*64
 expect("identical transcripts fail independence",lambda:loader.validate_candidate_independence(same_tx,12),"CANDIDATE_TRANSCRIPT_NOT_DISTINCT")
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
