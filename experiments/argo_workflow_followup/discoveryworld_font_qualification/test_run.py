#!/usr/bin/env python3
from __future__ import annotations
import json,os,signal,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE));import run
class Tests(unittest.TestCase):
 def test_awaiting_approval_blocks_before_consumption(self):
  approval=json.loads((ROOT/"paper/research/discoveryworld-font-registry-qualification-approval-v1.json").read_text());result=run.validate_approval(approval,ROOT);self.assertFalse(result["approved"]);self.assertIn("STATUS",result["errors"]);self.assertFalse((ROOT/"paper/research/receipts/discoveryworld-font-registry-qualification-v1.marker.json").exists())
 def test_profiles_separate_fork_boundary(self):
  pinned=run.profile("pinned",HERE,Path("/sealed/python"));native=run.profile("native",HERE,Path("/sealed/python"));self.assertNotIn("(allow process-fork)",pinned);self.assertIn("(allow process-fork)",native);self.assertNotIn("fc-list",pinned);self.assertIn('/usr/bin/true',pinned);self.assertIn('/opt/X11/bin/fc-list',native);self.assertIn("(deny default)",pinned)
 def test_atomic_publish_never_replaces_final(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);pending=root/"pending";final=root/"final";final.write_bytes(b"old")
   with self.assertRaises(FileExistsError):run.atomic_publish(pending,final,b"new")
   self.assertEqual(final.read_bytes(),b"old")
 def test_output_preflight_rejects_symlink_parent(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);real=root/"real";real.mkdir();link=root/"link";link.symlink_to(real);out=run.output_preflight([link/"out"],root);self.assertFalse(out["passed"])
 def test_font_stat_binds_symlink_and_target(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);target=root/"target";target.write_bytes(b"x");link=root/"link";link.symlink_to(target);value=run.stat_font(link);self.assertEqual(value["path_kind"],"symlink");self.assertEqual(value["resolved_target"],str(target));self.assertEqual(value["sha256"],run.sha(target))
 def test_exclusive_write(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   p=Path(td)/"x";run.exclusive(p,b"one")
   with self.assertRaises(FileExistsError):run.exclusive(p,b"two")
   self.assertEqual(p.read_bytes(),b"one")
 def test_late_blocked_signal_is_consumed_by_latch_before_handler_restore(self):
  latch=run.SignalLatch();latch.install();latch.block_for_closure();os.kill(os.getpid(),signal.SIGTERM);self.assertTrue(latch.closure_pending());self.assertTrue(latch.restore())
 def test_runtime_destination_is_shared_base_python(self):
  environment=json.loads((HERE/"environment-content-manifest.json").read_text());base,site=run.runtime_paths(Path("/sealed"),environment);self.assertEqual(base,Path("/sealed/runtime/base-python"));self.assertEqual(site,Path("/sealed/runtime/site-packages"))
 def test_sysfont_hash_three_way_invariant(self):
  font=json.loads((ROOT/"paper/research/discoveryworld-pinned-font-manifest-v1.json").read_text());environment=json.loads((HERE/"environment-content-manifest.json").read_text());entry=next(x for spec in environment["roots"] if spec["name"]=="site_packages" for x in spec["entries"] if x.get("path")=="pygame/sysfont.py");self.assertEqual(run.SYSFONT_SHA,font["source"]["pygame_sysfont_sha256"]);self.assertEqual(run.SYSFONT_SHA,entry["sha256"])
 def test_execution_root_binds_runtime_paths_and_hashes(self):
  approval=json.loads((ROOT/"paper/research/discoveryworld-font-registry-qualification-approval-v1.json").read_text());material=run.execution_material(approval)
  for key in ["source_commit","source_tree","source_archive_sha256","worker_interpreter","worker_interpreter_sha256","controller_interpreter","controller_interpreter_sha256","sandbox_exec","sandbox_exec_sha256"]:self.assertIn(key,material)
 def test_manifest_is_two_cell_zero_scenario(self):
  value=json.loads((HERE/"manifest.json").read_text());self.assertEqual([x["mode"] for x in value["ordered_cells"]],["native","pinned"]);self.assertEqual(value["budgets"]["scenario_loads"],0);self.assertEqual(value["budgets"]["controller_hard_deadline_seconds"],120)
if __name__=="__main__":unittest.main(verbosity=2)
