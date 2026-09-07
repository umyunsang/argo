# HousePrice Option A2 combination-fixture independent review v2

## Decision

**CFX-001 is resolved. CBR-03 still needs one P1 deadline repair.**

The fixed second solution/intent hashes are now independent authority, the run and binding must match them before the second `mark_done`, and final source bytes are reopened against the original directory identity before tree capture. However, close can still return `confirmed=true` after the total two-second deadline has expired if a timed join returns late with the cleanup thread already stopped.

The supplied 14 mock tests pass. One additional fake-clock/fake-thread probe reproduces the deadline error. No real thread, server, socket, NativeHarness, Bridge, Git, fake ORX, process, provider/auth, Docker, data, or P0 ran.

## Frozen inputs

| File | Bytes | SHA-256 | Root hash match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/combination_fixture.py` | 30848 | `5a1ea34f0a291ec0344fba1c130e56b2c2883c8f52eafa49ff812b503dc84306` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_combination_fixture.py` | 27737 | `88e3439145fd50592a5e02d4afdef9d5042641d244b587c34fb8924b06e00d25` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-combination-fixture-report-v2.json` | 9295 | `8a868d25c86b909b459485565bde4beec73ce27728fa2f622a442103f8313264` | yes |

All three were read in full. Their archived v2 copies are byte-identical.

Contracts:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-combination-fixture-repair-v2.json` — `7e215ca78e790d8b3a50b46f7a2461c4b37ffe70dee10be5ba4cfb84c3b13d0b` (2148 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-fixture-close-contract-v1.json` — `9ea70be0563bfc69768d87f3629b5d17d3bab2cedb8fd2359c8b6fe2158e7dcb` (3710 bytes)

The v1 independent review remains unchanged at `f3de4ad7516503f95b1db5768a0796071249bbd3e576049e2dce15b9ff3e3b40` and `52e9277b2e4b065521172bf5a304644249a6c8fb0a707448a84919be0774f21d`.

## CFX-001 closure — PASS

Locations: `combination_fixture.py:342-378,517-543,617-671`.

The repair now:

1. hashes only fixed `SECOND_SOLUTION` bytes;
2. builds canonical intent bytes with the first native run UUID as parent and hashes those bytes;
3. requires the second run response to match both hashes before binding/observation;
4. requires the matched binding to match both hashes before the second `mark_done`;
5. seeds final expected results from the fixed hash, not the returned hash;
6. reopens final `solution.py` and `intent.json` through the original `DirectoryIdentity`, with nofollow, single-link, size, pre/post identity, named entry, and root identity checks;
7. compares exact bytes before capturing the three trees.

The two new source regressions are well placed:

- a mutually self-consistent wrong candidate and wrong parent rejects before the second mark, closes once, and retains the base;
- a late final source-byte mutation after the correct second mark rejects before tree return, closes once, and retains the base.

The v1 independent counterexample is closed.

## Finding

### CBR03-001 — P1 — a late timed join can confirm cleanup after the deadline

Locations: `combination_fixture.py:181-258`; `test_combination_fixture.py:498-545`.

After `cleanup_thread.join(_remaining(deadline))`, the implementation defines timeout only as `not cleanup_stopped`. It does not sample whether `time.monotonic()` has crossed `deadline`. The same applies after the serving-thread join. Python timed joins may return slightly after their timeout. If the thread finishes during that overshoot, `is_alive()` is false, all state/socket checks pass, and the function returns confirmed even though elapsed time exceeds two seconds.

The independent probe used only the existing fake clock/server/serve-thread plus a fake cleanup thread. Its `join(2.0)` completed cleanup at simulated time 2.25. Actual result:

```text
confirmed=True
timed_out=False
error=None
elapsed_seconds=2.25
shutdown_completed=True
threads_socket=(True, True, True)
```

This violates the contract's one total 2.0-second deadline and its rule that confirmation requires no expired deadline. A future case receipt could derive `cleanup_confirmed=true` from a late result.

Required repair:

1. After each timed join, sample the monotonic clock and set `timed_out=true` if the current time is greater than the shared deadline, even when `is_alive()` is already false.
2. Before returning confirmed, recheck that the deadline has not expired. A clock read failure/nonfinite value must not confirm.
3. Optionally make `_close_harness` reject any externally returned `confirmed=true` result whose elapsed time exceeds 2.0 seconds.
4. Add a fake-clock regression where cleanup completes after the join timeout and all threads/socket appear stopped. Require cached `CLOSE_TIMEOUT`, `confirmed=false`, and no retry.

## Passing CBR-03 controls

Subject to CBR03-001:

- `FixtureCloseResult` has the exact frozen typed fields. `_close_harness` rejects malformed types, illegal errors, inconsistent timeout, nonfinite/negative elapsed time, and inferred confirmation.
- Owned server and retained serving thread identity must match before cleanup; mismatch returns cached `CLOSE_IDENTITY_UNKNOWN` without starting cleanup.
- First close starts one daemon cleanup thread that calls only `shutdown` then `server_close`. It joins only owned cleanup/serve threads with remaining-time arguments.
- Shutdown exception, open socket, live serving thread at the sampled boundary, and cleanup still alive return typed unconfirmed results.
- Socket closure is based on exact integer `fileno() == -1`; no thread enumeration, kill, port rebind, or absence-based inference occurs.
- Sequential repeated close returns the identical cached result and never retries. Late completion cannot upgrade a cached timeout.
- Prepare failures after owned server creation attach the typed close result and created-base identity; before server creation the close result remains null. Partial base is retained.
- The owned HTTP handler keeps the one GET route, credential-header rejection, bounded response headers, and silent logging shape under mock-only parity tests.

## Evidence archive

All four files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-combination-fixture-v2-repaired` were read in full:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `a2-combination-fixture-report-v2.json` | 9295 | `8a868d25c86b909b459485565bde4beec73ce27728fa2f622a442103f8313264` |
| `combination_fixture-v1-v2.diff` | 20688 | `825406f01feff231145ad48bf9513ef7597049562c1cc3fac829c446849e54a4` |
| `combination_fixture.py.snapshot` | 30848 | `5a1ea34f0a291ec0344fba1c130e56b2c2883c8f52eafa49ff812b503dc84306` |
| `test_combination_fixture.py.snapshot` | 27737 | `88e3439145fd50592a5e02d4afdef9d5042641d244b587c34fb8924b06e00d25` |

The producer report honestly states 14 mocks and no real fixture/thread/socket. It records direct CFX-001 REDs and CBR-03 skeleton REDs, then the final green. The stored diff and source/test/report snapshots match the reviewed bytes. It does not contain a late-completion-after-deadline regression.

Dependencies still match:

| Dependency | SHA-256 | Match |
|---|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py` | `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/grading.py` | `bf8b2deb3f4113c4b3f734928642a37fd84410546bc0c22725e8f495d6ccc0be` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/source_closure.py` | `e4b0b8732d48d2ecbcd57b6d9e01dbf88200ab5e57bf12426d28d22017ae4466` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/staging.py` | `9813081081af6b128a1c91eb06c4ba07fa6c260eee8984c708c3094e3a635800` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_bridge.py` | `5a45ef18dd0486a5b5eb9dccfe1090c1258a3b42fbb2768a63b749bd0ef424c2` | yes |

## Exact executions

### Fourteen supplied mocks

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture
test_action_error_closes_once_without_deleting_partial_evidence (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_action_error_closes_once_without_deleting_partial_evidence) ... ok
test_config_collision_closes_once_and_preserves_collision (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_config_collision_closes_once_and_preserves_collision) ... ok
test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base) ... ok
test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor) ... ok
test_final_source_mismatch_rejects_before_tree_return (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_final_source_mismatch_rejects_before_tree_return) ... ok
test_owned_close_alive_serve_thread_uses_remaining_deadline_and_times_out (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_alive_serve_thread_uses_remaining_deadline_and_times_out) ... ok
test_owned_close_exception_and_open_socket_never_infer_confirmation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_exception_and_open_socket_never_infer_confirmation) ... ok
test_owned_close_identity_mismatch_is_unconfirmed_without_cleanup_thread (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_identity_mismatch_is_unconfirmed_without_cleanup_thread) ... ok
test_owned_close_success_is_confirmed_bounded_and_cached (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_success_is_confirmed_bounded_and_cached) ... ok
test_owned_close_timeout_is_unconfirmed_and_never_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_close_timeout_is_unconfirmed_and_never_retried) ... ok
test_owned_handler_matches_frozen_route_and_rejects_credentials_without_socket (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_owned_handler_matches_frozen_route_and_rejects_credentials_without_socket) ... ok
test_self_consistent_wrong_second_candidate_and_parent_reject_before_second_mark (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_self_consistent_wrong_second_candidate_and_parent_reject_before_second_mark) ... ok
test_success_returns_exact_owned_snapshot_and_idempotent_close (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_success_returns_exact_owned_snapshot_and_idempotent_close) ... ok
test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.054s

OK
EXIT_CODE=0
```

### Late-deadline probe

Fixture: `/tmp/hp-a2-fixture-v2-review-_k09hh1q/late_deadline_probe.py` — `ed14d3de8dd2227cc1fa779c00d80c1210f496da3e2d0b998e122accbab619da` (1424 bytes).

```text
$ PYTHONPATH=/Users/um-yunsang/argo-paper-orx /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B /tmp/hp-a2-fixture-v2-review-_k09hh1q/late_deadline_probe.py
confirmed=True
timed_out=False
error=None
elapsed_seconds=2.25
shutdown_completed=True
threads_socket=(True, True, True)
EXIT_CODE=0
```

The probe patched cleanup Thread and monotonic time and used only fake server/socket/thread objects. It started no real thread or socket.

## External conditions and nonclaims

1. CFX-001 is locally closed only for this test fixture. Real Bridge/test-harness/member identities remain root authority.
2. Close covers only the exact owned server/socket/serving/cleanup threads. It is not whole-host or descendant cleanup proof.
3. Concurrent calls to `close()` were not evaluated; the accepted caller model is sequential root ownership.
4. FEF-001 and the separate capsule/preflight/acceptance/driver integration remain independent gates.
5. No actual fixture, thread, server, socket, NativeHarness, Bridge, Git, fake ORX, process, provider/auth, Docker, data, score, or P0 ran. Live P0 remains held.
