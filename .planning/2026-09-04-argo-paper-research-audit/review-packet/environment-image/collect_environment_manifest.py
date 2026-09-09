#!/usr/bin/env python3
import argparse,hashlib,importlib.metadata as md,json,os,platform,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--role",choices=("agent","scorer"),required=True);p.add_argument("--digest",required=True);a=p.parse_args()
def fh(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def dist_digest(d):
 rows=[]
 for f in sorted(d.files or [],key=lambda x:str(x)):
  q=Path(d.locate_file(f))
  if q.is_file(): rows.append([str(f),q.stat().st_size,fh(q)])
 return hashlib.sha256(json.dumps(rows,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
packages=[]
for d in md.distributions():
 name=d.metadata.get("Name")
 if name:packages.append({"name":name,"version":d.version,"artifact_sha256":dist_digest(d),"source":"wheel"})
packages.sort(key=lambda x:x["name"].lower())
dpkg=subprocess.run(["dpkg-query","-W","-f=${Package}\t${Version}\t${Architecture}\n"],check=True,capture_output=True,text=True).stdout
lines=sorted(x for x in dpkg.splitlines() if x)
dpkg_text="\n".join(lines)+"\n"
obj={"schema_version":"argo-installed-environment-manifest/v1","role":a.role,"os":sys_platform if False else platform.system().lower(),"architecture":platform.machine(),"python":platform.python_version(),"container_digest":a.digest,"package_digest_semantics":"canonical SHA-256 over every installed distribution file path, byte length, and byte SHA-256; stronger for parity than name/version alone; not asserted to equal the upstream wheel archive hash","packages":packages,"debian_packages":lines,"debian_manifest_sha256":hashlib.sha256(dpkg_text.encode()).hexdigest()}
print(json.dumps(obj,sort_keys=True,separators=(",",":")))
