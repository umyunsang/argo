# HousePrice Option A2 phase-completion independent review v1

## Decision

**NEEDS ONE P1 REPAIR before terminal completion can be admitted.**

`complete_phase` accepts JSON boolean `false` as the process receipt `returncode` and publishes `INITIAL_HANDOFF_PUBLISHED: VERIFIED`. The output contract requires exact integer zero. All 15 supplied tests pass, and four independent gate/process/session/final cross-binding controls confirm the other main guards are necessary and effective.

This is a synthetic read-only review. It did not call `evaluate_gate_config`, manufacture a new gate outcome through the gate API, execute a real controller/bootstrap/Prime/provider/auth/ORX/Docker/data path, inspect a hidden score, edit source, run npm, commit, or nest another agent. Changing bootstrap/producer/phase-driver files were not reviewed. Live P0 remains held.

## Hash-bound inputs

All three requested artifacts were read in full and matched the root hashes:

| File | Bytes | SHA-256 |
|---|---:|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/phase_completion.py` | 36820 | `961dadaa0179aa3de9462ed58eded8234a853350322afb970587cbac1a05880f` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_phase_completion.py` | 36786 | `018be082241e637b107e737cada4e67c6225f4159453ab630566b9ab5783c66c` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-phase-completion-report-v1.json` | 21063 | `2c7371cab2ae804fefd23803a95fa91c502cfeab678f58cabc0e4bb9b75d824b` |

Contracts read in full:

| File | Bytes | SHA-256 |
|---|---:|---|
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-completion-contract-v1.json` | 5373 | `1f61d6e6e392d600236d6194230ef935d4711bba8b12d886a40adcedc868c233` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-completion-output-contract-v1.json` | 3551 | `afc481aa5d499917fa961d3737561beafcbc9e5ff67ae041be77b3d12244a4d2` |

The source and test archived snapshots are byte-identical to the reviewed files. The archived report is byte-identical to the reviewed report.

## Finding

### PC-001 — P1 — boolean `false` is accepted as exact process return code zero

Locations: `phase_completion.py:190-194,330-364`; stable dependency `bridge.py:1951-1963` at hash `979c84adc265541c816a01eca39ec775eaa6374a7bc4495a2366b6ca6eefdd03`.

The completion contract requires `returncode` to be exact-int `0`. `phase_completion` delegates terminal shape to `_valid_prior_process_receipt` and does not check `returncode` again. The stable helper uses:

```python
value.get("returncode") != 0
```

In Python, `False == 0`, so JSON `"returncode": false` passes. `_verify_process_receipt` checks paths, environment keys, start time, and resource caps, but not return-code type.

Independent negative control:

```text
NC02_boolean_returncode=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
```

The control changed only the root-bound synthetic receipt from numeric `0` to JSON `false`, recomputed its `FileBinding`, and used the normal completion path with the mocked read-only Bridge. This is a real incorrect admission, not an omission-mutant demonstration.

Required repair:

- Before accepting terminal evidence, require `type(receipt.get("returncode")) is int and receipt["returncode"] == 0` in `phase_completion`.
- Add a regression that changes only `returncode` to `False` and proves `NOT_ADMITTED / EVIDENCE_MISMATCH` with an empty completion directory.
- Harden `_valid_prior_process_receipt` similarly, or record why other dependency callers are separately guarded. The local exact check is required even if the shared helper repair is deferred.

## Independent guard controls

The bounded control fixture used `CompletionFixture` with fabricated files and `FakeBridge`. No real Bridge, process, or gate evaluator ran.

### NC-01 — native gate decision/view cross-binding

A corrupted latest research view hash was rejected with zero publications. Omitting only `_verify_latest_gate` caused an initial handoff to publish. This confirms the implementation does not trust typed READY alone.

```text
NC01_gate_hash_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC01_gate_hash_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
```

### NC-02 — process terminal/path cross-binding

A receipt frontend path differing from the process config was rejected. Omitting only `_verify_process_receipt` published a handoff. The same group exposed PC-001 without omitting any guard.

```text
NC02_process_path_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC02_process_path_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC02_boolean_returncode=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
```

### NC-03 — current checkpoint and prior-session cross-binding

Changing current session bytes/tokens while updating only the root `FileBinding` was rejected against the existing gate checkpoint. Omitting `_verify_gate_usage` published. A continuation that replayed the prior response ID was rejected with zero publications.

```text
NC03_current_gate_usage_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC03_current_gate_usage_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC03_prior_current_replay=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
```

### NC-04 — final scientific identity cross-binding

A canonical lock whose task hash differed from the Bridge task identity was rejected. Replacing `_read_final_lock` with a controlled trust-only stub published that wrong task hash, while still recording `hidden_score_observed=False`. This confirms the real scientific identity comparison is decisive and no score is needed.

```text
NC04_final_science_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC04_final_science_guard_omitted=FINAL_COMPLETION_PUBLISHED:VERIFIED:files=1
NC04_omitted_published_wrong_task=True
NC04_hidden_score_observed=False
```

## Scoped passing controls

Subject to PC-001:

- Invalid input returns the fixed safe result, while `BaseException` is not caught.
- Gate config, process config/receipt, frontend deployment, current/prior session, bridge config, gate history/latest record, Bridge context rights/views, usage checkpoint, and final lock are reopened through bounded readers.
- Missing gate history, active gate lock, chain corruption, session mutation, incomplete usage, replayed response ID, budget exhaustion, non-READY decision, foreign context, and final scientific mismatch do not publish.
- The latest native gate is selected from the actual contiguous private history; this reader never calls `evaluate_gate_config`.
- Initial publication preserves the exact 13-field handoff schema. Final publication binds process/gate/Bridge/current+prior/final-lock evidence and emits `hidden_score_observed=false` without scoring.
- Completion publication uses fixed names, `O_EXCL`, bounded full writes, fsync, reopen/hash binding, and no fabricated binding on partial failure.
- The independent omission controls show gate view, process path, current usage checkpoint, and final scientific checks each prevent an otherwise publishable false completion.

## Dependency identity check

The eight private dependency bytes still match the producer report. This is identity confirmation, not a new review of their changing behavior.

| Dependency | SHA-256 | Match |
|---|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py` | `979c84adc265541c816a01eca39ec775eaa6374a7bc4495a2366b6ca6eefdd03` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/campaign_usage.py` | `d1e658d8402eee0e967ad05f35f4f5945d2025a6484ff658f8ea30efb76dc13a` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_process.py` | `135a3e28291ea8e7db3b85cdd4fda05124113baaeb0d1a1335a905bc5bdd3f33` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/grading.py` | `bf8b2deb3f4113c4b3f734928642a37fd84410546bc0c22725e8f495d6ccc0be` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/phase_gate.py` | `94c43549e17ed453b9b7ada622957f74aff0530b33d8d6df095c4aae1bc631ba` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/staging.py` | `9813081081af6b128a1c91eb06c4ba07fa6c260eee8984c708c3094e3a635800` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/trusted_io.py` | `66a4e8ae3dedf96d6e621a88931bd2e4b97cc746b9c2ef76644850e870fcd2e0` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/usage_observer.py` | `d336bd567ee381d2b244271bc8bc8a28c471a2702ce6d15b6a363efb77f1e57c` | yes |

`FileBinding` values remain root-caller authority. Reopening a self-consistent binding does not prove that the caller selected the approved artifact; the root driver must bind these exact identities in its immutable completion request.

## Qualification evidence

All four files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-phase-completion-v1` were read in full:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `a2-phase-completion-report-v1.json` | 21063 | `2c7371cab2ae804fefd23803a95fa91c502cfeab678f58cabc0e4bb9b75d824b` |
| `a2-phase-completion-report-v1.pre-correction.json.snapshot` | 20907 | `6b388219c5a3ca68739f27613386654cdc68d891e8c637d2b1da275f03b5537c` |
| `phase_completion.py.snapshot` | 36820 | `961dadaa0179aa3de9462ed58eded8234a853350322afb970587cbac1a05880f` |
| `test_phase_completion.py.snapshot` | 36786 | `018be082241e637b107e737cada4e67c6225f4159453ab630566b9ab5783c66c` |

Evidence interpretation:

- The ambient Python 3.14 missing-module collection failure is excluded. It is not behavioral RED and is not approved-kernel evidence.
- The 11-test implementation iteration is a genuine fail-closed intermediate, not proof that every final guard had failing-first coverage.
- The final 15-test Python 3.11 run is the supplied green baseline.
- The independent NC-01 through NC-04 omission/negative controls add targeted qualification for the most important gate, process, current/prior usage, and final scientific cross-bindings.

## Exact executions

### Exact 15-test suite

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion
test_continuation_publishes_exact_final_completion_without_hidden_score (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_continuation_publishes_exact_final_completion_without_hidden_score) ... ok
test_existing_name_is_publication_failed_without_overwrite (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_existing_name_is_publication_failed_without_overwrite) ... ok
test_final_scientific_identity_mismatch_does_not_publish (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_final_scientific_identity_mismatch_does_not_publish) ... ok
test_foreign_bridge_context_does_not_publish (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_foreign_bridge_context_does_not_publish) ... ok
test_incomplete_current_session_maps_to_usage_unknown (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_incomplete_current_session_maps_to_usage_unknown) ... ok
test_initial_publishes_exact_handoff_from_terminal_evidence (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_initial_publishes_exact_handoff_from_terminal_evidence) ... ok
test_invalid_config_returns_safe_result_but_base_exception_is_not_caught (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_invalid_config_returns_safe_result_but_base_exception_is_not_caught) ... ok
test_missing_actual_gate_and_active_gate_lock_are_evidence_mismatch (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_missing_actual_gate_and_active_gate_lock_are_evidence_mismatch) ... ok
test_mutated_session_or_history_never_publishes (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_mutated_session_or_history_never_publishes) ... ok
test_native_budget_stop_maps_to_budget_exhausted (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_native_budget_stop_maps_to_budget_exhausted) ... ok
test_nonready_native_gate_does_not_publish (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_nonready_native_gate_does_not_publish) ... ok
test_partial_publication_failure_returns_no_fabricated_binding_and_preserves_partial (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_partial_publication_failure_returns_no_fabricated_binding_and_preserves_partial) ... ok
test_process_config_environment_must_match_sealed_frontend_deployment (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_process_config_environment_must_match_sealed_frontend_deployment) ... ok
test_process_receipt_boolean_and_mismatched_path_do_not_prove_termination (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_process_receipt_boolean_and_mismatched_path_do_not_prove_termination) ... ok
test_replayed_response_id_across_contexts_never_publishes (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_replayed_response_id_across_contexts_never_publishes) ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.140s

OK
EXIT_CODE=0
```

### Independent bounded controls

Fixture: `/tmp/hp-a2-phase-completion-review-ogv_7po6/independent_controls.py` — `17bd5be7d191801638f1a9232c0a5e81f792f1058d1239b3f61a4a10ef73f72a` (4374 bytes). The complete fixture source is preserved in the JSON report.

```text
$ PYTHONPATH=/Users/um-yunsang/argo-paper-orx /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B /tmp/hp-a2-phase-completion-review-ogv_7po6/independent_controls.py
NC01_gate_hash_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC01_gate_hash_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC02_process_path_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC02_process_path_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC02_boolean_returncode=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC03_current_gate_usage_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC03_current_gate_usage_guard_omitted=INITIAL_HANDOFF_PUBLISHED:VERIFIED:files=1
NC03_prior_current_replay=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC04_final_science_guard=NOT_ADMITTED:EVIDENCE_MISMATCH:files=0
NC04_final_science_guard_omitted=FINAL_COMPLETION_PUBLISHED:VERIFIED:files=1
NC04_omitted_published_wrong_task=True
NC04_hidden_score_observed=False
EXIT_CODE=0
```

## External integration conditions and nonclaims

1. The root driver must supply the approved `FileBinding` and `DirectoryIdentity` values after a clean process return. Root-selected bindings are authority; model/self-attested hashes are not.
2. The real Bridge loader and read-only views, final trusted-I/O lineage, installed namespace, deployment/frontend identities, and terminal process receipt must be frozen together in the completion closure.
3. The completion directory and evidence roots remain root-private under the no-malicious-concurrent-same-UID TCB. This is not hostile-host or whole-OS isolation.
4. Process completion is not provider correctness, a hard current-response token cap, a hidden score, or scientific performance evidence.
5. Bootstrap/producer/phase driver, controller-deployment, full combination, OAuth, provider identity, actual data/ORX/Docker, immutable production receipts, and actual P0 remain pending.
