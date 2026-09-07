# HousePrice Option A2 deployment-assets independent review v1

## Decision

**NEEDS ONE NARROW REPAIR before deployment integration.**

One P2 contract defect remains: `write_module_bootstrap` can place the bootstrap inside the namespace it just verified, which immediately invalidates the returned `SourceTree`. The five supplied synthetic tests pass, and the other reviewed deployment controls are sound within their stated root-private TCB.

This review used no actual bootstrap execution, Prime/provider/auth, ORX, Docker, task data, controller process, npm, source edit, commit, or actual P0. It did not inspect the changing terminal-driver/completion files. Native construction remains paused and live P0 remains held.

## Hash-bound inputs

| File | Bytes | SHA-256 | Expected match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/deployment_assets.py` | 6114 | `f92db31b687388a7b05a68eea3cf07347dc789cdfd09f1d568c0c0175083775b` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_deployment_assets.py` | 5943 | `5ec7b0484fff371be255f30b0c1dcf40787bbc6da9b1027195b17b7e877d3751` | yes |

Contracts and receipts read in full:

| File | Bytes | SHA-256 |
|---|---:|---|
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-regular-namespace-deployment-v1.json` | 3384 | `b4c62f28de89db1f3071413f0a8f1699973f5a81343b94517fcfbaf45073feed` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-scope-v1.json` | 1401 | `d8e858266a91b9d0e072fb768069365db10476831114c9b8e574a22a0d317695` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-final-intake-v1.json` | 2176 | `3c9f2139ad484af4c24403f86b1fcea4bf1a958ecc0a96ba57c3c5c37b400afc` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-validation-v1.json` | 1894 | `fc39cade5c3ecb3648dde37edf70c44cd142ff6c7fc8656ecc301adc0696d807` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-deployment-assets-mutation-controls-v1.json` | 2246 | `c65f622418a7b224e1681541725402b342a7214752a5e9613c801eaee03d070d` |

## Finding

### DA-001 — P2 — bootstrap output is not required to be outside the sealed namespace

Locations: `deployment_assets.py:39-48,98-120`.

The contract requires gate and Bridge bootstraps outside the namespace to avoid changing the namespace after its source tree is sealed. `write_module_bootstrap` knows both `output` and `namespace.root`, but it does not compare them.

For `output = Path(namespace.root) / "gate-entry"`:

1. `_new_private_path(output)` accepts the canonical, root-owned `0700` namespace as the parent.
2. `verify_tree(root, namespace, LIMITS)` passes before the write.
3. `_write_new(output, data, 0o700)` adds the bootstrap beneath `root`.
4. The function returns a successful `FileBinding`, but the supplied `SourceTree` is now stale and the namespace contains an undeclared extra file.

The same missing disjointness check permits `config.path` to refer inside the namespace, although a correctly reviewed config/module manifest should prevent that configuration externally.

Required repair:

- Before interpreter capture or tree verification, reject `output == root` and `root in output.parents`.
- Enforce the contract's config disjointness too: reject `config.path == root` or `root in config.path.parents`.
- Add a regression that requests an in-namespace bootstrap and proves no output was created and the original tree still verifies. Add the analogous config-path negative if the helper, rather than the deployment caller, owns that invariant.

No mutation was executed for this finding because the review instruction allowed only the exact five-test command. The control flow above follows directly from the frozen code and the explicit outside-namespace contract.

## Passing controls

- `materialize_namespace` accepts only 1–128 tuple members with unique frozen allowlisted relative paths.
- Each supplied source is reopened through `read_bound` with a 1 MiB cap. Aggregate bytes are capped at 8 MiB before destination creation.
- Destination, package directories, empty `__init__.py` files, and source modules are newly created. Files are regular; namespace capture rejects symlinks, hardlinks, and special entries. Existing destinations are not overwritten.
- Package/file counts are checked against the supplied member count. Partial namespace evidence remains and prevents retry in the same filesystem state.
- Bootstrap output uses a new `0700` regular file under a canonical root-owned `0700` parent outside a Git worktree.
- Interpreter invocation path is fixed. Its identity is recaptured and compared before generation.
- Namespace bytes are rederived before bootstrap generation. Only the exact Bridge or phase-gate module names are admitted.
- Config bytes are reopened through their `FileBinding` before the fixed argv is generated.
- Generated source has only top-level `os`/`sys` imports, rejects any script argument, changes to the sealed namespace, and calls `os.execve` with the fixed `-B -m` argv and only `LANG`, `LC_ALL`, `PATH`, and `TZ`.
- The bootstrap full-write loop handles short writes and fsyncs successful files/directories. `O_EXCL` blocks overwrite.

## Qualification evidence

All 14 archived evidence files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-deployment-assets-v1` were read in full.

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `01-system39-collection-fail.log` | 2374 | `2d623951b12ccc156717c6631600a8c9cd76c78dcd68d56e95a09c88cbd9393e` |
| `02-system39-collection-fail.log` | 2374 | `2d623951b12ccc156717c6631600a8c9cd76c78dcd68d56e95a09c88cbd9393e` |
| `03-native311-stub-negative.log` | 5546 | `272d168aeb217fe5b0d98e1eca95e1e26bc9b1443002b79279b91de1215b96b7` |
| `04-native311-green.log` | 1384 | `575f2a554dc7dd038b3a6b27cf906e6fae821a7ca3e4e5346996eeade253346e` |
| `05-native311-final-green.log` | 1384 | `6337c748c60b663ebdba840eb82d2d91456c2f2793f955cc30af819587562933` |
| `bootstrap-arg-guard-omitted.log` | 2305 | `7bf246da245ce063162743a6abcb96e155ed39b02ca886185b16664b8438f7f8` |
| `bootstrap-arg-guard-omitted.py.snapshot` | 6101 | `2889161049ce99484c82d796c90a1f97e4f2ad79a2d67f5679d562ec5c919f93` |
| `deployment_assets.py.snapshot` | 6114 | `f92db31b687388a7b05a68eea3cf07347dc789cdfd09f1d568c0c0175083775b` |
| `source-hash-omitted.log` | 2224 | `0e910cd285b7581fabd1c41244d34d794cbea70605574ab54ddf301e0f26b8a0` |
| `source-hash-omitted.py.snapshot` | 6112 | `e7d7f05e57720bf8c293f363d94bc27a28a33c96fccd982387e1e156a64d8077` |
| `test_deployment_assets-v2.py.snapshot` | 5943 | `5ec7b0484fff371be255f30b0c1dcf40787bbc6da9b1027195b17b7e877d3751` |
| `test_deployment_assets.py.snapshot` | 5925 | `60b3e2c3eca4a0953eee7145bffdc81c827f94dbf01ce56ee715c5946efedcc9` |
| `tree-verify-omitted.log` | 2277 | `d9e5a1ca8f087f2198032d0b19721033172a68f6fd5b8fef27187e2f6921f3d2` |
| `tree-verify-omitted.py.snapshot` | 6135 | `0d94452db60f412faaeda953ccff4701508d3c375cb503f14b6b1d0a93392f69` |

Evidence interpretation:

- `01` and `02` are Python 3.9 collection failures in `controller_process.py`. They are not functional RED evidence for deployment assets.
- `03` is an isolated Python 3.11 empty-stub witness. It shows the tests reject an unimplemented helper, but it is not a true before-edit functional RED.
- The three retrospective omission mutants are honest targeted qualification. Removing source hash reopening, tree verification, or the bootstrap argument guard causes exactly one relevant test failure. Their source and log hashes match the mutation receipt.
- `04` is the intermediate five-test green with the earlier test hash. `05` and the final intake bind the final test hash `5ec7b0484fff371be255f30b0c1dcf40787bbc6da9b1027195b17b7e877d3751`.

The existing mutants do not cover DA-001.

## Exact allowed test execution

Kernel:

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python --version
Python 3.11.15
```

Command:

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets
test_changed_tree_interpreter_or_module_does_not_publish_bootstrap (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_changed_tree_interpreter_or_module_does_not_publish_bootstrap) ... ok
test_materializes_exact_regular_namespace_and_never_overwrites (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_materializes_exact_regular_namespace_and_never_overwrites) ... ok
test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_module_bootstrap_uses_fixed_exec_and_environment_not_inherited_arguments) ... ok
test_partial_copy_is_retained_and_cannot_be_retried (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_partial_copy_is_retained_and_cannot_be_retried) ... ok
test_rejects_bad_source_identity_and_noncode_namespace_members (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_deployment_assets.DeploymentAssetsTest.test_rejects_bad_source_identity_and_noncode_namespace_members) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.077s

OK
EXIT_CODE=0
```

Result: 5/5 synthetic mock tests passed. The bootstrap body was compiled and evaluated only with mocked `os.chdir` and `os.execve`; no child process was executed.

## External integration conditions and nonclaims

These are not additional findings in the two reviewed files:

1. The root caller must bind the exact reviewed relative-path-to-source-hash member manifest. `NamespaceMember` plus `read_bound` verifies supplied bindings; it does not establish that the caller supplied the approved hash for each name.
2. The root must keep namespace, bootstraps, config/state, public cwd, session, profile, artifact census, and source directories disjoint and must rederive the namespace and installed Prime tree before process imports.
3. `InterpreterIdentity` and `read_bound` are existing dependencies outside this narrow review. Their real production identities remain root fan-in obligations.
4. The regular-file namespace is root-private and assumes no malicious concurrent same-UID mutator. It is not `fexecve`/pidfd, hostile-host, or whole-OS isolation.
5. The early Python 3.9 failures confer no behavioral confidence. The original tests and mutants are synthetic. No real bootstrap, provider response, OAuth, or scientific run was exercised.
6. Completion/terminal driver, full combination, immutable deployment receipts, and OAuth remain pending. Actual P0 remains blocked.
