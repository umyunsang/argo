#!/usr/bin/env python3
"""Failing-first tests for condition blindness and OS-level oracle boundaries."""
from __future__ import annotations
import copy
import scorer_boundary as sb
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except sb.BoundaryViolation as e:check(n,text in str(e),str(e))
def payload():return {"task_hash":"a"*64,"attempt_id":"attempt-0123456789abcdef","output_files":[{"path":"submission/answer.json","sha256":"b"*64}],"scorer_hash":"c"*64,"environment_hash":"d"*64}
def namespace():return {"target_platform":"linux-x86_64","isolation_engine":"bubblewrap-or-equivalent","agent_network":False,"scorer_network":False,"oracle_source_ids":["oracle:task-1","scorer:task-1"],"agent_mounts":[{"source_id":"task:task-1","target":"/task","mode":"ro","role":"task_input"},{"source_id":"workspace:attempt","target":"/workspace","mode":"rw","role":"workspace"},{"source_id":"runtime:image","target":"/runtime","mode":"ro","role":"runtime"}],"scorer_mounts":[{"source_id":"scorer:task-1","target":"/scorer","mode":"ro","role":"scorer_code"},{"source_id":"oracle:task-1","target":"/gold","mode":"ro","role":"gold"},{"source_id":"workspace:attempt","target":"/submission","mode":"ro","role":"submission"}]}
def events():return [{"actor":"agent","kind":"file","target":"/task/input.json","resolved_source_id":"task:task-1","result":"allowed"},{"actor":"agent","kind":"file","target":"/workspace/answer.json","resolved_source_id":"workspace:attempt","result":"allowed"},{"actor":"scorer","kind":"file","target":"/gold/answer.json","resolved_source_id":"oracle:task-1","result":"allowed"}]
def main():
 p=payload();check("minimal scorer payload passes",sb.validate_scorer_payload(p)["passed"])
 leaked=copy.deepcopy(p);leaked["arm_id"]="G1C1F1";expect("arm field leaks condition",lambda:sb.validate_scorer_payload(leaked),"SCORER_PAYLOAD_FORBIDDEN_FIELD: arm_id")
 path=copy.deepcopy(p);path["output_files"][0]["path"]="G1C1F1/answer.json";expect("condition path leaks",lambda:sb.validate_scorer_payload(path),"SCORER_PATH_CONDITION_LEAK")
 absolute=copy.deepcopy(p);absolute["output_files"][0]["path"]="/tmp/answer.json";expect("absolute host path fails",lambda:sb.validate_scorer_payload(absolute),"SCORER_OUTPUT_PATH_NOT_NEUTRAL")
 check("blind payload hash is deterministic",sb.scorer_payload_hash(p)==sb.scorer_payload_hash(copy.deepcopy(p)))
 ns=namespace();check("separate namespace manifest passes",sb.validate_namespace(ns)["passed"])
 mounted=copy.deepcopy(ns);mounted["agent_mounts"].append({"source_id":"oracle:task-1","target":"/hidden","mode":"ro","role":"task_input"});expect("oracle mount in agent fails",lambda:sb.validate_namespace(mounted),"ORACLE_MOUNT_EXPOSED")
 writable=copy.deepcopy(ns);writable["scorer_mounts"][1]["mode"]="rw";expect("writable gold fails",lambda:sb.validate_namespace(writable),"SCORER_GOLD_NOT_READ_ONLY")
 no_net=copy.deepcopy(ns);no_net["agent_network"]=True;expect("agent network fails",lambda:sb.validate_namespace(no_net),"AGENT_NETWORK_NOT_ISOLATED")
 check("valid OS access log passes",sb.validate_access_log(events(),ns)["passed"])
 expect("missing access log fails",lambda:sb.validate_access_log([],ns),"OS_ACCESS_LOG_MISSING")
 direct=events()+[{"actor":"agent","kind":"file","target":"/gold/answer.json","resolved_source_id":"oracle:task-1","result":"denied"}];expect("direct oracle attempt fails even when denied",lambda:sb.validate_access_log(direct,ns),"ORACLE_ACCESS_ATTEMPT")
 symlink=events()+[{"actor":"agent","kind":"symlink","target":"/workspace/link","resolved_source_id":"oracle:task-1","result":"denied"}];expect("symlink oracle attempt fails",lambda:sb.validate_access_log(symlink,ns),"ORACLE_ACCESS_ATTEMPT")
 fd=events()+[{"actor":"agent","kind":"inherited_fd","target":"fd:7","resolved_source_id":"oracle:task-1","result":"denied"}];expect("inherited fd oracle attempt fails",lambda:sb.validate_access_log(fd,ns),"ORACLE_ACCESS_ATTEMPT")
 network=events()+[{"actor":"agent","kind":"network","target":"127.0.0.1:9000","resolved_source_id":None,"result":"denied"}];expect("network attempt fails",lambda:sb.validate_access_log(network,ns),"AGENT_NETWORK_ACCESS_ATTEMPT")
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
