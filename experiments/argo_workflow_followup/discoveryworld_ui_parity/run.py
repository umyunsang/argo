#!/usr/bin/env python3
"""One-shot journaled controller for DiscoveryWorld official/UI-only parity."""
from __future__ import annotations
import argparse,hashlib,json,os,signal,subprocess,tarfile,tempfile,time,shutil,sys
from pathlib import Path
from lifecycle import append_record,atomic_create,canonical,final_status,publish_exclusive,validate_ledger,validate_manifest
from protocol import compare_pair,validate_cell
HERE=Path(__file__).resolve().parent
EXPECTED_RUN_ID="dw-ui-parity-20260906-v1"
SOURCE_COMMIT="fd591323920be0d3786ef350955de1945aa571e5"
SOURCE_TREE="e83be66c3f357352e8d5d68755100cbc8fdc4d11"
SOURCE_ARCHIVE_SHA="0dafdd25b5a51892bd470dc20ea2fba4fc78abe2a986f20e4ce132f42b3ddb6a"
API_SOURCE_SHA="c455e32ddb5e676a83b7b3e349dda8262473ca54fec217650497a73603d46dc8"
UI_SOURCE_SHA="135f80c0ebc3a909f09cb72306226368b2ca38d657429ded4a700aee76aa3934"
INTERPRETER="/Users/um-yunsang/.cache/argo-research/DiscoveryWorld/.venv/bin/python"
UV="/opt/homebrew/bin/uv"
SANDBOX_EXEC="/usr/bin/sandbox-exec"
ENV_FREEZE_SHA="d6d3a805361e02691e3a3ccb872df18a8f1afc7e91b355731962358f9246fb09"
SOURCE_REPO="/Users/um-yunsang/.cache/argo-research/DiscoveryWorld"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(root,p):return Path(p) if Path(p).is_absolute() else Path(root)/p
def sanitized_env(bundle,source,work):return {"HOME":str(work),"TMPDIR":str(work/"tmp"),"PATH":"/usr/bin:/bin:/opt/homebrew/bin","PYTHONPATH":str(bundle)+os.pathsep+str(source),"PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def validate_approval(a,root):
 root=Path(root);checks={"SCHEMA":a.get("schema_version")=="argo-discoveryworld-ui-parity-approval/v1","STATUS":a.get("status")=="APPROVED" and a.get("approved_by")=="user","RUN":a.get("run_id")==EXPECTED_RUN_ID,"GRID":a.get("cells")==30 and a.get("steps_per_cell")==1000 and a.get("timeout_seconds")==180 and a.get("controller_hard_deadline_seconds")==5520,"SOURCE":a.get("source_repo")==SOURCE_REPO and a.get("source_commit")==SOURCE_COMMIT and a.get("source_tree")==SOURCE_TREE and a.get("source_archive_sha256")==SOURCE_ARCHIVE_SHA and a.get("api_source_sha256")==API_SOURCE_SHA and a.get("ui_source_sha256")==UI_SOURCE_SHA,"INTERPRETER":a.get("interpreter")==INTERPRETER and Path(INTERPRETER).is_file() and a.get("interpreter_sha256")==sha(INTERPRETER) and Path(a.get("controller_interpreter","")).resolve()==Path(sys.executable).resolve() and a.get("controller_interpreter_sha256")==sha(sys.executable) and a.get("uv_path")==UV and a.get("uv_sha256")==sha(UV) and a.get("sandbox_exec_path")==SANDBOX_EXEC and a.get("sandbox_exec_sha256")==sha(SANDBOX_EXEC) and a.get("environment_freeze_sha256")==ENV_FREEZE_SHA,"BOUNDARY":a.get("model_calls")==0 and a.get("docker_calls")==0 and a.get("scorecard_access") is False and a.get("gold_generation") is False and a.get("api_spend_usd")==0.0,"PATHS":a.get("result_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-result.json" and a.get("marker_path")=="paper/research/receipts/discoveryworld-ui-parity-v1.marker.json" and a.get("ledger_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-ledger.jsonl" and a.get("sidecar_root")=="paper/research/receipts/discoveryworld-ui-parity-v1-sidecars" and a.get("result_temp_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-result.pending"}
 for key in ["proposal","design","manifest","schemas","runner","episode","adapter","state_projection","lifecycle","protocol","environment_freeze","prior_failure_closure","calibration_closure"]:
  spec=a.get("bindings",{}).get(key,{});p=rel(root,spec.get("path",""));checks["BIND_"+key.upper()]=p.is_file() and spec.get("sha256")==sha(p)
 errors=[k for k,v in checks.items() if not v];return {"approved":not errors,"checks":checks,"errors":errors}
def preflight_paths(m,root):
 root=Path(root);errors=[];paths=[rel(root,p) for p in m.get("paths",{}).values()]
 for p in paths:
  if p.exists() or p.is_symlink():errors.append("EXISTS:"+str(p))
  cur=p.parent
  while cur!=cur.parent and cur!=root.parent:
   if cur.is_symlink():errors.append("SYMLINK_PARENT:"+str(cur));break
   if cur==root:break
   cur=cur.parent
 if len({str(p.resolve(strict=False)) for p in paths})!=len(paths):errors.append("ALIAS")
 return {"passed":not errors,"errors":errors}
def sandbox_profile(work,bundle=None,source=None):
 def esc(value):return str(Path(value).resolve()).replace("\\","\\\\").replace('"','\\"')
 work_path=esc(work);home=Path("/Users/um-yunsang");denied=[HERE.parents[2],home/".prime",home/".ssh",home/".aws",home/".config",home/".gnupg",home/".kube",home/".docker",home/".netrc",home/".git-credentials",home/".npmrc",home/".pypirc",home/"Library/Keychains",home/"DeepVoice",home/"lgaimer9",home/".cache/argo-research/DeepVoice",Path(SOURCE_REPO)/".git"]
 if source is not None:denied.extend(Path(SOURCE_REPO)/path.name for path in Path(source).iterdir())
 deny_rules=" ".join(f'(subpath "{esc(value)}")' for value in denied)
 return f'(version 1)\n(deny default)\n(allow process*)\n(allow file-read*)\n(deny file-read* {deny_rules})\n(allow file-write* (subpath "{work_path}"))\n(allow file-write* (literal "/dev/null"))\n(allow sysctl-read)\n(allow mach-lookup)\n(allow ipc-posix-shm)\n(allow signal (target self))\n'
def write_sandbox_profile(work,bundle,source):
 path=Path(work)/"worker.sb"
 if not atomic_create(path,sandbox_profile(work,bundle,source).encode()):raise RuntimeError("SANDBOX_PROFILE_EXISTS")
 path.chmod(0o444);fsync_existing(path);return path
def build_argv(c,interpreter,episode,bundle,source):
 return [str(interpreter),str(episode),"--run-id",EXPECTED_RUN_ID,"--cell-id",c["cell_id"],"--cell-nonce",c["cell_nonce"],"--scenario",c["scenario"],"--difficulty",c["difficulty"],"--seed",str(c["seed"]),"--mode",c["mode"],"--repeat",str(c["repeat"]),"--steps","1000","--thread-id",str(c["thread_id"]),"--source-commit",SOURCE_COMMIT,"--source-tree",SOURCE_TREE,"--source-archive-sha256",SOURCE_ARCHIVE_SHA,"--adapter-sha256",sha(Path(bundle)/"adapter_v2.py"),"--state-projection-sha256",sha(Path(bundle)/"state_projection.py"),"--frame-directory",str(Path(c["workdir"])/"frames"),"--ui-gzip-path",str(c["ui_gzip_path"]),"--event-fd","{EVENT_FD}"]
def group_exists(pgid):
 try:os.killpg(pgid,0);return True
 except ProcessLookupError:return False
def terminate_group(proc,pgid,grace=2):
 try:os.killpg(pgid,signal.SIGTERM)
 except ProcessLookupError:pass
 try:proc.wait(timeout=grace)
 except subprocess.TimeoutExpired:pass
 if group_exists(pgid):
  try:os.killpg(pgid,signal.SIGKILL)
  except ProcessLookupError:pass
 try:proc.wait(timeout=grace)
 except subprocess.TimeoutExpired:return True
 deadline=time.monotonic()+grace
 while group_exists(pgid) and time.monotonic()<deadline:time.sleep(0.01)
 return group_exists(pgid)
def managed_run(argv,cwd,env,stdout_path,stderr_path,event_path,timeout,remaining,on_spawn=None):
 cwd=Path(cwd);cwd.mkdir(parents=True,exist_ok=True);(cwd/"tmp").mkdir(exist_ok=True)
 for p in [stdout_path,stderr_path,event_path]:Path(p).parent.mkdir(parents=True,exist_ok=True)
 flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fds=[];started=time.monotonic();proc=None;pgid=None;failure=None;result=None;old_handlers={};blocked={signal.SIGINT,signal.SIGTERM,signal.SIGHUP};old_mask=signal.pthread_sigmask(signal.SIG_BLOCK,blocked);mask_restored=False
 try:
  for p in [stdout_path,stderr_path,event_path]:fds.append(os.open(p,flags,0o600))
  command=[str(fds[2]) if x=="{EVENT_FD}" else x for x in argv]
  proc=subprocess.Popen(command,cwd=cwd,env=env,stdout=fds[0],stderr=fds[1],pass_fds=(fds[2],),start_new_session=True,close_fds=True);pgid=proc.pid;pgid=os.getpgid(proc.pid)
  def controller_signal(signum,frame):
   terminate_group(proc,pgid);raise KeyboardInterrupt(f"controller signal {signum}")
  for sig in [signal.SIGINT,signal.SIGTERM,signal.SIGHUP]:old_handlers[sig]=signal.getsignal(sig);signal.signal(sig,controller_signal)
  signal.pthread_sigmask(signal.SIG_SETMASK,old_mask);mask_restored=True
  try:
   if on_spawn:on_spawn(proc.pid,pgid)
  except BaseException as exc:
   if terminate_group(proc,pgid):raise RuntimeError("UNREAPED_ON_SPAWN") from exc
   raise RuntimeError("ON_SPAWN_FAILURE") from exc
  timed=False;unreaped=False
  try:code=proc.wait(timeout=max(0.001,min(timeout,remaining)))
  except subprocess.TimeoutExpired:timed=True;unreaped=terminate_group(proc,pgid);code=124
  if not timed and group_exists(pgid):unreaped=True;terminate_group(proc,pgid)
  result={"exit_code":code,"timed_out":timed,"unreaped":unreaped,"duration_seconds":round(time.monotonic()-started,6),"pid":proc.pid,"pgid":pgid}
 except BaseException as exc:
  failure=exc
  if proc is not None and pgid is not None and terminate_group(proc,pgid):failure=RuntimeError("UNREAPED_AFTER_EXCEPTION")
 for sig,handler in old_handlers.items():signal.signal(sig,handler)
 if not mask_restored:signal.pthread_sigmask(signal.SIG_SETMASK,old_mask)
 durability=[]
 for fd in fds:
  try:os.fsync(fd)
  except OSError as exc:durability.append(exc)
  try:os.close(fd)
  except OSError as exc:durability.append(exc)
 if failure is not None:raise failure
 if durability:raise OSError("SIDECAR_FSYNC_OR_CLOSE_FAILURE") from durability[0]
 return result

def file_meta(path):
 p=Path(path);return {"path":str(p),"size":p.stat().st_size,"sha256":sha(p)}
def frame_manifest(frame_dir):
 p=Path(frame_dir);files=[]
 for f in sorted(p.rglob("*")) if p.exists() else []:
  if f.is_file():files.append({"path":str(f.relative_to(p)),"size":f.stat().st_size,"sha256":sha(f)})
 return {"files":files,"count":len(files),"bytes":sum(x["size"] for x in files)}
def revalidate_complete_cells(manifest,cell_results,root,source,bundle):
 closed={}
 for cell in manifest["ordered_cells"]:
  prior=cell_results.get(cell["cell_id"])
  if prior is None:continue
  value=dict(prior)
  if prior.get("status")=="valid_complete":
   try:
    frame_path=rel(root,cell["frame_manifest_path"]);frames=json.loads(frame_path.read_bytes());runtime_cell={**cell,"workdir":prior["runtime_workdir"]};validation=validate_cell(runtime_cell,prior["run"],rel(root,cell["event_path"]),rel(root,cell["ui_gzip_path"]),frames,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_archive_sha256=SOURCE_ARCHIVE_SHA,adapter_sha256=sha(bundle/"adapter_v2.py"),state_projection_sha256=sha(bundle/"state_projection.py"),source_root=source,bundle_root=bundle);value.update({"status":validation["status"],"errors":validation.get("errors",[]),"ui_hashes":validation.get("ui_hashes",[]),"pre_state_hashes":validation.get("pre_state_hashes",[]),"post_state_hashes":validation.get("post_state_hashes",[]),"event_sha256":validation.get("event_sha256"),"ui_gzip_sha256":validation.get("ui_gzip_sha256")})
   except BaseException as exc:value.update({"status":"sidecar_error","errors":["CLOSURE_"+type(exc).__name__],"ui_hashes":[],"pre_state_hashes":[],"post_state_hashes":[]})
  closed[cell["cell_id"]]=value
 return closed
def write_atomic(path,value):
 path=Path(path);tmp=path.with_name(path.name+".tmp");data=json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n"
 if not atomic_create(tmp,data):raise FileExistsError(tmp)
 os.replace(tmp,path);fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def prepare_snapshot(temp_root):
 archive=Path(temp_root)/"source.tar"
 status=subprocess.run(["git","-C",SOURCE_REPO,"status","--porcelain"],text=True,capture_output=True,check=False)
 head=subprocess.run(["git","-C",SOURCE_REPO,"rev-parse","HEAD"],text=True,capture_output=True,check=False)
 tree=subprocess.run(["git","-C",SOURCE_REPO,"rev-parse","HEAD^{tree}"],text=True,capture_output=True,check=False)
 if status.returncode!=0 or status.stdout!="" or head.stdout.strip()!=SOURCE_COMMIT or tree.stdout.strip()!=SOURCE_TREE:raise RuntimeError("SOURCE_REPO_IDENTITY")
 with archive.open("wb") as stream:d=subprocess.run(["git","-C",SOURCE_REPO,"archive","--format=tar",SOURCE_COMMIT],stdout=stream,stderr=subprocess.PIPE,check=False)
 if d.returncode!=0 or sha(archive)!=SOURCE_ARCHIVE_SHA:raise RuntimeError("SOURCE_ARCHIVE_IDENTITY")
 source=Path(temp_root)/"source";source.mkdir()
 with tarfile.open(archive) as t:
  for m in t.getmembers():
   target=(source/m.name).resolve()
   if not str(target).startswith(str(source.resolve())+os.sep):raise RuntimeError("UNSAFE_ARCHIVE")
  t.extractall(source)
 if sha(source/"discoveryworld/DiscoveryWorldAPI.py")!=API_SOURCE_SHA or sha(source/"discoveryworld/UserInterface.py")!=UI_SOURCE_SHA:raise RuntimeError("SOURCE_FILE_IDENTITY")
 for path in sorted(source.rglob("*"),reverse=True):path.chmod(0o555 if path.is_dir() else 0o444)
 source.chmod(0o555)
 return source
# Main execution is intentionally available only after a fully bound approval template is generated.
def freeze_sha():
 done=subprocess.run([UV,"pip","freeze","--python",INTERPRETER],text=True,capture_output=True,check=False)
 if done.returncode!=0:raise RuntimeError("FREEZE_COMMAND")
 return hashlib.sha256(done.stdout.encode()).hexdigest()
def source_repo_identity():
 status=subprocess.run(["git","-C",SOURCE_REPO,"status","--porcelain"],text=True,capture_output=True,check=False)
 head=subprocess.run(["git","-C",SOURCE_REPO,"rev-parse","HEAD"],text=True,capture_output=True,check=False)
 tree=subprocess.run(["git","-C",SOURCE_REPO,"rev-parse","HEAD^{tree}"],text=True,capture_output=True,check=False)
 return status.returncode==0 and status.stdout=="" and head.stdout.strip()==SOURCE_COMMIT and tree.stdout.strip()==SOURCE_TREE
def fsync_existing(path):
 fd=os.open(path,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def runtime_identity(approval,root,approval_path,approval_bytes,manifest_path,manifest_bytes,bundle,source):
 try:
  if Path(approval_path).read_bytes()!=approval_bytes or Path(manifest_path).read_bytes()!=manifest_bytes:return False
  if sha(INTERPRETER)!=approval["interpreter_sha256"] or sha(sys.executable)!=approval["controller_interpreter_sha256"] or sha(UV)!=approval["uv_sha256"] or sha(SANDBOX_EXEC)!=approval["sandbox_exec_sha256"]:return False
  for spec in approval["bindings"].values():
   p=rel(root,spec["path"])
   if not p.is_file() or sha(p)!=spec["sha256"]:return False
  expected={"run.py":approval["bindings"]["runner"]["sha256"],"episode.py":approval["bindings"]["episode"]["sha256"],"adapter_v2.py":approval["bindings"]["adapter"]["sha256"],"state_projection.py":approval["bindings"]["state_projection"]["sha256"],"lifecycle.py":approval["bindings"]["lifecycle"]["sha256"],"protocol.py":approval["bindings"]["protocol"]["sha256"],"schemas.json":approval["bindings"]["schemas"]["sha256"],"manifest.json":approval["bindings"]["manifest"]["sha256"],"proposal.json":approval["bindings"]["proposal"]["sha256"],"design.json":approval["bindings"]["design"]["sha256"],"approval.json":hashlib.sha256(approval_bytes).hexdigest()}
  if any(not (bundle/name).is_file() or sha(bundle/name)!=digest for name,digest in expected.items()):return False
  return sha(source/"discoveryworld/DiscoveryWorldAPI.py")==API_SOURCE_SHA and sha(source/"discoveryworld/UserInterface.py")==UI_SOURCE_SHA
 except (OSError,KeyError,TypeError):return False
def preflight_identity_record(approval):
 return {"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"interpreter_sha256":sha(INTERPRETER),"controller_interpreter_sha256":sha(sys.executable),"uv_sha256":sha(UV),"sandbox_exec_sha256":sha(SANDBOX_EXEC),"environment_freeze_sha256":ENV_FREEZE_SHA,"bindings":{key:value["sha256"] for key,value in sorted(approval["bindings"].items())}}
def result_bytes(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n"
class ControllerSignalLatch:
 SIGNALS=(signal.SIGINT,signal.SIGTERM,signal.SIGHUP)
 def __init__(self):self.pending=None;self.previous={}
 def handler(self,signum,frame):self.pending=self.pending or signum
 def install(self):
  for sig in self.SIGNALS:self.previous[sig]=signal.getsignal(sig);signal.signal(sig,self.handler)
 def begin_durable_closure(self):
  for sig in self.SIGNALS:signal.signal(sig,signal.SIG_IGN)
 def restore(self):
  for sig,handler in self.previous.items():signal.signal(sig,handler)
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);args=p.parse_args();root=Path.cwd();approval_bytes=args.approval.read_bytes();approval_sha=hashlib.sha256(approval_bytes).hexdigest();approval=json.loads(approval_bytes);check=validate_approval(approval,root)
 if not check["approved"]:
  value={"status":"BLOCKED_BEFORE_CONSUMPTION","approval":check,"cells_planned":0,"cells_spawned":0,"model_calls":0,"spend_usd":0.0};print(json.dumps(value,indent=2,sort_keys=True));return 2
 manifest_path=rel(root,approval["bindings"]["manifest"]["path"]);manifest_bytes=manifest_path.read_bytes();manifest_sha=hashlib.sha256(manifest_bytes).hexdigest();manifest=json.loads(manifest_bytes);mcheck=validate_manifest(manifest)
 if not mcheck["passed"]:raise RuntimeError("MANIFEST_INVALID")
 if args.out.resolve()!=rel(root,manifest["paths"]["result"]).resolve():raise RuntimeError("RESULT_PATH_MISMATCH")
 pre=preflight_paths(manifest,root)
 if not pre["passed"]:raise RuntimeError("OUTPUT_COLLISION:"+str(pre["errors"]))
 if freeze_sha()!=ENV_FREEZE_SHA or not source_repo_identity():raise RuntimeError("PREFLIGHT_ENVIRONMENT_IDENTITY")
 with tempfile.TemporaryDirectory(prefix="dw-ui-parity-sealed-") as td:
  temp=Path(td);source=prepare_snapshot(temp);bundle=temp/"bundle";bundle.mkdir()
  for name in ["run.py","episode.py","adapter_v2.py","state_projection.py","lifecycle.py","protocol.py","schemas.json","manifest.json","approval.json","proposal.json","design.json"]:
   if name=="manifest.json":data=manifest_bytes
   elif name=="approval.json":data=approval_bytes
   elif name=="proposal.json":data=rel(root,approval["bindings"]["proposal"]["path"]).read_bytes()
   elif name=="design.json":data=rel(root,approval["bindings"]["design"]["path"]).read_bytes()
   else:data=(HERE/name).read_bytes()
   target=bundle/name;target.write_bytes(data);target.chmod(0o444);fsync_existing(target)
  fsync_existing(bundle)
  if args.approval.read_bytes()!=approval_bytes or manifest_path.read_bytes()!=manifest_bytes:raise RuntimeError("AUTHORITY_TOCTOU_BEFORE_CONSUMPTION")
  if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source):raise RuntimeError("BYTE_IDENTITY_BEFORE_CONSUMPTION")
  preflight_identity_sha=hashlib.sha256(canonical(preflight_identity_record(approval))).hexdigest()
  marker=rel(root,manifest["paths"]["marker"]);ledger=rel(root,manifest["paths"]["ledger"]);side_root=rel(root,manifest["paths"]["sidecar_root"]);result_path=rel(root,manifest["paths"]["result"]);result_temp=rel(root,manifest["paths"]["result_temp"]);consumed_at=__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds");marker_value={"schema_version":"argo-ui-parity-marker/v1","run_id":EXPECTED_RUN_ID,"approval_sha256":approval_sha,"manifest_sha256":manifest_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"consumed_at":consumed_at}
  if not atomic_create(marker,canonical(marker_value)+b"\n"):raise RuntimeError("MARKER_EXISTS")
  signal_latch=ControllerSignalLatch();signal_latch.install()
  side_root.mkdir(parents=True);fsync_existing(side_root.parent);previous=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":EXPECTED_RUN_ID,"manifest_sha256":manifest_sha,"approval_sha256":approval_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"started_at":consumed_at});seq=0;deadline=time.monotonic()+manifest["budgets"]["controller_hard_deadline_seconds"];cell_results={};controller_error=None
  for cell in manifest["ordered_cells"]:
   if signal_latch.pending is not None:controller_error="CONTROLLER_SIGNAL_"+str(signal_latch.pending);break
   if time.monotonic()>=deadline:controller_error="GLOBAL_DEADLINE";break
   if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source):controller_error="RUNTIME_IDENTITY_DRIFT";break
   new_seq=seq+1;new_previous=append_record(ledger,{"event":"planned","sequence":new_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=new_seq,new_previous
   work=temp/cell["workdir"];frame=work/"frames";event=rel(root,cell["event_path"]);ui_gz=rel(root,cell["ui_gzip_path"]);stdout=rel(root,cell["stdout_path"]);stderr=rel(root,cell["stderr_path"]);temp_event=work/"events.ndjson";temp_ui_gz=work/"ui.ndjson.gz";temp_stdout=work/"stdout.bin";temp_stderr=work/"stderr.bin";runtime_cell={**cell,"workdir":str(work),"event_path":str(temp_event),"ui_gzip_path":str(temp_ui_gz)};worker_argv=None;profile=None;argv=None;spawned_durable=False
   def spawned(pid,pgid,cell=cell):
    nonlocal seq,previous,spawned_durable
    candidate_seq=seq+1;candidate_previous=append_record(ledger,{"event":"spawned","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"pid":pid,"pgid":pgid,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous;spawned_durable=True
   fm_path=rel(root,cell["frame_manifest_path"])
   try:
    worker_argv=build_argv(runtime_cell,INTERPRETER,bundle/"episode.py",bundle,source);profile=write_sandbox_profile(work,bundle,source);argv=[SANDBOX_EXEC,"-f",str(profile),*worker_argv]
    run=managed_run(argv,work,sanitized_env(bundle,source,work),temp_stdout,temp_stderr,temp_event,cell["timeout_seconds"],deadline-time.monotonic(),spawned)
    for src,dest in [(temp_stdout,stdout),(temp_stderr,stderr),(temp_event,event),(temp_ui_gz,ui_gz)]:
     if src.is_file() and not atomic_create(dest,src.read_bytes()):raise RuntimeError("SIDECAR_EXISTS")
    frames=frame_manifest(frame);write_atomic(fm_path,frames);validation=validate_cell(runtime_cell,run,event,ui_gz,frames,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_archive_sha256=SOURCE_ARCHIVE_SHA,adapter_sha256=sha(bundle/"adapter_v2.py"),state_projection_sha256=sha(bundle/"state_projection.py"),source_root=source,bundle_root=bundle);status="unreaped" if run["unreaped"] else validation["status"]
   except BaseException as exc:
    salvage_errors=[]
    for src,dest in [(temp_stdout,stdout),(temp_stderr,stderr),(temp_event,event),(temp_ui_gz,ui_gz)]:
     if src.is_file() and not dest.exists():
      try:
       if not atomic_create(dest,src.read_bytes()):raise FileExistsError(dest)
      except OSError as salvage:salvage_errors.append(type(salvage).__name__)
    run={"exit_code":None,"timed_out":False,"unreaped":False,"duration_seconds":0};frames={"files":[],"count":0,"bytes":0};validation={"status":"unreaped" if str(exc) in {"UNREAPED_ON_SPAWN","UNREAPED_AFTER_EXCEPTION"} else "ledger_error" if str(exc)=="ON_SPAWN_FAILURE" or isinstance(exc,KeyboardInterrupt) else "spawn_failure" if isinstance(exc,FileNotFoundError) else "sidecar_error","errors":[type(exc).__name__,*salvage_errors]};status=validation["status"];controller_error=type(exc).__name__+("+SALVAGE:"+",".join(salvage_errors) if salvage_errors else "")
   metas={k:file_meta(path) for k,path in [("stdout",stdout),("stderr",stderr),("events",event),("ui_gzip",ui_gz)] if Path(path).is_file()};fm_meta=file_meta(fm_path) if fm_path.is_file() else {};new_seq=seq+1;new_previous=append_record(ledger,{"event":"finished","sequence":new_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"status":status,"exit_code":run.get("exit_code"),"timed_out":run.get("timed_out"),"stdout":metas.get("stdout",{}),"stderr":metas.get("stderr",{}),"events":metas.get("events",{}),"ui_gzip":metas.get("ui_gzip",{}),"frame_manifest":fm_meta,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=new_seq,new_previous;cell_results[cell["cell_id"]]={"status":status,"errors":validation.get("errors",[]),"ui_hashes":validation.get("ui_hashes",[]),"pre_state_hashes":validation.get("pre_state_hashes",[]),"post_state_hashes":validation.get("post_state_hashes",[]),"run":run,"sidecars":metas,"frame_manifest":frames,"runtime_workdir":str(work),"event_sha256":validation.get("event_sha256"),"ui_gzip_sha256":validation.get("ui_gzip_sha256")};shutil.rmtree(work,ignore_errors=True)
   if signal_latch.pending is not None:controller_error=controller_error or "CONTROLLER_SIGNAL_"+str(signal_latch.pending)
   sidecar_bytes=sum(path.stat().st_size for path in side_root.rglob("*") if path.is_file())
   if sidecar_bytes>manifest["budgets"]["sidecar_total_bytes_max"]:controller_error="SIDECAR_DISK_BUDGET"
   if time.monotonic()>=deadline:controller_error=controller_error or "GLOBAL_DEADLINE"
   if controller_error or status in {"unreaped","sidecar_error","ledger_error","global_deadline"}:break
  cell_results=revalidate_complete_cells(manifest,cell_results,root,source,bundle)
  mode=[{**pair,"status":compare_pair(cell_results.get(pair["official"],{}),cell_results.get(pair["ui_only"],{}))} for pair in manifest["mode_pairs"]];ui_pairs=[{**pair,"status":compare_pair(cell_results.get(pair["left"],{}),cell_results.get(pair["right"],{}))} for pair in manifest["ui_repeat_pairs"]];statuses=[cell_results[cell["cell_id"]]["status"] for cell in manifest["ordered_cells"] if cell["cell_id"] in cell_results];pair_statuses=[pair["status"] for pair in mode+ui_pairs]
  if signal_latch.pending is not None:controller_error=controller_error or "CONTROLLER_SIGNAL_"+str(signal_latch.pending)
  if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source):controller_error=controller_error or "FINAL_RUNTIME_IDENTITY_DRIFT"
  if time.monotonic()>=deadline:controller_error=controller_error or "FINAL_GLOBAL_DEADLINE"
  expected_header={"manifest_sha256":manifest_sha,"approval_sha256":approval_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha};preledger=validate_ledger(ledger,manifest,allow_partial=True,expected_header=expected_header,strict_sidecars=True)
  if not preledger["passed"]:controller_error=controller_error or "LEDGER_INVALID"
  status=final_status(statuses,pair_statuses,30)
  if controller_error:status="INCOMPLETE" if len(statuses)<30 else "INVALID"
  if controller_error:
   candidate_seq=seq+1;candidate_previous=append_record(ledger,{"event":"controller_stop","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"reason":controller_error,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous
  result={"schema_version":"argo-discoveryworld-ui-parity-result/v1","run_id":EXPECTED_RUN_ID,"status":status,"approval_sha256":approval_sha,"manifest_sha256":manifest_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"cells":cell_results,"mode_pairs":mode,"ui_repeat_pairs":ui_pairs,"summary":{"cells_planned":len(statuses),"valid_complete":sum(x=="valid_complete" for x in statuses),"mode_exact":sum(x["status"]=="EXACT" for x in mode),"mode_mismatch":sum(x["status"]=="OBSERVED_MISMATCH" for x in mode),"mode_unobservable":sum(x["status"]=="UNOBSERVABLE" for x in mode),"ui_repeat_exact":sum(x["status"]=="EXACT" for x in ui_pairs),"controller_error":controller_error},"ledger_last_record_sha256_before_final":previous,"model_calls":0,"spend_usd":0.0};payload=result_bytes(result);payload_sha=hashlib.sha256(payload).hexdigest()
  signal_latch.begin_durable_closure()
  if not atomic_create(result_temp,payload):raise RuntimeError("RESULT_TEMP_EXISTS")
  candidate_seq=seq+1;candidate_previous=append_record(ledger,{"event":"finalized","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"status":status,"result_sha256":payload_sha,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous
  closed=validate_ledger(ledger,manifest,allow_partial=status=="INCOMPLETE",expected_header=expected_header,strict_sidecars=True)
  if not closed["passed"] or not closed["finalized"]:raise RuntimeError("CLOSED_LEDGER_INVALID:"+str(closed["errors"]))
  publish_exclusive(result_temp,result_path);signal_latch.restore()
  print(json.dumps({"status":status,"summary":result["summary"]},indent=2,sort_keys=True));return 0 if status=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
