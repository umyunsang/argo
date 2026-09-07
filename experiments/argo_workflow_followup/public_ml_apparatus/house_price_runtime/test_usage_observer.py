"""Root-selected native session directory reader; synthetic session bytes only."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import parse_session_usage
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import UsageObserver, UsageObserverConfig, UsageObservationError

HERE=Path(__file__).parent
FIXTURE=HERE/"a2-frontend-probes"/"evidence"/"installed-main-native-session-v1.jsonl"

class UsageObserverTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-usage-observer-")
        self.root=Path(self.temp.name).resolve()
        self.current=self.root/"session";self.current.mkdir(mode=0o700)
        self.identity=DirectoryIdentity(self.current,self.current.stat().st_dev,self.current.stat().st_ino)
        original=FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(),"3f7b6a84d8ed486b549f6fb4c255fad64c13d4d19b58e60cc8b5eff7fd6b937a")
        self.records=[json.loads(line) for line in original.split(b"\n") if line]
        # This derived positive fixture is not an unchanged native capture.
        for row in self.records:
            if row.get("message",{}).get("role")=="assistant":
                row["message"]["responseId"]="synthetic-response-"+row["id"]
        self.raw=("\n".join(json.dumps(row,separators=(",",":")) for row in self.records)+"\n").encode()
        self.header=self.records[0]
        self.config=UsageObserverConfig(self.identity,self.header["cwd"],"a2-faux-6122","a2-probe",120000,())
        self.observer=UsageObserver(self.config)
    def tearDown(self):self.temp.cleanup()
    def write(self,records=None):
        path=self.current/(self.header["id"]+".jsonl")
        path.write_bytes(self.raw if records is None else ("\n".join(json.dumps(row) for row in records)+"\n").encode())
        return path
    def test_waiting_is_not_zero_complete_and_native_bytes_count(self):
        waiting=self.observer.observe()
        self.assertEqual(waiting.state,"WAITING_FIRST_USAGE");self.assertFalse(waiting.complete)
        self.assertIsNone(waiting.current_tokens);self.assertIsNone(waiting.stop_reason)
        self.write();result=self.observer.observe()
        self.assertEqual(result.state,"WITHIN_BUDGET");self.assertEqual(result.current_tokens,3745)
        self.assertTrue(result.complete);self.assertIsNone(result.stop_reason)
        self.assertEqual(result.session_sha256,hashlib.sha256(self.raw).hexdigest())
    def test_combined_limit_counts_prior_not_reset_and_disallows_duplicate_session(self):
        prior_id="ff653932-3e4e-4bb6-8fab-f6c3764a1acb"
        prior_rows=json.loads(json.dumps(self.records));prior_rows[0]["id"]=prior_id
        for row in prior_rows:
            msg=row.get("message",{})
            if msg.get("responseId"):msg["responseId"]+="-prior"
        raw=("\n".join(json.dumps(row) for row in prior_rows)+"\n").encode()
        prior=parse_session_usage(raw,prior_id,self.header["cwd"],"a2-faux-6122","a2-probe")
        observer=UsageObserver(UsageObserverConfig(self.identity,self.header["cwd"],"a2-faux-6122","a2-probe",7000,(prior,)))
        self.write();result=observer.observe()
        self.assertEqual(result.total_tokens,7490);self.assertEqual(result.stop_reason,"CAMPAIGN_TOKEN_TRIGGER")
        repeated=parse_session_usage(self.raw,self.header["id"],self.header["cwd"],"a2-faux-6122","a2-probe")
        observer=UsageObserver(UsageObserverConfig(self.identity,self.header["cwd"],"a2-faux-6122","a2-probe",120000,(repeated,)))
        self.assertEqual(observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
    def test_unknown_partial_and_counter_regression_stop_after_record(self):
        path=self.write();self.observer.observe()
        path.write_bytes(self.raw[:-1]);self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        self.write();self.observer.observe()
        earlier=self.records[:-1];self.write(earlier)
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
    def test_links_multiple_files_and_root_replacement_are_rejected(self):
        target=self.root/"outside.jsonl";target.write_bytes(self.raw)
        link=self.current/(self.header["id"]+".jsonl");link.symlink_to(target)
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        link.unlink();self.write();(self.current/"extra.jsonl").write_bytes(self.raw)
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        self.current.rename(self.root/"old");self.current.mkdir()
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
    def test_wrong_native_identity_and_oversize_fail_closed(self):
        changed=json.loads(json.dumps(self.records));changed[0]["cwd"]="/wrong"
        self.write(changed);self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        path=self.write()
        with path.open("wb") as stream:stream.truncate(8388609)
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")

    def test_foreign_filename_and_sticky_unknown_never_reenable_work(self):
        foreign=self.current/"foreign.jsonl";foreign.write_bytes(self.raw)
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        foreign.unlink();self.write()
        self.assertEqual(self.observer.observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")

    def test_counter_regression_is_detected_without_prior_unknown_state(self):
        self.write();self.observer.observe()
        self.write(self.records[:-1])
        result=self.observer.observe()
        self.assertEqual(result.stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        self.assertEqual(result.total_tokens,3745)

    def test_restored_checkpoint_rejects_rollback_and_missing_file(self):
        path=self.write();first=self.observer.observe()
        checkpoint=self.observer.export_checkpoint()
        self.write(self.records[:-1])
        restored=UsageObserver(self.config,checkpoint=checkpoint)
        result=restored.observe()
        self.assertEqual(result.stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        self.assertEqual(result.total_tokens,first.total_tokens)
        stopped=restored.export_checkpoint()
        path.unlink()
        self.assertEqual(UsageObserver(self.config,checkpoint=stopped).observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")

    def test_restored_checkpoint_validates_configuration_types_and_prefix(self):
        path=self.write();self.observer.observe();checkpoint=self.observer.export_checkpoint()
        restored=UsageObserver(self.config,checkpoint=checkpoint)
        self.assertEqual(restored.observe().total_tokens,3745)
        for field,value in [("config_sha256","0"*64),("counts",[True,13,503,1615])]:
            changed=json.loads(json.dumps(checkpoint));changed[field]=value
            with self.assertRaises(UsageObservationError):UsageObserver(self.config,checkpoint=changed)
        data=path.read_bytes();path.write_bytes(data.replace(b"synthetic",b"sYnthEtic"))
        # Alter a complete byte prefix even if numeric counters stay unchanged.
        if path.read_bytes()==data:path.write_bytes(data.replace(b"assistant",b"Assistant",1))
        self.assertEqual(UsageObserver(self.config,checkpoint=checkpoint).observe().stop_reason,"CAMPAIGN_USAGE_UNKNOWN")

    def test_restored_checkpoint_allows_only_real_append_and_preserves_waiting(self):
        empty=self.observer.observe()
        resumed=UsageObserver(self.config,checkpoint=self.observer.export_checkpoint())
        self.assertEqual(resumed.observe(),empty)
        path=self.write()
        prefix=b"\n".join(self.raw.split(b"\n")[:-2])+b"\n"
        path.write_bytes(prefix)
        first=resumed.observe();self.assertEqual(first.state,"WITHIN_BUDGET")
        self.assertLess(first.current_tokens,3745)
        checkpoint=resumed.export_checkpoint()
        path.write_bytes(self.raw)
        appended=UsageObserver(self.config,checkpoint=checkpoint).observe()
        self.assertEqual(appended.current_tokens,3745)
        self.assertEqual(appended.state,"WITHIN_BUDGET")

    def test_restored_checkpoint_rejects_replaced_identical_file(self):
        path=self.write();first=self.observer.observe();checkpoint=self.observer.export_checkpoint()
        replacement=self.root/"replacement.jsonl";replacement.write_bytes(self.raw)
        replacement.replace(path)
        result=UsageObserver(self.config,checkpoint=checkpoint).observe()
        self.assertEqual(result.stop_reason,"CAMPAIGN_USAGE_UNKNOWN")
        self.assertEqual(result.current_tokens,first.current_tokens)

    def test_original_native_capture_missing_ids_stops_but_retains_known_counts(self):
        path=self.write();path.write_bytes(FIXTURE.read_bytes())
        result=self.observer.observe()
        self.assertEqual(result.state,"USAGE_UNKNOWN")
        self.assertEqual(result.current_tokens,3745)
        self.assertFalse(result.complete)
        restored=UsageObserver(self.config,checkpoint=self.observer.export_checkpoint())
        self.assertEqual(restored.observe(),result)

if __name__=="__main__":unittest.main(verbosity=2)
