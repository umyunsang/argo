#!/usr/bin/env python3
"""Post-run defect audit and status-only sensitivity; never overwrites original scores."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json
from pathlib import Path
from task_pack import family

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--receipt",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();r=json.loads(a.receipt.read_text());rows=[]
 for ep in r["episodes"]:
  spec=family(ep["family"]);payload=json.loads((Path(ep["workdir"])/"decision.json").read_text());truth=spec["truth"]["constraint_status"];status=payload["constraint_status"]
  affected=spec["decision_node"] in spec["oracle_affected"]
  rows.append({"episode_id":ep["episode_id"],"family":ep["family"],"condition":ep["condition"],"affected_decision":affected,"truth_status":truth,"reported_status":status,"status_correct":status==truth,"resolved":status!="unverified","stale_consistent_status_only":truth=="withdrawn" and status=="valid","original_score":ep["score"],"reason":payload["reason"],"verification_records":ep["verification_records"]})
 pairs=[]
 for fam in sorted(set(x["family"] for x in rows)):
  p={x["condition"]:x for x in rows if x["family"]==fam};pairs.append({"family":fam,"affected_decision":p["C_BASE"]["affected_decision"],"base_status_correct":p["C_BASE"]["status_correct"],"target_status_correct":p["C_TARGET"]["status_correct"],"base_resolved":p["C_BASE"]["resolved"],"target_resolved":p["C_TARGET"]["resolved"],"status_correct_delta":int(p["C_TARGET"]["status_correct"])-int(p["C_BASE"]["status_correct"]),"resolved_delta":int(p["C_TARGET"]["resolved"])-int(p["C_BASE"]["resolved"])})
 affected=[x for x in pairs if x["affected_decision"]];unaffected=[x for x in pairs if not x["affected_decision"]]
 out={"schema_version":"argo-corrected-b2-defect-audit/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"source_receipt_sha256":sha(a.receipt),"protocol_defects":["stale_consistent hardcoded valid/proceed as stale even when valid is ground truth","action proceed/recheck semantics are ambiguous for a confirmed withdrawal","read_record enum omits C and R6 used by the multi-hop family","frozen 3-of-4 win rule incorrectly treats unaffected-family ties as evidence against a targeted mechanism"],"original_endpoint_status":"INVALID_FOR_CAUSAL_DECISION; preserve unchanged","status_only_sensitivity":{"affected_families":len(affected),"affected_target_wins":sum(x["status_correct_delta"]>0 for x in affected),"affected_losses":sum(x["status_correct_delta"]<0 for x in affected),"unaffected_families":len(unaffected),"unaffected_no_harm":sum(x["status_correct_delta"]>=0 for x in unaffected),"all_target_status_correct":sum(x["target_status_correct"] for x in pairs),"all_base_status_correct":sum(x["base_status_correct"] for x in pairs)},"pairs":pairs,"rows":rows,"interpretation":"post-hoc status-only diagnostic: targeting improved status resolution in both affected families and preserved both unaffected families, but no efficacy claim is admissible","decision":"HOLD_C_AND_REDESIGN_OUTCOME_CONTRACT","model_calls":0,"spend_usd":0.0}
 a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n");print(json.dumps(out["status_only_sensitivity"],indent=2))
if __name__=="__main__":main()
