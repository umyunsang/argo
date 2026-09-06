#!/usr/bin/env python3
"""Pinned pygame font registry for no-fork DiscoveryWorld qualification."""
from __future__ import annotations
import ast,hashlib,json,os,subprocess,warnings
from pathlib import Path
EXPECTED_CALLS=[("discoveryworld/World.py",63,"Arial",8,False,False),("discoveryworld/World.py",552,"monospace",15,True,False),("discoveryworld/UserInterface.py",21,"monospace",10,False,False),("discoveryworld/UserInterface.py",22,"monospace",15,False,False),("discoveryworld/UserInterface.py",23,"monospace",15,True,False)]
EXPECTED_CENSUS=[("discoveryworld/UserInterface.py",21,"pygame.font.SysFont","monospace",10,False,False),("discoveryworld/UserInterface.py",22,"pygame.font.SysFont","monospace",15,False,False),("discoveryworld/UserInterface.py",23,"pygame.font.SysFont","monospace",15,True,False),("discoveryworld/World.py",63,"pygame.font.SysFont","Arial",8,False,False),("discoveryworld/World.py",552,"pygame.font.SysFont","monospace",15,True,False),("scripts/misc-util/UtilSpriteSheetGrid.py",38,"pygame.font.SysFont","Arial","<dynamic>",False,False),("scripts/userstudy.py",29,"pygame.font.SysFont","monospace",15,False,False),("scripts/userstudy.py",30,"pygame.font.SysFont","monospace",15,True,False)]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def call_name(node):
 if isinstance(node,ast.Name):return node.id
 if isinstance(node,ast.Attribute):
  left=call_name(node.value);return (left+"." if left else "")+node.attr
 return "<dynamic>"
def literal(node):
 try:return ast.literal_eval(node)
 except (ValueError,TypeError):return "<dynamic>"
def scan_calls(source_root):
 rows=[];root=Path(source_root)
 for path in sorted(root.rglob("*.py")):
  relative=path.relative_to(root)
  if any(part in {".venv",".git","__pycache__"} for part in relative.parts):continue
  with warnings.catch_warnings():warnings.simplefilter("ignore",SyntaxWarning);tree=ast.parse(path.read_text())
  aliases={alias.asname or alias.name for node in ast.walk(tree) if isinstance(node,ast.ImportFrom) for alias in node.names if alias.name=="SysFont"}
  for node in ast.walk(tree):
   name=call_name(node.func) if isinstance(node,ast.Call) else "";getattr_sysfont=isinstance(node,ast.Call) and isinstance(node.func,ast.Call) and call_name(node.func.func)=="getattr" and len(node.func.args)>1 and literal(node.func.args[1])=="SysFont"
   if isinstance(node,ast.Call) and (name.split(".")[-1]=="SysFont" or name in aliases or getattr_sysfont):
    if getattr_sysfont:name="getattr.SysFont"
    args=[literal(value) for value in node.args];kwargs={item.arg:literal(item.value) for item in node.keywords};rows.append((relative.as_posix(),node.lineno,name,args[0] if args else kwargs.get("name","<missing>"),args[1] if len(args)>1 else kwargs.get("size","<missing>"),bool(kwargs.get("bold",False)),bool(kwargs.get("italic",False))))
 return sorted(rows)
def source_identity(source_root):
 root=str(Path(source_root));status=subprocess.run(["git","-C",root,"status","--porcelain"],text=True,capture_output=True,check=False);head=subprocess.run(["git","-C",root,"rev-parse","HEAD"],text=True,capture_output=True,check=False);tree=subprocess.run(["git","-C",root,"rev-parse","HEAD^{tree}"],text=True,capture_output=True,check=False);return {"clean":status.returncode==0 and status.stdout=="","commit":head.stdout.strip(),"tree":tree.stdout.strip()}
def validate_manifest(manifest,source_root,check_source_identity=False,pygame_sysfont_path=None):
 errors=[]
 if manifest.get("schema_version")!="argo-discoveryworld-pinned-font-manifest/v1":errors.append("SCHEMA")
 if scan_calls(source_root)!=EXPECTED_CENSUS:errors.append("SOURCE_CALLS")
 source=manifest.get("source",{})
 if check_source_identity:
  identity=source_identity(source_root)
  if not identity["clean"] or identity["commit"]!=source.get("discoveryworld_commit") or identity["tree"]!=source.get("discoveryworld_tree"):errors.append("SOURCE_IDENTITY")
 sysfont=Path(pygame_sysfont_path or source.get("pygame_sysfont_path",""))
 if not sysfont.is_file() or sha(sysfont)!=source.get("pygame_sysfont_sha256"):errors.append("PYGAME_SYSFONT")
 calls=manifest.get("calls",[])
 if [(x.get("source"),x.get("line"),x.get("name"),x.get("size"),x.get("bold"),x.get("italic")) for x in calls]!=EXPECTED_CALLS:errors.append("MANIFEST_CALLS")
 for call in calls:
  path=Path(call.get("resolved_path",""));policy=call.get("path_policy",{})
  if policy.get("kind")=="regular":path_ok=path.is_file() and not path.is_symlink() and str(path.resolve())==policy.get("resolved_target")
  elif policy.get("kind")=="symlink":path_ok=path.is_symlink() and os.readlink(path)==policy.get("link_target") and str(path.resolve())==policy.get("resolved_target") and path.resolve().is_file()
  else:path_ok=False
  if not path_ok or sha(path)!=call.get("sha256"):errors.append("FONT_BYTES:"+str(path))
 return {"passed":not errors,"errors":errors}
def configure(pygame_module,manifest,source_root,validated=False,pygame_sysfont_path=None):
 if not validated:
  check=validate_manifest(manifest,source_root,pygame_sysfont_path=pygame_sysfont_path)
  if not check["passed"]:raise RuntimeError("FONT_MANIFEST:"+",".join(check["errors"]))
 paths={(call["name"].lower(),call["bold"],call["italic"]):call["resolved_path"] for call in manifest["calls"]};sysfont=pygame_module.sysfont;sysfont.Sysfonts.clear();sysfont.Sysalias.clear();sysfont.Sysfonts["arial"]={(False,False):paths[("arial",False,False)]};mono={(False,False):paths[("monospace",False,False)],(True,False):paths[("monospace",True,False)]};sysfont.Sysalias["monospace"]=mono;sysfont.is_init=True;return {"arial":sysfont.Sysfonts["arial"],"monospace":mono}
def load(path):return json.loads(Path(path).read_text())
