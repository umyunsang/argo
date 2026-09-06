#!/usr/bin/env python3
from __future__ import annotations
import copy,json,sys,tempfile,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from font_registry import EXPECTED_CENSUS,configure,scan_calls,validate_manifest
SOURCE=Path("/Users/um-yunsang/.cache/argo-research/DiscoveryWorld");MANIFEST=ROOT/"paper/research/discoveryworld-pinned-font-manifest-v1.json"
class Sysfont:
 def __init__(self):self.Sysfonts={"old":{}};self.Sysalias={"old":{}};self.is_init=False
class Tests(unittest.TestCase):
 def test_alias_keyword_dynamic_calls_are_visible(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);(root/"x.py").write_text("from pygame.font import SysFont as SF\nSF(name='Arial', size=8)\ngetattr(pygame.font, 'SysFont')('Arial', 8)\n");rows=scan_calls(root);self.assertEqual(len(rows),2);self.assertEqual({row[2] for row in rows},{"SF","getattr.SysFont"});self.assertEqual(rows[0][3:5],("Arial",8))
 def test_source_call_census(self):self.assertEqual(scan_calls(SOURCE),EXPECTED_CENSUS)
 def test_current_manifest(self):self.assertTrue(validate_manifest(json.loads(MANIFEST.read_text()),SOURCE)["passed"])
 def test_hash_drift_fails(self):
  value=json.loads(MANIFEST.read_text());value["calls"][0]["sha256"]="0"*64;self.assertFalse(validate_manifest(value,SOURCE)["passed"])
 def test_configure_exact_registry_without_discovery(self):
  module=types.SimpleNamespace(sysfont=Sysfont());value=json.loads(MANIFEST.read_text());result=configure(module,value,SOURCE);self.assertTrue(module.sysfont.is_init);self.assertEqual(set(module.sysfont.Sysfonts),{"arial"});self.assertEqual(set(module.sysfont.Sysalias),{"monospace"});self.assertEqual(result["arial"][(False,False)],value["calls"][0]["resolved_path"])
if __name__=="__main__":unittest.main(verbosity=2)
