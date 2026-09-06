#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from run import ControllerSignalLatch,GlobalDeadlineError,_main,SANDBOX_EXEC,SOURCE_REPO,build_argv,managed_run,preflight_paths,classify_failure,copy_bound_output,execution_root_sha,frame_manifest,group_exists,open_frame_directory,revalidate_complete_cells,runtime_identity,sandbox_profile,validate_approval,write_abort_receipt
M=json.loads((HERE/"manifest.json").read_text())
class Tests(unittest.TestCase):
 def test_approved_direct_runner_rejects_unsealed_controller(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);approval=root/"approval";approval.write_text("{}");args=type("A",(),{"approval":approval,"out":root/"out"})()
   with patch("run.argparse.ArgumentParser.parse_args",return_value=args),patch("run.Path.cwd",return_value=root),patch("run.validate_approval",return_value={"approved":True,"checks":{},"errors":[]}):
    with self.assertRaises(RuntimeError):_main()
 def test_unapproved_fails(self):self.assertFalse(validate_approval(json.loads((HERE/"approval-template.json").read_text()),ROOT)["approved"])
 def test_exact_approval_passes(self):
  a=json.loads((HERE/"approval-template.json").read_text());a.update({"status":"APPROVED","approved_by":"user","approved_at":"2026-09-06T00:00:00+09:00","engine_repo":str(ROOT.resolve())});a["user_approval_message"]=a["required_approval_text"];a["user_approval_message_sha256"]=hashlib.sha256(a["user_approval_message"].encode()).hexdigest()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);execution=execution_root_sha(a);a["execution_root_sha256"]=execution
   for key,verdict in [("immutable_validation","PASS"),("method_review","PASS"),("runtime_review","PASS"),("handoff_review","ACCEPT")]:
    path=root/(key+".json");path.write_text(json.dumps({"execution_root_sha256":execution,"verdict":verdict}));a["bindings"][key]={"path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
   with patch("run.ENGINE_REPO",str(ROOT.resolve())):self.assertTrue(validate_approval(a,ROOT)["approved"])
 def test_manifest_hash_drift_fails(self):
  a=json.loads((HERE/"approval-template.json").read_text());a.update({"status":"APPROVED","approved_by":"user"});a["bindings"]["manifest"]["sha256"]="0"*64;self.assertFalse(validate_approval(a,ROOT)["approved"])
 def test_post_consumption_identity_uses_no_subprocess(self):
  import shutil
  from unittest.mock import patch
  template=json.loads((HERE/"approval-template.json").read_text())
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);execution=execution_root_sha(template);template["execution_root_sha256"]=execution
   for key,verdict in [("immutable_validation","PASS"),("method_review","PASS"),("runtime_review","PASS"),("handoff_review","ACCEPT")]:
    review=root/(key+".json");review.write_text(json.dumps({"execution_root_sha256":execution,"verdict":verdict}));template["bindings"][key]={"path":str(review),"sha256":hashlib.sha256(review.read_bytes()).hexdigest()}
   approval_path=root/"approval.json";approval_path.write_text(json.dumps(template));approval_bytes=approval_path.read_bytes();approval=template;manifest_path=ROOT/approval["bindings"]["manifest"]["path"];manifest_bytes=manifest_path.read_bytes();bundle=root/"bundle";source=root/"source"/"discoveryworld";bundle.mkdir();source.mkdir(parents=True)
   mapping={"run.py":HERE/"run.py","episode.py":HERE/"episode.py","adapter_v2.py":HERE/"adapter_v2.py","state_projection.py":HERE/"state_projection.py","lifecycle.py":HERE/"lifecycle.py","protocol.py":HERE/"protocol.py","schemas.json":HERE/"schemas.json","manifest.json":manifest_path,"proposal.json":ROOT/approval["bindings"]["proposal"]["path"],"design.json":ROOT/approval["bindings"]["design"]["path"],"environment_manifest.py":HERE/"environment_manifest.py","environment-content-manifest.json":HERE/"environment-content-manifest.json","bootstrap.py":HERE/"bootstrap.py","approval.json":approval_path}
   for name,path in mapping.items():shutil.copy2(path,bundle/name)
   shutil.copy2(Path(SOURCE_REPO)/"discoveryworld/DiscoveryWorldAPI.py",source/"DiscoveryWorldAPI.py");shutil.copy2(Path(SOURCE_REPO)/"discoveryworld/UserInterface.py",source/"UserInterface.py")
   with patch("run.subprocess.run",side_effect=AssertionError("post-consumption subprocess")):
    self.assertTrue(runtime_identity(approval,ROOT,approval_path,approval_bytes,manifest_path,manifest_bytes,bundle,source.parent))
 def test_strong_closure_revalidates_prior_valid_cell(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);cell=copy.deepcopy(M["ordered_cells"][0]);cell.update({"event_path":"event","ui_gzip_path":"ui","frame_manifest_path":"frame"});(root/"event").write_bytes(b"e");(root/"ui").write_bytes(b"u");(root/"frame").write_text('{"files":[],"count":0,"bytes":0}');bundle=root/"bundle";source=root/"source";bundle.mkdir();source.mkdir();(bundle/"adapter_v2.py").write_bytes(b"a");(bundle/"state_projection.py").write_bytes(b"s");(bundle/"environment-content-manifest.json").write_bytes(b"e");(bundle/"bootstrap.py").write_bytes(b"b");prior={cell["cell_id"]:{"status":"valid_complete","runtime_workdir":"/sealed/work","run":{"exit_code":0,"timed_out":False},"sidecars":{}}};vectors={"status":"valid_complete","errors":[],"ui_hashes":["a"*64]*1001,"pre_state_hashes":["b"*64]*1001,"post_state_hashes":["c"*64]*1001,"event_sha256":"d"*64,"ui_gzip_sha256":"e"*64}
   with patch("run.validate_cell",return_value=vectors) as validate:
    closed=revalidate_complete_cells({"ordered_cells":[cell]},prior,root,source,bundle,"/runtime/base/bin/python","/site")
   validate.assert_called_once();self.assertEqual(closed[cell["cell_id"]]["ui_hashes"],vectors["ui_hashes"])
 def test_preflight_path_collision(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);m=copy.deepcopy(M);m["paths"]={k:k for k in m["paths"]};(root/m["paths"]["marker"]).write_text("x");self.assertFalse(preflight_paths(m,root)["passed"])
 def test_preflight_clean_paths(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);m=copy.deepcopy(M);m["paths"]={k:k for k in m["paths"]};self.assertTrue(preflight_paths(m,root)["passed"])
 def test_golden_argv_identity(self):
  c=M["ordered_cells"][0];argv=build_argv(c,"/python",HERE/"episode.py",HERE,"/source");self.assertIn(c["cell_id"],argv);self.assertIn(c["cell_nonce"],argv);self.assertIn(str(c["thread_id"]),argv);self.assertIn(str(HERE/"episode.py"),argv)
 def test_sealed_worker_argv_is_isolated(self):
  c=M["ordered_cells"][0];argv=build_argv(c,"/sealed/python",HERE/"episode.py",HERE,"/source","/sealed/site");self.assertEqual(argv[:9],["/sealed/python","-I","-S","-B",str(HERE/"bootstrap.py"),"worker",str(HERE),"/source","/sealed/site"]);self.assertIn("{EVENT_FD}",argv);self.assertIn("{UI_FD}",argv);self.assertNotIn(str(HERE/"episode.py"),argv)
 def test_timeout_kills_process_group(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);r=managed_run([sys.executable,"-c","import time; time.sleep(5)"],p,{},p/"o",p/"e",p/"events",0.05,1.0);self.assertTrue(r["timed_out"]);self.assertEqual(r["exit_code"],124);self.assertFalse(r["unreaped"])
 def test_complete_then_exit_nonzero_stays_nonzero(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);r=managed_run([sys.executable,"-c","import sys; print('complete'); sys.exit(1)"],p,{},p/"o",p/"e",p/"events",2,3);self.assertEqual(r["exit_code"],1)
 def test_timeout_kills_term_ignoring_grandchild_group(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);code="import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(5)']); time.sleep(5)";r=managed_run([sys.executable,"-c",code],p,{},p/"o",p/"e",p/"events",0.1,1.0);self.assertTrue(r["timed_out"]);self.assertFalse(r["unreaped"])
 def test_on_spawn_failure_kills_group(self):
  import os
  seen={}
  def fail(pid,pgid):seen.update({"pid":pid,"pgid":pgid});raise OSError("ledger")
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with self.assertRaises(RuntimeError):managed_run([sys.executable,"-c","import time; time.sleep(5)"],p,{},p/"o",p/"e",p/"events",2,3,fail)
   with self.assertRaises(ProcessLookupError):os.killpg(seen["pgid"],0)
 def test_expired_absolute_deadline_never_spawns(self):
  import time
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with patch("run.subprocess.Popen") as popen:
    with self.assertRaises(GlobalDeadlineError):managed_run([sys.executable,"-c","pass"],p,{},p/"o",p/"e",p/"events",2,absolute_deadline=time.monotonic()-1)
    popen.assert_not_called()
 def test_fd_open_failure_never_spawns(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with patch("run.os.open",side_effect=OSError("open")),patch("run.subprocess.Popen") as popen:
    with self.assertRaises(OSError):managed_run([sys.executable,"-c","pass"],p,{},p/"o",p/"e",p/"events",2,3)
    popen.assert_not_called()
 def test_popen_failure_is_propagated(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with patch("run.subprocess.Popen",side_effect=OSError("popen")):
    with self.assertRaises(OSError):managed_run([sys.executable,"-c","pass"],p,{},p/"o",p/"e",p/"events",2,3)
 def test_permission_error_means_group_may_still_exist(self):
  from unittest.mock import patch
  with patch("run.os.killpg",side_effect=PermissionError()):self.assertTrue(group_exists(123))
 def test_unreaped_status_dominates_later_sidecar_error(self):self.assertEqual(classify_failure({"unreaped":True},OSError("copy")),"unreaped")
 def test_getpgid_failure_kills_child_group(self):
  import os
  from unittest.mock import patch
  seen={}
  def fail(pid):seen["pgid"]=pid;raise OSError("getpgid")
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with patch("run.os.getpgid",side_effect=fail):
    with self.assertRaises(OSError):managed_run([sys.executable,"-c","import time; time.sleep(5)"],p,{},p/"o",p/"e",p/"events",2,3)
   with self.assertRaises(ProcessLookupError):os.killpg(seen["pgid"],0)
 def test_worker_does_not_inherit_blocked_term_mask(self):
  import os,signal,threading,time
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);graceful=root/"graceful"
   def send():time.sleep(0.1);os.kill(os.getpid(),signal.SIGTERM)
   threading.Thread(target=send,daemon=True).start();code="import signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,lambda *args:(Path("+repr(str(graceful))+").write_text('yes'),exit(0)));time.sleep(5)"
   run=managed_run([sys.executable,"-c",code],root,{},root/"o",root/"e",root/"events",5,6);self.assertEqual(run["controller_signal"],signal.SIGTERM);self.assertFalse(run["unreaped"]);self.assertTrue(graceful.exists())
 def test_controller_sigterm_kills_active_child_group(self):
  import os,signal,subprocess,time
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);state=p/"pgid"
   code="import sys;from pathlib import Path;sys.path.insert(0,"+repr(str(HERE))+ ");from run import managed_run;p=Path("+repr(str(p))+ ");managed_run([sys.executable,'-c','import time;time.sleep(20)'],p,{},p/'o',p/'e',p/'events',20,25,lambda pid,pgid:(p/'pgid').write_text(str(pgid)))"
   controller=subprocess.Popen([sys.executable,"-c",code],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   deadline=time.monotonic()+3
   while not state.exists() and time.monotonic()<deadline:time.sleep(0.01)
   self.assertTrue(state.exists());pgid=int(state.read_text());os.kill(controller.pid,signal.SIGTERM);controller.wait(timeout=8)
   with self.assertRaises(ProcessLookupError):os.killpg(pgid,0)
 def test_closure_blocks_and_detects_pending_signal(self):
  import os,signal
  with tempfile.TemporaryDirectory() as td:
   output=Path(td)/"published";latch=ControllerSignalLatch();latch.install()
   try:
    latch.block_for_closure();self.assertFalse(latch.closure_pending());os.kill(os.getpid(),signal.SIGTERM);output.write_bytes(b"complete");latch.restore();self.assertEqual(latch.pending,signal.SIGTERM);self.assertEqual(output.read_bytes(),b"complete")
   finally:latch.restore()
 def test_abort_receipt_is_atomic_and_requires_marker(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);self.assertFalse(write_abort_receipt(root,RuntimeError("x")));marker=root/"paper/research/receipts/discoveryworld-ui-parity-v1.marker.json";marker.parent.mkdir(parents=True);marker.write_bytes(b"marker");self.assertTrue(write_abort_receipt(root,RuntimeError("x")));abort=root/"paper/research/receipts/discoveryworld-ui-parity-v1-controller-abort.json";self.assertEqual(json.loads(abort.read_text())["status"],"CONTROLLER_ABORT");self.assertFalse((root/"paper/research/receipts/discoveryworld-ui-parity-v1-controller-abort.pending").exists())
 def test_controller_signal_latch_preserves_terminalization_failpoints(self):
  import os,signal
  for label in ["copy","validation","finished_append","cleanup"]:
   latch=ControllerSignalLatch();latch.install()
   try:
    os.kill(os.getpid(),signal.SIGTERM);completed=[];completed.append(label);self.assertEqual(completed,[label]);self.assertEqual(latch.pending,signal.SIGTERM)
   finally:latch.restore()
 def test_frame_manifest_rejects_symlink_entry_and_directory_swap(self):
  import os
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);frame=root/"frames";fd,identity=open_frame_directory(frame);(frame/"ok.png").write_bytes(b"png");self.assertEqual(frame_manifest(frame,fd,identity)["count"],1);(frame/"leak.png").symlink_to(ROOT/"README.md")
   with self.assertRaises(RuntimeError):frame_manifest(frame,fd,identity)
   (frame/"leak.png").unlink();frame.rename(root/"old");frame.mkdir()
   with self.assertRaises(RuntimeError):frame_manifest(frame,fd,identity)
   os.close(fd)
 def test_output_symlink_substitution_cannot_confuse_controller(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);output=root/"o";code="import os;os.unlink("+repr(str(output))+");os.symlink("+repr(str(ROOT/"README.md"))+","+repr(str(output))+")";run=managed_run([sys.executable,"-c",code],root,{},output,root/"e",root/"events",2,3);dest=root/"copied"
   with self.assertRaises(OSError):copy_bound_output(output,dest,run["output_identities"])
   self.assertFalse(dest.exists())
 def test_symlink_output_collision_blocks(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);target=root/"target";target.mkdir();(root/"marker").symlink_to(target,target_is_directory=True);m=copy.deepcopy(M);m["paths"]={k:k for k in m["paths"]};self.assertFalse(preflight_paths(m,root)["passed"])
 def test_raw_binary_stdout_is_retained(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);code="import os; os.write(1,b'\\xff\\x00')";r=managed_run([sys.executable,"-c",code],p,{},p/"o",p/"e",p/"events",2,3);self.assertEqual(r["exit_code"],0);self.assertEqual((p/"o").read_bytes(),b"\xff\x00");self.assertEqual((p/"events").read_bytes(),b"")
 def test_fsync_failure_is_not_swallowed(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   with patch("run.os.fsync",side_effect=OSError("disk")):
    with self.assertRaises(OSError):managed_run([sys.executable,"-c","pass"],p,{},p/"o",p/"e",p/"events",2,3)
 def test_os_sandbox_denies_network_and_external_write(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();work=root/"work";work.mkdir();source=root/"snapshot";source.mkdir();(source/"discoveryworld").mkdir();profile=work/"worker.sb";profile.write_text(sandbox_profile(work,source=source));outside=root/"outside";secret=ROOT/"README.md";original=Path(SOURCE_REPO)/"discoveryworld/DiscoveryWorldAPI.py";code="import socket,subprocess;from pathlib import Path;net=write=read=original=fork=False;s=socket.socket();\ntry:s.bind(('127.0.0.1',0))\nexcept OSError:net=True\ntry:Path("+repr(str(outside))+").write_text('x')\nexcept OSError:write=True\ntry:Path("+repr(str(secret))+").read_text()\nexcept OSError:read=True\ntry:Path("+repr(str(original))+").read_text()\nexcept OSError:original=True\ntry:subprocess.run(['/usr/bin/true'],check=True)\nexcept (OSError,subprocess.SubprocessError):fork=True\nPath('inside').write_text('x');print(net,write,read,original,fork)";r=managed_run([SANDBOX_EXEC,"-f",str(profile),"/opt/homebrew/bin/python3","-c",code],work,{},work/"o",work/"e",work/"events",2,3);self.assertEqual(r["exit_code"],0,(work/"e").read_text());self.assertEqual((work/"o").read_text().strip(),"True True True True True");self.assertFalse(outside.exists());self.assertTrue((work/"inside").exists())
if __name__=="__main__":unittest.main(verbosity=2)
