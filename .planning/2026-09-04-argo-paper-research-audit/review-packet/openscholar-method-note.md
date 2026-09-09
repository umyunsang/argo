# OpenScholar Full-Read Method Note — Corpus, Factor-Separation, and Evaluation Boundaries

Source: Asai et al., *OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs*, arXiv:2411.14199.  
Read receipt: `openscholar-full-read-receipt.json` SHA-256 `b3b54d46e10bf5e2b70f273362c4017639b521626a9f3bf722be0f53016379e0`  
Locators: `openscholar-locators.json` SHA-256 `cd6979a609086dce2365b5623005be9e5e0ddf47a517620ebc05a8141e998d8f`

## What transfers to Stage R

A literature answer should identify papers, link citations to supporting passages, and synthesize the query
(`openscholar_task_citation_span`). Datastore version and cutoff matter: the study distinguishes a January-2023 v2
corpus used for evaluation from an October-2024 v3 corpus (`openscholar_datastore_cutoff`). Stage R must freeze corpus
bytes, index, cutoff, and acceptable source identities before outcomes.

Retriever and reranker are separate surfaces (`openscholar_reranker_surface`). The reported candidate pool also mixes a
local datastore with Semantic Scholar and web APIs (`openscholar_three_retrieval_sources`). Live API results are not a
fixed corpus. ARGO screening therefore materializes and hashes every candidate corpus before comparison; no live search
is allowed during scoring.

## Factor separation

OpenScholar couples retrieval, reranking, iterative self-feedback, extra retrieval, and citation verification
(`openscholar_self_feedback_pipeline`). Stage R varies retrieval policy only. Reranking, generation, feedback, and
attribution must be byte-identical across NONE/SEMANTIC_VECTOR/CITATION_ENTITY_GRAPH, otherwise R is confounded with F
or the generator. The paper's system-level results cannot identify an isolated local retrieval effect.

## Evaluation boundary

Citation precision/recall are sentence-level and the authors warn that adjacent citations can make them overly strict
(`openscholar_citation_metrics`, `openscholar_evaluation_limitations`). ARGO uses atomic claim units with explicit source
spans and reports adjacent-citation sensitivity separately. Long-form correctness uses heuristic weighting and an LLM
judge; reported evaluator-human agreement is weak on several dimensions (`openscholar_judge_agreement`). Such scores are
secondary only.

## Refinement counterevidence

The initial output was preferred over its refined version around 20% of the time due to over-editing or redundancy
(`openscholar_overediting`). This is direct counterevidence to monotone-refinement assumptions. F retains a bounded cap,
non-oracle stopping, and the unrefined candidate for final paired comparison.

## Reproducibility boundary

The actual corpus/API/index/model version is the treatment. Product or interface names are insufficient. Proprietary
API evolution and missed representative papers are explicit limitations (`openscholar_model_limitations`). No local
benefit claim is allowed until Stage R runs on frozen bytes.
