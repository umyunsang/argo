# Experimental Design: Retrieval Evaluation at Scale

**Research Question (T4-retrieval-scale):** How should a retrieval and reranking pipeline for scientific question answering be evaluated as the corpus grows?

---

## 1. Sampling Frame and Experimental Population

**Sampling Frame (explicit reference):** Population = scientific questions with publicly available relevance labels drawn from BEIR benchmarks, MS MARCO, Natural Questions, and SQuAD-Open. Unit of analysis = (question, corpus_size, embedding_model, sparse_index) tuples. We sample across four fixed corpus sizes {10K, 50K, 100K, 500K} documents and measure both rank-based and resource-aware metrics on the same question set across all sizes.

This frame is chosen because:
- BEIR benchmarks represent realistic scientific QA evaluation scenarios across multiple domains (TREC, DBpedia, SciFact, FEVER, etc.)
- MS MARCO and Natural Questions span millions of documents, making 10K–500K a realistic subset range for staged evaluation
- Holding question set constant across corpus sizes isolates the effect of corpus growth on retrieval quality and cost

---

## 2. Main Comparison and Conditions

**Comparison:** Do rank-based metrics (NDCG@10, MRR) capture sufficient evaluation signal as corpus size increases, or do resource-aware metrics (index memory cost, query latency cost per relevant document) reveal degradation that rank metrics miss?

**Conditions (Main Factors):**

1. **Corpus Size:** Four levels
   - C₁: 10K documents (small, low-cost baseline)
   - C₂: 50K documents (medium)
   - C₃: 100K documents (scaling transition point)
   - C₄: 500K documents (large, high-cost)

2. **Retrieval Pipeline Components (Fixed):**
   - **Embedding Model:** One model (TBD: e.g., Sentence-BERT, all-MiniLM-L6-v2, or domain-specific embedder available in the constraint set). Use only one to isolate corpus size effects.
   - **Sparse Index:** One index method (TBD: BM25/Elasticsearch, TF-IDF, or existing Lucene-based index). Use only one to meet constraint.
   - **Reranker (optional ablation):** See Section 3.

3. **Question Subset:** At least two independent subsets from the sampling frame, each with ≥100 unique questions and relevance labels
   - Subset A: Natural Questions dev set (queries about Wikipedia)
   - Subset B: MS MARCO v2 subset or BEIR component (e.g., DBpedia or Trec-COVID, depending on relevance label availability)

---

## 3. Ablation Study

**Ablation 1: Reranker Presence vs. Absence**

- **Rationale:** Reranking is a common scaling cost; as corpus grows, retrieval candidate pools expand, increasing reranking cost. This ablation separates rank-based retrieval quality from end-to-end system cost.
- **Design:** Two variants at each corpus size:
  - **V₁ (Retrieval only):** Dense embedding + sparse index, top-100 candidates retrieved, no reranking.
  - **V₂ (Retrieval + Reranking):** Same retrieval, then apply a lightweight reranker (e.g., MonoBERT, cross-encoder, or available BERT-based reranker) to top-20 candidates.
- **Measurement:** For each variant, record NDCG@10, MRR, and Recall@100; also log index build time, index size, and query latency (retrieval time + reranking time if applicable).
- **Expected Effect:** If reranking cost grows superlinearly (e.g., >2x latency per 5x corpus growth), resource-aware metrics will diverge from rank-based metrics, supporting the design's premise.

---

## 4. Outcome Metrics

### Rank-Based Metrics (Fixed-Cost)
1. **MRR (Mean Reciprocal Rank):** Position of first relevant document. Sensitive to top-1 performance.
2. **NDCG@10:** Normalized discounted cumulative gain at cutoff 10. Standard metric for learning-to-rank.
3. **Recall@100:** Proportion of relevant documents in top 100. Indicates coverage of retrieval recall.

### Resource-Aware Metrics (Cost-Sensitive)
1. **Index Memory Cost:** Index size (MB) per retrieval query. Proxy for system deployment memory footprint. Calculated as: (index size in bytes) / (number of queries).
2. **Query Latency:** Wall-clock time (ms) to retrieve top-100 candidates. Measured end-to-end for retrieval + reranking variants.
3. **Cost-Normalized Recall:** Recall@100 per unit of index memory. Metric definition: Recall@100 / (index size in MB). Combines rank quality with resource cost.
4. **Cost-Precision Trade-off:** For each corpus size, plot NDCG@10 (y-axis) against index memory (x-axis) to visualize efficiency frontier.

---

## 5. Analysis Plan

### Step 1: Data Collection and Organization
- For each condition (corpus size × question subset × variant):
  - Retrieve top-100 candidates using embedding model + sparse index
  - Apply reranker if V₂ variant
  - Record: NDCG@10, MRR, Recall@100, latency (ms), index size (MB)
  - Compute cost-normalized metrics
- Organize results in a table: Corpus Size × Metric × Variant × Question Subset

### Step 2: Metric Stability Check
- For each rank-based metric (NDCG@10, MRR, Recall@100), compute coefficient of variation (CV) across the two question subsets within each corpus size and variant.
- Requirement: CV < 5% indicates stable, reproducible measurement.
- If CV ≥ 5%, flag for additional question subsets or investigate corpus/label inconsistency.

### Step 3: Corpus-Size Scaling Analysis
- **Primary Analysis:** For each metric (rank-based and resource-aware), fit a trend line across corpus sizes {10K, 50K, 100K, 500K}.
  - Rank-based metrics (NDCG@10, MRR, Recall@100): Expected trend = flat or slight increase (diminishing returns). If trend is downward, corpus size degrades rank quality (suspicious finding).
  - Resource metrics (index memory, latency): Expected trend = monotonic increase. Quantify slope: linear, superlinear, or sublinear?
- **Superlinearity Test:** If index memory grows >1.5x per 5x corpus increase (ratio > 1.5^(log(500K/10K)/log(5))), flag as superlinear cost growth.

### Step 4: Divergence Detection
- Compare trajectories: Do rank-based metrics remain stable while resource costs grow? This is the key divergence.
- For each variant (retrieval-only vs. retrieval+reranking), create a **divergence score**:
  - If NDCG@10 CV across corpus sizes < 5% AND index memory growth > 1.5x superlinear, divergence is high (metrics contradict each other on value).
  - If divergence score is high, recommend resource-aware metrics; if low, rank-based metrics may suffice.

### Step 5: Reranker Ablation Analysis
- Compare V₁ (retrieval-only) and V₂ (retrieval+reranking) across all corpus sizes.
- Quantify improvement: ΔNDCG@10 = NDCG@10(V₂) - NDCG@10(V₁). Expected: positive (reranking improves rank quality).
- Quantify cost: ΔLatency = Latency(V₂) - Latency(V₁). Expected: positive (reranking adds latency).
- Cost-benefit ratio: ΔNDCG@10 / ΔLatency (improvement per ms added). If ratio decreases as corpus grows, reranking becomes less cost-effective at larger corpora.

### Step 6: Uncertainty Quantification
- **Bootstrap Resampling:** For each corpus size and metric, resample questions (with replacement) from the pooled {Subset A, Subset B} set. Compute 95% confidence intervals on metrics across 1000 bootstrap samples.
  - Example: NDCG@10 (100K corpus) = 0.52 [95% CI: 0.49–0.55]
- **Variance Decomposition:** Separate variance due to (a) question variability and (b) corpus sampling variability.
  - Use two-way ANOVA or mixed effects model: Metric ~ Corpus Size + Question Set + (1 | Question).
  - Interpret random effect variance for Question to estimate question-level noise.

---

## 6. Concrete Resources

### Datasets
- **Sampling Frame Source (BEIR Benchmarks):**
  - [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://github.com/beir-cellar/beir)
  - Provides ~20 evaluation benchmarks with relevance labels (qrels). Use subsets: Natural Questions, TREC-COVID, DBpedia, or SciFact.
  
- **Corpus Sampling Strategy:**
  - For Natural Questions: Use Wikipedia dump (publicly available). Sample 10K, 50K, 100K, 500K articles by random stratified sampling (maintain distribution of article lengths/topics).
  - For MS MARCO: Use provided corpus splits. Sample subsets by random document sampling (ID-based).
  - Tools: Python, pandas, random sampling without replacement.

### Embedding and Indexing
- **Embedding Model (one, fixed per design):**
  - Option: HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (lightweight, publicly available, widely used in BEIR benchmarks).
  - Alternative: Domain-specific model if one is already available (e.g., SciBERT for scientific QA, BioBERT for biomedical).
  
- **Sparse Index (one, fixed per design):**
  - Option: Elasticsearch BM25 (open-source, standard in BEIR evaluations, reproducible).
  - Alternative: TF-IDF via scikit-learn or Lucene-based Anserini toolkit.
  
- **Reranker (for ablation):**
  - Option: HuggingFace `cross-encoder/ms-marco-MiniLM-L-6-v2` (lightweight cross-encoder trained on MS MARCO, publicly available).
  - Alternative: MonoBERT variant if available.

### Infrastructure
- **Compute Environment:**
  - Single machine: CPU + optional GPU (GPU for embedding inference if time-critical).
  - Storage: ≥200 GB for corpus indexing and model storage.
  - Runtime estimate: ~1–4 hours per condition (retrieval + evaluation), ~40 hours total for all conditions (parallelizable).
  
- **Software Stack:**
  - Python 3.8+
  - PyTorch for model inference
  - Elasticsearch server (or scikit-learn for sparse indexing)
  - Sentence-transformers library
  - BEIR evaluation scripts (publicly available on GitHub)

### Evaluation Code
- **Metrics Computation:**
  - NDCG, MRR, Recall: Use `pytrec_eval` (standard TREC evaluation library) or BEIR's built-in metrics.
  - Latency measurement: Python `time.perf_counter()` for query execution timing.
  - Index metrics: Elasticsearch API calls to retrieve index size; filesystem checks for index directory size.

---

## 7. How to Quantify Uncertainty

### 7.1 Confidence Intervals (via Bootstrap)
For each corpus size C and metric M:
1. Pool all questions from Subset A and Subset B (total ≥200 questions).
2. Resample 200 questions with replacement, compute M for resampled set.
3. Repeat 1000 times → distribution of M.
4. Extract 2.5th and 97.5th percentiles → 95% CI.

Example output:
```
Corpus Size | Metric  | Point Est. | 95% CI Lower | 95% CI Upper | Width
10K         | NDCG@10 | 0.58       | 0.54         | 0.62         | 0.08
50K         | NDCG@10 | 0.56       | 0.52         | 0.60         | 0.08
100K        | NDCG@10 | 0.55       | 0.51         | 0.59         | 0.08
500K        | NDCG@10 | 0.54       | 0.50         | 0.58         | 0.08
```

### 7.2 Trend Uncertainty (Regression-Based)
Fit linear regression: Metric ~ Corpus Size (treated as continuous: log(corpus size) or rank 1–4).
- Extract slope coefficient and 95% CI on slope.
- If CI includes 0, no significant trend detected.
- Report: Slope = [lower CI, upper CI].

Example:
```
Metric            | Slope Estimate | 95% CI          | Interpretation
NDCG@10           | -0.02          | [-0.05, 0.01]   | Flat or slight decline, not significant
Index Memory (MB) | +45            | [+40, +50]      | Significant increase, ~45 MB per 5x corpus growth
```

### 7.3 Cost-Benefit Ratio Uncertainty (Delta Metrics)
For reranker ablation (V₂ vs. V₁):
- Compute ΔNDCG@10 and ΔLatency for each question subset.
- Bootstrap resample to get 95% CI on Δ metrics.
- Compute cost-benefit ratio and its CI: Ratio = ΔNDCG@10 / ΔLatency (point estimate ± 95% CI).

Example:
```
Corpus Size | Cost-Benefit Ratio | 95% CI              
10K         | 0.0025 points/ms   | [0.0020, 0.0030]  
500K        | 0.0008 points/ms   | [0.0005, 0.0011]  
```

### 7.4 Reproducibility and Reporting
- Report all random seeds used (for data sampling, bootstrap resampling, model initialization).
- Provide detailed query logs: for each question, record retrieved documents, rank scores, latency, and relevance judgments.
- Make code and results reproducible: GitHub repo with scripts, config files (corpus size, model paths, hyperparameters), and output CSVs.

---

## 8. Decision Criteria and Stopping Rule

**Primary Decision Point:** After all corpus sizes have been evaluated with CV < 5% across question subsets, evaluate divergence.

**Stopping Rule (from state.md):** Stop data collection when:
1. All four corpus sizes {10K, 50K, 100K, 500K} have been evaluated on at least two question subsets with ≥100 questions each.
2. Rank-based metrics (NDCG@10, MRR, Recall@100) have stabilized (CV < 5% across subsets).

**Interpretation Framework:**
- **If divergence is HIGH** (NDCG@10 CV < 5% AND index memory growth >1.5x superlinear):
  - **Recommendation:** Use resource-aware metrics (index memory, query latency, cost-normalized recall) alongside rank-based metrics.
  - **Rationale:** Rank metrics alone mask computational cost increases and risk optimizing for metrics that diverge from deployment value.
  
- **If divergence is LOW** (NDCG@10 CV < 5% AND index memory growth < 1.5x superlinear):
  - **Recommendation:** Rank-based metrics may suffice; resource-aware metrics add marginal value.
  - **Rationale:** If cost remains sublinear and rank quality stable, simple metrics are effective.

---

## 9. Ablation and Sensitivity Summary

| Ablation                         | Hypothesis                                      | Success Criterion                      |
|----------------------------------|-------------------------------------------------|----------------------------------------|
| Reranker (V₂ vs. V₁)             | Reranking cost grows superlinearly with corpus  | ΔLatency > 2x per 5x corpus growth     |
| Question Subset Variability      | Metrics stable across question distributions    | CV(NDCG@10) < 5% across subsets        |
| Corpus Sampling Variability      | Metrics stable within corpus size               | Bootstrap CI width < 10% of point est. |

---

## Summary

This design uses a **sampling frame** of scientific QA questions from BEIR, MS MARCO, and Natural Questions. It compares rank-based and resource-aware metrics across corpus sizes {10K, 50K, 100K, 500K} using fixed embedding and sparse index implementations. A reranker ablation isolates cost-benefit trade-offs. Uncertainty is quantified via bootstrap resampling and regression-based trend analysis. The design explicitly tests whether rank metrics diverge from resource metrics as corpus grows—the core premise of the research question.
