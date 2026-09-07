# HousePrice Option A2 namespace-validator addition independent review v1

## Decision

**SCOPED PASS: only `controller_deployment.py` was added to the production namespace allowlist.**

No new finding was identified in this one-member delta. The exact new module name is admitted, while the named test helper, combination driver, and lookalike module remain denied. All ten prior deployment/bootstrap behaviors remain green, for 11/11 synthetic tests.

This is not actual namespace materialization or P0 admission. It ran no bootstrap, controller, provider/auth, ORX, Docker, task data, native change, npm, or actual P0.

## Frozen inputs

| File | Bytes | SHA-256 | Validation match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/deployment_assets.py` | 7508 | `2087db073f9c10f3cb7264fc1dda1df2e31a7cdfb6671af0fce537720b3faccc` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_deployment_assets.py` | 11416 | `2c2b7bdadc00eb70e680926cda25eacaf7a97f2274e9fe1a2393d4930e7d54b2` | yes |

Both files were read in full. The before/after snapshots and RED/GREEN logs were also read in full.

Contracts and dependency intake:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-driver-validator-dependency-v1.json` — `2a638ace16b277c764e5deef4f9c536563092349b0b9f554ce6d2826c4fb2630` (1507 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-namespace-validator-addition-v1.json` — `8404bbffdca56bacbeda220ae14173d2ee9b55736ec543f00b538a1a5afaa8fa` (1173 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-controller-deployment-independent-review-v2.json` — `2d9169c40dd379517bd5409f18e70c6fbea6454c22105806e6d3d8a575732f07` (8856 bytes), scoped controller-deployment 13-test PASS at `controller_deployment.py` hash `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`.

## Delta review

Location: `deployment_assets.py:17-22`.

The complete source change is one allowlist element:

```diff
-    "bridge.py",...,"controller_process.py",
+    "bridge.py",...,"controller_process.py","controller_deployment.py",
```

Because `MEMBER_PATHS` is derived from `RUNTIME_NAMES` under the fixed runtime prefix, this admits exactly:

```text
experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller_deployment.py
```

It does not add a module to the executable bootstrap `MODULES` set. It grants no import-time execution by `deployment_assets`; it only permits the root caller to copy a separately bound regular file into the sealed namespace.

The test delta adds one method. Its positive case materializes the exact new relative path and confirms copied bytes and the expected one-member-plus-four-initializers file count. Its negatives prove these names remain outside `MEMBER_PATHS`:

- `test_bridge.py`;
- `a2_combination_driver.py`;
- `controller_deployment_extra.py`.

All other non-allowlisted names remain denied by exact set membership. No wildcard, prefix, suffix, or substring admission was introduced.

## Failing-first evidence

All six archive files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-namespace-validator-addition-v1` matched the validation hashes:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `01-new-member-red.log` | 4049 | `09d80240619d2cd48afe0336acd8374deb1cbb85552fd9183e11144ecb620180` |
| `02-eleven-green.log` | 2907 | `e42191742385f38bf5da2b49365b9e7da6b99bc8ababb93d90cba439cda13753` |
| `deployment_assets.py.before.snapshot` | 7481 | `e0a881f75cbb48a051028c1d64896ec8dbcfe6657a3411119e39627c4392e9ac` |
| `deployment_assets.py.snapshot` | 7508 | `2087db073f9c10f3cb7264fc1dda1df2e31a7cdfb6671af0fce537720b3faccc` |
| `test_deployment_assets.py.before.snapshot` | 10741 | `667efea0e99559b7615e9cc7dc802dfba686d512e9dea96b272fe1a784505ea1` |
| `test_deployment_assets.py.snapshot` | 11416 | `2c2b7bdadc00eb70e680926cda25eacaf7a97f2274e9fe1a2393d4930e7d54b2` |

- Old source RED: the exact `controller_deployment.py` member raised `DeploymentError`; the other ten tests passed.
- Repaired GREEN: the new member passed and the three negative names remained rejected; all 11 tests passed.
- Source before/after differs only by the one allowlist string. Test before/after differs only by the one focused test.

This is genuine behavioral RED for the required dependency addition, not an import or collection failure.

## Exact independent execution

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets
test_bootstrap_and_config_must_stay_outside_sealed_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_bootstrap_and_config_must_stay_outside_sealed_namespace) ... ok
test_changed_tree_interpreter_or_module_does_not_publish_bootstrap (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_changed_tree_interpreter_or_module_does_not_publish_bootstrap) ... ok
test_generated_bridge_failure_is_fixed_json_and_nonzero (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_bridge_failure_is_fixed_json_and_nonzero) ... ok
test_generated_gate_maps_preexec_failures_without_private_text (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_gate_maps_preexec_failures_without_private_text) ... ok
test_generated_gate_refuses_replaced_directory_with_safe_stop (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_generated_gate_refuses_replaced_directory_with_safe_stop) ... ok
test_inside_namespace_config_does_not_publish_or_change_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_inside_namespace_config_does_not_publish_or_change_namespace) ... ok
test_materializes_exact_regular_namespace_and_never_overwrites (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_materializes_exact_regular_namespace_and_never_overwrites) ... ok
test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments) ... ok
test_namespace_admits_only_the_new_shared_validator_not_test_helpers (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_namespace_admits_only_the_new_shared_validator_not_test_helpers) ... ok
test_partial_copy_is_retained_and_cannot_be_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_partial_copy_is_retained_and_cannot_be_retried) ... ok
test_rejects_bad_source_identity_and_noncode_namespace_members (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_rejects_bad_source_identity_and_noncode_namespace_members) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.198s

OK
EXIT_CODE=0
```

Result: 11/11 Python 3.11 synthetic mock tests passed. The test used fabricated source bytes and did not import or execute `controller_deployment.py` from a materialized namespace.

## Preserved controls

- `materialize_namespace` still accepts only exact names from `MEMBER_PATHS`, with duplicate rejection and 1 MiB/member, 8 MiB aggregate bounds.
- Supplied bytes are reopened through `FileBinding`, written as new `0600` regular files, and included in the rederived whole-tree count/digest.
- Test/data/auth/helper names remain outside the namespace unless explicitly enumerated as production modules.
- DA-001 output/config disjointness and the later held-directory/bootstrap safe-failure behaviors remain green in the 11-test suite.
- Bridge and gate bootstraps remain the only admitted bootstrap modules. Adding the validator as a namespace member does not make it an executable entrypoint.

## Authority and limits

1. The root caller must bind the exact reviewed `controller_deployment.py` bytes at hash `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`. This allowlist change alone is not member-hash authority.
2. The caller must materialize the full exact dependency set and rederive the entire namespace `SourceTree`. The one-member synthetic test is only allowlist mechanics.
3. The controller-deployment review remains its own authority for `_revalidate_frontend_deployment`; this review does not re-review that 19,605-byte module.
4. Prior deployment-assets reviews remain unchanged:
   - `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-independent-review-v1.md` — `1121cfb5827b0c46f977214f7cb328726801b52a8d531d5ed1863ce8bfef76f7`
   - `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-independent-review-v1.json` — `2d237dc1c6494251738933d11b5891f7c9fe4312b1e13e4568232702b55b2103`
   - `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-independent-review-v2.md` — `de238642c7253a4c39aeebd7990a77b2c9f36b7c7d114e6be6518f9b3a14717d`
   - `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-independent-review-v2.json` — `1f82a6d7b661a47ebfc27b3278c172e0e299ff4e931543277172393531e4c711`
5. No actual bootstrap/namespace/controller/provider/auth/ORX/Docker/data or P0 ran. Full combination, OAuth, immutable production receipts, and actual P0 remain pending.
