# Episode preparation utility

Implemented `experiments/argo_study_20260909/prepare_episode.py` and its focused `test_prepare_episode.py`. **9 synthetic tests passed**. No real episode was prepared, real custody rows read, model called, scientific training run, ORX node created or native source changed in this lane.

Root invokes the following only after choosing the parent and pinning the flat apparatus snapshot:

```sh
/opt/homebrew/bin/python3 experiments/argo_study_20260909/prepare_episode.py prepare \
  --episode-id dev-b0-task37-r1 --arm B --candidate-id B0 --task-id 37 \
  --parent-experiment-id PARENT_UUID --code-root ABSOLUTE_FLAT_APPARATUS_DIRECTORY
```

Supported current task IDs are37,146820,31,146821; B accepts onlyB0 and R onlyR0. The code directory must contain controller.ts, model_meter.ts, runner.py, scientific_bridge.py, candidate_entry.py, scoring.py, kernel_wrapper.py, plus prompts/common.md, B0.md, R0.md and manifest.json. It has no ambiguous repository-layout fallback. The utility emits a config path/hash, private preparation-receipt path/hash and code-file hashes; row values and credential contents are never output.

A fresh episode is created under `~/.local/share/argo-study-20260909/episodes/<id>/`. Existing episode paths are refused and their files are preserved. Directories are0700 and initial files0400. Its initial structure is:

```text
episode/
  workspace/  inner_train.csv, public.json, TASK.md
  artifacts/  initially empty; native session/kernel/harness state
  control/
    episode.json, kernel.json, preparation-receipt.json
    common.md, policy.md, task-prompt.md
    corpus/   five immutable method excerpts
    scientific/  initially empty; bridge/model/controller private receipts
```

The worker receives only supervised inner-training data and a six-field public schema. Supervised targets inside inner_train.csv are necessary and allowed. No dev/test label files, outer_train, dev/test feature files, row_identity, original source files or full custody metadata are copied into either public mount. The existing auth path is checked as a file reference without opening or copying its contents. Host prompts and corpus remain unmounted and are exposed only through the controller's existing prompt/read_corpus interfaces.

Metadata is referenced at `custody/task_<id>/metadata.json`. Its hash must match the trusted current data-custody summary, and task/data version/allocation must match the development roster. The inner_train hash, header, row count and integer target schema are checked before output creation. Public schema contains exactly target_column, feature_columns, numeric_columns, categorical_columns, class_mapping and classes. The common/B0/R0 prompt manifest is checked. Code hashes are measured for the supplied snapshot; root separately confirms those identities before freezing and launching.

The combined episode config carries all current controller and bridge fields. Native artifacts are the episode/artifacts sibling; private_artifact_dir is episode/control/scientific, as required by the bridge. Project ID is c9443332-b7f0-40db-9f5d-68b7cf4f4bff, projectPath is the privateorx-project under the study root, and the fixed command is `/opt/homebrew/bin/python3 runner.py`. Family ledgers are referenced at ledgers/B.json or ledgers/R.json and are not initialized or modified by this utility.

Limits are80000 normalized model tokens,1.5M family tokens,$45 family budget, deadline=preparation time+5400seconds, shared2CPUs/8GiB/7200CPU-core-seconds, feedback12 and final refit1. Kernel image is sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c. The default kernel share is0.5CPU/512MiB, matching the existing wrapper/bridge pool.

TASK.md explains fit(train_X, train_y, frozen_config), predict(X), exact class/row alignment, serialization across fit/predict containers, source/config submission and host feedback/locking tools. The controller's initialize registers the RF100 default and consumes its first feedback slot; the preparation utility does not create or fit another baseline and does not invent a default solution.py. A changed solution.py is authored by the evaluated agent. The registered default remains selected if no replacement is locked.

Method-only excerpts are copied from the existing hash-pinned five-anchor texts: Prime131–293, HoH285–430, Scroll274–352, HarnessDev200–227, RecEvolve180–269. These ranges were read directly. Prime's Evaluation heading294 and dangling/incomplete adjacent sections are omitted. Scroll's method-interface table is retained; evaluation tables are excluded. Source hashes, exact ranges, excerpt hashes and sizes appear in each preparation receipt. Every excerpt is at most24000bytes for read_corpus.

Verification used `/opt/homebrew/bin/python3 -B -m unittest -v test_prepare_episode.py` from the apparatus directory:9/9 PASS in0.094seconds. Fixtures use only synthetic train/hidden/auth/prompt/corpus placeholders. Tests check the actual kernel configuration loader, static bridge dataclass field parity, B/R shared corpus access, no auth reads, public/private separation, no-overwrite, metadata/train/prompt/source hash mismatch rejection, header/row-ID exclusion, path/task/arm rejection, and CLI output redaction. No Docker process or live bridge operation is invoked.

This qualifies preparation and configuration behavior, not a scientific run. Root must initialize family ledgers separately, verify code/config hashes, choose and commit the ORX episode spec, then launch. Prepare immediately before admission because its deadline starts at preparation and is not extended. A filesystem failure after claiming the fresh directory can leave a partial episode; subsequent calls refuse to overwrite it and root must inspect that partial state.
