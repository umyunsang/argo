#!/usr/bin/env python3
from __future__ import annotations
import argparse,ast,hashlib,json,os,platform,shutil,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def tree_manifest(root:Path)->list[dict]:
 return [{"path":str(p.relative_to(root)),"size":p.stat().st_size,"sha256":sha(p)} for p in sorted(root.rglob("*")) if p.is_file()]
def copy_positive(gold:Path,pred:Path)->None:pred.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(gold,pred)
def mutate(path:Path,spec:dict)->None:
 kind=spec["kind"]
 if kind.startswith("csv_"):
  sep=spec.get("sep",",");df=pd.read_csv(path,sep=sep)
  if kind=="csv_set":
   for c in spec["columns"]:df[c]=spec["value"]
  elif kind=="csv_invert_bool":
   for c in spec["columns"]:df[c]=~df[c].astype(bool)
  elif kind=="csv_binary_invert":
   for c in spec["columns"]:df[c]=1-pd.to_numeric(df[c])
  elif kind=="csv_add":
   for c in spec["columns"]:df[c]=pd.to_numeric(df[c])+spec["value"]
  elif kind=="csv_add_all_numeric":
   cols=list(df.select_dtypes(include=["number"]).columns)
   if not cols:raise ValueError("no numeric columns")
   df[cols]=df[cols]+spec["value"]
  else:raise ValueError(kind)
  df.to_csv(path,index=False,sep=sep);return
 if kind=="npy_add":np.save(path,np.load(path)+spec["value"]);return
 if kind=="json_add":
  obj=json.loads(path.read_text());
  for k,v in obj.items():
   if isinstance(v,(int,float)) and not isinstance(v,bool):obj[k]=v+spec["value"]
  path.write_text(json.dumps(obj,sort_keys=True));return
 if kind=="numeric_text_add":np.savetxt(path,np.loadtxt(path)+spec["value"]);return
 if kind=="text_empty":path.write_text("");return
 if kind=="raster_all_different":
  with rasterio.open(path) as src:arr=src.read();profile=src.profile
  arr=np.where(arr==0,1,0).astype(arr.dtype)
  with rasterio.open(path,"w",**profile) as dst:dst.write(arr)
  return
 raise ValueError(kind)
def parse_score(stdout:str):
 lines=[x.strip() for x in stdout.splitlines() if x.strip()]
 if not lines:return None
 try:obj=ast.literal_eval(lines[-1])
 except Exception:return None
 if isinstance(obj,(tuple,list)) and len(obj)>=1 and obj[0] in (0,1,False,True):return int(obj[0])
 return None
def evaluate(eval_script:Path,cwd:Path,timeout:int)->dict:
 env={**os.environ,"PYTHONHASHSEED":"0","OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"}
 t=time.monotonic()
 try:r=subprocess.run(["python",str(eval_script)],cwd=cwd,capture_output=True,text=True,timeout=timeout,env=env)
 except subprocess.TimeoutExpired as e:return {"exit_code":None,"timed_out":True,"score":None,"duration_seconds":round(time.monotonic()-t,6),"stdout":e.stdout or "","stderr":e.stderr or ""}
 return {"exit_code":r.returncode,"timed_out":False,"score":parse_score(r.stdout) if r.returncode==0 else None,"duration_seconds":round(time.monotonic()-t,6),"stdout":r.stdout,"stderr":r.stderr}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--benchmark",type=Path,required=True);p.add_argument("--verified",type=Path,required=True);p.add_argument("--fixtures",type=Path,required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--image-digest",required=True);p.add_argument("--repeats",type=int,default=3);p.add_argument("--timeout",type=int,default=120);a=p.parse_args()
 rows={int(x["instance_id"]):x for x in json.loads(a.verified.read_text())};specs=json.loads(a.fixtures.read_text())["tasks"];a.out.mkdir(parents=True,exist_ok=True);records=[]
 for spec in specs:
  tid=spec["task_id"];row=rows[tid];ev=a.benchmark/"eval_programs"/row["eval_script_name"];gold_dir=a.benchmark/"eval_programs/gold_results";task_runs=[]
  task_meta={"instance_id":tid,"domain":row["domain"],"task_sha256":hashlib.sha256(json.dumps(row,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest(),"eval_script":row["eval_script_name"],"eval_script_sha256":sha(ev),"declared_output":row["output_fname"],"outputs":spec["outputs"],"gold_sha256":{g:sha(gold_dir/g) for g in sorted(set(spec["outputs"].values()))}}
  for fixture,expected in (("positive",1),("corrupt",0)):
   for rep in range(1,a.repeats+1):
    wd=a.out/f"task-{tid}"/f"{fixture}-{rep}";
    if wd.exists():shutil.rmtree(wd)
    (wd/"pred_results").mkdir(parents=True);(wd/"benchmark").symlink_to(a.benchmark)
    for pred,gold in spec["outputs"].items():
     target=wd/"pred_results"/pred;copy_positive(gold_dir/gold,target)
     if fixture=="corrupt":mutate(target,spec["mutation"])
    out_manifest=tree_manifest(wd/"pred_results");res=evaluate(ev,wd,a.timeout);(wd/"benchmark").unlink();res.update({"fixture":fixture,"repeat":rep,"expected_score":expected,"output_manifest":out_manifest});task_runs.append(res)
  pos=[x for x in task_runs if x["fixture"]=="positive"];neg=[x for x in task_runs if x["fixture"]=="corrupt"]
  deterministic=lambda xs:len({(x["exit_code"],x["timed_out"],x["score"],x["stdout"],x["stderr"],json.dumps(x["output_manifest"],sort_keys=True)) for x in xs})==1
  checks={"positive_three_pass":all(x["exit_code"]==0 and not x["timed_out"] and x["score"]==1 for x in pos),"corrupt_three_fail":all(x["exit_code"]==0 and not x["timed_out"] and x["score"]==0 for x in neg),"positive_deterministic":deterministic(pos),"corrupt_deterministic":deterministic(neg)}
  records.append({**task_meta,"mutation":spec["mutation"],"runs":task_runs,"checks":checks,"scorer_certified":all(checks.values())})
 receipt={"schema_version":"argo-sab-task-scorer-certification/v1","created_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"official_rule_based_evaluator_positive_and_format_preserving_corruption","verified_split_path":str(a.verified),"verified_split_sha256":sha(a.verified),"fixture_spec_path":str(a.fixtures),"fixture_spec_sha256":sha(a.fixtures),"container_digest":a.image_digest,"platform":{"os":platform.system().lower(),"machine":platform.machine(),"python":platform.python_version()},"repeat_count":a.repeats,"tasks":records,"scorer_certified_count":sum(x["scorer_certified"] for x in records),"task_count":len(records),"all_scorers_certified":all(x["scorer_certified"] for x in records),"os_oracle_isolation_certified":False,"fully_certified_task_count":0,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0}
 rp=a.out/"certification-receipt.json";rp.write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps({k:receipt[k] for k in ("scorer_certified_count","task_count","all_scorers_certified","fully_certified_task_count","experiment_authorized")}));return 0 if receipt["all_scorers_certified"] else 2
if __name__=="__main__":raise SystemExit(main())
