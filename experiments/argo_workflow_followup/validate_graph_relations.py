#!/usr/bin/env python3
"""Validate graph relation vocabulary and explicit predecessor snapshot semantics."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
def validate(graph):
 errors=[];v=graph.get("edge_vocabulary")
 if not isinstance(v,list) or len(v)!=len(set(v)):errors.append("VOCABULARY_DUPLICATE_OR_MALFORMED")
 used={e.get("relation") for e in graph.get("edges",[])};vset=set(v or [])
 if used-vset:errors.append("UNDECLARED_RELATIONS:"+",".join(sorted(used-vset)))
 if vset-used:errors.append("UNUSED_RELATIONS:"+",".join(sorted(vset-used)))
 if any(not isinstance(x,str) or not x for x in used):errors.append("MALFORMED_RELATION")
 lineage=graph.get("projection_lineage",{})
 if not re.fullmatch(r"[0-9a-f]{9,40}",lineage.get("predecessor_commit","")):errors.append("PREDECESSOR_COMMIT")
 if not re.fullmatch(r"[0-9a-f]{64}",lineage.get("predecessor_snapshot_sha256","")):errors.append("PREDECESSOR_SHA")
 if "successor" not in lineage.get("semantics",""):errors.append("PREDECESSOR_SEMANTICS")
 return {"passed":not errors,"errors":errors,"used_relations":sorted(used),"vocabulary":sorted(vset)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--graph",type=Path,required=True);a=p.parse_args();r=validate(json.loads(a.graph.read_text()));print(json.dumps(r,indent=2,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
