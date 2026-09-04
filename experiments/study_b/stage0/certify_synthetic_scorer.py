#!/usr/bin/env python3
"""Zero-cost three-repeat certification of adapter score-state semantics."""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;TASKS=HERE.parent/"tasks";sys.path.insert(0,str(TASKS));import run_t1
import scorer_certification as cert
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def setup(root:Path):
 b=root/"bench";data=b/"benchmark/datasets/fixture";ev=b/"benchmark/eval_programs";gold=ev/"gold_results";data.mkdir(parents=True);gold.mkdir(parents=True);(data/"input.csv").write_text("x\n1\n");(gold/"answer.txt").write_text("gold");fields=["instance_id","domain","task_inst","output_fname","domain_knowledge","dataset_folder_tree","dataset_preview","eval_script_name"];row={"instance_id":"999","domain":"Fixture","task_inst":"produce output","output_fname":"pred_results/out.csv","domain_knowledge":"fixture","dataset_folder_tree":"|-- fixture/\n    |-- input.csv","dataset_preview":"x\n1","eval_script_name":"fixture_eval.py"}
 with (b/"ScienceAgentBench.csv").open("w",newline="") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
 ws=root/"ws";run_t1.setup_workspace(999,b,ws);return b,ws
def evaluator(b:Path,code:str):(b/"benchmark/eval_programs/fixture_eval.py").write_text("# gold_results/answer.txt\n"+code+"\n")
def record(score,raw):
 o=json.loads(raw);return {"ordinal_score":score,"official_score":o.get("raw_score",0),"inadmissible_execution":o.get("inadmissible_execution"),"status":o.get("status")}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();anchors={"fatal":[],"valid_wrong":[],"valid_correct":[]}
 with tempfile.TemporaryDirectory() as td:
  b,ws=setup(Path(td));out=ws/"pred_results/out.csv"
  for _ in range(3):
   if out.exists():out.unlink()
   s,r=run_t1.verify_output(999,b,ws);anchors["fatal"].append(record(s,r))
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text("prediction\n0\n")
  evaluator(b,'print("0, wrong")')
  for _ in range(3):s,r=run_t1.verify_output(999,b,ws);anchors["valid_wrong"].append(record(s,r))
  evaluator(b,'print("1, correct")')
  for _ in range(3):s,r=run_t1.verify_output(999,b,ws);anchors["valid_correct"].append(record(s,r))
 result=cert.validate_anchors(anchors);receipt={"schema_version":"argo-synthetic-scorer-anchor/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_synthetic_fixture","adapter_path":str((TASKS/"run_t1.py").resolve()),"adapter_sha256":sha(TASKS/"run_t1.py"),"anchors":anchors,"validation":result,"development_distribution_executed":False,"real_task_scorer_certified":False,"stage0_runner_certified":False,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps(result,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
