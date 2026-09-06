#!/usr/bin/env python3
"""One-shot manifest, atomic marker, and hash-chained ledger primitives."""
from __future__ import annotations
import hashlib,json,os,re,stat
from pathlib import Path,PurePosixPath
CELL_TERMINAL={"valid_complete","timeout","crash","malformed","identity_drift","spawn_failure","unreaped","sidecar_error","ledger_error","global_deadline","controller_signal"}
COMMON={"previous_record_sha256","record_sha256"}
LEDGER_KEYS={
 "header":COMMON|{"event","schema_version","run_id","manifest_sha256","approval_sha256","source_archive_sha256","preflight_identity_sha256","execution_root_sha256","started_at"},
 "planned":COMMON|{"event","sequence","run_id","cell_id","cell_nonce","cell_index","timestamp"},
 "spawned":COMMON|{"event","sequence","run_id","cell_id","cell_nonce","cell_index","pid","pgid","timestamp"},
 "finished":COMMON|{"event","sequence","run_id","cell_id","cell_nonce","cell_index","status","exit_code","timed_out","stdout","stderr","events","ui_gzip","frame_manifest","timestamp"},
 "controller_stop":COMMON|{"event","sequence","run_id","reason","timestamp"},
 "finalized":COMMON|{"event","sequence","run_id","status","result_sha256","timestamp"},
}
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def safe_path(value):
 try:p=PurePosixPath(value);return bool(value) and not p.is_absolute() and ".." not in p.parts
 except TypeError:return False
def validate_manifest(m):
 errors=[]
 if m.get("schema_version")!="argo-discoveryworld-ui-parity-manifest/v1":errors.append("SCHEMA")
 cells=m.get("ordered_cells",[])
 if len(cells)!=30:errors.append("CELL_COUNT")
 expected=[];idx=0
 for family,scenario in [("chemistry","Combinatorial Chemistry"),("archaeology","Archaeology Dating")]:
  for seed in range(5):
   for mode,repeat in [("official",0),("ui_only",0),("ui_only",1)]:
    expected.append((idx,f"{family}-s{seed}-{mode}-r{repeat}",family,scenario,seed,mode,repeat,1000,1110000+idx));idx+=1
 keys=[];paths=[]
 for cell,want in zip(cells,expected):
  got=(cell.get("index"),cell.get("cell_id"),cell.get("family"),cell.get("scenario"),cell.get("seed"),cell.get("mode"),cell.get("repeat"),cell.get("steps"),cell.get("thread_id"))
  if got!=want or any(type(x) is not int for x in [cell.get("index"),cell.get("seed"),cell.get("repeat"),cell.get("steps"),cell.get("thread_id"),cell.get("timeout_seconds")]):errors.append("CELL_GRID:"+str(cell.get("index")))
  if not re.fullmatch(r"[0-9a-f]{32}",str(cell.get("cell_nonce",""))):errors.append("NONCE")
  keys.append(cell.get("cell_id"))
  for k in ["workdir","event_path","ui_gzip_path","stdout_path","stderr_path","frame_manifest_path"]:
   p=cell.get(k);paths.append(p)
   if not safe_path(p):errors.append("PATH:"+k)
 if len(keys)!=len(set(keys)):errors.append("DUPLICATE_CELL")
 if len(paths)!=len(set(paths)):errors.append("DUPLICATE_PATH")
 if len({c.get("cell_nonce") for c in cells})!=len(cells):errors.append("DUPLICATE_NONCE")
 if len({c.get("thread_id") for c in cells})!=len(cells):errors.append("DUPLICATE_THREAD")
 if [c.get("index") for c in cells]!=list(range(30)):errors.append("ORDER")
 if len(m.get("mode_pairs",[]))!=20 or len(m.get("ui_repeat_pairs",[]))!=10:errors.append("PAIR_COUNT")
 all_ids=set(keys)
 if any(set(p.values())-all_ids for p in m.get("mode_pairs",[])+m.get("ui_repeat_pairs",[])):errors.append("PAIR_KEY")
 return {"passed":not errors,"errors":errors}
def write_all(fd,data):
 view=memoryview(data)
 while view:
  written=os.write(fd,view)
  if written<=0:raise OSError("short durable write")
  view=view[written:]
def fsync_parent(path):
 fd=os.open(str(Path(path).parent),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def ensure_directory_durable(path):
 path=Path(path);missing=[];current=path
 while not current.exists():missing.append(current);current=current.parent
 for directory in reversed(missing):directory.mkdir();fsync_parent(directory)
def atomic_create(path,data):
 path=Path(path);ensure_directory_durable(path.parent);flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 try:fd=os.open(path,flags,0o600)
 except FileExistsError:return False
 try:
  write_all(fd,data);os.fsync(fd)
 finally:os.close(fd)
 fsync_parent(path);return True
def publish_exclusive(temp_path,result_path):
 temp_path=Path(temp_path);result_path=Path(result_path);ensure_directory_durable(result_path.parent)
 os.link(temp_path,result_path,follow_symlinks=False);fsync_parent(result_path);os.unlink(temp_path);fsync_parent(result_path)
def append_record(path,record,previous=None):
 path=Path(path);ensure_directory_durable(path.parent);value=dict(record);value["previous_record_sha256"]=previous or "0"*64;value["record_sha256"]=hashlib.sha256(canonical(value)).hexdigest();line=canonical(value)+b"\n";flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND
 if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
 fd=os.open(path,flags,0o600)
 try:write_all(fd,line);os.fsync(fd)
 finally:os.close(fd)
 fsync_parent(path);return value["record_sha256"]
def validate_ledger(path,manifest,allow_partial=False,expected_header=None,strict_sidecars=False,result_payload_path=None,artifact_root=None,ledger_bytes=None,artifact_reader=None):
 errors=[];records=[]
 try:
  lines=(Path(path).read_bytes() if ledger_bytes is None else ledger_bytes).splitlines();records=[json.loads(line) for line in lines]
  if any(canonical(record)!=line for record,line in zip(records,lines)):errors.append("NONCANONICAL")
 except Exception:return {"passed":False,"errors":["READ"]}
 prev="0"*64;states={};last_seq=0;finalized=False;planned_order=[];cells={c["cell_id"]:c for c in manifest.get("ordered_cells",[])}
 for i,r in enumerate(records):
  got=r.get("record_sha256");value=dict(r);value.pop("record_sha256",None)
  if r.get("previous_record_sha256")!=prev or hashlib.sha256(canonical(value)).hexdigest()!=got:errors.append("HASH_CHAIN")
  prev=got or prev;event=r.get("event")
  if finalized:errors.append("POST_FINALIZED")
  if event not in LEDGER_KEYS or set(r)!=LEDGER_KEYS.get(event,set()):errors.append("RECORD_SCHEMA")
  if i==0:
   if event!="header" or r.get("schema_version")!="argo-ui-parity-ledger/v1" or r.get("run_id")!=manifest.get("run_id"):errors.append("HEADER")
   if expected_header and any(r.get(k)!=v for k,v in expected_header.items()):errors.append("HEADER_IDENTITY")
   continue
  if r.get("run_id")!=manifest.get("run_id"):errors.append("RUN_IDENTITY")
  seq=r.get("sequence")
  if type(seq) is not int or seq!=last_seq+1:errors.append("SEQUENCE")
  else:last_seq=seq
  cid=r.get("cell_id")
  if event in {"planned","spawned","finished"}:
   cell=cells.get(cid)
   if cell is None or r.get("cell_nonce")!=cell["cell_nonce"] or r.get("cell_index")!=cell["index"]:errors.append("CELL_IDENTITY")
  if event=="planned":
   if cid in states:errors.append("DUPLICATE_PLANNED")
   states[cid]="planned";planned_order.append(cid)
   if planned_order!=[c["cell_id"] for c in manifest["ordered_cells"][:len(planned_order)]]:errors.append("PLAN_ORDER")
  elif event=="spawned":
   if states.get(cid)!="planned":errors.append("BAD_SPAWN_TRANSITION")
   states[cid]="spawned"
  elif event=="finished":
   status=r.get("status")
   if type(r.get("timed_out")) is not bool or (r.get("exit_code") is not None and type(r.get("exit_code")) is not int):errors.append("FINISHED_SCHEMA")
   if strict_sidecars:
    for key in ["stdout","stderr","events","ui_gzip","frame_manifest"]:
     meta=r.get(key)
     if meta=={}:
      if status=="valid_complete":errors.append("SIDECAR_MISSING:"+key)
      continue
     valid_meta=isinstance(meta,dict) and set(meta)=={"path","size","sha256"} and type(meta.get("size")) is int and meta.get("size")>=0 and re.fullmatch(r"[0-9a-f]{64}",str(meta.get("sha256","")))
     if not valid_meta:errors.append("SIDECAR_META:"+key);continue
     if artifact_root is not None:
      manifest_key={"stdout":"stdout_path","stderr":"stderr_path","events":"event_path","ui_gzip":"ui_gzip_path","frame_manifest":"frame_manifest_path"}[key];expected_path=(Path(artifact_root)/cell[manifest_key]).resolve()
      if Path(meta["path"]).resolve()!=expected_path:errors.append("SIDECAR_PATH:"+key)
     sidecar=Path(meta["path"])
     try:data=artifact_reader(meta["path"]) if artifact_reader is not None else sidecar.read_bytes()
     except (OSError,RuntimeError,ValueError):data=None
     if data is None or len(data)!=meta["size"] or hashlib.sha256(data).hexdigest()!=meta["sha256"]:errors.append("SIDECAR_BYTES:"+key)
     if status=="valid_complete" and key in {"events","ui_gzip","frame_manifest"} and meta["size"]==0:errors.append("SIDECAR_EMPTY:"+key)
    if status=="valid_complete" and (r.get("exit_code")!=0 or r.get("timed_out") is not False):errors.append("VALID_COMPLETE_PROCESS")
   legal=states.get(cid)=="spawned" and status in CELL_TERMINAL
   legal_pre=states.get(cid)=="planned" and status in {"spawn_failure","sidecar_error","ledger_error","global_deadline","controller_signal"}
   if not (legal or legal_pre):errors.append("BAD_FINISH_TRANSITION")
   states[cid]="finished"
  elif event=="controller_stop":pass
  elif event=="finalized":
   if finalized:errors.append("DUPLICATE_FINALIZED")
   if r.get("status") not in {"PASS","FAIL_PARITY_NOT_ESTABLISHED","INVALID","INCOMPLETE"} or not re.fullmatch(r"[0-9a-f]{64}",str(r.get("result_sha256",""))):errors.append("FINALIZED_SCHEMA")
   if result_payload_path is not None:
    payload=Path(result_payload_path)
    try:
     payload_bytes=artifact_reader(str(payload)) if artifact_reader is not None else payload.read_bytes();result=json.loads(payload_bytes)
     if canonical(result)+b"\n"!=payload_bytes:errors.append("FINALIZED_RESULT_CANONICAL")
     if hashlib.sha256(payload_bytes).hexdigest()!=r.get("result_sha256"):errors.append("FINALIZED_RESULT_BYTES")
     if result.get("ledger_last_record_sha256_before_final")!=r.get("previous_record_sha256") or result.get("status")!=r.get("status"):errors.append("FINALIZED_RESULT_BINDING")
    except (OSError,RuntimeError,ValueError,json.JSONDecodeError,AttributeError):errors.append("FINALIZED_RESULT_BYTES")
   finalized=True
  else:errors.append("UNKNOWN_EVENT")
 if any(v!="finished" for v in states.values()):errors.append("PLANNED_NOT_TERMINAL")
 if not allow_partial:
  if len(states)!=30:errors.append("INCOMPLETE")
  if sum(r.get("event")=="finalized" for r in records)!=1:errors.append("FINALIZED_COUNT")
 return {"passed":not errors,"errors":errors,"records":len(records),"last_record_sha256":prev,"states":states,"finalized":finalized}
class ArtifactNamespace:
 def __init__(self,root):
  self.root=Path(root).resolve();flags=os.O_RDONLY
  if hasattr(os,"O_DIRECTORY"):flags|=os.O_DIRECTORY
  if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
  self.root_fd=os.open(self.root,flags);st=os.fstat(self.root_fd);self.root_identity=(st.st_dev,st.st_ino);self.dirs={"":self.root_fd};self.files={}
 def _parts(self,relative):
  path=PurePosixPath(relative)
  if path.is_absolute() or not path.parts or ".." in path.parts:raise ValueError("unsafe artifact path")
  return path.parts
 def ensure_dir(self,relative):
  parts=self._parts(relative);current=self.root_fd;key=[]
  for part in parts:
   key.append(part);joined="/".join(key)
   if joined in self.dirs:current=self.dirs[joined];continue
   try:os.mkdir(part,0o700,dir_fd=current);os.fsync(current)
   except FileExistsError:pass
   flags=os.O_RDONLY
   if hasattr(os,"O_DIRECTORY"):flags|=os.O_DIRECTORY
   if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
   current=os.open(part,flags,dir_fd=current);self.dirs[joined]=current
  return current
 def _parent(self,relative):
  parts=self._parts(relative);parent="/".join(parts[:-1]);return (self.ensure_dir(parent) if parent else self.root_fd),parts[-1]
 def create_bytes(self,relative,data):
  if relative in self.files:raise FileExistsError(relative)
  parent,name=self._parent(relative);flags=os.O_RDWR|os.O_CREAT|os.O_EXCL
  if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
  fd=os.open(name,flags,0o600,dir_fd=parent)
  try:write_all(fd,data);os.fsync(fd);os.fsync(parent)
  except BaseException:os.close(fd);raise
  self.files[relative]=fd;return fd
 def read_bytes(self,relative):
  fd=self.files.get(relative)
  if fd is None:
   parent,name=self._parent(relative);flags=os.O_RDONLY
   if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
   fd=os.open(name,flags,dir_fd=parent);self.files[relative]=fd
  st=os.fstat(fd);parent,name=self._parent(relative);named=os.stat(name,dir_fd=parent,follow_symlinks=False)
  if not stat.S_ISREG(st.st_mode) or (st.st_dev,st.st_ino)!=(named.st_dev,named.st_ino):raise RuntimeError("ARTIFACT_INODE_DRIFT:"+relative)
  size=st.st_size;chunks=[];offset=0
  while offset<size:
   chunk=os.pread(fd,min(1048576,size-offset),offset)
   if not chunk:raise OSError("short artifact read")
   chunks.append(chunk);offset+=len(chunk)
  return b"".join(chunks)
 def append_record(self,relative,record,previous=None):
  fd=self.files.get(relative)
  if fd is None:fd=self.create_bytes(relative,b"")
  value=dict(record);value["previous_record_sha256"]=previous or "0"*64;value["record_sha256"]=hashlib.sha256(canonical(value)).hexdigest();os.lseek(fd,0,os.SEEK_END);write_all(fd,canonical(value)+b"\n");os.fsync(fd);return value["record_sha256"]
 def metadata(self,relative):
  data=self.read_bytes(relative);return {"path":str(self.root/relative),"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}
 def publish(self,pending,result):
  source_parent,source_name=self._parent(pending);target_parent,target_name=self._parent(result);source=os.fstat(self.files[pending]);os.link(source_name,target_name,src_dir_fd=source_parent,dst_dir_fd=target_parent,follow_symlinks=False);os.fsync(target_parent);target=os.stat(target_name,dir_fd=target_parent,follow_symlinks=False)
  if not stat.S_ISREG(target.st_mode) or (source.st_dev,source.st_ino)!=(target.st_dev,target.st_ino):
   os.unlink(target_name,dir_fd=target_parent);os.fsync(target_parent);raise RuntimeError("PUBLISHED_INODE_DRIFT")
  pending_fd=self.files.pop(pending);self.files[result]=pending_fd;os.unlink(source_name,dir_fd=source_parent);os.fsync(source_parent);return target
 def remove(self,relative):
  parent,name=self._parent(relative);fd=self.files.pop(relative,None);os.unlink(name,dir_fd=parent);os.fsync(parent)
  if fd is not None:os.close(fd)
 def verify(self):
  try:
   current=self.root.lstat()
   if self.root.is_symlink() or (current.st_dev,current.st_ino)!=self.root_identity:return False
   for relative,fd in self.dirs.items():
    if not relative:continue
    named=os.stat(relative,dir_fd=self.root_fd,follow_symlinks=False);actual=os.fstat(fd)
    if not stat.S_ISDIR(named.st_mode) or (named.st_dev,named.st_ino)!=(actual.st_dev,actual.st_ino):return False
   for relative in self.files:self.read_bytes(relative)
   return True
  except (OSError,RuntimeError):return False
 def close(self):
  seen=set()
  for fd in list(self.files.values())+list(self.dirs.values()):
   if fd not in seen:
    seen.add(fd)
    try:os.close(fd)
    except OSError:pass
  self.files.clear();self.dirs.clear()
def final_status(cell_statuses,pair_statuses,planned=30):
 if len(cell_statuses)<planned:return "INCOMPLETE"
 if len(cell_statuses)!=planned or any(x!="valid_complete" for x in cell_statuses):return "INVALID"
 if any(x=="UNOBSERVABLE" for x in pair_statuses) or len(pair_statuses)!=30:return "INVALID"
 if any(x=="OBSERVED_MISMATCH" for x in pair_statuses):return "FAIL_PARITY_NOT_ESTABLISHED"
 return "PASS" if all(x=="EXACT" for x in pair_statuses) else "INVALID"
