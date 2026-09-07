# HousePrice P0 Option A2 phase driver independent review v2

## Verdict

**NOT ADMITTED.** The exact repaired source/test/report hashes match the root request. All four original counterexamples and the full 15-test Python 3.11 suite pass. R1, R3, and R4 are closed. R2 is substantially repaired through the root validator, but one active prompt remains outside the asserted frontend SourceTree membership check. This residual source-lineage defect blocks execution admission.

Reviewed exact bytes:

- `phase_driver.py` — `4ac115ee650ad7d556118c4d8cb186e323e58f504acf504849cd0d47b3aef4dc`
- `test_phase_driver.py` — `b38c23977907f731c2a1e28bc010bba3a27a5c02fb89c621e746674088b29096`
- `a2-phase-driver-report-v2.json` — `e1557697c1f2130d0d8110fb28b73f2615b6bda44951db29dc53f4921e691fe5`

## Original finding disposition

### A2PD-R1 — CLOSED

`_current_session` now receives the expected DirectoryIdentity, opens it with `O_DIRECTORY|O_NOFOLLOW`, checks held and named mode/UID/device/inode before and after, reads the UUID file relative to the held descriptor, and checks file identity/length/hash. The exact directory-replacement counterexample now returns no current binding and cannot be clean.

### A2PD-R2 — PARTIAL; residual blocker below

The driver statically calls the frozen `controller_deployment._revalidate_frontend_deployment` and binds its exact `c26c57...` module inside the namespace closure. The old incomplete three-asset deployment is rejected. Exact `dbe87f...` frontend, `c8c19...` process executor, `135a3e...` process core, runtime schema, bootstrap provenance, and most active frontend assets are now rechecked before admission. No Faux relaxation was added.

### A2PD-R3 — CLOSED

`_clean_process` now requires typed handle/resources/cleanup, passes canonical receipt JSON through the frozen Bridge terminal validator, checks exact fixed paths/environment keys/resource caps, exact-int zero, confirmed reaping, no alive/error residue, complete below-budget usage, and the rebound current session. The malformed/foreign receipt counterexample now returns false.

### A2PD-R4 — CLOSED

All three SourceTree roots now reject equality and ancestor/descendant overlap before admission. The original nested-root counterexample is rejected with an empty evidence directory.

## Residual finding

### A2PD2-R2A — BLOCKER — `system_prompt` is reopened but not bound to the frontend SourceTree

At `phase_driver.py` in the `frontend_asset_names` membership loop, the set includes `prime_closure_manifest`, `controller_main`, `frontend_closure_manifest`, `extension`, `binding`, `task_prompt`, and `autonomous_gate`, but omits `system_prompt`. The root controller-deployment validator reopens and validates the system prompt's FileBinding/content, but it does not establish membership in the separately asserted frontend SourceTree.

A bounded omission probe used the complete dependency seam, placed `system_prompt` outside `frontend_tree.root`, and recorded every asset passed to `_asset_binding_from_deployment`. The driver accepted the closure. The call list included all seven names above and never included `system_prompt`.

Impact: an active model instruction can come from bytes outside the source closure that the admission record claims for the frontend. This violates the contract statement that the frontend tree binds both prompts and prevents a complete source-lineage claim.

Required fix: add `system_prompt` to the frontend membership/reopen set and add a negative test that places only that prompt outside the frontend root. Keep `settings` in the separately bound profile, node as its executable identity, and Prime entry in installedPrime; do not broaden those exceptions or add Faux support.

## Scoped passes

- Exact repaired hashes and dependency hashes matched.
- Four repair counterexamples pass independently under `.venv-sab` Python 3.11 with `-B`.
- The full 15-test suite passes under the same interpreter.
- `run_controller` is mocked in all execute paths.
- Existing fence, source-preflight-before-admission, same-observer campaign guard, combined prior usage, late unknown, and recording-failure behavior remain intact.
- No production namespace copy was made. `controller_deployment.py` is only a declared post-review dependency.

## Dependency boundary

The rereview used exact local copies:

- `controller_deployment.py` — `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`; root reports 13 green tests, independent v2 review still pending.
- `bridge.py` — `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558`; root reports independent exact-zero pass.
- `controller_process.py` — `135a3e28291ea8e7db3b85cdd4fda05124113baaeb0d1a1335a905bc5bdd3f33`.
- `process_exec.py` — `c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840`.

These dependency reports are not relabeled as live combination evidence.

## Validation logs

Four repaired counterexamples:

```text
test_all_source_tree_roots_must_be_pairwise_nonoverlapping (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_all_source_tree_roots_must_be_pairwise_nonoverlapping) ... ok
test_incomplete_frontend_deployment_is_rejected_before_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_incomplete_frontend_deployment_is_rejected_before_admission) ... ok
test_malformed_or_foreign_process_receipt_is_never_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_malformed_or_foreign_process_receipt_is_never_clean) ... ok
test_replaced_session_directory_identity_never_returns_current_or_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_replaced_session_directory_identity_never_returns_current_or_clean) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.015s

OK
```

Full 15:

```text
test_all_source_tree_roots_must_be_pairwise_nonoverlapping (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_all_source_tree_roots_must_be_pairwise_nonoverlapping) ... ok
test_incomplete_frontend_deployment_is_rejected_before_admission (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_incomplete_frontend_deployment_is_rejected_before_admission) ... ok
test_malformed_or_foreign_process_receipt_is_never_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_malformed_or_foreign_process_receipt_is_never_clean) ... ok
test_replaced_session_directory_identity_never_returns_current_or_clean (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_driver.PhaseDriverRepairTests.test_replaced_session_directory_identity_never_returns_current_or_clean) ... ok
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
Ran 15 tests in 0.061s

OK
```

Residual system-prompt membership probe:

```json
{
  "accepted_with_system_prompt_outside_frontend_tree": true,
  "asset_binding_calls": [
    "autonomous_gate",
    "binding",
    "controller_main",
    "extension",
    "frontend_closure_manifest",
    "frontend_closure_manifest",
    "prime_closure_manifest",
    "task_prompt"
  ],
  "frontend_root": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-a2-phase-driver-rts9409a/frontend",
  "system_prompt_path": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-a2-phase-driver-rts9409a/outside-system-prompt.txt",
  "system_prompt_reopened_or_membership_checked": false
}
```

Probe source SHA-256: `b71a1864452eba06cb5e786ea26c211108e9b849c1f27f9ac201a9dca9d78a29`; full source is embedded in the JSON review.

## Scope

No source/test change, real child, real run_controller, core 20-suite, Prime/Faux, ORX, Docker, provider, auth, data, scoring, or P0 occurred. No npm or commit was used.
