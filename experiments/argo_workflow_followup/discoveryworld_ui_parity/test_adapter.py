#!/usr/bin/env python3
from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from adapter import get_ui_only_observation
class World:pass
class FakeUI:
 def __init__(self,queue,dialog=False):self.queue=list(queue);self.calls=0;self.dialog=dialog
 def renderJSON(self):
  self.calls+=1;message=self.queue.pop(0) if self.queue else "";return {"taskProgress":[],"world_steps":7,"extended_action_message":message,"dialog_box":{"is_in_dialog":self.dialog}}
class API:
 def __init__(self,queue,dialog=False):self.numUserAgents=1;self.world=World();self.ui=[FakeUI(queue,dialog)];self.taskProgress=None;self.steps=None
class Tests(unittest.TestCase):
 def test_empty_queue_single_read(self):
  a=API([]);r=get_ui_only_observation(a,0);self.assertEqual((a.ui[0].calls,r["ui"]["extended_action_message"]),(1,""))
 def test_one_item_queue_pops_once(self):
  a=API(["one"]);r=get_ui_only_observation(a,0);self.assertEqual((a.ui[0].calls,r["ui"]["extended_action_message"],a.ui[0].queue),(1,"one",[]))
 def test_two_item_queue_transitions(self):
  a=API(["one","two"]);r1=get_ui_only_observation(a,0);self.assertEqual(a.ui[0].queue,["two"]);r2=get_ui_only_observation(a,0);self.assertEqual((r1["ui"]["extended_action_message"],r2["ui"]["extended_action_message"],a.ui[0].queue),("one","two",[]))
 def test_dialog_preserved(self):
  a=API([],True);self.assertTrue(get_ui_only_observation(a,0)["ui"]["dialog_box"]["is_in_dialog"])
 def test_updates_api_projection(self):
  a=API([]);get_ui_only_observation(a,0);self.assertEqual((a.taskProgress,a.steps),([],7))
if __name__=="__main__":unittest.main(verbosity=2)
