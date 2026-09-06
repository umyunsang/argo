#!/usr/bin/env python3
from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from state_projection import canonical_bytes,project_state,projection_sha256
class O:
 def __init__(self,u):self.uuid=u
class W:
 def getStepCounter(self):return 7
class U:
 inModal=True;inDiscoveryFeedModal=False;dialogToDisplay={"dialogText":"d","dialogOptions":["x"]};messageQueueText=["m"];argObjectsList=[O(2),O(1)];curSelectedArgument1Idx=0;curSelectedArgument2Idx=1;curSelectedArgument1Obj=argObjectsList[0];curSelectedArgument2Obj=argObjectsList[1]
 def __init__(self):self.currentAgent=type("A",(),{"attributes":{"objectToShow":O(1)}})()
class A:
 def __init__(self):self.ui=[U()];self.taskProgress=[{"completed":False}];self.steps=7;self.world=W()
class Tests(unittest.TestCase):
 def test_exact_fields(self):self.assertEqual(set(project_state(A(),0)),{"inModal","inDiscoveryFeedModal","dialog_present","dialog_text","dialog_options","message_queue","arg_object_uuids","arg1_index","arg2_index","arg1_uuid","arg2_uuid","object_to_show_uuid","task_progress","api_steps","world_counter"})
 def test_order_preserved(self):self.assertEqual(project_state(A(),0)["arg_object_uuids"],[2,1])
 def test_canonical_utf8(self):self.assertEqual(canonical_bytes({"b":"한","a":1}),'{"a":1,"b":"한"}'.encode())
 def test_hash_stable(self):self.assertEqual(projection_sha256(project_state(A(),0)),projection_sha256(project_state(A(),0)))
if __name__=="__main__":unittest.main(verbosity=2)
