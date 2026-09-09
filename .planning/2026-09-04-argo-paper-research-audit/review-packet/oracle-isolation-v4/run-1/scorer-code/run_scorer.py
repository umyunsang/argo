#!/usr/bin/env python3
import json,os,subprocess
from pathlib import Path
fifo=Path("/tmp/start")
try:os.mkfifo(fifo,0o600)
except FileExistsError:pass
print(json.dumps({"ready":True,"pid":os.getpid(),"fifo":str(fifo)}),flush=True)
with fifo.open("rb",buffering=0) as f:f.read(1)
work=Path("/tmp/work");(work/"benchmark/eval_programs").mkdir(parents=True);(work/"benchmark/eval_programs/gold_results").symlink_to("/gold");(work/"pred_results").symlink_to("/submission")
r=subprocess.run(["python","/scorer/eval_fingerprint.py"],cwd=work,capture_output=True,text=True)
print(json.dumps({"exit_code":r.returncode,"stdout":r.stdout,"stderr":r.stderr}),flush=True)
raise SystemExit(r.returncode)
