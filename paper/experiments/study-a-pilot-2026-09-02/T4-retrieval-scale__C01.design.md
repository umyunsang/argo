# Experimental Design: Retrieval and Reranking Evaluation at Corpus Scale

## Research Question

How should a retrieval and reranking pipeline for scientific question answering be evaluated as the corpus grows?

## Motivation and Problem Framing

Retrieval-augmented question answering systems exhibit scale-dependent behavior: as corpus size increases, the same retrieval pipeline may fail in new ways (e.g., false positives from large candidate sets, degraded recall despite larger corpus). Traditional evaluation fixes corpus size, making it unclear whether results generalize to production scale or which failure modes emerge at different scales. Given expensive relevance labels, efficient evaluation strategies become critical.

## Design Overview

**Main Comparison:** Retrieval-only (baseline) vs. Retrieval + Reranking (intervention), evaluated across three corpus sizes (small, medium, large). The primary comparison tests whether reranking becomes more valuable as corpus grows.

**Corpus Sizes:**
- Small: ~100K documents (in-memory feasible; high precision expected)
- Medium: ~1M documents (typical academic search corpus)
- Large: ~10M documents (production scale; evidence of saturation effects expected)

## Main Comparison Design

### Conditions

**Condition 1: Retrieval-Only (Baseline)**
- Single-stage: embed query, retrieve top-k using one embedding model and one sparse index
- k = 5 (production default for QA)
- Fixed: embedding model and sparse index unchanged across all three corpus sizes

**Condition 2: Retrieval + Reranking (Intervention)**
- Two-stage: retrieve top-m using same embedding model and sparse index (m = 100)
- Apply learned reranker (LLM-based, deterministic, cost-bounded) to reorder top-100
- Select top-5 for QA generation
- Same embedding model and sparse index, same retrieval step, but with additional ranking stage

**Rationale:** Reranking is cheaper than expanding the retrieval model. As corpus grows, retrievers degrade gracefully (more noise in top-100), making reranking more valuable. The design isolates reranking value by holding retrieval constant.

### Concrete Resources

**Embedding Model:** 
- use-case: scientific question answering
- Choice: one of {Sentence-BERT (all-MiniLM-L6-v2), E5-small, BGE-small} — chosen by availability and reproducibility
- Frozen across all conditions and corpus sizes

**Sparse Index:** 
- Choice: BM25 via Elasticsearch or Lucene (one index per corpus size, reindexed at small/medium/large)
- Provides rank-m candidates for reranking stage; standard/reproducible

**Reranker:**
- Choice: GPT-4-based ranker (zero-shot prompt or few-shot with 2-3 examples)
- Cost constraint: rank 100 documents per query
- Why LLM: captures semantic relevance better than learned linear ranker at scale; cold-start (no fine-tuning needed)

**Datasets:**
- Primary: MS MARCO passages + SQuAD-style QA pairs (public, fixed, ~100K questions available)
- Corpus construction: subsample MS MARCO passages to create three corpus sizes (100K, 1M, 10M); maintain same document pool, vary corpus membership
- Relevance labels: use available human labels from MS MARCO for small/medium corpus; for large corpus, use weak labels (hybrid approach, see Uncertainty section)

## Ablations

### Ablation 1: Reranker Type (to isolate reranking signal)

**A1a:** Dense-only reranker (e.g., cross-encoder, pre-trained)
- Measure: does LLM-based reranking outperform dense cross-encoder?
- Justification: separates "better ranker" from "LLM as a tool" effect; addresses citation evidence 2310.11511 (self-critique) vs 2405.14831 (single-step structured retrieval)

**A1b:** No reranking (retrieve only; also your Condition 1)
- Measure: confirm baseline; compare to both reranker types

### Ablation 2: Corpus Scaling Mechanism (to isolate corpus-size effect from distribution shift)

**A2a:** True corpus growth (add new, in-domain documents)
- Small: 100K curated high-quality papers
- Medium: 100K + 900K relevant papers
- Large: 1M + 9M papers (including lower-quality/peripheral papers)
- Rationale: realistic; introduces gradual distribution shift

**A2b:** Fixed-corpus repeated sampling (keep same document pool, sample differently)
- All sizes: sample 100K, 1M, 10M from the *same* document pool uniformly
- Rationale: isolates corpus size effect from distribution shift
- Comparison: if A2b shows no degradation, the problem is corpus composition, not scale per se

## Analysis Plan

### Primary Analysis

1. **Performance Curves by Corpus Size**
   - Metric: Mean Reciprocal Rank (MRR@5) for each condition and corpus size
   - Plot: MRR@5 (y-axis) vs. corpus size in log scale (x-axis)
   - Hypothesis: Retrieval-only degrades with corpus growth; Retrieval+Reranking degrades slower
   - Evidence source: Analogous to retrieval vs. utilization gap analysis in 2608.01913

2. **Reranking Gain (Delta)**
   - Metric: Δ MRR@5 = MRR@5(Retrieval+Reranking) - MRR@5(Retrieval-Only) for each corpus size
   - Plot: reranking gain (y-axis) vs. corpus size (x-axis)
   - Hypothesis: Gain increases with corpus size (reranking becomes more necessary)

3. **Cumulative Retrieval Recall**
   - Metric: fraction of relevant documents retrieved in top-100 by corpus size
   - Rationale: diagnoses whether retrieval saturation or reranking signal loss drives performance delta (from 2608.01913's retrieval vs. utilization decomposition)

### Secondary Analyses

4. **Stratified by Question Complexity** (following 2403.14403)
   - Tag questions by complexity (simple vs. multi-hop) using a small fixed classifier
   - Measure: does reranking gain vary by complexity?
   - Hypothesis: reranking helps complex questions more (more noise in top-100)

5. **Cost-Adjusted Efficiency**
   - Metric: Utility = MRR@5 / (LLM tokens for reranking)
   - Rationale: reranking is not free; as corpus grows, cost may exceed gain (see cost analysis in 2405.14831)

6. **Ablation 1 Comparison: Reranker Types**
   - Plot: MRR@5 for LLM ranker vs. cross-encoder vs. none, by corpus size
   - Hypothesis: LLM ranker is more stable at large corpus size; cross-encoder may plateau

7. **Ablation 2 Comparison: Corpus Growth vs. Fixed Sampling**
   - Plot: MRR@5 for A2a (true growth) vs. A2b (fixed sampling)
   - If A2b shows no degradation: corpus composition is the driver
   - If A2a shows more degradation: distribution shift exacerbates scale effects

### Statistical Analysis

**Power and Resolution** (following 2010.06595 and 2605.30315):
- Each condition × corpus size: plan N=500 questions (see Label Budget section)
- For each condition pair and corpus size, compute: 
  - Effect size δ = (μ₁ - μ₂) / σ (estimated from pilot on medium corpus)
  - Sample size needed for 80% power at α=0.05 using paired t-test (or non-parametric alternative if MRR is skewed)
  - Resolution ratio q = N_actual / N_required (must be ≥1)
- Report: q for each hypothesis test, unresolved comparisons flagged

**Variance Decomposition** (following 2607.13304):
- Model: MRR ~ Corpus Size + Condition + Question Complexity + (1 | Question) + (1 | Document Sample)
- Decompose: total variance into question variance, question-document interaction, within-question noise
- Allocation: if question variance is large, invest more questions; if document sample variance dominates, try multiple resamples

### Handling Label Scarcity

**Label Budget:** Assume access to ~5000 relevance labels (expensive; realistic budget).

**Strategy:**
- Small corpus (100K): use all available MS MARCO labels (abundant; no budget constraint)
- Medium corpus (1M): subsample MS MARCO labels to ~2000 unique questions with relevance judgments
- Large corpus (10M): use weak labels (hybrid approach)
  - BM25 score as weak label proxy (documents ranked by BM25 ≥ threshold as relevant)
  - Validate on ~500 gold labels to estimate label quality
  - Measure: how much does weak label noise inflate variance / reduce detectable effect size?
  - Report: label quality (precision of BM25 labels), adjusted effect sizes (see 2608.01913 on evidence saturation)

**Sensitivity Analysis:**
- Rerun primary analysis on three label-quality scenarios (gold, high-quality weak, low-quality weak)
- Plot: MRR@5 under each scenario; if reranking gain persists, conclusion is robust

## Outcome Metrics

| Metric | Definition | Primary? | Rationale |
|--------|-----------|----------|-----------|
| MRR@5 | Mean Reciprocal Rank of first relevant doc in top-5 | Yes | Standard QA metric; directly comparable across scales |
| Retrieval Recall@100 | % relevant docs in top-100 retrieved set | Yes | Diagnoses whether reranking has "good candidates" (2608.01913) |
| Precision@5 | % of top-5 results relevant | Yes | User-facing; what practitioners care about |
| Reranking Gain (Δ MRR@5) | Difference in MRR@5 between conditions | Yes | Answers main comparison directly |
| Cost per Query (LLM tokens) | Tokens used by reranker per query | Secondary | Essential for production viability |
| Utility = MRR@5 / Cost | Efficiency metric | Secondary | Balances performance and expense |
| Label Quality (Precision of Weak Labels) | Agreement between weak and gold labels | Secondary | Justifies large-corpus results |

## Quantifying Uncertainty

### Sources of Uncertainty

1. **Sampling uncertainty:** finite question set introduces noise around estimated MRR@5
2. **Label uncertainty:** weak labels in large corpus add noise to ground truth
3. **Retrieval variance:** embedding/index may have inherent randomness (tokenization, tie-breaking)
4. **Reranker variance:** LLM ranker is stochastic (temperature=0 assumed; if not, use multiple runs)

### Quantification Methods

**Method 1: Confidence Intervals via Bootstrap**
- For each condition and corpus size, bootstrap resample questions (with replacement) 1000 times
- Compute MRR@5 per resample
- Report: 95% CI (2.5th, 97.5th percentiles)
- Plots: overlay CIs on main performance curves; if CIs don't overlap between conditions at a corpus size, claim is robust

**Method 2: Bayesian Posterior (Optional)**
- Model: MRR ~ N(μ, σ²)
- Priors: μ ~ N(0.4, 0.05²) (weak; based on typical QA performance), σ² ~ Inv-Gamma(2, 0.1)
- Posterior: compute via MCMC or variational Bayes
- Report: posterior credible intervals (95% HDI) for MRR@5 and Δ MRR@5
- Advantage: naturally incorporates prior knowledge and label uncertainty (see 2607.13304 on generalizability theory)

**Method 3: Power Analysis and Resolution (Paired-Test Frame)**
- Following 2605.30315: frame as paired hypothesis test H₀: μ₁ = μ₂ for each corpus size
- Compute minimum detectable effect (MDE) given N=500 questions and α=0.05, 1-β=0.8
- Report: MDE per corpus size; if observed effect is smaller than MDE, result is underpowered
- Resolution ratio q = |effect| / MDE (q ≥ 1 means resolved; q < 1 means underpowered)

**Method 4: Sensitivity to Label Quality**
- For large corpus (weak labels), run analysis under three label-quality regimes (gold, 80% precision weak, 60% precision weak)
- Plot: MRR@5 and confidence intervals across label-quality scenarios
- If reranking gain persists across all, conclusion is robust to label noise

## Experiment Execution Plan

### Phase 1: Pilot (Weeks 1–2)
- Small corpus only; Retrieval-only vs. Retrieval+Reranking; N=100 questions
- Estimate effect size, variance, cost, label availability
- Compute sample size for Phase 2 using formulas from 2010.06595

### Phase 2: Main Study (Weeks 3–8)
- All three corpus sizes; both main conditions; Ablation 1 (reranker type)
- N=500 questions per condition-corpus pair (3 corpus × 2 conditions × 500 = 3000 query-runs + ablation runs)
- Collect all labels (gold for small/medium, weak for large with validation)
- Run primary and secondary analyses

### Phase 3: Sensitivity (Week 9)
- Ablation 2: fixed-corpus sampling
- Label-quality scenarios
- Rerun analyses; compare to Phase 2

### Phase 4: Writing and Reporting (Week 10)
- Produce tables and figures (power analysis, performance curves, CIs, ablations)
- Report unresolved comparisons; discuss limitations

## Potential Pitfalls and Mitigations

| Pitfall | Mitigation |
|---------|-----------|
| Embedding/index bias favors retrieval at small scale | Run Ablation 2 (fixed-corpus); if no degradation, bias is the issue |
| LLM reranker not deterministic (high variance) | Use temperature=0; run 3 reranking passes per query for variance estimate |
| Label scarcity makes large-corpus results unreliable | Use weak labels + validation; report label quality; show sensitivity to label noise |
| Reranking cost dominates gain at large scale | Measure cost per query; compute utility metric; compare to dense cross-encoder cost |
| Questions/corpus interaction (some questions only hard in large corpus) | Use stratified analysis by complexity; report interaction effects |
| Distribution shift between corpus sizes confounds scale effect | Ablation 2 isolates this; compare true growth (A2a) to fixed-pool sampling (A2b) |

## Justification for Design Choices

### Why Paired Retrieval + Reranking, not retrieval-only variants?
**Evidence:** 2405.14831 (HippoRAG) shows single-step retrieval with structured indexing can match iterative retrieval at lower cost. Reranking is a pragmatic two-stage alternative to retrieval retraining. 2310.11511 (SELF-RAG) shows on-demand retrieval + critique is learnable and efficient.

### Why three corpus sizes and not more granular sampling?
**Evidence:** 2608.01913 proposes retrieval vs. utilization gap analysis; small/medium/large corpus creates three clear regimes. More granular sampling wastes labels.

### Why weak labels for large corpus?
**Evidence:** 2606.07591 (ResearchClawBench) shows rubric-based partial labeling can scale; 2607.13304 (variance components) shows how to allocate label budget across conditions. Weak labels are standard practice when budget is tight.

### Why power analysis?
**Evidence:** 2010.06595 shows NLP experiments are frequently underpowered; 2605.30315 shows leaderboard comparisons fail resolution targets. Must report power and resolution ratio.

### Why outcome-only analysis insufficient?
**Evidence:** 2609.00038 (trajectory-judge) shows outcome-only evaluation misses silent failures. Ablation 2 (fixed-corpus) and cumulative recall analysis diagnose where performance comes from.

### Why generalizability theory for variance?
**Evidence:** 2607.13304 shows crossed-effects decomposition reveals which sources of noise matter most (question vs. reranker vs. document sample). Informs label allocation strategy.

---

## References (Evidence Files Used)

1. **2010.06595** — Card et al., "With Little Power Comes Great Responsibility": power analysis, sample size planning, underpowered experiments, power norms in NLP.

2. **2310.11511** — Asai et al., "SELF-RAG": on-demand retrieval, critique tokens, adaptive retrieval-augmented generation.

3. **2403.14403** — Jeong et al., "Adaptive-RAG": complexity-conditioned routing, strategy selection, multi-stage retrieval.

4. **2405.14831** — Gutiérrez et al., "HippoRAG": single-step structured retrieval, knowledge graphs, efficiency gains vs. iterative methods.

5. **2605.30315** — Kotawala, "Resolution Diagnostics for Paired LLM Evaluation": paired hypothesis testing, minimum detectable effect, resolution ratio, underpowered leaderboards.

6. **2606.07591** — Shanghai AI Lab, "ResearchClawBench": rubric-based evaluation, partial/multimodal labeling, scaling evaluation.

7. **2607.09195** — Takahara & Mizoguchi, "Hypothesis Evolution Protocol": externalized state, auditable reasoning, belief-evidence-hypothesis cycles.

8. **2607.13304** — Zatuchin, "Variance-Components Decomposition": generalizability theory, crossed random effects, repeat allocation, label budget.

9. **2608.01913** — Liu et al., "Diagnosing Search Behavior": retrieval vs. utilization gaps, cumulative recall, trajectory analysis.

10. **2608.03501** — Liu et al., "Can LLM design high-quality experiments?": stage isolation, redline scoring, experimental design quality benchmarking.

11. **2608.29517** — Sunkavalli, "LLM Judges as Raters": rater effects (severity, halo, drift), generalizability studies, rater-effects batteries.

12. **2609.00038** — Mohammadi, "trajectory-judge": outcome-only blind spots, silent vs. loud failures, trajectory-level diagnosis.

---

## Appendix: Label Budget Breakdown

| Corpus | Size | Strategy | Labels Needed | Budget |
|--------|------|----------|---------------|--------|
| Small | 100K | All gold (MS MARCO available) | ~2000 questions × 1–3 labels each | ~3000 labels |
| Medium | 1M | Subsample gold labels | ~2000 questions × 1–3 labels each | ~2000 labels |
| Large | 10M | Weak labels (BM25 ≥ threshold) + validation | ~1000 queries with weak, ~500 gold for validation | ~1500 labels |
| **Total** | — | — | — | **~6500 labels** |

**Note:** Assumes 5000-label budget is available (realistic for academic study). If tighter, deprioritize large-corpus gold validation or reduce question count.
