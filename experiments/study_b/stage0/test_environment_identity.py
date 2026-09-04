#!/usr/bin/env python3
"""Failing-first tests for exact agent/scorer environment parity."""
from __future__ import annotations
import copy
import environment_identity as env
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except env.EnvironmentViolation as e:check(n,text in str(e),str(e))
def manifest():return {"os":"linux","architecture":"x86_64","python":"3.11.15","container_digest":"sha256:"+"a"*64,"packages":[{"name":"numpy","version":"1.26.4","artifact_sha256":"b"*64,"source":"wheel"},{"name":"scipy","version":"1.15.3","artifact_sha256":"c"*64,"source":"wheel"}]}
def main():
 a=manifest();b=copy.deepcopy(a);result=env.require_parity(a,b,{"numpy","scipy"});check("identical environments pass",result["passed"])
 missing=copy.deepcopy(b);missing["packages"].pop();expect("missing package fails",lambda:env.require_parity(a,missing,{"numpy","scipy"}),"ENVIRONMENT_PACKAGE_SET_MISMATCH")
 version=copy.deepcopy(b);version["packages"][0]["version"]="1.26.3";expect("version drift fails",lambda:env.require_parity(a,version,{"numpy","scipy"}),"ENVIRONMENT_PACKAGE_IDENTITY_MISMATCH: numpy")
 artifact=copy.deepcopy(b);artifact["packages"][0]["artifact_sha256"]="d"*64;expect("artifact drift fails",lambda:env.require_parity(a,artifact,{"numpy","scipy"}),"ENVIRONMENT_PACKAGE_IDENTITY_MISMATCH: numpy")
 extra=copy.deepcopy(b);extra["packages"].append({"name":"pandas","version":"2.0.3","artifact_sha256":"e"*64,"source":"wheel"});expect("extra package fails parity",lambda:env.require_parity(a,extra,{"numpy","scipy"}),"ENVIRONMENT_PACKAGE_SET_MISMATCH")
 platform=copy.deepcopy(b);platform["architecture"]="arm64";expect("platform drift fails",lambda:env.require_parity(a,platform,{"numpy","scipy"}),"ENVIRONMENT_PLATFORM_MISMATCH: architecture")
 unpinned=manifest();unpinned["packages"][0]["version"]="<2.0";expect("version range is not exact",lambda:env.validate_manifest(unpinned),"ENVIRONMENT_VERSION_NOT_EXACT: numpy")
 moving=manifest();moving["packages"][0].update(source="git",source_ref="main");expect("moving git ref fails",lambda:env.validate_manifest(moving),"ENVIRONMENT_SOURCE_REF_NOT_IMMUTABLE: numpy")
 dup=manifest();dup["packages"].append(copy.deepcopy(dup["packages"][0]));expect("duplicate package fails",lambda:env.validate_manifest(dup),"ENVIRONMENT_DUPLICATE_PACKAGE: numpy")
 absent_req=manifest();expect("task requirement must be present",lambda:env.require_parity(absent_req,copy.deepcopy(absent_req),{"numpy","pandas"}),"ENVIRONMENT_REQUIRED_PACKAGE_MISSING: pandas")
 check("environment hash is deterministic",env.environment_hash(a)==env.environment_hash(copy.deepcopy(a)))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
