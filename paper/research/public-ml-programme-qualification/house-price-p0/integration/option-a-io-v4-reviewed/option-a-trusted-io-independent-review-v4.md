# HousePrice Option-A trusted I/O focused final-byte review v4

**Scoped verdict: local pass for HPIOV3-001; external gates unchanged; no P0 launch.**

Reviewed frozen bytes:

- `trusted_io.py` `66a4e8ae3dedf96d6e621a88931bd2e4b97cc746b9c2ef76644850e870fcd2e0`
- `test_trusted_io.py` `b1a0277efe1b3cfc1faf675d76c3ff36d060fcbe9552abf307988c37f2f10881`
- `trusted-io-report.json` `5a05a7fce4947fed05aa40ade363cfc9c47c1271bd36559dad15feaefa74ee35`

All hashes matched the root-supplied values before and after testing. V1–V3 review files remain unchanged. I changed no source, test, native, or shared file. I used no ORX, provider/auth, real data, Docker, nested agent, or commit.

This review covers only HPIOV3-001, its two new regressions, BaseException preservation/accounting, and the 29-test known critical regression suite.

## HPIOV3-001 — verified fixed

The new order is correct (`trusted_io.py:645-663`):

1. create the private temp directory;
2. open it and record device/inode;
3. fsync the snapshots parent;
4. write and fsync contents;
5. convert non-crash `OSError` to `TrustedIoError(UNSAFE_FILE)`.

The existing outer handler then performs exact-identity cleanup (`674-677`). `BaseException` is outside both catches, so crash-like evidence remains for census.

Independent public-path results:

- Post-mkdir parent fsync failure: `UNSAFE_FILE`, zero exact temp entries, no `state.json`, and `ADMISSION_NOT_FOUND`.
- Explicit completed-temp fsync failure: `UNSAFE_FILE`, zero exact temp entries, no `state.json`, and `ADMISSION_NOT_FOUND`.
- `CrashSentinel(BaseException)`: one temp preserved; census reported count 1 and 11 bytes; retry under `max_snapshot_count=1` returned `LIMIT_EXCEEDED`; no state was published.

The exact copied suite ran 29 tests and passed, including both new fsync regressions and the prior critical HPIO/T07/T09/T14 controls.

## External conditions unchanged

This narrow pass is not whole-launch approval. These remain open:

- HPIO-003 actual root-opened dev-receipt and artifact provenance;
- stable canonical roots/ancestors/mounts across a fresh process restart;
- actual T16 extension/root evidence;
- remaining bridge, ORX, container, custody, scorer, provider, and data gates.

## Exact validation

Environment: `Python 3.9.6`; `Darwin 25.5.0 arm64`; `/usr/bin/python3`.

Disposable exact-copy directory: `/tmp/hp-optiona-independent-audit-v4-pwmfbqzz`.

### Compile

```text
$ /usr/bin/python3 -m py_compile trusted_io.py test_trusted_io.py
[exit 0; no output]
```

### Known critical 29-test suite

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
test_hpiov3_completed_temp_fsync_failure_cleans_identified_temp_with_safe_enum (__main__.TrustedIoTest) ... ok
test_hpiov3_parent_fsync_failure_cleans_identified_temp_with_safe_enum (__main__.TrustedIoTest) ... ok
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
Ran 29 tests in 1.164s

OK
```

### Independent focused fixture

Script SHA-256: `881051c525efc3c5f6766efb645863a4a490c7c3d07da3f7ad1ff18507bb8ed4`

```text
$ /usr/bin/python3 focused_fsync_v4.py
parent_fsync=UNSAFE_FILE;exact_temp_entries=0;state_exists=False;admission=ADMISSION_NOT_FOUND
completed_temp_fsync=UNSAFE_FILE;exact_temp_entries=0;state_exists=False;admission=ADMISSION_NOT_FOUND
baseexception=CrashSentinel;preserved_entries=1;census_count=1;census_bytes=11;retry=LIMIT_EXCEEDED;state_exists=False
```

## Disposition

1. Accept HPIOV3-001 as locally closed for these frozen hashes.
2. Keep P0 unlaunched and native ARGO construction paused.
3. Keep all external conditions open. This narrow review does not authorize launch.
