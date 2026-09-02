# Minimum executable experiment unit: Study A instrument pilot

**Status:** preregistered proposal; unexecuted; not efficacy evidence
**Owner:** root agent session
**Decision record:** `paper/research/autonomous-research-decision-ledger.json` (`RD-2026-09-02-01`)
**OpenResearch rule:** one fixed command; treatment differences live only in committed configuration; answered nodes are immutable.

## 1. Research purpose

The first executable unit does not attempt to prove that the full autonomous R&D harness improves research. It tests whether a four-condition experimental-design comparison can be executed without hidden-evidence leakage, budget mismatch, evaluator self-attestation, or output-schema failure. A passing pilot licenses sample-size planning; it does not support an efficacy sentence in the thesis.

The design follows five full-paper reads selected by the root agent:

- [SCOPE](https://www.alphaxiv.org/abs/2608.03501) separates high-level protocol planning from low-level resource configuration and reports direct counterevidence to naive search access.
- [ResearchClawBench](https://www.alphaxiv.org/abs/2606.07591) supplies hidden-target, paper-derived task and rubric patterns but mainly scores final reports.
- [Arbor](https://www.alphaxiv.org/abs/2606.11926) distinguishes a flat queue, a tree without propagated insight, and a full tree-plus-insight system under matched access and budgets.
- [long-horizon search diagnosis](https://www.alphaxiv.org/abs/2608.01913) separates retrieval from utilization gaps and measures evidence gain and wasted search tails.
- [HEP](https://www.alphaxiv.org/abs/2607.09195) compares explicit hypothesis/evidence operations with planning under the same goal, tools, and model, while identifying same-agent evidence validation as a limitation.

All five are `FULL_PAPER_READ` records with exact-version source archives and reviewed locators. Their results are prior evidence, not local outcomes.

## 2. Unit of randomization and task sample

The unit is one `(task, condition, clean session)` research-design episode. The instrument pilot uses four paper-derived dry-lab tasks, deterministically sampled from four distinct task families after eligibility filtering. The root agent sees only released task packets. It does not inspect target papers or evaluator rubrics.

The pilot has `4 tasks × 4 conditions × 1 clean session = 16 episodes`. This is the smallest complete factorial block that exercises every condition on more than one task family. It is intentionally too small for an efficacy estimate. No p-value, confidence interval, or superiority claim from these 16 episodes enters the thesis.

If the pilot passes, a separate development pilot estimates:

- paired binary discordance for fatal-error-free completion;
- within-task stochastic variance for six design dimensions;
- task-family intraclass correlation;
- judge–human disagreement;
- token and wall-time dispersion.

The confirmatory task and repeat counts are selected by simulation from those quantities. Pilot tasks are excluded from confirmation.

## 3. Conditions

| ID | Structured protocol | Dynamic retrieval | Execution path |
|---|---:|---:|---|
| `C00` | No | No | Prime Agent receives the released task packet and writes a free-form plan. Research/search tools and graph mutation are absent from the capability profile. |
| `C01` | No | Yes | Same task, model, and budget; literature/search tools are enabled, but state is ordinary notes and no typed graph or stage gate is available. |
| `C10` | Yes | No | Search is disabled. The agent must use stage-isolated configuration, protocol, and reporting records plus typed decision/evidence graph operations. |
| `C11` | Yes | Yes | Both stage-isolated graph operations and adaptive retrieval are available. Retrieval must link to a decision change or an explicit no-change record. |

The structured protocol requires: candidate alternatives, selected resource/method, rationale, evidence dependency, matched control, metric, uncertainty method, falsifier, stopping rule, and descendant-only revision history. It does not reveal evaluator facts.

## 4. Fixed execution contract

Create a separate OpenResearch project only after the runner passes local preflight. Every node inherits exactly:

```text
/usr/bin/python3 experiments/study_a/run_episode.py
```

The script reads committed `experiments/study_a/config.json`; task IDs and condition profiles are committed code/config differences, never environment variables or command-line knobs. The condition nodes form one first-round bush: `C00` is the baseline and `C01`, `C10`, and `C11` are co-equal children.

The runner:

1. verifies the release manifest and hashes;
2. constructs a clean workspace containing only the released task packet;
3. starts the same Prime Agent model revision in a filesystem and capability sandbox;
4. enforces the condition tool profile and common budgets;
5. captures delivered prompt, tools, queries, graph mutations, output plan, tokens, tool calls, and timestamps;
6. closes the treatment process before scoring;
7. passes only the final artifacts to the evaluator-owned scoring process;
8. prints a compact result and configuration summary to stdout for `orx logs`.

No DeepVoice data, files, outputs, or identifiers are used.

## 5. Hidden-evidence boundary

The target paper and rubric may not exist in the treatment source archive, treatment workspace, parent-readable mounts, environment, prompt, tool results, or network routes. Prompt omission is not a security boundary.

Failing-first preflight must prove that a deliberately malicious treatment process cannot:

- traverse to target or rubric paths;
- enumerate evaluator filenames or hashes;
- read a target through symlink, hardlink, archive, environment variable, inherited descriptor, process argument, cache, or error message;
- query the evaluator before treatment termination;
- infer condition-specific evaluator feedback.

The pinned ResearchClawBench runner copies `data/` and `related_work/` but launches a general shell subprocess in its workspace; that function does not itself prove filesystem isolation. Study A therefore uses a stricter release/sandbox boundary rather than assuming the upstream prompt convention is sufficient.

## 6. Budget invariants

All conditions receive the same upper bounds:

- model and revision: identical `openai-codex/gpt-5.6-sol`;
- model-token budget: 32,000 input-plus-output tokens per episode;
- tool-call budget: 12 calls per episode;
- wall time: 45 minutes per episode;
- target-evaluation queries during treatment: zero;
- evaluator revision and scoring prompt: identical and condition-blind;
- task information and output schema: identical;
- machine class and clean-session policy: identical.

Search-disabled conditions retain the same total token and wall-time ceilings; their unused search capability is not reallocated as hidden evaluator access. Search results count against the common context and tool budgets.

Pilot upper bound: `16 × 32,000 = 512,000` treatment tokens. Condition-blind scoring is capped at 8,000 tokens per episode, adding at most 128,000 tokens. Total model-token ceiling is 640,000. With four concurrent episode slots, the 45-minute cap implies at most three hours of treatment wall time plus scoring and setup; sequential worst case is twelve hours. Dollar cost is not asserted until the effective model price and cached-token accounting are captured.

## 7. Outcomes

### Primary instrument endpoint

`FEC` (fatal-error-free complete design) is one only when all six design dimensions are present and no redline occurs:

- main experiment;
- ablation experiment;
- analysis experiment;
- dataset/resource configuration;
- baselines and controls;
- metrics and uncertainty.

Redlines include fabricated resources, incompatible metrics, constraint violation, undeclared arm differences, target/rubric access, post-outcome protocol change, execution failure reported as hypothesis falsification, or a conclusion broader than the released task.

### Secondary diagnostics

- six dimension scores, retained separately;
- retrieval gap and utilization gap;
- productive, redundant, and unproductive search episodes;
- evidence recall/coverage when evaluator relevance labels exist;
- fraction of retrievals that change a hypothesis, resource, control, metric, or stopping rule;
- duplicate-query rate and evidence-saturation tail;
- graph mutation count and invalid-edge count;
- tokens, tool calls, wall time, and human intervention.

Presentation quality, citation count, search count, and report length are not efficacy endpoints.

## 8. Hypotheses and falsifiers

- **H-A — structured-state main effect.** `C10/C11` improve FEC relative to `C00/C01`. Falsified if the paired contrast is not positive or disappears under deterministic/condition-blind review.
- **H-B — retrieval is not presumed beneficial.** Estimate the retrieval main effect without a directional superiority claim. Counterevidence to the present expectation is consistent C01 improvement across high- and low-level design without additional redlines.
- **H-C — positive interaction.** `C11 − C10` exceeds `C01 − C00` because structure converts retrieval into decision-relevant evidence. Falsified if the interaction is nonpositive or retrieval only increases citations/searches.

A pilot cannot confirm these hypotheses. It can only show that their contrasts and measurements are executable.

## 9. Pilot admission and stopping rules

Do not launch the OpenResearch pilot until all are true:

1. malicious leakage probes fail to obtain hidden bytes;
2. every condition profile rejects undeclared tools;
3. the four conditions produce the same output schema;
4. deterministic redlines match manual review on fixture plans;
5. condition labels are absent from scorer inputs;
6. the fixed command prints configuration, hashes, outcomes, and compact summary;
7. no target or rubric file appears in the source archive.

During execution, two consecutive infrastructure-only failures stop and repair the same provisional node. They do not update H-A through H-C. Scientific stopping occurs only after the complete 16-episode block; partial condition completion cannot be interpreted. Any leakage, budget mismatch, scorer identity mismatch, or target-evaluation access invalidates the full pilot block.

## 10. Result-driven next action

- **Preflight pass:** create the separate Study A OpenResearch project and the first-round condition bush.
- **Leakage failure:** keep E5 blocked; search only the concrete sandbox/capability failure and repair preflight.
- **Measurement disagreement:** improve deterministic checks and human calibration; do not add treatment episodes.
- **Pilot positive pattern:** plan a disjoint development pilot and search for replications and confounds.
- **Pilot null pattern:** inspect variance, rubric sensitivity, and task heterogeneity before changing the treatment.
- **Pilot negative pattern:** inspect graph overhead, cross-stage anchoring, and evidence-utilization failures; narrow only the tested protocol.

No branch proceeds to manuscript results until immutable OpenResearch logs and artifacts answer a preregistered confirmatory node.
