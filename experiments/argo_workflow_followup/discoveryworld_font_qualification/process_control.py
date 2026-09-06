#!/usr/bin/env python3
"""Bounded one-process-group execution with full-group cleanup."""
from __future__ import annotations
import json,os,signal,stat,subprocess,time
from pathlib import Path
def group_exists(pgid):
 try:os.killpg(pgid,0);return True
 except ProcessLookupError:return False
 except PermissionError:return True
def terminate_group(proc,pgid,grace=1.0):
 try:os.killpg(pgid,signal.SIGTERM)
 except ProcessLookupError:pass
 try:proc.wait(timeout=grace)
 except subprocess.TimeoutExpired:pass
 if group_exists(pgid):
  try:os.killpg(pgid,signal.SIGKILL)
  except ProcessLookupError:pass
 try:proc.wait(timeout=grace)
 except subprocess.TimeoutExpired:pass
 end=time.monotonic()+grace
 while group_exists(pgid) and time.monotonic()<end:time.sleep(0.01)
 return group_exists(pgid)
def write_registry(fd,phase,pid,pgid,sid):
 payload=json.dumps({"schema_version":"argo-font-worker-pgid/v2","phase":phase,"pid":pid,"pgid":pgid,"sid":sid},sort_keys=True,separators=(",",":")).encode()+b"\n";view=memoryview(payload)
 while view:
  n=os.write(fd,view)
  if n<=0:raise OSError("supervisor registry")
  view=view[n:]
def terminate_candidate(proc,pgid=None):
 if pgid is not None:return terminate_group(proc,pgid)
 try:current=os.getpgid(proc.pid)
 except ProcessLookupError:return False
 if current==proc.pid:return terminate_group(proc,current)
 try:proc.terminate()
 except ProcessLookupError:return False
 try:proc.wait(timeout=.5)
 except subprocess.TimeoutExpired:
  try:proc.kill()
  except ProcessLookupError:pass
  try:proc.wait(timeout=.5)
  except subprocess.TimeoutExpired:return True
 return proc.poll() is None
def run_process(argv,cwd,env,stdout_path,stderr_path,event_path,cell_timeout,absolute_deadline,on_spawn=None,stop_signal=None,supervisor_fd=None,ack_fd=None):
 if time.monotonic()>=absolute_deadline:raise TimeoutError("GLOBAL_DEADLINE_BEFORE_FD")
 cwd=Path(cwd);cwd.mkdir(parents=True,exist_ok=True);paths=[Path(stdout_path),Path(stderr_path),Path(event_path)];fds=[];proc=None;pgid=None;gate_ack_read=None;gate_ack_write=None;started=time.monotonic();flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 try:
  for path in paths:
   path.parent.mkdir(parents=True,exist_ok=True);fd=os.open(path,flags,0o600);fds.append(fd)
   if not stat.S_ISREG(os.fstat(fd).st_mode):raise RuntimeError("OUTPUT_NOT_REGULAR")
  if time.monotonic()>=absolute_deadline:raise TimeoutError("GLOBAL_DEADLINE_BEFORE_SPAWN")
  handshake=supervisor_fd is not None and ack_fd is not None
  if handshake:gate_ack_read,gate_ack_write=os.pipe()
  command=[str(fds[2]) if item=="{EVENT_FD}" else str(gate_ack_read) if item=="{CONTROLLER_ACK_FD}" else item for item in argv];passed=(fds[2],)+(() if supervisor_fd is None else (supervisor_fd,))+(() if ack_fd is None else (ack_fd,))+(() if gate_ack_read is None else (gate_ack_read,));proc=subprocess.Popen(command,cwd=cwd,env=env,stdout=fds[0],stderr=fds[1],pass_fds=passed,start_new_session=not handshake,close_fds=True)
  if handshake:
   initial_group=os.getpgid(proc.pid);initial_sid=os.getsid(proc.pid)
   if initial_group!=os.getpgrp():raise RuntimeError("GATE_ESCAPED_BEFORE_REGISTRATION")
   write_registry(supervisor_fd,"controller_pre_session",proc.pid,initial_group,initial_sid);handshake_deadline=min(absolute_deadline,time.monotonic()+5)
   while True:
    if stop_signal is not None and stop_signal() is not None:raise RuntimeError("SIGNAL_DURING_HANDSHAKE")
    if proc.poll() is not None:raise RuntimeError("GATE_EXIT_DURING_HANDSHAKE")
    try:observed_group=os.getpgid(proc.pid);observed_sid=os.getsid(proc.pid)
    except ProcessLookupError:raise RuntimeError("GATE_LOST_DURING_HANDSHAKE")
    if observed_group==proc.pid and observed_sid==proc.pid:break
    if observed_group!=initial_group or observed_sid!=initial_sid:raise RuntimeError("GATE_PARTIAL_SESSION_TRANSITION")
    if time.monotonic()>=handshake_deadline:raise TimeoutError("GATE_HANDSHAKE")
    time.sleep(.005)
   pgid=proc.pid;write_registry(supervisor_fd,"controller_post_session",proc.pid,pgid,observed_sid)
  else:
   pgid=proc.pid
   if os.getpgid(proc.pid)!=pgid:raise RuntimeError("PROCESS_GROUP")
  if on_spawn:on_spawn(proc.pid,pgid)
  if handshake:
   if os.write(gate_ack_write,b"C")!=1:raise OSError("controller ack")
   os.close(gate_ack_write);gate_ack_write=None;os.close(gate_ack_read);gate_ack_read=None
  end=min(started+cell_timeout,absolute_deadline);timed_out=False;global_deadline=False
  controller_signal=None
  while True:
   if stop_signal is not None and stop_signal() is not None:controller_signal=stop_signal();code=130;timed_out=False;break
   now=time.monotonic()
   if now>=end:timed_out=True;global_deadline=absolute_deadline<=started+cell_timeout;code=124;break
   try:code=proc.wait(timeout=min(0.05,end-now));break
   except subprocess.TimeoutExpired:continue
  unreaped=False
  if timed_out or controller_signal is not None or group_exists(pgid):unreaped=terminate_group(proc,pgid)
  if unreaped:raise RuntimeError("UNREAPED_PROCESS_GROUP")
  return {"exit_code":code,"timed_out":timed_out,"global_deadline":global_deadline,"controller_signal":controller_signal,"unreaped":unreaped,"pid":proc.pid,"pgid":pgid,"duration_seconds":round(time.monotonic()-started,6)}
 except BaseException as exc:
  if proc is not None and terminate_candidate(proc,pgid):raise RuntimeError("UNREAPED_AFTER_EXCEPTION") from exc
  raise
 finally:
  for extra in [gate_ack_read,gate_ack_write]:
   if extra is not None:
    try:os.close(extra)
    except OSError:pass
  for fd in fds:
   try:os.fsync(fd)
   except OSError:pass
   try:os.close(fd)
   except OSError:pass
