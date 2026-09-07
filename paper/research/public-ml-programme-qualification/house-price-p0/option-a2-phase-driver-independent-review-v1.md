# HousePrice P0 Option A2 phase driver independent review v1

## Verdict

**NOT ADMITTED for execution or P0.** The exact source/test/report hashes match the root request and the 11 isolated Python 3.11 mock tests pass. Two blocker defects, one high defect, and one medium closure defect remain. No source was edited.

Reviewed bytes:

- `phase_driver.py` — `57ae9cca3e895ddc7fdb2cd286e408640f2c4af87c5b126f1123494ae0623d83`
- `test_phase_driver.py` — `4d42ffa3d2ccc9d4abfa531591f515fcae26403279068640b7611eb68060cca0`
- `a2-phase-driver-report-v1.json` — `0dcf348ac31e970dbc69db633d05d1828c20d42287d736789839aafe25824932`

## Findings

### A2PD-R1 — BLOCKER — current session loses its bound directory identity after observation

`_current_session` at `phase_driver.py:576-600` rebuilds the path from `process_config.session_dir`, calls `path.lstat()`, and then `_gate_read(path, ...)`. It never reopens the configured session directory by the expected device/inode from `process_config.session_dir_identity` or `gate.session_directory`. `_clean_process` at lines 603-625 compares only the path string.

A bounded mocked omission probe replaced the whole session directory after the final observer returned, copied the exact same bounded session bytes under the same UUID filename, and preserved the path string. The configured inode was `165682011`, the replacement inode was `165682030`, yet the driver returned `PROCESS_RECORDED`, a non-null current-session binding, and `clean_process=true`.

Impact: root can call phase completion on evidence that no longer belongs to the exact observed native session-directory identity. This violates the current-native-identity binding and clean-process precondition.

Required fix: pass the expected `DirectoryIdentity` into `_current_session`; open the directory with `O_DIRECTORY|O_NOFOLLOW`, verify held and named device/inode/mode before and after opening the UUID file relative to that descriptor, and make clean false on any root/file identity change.

### A2PD-R2 — BLOCKER — frontend source closure checks only three assets and one runtime field

`_verify_source_closures` verifies aggregate trees at lines 398-401, but it only reads `controller_main`, `node_executable`, and `prime_entry` from the deployment at lines 419-465. It does not require the controller-main deployment's exact asset set or bind `extension`, extension `binding`, prompts, autonomous gate, and closure manifests to the verified frontend/Prime trees. It also checks only `runtime.model` at lines 477-489, not phase, mode, print, offline, fresh-session, tools, or exact production limits.

A bounded omission probe supplied a deployment with only the three inspected assets and `runtime={model}`. With filesystem readers patched only to isolate this omission, `_verify_source_closures` accepted it. The real controller frontend would reject some omissions only after the admission fence and process call; arbitrary sealed external extension/prompt paths can also escape the asserted frontend tree.

Impact: the driver can consume its one-shot admission and enter `run_controller` before proving the complete executable frontend closure required by the contract. Aggregate tree verification does not prove that deployment references point into that tree.

Required fix: require the exact controller deployment schema and all exact asset/runtime/environment/limit keys before admission. For every active source asset, require the expected root membership and reopen its FileSeal bytes. Keep the exact production frontend anchor `dbe87f...`; do not add Faux or test-only production relaxation.

### A2PD-R3 — HIGH — `clean_process` does not validate the returned process receipt

`_clean_process` at lines 603-625 checks status, terminal reason, exact-int return code, and only `handle.session_dir`. It does not require clean `cleanup`/`resources`, root reaping, tracked-process cleanup, observer/census error absence, or exact handle process-exec/frontend/deployment/environment paths.

The test fixture's successful receipt has `resources=None` and `cleanup=None`. A bounded probe also replaced the handle's frontend and process-exec paths with foreign paths. `_clean_process` still returned true.

Impact: `clean_process` is not the advertised observed-only terminal predicate. Although the later phase-completion reader can reject a malformed persisted receipt, the driver itself can incorrectly authorize that next root step.

Required fix: validate the returned `ControllerRunReceipt` against the input `RunControllerConfig` before setting clean. Reuse the already reviewed terminal receipt validator where possible, then cross-check every fixed handle/resource path and cleanup predicate.

### A2PD-R4 — MEDIUM — source-tree roots may overlap

`_validate_config_shape` at lines 192-198 requires only three unequal root strings. It does not reject an ancestor relationship. A bounded pure probe used a frontend root nested under the namespace root; shape validation accepted it and created no evidence files.

Impact: independently named installed/namespace/frontend closure claims can collapse onto overlapping bytes, weakening the intended separation and admission provenance.

Required fix: reject equality and either-direction ancestry across every pair of source roots before any admission.

## Scoped passes

- Exact hashes matched before review.
- The 11 existing tests passed under `/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B`.
- Existing admission or a partial admission blocks another attempt.
- Invalid/gate-session mismatch and stale-source paths create no admission and do not call the mocked controller.
- The same observer supplies a callable campaign guard and final observation.
- Prior usage is retained; startup waiting, budget stop, unknown, and late unknown do not become clean success.
- Recording failure retains the admission and does not claim clean success.
- Fixed constants bind current controller process `135a3e...`, process executor `c8c19b...`, and production frontend `dbe87f...`. No Faux relaxation exists.
- `run_controller` was mocked in every review execution.

## Validation

Existing suite:

```text
test_budget_guard_uses_prior_sessions_without_reset_and_clean_is_false (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_budget_guard_uses_prior_sessions_without_reset_and_clean_is_false) ... ok
test_existing_admission_fence_denies_second_attempt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_existing_admission_fence_denies_second_attempt) ... ok
test_gate_config_pure_reader_binds_current_observer_inputs (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_gate_config_pure_reader_binds_current_observer_inputs) ... ok
test_guard_unknown_is_passed_through_and_never_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_guard_unknown_is_passed_through_and_never_clean) ... ok
test_invalid_input_and_orphan_receipt_create_no_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_invalid_input_and_orphan_receipt_create_no_admission) ... ok
test_late_unknown_prevents_clean_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_late_unknown_prevents_clean_success) ... ok
test_process_and_gate_session_mismatch_fails_before_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_process_and_gate_session_mismatch_fails_before_admission) ... ok
test_recording_failure_keeps_admission_and_never_clean_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_recording_failure_keeps_admission_and_never_clean_success) ... ok
test_stale_source_tree_fails_before_admission_or_process (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_stale_source_tree_fails_before_admission_or_process) ... ok
test_startup_guard_is_callable_and_same_observer_finalizes_clean_receipts (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_startup_guard_is_callable_and_same_observer_finalizes_clean_receipts) ... ok
test_wrong_session_path_or_identity_never_becomes_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverTests.test_wrong_session_path_or_identity_never_becomes_clean) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.045s

OK
```

Omission probe output:

```json
{
  "clean_process_malformed_receipt": {
    "accepted_clean": true,
    "cleanup_is_none": true,
    "foreign_frontend": true,
    "foreign_process_exec": true,
    "resources_is_none": true
  },
  "frontend_closure_omission": {
    "accepted": true,
    "asset_keys": [
      "controller_main",
      "node_executable",
      "prime_entry"
    ],
    "missing_security_fields": [
      "extension",
      "binding",
      "system_prompt",
      "task_prompt",
      "autonomous_gate",
      "phase",
      "mode",
      "print",
      "offline",
      "fresh_session",
      "tools"
    ],
    "runtime_keys": [
      "model"
    ]
  },
  "overlapping_source_roots": {
    "accepted": true,
    "evidence_files_after": [],
    "namespace_is_frontend_ancestor": true
  },
  "session_directory_replaced_after_observation": {
    "clean_process": true,
    "configured_inode": 165682011,
    "current_session_returned": true,
    "disposition": "PROCESS_RECORDED",
    "new_inode": 165682030,
    "old_inode": 165682011
  }
}
```

Probe source SHA-256: `b1489931a7cce67c11ebecf62941d7d1434e0a1638baf0290ac5dce498c5e4fb`. The full source is embedded in the JSON review for reproducibility.

## Scope boundary

No actual child process, old controller/20-test suite, Prime/Faux frontend, ORX, Docker, provider, auth, data, scoring, or P0 was invoked. The initial direct `/tmp` script collection failure due normal module search path was excluded as environmental and not treated as a behavioral red. This review changes only its two review artifacts.
