#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from run import IMAGE, TIMEOUT_SECONDS, build_command, execute, parse_canary, validate_approval

RUNNER=HERE/"run.py"; POLICY=HERE/"policy_stdout.py"; RELEASED=HERE.parent/"historical_multihop/released"
TEMPLATE=json.loads((HERE/"approval-template.json").read_text())

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def valid():
    value=copy.deepcopy(TEMPLATE);value.update({"status":"APPROVED","approved_by":"user","runner_sha256":sha(RUNNER),"policy_sha256":sha(POLICY)});return value

class V3Tests(unittest.TestCase):
    def test_unapproved_fails_closed(self): self.assertFalse(validate_approval(TEMPLATE,RUNNER,POLICY)["approved"])
    def test_exact_approval_passes(self): self.assertTrue(validate_approval(valid(),RUNNER,POLICY)["approved"])
    def test_hash_drift_fails(self):
        value=valid();value["policy_sha256"]="0"*64;self.assertFalse(validate_approval(value,RUNNER,POLICY)["approved"])
    def test_no_writable_host_or_temp_mount(self):
        command=build_command(POLICY,RELEASED);mounts=[command[i+1] for i,x in enumerate(command) if x=="--mount"]
        self.assertEqual(len(mounts),2);self.assertTrue(all("readonly" in x for x in mounts));self.assertFalse(any("/output" in x or "/var/folders" in x for x in mounts))
    def test_security_resource_flags(self):
        joined=" ".join(build_command(POLICY,RELEASED))
        for required in ["--pull never","--network none","--read-only","--cap-drop ALL","--pids-limit 64","--memory 256m","--cpus 1","--user 501:20"]: self.assertIn(required,joined)
    def test_stdout_json_is_parsed(self):
        run={"exit_code":0,"timed_out":False,"stdout":json.dumps({"released_case_readable":True}),"stderr":""};self.assertTrue(parse_canary(run)["released_case_readable"])
    def test_failed_run_has_no_canary(self): self.assertEqual(parse_canary({"exit_code":125,"timed_out":False,"stdout":"","stderr":"x"}),{})
    def test_timeout_fails_closed(self):
        with patch("run.subprocess.run",side_effect=subprocess.TimeoutExpired(["docker"],30)): result=execute(["docker","run"])
        self.assertEqual(result["exit_code"],124);self.assertTrue(result["timed_out"]);self.assertEqual(TIMEOUT_SECONDS,30)

if __name__=="__main__": unittest.main(verbosity=2)
