#!/usr/bin/env python3
"""Exact environment-manifest validation for agent/scorer parity."""
from __future__ import annotations
import hashlib,json,re
class EnvironmentViolation(ValueError):pass
HEX64=re.compile(r"^[0-9a-f]{64}$");HEX40=re.compile(r"^[0-9a-f]{40}$")
def require(ok:bool,msg:str)->None:
 if not ok:raise EnvironmentViolation(msg)
def normalize_name(name:str)->str:return re.sub(r"[-_.]+","-",name.strip().lower())
def validate_manifest(m:dict)->dict:
 for field in ("os","architecture","python","container_digest","packages"):require(field in m,f"ENVIRONMENT_FIELD_MISSING: {field}")
 require(isinstance(m["container_digest"],str) and m["container_digest"].startswith("sha256:") and bool(HEX64.fullmatch(m["container_digest"][7:])),"ENVIRONMENT_CONTAINER_DIGEST_INVALID")
 require(isinstance(m["packages"],list),"ENVIRONMENT_PACKAGES_INVALID")
 seen={};normalized=[]
 for p in m["packages"]:
  name=normalize_name(str(p.get("name","")));require(bool(name),"ENVIRONMENT_PACKAGE_NAME_MISSING");require(name not in seen,f"ENVIRONMENT_DUPLICATE_PACKAGE: {name}")
  version=p.get("version");require(isinstance(version,str) and bool(version) and not re.search(r"[<>=~!*]",version),f"ENVIRONMENT_VERSION_NOT_EXACT: {name}")
  artifact=p.get("artifact_sha256");require(isinstance(artifact,str) and bool(HEX64.fullmatch(artifact)),f"ENVIRONMENT_ARTIFACT_HASH_INVALID: {name}")
  source=p.get("source");require(source in ("wheel","sdist","conda","git"),f"ENVIRONMENT_SOURCE_INVALID: {name}")
  if source=="git":require(bool(HEX40.fullmatch(str(p.get("source_ref","")))),f"ENVIRONMENT_SOURCE_REF_NOT_IMMUTABLE: {name}")
  rec={"name":name,"version":version,"artifact_sha256":artifact,"source":source}
  if source=="git":rec["source_ref"]=p["source_ref"]
  seen[name]=rec;normalized.append(rec)
 return {"passed":True,"packages":dict(sorted(seen.items())),"package_count":len(seen)}
def environment_hash(m:dict)->str:
 v=validate_manifest(m);canonical={"os":m["os"],"architecture":m["architecture"],"python":m["python"],"container_digest":m["container_digest"],"packages":[v["packages"][k] for k in sorted(v["packages"])]};return hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def require_parity(agent:dict,scorer:dict,required_packages:set[str])->dict:
 a=validate_manifest(agent);s=validate_manifest(scorer)
 for field in ("os","architecture","python","container_digest"):
  require(agent[field]==scorer[field],f"ENVIRONMENT_PLATFORM_MISMATCH: {field} agent={agent[field]} scorer={scorer[field]}")
 an=set(a["packages"]);sn=set(s["packages"]);require(an==sn,f"ENVIRONMENT_PACKAGE_SET_MISMATCH: agent_only={sorted(an-sn)} scorer_only={sorted(sn-an)}")
 for name in sorted(normalize_name(x) for x in required_packages):require(name in an,f"ENVIRONMENT_REQUIRED_PACKAGE_MISSING: {name}")
 for name in sorted(an):require(a["packages"][name]==s["packages"][name],f"ENVIRONMENT_PACKAGE_IDENTITY_MISMATCH: {name}")
 ah=environment_hash(agent);sh=environment_hash(scorer);require(ah==sh,f"ENVIRONMENT_HASH_MISMATCH: agent={ah} scorer={sh}")
 return {"passed":True,"environment_hash":ah,"package_count":len(an),"required_packages":sorted(normalize_name(x) for x in required_packages)}
