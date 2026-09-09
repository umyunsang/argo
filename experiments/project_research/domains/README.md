# Development domain apparatus

This is research apparatus, not native ARGO runtime. The three commands perform real development baseline/hypothesis measurements. They do not implement autonomous B/H/P campaigns, award AAA, access final evaluation, or declare PI completion. A negative or uncertain result remains a valid observation.

The external controller owns ORX lifecycle, effective mount isolation, aggregate resource caps, serialization, budget accounting, interruption and final-evaluation gates. Use one measured container at a time, one CPU, at most 2 GiB RAM, and thread limits of one. Commands neither launch extra containers nor choose a model.

## Environment

Use the parent's bounded, pinned Python 3.11 research image and `requirements.txt`. Exact package versions are checked before each CLI command. All seven releases were verified older than seven days on 2026-09-09. PyAMG 5.3.0 needs a source build on Linux aarch64; its official release has no wheel for that platform. Preserve the parent's resulting image and wheel hashes.

Provision DuckDB's `tpch` extension during image construction. Offline execution uses `DUCKDB_EXTENSION_DIRECTORY=/opt/duckdb-extensions`, explicitly disables automatic extension installation/loading, and loads only the provisioned `tpch`. Do not install an extension inside a measured run.

## Trusted preparation

Create the parent directories before running. Worker and evaluator roots must be new, separate nonnested directories. Never mount the raw archive, evaluator directory, preparation record, or parent private root to a worker.

```sh
python -m experiments.project_research.domains.cli prepare-wine \
  --worker-root PRIVATE/worker/wine --evaluator-root PRIVATE/evaluator/wine \
  --seed 20260909 --output PRIVATE/runs/wine-preparation.json
python -m experiments.project_research.domains.cli prepare-settings \
  --evaluator-root PRIVATE/evaluator/settings --seed 720260909 \
  --output PRIVATE/runs/settings-preparation.json
```

Wine acquisition downloads the official UCI archive and verifies the archive plus red/white member SHA-256 values. `--source-archive` allows a previously downloaded exact archive. Canonical numeric identity of all 11 physicochemical inputs defines groups; target and color are excluded. Whole groups enter train/dev/final/future in 60/20/10/10 proportions of unique groups. Target-disagreeing duplicates and identical inputs across colors remain together. The split seed stays in evaluator/preparation records. All four partitions must contain both colors.

Workers receive only `train.csv`, `dev.csv` and `manifest.json`. Final/future labeled rows and the original archive stay in evaluator custody. Public source provenance alone cannot make public labels secret against deliberate reacquisition; effective access and network restrictions require separate controller evidence.

`prepare-settings` preserves disjoint unseen final/future query cutoffs and numerical parameter sets in evaluator custody. No final command is launched automatically. The evaluator may call the domain functions with frozen settings after the parent's freeze gate; these development CLI commands cannot certify that gate.

## Development commands

Launch these through the parent's ORX fixed command, with worker inputs read-only at `/workspace/wine`, code read-only, and a writable `/output` directory:

```sh
python -m experiments.project_research.domains.cli wine \
  --input /workspace/wine --output /output/wine.json --seed 20260909
python -m experiments.project_research.domains.cli duckdb \
  --scale-factor 0.05 --repeats 20 --workload-cycles 4 \
  --output /output/duckdb.json --seed 20260909
python -m experiments.project_research.domains.cli diffusion \
  --grids 48,80 --epsilons 0.1,0.01 --angles 0,0.5235987755982988 \
  --repeats 3 --rhs-count 3 --output /output/diffusion.json --seed 20260909
```

Every output is create-only. `wine.json` creates `wine.events.jsonl` and `wine-artifacts/` alongside it. A failed attempt retains its result, event journal, exception type and partial artifacts; use a new path to retry. Each result records command, code hashes, source identities, package versions, seeds, wall/CPU use and peak RSS. Local compute has no assigned monetary price; a null amount is not zero budget expenditure.

Wine compares pooled histogram boosting and pooled ExtraTrees with separate-color ExtraTrees. It reports red, white and equal-color MAE, plus row-weight MAE for transparency. The strongest observed development comparator is an exploratory choice and is not an unbiased hidden-test estimate. Each retained prediction file includes ordered row identities.

DuckDB reconstructs a parameterized Q1-derived workload on actual `dbgen` data. The baseline aggregates original columns; the candidate creates daily partial aggregates and recombines them. Both pay connection/configuration costs, the candidate pays materialization every arm, and totals include all queries and connection cleanup. Source generation and warmup are measured separately. At least 20 randomized, balanced-order pairs are required. Decimal sums, keys and counts match exactly; floating averages use declared numerical tolerances. A paired bootstrap interval for the ratio of mean total times must have a 95% lower reduction bound of at least 10% to support that threshold in this development session. Independent measurement and unseen parameters remain required. This is not official TPC-H performance.

Diffusion compares SuperLU, Jacobi-CG and smoothed-aggregation-preconditioned CG on PyAMG finite-element stencils. An independently applied local stencil forms the right-hand sides from known nodal solutions and checks residuals after solving. The separate true-solution error check prevents a small residual from hiding a materially wrong solution. Setup is paid once per trial and amortized over the declared right-hand sides; both components and their sum are retained. Every failed or inaccurate method stays in the result and cannot support a speed claim. This is an algebraic solver experiment, not a PDE discretization-accuracy claim.

## Reproduction and checks

Run the same domain command in a fresh ORX execution with a new output name for independent retraining/remeasurement. A rescore only checks existing outputs and does not replace rerunning the method:

```sh
python -m experiments.project_research.domains.cli rescore-wine \
  --input /workspace/wine --result /output/wine.json --output /output/wine-rescore.json
python -m experiments.project_research.domains.cli rescore-diffusion \
  --artifacts /output/diffusion-artifacts --output /output/diffusion-rescore.json
python -m unittest experiments.project_research.test_domains -v
```

Unit tests use small data and numerical fixtures. They verify duplicate grouping, custody/manifest integrity, MAE weighting, query equivalence, paired precision, independent residual/error checks and failure retention. They are not study experiments or autonomous-campaign evidence.

Official API and source evidence is recorded in `source-lock.json`. No paper efficacy claim is based on these documentation pages.
