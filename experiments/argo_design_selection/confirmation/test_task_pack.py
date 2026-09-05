#!/usr/bin/env python3
import importlib.util,tempfile
from pathlib import Path
from task_pack import AFFECTED_SHAPES,SHAPES,UNAFFECTED_SHAPES,build,canonical_signature,graph,primary_schedule,replication_schedule
from targeting import oracle_target,policy_cascade
F=[]
def check(n,x,d=""):print(("PASS " if x else "FAIL ")+n+(" :: "+d if d and not x else ""));F.append(n) if not x else None
def main():
 specs=[graph(s) for s in SHAPES];sigs=[canonical_signature(x) for x in specs];check("sixteen structures",len(specs)==16 and len(set(sigs))==16,str(len(set(sigs))))
 v2path=Path(__file__).resolve().parents[1]/"pilot_v2/task_pack.py";sp=importlib.util.spec_from_file_location("pilot_v2_pack",v2path);v2=importlib.util.module_from_spec(sp);sp.loader.exec_module(v2);old={canonical_signature(v2.family(n)) for n in v2.FAMILIES};check("disjoint from B3 structures",not (set(sigs)&old),str(len(set(sigs)&old)))
 check("affected strata eight",sum(x["affected"] for x in specs)==8);check("truths balanced",sum(x["truth"]["constraint_status"]=="valid" for x in specs)==8);check("oracle agrees with stratum",all(("D" in oracle_target(x["graph"]))==x["affected"] for x in specs));check("cascade has an unaffected over-revocation fixture",any("D" in policy_cascade(x["graph"])["marked"] for x in specs if not x["affected"]));ps=primary_schedule();rs=replication_schedule();check("primary exact order balance",len(ps)==32 and sum(ps[i][1]=="C_BASE" for i in range(0,32,2))==8);check("replication reverses every pair",all(a[0]==b[0] and a[1]!=b[1] for a,b in zip(ps,rs)))
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  for shape in SHAPES:
   b=build(shape,"C_BASE",root/shape/"b");t=build(shape,"C_TARGET",root/shape/"t");check(shape+" bytes",(root/shape/"b/TASK.md").read_bytes()==(root/shape/"t/TASK.md").read_bytes() and (root/shape/"b/index.json").read_bytes()==(root/shape/"t/index.json").read_bytes() and (root/shape/"b/allocation.json").stat().st_size==(root/shape/"t/allocation.json").stat().st_size==768);check(shape+" records",b["records"]==t["records"]);check(shape+" allocation",t["allocated_record"]==t["target_record"] and b["allocated_record"]==b["decoy_record"]);check(shape+" opaque labels",all(x not in (root/shape/"b/TASK.md").read_text().lower()+(root/shape/"t/TASK.md").read_text().lower() for x in ("c_base","c_target","treatment","control")))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
