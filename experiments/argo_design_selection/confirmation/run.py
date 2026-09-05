#!/usr/bin/env python3
"""Fail-closed confirmation runner for C32 or C64; no approval means no call."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from score import score
from task_pack import build,primary_schedule,replication_schedule
HERE=Path(__file__).resolve().parent;MODEL="anthropic/claude-opus-4-6";PROMPT="Use the four research tools, respect the two-record budget, and submit one unambiguous decision.";TIMEOUT=600
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def usage(t):
 n=0;c=0.0
 for l in t.splitlines():
  try:e=json.loads(l)
  except:continue
  if e.get("type")=="message_end" and (e.get("message") or {}).get("role")=="assistant":u=e["message"].get("usage") or {};n+=int(u.get("totalTokens",0));c+=float((u.get("cost") or {}).get("total",0) or 0)
 return {"total_tokens":n,"catalog_accounting_usd_not_billing":round(c,6)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--approval",type=Path,required=True);ap.add_argument("--outdir",type=Path,required=True);ap.add_argument("--receipt",type=Path,required=True);a=ap.parse_args();auth=json.loads(a.approval.read_text());opt=auth.get("option");expected={"C32":32,"C64":64}
 if auth.get("status")!="APPROVED" or auth.get("model")!=MODEL or opt not in expected or auth.get("episodes")!=expected[opt]:raise ValueError("C_NOT_APPROVED")
 plan=[("primary",x) for x in primary_schedule()]+([("replication",x) for x in replication_schedule()] if opt=="C64" else []);assert len(plan)==expected[opt];code={n:sha(HERE/n) for n in ("task_pack.py","score.py","tools.js","run.py")};ad=Path("/tmp/argo-confirmation-auth");ad.mkdir(exist_ok=True);src=Path.home()/".prime/agent/auth.json"
 if src.is_file():shutil.copy2(src,ad/"auth.json")
 rows=[]
 for i,(block,(shape,cond)) in enumerate(plan,1):
  opaque=hashlib.sha256(f"ARGO-C|{block}|{shape}|{cond}".encode()).hexdigest()[:16];wd=a.outdir/f"attempt-{opaque}"
  if wd.exists():shutil.rmtree(wd)
  m=build(shape,cond,wd);sess=wd/"_sess";sess.mkdir();cmd=["prime-agent","-p","--no-session","--mode","json","--cwd",str(wd),"--session-dir",str(sess),"-nc","-ns","-np","--model",MODEL,"--thinking","high","--system-prompt",PROMPT,"--no-builtin-tools","-e",str(HERE/"tools.js"),(wd/"TASK.md").read_text()];env=dict(os.environ);env["PRIME_AGENT_CODING_AGENT_DIR"]=str(ad);t0=time.time()
  try:p=subprocess.run(cmd,cwd=wd,capture_output=True,text=True,timeout=TIMEOUT,env=env);txt=p.stdout+"\n"+p.stderr;ec=p.returncode;to=False
  except subprocess.TimeoutExpired as e:txt=(e.stdout or "")+"\n"+(e.stderr or "");ec=None;to=True
  (wd/"transcript.jsonl").write_text(txt);al=wd/"record_access_log.json";ars=json.loads(al.read_text()) if al.is_file() else [];reads=sorted(set(str(x.get("record_id","")).upper() for x in ars if x.get("tool")=="read_record" and x.get("charged")));alloc=json.loads((wd/"allocation.json").read_text())["allocated_record"]["id"];vr=sorted(set(reads+[alloc]));payload=json.loads((wd/"decision.json").read_text()) if (wd/"decision.json").is_file() else None;s=score(payload,m["truth"],m["critical_record"],2,vr) if payload else {"admissible":False,"reason":"missing"};row={"episode_id":f"{block}|{shape}|{cond}","block":block,"shape":shape,"condition":cond,"affected":m["affected"],"truth":m["truth"],"model":MODEL,"exit_code":ec,"timed_out":to,"duration_seconds":round(time.time()-t0,3),"usage":usage(txt),"allocated_record":alloc,"model_reads":reads,"verification_records":vr,"score":s,"workdir":str(wd),"transcript_sha256":sha(wd/"transcript.jsonl"),"access_log_sha256":sha(al) if al.is_file() else None,"structural_signature":m["signature"]};rows.append(row);rec={"schema_version":"argo-confirmation-run/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"approval_path":str(a.approval.resolve()),"approval_sha256":sha(a.approval),"option":opt,"model":MODEL,"thinking":"high","code":code,"planned_episodes":expected[opt],"completed_episodes":len(rows),"episodes":rows,"scope":"synthetic structural confirmation population; replication nested if present"};a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(rec,indent=2)+"\n");print(json.dumps({"i":i,"of":len(plan),"episode":row["episode_id"],"correct":s.get("fully_correct"),"stale":s.get("stale_consistent"),"tokens":row["usage"]["total_tokens"]}),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())
