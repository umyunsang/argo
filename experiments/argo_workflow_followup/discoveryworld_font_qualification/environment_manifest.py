#!/usr/bin/env python3
"""Content closure and sealed-copy helpers for the DiscoveryWorld worker runtime."""
from __future__ import annotations
import hashlib,json,os,shutil,stat
from pathlib import Path
EXCLUDED_DIRS={"__pycache__"}
EXCLUDED_SUFFIXES={".pyc",".pyo"}
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def included(path):return not any(part in EXCLUDED_DIRS for part in path.parts) and path.suffix not in EXCLUDED_SUFFIXES and path.name!=".DS_Store"
def scan(root):
 root=Path(root).resolve();entries=[];seen_inodes={}
 for path in sorted(root.rglob("*")):
  rel=path.relative_to(root)
  if not included(rel):continue
  if path.is_symlink():
   target=os.readlink(path);resolved=(path.parent/target).resolve(strict=False)
   if Path(target).is_absolute() or resolved!=root and root not in resolved.parents:raise RuntimeError("ESCAPING_RUNTIME_SYMLINK:"+str(rel))
   entries.append({"path":rel.as_posix(),"type":"symlink","target":target})
  elif path.is_dir():continue
  elif path.is_file():
   st=path.stat();inode=(st.st_dev,st.st_ino)
   if inode in seen_inodes:raise RuntimeError("RUNTIME_HARDLINK:"+seen_inodes[inode]+":"+rel.as_posix())
   seen_inodes[inode]=rel.as_posix();entries.append({"path":rel.as_posix(),"type":"file","size":st.st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"executable":bool(st.st_mode&0o111)})
  else:raise RuntimeError("UNSUPPORTED_RUNTIME_ENTRY:"+str(rel))
 return entries

def scan_sha(entries):return hashlib.sha256(canonical(entries)).hexdigest()
def verify_root(spec,root=None):
 source=Path(root or spec["source_root"]);actual=scan(source)
 return actual==spec["entries"] and scan_sha(actual)==spec["entries_sha256"]
def copy_and_verify(manifest,destination):
 destination=Path(destination);destination.mkdir()
 copied={}
 for spec in manifest["roots"]:
  if not verify_root(spec):raise RuntimeError("RUNTIME_SOURCE_DRIFT:"+spec["name"])
  target=destination/spec["destination"]
  shutil.copytree(spec["source_root"],target,symlinks=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.pyo",".DS_Store"))
  if not verify_root(spec,target):raise RuntimeError("RUNTIME_COPY_DRIFT:"+spec["name"])
  copied[spec["name"]]=target
 for path in sorted(destination.rglob("*"),reverse=True):
  if not path.is_symlink():path.chmod(0o555 if path.is_dir() else 0o555 if path.stat().st_mode&0o111 else 0o444)
 destination.chmod(0o555)
 return copied
def build_manifest(specs):
 roots=[]
 for name,source,destination in specs:
  entries=scan(source);roots.append({"name":name,"source_root":str(Path(source).resolve()),"destination":destination,"entries":entries,"entries_sha256":scan_sha(entries)})
 value={"schema_version":"argo-ui-parity-environment-content/v1","exclusions":{"directories":sorted(EXCLUDED_DIRS),"suffixes":sorted(EXCLUDED_SUFFIXES),"names":[".DS_Store"]},"roots":roots}
 value["aggregate_sha256"]=hashlib.sha256(canonical(roots)).hexdigest();return value
