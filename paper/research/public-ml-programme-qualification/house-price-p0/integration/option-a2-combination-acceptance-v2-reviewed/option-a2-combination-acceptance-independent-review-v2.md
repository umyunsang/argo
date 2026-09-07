# Independent rereview: A2 synthetic combination acceptor v2

## Verdict

**SCOPED PASS.** CAA-I1 and the gate-config source-location join are resolved for the approved pure file/mock scope. I found no new blocking source defect.

This does not admit a synthetic combination or P0. No actual producer, driver, Prime/Faux registration or stream, process, NativeHarness, Bridge, Git, socket, ORX, Docker, auth, data, model, or task ran.

## Reviewed bytes

| File | Bytes | SHA-256 |
|---|---:|---|
| `combination_acceptance.py` | 37,612 | `000c7fe610c9285a8860398fa2bdc6781d75612189e3dd94c4bcb73570907d08` |
| `test_combination_acceptance.py` | 31,618 | `896550ec6d2a53b94b68e77056079183c08d306c13582d3a6e00f00052d8d5b5` |
| `a2-combination-acceptance-report-v2.json` | 12,767 | `2cbb5107dd2b039bb922ee7f73926b7010e9bc50c0d791719fe197184fe1ad68` |

All equal the repaired archive under `integration/option-a2-combination-acceptance-v2-repaired`. The v1 independent review remains unchanged.

Authority included:

- task-binding repair v2: `1d2e9014...c77b6`;
- gate-config source location: `31f984b0...ffbb6`;
- acceptance contract/IO addendum/tool-wire v2;
- reviewed Faux source anchor `4c9b73...b09d6` and schema `553e00...ad61`;
- evidence limits; and
- root producer-consumer layout result v2 (`ed63cffe...40608`, 3/3 file-only tests, not rerun here).

## CAA-I1 result: resolved

### Deployment identity

`_load_configs` still permits only `frontend_path` and `frontend_identity` to differ. `_task_prompt` then requires normal and synthetic process configs to have the exact same original `deployment_path` and full `deployment_identity` (`combination_acceptance.py:379-388`).

It reopens deployment bytes through that stored hash, size, and mtime (`:389-400`). No new path recapture becomes authority.

### Prompt asset

The reader requires exact deployment top-level keys and exact asset, directory, runtime, environment, and limit key sets (`:400-416`). The `task_prompt` seal requires exactly `path, sha256, bytes, mtime_ns_max`, strict types, lower64 hash, 1..131072 bytes, and a bounded decimal mtime. Its path must be inside the frontend SourceTree (`:417-432`).

It reopens the prompt under those values, decodes strict UTF-8, requires nonempty/no NUL, and returns the exact text without trim or normalization (`:433-446`).

### Native user message

`_transcript` requires exactly four message roles. The user object must have exactly `role, content, timestamp`; timestamp must be a non-bool safe integer; content must equal exactly:

```json
[{"type":"text","text":"<opened task prompt text>"}]
```

There is no string shorthand, image, extra block/key, normalized text, or missing field path (`:492-520`).

### Independent internally consistent falsification

The targeted control changed the sole user text, assigned the new session binding as the fixture's current session, regenerated the UsageObserver checkpoint/latest gate over those same bytes, and left deployment unchanged. Result:

```json
{"reason":"TOOL_TRANSCRIPT_INVALID","status":"NOT_ADMITTED"}
```

This closes the original behavioral counterexample.

## Gate-config location result: resolved

`_verify_trees` requires:

```text
expectation.gate_config.path == frontend_tree.root / "gate-config.json"
```

Only this fixed gate input may overlap the frontend SourceTree. It must remain disjoint from the namespace, installed Prime, and all three state roots. Normal/synthetic process configs, process receipt, metadata, session, artifact, profile, session directory, and tmp remain outside all six trees (`combination_acceptance.py:343-376`).

A fresh targeted control moved gate config outside that exact path without first mutating the prompt. It returned `NOT_ADMITTED / SOURCE_MISMATCH`. Therefore the gate-path evidence is not masked by stale prompt mtime.

Root's separate producer-consumer layout suite reports that actual `_prepare_environment` writes `frontend/gate-config.json`, the pure layout accepts that path, and a foreign path fails. This review did not rerun those producer tests.

## Missing-required and output-format checks

Source review confirms:

1. deployment and each nested top-level group require exact key sets;
2. prompt seal is exact and bounded before read;
3. prompt bytes are strict UTF-8, nonempty, no NUL, and compared verbatim;
4. user object requires all three exact keys;
5. timestamp uses `type(...) is int`, so `bool` cannot pass;
6. content equality rejects missing `type/text`, extra key/block, alternate string form, image, or changed text; and
7. prompt mismatch maps to `TOOL_TRANSCRIPT_INVALID`.

The overbound-seal control changed the task seal to 131073 bytes, rehashed the deployment, and regenerated both process config bindings. It returned `NOT_ADMITTED / CONFIG_INVALID` without allocating a large prompt file.

## Author-test masking qualifications

Two author tests need precise interpretation even though independent controls close the behavior:

- `test_task_prompt_asset_change_and_foreign_gate_location_reject` first changes the prompt and then writes the original text back. The old seal's mtime is stale. Its second `SOURCE_MISMATCH` assertion alone would still pass if the gate-location check disappeared, because later prompt reopening would fail. The fresh independent foreign-gate control and root's 3/3 layout suite are the unmasked evidence.
- `test_wrong_bound_user_prompt_rejects_with_consistent_session_and_gate` writes a new session but does not assign that binding to `self.session_binding` before calling `make_latest_gate`; its mocked gate checkpoint is therefore based on the prior fixture session. The independent control explicitly rebinds it and regenerates matching usage/gate evidence.

These are test-proof qualifications, not open source defects after the independent controls.

## Exact author suite

Command:

```text
/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance
```

Exit: `0`  
Duration: `0.319267` seconds  
Tests: 13

```text
test_false_process_exit_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_false_process_exit_rejects) ... ok
test_incomplete_usage_and_cross_response_replay_reject (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_incomplete_usage_and_cross_response_replay_reject) ... ok
test_metadata_mismatch_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_metadata_mismatch_rejects) ... ok
test_missing_gate_rejects_without_manufacture (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_missing_gate_rejects_without_manufacture) ... ok
test_output_aggregate_cap_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_output_aggregate_cap_rejects) ... ok
test_output_file_count_cap_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_output_file_count_cap_rejects) ... ok
test_positive_verifies_one_synthetic_combination (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_positive_verifies_one_synthetic_combination) ... ok
test_source_change_or_missing_proof_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_source_change_or_missing_proof_rejects) ... ok
test_task_prompt_asset_change_and_foreign_gate_location_reject (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_task_prompt_asset_change_and_foreign_gate_location_reject) ... ok
test_tool_result_wire_rejects_extra_key_bool_timestamp_and_envelope (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_tool_result_wire_rejects_extra_key_bool_timestamp_and_envelope) ... ok
test_wrong_bound_user_prompt_rejects_with_consistent_session_and_gate (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_wrong_bound_user_prompt_rejects_with_consistent_session_and_gate) ... ok
test_wrong_faux_config_normalization_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_wrong_faux_config_normalization_rejects) ... ok
test_wrong_tool_id_and_extra_tool_call_reject (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_wrong_tool_id_and_extra_tool_call_reject) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.165s

OK
```

## Exact targeted controls

Command:

```text
/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B -c "exec(compile(open('/tmp/a2_acceptance_v2_controls.py').read(),'/tmp/a2_acceptance_v2_controls.py','exec'))"
```

Exit: `0`  
Duration: `0.177762` seconds

```text
{"fresh_foreign_gate_path":{"reason":"SOURCE_MISMATCH","status":"NOT_ADMITTED"},"internally_consistent_wrong_prompt":{"reason":"TOOL_TRANSCRIPT_INVALID","status":"NOT_ADMITTED"},"overbound_task_prompt_seal":{"reason":"CONFIG_INVALID","status":"NOT_ADMITTED"}}
```

Expected and observed:

| Control | Result |
|---|---|
| Internally consistent wrong user prompt | `NOT_ADMITTED / TOOL_TRANSCRIPT_INVALID` |
| Task prompt seal bytes=131073 with consistent deployment/process bindings | `NOT_ADMITTED / CONFIG_INVALID` |
| Fresh foreign gate path with untouched prompt/mTime | `NOT_ADMITTED / SOURCE_MISMATCH` |

The temporary control script was deleted.

## Preserved passing checks

- normal/Faux configs use full production settings and differ only in frontend identity;
- process receipt uses shared handle/resource/cleanup checks and bounded stdout/stderr;
- usage requires exact session/cwd/provider/model, two ordered nonempty response IDs, all four positive categories, and total below 120000;
- tool call/result/public wire and gate public-envelope hash are exact;
- latest gate interface requires READY, exact checkpoint/session identity, and research/public view hashes;
- missing gate is not evaluated or manufactured;
- typed metadata remains separate from native usage/response proof;
- SourceTrees remain pairwise disjoint except the one fixed frontend gate config; and
- artifact census is descriptor-relative and bounded; assessor publishes nothing.

## Coverage and nonclaims

- Tests use fabricated files and mock `verify_tree` / `_latest_gate`. No actual history, Bridge, source traversal, process or provider path runs.
- The acceptor validates the deployment envelope/key sets and task-prompt seal. It does not independently revalidate every non-prompt deployment value; normalized process configs/shared receipt and producer tests remain separate authority.
- Faux source/schema/metadata are source anchors only. They do not prove native response IDs, usage, OAuth, or transport.
- The dev view remains gate-hash-bound only under the IO addendum; no target regrade is claimed.
- Driver/producer changes, production completion, current-response resource behavior, and P0 remain held.

## Prohibitions

No reviewed source, test, producer, driver, or report was edited. No npm, commit, nesting, real producer/driver/combination/Prime/Faux/process/fixture/Bridge/Git/socket/ORX/Docker/auth/data/model/P0.
