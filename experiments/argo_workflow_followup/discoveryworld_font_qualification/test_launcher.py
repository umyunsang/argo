#!/usr/bin/env python3
from __future__ import annotations
import json,os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE));import launcher,run
class Tests(unittest.TestCase):
 def test_awaiting_canonical_approval_blocked(self):
  path=ROOT/launcher.APPROVAL_REL;value=json.loads(path.read_text());self.assertFalse(launcher.validate(value,path,ROOT))
 def test_execution_key_agreement(self):self.assertEqual(set(launcher.EXEC_KEYS),set(run.EXEC_KEYS));self.assertEqual(launcher.EXEC_NAMES["launcher"],"launcher.py")
 def test_root_formula_agreement(self):
  value=json.loads((ROOT/launcher.APPROVAL_REL).read_text());proposal=json.loads((ROOT/value["bindings"]["proposal"]["path"]).read_text());self.assertEqual(launcher.execution_root(value),run.execution_root(value));self.assertEqual(launcher.authority_root(value,proposal),run.authority_root(value,proposal));self.assertEqual(launcher.required_text(value,"e","a"),run.approval_text(value,"e","a"))
 def test_supervisor_enforces_hard_deadline(self):
  read_fd,write_fd=os.pipe();os.close(write_fd);proc=subprocess.Popen([sys.executable,"-c","import time;time.sleep(10)"],start_new_session=True);started=time.monotonic()
  try:out=launcher.supervise_process(proc,started,read_fd,.1)
  finally:os.close(read_fd)
  self.assertTrue(out["timed_out"]);self.assertFalse(out["unreaped"]);self.assertFalse(out["descendant_leak"]);self.assertTrue(out["registry_eof"]);self.assertEqual(out["controller_exit_code"],124)
 def test_supervisor_tracks_and_kills_separate_worker_group(self):
  read_fd,write_fd=os.pipe();code="import os,subprocess,sys,time;fd=int(sys.argv[1]);subprocess.Popen([sys.executable,sys.argv[2],str(fd),sys.executable,'-c','import time;time.sleep(10)'],pass_fds=(fd,),start_new_session=True);os.close(fd);time.sleep(10)";proc=subprocess.Popen([sys.executable,"-c",code,str(write_fd),str(HERE/"worker_gate.py")],pass_fds=(write_fd,),start_new_session=True);os.close(write_fd)
  try:out=launcher.supervise_process(proc,time.monotonic(),read_fd,.2)
  finally:os.close(read_fd)
  self.assertTrue(out["timed_out"]);self.assertEqual(len(out["worker_pgids"]),1);self.assertTrue(out["descendant_leak"]);self.assertFalse(out["unreaped"])
 def test_supervisor_interrupt_callback_cleans_controller(self):
  read_fd,write_fd=os.pipe();os.close(write_fd);proc=subprocess.Popen([sys.executable,"-c","import time;time.sleep(10)"],start_new_session=True);calls=[0]
  def stop():calls[0]+=1;return 15 if calls[0]>1 else None
  try:out=launcher.supervise_process(proc,time.monotonic(),read_fd,2,stop_signal=stop)
  finally:os.close(read_fd)
  self.assertTrue(out["interrupted"]);self.assertFalse(out["unreaped"]);self.assertEqual(out["controller_exit_code"],130)
 def test_read_once_rejects_symlink(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);target=root/"t";target.write_text("x");link=root/"l";link.symlink_to(target)
   with self.assertRaises(OSError):launcher.read_once(link)
if __name__=="__main__":unittest.main(verbosity=2)
