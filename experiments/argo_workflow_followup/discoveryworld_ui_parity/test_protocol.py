#!/usr/bin/env python3
from __future__ import annotations
import copy,gzip,hashlib,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from protocol import compare_pair,validate_cell
from state_projection import canonical_bytes
M=json.loads((HERE/"manifest.json").read_text());CELL=M["ordered_cells"][0]
def fixture(td,cell=CELL):
 td=Path(td);event=td/"e";ui=td/"u.gz";frame_names=[f"ui_agent_0_frame_{i}.png" for i in range(1,1002)]+["ui_agent_0_current_viewport.png"];frame={"files":[{"path":name,"size":1,"sha256":"a"*64} for name in frame_names],"count":1002,"bytes":1002};events=[{"event":"start","schema_version":"argo-discoveryworld-ui-parity-worker/v1","run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"scenario":cell["scenario"],"difficulty":cell["difficulty"],"seed":cell["seed"],"mode":cell["mode"],"repeat":cell["repeat"],"steps":1000,"thread_id":cell["thread_id"],"source_commit":"c","source_tree":"t","source_archive_sha256":"d"*64,"adapter_sha256":"e"*64,"state_projection_sha256":"f"*64,"environment_content_sha256":"1"*64,"bootstrap_sha256":"2"*64,"execution_root_sha256":"3"*64,"interpreter_sha256":"4"*64,"interpreter_path":"/runtime/base/bin/python","interpreter_prefix":"/runtime/base","sys_path":["/bundle","/snapshot","/site"],"numpy_module_path":"/site/numpy/__init__.py","pygame_module_path":"/site/pygame/__init__.py","module_path":"/snapshot/discoveryworld/__init__.py","adapter_module_path":"/bundle/adapter_v2.py","state_projection_module_path":"/bundle/state_projection.py"}];raw=[]
 for i in range(1001):
  u={"world_steps":i+1};ub=canonical_bytes(u);pre={"inModal":False,"inDiscoveryFeedModal":False,"dialog_present":False,"dialog_text":None,"dialog_options":None,"message_queue":[],"arg_object_uuids":[],"arg1_index":-1,"arg2_index":-1,"arg1_uuid":None,"arg2_uuid":None,"object_to_show_uuid":None,"task_progress":[],"api_steps":i,"world_counter":i+1};post={**pre,"api_steps":i+1};events.append({"event":"observation","cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"observation_index":i,"world_counter":i+1,"ui_sha256":hashlib.sha256(ub).hexdigest(),"pre_state_sha256":hashlib.sha256(canonical_bytes(pre)).hexdigest(),"pre_state":pre,"post_state_sha256":hashlib.sha256(canonical_bytes(post)).hexdigest(),"post_state":post,"action_success":None if i==0 else True,"tick_success":None if i==0 else True});raw.append(canonical_bytes({"observation_index":i,"ui":u})+b"\n")
 events.append({"event":"complete","cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"observations":1001,"transitions":1000,"action_successes":1000,"tick_successes":1000,"start_counter":1,"end_counter":1001,"counter_delta":1000,"frame_directory":str(Path(cell["workdir"]).resolve()/"frames"),"vision_generated":True,"vision_consumed":False,"model_calls":0,"spend_usd":0.0});event.write_bytes(b"".join(canonical_bytes(x)+b"\n" for x in events));
 with gzip.open(ui,"wb",mtime=0) if False else gzip.GzipFile(filename=str(ui),mode="wb",mtime=0) as g:
  for x in raw:g.write(x)
 run={"exit_code":0,"timed_out":False};return event,ui,frame,run
def kwargs():return {"source_commit":"c","source_tree":"t","source_archive_sha256":"d"*64,"adapter_sha256":"e"*64,"state_projection_sha256":"f"*64,"environment_content_sha256":"1"*64,"bootstrap_sha256":"2"*64,"execution_root_sha256":"3"*64,"interpreter_sha256":"4"*64,"interpreter_path":"/runtime/base/bin/python","site_packages":"/site","source_root":"/snapshot","bundle_root":"/bundle"}
class Tests(unittest.TestCase):
 def test_artifact_reader_binds_validation_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);bound={str(e):e.read_bytes(),str(u):u.read_bytes()};e.write_bytes(b"replaced");u.write_bytes(b"replaced");options=kwargs();options["artifact_reader"]=lambda path:bound[path];self.assertEqual(validate_cell(CELL,r,e,u,f,**options)["status"],"valid_complete")
 def test_valid_official(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"valid_complete")
 def test_nonzero_exit_crash(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);r["exit_code"]=1;self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"crash")
 def test_missing_observation_malformed(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_bytes().splitlines();e.write_bytes(b"\n".join(lines[:-2]+lines[-1:])+b"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_bad_counter_malformed(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();x=json.loads(lines[2]);x["world_counter"]=99;lines[2]=json.dumps(x,sort_keys=True,separators=(",",":"));e.write_text("\n".join(lines)+"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_pre_post_api_step_lag_contract(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();step0=json.loads(lines[1]);step1=json.loads(lines[2]);self.assertEqual((step0["pre_state"]["api_steps"],step0["pre_state"]["world_counter"],step0["post_state"]["api_steps"],step0["post_state"]["world_counter"]),(0,1,1,1));self.assertEqual((step1["pre_state"]["api_steps"],step1["pre_state"]["world_counter"],step1["post_state"]["api_steps"],step1["post_state"]["world_counter"]),(1,2,2,2));self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"valid_complete")
 def test_ui_hash_mismatch(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();x=json.loads(lines[1]);x["ui_sha256"]="0"*64;lines[1]=json.dumps(x,sort_keys=True,separators=(",",":"));e.write_text("\n".join(lines)+"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_official_frame_count(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);f["count"]=1;self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_ui_only_zero_frames(self):
  cell=copy.deepcopy(CELL);cell.update({"cell_id":"chemistry-s0-ui_only-r0","mode":"ui_only"})
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td,cell);f={"files":[],"count":0,"bytes":0};lines=e.read_text().splitlines();s=json.loads(lines[0]);s["cell_id"]=cell["cell_id"];s["mode"]="ui_only";lines[0]=json.dumps(s,sort_keys=True,separators=(",",":"));c=json.loads(lines[-1]);c["cell_id"]=cell["cell_id"];c["vision_generated"]=False;lines[-1]=json.dumps(c,sort_keys=True,separators=(",",":"));e.write_text("\n".join(lines)+"\n");self.assertEqual(validate_cell(cell,r,e,u,f,**kwargs())["status"],"valid_complete")
 def test_pair_enums(self):
  a={"status":"valid_complete","ui_hashes":["a"*64]*1001,"pre_state_hashes":["c"*64]*1001,"post_state_hashes":["b"*64]*1001};self.assertEqual(compare_pair(a,a),"EXACT");b=copy.deepcopy(a);b["ui_hashes"][0]="d"*64;self.assertEqual(compare_pair(a,b),"OBSERVED_MISMATCH");self.assertEqual(compare_pair(a,{"status":"timeout"}),"UNOBSERVABLE")
 def test_unknown_event_field_malformed(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();x=json.loads(lines[1]);x["unknown"]=1;lines[1]=json.dumps(x,sort_keys=True,separators=(",",":"));e.write_text("\n".join(lines)+"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_duplicate_complete_malformed(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();e.write_text("\n".join(lines+[lines[-1]])+"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
 def test_nonfinite_json_malformed(self):
  with tempfile.TemporaryDirectory() as td:
   e,u,f,r=fixture(td);lines=e.read_text().splitlines();lines[1]=lines[1].replace('"world_counter":1','"world_counter":NaN');e.write_text("\n".join(lines)+"\n");self.assertEqual(validate_cell(CELL,r,e,u,f,**kwargs())["status"],"malformed")
if __name__=="__main__":unittest.main(verbosity=2)
