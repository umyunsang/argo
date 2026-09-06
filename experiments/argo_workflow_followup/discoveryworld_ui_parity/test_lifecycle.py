#!/usr/bin/env python3
from __future__ import annotations
import copy,json,sys,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from lifecycle import append_record,atomic_create,final_status,validate_ledger,validate_manifest
M=json.loads((HERE/"manifest.json").read_text())
class Tests(unittest.TestCase):
 def test_manifest_valid(self):self.assertTrue(validate_manifest(M)["passed"])
 def test_exact_grid_not_counts_only(self):
  x=copy.deepcopy(M);x["ordered_cells"][1]["cell_id"]=x["ordered_cells"][0]["cell_id"];self.assertFalse(validate_manifest(x)["passed"])
 def test_path_traversal_rejected(self):
  x=copy.deepcopy(M);x["ordered_cells"][0]["stdout_path"]="../x";self.assertFalse(validate_manifest(x)["passed"])
 def test_bool_not_integer(self):
  x=copy.deepcopy(M);x["ordered_cells"][0]["seed"]=True;self.assertFalse(validate_manifest(x)["passed"])
 def test_atomic_race_one_winner(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"m";
   with ThreadPoolExecutor(max_workers=2) as ex:r=list(ex.map(lambda _:atomic_create(p,b"x"),range(2)))
   self.assertEqual(sorted(r),[False,True])
 def test_hash_chain_and_transitions(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"started_at":"t"});cell=M["ordered_cells"][0];h=append_record(p,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"timestamp":"t"},h);h=append_record(p,{"event":"spawned","sequence":2,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"pid":1,"pgid":1,"timestamp":"t"},h);append_record(p,{"event":"finished","sequence":3,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"status":"valid_complete","exit_code":0,"timed_out":False,"stdout":{},"stderr":{},"events":{},"ui_gzip":{},"frame_manifest":{},"timestamp":"t"},h);self.assertTrue(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_tampered_ledger_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"started_at":"t"});p.write_text(p.read_text().replace('"run_id"', '"run_ix"',1));self.assertFalse(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_header_identity_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"started_at":"t"});self.assertFalse(validate_ledger(p,M,allow_partial=True,expected_header={"manifest_sha256":"d"*64})["passed"])
 def test_final_statuses(self):
  self.assertEqual(final_status(["valid_complete"]*30,["EXACT"]*30),"PASS");self.assertEqual(final_status(["valid_complete"]*30,["EXACT"]*29+["OBSERVED_MISMATCH"]),"FAIL_PARITY_NOT_ESTABLISHED");self.assertEqual(final_status(["timeout"]+["valid_complete"]*29,["UNOBSERVABLE"]*30),"INVALID");self.assertEqual(final_status(["valid_complete"]*29,["UNOBSERVABLE"]*30),"INCOMPLETE")
 def test_planned_to_spawn_failure_is_legal(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"started_at":"t"});c=M["ordered_cells"][0];h=append_record(p,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":c["cell_id"],"cell_nonce":c["cell_nonce"],"cell_index":0,"timestamp":"t"},h);append_record(p,{"event":"finished","sequence":2,"run_id":M["run_id"],"cell_id":c["cell_id"],"cell_nonce":c["cell_nonce"],"cell_index":0,"status":"spawn_failure","exit_code":None,"timed_out":False,"stdout":{},"stderr":{},"events":{},"ui_gzip":{},"frame_manifest":{},"timestamp":"t"},h);self.assertTrue(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_post_final_record_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"started_at":"t"});h=append_record(p,{"event":"finalized","sequence":1,"run_id":M["run_id"],"status":"INCOMPLETE","result_sha256":"a"*64,"timestamp":"t"},h);append_record(p,{"event":"controller_stop","sequence":2,"run_id":M["run_id"],"reason":"x","timestamp":"t"},h);self.assertFalse(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_write_all_handles_short_writes(self):
  import lifecycle,os
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"m";original=os.write
   def short(fd,data):return original(fd,bytes(data[:max(1,len(data)//2)]))
   with patch("lifecycle.os.write",side_effect=short):self.assertTrue(atomic_create(p,b"abcdefghij"))
   self.assertEqual(p.read_bytes(),b"abcdefghij")
if __name__=="__main__":unittest.main(verbosity=2)
