#!/usr/bin/env python3
from __future__ import annotations
import json,os,sys,tempfile,time,unittest
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from process_control import group_exists,run_process
class Tests(unittest.TestCase):
 def paths(self,root):return root/"o",root/"e",root/"v"
 def test_controller_registers_worker_pgid_before_callback(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root);read_fd,write_fd=os.pipe();seen=[]
   try:r=run_process(["/usr/bin/true"],root,dict(os.environ),o,e,v,2,time.monotonic()+3,on_spawn=lambda pid,pgid:seen.append((pid,pgid)),supervisor_fd=write_fd);record=json.loads(os.read(read_fd,4096));self.assertEqual(record["source"],"controller");self.assertEqual((record["pid"],record["pgid"]),seen[0]);self.assertEqual(record["sid"],record["pgid"])
   finally:os.close(read_fd);os.close(write_fd)
 def test_success_and_event_fd(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root);r=run_process([sys.executable,"-c","import os,sys;os.write(int(sys.argv[1]),b'{}\\n')","{EVENT_FD}"],root,dict(os.environ),o,e,v,2,time.monotonic()+3);self.assertEqual(r["exit_code"],0);self.assertEqual(v.read_bytes(),b"{}\n");self.assertFalse(group_exists(r["pgid"]))
 def test_signal_callback_kills_group(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root);calls=[0]
   def stop():calls[0]+=1;return 15 if calls[0]>2 else None
   r=run_process([sys.executable,"-c","import time;time.sleep(10)"],root,dict(os.environ),o,e,v,2,time.monotonic()+3,stop_signal=stop);self.assertEqual(r["exit_code"],130);self.assertEqual(r["controller_signal"],15);self.assertFalse(group_exists(r["pgid"]))
 def test_unreaped_is_exception(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root)
   with patch("process_control.group_exists",return_value=True),patch("process_control.terminate_group",return_value=True):
    with self.assertRaisesRegex(RuntimeError,"UNREAPED"):run_process([sys.executable,"-c","pass"],root,dict(os.environ),o,e,v,1,time.monotonic()+2)
 def test_timeout_kills_group(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root);code="import subprocess,time,sys;subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)']);time.sleep(10)";r=run_process([sys.executable,"-c",code],root,dict(os.environ),o,e,v,.2,time.monotonic()+2);self.assertEqual(r["exit_code"],124);self.assertFalse(r["unreaped"]);self.assertFalse(group_exists(r["pgid"]))
 def test_global_deadline_before_files(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root)
   with self.assertRaises(TimeoutError):run_process([sys.executable,"-c","pass"],root,dict(os.environ),o,e,v,1,time.monotonic()-1)
   self.assertFalse(o.exists())
 def test_exclusive_outputs(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);o,e,v=self.paths(root);o.write_text("x")
   with self.assertRaises(FileExistsError):run_process([sys.executable,"-c","pass"],root,dict(os.environ),o,e,v,1,time.monotonic()+2)
if __name__=="__main__":unittest.main(verbosity=2)
