# HousePrice Option A2 root-reader independent review

## Decision

**NEEDS REPAIR before actual P0.**

Five concrete defects remain in the frozen root gate, native-usage, and source-closure reader surface. The normal suites pass, but independent mutations show one cross-invocation usage rollback, two native-usage provenance gaps, one contradictory READY state, and one strict expected-record type gap.

This was a synthetic, read-only review. It made no shared source, test, native runtime, provider/auth, ORX, Docker, `run_controller`, commit, or actual-P0 change. Native ARGO construction remains paused. A2/start approval remains in force, but it is not launch authority. User-local OAuth confirmation and full integration remain pending.

## Hash-bound review inputs

Review request: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-root-readers-review-request-v1.json` — `ef617534e4dd8919d36ff4a5cc77419798b7d2e3d75b21b7bb338be9fa4c134a` (2856 bytes).

All eight requested files were read in full and matched before testing:

| File | Bytes | SHA-256 | Request match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/phase_gate.py` | 19284 | `803b43a04bc03c07e791ccebe6bd7bd0f9046704d8f69f4df4a844cbcafa6818` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_phase_gate.py` | 14423 | `e02213c8fc7c44f62f1003b0e741529eba266a238bdea839a493757c13a9a150` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/campaign_usage.py` | 6617 | `d5fd996855dd2ee0168a3bd25be37a3c7ff991201c46384d71225bdf1f278396` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_campaign_usage.py` | 5399 | `9f5a0b268a1480305dbc723ae6dce76bea2d0706adb55b5d9d23b8b820fbd40b` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/usage_observer.py` | 8040 | `4f64631ad0bfae0cfc33c2d066da7c599deeddd16bc08ca1fb7df4b671a06c28` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_usage_observer.py` | 5669 | `73de94151f55035d2faded1a4cb2a093ab3d61a45f282f078ab70b921b09daa0` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/source_closure.py` | 6540 | `08a33f0d08d1ddc8f1494d44be0a959160028dcb43bc49500f4b0d0dbecf534e` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_source_closure.py` | 3274 | `5daa49587f10ccb69b67dbc85d5ca8f77dbac06d69b4728751bf36d7ffe5041c` | yes |

Contracts read in full:

| File | Bytes | SHA-256 |
|---|---:|---|
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-gate-cli-contract-v1.json` | 2550 | `04e96dc1c53f5848d4ed9deb3032c1d57dd0f473eba9d5d39c0d639875522aec` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-gate-exit-semantics-v2.json` | 1355 | `31829eb6c2f01c5756097a37aeaa66f5e3e02e841ceb238de8f3146b6343ed4b` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-predicate-interface-v1.json` | 1742 | `a72ce6864fa8e0ff73cc2ce18f190ba21300194961a5df59b54cda396d085308` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-native-usage-observer-contract-v1.json` | 2002 | `8f2af85aa33adf9c6b79affde5af57880d97f4e89131d495ef94010190834331` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-source-closure-contract-v1.json` | 1741 | `efc817ca1b33155a930b2637a0d28cd8accc2ec54710a6fdb322239a2d8d3304` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-campaign-budget-guard-v2.json` | 1597 | `49b125dc3b955b611213876ffb28e95c3cb2b1568723855a380874cb73d4ee13` |

## Findings

### F-01 — P1 — append/counter rollback protection is lost on every gate subprocess

Locations: `usage_observer.py:77,125-164`; `phase_gate.py:371-372`.

`UsageObserver` detects prefix or counter regression only in one Python object. `_evaluate_gate` constructs a fresh observer on every CLI invocation and supplies no previous current-session observation. A prior gate can observe 236 tokens; after the same inode is truncated to a valid 118-token transcript, a persistent object returns sticky `USAGE_UNKNOWN`, but the next gate-style fresh object returns complete `WITHIN_BUDGET:118`.

This contradicts the observer contract's append-prefix/counter-regression requirement and can reset the campaign denominator across repeated autonomous-gate commands. The same state-loss also means a later missing file can be classified as `WAITING_FIRST_USAGE` instead of unknown.

Required repair: carry a root-sealed prior current-session observation into each new gate invocation, or keep one observer alive across all sample points. Bind session ID, file device/inode, prior byte-prefix identity or an append-verifiable checkpoint, category counts, byte count, and last complete hash. After any prior completed usage, missing, replaced, shorter, non-prefix, or lower-count input must produce durable `STOP_USAGE_UNKNOWN`.

Independent evidence: M02.

### F-02 — P1 — usage-bearing native attribution records are silently ignored

Location: `campaign_usage.py:112-113`.

The parser accepts every non-`message` entry without validating whether it carries usage. Prime v3 has `child_usage_attributed` records. Their `aggregateUsage` is applied to the target assistant when Prime reloads a session, but this parser ignores the record and counts only the original serialized assistant usage. The mutation added a native-shaped attribution with 5,200 child tokens; parsing remained complete and reported 118.

The evaluated P0 is supposed to expose exactly six tools and no RLM. Therefore the smallest safe A2 repair is to reject `child_usage_attributed` and any unsupported usage-bearing entry as usage unknown. If later protocols allow child work, implement and test Prime's exact latest-attribution semantics rather than adding the child and aggregate fields together.

Independent evidence: M04.

### F-03 — P2 — missing response IDs make cross-session replay undetectable

Locations: `campaign_usage.py:127-133,164-166`.

`responseId` is optional in the parser. Two complete sessions with omitted IDs therefore have empty response-ID sets and combine successfully, even when the counted response is otherwise a replay. The fixed `openai-codex` response path exposes a response identity; absence should be conservative unknown for this protocol.

Required repair: require one bounded nonempty response ID for every counted assistant record in this fixed provider/model deployment. Retain duplicate rejection within and across sessions. If a failed/aborted record lacks the ID, preserve its known usage but keep the campaign incomplete/unknown.

Independent evidence: M03.

### F-04 — P2 — an impossible remaining-opportunity census can still publish READY

Locations: `phase_gate.py:80-103,182-194`.

The gate type-checks `remaining_dev_opportunities` but never relates it to eligible dev results or the attempt census. Two verified dev results are necessarily at least two metric-bearing opportunities, so all three metric opportunities cannot remain. The mutation changed only this field from 1 to 3; both forms returned `READY_INITIAL_CHECKPOINT`.

Required repair: reject impossible conservation states before READY. At minimum, `remaining_dev_opportunities <= max(0, 3 - len(verified_dev_ids))`. Stronger exact validation may use a producer-supplied, independently checked repair classification; do not guess repair eligibility from status alone.

Independent evidence: M01.

### F-05 — P3 — `verify_tree` accepts boolean expected counters as integer census values

Location: `source_closure.py:135-139`.

`verify_tree` checks only `isinstance(expected, SourceTree)` and dataclass equality. Python makes `True == 1` and `False == 0`. For a one-file tree, replacing the expected `file_count` with `True` is accepted. Tree bytes and digest are still rederived, so this is not a content bypass, but it violates strict typed summary validation at the future root adapter boundary.

Required repair: validate every expected field before capture/comparison. Require exact `str`/`int` types, nonnegative bounded counts/bytes/time/device/inode, canonical root equality, and a lower-case 64-hex tree hash. Add boolean negatives for all numeric fields.

Independent evidence: M05 boolean case.

## Scoped passing controls

- All 13 phase-gate, 6 campaign-usage, 7 usage-observer, and 4 source-closure tests pass on the frozen files.
- Malformed strict envelopes, duplicate run IDs, unknown run status, unbound attempt counts, active runs, invalid metrics/rows/hashes, and mismatched final run/code/artifact lock fields stop or remain not-ready as intended.
- `STOP_*` and READY intentionally exit 0; only `NOT_READY` exits 1. This is correct under exit-semantics v2. Exit 0 alone is never scientific success.
- The campaign total includes input, output, cache read, and cache write. It does not use `native_autonomous_tokens`, which excludes cache reads.
- Existing linear parent-chain, duplicate entry/response ID, partial record, missing usage, zero usage, failed/aborted response, root session identity, exact filename, symlink/hardlink, multiple-file, file-size, and file replacement controls pass within one observer instance.
- The fake source tree rederives every regular-file byte digest, path, type, and mode; counts hidden files/directories/symlinks; binds literal internal symlink targets; rejects external symlinks, special files, hardlinks, bound violations, mutation, and root inode replacement.
- M05 also observed that a root-directory mode change is not part of `SourceTree`. The frozen source-closure format binds root path/device/inode, not root mode. This review does not expand that explicit format into a whole-OS permission claim.

## External integration and producer conditions

These are not additional defects in the eight reviewed files:

1. The parent must independently open the newly published typed outcome and accept phase advance only for durable `READY_INITIAL_CHECKPOINT` or `READY_FINAL_LOCK`, with the exact config/bridge/view/session/source identities and a clean process receipt. Process exit 0, stdout, or a missing receipt is a protocol-invalid stop.
2. The continuation predicate has no prior-checkpoint receipt input. The parent must bind the durable initial READY receipt, prior native session, method handoff, and selected-code lineage before spawning continuation. A valid current final view alone is not handoff proof.
3. `decide_phase` validates all final-lock fields syntactically but directly matches only run ID, code hash, and artifact hash. Independent task/environment/protocol/closure fields remain the trusted-I/O producer and root-loader obligation.
4. The direct gate calls the hash-bound Bridge read surface. Real Bridge config/input provenance and strict producer derivation remain separate review conditions. This review used a mocked loader only.
5. Source closure still needs a strict expected-record loader and a pre-import root integration. It proves bytes only under the declared installed tree. It is not kernel-atomic execution, an OS shared-library seal, or a whole-host isolation control. The live installed-tree capture was not rerun.
6. Exact six-tool/no-RLM census, the separately repaired process-callback guards, OAuth confirmation, full integration, and immutable source/config fan-in remain required before actual P0.

## Exact executions

Environment query:

```text
$ /usr/bin/python3 --version
Python 3.9.6
```

### Phase gate — 13 tests

```text
$ PYTHONPATH=$PWD /usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate
test_corrupt_usage_stops_without_claiming_readiness (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_final_lock_is_reopened_and_compared_to_bridge_canonical_lock (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_reads_same_bridge_views_and_publishes_hashed_native_usage_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_terminal_failure_stdout_is_safe_stop_not_retry (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_wrong_lock_path_and_config_hash_fail_before_bridge_call (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateCliTest) ... ok
test_budget_unknown_and_waiting_are_distinct_from_completion (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_exact_schemas_duplicate_ids_type_bounds_and_hashes_are_checked (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_final_requires_root_loaded_lock_matches_native_artifact_and_selected_dev_code (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_first_result_or_active_run_is_not_ready_and_unknown_is_not_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_initial_cannot_skip_handoff_or_accept_self_declared_eligibility (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_initial_exact_two_verified_results_and_hashed_research_are_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_known_failed_attempt_is_preserved_without_becoming_eligible (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok
test_unbound_attempt_or_missing_final_reference_never_reports_ready (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_gate.PhaseGateTest) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.016s

OK
EXIT_CODE=0
```

### Campaign usage — 6 tests

```text
$ cd experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime && PYTHONPATH=/Users/um-yunsang/argo-paper-orx /usr/bin/python3 -B -m unittest -v test_campaign_usage
test_all_four_categories_including_cache_reads_are_counted (test_campaign_usage.CampaignUsageTest) ... ok
test_archived_installed_prime_session_matches_exact_category_totals (test_campaign_usage.CampaignUsageTest) ... ok
test_combined_budget_never_resets_and_session_duplicates_are_rejected (test_campaign_usage.CampaignUsageTest) ... ok
test_missing_partial_and_zero_error_usage_is_unknown_not_free (test_campaign_usage.CampaignUsageTest) ... ok
test_native_identity_duplicate_or_malformed_usage_rejected (test_campaign_usage.CampaignUsageTest) ... ok
test_nonassistant_rows_do_not_manufacture_usage_and_branches_rejected (test_campaign_usage.CampaignUsageTest) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.002s

OK
EXIT_CODE=0
```

### Usage observer — 7 tests

```text
$ PYTHONPATH=$PWD /usr/bin/python3 -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer
test_combined_limit_counts_prior_not_reset_and_disallows_duplicate_session (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_counter_regression_is_detected_without_prior_unknown_state (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_foreign_filename_and_sticky_unknown_never_reenable_work (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_links_multiple_files_and_root_replacement_are_rejected (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_unknown_partial_and_counter_regression_stop_after_record (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_waiting_is_not_zero_complete_and_native_bytes_count (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok
test_wrong_native_identity_and_oversize_fail_closed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_usage_observer.UsageObserverTest) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.010s

OK
EXIT_CODE=0
```

### Source closure — 4 tests

```text
$ cd experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime && PYTHONPATH=/Users/um-yunsang/argo-paper-orx /usr/bin/python3 -B -m unittest -v test_source_closure
test_caps_before_read_and_root_identity_changes (test_source_closure.ClosureTest) ... ok
test_complete_tree_and_rederived_bytes_not_self_attestation (test_source_closure.ClosureTest) ... ok
test_internal_symlink_bound_external_and_fifo_rejected (test_source_closure.ClosureTest) ... ok
test_mutation_hidden_add_remove_and_preserved_mtime_rejected (test_source_closure.ClosureTest) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.009s

OK
EXIT_CODE=0
```

### Independent synthetic mutations

Disposable script: `/tmp/hp-a2-root-reader-review-ls5rx7py/independent_mutations.py` — `2afd974cc9790177377226ee94553f31ec41a125ea0e08e18f8b7e3c8da8cd90` (6369 bytes).

```text
$ PYTHONPATH=/Users/um-yunsang/argo-paper-orx /usr/bin/python3 -B /tmp/hp-a2-root-reader-review-ls5rx7py/independent_mutations.py
M01_consistent_remaining=READY_INITIAL_CHECKPOINT
M01_contradictory_remaining=READY_INITIAL_CHECKPOINT
M02_high_total=236
M02_persistent_after_rollback=USAGE_UNKNOWN:236
M02_fresh_after_rollback=WITHIN_BUDGET:118
M03_missing_response_ids_complete=True
M03_response_id_sets=((), ())
M03_cross_session_duplicate_accepted_total=236
M04_attribution_accepted_complete=True
M04_parser_total_with_5200_child=118
M05_root_mode_change_accepted=True
M05_boolean_expected_count_accepted=True
EXIT_CODE=0
```

No mutation touched a reviewed or shared file. All generated data stayed in disposable temporary directories and below the stated limits.
