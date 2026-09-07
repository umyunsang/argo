# Independent review: A2 one-shot process boundary

- Generated: `2026-09-07T20:36:08.594169+09:00`
- Decision: **FAIL CURRENT FROZEN PROCESS BOUNDARY**
- Status: `EXECUTION_BLOCKED__4_FINDINGS__NO_REAL_P0`
- Review request: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-process-review-request-v1.json` (`845a63545a09ef8e4675293a124663738fc47f6ad41bebc2d1d9023e4eb02c5c`)
- Execution hold: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-process-group-safety-hold-v1.json` (`6cc69fc2163f2c881abfddba08a4aafd066411697c5917b8ed7f1ecaa5ad5351`)
- Review type: code-first, independent, synthetic only. No real Prime, provider, auth, data, ORX, Docker, or P0 action.

## Bottom line

The 20 frozen synthetic component tests pass from byte-exact external copies. The approved RSS control is correctly described as a sampled trigger that may overshoot, not a hard memory limit. CPU and file-size limits are per-process and per-file. Aggregate bytes and file count are monitored census triggers.

The component is still blocked. Cleanup can signal a recycled unrelated OS identity. Three additional fail-closed or durability defects remain. `cleanup_unconfirmed` is not mitigation for an unsafe signal already sent.

## Source hash closure

| Path | Bytes | Expected SHA-256 | Post-check SHA-256 | Match |
|---|---:|---|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py` | 65211 | `325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0` | `325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py` | 11770 | `38222a04f075e313f7281ccef32c33a7f23796aee355054ae7f292adc1b9dcf2` | `38222a04f075e313f7281ccef32c33a7f23796aee355054ae7f292adc1b9dcf2` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py` | 23058 | `f44f1d3d562834abf4f9a88ceef4cdf3ea4e7380b7aac1db28829c045a275e6a` | `f44f1d3d562834abf4f9a88ceef4cdf3ea4e7380b7aac1db28829c045a275e6a` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json` | 22636 | `252258df2156815b65524472cafc4a511843ddd22e01579a91d19ceb87499f7e` | `252258df2156815b65524472cafc4a511843ddd22e01579a91d19ceb87499f7e` | true |

Exact external copy root: `/private/tmp/argo-a2-independent-review-_834rq5n`. Each of the four copied files matched the repo source hash before execution. The post-check hash command below confirms the repo sources remained unchanged.

## Findings

### 1. A2-PROCESS-001 — P0 BLOCKER: Cleanup can signal a recycled unrelated PID or process group from stale/coarse process identity

**Locations:** `controller_process.py:415-426`, `controller_process.py:541-553`, `controller_process.py:945-1010`, `controller_process.py:1147-1186`, `controller_process.py:1189-1230`

**Evidence**

- On process-table failure, sample() appends process_table_unavailable but does not clear last_rows.
- _bounded_cleanup() ignores the return value of cleanup samples and then _signal_tracked() authorizes signals from alive_tracked(), which reads last_rows.
- With a reaped fake root and a stale same-PGID descendant, the mock-only fixture recorded killpg(424242, SIGTERM) and killpg(424242, SIGKILL); cleanup_confirmed=false is recorded only after those calls.
- The sole non-root identity field is /bin/ps lstart text. A fresh fake row with a recycled escaped-descendant PID and the same one-second lstart string was accepted and os.kill(515152, SIGTERM) would be sent. The existing root-reuse test excludes a reaped root PID through the Popen state and therefore does not cover escaped descendants.

**Impact:** The controller can harm an unrelated OS process or group. A cleanup_unconfirmed receipt is not mitigation because it is produced after the unsafe signal.

**Required repair**

- Treat a successful, immediately preceding process snapshot as signal authorization. Clear/invalidate last_rows on every observer error or missing required identity.
- Keep the direct live Popen root group as a separate safe case: killpg is allowed only while process.poll() is None, root_pgid == process.pid, and the owned setsid condition is established.
- Never signal an obsolete root PGID from stale rows after the Popen root has been reaped. For escaped observed PIDs/groups, require a fresh unambiguous higher-resolution start identity immediately before signaling; if that cannot be proven, send no signal and return cleanup_unconfirmed.

**Narrow regression:** Mock a reaped root, stale same-PGID descendant, and _snapshot_processes failure; patch os.kill/os.killpg and assert zero calls plus cleanup_unconfirmed. Separately inject a recycled escaped-descendant PID with an ambiguous same-second lstart identity and assert zero calls.

### 2. A2-PROCESS-002 — P1 HIGH: A final artifact-census failure can still produce succeeded

**Locations:** `controller_process.py:500-512`, `controller_process.py:1196-1230`, `controller_process.py:1533-1553`

**Evidence**

- Monitor.sample() returns artifact_census_failed and appends census_errors, but _bounded_cleanup() discards every sample return.
- Cleanup confirmation tests observer_errors but not census_errors. The status branch then selects succeeded for returncode 0 when the earlier run-loop reason remained None.
- The mock-only final-census fixture returned two artifact_root_stat_missing errors, cleanup_confirmed=true, and the exact run-controller status branch evaluates to succeeded.

**Impact:** A fast child can mutate artifacts and exit between the last run-loop sample and cleanup; a missing/replaced/unreadable artifact root discovered only during cleanup is not fail-closed.

**Required repair**

- Propagate cleanup-sample terminal reasons. Include census_errors in cleanup/resource validity. A final census error must prevent succeeded and retain artifact_census_failed (or a stricter invalid status).

**Narrow regression:** Use a reaped fake process with returncode 0, prior reason None, a successful fake process snapshot, and a final _Census error; assert the composed run receipt is not succeeded.

### 3. A2-PROCESS-003 — P1 HIGH: Canonical file identity and config size checks are not descriptor-bound

**Locations:** `process_exec.py:41-77`, `process_exec.py:285-326`, `controller_process.py:1579-1588`

**Evidence**

- _verify_file() stats a pathname, _sha256() opens it again, returns the pathname, and execve/Node later opens that pathname. There is no descriptor binding across stat, hash, and use.
- The mock-only race swapped the frontend pathname after the verified hash read. _verify_file() returned normally although the pathname then had a different inode and SHA-256.
- _read_config() stats size <=1 MiB and then opens by pathname. A bounded fake race replaced the 2-byte file before open; json.load read and accepted 1,048,847 bytes, above the 1,048,576-byte gate.

**Impact:** Concurrent same-owner mutation can make the executed/read bytes differ from the frozen identities and can bypass the config read bound. The checks do not establish an atomic launch identity.

**Required repair**

- Open with O_NOFOLLOW, validate fstat identity, hash/read from that same descriptor with a strict byte bound, and reject trailing bytes or post-read identity change. Keep execution/use bound to the verified descriptor or a measured equivalent that closes the pathname race.

**Narrow regression:** Deterministically replace the pathname between stat/hash/open/use and assert preflight rejection; replace a small config between stat and open with >1 MiB JSON and assert bounded rejection before full read.

### 4. A2-PROCESS-004 — P1 HIGH: Receipt creation can return normally after a partial write and does not durably commit the directory entry

**Locations:** `controller_process.py:1591-1604`

**Evidence**

- _write_receipt() calls os.write() once and ignores its returned byte count.
- The mock-only partial-write fixture wrote one byte (`{`); _write_receipt() returned normally.
- Only the regular-file descriptor is fsynced. The parent directory containing the new O_EXCL receipt is never fsynced.

**Impact:** The CLI can report success while the receipt is truncated, and a crash can lose the new receipt directory entry even after file fsync.

**Required repair**

- Write until the full payload is committed, treat zero/short terminal writes as failure, fsync the file, then fsync the parent directory. Ensure failure does not leave an apparently final receipt that blocks safe retry.

**Narrow regression:** Patch os.write to return a sequence of short writes and assert full valid JSON plus newline; record fsync targets and assert both regular file and parent directory are synced.

## Scoped results

| Area | Result | Detail |
|---|---|---|
| Frozen inputs | `PASS` | All four request-bound repo files matched expected SHA-256 before copy and after checks. |
| Independent component suite | `PASS_WITH_SCOPE` | 20/20 synthetic tests passed from byte-exact external copies in 5.582s. These tests exercise real POSIX RLIMIT_CPU/RLIMIT_FSIZE and fake frontend processes only. |
| CPU/file limits | `PASS_WITH_SCOPE` | RLIMIT_CPU is per process and RLIMIT_FSIZE is per regular file. Neither is an aggregate-tree hard limit; the receipts state this. |
| Wall deadline | `PASS_WITH_SCOPE` | Phase and campaign monotonic deadlines are parent-side, outside Node. Terminal elapsed includes bounded TERM/KILL/reap grace and is not equal to the raw deadline. |
| RSS and aggregate controls | `PASS_WITH_SCOPE` | RSS, aggregate bytes, and file count are sampled/observed triggers with recorded overshoot. RSS is not represented as a kernel hard memory ceiling. |
| Observed tree/setsid | `BLOCKED_BY_A2-PROCESS-001` | The existing setsid escape case passes normal-path cleanup, but stale/coarse identity signal authorization is unsafe. Claims remain observed-only and never all-descendant. |
| Observer/missing root | `PASS_WITH_DEFECT_BOUNDARY` | A missing live root in an otherwise successful snapshot returns process_observer_failed. Observer failure becomes cleanup_unconfirmed, but A2-PROCESS-001 shows signals may already have been unsafe. |
| Direct dataclass numeric caps | `PASS` | The suite rejects NaN, infinities, and booleans. Source validation also rejects nonpositive caps, oversized grace/observer windows, and nonzero provider retries. |
| Production command/environment/stdin | `PASS_SOURCE_ONLY` | The final target argv exactly matches the frozen seven-element argv contract; production child environment is exactly the frozen eight keys; child stdin is DEVNULL. No production frontend/provider was executed. |
| Output/receipt | `BLOCKED_BY_A2-PROCESS-004` | stdout/stderr creation is O_EXCL, no-follow where available, regular 0600. Final receipt durability/completeness is not proven. |

## External gates

- **A2 execution hold — `BLOCKING`:** Do not execute run_controller/cleanup from controller SHA 325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0 until A2-PROCESS-001 is repaired and independently reviewed.
- **Frontend artifact-root mtime ordering — `EXTERNAL_FRONTEND_OWNER`:** Known integration condition. Frontend owner is repairing/testing it separately. It is not counted as a new process-boundary finding.
- **Root usage accounting — `EXTERNAL_ROOT_GATE`:** Completed-record/session JSONL parsing and live missing/in-flight stop integration remain root-owned and absent here. Missing/in-flight usage must remain unknown, never zero.
- **Production integration — `NOT_TESTED`:** controller-main source is contextual only. Fake-Python component tests do not prove the full production frontend, auth, provider, session-record, or P0 path.

## Commands and full outputs

### recovery_process_scan

Command:
```text
ps -axo pid=,ppid=,etime=,command= | grep -E 'option-a2|house-price-p0|p0.*synthetic|synthetic.*p0' | grep -v grep
```
Exit code: `1`

Full output:
```text
(no stdout or stderr)
```

### independent_20_case_suite

Command:
```text
cd /private/tmp/argo-a2-independent-review-_834rq5n && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -m unittest -v test_controller_process.py
```
Exit code: `0`; duration: `5.710801s`

Full output:
```text
test_artifact_symlink_census_fails_closed (test_controller_process.ControllerProcessTests.test_artifact_symlink_census_fails_closed) ... ok
test_cli_sigterm_handler_preserves_receipt_and_cleans_child (test_controller_process.ControllerProcessTests.test_cli_sigterm_handler_preserves_receipt_and_cleans_child) ... ok
test_cpu_rlimit_is_actual_posix_behavior (test_controller_process.ControllerProcessTests.test_cpu_rlimit_is_actual_posix_behavior) ... ok
test_created_regular_file_is_hard_capped_by_actual_rlimit_fsize (test_controller_process.ControllerProcessTests.test_created_regular_file_is_hard_capped_by_actual_rlimit_fsize) ... ok
test_environment_is_allowlisted_before_helper_and_worker_flags_are_stripped (test_controller_process.ControllerProcessTests.test_environment_is_allowlisted_before_helper_and_worker_flags_are_stripped) ... ok
test_escaped_setsid_descendant_is_ancestry_tracked_and_individually_cleaned (test_controller_process.ControllerProcessTests.test_escaped_setsid_descendant_is_ancestry_tracked_and_individually_cleaned) ... ok
test_exit_zero_retains_private_raw_files_and_typed_handle (test_controller_process.ControllerProcessTests.test_exit_zero_retains_private_raw_files_and_typed_handle) ... ok
test_extra_environment_keys_fail_before_spawn (test_controller_process.ControllerProcessTests.test_extra_environment_keys_fail_before_spawn) ... ok
test_frozen_production_target_argv_and_environment_names (test_controller_process.ControllerProcessTests.test_frozen_production_target_argv_and_environment_names) ... ok
test_hard_phase_deadline_is_outside_uncooperative_child (test_controller_process.ControllerProcessTests.test_hard_phase_deadline_is_outside_uncooperative_child) ... ok
test_interpreter_chain_identity_change_fails_before_spawn (test_controller_process.ControllerProcessTests.test_interpreter_chain_identity_change_fails_before_spawn) ... ok
test_monitored_aggregate_trigger_records_sampled_overshoot (test_controller_process.ControllerProcessTests.test_monitored_aggregate_trigger_records_sampled_overshoot) ... ok
test_monitored_file_count_trigger_records_overshoot (test_controller_process.ControllerProcessTests.test_monitored_file_count_trigger_records_overshoot) ... ok
test_nonfinite_and_boolean_caps_fail_before_spawn (test_controller_process.ControllerProcessTests.test_nonfinite_and_boolean_caps_fail_before_spawn) ... ok
test_nonzero_exit_is_terminal_and_not_retried (test_controller_process.ControllerProcessTests.test_nonzero_exit_is_terminal_and_not_retried) ... ok
test_parent_abort_terminates_and_escalates_when_term_is_ignored (test_controller_process.ControllerProcessTests.test_parent_abort_terminates_and_escalates_when_term_is_ignored) ... ok
test_path_identity_change_fails_closed_without_spawn (test_controller_process.ControllerProcessTests.test_path_identity_change_fails_closed_without_spawn) ... ok
test_root_pid_identity_is_latched_and_reused_pid_is_not_adopted (test_controller_process.ControllerProcessTests.test_root_pid_identity_is_latched_and_reused_pid_is_not_adopted) ... ok
test_sampled_rss_trigger_records_overshoot_and_coverage (test_controller_process.ControllerProcessTests.test_sampled_rss_trigger_records_overshoot_and_coverage) ... ok
test_stdout_is_hard_capped_by_actual_rlimit_fsize (test_controller_process.ControllerProcessTests.test_stdout_is_hard_capped_by_actual_rlimit_fsize) ... ok

----------------------------------------------------------------------
Ran 20 tests in 5.582s

OK

```

### negative_fixture_initial_noncanonical_temp_setup

Command:
```text
cd /private/tmp/argo-a2-independent-review-_834rq5n && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python independent_negative_fixtures.py
```
Exit code: `1`; duration: `0.120544s`

Full output:
```text
Traceback (most recent call last):
  File "/private/tmp/argo-a2-independent-review-_834rq5n/independent_negative_fixtures.py", line 116, in <module>
    returned = pe._verify_file(
               ^^^^^^^^^^^^^^^^
  File "/private/tmp/argo-a2-independent-review-_834rq5n/process_exec.py", line 63, in _verify_file
    raise ValueError("noncanonical_file")
ValueError: noncanonical_file

```

Evidence use: excluded; setup path was not canonical.

### negative_fixture_corrected_mock_only

Command:
```text
cd /private/tmp/argo-a2-independent-review-_834rq5n && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python independent_negative_fixtures.py
```
Exit code: `0`; duration: `0.085837s`

Full output:
```text
{
  "config_size_check_not_descriptor_bound": {
    "accepted_over_cap_replacement": true,
    "bytes_actually_read": 1048847,
    "nominal_cap_bytes": 1048576,
    "result": "accepted-replacement"
  },
  "missing_live_root_snapshot_positive_control": {
    "observer_errors": [
      "live_root_missing_from_process_table"
    ],
    "reason": "process_observer_failed"
  },
  "observer_failure_stale_group_signal": {
    "cleanup_confirmed": false,
    "group_signals_that_would_be_sent": [
      [
        424242,
        "SIGTERM"
      ],
      [
        424242,
        "SIGKILL"
      ]
    ],
    "observer_errors": [
      "process_table_unavailable",
      "process_table_unavailable",
      "process_table_unavailable",
      "process_table_unavailable",
      "process_table_unavailable"
    ],
    "pid_signals_that_would_be_sent": []
  },
  "receipt_partial_write_and_fsync_scope": {
    "fsync_descriptor_kinds": [
      "regular_file"
    ],
    "parent_directory_fsynced": false,
    "receipt_bytes": "{",
    "writer_returned_normally": true
  },
  "same_second_descendant_pid_reuse": {
    "group_signals_that_would_be_sent": [],
    "identity_surface": "ps lstart (one-second text)",
    "pid_signals_that_would_be_sent": [
      [
        515152,
        "SIGTERM"
      ]
    ]
  },
  "verified_path_changes_before_use": {
    "different_after_verify": true,
    "expected_sha256": "a545a4a5c6ccf087bde8db7f1ec55743915f010d804327d16e5633a15b0813ad",
    "inode_changed_after_verify": true,
    "post_verify_sha256": "ee1c5bc4f3faa1acf2348d44b86250d21f93eb67bc8b642a68c84ba2b97a5dc7",
    "verify_returned": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-a2-negative-fixtures-0o9nv4if/frontend.py"
  }
}

```

### final_census_mock_only

Command:
```text
cd /private/tmp/argo-a2-independent-review-_834rq5n && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python independent_final_census_fixture.py
```
Exit code: `0`; duration: `0.100399s`

Full output:
```text
{
  "census_errors": [
    "artifact_root_stat_missing",
    "artifact_root_stat_missing"
  ],
  "cleanup_confirmed": true,
  "observer_errors": [],
  "returncode": 0,
  "run_controller_status_branch_if_prior_reason_none": "succeeded"
}

```

### post_check_source_hash_closure

Command:
```text
cd /Users/um-yunsang/argo-paper-orx && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -c 'import hashlib,json,pathlib
root=pathlib.Path("/Users/um-yunsang/argo-paper-orx")
items=[('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py'"'"', '"'"'325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py'"'"', '"'"'38222a04f075e313f7281ccef32c33a7f23796aee355054ae7f292adc1b9dcf2'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py'"'"', '"'"'f44f1d3d562834abf4f9a88ceef4cdf3ea4e7380b7aac1db28829c045a275e6a'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json'"'"', '"'"'252258df2156815b65524472cafc4a511843ddd22e01579a91d19ceb87499f7e'"'"')]
print(json.dumps([{"path":p,"expected":x,"actual":hashlib.sha256((root/p).read_bytes()).hexdigest(),"bytes":(root/p).stat().st_size,"mtime_ns":(root/p).stat().st_mtime_ns} for p,x in items],sort_keys=True,indent=2))'
```
Exit code: `0`; duration: `0.064455s`

Full output:
```text
[
  {
    "actual": "325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0",
    "bytes": 65211,
    "expected": "325767163f1b315a2fcba3dcd65b8941f136bbc7753a8055f1bbd12d55297df0",
    "mtime_ns": 1788778426479380962,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py"
  },
  {
    "actual": "38222a04f075e313f7281ccef32c33a7f23796aee355054ae7f292adc1b9dcf2",
    "bytes": 11770,
    "expected": "38222a04f075e313f7281ccef32c33a7f23796aee355054ae7f292adc1b9dcf2",
    "mtime_ns": 1788778343734812232,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py"
  },
  {
    "actual": "f44f1d3d562834abf4f9a88ceef4cdf3ea4e7380b7aac1db28829c045a275e6a",
    "bytes": 23058,
    "expected": "f44f1d3d562834abf4f9a88ceef4cdf3ea4e7380b7aac1db28829c045a275e6a",
    "mtime_ns": 1788778289609438599,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py"
  },
  {
    "actual": "252258df2156815b65524472cafc4a511843ddd22e01579a91d19ceb87499f7e",
    "bytes": 22636,
    "expected": "252258df2156815b65524472cafc4a511843ddd22e01579a91d19ceb87499f7e",
    "mtime_ns": 1788778727892461196,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json"
  }
]

```

## Fixture provenance

- `independent_negative_fixtures.py`: SHA-256 `01394b629bf16c6fcf793c08aa2aa1fec13a0a35b31fd23bcbcc2dc014072874`. Exact source is embedded in `option-a2-process-independent-review.json`.
- `independent_final_census_fixture.py`: SHA-256 `862ed984fc6266e07097d30d9f5ac2ac49161ff3973ad963412579adc7bf950e`. Exact source is embedded in `option-a2-process-independent-review.json`.
- All signal functions were mocked in negative reproductions. No live signal was sent.
- The 20-case suite ran before the root execution hold was received. After the hold, only mock-only/read-only evidence checks ran.

## Scope boundary

The fake-Python suite is component evidence only. It does not prove the full production `controller-main` frontend, native auth/provider behavior, completed session-record parsing, or live campaign stop integration. The known artifact-root directory-mtime ordering issue remains with the frontend owner and is not counted as a new finding here. Root-owned completed-record parsing and missing/in-flight usage stop integration remain explicit external gates. Missing or in-flight usage is unknown, never zero.
