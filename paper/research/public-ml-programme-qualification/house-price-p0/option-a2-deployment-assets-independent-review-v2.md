# HousePrice Option A2 deployment-assets independent review v2

## Decision

**SCOPED PASS: DA-001 is resolved on the two frozen repair hashes.**

No new finding was identified in the DA-001 repair scope. Bootstrap output and config paths equal to or below the sealed namespace are rejected before interpreter capture, tree verification, or output publication. The new regression also rederives the unchanged `SourceTree` and proves no denied file was created.

This is not deployment or P0 admission. It used only the exact seven synthetic tests with mocked bootstrap execution. It did not run a real bootstrap, Prime, provider/auth, ORX, Docker, task data, controller process, npm, or actual P0. It did not inspect the separate changing controller-deployment, terminal-driver, or completion files.

## Frozen inputs

Repair validation: `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-repair-validation-v2.json` — `1d9750d604e6bb285b3aacc918389529d1f25913968507362861552e0bb6cb1c` (2481 bytes).

| File | Bytes | SHA-256 | Validation match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/deployment_assets.py` | 6345 | `bad8dd3555c745474bc678d5c3cc9eab66fcde874293f4687e4583f4327f9f09` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_deployment_assets.py` | 7524 | `88e95a9d1601b163d4e65de25426913c38702f259f7019255df6497c88964cc3` | yes |

Both files were read in full. Their archived v2 snapshots are byte-identical.

## DA-001 closure

Locations: `deployment_assets.py:101-111`; `test_deployment_assets.py:93-115`.

The repair derives `root = Path(namespace.root)` and rejects:

- `output == root`;
- `root in output.parents`;
- `config.path == root`;
- `root in config.path.parents`.

It also requires `config` to be a `FileBinding` with a `Path` before interpreter capture. `_new_private_path(output)` performs no write, so an in-namespace output reaches the new rejection without changing the namespace. An in-namespace config is rejected before the outside output is created.

The combined regression records all files under the namespace before both denials, proves the denied paths do not exist, compares the after-census bytes to the before-census, and calls `verify_tree` on the original `SourceTree`. The separate config regression supplied the second genuine failing-first control.

Result: the bootstrap can no longer invalidate its input namespace seal, and the config cannot violate the contract's outside-namespace layout through this helper.

## Repair evidence

All five files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-deployment-assets-v2-repaired` were read in full. Their hashes and sizes match the repair validation.

| File | Bytes | SHA-256 |
|---|---:|---|
| `01-output-inside-red.log` | 1098 | `9a683dc6d3bb9a00b27e782f2b739930b9d997561181ce79711d8483df7387b9` |
| `02-config-inside-red.log` | 1124 | `08935a26ff3f190e3a46926efa46aa6e8e4f25e07de28c4d9d02039006ca3464` |
| `03-seven-green.log` | 1894 | `fd5732d0dc1fb61664a79ef7d4a54fd11d345165631612984c6c23cc84e9ade3` |
| `deployment_assets.py.snapshot` | 6345 | `bad8dd3555c745474bc678d5c3cc9eab66fcde874293f4687e4583f4327f9f09` |
| `test_deployment_assets.py.snapshot` | 7524 | `88e95a9d1601b163d4e65de25426913c38702f259f7019255df6497c88964cc3` |

- `01-output-inside-red.log`: the old source failed the new output-disjointness test because no `DeploymentError` was raised.
- `02-config-inside-red.log`: the old source independently failed the config-disjointness test.
- `03-seven-green.log`: all seven tests passed after the narrow source repair.

The old reviewed source and v1 review remain preserved under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-deployment-assets-v1-reviewed`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `deployment_assets.py.snapshot` | 6114 | `f92db31b687388a7b05a68eea3cf07347dc789cdfd09f1d568c0c0175083775b` |
| `option-a2-deployment-assets-independent-review-v1.json` | 13493 | `2d237dc1c6494251738933d11b5891f7c9fe4312b1e13e4568232702b55b2103` |
| `option-a2-deployment-assets-independent-review-v1.md` | 11115 | `1121cfb5827b0c46f977214f7cb328726801b52a8d531d5ed1863ce8bfef76f7` |
| `test_deployment_assets.py.snapshot` | 5943 | `5ec7b0484fff371be255f30b0c1dcf40787bbc6da9b1027195b17b7e877d3751` |

The v1-to-v2 source diff is limited to the four path/type checks and moving `root` derivation before interpreter capture. The test diff adds only the required disjointness/unchanged-tree regressions and imports their existing verifier/limits.

## Exact independent execution

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets
test_bootstrap_and_config_must_stay_outside_sealed_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_bootstrap_and_config_must_stay_outside_sealed_namespace) ... ok
test_changed_tree_interpreter_or_module_does_not_publish_bootstrap (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_changed_tree_interpreter_or_module_does_not_publish_bootstrap) ... ok
test_inside_namespace_config_does_not_publish_or_change_namespace (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_inside_namespace_config_does_not_publish_or_change_namespace) ... ok
test_materializes_exact_regular_namespace_and_never_overwrites (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_materializes_exact_regular_namespace_and_never_overwrites) ... ok
test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments) ... ok
test_partial_copy_is_retained_and_cannot_be_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_partial_copy_is_retained_and_cannot_be_retried) ... ok
test_rejects_bad_source_identity_and_noncode_namespace_members (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_rejects_bad_source_identity_and_noncode_namespace_members) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.100s

OK
EXIT_CODE=0
```

Result: 7/7 synthetic tests passed on the approved Python 3.11 kernel. The only bootstrap evaluation in the suite uses mocked `os.chdir` and `os.execve`; no child process ran.

## Preserved passing controls

The v1 passing controls remain unchanged:

- new private namespace and `O_EXCL` no-overwrite behavior;
- frozen member-name allowlist, duplicate rejection, 1 MiB/member and 8 MiB aggregate caps;
- source `FileBinding` reopening and post-copy whole-tree capture/counts;
- four empty package initializers and no test/data/auth namespace members;
- partial namespace retention/no retry;
- fixed interpreter identity, exact Bridge/phase-gate modules, config reopening;
- fixed `-B -m` argv, exact four-key environment, top-level stdlib-only bootstrap, and unexpected-argument rejection;
- successful full-write/fsync and executable `0700` bootstrap receipt.

## External conditions and nonclaims

1. The caller still binds the approved exact relative-path-to-source-hash member manifest. The helper verifies supplied bindings; it does not prove caller approval.
2. The caller keeps the namespace outside public/model/source/auth/artifact roots and rederives the namespace and installed Prime tree before import.
3. The root-private no-malicious-concurrent-same-UID TCB remains. This is not `fexecve`/pidfd, hostile-host, or whole-OS proof.
4. The historic Python 3.9 collection failures remain non-RED. The repaired RED/GREEN evidence is synthetic and does not prove a live bootstrap or provider path.
5. Controller-deployment, terminal/completion, full combination, immutable production receipts, OAuth, and actual provider identity remain separate pending gates. Live P0 remains held.
