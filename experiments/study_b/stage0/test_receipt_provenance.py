#!/usr/bin/env python3
"""Failing-first tests for receipt provenance and referenced-byte identity."""
from __future__ import annotations
import copy, hashlib, tempfile
from pathlib import Path
import receipt_provenance as prov
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def expect(n,fn,text):
 try:fn();check(n,False,"no error")
 except prov.ProvenanceViolation as e:check(n,text in str(e),str(e))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);tr=root/"transcript.jsonl";art=root/"answer.json";tr.write_text("event\n");art.write_text("{}\n")
  r={"origin":"model_call","model_provider_revision":{"model_id":"model-x","api_revision":"2026-09-04","provider_revision":"rev-1"},"protocol_fingerprint":"a"*64,"harness_commit":"b"*40,"task_hash":"c"*64,"command":["runner","--cell","G1C1F1"],"environment_hash":"d"*64,"transcript_paths":[{"path":"transcript.jsonl","sha256":h(tr)}],"artifact_paths":[{"path":"answer.json","sha256":h(art)}],"started_at":"2026-09-04T10:00:00+09:00","finished_at":"2026-09-04T10:01:00+09:00","exit_state":"success","usage":{"tokens":100,"tool_calls":3,"wall_seconds":60.0,"cost_usd":0.01}}
  check("complete provenance passes",prov.validate(r,root)["passed"])
  missing=copy.deepcopy(r);missing.pop("task_hash");expect("missing field is named",lambda:prov.validate(missing,root),"RECEIPT_PROVENANCE_MISSING: task_hash")
  stale=copy.deepcopy(r);stale["artifact_paths"][0]["sha256"]="0"*64;expect("stale artifact hash fails",lambda:prov.validate(stale,root),"RECEIPT_ARTIFACT_IDENTITY_MISMATCH: answer.json")
  absent=copy.deepcopy(r);absent["transcript_paths"][0]["path"]="absent.jsonl";expect("absent transcript fails",lambda:prov.validate(absent,root),"RECEIPT_TRANSCRIPT_IDENTITY_MISMATCH: absent.jsonl")
  backwards=copy.deepcopy(r);backwards["finished_at"]="2026-09-04T09:59:00+09:00";expect("backwards time fails",lambda:prov.validate(backwards,root),"RECEIPT_TIME_ORDER_INVALID")
  guessed=copy.deepcopy(r);guessed["usage"]["tokens"]=-1;expect("negative usage fails",lambda:prov.validate(guessed,root),"RECEIPT_USAGE_INVALID: tokens")
  shell=copy.deepcopy(r);shell["command"]="runner --cell G1C1F1";expect("shell command string fails",lambda:prov.validate(shell,root),"RECEIPT_COMMAND_NOT_ARGV")
  badfp=copy.deepcopy(r);badfp["protocol_fingerprint"]="short";expect("protocol digest shape fails",lambda:prov.validate(badfp,root),"RECEIPT_PROTOCOL_FINGERPRINT_INVALID")
  no_rev=copy.deepcopy(r);no_rev["model_provider_revision"]["provider_revision"]="";expect("provider revision is required",lambda:prov.validate(no_rev,root),"RECEIPT_PROVIDER_REVISION_MISSING")
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
