#!/usr/bin/env python3
"""Fail-closed Opus 4.6 OAuth runner for the unambiguous four-family pilot."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from build_task import build,schedule
from score import score
HERE=Path(__file__).resolve().parent;MODEL="anthropic/claude-opus-4-6";TIMEOUT=600;PROMPT="Use the four provided tools, respect the two-record budget, and submit one unambiguous decision."
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def usage(t):
 n=0;c=0.0
 for l in t.splitlines():
  try:e=json.loads(l)
  except:continue
  if e.get("type")=="message_end" and (e.get("message") or {}).get("role")=="assistant":u=e["message"].get("usage") or {};n+=int(u.get("totalTokens",0));c+=float((u.get("cost") or {}).get("total",0) or 0)
 return {"total_tokens":n,"catalog_accounting_usd_not_billing":round(c,6)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--approval",type=Path,required=True);ap.add_argument("--outdir",type=Path,required=True);ap.add_argument("--receipt",type=Path,required=True);a=ap.parse_args();auth=json.loads(a.approval.read_text())
 if auth.get("status")!="APPROVED" or auth.get("model")!=MODEL or auth.get("episodes")!=8:raise ValueError("B3_NOT_APPROVED")
 code={n:sha(HERE/n) for n in ("build_task.py","score.py","tools.js","run.py")};ad=Path("/tmp/argo-pilot-v3-auth");ad.mkdir(exist_ok=True);src=Path.home()/".prime/agent/auth.json"
 if src.is_file():shutil.copy2(src,ad/"auth.json")
 rows=[];plan=schedule();assert len(plan)==8
 for i,(fam,cond) in enumerate(plan,1):
  wd=a.outdir/("attempt-"+hashlib.sha256(f"ARGO-V3|{fam}|{cond}".encode()).hexdigest()[:16]);
  if wd.exists():shutil.rmtree(wd)
  m=build(fam,cond,wd);sess=wd/"_sess";sess.mkdir();cmd=["prime-agent","-p","--no-session","--mode","json","--cwd",str(wd),"--session-dir",str(sess),"-nc","-ns","-np","--model",MODEL,"--thinking","high","--system-prompt",PROMPT,"--no-builtin-tools","-e",str(HERE/"tools.js"),(wd/"TASK.md").read_text()];env=dict(os.environ);env["PRIME_AGENT_CODING_AGENT_DIR"]=str(ad);t0=time.time()
  try:p=subprocess.run(cmd,cwd=wd,capture_output=True,text=True,timeout=TIMEOUT,env=env);txt=p.stdout+"\n"+p.stderr;ec=p.returncode;to=False
  except subprocess.TimeoutExpired as e:txt=(e.stdout or "")+"\n"+(e.stderr or "");ec=None;to=True
  (wd/"transcript.jsonl").write_text(txt);al=wd/"record_access_log.json";ars=json.loads(al.read_text()) if al.is_file() else [];reads=sorted(set(str(x.get("record_id","")).upper() for x in ars if x.get("tool")=="read_record" and x.get("charged")));alloc=json.loads((wd/"allocation.json").read_text())["allocated_record"]["id"];vr=sorted(set(reads+[alloc]));payload=json.loads((wd/"decision.json").read_text()) if (wd/"decision.json").is_file() else None;s=score(payload,m["truth_v3"],m["critical_record"],2,vr) if payload else {"admissible":False,"reason":"missing"};row={"episode_id":f"{fam}|{cond}","family":fam,"condition":cond,"model":MODEL,"exit_code":ec,"timed_out":to,"duration_seconds":round(time.time()-t0,3),"usage":usage(txt),"allocated_record":alloc,"model_reads":reads,"verification_records":vr,"truth":m["truth_v3"],"score":s,"workdir":str(wd),"transcript_sha256":sha(wd/"transcript.jsonl"),"access_log_sha256":sha(al) if al.is_file() else None,"structural_signature":m["structural_signature"]};rows.append(row);rec={"schema_version":"argo-b3-unambiguous-pilot/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"approval_path":str(a.approval.resolve()),"approval_sha256":sha(a.approval),"model":MODEL,"thinking":"high","code":code,"planned_episodes":8,"completed_episodes":len(rows),"episodes":rows,"scope":"development pilot; four structural families; not confirmation"};a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(rec,indent=2)+"\n");print(json.dumps({"i":i,"episode":row["episode_id"],"fully_correct":s.get("fully_correct"),"partial":s.get("partial_safe"),"stale":s.get("stale_consistent"),"overreaction":s.get("overreaction"),"tokens":row["usage"]["total_tokens"]}),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())
