#!/usr/bin/env python3
"""Pinned pygame font registry for no-fork DiscoveryWorld qualification."""
from __future__ import annotations
import ast,hashlib,json
from pathlib import Path
EXPECTED_CALLS=[("discoveryworld/World.py",63,"Arial",8,False,False),("discoveryworld/World.py",552,"monospace",15,True,False),("discoveryworld/UserInterface.py",21,"monospace",10,False,False),("discoveryworld/UserInterface.py",22,"monospace",15,False,False),("discoveryworld/UserInterface.py",23,"monospace",15,True,False)]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def scan_calls(source_root):
 rows=[]
 for relative in ["discoveryworld/World.py","discoveryworld/UserInterface.py"]:
  tree=ast.parse((Path(source_root)/relative).read_text())
  for node in ast.walk(tree):
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=="SysFont" and len(node.args)>=2 and isinstance(node.args[0],ast.Constant) and isinstance(node.args[1],ast.Constant):
    kwargs={item.arg:ast.literal_eval(item.value) for item in node.keywords};rows.append((relative,node.lineno,node.args[0].value,node.args[1].value,bool(kwargs.get("bold",False)),bool(kwargs.get("italic",False))))
 return sorted(rows)
def validate_manifest(manifest,source_root):
 errors=[]
 if manifest.get("schema_version")!="argo-discoveryworld-pinned-font-manifest/v1":errors.append("SCHEMA")
 if scan_calls(source_root)!=sorted(EXPECTED_CALLS):errors.append("SOURCE_CALLS")
 calls=manifest.get("calls",[])
 if [(x.get("source"),x.get("line"),x.get("name"),x.get("size"),x.get("bold"),x.get("italic")) for x in calls]!=EXPECTED_CALLS:errors.append("MANIFEST_CALLS")
 for call in calls:
  path=Path(call.get("resolved_path",""))
  if not path.is_file() or sha(path)!=call.get("sha256"):errors.append("FONT_BYTES:"+str(path))
 return {"passed":not errors,"errors":errors}
def configure(pygame_module,manifest,source_root):
 check=validate_manifest(manifest,source_root)
 if not check["passed"]:raise RuntimeError("FONT_MANIFEST:"+",".join(check["errors"]))
 paths={(call["name"].lower(),call["bold"],call["italic"]):call["resolved_path"] for call in manifest["calls"]};sysfont=pygame_module.sysfont;sysfont.Sysfonts.clear();sysfont.Sysalias.clear();sysfont.Sysfonts["arial"]={(False,False):paths[("arial",False,False)]};mono={(False,False):paths[("monospace",False,False)],(True,False):paths[("monospace",True,False)]};sysfont.Sysalias["monospace"]=mono;sysfont.is_init=True;return {"arial":sysfont.Sysfonts["arial"],"monospace":mono}
def load(path):return json.loads(Path(path).read_text())
