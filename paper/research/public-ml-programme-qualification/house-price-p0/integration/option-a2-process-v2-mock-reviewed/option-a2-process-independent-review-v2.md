# Independent re-review: A2 process mock repair v2

- Generated: `2026-09-07T21:15:00.848628+09:00`
- Result: **SCOPED PASS**
- Decision: all four prior findings are fixed for the requested mock-only scope.
- Clearance recommendation: root may authorize exactly one new bounded synthetic 20-case process component suite on the four reviewed hashes.
- Not authorized: actual P0, production Prime/frontend/provider/auth/data/ORX/Docker execution, or any native product change.
- Current state: both old and repaired live execution remain held until root explicitly grants the narrow suite clearance.

## Hash-bound inputs

| Path | Bytes | SHA-256 | Post-review match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py` | 77092 | `28aa4af2864ec310f1205c58d12a26231c17eedaf1aa02d4dd7300854f5e872f` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py` | 17435 | `c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py` | 35048 | `3ff2d71df5fc8068ceec9fce2653f11533968bb3556926f1e42859879215b578` | true |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json` | 35854 | `67e482428f5ac26b404bff19f72f82a08eb2a5ed3dfcc2d9741c7b7d254bd04d` | true |

- Request: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-process-mock-review-request-v2.json` — `957b9e3095e6d8b9698d4f5e94bf9777ec1cf6228bdae06a60e19c8081d6c339`
- Repair mechanism: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-process-repair-mechanism-v2.json` — `b9df3da1542bdaf3d3dcc9d785903572ab69efe169cb7a603a21153f84a8d1a6`
- Exact external copy root: `/private/tmp/argo-a2-mock-rereview-edfyb0df`
- All four repo/copy hashes matched before mock execution. All four repo hashes matched again after review.

## Prior findings

### 1. A2-PROCESS-001 — `FIXED_FOR_SCOPED_SYNTHETIC_SUITE`

- Every observer failure invalidates last_rows and the snapshot timestamp.
- killpg authority exists only while the directly owned Popen root is live, root_pgid equals pid, and owned_setsid_established is true.
- After root reap, non-root signaling requires a new process snapshot, a tracked and current Darwin microsecond identity, and a second immediate libproc identity/ppid/pgid match. Missing, coarse, short, changed, or unavailable identity causes no PID signal and cleanup_unconfirmed.
- Owner 7-case mocks and independent 8-case mocks patch every os.kill/os.killpg call. Stale/coarse/unavailable cases made zero calls; the only positive non-root authorization reached a patched os.kill after two matching strong observations.

**Residual boundary:** Darwin microsecond identity is not pidfd. The immediate-check-to-signal window remains under the explicitly accepted trusted-host/no-concurrent-same-UID-mutator TCB.

### 2. A2-PROCESS-002 — `FIXED_FOR_SCOPED_SYNTHETIC_SUITE`

- Cleanup confirmation now requires no census_errors.
- _classify_terminal_status checks census errors before success and retains cleanup artifact reasons. The final-census mock returns resource_invalid/artifact_census_failed for returncode 0.

**Residual boundary:** Artifact count and aggregate size remain sampled census triggers and may overshoot; this is unchanged and approved.

### 3. A2-PROCESS-003 — `FIXED_WITH_ACCEPTED_TCB`

- Config and asset reads use O_NOFOLLOW descriptors, fstat identity, bounded reads/hashes, post-read fstat, and pathname identity checks.
- process_exec keeps node/frontend/deployment descriptors open and rehashes/revalidates descriptor plus final pathname immediately before the unchanged pathname exec.
- Owner and independent swap mocks reject descriptor/path replacement and reject an over-cap config before reading it.

**Residual boundary:** The final pathname-check-to-exec window is not kernel atomic. Clearance depends on the explicitly accepted private 0700 closure and no concurrent same-UID mutator. This review does not claim fexecve.

### 4. A2-PROCESS-004 — `FIXED_FOR_SCOPED_SYNTHETIC_SUITE`

- Receipt bytes are written with a progress-checked loop, the temporary regular file is fsynced, publication is no-replace via hard link, and the parent directory is fsynced after publication and temporary removal.
- Successful short-write mocks produce complete newline-terminated JSON. Independent mocks show an existing final receipt is not replaced and first-directory-fsync publication failure removes both apparent final and incomplete names before raising.

**Residual boundary:** Durability remains subject to normal filesystem/fsync guarantees; no stronger hardware persistence claim is made.

## Independent result

- Owner mock suite: **7/7 passed** on byte-exact external copies.
- Independent prior-negative suite: **8/8 passed**. All signal calls were patched. No live signal or child process was used.
- New blocking findings in the requested four-finding scope: **none**.
- Darwin SDK headers match the report hashes. `PROC_PIDTBSDINFO` is flavor 3. `proc_bsdinfo` contains `pbi_start_tvsec` and `pbi_start_tvusec`; the 136-byte ctypes structure and short-return rejection passed mocked checks.

## Conditions for the one synthetic suite

1. Root must explicitly clear the hold for these exact hashes and for one suite only.
2. Maintain the canonical private 0700 closure. Allow no concurrent same-UID mutator between final pathname verification and exec.
3. Any observer, libproc, cleanup, census, or receipt failure fails the suite. Keep no-signal/unconfirmed behavior when non-root identity is unavailable or ambiguous.
4. RSS, aggregate bytes, and file count remain sampled triggers with possible overshoot. This review does not claim a hard RSS limit.
5. The suite must remain fake/synthetic. It cannot call Prime, a provider, auth, data, ORX, Docker, or P0.

## External gates unchanged

- Root completed-record/session usage parsing and live missing/in-flight stop integration remain external. Unknown usage is never zero.
- Frontend artifact-root mtime ordering remains separately owned. These Python mocks do not validate it.
- A passing synthetic process suite is not production or actual-P0 admission.

## Commands and full outputs

### `owner_seven_mock_only_tests_on_exact_external_copies`

**Command**

```text
cd /private/tmp/argo-a2-mock-rereview-edfyb0df && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -m unittest -v test_controller_process.MockOnlyRepairTests
```

Exit code: `0`. Duration: `0.14535087498370558` seconds.

**Full output**

```text
test_ambiguous_same_second_escaped_pid_is_never_signaled (test_controller_process.MockOnlyRepairTests.test_ambiguous_same_second_escaped_pid_is_never_signaled) ... ok
test_config_read_is_descriptor_bounded_and_detects_path_swap (test_controller_process.MockOnlyRepairTests.test_config_read_is_descriptor_bounded_and_detects_path_swap) ... ok
test_darwin_libproc_identity_validates_struct_and_short_return (test_controller_process.MockOnlyRepairTests.test_darwin_libproc_identity_validates_struct_and_short_return) ... ok
test_file_swap_during_descriptor_hash_is_rejected (test_controller_process.MockOnlyRepairTests.test_file_swap_during_descriptor_hash_is_rejected) ... ok
test_final_census_failure_cannot_classify_success (test_controller_process.MockOnlyRepairTests.test_final_census_failure_cannot_classify_success) ... ok
test_observer_failure_never_authorizes_stale_group_or_pid_signal (test_controller_process.MockOnlyRepairTests.test_observer_failure_never_authorizes_stale_group_or_pid_signal) ... ok
test_receipt_short_writes_complete_and_sync_file_and_parent (test_controller_process.MockOnlyRepairTests.test_receipt_short_writes_complete_and_sync_file_and_parent) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.019s

OK
```

### `independent_prior_finding_mock_only_regressions`

**Command**

```text
cd /private/tmp/argo-a2-mock-rereview-edfyb0df && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python independent_prior_finding_regressions_v2.py
```

Exit code: `0`. Duration: `0.08990912500303239` seconds.

**Full output**

```text
test_coarse_and_failed_immediate_nonroot_identity_never_signal (__main__.IndependentPriorFindingRegressions.test_coarse_and_failed_immediate_nonroot_identity_never_signal) ... ok
test_config_descriptor_bound_rejects_over_cap_swap_without_read (__main__.IndependentPriorFindingRegressions.test_config_descriptor_bound_rejects_over_cap_swap_without_read) ... ok
test_direct_live_root_group_authority_expires_with_popen (__main__.IndependentPriorFindingRegressions.test_direct_live_root_group_authority_expires_with_popen) ... ok
test_final_census_failure_prevents_success (__main__.IndependentPriorFindingRegressions.test_final_census_failure_prevents_success) ... ok
test_held_descriptor_and_final_path_revalidation_detect_swap (__main__.IndependentPriorFindingRegressions.test_held_descriptor_and_final_path_revalidation_detect_swap) ... ok
test_matching_strong_nonroot_identity_reaches_only_mocked_pid_signal (__main__.IndependentPriorFindingRegressions.test_matching_strong_nonroot_identity_reaches_only_mocked_pid_signal) ... ok
test_receipt_no_replace_and_failed_publication_cleanup (__main__.IndependentPriorFindingRegressions.test_receipt_no_replace_and_failed_publication_cleanup) ... ok
test_stale_snapshot_never_signals (__main__.IndependentPriorFindingRegressions.test_stale_snapshot_never_signals) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.011s

OK
```

### `post_review_hash_closure`

**Command**

```text
cd /Users/um-yunsang/argo-paper-orx && /Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -c 'import hashlib,json,pathlib
root=pathlib.Path("/Users/um-yunsang/argo-paper-orx")
items=[('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py'"'"', '"'"'28aa4af2864ec310f1205c58d12a26231c17eedaf1aa02d4dd7300854f5e872f'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py'"'"', '"'"'c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py'"'"', '"'"'3ff2d71df5fc8068ceec9fce2653f11533968bb3556926f1e42859879215b578'"'"'), ('"'"'experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json'"'"', '"'"'67e482428f5ac26b404bff19f72f82a08eb2a5ed3dfcc2d9741c7b7d254bd04d'"'"')]
print(json.dumps([{"path":p,"expected":x,"actual":hashlib.sha256((root/p).read_bytes()).hexdigest(),"bytes":(root/p).stat().st_size,"mtime_ns":(root/p).stat().st_mtime_ns,"match":hashlib.sha256((root/p).read_bytes()).hexdigest()==x} for p,x in items],sort_keys=True,indent=2))'
```

Exit code: `0`. Duration: `0.05553945800056681` seconds.

**Full output**

```text
[
  {
    "actual": "28aa4af2864ec310f1205c58d12a26231c17eedaf1aa02d4dd7300854f5e872f",
    "bytes": 77092,
    "expected": "28aa4af2864ec310f1205c58d12a26231c17eedaf1aa02d4dd7300854f5e872f",
    "match": true,
    "mtime_ns": 1788782511849980682,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py"
  },
  {
    "actual": "c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840",
    "bytes": 17435,
    "expected": "c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840",
    "match": true,
    "mtime_ns": 1788782315110887540,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/process_exec.py"
  },
  {
    "actual": "3ff2d71df5fc8068ceec9fce2653f11533968bb3556926f1e42859879215b578",
    "bytes": 35048,
    "expected": "3ff2d71df5fc8068ceec9fce2653f11533968bb3556926f1e42859879215b578",
    "match": true,
    "mtime_ns": 1788782534760390256,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_controller_process.py"
  },
  {
    "actual": "67e482428f5ac26b404bff19f72f82a08eb2a5ed3dfcc2d9741c7b7d254bd04d",
    "bytes": 35854,
    "expected": "67e482428f5ac26b404bff19f72f82a08eb2a5ed3dfcc2d9741c7b7d254bd04d",
    "match": true,
    "mtime_ns": 1788782655598105674,
    "path": "experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-process-report.json"
  }
]
```

## Independent fixture

- SHA-256: `df24cdff942de0cafd82f37339393a50b01f56e9bf24f92bc2ff767df758fdb3`
- Full source is embedded in `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-process-independent-review-v2.json`.

## Conclusion

The repaired bytes close A2-PROCESS-001 through A2-PROCESS-004 for the requested mock-only scope and accepted TCB. Root may move only to one bounded synthetic process suite. No actual P0 or production execution is admitted.
