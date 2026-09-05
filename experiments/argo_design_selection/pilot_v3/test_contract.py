#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from build_task import FAMILIES,build,schedule
from score import Violation,score
F=[]
def check(n,x):print(("PASS " if x else "FAIL ")+n);F.append(n) if not x else None
def main():
 with tempfile.TemporaryDirectory() as td:
  for name in FAMILIES:
   b=build(name,"C_BASE",Path(td)/name/"b");t=build(name,"C_TARGET",Path(td)/name/"t")
   check(name+" identical task",b["task_sha256"]==t["task_sha256"] and (Path(td)/name/"b/TASK.md").read_bytes()==(Path(td)/name/"t/TASK.md").read_bytes())
   check(name+" unambiguous truth",t["truth_v3"]["constraint_disposition"] in ("apply","do_not_apply") and t["truth_v3"]["needs_more_verification"] is False)
 truth={"constraint_status":"withdrawn","constraint_disposition":"do_not_apply","needs_more_verification":False}
 good={**truth,"records_inspected":["R1","R3"],"reason":"x"};s=score(good,truth,"R3",2,["R1","R3"]);check("withdrawn maps to do_not_apply",s["fully_correct"] and not s["stale_consistent"])
 ambiguous={"constraint_status":"withdrawn","constraint_disposition":"apply","needs_more_verification":False,"records_inspected":[],"reason":"x"};s=score(ambiguous,truth,"R3",2,[]);check("withdrawn plus apply is inconsistent",not s["schema_semantically_consistent"] and s["stale_consistent"])
 partial={"constraint_status":"unverified","constraint_disposition":"undetermined","needs_more_verification":True,"records_inspected":[],"reason":"x"};check("unverified maps to safe partial",score(partial,truth,"R3",2,[])["partial_safe"])
 valid={"constraint_status":"valid","constraint_disposition":"apply","needs_more_verification":False}
 v={**valid,"records_inspected":["R2"],"reason":"x"};sv=score(v,valid,"R2",2,["R2"]);check("valid apply is correct not stale",sv["fully_correct"] and not sv["stale_consistent"] and not sv["overreaction"])
 try:score(dict(good,reason="treatment arm"),truth,"R3",2,["R3"]);caught=False
 except Violation:caught=True
 check("condition leak fails closed",caught)
 check("schedule remains exactly balanced",[x[1] for x in schedule()]==["C_BASE","C_TARGET","C_TARGET","C_BASE","C_BASE","C_TARGET","C_TARGET","C_BASE"])
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
