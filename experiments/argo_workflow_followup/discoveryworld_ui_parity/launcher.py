#!/usr/bin/env python3
"""Pin and seal the canonical UI-parity controller before any project import."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,tempfile
from pathlib import Path
ENGINE_REPO='/Users/um-yunsang/argo-paper-orx'
APPROVAL_REL='experiments/argo_workflow_followup/discoveryworld_ui_parity/approval-template.json'
DESIGN_REL='paper/research/discoveryworld-ui-adapter-parity-design.json'
PROPOSAL_REL='paper/research/discoveryworld-ui-adapter-parity-proposal.json'
CONTROLLER_INTERPRETER='/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/bin/python3.14'
CONTROLLER_INTERPRETER_SHA256='2477b47fa3ae65b9574eb18a15edb364e96948eaa1875ad3f1c80d780efc9c12'
PINNED={"adapter":{"name":"adapter_v2.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/adapter_v2.py","sha256":"66eaa5f4fef10485d48356ec23ed1290683cd468c61ac3624479c1f2d76309c7"},"admission_consumer":{"name":"admit_result.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/admit_result.py","sha256":"4b6c57d54a5182789e63653ee4d62989930100a0eebfed2adb846070316ee098"},"bootstrap":{"name":"bootstrap.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/bootstrap.py","sha256":"0569046a5169bcd5f414fb0dbfcd25b7db29610ecae1356dc34dd84ec2680c74"},"environment_content_manifest":{"name":"environment-content-manifest.json","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/environment-content-manifest.json","sha256":"5fbf583227ace63e4e298b4d6692ce6f558e51acdb73cb571c9c6ec85a3b8629"},"environment_manifest_module":{"name":"environment_manifest.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/environment_manifest.py","sha256":"e04c2355b38a81e19c37ed91fa18262194ccd66063dba2a3e9c4274f6ca9bc17"},"episode":{"name":"episode.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/episode.py","sha256":"54c4bc76b75e98270ef8211bdc5dd0bc4e22ddaa6a1103b67f9d1183ff0f4be9"},"lifecycle":{"name":"lifecycle.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/lifecycle.py","sha256":"14b039a05eea6aec2698a7181fd099b630e2da52aa46a6c7f934ac2db61dc234"},"manifest":{"name":"manifest.json","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/manifest.json","sha256":"df677548830cc7d409c7f3c2a898ba90676fd9b482ad12e8695cfdf4537615ca"},"protocol":{"name":"protocol.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/protocol.py","sha256":"5af6a717351df630714b333989c294858d768c9c355b3bc4362c524ae1ae9144"},"result_verifier":{"name":"verify_result.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/verify_result.py","sha256":"442a19a37bcfabb84d289c0180156930dc76a73ce84c70ee73161f850fa78ce0"},"runner":{"name":"run.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/run.py","sha256":"9e182fdf3b0bb5134725ad11caf1a6e443940a7e6567995dc080a7277f94844d"},"schemas":{"name":"schemas.json","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/schemas.json","sha256":"8cefc68e775aeb6c0f9d06bc85a751a2426a40f3bca9ce9400c7fd5fd9b265bf"},"state_projection":{"name":"state_projection.py","path":"experiments/argo_workflow_followup/discoveryworld_ui_parity/state_projection.py","sha256":"46ac3d488b8ac7c1f719b30db8c73fea61adb24af817acc1280845649bbaf8e0"}}
EXECUTION_KEYS=("runner","lifecycle","protocol","episode","adapter","state_projection","manifest","schemas","launcher","bootstrap","environment_manifest_module","environment_content_manifest","result_verifier","admission_consumer")
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def read_once(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  st=os.fstat(fd)
  if not stat.S_ISREG(st.st_mode):raise RuntimeError("NOT_REGULAR:"+str(path))
  chunks=[]
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   chunks.append(chunk)
  return b"".join(chunks)
 finally:os.close(fd)
def write_once(path,data,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 try:
  view=memoryview(data)
  while view:
   written=os.write(fd,view)
   if written<=0:raise OSError("short write")
   view=view[written:]
  os.fsync(fd)
 finally:os.close(fd)
def execution_root(approval,self_sha):
 hashes={key:(self_sha if key=="launcher" else PINNED[key]["sha256"]) for key in EXECUTION_KEYS}
 return hashlib.sha256(canonical(hashes)).hexdigest()
def proposal_core_sha(proposal):
 value=dict(proposal);value.pop("required_approval_text",None);return sha_bytes(canonical(value))
def authority_root(approval,proposal,self_sha):
 hashes={key:(self_sha if key=="launcher" else PINNED[key]["sha256"]) for key in EXECUTION_KEYS};hashes.update({"design":approval.get("bindings",{}).get("design",{}).get("sha256"),"proposal_core":proposal_core_sha(proposal)});return sha_bytes(canonical(hashes))
def validate_canonical_approval(approval,approval_path,root,self_sha):
 if Path(root).resolve()!=Path(ENGINE_REPO) or Path(approval_path).resolve()!=Path(root,APPROVAL_REL).resolve():return False
 if sha_bytes(read_once(CONTROLLER_INTERPRETER))!=CONTROLLER_INTERPRETER_SHA256:return False
 for key,spec in PINNED.items():
  if approval.get("bindings",{}).get(key)!={"path":spec["path"],"sha256":spec["sha256"]}:return False
 if approval.get("bindings",{}).get("launcher")!={"path":'experiments/argo_workflow_followup/discoveryworld_ui_parity/launcher.py',"sha256":self_sha}:return False
 design_spec=approval.get("bindings",{}).get("design",{});proposal_spec=approval.get("bindings",{}).get("proposal",{})
 if design_spec.get("path")!=DESIGN_REL or proposal_spec.get("path")!=PROPOSAL_REL:return False
 try:
  design_bytes=read_once(Path(root,DESIGN_REL));proposal_bytes=read_once(Path(root,PROPOSAL_REL));proposal=json.loads(proposal_bytes)
 except (OSError,json.JSONDecodeError):return False
 if sha_bytes(design_bytes)!=design_spec.get("sha256") or sha_bytes(proposal_bytes)!=proposal_spec.get("sha256"):return False
 required=approval.get("required_approval_text");message=approval.get("user_approval_message");root_sha=execution_root(approval,self_sha);authority_sha=authority_root(approval,proposal,self_sha);expected=f'I approve exactly one local zero-model DiscoveryWorld UI-parity run {approval.get("run_id")} for execution root {root_sha}, authority root {authority_sha}, and design SHA-256 {design_spec.get("sha256")}, limited to {approval.get("cells")} cells, {approval.get("steps_per_cell")} transitions per cell, a {approval.get("controller_hard_deadline_seconds")}-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.'
 return required==expected and approval.get("proposal_core_sha256")==proposal_core_sha(proposal) and approval.get("authority_root_sha256")==authority_sha and approval.get("engine_repo")==ENGINE_REPO and approval.get("controller_interpreter")==CONTROLLER_INTERPRETER and approval.get("controller_interpreter_sha256")==CONTROLLER_INTERPRETER_SHA256 and approval.get("execution_root_sha256")==execution_root(approval,self_sha) and approval.get("status")=="APPROVED" and approval.get("approved_by")=="user" and isinstance(approval.get("approved_at"),str) and isinstance(message,str) and message==required and approval.get("user_approval_message_sha256")==sha_bytes(message.encode())
def seal_controller(approval,approval_bytes,approval_path,root,destination,pinned=None):
 pinned=PINNED if pinned is None else pinned;destination=Path(destination);destination.mkdir(mode=0o700);hashes={};self_bytes=read_once(__file__);self_sha=sha_bytes(self_bytes)
 for key,spec in pinned.items():
  data=read_once(Path(root,spec["path"]))
  if sha_bytes(data)!=spec["sha256"]:raise RuntimeError("PINNED_DRIFT:"+key)
  target=destination/spec["name"];write_once(target,data,0o500 if spec["name"].endswith(".py") else 0o400);hashes[spec["name"]]=spec["sha256"]
 write_once(destination/"launcher.py",self_bytes,0o500);hashes["launcher.py"]=self_sha;write_once(destination/"approval.json",approval_bytes,0o400);hashes["approval.json"]=sha_bytes(approval_bytes)
 seal={"schema_version":"argo-ui-parity-controller-seal/v2","execution_root_sha256":execution_root(approval,self_sha),"files":hashes,"original_approval_path":str(Path(approval_path).resolve())};seal_bytes=canonical(seal)+b"\n";write_once(destination/"seal.json",seal_bytes,0o400);fd=os.open(destination,os.O_RDONLY);os.fsync(fd);os.close(fd);destination.chmod(0o500);return sha_bytes(seal_bytes)
def main():
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();root=Path.cwd();approval_bytes=read_once(a.approval);approval=json.loads(approval_bytes);self_sha=sha_bytes(read_once(__file__))
 if not validate_canonical_approval(approval,a.approval,root,self_sha):print(json.dumps({"status":"BLOCKED_BEFORE_CONSUMPTION","reason":"CANONICAL_APPROVAL"},sort_keys=True));return 2
 seal_parent=Path(tempfile.mkdtemp(prefix="dw-ui-controller-seal-"));destination=seal_parent/"controller";seal_sha=seal_controller(approval,approval_bytes,a.approval,root,destination);env=dict(os.environ);env.update({"ARGO_UI_PARITY_CONTROLLER_SEAL":str(destination),"ARGO_UI_PARITY_CONTROLLER_SEAL_SHA256":seal_sha});argv=[CONTROLLER_INTERPRETER,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(a.approval.resolve()),"--out",str(a.out.resolve())];os.execve(CONTROLLER_INTERPRETER,argv,env)
if __name__=="__main__":raise SystemExit(main())
