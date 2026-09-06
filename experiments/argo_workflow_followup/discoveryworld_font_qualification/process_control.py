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
def run_process(argv,cwd,env,stdout_path,stderr_path,event_path,cell_timeout,absolute_deadline,on_spawn=None,stop_signal=None,supervisor_fd=None):
 if time.monotonic()>=absolute_deadline:raise TimeoutError("GLOBAL_DEADLINE_BEFORE_FD")
 cwd=Path(cwd);cwd.mkdir(parents=True,exist_ok=True);paths=[Path(stdout_path),Path(stderr_path),Path(event_path)];fds=[];proc=None;pgid=None;started=time.monotonic();flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 try:
  for path in paths:
   path.parent.mkdir(parents=True,exist_ok=True);fd=os.open(path,flags,0o600);fds.append(fd)
   if not stat.S_ISREG(os.fstat(fd).st_mode):raise RuntimeError("OUTPUT_NOT_REGULAR")
  if time.monotonic()>=absolute_deadline:raise TimeoutError("GLOBAL_DEADLINE_BEFORE_SPAWN")
  command=[str(fds[2]) if item=="{EVENT_FD}" else item for item in argv];passed=(fds[2],) if supervisor_fd is None else (fds[2],supervisor_fd);proc=subprocess.Popen(command,cwd=cwd,env=env,stdout=fds[0],stderr=fds[1],pass_fds=passed,start_new_session=True,close_fds=True);pgid=proc.pid
  if os.getpgid(proc.pid)!=pgid:raise RuntimeError("PROCESS_GROUP")
  if supervisor_fd is not None:
   payload=json.dumps({"schema_version":"argo-font-worker-pgid/v1","source":"controller","pid":proc.pid,"pgid":pgid,"sid":os.getsid(proc.pid)},sort_keys=True,separators=(",",":")).encode()+b"\n";view=memoryview(payload)
   while view:
    n=os.write(supervisor_fd,view)
    if n<=0:raise OSError("supervisor registry")
    view=view[n:]
  if on_spawn:on_spawn(proc.pid,pgid)
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
  if proc is not None and pgid is not None and terminate_group(proc,pgid):raise RuntimeError("UNREAPED_AFTER_EXCEPTION") from exc
  raise
 finally:
  for fd in fds:
   try:os.fsync(fd)
   except OSError:pass
   try:os.close(fd)
   except OSError:pass
