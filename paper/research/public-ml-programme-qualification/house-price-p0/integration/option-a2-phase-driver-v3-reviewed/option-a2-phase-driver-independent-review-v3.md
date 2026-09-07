# HousePrice P0 Option A2 phase driver independent review v3

## Verdict

**SCOPED PASS for the source/mock phase-driver contract; not live execution or P0 admission.** The exact repaired hashes match. The one-line R2A repair closes the final source-membership finding. R1, R3, and R4 remain closed. The 16-test Python 3.11 suite and the same independent outside-system-prompt probe pass.

Reviewed exact bytes:

- `phase_driver.py` — `dc2bf22e7d1a33c52660200b8e25ab90c98cabce91f271befa781e0280cbec77`
- `test_phase_driver.py` — `d24120fd2b611726a3c81d711467d51c389d09efa6757d3845dfb0b1e1eebfaf`

## Finding disposition

- **A2PD-R1 CLOSED:** held/named session-directory identity and relative file identity remain checked before and after the current-session read.
- **A2PD-R2 CLOSED in source/mock scope:** the exact root deployment validator remains mandatory; active frontend assets are reopened and root-checked. `system_prompt` is now included in the frontend membership set. The old incomplete-deployment counterexample and the same outside-prompt counterexample both reject before admission/process.
- **A2PD-R3 CLOSED:** clean process still requires typed, canonically validated receipt/resources/cleanup; exact paths/caps; exact-int zero; clean process-tree evidence; and bound current usage/session.
- **A2PD-R4 CLOSED:** all three source roots remain pairwise non-overlapping.
- **A2PD2-R2A CLOSED:** the source delta from v2 is exactly one membership-set item, `system_prompt`. The independent probe now reports `accepted_with_system_prompt_outside_frontend_tree=false` and confirms that `system_prompt` reached the byte/membership helper.

## Dependency closure

This review observed exact local dependency copies:

- `controller_deployment.py` — `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`; root reports its 13-test independent scoped pass.
- `bridge.py` — `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558`; root reports the exact-zero independent pass.
- `controller_process.py` — `135a3e28291ea8e7db3b85cdd4fda05124113baaeb0d1a1335a905bc5bdd3f33`.
- `process_exec.py` — `c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840`.

The dependency is declared only. No production namespace copy or live combined execution occurred.

## Validation

Exact 16-test command:

```text
test_all_source_tree_roots_must_be_pairwise_nonoverlapping (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_all_source_tree_roots_must_be_pairwise_nonoverlapping) ... ok
test_incomplete_frontend_deployment_is_rejected_before_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_incomplete_frontend_deployment_is_rejected_before_admission) ... ok
test_malformed_or_foreign_process_receipt_is_never_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_malformed_or_foreign_process_receipt_is_never_clean) ... ok
test_replaced_session_directory_identity_never_returns_current_or_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_replaced_session_directory_identity_never_returns_current_or_clean) ... ok
test_system_prompt_must_belong_to_the_frontend_tree (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_system_prompt_must_belong_to_the_frontend_tree) ... ok
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
Ran 16 tests in 0.064s

OK
```

Same independent outside-prompt probe:

```json
{
  "accepted_with_system_prompt_outside_frontend_tree": false,
  "asset_binding_calls": [
    "autonomous_gate",
    "extension",
    "frontend_closure_manifest",
    "prime_closure_manifest",
    "system_prompt",
    "task_prompt"
  ],
  "frontend_root": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-a2-phase-driver-14y_0l1w/frontend",
  "system_prompt_path": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-a2-phase-driver-14y_0l1w/outside-system-prompt.txt",
  "system_prompt_reopened_or_membership_checked": true
}
```

Probe source SHA-256: `b71a1864452eba06cb5e786ea26c211108e9b849c1f27f9ac201a9dca9d78a29`. Full source is embedded in the JSON review.

## Remaining external gates

A source/mock pass does not establish deployment materialization, namespace installation, real controller/observer combination, process cleanup on this instance, Prime/provider/auth readiness, ORX/Docker/task/data compatibility, or P0 performance. Root must freeze the exact combined closure and separately authorize any live start.

## Scope

No source/test changes, real `run_controller`, child process, old core 20-suite, Prime/Faux, ORX, Docker, provider, auth, data, scoring, P0, npm, or commit.
