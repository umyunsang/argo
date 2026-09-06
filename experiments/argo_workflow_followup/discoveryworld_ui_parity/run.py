#!/usr/bin/env python3
"""One-shot journaled controller for DiscoveryWorld official/UI-only parity."""
from __future__ import annotations
import argparse,hashlib,json,os,signal,stat,subprocess,tarfile,tempfile,time,shutil,sys
from pathlib import Path
import environment_manifest as environment_manifest_module
import lifecycle as lifecycle_module
import protocol as protocol_module
from environment_manifest import copy_and_verify,verify_root
from lifecycle import ArtifactNamespace,append_record,atomic_create,canonical,final_status,publish_exclusive,validate_ledger,validate_manifest
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
ENGINE_REPO="/Users/um-yunsang/argo-paper-orx"
MARKER_REL="paper/research/receipts/discoveryworld-ui-parity-v1.marker.json"
ABORT_REL="paper/research/receipts/discoveryworld-ui-parity-v1-controller-abort.json"
ABORT_PENDING_REL="paper/research/receipts/discoveryworld-ui-parity-v1-controller-abort.pending"
EXECUTION_BINDING_KEYS=("runner","lifecycle","protocol","episode","adapter","state_projection","manifest","schemas","launcher","bootstrap","environment_manifest_module","environment_content_manifest")
AUTHORITY_BINDING_KEYS=EXECUTION_BINDING_KEYS+("design","proposal")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(root,p):return Path(p) if Path(p).is_absolute() else Path(root)/p
def sanitized_env(bundle,source,site_packages,work):return {"HOME":str(work),"TMPDIR":str(work/"tmp"),"PATH":"/usr/bin:/bin:/opt/homebrew/bin","PYTHONPATH":str(bundle)+os.pathsep+str(source)+os.pathsep+str(site_packages),"PYTHONNOUSERSITE":"1","PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def validate_approval(a,root):
 root=Path(root);checks={"REPO":root.resolve()==Path(ENGINE_REPO) and a.get("engine_repo")==ENGINE_REPO,"SCHEMA":a.get("schema_version")=="argo-discoveryworld-ui-parity-approval/v1","STATUS":a.get("status")=="APPROVED" and a.get("approved_by")=="user" and isinstance(a.get("approved_at"),str) and a.get("user_approval_message")==a.get("required_approval_text") and isinstance(a.get("user_approval_message"),str) and a.get("user_approval_message_sha256")==hashlib.sha256(a["user_approval_message"].encode()).hexdigest(),"RUN":a.get("run_id")==EXPECTED_RUN_ID,"GRID":a.get("cells")==30 and a.get("steps_per_cell")==1000 and a.get("timeout_seconds")==180 and a.get("controller_hard_deadline_seconds")==5520,"SOURCE":a.get("source_repo")==SOURCE_REPO and a.get("source_commit")==SOURCE_COMMIT and a.get("source_tree")==SOURCE_TREE and a.get("source_archive_sha256")==SOURCE_ARCHIVE_SHA and a.get("api_source_sha256")==API_SOURCE_SHA and a.get("ui_source_sha256")==UI_SOURCE_SHA,"INTERPRETER":a.get("interpreter")==INTERPRETER and Path(INTERPRETER).is_file() and a.get("interpreter_sha256")==sha(INTERPRETER) and Path(a.get("controller_interpreter","")).resolve()==Path(sys.executable).resolve() and a.get("controller_interpreter_sha256")==sha(sys.executable) and a.get("uv_path")==UV and a.get("uv_sha256")==sha(UV) and a.get("sandbox_exec_path")==SANDBOX_EXEC and a.get("sandbox_exec_sha256")==sha(SANDBOX_EXEC) and a.get("environment_freeze_sha256")==ENV_FREEZE_SHA,"BOUNDARY":a.get("model_calls")==0 and a.get("docker_calls")==0 and a.get("scorecard_access") is False and a.get("gold_generation") is False and a.get("api_spend_usd")==0.0,"PATHS":a.get("result_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-result.json" and a.get("marker_path")=="paper/research/receipts/discoveryworld-ui-parity-v1.marker.json" and a.get("ledger_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-ledger.jsonl" and a.get("sidecar_root")=="paper/research/receipts/discoveryworld-ui-parity-v1-sidecars" and a.get("result_temp_path")=="paper/research/receipts/discoveryworld-ui-parity-v1-result.pending" and a.get("controller_abort_path")==ABORT_REL and a.get("controller_abort_pending_path")==ABORT_PENDING_REL}
 for key in ["proposal","design","manifest","schemas","runner","episode","adapter","state_projection","lifecycle","protocol","launcher","environment_manifest_module","environment_content_manifest","bootstrap","environment_freeze","prior_failure_closure","calibration_closure","immutable_validation","method_review","runtime_review","handoff_review","user_authorization"]:
  spec=a.get("bindings",{}).get(key,{});p=rel(root,spec.get("path",""));checks["BIND_"+key.upper()]=p.is_file() and spec.get("sha256")==sha(p)
 try:
  env_spec=a.get("bindings",{}).get("environment_content_manifest",{});env_obj=json.loads(rel(root,env_spec.get("path","")).read_bytes());checks["ENVIRONMENT_CONTENT"]=env_obj.get("schema_version")=="argo-ui-parity-environment-content/v1" and env_obj.get("aggregate_sha256")==a.get("environment_content_aggregate_sha256")
 except (OSError,json.JSONDecodeError,TypeError):checks["ENVIRONMENT_CONTENT"]=False
 execution={key:a.get("bindings",{}).get(key,{}).get("sha256") for key in EXECUTION_BINDING_KEYS};execution_sha=hashlib.sha256(canonical(execution)).hexdigest();authority={key:a.get("bindings",{}).get(key,{}).get("sha256") for key in AUTHORITY_BINDING_KEYS};authority_sha=hashlib.sha256(canonical(authority)).hexdigest();checks["EXECUTION_ROOT"]=execution_sha==a.get("execution_root_sha256");checks["AUTHORITY_ROOT"]=authority_sha==a.get("authority_root_sha256");derived=derive_approval_text(a,execution_sha,authority_sha)
 try:proposal=json.loads(rel(root,a["bindings"]["proposal"]["path"]).read_bytes());checks["APPROVAL_TEXT"]=a.get("required_approval_text")==derived and proposal.get("required_approval_text")==derived
 except (OSError,KeyError,TypeError,json.JSONDecodeError):checks["APPROVAL_TEXT"]=False
 for key,verdict,root_key in [("immutable_validation","PASS","execution_root_sha256"),("method_review","PASS","authority_root_sha256"),("runtime_review","PASS","execution_root_sha256"),("handoff_review","ACCEPT","authority_root_sha256")]:
  try:
   spec=a["bindings"][key];review=json.loads(rel(root,spec["path"]).read_bytes());expected=authority_sha if root_key=="authority_root_sha256" else execution_sha;checks["REVIEW_"+key.upper()]=review.get(root_key)==expected and review.get("verdict")==verdict
  except (OSError,KeyError,TypeError,json.JSONDecodeError):checks["REVIEW_"+key.upper()]=False
 try:
  spec=a["bindings"]["user_authorization"];receipt=json.loads(rel(root,spec["path"]).read_bytes());checks["USER_AUTHORIZATION"]=receipt.get("schema_version")=="argo-ui-parity-user-authorization/v1" and receipt.get("authority_root_sha256")==authority_sha and receipt.get("message")==derived and receipt.get("message_sha256")==hashlib.sha256(derived.encode()).hexdigest() and receipt.get("approved_at")==a.get("approved_at") and a.get("user_approval_message")==receipt.get("message")
 except (OSError,KeyError,TypeError,json.JSONDecodeError):checks["USER_AUTHORIZATION"]=False
 errors=[k for k,v in checks.items() if not v];return {"approved":not errors,"checks":checks,"errors":errors}
def execution_root_sha(approval):
 value={key:approval.get("bindings",{}).get(key,{}).get("sha256") for key in EXECUTION_BINDING_KEYS}
 return hashlib.sha256(canonical(value)).hexdigest()
def authority_root_sha(approval):
 value={key:approval.get("bindings",{}).get(key,{}).get("sha256") for key in AUTHORITY_BINDING_KEYS}
 return hashlib.sha256(canonical(value)).hexdigest()
def derive_approval_text(approval,execution_root,authority_root):
 return f'I approve exactly one local zero-model DiscoveryWorld UI-parity run {approval.get("run_id")} for execution root {execution_root} and design SHA-256 {approval.get("bindings",{}).get("design",{}).get("sha256")}, limited to {approval.get("cells")} cells, {approval.get("steps_per_cell")} transitions per cell, a {approval.get("controller_hard_deadline_seconds")}-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.'
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
 work_path=esc(work);home=Path("/Users/um-yunsang");denied=[Path(ENGINE_REPO),home/".prime",home/".ssh",home/".aws",home/".config",home/".gnupg",home/".kube",home/".docker",home/".netrc",home/".env",home/".git-credentials",home/".npmrc",home/".pypirc",home/"Library/Keychains",home/"DeepVoice",home/"lgaimer9",home/".cache/argo-research/DeepVoice",Path(SOURCE_REPO),Path(INTERPRETER).resolve().parents[1]]
 deny_rules=" ".join(f'(subpath "{esc(value)}")' for value in denied)
 return f'(version 1)\n(deny default)\n(allow process-exec)\n(allow file-read*)\n(deny file-read* {deny_rules})\n(allow file-write* (subpath "{work_path}"))\n(allow file-write* (literal "/dev/null"))\n(allow sysctl-read)\n(allow mach-lookup)\n(allow ipc-posix-shm)\n(allow signal (target self))\n'
def write_sandbox_profile(work,bundle,source):
 path=Path(work)/"worker.sb"
 if not atomic_create(path,sandbox_profile(work,bundle,source).encode()):raise RuntimeError("SANDBOX_PROFILE_EXISTS")
 path.chmod(0o444);fsync_existing(path);return path
def build_argv(c,interpreter,episode,bundle,source,site_packages=None):
 prefix=[str(interpreter)]
 if site_packages is not None:prefix += ["-I","-S","-B",str(Path(bundle)/"bootstrap.py"),"worker",str(bundle),str(source),str(site_packages)]
 else:prefix += [str(episode)]
 return prefix+["--run-id",EXPECTED_RUN_ID,"--cell-id",c["cell_id"],"--cell-nonce",c["cell_nonce"],"--scenario",c["scenario"],"--difficulty",c["difficulty"],"--seed",str(c["seed"]),"--mode",c["mode"],"--repeat",str(c["repeat"]),"--steps","1000","--thread-id",str(c["thread_id"]),"--source-commit",SOURCE_COMMIT,"--source-tree",SOURCE_TREE,"--source-archive-sha256",SOURCE_ARCHIVE_SHA,"--adapter-sha256",sha(Path(bundle)/"adapter_v2.py"),"--state-projection-sha256",sha(Path(bundle)/"state_projection.py"),"--environment-content-sha256",sha(Path(bundle)/"environment-content-manifest.json"),"--bootstrap-sha256",sha(Path(bundle)/"bootstrap.py"),"--frame-directory",str(Path(c["workdir"])/"frames"),"--ui-fd","{UI_FD}","--event-fd","{EVENT_FD}"]

def group_exists(pgid):
 try:os.killpg(pgid,0);return True
 except ProcessLookupError:return False
 except PermissionError:return True
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
class GlobalDeadlineError(RuntimeError):pass
class ManagedSignalError(RuntimeError):pass
def managed_run(argv,cwd,env,stdout_path,stderr_path,event_path,timeout,remaining=None,on_spawn=None,ui_path=None,absolute_deadline=None,control_latch=None,clock=time.monotonic):
 cwd=Path(cwd);cwd.mkdir(parents=True,exist_ok=True);(cwd/"tmp").mkdir(exist_ok=True);paths=[Path(stdout_path),Path(stderr_path),Path(event_path)]+([Path(ui_path)] if ui_path is not None else [])
 for path in paths:path.parent.mkdir(parents=True,exist_ok=True)
 flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fds=[];identities={};started=clock();proc=None;pgid=None;failure=None;result=None;owns_latch=control_latch is None;local_latch=control_latch or ControllerSignalLatch()
 if owns_latch:local_latch.install()
 if absolute_deadline is None:absolute_deadline=started+(remaining if remaining is not None else timeout)
 try:
  if clock()>=absolute_deadline:raise GlobalDeadlineError("GLOBAL_DEADLINE_BEFORE_FD")
  for path in paths:
   fd=os.open(path,flags,0o600);fds.append(fd);st=os.fstat(fd);identities[str(path)]={"device":st.st_dev,"inode":st.st_ino,"mode":stat.S_IFMT(st.st_mode)}
  if local_latch.pending is not None:raise ManagedSignalError("CONTROLLER_SIGNAL_BEFORE_SPAWN")
  command=[str(fds[2]) if x=="{EVENT_FD}" else str(fds[3]) if x=="{UI_FD}" else x for x in argv]
  if clock()>=absolute_deadline:raise GlobalDeadlineError("GLOBAL_DEADLINE_BEFORE_SPAWN")
  proc=subprocess.Popen(command,cwd=cwd,env=env,stdout=fds[0],stderr=fds[1],pass_fds=tuple(fds[2:]),start_new_session=True,close_fds=True);pgid=proc.pid;observed=os.getpgid(proc.pid)
  if observed!=pgid:raise RuntimeError("UNEXPECTED_PROCESS_GROUP")
  if local_latch.pending is not None:raise ManagedSignalError("CONTROLLER_SIGNAL_AFTER_SPAWN")
  if clock()>=absolute_deadline:raise GlobalDeadlineError("GLOBAL_DEADLINE_AFTER_SPAWN")
  try:
   if on_spawn:on_spawn(proc.pid,pgid)
  except BaseException as exc:
   if terminate_group(proc,pgid):raise RuntimeError("UNREAPED_ON_SPAWN") from exc
   raise RuntimeError("ON_SPAWN_FAILURE") from exc
  cell_deadline=started+timeout;end=min(cell_deadline,absolute_deadline);timed=False;unreaped=False;global_deadline=False;controller_signal=None
  while True:
   if local_latch.pending is not None:
    controller_signal=local_latch.pending;unreaped=terminate_group(proc,pgid);code=130;break
   now=clock()
   if now>=end:
    global_deadline=absolute_deadline<=cell_deadline;timed=not global_deadline;unreaped=terminate_group(proc,pgid);code=124;break
   try:
    code=proc.wait(timeout=min(0.1,end-now))
    if clock()>end:
     global_deadline=absolute_deadline<=cell_deadline;timed=not global_deadline;code=124
    break
   except subprocess.TimeoutExpired:continue
  if group_exists(pgid):unreaped=terminate_group(proc,pgid) or True
  result={"exit_code":code,"timed_out":timed,"global_deadline":global_deadline,"controller_signal":controller_signal,"unreaped":unreaped,"duration_seconds":round(clock()-started,6),"pid":proc.pid,"pgid":pgid,"output_identities":identities}
 except BaseException as exc:
  failure=exc;target=pgid or (proc.pid if proc is not None else None)
  if proc is not None and target is not None and terminate_group(proc,target):failure=RuntimeError("UNREAPED_AFTER_EXCEPTION")
 finally:
  durability=[]
  for fd in fds:
   try:os.fsync(fd)
   except OSError as exc:durability.append(exc)
   try:os.close(fd)
   except OSError as exc:durability.append(exc)
  if result is not None and local_latch.pending is not None:result["controller_signal"]=result.get("controller_signal") or local_latch.pending
  if owns_latch:local_latch.restore()
 if failure is not None:
  try:setattr(failure,"output_identities",identities)
  except (AttributeError,TypeError):pass
  raise failure
 if durability:
  error=OSError("SIDECAR_FSYNC_OR_CLOSE_FAILURE");error.output_identities=identities;error.unreaped=bool(result and result.get("unreaped"));raise error from durability[0]
 return result

def path_entry_exists(path):
 try:os.lstat(path);return True
 except FileNotFoundError:return False
def secure_read_bytes(path,identity):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  st=os.fstat(fd)
  if not stat.S_ISREG(st.st_mode) or st.st_dev!=identity["device"] or st.st_ino!=identity["inode"]:raise RuntimeError("OUTPUT_INODE_DRIFT")
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def copy_bound_output(src,dest,identities,writer=None):
 identity=identities.get(str(Path(src)))
 if identity is None:raise RuntimeError("OUTPUT_IDENTITY_MISSING")
 data=secure_read_bytes(src,identity)
 if writer is not None:writer(dest,data)
 elif not atomic_create(dest,data):raise FileExistsError(dest)
def classify_failure(run,exc):
 if isinstance(run,dict) and run.get("unreaped") is True or getattr(exc,"unreaped",False) is True or str(exc) in {"UNREAPED_ON_SPAWN","UNREAPED_AFTER_EXCEPTION"}:return "unreaped"
 if isinstance(exc,GlobalDeadlineError):return "global_deadline"
 if isinstance(exc,(KeyboardInterrupt,ManagedSignalError)):return "controller_signal"
 if str(exc)=="ON_SPAWN_FAILURE":return "ledger_error"
 if isinstance(exc,FileNotFoundError):return "spawn_failure"
 return "sidecar_error"
def file_meta(path):
 p=Path(path);return {"path":str(p),"size":p.stat().st_size,"sha256":sha(p)}
def open_frame_directory(path):
 path=Path(path);path.mkdir();flags=os.O_RDONLY
 if hasattr(os,"O_DIRECTORY"):flags|=os.O_DIRECTORY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags);st=os.fstat(fd);return fd,{"device":st.st_dev,"inode":st.st_ino}
def frame_manifest(frame_dir,frame_fd,identity):
 path=Path(frame_dir);current=path.lstat();
 if path.is_symlink() or current.st_dev!=identity["device"] or current.st_ino!=identity["inode"]:raise RuntimeError("FRAME_DIRECTORY_DRIFT")
 files=[];flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 for name in sorted(os.listdir(frame_fd)):
  st=os.stat(name,dir_fd=frame_fd,follow_symlinks=False)
  if not stat.S_ISREG(st.st_mode):raise RuntimeError("FRAME_ENTRY_NOT_REGULAR")
  fd=os.open(name,flags,dir_fd=frame_fd)
  try:
   fst=os.fstat(fd)
   if fst.st_dev!=st.st_dev or fst.st_ino!=st.st_ino:raise RuntimeError("FRAME_INODE_DRIFT")
   digest=hashlib.sha256();size=0
   while True:
    chunk=os.read(fd,1048576)
    if not chunk:break
    digest.update(chunk);size+=len(chunk)
   files.append({"path":name,"size":size,"sha256":digest.hexdigest()})
  finally:os.close(fd)
 return {"files":files,"count":len(files),"bytes":sum(x["size"] for x in files)}

def revalidate_complete_cells(manifest,cell_results,root,source,bundle,sealed_interpreter,sealed_site_packages,artifact_reader=None):
 closed={}
 for cell in manifest["ordered_cells"]:
  prior=cell_results.get(cell["cell_id"])
  if prior is None:continue
  value=dict(prior)
  if prior.get("status")=="valid_complete":
   try:
    frame_path=rel(root,cell["frame_manifest_path"]);frames=json.loads(artifact_reader(str(frame_path)) if artifact_reader is not None else frame_path.read_bytes());runtime_cell={**cell,"workdir":prior["runtime_workdir"]};validation=validate_cell(runtime_cell,prior["run"],rel(root,cell["event_path"]),rel(root,cell["ui_gzip_path"]),frames,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_archive_sha256=SOURCE_ARCHIVE_SHA,adapter_sha256=sha(bundle/"adapter_v2.py"),state_projection_sha256=sha(bundle/"state_projection.py"),environment_content_sha256=sha(bundle/"environment-content-manifest.json"),bootstrap_sha256=sha(bundle/"bootstrap.py"),interpreter_path=sealed_interpreter,site_packages=sealed_site_packages,source_root=source,bundle_root=bundle,artifact_reader=artifact_reader);value.update({"status":validation["status"],"errors":validation.get("errors",[]),"ui_hashes":validation.get("ui_hashes",[]),"pre_state_hashes":validation.get("pre_state_hashes",[]),"post_state_hashes":validation.get("post_state_hashes",[]),"event_sha256":validation.get("event_sha256"),"ui_gzip_sha256":validation.get("ui_gzip_sha256")})
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
   if not str(target).startswith(str(source.resolve())+os.sep) or not (m.isfile() or m.isdir()):raise RuntimeError("UNSAFE_ARCHIVE")
  t.extractall(source,filter="data")
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
  expected={"run.py":approval["bindings"]["runner"]["sha256"],"episode.py":approval["bindings"]["episode"]["sha256"],"adapter_v2.py":approval["bindings"]["adapter"]["sha256"],"state_projection.py":approval["bindings"]["state_projection"]["sha256"],"lifecycle.py":approval["bindings"]["lifecycle"]["sha256"],"protocol.py":approval["bindings"]["protocol"]["sha256"],"schemas.json":approval["bindings"]["schemas"]["sha256"],"manifest.json":approval["bindings"]["manifest"]["sha256"],"proposal.json":approval["bindings"]["proposal"]["sha256"],"design.json":approval["bindings"]["design"]["sha256"],"environment_manifest.py":approval["bindings"]["environment_manifest_module"]["sha256"],"environment-content-manifest.json":approval["bindings"]["environment_content_manifest"]["sha256"],"bootstrap.py":approval["bindings"]["bootstrap"]["sha256"],"approval.json":hashlib.sha256(approval_bytes).hexdigest()}
  if any(not (bundle/name).is_file() or sha(bundle/name)!=digest for name,digest in expected.items()):return False
  return sha(source/"discoveryworld/DiscoveryWorldAPI.py")==API_SOURCE_SHA and sha(source/"discoveryworld/UserInterface.py")==UI_SOURCE_SHA
 except (OSError,KeyError,TypeError):return False
def sealed_controller_identity(approval,approval_bytes):
 try:
  root=Path(os.environ["ARGO_UI_PARITY_CONTROLLER_SEAL"]).resolve()
  if root!=HERE:return False
  seal_bytes=(root/"seal.json").read_bytes()
  if hashlib.sha256(seal_bytes).hexdigest()!=os.environ["ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256"]:return False
  seal=json.loads(seal_bytes);expected={"run.py":approval["bindings"]["runner"]["sha256"],"lifecycle.py":approval["bindings"]["lifecycle"]["sha256"],"protocol.py":approval["bindings"]["protocol"]["sha256"],"episode.py":approval["bindings"]["episode"]["sha256"],"adapter_v2.py":approval["bindings"]["adapter"]["sha256"],"state_projection.py":approval["bindings"]["state_projection"]["sha256"],"schemas.json":approval["bindings"]["schemas"]["sha256"],"manifest.json":approval["bindings"]["manifest"]["sha256"],"environment_manifest.py":approval["bindings"]["environment_manifest_module"]["sha256"],"environment-content-manifest.json":approval["bindings"]["environment_content_manifest"]["sha256"],"bootstrap.py":approval["bindings"]["bootstrap"]["sha256"],"launcher.py":approval["bindings"]["launcher"]["sha256"],"approval.json":hashlib.sha256(approval_bytes).hexdigest()}
  module_roots={Path(environment_manifest_module.__file__).resolve().parent,Path(lifecycle_module.__file__).resolve().parent,Path(protocol_module.__file__).resolve().parent}
  return module_roots=={HERE} and seal.get("files")==expected and all((root/name).is_file() and sha(root/name)==digest for name,digest in expected.items())
 except (OSError,KeyError,TypeError,json.JSONDecodeError):return False
def sealed_runtime_identity(manifest,copied):
 try:return all(verify_root(spec,copied[spec["name"]]) for spec in manifest["roots"])
 except (OSError,KeyError,TypeError):return False
def preflight_identity_record(approval):
 return {"controller_seal_sha256":os.environ.get("ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256"),"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"interpreter_sha256":sha(INTERPRETER),"controller_interpreter_sha256":sha(sys.executable),"uv_sha256":sha(UV),"sandbox_exec_sha256":sha(SANDBOX_EXEC),"environment_freeze_sha256":ENV_FREEZE_SHA,"environment_content_aggregate_sha256":approval["environment_content_aggregate_sha256"],"bindings":{key:value["sha256"] for key,value in sorted(approval["bindings"].items())}}
def result_bytes(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n"
class ControllerSignalLatch:
 SIGNALS=(signal.SIGINT,signal.SIGTERM,signal.SIGHUP)
 def __init__(self):self.pending=None;self.previous={};self.previous_mask=None
 def handler(self,signum,frame):self.pending=self.pending or signum
 def install(self):
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,set(self.SIGNALS))
  try:
   for sig in self.SIGNALS:self.previous[sig]=signal.getsignal(sig);signal.signal(sig,self.handler)
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,prior)
 def block_for_closure(self):self.previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,set(self.SIGNALS))
 def closure_pending(self):return self.pending is not None or bool(set(signal.sigpending())&set(self.SIGNALS))
 def restore(self):
  if self.previous_mask is not None:signal.pthread_sigmask(signal.SIG_SETMASK,self.previous_mask);self.previous_mask=None
  for sig,handler in self.previous.items():signal.signal(sig,handler)
def _main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);args=p.parse_args();root=Path.cwd();approval_bytes=args.approval.read_bytes();approval_sha=hashlib.sha256(approval_bytes).hexdigest();approval=json.loads(approval_bytes);check=validate_approval(approval,root)
 if not check["approved"]:
  value={"status":"BLOCKED_BEFORE_CONSUMPTION","approval":check,"cells_planned":0,"cells_spawned":0,"model_calls":0,"spend_usd":0.0};print(json.dumps(value,indent=2,sort_keys=True));return 2
 if not sealed_controller_identity(approval,approval_bytes):raise RuntimeError("UNSEALED_CONTROLLER")
 manifest_path=rel(root,approval["bindings"]["manifest"]["path"]);manifest_bytes=manifest_path.read_bytes();manifest_sha=hashlib.sha256(manifest_bytes).hexdigest();manifest=json.loads(manifest_bytes);mcheck=validate_manifest(manifest)
 if not mcheck["passed"]:raise RuntimeError("MANIFEST_INVALID")
 if args.out.resolve()!=rel(root,manifest["paths"]["result"]).resolve():raise RuntimeError("RESULT_PATH_MISMATCH")
 pre=preflight_paths(manifest,root)
 if not pre["passed"]:raise RuntimeError("OUTPUT_COLLISION:"+str(pre["errors"]))
 if freeze_sha()!=ENV_FREEZE_SHA or not source_repo_identity():raise RuntimeError("PREFLIGHT_ENVIRONMENT_IDENTITY")
 with tempfile.TemporaryDirectory(prefix="dw-ui-parity-sealed-") as td:
  temp=Path(td);source=prepare_snapshot(temp);bundle=temp/"bundle";bundle.mkdir()
  for name in ["run.py","episode.py","adapter_v2.py","state_projection.py","lifecycle.py","protocol.py","schemas.json","manifest.json","environment_manifest.py","environment-content-manifest.json","bootstrap.py","approval.json","proposal.json","design.json"]:
   if name=="manifest.json":data=manifest_bytes
   elif name=="approval.json":data=approval_bytes
   elif name=="proposal.json":data=rel(root,approval["bindings"]["proposal"]["path"]).read_bytes()
   elif name=="design.json":data=rel(root,approval["bindings"]["design"]["path"]).read_bytes()
   else:data=(HERE/name).read_bytes()
   target=bundle/name;target.write_bytes(data);target.chmod(0o444);fsync_existing(target)
  fsync_existing(bundle);bundle.chmod(0o555)
  environment_manifest=json.loads((HERE/"environment-content-manifest.json").read_bytes());copied_runtime=copy_and_verify(environment_manifest,temp/"runtime");sealed_interpreter=copied_runtime["base_python"]/"bin/python3.11";sealed_site_packages=copied_runtime["site_packages"]
  if not sealed_runtime_identity(environment_manifest,copied_runtime):raise RuntimeError("SEALED_RUNTIME_IDENTITY")
  if args.approval.read_bytes()!=approval_bytes or manifest_path.read_bytes()!=manifest_bytes:raise RuntimeError("AUTHORITY_TOCTOU_BEFORE_CONSUMPTION")
  if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source) or not sealed_runtime_identity(environment_manifest,copied_runtime):raise RuntimeError("BYTE_IDENTITY_BEFORE_CONSUMPTION")
  preflight_identity_sha=hashlib.sha256(canonical(preflight_identity_record(approval))).hexdigest();execution_root_value=execution_root_sha(approval)
  signal_latch=ControllerSignalLatch();signal_latch.install()
  if signal_latch.pending is not None:signal_latch.restore();return 130
  receipts_root=root/"paper/research/receipts";artifacts=ArtifactNamespace(receipts_root)
  def artifact_name(path):return Path(path).resolve().relative_to(receipts_root.resolve()).as_posix()
  def pinned_reader(path):return artifacts.read_bytes(artifact_name(path))
  marker=rel(root,manifest["paths"]["marker"]);ledger=rel(root,manifest["paths"]["ledger"]);side_root=rel(root,manifest["paths"]["sidecar_root"]);result_path=rel(root,manifest["paths"]["result"]);result_temp=rel(root,manifest["paths"]["result_temp"]);marker_name=artifact_name(marker);ledger_name=artifact_name(ledger);side_name=artifact_name(side_root);result_name=artifact_name(result_path);result_temp_name=artifact_name(result_temp);consumed_at=__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds");marker_value={"schema_version":"argo-ui-parity-marker/v1","run_id":EXPECTED_RUN_ID,"approval_sha256":approval_sha,"manifest_sha256":manifest_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"execution_root_sha256":execution_root_value,"consumed_at":consumed_at}
  artifacts.create_bytes(marker_name,canonical(marker_value)+b"\n");artifacts.ensure_dir(side_name);previous=artifacts.append_record(ledger_name,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":EXPECTED_RUN_ID,"manifest_sha256":manifest_sha,"approval_sha256":approval_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"execution_root_sha256":execution_root_value,"started_at":consumed_at});seq=0;deadline=time.monotonic()+manifest["budgets"]["controller_hard_deadline_seconds"];cell_results={};controller_error=None
  for cell in manifest["ordered_cells"]:
   if signal_latch.pending is not None:controller_error="CONTROLLER_SIGNAL_"+str(signal_latch.pending);break
   if time.monotonic()>=deadline:controller_error="GLOBAL_DEADLINE";break
   if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source):controller_error="RUNTIME_IDENTITY_DRIFT";break
   if signal_latch.pending is not None:controller_error="CONTROLLER_SIGNAL_"+str(signal_latch.pending);break
   if time.monotonic()>=deadline:controller_error="GLOBAL_DEADLINE";break
   new_seq=seq+1;new_previous=artifacts.append_record(ledger_name,{"event":"planned","sequence":new_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=new_seq,new_previous
   work=temp/cell["workdir"];frame=work/"frames";event=rel(root,cell["event_path"]);ui_gz=rel(root,cell["ui_gzip_path"]);stdout=rel(root,cell["stdout_path"]);stderr=rel(root,cell["stderr_path"]);temp_event=work/"events.ndjson";temp_ui_gz=work/"ui.ndjson.gz";temp_stdout=work/"stdout.bin";temp_stderr=work/"stderr.bin";runtime_cell={**cell,"workdir":str(work),"event_path":str(temp_event),"ui_gzip_path":str(temp_ui_gz)};worker_argv=None;profile=None;argv=None;run=None;frame_fd=None;frame_identity=None;spawned_durable=False
   def spawned(pid,pgid,cell=cell):
    nonlocal seq,previous,spawned_durable
    candidate_seq=seq+1;candidate_previous=artifacts.append_record(ledger_name,{"event":"spawned","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"pid":pid,"pgid":pgid,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous;spawned_durable=True
   fm_path=rel(root,cell["frame_manifest_path"])
   try:
    if signal_latch.pending is not None:raise ManagedSignalError("CONTROLLER_SIGNAL_"+str(signal_latch.pending))
    if time.monotonic()>=deadline:raise GlobalDeadlineError("GLOBAL_DEADLINE_BEFORE_SETUP")
    frame_fd,frame_identity=open_frame_directory(frame)
    worker_argv=build_argv(runtime_cell,sealed_interpreter,bundle/"episode.py",bundle,source,sealed_site_packages);profile=write_sandbox_profile(work,bundle,source);argv=[SANDBOX_EXEC,"-f",str(profile),*worker_argv]
    run=managed_run(argv,work,sanitized_env(bundle,source,sealed_site_packages,work),temp_stdout,temp_stderr,temp_event,cell["timeout_seconds"],on_spawn=spawned,ui_path=temp_ui_gz,absolute_deadline=deadline,control_latch=signal_latch)
    for src,dest in [(temp_stdout,stdout),(temp_stderr,stderr),(temp_event,event),(temp_ui_gz,ui_gz)]:
     if path_entry_exists(src):copy_bound_output(src,dest,run["output_identities"],lambda path,data:artifacts.create_bytes(artifact_name(path),data))
    frames=frame_manifest(frame,frame_fd,frame_identity);os.close(frame_fd);frame_fd=None;artifacts.create_bytes(artifact_name(fm_path),json.dumps(frames,ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n");validation=validate_cell(runtime_cell,run,event,ui_gz,frames,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_archive_sha256=SOURCE_ARCHIVE_SHA,adapter_sha256=sha(bundle/"adapter_v2.py"),state_projection_sha256=sha(bundle/"state_projection.py"),environment_content_sha256=sha(bundle/"environment-content-manifest.json"),bootstrap_sha256=sha(bundle/"bootstrap.py"),interpreter_path=sealed_interpreter,site_packages=sealed_site_packages,source_root=source,bundle_root=bundle,artifact_reader=pinned_reader);status="unreaped" if run["unreaped"] else "global_deadline" if run.get("global_deadline") else "controller_signal" if run.get("controller_signal") is not None else validation["status"]
    if run.get("controller_signal") is not None:controller_error="CONTROLLER_SIGNAL_"+str(run["controller_signal"])
   except BaseException as exc:
    salvage_errors=[]
    if frame_fd is not None:
     try:os.close(frame_fd)
     except OSError as frame_close:salvage_errors.append(type(frame_close).__name__)
     frame_fd=None
    failure_identities=getattr(exc,"output_identities",{})
    for src,dest in [(temp_stdout,stdout),(temp_stderr,stderr),(temp_event,event),(temp_ui_gz,ui_gz)]:
     if path_entry_exists(src) and artifact_name(dest) not in artifacts.files:
      try:copy_bound_output(src,dest,failure_identities,lambda path,data:artifacts.create_bytes(artifact_name(path),data))
      except (OSError,RuntimeError) as salvage:salvage_errors.append(type(salvage).__name__)
    unreaped_before=isinstance(run,dict) and run.get("unreaped") is True;run={"exit_code":None,"timed_out":False,"global_deadline":False,"unreaped":unreaped_before,"duration_seconds":0};frames={"files":[],"count":0,"bytes":0};validation={"status":classify_failure({"unreaped":unreaped_before},exc),"errors":[type(exc).__name__,*salvage_errors]};status=validation["status"];controller_error=type(exc).__name__+("+SALVAGE:"+",".join(salvage_errors) if salvage_errors else "")
   metas={k:artifacts.metadata(artifact_name(path)) for k,path in [("stdout",stdout),("stderr",stderr),("events",event),("ui_gzip",ui_gz)] if artifact_name(path) in artifacts.files};fm_meta=artifacts.metadata(artifact_name(fm_path)) if artifact_name(fm_path) in artifacts.files else {};new_seq=seq+1;new_previous=artifacts.append_record(ledger_name,{"event":"finished","sequence":new_seq,"run_id":EXPECTED_RUN_ID,"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":cell["index"],"status":status,"exit_code":run.get("exit_code"),"timed_out":run.get("timed_out"),"stdout":metas.get("stdout",{}),"stderr":metas.get("stderr",{}),"events":metas.get("events",{}),"ui_gzip":metas.get("ui_gzip",{}),"frame_manifest":fm_meta,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=new_seq,new_previous;cell_results[cell["cell_id"]]={"status":status,"errors":validation.get("errors",[]),"ui_hashes":validation.get("ui_hashes",[]),"pre_state_hashes":validation.get("pre_state_hashes",[]),"post_state_hashes":validation.get("post_state_hashes",[]),"run":run,"sidecars":metas,"frame_manifest":frames,"runtime_workdir":str(work),"event_sha256":validation.get("event_sha256"),"ui_gzip_sha256":validation.get("ui_gzip_sha256")};shutil.rmtree(work,ignore_errors=True)
   if signal_latch.pending is not None:controller_error=controller_error or "CONTROLLER_SIGNAL_"+str(signal_latch.pending)
   sidecar_bytes=sum(os.fstat(fd).st_size for name,fd in artifacts.files.items() if name.startswith(side_name+"/"))
   if sidecar_bytes>manifest["budgets"]["sidecar_total_bytes_max"]:controller_error="SIDECAR_DISK_BUDGET"
   if time.monotonic()>=deadline:controller_error=controller_error or "GLOBAL_DEADLINE"
   if controller_error or status in {"unreaped","sidecar_error","ledger_error","global_deadline","controller_signal"}:break
  cell_results=revalidate_complete_cells(manifest,cell_results,root,source,bundle,sealed_interpreter,sealed_site_packages,pinned_reader)
  mode=[{**pair,"status":compare_pair(cell_results.get(pair["official"],{}),cell_results.get(pair["ui_only"],{}))} for pair in manifest["mode_pairs"]];ui_pairs=[{**pair,"status":compare_pair(cell_results.get(pair["left"],{}),cell_results.get(pair["right"],{}))} for pair in manifest["ui_repeat_pairs"]];statuses=[cell_results[cell["cell_id"]]["status"] for cell in manifest["ordered_cells"] if cell["cell_id"] in cell_results];pair_statuses=[pair["status"] for pair in mode+ui_pairs]
  if signal_latch.pending is not None:controller_error=controller_error or "CONTROLLER_SIGNAL_"+str(signal_latch.pending)
  if not runtime_identity(approval,root,args.approval,approval_bytes,manifest_path,manifest_bytes,bundle,source) or not sealed_runtime_identity(environment_manifest,copied_runtime):controller_error=controller_error or "FINAL_RUNTIME_IDENTITY_DRIFT"
  if time.monotonic()>=deadline:controller_error=controller_error or "FINAL_GLOBAL_DEADLINE"
  expected_header={"manifest_sha256":manifest_sha,"approval_sha256":approval_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"execution_root_sha256":execution_root_value};preledger=validate_ledger(ledger,manifest,allow_partial=True,expected_header=expected_header,strict_sidecars=True,artifact_root=root,ledger_bytes=artifacts.read_bytes(ledger_name),artifact_reader=pinned_reader)
  if not preledger["passed"]:controller_error=controller_error or "LEDGER_INVALID"
  if not artifacts.verify():controller_error=controller_error or "ARTIFACT_NAMESPACE_DRIFT"
  signal_latch.block_for_closure()
  if signal_latch.closure_pending():controller_error=controller_error or "CONTROLLER_SIGNAL_BEFORE_CLOSURE"
  status=final_status(statuses,pair_statuses,30)
  if controller_error:status="INCOMPLETE" if len(statuses)<30 else "INVALID"
  if controller_error:
   candidate_seq=seq+1;candidate_previous=artifacts.append_record(ledger_name,{"event":"controller_stop","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"reason":controller_error,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous
  result={"schema_version":"argo-discoveryworld-ui-parity-result/v1","run_id":EXPECTED_RUN_ID,"status":status,"approval_sha256":approval_sha,"manifest_sha256":manifest_sha,"source_archive_sha256":SOURCE_ARCHIVE_SHA,"preflight_identity_sha256":preflight_identity_sha,"execution_root_sha256":execution_root_value,"cells":cell_results,"mode_pairs":mode,"ui_repeat_pairs":ui_pairs,"summary":{"cells_planned":len(statuses),"valid_complete":sum(x=="valid_complete" for x in statuses),"mode_exact":sum(x["status"]=="EXACT" for x in mode),"mode_mismatch":sum(x["status"]=="OBSERVED_MISMATCH" for x in mode),"mode_unobservable":sum(x["status"]=="UNOBSERVABLE" for x in mode),"ui_repeat_exact":sum(x["status"]=="EXACT" for x in ui_pairs),"controller_error":controller_error},"ledger_last_record_sha256_before_final":previous,"model_calls":0,"spend_usd":0.0};payload=result_bytes(result);payload_sha=hashlib.sha256(payload).hexdigest()
  artifacts.create_bytes(result_temp_name,payload)
  candidate_seq=seq+1;candidate_previous=artifacts.append_record(ledger_name,{"event":"finalized","sequence":candidate_seq,"run_id":EXPECTED_RUN_ID,"status":status,"result_sha256":payload_sha,"timestamp":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")},previous);seq,previous=candidate_seq,candidate_previous
  closed=validate_ledger(ledger,manifest,allow_partial=status=="INCOMPLETE",expected_header=expected_header,strict_sidecars=True,result_payload_path=result_temp,artifact_root=root,ledger_bytes=artifacts.read_bytes(ledger_name),artifact_reader=pinned_reader)
  if not closed["passed"] or not closed["finalized"]:raise RuntimeError("CLOSED_LEDGER_INVALID:"+str(closed["errors"]))
  pending_stat=os.fstat(artifacts.files[result_temp_name]);published_stat=artifacts.publish(result_temp_name,result_name)
  if (pending_stat.st_dev,pending_stat.st_ino)!=(published_stat.st_dev,published_stat.st_ino) or hashlib.sha256(artifacts.read_bytes(result_name)).hexdigest()!=payload_sha or not artifacts.verify():
   try:artifacts.remove(result_name)
   except OSError:pass
   raise RuntimeError("PUBLISHED_RESULT_OR_NAMESPACE_BINDING")
  signal_latch.restore();artifacts.close()
  try:print(json.dumps({"status":status,"summary":result["summary"]},indent=2,sort_keys=True))
  except OSError:pass
  return 0 if status=="PASS" else 1
def write_abort_receipt(root,exc):
 root=Path(root);marker=root/MARKER_REL;abort=root/ABORT_REL;canonical_result=root/"paper/research/receipts/discoveryworld-ui-parity-v1-result.json"
 if not marker.is_file() or canonical_result.exists():return False
 value={"schema_version":"argo-ui-parity-controller-abort/v1","status":"CONTROLLER_ABORT","error_type":type(exc).__name__,"error":str(exc),"marker_sha256":sha(marker),"canonical_result_exists":False,"recorded_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")}
 pending=root/ABORT_PENDING_REL
 if not atomic_create(pending,canonical(value)+b"\n"):return False
 publish_exclusive(pending,abort);return True
def main():
 try:return _main()
 except BaseException as exc:
  try:write_abort_receipt(Path.cwd(),exc)
  except BaseException:pass
  print(json.dumps({"status":"CONTROLLER_ABORT","error_type":type(exc).__name__},sort_keys=True));return 1
if __name__=="__main__":raise SystemExit(main())
