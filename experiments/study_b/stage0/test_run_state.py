#!/usr/bin/env python3
"""Failing-first tests for stale/orphan run-state classification."""
from __future__ import annotations
import run_state
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def classify(**kw):
 base={"registry_state":"running","pid_exists":True,"registered_process_start":"start-a","observed_process_start":"start-a","heartbeat_age_s":5,"heartbeat_max_age_s":60,"log_size_before":100,"log_size_after":120,"exit_code":None,"result_receipt_exists":False};base.update(kw);return run_state.classify(base)
def main():
 live=classify();check("live worker requires progress evidence",live["status"]=="RUNNING_LIVE",str(live));check("live run has no verdict",live["verdict"] is None,str(live))
 dead=classify(pid_exists=False,log_size_before=0,log_size_after=0);check("dead pid is orphaned",dead["status"]=="ORPHANED_NO_VERDICT",str(dead));check("orphan never gets verdict",dead["verdict"] is None,str(dead))
 reused=classify(observed_process_start="start-b");check("reused pid is orphaned",reused["status"]=="ORPHANED_PID_REUSED",str(reused))
 stalled=classify(heartbeat_age_s=120,log_size_after=100);check("alive stale worker is stalled",stalled["status"]=="STALLED_NO_VERDICT",str(stalled))
 heartbeat=classify(log_size_after=100,heartbeat_age_s=5);check("fresh heartbeat can establish liveness",heartbeat["status"]=="RUNNING_LIVE",str(heartbeat))
 complete=classify(exit_code=0,result_receipt_exists=True,log_size_after=100);check("terminal evidence overrides stale registry",complete["status"]=="COMPLETED_REGISTRY_STALE",str(complete));check("completed verdict is pass",complete["verdict"]=="PASS",str(complete))
 failed=classify(exit_code=3,result_receipt_exists=True);check("nonzero terminal verdict is fail",failed["verdict"]=="FAIL",str(failed))
 no_receipt=classify(exit_code=0,result_receipt_exists=False);check("exit code without result receipt has no verdict",no_receipt["status"]=="TERMINATED_MISSING_RESULT",str(no_receipt));check("missing result verdict is null",no_receipt["verdict"] is None,str(no_receipt))
 terminal=classify(registry_state="cancelled",pid_exists=False);check("terminal registry is preserved",terminal["status"]=="REGISTRY_TERMINAL",str(terminal))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
