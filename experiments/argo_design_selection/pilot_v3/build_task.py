#!/usr/bin/env python3
"""Unambiguous outcome-contract wrapper around the immutable v2 task pack."""
from __future__ import annotations
import hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"pilot_v2"))
from task_pack import FAMILIES,build as build_v2,schedule  # noqa: E402

def build(name,condition,out):
 meta=build_v2(name,condition,out)
 task=("Use read_index and read_allocation. One slot is already allocated; open at most one additional record with read_record. "
       "Decide the active constraint. Submit through write_decision with constraint_status valid/withdrawn/unverified; "
       "constraint_disposition apply/do_not_apply/undetermined; needs_more_verification true/false; records_inspected; and reason. "
       "If status is withdrawn, disposition must be do_not_apply. If evidence is insufficient, choose unverified, undetermined, true.")
 (out/"TASK.md").write_text(task+"\n")
 meta["task_sha256"]=hashlib.sha256((task+"\n").encode()).hexdigest()
 meta["truth_v3"]={"constraint_status":meta["truth"]["constraint_status"],"constraint_disposition":"apply" if meta["truth"]["constraint_status"]=="valid" else "do_not_apply","needs_more_verification":False}
 return meta
