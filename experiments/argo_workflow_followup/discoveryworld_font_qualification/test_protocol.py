#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,tempfile,unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from protocol import compare,validate_event
H="a"*64;IDENTITY={"source_commit":"c","source_tree":"t","source_archive_sha256":H,"pygame_sysfont_sha256":H,"font_manifest_sha256":H,"python_executable":"/python","pygame_sysfont_path":"/sysfont.py","episode_path":"/episode.py","episode_sha256":H,"font_registry_path":"/font_registry.py","font_registry_sha256":H};CALLS=[]
for source,line,name,size,bold in [("discoveryworld/World.py",63,"Arial",8,False),("discoveryworld/World.py",552,"monospace",15,True),("discoveryworld/UserInterface.py",21,"monospace",10,False),("discoveryworld/UserInterface.py",22,"monospace",15,False),("discoveryworld/UserInterface.py",23,"monospace",15,True)]:CALLS.append({"source":source,"line":line,"name":name,"size":size,"bold":bold,"italic":False,"resolved_path":"/font","font_sha256":H,"samples":[{"sample":x,"size":[1,2],"metrics":[[1,2,3,4,5] for _ in x],"render_rgba_sha256":H} for x in ["ARGO 0123","한글 ARGO"]]})
FM={"calls":[{k:v for k,v in row.items() if k in {"source","line","name","size","bold","italic"}} for row in CALLS]}
def event(mode):return {"schema_version":"argo-font-qualification-cell/v1","mode":mode,**IDENTITY,"calls":copy.deepcopy(CALLS),"font_discovery_subprocesses":[["/usr/X11/bin/fc-list",":","file","family","style"]] if mode=="native" else [],"os_fork_denied":None if mode=="native" else True,"scenario_loads":0,"agent_observations":0,"model_calls":0,"spend_usd":0.0}
class Tests(unittest.TestCase):
 def check(self,value,mode="native",suffix=b"\n"):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   p=Path(td)/"event";p.write_bytes(json.dumps(value,separators=(",",":"),ensure_ascii=False).encode()+suffix);return validate_event(p,mode,FM,IDENTITY)
 def test_valid_both(self):self.assertTrue(self.check(event("native"))["passed"]);self.assertTrue(self.check(event("pinned"),"pinned")["passed"])
 def test_extra_and_wrong_mode_fail(self):v=event("native");v["extra"]=1;self.assertFalse(self.check(v)["passed"]);self.assertFalse(self.check(event("pinned"))["passed"])
 def test_no_multiple_truncated_fail(self):self.assertFalse(self.check(event("native"),suffix=b"")["passed"]);self.assertFalse(self.check(event("native"),suffix=b"\n{}\n")["passed"])
 def test_wrong_process_or_scope_fail(self):v=event("pinned");v["font_discovery_subprocesses"]=[["x"]];self.assertFalse(self.check(v,"pinned")["passed"]);v=event("native");v["scenario_loads"]=1;self.assertFalse(self.check(v)["passed"])
 def test_call_sample_schema_fail(self):v=event("native");v["calls"][0]["samples"][0]["metrics"]=[None];self.assertFalse(self.check(v)["passed"])
 def test_compare_exact(self):n=event("native");p=event("pinned");self.assertTrue(compare(n,p)["passed"]);p["calls"][2]["samples"][0]["size"]=[2,2];self.assertFalse(compare(n,p)["passed"])
if __name__=="__main__":unittest.main(verbosity=2)
