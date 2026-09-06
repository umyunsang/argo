#!/usr/bin/env python3
"""Validate authority, seal the font controller, then replace this process."""
from __future__ import annotations
import argparse,fcntl,hashlib,json,os,signal,shutil,stat,subprocess,tempfile,time
from pathlib import Path
ENGINE=Path("/Users/um-yunsang/argo-paper-orx");CONTROLLER_INTERPRETER=Path("/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/bin/python3.14");APPROVAL_REL=Path("paper/research/discoveryworld-font-registry-qualification-approval-v1.json");RUN_ID="dw-font-registry-qual-20260906-v1"
EXEC_NAMES={"runner":"run.py","episode":"episode.py","font_registry":"font_registry.py","protocol":"protocol.py","process_control":"process_control.py","manifest":"manifest.json","font_manifest":"font-manifest.json","environment_manifest":"environment_manifest.py","environment_content":"environment-content-manifest.json","bootstrap":"bootstrap.py","worker_gate":"worker_gate.py","launcher":"launcher.py","result_verifier":"verify_result.py","admission_consumer":"admit_result.py"}
EXEC_KEYS=tuple(EXEC_NAMES);EXPECTED={key:Path("experiments/argo_workflow_followup/discoveryworld_font_qualification")/name for key,name in EXEC_NAMES.items()};EXPECTED["font_manifest"]=Path("paper/research/discoveryworld-pinned-font-manifest-v1.json")
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def read_once(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  if not stat.S_ISREG(os.fstat(fd).st_mode):raise RuntimeError("NOT_REGULAR")
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def write_once(path,data,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 try:
  view=memoryview(data)
  while view:
   n=os.write(fd,view)
   if n<=0:raise OSError("write")
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
def proposal_core(value):
 v=dict(value);v.pop("required_approval_text",None);return sha_bytes(canonical(v))
def execution_material(a):return {**{k:a.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS},"source_commit":a.get("source_commit"),"source_tree":a.get("source_tree"),"source_archive_sha256":a.get("source_archive_sha256"),"worker_interpreter":a.get("interpreter"),"worker_interpreter_sha256":a.get("interpreter_sha256"),"controller_interpreter":a.get("controller_interpreter"),"controller_interpreter_sha256":a.get("controller_interpreter_sha256"),"sandbox_exec":a.get("sandbox_exec"),"sandbox_exec_sha256":a.get("sandbox_exec_sha256")}
def execution_root(a):return sha_bytes(canonical(execution_material(a)))
def authority_root(a,p):return sha_bytes(canonical({**{k:a.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS},"design":a.get("bindings",{}).get("design",{}).get("sha256"),"proposal_core":proposal_core(p)}))
def required_text(a,er,ar):return f'I approve exactly one local zero-model DiscoveryWorld font-registry qualification run {RUN_ID} for execution root {er}, authority root {ar}, and design SHA-256 {a.get("bindings",{}).get("design",{}).get("sha256")}, limited to exactly two zero-scenario cells, a 120-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.'
def validate(a,approval_path,root):
 if Path(root).resolve()!=ENGINE or Path(approval_path).resolve()!=ENGINE/APPROVAL_REL:return False
 if a.get("status")!="APPROVED" or a.get("approved_by")!="user" or a.get("run_id")!=RUN_ID:return False
 if set(a.get("bindings",{}))!=set(EXEC_KEYS)|{"design","proposal","immutable_validation","method_review","runtime_review","handoff_review","user_authorization"}:return False
 for key,path in EXPECTED.items():
  spec=a.get("bindings",{}).get(key,{});actual=ENGINE/path
  if spec.get("path")!=path.as_posix() or not actual.is_file() or sha_bytes(read_once(actual))!=spec.get("sha256"):return False
 for key in ["design","proposal","immutable_validation","method_review","runtime_review","handoff_review","user_authorization"]:
  spec=a.get("bindings",{}).get(key,{});actual=ENGINE/spec.get("path","")
  if not actual.is_file() or sha_bytes(read_once(actual))!=spec.get("sha256"):return False
 try:proposal=json.loads(read_once(ENGINE/a["bindings"]["proposal"]["path"]));er=execution_root(a);ar=authority_root(a,proposal);text=required_text(a,er,ar)
 except (OSError,KeyError,json.JSONDecodeError,TypeError):return False
 if a.get("execution_root_sha256")!=er or a.get("authority_root_sha256")!=ar or a.get("proposal_core_sha256")!=proposal_core(proposal) or proposal.get("required_approval_text")!=text or a.get("required_approval_text")!=text or a.get("user_approval_message")!=text or a.get("user_approval_message_sha256")!=sha_bytes(text.encode()):return False
 if a.get("controller_interpreter")!=str(CONTROLLER_INTERPRETER) or sha_bytes(read_once(CONTROLLER_INTERPRETER))!=a.get("controller_interpreter_sha256"):return False
 return True
def seal(a,approval_bytes,destination):
 destination=Path(destination);destination.mkdir(mode=0o700);files={}
 for key,name in EXEC_NAMES.items():
  source=ENGINE/a["bindings"][key]["path"];data=read_once(source);target=destination/name;write_once(target,data,0o500 if name.endswith(".py") else 0o400);files[name]=sha_bytes(data)
 write_once(destination/"approval.json",approval_bytes,0o400);files["approval.json"]=sha_bytes(approval_bytes);value={"schema_version":"argo-font-controller-seal/v1","execution_root_sha256":execution_root(a),"files":files};data=canonical(value)+b"\n";write_once(destination/"seal.json",data,0o400);fd=os.open(destination,os.O_RDONLY);os.fsync(fd);os.close(fd);destination.chmod(0o500);return sha_bytes(data)
def group_exists(pgid):
 try:os.killpg(pgid,0);return True
 except ProcessLookupError:return False
 except PermissionError:return True
def process_exists(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False
 except PermissionError:return True
def kill_pid(pid):
 try:os.kill(pid,signal.SIGTERM)
 except ProcessLookupError:return False
 time.sleep(.02)
 if process_exists(pid):
  try:os.kill(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.02);return process_exists(pid)
def kill_group(pgid,proc=None):
 try:os.killpg(pgid,signal.SIGTERM)
 except ProcessLookupError:pass
 if proc is not None:
  try:proc.wait(timeout=.5)
  except subprocess.TimeoutExpired:pass
 time.sleep(.02)
 if group_exists(pgid):
  try:os.killpg(pgid,signal.SIGKILL)
  except ProcessLookupError:pass
  if proc is not None:
   try:proc.wait(timeout=.5)
   except subprocess.TimeoutExpired:pass
 time.sleep(.02);return group_exists(pgid)
def drain_registry(fd,ack_fd,state):
 while True:
  try:chunk=os.read(fd,4096)
  except BlockingIOError:break
  if not chunk:state["eof"]=True;break
  state["buffer"]+=chunk
  if len(state["buffer"])>65536:state["errors"].append("REGISTRY_OVERSIZE");state["buffer"]=b"";break
  while b"\n" in state["buffer"]:
   line,state["buffer"]=state["buffer"].split(b"\n",1)
   try:record=json.loads(line)
   except (UnicodeDecodeError,json.JSONDecodeError):state["errors"].append("REGISTRY_JSON");continue
   phase=record.get("phase");pid=record.get("pid");pgid=record.get("pgid");sid=record.get("sid")
   if set(record)!={"schema_version","phase","pid","pgid","sid"} or record.get("schema_version")!="argo-font-worker-pgid/v2" or phase not in {"pre_session","controller_pre_session","post_session","controller_post_session"} or not all(isinstance(x,int) and x>0 for x in [pid,pgid,sid]):state["errors"].append("REGISTRY_RECORD");continue
   if phase in {"post_session","controller_post_session"} and (pid!=pgid or pid!=sid):state["errors"].append("REGISTRY_POST_IDENTITY");continue
   phases=state["phases"].setdefault(pid,set())
   if phase in phases:state["errors"].append("REGISTRY_DUPLICATE")
   phases.add(phase);state["pids"].add(pid)
   if phase in {"pre_session","controller_pre_session"}:state["pre_identity"].setdefault(pid,{})[phase]=(pgid,sid)
   if phase in {"post_session","controller_post_session"}:state["pgids"].add(pgid)
   pre=state["pre_identity"].get(pid,{})
   if {"pre_session","controller_pre_session"}.issubset(phases) and pid not in state["acked"]:
    if pre["pre_session"]!=pre["controller_pre_session"] or pre["pre_session"]!=(state["controller_pgid"],state["controller_sid"]) or pid==state["controller_pgid"]:state["errors"].append("REGISTRY_PRE_CONTAINMENT")
    else:
     try:
      if os.write(ack_fd,b"G")!=1:raise OSError("ack")
      state["acked"].add(pid)
     except OSError:state["errors"].append("REGISTRY_ACK")
def supervise_process(proc,started,registry_fd,ack_fd,deadline_seconds=120,stop_signal=None):
 deadline=started+deadline_seconds;timed_out=False;interrupted=False;unreaped=False;descendant_leak=False;code=None;state={"buffer":b"","pids":set(),"pgids":set(),"phases":{},"pre_identity":{},"acked":set(),"errors":[],"eof":False,"controller_pgid":proc.pid,"controller_sid":proc.pid};fcntl.fcntl(registry_fd,fcntl.F_SETFL,fcntl.fcntl(registry_fd,fcntl.F_GETFL)|os.O_NONBLOCK)
 try:
  while True:
   drain_registry(registry_fd,ack_fd,state)
   if stop_signal is not None and stop_signal() is not None:interrupted=True;code=130;break
   now=time.monotonic()
   if now>=deadline:timed_out=True;code=124;break
   try:code=proc.wait(timeout=min(.05,deadline-now));break
   except subprocess.TimeoutExpired:continue
 finally:
  if timed_out or interrupted or proc.poll() is None:unreaped=kill_group(proc.pid,proc) or unreaped
  end=time.monotonic()+.5
  while not state["eof"] and time.monotonic()<end:drain_registry(registry_fd,ack_fd,state);time.sleep(.01)
  drain_registry(registry_fd,ack_fd,state)
  if state["buffer"]:state["errors"].append("REGISTRY_TRUNCATED")
  for pgid in sorted(state["pgids"]):
   if group_exists(pgid):descendant_leak=True;unreaped=kill_group(pgid) or unreaped
  for pid in sorted(state["pids"]):
   if process_exists(pid):descendant_leak=True;unreaped=kill_pid(pid) or unreaped
  if group_exists(proc.pid):descendant_leak=True;unreaped=kill_group(proc.pid,proc) or unreaped
 return {"controller_exit_code":code,"timed_out":timed_out,"interrupted":interrupted,"unreaped":unreaped,"descendant_leak":descendant_leak,"worker_pids":sorted(state["pids"]),"worker_pgids":sorted(state["pgids"]),"worker_registry_phases":{str(k):sorted(v) for k,v in sorted(state["phases"].items())},"registry_errors":state["errors"],"registry_eof":state["eof"],"elapsed_seconds":time.monotonic()-started}
class SupervisorLatch:
 SIGNALS=(signal.SIGINT,signal.SIGTERM,signal.SIGHUP)
 def __init__(self):self.pending=None;self.old={}
 def handler(self,signum,frame):self.pending=self.pending or signum
 def install(self):
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,set(self.SIGNALS))
  try:
   for sig in self.SIGNALS:
    current=signal.getsignal(sig);allowed={signal.SIG_DFL,signal.default_int_handler} if sig==signal.SIGINT else {signal.SIG_DFL}
    if current not in allowed:raise RuntimeError("NONTERMINATING_INHERITED_SIGNAL_POLICY")
    self.old[sig]=current;signal.signal(sig,self.handler)
  except BaseException:
   for sig,value in self.old.items():signal.signal(sig,value)
   self.old.clear();raise
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,prior)
 def restore(self):
  for sig,value in self.old.items():signal.signal(sig,value)
def ledger_pgids(path):
 try:return sorted({row["pgid"] for row in [json.loads(line) for line in read_once(path).splitlines()] if row.get("event")=="spawned" and isinstance(row.get("pgid"),int)})
 except (OSError,KeyError,json.JSONDecodeError):return []
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);x=p.parse_args(argv);root=Path.cwd();approval_bytes=read_once(x.approval);a=json.loads(approval_bytes)
 if not validate(a,x.approval,root):print(json.dumps({"status":"BLOCKED_BEFORE_CONSUMPTION","reason":"CANONICAL_APPROVAL"}));return 2
 parent=Path(tempfile.mkdtemp(prefix="dw-font-controller-seal-"));destination=parent/"controller";seal_sha=seal(a,approval_bytes,destination);started=time.monotonic();env=dict(os.environ);read_fd,write_fd=os.pipe();ack_read,ack_write=os.pipe();env.update({"ARGO_FONT_CONTROLLER_SEAL":str(destination),"ARGO_FONT_CONTROLLER_SEAL_SHA256":seal_sha,"ARGO_FONT_LAUNCH_MONOTONIC":repr(started),"ARGO_FONT_SUPERVISOR_FD":str(write_fd),"ARGO_FONT_SUPERVISOR_ACK_FD":str(ack_read)});python=a["controller_interpreter"];args=[python,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(x.approval.resolve()),"--out",str(x.out.resolve())];latch=SupervisorLatch();latch.install();proc=None
 try:
  if latch.pending is not None:return 130
  proc=subprocess.Popen(args,env=env,pass_fds=(write_fd,ack_read),start_new_session=True)
  try:
   os.close(write_fd);write_fd=-1;os.close(ack_read);ack_read=-1;observed=supervise_process(proc,started,read_fd,ack_write,120,stop_signal=lambda:latch.pending)
  except BaseException:
   if proc is not None:supervise_process(proc,started,read_fd,ack_write,0,stop_signal=lambda:130)
   raise
 finally:
  if write_fd>=0:os.close(write_fd)
  if ack_read>=0:os.close(ack_read)
  os.close(ack_write);os.close(read_fd);latch.restore()
 if latch.pending is not None:observed["interrupted"]=True;observed["controller_exit_code"]=130
 code=observed["controller_exit_code"]
 try:destination.chmod(0o700);shutil.rmtree(parent);seal_removed=not parent.exists()
 except OSError:seal_removed=False
 manifest=json.loads(read_once(ENGINE/a["bindings"]["manifest"]["path"]));paths={k:ENGINE/v for k,v in manifest["paths"].items()};result_sha=sha_bytes(read_once(paths["result"])) if paths["result"].is_file() else None;marker_sha=sha_bytes(read_once(paths["marker"])) if paths["marker"].is_file() else None;spawned=ledger_pgids(paths["ledger"]) if paths["ledger"].is_file() else [];required_phases=["controller_post_session","controller_pre_session","post_session","pre_session"];registry_matches=spawned==observed["worker_pgids"] and spawned==observed["worker_pids"] and all(phases==required_phases for phases in observed["worker_registry_phases"].values());passed=not observed["timed_out"] and not observed["interrupted"] and not observed["unreaped"] and not observed["descendant_leak"] and not observed["registry_errors"] and observed["registry_eof"] and registry_matches and seal_removed and code in {0,1} and observed["elapsed_seconds"]<120 and result_sha is not None and marker_sha is not None;receipt={"schema_version":"argo-font-qualification-supervision/v1","run_id":RUN_ID,"passed":passed,**observed,"ledger_spawned_pgids":spawned,"pgid_registry_matches":registry_matches,"controller_seal_removed":seal_removed,"launch_monotonic":started,"observed_completion_monotonic":time.monotonic(),"deadline_seconds":120,"marker_sha256":marker_sha,"result_sha256":result_sha};write_once(paths["supervision"],canonical(receipt)+b"\n",0o600);fd=os.open(paths["supervision"].parent,os.O_RDONLY);os.fsync(fd);os.close(fd);return code if passed else 1
if __name__=="__main__":raise SystemExit(main())
