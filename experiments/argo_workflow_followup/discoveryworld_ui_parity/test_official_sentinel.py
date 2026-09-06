#!/usr/bin/env python3
from __future__ import annotations
import io,sys,tempfile,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from adapter_v2 import get_ui_only_observation
from state_projection import project_state
import discoveryworld.DiscoveryWorldAPI as api_module
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from discoveryworld.UserInterface import UserInterface
class Obj:
 def __init__(self,u,name):self.uuid=u;self.name=name
 def getTextDescription(self):return self.name
class Feed:
 def getRecentPosts(self,curStep,lastNSteps):return []
 def getPosts(self):return []
class Font:
 def render(self,*args):return object()
class Scorer:tasks=[]
class World:
 def __init__(self):self.discoveryFeed=Feed();self.taskScorer=Scorer();self.counter=1
 def getStepCounter(self):return self.counter
 def renderViewport(self,*args,**kwargs):pass
class Agent:
 def __init__(self,world):self.world=world;self.attributes={"gridX":0,"gridY":0,"faceDirection":"north","objectToShow":None};self.inv=[Obj(1,"one")];self.env=[Obj(2,"two")]
 def getWorldLocation(self):return (0,0)
 def getValidDirectionsToMoveTo(self):return (["north"],[])
 def getInventory(self):return self.inv
 def getObjectsAgentFacing(self,respectContainerStatus=True):return self.env
 def getNearbyVisibleObjects(self,maxDistance,includeUUID):return ([],[],{})
 def updateLastInteractedObject(self,values):self.attributes["objectToShow"]=next((x for x in values if x in self.inv),None)
class Window:
 def fill(self,*args):pass
 def blit(self,*args):pass
 def get_height(self):return 100
 def get_width(self):return 100
class Surface:
 def __init__(self,*args):pass
 def blit(self,*args):pass
class Image:
 @staticmethod
 def save(surface,target,*args):
  if hasattr(target,"write"):target.write(b"png")
  else:Path(target).write_bytes(b"png")
class Display:
 @staticmethod
 def flip():pass
class FakePygame:Surface=Surface;image=Image;display=Display

def make_api(frame,queue,dialog):
 world=World();agent=Agent(world);ui=object.__new__(UserInterface);ui.currentAgent=agent;ui.curSelectedInventoryIdx=0;ui.curSelectedEnvironmentIdx=0;ui.curSelectedArgument1Idx=9;ui.curSelectedArgument2Idx=9;ui.curSelectedArgument1Obj=None;ui.curSelectedArgument2Obj=None;ui.argObjectsList=[];ui.dialogToDisplay=dialog;ui.messageQueueText=list(queue);ui.lastActionMessage="last";ui.inModal=False;ui.inDiscoveryFeedModal=False;ui.showScoreToUser=False;ui.fontBold=Font();ui.lastDiscoveryFeedPostCount=0;ui.extendedPlayEnabled=False;ui.renderObjectSelectionBox=lambda *a,**k:None;ui.renderTextBox=lambda *a,**k:None;ui.renderLastActionMessage=lambda *a,**k:None
 window=Window();ui.window=window;api=object.__new__(DiscoveryWorldAPI);api.numUserAgents=1;api.world=world;api.ui=[ui];api.viewportSizeX=24;api.viewportSizeY=16;api.renderScale=2.0;api.window=window;api.FRAME_DIR=str(frame)+"/";api.taskProgress=[];api.steps=0;return api
class Tests(unittest.TestCase):
 def one_case(self,queue,dialog=None):
  with tempfile.TemporaryDirectory() as td1,tempfile.TemporaryDirectory() as td2:
   official=make_api(Path(td1),queue,dialog);adapted=make_api(Path(td2),queue,dialog);old=api_module.pygame;api_module.pygame=FakePygame
   try:
    for _ in range(2):
     ro=DiscoveryWorldAPI.getAgentObservation(official,0);ra=get_ui_only_observation(adapted,0);self.assertEqual(set(ro),{"errors","ui","vision"});self.assertEqual(set(ra),{"errors","ui"});self.assertEqual(ro["errors"],[]);self.assertEqual(ra["errors"],[]);self.assertEqual(ro["ui"],ra["ui"]);self.assertEqual(project_state(official,0),project_state(adapted,0));self.assertEqual(set(ro["vision"]),{"base64_no_grid","base64_with_grid"});self.assertNotIn("vision",ra)
   finally:api_module.pygame=old
   self.assertEqual(len(list(Path(td1).glob("*.png"))),2);self.assertEqual(len(list(Path(td2).glob("*.png"))),0)
 def test_queue_0(self):self.one_case([])
 def test_queue_1(self):self.one_case(["one"])
 def test_queue_2(self):self.one_case(["one","two"])
 def test_dialog_and_queue(self):self.one_case(["one","two"],{"dialogText":"dialog","dialogOptions":["yes"]})
if __name__=="__main__":unittest.main(verbosity=2)
