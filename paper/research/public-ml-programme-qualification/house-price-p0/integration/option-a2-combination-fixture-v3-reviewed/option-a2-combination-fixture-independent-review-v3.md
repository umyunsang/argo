# HousePrice Option A2 combination-fixture independent review v3

## Decision

**SCOPED PASS: CBR03-001 is resolved. CFX-001 remains closed.**

The close path now requires finite clock samples at start, after bounded joins, and immediately before confirmation. A cleanup that completes at fake time 2.25 is a cached `CLOSE_TIMEOUT`, not confirmation. Externally supplied confirmed results above two seconds are normalized to unconfirmed.

No new finding was identified in this deadline-only repair. All 17 synthetic mock tests pass. No real thread, socket, NativeHarness, Bridge, Git, fake ORX, provider/auth, data, Docker, controller, or P0 ran.

## Frozen inputs

Review request: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-fixture-deadline-review-request-v3.json` — `aa007612a2aa07f6d03c6a2f046d1e9a185b10337004ef77b58256b5a5a26da0` (1589 bytes).

| File | Bytes | SHA-256 | Request match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/combination_fixture.py` | 32505 | `a1adde7fdea63cdac8458f5e64c7aa7008540abb0068128902e838b264152f6a` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_combination_fixture.py` | 31235 | `1156e5112a00248dcfb1dde4139b32a2e9b385b9029cc0bc72e3a36b4f0028e0` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-combination-fixture-report-v3.json` | 6223 | `7947e2c46164ae2ee7454e651ec26135297fc5a9c77df22f51e19cb3cbeb14a5` | yes |

All three files were read in full. Their archived copies are byte-identical.

Repair contract: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-fixture-close-deadline-repair-v1.json` — `235499482600ea8de1ee1a97333aefbc6732945e6e70ff3a7a54ec46e63b8e22` (1559 bytes).

Previous reviews remain unchanged:

- v1 Markdown `f3de4ad7516503f95b1db5768a0796071249bbd3e576049e2dce15b9ff3e3b40`
- v1 JSON `52e9277b2e4b065521172bf5a304644249a6c8fb0a707448a84919be0774f21d`
- v2 Markdown `f8562f83cd5bdad4fabb63c6cc7230827cd14ca9485cd4eeddc4e8882742923e`
- v2 JSON `3e22fd36c294ef9dbde2abad9f7ee6157475749405fad7d2e9a11190919e5328`

## CBR03-001 closure

Locations: `combination_fixture.py:121-148,179-294,312-326`; `test_combination_fixture.py:541-610`.

The repair adds:

1. `_clock_now`, which accepts only finite non-boolean numeric monotonic values and converts them to float.
2. A required finite start sample. Failure returns `CLOSE_IDENTITY_UNKNOWN` without creating a cleanup thread.
3. A deadline sample immediately after cleanup-thread join. `now > deadline` sets timeout even if the thread has stopped and shutdown completed.
4. The same deadline sample after a serving-thread join.
5. A final finite monotonic sample immediately before confirmation. Confirmation requires finite nonnegative elapsed time no greater than 2.0 and a nonexpired deadline.
6. `_close_harness` normalization of any externally supplied `confirmed=true` result with `elapsed_seconds > 2.0` to `CLOSE_IDENTITY_UNKNOWN`.

The exact prior 2.25 control now asserts:

- `confirmed=false`;
- `timed_out=true`;
- `error=CLOSE_TIMEOUT`;
- `elapsed_seconds=2.25`;
- identical cached repeat;
- exactly one cleanup thread and one shutdown call.

The existing 2.0 serving-thread deadline remains `CLOSE_TIMEOUT`. Initial nonfinite time starts no cleanup. A nonfinite final sample after completed cleanup remains unconfirmed `CLOSE_IDENTITY_UNKNOWN`. These satisfy the frozen finite-clock and cache requirements.

## CFX-001 preservation

The v2-to-v3 source diff touches only clock/deadline validation and external close-result normalization. The fixed second solution/intent/parent checks and final nofollow source-byte reads are unchanged. Their two regressions remain green in the 17-test suite. CFX-001 stays closed in its prior scope.

## Archive evidence

All five files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-combination-fixture-v3-deadline` were read in full:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `a2-combination-fixture-report-v3.json` | 6223 | `7947e2c46164ae2ee7454e651ec26135297fc5a9c77df22f51e19cb3cbeb14a5` |
| `combination_fixture.py.diff` | 4576 | `b993347d167a3b83b90af2b058edcff7fae2442ad75e0b40dbf6ffb7f681faa6` |
| `combination_fixture.py.snapshot` | 32505 | `a1adde7fdea63cdac8458f5e64c7aa7008540abb0068128902e838b264152f6a` |
| `test_combination_fixture.py.diff` | 3980 | `c658968627090db6ebd74954bb49124065e329f0e18b3634fd98c487c6efadb1` |
| `test_combination_fixture.py.snapshot` | 31235 | `1156e5112a00248dcfb1dde4139b32a2e9b385b9029cc0bc72e3a36b4f0028e0` |

- The report records the genuine old-source 2.25 RED and the 17-test GREEN.
- Both source/test diffs are limited to deadline-clock code and three focused tests.
- Current source, test, and report exactly match their archive snapshots.

## Exact independent execution

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture
test_action_error_closes_once_without_deleting_partial_evidence (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_action_error_closes_once_without_deleting_partial_evidence) ... ok
test_config_collision_closes_once_and_preserves_collision (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_config_collision_closes_once_and_preserves_collision) ... ok
test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base) ... ok
test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor) ... ok
test_external_confirmed_result_over_deadline_is_normalized_unconfirmed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_external_confirmed_result_over_deadline_is_normalized_unconfirmed) ... ok
test_final_source_mismatch_rejects_before_tree_return (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_final_source_mismatch_rejects_before_tree_return) ... ok
test_owned_close_alive_serve_thread_uses_remaining_deadline_and_times_out (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_alive_serve_thread_uses_remaining_deadline_and_times_out) ... ok
test_owned_close_exception_and_open_socket_never_infer_confirmation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_exception_and_open_socket_never_infer_confirmation) ... ok
test_owned_close_identity_mismatch_is_unconfirmed_without_cleanup_thread (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_identity_mismatch_is_unconfirmed_without_cleanup_thread) ... ok
test_owned_close_late_completed_join_is_cached_timeout_not_confirmation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_late_completed_join_is_cached_timeout_not_confirmation) ... ok
test_owned_close_nonfinite_clock_never_manufactures_confirmation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_nonfinite_clock_never_manufactures_confirmation) ... ok
test_owned_close_success_is_confirmed_bounded_and_cached (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_success_is_confirmed_bounded_and_cached) ... ok
test_owned_close_timeout_is_unconfirmed_and_never_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_timeout_is_unconfirmed_and_never_retried) ... ok
test_owned_handler_matches_frozen_route_and_rejects_credentials_without_socket (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_handler_matches_frozen_route_and_rejects_credentials_without_socket) ... ok
test_self_consistent_wrong_second_candidate_and_parent_reject_before_second_mark (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_self_consistent_wrong_second_candidate_and_parent_reject_before_second_mark) ... ok
test_success_returns_exact_owned_snapshot_and_idempotent_close (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_success_returns_exact_owned_snapshot_and_idempotent_close) ... ok
test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.055s

OK
EXIT_CODE=0
```

Result: 17/17 Python 3.11 synthetic tests passed. The same 2.25 case, finite-clock failures, external late-confirmed result, and cached repeat are included directly in the suite. No separate probe was needed or run.

## Preserved controls and limits

- Confirmed close still requires completed shutdown, stopped owned cleanup and serving threads, exact closed owned socket, no error, and no timeout.
- Identity mismatch, shutdown exception, open socket, live threads, invalid result fields, or nonfinite/negative elapsed time remain unconfirmed.
- Sequential repeat returns the identical first result and starts no second cleanup thread. Late completion cannot upgrade it.
- Prepare failure retains the base and carries only typed close result/base identity.
- CFX fixed second-candidate/intent/parent/final-source authority remains green.
- Close scope covers only retained owned server/socket/serve/cleanup handles. It is not whole-host cleanup proof.
- Concurrent close calls were not tested; accepted caller ownership is sequential.
- FEF-001, capsule/preflight/acceptance/driver combination, OAuth/provider/data/ORX/Docker, immutable production receipts, and actual P0 remain separate gates. Live P0 remains held.
