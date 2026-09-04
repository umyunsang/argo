#!/usr/bin/env python3
"""Derive task dependency candidates from pinned ScienceAgentBench Python sources."""
from __future__ import annotations
import argparse, ast, collections, datetime as dt, hashlib, importlib.util, json, re, sys, sysconfig
from pathlib import Path
MAP={"Bio":"biopython","DeepPurpose":"deeppurpose","MDAnalysis":"mdanalysis","sklearn":"scikit-learn","iris":"scitools-iris","papyrus_scripts":"papyrus-scripts"}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def roots(p:Path)->set[str]:
 tree=ast.parse(p.read_text(encoding="utf-8",errors="replace"));out=set()
 for n in ast.walk(tree):
  if isinstance(n,ast.Import):out.update(x.name.split(".")[0] for x in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:out.add(n.module.split(".")[0])
 return out
def dist(root:str)->str:return MAP.get(root,root.replace("_","-").lower())
def is_stdlib(root:str)->bool:
 names=getattr(sys,"stdlib_module_names",None)
 if names is not None:return root in names
 spec=importlib.util.find_spec(root)
 if spec is None or spec.origin in (None,"built-in","frozen"):return spec is not None
 origin=Path(spec.origin).resolve();stdlib=Path(sysconfig.get_paths()["stdlib"]).resolve()
 try:origin.relative_to(stdlib)
 except ValueError:return False
 return "site-packages" not in origin.parts and "dist-packages" not in origin.parts
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--benchmark",type=Path,required=True);ap.add_argument("--certification",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args();cert=json.loads(a.certification.read_text());rows={int(r["instance_id"]):r for r in __import__("csv").DictReader((a.benchmark/"ScienceAgentBench.csv").open(encoding="utf-8"))};tasks=[];union=set()
 for item in cert["task_details"]:
  tid=int(item["instance_id"]);row=rows[tid];files=[a.benchmark/"benchmark/gold_programs"/row["gold_program_name"],a.benchmark/"benchmark/eval_programs"/row["eval_script_name"]];imps=set()
  for p in files:imps|={x for x in roots(p) if not is_stdlib(x) and x!="benchmark"}
  pkgs=sorted(dist(x) for x in imps);union.update(pkgs);tasks.append({"instance_id":tid,"domain":row["domain"],"gold_program":row["gold_program_name"],"gold_program_sha256":sha(files[0]),"eval_script":row["eval_script_name"],"eval_script_sha256":sha(files[1]),"import_roots":sorted(imps),"distribution_candidates":pkgs,"exact_lock_status":"PENDING"})
 cfg=a.benchmark/"config_conda_env.py";req=a.benchmark/"requirements.txt";text=cfg.read_text();hazards=[]
 if "pipreqs" in text:hazards.append("dependencies are derived dynamically from a program at setup time")
 if "@main" in text:hazards.append("git dependency uses moving @main reference")
 if re.search(r"(?:<=|<)[0-9]",text):hazards.append("core packages use version ranges rather than exact artifacts")
 if "cu121" in text:hazards.append("DGL fallback uses a CUDA 12.1 wheel index and is not a platform-neutral lock")
 receipt={"schema_version":"argo-sab-dependency-inventory/v1","checked_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"origin":"deterministic_ast_read_only_audit","benchmark":{"path":str(a.benchmark),"commit":"c26e151ed601ba109dc4d35e057ff8e73fec469d","config_path":str(cfg),"config_sha256":sha(cfg),"requirements_path":str(req),"requirements_sha256":sha(req)},"candidate_task_count":len(tasks),"domain_counts":dict(sorted(collections.Counter(x["domain"] for x in tasks).items())),"distribution_candidate_count":len(union),"distribution_candidates":sorted(union),"tasks":tasks,"official_setup_hazards":hazards,"selected_target_platform":"linux-x86_64 container, exact Python and artifact locks pending","current_host_is_certification_target":False,"install_performed":False,"exact_lock_built":False,"agent_scorer_environment_parity":False,"certified_task_count":0,"experiment_authorized":False,"model_calls":0,"spend_usd":0.0};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");print(json.dumps({k:receipt[k] for k in ("candidate_task_count","domain_counts","distribution_candidate_count","distribution_candidates","official_setup_hazards","selected_target_platform","exact_lock_built")},ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
