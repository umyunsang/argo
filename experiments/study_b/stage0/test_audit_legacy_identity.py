#!/usr/bin/env python3
"""Tests for deterministic legacy receipt identity auditing."""
from __future__ import annotations
import json, tempfile
from pathlib import Path
import audit_legacy_identity as audit
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def main():
 with tempfile.TemporaryDirectory(dir=audit.ROOT) as td:
  root=Path(td);p1=root/"seed3-receipt.json";p2=root/"seed4-receipt.json"
  p1.write_text(json.dumps({"episodes":[{"seed":0,"task_sha256":"a"},{"seed":0,"task_sha256":"a"}]}))
  p2.write_text(json.dumps({"seed":0,"task_sha256":"a"}))
  rs=audit.records([p1,p2]);s=audit.summarize("fixture",rs)
  check("episode flattening is exact",s["episode_count"]==3,str(s))
  check("outer labels come from filenames",s["outer_label_count"]==2,str(s))
  check("inner seed remains zero",s["inner_seed_values"]==[0],str(s))
  check("all outer-inner pairs mismatch",s["outer_inner_mismatch_count"]==3,str(s))
  check("one task hash is not three tasks",s["unique_task_hash_count"]==1,str(s))
 check("T1 filename label is parsed",audit.outer_label(Path("block_t1_task5_s12_B0.json"))==12)
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
