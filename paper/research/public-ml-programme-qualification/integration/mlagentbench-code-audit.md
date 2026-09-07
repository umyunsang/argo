# MLAgentBench pinned-public-code audit

## Decision

**Single proposed P0 source: `MLAgentBench/benchmarks/cifar10`. Status: `NOT_CERTIFIED`; no run is authorized.**

CIFAR-10 is the only one of the three fully reviewed candidates whose declared task path does not invoke an account credential or consent flow. It also has a complete from-scratch starter, five starter epochs, a task cap of ten epochs, and CUDA-or-CPU selection. These code traits make it the best account-free, small-compute-shaped *source*. Live access, data rights, exact data bytes, CPU/GPU cost, baseline score, improvement headroom, and any G-arm benefit remain `NOT_VERIFIED`. [C1: `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` L1-L1] [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [C8: `MLAgentBench/benchmarks/cifar10/env/train.py` L7-L31]

The source task is unusable as-is for hidden selection: editable `train.py` loads scorer-test labels and prints test accuracy every epoch. The upstream runner has no immutable one-artifact lock. The proposal therefore reuses only the task idea, baseline structure, probability output shape, and top-1 metric concept. It does **not** certify the upstream preparation, environment, executor, or scorer as a trusted boundary. [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [C4: `MLAgentBench/benchmarks/cifar10/env/train.py` L51-L94] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15] [G13: `MLAgentBench/environment.py` L339-L371] [G15: `MLAgentBench/eval.py` L69-L129]

Current authority permits apparatus code and local static mocks, but no specific scientific run, data/scorer/runtime gate, or native change. This artifact is document-level qualification only. [A1: `paper/research/public-ml-programme-qualification/effective-authority-v1.json` L18-L31] [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]

## Scope and method

- Static, read-only inspection of the pinned source directory.
- Fully read the repository README/license, task discovery, requirements/install surface, environment, actions, runner, scorer, and agent selection behavior.
- Fully read preparation, task description, starter training code, scorer, and read-only list for `cifar10`, `house-price`, and `spaceship-titanic`.
- Did not read historical logs, result JSONs, result figures as evidence, dataset payloads, payload labels, `answer.csv`, or model payloads.
- Did not use network, download, install, import the project, execute source, test, evaluate a submission/model, or spawn another agent.
- `ACTUAL_CODE_FACT` means the cited bytes say it. `NOT_VERIFIED` marks runtime, data, access, license, performance, or compute claims not established by this static audit.

## Source-manifest binding

- Manifest: `paper/research/public-ml-programme-qualification/pinned-public-code-manifest-v1.json`
- Manifest SHA-256: `07c9820a59d4217c8f94c0613a677593d486931899d55ddd40d18980423715a8`
- Repository: `snap-stanford/MLAgentBench`
- Commit: `5d71205cc20a8e95d43aa7cb7120e89ca3323e31`
- Tree: `1e751b8483ed9f3f01b2dd6473dc2e00c691d2d0`
- Archive SHA-256: `db86702c1366338b517d3c4ee729ecec14a22455126a18022fc759258e0ad66b`
- Local source: `/Users/um-yunsang/.cache/argo-research/public-ml-source/MLAgentBench-5d71205cc20a8e95d43aa7cb7120e89ca3323e31`
- Manifest declares `388` verified files. This lane recomputed SHA-256 for all `38` source files it fully read; `38/38` matched the manifest. Git blob SHA-1 values below are manifest values and were not independently recomputed in this lane. [M1: `paper/research/public-ml-programme-qualification/pinned-public-code-manifest-v1.json` L1-L17]

## Authority and qualification contract

- Primary outcome must be the hidden score of one agent-selected artifact locked by ID/hash before hidden scoring. No-lock, scorer failure, and score missingness need separate predeclared handling. [A2: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L69-L82]
- P0 task/source-data/generator ancestry is development-side and must be excluded from P2. P0 must also record latency, UNKNOWN/BLOCKED, gate, bypass, lock, scorer, and cost denominators rather than turn unobserved values into zero. [A3: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L105-L118]
- Public/shared contamination is not proof of clean-task generalization. It can at most support a policy contrast in the declared contaminated task population under a valid matched/randomized design. [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158]
- Actual P0 still needs exact task/code/prompt/environment/command/selection/analysis/numeric-envelope review and separate user execution approval. [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]

## Registry and common harness findings

1. `tasks.json` is not a complete curated registry. It contains only `debug -> cifar10`; `get_task_info` also accepts any benchmark directory with `env/`. Filesystem presence is not qualification. [G6: `MLAgentBench/benchmarks/tasks.json` L1-L6] [G7: `MLAgentBench/prepare_task.py` L15-L35]
2. Upstream intends `env/` to be visible and `scripts/prepare.py`/`eval.py` hidden. The environment runs preparation in the benchmark tree, deletes any existing work directory, copies `env/` with symlinks, and derives read-only names from task globs. [G5: `README.md` L114-L120] [G8: `MLAgentBench/prepare_task.py` L38-L51] [G9: `MLAgentBench/environment.py` L148-L181]
3. “Read-only” protects writes only. `read_file` can read these files, executed Python can read them, `Execute Script` uses `shell=True`, and the Python REPL uses `exec`. This cannot serve as scorer/data/launch custody. [G10: `MLAgentBench/low_level_actions.py` L56-L107] [G11: `MLAgentBench/low_level_actions.py` L171-L246]
4. Each action snapshots mutable non-read-only workspace files. Runner saves `step_final_files` after exit. Core evaluation can score intermediate snapshots and the final snapshot, while scorer exceptions are suppressed. No artifact ID/hash lock is present in these paths. [G13: `MLAgentBench/environment.py` L339-L371] [G14: `MLAgentBench/runner.py` L18-L35] [G15: `MLAgentBench/eval.py` L69-L129]
5. The repo-wide dependency path is unsuitable for a small reproducible P0: it mixes broad, mostly unpinned ML/LLM/graph packages and installs CUDA/JAX stacks. A task-minimal digest-pinned environment is required. [G16: `requirements.txt` L1-L18] [G17: `requirements.txt` L25-L64] [G18: `install.sh` L9-L17]
6. The root license contains MIT software-license text with unresolved `[year] [fullname]` placeholders. No reviewed task folder contains a dataset-license/terms receipt. The software license is not treated as data authorization. [L1: `LICENSE` L1-L20]

## Candidate matrix

| Candidate | Access and license | Declared split/custody | Scorer and selection | Baseline/compute | Decision |
|---|---|---|---|---|---|
| **CIFAR-10** | `torchvision.datasets.CIFAR10(download=True)`; no credential code. Live source/hash/license `NOT_VERIFIED`; dataset rights blocked. | Official `train=True` and `train=False`; no train/dev split or seed. Test labels are loaded in editable code and test accuracy is emitted each epoch. | Top-1 argmax accuracy. No explicit schema/finiteness/probability checks. No score-free surface or artifact lock as-is. | Complete shallow 2-conv/3-linear baseline; 5 epochs, <=10 cap; CUDA-or-CPU. Time/RAM/VRAM and score `NOT_VERIFIED`. | **PROPOSE SOURCE; `NOT_CERTIFIED`** |
| **House Price** | Kaggle `home-data-for-ml-course`; credential and manual consent path. Competition terms/data rights `NOT_VERIFIED`. | Deterministic raw-train prefix 80% exposed, suffix 20% answer/test; inner `train_test_split(random_state=1)`. Public raw file reconstructs held suffix. | Positional SalePrice MAE. No explicit Id/schema/finite/missingness checks; no artifact lock. | Starter model/MAE assignments are blank. Likely CPU-shaped, but runtime `NOT_VERIFIED`. | **REJECT account-free P0** |
| **Spaceship Titanic** | Kaggle competition URL; credential and manual consent path. Competition terms/data rights `NOT_VERIFIED`. | Same deterministic outer prefix/suffix split; seeded inner shuffle/split omits one boundary row. Public raw file reconstructs held suffix. | Transported equality divided by submitted row count. PassengerId and expected row count are not explicitly validated; no artifact lock. | Feature code exists but model/accuracy assignments are blank. Likely CPU-shaped, but runtime `NOT_VERIFIED`. | **REJECT account-free P0** |

### CIFAR-10 source facts

- **Input/access:** preparation, starter, and scorer all resolve CIFAR-10 through installed `torchvision`; preparation requests both official splits with `download=True`. No task credential code appears, but exact publisher URL/archive hash/license/counts are absent from the pinned task. [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15]
- **Train/dev/test:** source declares official training and test flags, not a train/dev generator. The shuffled training loader, model initialization, and overall run have no explicit seed. [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49]
- **Custody leak:** editable `train.py` receives `(inputs, labels)` from the test loader, computes accuracy, and prints it for every epoch and at the end. The same public test split is scorer gold. Read-only `data/*` only blocks writes. [C4: `MLAgentBench/benchmarks/cifar10/env/train.py` L51-L94] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15] [C7: `MLAgentBench/benchmarks/cifar10/scripts/read_only_files.txt` L1-L1] [G10: `MLAgentBench/low_level_actions.py` L56-L107]
- **Metric:** scorer reloads CIFAR test and returns correct row-indexed argmax predictions divided by dataset length. This arithmetic is deterministic for fixed exact bytes, but the current source does not validate a task manifest, exact columns/rows/order, finite values, or probability constraints. [C5: `MLAgentBench/benchmarks/cifar10/env/train.py` L97-L106] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15]
- **Baseline and room:** code defines a shallow network with normalization-only transforms, SGD, and five epochs. The source task permits changes within ten epochs. Architecture, augmentation, optimizer, and training-policy room is visible in code, but no amount of improvement is asserted. [C1: `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` L1-L1] [C8: `MLAgentBench/benchmarks/cifar10/env/train.py` L7-L31] [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49]
- **Device/dependencies:** starter uses `cuda:0` when available and CPU otherwise; task imports `torch`, `torchvision`, and `pandas`. The broad root environment is not a task lock. [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [G16: `requirements.txt` L1-L18] [G17: `requirements.txt` L25-L64]

### House Price source facts

- Preparation requires consent and Kaggle CLI access, downloads `home-data-for-ml-course`, keeps the first 80% of raw training rows as exposed `train.csv`, and converts the suffix into scorer `answer.csv` plus unlabeled `test.csv`. [H1: `MLAgentBench/benchmarks/house-price/scripts/prepare.py` L5-L22] [G3: `README.md` L44-L57]
- The split is positional and public. Reacquiring the same competition `train.csv` and replaying these exact lines reconstructs the held labels. This audit did not acquire or inspect them. [H1: `MLAgentBench/benchmarks/house-price/scripts/prepare.py` L5-L22]
- Starter makes a seeded internal development split, but its model block and `train_mae`/`valid_mae` assignments are empty. It cannot serve as an executable frozen baseline as-is. [H2: `MLAgentBench/benchmarks/house-price/env/train.py` L7-L24] [H3: `MLAgentBench/benchmarks/house-price/env/train.py` L32-L41]
- Scorer uses SalePrice Series position and `answer.csv` to compute MAE; it does not explicitly validate Id correspondence, exact schema/rows, finite values, or typed missingness. [H4: `MLAgentBench/benchmarks/house-price/scripts/eval.py` L7-L14]

### Spaceship Titanic source facts

- Preparation links the Kaggle competition, prompts for consent, downloads via Kaggle CLI, and uses the same deterministic prefix/suffix recipe. This is not account-free and enables reconstruction by anyone with the same raw labeled file. [S2: `MLAgentBench/benchmarks/spaceship-titanic/scripts/source_code.txt` L1-L1] [S3: `MLAgentBench/benchmarks/spaceship-titanic/scripts/prepare.py` L5-L21] [G3: `README.md` L44-L57]
- The exposed training data is shuffled with `random_state=1`; its validation slice starts at `floor(0.8*N)+1`, omitting one boundary row. Model and accuracy assignments remain blank. [S4: `MLAgentBench/benchmarks/spaceship-titanic/env/train.py` L18-L44] [S5: `MLAgentBench/benchmarks/spaceship-titanic/env/train.py` L52-L69]
- Scorer compares only the `Transported` Series and divides by submitted row count. It does not explicitly verify `PassengerId`, expected row set/count/order, schema, or missingness. [S6: `MLAgentBench/benchmarks/spaceship-titanic/scripts/eval.py` L8-L16]

## Single proposed next task: adapted CIFAR-10 P0 source (`NOT_CERTIFIED`)

**Task statement:** adapt the pinned CIFAR-10 task into a bounded from-scratch image-classification P0 development instance. The research agent may iterate only on exposed train/dev evidence under the frozen `<=10` epochs per candidate plus a separately approved total trial/time/device budget. It must lock one probability submission by artifact ID and SHA-256 before exactly one scorer-held top-1-accuracy evaluation.

**Reuse boundary:** reuse the task idea, shallow starter baseline structure, probability-submission shape, and top-1 metric concept from the five pinned CIFAR files. Do not reuse upstream `prepare_task`, environment/actions, runner, or evaluation driver as authority or custody. Use the existing Prime-Agent RLM plus the separately permitted apparatus. Make no native runtime change.

**Task-source provenance:**

- `snap-stanford/MLAgentBench@5d71205cc20a8e95d43aa7cb7120e89ca3323e31`, tree `1e751b8483ed9f3f01b2dd6473dc2e00c691d2d0`.
- `MLAgentBench/benchmarks/cifar10/env/train.py` — SHA-256 `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad`
- `MLAgentBench/benchmarks/cifar10/scripts/eval.py` — SHA-256 `7c0b387a0b25c991045f2edba90cf56c13aa730a4985941ae07593afc5197e51`
- `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` — SHA-256 `b8e0a19b6d35d5e401579e30ec6947dffb47f96489c9e61ec976fe0bf83b7c39`
- `MLAgentBench/benchmarks/cifar10/scripts/read_only_files.txt` — SHA-256 `f1cffc9e04f54186b51f98bdd6866dc789a587efe29d7e2d51d4ad637bb8ac77`
- `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` — SHA-256 `19a3fe2fb03b45b14386d74fddac2806827402d0aca6a3e87bf861bc8a373559`
- Upstream data resolver: `torchvision.datasets.CIFAR10(download=True)`. Exact dataset URL/archive hash/license is absent and `NOT_VERIFIED`.
- Ancestry: `P0_DEVELOPMENT_ONLY`. The same task/source-data/generator family is excluded from P2. Public test labels make clean-task generalization unavailable even if within-run access is isolated. [A3: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L105-L118] [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158]

## Concrete blockers and least-change fixes

1. **`B1_DATA_RIGHTS` — BLOCKING**
   - Finding: No task-level CIFAR-10 data-license/terms receipt or approved asset hash exists; repository MIT text covers software documentation text but cannot be treated as dataset authorization.
   - Least-change fix: Before any acquisition, create a task asset receipt with publisher/source URL, exact archive SHA256, license/terms text/hash, permitted local research use/redistribution decision, acquisition actor/date, and user approval. Do not place data in the public engine repo.
   - Evidence: [L1: `LICENSE` L1-L20] [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [A1: `paper/research/public-ml-programme-qualification/effective-authority-v1.json` L18-L31]
2. **`B2_INPUT_REPRODUCIBILITY` — BLOCKING**
   - Finding: CIFAR source/archive resolution is delegated to whichever torchvision satisfies broad requirements; exact URL, archive hash, extracted bytes/counts, and compatibility are not pinned.
   - Least-change fix: Use a trusted preparation step outside the agent workspace. Pin task-minimal Python/wheels/container by digest, fetch once only after B1, hash the downloaded archive and each derived split artifact, and bind all hashes to the P0 protocol. Do not run the repo-wide install.sh.
   - Evidence: [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [G16: `requirements.txt` L1-L18] [G17: `requirements.txt` L25-L64] [G18: `install.sh` L9-L17]
3. **`B3_SPLIT_AND_SCORER_CUSTODY` — BLOCKING**
   - Finding: As-is editable train.py loads test labels and prints test accuracy each epoch; data/* is only protected from writes, not reads or execution.
   - Least-change fix: Expose only training labels plus a declared development split and scorer-test inputs. Keep scorer-test labels outside the agent process/workspace and remove all test-label/test-score code from the editable surface. Disable network and unapproved file access at a trusted outer boundary; the upstream read-only decorator is not sufficient.
   - Evidence: [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [C4: `MLAgentBench/benchmarks/cifar10/env/train.py` L51-L94] [C7: `MLAgentBench/benchmarks/cifar10/scripts/read_only_files.txt` L1-L1] [G9: `MLAgentBench/environment.py` L148-L181] [G10: `MLAgentBench/low_level_actions.py` L56-L107] [G11: `MLAgentBench/low_level_actions.py` L171-L246]
4. **`B4_SPLIT_PROTOCOL` — BLOCKING**
   - Finding: Source has official train/test flags but no train/dev generator/seed; model initialization and shuffled training are unseeded.
   - Least-change fix: Freeze the exact source archive, official split identity, train/dev generator algorithm/version, seed, index-list hashes, seed policy, PyTorch/DataLoader seeds, and deterministic-operation policy before P0. Report any hardware nondeterminism.
   - Evidence: [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49]
5. **`B5_PUBLIC_GOLD_CONTAMINATION` — QUALIFICATION_LIMIT**
   - Finding: CIFAR-10 scorer labels are public through the same torchvision source. Isolation can prevent within-run access but cannot prove no prior model/agent exposure or clean-task generalization.
   - Least-change fix: Declare P0 target as the observed public-known contaminated task population; record model/agent prior exposure; randomize arms on matched task instances; make this source/data/generator family development-only and exclude it from P2. Do not claim clean-task generalization.
   - Evidence: [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15] [A3: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L105-L118] [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158]
6. **`B6_ARTIFACT_SELECTION_LOCK` — BLOCKING**
   - Finding: Core runner saves mutable final/intermediate workspace snapshots. It has no single-artifact ID/hash lock, mutation check, lock deadline, or task-bound no-lock rule; intermediate scorer calls are supported.
   - Least-change fix: At a trusted apparatus boundary, require the agent to nominate exactly one eligible submission by artifact ID and SHA256 before deadline; copy it atomically to immutable scorer custody; reject byte changes; call hidden scorer exactly once; freeze no-lock/incomplete-lock/fallback handling before P0.
   - Evidence: [G12: `MLAgentBench/environment.py` L276-L282] [G13: `MLAgentBench/environment.py` L339-L371] [G14: `MLAgentBench/runner.py` L18-L35] [G15: `MLAgentBench/eval.py` L69-L129] [A2: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L69-L82] [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158]
7. **`B7_SCORER_CONTRACT` — BLOCKING**
   - Finding: CIFAR scorer computes argmax accuracy but lacks explicit manifest row/column/order, finite-value, probability, error, and missingness checks; dataset/runtime bytes are unresolved.
   - Least-change fix: Define a pure deterministic scorer over pinned data bytes. Validate exact task-manifest row IDs/count/order, exactly the declared class columns, numeric finiteness and probability constraints, and one submission only. Emit typed VALID/INVALID/SCORER_ERROR/MISSING outcomes separately from score.
   - Evidence: [C5: `MLAgentBench/benchmarks/cifar10/env/train.py` L97-L106] [C6: `MLAgentBench/benchmarks/cifar10/scripts/eval.py` L5-L15] [A2: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L69-L82]
8. **`B8_BASELINE_AND_RESEARCH_ROOM` — BLOCKING_FOR_PROTOCOL**
   - Finding: CIFAR starter is executable in code and visibly simple, but baseline performance, variance, practical runtime, a competing method space, primary contrast, and MUE are not established by this audit.
   - Least-change fix: In the task-bound protocol, freeze the baseline bytes and allowed editable surface, training-from-scratch/no-model-download rule, candidate eligibility, development metric, exact primary contrast, MUE timing/derivation, and numeric envelope. Measure baseline/variance only in a separately approved run; do not presume a G-arm benefit.
   - Evidence: [C1: `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` L1-L1] [C8: `MLAgentBench/benchmarks/cifar10/env/train.py` L7-L31] [G4: `README.md` L88-L101] [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158] [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]
9. **`B9_COMPUTE_AND_SIDE_EFFECT_BUDGET` — BLOCKING**
   - Finding: Five/ten epochs and CPU fallback make CIFAR small-compute-shaped, but actual latency/RAM/VRAM and device determinism are unmeasured; upstream paths download, delete, execute shell, and mutate caches.
   - Least-change fix: Obtain exact user approval for device, run/trial count, epoch cap, wall time, storage, network-off policy, cost, retries/repair/no-replacement, and full R1/R2/UNKNOWN census. Use isolated scratch; never run preparation in the pinned source tree.
   - Evidence: [C1: `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` L1-L1] [C2: `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` L1-L8] [C3: `MLAgentBench/benchmarks/cifar10/env/train.py` L34-L49] [G9: `MLAgentBench/environment.py` L148-L181] [G11: `MLAgentBench/low_level_actions.py` L171-L246] [G18: `install.sh` L9-L17] [A3: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L105-L118] [A4: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L123-L158] [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]
10. **`B10_AUTHORITY` — BLOCKING_EXECUTION_ONLY**
   - Finding: A specific scientific run, install target, data/scorer/runtime gate, and native changes are not authorized.
   - Least-change fix: Keep this result document-only and NOT_CERTIFIED. Submit a task-bound P0 protocol and exact arm manifest for independent review and explicit user execution approval. Use existing Prime-Agent RLM and permitted apparatus; make no native runtime change.
   - Evidence: [A1: `paper/research/public-ml-programme-qualification/effective-authority-v1.json` L18-L31] [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]

No blocker above is closed by this audit. In particular, the current authority does not supply a task, protocol, numeric budget, data asset, scorer custody, or execution approval. The next review is a task-bound P0 protocol review, not an experiment launch. [A1: `paper/research/public-ml-programme-qualification/effective-authority-v1.json` L18-L31] [A5: `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` L160-L171]

## `NOT_VERIFIED` ledger

- live URLs, account-free availability, or download success
- CIFAR-10 archive URL/hash/license/terms, record counts, or extracted bytes
- Kaggle credentials, rule consent, terms, downloads, or data bytes
- any payload row, label, answer.csv content, or model artifact
- package installation, importability, version compatibility, or scorer execution
- baseline scores, candidate scores, score variance, headroom, or G-arm benefit
- CPU/GPU wall time, RAM/VRAM, energy, or monetary cost
- runtime determinism, complete launch census, bypass coverage, or failure rates

## Exact LF evidence index

Line spans are 1-based over the exact LF-delimited bytes at the listed SHA-256. Full excerpts are preserved in the companion JSON.

| ID | Path and exact LF span | SHA-256 | Supports |
|---|---|---|---|
| M1 | `paper/research/public-ml-programme-qualification/pinned-public-code-manifest-v1.json:L1-L17` | `07c9820a59d4217c8f94c0613a677593d486931899d55ddd40d18980423715a8` | Pinned repository, commit, tree, archive, local directory, and 388-file verification declaration. |
| A1 | `paper/research/public-ml-programme-qualification/effective-authority-v1.json:L18-L31` | `9f68eb4074ec25e7b90bf63fffdc6e758e51b33ea6bb0e2a4287f3460ae8cdd2` | Apparatus and static mocks are authorized; native changes and a specific scientific run are not. |
| A2 | `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json:L69-L82` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | Primary is one agent-selected locked artifact; hidden score, lock failure, scorer failure, and missingness need task-bound rules. |
| A3 | `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json:L105-L118` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | P0 source/data/generator ancestry is development-only and P0 must measure feasibility census fields. |
| A4 | `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json:L123-L158` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | Task protocol needs exact preflight/lock/outcome rules; public contamination does not establish clean-task generalization. |
| A5 | `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json:L160-L171` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | Document-level qualification is next; actual P0 needs exact review and approval and remains unauthorized. |
| G1 | `README.md:L3-L13` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | Repository declares end-to-end agent ML tasks with repeated experimentation. |
| G2 | `README.md:L19-L28` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | Upstream setup uses editable install, Python 3.10, broad install script, and recommends sandboxing. |
| G3 | `README.md:L44-L57` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | Preparation is run per task; Kaggle tasks need API credentials and may need manual consent. |
| G4 | `README.md:L88-L101` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | Core evaluation reads log folders; trivial baseline executes train.py then submits. |
| G5 | `README.md:L114-L120` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | Upstream intends env as visible and scripts such as prepare/eval as hidden. |
| G6 | `MLAgentBench/benchmarks/tasks.json:L1-L6` | `1cd745ac76785a03fc8d1b6fb88955d72305041a470b0a8ad4060946d5caa285` | Explicit registry contains only debug -> cifar10. |
| G7 | `MLAgentBench/prepare_task.py:L15-L35` | `6ac54ff89e5e2b6c8264e500b4af73fbfb20492065053aa9e86d853824373ce0` | Unregistered benchmark directories with env folders are accepted; task text is loaded from research_problem.txt. |
| G8 | `MLAgentBench/prepare_task.py:L38-L51` | `6ac54ff89e5e2b6c8264e500b4af73fbfb20492065053aa9e86d853824373ce0` | Preparation runs scripts/prepare.py once based on a mutable scripts/prepared marker. |
| G9 | `MLAgentBench/environment.py:L148-L181` | `8780d9c8b7d15ad583fbe11e2d9013fb1e9e0902e253bd31e51ee84c6adbfe3f` | Runner deletes prior work directory, runs preparation, copies env including symlinks, and derives read-only path names from glob patterns. |
| G10 | `MLAgentBench/low_level_actions.py:L56-L107` | `e3ae15009cdcd9c8d00b160653aac1d095e7c67e54edc5790acb280886a156a9` | Read-only decorator applies to writes; read_file has only work-directory containment. |
| G11 | `MLAgentBench/low_level_actions.py:L171-L246` | `e3ae15009cdcd9c8d00b160653aac1d095e7c67e54edc5790acb280886a156a9` | Execute Script uses shell=True and Python REPL uses exec; this is not a trusted custody or network boundary. |
| G12 | `MLAgentBench/environment.py:L276-L282` | `8780d9c8b7d15ad583fbe11e2d9013fb1e9e0902e253bd31e51ee84c6adbfe3f` | Finality is max steps, Final Answer, or wall time. |
| G13 | `MLAgentBench/environment.py:L339-L371` | `8780d9c8b7d15ad583fbe11e2d9013fb1e9e0902e253bd31e51ee84c6adbfe3f` | Every action snapshots non-read-only workspace files; no hash lock is created here. |
| G14 | `MLAgentBench/runner.py:L18-L35` | `0fdc238f5a06b18af0df98a00f5905b75993d9374cbb587066269a66aa323b46` | After agent exit, runner saves a final workspace snapshot. |
| G15 | `MLAgentBench/eval.py:L69-L129` | `778ffb72ac7ea2b6197bec455905091571c15063d34e758ee057c071402ca2fc` | Evaluator can score intermediate snapshots and scores step_final_files; exceptions are printed and suppressed. |
| G16 | `requirements.txt:L1-L18` | `d486d72b77ea5a6341e102159afce38af7ec87805398a837fdb30302270ed629` | Root requirements include broad lower bounds and a git dependency, not a task-minimal frozen environment. |
| G17 | `requirements.txt:L25-L64` | `d486d72b77ea5a6341e102159afce38af7ec87805398a837fdb30302270ed629` | Root requirements mix many ML, LLM, graph, and utility packages and are mostly unpinned. |
| G18 | `install.sh:L9-L17` | `f43772a618f5bcafb055d1559fd42b76f275d554e6268477bcd255f5856a0e36` | Install script performs CUDA/JAX and multiple remote pip/conda installs. |
| L1 | `LICENSE:L1-L20` | `002c2696d92b5c8cf956c11072baa58eaf9f6ade995c031ea635c6a1ee342ad1` | Repository contains MIT software license text with unresolved copyright placeholders. |
| C1 | `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt:L1-L1` | `19a3fe2fb03b45b14386d74fddac2806827402d0aca6a3e87bf861bc8a373559` | CIFAR task caps training at ten epochs and requires per-class test probabilities. |
| C2 | `MLAgentBench/benchmarks/cifar10/scripts/prepare.py:L1-L8` | `b8e0a19b6d35d5e401579e30ec6947dffb47f96489c9e61ec976fe0bf83b7c39` | Preparation calls torchvision CIFAR10 downloader for both train and test; no credential call appears. |
| C3 | `MLAgentBench/benchmarks/cifar10/env/train.py:L34-L49` | `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad` | Starter has CPU fallback, loads both labeled official splits, and uses shuffled training without an explicit seed. |
| C4 | `MLAgentBench/benchmarks/cifar10/env/train.py:L51-L94` | `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad` | Starter computes and prints scorer-test accuracy every epoch and at end. |
| C5 | `MLAgentBench/benchmarks/cifar10/env/train.py:L97-L106` | `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad` | Starter emits one probability row for each test dataset element. |
| C6 | `MLAgentBench/benchmarks/cifar10/scripts/eval.py:L5-L15` | `7c0b387a0b25c991045f2edba90cf56c13aa730a4985941ae07593afc5197e51` | Scorer independently reloads torchvision test split and computes top-1 accuracy from row-indexed argmax. |
| C7 | `MLAgentBench/benchmarks/cifar10/scripts/read_only_files.txt:L1-L1` | `f1cffc9e04f54186b51f98bdd6866dc789a587efe29d7e2d51d4ad637bb8ac77` | Only a data/* write-protection pattern is declared. |
| C8 | `MLAgentBench/benchmarks/cifar10/env/train.py:L7-L31` | `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad` | Starter is a shallow two-convolution/three-linear-layer network with normalization-only transforms. |
| H1 | `MLAgentBench/benchmarks/house-price/scripts/prepare.py:L5-L22` | `32f1e4bf49de46818b4bcd98ff1bd407c9ecfd47c96f35ee6e4397603987dba7` | House-price source is Kaggle; preparation prompts for consent, downloads, and makes deterministic prefix/suffix 80/20 split with answer.csv. |
| H2 | `MLAgentBench/benchmarks/house-price/env/train.py:L7-L24` | `9b264f3821e697c48fd6152b53b5cd55e83f5000e0a52cabf11de7643b700b5b` | Starter exposes SalePrice labels and makes a seeded internal train/validation split but leaves model code incomplete. |
| H3 | `MLAgentBench/benchmarks/house-price/env/train.py:L32-L41` | `9b264f3821e697c48fd6152b53b5cd55e83f5000e0a52cabf11de7643b700b5b` | Starter expects MAE variables/model and emits Id/SalePrice predictions. |
| H4 | `MLAgentBench/benchmarks/house-price/scripts/eval.py:L7-L14` | `610063c5986a5f8674b276db98b97579d481333fdc19563dd1f7b0509b762bb1` | Scorer computes positional SalePrice MAE against answer.csv without explicit Id/schema/finite validation. |
| H5 | `MLAgentBench/benchmarks/house-price/scripts/read_only_files.txt:L1-L2` | `899c264a6c0508ceecdf7ecec0c89840be4ff4ad57ee969bac4c1dead1027e74` | Train and test CSVs are marked read-only for writes. |
| H6 | `MLAgentBench/benchmarks/house-price/scripts/research_problem.txt:L1-L3` | `9c87fc5edb5067a979042ead668ab5b6f1db96c779d510b6ebcdba26c83fa817` | Prompt asks model/feature iteration and says not to read CSVs directly. |
| S1 | `MLAgentBench/benchmarks/spaceship-titanic/env/task_descriptor.txt:L1-L22` | `3a74deed3e81908d3b773ea46839eba966f11c5d02ac99241387da1f3623d318` | Descriptor defines binary Transported target and submission columns. |
| S2 | `MLAgentBench/benchmarks/spaceship-titanic/scripts/source_code.txt:L1-L1` | `b12b16833cdadb2b8792407b2971bd0c6e57569082b064d2b303feee7273f817` | Task source URL is the Kaggle Spaceship Titanic competition data page. |
| S3 | `MLAgentBench/benchmarks/spaceship-titanic/scripts/prepare.py:L5-L21` | `62d1e5c000ae715f9f9e7ca848e0fe59741dcfcbad05e57c76e848662cb23935` | Preparation prompts for Kaggle consent, downloads, and makes deterministic prefix/suffix 80/20 split with answer.csv. |
| S4 | `MLAgentBench/benchmarks/spaceship-titanic/env/train.py:L18-L44` | `8e72c872437278cfbfa5a649f4a66178edb5f5f2aa3dbc755db18dcf65bf598f` | Starter makes deterministic internal split with one skipped boundary row and leaves model block incomplete. |
| S5 | `MLAgentBench/benchmarks/spaceship-titanic/env/train.py:L52-L69` | `8e72c872437278cfbfa5a649f4a66178edb5f5f2aa3dbc755db18dcf65bf598f` | Starter expects train/validation accuracy and emits PassengerId/Transported predictions. |
| S6 | `MLAgentBench/benchmarks/spaceship-titanic/scripts/eval.py:L8-L16` | `920c95258d924b6bfddead9cef19ab737ab3f839aea6ace9146515ff866e7599` | Scorer compares Transported by Series index and divides by submitted row count; it has no explicit ID/row-count/schema validation. |
| S7 | `MLAgentBench/benchmarks/spaceship-titanic/scripts/read_only_files.txt:L1-L2` | `899c264a6c0508ceecdf7ecec0c89840be4ff4ad57ee969bac4c1dead1027e74` | Train and test CSVs are marked read-only for writes. |

## Control files read in full

| Path | SHA-256 | Bytes | LF lines |
|---|---|---:|---:|
| `AGENTS.md` | `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455` | 14285 | 269 |
| `docs/argo/agent-brief.md` | `b7e7f488872b561adc8a243a86de2588e1e98f8f380f895195ac36745e16c62a` | 3540 | 47 |
| `docs/argo/migration-state.json` | `bb7105c7ce57e6f29d67b0f1e811b3128828f0fd3f0dfee2954d43d52f8e103e` | 8286 | 299 |
| `paper/research/public-ml-programme-qualification/effective-authority-v1.json` | `9f68eb4074ec25e7b90bf63fffdc6e758e51b33ea6bb0e2a4287f3460ae8cdd2` | 1563 | 32 |
| `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | 15348 | 172 |
| `paper/research/public-ml-programme-qualification/pinned-public-code-manifest-v1.json` | `07c9820a59d4217c8f94c0613a677593d486931899d55ddd40d18980423715a8` | 340953 | 7147 |

## Pinned source files read in full

| Path | SHA-256 | Manifest Git blob SHA-1 | Bytes | LF lines | Match |
|---|---|---|---:|---:|---|
| `README.md` | `545bf7bf3faedaebb1270841c3998a8635bcf548d01a4802d68c449ad075260b` | `26bf1add856793787f980ab8ea8785722f57a835` | 6567 | 138 | yes |
| `LICENSE` | `002c2696d92b5c8cf956c11072baa58eaf9f6ade995c031ea635c6a1ee342ad1` | `8aa26455d23acf904be3ed9dfb3a3efe3e49245a` | 1069 | 21 | yes |
| `requirements.txt` | `d486d72b77ea5a6341e102159afce38af7ec87805398a837fdb30302270ed629` | `b2c270cd3acb9c8c2b9925c93320b549bc1a04b8` | 761 | 64 | yes |
| `setup.py` | `511f675d48b436b2b108feb9f86663eee047cbb576a9e6612f1e539ca1bf84fe` | `66c1145aa8bdb7d671992f74a542f92ceedeb3c9` | 147 | 7 | yes |
| `Dockerfile` | `b2fb99452309d3a88171a54a7d1a54d76ac4b4d75a4578cd6b0a807ddaeaec26` | `a7a86d17203413ca99554cdd85d9543ccc29ac8e` | 759 | 29 | yes |
| `install.sh` | `f43772a618f5bcafb055d1559fd42b76f275d554e6268477bcd255f5856a0e36` | `d1e1126d4d09850159cd521504b8a366d18598a1` | 633 | 17 | yes |
| `baseline.sh` | `ba5571b8525e7d1d08139aaa8543c532999c88a9153654f2e8efb370a9b93ba3` | `81c491826defb536376347fa6ccbdce780ba237b` | 382 | 11 | yes |
| `eval.sh` | `75d621eb5b7fc17b6a57c37564cc62bdb8e7242b661cff52031b70003175c425` | `ec96555702c81a05d914ddc72298b524993ecf07` | 495 | 15 | yes |
| `MLAgentBench/benchmarks/tasks.json` | `1cd745ac76785a03fc8d1b6fb88955d72305041a470b0a8ad4060946d5caa285` | `3d27f3fd8940a59ddee39e94d0a50d01df072e0c` | 217 | 6 | yes |
| `MLAgentBench/environment.py` | `8780d9c8b7d15ad583fbe11e2d9013fb1e9e0902e253bd31e51ee84c6adbfe3f` | `527d5fb80b74d407c67b93012870c42f47c7a0a8` | 16268 | 387 | yes |
| `MLAgentBench/eval.py` | `778ffb72ac7ea2b6197bec455905091571c15063d34e758ee057c071402ca2fc` | `702c22196c979cfa73a1bdf19f867b4e8c9d66ed` | 6767 | 166 | yes |
| `MLAgentBench/prepare_task.py` | `6ac54ff89e5e2b6c8264e500b4af73fbfb20492065053aa9e86d853824373ce0` | `73c5b2951407d98e77b23069e1edd24da4f96ce6` | 2348 | 62 | yes |
| `MLAgentBench/runner.py` | `0fdc238f5a06b18af0df98a00f5905b75993d9374cbb587066269a66aa323b46` | `b75e18f8d01c9df8fbf4d294fc3aba7e24cd1e7b` | 4439 | 80 | yes |
| `MLAgentBench/schema.py` | `0077751a8cbe7abf60c38e951dbef4cbe8f5e7d834350fe6a5ef50bef476a310` | `e06623bb95fc5c6641fe8fa6c1737f6b2b6d3159` | 1284 | 57 | yes |
| `MLAgentBench/high_level_actions.py` | `7e4d39339497f91a3c0c42d04e5e4b96c1e332276d9b4c2feff33230166a78f3` | `dc44ba621e60dfce16dfea32b924e107d40a96d5` | 13450 | 271 | yes |
| `MLAgentBench/low_level_actions.py` | `e3ae15009cdcd9c8d00b160653aac1d095e7c67e54edc5790acb280886a156a9` | `a126528a158e745858458dc6bc48e9e35e01a8a8` | 13994 | 359 | yes |
| `MLAgentBench/benchmarks/cifar10/env/train.py` | `1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad` | `3519a1b42f3df04f0b4bd1348d25ec15c6b0844b` | 3554 | 106 | yes |
| `MLAgentBench/benchmarks/cifar10/scripts/eval.py` | `7c0b387a0b25c991045f2edba90cf56c13aa730a4985941ae07593afc5197e51` | `ab507739d54beca333d686aed5076f5422fcdd22` | 538 | 18 | yes |
| `MLAgentBench/benchmarks/cifar10/scripts/prepare.py` | `b8e0a19b6d35d5e401579e30ec6947dffb47f96489c9e61ec976fe0bf83b7c39` | `4d38e44c752b4fbeeb24160610db8b0cfa40e155` | 268 | 8 | yes |
| `MLAgentBench/benchmarks/cifar10/scripts/read_only_files.txt` | `f1cffc9e04f54186b51f98bdd6866dc789a587efe29d7e2d51d4ad637bb8ac77` | `07f43b870eb6ed97c32d56947e935a0a6939f3c7` | 6 | 1 | yes |
| `MLAgentBench/benchmarks/cifar10/scripts/research_problem.txt` | `19a3fe2fb03b45b14386d74fddac2806827402d0aca6a3e87bf861bc8a373559` | `5b9fcc209519eddca68ccef00992f0a701486879` | 286 | 1 | yes |
| `MLAgentBench/benchmarks/house-price/env/data_description.txt` | `356a4670aa688afa8ba44b1365b633fbbac2dae535fe4638532630607d64070d` | `cba0710286136ba64d273612bda60742f00f1501` | 13370 | 523 | yes |
| `MLAgentBench/benchmarks/house-price/env/train.py` | `9b264f3821e697c48fd6152b53b5cd55e83f5000e0a52cabf11de7643b700b5b` | `50978e6903726a499061c123cc7a4b2559386c51` | 1768 | 41 | yes |
| `MLAgentBench/benchmarks/house-price/scripts/eval.py` | `610063c5986a5f8674b276db98b97579d481333fdc19563dd1f7b0509b762bb1` | `9d807dff8c621be6d13e6938cc1da1cfca0d4588` | 501 | 17 | yes |
| `MLAgentBench/benchmarks/house-price/scripts/prepare.py` | `32f1e4bf49de46818b4bcd98ff1bd407c9ecfd47c96f35ee6e4397603987dba7` | `ebbc919184dc3bf67b7168a38c1e104a2eb3a361` | 950 | 23 | yes |
| `MLAgentBench/benchmarks/house-price/scripts/read_only_files.txt` | `899c264a6c0508ceecdf7ecec0c89840be4ff4ad57ee969bac4c1dead1027e74` | `b52a2f84949552fdc7bbdacefeb1a171b482a09a` | 22 | 2 | yes |
| `MLAgentBench/benchmarks/house-price/scripts/research_problem.txt` | `9c87fc5edb5067a979042ead668ab5b6f1db96c779d510b6ebcdba26c83fa817` | `471ad8218730e49feb8b081ab2cec721fb81b02c` | 429 | 3 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/env/task_descriptor.txt` | `3a74deed3e81908d3b773ea46839eba966f11c5d02ac99241387da1f3623d318` | `6c430f13a25d4f68ba60be8c24794248656840c5` | 1945 | 22 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/env/train.py` | `8e72c872437278cfbfa5a649f4a66178edb5f5f2aa3dbc755db18dcf65bf598f` | `fb29ff9fb9dc7220be0a9c869f670b4c9b72de26` | 2404 | 69 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/scripts/eval.py` | `920c95258d924b6bfddead9cef19ab737ab3f839aea6ace9146515ff866e7599` | `86bfae9b933e16f3851ed7269620652c53925205` | 569 | 19 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/scripts/prepare.py` | `62d1e5c000ae715f9f9e7ca848e0fe59741dcfcbad05e57c76e848662cb23935` | `bcb8859b345b84ca3e49ee9c0b715334e29257f3` | 884 | 21 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/scripts/read_only_files.txt` | `899c264a6c0508ceecdf7ecec0c89840be4ff4ad57ee969bac4c1dead1027e74` | `b52a2f84949552fdc7bbdacefeb1a171b482a09a` | 22 | 2 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/scripts/research_problem.txt` | `0c81e9260d8611884a3d904d56b03e270ea8d70292ba9f6a1d165d21df928ec0` | `61594878d9ae2e481b03443531c443dd0b638a3b` | 423 | 3 | yes |
| `MLAgentBench/benchmarks/spaceship-titanic/scripts/source_code.txt` | `b12b16833cdadb2b8792407b2971bd0c6e57569082b064d2b303feee7273f817` | `1b18fff4edacf78fd21ce540e26739dc2cee0292` | 58 | 1 | yes |
| `MLAgentBench/agents/agent.py` | `495beb65263614e5258ebb139d802258bf7a7edc760cc2935fa10daedf9e8ae1` | `8635b347b2b36163ebccfcd7f7f1904c8bd702a5` | 13313 | 333 | yes |
| `MLAgentBench/agents/agent_research.py` | `95ee6c620fd7c0f3b62ff723a3f63c518ccccb1eaa5e2f37948b8d58529e553b` | `5673652d0d0784532a79c220ec89ad96edc59e75` | 14754 | 289 | yes |
| `run_experiments.sh` | `95483641153199a58ed07ab55daf1fad5bf8fbd57c21b87bb30eaf732c280521` | `3a1dd4cfd522608f542e4002706898df89888126` | 896 | 35 | yes |
| `multi_run_experiment.sh` | `6570175b6b5c9afae60576345526f1a61ffc5612e60535d44395b9c18062698b` | `eaa2557551546ef9512e939aab795c40647691fb` | 1040 | 50 | yes |
