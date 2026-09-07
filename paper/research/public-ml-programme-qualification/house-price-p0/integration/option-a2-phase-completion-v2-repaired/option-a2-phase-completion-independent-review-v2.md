# HousePrice Option A2 phase-completion independent review v2

## Decision

**SCOPED PASS: PC-001 is resolved in `phase_completion`.**

The local terminal reader now requires exact integer return code zero before calling the shared receipt helper. JSON boolean `false`, float zero, missing values, and other non-integers cannot pass this check. The new failing-first regression proves the original incorrect handoff and the repaired 16-test suite passes.

This closes only the `phase_completion` path. The stable Bridge dependency still has the same `False == 0` gap and remains a separate pre-P0 blocker. No broader readiness is claimed.

## Frozen inputs

Repair receipt: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-completion-pc001-repair-v1.json` — `d8d58c8675062fc37334d1a370ccb3b62a76a9abdec0a6cee741996ef412a70a` (1355 bytes).

| File | Bytes | SHA-256 | Receipt match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/phase_completion.py` | 36910 | `4153bb2d4b92d8602211220913309fd73a995de3b0f83cd28107128896c73f98` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_phase_completion.py` | 37566 | `7ecf838c6c0dae94f1861f619cbf3958cb6674b425641798420c68097ff45cff` | yes |

Both files were read in full. The v2 archive snapshots are byte-identical.

The v1 independent review is preserved unchanged:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-completion-independent-review-v1.md` — `725550e461c63f56893bd1f27154aaf6a5b80b57c311d96e8db91e04361e11db` (16497 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-phase-completion-independent-review-v1.json` — `adacf3d46501ba50ab0fe7c0fb16b123fa1be723e9e1af9a42f4a8548a1fe56b` (21064 bytes)

## PC-001 closure

Location: `phase_completion.py:190-195`.

The original code relied only on `_valid_prior_process_receipt`, where `False == 0` allowed a JSON boolean to satisfy `returncode != 0`. The local repair now requires:

```python
if (type(receipt.get("returncode")) is not int or receipt["returncode"] != 0 or
        not _valid_prior_process_receipt(receipt, config.current_session.path)):
    raise _CompletionError("EVIDENCE_MISMATCH")
```

The exact-type check occurs after the bounded, hash-bound receipt read and before the shared helper, Bridge load, session/gate verification, or publication. Missing `returncode` is handled by short-circuiting on the type check.

New regression: `test_false_returncode_cannot_publish_a_handoff` changes only numeric `0` to JSON `false`, recomputes the root test binding, then requires `NOT_ADMITTED / EVIDENCE_MISMATCH` and an empty completion directory.

The archived RED on the old source showed:

```text
('INITIAL_HANDOFF_PUBLISHED', 'VERIFIED') != ('NOT_ADMITTED', 'EVIDENCE_MISMATCH')
```

The repaired source passes that exact test. PC-001 is therefore closed locally.

## Repair evidence

All four files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-phase-completion-v2-repaired` were read in full. Their hashes and sizes match the repair receipt.

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `01-false-returncode-red.log` | 5025 | `d2ccc879fb3e7941e9156dcd5abafb2659234e34af92d213416916b4753a9558` |
| `02-sixteen-green.log` | 4039 | `54a5a49137faa2c16feeca9a995f18a9bd4fb617ca98f5625c92d9c6ba829a54` |
| `phase_completion.py.snapshot` | 36910 | `4153bb2d4b92d8602211220913309fd73a995de3b0f83cd28107128896c73f98` |
| `test_phase_completion.py.snapshot` | 37566 | `7ecf838c6c0dae94f1861f619cbf3958cb6674b425641798420c68097ff45cff` |

- `01-false-returncode-red.log` is genuine behavioral RED against the old source: the exact malformed boolean receipt published a handoff.
- `02-sixteen-green.log` is the repaired full suite.
- Both source snapshots equal the current frozen bytes.

The source diff adds only the local exact-type/zero guard. The test diff adds only the false-returncode/no-output regression.

## Exact independent execution

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion
test_continuation_publishes_exact_final_completion_without_hidden_score (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_continuation_publishes_exact_final_completion_without_hidden_score) ... ok
test_existing_name_is_publication_failed_without_overwrite (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_existing_name_is_publication_failed_without_overwrite) ... ok
test_false_returncode_cannot_publish_a_handoff (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_phase_completion.PhaseCompletionTest.test_false_returncode_cannot_publish_a_handoff) ... ok
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
Ran 16 tests in 0.137s

OK
EXIT_CODE=0
```

Result: 16/16 synthetic Python 3.11 tests passed. All Bridge/process/files remained mocked or fabricated. No real bootstrap, controller, provider, ORX, Docker, data, auth, hidden score, or P0 ran.

## Preserved scope and external blocker

The v1 gate/process/current+prior/final scientific controls remain unchanged and passed in the 16-test suite. No new finding was found in the two-line local repair.

The shared stable dependency still contains:

```python
value.get("returncode") != 0
```

without an exact-type check. The local guard prevents this completion reader from inheriting that bug. It does not repair other callers, including the Bridge continuation-checkpoint path. The root must fix and independently review that dependency before any real P0.

Other external conditions remain unchanged:

1. Root caller bindings and directory identities, not self-consistent/model claims, are authority.
2. Bridge/read views, trusted-I/O final lineage, namespace/deployment, and process receipt must freeze together.
3. Root-private no-malicious-concurrent-same-UID TCB only; no hostile-host or whole-OS claim.
4. Completion is not provider correctness, hidden score, performance evidence, or a hard current-response token cap.
5. Changing bootstrap/producer/phase-driver/controller-deployment files, full combination, OAuth, provider/data/ORX/Docker, immutable production receipts, and actual P0 remain pending.

No source, test, dependency, npm, or commit changes were made by this review. Only the exact 16-test command ran.
