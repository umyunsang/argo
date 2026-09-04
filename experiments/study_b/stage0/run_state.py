#!/usr/bin/env python3
"""Pure classification of live, stale, orphaned, and terminal run snapshots."""
from __future__ import annotations
class RunStateViolation(ValueError):pass
def classify(s:dict)->dict:
 registry=s.get("registry_state")
 if registry!="running":return {"status":"REGISTRY_TERMINAL","registry_state":registry,"verdict":None,"reason":f"registry state is {registry!r}, not running"}
 exit_code=s.get("exit_code")
 if exit_code is not None:
  if s.get("result_receipt_exists") is True:return {"status":"COMPLETED_REGISTRY_STALE","registry_state":registry,"verdict":"PASS" if exit_code==0 else "FAIL","reason":f"terminal exit_code={exit_code} and result receipt exist while registry says running"}
  return {"status":"TERMINATED_MISSING_RESULT","registry_state":registry,"verdict":None,"reason":f"exit_code={exit_code} exists but result receipt is absent"}
 if s.get("pid_exists") is not True:return {"status":"ORPHANED_NO_VERDICT","registry_state":registry,"verdict":None,"reason":"registry says running but worker PID is absent"}
 registered=s.get("registered_process_start");observed=s.get("observed_process_start")
 if registered is not None and observed is not None and registered!=observed:return {"status":"ORPHANED_PID_REUSED","registry_state":registry,"verdict":None,"reason":f"PID exists but process start identity differs: registered={registered} observed={observed}"}
 before=s.get("log_size_before",0);after=s.get("log_size_after",0);age=s.get("heartbeat_age_s");limit=s.get("heartbeat_max_age_s")
 progress=isinstance(before,int) and isinstance(after,int) and after>before
 fresh=isinstance(age,(int,float)) and isinstance(limit,(int,float)) and age<=limit
 if progress or fresh:return {"status":"RUNNING_LIVE","registry_state":registry,"verdict":None,"reason":f"worker PID matches; log_progress={progress}; heartbeat_fresh={fresh}"}
 return {"status":"STALLED_NO_VERDICT","registry_state":registry,"verdict":None,"reason":"worker exists but no fresh heartbeat or observed log growth"}
