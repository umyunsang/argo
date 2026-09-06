#!/usr/bin/env python3
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import bootstrap
class Tests(unittest.TestCase):
 def test_controller_inserts_only_sealed_root_first(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/"run.py").write_text("x=1")
   with patch("bootstrap.runpy.run_path") as run:bootstrap.main(["controller",str(root),"--x"]);self.assertEqual(sys.path[0],str(root.resolve()));run.assert_called_once_with(str(root.resolve()/"run.py"),run_name="__main__")
 def test_worker_root_order(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);bundle=root/"bundle";source=root/"source";site=root/"site"
   for path in [bundle,source,site]:path.mkdir()
   (bundle/"episode.py").write_text("x=1")
   with patch("bootstrap.runpy.run_path") as run:bootstrap.main(["worker",str(bundle),str(source),str(site),"--cell-id","x"]);self.assertEqual(sys.path[:3],[str(bundle.resolve()),str(source.resolve()),str(site.resolve())]);self.assertEqual(sys.argv[1:],["--cell-id","x"])
 def test_invalid_role_fails(self):
  with self.assertRaises(RuntimeError):bootstrap.main(["bad"])
if __name__=="__main__":unittest.main(verbosity=2)
