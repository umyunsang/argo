# HousePrice P0 A2 combination driver independent review v2

## Verdict

**SCOPED PASS for source/mock orchestration; not whole-case or P0 admission.** Exact repaired hashes match. CDRV-01, CDRV-02, and CDRV-03 are closed. All 16 kernel-Python 3.11 mock tests pass, and the same three independent controls now fail closed.

Reviewed exact bytes:

- `combination_driver.py` — `def87800b6e1dab337cec8bd8496a892762fe7ceaa9569c2a19d8773bc9f0413`
- `test_combination_driver.py` — `df2f6b4a465268192c423f6d668db33be4bf85ff5913e8b2a8452015e8a1d87e`

## Finding disposition

### CDRV-01 — CLOSED

`CombinationCaseConfig` v2 requires `CaseProtectedRoots(raw, auth, profile, controller, public)`. The driver serializes all five DirectoryIdentity records into admission/final source bindings. It opens/rechecks type/owner/device/inode without reading contents and rejects case-root equality or either-direction ancestry before source work, after source verification, and around final publication. The fixed pre-import v2 contract owns the matching stdlib-only JSON validation.

The same case-under-profile control now returns `NOT_STARTED` and makes zero mocked process calls.

### CDRV-02 — CLOSED

`run_case` latches finite monotonic seconds and nanoseconds at entry before input/source validation. Regressed/nonfinite clocks reject. It checks the 160-second ceiling after source verification and again before the controller, and the 180-second ceiling after controller, through cleanup/revalidation, and before verified return. The final elapsed now covers driver input/source/preparation/controller/acceptance/cleanup work; external preflight duration remains separately recorded.

The same simulated 170-second source-verification control now returns `NOT_STARTED` and makes zero mocked process calls.

### CDRV-03 — CLOSED

After the first PASS assessment and typed fixture close, the driver:

- captures and reopens the original evidence/session/artifact/frontend/control/fixture directories;
- reopens normal/synthetic configs, process receipt, gate config, bridge config, Faux entry, metadata, and current session with original hash/size/mtime;
- fsyncs and rechecks the original metadata file and artifact parent;
- re-verifies source/seed/Prime and repeats the pure acceptor;
- requires an identical typed PASS/usage/session/gate result;
- reopens references again after final publication before returning verified.

Any missing/changed reference downgrades before a VERIFIED return. The same metadata-deletion control now returns `NOT_ADMITTED`. Its failure receipt may retain the historical metadata binding and first assessment, but its status/reason no longer claim verification.

## Scoped passes

- Required case policy round-trips through strict config v2; missing/replaced/overlapping roots reject without content reads.
- Existing case and source mismatch remain no-effect paths.
- O_EXCL case admission still precedes fixture/process work.
- Exactly one mocked process gets the same observer guard and 20-second Event; normal config remains unexecuted.
- Typed fixture close/CFX partial lineage, assessment rejection, evidence caps, short-write loops, partial retention, and no retry remain intact.
- Metadata fsync failure, cleanup mutation, changed references, or second assessment mismatch cannot return verified.

## Validation

Exact 16-test command:

```text
test_admission_and_final_receipts_bind_policy_without_reading_contents (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_admission_and_final_receipts_bind_policy_without_reading_contents) ... ok
test_bad_source_fails_before_case_creation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_bad_source_fails_before_case_creation) ... ok
test_case_config_v2_rejects_missing_policy_and_roundtrips_exact_roles (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_case_config_v2_rejects_missing_policy_and_roundtrips_exact_roles) ... ok
test_case_policy_is_required_and_replaced_root_blocks_before_creation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_case_policy_is_required_and_replaced_root_blocks_before_creation) ... ok
test_case_root_inside_protected_profile_starts_nothing (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_case_root_inside_protected_profile_starts_nothing) ... ok
test_cleanup_mutation_or_second_assessment_failure_prevents_verified (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_cleanup_mutation_or_second_assessment_failure_prevents_verified) ... ok
test_evidence_writer_rejects_caps_completes_short_writes_and_retains_partial (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_evidence_writer_rejects_caps_completes_short_writes_and_retains_partial) ... ok
test_existing_case_cannot_start_or_write (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_existing_case_cannot_start_or_write) ... ok
test_fixture_error_preserves_admission_without_process_or_exception_payload (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_fixture_error_preserves_admission_without_process_or_exception_payload) ... ok
test_metadata_deleted_after_assessment_cannot_be_verified (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_metadata_deleted_after_assessment_cannot_be_verified) ... ok
test_metadata_parent_fsync_failure_never_publishes_verified (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_metadata_parent_fsync_failure_never_publishes_verified) ... ok
test_one_synthetic_process_uses_guard_and_typed_cleanup_before_receipt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_one_synthetic_process_uses_guard_and_typed_cleanup_before_receipt) ... ok
test_partially_created_fixture_with_unconfirmed_close_is_not_generic_failure (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_partially_created_fixture_with_unconfirmed_close_is_not_generic_failure) ... ok
test_rejected_assessment_retains_one_attempt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_rejected_assessment_retains_one_attempt) ... ok
test_source_validation_time_counts_before_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_source_validation_time_counts_before_admission) ... ok
test_unknown_cleanup_or_failed_assessment_never_passes (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_unknown_cleanup_or_failed_assessment_never_passes) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.139s

OK
```

Same three independent controls:

```json
{
  "case_root_inside_profile": {
    "accepted": false,
    "case_root": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/hp-case-driver-mock-jcjei907/user-profile/case",
    "process_calls": 0,
    "status": "NOT_STARTED"
  },
  "metadata_missing_at_verified_return": {
    "binding_present": true,
    "file_exists": false,
    "process_calls": 1,
    "status": "NOT_ADMITTED"
  },
  "source_verification_elapsed_excluded": {
    "accepted": false,
    "process_calls": 0,
    "simulated_pre_source_seconds": 170,
    "status": "NOT_STARTED"
  }
}
```

Probe source SHA-256: `15b5c39085a861f9fa282c11a282c931029563f50c69935a7289480dcdcabd75`; full source is embedded in the JSON review.

## Dependency boundary

The matching pre-import v2 config reader is separate and newly delivered; it is not imported by the driver. Acceptance source anchor `4c9b...` and test anchor `47ec...` remain under their own independent review. Fixture/Faux/preflight/capsule sources and real native gate/session ordering remain separate dependencies. This scoped pass cannot freeze the whole case until those exact reviews and the combined closure pass.

## Scope

All fixture/environment/main/CLI/controller/Timer/Bridge/Prime/Faux effects were mocked. No actual fixture, `_prepare_environment`, CLI, `run_controller`, Timer, Git, socket, Docker, provider, auth, data, ORX, P0, old core suite, npm, commit, or nested worker.
