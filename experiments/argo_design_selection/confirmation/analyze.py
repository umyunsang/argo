#!/usr/bin/env python3
"""Validate confirmation bytes and report primary and replication separately."""
from __future__ import annotations
import argparse,hashlib,json,math,re
from pathlib import Path
from score import score
from task_pack import graph,primary_schedule,replication_schedule
OPAQUE=re.compile(r"^attempt-[0-9a-f]{16}$")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def req(x,m):
 if not x:raise ValueError(m)
def pmf(k,n):return math.comb(n,k)*0.5**n
def sign_p(w,d):
 if d==0:return 1.0
 o=pmf(w,d);return min(1.0,sum(pmf(k,d) for k in range(d+1) if pmf(k,d)<=o+1e-15))
def summarize(rows):
 by={}
 for e in rows:by.setdefault(e["shape"],{})[e["condition"]]=e
 wins=losses=ties=0
 for p in by.values():
  b=int(p["C_BASE"]["score"].get("fully_correct",False));t=int(p["C_TARGET"]["score"].get("fully_correct",False));wins+=t>b;losses+=b>t;ties+=b==t
 tt=sum(e["usage"]["total_tokens"] for e in rows if e["condition"]=="C_TARGET");bt=sum(e["usage"]["total_tokens"] for e in rows if e["condition"]=="C_BASE");d=wins+losses
 return {"tasks":len(by),"target_wins":wins,"base_wins":losses,"ties":ties,"discordant":d,"two_sided_exact_p":sign_p(wins,d),"mean_fully_correct_delta":(wins-losses)/len(by),"affected_target_stale":sum(e["score"].get("stale_consistent",False) for e in rows if e["condition"]=="C_TARGET" and e["affected"]),"unaffected_target_overreaction":sum(e["score"].get("overreaction",False) for e in rows if e["condition"]=="C_TARGET" and not e["affected"]),"target_tokens":tt,"base_tokens":bt,"token_ratio":tt/bt}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--receipt",type=Path,required=True);ap.add_argument("--approval",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();r=json.loads(a.receipt.read_text());auth=json.loads(a.approval.read_text());req(r["approval_sha256"]==sha(a.approval),"APPROVAL");req(r["completed_episodes"]==r["planned_episodes"]==auth["episodes"],"COUNT");req(r["code"]=={n:sha(Path(__file__).parent/n) for n in ("task_pack.py","score.py","tools.js","run.py")},"CODE")
 schedules={"primary":[f"primary|{s}|{c}" for s,c in primary_schedule()],"replication":[f"replication|{s}|{c}" for s,c in replication_schedule()]};blocks={}
 for e in r["episodes"]:
  wd=Path(e["workdir"]);req(OPAQUE.fullmatch(wd.name) and e["condition"].lower() not in str(wd).lower(),"OPAQUE");req(sha(wd/"transcript.jsonl")==e["transcript_sha256"] and sha(wd/"record_access_log.json")==e["access_log_sha256"],"BYTES");al=json.loads((wd/"record_access_log.json").read_text());reads=sorted(set(str(x.get("record_id","")).upper() for x in al if x.get("tool")=="read_record" and x.get("charged")));alloc=json.loads((wd/"allocation.json").read_text())["allocated_record"]["id"];vr=sorted(set(reads+[alloc]));req(vr==e["verification_records"] and len(vr)<=2,"BUDGET");payload=json.loads((wd/"decision.json").read_text());g=graph(e["shape"]);rescore=score(payload,g["truth"],g["critical_record"],2,vr);req(rescore==e["score"],"SCORE");blocks.setdefault(e["block"],[]).append(e)
 for block,rows in blocks.items():req([e["episode_id"] for e in rows]==schedules[block],"ORDER")
 primary=summarize(blocks["primary"]);primary["success"]=(primary["two_sided_exact_p"]<=0.05 and primary["mean_fully_correct_delta"]>0 and primary["affected_target_stale"]==0 and primary["unaffected_target_overreaction"]==0 and primary["token_ratio"]<=1.2);out={"schema_version":"argo-confirmation-analysis/v1","source_receipt_sha256":sha(a.receipt),"validation":{"passed":True,"episodes":len(r["episodes"]),"bytes_scores_budgets_rederived":len(r["episodes"])},"primary":primary,"replication":summarize(blocks["replication"]) if "replication" in blocks else None,"claim_scope":"synthetic 16-structure task population and Opus 4.6 only"};a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
