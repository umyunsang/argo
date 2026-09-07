# HousePrice Option A2 root-reader independent review v2

## Decision

**SCOPED PASS: F-01 through F-05 are resolved on the eight frozen v2 hashes.**

No new behavioral defect was found in the repaired scope. The five v1 counterexamples now fail closed or preserve the intended pending state. The 46-test synthetic suite passed independently, and a separate bounded mutation fixture reproduced the five prior failures plus the required gate-history and checkpoint cases.

This is not generic launch readiness. It used no actual data, provider/auth, Prime process, Bridge call, ORX, Docker, controller process, npm, native runtime change, source edit, commit, or actual P0. Native construction remains paused. Actual P0 remains held pending root integration and OAuth confirmation.

## Authority and preserved review

- Repair validation: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-root-readers-repair-validation-v2.json` — `123b03411904d09ccacfbc43225723e4a12367ae18d4fac6b3a8931806c8d700` (9331 bytes).
- Repair scope: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-root-readers-repair-scope-v2.json` — `6a6c2aa7d18f9dc1abacc8c3261b6438e70e96909e7e0dcbb32a358ff14fb2e8` (2014 bytes).
- Original v1 Markdown remains `4717019be4665905d3685e11ccbbc83354b74125171958561670a5ffdd54ed38` (18657 bytes).
- Original v1 JSON remains `5dbc6043653fcd332c3585fcb6dbcc525708211ca454b824c800dde2a7b8a2b9` (29129 bytes).

## Frozen source hashes

All eight sources were read in full. Each matches the v2 validation and its archived snapshot byte-for-byte.

| File | Bytes | SHA-256 | Validation match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/phase_gate.py` | 24124 | `94c43549e17ed453b9b7ada622957f74aff0530b33d8d6df095c4aae1bc631ba` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_phase_gate.py` | 19657 | `5680a3491c1d45d98de97fd55ee5bccd3d967a3ea684ec79af0f945b596bc649` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/campaign_usage.py` | 7505 | `d1e658d8402eee0e967ad05f35f4f5945d2025a6484ff658f8ea30efb76dc13a` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_campaign_usage.py` | 6773 | `b0a1fafc2934abe38e8630cb90d50ba61b33fed99530554d1b80f11904abc1de` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/usage_observer.py` | 13833 | `d336bd567ee381d2b244271bc8bc8a28c471a2702ce6d15b6a363efb77f1e57c` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_usage_observer.py` | 9530 | `b84be49b610e6860696eee86f57884806baaeb3f01380c51a4f94fb2e126ef47` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/source_closure.py` | 7962 | `e4b0b8732d48d2ecbcd57b6d9e01dbf88200ab5e57bf12426d28d22017ae4466` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_source_closure.py` | 4208 | `691fd50d3d6fbb6557853cabe87f6a68661f883c9aef961e1764b7b92832680b` | yes |

## Finding closure

### F-01 — RESOLVED — usage lineage survives fresh gate invocations

Locations: `usage_observer.py:99-180,223-260`; `phase_gate.py:326-411,448-486`.

The observer exports a bounded, config-bound checkpoint with the exact native filename/device/inode, category counts, observed byte count, and prior full-prefix hash. A fresh observer validates and restores it. The v2 gate serializes evaluations with a private `O_EXCL` lock, reads a contiguous maximum-40 outcome chain, validates each checkpoint, and appends a chained v2 outcome.

Independent results:

- 3,745-token complete state followed by rollback or file deletion: `STOP_USAGE_UNKNOWN`, retaining 3,745.
- Partial append: `STOP_USAGE_UNKNOWN`, retaining the 2,082 known complete tokens; later file repair remains sticky stop.
- Valid append: 2,082 -> 3,745 and remains READY.
- Exact-byte inode replacement: `STOP_USAGE_UNKNOWN`, retaining 3,745.
- No startup file: `WAITING_FIRST_USAGE` / `NOT_READY`; a later first valid file becomes READY.
- Contiguous chain succeeds. A hole, changed sequence, or pre-existing lock fails closed.
- Short writes are completed by the write loop. An interrupted 11-byte outcome is retained and blocks the next invocation.
- The 41st outcome is rejected with exactly 40 durable outcomes retained.

This closes the cross-process rollback found in v1 without a new lifecycle registry.

### F-02 — RESOLVED — unsupported usage attribution is unknown

Locations: `campaign_usage.py:80-91,128-136`.

`child_usage_attributed` is always marked `UNSUPPORTED_USAGE_ATTRIBUTION`. Other non-assistant records with nested usage keys are also incomplete. Known assistant usage remains counted. This is the correct fail-closed behavior for the fixed six-tool, no-RLM P0 protocol.

Independent result: a record carrying a 5,200-token aggregate produced incomplete usage with known total 118 and `UNSUPPORTED_USAGE_ATTRIBUTION`.

### F-03 — RESOLVED — missing response identity is unknown and counts remain

Locations: `campaign_usage.py:145-153`.

Missing or empty `responseId` now adds `MISSING_RESPONSE_ID`; it cannot yield complete campaign usage. Known categories remain counted, and existing duplicate-ID checks remain unchanged.

Independent result: a missing-ID assistant produced incomplete usage with known total 118. The original installed Faux capture is correctly reclassified as incomplete `MISSING_RESPONSE_ID` with known total 3,745. Its unchanged bytes do not prove that a real provider response will carry an ID. Positive fixtures explicitly add synthetic IDs and are not provider evidence.

### F-04 — RESOLVED — verified metrics constrain remaining opportunities

Location: `phase_gate.py:184-185`.

The predicate now rejects `remaining_dev_opportunities > max(0, 3 - verified_dev_count)`. It does not infer infrastructure-repair status from public status.

Independent result: two verified dev results with `remaining_dev_opportunities=3` return `STOP_PROTOCOL_INVALID`, not READY.

### F-05 — RESOLVED — expected SourceTree has strict types and bounds

Locations: `source_closure.py:138-165`.

The expected record is validated before tree capture. Root/hash strings, canonical root identity, exact integer types, counters, aggregate entry bound, bytes, inode/device, and mtime bounds are checked. Boolean numeric fields are rejected.

Independent result: `file_count=True` raises `ClosureError` on a one-file tree.

## Archived repair evidence

All 27 files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-root-readers-v2-repaired` were read in full. All 11 recorded RED/partial/GREEN log hashes and sizes match the validation. All eight snapshots equal the current frozen source bytes.

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `01-usage-source-red.log` | 5286 | `66585600c34df465813aa348fa3be572c8045796dff64cfd4902b833986ec4b9` |
| `02-gate-red.log` | 4404 | `03e48bdfe698d9719bdfa424e92ddc1c8231c7385789949e99650215a7b4b985` |
| `03-usage-source-partial-green-failed.log` | 2099 | `6705f967ab55e4f9df1187563df5aae9b2284048b838693881e2c1c56828bd12` |
| `04-observer-checkpoint-red.log` | 5698 | `8d3c036e819c7450f191ded7e31b1b8386d505800814702c6e7906bf2d650edd` |
| `05-F01-derived-positive-still-red.log` | 1967 | `8764694a7b93eff5cd3c2bf34c17035f6b3553bae762d0cf87da0e62e80df0e6` |
| `06-observer-green.log` | 1752 | `9f10d701f3bc7570a96ef314794fd2a96074154c067e2cc5500420da201ac1a3` |
| `07-gate-history-red.log` | 6268 | `b5e15ace9c4898ad0cfbd10877c4f32a707debfc6b55e40e86a0887101b25701` |
| `08-gate-green.log` | 3347 | `3b2626c3c6dd8d0a618cf668e88152c9ff92c2bb2ae96a484e057c02e3d5a213` |
| `09-gate-observer-green.log` | 5922 | `932c70f2359a063748c292754a222939a332b63ca8e967286481b3c3c0b1a8ce` |
| `10-usage-source-green.log` | 1497 | `30c70ec9f5872267bd323b84b049351289f1169743d9d0e7ce1af5c4a55a4089` |
| `11-gate-final-green.log` | 3893 | `a01f710429bf8f5ae2d7b44e5ed0ae00400c0b59d00296f77d9acf28f10ba67d` |
| `campaign_usage.py.diff` | 2154 | `348320b488f7d776f88e4797c307fade95ca6808ec7f828d99e9397d78c016dd` |
| `campaign_usage.py.snapshot` | 7505 | `d1e658d8402eee0e967ad05f35f4f5945d2025a6484ff658f8ea30efb76dc13a` |
| `phase_gate.py.diff` | 13626 | `a9120c9864cd9d986da6b86605ff4ec14f8dc3360ce0d145216bbef21f016242` |
| `phase_gate.py.snapshot` | 24124 | `94c43549e17ed453b9b7ada622957f74aff0530b33d8d6df095c4aae1bc631ba` |
| `source_closure.py.diff` | 1973 | `aaf75b42cfd7ae245a8782cb47346aef62cfa972b297f92cbd568c6d60b8cdd2` |
| `source_closure.py.snapshot` | 7962 | `e4b0b8732d48d2ecbcd57b6d9e01dbf88200ab5e57bf12426d28d22017ae4466` |
| `test_campaign_usage.py.diff` | 2018 | `23706b8671d7f51310859bd30898561e469860be44328b9e5c0912c8d71d80d3` |
| `test_campaign_usage.py.snapshot` | 6773 | `b0a1fafc2934abe38e8630cb90d50ba61b33fed99530554d1b80f11904abc1de` |
| `test_phase_gate.py.diff` | 6497 | `7c4e85a301153e0653a3ad5cd0b2074225ed67b73f6446c00b858b517a18c65f` |
| `test_phase_gate.py.snapshot` | 19657 | `5680a3491c1d45d98de97fd55ee5bccd3d967a3ea684ec79af0f945b596bc649` |
| `test_source_closure.py.diff` | 1294 | `e89663a4ca613bb77c63efc47ea7e527382af40097325dc5ec4f6e09972e5c92` |
| `test_source_closure.py.snapshot` | 4208 | `691fd50d3d6fbb6557853cabe87f6a68661f883c9aef961e1764b7b92832680b` |
| `test_usage_observer.py.diff` | 4860 | `7cb6a42c14a4114990d811f312919d331af57c1dec0c83e7a9f756f1ed6bbc3e` |
| `test_usage_observer.py.snapshot` | 9530 | `b84be49b610e6860696eee86f57884806baaeb3f01380c51a4f94fb2e126ef47` |
| `usage_observer.py.diff` | 10130 | `3f6781b15085cdeb81bc03dc18d106f6b18214cd51c1d33b724c867c33609eaa` |
| `usage_observer.py.snapshot` | 13833 | `d336bd567ee381d2b244271bc8bc8a28c471a2702ce6d15b6a363efb77f1e57c` |

The archived sequence supplies failing-first evidence for all five v1 findings, then checkpoint/history negatives, then the final 21 gate + 12 observer + 8 usage + 5 closure green state. The first green observer log has 9 tests and is intermediate; the final counts are taken only from `09`, `10`, and `11` and the independently rerun suites below.

## Exact independent executions

### Campaign usage and source closure — 13 tests

```text
$ cd experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime && /usr/bin/python3 -B -m unittest -v test_campaign_usage.py test_source_closure.py
test_all_four_categories_including_cache_reads_are_counted (test_campaign_usage.CampaignUsageTest) ... ok
test_archived_installed_prime_session_matches_exact_category_totals (test_campaign_usage.CampaignUsageTest) ... ok
test_child_or_unsupported_usage_attribution_is_unknown_in_no_rlm_protocol (test_campaign_usage.CampaignUsageTest) ... ok
test_combined_budget_never_resets_and_session_duplicates_are_rejected (test_campaign_usage.CampaignUsageTest) ... ok
test_missing_partial_and_zero_error_usage_is_unknown_not_free (test_campaign_usage.CampaignUsageTest) ... ok
test_missing_response_identity_is_incomplete_without_losing_known_usage (test_campaign_usage.CampaignUsageTest) ... ok
test_native_identity_duplicate_or_malformed_usage_rejected (test_campaign_usage.CampaignUsageTest) ... ok
test_nonassistant_rows_do_not_manufacture_usage_and_branches_rejected (test_campaign_usage.CampaignUsageTest) ... ok
test_boolean_expected_fields_are_not_integer_census_values (test_source_closure.ClosureTest) ... ok
test_caps_before_read_and_root_identity_changes (test_source_closure.ClosureTest) ... ok
test_complete_tree_and_rederived_bytes_not_self_attestation (test_source_closure.ClosureTest) ... ok
test_internal_symlink_bound_external_and_fifo_rejected (test_source_closure.ClosureTest) ... ok
test_mutation_hidden_add_remove_and_preserved_mtime_rejected (test_source_closure.ClosureTest) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.014s

OK
EXIT_CODE=0
```

### Usage observer — 12 tests

```text
$ /usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer
test_combined_limit_counts_prior_not_reset_and_disallows_duplicate_session (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_counter_regression_is_detected_without_prior_unknown_state (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_foreign_filename_and_sticky_unknown_never_reenable_work (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_links_multiple_files_and_root_replacement_are_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_original_native_capture_missing_ids_stops_but_retains_known_counts (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_restored_checkpoint_allows_only_real_append_and_preserves_waiting (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_restored_checkpoint_rejects_replaced_identical_file (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_restored_checkpoint_rejects_rollback_and_missing_file (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_restored_checkpoint_validates_configuration_types_and_prefix (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_unknown_partial_and_counter_regression_stop_after_record (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_waiting_is_not_zero_complete_and_native_bytes_count (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_wrong_native_identity_and_oversize_fail_closed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.017s

OK
EXIT_CODE=0
```

### Phase gate — 21 tests

```text
$ /usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate
test_corrupt_or_busy_history_fails_closed_without_new_outcome (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_corrupt_usage_stops_without_claiming_readiness (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_final_lock_is_reopened_and_compared_to_bridge_canonical_lock (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_fresh_gate_invocation_cannot_roll_back_or_forget_completed_usage (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_fresh_gate_keeps_valid_append_but_denies_identical_inode_replacement (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_outcome_chain_is_contiguous_and_checkpoint_is_exact (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_outcome_count_cap_and_short_write_are_fail_closed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_partial_outcome_write_is_retained_and_blocks_next_invocation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_reads_same_bridge_views_and_publishes_hashed_native_usage_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_terminal_failure_stdout_is_safe_stop_not_retry (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_unknown_usage_cannot_be_repaired_into_readiness_on_next_call (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_wrong_lock_path_and_config_hash_fail_before_bridge_call (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_budget_unknown_and_waiting_are_distinct_from_completion (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_exact_schemas_duplicate_ids_type_bounds_and_hashes_are_checked (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_final_requires_root_loaded_lock_matches_native_artifact_and_selected_dev_code (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_first_result_or_active_run_is_not_ready_and_unknown_is_not_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_initial_cannot_skip_handoff_or_accept_self_declared_eligibility (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_initial_exact_two_verified_results_and_hashed_research_are_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_known_failed_attempt_is_preserved_without_becoming_eligible (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_unbound_attempt_or_missing_final_reference_never_reports_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_verified_metric_count_bounds_remaining_opportunities (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.221s

OK
EXIT_CODE=0
```

Total: 46 synthetic tests; all passed.

### Independent mutation fixture

Disposable fixture: `/tmp/hp-a2-root-readers-v2-rereview-lbmonvk0/independent_rereview.py` — `d0122c9663fe75f8bfeea7a7bb87159d846e3ea492ec08ce6fe64a84973590f4` (7465 bytes).

```text
$ PYTHONPATH=/Users/um-yunsang/argo-paper-orx /usr/bin/python3 -B /tmp/hp-a2-root-readers-v2-rereview-lbmonvk0/independent_rereview.py
F01_first=READY_INITIAL_CHECKPOINT:3745
F01_fresh_rollback=STOP_USAGE_UNKNOWN:3745
F01_fresh_missing=STOP_USAGE_UNKNOWN:3745
F01_partial=STOP_USAGE_UNKNOWN:2082
F01_partial_repaired_but_sticky=STOP_USAGE_UNKNOWN:2082
F01_valid_append=(2082, 3745, 'READY_INITIAL_CHECKPOINT')
F01_identical_replacement=STOP_USAGE_UNKNOWN:3745
F01_absent_start=WAITING_FIRST_USAGE:NOT_READY
F01_after_absent_valid_file=READY_INITIAL_CHECKPOINT:3745
CHAIN_contiguous=(1, 2, True)
CHAIN_hole_blocked=(True, 1)
CHAIN_corruption_blocked=True
CHAIN_O_EXCL_busy_lock=(True, True)
CHAIN_short_write_completed=('READY_INITIAL_CHECKPOINT', 1)
CHAIN_partial_write=(True, 11, True, 1)
CHAIN_count_bound=(True, 40)
F03_missing_response=(False, 118, ('MISSING_RESPONSE_ID',))
F02_child_attribution=(False, 118, ('UNSUPPORTED_USAGE_ATTRIBUTION',))
F04_contradictory_remaining=STOP_PROTOCOL_INVALID
F05_boolean_expected_rejected=True
EXIT_CODE=0
```

The fixture used `PhaseGateCliTest` only for its synthetic config and `FakeGateBridge`; every gate call patched `load_bridge_from_config`. No actual Bridge method, provider, controller, or scientific run was invoked. Temporary data and the 40-outcome cap fixture remained below 1 MiB.

## Scoped passing controls and limits

- F-01 history is bounded to 40 exact `0600` regular single-link outcomes and 1 MiB. File reads are bounded to 16 KiB each. The current session remains bounded to 8 MiB.
- The checkpoint is tied to the full observer config. Invalid types, config hash, prefix bytes, filename, file identity, counters, observation shape, or sticky-stop transition fail closed.
- Missing/partial/unsupported/failed usage is never converted to free usage. All four categories, including cache reads, remain in the campaign total.
- The phase predicate still requires strict bridge envelopes, two eligible dev results for initial readiness, hashed nonempty research, no unknown run, and the final run/code/artifact lock match.
- Source closure still rederives the whole declared fake tree rather than trusting the summary. Existing hidden-entry, mutation, symlink, special-file, hardlink, count, size, depth, and root identity checks remain.

Explicit TCB and nonclaims:

1. Gate history is root-private and assumes no malicious concurrent same-UID mutator. A hash chain does not prevent trusted wholesale history deletion or tail replacement. This scoped pass makes no hostile-host claim.
2. The observer accounts completed native responses. It does not impose provider backpressure or a hard current-response token cap. Overshoot remains monitored and recorded.
3. `STOP_*` and READY intentionally exit 0. The parent must independently open the latest durable typed outcome, verify its provenance and clean process receipt, and never treat process 0 or stdout alone as scientific success.
4. Initial-to-continuation handoff and non-run/code/artifact final-lock fields remain parent/producer proof obligations outside these five repairs.
5. Source closure proves bytes only under the declared tree. It is not kernel-atomic execution, an OS shared-library seal, or whole-host isolation. The live installed-tree capture was not rerun.
6. Exact provider response identity, OAuth, full process integration, immutable config/source fan-in, and the already identified process-callback repairs remain external gates. Actual P0 remains blocked.
