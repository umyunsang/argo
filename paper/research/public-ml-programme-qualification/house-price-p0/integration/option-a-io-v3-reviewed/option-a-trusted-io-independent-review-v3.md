# HousePrice Option-A trusted I/O narrow final-byte review v3

**Scoped verdict: one local revision remains; external launch gates are unchanged; no P0 launch.**

Reviewed frozen bytes:

- `trusted_io.py` `226df0f09185afedb84d8879dcc8ceeea555c6b441f37e8bb796b0a4a57c2380`
- `test_trusted_io.py` `b9ca0a680e512dae29d8f0e5e90701b9b2026be9ba571c5e12fe61efffcb23e5`
- `trusted-io-report.json` `1c3bb0352e1995dbefa7d1384429a9a712ce72a00824b0041b77a6be1f0755d9`

The hashes matched the root-supplied values before and after testing. V1 and V2 review files remain unchanged. I changed no implementation, test, native, or shared file. I used no real data, provider/auth, ORX run, Docker, large output, commit, or nested agent.

This review covers only HPIOV2-001, HPIOV2-002, their regressions, and the historical-selection non-regression.

## HPIOV2-001 — verified fixed

`_read_state` now compares all three duplicated final-lock fields against `final_refit_admission` (`trusted_io.py:1028-1048`):

- `execution_config_sha256`
- `outer_training_manifest_sha256`
- `hidden_features_manifest_sha256`

The exact 27-test suite passed. I also prepared three separately tampered locked states, then loaded each in a separate `/usr/bin/python3` process. All returned `STATE_CORRUPT`.

## HPIOV2-002 — partially fixed

Verified fixes:

- `admit_intent` preflights the next state before creating the store (`338-344`). With `max_state_bytes=400`, two candidates fit; the rejected closure created no extra directory.
- Census and explicit `max_snapshot_count`/`max_snapshot_bytes` enforce count and logical-byte bounds (`557-618`).
- Count boundary 2 produced `ACCEPTED, ACCEPTED, LIMIT_EXCEEDED` with two directories.
- One snapshot of exact logical size 385 was accepted. Limit 384 returned `LIMIT_EXCEEDED` with zero directories.
- A known crash/incomplete `.snapshot-<32hex>` consumed the count cap, blocked a new canonical store, and remained preserved.
- The authored mid-file `TrustedIoError` path cleaned the created temp and published no admission.
- Historical candidate A remained selected and copied after candidate B and a `final_refit` intent.

Production draft arithmetic: five maximum 393,216-byte closures plus five 350-byte manifests use 1,967,830 logical bytes. The 2,097,152-byte cap leaves 129,322 bytes. Known incomplete evidence is also counted, so it only reduces available capacity. This is a logical census, not a filesystem quota.

## HPIOV3-001 — MEDIUM: two fsync paths bypass complete handled cleanup

The cleanup fix captures the temp identity only after this sequence (`645-654`):

1. `os.mkdir(temporary)`
2. `os.fsync(snapshots_fd)`
3. open temp and record device/inode

If step 2 fails, the code converts the error to `UNSAFE_FILE`, but `temporary_identity` is still `None`; outer cleanup (`671-674`) cannot remove the directory. The fixture returned `UNSAFE_FILE`, left one temp, and published no state.

A second gap exists at `os.fsync(temporary_fd)` (`660`). It is outside an `OSError` conversion, while the outer handler catches only `TrustedIoError`. The fixture returned raw `OSError`, left one complete temp, and published no state.

The census preserves and counts both remnants on the next call, so behavior is fail closed. However, the advertised handled-failure cleanup is incomplete, avoidable capacity is consumed, and the raw error violates the safe-enum discipline.

Required fix:

1. Open the new temp and capture device/inode before the first parent-directory fsync.
2. Put all non-crash post-create `OSError` paths through identity-checked cleanup.
3. Re-raise them as `TrustedIoError(UNSAFE_FILE)`.
4. Preserve `BaseException`/real process-crash evidence.
5. Add regressions for parent fsync failure immediately after mkdir and explicit completed-temp fsync failure. Require safe enum, zero temp entries, and no admission.

## External conditions unchanged

This narrow result is not whole-launch approval. These remain open:

- HPIO-003 actual root-opened eligible dev receipt and artifact provenance;
- stable canonical roots/ancestors/mounts across a fresh process restart;
- actual T16 extension/root receipt;
- remaining bridge, ORX, container, custody, scorer, provider, and data gates.

## Exact validation

Environment: `Python 3.9.6`; `Darwin 25.5.0 arm64`; `/usr/bin/python3`.

Disposable exact-copy directory: `/tmp/hp-optiona-independent-audit-v3-5he3gd8l`.

### Compile

```text
$ /usr/bin/python3 -m py_compile trusted_io.py test_trusted_io.py
[exit 0; no output]
```

### Authored 27 tests

```text
$ /usr/bin/python3 test_trusted_io.py
test_hpio001_historical_snapshot_is_private_and_selectable_after_final_intent (__main__.TrustedIoTest) ... ok
test_hpio001_incomplete_private_snapshot_fails_closed_and_remains (__main__.TrustedIoTest) ... ok
test_hpio001_tampered_private_snapshot_cannot_be_selected (__main__.TrustedIoTest) ... ok
test_hpio002_aggregate_cap_rejects_before_second_descriptor_read (__main__.TrustedIoTest) ... ok
test_hpio004_final_identity_changes_with_stored_code_and_task (__main__.TrustedIoTest) ... ok
test_hpio005_forged_snapshot_fields_are_rederived_and_rejected (__main__.TrustedIoTest) ... ok
test_hpio006_anchored_source_and_state_root_replacement_fail_closed (__main__.TrustedIoTest) ... ok
test_hpiov2_final_lock_restart_rejects_each_duplicated_refit_field (__main__.TrustedIoTest) ... ok
test_hpiov2_handled_mid_store_failure_cleans_only_created_temp (__main__.TrustedIoTest) ... ok
test_hpiov2_known_incomplete_temp_counts_against_snapshot_caps (__main__.TrustedIoTest) ... ok
test_hpiov2_max_state_400_preflights_before_extra_store (__main__.TrustedIoTest) ... ok
test_snapshot_identity_is_opened_bytes_not_intent_self_attestation (__main__.TrustedIoTest) ... ok
test_t07_descriptor_identity_detects_fixture_swap_during_read (__main__.TrustedIoTest) ... ok
test_t07_naive_prefix_control_and_flat_name_rejection (__main__.TrustedIoTest) ... ok
test_t07_size_and_expected_hash_controls (__main__.TrustedIoTest) ... ok
test_t07_symlink_hardlink_and_fifo_controls (__main__.TrustedIoTest) ... ok
test_t07_write_rejects_existing_unsafe_target (__main__.TrustedIoTest) ... ok
test_t09_crash_stale_transaction_lock_fails_closed (__main__.TrustedIoTest) ... ok
test_t09_distinct_immutable_closures_can_be_admitted (__main__.TrustedIoTest) ... ok
test_t09_final_refit_is_one_fence_across_processes_and_restart (__main__.TrustedIoTest) ... ok
test_t09_parallel_processes_admit_one_and_only_one (__main__.TrustedIoTest) ... ok
test_t09_reload_pending_admission_is_uncertain_not_retried (__main__.TrustedIoTest) ... ok
test_t14_final_lock_binds_trusted_inputs_and_is_single_use (__main__.TrustedIoTest) ... ok
test_t14_final_lock_detects_final_code_fixture_mutation (__main__.TrustedIoTest) ... ok
test_t14_final_refit_requires_selection_binding_and_bound_run (__main__.TrustedIoTest) ... ok
test_t14_parallel_select_write_cannot_mutate_selected_code (__main__.TrustedIoTest) ... ok
test_t14_selection_requires_matching_permitted_receipt_and_freezes_writes (__main__.TrustedIoTest) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.960s

OK
```

### Independent narrow fixtures

Script SHA-256: `699496f4f5e5e1ee76ca339bb021df7fa33fdaead11654a96c9f6a5deea9159b`

```text
$ /usr/bin/python3 independent_narrow_v3.py
mid_store_handled=UNSAFE_FILE;entries=0;state_exists=False
temp_parent_fsync_failure=UNSAFE_FILE;stale_temps=1;state_exists=False
completed_temp_fsync_failure=OSError;stale_temps=1;state_exists=False
state_cap_accepted=2;rejection=LIMIT_EXCEEDED;stored=2;rejected_absent=True
crash_temp_count_boundary=LIMIT_EXCEEDED;preserved=True;canonical_absent=True
snapshot_count_boundary=['ACCEPTED', 'ACCEPTED', 'LIMIT_EXCEEDED'];directories=2
snapshot_byte_boundary_exact=ACCEPTED;below=LIMIT_EXCEEDED;below_dirs=0;exact_bytes=385
production_snapshot_cap=2097152;worst_logical=1967830;headroom=129322
historical_selection=True;copied_a=True;active_differs=True
```

### Three separate-process final-lock tamper reloads

Script SHA-256: `c8c5dce19f74781b69a6ba53bc8b5f1c2189a8ba679b3921017dc8d2e6807b43`

```text
$ cd /tmp/hp-optiona-independent-audit-v3-5he3gd8l && /usr/bin/python3 restart_lock_tamper_v3.py prepare /tmp/hp-optiona-independent-audit-v3-5he3gd8l/lock-tamper-restarts
prepared=execution_config_sha256,outer_training_manifest_sha256,hidden_features_manifest_sha256
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v3-5he3gd8l && /usr/bin/python3 restart_lock_tamper_v3.py check /tmp/hp-optiona-independent-audit-v3-5he3gd8l/lock-tamper-restarts execution_config_sha256
restart_execution_config_sha256=STATE_CORRUPT
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v3-5he3gd8l && /usr/bin/python3 restart_lock_tamper_v3.py check /tmp/hp-optiona-independent-audit-v3-5he3gd8l/lock-tamper-restarts outer_training_manifest_sha256
restart_outer_training_manifest_sha256=STATE_CORRUPT
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v3-5he3gd8l && /usr/bin/python3 restart_lock_tamper_v3.py check /tmp/hp-optiona-independent-audit-v3-5he3gd8l/lock-tamper-restarts hidden_features_manifest_sha256
restart_hidden_features_manifest_sha256=STATE_CORRUPT
[exit 0]
```

## Required disposition

1. Keep P0 unlaunched and native ARGO construction paused.
2. Fix HPIOV3-001 and rerun its two fsync negatives plus the 27 authored tests on new hashes.
3. Keep all external conditions open. This narrow review does not authorize launch.
