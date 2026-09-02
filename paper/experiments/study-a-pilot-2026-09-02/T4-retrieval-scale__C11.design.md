# Experimental Design: Retrieval Pipeline Evaluation Across Corpus Scales

## Overview

This design specifies a factorial experiment to measure how retrieval and reranking pipeline quality degrades (or plateaus) as corpus size increases. It answers: **At what corpus sizes do scientific-QA retrieval systems degrade, and what corpus size ensures quality stability?**

The design separates **retrieval gaps** (evidence never found) from **utilization gaps** (evidence retrieved but not used), following the diagnostic framework in 2608.01913. It uses stratified, budget-aware label allocation (2607.13304) and ensures statistical power via resolution targets (2605.30315), grounded in prior NLP power norms (2010.06595).

---

## 1. Research Question and Hypothesis

**Primary Question:**  
How does retrieval quality degrade as corpus size grows? Specifically:
- At what corpus size (if any) do nDCG@10 and MRR plateau?
- Does a 10x increase in corpus size (10k → 100k) incur a measurable retrieval penalty?

**Hypothesis (directional):**  
As corpus size grows, pipeline quality will decline because:
1. Embedding models may suffer from scale overload or index corruption at very large scales.
2. Sparse index recall degrades if query-document lexical overlap becomes more dilute.
3. Reranking overhead may cause timeout or truncation at large scales.

**Null Hypothesis:**  
Pipeline quality does not significantly differ across corpus sizes (at conventional power, α=0.05, 1−β=0.8).

---

## 2. Sampling Frame and Population

**Sampling Frame (as filled in state.md):**

This experiment's sampling frame is: **Scientific QA questions × corpus-size conditions {10k, 50k, 100k, 500k, 1M documents}, stratified by question difficulty (Hard/Medium/Easy).** All analyses condition on this frame. The design evaluates (question, corpus_size) pairs, where each pair is independently labeled for document-level relevance by trained crowdworkers.

- **Population:** Scientific questions from benchmark QA datasets (e.g., Natural Questions dev set, SCIQ, or arXiv-backed retrieval benchmarks).
- **Unit:** (question, corpus_size) pair, where corpus_size ∈ {10k, 50k, 100k, 500k, 1M documents}.
- **Stratification:** Questions stratified into three tiers by *a priori* retrieval difficulty, estimated from the full-corpus evaluation:
  - **Tier 1 (Hard):** retrieval recall on full corpus < 50%
  - **Tier 2 (Medium):** 50% ≤ recall < 80%
  - **Tier 3 (Easy):** recall ≥ 80%
- **Document Pool:** Subset of arXiv abstracts + Wikipedia article text + ACL anthology papers (~1M+ documents available). Corpus subsets at each size are created by **stratified random sampling without replacement**, ensuring representative topic distribution.
- **Relevance Labels:** Document-level binary or graded (0-3) relevance judgments:
  - 0 = not relevant
  - 1 = somewhat relevant (mentions topic but does not directly answer)
  - 2 = relevant (directly addresses question)
  - 3 = highly relevant (central to answer)

---

## 3. Main Comparison: Corpus Size Effect

**Fixed Factors:**
- Embedding model: 1 (e.g., `contriever-msmarco` or similar publicly available dense retriever)
- Sparse index: 1 (e.g., BM25 via Elasticsearch or Lucene)
- Reranker: 1 (e.g., cross-encoder on top-k candidates)
- Timeout/truncation: Fixed per corpus size (e.g., 30s wall-clock, return top-50 documents)

**Varying Factor (Main Comparison):**
- **Corpus Size:** 5 levels: {10k, 50k, 100k, 500k, 1M documents}

**Outcome Metrics (Primary):**
- **nDCG@10** (Normalized Discounted Cumulative Gain at rank 10)
  - Computed from binary relevance (rel=2 or 3 → relevant) or graded if using 0-3 scale
  - Normalized by ideal ranking (all relevant docs at top)
- **MRR** (Mean Reciprocal Rank)
  - Reciprocal of rank of the first relevant document
  - Robustness check for sparse index collapse at large scales
- **Recall@50**
  - Proportion of all relevant documents retrieved in top 50
  - Sensitivity to recall degradation with scale

**Outcome Metrics (Secondary—Retrieval vs. Utilization Diagnosis):**

Following 2608.01913, for a subset of trajectories run the resulting top-k documents through an LLM reader:
- **Reader Accuracy:** Given retrieved top-5 documents, does the LLM answer the question correctly?
- **Evidence Presence:** Was at least one gold-relevant document in top-5?
- **Retrieval Gap Indicator:** Reader accuracy = 0 AND no gold doc in top-5 → retrieval gap
- **Utilization Gap Indicator:** Reader accuracy = 0 AND ≥1 gold doc in top-5 → utilization gap

This decomposition reveals whether corpus-size degradation is due to retrieval failure or reasoning failure.

---

## 4. Ablation: Embedding vs. Sparse Index

**Hypothesis:** Embedding models scale better than sparse indexes to large corpora.

**Design:**
Run two retrieval backends on a subset of corpus-size conditions:
1. **Dense embedding retrieval** (default): Contriever or similar, top-k by cosine similarity
2. **Sparse BM25 retrieval**: Traditional keyword-based, top-k by TF-IDF score

**Application:** Evaluate both on 3 corpus-size conditions: {10k, 100k, 1M}.

**Outcome:** Interaction plot of backend × corpus_size on nDCG@10 will show whether embedding degradation is steeper than sparse.

---

## 5. Analysis Plan

### 5.1 Power Analysis and Sample Size (following 2010.06595, 2605.30315)

**Minimum Detectable Effect (MDE):**

Assume a two-sample t-test comparing nDCG@10 between successive corpus sizes (e.g., 10k vs. 100k). Using Equation (4) from 2605.30315:

$$\delta_{MDE}(N; lpha=0.05, eta=0.2) = rac{(z_{0.975} + z_{0.8})\sigma_D}{\sqrt{N}}$$

where $\sigma_D$ is the standard deviation of the nDCG difference.

**Assumptions:**
- $\sigma_D pprox 0.15$ (conservative estimate for nDCG diffs; to be refined after pilot)
- $z_{0.975} pprox 1.96$, $z_{0.8} pprox 0.84$ → $(z_{0.975} + z_{0.8}) pprox 2.80$
- Target: $\delta_{MDE} pprox 0.02$ nDCG points (practical significance)

**Solving for N:**
$$N^* = \left( rac{2.80 	imes 0.15}{0.02} 
ight)^2 pprox 176 	ext{ questions per corpus-size condition}$$

**Sample Size:**
- **Main comparison:** 5 corpus-size conditions × 176 questions/condition ≈ 880 questions
- **Stratified allocation:** Allocate proportionally to tier sizes, or oversample hard tier for power (decision to make with stakeholder)
- **With replicates (if labeling varies):** If each question gets 2–3 independent label sets for uncertainty, multiply by that factor

**Power check:** With N=176, power to detect ≥0.02 nDCG difference is ≥0.80. If pilot data shows $\sigma_D > 0.15$, re-scale N upward.

### 5.2 Label Budget Allocation (following 2607.13304)

**Variance Components to Partition:**

The total variance in relevance judgment can come from:
1. **Question variance:** Inherent difficulty of the question
2. **Corpus size variance:** Effect of corpus size on retrievability
3. **Judge variance:** Variation across annotators or crowdworkers
4. **Residual:** Noise

**Allocation Strategy (Generalizability Theory):**

1. Run a **pilot study** on 50 questions × 3 corpus sizes, with 2 independent judges per (question, corpus_size, result) triplet.
2. Fit a crossed random-effects model: `relevance ~ 1 + (1 | question) + (1 | judge) + (1 | corpus_size) + (question:corpus_size)`, estimate variance components via REML.
3. From the fitted model, compute decision-study allocations:
   - If judge variance is small (ICC ≪ 0.10), single judge per question suffices.
   - If question×corpus_size interaction is large, allocate more questions at informative corpus-size pairs.
4. **Decision rule** (following 2607.13304 logic):
   - Spend the label budget (total dollar cap) by spreading across diverse (question, corpus_size) pairs rather than re-labeling the same pair.

**Concrete allocation (example, to be refined after pilot):**
- Total label budget: ~5,000 relevance judgments
- Breakdown:
  - Main conditions (5 corpus sizes × 176 questions × 1 label/triplet) = 880 labels
  - Ablation conditions (2 backends × 3 sizes × 50 questions × 1 label) = 300 labels
  - Judge consensus/calibration set (100 questions × 2 judges) = 200 labels
  - Pilot data (50 questions × 3 sizes × 2 judges) = 300 labels
  - Reserve for uncertainty (20% buffer) = 1000 labels
  - **Total ~3,100 labels** (adjust based on crowdsourcing unit costs)

### 5.3 Primary Analysis

**Inferential Pipeline:**

1. **Descriptive Statistics:**
   - For each corpus size, report mean ± SD of nDCG@10, MRR, Recall@50, stratified by question tier.
   - Construct profile plots (corpus size on x-axis, nDCG on y-axis) for each tier and overall.

2. **Hypothesis Test (Main Comparison):**
   - **Test:** Linear mixed-effects model (LMM)
   ```
   outcome ~ corpus_size + (1 | question) + (1 | judge) + (1 | tier)
   ```
   - **Outcome:** nDCG@10 (primary), MRR, Recall@50 (secondary)
   - **Fixed effect of interest:** Slope of corpus_size (test H0: β = 0)
   - **Random intercepts:** account for within-question and within-judge clustering

   Rationale: LMM handles unbalanced designs and partial dependence (same questions labaled by multiple judges). Random intercepts capture question difficulty and judge severity (2608.29517), reducing residual variance.

3. **Post-hoc Comparisons:**
   - If corpus_size effect is significant, conduct pairwise comparisons between consecutive corpus sizes (10k vs 50k, 50k vs 100k, etc.) using Holm-corrected t-tests or Tukey HSD on estimated marginal means.
   - Report 95% confidence intervals on differences (CIs that exclude zero indicate significant difference).

4. **Resolution Diagnostic (following 2605.30315):**
   - For each pairwise comparison (e.g., 1M vs 10k), compute:
     - Observed gap $\hat{\delta}$ in mean nDCG
     - Resolution ratio $q = N / N^*(\hat{\delta})$
     - If $q \geq 1$, the gap is resolved at (α, 1−β) = (0.05, 0.8); otherwise, unresolved
   - Report resolution status alongside each p-value.

### 5.4 Ablation Analysis (Embedding vs. Sparse)

**Inferential Pipeline:**

1. **Interaction Model:**
   ```
   outcome ~ backend * corpus_size + (1 | question)
   ```
   - Fixed effects: main effects of backend and corpus_size, plus their interaction
   - Test H0: interaction = 0 (i.e., both backends degrade equally with scale)

2. **If interaction is significant:**
   - Separate the regression by backend and report the slope of corpus_size for each.
   - Visualize as two regression lines (one per backend) on a single plot.

3. **Practical Interpretation:**
   - If dense embedding slope is flatter than sparse slope → embedding scales better.
   - If slopes cross (one improves, one worsens with scale) → complex interaction (explore further).

### 5.5 Retrieval vs. Utilization Diagnosis

**Subset (20–30 questions) with Reader Evaluation:**

1. For each (question, corpus_size) pair in the subset:
   - Retrieve top-5 documents using the pipeline.
   - Pass top-5 + question to an LLM reader (e.g., GPT-4, Claude 3.5 Sonnet in a zero-shot setting).
   - Record: (a) reader's answer, (b) reader's confidence, (c) presence of gold-relevant doc in top-5.

2. **Classify failures:**
   - Retrieval gap: Reader fails AND no gold doc in top-5 → fix by improving retrieval.
   - Utilization gap: Reader fails AND gold doc present → fix by improving reasoning/reranking.
   - Correct: Reader succeeds (gold doc presence immaterial).

3. **Analysis:**
   - For each corpus size, report the count of retrieval gaps vs. utilization gaps.
   - Hypothesis: As corpus size grows, retrieval gaps should increase (supporting the hypothesis that retrieval becomes harder); utilization gaps should remain constant.
   - Plot gap count (y-axis) vs corpus size (x-axis), stratified by gap type.

### 5.6 Uncertainty Quantification

**Bootstrap Confidence Intervals (following 2010.06595, 2605.30315):**

1. **Stratified Bootstrap:**
   - Resample questions (not individual documents) with replacement, stratified by tier.
   - Repeat 1,000 times.
   - For each resample, recompute nDCG@10 mean and all pairwise differences.

2. **Confidence Intervals:**
   - Report 95% percentile CIs on:
     - Mean nDCG@10 per corpus size
     - Difference in nDCG@10 between corpus sizes
   - Visualize as error bars on profile plots.

3. **Multiplicity Correction:**
   - Apply Bonferroni or Holm correction to the family of pairwise comparisons (10 pairs for 5 corpus sizes: C(5,2) = 10).
   - Adjusted α = 0.05 / 10 = 0.005 (Bonferroni) or use Holm step-down.

---

## 6. Concrete Resources and Setup

### 6.1 Datasets and Corpora

**Benchmark Questions:**
- **Source:** Natural Questions dev set (or SCIQ if smaller budget needed)
- **Rationale:** Natural Questions has >7,000 questions from Google searches with human-annotated evidence paragraphs; SCIQ is smaller (~12k) but domain-specific (science)
- **Size:** 600–900 questions (stratified by difficulty)

**Document Corpora:**
- **Base corpus:** ArXiv (abstracts + intro sections), English Wikipedia articles, ACL anthology papers; total ~1.5M documents available
- **Subsets:** Create random samples of sizes 10k, 50k, 100k, 500k, 1M by stratified sampling (maintaining topic distribution if possible, e.g., sample evenly across arXiv categories)
- **Tooling:** 
  - Elasticsearch or Weaviate for dense index (stores embeddings)
  - Lucene or BM25 via Pyserini for sparse index

### 6.2 Retrieval Pipeline Components

**Embedding Model (Public):**
- **Option A:** `contriever-msmarco` (Meta; trained on MS MARCO passages; 768 dims; ~100M params)
  - Availability: Hugging Face model hub
  - Cost: Free; runs on CPU/GPU locally or via cloud inference
- **Option B:** `bge-large-en-v1.5` (BAAI; BEIR benchmark; 1024 dims)
  - Availability: Hugging Face
  - Cost: Free; larger model, higher precision expected

**Reranker (Public):**
- **Option A:** `cross-encoder/ms-marco-MiniLM-L-12-v2` (Hugging Face Sentence Transformers)
  - Fast, suitable for reranking top-50 candidates
  - Cost: Free
- **Option B:** Proprietary (GPT-4 API) for trajectory-level reader evaluation only; not for main retrieval ranking

**Infrastructure:**
- **Indexing:** Custom Python scripts using Weaviate Python client or Haystack
- **Retrieval:** REST API or Python library (same)
- **Latency constraint:** Enforce 30-second timeout per query to mimic production retrieval SLAs

### 6.3 Relevance Annotation

**Annotators:**
- **Option A:** Trained crowdworkers (e.g., via Appen, Scale AI, or in-house contractors)
  - Cost: ~$0.05–0.15 per judgment (varies by platform and quality tier)
  - Quality: Fleiss' κ typically 0.65–0.75 for relevance tasks (2608.29517 shows LLM judges have κ ≈ 0.47–0.56)

- **Option B:** Domain experts (grad students or postdocs in ML/NLP)
  - Cost: ~$0.30–0.50 per judgment (higher but higher agreement expected)
  - Quality: Fleiss' κ ≈ 0.75–0.85 expected

**Recommendation:** Use crowdworkers with multi-judge consensus (2 judges per item) and retain a 10% expert overlap for calibration. Expert-resolved ties break disagreements.

**Training:**
- Provide 50 example (question, document, relevance_label) triplets with expert explanations.
- Pilot with 100 questions × 2 judges; measure Fleiss' κ; retrain if κ < 0.60.

---

## 7. Metrics and Outcome Definition

### 7.1 Primary Metrics

| Metric | Definition | Threshold | Interpretation |
|--------|-----------|-----------|-----------------|
| **nDCG@10** | Normalized Discounted Cumulative Gain | ≥ 0.02 difference → significant | Quality of top-10 ranking; sensitive to reranking and scale effects |
| **MRR** | Mean Reciprocal Rank (1 / rank of first relevant) | ≥ 0.05 difference → significant | Speed to relevant doc; robustness to index collapse |
| **Recall@50** | Proportion of relevant docs in top 50 | ≥ 0.10 difference → significant | Coverage; detects if hard corpus sizes miss evidence entirely |

### 7.2 Resolution Target

**Minimum Detectable Effect (MDE):**
- **Primary:** nDCG difference of ≥ 0.02 points (relative effect size ~5% at mean nDCG ≥ 0.40) at N ≈ 176 questions/condition, α = 0.05, 1−β = 0.8.
- **Secondary:** MRR, Recall@50 differences of ≥ 0.05 and ≥ 0.10 respectively.

**Resolution Ratio:**
- If $q = N / N^* \geq 1$, declared resolved. Report $q$ alongside all pairwise comparisons.

### 7.3 Redline Mechanism (following 2608.03501)

**Zero score if:**
1. Question relevance labels do not come from the same annotator pool (e.g., mixing expert and crowdworker without calibration).
2. Embedding model or reranker version is not frozen during experiment (to avoid confounding with model updates).
3. Corpus subsets are not created via random sampling (e.g., if a corpus size is hand-curated, it introduces selection bias).
4. Corpus size conditions do not use the same retrieval timeout or truncation policy (different latency budgets confound scale effects with speed-quality tradeoff).

**Remediation:** If any redline is triggered, the experiment restarts with the offending component fixed.

---

## 8. Stopping Rules

**Per-Condition Stopping (following state.md):**

For each corpus_size condition, stop labeling when:

1. **MDE Criterion:** MDE at current N falls below 0.02 nDCG points at α=0.05, 1−β=0.8, **OR**
2. **CI Non-Overlap Criterion:** 95% bootstrap CI on nDCG@10 for corpus_size *k* and corpus_size *k−1* no longer overlap, **OR**
3. **Variance Stabilization Criterion:** Gelman-Rubin shrinkage diagnostic on variance estimate (from hierarchical model) ≤ 1.05.

**Study-Level Stopping:**

Stop the entire experiment when:
- All 5 corpus-size conditions meet their individual stopping criterion, **OR**
- Label budget is exhausted, **OR**
- Calendar deadline is reached.

**Monitoring:**
- Compute stopping diagnostics weekly as labels arrive.
- Do **not** peek at p-values during data collection (data-dependent stopping inflates Type I error); only use MDE, CI overlap, and variance diagnostics.

---

## 9. Design Summary Table

| Element | Specification |
|---------|---------------|
| **Main Factor** | Corpus Size: {10k, 50k, 100k, 500k, 1M documents} |
| **Stratification** | Question difficulty tier (Hard, Medium, Easy) |
| **Sampling Frame** | Natural Questions dev set (~600–900 Qs) or SCIQ (~400–500 Qs) × 5 corpus sizes |
| **Primary Outcome** | nDCG@10 (binary relevance: rel ≥ 2) |
| **Secondary Outcomes** | MRR, Recall@50, Retrieval Gap / Utilization Gap counts |
| **Ablation** | Dense Embedding (contriever) vs. Sparse (BM25) on {10k, 100k, 1M} |
| **Annotation** | Document-level binary/graded relevance (0–3 scale) |
| **Annotator Pool** | Trained crowdworkers (Appen, Scale, or in-house) with expert oversight |
| **Labels per Sample** | 2 independent judges per (question, corpus_size, result) triplet for main conditions |
| **Sample Size (Power)** | N ≈ 176 questions per corpus size (MDE = 0.02 nDCG, α=0.05, 1−β=0.8) |
| **Total Main Experiment** | 5 conditions × 176 Qs × 2 judges ≈ 1,760 labels |
| **Ablation Experiment** | 2 backends × 3 sizes × 50 Qs × 1 judge ≈ 300 labels |
| **Pilot + Calibration** | 50 Qs × 3 sizes × 2 judges + 100 expert-overlap = 400 labels |
| **Reserve** | ~20% of main for uncertainty (340 labels) |
| **Total Budget** | ~2,800–3,100 relevance judgments |
| **Crowdsourcing Cost (estimate)** | $150–400 USD (at $0.05–0.15 per label) |
| **Infrastructure Cost** | $0 (all tools open-source) or ~$50–200 if using managed embedding service (e.g., Weaviate Cloud) |
| **Inference Engine** | Python + Weaviate/Elasticsearch + Hugging Face Transformers |
| **Timeline** | ~6–8 weeks (pilot: 1w, main experiment: 4–6w, analysis: 1w) |

---

## 10. Reporting and Falsifiability

### 10.1 Primary Findings

Report as a profile plot + table:

| Corpus Size | n_questions | nDCG@10 (M±SD) | MRR (M±SD) | Recall@50 (M±SD) | 95% CI | Resolution Ratio q |
|-------------|-------------|----------------|-----------|------------------|--------|-------------------|
| 10k | 176 | 0.42 ± 0.18 | 0.55 ± 0.20 | 0.68 ± 0.14 | [0.38, 0.46] | — |
| 50k | 176 | 0.41 ± 0.19 | 0.54 ± 0.21 | 0.67 ± 0.14 | [0.36, 0.45] | q=0.95 (vs 10k) |
| ... | ... | ... | ... | ... | ... | ... |

### 10.2 Evidence for/against Hypothesis

**In Favor:** If all pairwise comparisons show q ≥ 1 and all CIs exclude zero, the effect of corpus size on quality is **resolved and significant**. Report the effect direction (degradation or plateau).

**Against (Falsified):** If the 95% CI on the largest effect (1M vs 10k) includes zero after Bonferroni correction, the hypothesis is **not resolvable** at the planned sample size; recommend larger study or accept the null.

### 10.3 Ablation Findings

Report as interaction plot + table:

| Backend | Corpus Size | nDCG@10 | Slope (Δ per 10-fold increase in corpus size) |
|---------|-------------|---------|----------------------------------------------|
| Dense | 10k, 100k, 1M | ... | −0.02 (slow degradation) |
| Sparse | 10k, 100k, 1M | ... | −0.05 (fast degradation) |

Conclude: "Dense embeddings scale better; sparse index collapses at 1M documents."

### 10.4 Retrieval vs. Utilization Breakdown

Report as counts + proportions:

| Corpus Size | Total Errors | Retrieval Gaps | Utilization Gaps | Ambiguous (unclear from top-5) |
|-------------|--------------|----------------|------------------|-------------------------------|
| 10k | 50 | 10 (20%) | 35 (70%) | 5 (10%) |
| 1M | 50 | 25 (50%) | 20 (40%) | 5 (10%) |

Interpretation: "Corpus size increases retrieval gap rate from 20% to 50%, suggesting the effect is primarily retrieval degradation."

### 10.5 Redline Checks

Before reporting, confirm:
- [ ] Embedding model version is frozen and documented
- [ ] Reranker version is frozen and documented
- [ ] Corpus subsets created via stratified random sampling (seed logged)
- [ ] Retrieval timeout uniform across conditions
- [ ] Annotator pool training and calibration κ ≥ 0.60
- [ ] No peeking at p-values during data collection (only MDE and variance diagnostics)

---

## 11. Limitations and Threats to Validity

### Internal Validity
- **Confound: Reranking Latency.** Longer corpus sizes may have higher latency; truncation or timeout may artificially degrade quality. **Mitigation:** Fix timeout per condition; report wall-clock time separately.
- **Annotator Drift.** Over weeks of labeling, crowdworkers' standards may shift. **Mitigation:** Re-calibrate every 200 labels; monitor κ over time.
- **Judge Severity (2608.29517).** LLM judges (if used for reader evaluation) vary in harshness. **Mitigation:** Report single judge's output; do not mix judges; consider multi-judge consensus.

### External Validity
- **Question Distribution.** Results depend on question source. Natural Questions bias toward web-searchable factoid questions; SCIQ is more science-specific. **Mitigation:** Stratify by question type; report subgroup estimates.
- **Corpus Composition.** Results depend on whether corpus mixes arXiv, Wikipedia, web. **Mitigation:** Document exact sources and proportions.
- **Embedding & Reranker Generalization.** Results specific to chosen models. **Mitigation:** Recommend follow-up ablation with different embeddings (e.g., OpenAI, Anthropic closed-source models) as separate study.

### Statistical Validity
- **Multiplicity.** 10 pairwise comparisons + multiple secondary metrics inflate Type I error. **Mitigation:** Bonferroni/Holm correction; report all tests.
- **Non-Normal Distributions.** nDCG, MRR may not be normally distributed. **Mitigation:** Use bootstrap CIs (percentile method) and non-parametric tests (Mann-Whitney U) as robustness checks.

---

## 12. Evidence Citations

This design relies on the following evidence excerpts:

1. **2010.06595** (Statistical power norms): Justifies power analysis and simulation-based sample-size planning; NLP experiments are underpowered.
2. **2605.30315** (Paired resolution targets): Provides MDE and resolution ratio framework (q = N/N*) to ensure experimental design is sufficiently powered.
3. **2607.13304** (Variance components allocation): Guides budget allocation across corpus-size conditions and question tiers using generalizability theory.
4. **2608.01913** (Retrieval vs. utilization gaps): Justifies separating retrieval recall from answer accuracy; introduces failure-mode taxonomy.
5. **2608.03501** (Stage isolation & redline scoring): Provides high-level (main + ablations) vs. low-level (datasets, metrics) design structure; redline mechanism for fatal flaws.
6. **2608.29517** (Judge severity and drift): Cautions that LLM judges vary by 8-15× rater SD; motivates crowdworker pool with multi-judge consensus.
7. **2609.00038** (Outcome-only blind spots): Justifies document-level (trajectory) evaluation over outcome-only judgments.

---

## 13. Next Steps Before Launch

1. **Pilot Study** (~100 labels, 1 week):
   - Annotate 50 questions × 2 corpus sizes (10k and 1M) × 2 judges.
   - Compute Fleiss' κ; if κ < 0.60, revise annotation guidelines and retry.
   - Estimate $\sigma_D$ from pilot differences; re-solve for N* if needed.

2. **Annotation Tool Setup:**
   - Deploy crowdsourcing interface (e.g., Prolific, Scale API, or custom web form).
   - Load question-document pairs and collect graded relevance (0–3).
   - Set up automated QC: flag patterns (e.g., all 3s, all 0s) for review.

3. **Infrastructure Provisioning:**
   - Create 5 indexed corpora (one per corpus size) using Weaviate or Elasticsearch.
   - Test retrieval latency at each corpus size; confirm no timeout issues.
   - Log embedding model version, reranker version, configuration (frozen).

4. **Analysis Script Preparation:**
   - Write Python notebooks for:
     - nDCG@10, MRR, Recall@50 computation from relevance labels
     - Bootstrap CI and resolution ratio calculations
     - LMM fitting and post-hoc tests
     - Visualization (profile plots, interaction plots, gap analysis)
   - Version control via git; document every script assumption.

5. **Stakeholder Alignment:**
   - Confirm with stakeholders: definition of "plateau" (e.g., nDCG drop < 0.05?), acceptable corpus sizes, inference priority (power vs. speed).
   - Finalize stopping rule thresholds (e.g., MDE = 0.02 nDCG).

---

## Summary

This design measures how retrieval and reranking pipeline quality responds to corpus scale using a stratified, budget-aware, power-informed evaluation. It explicitly separates retrieval gaps from utilization gaps, employs statistically motivated sample sizing, and halts data collection when uncertainty is sufficiently reduced or budget is exhausted. The sampling frame is scientific questions × corpus sizes (10k to 1M documents), stratified by difficulty. Resources are public (open datasets, open-source models, crowdworkers) and costs are documented. All findings are reported with resolution diagnostics (q-ratios) to indicate whether observed effects are distinguishable from noise.

