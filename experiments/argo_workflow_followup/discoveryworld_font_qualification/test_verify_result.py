#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import verify_result as V
RUN="dw-font-registry-qual-20260906-v1"
def fixture(root):
 paths={"marker":"marker","ledger":"ledger","result":"result"};manifest={"paths":paths};(root/"manifest").write_text(json.dumps(manifest));approval={"bindings":{"manifest":{"path":"manifest"}}};(root/"approval").write_text(json.dumps(approval));marker={"run_id":RUN,"no_retry":True};(root/"marker").write_bytes(V.canonical(marker)+b"\n");result={"schema_version":"argo-font-qualification-result/v1","run_id":RUN,"status":"PASS","cells_planned":2,"cell_results":[{"validation":{"passed":True},"run":{"unreaped":False}},{"validation":{"passed":True},"run":{"unreaped":False}}],"comparison":{"passed":True,"matched_calls":5},"font_pre_post_stable":True,"source_pre_post_stable":True,"sealed_runtime_postcheck":True,"within_deadline":True,"scenario_loads":0,"agent_observations":0,"model_calls":0,"docker_calls":0,"spend_usd":0.0,"no_retry":True};rb=V.canonical(result)+b"\n";(root/"result").write_bytes(rb);previous=None;rows=[]
 for event in ["header","planned","spawned","finished","planned","spawned","finished"]:
  row={"event":event,"previous_sha256":previous};row["record_sha256"]=hashlib.sha256(V.canonical(row)).hexdigest();previous=row["record_sha256"];rows.append(row)
 row={"event":"finalized","status":"PASS","result_sha256":hashlib.sha256(rb).hexdigest(),"previous_sha256":previous};row["record_sha256"]=hashlib.sha256(V.canonical(row)).hexdigest();rows.append(row);(root/"ledger").write_bytes(b"".join(V.canonical(x)+b"\n" for x in rows));return root/"approval"
class Tests(unittest.TestCase):
 def test_valid_pass_integrity(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);approval=fixture(root)
   with patch.object(V,"validate_approval",return_value={"approved":True}):out=V.verify(root,approval)
   self.assertEqual(out["verdict"],"PASS");self.assertEqual(out["controller_status"],"PASS")
 def test_invalid_result_can_be_integrity_pass(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);approval=fixture(root);r=json.loads((root/"result").read_text());r["status"]="INVALID";(root/"result").write_bytes(V.canonical(r)+b"\n");lines=[json.loads(x) for x in (root/"ledger").read_bytes().splitlines()];body=dict(lines[-1]);body.update({"status":"INVALID","result_sha256":V.sha(root/"result")});body.pop("record_sha256");body["record_sha256"]=hashlib.sha256(V.canonical(body)).hexdigest();lines[-1]=body;(root/"ledger").write_bytes(b"".join(V.canonical(x)+b"\n" for x in lines))
   with patch.object(V,"validate_approval",return_value={"approved":True}):out=V.verify(root,approval)
   self.assertEqual(out["verdict"],"PASS");self.assertEqual(out["controller_status"],"INVALID")
 def test_ledger_mutation_fails(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=Path(td);approval=fixture(root);lines=(root/"ledger").read_bytes().splitlines();row=json.loads(lines[2]);row["pid"]=1;lines[2]=V.canonical(row);(root/"ledger").write_bytes(b"\n".join(lines)+b"\n")
   with patch.object(V,"validate_approval",return_value={"approved":True}):out=V.verify(root,approval)
   self.assertEqual(out["verdict"],"FAIL")
if __name__=="__main__":unittest.main(verbosity=2)
