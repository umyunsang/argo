#!/usr/bin/env python3
"""One sealed DiscoveryWorld official/UI-only parity cell."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,signal,socket,sys,time
from pathlib import Path
import adapter_v2,state_projection
from adapter_v2 import get_ui_only_observation
from state_projection import canonical_bytes,project_state,projection_sha256

def block_network():
    def denied(*args,**kwargs):raise OSError("NETWORK_DISABLED_BY_UI_PARITY")
    socket.create_connection=denied;original=socket.socket
    class NoNetworkSocket(original):
        def connect(self,address):raise OSError("NETWORK_DISABLED_BY_UI_PARITY")
        def connect_ex(self,address):return 1
    socket.socket=NoNetworkSocket

def write_all(fd:int,data:bytes):
    while data:
        n=os.write(fd,data)
        if n<=0:raise OSError("event fd write failed")
        data=data[n:]

def emit(fd:int,value:dict):write_all(fd,canonical_bytes(value)+b"\n")
def main():
    signal.pthread_sigmask(signal.SIG_UNBLOCK,{signal.SIGINT,signal.SIGTERM,signal.SIGHUP})
    p=argparse.ArgumentParser()
    for name in ["run-id","cell-id","cell-nonce","scenario","difficulty","mode","source-commit","source-tree","source-archive-sha256","adapter-sha256","state-projection-sha256","environment-content-sha256","bootstrap-sha256","execution-root-sha256","interpreter-sha256","frame-directory"]:p.add_argument("--"+name,required=True)
    p.add_argument("--seed",type=int,required=True);p.add_argument("--ui-fd",type=int,required=True);p.add_argument("--repeat",type=int,required=True);p.add_argument("--steps",type=int,choices=[1000],required=True);p.add_argument("--thread-id",type=int,required=True);p.add_argument("--event-fd",type=int,required=True);a=p.parse_args()
    if a.mode not in {"official","ui_only"}:raise ValueError("invalid mode")
    block_network();started=time.monotonic();import discoveryworld,numpy,pygame
    from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
    api=DiscoveryWorldAPI(threadID=a.thread_id);api.FRAME_DIR=str(Path(a.frame_directory).resolve())+"/";loaded=api.loadScenario(a.scenario,a.difficulty,a.seed,numUserAgents=1)
    if loaded is not True:raise RuntimeError("SCENARIO_LOAD_FAILED")
    emit(a.event_fd,{"event":"start","schema_version":"argo-discoveryworld-ui-parity-worker/v1","run_id":a.run_id,"cell_id":a.cell_id,"cell_nonce":a.cell_nonce,"scenario":a.scenario,"difficulty":a.difficulty,"seed":a.seed,"mode":a.mode,"repeat":a.repeat,"steps":a.steps,"thread_id":a.thread_id,"source_commit":a.source_commit,"source_tree":a.source_tree,"source_archive_sha256":a.source_archive_sha256,"adapter_sha256":a.adapter_sha256,"state_projection_sha256":a.state_projection_sha256,"environment_content_sha256":a.environment_content_sha256,"bootstrap_sha256":a.bootstrap_sha256,"execution_root_sha256":a.execution_root_sha256,"interpreter_sha256":a.interpreter_sha256,"interpreter_path":str(Path(sys.executable).resolve()),"interpreter_prefix":str(Path(sys.prefix).resolve()),"sys_path":[str(Path(value).resolve()) for value in sys.path],"numpy_module_path":str(Path(numpy.__file__).resolve()),"pygame_module_path":str(Path(pygame.__file__).resolve()),"module_path":str(Path(discoveryworld.__file__).resolve()),"adapter_module_path":str(Path(adapter_v2.__file__).resolve()),"state_projection_module_path":str(Path(state_projection.__file__).resolve())})
    raw_file=os.fdopen(a.ui_fd,"wb",closefd=False);gz=gzip.GzipFile(fileobj=raw_file,mode="wb",mtime=0);actions=ticks=0;vision_generated=False;directions=["north","east","south","west"]
    try:
        for step in range(0,a.steps+1):
            action_success=tick_success=None
            if step>0:
                action={"action":"ROTATE_DIRECTION","arg1":directions[(step-1)%4]};ar=api.performAgentAction(0,action);tr=api.tick();action_success=ar.get("success");tick_success=tr.get("success");actions+=action_success is True;ticks+=tick_success is True
            pre=project_state(api,0)
            if a.mode=="official":
                observation=api.getAgentObservation(0);vision_generated=vision_generated or bool(observation.get("vision"))
            else:observation=get_ui_only_observation(api,0)
            expected_outer={"errors","ui","vision"} if a.mode=="official" else {"errors","ui"}
            if type(observation) is not dict or set(observation)!=expected_outer or observation["errors"]!=[] or type(observation["ui"]) is not dict:raise RuntimeError("OBSERVATION_OUTER_SCHEMA")
            post=project_state(api,0);ui=observation["ui"];ui_bytes=canonical_bytes({"observation_index":step,"ui":ui});gz.write(ui_bytes+b"\n")
            emit(a.event_fd,{"event":"observation","cell_id":a.cell_id,"cell_nonce":a.cell_nonce,"observation_index":step,"world_counter":api.world.getStepCounter(),"ui_sha256":hashlib.sha256(canonical_bytes(ui)).hexdigest(),"pre_state_sha256":projection_sha256(pre),"pre_state":pre,"post_state_sha256":projection_sha256(post),"post_state":post,"action_success":action_success,"tick_success":tick_success})
    finally:
        gz.close();raw_file.flush();os.fsync(raw_file.fileno());raw_file.close()
    emit(a.event_fd,{"event":"complete","cell_id":a.cell_id,"cell_nonce":a.cell_nonce,"observations":a.steps+1,"transitions":a.steps,"action_successes":actions,"tick_successes":ticks,"start_counter":1,"end_counter":api.world.getStepCounter(),"counter_delta":api.world.getStepCounter()-1,"frame_directory":str(Path(a.frame_directory).resolve()),"vision_generated":vision_generated,"vision_consumed":False,"model_calls":0,"spend_usd":0.0})
    os.fsync(a.event_fd);return 0
if __name__=="__main__":raise SystemExit(main())
