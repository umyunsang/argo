# Existing corpus inventory and scoped gaps

Date: 2026-09-08. This is a structural audit of existing `paper/sources/*source-receipts.json`, `arxiv-metadata*` receipts/XML, and `claim-locators.json`. No paper fulltext was read for this inventory. `FULL_PAPER_READ` below is an existing receipt label, not this agent's reading attestation. Gap judgments concern the retained claim scopes, not every statement in the underlying papers.

## Coverage and identity

- 43 source-receipt files contain 137 distinct source IDs/versions: 129 carry `FULL_PAPER_READ`; 8 have no `reading_level` field (`UNSPECIFIED` in the index). All 137 titles match metadata directly.
- The claim ledger contains 339 locators. 176 belong to those 137 sources; 163 belong to 17 additional IDs with no matching source receipt or metadata in the inspected set. The combined index therefore has 154 source IDs. These 17 entries retain `null` version and no title; guessing is prohibited.
- In particular, `2409.11363` has 3 existing claim locators. It is **not new to the claim corpus**, although its source receipt/version/title are absent from this inspected evidence set.
- Deduplication is by exact ID/version; the index preserves locator scopes, receipt artifact paths/hashes, and metadata provenance. Claim-only entries do not assert a version.
- Machine-readable index: `corpus-index.json`.

## Ten related sources already labeled FULL_PAPER_READ

| Source / version | Exact metadata title | Existing claim scope | Remaining design question |
|---|---|---|---|
| 2605.26340 v1 | ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence | Claim-specific evidence chains; evidence-tagged research representation and writing; type-specific verification and promotion blocking. 3 locators. | Generic claim/evidence typing and promotion gates are already prior work. An incremental ARGO contribution requires testing a narrower mechanism against this scope. Abstract-entailment checking is not wholly deterministic. |
| 2607.12301 v1 | XScientist: A Git-Like Research Protocol for Long-Running Autonomous Scientific Discovery | Research artifact with exploration DAG, code/output nodes, claim anchors, hashes, provenance, and re-execution hooks. 1 locator. | DAG lineage and portable research artifacts alone do not establish originality. Need evidence for comparative value of the selected invalidation/reuse policy. |
| 2606.11926 v1 | Toward Generalist Autonomous Research via Hypothesis-Tree Refinement | Matched-budget flat-queue/tree-without-insights/full-system ablation; narrow task suite and fixed scalar objectives. 2 locators. | Strong tree-plus-insight controls are required before assigning gains to a graph. Multi-objective, cross-branch experimental decision state remains outside the retained claims. |
| 2602.15112 v2 | ResearchGym: Evaluating Language Model Agents on Real-World AI Research | Full research-loop execution grading; expert calibration; isolated single-GPU tasks and integrity provisions. 2 locators. | Long-run evaluation needs executable outcomes, resource accounting, and integrity controls. These claims do not establish that the proposed local task set meets those conditions. |
| 2405.14831 v3 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | Schemaless KG indexing and graph-walk retrieval for multi-hop QA. 2 locators. | Retrieval graphs and research decision-state graphs have different validity targets. Extraction error, graph construction cost, and scientific-task transfer need separate evaluation. |
| 2606.10241 v1 | Regimes: An Auditable, Held-Out-Gated Improvement Loop Demonstrated on LongMemEval with ActiveGraph | Held-out promotion gate with append-only, event-sourced improvement decisions. 1 locator. | Event sourcing plus held-out gating is already prior work. A local mechanism must add a measured benefit beyond those structures. |
| 2608.13417 v1 | Beyond Final Scores: A Systematic Evaluation of Agents for Long-Horizon AI Research and Development | Similar final scores can hide different process bottlenecks; 7 models and 36 long-horizon tasks in its setting. 1 locator. | Process traces, unsuccessful branches, and normalized resource use must accompany end scores; effects are not ARGO evidence. |
| 2608.03860 v1 | SciRet: A Compute-Aware Empirical Study of Retrieval and Reranking for Scientific RAG | Controlled retrieval pipeline; small query set/circular pseudo-label limitation; domain reranker negative result. 2 locators. | Need independently judged scientific relevance and adequate query diversity. Existing retained evidence is too weak for scientific retrieval efficacy or a universal reranking benefit. |
| 2608.01913 v1 | Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents | Fixed-retriever/harness diagnosis separates retrieval gaps from utilization gaps; evidence gain and wasted-tail measures. 2 locators. | Search quality and evidence utilization must be measured separately. A long search trace alone cannot support research-quality or stopping-policy claims. |
| 2604.06236 v1 | LLMs Have Made Failure Worth Publishing | Position argument: publication filters negative results and models inherit positive bias. 1 locator. | This motivates negative-knowledge research but does not establish an operational representation, applicability rule, or controlled benefit for reusing failed experiments. |

## EviGraph and the actual delta

`2608.04738 v2`, **EviGraph: Evidence-Guided Autonomous Research Agents**, already has one locator covering typed operational evidence graphs, weak-node repair, checkpointing, and graph-gated manuscript generation. Its original source receipt has no `reading_level`; that is not evidence of either unread status or complete reading. Reviewing its full v2 text would be a **reading-depth expansion**, not discovery of a new paper/version. A graph/repair/gating package alone overlaps this retained prior-art scope.

The additional search should resolve bounded gaps:

1. **Evidence graphs:** exact update/invalidation semantics, verification dependency handling, comparable controls, and whether effects survive equal backbone, tools, judge, and budget.
2. **Negative knowledge:** typed failed-experiment evidence with scope/conditions, expiry or contradiction handling, and whether reuse reduces repeated failure without suppressing valid new hypotheses.
3. **Strong tree controls:** tree-plus-insight and serious exploration baselines, with equal access/resources; isolate graph topology from memory volume, extra agents, and extra verification.
4. **Long-horizon evaluation:** trace-based efficiency, repeated-run variance, executable outcomes, integrity constraints, and saturation-resistant discrimination.
5. **Scientific retrieval:** independently assessed relevance and evidence utilization, source completeness, literature version identity, and marginal scientific information gained per cost.

## Exa candidate identity comparison

The root supplied these candidate IDs; this inventory does not validate the search claims.

- Already in source receipts: `2608.04738 v2`, `2605.26340 v1`, `2607.12301 v1`, `2606.11926 v1`, `2602.15112 v2`.
- Already in claim locators, receipt/version unresolved: `2409.11363` (3 locators).
- Absent from all inspected receipt/metadata/claim records: `2606.18874`, `2606.21024`, `2608.12847`, `2608.11248`, `2606.12563`, `2603.26499`, `2507.02554`, `2602.02905`, `2510.21652`, `2608.19799`, `2606.26158`.
- The different IDs `2606.11926` and `2606.12563` must never be deduplicated by the shared name “Arbor.”

## Current-byte checks, not a full corpus integrity audit

Five load-bearing source identities were selected. Recorded results and complete hashes are in `corpus-index.json`.

- `2606.11926` fulltext: current bytes match the stored SHA-256.
- `2602.15112` fulltext: current bytes match the stored SHA-256.
- `2608.03860` fulltext: current bytes match the stored SHA-256.
- `2608.04738`: the receipt archive path is missing. Its retained claim source `main_arXiv.tex` exists and matches the locator SHA-256. This verifies the retained claim source, not current retention of the source archive.
- `2605.26340`: the receipt archive path is missing. Both distinct TeX files used by its 3 locators exist and match their locator SHA-256. This verifies those retained claim sources, not current retention of the source archive.

No canonical corpus, manuscript, runtime, credentials, or experiments were modified by this inventory.
