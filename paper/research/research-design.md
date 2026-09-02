# Research design: harnessed LLM-agent system for autonomous R&D

**Status:** preregistration-ready design. The instrument pilot has been **executed** (16 episodes, `paper/experiments/study-a-pilot-receipt.json`) and validated the instruments rather than any hypothesis. No treatment effect is estimated, and confirmation has not started.
**Root design authority:** the root agent selected the questions, factors, endpoints, falsifiers, and resource ceilings from retained evidence; no empirical outcome has been observed.
**Planning deadline:** department plan submission `2026-10-31` (user-confirmed).
**Inputs:** `paper/research/capability-map.md`, `paper/research/autonomous-research-decision-ledger.json`, `paper/research/coding-harness-differentiation-matrix.md`.

## 1. Research questions and necessity

A standalone LLM call has no durable scientific state, evaluator boundary, resource identity, or obligation to preserve null and failed executions. Long-horizon evidence indicates several distinct failure surfaces: experiment-design resource errors and search-induced reasoning degradation (SCOPE, `2608.03501`, FULL), protocol/evidence mismatch in end-to-end research (ResearchClawBench, `2606.07591`, FULL), retrieval versus utilization gaps and wasted search tails (`2608.01913`, FULL), unexternalized belief updates (HEP, `2607.09195`, FULL), and task-state loss in growing contexts (LongHorizon-Harness, `2608.01964`, FULL). Programmatic-context work (`2608.21690`, FULL) provides a direct mechanism for recoverable state without serializing all history into every prompt.

The thesis asks:

- **RQ1:** Does a stage-isolated decision/evidence graph improve experimental-design validity under matched budgets?
- **RQ2:** What is the main effect of dynamic retrieval, and does structured state change that effect?
- **RQ3:** Can hidden-task release, deterministic redlines, condition-blind scoring, and trace diagnostics distinguish scientific quality from polished reports and high search volume?
- **RQ4 (deferred):** After a valid research-state treatment exists, do hypothesis-tree and insight propagation improve held-out artifact optimization?
- **RQ5 (deferred):** After Study A, can query-, role-, and recursion-depth-conditioned model/workflow routing improve the quality–cost frontier relative to one fixed model without increasing fatal errors?

## 2. Falsifiable hypotheses

| ID | Hypothesis | Expected direction / magnitude | Falsifier |
|---|---|---|---|
| H-A | Structured state raises redline-adjusted experimental-design score and FEC relative to free-form notes. | Positive; literature shows large workflow effects, but no local standardized effect is assumed. Confirmatory continuous-score target MDE is 0.63 paired SD at 24 tasks; FEC is reported with CI and may remain underpowered. | Nonpositive structured-state contrast, or gain disappears under deterministic/blinded review. |
| H-B | Retrieval has no presumed positive main effect; unstructured retrieval may be null or harmful. | Two-sided. SCOPE reports five of seven models without significant gain and one degradation. | C01 improves high- and low-level design without extra redlines and the effect replicates under independent scoring. |
| H-C | Structure × retrieval interaction is positive because stage isolation converts retrieved material into decision-relevant evidence. | Positive interaction. No precedent supplies a transportable local effect size. | `(C11−C10)−(C01−C00) ≤ 0`, or retrieval changes citations/search count but no valid decision. |
| H-D (deferred) | A hypothesis tree plus propagated insight improves held-out artifact optimization over a flat queue or a tree without insight. | Positive; Arbor reports large benchmark differences, but cost and task scope prevent current-cycle confirmation. | No held-out advantage, validation-only gain, or benefit disappears under matched budget. |
| H-E (deferred) | Calibrated, query/role/depth-conditioned model–workflow routing improves quality per unit cost over a fixed-model policy. | Positive only within an independently validated candidate pool and verifier regime; no transportable magnitude is assumed. | No Pareto improvement, fatal errors rise, benefit disappears under held-out tasks, or routing decisions fail calibration/fallback gates. |

## 3. Variables and conditions

### Independent variables

- `S`: structured research protocol off/on.
- `R`: dynamic retrieval off/on.

### Conditions

| ID | S | R | Treatment |
|---|---:|---:|---|
| C00 | 0 | 0 | Free-form plan, released packet only, ordinary notes. |
| C01 | 0 | 1 | Free-form plan plus adaptive literature/method search. |
| C10 | 1 | 0 | Stage-isolated configuration→protocol→reporting and typed decision/evidence graph, no search. |
| C11 | 1 | 1 | Structured protocol plus adaptive retrieval linked to decision-change or explicit no-change records. |

### Dependent variables

- redline-adjusted total design score (0–30) and six 0–5 dimensions;
- fatal-error-free complete design (`FEC`), binary;
- retrieval/utilization gaps, productive/redundant/unproductive episodes;
- decision-changing retrieval share, duplicate-query rate, graph errors;
- tokens, calls, wall time, and human interventions;
- retrieval-decision quality inside retrieval-on conditions: share of retrievals that a condition-blind reviewer judges appropriate to the stated need (`RD-2026-09-02-08B`, secondary and possibly underpowered).

### Controls

The treatment backend is pinned to one selector for every condition after a live availability probe, and rubric judging is reserved for a different provider family so judge and treatment do not share a blind spot (`RD-2026-09-02-10C`). Model revision, task packet, clean-session policy, output schema, 32k-token ceiling, 12-call ceiling, 45-minute ceiling, machine class, scorer revision, and zero target-evaluation calls during treatment are fixed. Dynamic model routing is not a Study A factor (`R-ROUTING-DEFER`): LLMRouter (`2608.06867`), budget-aware resample/reroute (`2607.08665`), controlled orchestration (`2608.00685`), and Agora (`2607.09600`) show that routing effects depend on task, budget, verifier, workflow, and backbone. Adding routing now would create at least eight conditions and confound the first two mechanisms.

## 4. Tasks, benchmarks, and data

### Candidate task sources

1. **ResearchClawBench**: public paper-derived dry-lab workspaces and rubrics; final-report emphasis and default runner boundary are insufficient without extension.
2. **SCOPE**: directly aligned 300-task design benchmark, but public task materials have not been located.
3. **Synthetic validity fixtures**: useful for deterministic redline precision/recall, but ineligible as the sole agent-behavior study.

### Selected pilot source

Use four paper-derived dry-lab tasks from four distinct families, sampled by a fixed seed after eligibility filtering. An evaluator-owned preparation step releases only instructions, data, and permitted related work. The root agent does not inspect target studies or scoring rubrics. Target bytes must be absent from source archives, mounts, environment, links, caches, process arguments, and error channels.

The 16-episode instrument pilot (`4 tasks × 4 conditions × 1 clean run`) validates only execution and measurement. Pilot tasks never enter development or confirmation.

The pilot ran on 2026-09-02: 4 tasks x 4 conditions x 1 run, all 16 episodes exited zero, no withheld canary reached any workspace. It produced three instrument corrections rather than an effect. Fabrication redlines fired on 0 of 16 artifacts, so five deterministic structural-completeness checks were added and flag 13 of 16 (`RD-2026-09-02-10B`). The manipulation probe fired on 7 of 8 structured episodes whose scaffold was demonstrably filled, so it was respecified from verbatim echo to filled-field consumption plus carry-through (`RD-2026-09-02-10A`). All four pilot tasks are development data and are permanently excluded from confirmation.

An attribution arm adds a controlled disclosure condition on a fixed two-task subset: the withheld target idea is stated in one sentence without resources, configuration, or code. Comparing disclosed and undisclosed episodes separates ideation failure from configuration failure (`RD-2026-09-02-08C`). Disclosed tasks are burned and never reused in confirmation.

Execution-graded closed-loop replication is not part of this cycle. It is deferred as Study C with an explicit resource RUNBOOK at `paper/research/study-c-runbook.md` (`RD-2026-09-02-08A`), because the reviewed environment requires a GPU and roughly 24 hours per task.

## 5. Metrics and baselines

### Co-primary descriptive endpoints

1. **Redline-adjusted design score**: six SCOPE-style dimensions, with fatal flaws zeroing the affected dimension. The six components are always reported; the total cannot hide a trade-off.
2. **FEC**: every main/ablation/analysis/resource/baseline/metric/uncertainty requirement is complete and no redline occurs.

### Resolution and equivalence reporting

Every pairwise contrast is reported against a pre-registered resolution target, and a contrast that cannot meet it is marked unresolved rather than null (`RD-2026-09-02-09B`). A non-significant structured-state contrast is additionally tested against a pre-registered equivalence margin with TOST on a task-clustered bootstrap, so absence of effect is a bounded claim rather than an absence of power.

### Judge admission

Rubric scores enter the analysis only after a calibration run on a human-anchored subset reports agreement, severity relative to the human anchor, and halo across dimensions; dimensions are scored in separate calls, and a step-level pass reviews trajectories for failures that are silent in the artifact (`RD-2026-09-02-09C`).

### Baselines

- C00 is the minimal persistent free-planning baseline.
- C01 is the unstructured-search baseline and direct counterfactual to “more retrieval is better.”
- C10 isolates structured state without search.
- For deferred H-D, baselines are flat queue and tree without insight; full tree-plus-insight is the treatment.

### Process metrics

Following `2608.01913`, search volume is not capability. Each episode is productive, redundant, or unproductive according to new evaluator-relevant evidence. Errors are retrieval gaps or utilization gaps. A retrieval is decision-changing only if it changes a resource, hypothesis, control, metric, stopping rule, or scoped interpretation.

## 6. Sample size and power

### Instrument pilot

`N=4` tasks and 16 episodes are chosen because one complete factorial block across four task families is the minimum that tests every condition, schema, leakage gate, and budget path more than once. It is not powered for H-A–H-C.

### Confirmatory sizing rule

No effect size is borrowed as if transportable. SCOPE, HEP, Arbor, and long-horizon studies use different tasks and endpoints. The development pilot estimates paired score SD, FEC discordance, task-family ICC, repeat variance, and judge–human disagreement. Confirmatory N is simulated from those values with family-level resampling.

Resource planning uses `24 independent tasks × 4 conditions × 2 repeats = 192 episodes` as a hard current-cycle ceiling, not a predetermined sample. With two-sided familywise alpha 0.05 across two co-primary endpoints and 80% power:

- at 24 paired tasks, the approximate continuous paired-score MDE is about `0.63 SD` before cluster/design inflation;
- the 95% CI half-width for a standardized paired mean is about `0.42 SD` before inflation;
- for binary FEC with absolute paired difference 0.15, approximate McNemar requirements range from 85 to 155 pairs as total discordance ranges 0.25–0.45, beyond the ceiling;
- with difference 0.25, the corresponding range is approximately 29–55 pairs, still often above 24.

Therefore FEC is a protected co-primary validity outcome but may be estimation-only in the current cycle. If pilot-based power requires more than 24 tasks, confirmation does not launch under the current resource plan; the study is narrowed or a resource decision is requested.

## 7. Procedure and reproducibility

1. Freeze task eligibility, release manifest, conditions, output schema, redlines, metrics, scorer, and budgets.
2. Run failing-first hidden-evidence probes and deterministic fixture tests with `experiments/study_a/release_sandbox.py`, verified by `experiments/study_a/test_release_sandbox.py`, whose six probes must fire on deliberately corrupted fixtures: edited or bypassed scoring code, released-task leakage into the scored artifact, and hardcoded metric values (`RD-2026-09-02-08C`, from `2602.15112`).
3. Create a separate experiment project with one fixed command: `/usr/bin/python3 experiments/study_a/run_episode.py`.
4. Encode conditions only in committed configuration. C00 is baseline; C01/C10/C11 are co-equal first-round children.
5. Start each episode in a clean capability sandbox; capture delivered prompt, tools, queries, graph mutations, output, tokens, and timestamps.
6. Terminate treatment before one-way artifact release to the evaluator.
7. Score deterministically first, then condition-blind rubric review. Human-review a calibration subset.
8. Persist configuration, hashes, metrics, compact summary, and failure class in immutable experiment logs.
9. Exclude instrument and development tasks from confirmation.
10. Analyze only the complete preregistered block.

Reproduction requires exact task-release hashes, model revision, capability profile, condition config, scorer revision, and source artifact hashes. Product-internal provider names and configuration files are not manuscript content.

## 8. Falsification and stopping

### Prelaunch failure

Any hidden-byte access, undeclared tool, schema difference, scorer-label exposure, missing effective configuration, or target-evaluation query blocks launch.

### Execution stopping

Two consecutive infrastructure-only failures stop and repair the same provisional node. They do not update scientific hypotheses. Any leakage, budget mismatch, or scorer identity mismatch invalidates the whole block.

### Retrieval stopping

Stop a retrieval line when new evidence does not change a hypothesis, method, resource, control, metric, stop rule, or scope and sufficient independent support exists. Search count and bibliography growth are not progress.

### Scientific stopping

Interpret only after every condition completes on the frozen block. Positive, null, negative, and execution-failure outcomes all remain. An opened confirmatory task becomes development evidence for any descendant repair.

## 9. Resources, cost, and calendar

### Allowed development

Configuration, skills, workflows, protocols, evaluation fixtures, and external experiment harnesses on the public reference base are allowed. New native runtime development and instance-specific work are excluded. Six capability groups confirmed in Q-0002 remain design-only/follow-up.

### Token and time ceilings

Instrument pilot: 512k treatment tokens plus 128k scoring tokens, total 640k. Four concurrent slots imply at most about three treatment hours plus setup/scoring; sequential maximum is 12 hours.

Confirmatory hard cap: 192 episodes ×32k = 6.144M treatment tokens; scoring cap 1.536M; total 7.68M. Four slots imply a 36-hour treatment ceiling. Dollar cost remains unset until effective model pricing and cached-token accounting are bound to a receipt.

### Planning schedule to department deadline

| Date | Milestone |
|---|---|
| 2026-09-02–09-15 | nine-area literature map, capability map, comparable experiments, design rationale |
| 2026-09-16–09-25 | hidden-release and evaluator preflight fixtures; fixed-runner design |
| 2026-09-26–10-05 | 16-episode instrument pilot if gates pass |
| 2026-10-06–10-15 | pilot diagnostics, variance/discordance estimates, design revision |
| 2026-10-16–10-24 | preregistration candidate and plan/thesis method synchronization |
| 2026-10-25–10-31 | department plan finalization, review buffer, submission by 2026-10-31 |

## 10. Validity threats and mitigations

| Threat | Consequence | Mitigation / residual risk |
|---|---|---|
| Public-task familiarity | target leakage without file access | disjoint tasks, byte isolation, contamination questions; model pretraining remains unobservable |
| Same-family model judge | correlated blind spots | deterministic redlines + blinded judge + human calibration; residual shared-model bias |
| Report-quality anchoring | polished prose mistaken for science | separate process/artifact metrics; presentation excluded from efficacy |
| Task-family heterogeneity | unstable aggregate | paired tasks, family bootstrap, no repeat-as-unit inflation |
| Search budget asymmetry | retrieval effect confounded by compute | common token/call/time ceilings and exact delivered-context logs |
| Graph overhead | lower score from interface burden | measure tool/time cost and graph errors; include C10/C11 comparison |
| Benchmark-target anchoring | re-discovery not novelty | scope conclusions to experimental-design validity, not scientific discovery |
| Routing/model variation | mechanism confound | fixed model in Study A; routing deferred |
| Structured state delivered but unused | a null H-A confounds "does not help" with "never read" | manipulation probe quarantines episodes whose artifact never cites a decision-relevant state field |
| Judge severity drift between versions | treatment effect confounded with rater bias | severity and halo diagnostics against a human anchor; pinned judge revision |
| Repeat allocation chosen by convention | wasted episodes on the wrong variance source | pre-registered crossed variance decomposition before any confirmatory allocation |

## 11. Design rationale and comparable experiments

### Design rationale records

| Choice | Alternatives reviewed | Evidence | Reasoning | Expected effect / risk | Falsifier |
|---|---|---|---|---|---|
| 2×2 factors | bundled 3-arm; synthetic validator only; 2×2 factorial | SCOPE `2608.03501` FULL; Arbor `2606.11926` FULL | Separates search from structured state and estimates interaction without an 8-arm routing factor. | Better attribution; risk of interface overhead. | interaction unidentifiable or budgets differ |
| Stage isolation + typed graph | free notes; flat graph; stage-isolated graph | SCOPE FULL; EviGraph `2608.04738` FULL; Arbor FULL | Low-level resources and high-level protocol interfere; hierarchy without insight is insufficient. | fewer redlines; risk anchoring/bureaucracy | no score/FEC gain under blind scoring |
| Hidden paper-derived tasks | synthetic fixtures; public target; hidden target | ResearchClawBench `2606.07591` FULL | Open-ended design needs external anchor, but target bytes must be absent. | credible scoring; risk target imitation. | leakage or target-only judge behavior |
| Redline-adjusted score + FEC | total score only; FEC only; co-primary | SCOPE FULL; ResearchClawBench FULL | Continuous score gives power; FEC preserves scientific validity. | sensitivity plus safety; multiplicity and binary underpower. | component trade-offs hidden or redlines misclassified |
| Fixed model in Study A | dynamic routing; routing-only first; fixed | LLMRouter `2608.06867`; resample/reroute `2607.08665`; controlled orchestration `2608.00685`; Agora `2607.09600` — FULL | Routing quality depends on task, budget, verifier, workflow, and backbone; including it now doubles conditions and confounds state/retrieval. | clean attribution; limited model generality. | fixed-model results fail to transfer, or a later matched routing study clears power, verifier, and candidate-pool gates |
| Layered protocol boundary | one monolithic protocol; application-specific messages; layered tool/agent/human protocols | protocol taxonomy `2606.19135`; CHAP `2606.09751` — FULL | Tool access, peer work, and accountable human collaboration have different counterparties, payloads, state, discovery, and authority semantics. | composability and auditability; evolving specs and draft human layer. | versioned interop or non-bypass tests show the layering loses required state or authority |
| Corpus-specific RAG pipeline | dense-only; sparse-only; hybrid + generic reranker; adaptive hybrid + validated reranker | InSemRAG `2606.01240`; SciRet `2608.03860`; adaptive RAG `2606.05658` — FULL | Chunking, intent, corpus scale, and reranker domain transfer change retrieval quality; extra decomposition/reranking can harm precision or latency. | better evidence coverage; risk of complex self-evaluation and repair overhead. | independent relevance labels show no benefit or fatal/context errors increase |
| Evidence-saturation stop | hard call cap; model self-stop; evidence stop | search diagnosis `2608.01913` FULL | 77.5–93.6% no-new-evidence episodes and wasted tails make effort a bad endpoint. | lower waste; risk premature stop. | missed evaluator-relevant evidence rises |
| Current-cycle capability slice | all 46 capabilities; validator only; connected 10-function slice | capability map + SCOPE/HEP/ResearchClaw FULL | Tests treatment and measurement prerequisites within non-native boundary. | executable causal path; limited coverage. | slice still requires native changes |

### Comparable experiments by hypothesis

| Hypothesis | Prior experiment | Task / N | Metric | Baseline | Reported effect | Statistics / use here |
|---|---|---|---|---|---|---|
| H-A | SCOPE `2608.03501` FULL | 300 paper-derived tasks, 19 areas | six 0–5 dimensions, total 0–30, redline | CoT-only / CoT+Search; OptED ablations | stage isolation consistently improves three tested models; full workflow HL +1.6 and LL +1.2 on average | paper reports significance for selected contrasts; exact standardized effect not transported |
| H-A | HEP `2607.09195` FULL | 3 materials tasks, n=3 runs/condition | step shares and transition probabilities | plan–execute–replan, same goal/tools/model | baseline 83% tests, 0% belief updates; HEP externalizes full cycle | mean±SD/transition description; supports process metric, not FEC MDE |
| H-A | LongHorizon-Harness `2608.01964` FULL | 3 long-horizon benchmarks; exact task N differs by benchmark | PassRate/binary completion | same backbone and native execution backend | 51.8→80.7, 69.7→77.2, 2.8→8.3 in reported settings | matched benchmark comparisons; scope prevents direct effect transfer |
| H-B | SCOPE `2608.03501` FULL | 300 tasks; 7 models | design score/redline | CoT-only vs CoT+Search | five models no significant total change; GPT-5.2 18.22→16.77; one redline 7.67→14.00 | direct counterevidence; statistical test details not located in scoped source |
| H-B | search diagnosis `2608.01913` FULL | 830 questions, 6 agents | recall, accuracy, calls/context, gap types | fixed retriever/harness across agents | recall–accuracy r=.99; context–accuracy r=.16; 77.5–93.6% episodes no new evidence | descriptive six-agent correlations; informs diagnostics, not causal MDE |
| H-B | Adaptive-RAG `2403.14403` FULL | 6 QA datasets; benchmark-native N | accuracy and per-query cost/latency | no-retrieval, single-step, and always-multi-step strategies | complexity-conditioned routing is reported more efficient than always-multi-step, with an oracle classifier as upper bound | positive conditioning precedent; silver labels are derived from the same strategies |
| H-B | Self-RAG `2310.11511` FULL | 6 tasks; benchmark-native N | task metrics plus support/utility judgements | indiscriminate retrieval and standard RAG | on-demand retrieval with explicit relevance/support judgements replaces always-retrieve | retrieval-decision precedent; critique tokens are self-generated, so support is not independently verified |
| H-A | HippoRAG `2405.14831` FULL | multi-hop QA benchmarks | accuracy, retrieval cost, latency | iterative retrieval and single-step dense baselines | graph-indexed single-step retrieval reported cheaper and faster than iterative retrieval at comparable or better accuracy | graph-state precedent for the structured condition; ratios do not transfer to design tasks |
| H-B | Agent-Orchestrated Adaptive RAG `2606.05658` FULL | 2 contrasting corpora; benchmark-native N | retrieval score, MRR, Success@5, citation/coverage, latency | direct/naive retrieval vs decomposed and reflective paths | decomposition helps the structured corpus but harms ranking on MuSiQue; reflection adds latency without consistent quality gain | direct retrieval-structure counterevidence; small assisted corpus and heuristic routing limit transfer |
| H-C | SCOPE `2608.03501` FULL | 300 tasks; six OptED model evaluations | HL/LL dimensions and redline | CoT+Search, stage-only, T-A-O, full | stage isolation consistent; T-A-O and norms add model-dependent gains | component ablation directly motivates interaction |
| H-C | Arbor `2606.11926` FULL | 6 AO tasks + MLE-Bench Lite; stochastic methods Avg@3 | held-out task metrics / Any Medal | flat queue; tree without insight | full 81.82% vs 63.64% no-tree and 54.54% no-insight on MLE Lite | matched access/budget; tests structure+insight complementarity |
| H-C | EviGraph `2608.04738` FULL | ARC-Bench-ML and NanoResearch-20 | claim support and data consistency | end-to-end research-agent baselines | +40.19% claim support over strongest baseline; 87.73% data consistency | exact task N/statistical uncertainty not used for local power |
| H-D | Arbor `2606.11926` FULL | 6 AO tasks, Avg@3 where stochastic | held-out gain/transfer | coding-agent baselines and tree ablations | >2.5× average relative gain; direct ablation above | principal deferred analogue |
| H-D | AHE `2604.25850` FULL | 10 evolution iterations + transfer benchmarks | pass@1, tokens, transfer | seed, human-designed, self-evolving baselines | 69.7→77.0 and reported transfer/ablation effects | observability/evolution precedent; not current-cycle effect |
| H-D | HarnessOpt-Bench `2608.06301` FULL | benchmark-native harness tasks | held-out target score and resource use | optimizer candidates under fixed budget | prior benchmark effects retained but not local | supplies trusted boundary/budget method |
| H-E | LLMRouter `2608.06867` FULL | 4,767 queries, 8 test sets, 5 tracks | task quality, inference cost, weighted reward | fixed smallest/largest models and 16+ router implementations | no router dominates all tasks or budgets; multi-round routing gives no consistent gain | common candidate matrix and frontier evaluation; external pool only |
| H-E | Resample or Reroute `2607.08665v1` FULL | 4 regenerated benchmark pools; budget sweep | expected correctness, spent cost, sequential rounds | single route, one-commit, best-of-K, cascade, random allocation | favorable frontier in tested regimes; gains shrink or invert with weak verifier | reviewed v1; cost proxies and verifier regimes bound transfer |
| H-E | Controlled orchestration `2608.00685` FULL | 5 backbones × 3 domains, paired difficulty-stratified items | accuracy, weighted tokens, workflow–backbone interactions | task-only and optimized CoT vs Self-Refine, best-of-N, debate | moderate benchmark-dependent gains at about 2–4× token use; difficulty alone does not predict benefit | equal optimization budget and paired bootstrap; model/workflow-specific |
| H-E | Agora `2607.09600v2` FULL | 5 main benchmarks, matched candidate pools | accuracy, calibrated confidence, cost/latency-sensitive bids | strong/weak fixed models, random, cascades, learned routers | improves or remains competitive; calibration failure and distribution shift delimit gains | candidate mechanism for subtask routing, not current-cycle evidence |

The active H-A–H-C hypotheses and deferred H-D each have at least three comparable full-read experiments. H-B now includes a direct retrieval-structure comparison with negative and mixed effects. H-E is deferred but its routing rationale is supported by the three comparable studies below; none supplies a transportable local effect size.

## 12. Reference mapping

| Design choice / claim | Source ids and read level |
|---|---|
| harness necessity beyond standalone generation | `2608.03501`, `2606.07591`, `2608.01964`, `2608.01913` — FULL |
| programmatic context and recoverable state | `2608.21690`, `2512.24601`, `2310.08560` — FULL |
| code-mediated agent harness | `2605.18747`, `2210.03629`, `2608.23552` — FULL |
| stage isolation and redlines | `2608.03501` — FULL |
| typed evidence graph | `2608.04738`, `2409.05556`, `2605.26340` — FULL |
| explicit hypothesis/evidence cycle | `2607.09195` — FULL |
| hidden tasks and rubric limitations | `2606.07591` — FULL |
| retrieval/utilization/stopping diagnostics | `2608.01913` — FULL |
| tree and insight propagation | `2606.11926` — FULL |
| deterministic held-out evaluation | `2608.09096`, `2608.06301`, `2608.25336` — FULL |
| dynamic model and workflow routing | `2608.06867`, `2607.08665v1`, `2608.00685`, `2607.09600v2` — FULL; deferred from Study A |
| agent/tool/human protocol layers | `2606.19135`, `2606.09751`, `2308.08155` — FULL; official evolving specifications still require version pins |
| RAG chunking, hybrid retrieval, reranking, adaptive orchestration | `2005.11401`, `2606.01240`, `2608.03860`, `2606.05658` — FULL |
| manipulation probe and equivalence testing for a null | `2607.27250` — FULL |
| scaffold elicitation gap and cost-per-correct reporting | `2606.08529` — FULL |
| judge severity, halo, drift, and step-level review | `2608.29517`, `2609.00038` — FULL |
| resolution targets, variance allocation, and power norms | `2605.30315`, `2607.13304`, `2010.06595` — FULL |
| complexity-conditioned retrieval and retrieval decisions | `2403.14403`, `2310.11511` — FULL |
| graph-indexed memory as a retrieval substrate | `2405.14831` — FULL |
| execution-graded closed-loop research and integrity provisions | `2602.15112` — FULL; deferred Study C |
| vector-database products and personalized memory | product/spec and privacy evidence gaps; design-only/follow-up |

## Supersession record

This document absorbs and replaces `paper/research/minimum-executable-experiment.md` as the active preregistration design. The earlier proposal remains a historical decision artifact and supplies no result authority.
