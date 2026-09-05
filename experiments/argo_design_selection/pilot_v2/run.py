#!/usr/bin/env python3
"""Fail-closed runner for a future approved non-isomorphic OAuth pilot."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/"pilot"))
from score import score_decision  # noqa: E402
from task_pack import build,schedule  # noqa: E402
MODEL="anthropic/claude-opus-4-6";SYSTEM_PROMPT="Use the four provided research tools, respect the two-record verification budget, and write one decision.";TIMEOUT=600

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse_usage(text):
 tokens=0;cost=0.0
 for line in text.splitlines():
  try:e=json.loads(line)
  except:continue
  if e.get("type")=="message_end" and (e.get("message") or {}).get("role")=="assistant":
   u=e["message"].get("usage") or {};tokens+=int(u.get("totalTokens",0));cost+=float((u.get("cost") or {}).get("total",0) or 0)
 return {"total_tokens":tokens,"catalog_accounting_usd_not_billing":round(cost,6)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--approval",type=Path,required=True);ap.add_argument("--outdir",type=Path,required=True);ap.add_argument("--receipt",type=Path,required=True);a=ap.parse_args()
 approval=json.loads(a.approval.read_text())
 if approval.get("status")!="APPROVED" or approval.get("model")!=MODEL or approval.get("episodes")!=8:raise ValueError("PAID_PILOT_NOT_APPROVED")
 code={n:sha(HERE/n) for n in ("task_pack.py","tools.js","run.py")}
 a.outdir.mkdir(parents=True,exist_ok=True);rows=[]
 authdir=Path("/tmp/argo_pilot_v2_agent");authdir.mkdir(exist_ok=True);src=Path.home()/".prime/agent/auth.json"
 if src.is_file():shutil.copy2(src,authdir/"auth.json")
 plan=schedule()
 if len(plan)!=8:raise ValueError("SCHEDULE_SIZE")
 for i,(family,condition) in enumerate(plan,1):
  opaque=hashlib.sha256(f"ARGO-V2|{family}|{condition}".encode()).hexdigest()[:16];wd=a.outdir/f"attempt-{opaque}"
  if wd.exists():shutil.rmtree(wd)
  meta=build(family,condition,wd);sess=wd/"_sess";sess.mkdir()
  task=(wd/"TASK.md").read_text();cmd=["prime-agent","-p","--no-session","--mode","json","--cwd",str(wd),"--session-dir",str(sess),"-nc","-ns","-np","--model",MODEL,"--thinking","high","--system-prompt",SYSTEM_PROMPT,"--no-builtin-tools","-e",str(HERE/"tools.js"),task]
  env=dict(os.environ);env["PRIME_AGENT_CODING_AGENT_DIR"]=str(authdir);t0=time.time()
  try:p=subprocess.run(cmd,cwd=wd,capture_output=True,text=True,timeout=TIMEOUT,env=env);text=p.stdout+"\n"+p.stderr;exit_code=p.returncode;timeout=False
  except subprocess.TimeoutExpired as e:text=(e.stdout or "")+"\n"+(e.stderr or "");exit_code=None;timeout=True
  (wd/"transcript.jsonl").write_text(text);access=wd/"record_access_log.json";ar=json.loads(access.read_text()) if access.is_file() else []
  reads=sorted(set(str(x.get("record_id","")).upper() for x in ar if x.get("tool")=="read_record" and x.get("charged")));allocated=json.loads((wd/"allocation.json").read_text())["allocated_record"]["id"];verification=sorted(set(reads+[allocated]));decision=json.loads((wd/"decision.json").read_text()) if (wd/"decision.json").is_file() else None
  score=score_decision(decision,meta["truth"],meta["critical_record"],2,verification) if decision else {"admissible":False,"reason":"missing"}
  row={"episode_id":f"{family}|{condition}","family":family,"condition":condition,"model":MODEL,"exit_code":exit_code,"timed_out":timeout,"duration_seconds":round(time.time()-t0,3),"usage":parse_usage(text),"allocated_record":allocated,"model_reads":reads,"verification_records":verification,"score":score,"workdir":str(wd),"transcript_sha256":sha(wd/"transcript.jsonl"),"access_log_sha256":sha(access) if access.is_file() else None,"task_sha256":meta["task_sha256"],"structural_signature":meta["structural_signature"]};rows.append(row)
  receipt={"schema_version":"argo-corrected-b2-pilot/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"approval_path":str(a.approval.resolve()),"approval_sha256":sha(a.approval),"model":MODEL,"thinking":"high","code":code,"planned_episodes":8,"completed_episodes":len(rows),"episodes":rows,"scope":"development pilot only; four structural families; not confirmatory"};a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps({"i":i,"episode":row["episode_id"],"correct":score.get("correct"),"stale":score.get("stale_consistent"),"tokens":row["usage"]["total_tokens"]}),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())
