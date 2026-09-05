#!/usr/bin/env python3
"""Audit whether record-language withdrawal scope matches the graph oracle."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json
from pathlib import Path
from collections import defaultdict,deque
from task_pack import SHAPES,graph,records

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reach_from(source,edges):
 a=defaultdict(list)
 for e in edges:a[e["source"]].append(e["target"])
 seen={source};q=deque([source])
 while q:
  for n in a[q.popleft()]:
   if n not in seen:seen.add(n);q.append(n)
 return seen
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();rows=[]
 for shape in SHAPES:
  s=graph(shape);g=s["graph"];removed=set(g["event"]["removed_edge_ids"]);kept=[e for e in g["edges"] if e["id"] not in removed];s1_reaches_decision_after="D" in reach_from("S1",kept);w=records(s)["W"];global_wording="S1 support" in w and "withdrawn" in w;conflict=(global_wording and s1_reaches_decision_after);rows.append({"shape":shape,"removed_edges":sorted(removed),"S1_reaches_decision_after_event":s1_reaches_decision_after,"W_global_source_withdrawal_wording":global_wording,"semantic_conflict":conflict})
 conflicts=[x["shape"] for x in rows if x["semantic_conflict"]];out={"schema_version":"argo-confirmation-semantic-audit/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"task_pack_sha256":sha(Path(__file__).parent/"task_pack.py"),"conflicts":conflicts,"conflict_count":len(conflicts),"rows":rows,"confirmatory_interpretation":"INVALID if any conflict; do not exclude post outcome","expected_fix":"future tasks must describe the removed edge, not globally revoke a multiply connected source","model_calls":0,"spend_usd":0.0};a.out.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({"conflicts":conflicts,"count":len(conflicts)}))
if __name__=="__main__":main()
