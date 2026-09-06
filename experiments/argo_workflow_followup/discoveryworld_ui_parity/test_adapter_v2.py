#!/usr/bin/env python3
from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from adapter_v2 import get_ui_only_observation
class Obj:
 def __init__(self,n):self.uuid=n
class Agent:
 def __init__(self):self.objectToShow=None
 def getInventory(self):return [Obj(1)]
 def getObjectsAgentFacing(self,respectContainerStatus=True):return [Obj(2)]
class UI:
 def __init__(self,queue=None,dialog=None):self.currentAgent=Agent();self.inModal=None;self.curSelectedArgument1Idx=9;self.curSelectedArgument2Idx=9;self.curSelectedArgument1Obj=None;self.curSelectedArgument2Obj=None;self.dialogToDisplay=dialog;self.messageQueueText=list(queue or []);self.render_calls=0;self.change_calls=[];self.argObjectsList=[]
 def _filterEnvObjects(self,a,b):return b
 def _filterDuplicateObjects(self,x):return x
 def updateArgumentObjects(self,x):self.argObjectsList=x
 def changeArgumentBox(self,delta,whichBox):
  self.change_calls.append(whichBox);idx=self.curSelectedArgument1Idx if whichBox==1 else self.curSelectedArgument2Idx;obj=self.argObjectsList[idx] if 0<=idx<len(self.argObjectsList) else None
  if whichBox==1:self.curSelectedArgument1Obj=obj
  else:self.curSelectedArgument2Obj=obj
  self.currentAgent.objectToShow=self.curSelectedArgument1Obj
 def renderJSON(self):
  self.render_calls+=1;message=self.messageQueueText.pop(0) if self.messageQueueText else "";return {"taskProgress":[],"world_steps":7,"extended_action_message":message,"dialog_box":{"is_in_dialog":self.dialogToDisplay is not None}}
class API:
 def __init__(self,queue=None,dialog=None):self.numUserAgents=1;self.world=object();self.ui=[UI(queue,dialog)];self.taskProgress=None;self.steps=None
class Tests(unittest.TestCase):
 def test_source_mirrored_updates(self):
  a=API();r=get_ui_only_observation(a,0);u=a.ui[0];self.assertEqual((u.render_calls,u.change_calls,u.curSelectedArgument1Idx,u.curSelectedArgument2Idx),(1,[1,2],1,1));self.assertEqual((a.taskProgress,a.steps),([],7));self.assertEqual(r["errors"],[])
 def test_queue_modal_and_single_pop(self):
  a=API(["one","two"]);r=get_ui_only_observation(a,0);self.assertTrue(a.ui[0].inModal);self.assertEqual((r["ui"]["extended_action_message"],a.ui[0].messageQueueText),("one",["two"]))
 def test_dialog_not_modal_and_preserved(self):
  a=API(["one"],{"dialogText":"x","dialogOptions":[]});r=get_ui_only_observation(a,0);self.assertFalse(a.ui[0].inModal);self.assertTrue(r["ui"]["dialog_box"]["is_in_dialog"])
 def test_invalid_agent_no_mutation(self):self.assertTrue(get_ui_only_observation(API(),2)["errors"])
 def test_uninitialized_no_render(self):
  a=API();a.world=None;r=get_ui_only_observation(a,0);self.assertTrue(r["errors"]);self.assertEqual(a.ui[0].render_calls,0)
if __name__=="__main__":unittest.main(verbosity=2)
