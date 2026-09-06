#!/usr/bin/env python3
from __future__ import annotations
import copy,json,os,sys,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from lifecycle import ArtifactNamespace,append_record,atomic_create,ensure_directory_durable,final_status,publish_exclusive,valid_run,validate_ledger,validate_manifest
M=json.loads((HERE/"manifest.json").read_text());EMPTY_RUN={"exit_code":None,"timed_out":False,"global_deadline":False,"controller_signal":None,"unreaped":False,"duration_seconds":0.0,"pid":None,"pgid":None,"output_identities":{}}
class Tests(unittest.TestCase):
 def test_manifest_valid(self):self.assertTrue(validate_manifest(M)["passed"])
 def test_exact_grid_not_counts_only(self):
  x=copy.deepcopy(M);x["ordered_cells"][1]["cell_id"]=x["ordered_cells"][0]["cell_id"];self.assertFalse(validate_manifest(x)["passed"])
 def test_path_traversal_rejected(self):
  x=copy.deepcopy(M);x["ordered_cells"][0]["stdout_path"]="../x";self.assertFalse(validate_manifest(x)["passed"])
 def test_bool_not_integer(self):
  x=copy.deepcopy(M);x["ordered_cells"][0]["seed"]=True;self.assertFalse(validate_manifest(x)["passed"]);bad=dict(EMPTY_RUN,duration_seconds=True);self.assertFalse(valid_run(bad));bad=dict(EMPTY_RUN,duration_seconds="slow");self.assertFalse(valid_run(bad))
 def test_pinned_namespace_rejects_root_symlink(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td);target=parent/"target";target.mkdir();link=parent/"receipts";link.symlink_to(target,target_is_directory=True)
   with self.assertRaises(OSError):ArtifactNamespace(link)
 def test_pinned_namespace_rejects_file_symlink_replacement(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);namespace=ArtifactNamespace(root);namespace.create_bytes("side/cell/raw",b"safe");secret=root/"secret";secret.write_bytes(b"secret");path=root/"side/cell/raw";path.unlink();path.symlink_to(secret)
   with self.assertRaises(RuntimeError):namespace.read_bytes("side/cell/raw")
   namespace.close()
 def test_pinned_namespace_detects_root_replacement(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td);root=parent/"receipts";root.mkdir();namespace=ArtifactNamespace(root);namespace.create_bytes("ledger",b"original");root.rename(parent/"old");root.mkdir();(root/"ledger").write_bytes(b"replacement");self.assertFalse(namespace.verify());self.assertEqual(os.pread(namespace.files["ledger"],8,0),b"original");namespace.close()
 def test_pinned_namespace_pending_symlink_cannot_publish(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);namespace=ArtifactNamespace(root);namespace.create_bytes("pending",b"payload");secret=root/"secret";secret.write_bytes(b"payload");(root/"pending").unlink();(root/"pending").symlink_to(secret)
   with self.assertRaises(RuntimeError):namespace.publish("pending","result")
   self.assertFalse((root/"result").exists());namespace.close()
 def test_pinned_namespace_publishes_same_inode_and_fd_ledger(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);namespace=ArtifactNamespace(root);previous=namespace.append_record("ledger",{"event":"x"});self.assertEqual(json.loads(namespace.read_bytes("ledger"))["record_sha256"],previous);namespace.create_bytes("pending",b"payload");identity=os.fstat(namespace.files["pending"]);published=namespace.publish("pending","result");self.assertEqual((published.st_dev,published.st_ino),(identity.st_dev,identity.st_ino));self.assertEqual(namespace.read_bytes("result"),b"payload");namespace.close()
 def test_atomic_race_one_winner(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"m";
   with ThreadPoolExecutor(max_workers=2) as ex:r=list(ex.map(lambda _:atomic_create(p,b"x"),range(2)))
   self.assertEqual(sorted(r),[False,True])
 def test_hash_chain_and_transitions(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});cell=M["ordered_cells"][0];h=append_record(p,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"timestamp":"t"},h);h=append_record(p,{"event":"spawned","sequence":2,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"pid":1,"pgid":1,"timestamp":"t"},h);append_record(p,{"event":"finished","sequence":3,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"status":"valid_complete","exit_code":0,"timed_out":False,"stdout":{},"stderr":{},"events":{},"ui_gzip":{},"frame_manifest":{},"run":EMPTY_RUN,"cell_result_sha256":"f"*64,"timestamp":"t"},h);self.assertTrue(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_tampered_ledger_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});p.write_text(p.read_text().replace('"run_id"', '"run_ix"',1));self.assertFalse(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_header_identity_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});self.assertFalse(validate_ledger(p,M,allow_partial=True,expected_header={"manifest_sha256":"d"*64})["passed"])
 def test_final_statuses(self):
  self.assertEqual(final_status(["valid_complete"]*30,["EXACT"]*30),"PASS");self.assertEqual(final_status(["valid_complete"]*30,["EXACT"]*29+["OBSERVED_MISMATCH"]),"FAIL_PARITY_NOT_ESTABLISHED");self.assertEqual(final_status(["timeout"]+["valid_complete"]*29,["UNOBSERVABLE"]*30),"INVALID");self.assertEqual(final_status(["valid_complete"]*29,["UNOBSERVABLE"]*30),"INCOMPLETE")
 def test_planned_to_spawn_failure_is_legal(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});c=M["ordered_cells"][0];h=append_record(p,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":c["cell_id"],"cell_nonce":c["cell_nonce"],"cell_index":0,"timestamp":"t"},h);append_record(p,{"event":"finished","sequence":2,"run_id":M["run_id"],"cell_id":c["cell_id"],"cell_nonce":c["cell_nonce"],"cell_index":0,"status":"spawn_failure","exit_code":None,"timed_out":False,"stdout":{},"stderr":{},"events":{},"ui_gzip":{},"frame_manifest":{},"run":EMPTY_RUN,"cell_result_sha256":"f"*64,"timestamp":"t"},h);self.assertTrue(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_post_final_record_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"l";h=append_record(p,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});h=append_record(p,{"event":"finalized","sequence":1,"run_id":M["run_id"],"status":"INCOMPLETE","result_sha256":"a"*64,"timestamp":"t"},h);append_record(p,{"event":"controller_stop","sequence":2,"run_id":M["run_id"],"reason":"x","timestamp":"t"},h);self.assertFalse(validate_ledger(p,M,allow_partial=True)["passed"])
 def test_write_all_handles_short_writes(self):
  import lifecycle,os
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"m";original=os.write
   def short(fd,data):return original(fd,bytes(data[:max(1,len(data)//2)]))
   with patch("lifecycle.os.write",side_effect=short):self.assertTrue(atomic_create(p,b"abcdefghij"))
   self.assertEqual(p.read_bytes(),b"abcdefghij")
 def test_result_publication_is_atomic_and_exclusive(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);temp=root/"pending";result=root/"result";self.assertTrue(atomic_create(temp,b"complete"));identity=(temp.stat().st_dev,temp.stat().st_ino);publish_exclusive(temp,result);self.assertEqual((result.stat().st_dev,result.stat().st_ino),identity);self.assertEqual(result.read_bytes(),b"complete");self.assertFalse(temp.exists());second=root/"second";self.assertTrue(atomic_create(second,b"other"))
   with self.assertRaises(FileExistsError):publish_exclusive(second,result)
   self.assertEqual(result.read_bytes(),b"complete")
 def test_nested_directory_creation_fsyncs_each_parent_entry(self):
  import lifecycle
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);calls=[];original=lifecycle.fsync_parent
   def record(path):calls.append(Path(path));return original(path)
   with patch("lifecycle.fsync_parent",side_effect=record):ensure_directory_durable(root/"sidecars"/"cell")
   self.assertEqual(calls,[root/"sidecars",root/"sidecars"/"cell"])
 def test_partial_mode_still_requires_every_planned_cell_terminal(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/"ledger";cell=M["ordered_cells"][0];h=append_record(path,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});append_record(path,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"timestamp":"t"},h);self.assertFalse(validate_ledger(path,M,allow_partial=True)["passed"])
 def test_finalized_result_mutual_binding_passes(self):
  import hashlib
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);ledger=root/"ledger";h=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});mode=[{**pair,"status":"UNOBSERVABLE"} for pair in M["mode_pairs"]];repeat=[{**pair,"status":"UNOBSERVABLE"} for pair in M["ui_repeat_pairs"]];timing=[{**pair,"observed":False,"official_seconds":None,"ui_only_seconds":None,"ui_minus_official_seconds":None,"ui_to_official_ratio":None} for pair in M["mode_pairs"]];summary={"cells_planned":0,"valid_complete":0,"mode_exact":0,"mode_mismatch":0,"mode_unobservable":20,"ui_repeat_exact":0,"ui_repeat_mismatch":0,"ui_repeat_unobservable":10,"timing_pairs_observed":0,"controller_error":None};result={"schema_version":"argo-discoveryworld-ui-parity-result/v1","run_id":M["run_id"],"status":"INCOMPLETE","approval_sha256":"b"*64,"manifest_sha256":"a"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"cells":{},"mode_pairs":mode,"ui_repeat_pairs":repeat,"timing_pairs":timing,"summary":summary,"ledger_last_record_sha256_before_final":h,"model_calls":0,"spend_usd":0.0};payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()+b"\n";path=root/"pending";path.write_bytes(payload);append_record(ledger,{"event":"finalized","sequence":1,"run_id":M["run_id"],"status":"INCOMPLETE","result_sha256":hashlib.sha256(payload).hexdigest(),"timestamp":"t"},h);self.assertTrue(validate_ledger(ledger,M,allow_partial=True,result_payload_path=path)["passed"])
 def test_two_field_result_is_rejected(self):
  import hashlib
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);ledger=root/"ledger";h=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});result={"status":"INCOMPLETE","ledger_last_record_sha256_before_final":h};payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()+b"\n";path=root/"pending";path.write_bytes(payload);append_record(ledger,{"event":"finalized","sequence":1,"run_id":M["run_id"],"status":"INCOMPLETE","result_sha256":hashlib.sha256(payload).hexdigest(),"timestamp":"t"},h);self.assertFalse(validate_ledger(ledger,M,allow_partial=True,result_payload_path=path)["passed"])
 def test_finalized_record_rehashes_pending_result(self):
  import hashlib
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);payload=root/"pending";payload.write_bytes(b"payload");ledger=root/"ledger";h=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});append_record(ledger,{"event":"finalized","sequence":1,"run_id":M["run_id"],"status":"INCOMPLETE","result_sha256":"0"*64,"timestamp":"t"},h);self.assertFalse(validate_ledger(ledger,M,allow_partial=True,result_payload_path=payload)["passed"])
 def test_failure_sidecar_is_rehashed_when_claimed(self):
  import hashlib
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);raw=root/"stdout";raw.write_bytes(b"failure");meta={"path":str(raw),"size":7,"sha256":hashlib.sha256(b"failure").hexdigest()};ledger=root/"ledger";h=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});cell=M["ordered_cells"][0];h=append_record(ledger,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"timestamp":"t"},h);append_record(ledger,{"event":"finished","sequence":2,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"status":"spawn_failure","exit_code":None,"timed_out":False,"stdout":meta,"stderr":{},"events":{},"ui_gzip":{},"frame_manifest":{},"run":{"exit_code":0,"timed_out":False,"global_deadline":False,"controller_signal":None,"unreaped":False,"duration_seconds":1.0,"pid":1,"pgid":1,"output_identities":{}},"cell_result_sha256":"f"*64,"timestamp":"t"},h);self.assertTrue(validate_ledger(ledger,M,allow_partial=True,strict_sidecars=True)["passed"]);raw.write_bytes(b"changed");self.assertFalse(validate_ledger(ledger,M,allow_partial=True,strict_sidecars=True)["passed"])
 def test_strict_valid_complete_rehashes_sidecars(self):
  import hashlib
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);ledger=root/"ledger";h=append_record(ledger,{"event":"header","schema_version":"argo-ui-parity-ledger/v1","run_id":M["run_id"],"manifest_sha256":"a"*64,"approval_sha256":"b"*64,"source_archive_sha256":"c"*64,"preflight_identity_sha256":"d"*64,"execution_root_sha256":"e"*64,"started_at":"t"});cell=M["ordered_cells"][0];h=append_record(ledger,{"event":"planned","sequence":1,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"timestamp":"t"},h);h=append_record(ledger,{"event":"spawned","sequence":2,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"pid":1,"pgid":1,"timestamp":"t"},h);metas={}
   for key in ["stdout","stderr","events","ui_gzip","frame_manifest"]:
    path=root/key;data=b"" if key in {"stdout","stderr"} else b"x";path.write_bytes(data);metas[key]={"path":str(path),"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}
   append_record(ledger,{"event":"finished","sequence":3,"run_id":M["run_id"],"cell_id":cell["cell_id"],"cell_nonce":cell["cell_nonce"],"cell_index":0,"status":"valid_complete","exit_code":0,"timed_out":False,**metas,"run":{"exit_code":0,"timed_out":False,"global_deadline":False,"controller_signal":None,"unreaped":False,"duration_seconds":1.0,"pid":1,"pgid":1,"output_identities":{}},"cell_result_sha256":"f"*64,"timestamp":"t"},h);self.assertTrue(validate_ledger(ledger,M,allow_partial=True,strict_sidecars=True)["passed"]);(root/"events").write_bytes(b"bad");self.assertFalse(validate_ledger(ledger,M,allow_partial=True,strict_sidecars=True)["passed"])
 def test_interrupted_result_publication_never_creates_partial_result(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);temp=root/"pending";result=root/"result";self.assertTrue(atomic_create(temp,b"complete"))
   with patch("lifecycle.os.link",side_effect=OSError("interrupt")):
    with self.assertRaises(OSError):publish_exclusive(temp,result)
   self.assertFalse(result.exists());self.assertEqual(temp.read_bytes(),b"complete")
if __name__=="__main__":unittest.main(verbosity=2)
