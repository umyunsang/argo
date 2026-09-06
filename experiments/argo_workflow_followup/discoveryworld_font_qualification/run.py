#!/usr/bin/env python3
"""One-shot two-cell DiscoveryWorld font-registry qualification controller."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,signal,stat,subprocess,sys,tarfile,tempfile,time
from pathlib import Path
import environment_manifest as environment_manifest_module
import font_registry as font_registry_module
import process_control as process_control_module
import protocol as protocol_module
from environment_manifest import copy_and_verify,verify_root
from font_registry import source_identity,validate_manifest
from process_control import run_process
from protocol import compare,validate_event
HERE=Path(__file__).resolve().parent
ENGINE=Path("/Users/um-yunsang/argo-paper-orx");SOURCE=Path("/Users/um-yunsang/.cache/argo-research/DiscoveryWorld");INTERPRETER=SOURCE/".venv/bin/python";SANDBOX=Path("/usr/bin/sandbox-exec")
RUN_ID="dw-font-registry-qual-20260906-v1";SOURCE_COMMIT="fd591323920be0d3786ef350955de1945aa571e5";SOURCE_TREE="e83be66c3f357352e8d5d68755100cbc8fdc4d11";SOURCE_ARCHIVE="0dafdd25b5a51892bd470dc20ea2fba4fc78abe2a986f20e4ce132f42b3ddb6a";SYSFONT_SHA="f3ea456b3dfbe017fb9134dc12a105e98375c0b8d482006b5b6f69f7a368c6c3"
EXEC_KEYS=("runner","episode","font_registry","protocol","process_control","manifest","font_manifest","environment_manifest","environment_content","bootstrap","launcher","result_verifier","admission_consumer")
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def fsync_path(path):
 fd=os.open(path,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def exclusive(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags,0o600)
 try:
  view=memoryview(data)
  while view:
   n=os.write(fd,view)
   if n<=0:raise OSError("write")
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 fsync_path(path.parent)
def atomic_publish(pending,final,data):
 exclusive(pending,data);os.replace(pending,final);fsync_path(Path(final).parent)
def append_ledger(path,record,previous):
 value=dict(record);value["previous_sha256"]=previous;value["record_sha256"]=hashlib.sha256(canonical(value)).hexdigest();line=canonical(value)+b"\n";flags=os.O_WRONLY|os.O_APPEND
 if not Path(path).exists():flags|=os.O_CREAT|os.O_EXCL
 fd=os.open(path,flags,0o600)
 try:os.write(fd,line);os.fsync(fd)
 finally:os.close(fd)
 return value["record_sha256"]
def stat_font(path):
 p=Path(path);lst=p.lstat();target=p.resolve();st=target.stat()
 if not stat.S_ISREG(st.st_mode):raise RuntimeError("FONT_TARGET_NOT_REGULAR")
 return {"path":str(p),"path_kind":"symlink" if p.is_symlink() else "regular","link_target":os.readlink(p) if p.is_symlink() else None,"resolved_target":str(target),"link_device":lst.st_dev,"link_inode":lst.st_ino,"link_mode":stat.S_IMODE(lst.st_mode),"device":st.st_dev,"inode":st.st_ino,"uid":st.st_uid,"gid":st.st_gid,"mode":stat.S_IMODE(st.st_mode),"size":st.st_size,"mtime_ns":st.st_mtime_ns,"sha256":sha(target)}
def profile(mode,work,sealed_python):
 esc=lambda p:str(Path(p).resolve()).replace("\\","\\\\").replace('"','\\"');home=Path("/Users/um-yunsang");denied=[ENGINE,SOURCE,home/".prime",home/".ssh",home/".aws",home/".config",home/".gnupg",home/".kube",home/".docker",home/".netrc",home/".env",home/".git-credentials",home/"Library/Keychains",home/"DeepVoice",home/"lgaimer9"]
 execs=[sealed_python] if mode=="pinned" else [sealed_python,Path("/usr/X11/bin/fc-list"),Path("/usr/X11R6/bin/fc-list"),Path("/opt/X11/bin/fc-list")];rules=" ".join(f'(literal "{p}")' for p in sorted({esc(x) for x in execs}));denies=" ".join(f'(subpath "{esc(p)}")' for p in denied);fork="" if mode=="pinned" else "(allow process-fork)"
 return f'(version 1)\n(deny default)\n(allow process-exec {rules})\n{fork}\n(allow file-read*)\n(deny file-read* {denies})\n(allow file-write* (subpath "{esc(work)}"))\n(allow file-write* (literal "/dev/null"))\n(allow sysctl-read)\n(allow mach-lookup)\n(allow ipc-posix-shm)\n(allow signal (target self))\n'
def proposal_core(value):
 v=dict(value);v.pop("required_approval_text",None);return hashlib.sha256(canonical(v)).hexdigest()
def execution_root(approval):return hashlib.sha256(canonical({k:approval.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS})).hexdigest()
def authority_root(approval,proposal):return hashlib.sha256(canonical({**{k:approval.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS},"design":approval.get("bindings",{}).get("design",{}).get("sha256"),"proposal_core":proposal_core(proposal)})).hexdigest()
def approval_text(a,er,ar):return f'I approve exactly one local zero-model DiscoveryWorld font-registry qualification run {RUN_ID} for execution root {er}, authority root {ar}, and design SHA-256 {a.get("bindings",{}).get("design",{}).get("sha256")}, limited to exactly two zero-scenario cells, a 120-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.'
def validate_approval(a,root):
 checks={"SCHEMA":a.get("schema_version")=="argo-font-qualification-approval/v1","STATUS":a.get("status")=="APPROVED" and a.get("approved_by")=="user","RUN":a.get("run_id")==RUN_ID,"REPO":Path(root).resolve()==ENGINE and a.get("engine_repo")==str(ENGINE),"SOURCE":a.get("source_commit")==SOURCE_COMMIT and a.get("source_tree")==SOURCE_TREE and a.get("source_archive_sha256")==SOURCE_ARCHIVE,"LIMITS":a.get("cells")==2 and a.get("scenario_loads")==0 and a.get("agent_observations")==0 and a.get("deadline_seconds")==120 and a.get("model_calls")==0 and a.get("docker_calls")==0 and a.get("api_spend_usd")==0.0,"TOOLS":a.get("interpreter")==str(INTERPRETER) and sha(INTERPRETER)==a.get("interpreter_sha256") and a.get("sandbox_exec")==str(SANDBOX) and sha(SANDBOX)==a.get("sandbox_exec_sha256") and Path(a.get("controller_interpreter","")).is_file() and sha(a["controller_interpreter"])==a.get("controller_interpreter_sha256")}
 for key,spec in a.get("bindings",{}).items():
  p=Path(root)/spec.get("path","");checks["BIND_"+key.upper()]=p.is_file() and sha(p)==spec.get("sha256")
 try:proposal=json.loads((Path(root)/a["bindings"]["proposal"]["path"]).read_bytes())
 except (OSError,KeyError,json.JSONDecodeError,TypeError):proposal={}
 er=execution_root(a);ar=authority_root(a,proposal);text=approval_text(a,er,ar);checks.update({"ROOTS":a.get("execution_root_sha256")==er and a.get("authority_root_sha256")==ar and a.get("proposal_core_sha256")==proposal_core(proposal),"TEXT":a.get("required_approval_text")==text and a.get("user_approval_message")==text and a.get("user_approval_message_sha256")==hashlib.sha256(text.encode()).hexdigest(),"PROPOSAL_TEXT":proposal.get("required_approval_text")==text})
 for key,verdict,rootkey in [("immutable_validation","PASS","execution_root_sha256"),("method_review","PASS","authority_root_sha256"),("runtime_review","PASS","execution_root_sha256"),("handoff_review","ACCEPT","authority_root_sha256")]:
  try:r=json.loads((Path(root)/a["bindings"][key]["path"]).read_bytes());checks["REVIEW_"+key.upper()]=r.get("verdict")==verdict and r.get(rootkey)==(ar if rootkey.startswith("authority") else er)
  except (OSError,KeyError,json.JSONDecodeError,TypeError):checks["REVIEW_"+key.upper()]=False
 try:u=json.loads((Path(root)/a["bindings"]["user_authorization"]["path"]).read_bytes());checks["USER_AUTHORIZATION"]=u.get("run_id")==RUN_ID and u.get("authority_root_sha256")==ar and u.get("message")==text and u.get("message_sha256")==hashlib.sha256(text.encode()).hexdigest()
 except (OSError,KeyError,json.JSONDecodeError,TypeError):checks["USER_AUTHORIZATION"]=False
 return {"approved":all(checks.values()),"checks":checks,"errors":[k for k,v in checks.items() if not v]}
def binding_snapshot(approval,root):return {key:sha(Path(root)/spec["path"]) for key,spec in sorted(approval["bindings"].items())}
def tree_digest(root):
 rows=[]
 for path in sorted(Path(root).rglob("*")):
  rel=path.relative_to(root).as_posix()
  if path.is_symlink():rows.append([rel,"symlink",os.readlink(path)])
  elif path.is_file():rows.append([rel,"file",sha(path)])
  elif path.is_dir():rows.append([rel,"dir"])
 return hashlib.sha256(canonical(rows)).hexdigest()
def prepare_source(temp):
 ident=source_identity(SOURCE)
 if not ident["clean"] or ident["commit"]!=SOURCE_COMMIT or ident["tree"]!=SOURCE_TREE:raise RuntimeError("SOURCE_IDENTITY")
 archive=Path(temp)/"source.tar"
 with archive.open("wb") as out:r=subprocess.run(["git","-C",str(SOURCE),"archive","--format=tar",SOURCE_COMMIT],stdout=out,stderr=subprocess.PIPE,check=False)
 if r.returncode or sha(archive)!=SOURCE_ARCHIVE:raise RuntimeError("SOURCE_ARCHIVE")
 target=Path(temp)/"source";target.mkdir()
 with tarfile.open(archive) as tf:
  for member in tf.getmembers():
   p=(target/member.name).resolve()
   if not str(p).startswith(str(target.resolve())+os.sep) or not (member.isfile() or member.isdir()):raise RuntimeError("UNSAFE_ARCHIVE")
  tf.extractall(target,filter="data")
 for p in sorted(target.rglob("*"),reverse=True):p.chmod(0o555 if p.is_dir() else 0o444)
 target.chmod(0o555);return target
class SignalLatch:
 def __init__(self):self.pending=None;self.old={}
 def handler(self,signum,frame):self.pending=self.pending or signum
 def install(self):
  for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):self.old[sig]=signal.getsignal(sig);signal.signal(sig,self.handler)
 def restore(self):
  for sig,value in self.old.items():signal.signal(sig,value)
def sanitized(bundle,source,site,work):return {"HOME":str(work),"TMPDIR":str(work/"tmp"),"PATH":"/usr/bin:/bin:/opt/homebrew/bin:/usr/X11/bin","PYTHONNOUSERSITE":"1","PYTHONHASHSEED":"0","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy","LC_ALL":"C.UTF-8","TZ":"UTC","PYTHONDONTWRITEBYTECODE":"1"}
def sealed_controller_identity(approval):
 try:
  root=Path(os.environ["ARGO_FONT_CONTROLLER_SEAL"]).resolve();seal_path=root/"seal.json";seal_bytes=seal_path.read_bytes()
  if root!=HERE or hashlib.sha256(seal_bytes).hexdigest()!=os.environ["ARGO_FONT_CONTROLLER_SEAL_SHA256"]:return False
  seal=json.loads(seal_bytes);expected={"run.py":"runner","episode.py":"episode","font_registry.py":"font_registry","protocol.py":"protocol","process_control.py":"process_control","manifest.json":"manifest","font-manifest.json":"font_manifest","environment_manifest.py":"environment_manifest","environment-content-manifest.json":"environment_content","bootstrap.py":"bootstrap","launcher.py":"launcher","verify_result.py":"result_verifier","admit_result.py":"admission_consumer"}
  return {Path(module.__file__).resolve().parent for module in [environment_manifest_module,font_registry_module,process_control_module,protocol_module]}=={root} and seal.get("execution_root_sha256")==execution_root(approval) and all((root/name).is_file() and sha(root/name)==approval["bindings"][key]["sha256"] for name,key in expected.items())
 except (OSError,KeyError,json.JSONDecodeError):return False
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args(argv);root=Path.cwd();approval_bytes=a.approval.read_bytes();approval=json.loads(approval_bytes);gate=validate_approval(approval,root)
 if not gate["approved"]:print(json.dumps({"status":"BLOCKED_BEFORE_CONSUMPTION","approval":gate},indent=2));return 2
 if not sealed_controller_identity(approval):raise RuntimeError("UNSEALED_CONTROLLER")
 authority_snapshot=binding_snapshot(approval,root)
 manifest=json.loads((HERE/"manifest.json").read_bytes());font_manifest=json.loads((HERE/"font-manifest.json").read_bytes());paths={k:root/v for k,v in manifest["paths"].items()}
 if a.out.resolve()!=paths["result"].resolve() or any(x.exists() or x.is_symlink() for x in paths.values()):raise RuntimeError("OUTPUT_PREFLIGHT")
 outer=validate_manifest(font_manifest,SOURCE,check_source_identity=True)
 if not outer["passed"]:raise RuntimeError("FONT_MANIFEST_OUTER:"+str(outer["errors"]))
 font_before=[stat_font(call["resolved_path"]) for call in font_manifest["calls"]]
 if not Path("/usr/bin/true").is_file() or Path("/usr/bin/true").is_symlink():raise RuntimeError("TRUE_PREFLIGHT")
 with tempfile.TemporaryDirectory(prefix="dw-font-qualification-") as td:
  temp=Path(td);source=prepare_source(temp);source_digest=tree_digest(source);bundle=temp/"bundle";bundle.mkdir()
  mapping={"episode.py":"episode","font_registry.py":"font_registry","protocol.py":"protocol","process_control.py":"process_control","manifest.json":"manifest","font-manifest.json":"font_manifest","environment_manifest.py":"environment_manifest","environment-content-manifest.json":"environment_content","bootstrap.py":"bootstrap"}
  for name,key in mapping.items():
   src=HERE/name;dest=bundle/name;dest.write_bytes(src.read_bytes());dest.chmod(0o444);fsync_path(dest)
  fsync_path(bundle);bundle.chmod(0o555);env_manifest=json.loads((bundle/"environment-content-manifest.json").read_bytes());copied=copy_and_verify(env_manifest,temp/"runtime");sealed_python=copied["base_python"]/"bin/python3.11";site=copied["site_packages"]
  if not all(verify_root(spec,copied[spec["name"]]) for spec in env_manifest["roots"]):raise RuntimeError("SEALED_RUNTIME")
  sealed_sysfont=site/"pygame/sysfont.py"
  if sha(sealed_sysfont)!=SYSFONT_SHA:raise RuntimeError("SEALED_SYSFONT")
  if a.approval.read_bytes()!=approval_bytes or binding_snapshot(approval,root)!=authority_snapshot or tree_digest(source)!=source_digest or [stat_font(call["resolved_path"]) for call in font_manifest["calls"]]!=font_before:raise RuntimeError("AUTHORITY_OR_INPUT_TOCTOU")
  latch=SignalLatch();latch.install();marker_owned=False
  try:
   if latch.pending is not None:return 130
   started=time.monotonic();deadline=started+120;work_deadline=deadline-15;marker={"schema_version":"argo-font-qualification-marker/v1","run_id":RUN_ID,"approval_sha256":hashlib.sha256(approval_bytes).hexdigest(),"execution_root_sha256":execution_root(approval),"authority_root_sha256":authority_root(approval,json.loads((root/approval["bindings"]["proposal"]["path"]).read_bytes())),"consumed_at":datetime.datetime.now().astimezone().isoformat(timespec="seconds"),"no_retry":True};exclusive(paths["marker"],canonical(marker)+b"\n");marker_owned=True;paths["sidecar_root"].mkdir(parents=True);fsync_path(paths["sidecar_root"].parent);previous=None;previous=append_ledger(paths["ledger"],{"event":"header","run_id":RUN_ID,"timestamp":marker["consumed_at"]},previous);results=[]
   for cell in manifest["ordered_cells"]:
    if latch.pending is not None or time.monotonic()>=work_deadline:break
    mode=cell["mode"];work=temp/mode;(work/"tmp").mkdir(parents=True);profile_path=work/"profile.sb";profile_path.write_text(profile(mode,work,sealed_python));profile_path.chmod(0o444);side=paths["sidecar_root"]/mode;side.mkdir();event=side/"event.jsonl";stdout=side/"stdout.bin";stderr=side/"stderr.bin";temp_event=work/"event.jsonl";temp_stdout=work/"stdout.bin";temp_stderr=work/"stderr.bin";previous=append_ledger(paths["ledger"],{"event":"planned","run_id":RUN_ID,"cell_id":cell["cell_id"],"mode":mode},previous)
    args=[str(SANDBOX),"-f",str(profile_path),str(sealed_python),"-I","-S","-B",str(bundle/"bootstrap.py"),"worker",str(bundle),str(source),str(site),"--mode",mode,"--manifest",str(bundle/"font-manifest.json"),"--source",str(source),"--event-fd","{EVENT_FD}","--source-commit",SOURCE_COMMIT,"--source-tree",SOURCE_TREE,"--source-archive-sha256",SOURCE_ARCHIVE,"--pygame-sysfont-sha256",SYSFONT_SHA,"--font-manifest-sha256",sha(bundle/"font-manifest.json"),"--episode-sha256",sha(bundle/"episode.py"),"--font-registry-sha256",sha(bundle/"font_registry.py")]
    def spawned(pid,pgid,cell=cell):
     nonlocal previous;previous=append_ledger(paths["ledger"],{"event":"spawned","run_id":RUN_ID,"cell_id":cell["cell_id"],"pid":pid,"pgid":pgid},previous)
    run=run_process(args,work,sanitized(bundle,source,site,work),temp_stdout,temp_stderr,temp_event,cell["timeout_seconds"],work_deadline,on_spawn=spawned,stop_signal=lambda:latch.pending);exclusive(stdout,temp_stdout.read_bytes());exclusive(stderr,temp_stderr.read_bytes());exclusive(event,temp_event.read_bytes());identity={"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"source_archive_sha256":SOURCE_ARCHIVE,"pygame_sysfont_sha256":SYSFONT_SHA,"font_manifest_sha256":sha(bundle/"font-manifest.json"),"python_executable":str(sealed_python.resolve()),"pygame_sysfont_path":str(sealed_sysfont.resolve()),"episode_path":str((bundle/"episode.py").resolve()),"episode_sha256":sha(bundle/"episode.py"),"font_registry_path":str((bundle/"font_registry.py").resolve()),"font_registry_sha256":sha(bundle/"font_registry.py")};validation=validate_event(event,mode,font_manifest,identity) if run["exit_code"]==0 and event.is_file() else {"passed":False,"errors":["PROCESS_OR_EVENT"]};value={"cell_id":cell["cell_id"],"mode":mode,"run":run,"validation":validation};results.append(value);previous=append_ledger(paths["ledger"],{"event":"finished","run_id":RUN_ID,"cell_id":cell["cell_id"],"exit_code":run["exit_code"],"valid":validation["passed"],"errors":validation["errors"]},previous)
   if latch.pending is not None:raise RuntimeError("CONTROLLER_SIGNAL:"+str(latch.pending))
   values={x["mode"]:x["validation"].get("value") for x in results if x["validation"]["passed"]};comparison=compare(values["native"],values["pinned"]) if set(values)=={"native","pinned"} else {"passed":False,"errors":["MISSING_VALID_CELL"],"matched_calls":0};font_after=[stat_font(call["resolved_path"]) for call in font_manifest["calls"]];runtime_ok=all(verify_root(spec,copied[spec["name"]]) for spec in env_manifest["roots"]);font_stable=font_before==font_after;source_stable=tree_digest(source)==source_digest;within=time.monotonic()<deadline;status="PASS" if len(results)==2 and all(x["validation"]["passed"] and not x["run"]["unreaped"] for x in results) and comparison["passed"] and font_stable and source_stable and runtime_ok and within else "INVALID";result={"schema_version":"argo-font-qualification-result/v1","run_id":RUN_ID,"status":status,"cells_planned":2,"cells_finished":len(results),"cell_results":results,"comparison":comparison,"font_pre_post_stable":font_stable,"source_pre_post_stable":source_stable,"sealed_runtime_postcheck":runtime_ok,"deadline_seconds":120,"within_deadline":within,"elapsed_seconds":round(time.monotonic()-started,6),"scenario_loads":0,"agent_observations":0,"model_calls":0,"docker_calls":0,"spend_usd":0.0,"no_retry":True};previous=append_ledger(paths["ledger"],{"event":"finalized","run_id":RUN_ID,"status":status,"result_sha256":hashlib.sha256(canonical(result)+b"\n").hexdigest()},previous);atomic_publish(paths["result_pending"],paths["result"],canonical(result)+b"\n");print(json.dumps(result,indent=2,ensure_ascii=False));return 0 if status=="PASS" else 1
  except BaseException as exc:
   if not marker_owned:raise
   abort={"schema_version":"argo-font-qualification-abort/v1","run_id":RUN_ID,"error":type(exc).__name__+":"+str(exc),"no_retry":True,"timestamp":datetime.datetime.now().astimezone().isoformat(timespec="seconds")};atomic_publish(paths["abort_pending"],paths["abort"],canonical(abort)+b"\n");raise
  finally:latch.restore()
if __name__=="__main__":raise SystemExit(main())
