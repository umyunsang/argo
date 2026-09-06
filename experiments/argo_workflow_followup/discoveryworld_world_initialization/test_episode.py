#!/usr/bin/env python3
from __future__ import annotations
import ast,math,sys,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from episode import EXPECTED_FONT_REQUESTS,digest,normalize,summarize
class Surface:
 def __init__(self,size):self.size=size
 def get_size(self):return self.size
class Window(Surface):pass
class Tests(unittest.TestCase):
 def test_normalize_is_order_stable_and_fail_closed(self):
  self.assertEqual(digest(normalize({"b":{2,1},"a":[1]})),digest(normalize({"a":[1],"b":{1,2}})))
  with self.assertRaises(RuntimeError):normalize(float("nan"))
  with self.assertRaises(RuntimeError):normalize(object())
 def test_projection_excludes_clock_value_and_hashes_loaded_state(self):
  tile={"WORLD":[]};world=types.SimpleNamespace(sizeX=2,sizeY=1,grid=[[tile,tile]],agents=[],taskScorer=types.SimpleNamespace(tasks=[]),step=0,worldHistory=[],teleportLocations={},liveUserPlaying=False,randomSeed=None,rng=None,uuidGenerator=types.SimpleNamespace(existingUUIDs=set()),spriteLibrary=types.SimpleNamespace(sprites={"b":Surface((2,3)),"a":Surface((1,1))}),objectMaker=types.SimpleNamespace(objectProperties={"x":{"v":1}},materialProperties={"m":{"v":2}},errors=[],warnings=[]),discoveryFeed=types.SimpleNamespace(articles=[],updatePosts=[],uniquePostIDs=1),startTime=123.5);api=types.SimpleNamespace(window=Window((10,20)),THREAD_ID=7,world=world,numUserAgents=0,ui=[],steps=0,agentsThatHaveActedThisStep=set(),taskProgress=[]);ui=types.SimpleNamespace(currentAgent=None,curSelectedInventoryIdx=0,showScoreToUser=False,lastActionMessage="",messageQueueText=[],dialogToDisplay=None,inModal=False,inDiscoveryFeedModal=False,curSelectedArgument1Idx=0,curSelectedArgument2Idx=0,curSelectedArgument1Obj=None,curSelectedArgument2Obj=None,argObjectsList=[],lastDiscoveryFeedPostCount=0,extendedPlayEnabled=False);out=summarize(api,world,ui,[]);self.assertEqual(out["world"]["size"],[2,1]);self.assertEqual(out["world"]["sprite_count"],2);self.assertTrue(out["world"]["start_time_is_finite"]);self.assertNotIn("startTime",str(out))
 def test_worker_call_graph_has_exact_world_constructor_and_no_forbidden_calls(self):
  tree=ast.parse((HERE/"episode.py").read_text());calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)];names=[ast.unparse(node.func) for node in calls];forbidden={"loadScenario","getAgentObservation","performAgentAction","tick","makeTask","addTask","render","renderViewport"};self.assertFalse([name for name in names if name.split(".")[-1] in forbidden]);world_call=next(node for node in calls if ast.unparse(node.func)=="World");self.assertEqual({x.arg:ast.literal_eval(x.value) for x in world_call.keywords},{"assetPath":None,"filenameSpriteIndex":"spriteIndex.json","dataPath":None,"filenameObjectData":"objects.tsv","filenameMaterialData":"materials.tsv","filenameDiscoveryFeed":"discoveryFeed.json"})
 def test_expected_font_requests_are_four_initialization_calls(self):self.assertEqual(EXPECTED_FONT_REQUESTS,[("Arial",8,False,False),("monospace",10,False,False),("monospace",15,False,False),("monospace",15,True,False)])
if __name__=="__main__":unittest.main(verbosity=2)
