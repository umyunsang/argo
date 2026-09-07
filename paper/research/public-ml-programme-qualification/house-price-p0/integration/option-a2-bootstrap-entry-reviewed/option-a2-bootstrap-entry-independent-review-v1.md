# Independent review: A2 bootstrap entry safety v1

## Decision

**SCOPED PASS.** The held-descriptor/fchdir successor closes the CD2 source-level gap for the reviewed mock-only scope. I found no blocking defect in the two reviewed files.

This is not production admission. No actual bootstrap, `fchdir`, `execve`, frontend, controller, provider, auth, Bridge, ORX, Docker, task data, or P0 ran.

## Reviewed authority and bytes

| Item | Bytes | SHA-256 |
|---|---:|---|
| `option-a2-bootstrap-entry-safety-v1.json` | 1,781 | `751ca0d4a579eaff7068c143b99ea5588bcfb27b6541b5265ec2ce0275d3468a` |
| `option-a2-bootstrap-entry-validation-v1.json` | 1,797 | `1e11b4e08662f60cb3d676f1fa06456c6d1073d1f32c72c9e8c73872e42916e1` |
| `deployment_assets.py` | 7,481 | `e0a881f75cbb48a051028c1d64896ec8dbcfe6657a3411119e39627c4392e9ac` |
| `test_deployment_assets.py` | 10,741 | `667efea0e99559b7615e9cc7dc802dfba686d512e9dea96b272fe1a784505ea1` |

Both current files equal the snapshots in `integration/option-a2-deployment-assets-v3-bootstrap`. The DA001 v2 archive remains unchanged (`bad8dd...f09` source, `88e95a...cc3` test), and its independent seven-test decision remains `SCOPED_PASS_DA001_RESOLVED`.

## Review results

### BE01 — held namespace identity: PASS

The generated entry opens the namespace with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW`. It checks the held descriptor is a directory with mode 0700 and exact recorded uid, device, and inode before changing cwd (`deployment_assets.py:127-133`). The replacement fixture renames the original namespace, creates another directory at the same name, and proves the generated gate emits only `STOP_PROTOCOL_INVALID` and never calls `execve`.

### BE02 — fchdir, not pathname chdir: PASS

Generated source calls `os.fchdir(descriptor)` and never `os.chdir` (`:133`). The success mock verifies `fchdir` exactly once and `chdir` never (`test_deployment_assets.py:61-65`). This avoids re-resolving the namespace name after the held descriptor identity check.

### BE03 — descriptor closed before exec: PASS

`fchdir` is inside `try/finally`; `os.close(descriptor)` precedes `os.execve` (`deployment_assets.py:128-136`). The success test reads the descriptor passed to `fchdir` and proves `os.fstat` already raises `OSError` before checking the mocked exec call (`test_deployment_assets.py:65-69`). Unexpected exec return is explicitly converted to failure.

### BE04 — fixed exec and four-key environment: PASS

Generation accepts only the exact Bridge or phase-gate module. It requires the pinned venv invocation, re-captures the interpreter identity, verifies the SourceTree, and reopens the config FileBinding. The emitted argv is exactly:

```text
<venv-python> -B -m <fixed-module> --config <fixed-absolute-path> --config-sha256 <fixed-hash>
```

The exec environment is exactly `LANG`, `LC_ALL`, `PATH`, and `TZ`. Tests compare all argv and environment values. There is no shell, interpolation, inherited environment, `PYTHONPATH`, `sys.path`, provider, model, or tool/action input.

### BE05 — unexpected arguments: PASS

The generated entry checks `len(sys.argv) == 1` before opening the namespace. The gate extra-argument mock proves no exec, fixed `STOP_PROTOCOL_INVALID`, and exit 0 (`test_deployment_assets.py:70-74`). Bridge uses the same generated guard with its fixed Bridge envelope.

### BE06 — fixed exception envelopes: PASS

The code catches `Exception` around argument validation, open/fstat/fchdir/close/exec and unexpected exec return. It prints only a compile-time constant:

- gate: `STOP_PROTOCOL_INVALID`, exit 0;
- Bridge: `{"error":"INTERNAL_ERROR","ok":false}`, exit 1.

The open, fchdir, and exec gate faults contain a private synthetic exception string, yet exact output contains none of it. The Bridge exec failure parses to exactly the safe object. No arbitrary exception, path, config, or namespace content is formatted.

### BE07 — DA001 and no-overwrite preservation: PASS

Bootstrap output and config equal to or lexically beneath the namespace remain rejected before publication. Generation still reopens the config, rederives the interpreter, verifies the SourceTree, uses `O_EXCL | O_NOFOLLOW`, completes full-write/fsync, and refuses overwrite. The predecessor archive supplies the independent DA001 evidence.

### BE08 — protocol surface: PASS

Bootstrap selects only two fixed module identities and adds no model-callable action. The six-action protocol stays in the unchanged Bridge module. No discovery/provider/runtime tool is introduced.

## Test execution

Command:

```text
/Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets
```

Cwd: `/Users/um-yunsang/argo-paper-orx`  
Exit: `0`  
Duration: `0.287794` seconds  
Tests: 10

```text
test_bootstrap_and_config_must_stay_outside_sealed_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_bootstrap_and_config_must_stay_outside_sealed_namespace) ... ok
test_changed_tree_interpreter_or_module_does_not_publish_bootstrap (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_changed_tree_interpreter_or_module_does_not_publish_bootstrap) ... ok
test_generated_bridge_failure_is_fixed_json_and_nonzero (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_bridge_failure_is_fixed_json_and_nonzero) ... ok
test_generated_gate_maps_preexec_failures_without_private_text (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_gate_maps_preexec_failures_without_private_text) ... ok
test_generated_gate_refuses_replaced_directory_with_safe_stop (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_gate_refuses_replaced_directory_with_safe_stop) ... ok
test_inside_namespace_config_does_not_publish_or_change_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_inside_namespace_config_does_not_publish_or_change_namespace) ... ok
test_materializes_exact_regular_namespace_and_never_overwrites (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_materializes_exact_regular_namespace_and_never_overwrites) ... ok
test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments) ... ok
test_partial_copy_is_retained_and_cannot_be_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_partial_copy_is_retained_and_cannot_be_retried) ... ok
test_rejects_bad_source_identity_and_noncode_namespace_members (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_rejects_bad_source_identity_and_noncode_namespace_members) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.169s

OK
```

Post-run source hashes still exactly match the reviewed inputs.

## Coverage qualifications

1. Extra-argument, replacement, and closed-fd behavior execute directly for the gate template. Bridge directly executes its fixed failure envelope. Bridge extra-argument and replacement paths share identical generated code but do not have separate cases.
2. Mocked calls prove ordering and arguments, not live kernel `fchdir`/`execve` or module lookup.
3. Bridge bootstrap exits 1 after emitting the safe JSON. The controller extension will classify the nonzero child as its fixed `INTERNAL_ERROR` rather than depend on forwarding that JSON. This remains safe but full frontend composition is outside this review.

## Residual nonclaims

- Python/site initialization occurs before bootstrap top-level guards. The venv, stdlib, site packages, shared libraries, and OS remain external TCB.
- Caller must rederive namespace and dependency bytes immediately before invocation. Generation-time `verify_tree` is not per-tool revalidation.
- The accepted no-concurrent-malicious-same-UID-mutator assumption remains. Held cwd is not fexecve/pidfd or hostile-host proof.
- Gate exit 0 on `STOP_PROTOCOL_INVALID` cannot prove readiness. Parent must independently open the latest durable typed outcome, session/provenance, and clean process receipt.
- `BaseException` is intentionally outside the handler. `SystemExit`, `KeyboardInterrupt`, stdout flush failure, and broken pipe are not claimed safe-envelope successes; absence of a durable outcome cannot admit P0.
- Production namespace allowlist, deployment/completion, full synthetic combination, OAuth, provider identity, and actual P0 remain separate gates.

## Outputs

- JSON review: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-bootstrap-entry-independent-review-v1.json`
- This review: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-bootstrap-entry-independent-review-v1.md`
