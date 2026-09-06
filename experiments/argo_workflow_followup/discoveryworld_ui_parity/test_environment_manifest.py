#!/usr/bin/env python3
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from environment_manifest import build_manifest,copy_and_verify,scan,verify_root
class Tests(unittest.TestCase):
 def fixture(self,root):
  a=root/"a";b=root/"b";a.mkdir();b.mkdir();(a/"x.py").write_text("x");(a/"__pycache__").mkdir();(a/"__pycache__/x.pyc").write_bytes(b"volatile");(b/"y.bin").write_bytes(b"y");return build_manifest([("base",a,"base"),("site",b,"site")]),a,b
 def test_copy_and_verify(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);manifest,a,b=self.fixture(root);copied=copy_and_verify(manifest,root/"sealed");self.assertTrue(verify_root(manifest["roots"][0],copied["base"]));self.assertFalse((copied["base"]/"__pycache__").exists())
 def test_live_mutation_after_copy_does_not_change_sealed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);manifest,a,b=self.fixture(root);copied=copy_and_verify(manifest,root/"sealed");a.joinpath("x.py").write_text("changed");self.assertFalse(verify_root(manifest["roots"][0]));self.assertTrue(verify_root(manifest["roots"][0],copied["base"]))
 def test_mutation_and_extra_file_fail(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);manifest,a,b=self.fixture(root);(a/"x.py").write_text("changed");self.assertFalse(verify_root(manifest["roots"][0]));(a/"x.py").write_text("x");(a/"extra").write_text("z");self.assertFalse(verify_root(manifest["roots"][0]))
 def test_escaping_symlink_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);inside=root/"inside";inside.mkdir();(inside/"escape").symlink_to("/etc/passwd")
   with self.assertRaises(RuntimeError):scan(inside)
 def test_manifest_is_canonical_and_exact(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);manifest,a,b=self.fixture(root);self.assertEqual([x["path"] for x in manifest["roots"][0]["entries"]],["x.py"]);self.assertEqual(manifest["schema_version"],"argo-ui-parity-environment-content/v1")
if __name__=="__main__":unittest.main(verbosity=2)
