# Experimental Design: Retrieval and Reranking Pipeline Evaluation at Scale

## 1. Research Question & Framing

**Primary Research Question:** How does retrieval performance (recall and rank quality) scale as corpus size increases for scientific question answering, and does reranking efficacy degrade with larger corpora?

**Operational form:** We will measure the quality of retrieved documents across corpus sizes with and without reranking, controlling for retrieval depth, to determine where retrieval quality plateaus and whether reranking ROI changes.

---

## 2. Main Comparison and Conditions

### Main Comparison
**Factor:** Corpus size (number of indexed scientific documents)

**Conditions (three levels):**
- **Small (S):** 10,000 documents
- **Medium (M):** 100,000 documents  
- **Large (L):** 1,000,000 documents

**Justification:** These powers-of-10 scaling points capture logarithmic behavior typical in retrieval systems and represent practical deployment phases (research, production pilot, enterprise scale).

### Resource Specification
- **Sparse Index:** BM25, implemented via [Lucene](https://lucene.apache.org/core/) (industry-standard, open-source, deterministic).
- **Dense Embedding Model:** [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) (384-dim, publicly available, widely used in scientific retrieval benchmarks, inference cost is trackable).
- **Corpus Source:** [Microsoft Academic Graph (MAG)](https://www.microsoft.com/research/project/microsoft-academic-graph/) or [arXiv](https://arxiv.org/) abstracts; we will use publicly available snapshots stratified by publication year to maintain document quality consistency across corpus sizes.

---

## 3. Ablation: Reranking vs. Reranking-Free Retrieval

### Ablation Comparison
For each corpus size condition (S, M, L), we will compare:

- **Condition A (Retrieval Only):** BM25 sparse index + top-k (k=100 documents returned).
- **Condition B (Retrieval + Dense Reranking):** BM25 sparse → top-100 → rescore using BAAI/bge-small-en-v1.5 embeddings → return top-10.

**Justification:**
- Reranking is a standard practice, but its absolute benefit and cost-to-benefit ratio are unknown at different scales.
- This ablation isolates the effect of the dense embedding component from the sparse retrieval baseline.
- Retrieval-only (A) establishes a lower bound; combined (B) establishes the practical pipeline.

---

## 4. Outcome Metrics and Uncertainty Quantification

### Primary Metrics (per query, per corpus size condition)

1. **Recall@k** (k ∈ {10, 50, 100})
   - Fraction of relevant documents in top-k / total relevant documents in corpus.
   - **Uncertainty:** Wilson score interval (95% CI) across query-level recall, accounting for variable relevant-document counts per query.

2. **Normalized Discounted Cumulative Gain (nDCG@10, nDCG@50)**
   - Penalizes rank position; ideal for ranking quality.
   - **Uncertainty:** Paired bootstrap confidence intervals (1,000 resamples, queries as units) comparing Conditions A and B.

3. **Mean Reciprocal Rank (MRR)**
   - Position of first relevant result; fast-moving outcome.
   - **Uncertainty:** Percentile bootstrap (2.5th–97.5th) to account for skew in rank distributions.

### Secondary Metrics

4. **Latency per Query**
   - Wall-clock time: BM25 retrieval + embedding + reranking (if B).
   - **Cost proxy:** Embedding inference cost (embeddings/query) scales linearly.

5. **Cost per Query Reached** (efficiency measure)
   - nDCG@10 ÷ (mean query latency in seconds).
   - Captures quality-per-unit-cost to detect diminishing returns.

### Uncertainty & Variance Decomposition

- **Query-level variance:** Computed separately for each corpus size (different queries may have different numbers of relevant documents).
- **Corpus-level variance:** Repeat each corpus size condition with two independent random samples of documents (e.g., different year ranges or topic strata from arXiv) to capture sampling variability.
- **Relevance label uncertainty:** Use the presence of relevance annotations in existing datasets (see below) rather than generate new labels, avoiding bias and cost; document the label source and any disagreement rates if available.

---

## 5. Data and Experimental Workflow

### Query Set
- **Source:** [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-20/) (scientific-domain subset) or [Natural Questions](https://ai.google.com/research/NaturalQuestions/) (filtered to scientific topics using keyword filters).
- **Rationale:** Publicly available, stable, relevance labels already exist (no new annotation needed, controlling cost).
- **Size:** Use ~1,000 queries per condition to stabilize metrics.

### Relevance Labels
- **Source:** Existing annotations in SQuAD/NQ (passage-level binary or soft relevance scores).
- **Limitation acknowledgment:** These datasets originally target different retrieval corpora, so we must verify that relevant passages actually appear in our MAG/arXiv corpus samples. We will retain only queries for which at least one relevant document appears in all three corpus sizes; this ensures fair comparison.
- **Fallback:** If label coverage is insufficient (<70% of queries), supplement with BM25-based weak labels (high BM25 score ≈ relevant) for held-out queries, documented as a secondary sensitivity analysis.

### Corpus Construction
- **Small (10K):** Randomly sample 10,000 documents from arXiv (2020–2021 publications).
- **Medium (100K):** Randomly sample 100,000 documents from arXiv (2018–2021).
- **Large (1M):** Combine arXiv (2016–2021) sampled documents + MAG snapshot covering computer science (public dump).
- **Rationale:** Stratified by year to maintain document-quality consistency and avoid temporal bias.

---

## 6. Analysis Plan

### Step 1: Baseline Comparisons (A vs. B within each corpus size)
For each corpus size (S, M, L):
- Compute mean nDCG@10, Recall@10, MRR for Condition A and Condition B.
- Test for significant difference using paired t-test on query-level nDCG; report 95% CI on the difference (e.g., "Reranking improves nDCG@10 by [x, y] with p < 0.05").

### Step 2: Scaling Analysis (Corpus size effect)
- Fit a regression model: Metric ~ log(Corpus Size) + Condition + Condition × log(Corpus Size).
- Report the coefficient on Corpus Size × Condition interaction to assess whether reranking benefit changes with scale.
- Visualize metric trends (line plot, separate lines for A and B, x-axis = log corpus size).

### Step 3: Sensitivity Analysis
- **Retrieval depth:** Repeat the full analysis with Condition A returning k ∈ {50, 200} instead of 100 to check robustness.
- **Embedding model robustness:** If budget allows, substitute a second dense model (e.g., [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)) for one corpus size and compare MRR/nDCG; report whether ranking conclusions hold.
- **Label uncertainty:** Recompute metrics using only high-confidence labels (if relevance scores exist) and low-confidence labels separately to bracket results.

### Step 4: Cost-Benefit Analysis
- Compute embeddings-per-query (sparse retrieval has ~1 BM25 score per document; reranking adds 1 embedding per retrieved document).
- Estimate wall-clock cost assuming standard GPU latency ([OpenAI embedding cost model](https://openai.com/pricing/embeddings) or local GPU inference time).
- Plot: Cost per query (x-axis) vs. nDCG@10 (y-axis), separate lines for corpus sizes; identify the Pareto frontier (best nDCG for each cost level).

---

## 7. Resources (Concrete, Existing)

| Resource | Source | Justification |
|----------|--------|---------------|
| **Query Set** | SQuAD 2.0 or Natural Questions | Public, labeled, stable. |
| **Corpus** | arXiv (public snapshots) + MAG (public dump) | Free, scientific domain, versioned snapshots. |
| **Sparse Index** | Apache Lucene | Open-source, deterministic, production-grade. |
| **Dense Model** | BAAI/bge-small-en-v1.5 (HuggingFace) | Lightweight, open-weights, competitive on scientific retrieval. |
| **Evaluation Metrics** | pytrec_eval or ir_measures Python packages | Standard IR evaluation libraries. |
| **Statistical Inference** | scipy.stats, statsmodels | Bootstrap CI, regression, t-tests. |

---

## 8. Expected Outcomes and Stopping Rules

### Hypothesis (qualitative, not reported numerically)
- We expect Recall@100 to saturate (diminishing gains from corpus growth beyond 100K docs).
- We expect reranking to improve nDCG@10, but reranking cost to grow linearly with corpus size (more candidates to rescore).
- We expect a cross-over point where reranking cost outweighs benefit (efficiency degrades).

### Stopping Rule
- Run all three corpus sizes for both conditions (A and B).
- Compute all primary metrics (Recall@{10,50,100}, nDCG@{10,50}, MRR) and their 95% CIs.
- Complete Step 1–4 analysis.
- **Do not** iterate further if results contradict hypotheses; report findings as-is with uncertainty intervals.

---

## 9. Limitations and Honest Caveats

1. **Relevance label cost:** We use existing labels, which were created for different corpus contexts. Label coverage at 100% corpus size is unknown; we will document the query drop rate.
2. **Model generalization:** BAAI/bge-small-en-v1.5 is optimized for general text; we have not verified its performance on scientific text specifically. (A sensitivity check with an alternative model is included in Step 3 to mitigate.)
3. **Corpus heterogeneity:** arXiv and MAG have different indexing standards and publication quality; the Large condition mixes sources, which may introduce confounds.
4. **Computational cost:** Dense reranking of top-100 per query scales linearly with query volume; we assume standard GPU/CPU and report wall-clock time, not absolute cost dollars.
5. **External validity:** Results apply to scientific QA; generalization to other domains (news, e-commerce) is unknown.

---

## 10. Summary Table

| Phase | Comparison | Conditions | Metrics | Uncertainty |
|-------|-----------|-----------|---------|------------|
| **Main** | Corpus size effect | S, M, L | nDCG@10, Recall@10, MRR | 95% CI (paired bootstrap) |
| **Ablation** | Reranking effect (A vs B) | Sparse only vs. Dense rescore | nDCG@{10,50}, MRR | Paired t-test, 95% CI on difference |
| **Scaling** | Interaction (size × reranking) | Regression model on log corpus size | Coefficient on interaction term | p-value, 95% CI on slope |
| **Cost-Benefit** | Efficiency | Latency, embedding count | nDCG@10 / latency | Pareto frontier visualization |
| **Sensitivity** | Robustness | Alternative retrieval depth, embedding model | Same metrics as main | Report % change in conclusions |

---

## 11. Conclusion

This design isolates the effect of corpus size and reranking on retrieval quality for scientific QA, uses publicly available and reproducible resources, quantifies all uncertainty via confidence intervals and statistical tests, and includes sensitivity analyses to strengthen confidence in findings. By anchoring resource choices to concrete, existing tools and datasets, the design is implementable and auditable.
