#!/usr/bin/env python3
from __future__ import annotations
import ast,copy,hashlib,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from run import TASKS,HORIZONS,REPEATS,TIMEOUT_SECONDS,build_commands,parse_events,sanitized_env,validate_approval
RUNNER=HERE/"run.py";EPISODE=HERE/"episode.py";TEMPLATE=json.loads((HERE/"approval-template.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid():
 x=copy.deepcopy(TEMPLATE);x.update({"status":"APPROVED","approved_by":"user","runner_sha256":sha(RUNNER),"episode_sha256":sha(EPISODE)});return x
class Tests(unittest.TestCase):
 def test_unapproved_fails(self):self.assertFalse(validate_approval(TEMPLATE,RUNNER,EPISODE)["approved"])
 def test_exact_approval_passes(self):self.assertTrue(validate_approval(valid(),RUNNER,EPISODE)["approved"])
 def test_grid(self):self.assertEqual((len(TASKS),HORIZONS,REPEATS),(2,[10,50,100],2));self.assertEqual(len(build_commands(TEMPLATE["interpreter"],EPISODE)),12);self.assertEqual(TEMPLATE["planned_steps"],640)
 def test_timeout(self):self.assertEqual(TIMEOUT_SECONDS,60);self.assertEqual(TEMPLATE["max_subprocess_wait_seconds"],720)
 def test_inference_units(self):self.assertEqual(TEMPLATE["task_families"],2);self.assertNotEqual(TEMPLATE["task_families"],TEMPLATE["episodes"])
 def test_sanitized_env(self):
  env=sanitized_env();bad=("ANTHROPIC","OPENAI","TOKEN","AWS_","AZURE_","GOOGLE_API");self.assertFalse(any(any(x in k.upper() for x in bad) for k in env));self.assertEqual(env["PYTHONHASHSEED"],"0")
 def test_progress_parser_keeps_partial(self):
  events=parse_events('{"event":"loaded"}\n{"event":"progress","step":10}\n');self.assertEqual([x["event"] for x in events],["loaded","progress"])
 def test_episode_flushes_progress(self):self.assertIn("flush=True",EPISODE.read_text());self.assertIn('"event":"progress"',EPISODE.read_text())
 def test_no_scorer_vision_or_gold_calls(self):
  tree=ast.parse(EPISODE.read_text());calls={n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Attribute,ast.Name))};self.assertFalse(calls & {"getTask"+"Scorecard","getGold","getWorld"});self.assertNotIn('["vision"]',EPISODE.read_text())
 def test_hash_drift(self):
  x=valid();x["runner_sha256"]="0"*64;self.assertFalse(validate_approval(x,RUNNER,EPISODE)["approved"])
if __name__=="__main__":unittest.main(verbosity=2)
