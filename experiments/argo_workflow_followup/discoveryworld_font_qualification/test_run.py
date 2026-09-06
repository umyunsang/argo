#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE));import run
class Tests(unittest.TestCase):
 def test_awaiting_approval_blocks_before_consumption(self):
  approval=json.loads((ROOT/"paper/research/discoveryworld-font-registry-qualification-approval-v1.json").read_text());result=run.validate_approval(approval,ROOT);self.assertFalse(result["approved"]);self.assertIn("STATUS",result["errors"]);self.assertFalse((ROOT/"paper/research/receipts/discoveryworld-font-registry-qualification-v1.marker.json").exists())
 def test_profiles_separate_fork_boundary(self):
  pinned=run.profile("pinned",HERE,Path("/sealed/python"));native=run.profile("native",HERE,Path("/sealed/python"));self.assertNotIn("(allow process-fork)",pinned);self.assertIn("(allow process-fork)",native);self.assertNotIn("fc-list",pinned);self.assertIn('/opt/X11/bin/fc-list',native);self.assertIn("(deny default)",pinned)
 def test_font_stat_binds_symlink_and_target(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);target=root/"target";target.write_bytes(b"x");link=root/"link";link.symlink_to(target);value=run.stat_font(link);self.assertEqual(value["path_kind"],"symlink");self.assertEqual(value["resolved_target"],str(target));self.assertEqual(value["sha256"],run.sha(target))
 def test_exclusive_write(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   p=Path(td)/"x";run.exclusive(p,b"one")
   with self.assertRaises(FileExistsError):run.exclusive(p,b"two")
   self.assertEqual(p.read_bytes(),b"one")
 def test_manifest_is_two_cell_zero_scenario(self):
  value=json.loads((HERE/"manifest.json").read_text());self.assertEqual([x["mode"] for x in value["ordered_cells"]],["native","pinned"]);self.assertEqual(value["budgets"]["scenario_loads"],0);self.assertEqual(value["budgets"]["controller_hard_deadline_seconds"],120)
if __name__=="__main__":unittest.main(verbosity=2)
