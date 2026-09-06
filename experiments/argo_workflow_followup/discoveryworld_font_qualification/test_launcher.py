#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE));import launcher,run
class Tests(unittest.TestCase):
 def test_awaiting_canonical_approval_blocked(self):
  path=ROOT/launcher.APPROVAL_REL;value=json.loads(path.read_text());self.assertFalse(launcher.validate(value,path,ROOT))
 def test_execution_key_agreement(self):self.assertEqual(set(launcher.EXEC_KEYS),set(run.EXEC_KEYS));self.assertEqual(launcher.EXEC_NAMES["launcher"],"launcher.py")
 def test_root_formula_agreement(self):
  value=json.loads((ROOT/launcher.APPROVAL_REL).read_text());proposal=json.loads((ROOT/value["bindings"]["proposal"]["path"]).read_text());self.assertEqual(launcher.execution_root(value),run.execution_root(value));self.assertEqual(launcher.authority_root(value,proposal),run.authority_root(value,proposal));self.assertEqual(launcher.required_text(value,"e","a"),run.approval_text(value,"e","a"))
 def test_read_once_rejects_symlink(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);target=root/"t";target.write_text("x");link=root/"l";link.symlink_to(target)
   with self.assertRaises(OSError):launcher.read_once(link)
if __name__=="__main__":unittest.main(verbosity=2)
