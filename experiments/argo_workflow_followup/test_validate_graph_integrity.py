#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from validate_graph_integrity import validate
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GRAPH=ROOT/"paper/context-graph.json"
def fixture():
 root=Path(tempfile.mkdtemp());graph=json.loads(GRAPH.read_text());projection={};
 for key,value in graph["projection_inputs"].items():
  if key.endswith("_path"):
   source=ROOT/value;target=root/value;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());projection[key]=value;projection[key[:-5]+"_sha256"]=hashlib.sha256(target.read_bytes()).hexdigest()
 graph["projection_inputs"]=projection;path=root/"paper/context-graph.json";path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n");return root,path,graph
class Tests(unittest.TestCase):
 def test_fixture_baseline(self):
  root,path,graph=fixture();self.assertTrue(validate(root,path)["passed"])
 def test_dangling_and_duplicate_fail(self):
  root,path,graph=fixture();graph["nodes"].append(copy.deepcopy(graph["nodes"][0]));graph["edges"][0]["target"]="missing";path.write_text(json.dumps(graph)+"\n");errors=validate(root,path)["errors"];self.assertIn("DUPLICATE_IDS",errors);self.assertIn("DANGLING_ENDPOINT",errors)
 def test_projection_drift_and_unpaired_key_fail(self):
  root,path,graph=fixture();key=next(key for key in graph["projection_inputs"] if key.endswith("_sha256"));graph["projection_inputs"][key]="0"*64;graph["projection_inputs"]["orphan_path"]="x";path.write_text(json.dumps(graph)+"\n");errors=validate(root,path)["errors"];self.assertIn("PROJECTION_KEY_PAIR",errors);self.assertTrue(any(error.startswith("PROJECTION_HASH") for error in errors))
if __name__=="__main__":unittest.main(verbosity=2)
