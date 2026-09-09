#!/usr/bin/env python3
import errno,json,os,platform,socket
from pathlib import Path
ws=Path("/workspace");fifo=Path("/tmp/start")
try:os.mkfifo(fifo,0o600)
except FileExistsError:pass
(ws/"target-ready.json").write_text(json.dumps({"pid":os.getpid(),"platform":platform.platform(),"fifo":str(fifo)})+"\n")
with fifo.open("rb",buffering=0) as f:f.read(1)
results={}
def file_try(name,path):
 rec={"path":path,"realpath":os.path.realpath(path)}
 try:rec.update(success=True,bytes=len(Path(path).read_bytes()))
 except OSError as e:rec.update(success=False,errno=e.errno,error=e.strerror)
 results[name]=rec
file_try("allowed","/workspace/allowed.txt")
file_try("direct","/oracle/eval_programs/gold_results/ligand_fingerprint_gold.csv")
link=ws/"oracle-link"
try:link.unlink()
except FileNotFoundError:pass
link.symlink_to("/oracle/eval_programs/gold_results/ligand_fingerprint_gold.csv")
file_try("symlink",str(link))
fds=[]
for p in sorted(Path("/proc/self/fd").iterdir(),key=lambda x:int(x.name)):
 try:target=os.readlink(p)
 except OSError as e:target=f"ERROR:{e.errno}"
 fds.append({"fd":int(p.name),"target":target,"oracle":("gold" in target.lower() or "oracle" in target.lower())})
results["inherited_fds"]={"entries":fds,"oracle_fd_count":sum(x["oracle"] for x in fds)}
def net_try(name,address):
 s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.settimeout(1.0)
 try:code=s.connect_ex(address);results[name]={"address":f"{address[0]}:{address[1]}","connect_ex":code,"error":os.strerror(code) if code else None,"success":code==0}
 finally:s.close()
net_try("network_external",("1.1.1.1",53));net_try("network_loopback",("127.0.0.1",9))
results["boundary_pass"]=(results["allowed"]["success"] and not results["direct"]["success"] and not results["symlink"]["success"] and results["inherited_fds"]["oracle_fd_count"]==0 and not results["network_external"]["success"] and not results["network_loopback"]["success"])
(ws/"agent-probe-result.json").write_text(json.dumps(results,sort_keys=True,indent=2)+"\n")
