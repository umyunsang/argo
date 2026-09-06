#!/usr/bin/env python3
from __future__ import annotations
import ast,copy,hashlib,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from run import TASKS,REPEATS,STEPS,TIMEOUT_SECONDS,build_commands,parse_events,sanitized_env,validate_approval
R=HERE/"run.py";E=HERE/"episode.py";T=json.loads((HERE/"approval-template.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid():
 x=copy.deepcopy(T);x.update({"status":"APPROVED","approved_by":"user","runner_sha256":sha(R),"episode_sha256":sha(E)});return x
class Tests(unittest.TestCase):
 def test_unapproved(self):self.assertFalse(validate_approval(T,R,E)["approved"])
 def test_exact_approval(self):self.assertTrue(validate_approval(valid(),R,E)["approved"])
 def test_grid(self):self.assertEqual(len(TASKS),10);self.assertEqual(len({x[0] for x in TASKS}),2);self.assertEqual(len(build_commands(T["interpreter"],E)),20)
 def test_fixed_budget(self):self.assertEqual((REPEATS,STEPS,TIMEOUT_SECONDS),(2,1000,180));self.assertEqual((T["total_steps"],T["max_subprocess_wait_seconds"]),(20000,3600))
 def test_nesting(self):self.assertEqual(T["task_families"],2);self.assertNotEqual(T["task_families"],T["episodes"])
 def test_progress(self):self.assertIn("flush=True",E.read_text());self.assertIn("1000",E.read_text());self.assertEqual([x["event"] for x in parse_events('{"event":"loaded"}\n{"event":"progress","step":500}\n')],["loaded","progress"])
 def test_no_hidden_endpoint_calls(self):
  tree=ast.parse(E.read_text());calls={n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Attribute,ast.Name))};self.assertFalse(calls & {"getTask"+"Scorecard","getGold","getWorld"});self.assertNotIn('["vision"]',E.read_text())
 def test_sanitized_env(self):
  env=sanitized_env();bad=("ANTHROPIC","OPENAI","TOKEN","AWS_","AZURE_","GOOGLE_API");self.assertFalse(any(any(x in k.upper() for x in bad) for k in env))
 def test_hash_drift(self):
  x=valid();x["episode_sha256"]="0"*64;self.assertFalse(validate_approval(x,R,E)["approved"])
 def test_prior_protocols_bound(self):self.assertTrue(T["prior_failure_closure_sha256"]);self.assertTrue(T["calibration_closure_sha256"])
if __name__=="__main__":unittest.main(verbosity=2)
