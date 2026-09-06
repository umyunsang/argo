#!/usr/bin/env python3
import json,os,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_gate_registers_separate_group_before_exec(self):
  read_fd,write_fd=os.pipe()
  try:
   proc=subprocess.Popen([sys.executable,str(HERE/"worker_gate.py"),str(write_fd),"/usr/bin/true"],pass_fds=(write_fd,),start_new_session=True);os.close(write_fd);write_fd=-1;data=os.read(read_fd,4096);self.assertEqual(proc.wait(timeout=2),0);record=json.loads(data);self.assertEqual(record["schema_version"],"argo-font-worker-pgid/v1");self.assertEqual(record["source"],"gate");self.assertEqual(record["pid"],record["pgid"]);self.assertEqual(record["pid"],proc.pid)
  finally:
   os.close(read_fd)
   if write_fd>=0:os.close(write_fd)
if __name__=="__main__":unittest.main(verbosity=2)
