"""Pinned ORX CLI capture parsers; mutation tests, not new process launches."""
from __future__ import annotations
import unittest
from pathlib import Path
from orx_text import ParseError, parse_created_experiment, parse_local_launch, parse_experiment_status, parse_run_rows, parse_log_window, parse_cancel_ack

FIXTURES = Path(__file__).with_name("orx_text_fixtures")
EXP="cbfc2315-b262-4608-806a-65f0080de6e5"
RUN="191407a0-84ce-47e6-afa4-298d034b8aa3"
COMMIT="99f66129ad6be4fa8feeb05377a113b63ad84162"
TITLE="HP native fixture success"
COMMAND="/usr/bin/python3 fixture.py"

def fixture(name):return (FIXTURES/name).read_text()

class OrxTextTest(unittest.TestCase):
    def test_create_and_launch_use_exact_field_not_all_uuid_occurrences(self):
        created=parse_created_experiment(fixture("create-baseline.txt"),TITLE,COMMAND)
        self.assertEqual(created.experiment_id,EXP)
        self.assertEqual(created.branch,"orx/hp-native-fixture-success")
        self.assertEqual(parse_local_launch(fixture("launch-local.txt"),EXP).run_id,RUN)
        for value in [fixture("launch-local.txt").replace("  run  "+RUN,"  run  "+EXP),
                      fixture("launch-local.txt")+"EXTRA\n",fixture("launch-local.txt").replace("✓ Local run started.","queued"),
                      fixture("launch-local.txt").replace("  run  ","  run  "+RUN+"\n  run  ")]:
            with self.assertRaises(ParseError):parse_local_launch(value,EXP)
        with self.assertRaises(ParseError):parse_created_experiment(fixture("create-baseline.txt"),"wrong",COMMAND)

    def test_child_creation_record_is_exact_and_inherits_command(self):
        child=parse_created_experiment(fixture("create-child.txt"),"HP native fixture failure",COMMAND)
        self.assertEqual(child.experiment_id,"0ff6de0a-bea0-4fb8-a76b-aaa82fbf5415")
        self.assertEqual(child.branch,"orx/hp-native-fixture-failure")
        with self.assertRaises(ParseError):
            parse_created_experiment(fixture("create-child.txt").replace("  command: ","  command: different "),"HP native fixture failure",COMMAND)

    def test_status_never_run_and_full_commit_after_terminal(self):
        never=parse_experiment_status(fixture("status-never-run.txt"),EXP,TITLE,COMMAND)
        self.assertIsNone(never.run_id);self.assertIsNone(never.commit_sha)
        done=parse_experiment_status(fixture("status-done.txt"),EXP,TITLE,COMMAND)
        self.assertEqual(done.run_id,RUN);self.assertEqual(done.status,"DONE")
        self.assertEqual(done.commit_sha,COMMIT)
        for value in [fixture("status-done.txt").replace(COMMIT,"0"*40),
                      fixture("status-done.txt")+"  shell: bad\n",
                      fixture("status-done.txt").replace("  id:       "+EXP,"  id:       "+RUN),
                      fixture("status-done.txt").replace("(done, commit","(newstate, commit")]:
            with self.assertRaises(ParseError):parse_experiment_status(value,EXP,TITLE,COMMAND)

    def test_failure_reason_not_returned_and_table_duplicates_fail(self):
        fail_exp="0ff6de0a-bea0-4fb8-a76b-aaa82fbf5415"
        failed=parse_experiment_status(fixture("status-failed.txt"),fail_exp,"HP native fixture failure",COMMAND)
        self.assertEqual(failed.status,"FAILED")
        self.assertNotIn("Job failed",repr(failed))
        rows=parse_run_rows(fixture("runs-done.txt"),TITLE)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0].run_id,RUN)
        self.assertEqual(rows[0].status,"DONE")
        failrows=parse_run_rows(fixture("runs-failed.txt"),"HP native fixture failure")
        self.assertEqual(failrows[0].status,"FAILED")
        duplicate=fixture("runs-done.txt")+fixture("runs-done.txt").split("\n")[2]+"\n"
        with self.assertRaises(ParseError):parse_run_rows(duplicate,TITLE)
        with self.assertRaises(ParseError):parse_run_rows(fixture("runs-done.txt"),"another title")

    def test_cancellation_ack_is_not_terminal_and_cancelled_capture_parses(self):
        run="ff653932-3e4e-4bb6-8fab-f6c3764a1acb"
        self.assertEqual(parse_cancel_ack(fixture("cancel-ack.txt"),run),run)
        with self.assertRaises(ParseError):parse_cancel_ack(fixture("cancel-ack.txt"),RUN)
        status=parse_experiment_status(fixture("status-cancelled.txt"),"ee8c06bb-dcce-410e-b5fe-23b271d51b38","HP native fixture cancellation",COMMAND)
        self.assertEqual(status.status,"CANCELLED")
        self.assertEqual(parse_run_rows(fixture("runs-cancelled.txt"),"HP native fixture cancellation")[0].status,"CANCELLED")

    def test_exact_observed_empty_runs_message_is_empty_but_other_prose_is_rejected(self):
        self.assertEqual(parse_run_rows(fixture("runs-empty.txt"),TITLE),())
        for text in ["No runs found.","No runs found.\nEXTRA\n","no runs found.\n","No runs.\n"]:
            with self.subTest(text=text),self.assertRaises(ParseError):parse_run_rows(text,TITLE)

    def test_log_offsets_not_display_byte_count_and_no_strip_of_real_lf(self):
        full=parse_log_window((FIXTURES/"log-full.stdout").read_bytes(),fixture("log-full.stderr"))
        window=parse_log_window((FIXTURES/"log-range.stdout").read_bytes(),fixture("log-range.stderr"))
        self.assertEqual(full.data,(FIXTURES/"log-full.stdout").read_bytes())
        self.assertEqual(window.data,full.data[:64]);self.assertTrue(window.transport_lf_removed)
        self.assertEqual(window.end,64);self.assertEqual(window.total,len(full.data))
        for data,meta in [(window.data+b"XX",fixture("log-range.stderr")),(b"x", "[local file] bytes 0–2 of 1\n"),(b"x", "unknown\n")]:
            with self.assertRaises(ParseError):parse_log_window(data,meta)

    def test_all_parsers_reject_oversized_or_injected_control_text(self):
        with self.assertRaises(ParseError):parse_local_launch("x"*70000,EXP)
        with self.assertRaises(ParseError):parse_local_launch(fixture("launch-local.txt").replace("  run", "\x00  run"),EXP)
        with self.assertRaises(ParseError):parse_run_rows(fixture("runs-done.txt").replace("done", "queued"),TITLE)

if __name__=="__main__":unittest.main(verbosity=2)
