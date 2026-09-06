#!/usr/bin/env python3
"""Validate authority, seal the font controller, then replace this process."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,tempfile
from pathlib import Path
ENGINE=Path("/Users/um-yunsang/argo-paper-orx");APPROVAL_REL=Path("paper/research/discoveryworld-font-registry-qualification-approval-v1.json");RUN_ID="dw-font-registry-qual-20260906-v1"
EXEC_NAMES={"runner":"run.py","episode":"episode.py","font_registry":"font_registry.py","protocol":"protocol.py","process_control":"process_control.py","manifest":"manifest.json","font_manifest":"font-manifest.json","environment_manifest":"environment_manifest.py","environment_content":"environment-content-manifest.json","bootstrap":"bootstrap.py","launcher":"launcher.py","result_verifier":"verify_result.py","admission_consumer":"admit_result.py"}
EXEC_KEYS=tuple(EXEC_NAMES);EXPECTED={key:Path("experiments/argo_workflow_followup/discoveryworld_font_qualification")/name for key,name in EXEC_NAMES.items()};EXPECTED["font_manifest"]=Path("paper/research/discoveryworld-pinned-font-manifest-v1.json")
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def read_once(path):
 flags=os.O_RDONLY
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags)
 try:
  if not stat.S_ISREG(os.fstat(fd).st_mode):raise RuntimeError("NOT_REGULAR")
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
   n=os.write(fd,view)
   if n<=0:raise OSError("write")
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
def proposal_core(value):
 v=dict(value);v.pop("required_approval_text",None);return sha_bytes(canonical(v))
def execution_root(a):return sha_bytes(canonical({k:a.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS}))
def authority_root(a,p):return sha_bytes(canonical({**{k:a.get("bindings",{}).get(k,{}).get("sha256") for k in EXEC_KEYS},"design":a.get("bindings",{}).get("design",{}).get("sha256"),"proposal_core":proposal_core(p)}))
def required_text(a,er,ar):return f'I approve exactly one local zero-model DiscoveryWorld font-registry qualification run {RUN_ID} for execution root {er}, authority root {ar}, and design SHA-256 {a.get("bindings",{}).get("design",{}).get("sha256")}, limited to exactly two zero-scenario cells, a 120-second launch/execution deadline, zero model calls, zero Docker calls, and USD 0 API spend. No retry or resume.'
def validate(a,approval_path,root):
 if Path(root).resolve()!=ENGINE or Path(approval_path).resolve()!=ENGINE/APPROVAL_REL:return False
 if a.get("status")!="APPROVED" or a.get("approved_by")!="user" or a.get("run_id")!=RUN_ID:return False
 for key,path in EXPECTED.items():
  spec=a.get("bindings",{}).get(key,{});actual=ENGINE/path
  if spec.get("path")!=path.as_posix() or not actual.is_file() or sha_bytes(read_once(actual))!=spec.get("sha256"):return False
 for key in ["design","proposal","immutable_validation","method_review","runtime_review","handoff_review","user_authorization"]:
  spec=a.get("bindings",{}).get(key,{});actual=ENGINE/spec.get("path","")
  if not actual.is_file() or sha_bytes(read_once(actual))!=spec.get("sha256"):return False
 try:proposal=json.loads(read_once(ENGINE/a["bindings"]["proposal"]["path"]));er=execution_root(a);ar=authority_root(a,proposal);text=required_text(a,er,ar)
 except (OSError,KeyError,json.JSONDecodeError,TypeError):return False
 if a.get("execution_root_sha256")!=er or a.get("authority_root_sha256")!=ar or a.get("proposal_core_sha256")!=proposal_core(proposal) or proposal.get("required_approval_text")!=text or a.get("required_approval_text")!=text or a.get("user_approval_message")!=text or a.get("user_approval_message_sha256")!=sha_bytes(text.encode()):return False
 if sha_bytes(read_once(a.get("controller_interpreter","")))!=a.get("controller_interpreter_sha256"):return False
 return True
def seal(a,approval_bytes,destination):
 destination=Path(destination);destination.mkdir(mode=0o700);files={}
 for key,name in EXEC_NAMES.items():
  source=ENGINE/a["bindings"][key]["path"];data=read_once(source);target=destination/name;write_once(target,data,0o500 if name.endswith(".py") else 0o400);files[name]=sha_bytes(data)
 write_once(destination/"approval.json",approval_bytes,0o400);files["approval.json"]=sha_bytes(approval_bytes);value={"schema_version":"argo-font-controller-seal/v1","execution_root_sha256":execution_root(a),"files":files};data=canonical(value)+b"\n";write_once(destination/"seal.json",data,0o400);fd=os.open(destination,os.O_RDONLY);os.fsync(fd);os.close(fd);destination.chmod(0o500);return sha_bytes(data)
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--approval",type=Path,required=True);p.add_argument("--out",type=Path,required=True);x=p.parse_args(argv);root=Path.cwd();approval_bytes=read_once(x.approval);a=json.loads(approval_bytes)
 if not validate(a,x.approval,root):print(json.dumps({"status":"BLOCKED_BEFORE_CONSUMPTION","reason":"CANONICAL_APPROVAL"}));return 2
 parent=Path(tempfile.mkdtemp(prefix="dw-font-controller-seal-"));destination=parent/"controller";seal_sha=seal(a,approval_bytes,destination);env=dict(os.environ);env.update({"ARGO_FONT_CONTROLLER_SEAL":str(destination),"ARGO_FONT_CONTROLLER_SEAL_SHA256":seal_sha});python=a["controller_interpreter"];args=[python,"-I","-S","-B",str(destination/"bootstrap.py"),"controller",str(destination),"--approval",str(x.approval.resolve()),"--out",str(x.out.resolve())];os.execve(python,args,env)
if __name__=="__main__":raise SystemExit(main())
