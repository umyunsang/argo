# Recent public ML programmes: focused task-source audit

**State:** `DOCUMENT_LEVEL_SOURCE_FIT_ONLY__NOT_CERTIFIED_FOR_RUN_OR_TASK_ADMISSION`

## Read and authority manifest

| Input | Read state | LF span | Verified hashes |
|---|---|---:|---|
| 1GC-7RC `2605.17046v2` | **FULL** versioned layout-text read | 1–943 | text `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`; PDF `7151a36b6590d7f4bdd9067943fb08f3fe87060e5e5ce33ae009f8774ef90969` |
| AgentHPOBench `2607.29626v1` | **FULL** versioned layout-text read | 1–3322 | text `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`; PDF `d9c395c0c4f5c25bc5a83b5fde380b60c0d19e47d9b8621b3eef8c7cd0692ec8` |
| Agent Laboratory `2501.04227v2` | **FULL** versioned layout-text read | 1–3977 | text `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`; PDF `67b9543ae1d8e3ad86a65e2a436ddbd12700d7c8f4a66c5b4c2a6fccc1674d75` |
| `secondary-reader-inputs.json` | FULL | n/a | `604579710fa5a782bffff0cccee48b8e2294290fb13ff12e2fa4dec39c869f22` |
| `task-qualification-requirements.json` | FULL | n/a | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` |
| colocated `arxiv-metadata.xml` | FULL | 1–141 | `0aa6909a80f61077cc3f72400f46e755b45d3aa91ed4e055a224ac41f07c8e29` |

All declared PDF/text hashes matched the observed bytes. Content review used the complete PDF-extracted layout texts. The PDFs were byte-hash verified, not independently page-rendered. No paper is a partial read.

The task prompt reports apparatus source/mocks and broad run/install/publication categories as approved, but no concrete run envelope. The reviewed requirements artifact itself still records its earlier false authorization fields. The operative boundary for this audit is narrower: documents only. No install, code inspection, run, training, evaluation, scoring, fixture, credential use, native change, manuscript change, or commit occurred. Native construction remains paused.

## Evidence-layer separation

- **Permission:** category-level approval does not supply a concrete task/run envelope. This audit adds none.
- **Software:** the papers print public URLs and describe harnesses, but no repository code, code license, asset script, lock gate, or scorer bytes were inspected.
- **Report:** paper task tables, scores, author hardware, task budgets, workflow inference time, and API cost are documentary evidence.
- **Runtime proof:** no local command trained or scored a model. Local CPU/GPU fit, wall time, memory, determinism, and account-free retrieval remain `NOT_OBSERVED` or `NOT_CERTIFIED`.

## Decision

**Propose the public 1GC-7RC repository, focused first on Task 4 `ogbg-molhiv`, as the next public-code inspection target:** `https://github.com/Strolchii/1GC-7RC-Benchmark`. This is an inspection target, not an admitted run.

The choice is based on natural task fit, not the published score or expected G advantage:

- T4 reports an official train/validation/test split, test AUROC, 41K molecular graphs, a pure-PyTorch GIN baseline, a 60-minute single-A100 budget, and an MIT-reported dataset license. `GC_T4` (LF 265–270; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`) `GC_LICENSES` (LF 806–825; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`)
- The method surface is substantive. Reported differences cover edge features, virtual nodes, residual paths, JK-sum, dual pooling, architecture pivots, loss choice, and heterogeneous blending. This is not only scalar HPO. `GC_ARCHITECTURE_VS_GRID` (LF 430–438; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`) `GC_WINNING_METHODS` (LF 462–473; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`)
- It is **not certified**. The paper's harness scans scored checkpoints and selects the overall best; agents can call the evaluator during development; Tasks 4–6 are scored on test. That is not one hidden deterministic score after one agent-selected artifact lock. `GC_HARNESS_SELECTION` (LF 289–306; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`) `GC_AGENT_EVAL_AND_ENSEMBLE` (LF 417–429; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`) `GC_RULES_SPLITS` (LF 313–333; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`)
- The paper does not establish the repository code license, account-free download, CPU feasibility, local wall time, evaluator independence, or lock enforcement.

## Comparative source fit

| Programme | Fit decision | Real method changes | Evaluation and leakage | Published compute evidence | License/access state |
|---|---|---|---|---|---|
| **1GC-7RC** | Best next source inspection; T4 first, T5 residual, T6 conditional. **NOT_CERTIFIED**. | Broad training-code changes. Actual results distinguish architecture-family changes from same-family grids. | Claims deterministic evaluation, but current selection is over scored checkpoints. T4–T6 use test. A new dev-only loop and one prehidden-score artifact lock are required. | 40–120 min/task on one A100 80 GB; study node used A100 SXM4, 64 GB RAM, 16 EPYC cores. This is author evidence, not local proof. | T4 MIT; T5 CC BY 4.0; T6 CC BY-ND 4.0 are reported. Code license and account-free access remain unverified. |
| **AgentHPOBench** | HPO comparator and task catalog, not the primary method-research substrate. **NOT_CERTIFIED**. | Intentionally narrow: only predefined discrete fields; data, split, metric, evaluator, metadata, and other method surfaces remain fixed/clamped. `HPO_CONSTRAINED_SCOPE` (LF 193–224; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`) | Repository objective, including some test metrics, is visible during decisions. The paper explicitly says there is no separate hidden test set. `HPO_NO_HIDDEN` (LF 900–912; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`) `HPO_NO_HIDDEN_EXPLICIT` (LF 977–979; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`) | Limited budget is approximately 10% of upstream, but no per-task time/memory table. Controlled runs used an H200 with 143,771 MiB. Not local proof. | No benchmark-code or per-task data/code licenses in the paper. Predownloaded assets do not prove account-free access. |
| **Agent Laboratory** | **Verified design/baseline input, not a task suite.** | `mle-solver` can replace/edit whole programs, but generic research mode uses an LLM reward. | Its MLE-Bench evaluation has 80/20 train/dev and evaluates highest-dev final code on test, but no byte lock or independent scorer contract is stated. The ten tasks are unnamed. `LAB_MLE_SUBSET` (LF 864–900; text SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`) | Paper-wide M3 Max/36 GB claim; 600s experiment timeout; two-hour solver statement. Workflow LLM inference time/API cost is not a task training envelope. | Kaggle task URLs, licenses, and account-free access are not established. |

## Candidate tasks

| Rank | Candidate | Why it remains live | Blocking gaps |
|---:|---|---|---|
| 1 | **1GC T4 — Graph Learning / `ogbg-molhiv`** | Broad GNN method competition; official three-way split; AUROC; MIT-reported data; 60-minute published single-GPU budget. | Inspect code/license/data retrieval; hide test; deterministic independent scorer; one artifact hash lock; local timing; MUE/failure/fallback/ancestry rules. |
| 2 | **1GC T5 — Forest Cover Type** | Broad residual/attention/classical/deep-blend choices; 80/10/10; CC BY 4.0 reported; 40-minute published budget. | Same lock/test-custody/code-license/access/local-runtime gaps. External TabNet reference uses a different split and is descriptive only. |
| 3 | **1GC T6 — ETTh1** | DLinear/PatchTST/Transformer, decomposition, loss, and regularization choices; 12/4/4-month split; 40-minute budget. | CC BY-ND scope needs a receipt; visible-test development must stop; ETT ancestry collides with five AgentHPOBench tasks. |
| — | 1GC T1 | No hidden split; no separate dataset license found. | Not initial. |
| — | 1GC T2 | No hidden split; TinyImageNet has ImageNet non-commercial research/education terms and no standalone license. | Not initial. |
| — | 1GC T3 | No hidden split; no standalone VOC license; Flickr terms; pretrained-weight boundary not established. | Not initial. |
| — | 1GC T7 | No standard dataset license; non-commercial README permission; test/validation terminology does not yield a hidden split. | Not initial. |

If T4 becomes P0, register `1GC-7RC / OGB / ogbg-molhiv / HIV graph-property` and the whole exposed programme on the development side. Do not rename or resplit it into P2. Likewise, ETTh1/ETTm1/ETTm2 tasks are one ETT source family, not independent confirmation.

## Task and source URL inventory printed by the papers

- **1GC-7RC:** `https://github.com/Strolchii/1GC-7RC-Benchmark`; T1 Language Modeling/TinyShakespeare, T2 Image Classification/TinyImageNet, T3 Semantic Segmentation/Pascal VOC 2012, T4 Graph Learning/ogbg-molhiv, T5 Tabular Prediction/Forest Cover, T6 Time Series Forecasting/ETTh1, T7 Text Classification/AG News. The paper does not print distinct task-directory URLs. `GC_REPO` (LF 29–33; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`) `GC_TASK_TABLE` (LF 176–188; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`)
- **AgentHPOBench:** `https://github.com/OpenMOSS/AgentHPOBench`. The paper prints repository labels and the 30 task names below, but no individual upstream repository code URLs. Do not expand labels into guessed GitHub links. `HPO_REPO` (LF 21–33; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`) `HPO_TASK_TABLE` (LF 795–825; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`)
  1. `llm.c` — FineWeb Pretraining
  2. `torch-conv-kan` — ConvKAN CIFAR-10
  3. `open-r1` — Open-R1 MATH-500
  4. `agent-lightning` — Room Selector Tuning
  5. `uni2ts` — Uni2TS ETTh1 Forecasting
  6. `timesfm` — TimesFM Long Horizon
  7. `ModernBERT` — ModernBERT MNLI
  8. `cifar10-airbench` — AirBench CIFAR-10
  9. `NoisyGL` — NoisyGL Cora GCN
  10. `TabMini` — TabMini Promoters
  11. `binary-diffusion-tabular` — Adult Tabular Diffusion
  12. `xlstm` — xLSTM Parity
  13. `vbll` — VBLL Yacht Regression
  14. `tabm` — TabM California Housing
  15. `TimeXer` — TimeXer PJM Forecasting
  16. `ABLkit` — ABLkit HWF Reasoning
  17. `tunedGNN` — tunedGNN Cora GCN
  18. `verl` — verl GRPO GSM8K
  19. `ForestDiffusion` — ForestDiffusion Iris
  20. `VAR` — VAR ImageNet 256
  21. `align-anything` — RAGEN Bandit Alignment
  22. `chronos-forecasting` — Chronos Weather Forecasting
  23. `HyperbolicCV` — HyperbolicCV CIFAR-100
  24. `iTransformer` — iTransformer ETTm2 Forecasting
  25. `TimeMixer` — TimeMixer ETTm2 Forecasting
  26. `ART` — ART 2048
  27. `open-r1-multimodal` — Multimodal Open-R1 MathVista
  28. `semi-supervised-regression` — RankUp UTKFace Regression
  29. `SparseTSF` — SparseTSF ETTm1 Forecasting
  30. `simpleRL-reason` — SimpleRL MATH-500
- **Agent Laboratory:** `https://AgentLaboratory.github.io`. Its five items are open research-question templates, not fixed datasets/splits/scorers. Its objective evaluation uses ten unnamed MLE-Bench text/tabular low-complexity Kaggle challenges; no challenge URLs are printed. `LAB_PROJECT_URL` (LF 14–37; text SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`) `LAB_FIXED_TOPICS` (LF 519–543; text SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`) `LAB_MLE_SUBSET` (LF 864–900; text SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`)

## Evaluation, artifact, and comparator boundary

Required adaptation for any surviving 1GC task:

1. Keep training and all research feedback on train/dev only.
2. Before any hidden access, require the agent to lock exactly one artifact ID, content hash, timestamp, eligibility record, and declared fallback outcome.
3. Call an independent deterministic hidden scorer once on that artifact. Do not use archive-best, hidden-score reselection, or a process/LLM judge as the task metric.
4. Record no-lock, invalid artifact, scorer failure, artifact-dependent crash, numerical missingness, assigned denominators, retries, costs, and right-censoring separately.
5. Treat all actual training and selection-performance evaluation as R1. No such authority is created here.

Residual comparators:

- 1GC baseline plus predeclared architecture variants. Published external reference numbers are descriptive only because the paper says they are not directly comparable. `GC_REFERENCE_LIMIT` (LF 773–803; text SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`)
- AgentHPOBench random search, TPE, and fixed-budget BOHB-style proposal policies on the same frozen HPO subspace. These are secondary HPO comparators, not method-family competitors. `HPO_HPO_BASELINES` (LF 1198–1219; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`)
- AgentHPOBench final-step versus best-so-far as a process diagnostic only. Primary efficacy remains the single prelocked artifact, not a post-hidden incumbent. `HPO_INCUMBENT_DIAGNOSTIC` (LF 1275–1282; text SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`)
- Agent Laboratory `mle-solver` as a whole-program-search/design baseline after a task is independently qualified. Its LLM reward must not replace the hidden task metric. `LAB_BROAD_EDIT_LLM_SCORE` (LF 293–345; text SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`)

## N1–N10 closure state

- **N1:** document only; no apparatus code.
- **N2:** trusted launch/lock/bypass coverage `NOT_CERTIFIED`.
- **N3:** no R1 permission created; no run performed.
- **N4:** MUE/value rule and commitment actor/time `NOT_DEFINED`.
- **N5:** single agent-selected artifact lock is proposed, not implemented.
- **N6:** failure/invalid/missing/fallback/denominator table `NOT_DEFINED`.
- **N7:** exact task/code/prompt/environment/command/numeric envelope and phase retry rules `NOT_DEFINED`.
- **N8:** Agent Laboratory is descriptive design/baseline input only; no whole-system causal or SOTA claim.
- **N9:** P0 programme/data/generator ancestry proposal is not frozen; ETT overlaps stay together.
- **N10:** latency, UNKNOWN/BLOCKED, gate/bypass, R2, lock/scorer defect, censoring, and total-cost census `NOT_OBSERVED`.

## Certification state

`task_admission=NOT_CERTIFIED`; `software_reproducibility=NOT_CERTIFIED`; `code_license=NOT_CERTIFIED`; `account_free_access=NOT_CERTIFIED`; `local_runtime=NOT_OBSERVED`; `hidden_scorer_independence=NOT_CERTIFIED`; `artifact_lock_enforcement=NOT_CERTIFIED`; `MUE=NOT_DEFINED`; `failure_policy=NOT_DEFINED`; `confirmation_ancestry=NOT_FROZEN`.

The paper-reported author budgets, API costs, and hardware are not local estimates. No hidden metric is replaced by a process judge.

## Decisive exact-source quotes

The companion JSON contains 1-based LF spans, complete exact quotes, and full source SHA-256 values for all 29 locators. The quotes below are the decisive subset.

### GC_T4

Source: `paper/research/public-ml-programme-qualification/sources/2605.17046v2-layout.txt`; LF 265–270; SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`.

```text
    Task 4 (Graph Learning). Binary classification of molecular graphs for HIV inhibition prediction
(ogbg-molhiv from the Open Graph Benchmark; 41 K graphs with 9-dim atom features and 3-dim edge
features, official train/val/test split). The baseline implements a 5-layer Graph Isomorphism Network
(GIN) [50] with learned atom embeddings (d = 64, summed per feature), hidden dimension 300, global
mean pooling, and an MLP classifier, all in pure PyTorch without PyG. A custom collate_graphs()
function batches variable-size graphs with node-offset tracking. The metric is AUROC on the test set.
```

### GC_HARNESS_SELECTION

Source: `paper/research/public-ml-programme-qualification/sources/2605.17046v2-layout.txt`; LF 289–306; SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`.

```text
3.3     Harness architecture
For each of the seven tasks, the harness is described in the following and illustrated in Figure 2.
    Step 1. Creation of an isolated run directory containing copies of the dataset and task-specific
program.md, as well as locked versions of prepare.py and the baseline train.py.
    Step 2. Launch of the agent as a CLI subprocess with a standardized prompt instructing it to
read program.md and, based on the provided train.py, generate its own run_{x}.py scripts with
improvements.
    Step 3. Streaming of the agent’s stdout to both the console and a log file, with structured JSON
events parsed for real-time monitoring.
    Step 4. Enforcement of a hard per-task wall-clock timeout (40-120 minutes, depending on dataset
size; see Table 2) via a daemon watchdog thread with a 30-second grace period.
    Step 5. After termination, scanning of the checkpoints/ directory for scored checkpoints, selection
of the overall best, clustering of remaining checkpoints into 5-minute windows (retaining only the best
per window to preserve diversity), and execution of prepare.py –eval to produce the official metric as
a JSON object.
    For Task 3, the harness additionally downloads and caches the two permitted DINOv3 backbone
weights in a weights/ directory prior to execution. All artifacts, including the final train.py, full
stdout logs, and result.json, are retained for post-hoc analysis.
```

### GC_ARCHITECTURE_VS_GRID

Source: `paper/research/public-ml-programme-qualification/sources/2605.17046v2-layout.txt`; LF 430–438; SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`.

```text
    Iteration count is not skill. Our experiments show a negative correlation between the mean
number of training scripts launched per task and the aggregate score, as shown in Appendix Figure 3.
Qwen launches the most scripts overall (often 20-30 per run on the heaviest tasks (T4 and T6), peaking
at 36 on a single Task 4 attempt) and finishes with the lowest Agg (+0.188). Opus 4.7 launches the
fewest (median 5-8 per task) and achieves the highest Agg (+0.302). The reason is visible in the run
dirs: Qwen’s high script counts are spent on hyperparameter grids that span a single architecture (e.g.
all 36 Task 4 scripts converge to vanilla GIN), whereas Opus 4.7 explores 3-7 architectural variants,
recognises diminishing returns early, and pivots to consolidation. What matters is not how many scripts
are launched but what dimension the variants span.
```

### GC_LICENSES

Source: `paper/research/public-ml-programme-qualification/sources/2605.17046v2-layout.txt`; LF 806–825; SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`.

```text
E       Dataset licenses
All datasets used in the 1gc-7rc benchmark are publicly available and are used in accordance with their
respective licensing terms, where specified, as well as applicable usage conditions:

    1. TinyShakespeare [24]: Text based on public-domain Shakespeare works; distributed via Karpa-
       thy’s MIT-licensed char-rnn repository. No separate dataset license found.
    2. TinyImageNet [27]: A downsampled subset of the ImageNet dataset; access and usage are subject
       to the ImageNet Terms of Access, which restrict usage to non-commercial research and educational
       purposes. No standalone license specific to TinyImageNet was found.
    3. Pascal VOC 2012 [15]: Provided as part of the PASCAL VOC 2012 challenge; usage of the
       included images must comply with the respective Flickr terms under which they were originally
       published. No explicit standalone dataset license is provided.
    4. ogbg-molhiv [20]: Released under the permissive MIT License as part of the Open Graph Bench-
       mark (OGB) initiative.
    5. Forest Cover Type [7]: Publicly available via the UCI Machine Learning Repository and dis-
       tributed under the Creative Commons Attribution 4.0 (CC BY 4.0) license.
    6. ETTh1 [55]: Released as part of the ETDataset repository under CC BY-ND 4.0; the Informer
       code repository is separately licensed under Apache 2.0.
    7. AG News [54]: Collected from the AG corpus; no standard license found, but the dataset
       README permits use for research, data mining, and other non-commercial activity.
```

### GC_HARDWARE

Source: `paper/research/public-ml-programme-qualification/sources/2605.17046v2-layout.txt`; LF 742–751; SHA-256 `f186d8c15b4c5af27d1b67ba14d3f13041770907daa502b46e7558c3ee591ea7`.

```text
B     Experimental setup
All experiments run sequentially with one reserved NVIDIA A100 SXM4 80 GB GPU on an NVIDIA
DGX A100 node, with 64 GB allocated system RAM and 16 cores of an AMD EPYC 7742 CPU. Each
agent is given the same system prompt, task description, and baseline train.py. The prompt instructs
the agent to read program.md and, based on the provided train.py, create its own run_{x}.py scripts
with improvements. All experiments were conducted in April 2026; exact start and end dates for each
agent are listed in Table 3. To account for the non-determinism inherent in LLM sampling (temperature,
top-p) and variability in training outcomes, we run each agent-task pair 5 times under the task-specific
time budget (Table 2) and report the mean and standard deviation of the official metric. Agent outputs
are streamed to a log file and parsed in real time via structured JSON events.
```

### HPO_CONSTRAINED_SCOPE

Source: `paper/research/public-ml-programme-qualification/sources/2607.29626v1-layout.txt`; LF 193–224; SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`.

```text
3        Method
We introduce AgentHPOBench, a benchmark and evaluation harness for assessing whether agents can
improve executable ML experiments through sequential hyperparameter interventions, as shown in Figure 2.
Unlike agent benchmarks that evaluate general execution across multiple steps, code modification, or paper
reproduction, AgentHPOBench isolates a specific experimental capability: converting the logs and metrics of
an executed repository experiment into a valid configuration for the next run. The agent selects values only
from the predefined intervention space, while the harness validates and executes the proposed configuration
and returns the resulting observations. This process is repeated for a predefined number of intervention steps.
Table 1 compares AgentHPOBench with representative HPO benchmarks. Most prior HPO benchmarks
provide controlled tabular, surrogate, or wrapped objectives for comparing optimization algorithms, but
abstract away repository execution details, textual logs, and sequential interaction. AgentHPOBench instead
exposes real research repositories as executable task units and evaluates sequential optimization using task
metrics tied to results reported by the corresponding papers or repositories.

3.1       AgentHPOBench
AgentHPOBench consists of 30 tasks constructed from 30 executable ML repositories on GitHub. Task
construction follows three principles. First, each task must require a substantive experimental decision within
an executable training or evaluation pipeline. Second, each task must provide measurable feedback after
every intervention, allowing the benchmark to evaluate how the agent uses previous outcomes to inform
subsequent decisions. Third, each task must remain close to real research practice by preserving the scripts,
dependencies, logs, and failure modes of the original repository whenever possible.
Each task is based on an executable experiment from the original repository or its official reproduction
environment. An executable task interface specifies how the harness launches the experiment, extracts the
target metric, and records the outputs under a standardized result protocol. For each task, we construct
the intervention space from the hyperparameters and valid values exposed by the official training scripts,
configuration files, or repository documentation. We retain only fields that affect the execution or outcome of


                                                                           4

the experiment. Agents may modify only these predefined fields, while the dataset, data split, target metric,
evaluation code, and benchmark metadata remain fixed.
```

### HPO_NO_HIDDEN

Source: `paper/research/public-ml-programme-qualification/sources/2607.29626v1-layout.txt`; LF 900–912; SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`.

```text
9   Implementation and Reproducibility Details
Common execution protocol. Unless stated otherwise, all results use the limited-budget protocol. Each
task first executes a fixed reference baseline and then permits five sequential interventions. The baseline
and every intervention use the same task-specific data split, metric, intervention space, and execution
budget. The limited setting uses approximately 10% of the corresponding original training or evaluation
budget. The full-budget study changes only this execution budget and retains the task definition, prompt,
intervention space, five-decision protocol, result schema, and scoring pipeline. Each decision must return
one complete configuration in the structured NEW_CONFIG format. Omitted fields retain their current values,
and configurations are validated and clamped to the task-specific discrete intervention space before execution.
The reported task result is the metric after intervention five, rather than the best intermediate metric.
The benchmark optimizes the objective exposed by each upstream repository. Some repositories report a test-
set metric, or a test metric at the checkpoint selected by validation performance, and this repository-defined
objective is visible during sequential decision making. AgentHPOBench therefore evaluates optimization
```

### HPO_NO_HIDDEN_EXPLICIT

Source: `paper/research/public-ml-programme-qualification/sources/2607.29626v1-layout.txt`; LF 977–979; SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`.

```text

of an observable experimental objective. It does not provide a separate hidden test set and should not be
interpreted as estimating generalization after adaptive model selection.
```

### HPO_HARDWARE_ASSETS

Source: `paper/research/public-ml-programme-qualification/sources/2607.29626v1-layout.txt`; LF 1107–1121; SHA-256 `04372a97e3f080c9a322b154daf64fdd4707f6292a16dba4bebec63639acb1a7`.

```text
Execution environment and reproducibility resources. The controlled experiments run on Linux development
machines equipped with NVIDIA H200 GPUs with 143,771 MiB of visible memory. The orchestration layer
uses Python 3.10 or newer. Because the 30 tasks depend on heterogeneous upstream repositories, each task
adapter invokes its repository-specific Conda environment rather than forcing all tasks into one dependency
stack. Model weights and datasets are downloaded before execution, and the reported runs use offline
Hugging Face modes.
For reproducibility, we record the upstream repository version, benchmark adaptations, environment and
asset-preparation requirements, model checkpoint, task seeds, baseline configuration, metric extraction rule,
intervention space, execution budget, and scoring reference for every task. Detailed setup instructions and
machine-readable task specifications will be provided in the public GitHub repository.

Result Validation. We include only task runs that complete the reference baseline and all five interventions,
with a valid configuration and metric recorded at every step. Interrupted or malformed runs are excluded
and rerun at the task level. All reported aggregates are computed from complete task records. The public
GitHub repository includes the corresponding validation and aggregation utilities.
```

### LAB_PROJECT_URL

Source: `paper/research/public-ml-programme-qualification/sources/2501.04227v2-layout.txt`; LF 14–37; SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`.

```text
                                         Historically, scientific discovery has been a lengthy and costly process, demanding substantial time and
                                         resources from initial conception to final results. To accelerate scientific discovery, reduce research costs,
                                         and improve research quality, we introduce Agent Laboratory, an autonomous LLM-based framework




arXiv:2501.04227v2 [cs.HC] 17 Jun 2025
                                         capable of completing the entire research process. This framework accepts a human-provided research
                                         idea and progresses through three stages—literature review, experimentation, and report writing to
                                         produce comprehensive research outputs, including a code repository and a research report, while
                                         enabling users to provide feedback and guidance at each stage. We deploy Agent Laboratory with
                                         various state-of-the-art LLMs and invite multiple researchers to assess its quality by participating in
                                         a survey, providing human feedback to guide the research process, and then evaluate the final paper.
                                         We found that: (1) Agent Laboratory driven by o1-preview generates the best research outcomes;
                                         (2) The generated machine learning code is able to achieve state-of-the-art performance compared to
                                         existing methods; (3) Human involvement, providing feedback at each stage, significantly improves the
                                         overall quality of research; (4) Agent Laboratory significantly reduces research expenses, achieving
                                         an 84% decrease compared to previous autonomous research methods. We hope Agent Laboratory
                                         enables researchers to allocate more effort toward creative ideation rather than low-level coding and
                                         writing, ultimately accelerating scientific discovery.


                                                                            § https://AgentLaboratory.github.io
```

### LAB_MLE_SUBSET

Source: `paper/research/public-ml-programme-qualification/sources/2501.04227v2-layout.txt`; LF 864–900; SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`.

```text
4.4. Evaluating mle-solver on MLE-Bench

Evaluating the entire Agent Laboratory workflow does not contain much information about the
ability of mle-solver specifically to solve individual ML problems. In order to evaluate mle-solver
more objectively, we use a subset of 10 ML challenges from MLE-Bench (Chan et al. (2024)). MLE-
Bench is a benchmark designed to assess the capability of agents in handling real-world ML tasks on
Kaggle competitions. This benchmark compares agent performances with human baselines, scoring
agents with Kaggle’s medal system, and incorporating mechanisms to mitigate contamination and
plagiarism risks. We include all challenges focusing on text and tabular data from the low complexity
category of MLE-Bench. We provide as input to mle-solver the following: Kaggle dataset description,
distilled knowledge from Kaggle notebooks, as well as an accessible train and dev set. Instead of
using an LLM scoring function, the mle-solver score is evaluated on the dev set, which is a 20%
random sample taken from the original training set, and the training set is represented by the other
80% split. All data (dev, test, train) is placed into arrays using the numpy library instead of providing



                                                                                                      18

                            Agent Laboratory: Using LLM Agents as Research Assistants



file locations in order to better emulate the data preparation phase. Once all mle-solver steps
have concluded, the final code with the highest score is evaluated on the actual Kaggle test set and a
benchmark score is recorded.
    We compare average scores across several runs from three other methods: MLAB (Huang et al.
(2024), gpt-4o backend), OpenHands (Wang et al. (2024b), gpt-4o backend), and AIDE (Schmidt
et al. (2024), o1-preview backend). While mle-solver submitted valid solutions for all MLE-Bench
challenges within two hours, prior methods often failed to submit, complicating scoring. We thus
calculated average scores by excluding invalid submissions from other works and averaging valid
ones. We find that Agent Laboratory’s mle-solver is more consistently high scoring than other
solvers, with mle-solver obtaining four medals (two gold, one silver, and one bronze) compared
with OpenHands (gpt-4o) obtaining two medals (two gold), AIDE (o1-preview) obtaining two medals
(one gold, one bronze) and MLAB obtaining zero medals. Additionally, mle-solver obtained above
median human performance on six out of ten benchmarks, with AIDE obtaining five out of ten,
OpenHands two out of ten, and MLAB zero out of ten. A detailed overview is provided in Figure 9.
```

### LAB_CONFIG_HARDWARE

Source: `paper/research/public-ml-programme-qualification/sources/2501.04227v2-layout.txt`; LF 1565–1602; SHA-256 `21114d368191bb274e14def500447b97fe4920d6a6c0f8fbbc6fbfdaf7516294`.

```text
A. Agent Laboratory configuration

A.1. Hyperparameters

Table 1 | Hyperparameters for A ge n t Labor atory.

                 Category                       Hyperparameter                          Value
                 Literature Review              Number of Paper Summaries               5
                                                Full Text History Decay Steps           3
                                                Agent temperature                       0.8
                 Data Preparation               Experiment Timeout                      120s
                 Running Experiments            mle-solver steps                        3
                                                Code repair attempts                    2
                                                Maximum top codes                       2
                                                Error history length                    5
                                                Code history length                     2
                                                Number of comparison trials             2
                                                Experiment Timeout                      600s
                                                Score generation temperature            0.6
                                                Repair temperature                      0.8
                                                Initial code temperature                1.0
                                                Solver temperature                      1.0
                 Paper Writing                  paper-solver steps                      5
                                                Maximum top papers                      1
                                                Paper history length                    10
                                                Number of Reviewers                     1
                                                Number of comparison trials             2
                                                Solver temperature                      1.0
                                                Initial paper temperature               0.8
                 Paper Refinement               Number of Reviewers                     3




A.2. Hardware

All experiments in this paper were run on a 2023 MacBook Pro with an Apple M3 Max processor and
36 GB of memory.
```
