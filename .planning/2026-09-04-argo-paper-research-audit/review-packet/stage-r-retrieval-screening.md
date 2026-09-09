# Stage R — Retrieval-Policy Screening

Status: **DEVELOPMENT-ONLY DRAFT; NO MODEL EPISODE OR SPEND AUTHORIZED**  
Created: 2026-09-04T15:43:42+09:00

## Question

Which fixed retrieval policy supplies evidence for the main G×C×F study under a controlled corpus and budget? This
stage selects a policy, not a product, and makes no scientific-benefit claim about a provider.

## Arms

1. **NONE:** no external retrieval; only the sealed task packet and corpus metadata.
2. **SEMANTIC_VECTOR:** fixed-budget semantic/vector retrieval over the sealed corpus snapshot.
3. **CITATION_ENTITY_GRAPH:** traverse a prebuilt citation/entity graph under the same maximum query, token, time, and
   cost budget.

The adapter/provider is an implementation detail. If a provider changes, the arm is a new version and must be screened
again. **Retrieval is the only varied surface:** reranker, generator, feedback policy, citation verification, prompts,
and maximum budgets are byte-identical across arms. This prevents the combined retrieval+self-feedback design in
OpenScholar (`openscholar_self_feedback_pipeline`) from contaminating the retrieval-policy contrast.

## Development set and blinding

Use only a development literature-task set that is permanently excluded from Stage 1 confirmation. Freeze before any
outcome is visible: task IDs/hashes, acceptable source identifiers, corpus cutoff and full corpus/index digest,
chunking, embedding model/version, provider/API revision, query template, top-k, reranking/RCS policy, graph schema,
query/tool/token/time/cost budgets, retry rule, and scorer. The scorer is blind to arm. All API/web results are materialized before screening; the manifest stores each document,
source ID, retrieval timestamp, licence/access status, bytes and hash. **No live corpus mutation or live search occurs
during scoring.** OpenScholar mixes a datastore, Semantic Scholar, and web APIs (`openscholar_three_retrieval_sources`),
while PaperQA2's reported server used non-public full-text search and citation traversal
(`paperqa2_open_source_infrastructure_gap`); interface names alone do not establish reproducibility.

## Outcomes

Following the metric separation in PaperQA2 (`paperqa2_litqa_metrics`), report:

- **answer precision:** correct / answered;
- **answer accuracy:** correct / all tasks;
- **source recall:** tasks whose answer attributes the frozen gold/acceptable source identifier / all tasks;
- recall after each stage: candidate search, vector/graph selection, evidence extraction, final attribution;
- evidence coverage, citation precision, cited-but-unsupported rate, justified abstention, latency, retrieval and model
  tokens, tool calls, and cost.

Citation support is scored on atomic claims linked to exact source spans. A sentence-level sensitivity analysis is
reported because OpenScholar notes that adjacent citations can make sentence-level precision/recall overly strict
(`openscholar_evaluation_limitations`). LLM-judge quality scores are secondary only.

A task can retrieve the right source and still answer incorrectly, or answer correctly from an acceptable alternative
source. Keep both facts; do not force them into one label or opaque composite.

## Selection predicate

A policy is eligible only if the task-cluster 95% lower bound for citation precision is no worse than NONE by 0.05 and
the upper bound for cited-but-unsupported rate does not exceed NONE by more than 0.02. Among eligible policies, select
the largest lower 95% bound for answer accuracy. If two bounds differ by less than 0.02, tie-break by source recall,
then lower conservative cost, lower latency, and arm ID. If neither retrieval arm clears the constraints, freeze NONE
for Stage 1. This rule is frozen before Stage R outcomes.

## Analysis and stopping

Treat the literature task as the unit. Use paired task-cluster bootstrap 95% intervals. Run a zero-cost scorer
certification first. Sample size and any paid envelope remain pending a disjoint power/cost simulation and human
approval. No Stage R outcome may alter the G×C×F confirmatory hypotheses.

## Counterevidence boundary

SCOPE's full-read locator `scope_search_counterevidence` reports that search mode alone did not reliably improve design
quality. Therefore retrieval is frozen as a controlled policy, not presumed beneficial. Product documentation proves
interface availability only.
