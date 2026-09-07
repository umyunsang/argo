# Independent review: A2 synthetic combination acceptor v1

## Verdict

**FAIL — one P1 task-to-session binding finding.**

The fixed eleven-test suite passes, and most acceptance checks are strict. A targeted valid falsification shows that `assess_combination` still returns `PASS / VERIFIED_SYNTHETIC_COMBINATION` after the only native user message is replaced with a different prompt and the session/gate usage hashes are updated consistently. The acceptor does not open the frontend deployment's sealed task prompt and does not compare it to the user message.

This blocks the acceptor from serving as independent combination admission evidence. It does not imply any execution, data, or credential exposure.

## Scope and bytes

I read the full 33,072-byte source, 26,032-byte test, and 24,988-byte author report. Current bytes equal `integration/option-a2-combination-acceptance-v1`.

| File | SHA-256 |
|---|---|
| `combination_acceptance.py` | `47ecec4f81706b1332dd9831fcf69ce15344eac39281a7bfa261b8fd76c73f1c` |
| `test_combination_acceptance.py` | `aea9d14212393fdae37713bae7ac22c67a84efc9289a2b2a3ff838bf5b4e1b27` |
| `a2-combination-acceptance-report-v1.json` | `30497d72c12d0d03a219a945c18b18925e1ba63c62ead48940f44d7647e0776f` |

Authority included the acceptance contract (`eaeed2...71819`), IO addendum (`d67c5f...982da`), tool-wire v2 (`f294ce...c4cf6`), reviewed Faux anchor v2 (`077cd9...c1517`), and evidence limits (`c95bc1...f404f`). The Faux source `4c9b73...b09d6` and tool-schema `553e00...ad61` are admitted only as source/mock anchors.

## Baseline execution

Command:

```text
/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance
```

Exit: `0`  
Duration: `0.275010` seconds  
Cases: 11

```text
test_false_process_exit_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_false_process_exit_rejects) ... ok
test_incomplete_usage_and_cross_response_replay_reject (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_incomplete_usage_and_cross_response_replay_reject) ... ok
test_metadata_mismatch_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_metadata_mismatch_rejects) ... ok
test_missing_gate_rejects_without_manufacture (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_missing_gate_rejects_without_manufacture) ... ok
test_output_aggregate_cap_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_output_aggregate_cap_rejects) ... ok
test_output_file_count_cap_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_output_file_count_cap_rejects) ... ok
test_positive_verifies_one_synthetic_combination (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_positive_verifies_one_synthetic_combination) ... ok
test_source_change_or_missing_proof_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_source_change_or_missing_proof_rejects) ... ok
test_tool_result_wire_rejects_extra_key_bool_timestamp_and_envelope (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_tool_result_wire_rejects_extra_key_bool_timestamp_and_envelope) ... ok
test_wrong_faux_config_normalization_rejects (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_wrong_faux_config_normalization_rejects) ... ok
test_wrong_tool_id_and_extra_tool_call_reject (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance.CombinationAcceptanceTests.test_wrong_tool_id_and_extra_tool_call_reject) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.130s

OK
```

All eleven author tests pass.

## Finding CAA-I1 — native user task prompt is not bound

Priority: **P1**  
Status: **OPEN**

### Source evidence

`_transcript` collects four messages and enforces roles `user, assistant, toolResult, assistant` (`combination_acceptance.py:399-414`). It then validates:

- the first assistant tool call and response ID;
- the complete tool-result wire and public body; and
- the final assistant response ID/text.

It never inspects `messages[0]` after checking its role.

`_load_configs` parses and normalizes the normal/synthetic process configs (`:288-325`). It never opens `synthetic.deployment_path`, never parses its `assets.task_prompt` seal, and never opens the root-sealed task prompt bytes. Therefore no independent edge connects the deployed task prompt to the persisted user message.

### Targeted behavioral falsification

The control:

1. creates the normal positive file/mock fixture;
2. replaces the only user message text with `UNEXPECTED_SYNTHETIC_USER_PROMPT`;
3. rewrites the session FileBinding;
4. derives a new valid UsageObserver checkpoint/latest-gate record over those changed bytes; and
5. leaves process configs, public tool result, metadata, state/source identities, response IDs, and all other expectations unchanged.

It uses the same approved mocks for `verify_tree` and `_latest_gate`; it does not call a driver, process, Bridge, or provider.

Command:

```text
/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B -c "exec(compile(open('/tmp/a2_acceptance_user_prompt_control.py').read(),'/tmp/a2_acceptance_user_prompt_control.py','exec'))"
```

Exit: `0`  
Duration: `0.154542` seconds

```text
{"campaign_tokens":278,"reason":"VERIFIED_SYNTHETIC_COMBINATION","status":"PASS"}
```

Observed `PASS` confirms the missing task-prompt binding.

### Impact

A root/miswired synthetic case can be accepted even when native Prime received a different user task from the sealed frontend deployment. The rest of the evidence can remain internally consistent because usage and gate checkpoint bind session bytes, not the intended task bytes.

This contradicts the contract's requirement that no unexpected messages pass. It leaves task-to-session lineage dependent on the same driver that the acceptor should independently check.

### Required repair

1. Open `synthetic.deployment_path` through its `deployment_identity` hash, size, mtime, and path.
2. Strictly parse the exact controller deployment without invoking a producer or driver.
3. Reopen `assets.task_prompt` from its FileBinding under the existing cap and strict UTF-8 rules.
4. Require the one user message to be exactly the expected text content with no image or extra content.
5. Because normal/synthetic configs are supposed to differ only by frontend identity, also require their deployment identity/path to match or compare both task-prompt bindings.
6. Add a failing-first case that keeps session/gate/usage hashes internally valid but changes the user prompt; expect `TOOL_TRANSCRIPT_INVALID`.

No repair was made in this review.

## Initial ImportError qualification

The first targeted command invoked a `/tmp` script normally. Python placed `/tmp`, not the repo, on `sys.path`, so import failed before acceptor execution:

```text
/Users/um-yunsang/argo-paper-orx/.venv-sab/bin/python -B /tmp/a2_acceptance_user_prompt_control.py
```

```text
Traceback (most recent call last):
  File "/tmp/a2_acceptance_user_prompt_control.py", line 3, in <module>
    from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_acceptance import CombinationAcceptanceTests
ModuleNotFoundError: No module named 'experiments'
```

This is setup failure only. It is **not** behavioral RED and is not used as finding evidence. The valid falsification used `python -c` so the repository cwd remained on the normal import path. The temporary script was deleted.

## Passing areas

The following remain strong source/mock evidence:

- normal and synthetic configs use full production environment/caps and normalize equal except frontend path/identity;
- exact normal/Faux/process-exec source hashes are bound;
- process receipt uses shared validators, exact integer return code 0, matching handles/resource values, confirmed cleanup, bounded stdout/stderr;
- current session parser requires exact provider/model/session, two ordered nonempty response IDs, all four positive usage categories, and total below 120000;
- tool call/result wire is strict, including fixed ID/name/empty args, exact result keys/details/nonerror, strict two-DONE-dev public body, and correct gate envelope hash;
- latest-gate interface requires exact READY decision/checkpoint/session identity and public/research view hashes; missing gate is not manufactured;
- metadata is exact and never used as response or usage proof;
- six SourceTrees are pairwise disjoint and reverified through the mock interface;
- artifact census is descriptor-relative, regular/single-link and bounded; and
- `assess_combination` writes nothing and converts failures to typed `NOT_ADMITTED`.

## Coverage and nonclaims

- Positive fixtures use a mock Bridge config and mock `verify_tree` / `_latest_gate`; no actual gate history, Bridge loader, source traversal, or process lifecycle runs.
- The author's missing-module and withheld-anchor failures are correctly non-behavioral and were not reused as RED.
- Typed metadata is not native proof. The Faux source/schema anchors do not prove provider transport, native response IDs, or usage.
- The dev-view digest is only gate-bound 64hex, as explicitly permitted. No independent target regrade is claimed.
- No driver/writer change is reviewed. Production completion, OAuth/provider, current-response resource behavior, and P0 remain held.

## Prohibitions

No source, test, report, or driver under review was edited. No publication API, Prime/Faux registration/stream, process, fixture, Bridge, Git, socket, ORX, Docker, auth, data, model, or P0 ran. No npm, commit, or nested worker was used.
