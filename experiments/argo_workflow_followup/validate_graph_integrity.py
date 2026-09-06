#!/usr/bin/env python3
"""Validate current append-only graph integrity without freezing predecessor cardinality."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate(root,graph_path):
 root=Path(root);errors=[]
 try:graph=json.loads(Path(graph_path).read_text())
 except Exception as exc:return {"passed":False,"errors":["READ:"+type(exc).__name__]}
 nodes=graph.get("nodes",[]);edges=graph.get("edges",[]);node_ids=[node.get("id") for node in nodes];edge_ids=[edge.get("id") for edge in edges];node_set=set(node_ids)
 if graph.get("schema_version")!="argo-paper-context-graph/v1":errors.append("SCHEMA")
 if len(node_ids)!=len(node_set) or len(edge_ids)!=len(set(edge_ids)):errors.append("DUPLICATE_IDS")
 if any(edge.get("source") not in node_set or edge.get("target") not in node_set for edge in edges):errors.append("DANGLING_ENDPOINT")
 used={edge.get("relation") for edge in edges};vocab=set(graph.get("edge_vocabulary",[]))
 if used!=vocab:errors.append("RELATION_VOCABULARY")
 projection=graph.get("projection_inputs",{});paths={key:value for key,value in projection.items() if key.endswith("_path")};hashes={key:value for key,value in projection.items() if key.endswith("_sha256")}
 if {key[:-5]+"_sha256" for key in paths}!={key for key in hashes}:errors.append("PROJECTION_KEY_PAIR")
 for key,relative in paths.items():
  path=root/relative
  if not path.is_file() or sha(path)!=projection.get(key[:-5]+"_sha256"):errors.append("PROJECTION_HASH:"+key)
 if graph.get("evidence_cutoff")!="2026-09-06":errors.append("EVIDENCE_CUTOFF")
 return {"passed":not errors,"errors":errors,"nodes":len(nodes),"edges":len(edges),"projection_paths":len(paths)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument("--graph",type=Path);a=p.parse_args();graph=a.graph or a.root/"paper/context-graph.json";result=validate(a.root,graph);print(json.dumps(result,indent=2,sort_keys=True));return 0 if result["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
