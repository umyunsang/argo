# ARGO paper research context graph

**Status:** living thesis-research projection at the 2 September 2026 evidence cutoff.
**OpenResearch node:** `c11c76ef-640e-4de7-8046-0507b163fa71` (living pre-run graph; no E1--E5 scientific result exists).
**Authority boundary:** this graph organizes public prior work, candidate methods, controls, gaps, and retrieval triggers. It is not ARGO runtime state, experiment lifecycle authority, or evidence of local efficacy.

## Research rule

Literature is an input to hypotheses, methods, comparators, and counterevidence. The presence or absence of a paper never decides a local result. Local efficacy requires immutable executed artifacts under a matched protocol. Detailed literature wording requires retained full source bytes and a reviewed locator.

The graph is refreshed after each meaningful execution outcome. Search terms must be derived from the observed mechanism, protocol, error, metric pattern, or scope rather than from a fixed reading list.

## Current method and experiment map

| Research area | Closest retained methods or experiments | Current ARGO residual | Prospective evaluation | Result-driven retrieval direction |
|---|---|---|---|---|
| Agent reasoning, memory, and orchestration | [ReAct](https://www.alphaxiv.org/abs/2210.03629), [Reflexion](https://www.alphaxiv.org/abs/2303.11366), [MemGPT](https://www.alphaxiv.org/abs/2310.08560), [AutoGen](https://www.alphaxiv.org/abs/2308.08155), [RAG](https://www.alphaxiv.org/abs/2005.11401), and [RLM](https://www.alphaxiv.org/abs/2512.24601) | One agent owns the complete long-running research design and result-driven revision loop | H1/RQ1–RQ2: research-design validity, method selection, context continuity, and retrieval value | Search from observed planning, memory, retrieval, tool, and coordination failures |
| Coding-harness and programmatic context architecture | [Prime Agent](https://www.alphaxiv.org/abs/2608.23552), [Code as Agent Harness](https://www.alphaxiv.org/abs/2605.18747), [public coding-harness design-space analysis](https://www.alphaxiv.org/abs/2604.14228), [LongHorizon-Harness](https://www.alphaxiv.org/abs/2608.01964), [LoopsBench](https://www.alphaxiv.org/abs/2608.00267), and [Context as an Environment](https://www.alphaxiv.org/abs/2608.21690) | Source-separated differentiation across programmatic context, code action, persistent loop state, delegation, and capabilities | capability map and sourced differentiation matrix; effects deferred | Search missing pi source, direct contrast harnesses, and routing anchors without making absence claims |
| Autonomous experimental design | [SCOPE](https://www.alphaxiv.org/abs/2608.03501), [ResearchClawBench](https://www.alphaxiv.org/abs/2606.07591), [Arbor](https://www.alphaxiv.org/abs/2606.11926), [search-trajectory diagnosis](https://www.alphaxiv.org/abs/2608.01913), and [HEP](https://www.alphaxiv.org/abs/2607.09195) | Separate retrieval access from stage-isolated decision/evidence state; preserve hidden tasks and independent scoring | E5: 2×2 structured-state × dynamic-retrieval pilot | Search only when evidence changes a resource, hypothesis, control, metric, stopping rule, or scoped interpretation |
| Comparison identity | [Rethinking Harness Evaluation](https://www.alphaxiv.org/abs/2607.12227), [HarnessOpt-Bench](https://www.alphaxiv.org/abs/2608.06301), [Evo-Bench](https://www.alphaxiv.org/abs/2608.09096) | Invariant protocol key + per-arm receipts + planned-contrast manifest | E2: false acceptance/rejection, matched budgets, inaccessible held-out state | Positive: seek replications and confounds; null: seek measurement sensitivity; negative: seek analogous mismatches and alternative causal designs |
| Dual refinement | [RSEA](https://www.alphaxiv.org/abs/2606.28374), [Regimes](https://www.alphaxiv.org/abs/2606.10241), [Autogenesis](https://www.alphaxiv.org/abs/2604.15034) | Typed scientific-state/engine-state noninterference beyond versioned held-out promotion | E4: matched unrefined control, task-level discovery control, rollback, contamination, cross-instance probes | Search from the observed promotion/regression signature, affected resource type, and protocol fingerprint |
| Evidence graph and paper lineage | [EviGraph](https://www.alphaxiv.org/abs/2608.04738), [Claim-Locked Reporting](https://www.alphaxiv.org/abs/2608.25336), [claim-aware observability](https://www.alphaxiv.org/abs/2608.18312), [XScientist](https://www.alphaxiv.org/abs/2607.12301), [ScientistOne](https://www.alphaxiv.org/abs/2605.26340) | Joint source-byte, answered-run, exact-contrast, authority/contribution, and final-build identity | E3: known-valid/invalid bundles and evaluator-owned terminal corruptions | Search from missed corruption types, false blocks, stale-link failures, and verifier disagreement |

## Current root-agent research decision

Decision `RD-2026-09-02-01` is provisional and recorded in `paper/research/autonomous-research-decision-ledger.json`; its unexecuted instrument pilot is specified in `paper/research/minimum-executable-experiment.md`. The previous BASE–RETRIEVAL–full comparison bundled too many causal constituents. SCOPE provides direct counterevidence that search access alone is not reliably beneficial, while Arbor shows that tree structure without propagated insight is insufficient. Study A therefore crosses two factors:

| Condition | Structured research protocol | Dynamic retrieval | Identified contrast |
|---|---:|---:|---|
| C00 | No | No | Free-form planning baseline |
| C01 | No | Yes | Main effect of unstructured retrieval |
| C10 | Yes | No | Main effect of stage-isolated decision/evidence state |
| C11 | Yes | Yes | Full treatment and structure × retrieval interaction |

The structured treatment separates resource configuration, protocol construction, and reporting. It records alternatives, rationale, falsifiers, and evidence links as typed graph state. The primary endpoint is fatal-error-free complete experimental design; search count and citation count are not success metrics. Secondary diagnostics separate retrieval gaps from utilization gaps and measure productive, redundant, and unproductive search episodes.

The design cannot launch until three gates close: the treatment workspace must exclude target papers and rubrics, scoring must combine deterministic redlines with condition-blind independent review, and a separate fixed OpenResearch run command must exist for Study A. Pinned ResearchClawBench runner code copies released data and related work but launches a general shell subprocess; that function does not by itself prove filesystem isolation. The current project command validates paper artifacts and is not an efficacy evaluator.

## Outcome-driven retrieval loop

| Outcome class | Context-graph update | Next literature action | Scientific update |
|---|---|---|---|
| Positive | Add the exact protocol, effect, uncertainty, and surviving alternatives | Find independent replications, transfer limits, causal alternatives, and negative counterevidence | Strengthen only the measured scope |
| Null | Record power, sensitivity, variance, and unresolved mechanisms | Find boundary conditions, measurement critiques, effect heterogeneity, and mechanism-distinct alternatives | Do not treat absence of evidence as global falsification |
| Negative | Record regression signature, affected component, and counterevidence | Find analogous failures, incompatible assumptions, safety regressions, and alternative methods | Narrow only the tested protocol; do not close the family |
| Execution failure | Record environment, dependency, command, and first failing artifact | Read primary implementation/specification material for that concrete failure | Update engineering state only; hypothesis remains unanswered |

## Material organization

- `paper/sources/reports/`: retained raw OpenResearch paper reports.
- `paper/sources/report-corrections.json`: rejected stale/unsupported report identity and terminology fields, re-derived from tracked source lines.
- `paper/sources/arxiv-metadata-*.xml` and receipts: exact source/version metadata; round-2 and foundational versioned downloads are bound to retained archive hashes.
- `paper/sources/adaptive-round5-source-receipts.json`: five root-selected full reads, exact archives, extracted TeX manifests, and decision-relevant locators.
- `paper/research/autonomous-research-decision-ledger.json`: candidate designs, non-compensatory eligibility gates, weighted decision criteria, hypotheses, falsifiers, budget invariants, and adaptive update rules.
- `paper/research/capability-map.md`: all 46 sub-capabilities across nine target R&D areas, with current state, work item, validation, phase, and rationale.
- `paper/research/coding-harness-differentiation-matrix.md`: area-7 axes with own, concept, and contrast evidence; unsourced cells remain non-comparable.
- `paper/research/paper-scope-exclusion-decision.json`: public-paper hard exclusions and deterministic source/PDF name-gate receipt.
- Private `paper/sources/arxiv/` plus extracted `paper/sources/tex/`: exact source archives remain private; selected authoritative TeX slices and their hashes are retained for claim re-derivation.
- `paper/sources/claim-locators.json`: 43 scoped source-line supports and counterevidence boundaries, including 11 adaptive-round5 locators re-derived from exact-version TeX.
- `paper/official-thesis-requirements.*`: machine- and human-readable requirements extracted from the department HWP files with the verified rhwp binary.
- `paper/hwp-plan-build-receipt.json`: reproducible official plan-form build with save/reopen, geometry, bounds, and visual-render checks; user-supplied university, department, student number, and name are filled, while major, date, advisor, and signatures remain blank.
- `paper/evidence-matrix.csv` / `.md`: facet coverage and component attribution.
- `paper/context-graph.json`: machine-readable nodes, edges, gaps, and outcome triggers.
- `paper.tex`: current autonomous-R&D manuscript. It reports no ARGO or test-instance efficacy result.
- OpenResearch run logs: sole execution evidence channel for paper validation nodes.

## Open gaps

1. Study A has no evaluator-owned hidden-task release boundary, independent scoring path, or fixed OpenResearch runner; E5 is blocked before launch.
2. The autonomous R&D treatment has not produced a comparative research or harness outcome, and no ARGO efficacy result exists.
3. SCOPE task materials are not publicly located; ResearchClawBench is available but emphasizes final reports and requires process-level extensions for this study.
4. Official versioned OpenTelemetry, W3C PROV, RO-Crate, and pinned OpenResearch source/specification receipts remain incomplete.
5. Human-agent communication, approval burden, interruption, and calibrated trust remain thinly sourced.
6. Area 7 still lacks a confirmed standalone pi paper, two direct coding-harness primary contrasts, and model-routing evidence; the differentiation matrix remains preliminary.
7. Area 9 has no three-paper FULL_READ foundation yet, so dynamic routing remains design-only and fixed in Study A.
8. Future retrieval must follow an observed outcome or named unresolved mechanism; bibliography growth alone is not progress.
