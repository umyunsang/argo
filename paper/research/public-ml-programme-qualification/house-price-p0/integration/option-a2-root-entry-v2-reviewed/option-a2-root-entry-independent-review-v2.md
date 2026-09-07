# Option A2 root entry independent review v2

## Decision

**PASS — all five v1 findings are resolved on the repaired hash-bound bytes.**

This is a narrow synthetic re-review only. It is not actual P0 execution or production admission. A2 approval `fe261b55`, paused native construction, and pending user-local OAuth remain unchanged.

## Repaired source hashes

All six files matched `option-a2-root-entry-repair-validation-v2.json` before and after this review.

| File | SHA-256 |
|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/run_entry.py` | `87ea3dfb433f96fd806bf112215ef3c1841ff51851bdaa5c900bbc929400b054` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_run_entry.py` | `39426510964153e5332313d72155b9ee691dce23265b7f95f24d53c9166cfe9f` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/staging.py` | `9813081081af6b128a1c91eb06c4ba07fa6c260eee8984c708c3094e3a635800` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_staging.py` | `a6308b655b964eff1e3d4d09f0b5732909959d6c2fde56202a8f09b7698b2d97` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/receipt_store.py` | `2c5a4b6978596b0f50a41543c909464f92d8a8376341f6bf0692ede5d79d4d4c` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_receipt_store.py` | `ea487c560560f35dbf1b43d3ef561c457e6ae6052ead7d74eb4577c3c9de56f8` |

Repair validation:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-root-entry-repair-validation-v2.json`
- SHA-256 `6f6aecbff0887ee1abb08b09efce99ec1cc6b9cac7f200cd2cb5b2ac7352ea31`

## Prior finding recheck

### F-01 — RESOLVED: Safe run-entry CSV and path-loop error closure

- run_entry.py:73-77 converts Path.resolve RuntimeError to EntryError.
- run_entry.py:312-313 converts csv.Error and RuntimeError to EntryError.
- test_run_entry.py:166-183 asserts each malformed-CSV/path-loop case returns 1, emits exactly one ARGO_HP_RESULT, exposes no temporary root path, and never calls the runner.

Conclusion: Malformed strict CSV and symlink-loop configuration now terminate through the one safe protocol record.

### F-02 — RESOLVED: Durable SCORER_ERROR after successful runner execution

- run_entry.py:289-297 catches post-run GradingError and sets status SCORER_ERROR with predictions, rows, and metric all null.
- run_entry.py:298-304 still validates the run directory and exclusively writes runner-receipt.json before returning.
- test_run_entry.py:185-193 uses exact-ID finite 1e32 predictions and verifies the saved receipt equals the returned SCORER_ERROR receipt.

Conclusion: The formerly receiptless finite-1e32 path now publishes the frozen durable terminal receipt with null metric/output fields.

### F-03 — RESOLVED: Bounded log counters and truncation consistency

- run_entry.py:256-264 enforces exact integer/nonnegative fields, aggregate <= log cap + 2048, truncation equivalence to aggregate > cap, LOG_LIMIT_EXCEEDED/truncation agreement, and no truncated SUCCESS.
- The +2048 allowance is the fixed upper overshoot from at most two 1024-byte drain reads already in flight in the hash-bound runner.
- test_run_entry.py:195-205 rejects the prior 10**100 case and four boundary/status inconsistencies without writing a receipt.

Conclusion: Malformed runner log claims no longer cross into the trusted receipt.

### F-04 — RESOLVED: Safe staging symlink-loop error

- staging.py:34-49 now maps RuntimeError to StagingError with fixed SELECTED_CODE_INVALID text.
- test_staging.py:46-49 exercises a self-referential symlink and asserts the exact safe error.

Conclusion: The staging helper no longer leaks Path.resolve RuntimeError.

### F-05 — RESOLVED: Descriptor-bound local-runs/run/repo cwd identity

- run_entry.py:89-111 opens local_runs_root, run UUID, and repo with O_DIRECTORY|O_NOFOLLOW and relative dir_fd traversal; fstat/lstat device+inode identities must agree.
- run_entry.py:173 and 207 call the identity verifier before and after config/runtime/input validation and require the same identity tuple.
- test_run_entry.py:207-229 observes relative descriptor opens and rejects a different repo inode before staging/dispatch.

Conclusion: The prior path-equality-only relationship is replaced by the required descriptor identity check and before/after agreement.

No new finding was found within this narrow scope.

## False-positive `001` correction

- The former substring assertion could match an unrelated SHA-256 value.
- The repaired test checks exact scalar string values for `001` and `002` and disallows row-bearing receipt schema keys.
- Receipt construction remains a fixed field dictionary. No production output byte/hash, prediction, final-target, or schema guard was removed.

## Exact native executions

### Full 22-test suite

Command:

```text
/usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_receipt_store
```

Full output:

```text
test_bad_config_paths_identity_runtime_caps_and_cwd_fail_before_runner (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_boolean_row_count_fails_closed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_descriptor_relationship_rejects_a_different_repo_inode (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_dev_receipt_from_actual_fixed_inputs_no_native_commit_selfhash (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_final_has_no_targets_or_metric_and_wrong_phase_config_fails (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_final_nonfinite_direct_artifact_is_rejected_by_host_even_if_runner_says_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_finite_out_of_public_range_score_publishes_scorer_error (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_log_counts_have_fixed_aggregate_and_truncation_consistency (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_malformed_csv_and_resolution_loop_emit_one_safe_protocol_record (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_run_directory_relationship_uses_relative_descriptor_opens (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_runner_failure_is_safe_and_has_no_score (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_runtime_hash_guard_detects_snapshot_module_change_before_any_runner_call (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_success_requires_runner_hash_and_exact_integer_count (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_ancestor_symlink_and_negative_identity_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_code_and_root_identity_tamper_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_copied_private_selected_bytes_not_mutable_source (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_symlink_hardlink_fifo_and_size_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_symlink_loop_is_a_safe_staging_error (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_every_expected_identity_field_is_checked_not_self_attested (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_receipt_store.DevReceiptTest) ... ok
test_exact_schema_duplicate_keys_hidden_phase_and_bad_unicode_are_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_receipt_store.DevReceiptTest) ... ok
test_expected_independent_provenance_and_recomputed_score_construct_internal_receipt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_receipt_store.DevReceiptTest) ... ok
test_scalar_metric_and_artifact_bindings_rederived_from_opened_bytes (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_receipt_store.DevReceiptTest) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.139s

OK
```

### Targeted seven regressions

Command:

```text
/usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_malformed_csv_and_resolution_loop_emit_one_safe_protocol_record experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_finite_out_of_public_range_score_publishes_scorer_error experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_log_counts_have_fixed_aggregate_and_truncation_consistency experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_run_directory_relationship_uses_relative_descriptor_opens experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_descriptor_relationship_rejects_a_different_repo_inode experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest.test_symlink_loop_is_a_safe_staging_error experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest.test_dev_receipt_from_actual_fixed_inputs_no_native_commit_selfhash
```

Full output:

```text
test_malformed_csv_and_resolution_loop_emit_one_safe_protocol_record (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_finite_out_of_public_range_score_publishes_scorer_error (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_log_counts_have_fixed_aggregate_and_truncation_consistency (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_run_directory_relationship_uses_relative_descriptor_opens (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_descriptor_relationship_rejects_a_different_repo_inode (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok
test_symlink_loop_is_a_safe_staging_error (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_staging.SelectedStagingTest) ... ok
test_dev_receipt_from_actual_fixed_inputs_no_native_commit_selfhash (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry.EntryTest) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.082s

OK
```

### Independent before/after directory-identity fixture

The external fixture source is recorded here because its temporary path is not durable.

Fixture SHA-256: `3f74fa22b1863533b60b5feb2fb46e5e3281ef804bc7279f445d01213bbdfd09`

Fixture source:

```python
from unittest.mock import patch
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_run_entry import EntryTest
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.run_entry import EntryError, execute_entry

case=EntryTest(methodName="test_dev_receipt_from_actual_fixed_inputs_no_native_commit_selfhash")
case.setUp()
try:
    case.write_config()
    first=((1,1),(2,2),(3,3))
    changed=((1,1),(2,2),(4,4))
    with patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.run_entry._verify_native_cwd",side_effect=[first,changed]) as identity, patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.run_entry.run_fixed_solution") as runner:
        try:
            execute_entry(case.snapshot)
            rejected=False
        except EntryError:
            rejected=True
    print("identity_checks="+str(identity.call_count))
    print("before_after_mismatch_rejected="+str(rejected))
    print("runner_called="+str(runner.called))
    print("stage_exists="+str((case.output/(".inputs-"+case.config.get("run_id", "191407a0-84ce-47e6-afa4-298d034b8aa3"))).exists()))
finally:
    case.tearDown()
```

Exact command:

```text
PYTHONPATH=/Users/um-yunsang/argo-paper-orx /usr/bin/python3 -B /private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/hp-a2-v2-before-after-gp89g9sm/before_after_fixture.py
```

Full output:

```text
identity_checks=2
before_after_mismatch_rejected=True
runner_called=False
stage_exists=False
```

## Scope boundary

- `receipt_store.py` and its tests are byte-identical to v1. Expected native-fact independence remains the known bridge condition; this review does not claim that helper types prove it.
- No actual data or labels, OAuth, provider, ORX, Docker, native edits, commits, or nested agents were used.
- No hostile whole-host isolation claim is made.
- Pending production command/config, immutable commit/source-digest fan-in, and OAuth remain external conditions.
