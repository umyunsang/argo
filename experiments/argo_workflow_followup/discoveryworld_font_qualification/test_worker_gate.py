#!/usr/bin/env python3
import json,os,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read_line(fd):
 data=b""
 while not data.endswith(b"\n"):data+=os.read(fd,1)
 return json.loads(data)
class Tests(unittest.TestCase):
 def test_gate_registers_before_and_after_new_session(self):
  read_fd,write_fd=os.pipe();ack_read,ack_write=os.pipe();controller_read,controller_write=os.pipe()
  try:
   proc=subprocess.Popen([sys.executable,str(HERE/"worker_gate.py"),str(write_fd),str(ack_read),str(controller_read),"/usr/bin/true"],pass_fds=(write_fd,ack_read,controller_read),start_new_session=False);pre=read_line(read_fd);self.assertEqual(pre["phase"],"pre_session");self.assertNotEqual(pre["pid"],pre["pgid"]);os.write(ack_write,b"G");post=read_line(read_fd);self.assertEqual(post["phase"],"post_session");self.assertEqual(post["pid"],post["pgid"]);self.assertEqual(post["pid"],post["sid"]);os.write(controller_write,b"C");self.assertEqual(proc.wait(timeout=2),0)
  finally:
   for fd in [read_fd,write_fd,ack_read,ack_write,controller_read,controller_write]:
    try:os.close(fd)
    except OSError:pass
if __name__=="__main__":unittest.main(verbosity=2)
