#!/usr/bin/env python3
"""Run the zero-cost scientific-choice manipulation diagnostic."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,platform,subprocess,sys,time
from pathlib import Path
from policy import evaluate
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--capsule",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();start=time.monotonic();capsule=json.loads(a.capsule.read_text());result=evaluate(capsule)
 root=Path(__file__).resolve().parents[2];commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
 receipt={"schema_version":"argo-scientific-choice-manipulation/v1","created_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"capsule_path":str(a.capsule.resolve()),"capsule_sha256":sha(a.capsule),"runner_path":str(Path(__file__).resolve()),"runner_sha256":sha(Path(__file__)),"policy_path":str((Path(__file__).parent/"policy.py").resolve()),"policy_sha256":sha(Path(__file__).parent/"policy.py"),"harness_commit":commit,"python":platform.python_version(),"python_executable":sys.executable,"python_executable_sha256":sha(Path(sys.executable)),"platform":platform.platform(),"result":result,"duration_seconds":round(time.monotonic()-start,6),"scope":"development manipulation only; not efficacy","model_calls":0,"tool_calls":0,"spend_usd":0.0,"paid_execution":False}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"passed":result["passed"],"typed_policy_manipulation_active":result["typed_policy_manipulation_active"],"efficacy_result":False,"model_calls":0,"spend_usd":0.0}));return 0 if result["passed"] else 2
if __name__=="__main__":raise SystemExit(main())
