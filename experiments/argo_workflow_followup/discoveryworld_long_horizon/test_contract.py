#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
from run import TASKS,REPEATS,STEPS,EPISODE_TIMEOUT_SECONDS,build_commands,sanitized_env,validate_approval
RUNNER=HERE/"run.py";EPISODE=HERE/"episode.py";TEMPLATE=json.loads((HERE/"approval-template.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid():
 x=copy.deepcopy(TEMPLATE);x.update({"status":"APPROVED","approved_by":"user","runner_sha256":sha(RUNNER),"episode_sha256":sha(EPISODE)});return x
class Tests(unittest.TestCase):
 def test_unapproved_fails(self):self.assertFalse(validate_approval(TEMPLATE,RUNNER,EPISODE)["approved"])
 def test_exact_approval_passes(self):self.assertTrue(validate_approval(valid(),RUNNER,EPISODE)["approved"])
 def test_grid_is_two_families_ten_tasks_twenty_episodes(self):
  self.assertEqual(len({x[0] for x in TASKS}),2);self.assertEqual(len(TASKS),10);self.assertEqual(len(build_commands(TEMPLATE["interpreter"],EPISODE)),20)
 def test_fixed_counts(self):self.assertEqual((REPEATS,STEPS,EPISODE_TIMEOUT_SECONDS),(2,1000,120));self.assertEqual(TEMPLATE["total_steps"],20000)
 def test_seed_rows_not_inference_units(self):self.assertEqual(TEMPLATE["task_families"],2);self.assertNotEqual(TEMPLATE["task_families"],TEMPLATE["episodes"])
 def test_sanitized_environment_has_no_credentials(self):
  env=sanitized_env();forbidden=("ANTHROPIC","OPENAI","TOKEN","AWS_","AZURE_","GOOGLE_API");self.assertFalse(any(any(t in k.upper() for t in forbidden) for k in env));self.assertEqual(env["PYTHONHASHSEED"],"0")
 def test_episode_source_has_no_hidden_scorer_access(self):
  import ast
  tree=ast.parse(EPISODE.read_text());calls={node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,(ast.Attribute,ast.Name))};forbidden={"getTask"+"Scorecard","getTask"+"Score","getGold","getWorld"};self.assertFalse(calls & forbidden)
 def test_episode_excludes_vision_and_blocks_network(self):
  text=EPISODE.read_text();self.assertIn("block_network()",text);self.assertIn('"vision_accessed":False',text);self.assertNotIn('["vision"]',text)
 def test_hash_drift_fails(self):
  x=valid();x["episode_sha256"]="0"*64;self.assertFalse(validate_approval(x,RUNNER,EPISODE)["approved"])
if __name__=="__main__":unittest.main(verbosity=2)
