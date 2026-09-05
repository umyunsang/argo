#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from task_pack import FAMILIES,build,family,schedule,signature
from targeting import oracle_target,policy_cascade

F=[]
def check(n,x,d=""):
 print(("PASS " if x else "FAIL ")+n+(" :: "+d if d and not x else ""));F.append(n) if not x else None

def main():
 specs=[family(n) for n in FAMILIES]
 sigs=[signature(s) for s in specs]
 check("four structural families",len(specs)==4 and len(set(sigs))==4,str(sigs))
 check("ground truths are balanced",[s["truth"]["action"] for s in specs].count("proceed")==2)
 check("affected and unaffected decisions both present",any(s["decision_node"] in s["oracle_affected"] for s in specs) and any(s["decision_node"] not in s["oracle_affected"] for s in specs))
 alt=next(s for s in specs if s["name"]=="alternate_support")
 check("alternate support keeps decision valid",alt["decision_node"] not in oracle_target(alt["graph"]))
 check("cascade is a failing-first comparator on alternate support",alt["decision_node"] in policy_cascade(alt["graph"])["marked"])
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  for name in FAMILIES:
   b=build(name,"C_BASE",root/name/"b");t=build(name,"C_TARGET",root/name/"t")
   check(name+" allocation bytes matched",b["allocation_bytes"]==t["allocation_bytes"]==512)
   check(name+" task bytes matched",b["task_sha256"]==t["task_sha256"])
   check(name+" record bytes matched",all((root/name/"b/records"/p.name).read_bytes()==p.read_bytes() for p in (root/name/"t/records").iterdir()))
   check(name+" target allocation relevant",t["allocated_record"]==t["target_record"])
   check(name+" base allocation decoy",b["allocated_record"]!=b["target_record"])
   for condition,sub in (("C_BASE","b"),("C_TARGET","t")):
    blob=(root/name/sub/"TASK.md").read_text().lower()+ (root/name/sub/"allocation.json").read_text().lower()
    check(name+" "+condition+" no condition label",all(x not in blob for x in ("c_base","c_target","treatment","control")))
 sched=schedule();check("schedule exact balance",len(sched)==8 and sum(1 for i in range(0,8,2) if sched[i][1]=="C_BASE")==2,str(sched))
 a=[build(n,c,Path(tempfile.mkdtemp())) for n,c in schedule()];b=[build(n,c,Path(tempfile.mkdtemp())) for n,c in schedule()]
 check("pack build deterministic",a==b)
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
