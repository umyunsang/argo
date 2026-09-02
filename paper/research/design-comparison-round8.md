# Design comparison — round 8/9 competitive analysis

**Purpose:** compare how adjacent controlled studies build their designs, then state explicitly what the local Study A inherits, rejects, or changes. Every row is a retained `FULL_PAPER_READ` with line-anchored locators.
**Status:** comparison only; no local result exists.
**Generated:** 2026-09-02T21:52:42+09:00

## Comparison matrix

| Prior experiment (read level) | Unit and N | Manipulated factor | Baseline / control | Primary outcome | Scoring authority | Budget matching | Uncertainty method | Power / MDE handling | Study A: adopt or reject |
|---|---|---|---|---|---|---|---|---|---|
| SCOPE `2608.03501` FULL | 300 paper-derived design tasks, 7 models | search access; stage isolation; typed operations | CoT-only single call | six 0–5 dimensions with redlines | LLM judge with human agreement checks | same model and task pool | reported per-contrast significance | not reported as MDE | **adopt** endpoint shape and stage isolation; **reject** treating search as monotonic good |
| ResearchClawBench `2606.07591` FULL | 40 dry-lab tasks | end-to-end research pipeline | provided baseline solutions | expert-weighted rubric on final report | expert rubric, target withheld | per-task workspace | not the focus | none | **adopt** hidden-target release; **reject** final-report-only scoring |
| Arbor `2606.11926` FULL | 6 AO tasks + benchmark subset | flat queue vs tree vs tree+insight | flat queue | held-out task metric | execution metric | matched access and workspace budget | Avg@3 over stochastic runs | none | **adopt** matched-budget ablation shape; **defer** as Study B |
| HEP `2607.09195` FULL | 3 materials tasks, 3 runs/condition | explicit hypothesis–evidence–belief state | plan–execute–replan | step shares and transition probabilities | same agent attaches and validates | same goal, tools, model | mean ± SD, transition description | none | **adopt** externalized belief state; **reject** same-agent validation |
| Search diagnosis `2608.01913` FULL | 830 questions, 6 agents | none (observational) | fixed retriever and harness | retrieval vs utilization gap | programmatic trace labels | identical retriever | descriptive correlations | none | **adopt** episode labels and evidence-saturation stop |
| Adaptive-RAG `2403.14403` FULL | 6 QA datasets | complexity-conditioned routing | no-retrieval, single-step, always-multi-step | accuracy and per-query cost | dataset gold answers | per-query cost reported | benchmark deltas | oracle classifier as upper bound | **adopt** conditioning as an inside-C11 mechanism; **reject** as a fifth arm |
| Agent-orchestrated adaptive RAG `2606.05658` FULL | 2 corpora | decomposition and reflection | direct retrieval | score, MRR, Success@5, latency | rubric plus retrieval metrics | none declared | point estimates | none | **adopt** as H-B mixed-effect comparator; **reject** unconditional pipeline growth |
| Controlled orchestration `2608.00685` FULL | 5 backbones × 3 domains, paired items | Self-Refine, BoN, Debate | task-only and optimized CoT | accuracy and weighted tokens | automatic verification | equal optimization budget | stratified paired bootstrap, mixed models | LRT model comparison | **adopt** equal-effort matching and workflow×backbone reporting |
| ResearchGym `2602.15112` FULL | 5 tasks from 2025 venues | full research loop | provided baseline as lower bound | execution metric from source paper | execution grading, no LLM judge | single GPU, ~24 h per task | best@k with mean ± SD | none | **adopt** integrity provisions; **defer** execution grading to Study C |
| Context files `2607.27250` FULL | 17 tasks, 2 agents, 288 runs | persistent external context file | no-context and alternative injection | hidden gold-test pass | programmatic gold tests | 3 strategies × 3 repeats per task | within-task permutation, clustered bootstrap | TOST equivalence plus Monte Carlo MDE | **adopt** manipulation probe and TOST; **treat as direct counterevidence to H-A** |
| Scaffold effects `2606.08529` FULL | GAIA L1–L2, 3 scaffolds × 5 models | scaffold identity | worst/best scaffold contrast | benchmark accuracy | benchmark answers | tasks and conditions fixed across cells | pre-registered comparison | pre-registered effect threshold | **adopt** cost-per-correct and scaffold×model reporting |
| Judge audit `2608.29517` FULL | public essay corpora, repeated calls | judge model and version | human-anchored scores | severity, halo, reliability, drift | many-facet measurement of raters | repeated calls budgeted | generalizability components | replication for stability | **adopt** severity and halo checks; **reject** agreement-only judge validation |
| Trajectory judge `2609.00038` FULL | trajectory set with injected failures | judge granularity | outcome-only judge | silent-failure recovery rate | programmatic rules and rubric judges | cost reported per judge | detection and calibration rates | none | **adopt** step-level judging for silent failures |
| Resolution diagnostics `2605.30315` FULL | 2 public leaderboards, 40+ pairs | none (audit) | displayed pairwise rankings | whether pairs meet a resolution target | paired tests | shared prompts | McNemar and paired bootstrap | explicit resolution target and MDE | **adopt** resolution target before reading any pairwise result |
| Variance components `2607.13304` FULL | repeated prompts across sources | none (measurement design) | single-sample practice | intraclass variance shares | programmatic outcome | fixed resample budget | crossed random effects | precision-versus-budget frontier | **adopt** variance decomposition to allocate repeats |
| Power meta-analysis `2010.06595` FULL | meta-analysis of prior work | none (audit) | published comparisons | achieved statistical power | reported results | not applicable | power computation | typical designs are underpowered | **adopt** as the reason FEC is estimation-only this cycle |

## Where Study A is stronger than the compared designs

1. **Factor separation.** Most rows manipulate one bundled treatment. Study A separates structured research state from dynamic retrieval and estimates their interaction, so a null retrieval effect cannot hide a positive structure effect.
2. **Evidence identity.** No compared row requires every claim to re-derive from committed bytes. Study A binds each design claim to a line-anchored locator and fails closed when a source is unreachable.
3. **Scoring independence by construction.** HEP lets the same agent validate its own evidence and ResearchClawBench scores mostly the final report; Study A separates deterministic redlines, a condition-blind rubric, and a human calibration subset.

## Where Study A is weaker

1. **No execution grading.** ResearchGym inherits metrics from source papers; Study A scores designs that are never run, so construct validity rests on the redline definition. Mitigation: deferred Study C.
2. **Sample size.** Context files used 288 runs and controlled orchestration used five backbones; Study A is capped at 192 episodes on one model, so FEC stays estimation-only.
3. **Single backbone.** Scaffold effects and controlled orchestration both show the effect depends on the model; Study A fixes one model and therefore claims nothing about generality.

## Changes taken into the design this round

| Change | Source rows | Decision record |
|---|---|---|
| Manipulation probe that the structured state was actually consumed | context files | `RD-2026-09-02-09A` |
| Pre-registered equivalence margin with TOST so a null is interpretable | context files, resolution diagnostics, power meta-analysis | `RD-2026-09-02-09B` |
| Judge calibration on severity and halo, dimensions scored in separate calls, step-level review for silent failures | judge audit, trajectory judge | `RD-2026-09-02-09C` |
| Variance-component decomposition to allocate repeats, keeping two repeats for now | variance components | `RD-2026-09-02-09D` (no change to the repeat count) |
