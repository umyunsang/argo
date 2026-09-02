# Experimental Design: T2-Orchestration-Cost

## 1. Research Question and Decision Frame

**Research Question:** Do multi-call orchestrations (iterative retrieval, step-by-step reasoning, 
self-correction loops) improve task accuracy enough to justify the additional inference cost 
(tokens and latency) they consume, compared to single-call baselines?

**Decision Context:** As LLM inference costs commoditize, whether orchestration overhead scales 
justifiably is a production-level question. The null hypothesis is that orchestration cost exceeds 
justified accuracy gain.

---

## 2. Sampling Frame

**Population:** Multi-hop open-domain question-answering tasks from HotpotQA (or 2WikiMultiHopQA), 
meeting the sampling frame criteria:
  - Known ground-truth answers (string or span level, human-verified)
  - Item-level baseline accuracy estimates (from prior LLM-backbone runs, stratified by annotator 
    consensus on reasoning-step count required)
  - Diverse reasoning paths requiring 2+ retrieval/composition steps

**Unit of Analysis:** Individual question-answer attempt, i.e., a single tuple 
(question_id, model_backbone, orchestration_method).

**Sampling Strategy (stratified random allocation):**
  - Stratify HotpotQA by baseline difficulty (3-tier: easy [>80% baseline], medium [50–80%], 
    hard [<50%]) using prior runs on single-call baselines.
  - Allocate 500 total questions: ~166 per difficulty tier.
  - Randomly sample within each tier without replacement.
  - Repeat each question-method combination 2 times (to capture within-prompt variance; 
    justified by 2607.13304 variance decomposition).

**Total sample:** 500 questions × 2 backbones × 3 methods × 2 repeats = **6,000 inference attempts**.

**Justification (citing evidence):**
  - HotpotQA is standard in 2403.14403 (Adaptive-RAG) and 2405.14831 (HippoRAG) for evaluating 
    orchestration cost-benefit.
  - Difficulty stratification ensures power for subgroup analysis (2010.06595 mandatory for NLP).
  - 500 items is minimum for 80% power to detect 1.5-point accuracy difference (2010.06595 norms).
  - 2× repeat balances variance estimation (2607.13304) against budget constraints.

---

## 3. Interventions and Conditions

### Main Comparison: Single-Call vs. Multi-Call Orchestration

**Condition A (Control): Single-Call Direct Answer**
  - Prompt: "Answer the following question: [question]"
  - Model generates answer in a single forward pass.
  - No intermediate reasoning steps, no retrieval, no self-correction.
  - Cost: 1 forward pass; tokens = input + output tokens.

**Condition B (Treatment 1): Iterative Retrieval (IR)**
  - Prompt: "[question] Find relevant passages step by step."
  - Model issues retrieval queries (e.g., via BM25 or dense retrieval API), incorporates passages, 
    re-queries if needed.
  - Orchestration depth: up to 3 retrieval cycles (or until model declares "sufficient").
  - Cost: 1 + N retrieval queries (N ∈ {1, 2, 3}) + composition pass.
  - Approximate multiplier (prior estimate from 2405.14831): 2–5× tokens vs. Condition A.

**Condition C (Treatment 2): Chain-of-Thought + Self-Correction (CoT-SC)**
  - Prompt: "[question] Break this into steps. First, reason. Then, check your reasoning."
  - Model emits step-by-step solution, then re-evaluates each step for errors.
  - Orchestration depth: reasoning phase + verification phase (2 internal loops).
  - No external retrieval; pure reasoning orchestration.
  - Cost: ~2× tokens vs. Condition A (two full-problem generations).

**Model Backbones:** Test across 2 backbones to avoid backbone-specific confounds:
  - Backbone 1: Llama-2-70B (or equivalent open-weights baseline)
  - Backbone 2: GPT-3.5-Turbo (or equivalent closed API)

**Design Justification (citing evidence):**
  - 2405.14831 (HippoRAG) tests iterative vs. single-step and finds single-step often sufficient, 
    justifying the control.
  - 2403.14403 (Adaptive-RAG) separates retrieval orchestration from reasoning orchestration; 
    testing both captures breadth.
  - Multiple backbones reduce model-specific artifacts (2607.13304 variance on model identity).

---

## 4. Outcome Metrics

### Primary Metrics (accuracy and cost)

**Metric 1: Task Accuracy (Exact Match + F1)**
  - Exact Match (EM): Binary indicator whether model output exactly matches gold answer span.
  - F1 Score: Token-level F1 between output and gold (handles partial/paraphrase answers).
  - Aggregate: Accuracy_overall = mean(EM) per condition; F1_overall = mean(F1).
  - Unit: Percentage points (0–100).

**Metric 2: Inference Cost (Token Count)**
  - Total tokens = input_tokens + output_tokens for all passes (retrieval queries, reasoning steps, etc.).
  - Cost multiplier = tokens_method_X / tokens_Condition_A.
  - Unit: Dimensionless ratio; also report absolute tokens per question.

**Metric 3: Accuracy-Adjusted Cost Ratio**
  - Define: Cost-per-accuracy-point = (cost_method_X / cost_A) / (accuracy_method_X / accuracy_A).
  - Ratio < 1.0 means method X gains more accuracy than it costs. Ratio > 1.0 means overhead 
    is not justified.
  - Unit: Dimensionless; interpreted as "cost multiplier per accuracy multiplier."

**Metric 4: Trajectory Quality Score (Secondary)**
  - Rubric-based evaluation of intermediate reasoning (retrieved passages marked as 
    "relevant," reasoning steps marked as "sound logic," self-corrections marked as "corrected actual error").
  - Rubric scoring (0–100 per trajectory) captures orchestration value invisible to outcome-only judges.
  - Justification: 2609.00038 shows outcome-only judges miss 55% of trajectory failures; 
    step-rubric achieves 77% recall.
  - Scoring: Two expert raters (or trained LLM + human verification on 10% of sample) 
    independently score ~100 randomly selected trajectories per condition.

---

## 5. Ablations

### Ablation 1: Difficulty-Stratified Effect Sizes

Separate the accuracy and cost gains by question difficulty (easy, medium, hard).

**Hypothesis:** Multi-call orchestration provides the most benefit on hard questions (where 
single-call baseline is weakest) and minimal benefit on easy questions (ceiling effect).

**Prediction:** Cost-per-accuracy-point ratio improves (decreases) as difficulty increases. 
E.g., hard questions: ratio = 0.8 (justified), medium: ratio = 1.2 (borderline), easy: ratio = 1.5+ 
(unjustified).

**Justification (citing evidence):** 2403.14403 shows routing decisions depend on query complexity; 
2608.01913 finds evidence retrieval and use vary by task. Ablation confirms orchestration is 
targeted, not blanket.

### Ablation 2: Orchestration Depth Sensitivity

For Condition B (IR), measure accuracy and cost as a function of retrieval depth 
(1 retrieval cycle vs. 2 vs. 3).

**Hypothesis:** Accuracy gains plateau after 2 cycles (diminishing returns), but cost grows linearly.

**Prediction:** Depth=1 provides 70% of depth=3 accuracy gain at 30% of depth=3 cost.

**Justification (citing evidence):** 2608.01913 finds evidence quality plateaus early in search 
trajectories; 2405.14831 shows single-step retrieval often matches iterative. Ablation reveals 
optimal depth tradeoff.

### Ablation 3: Backbone Interaction

Test whether accuracy-cost ratio is consistent across Llama-2-70B and GPT-3.5-Turbo, or 
if one backbone benefits disproportionately from orchestration.

**Hypothesis:** Cost-per-accuracy ratio is backbone-invariant (orchestration is universally justified 
or not).

**Prediction:** Ratio differences <0.2 (relative) between backbones; if >0.2, orchestration favors 
larger models.

**Justification (citing evidence):** 2607.13304 shows model identity is a major variance component; 
ablation checks generalizability across backbones (required before production deployment).

---

## 6. Analysis Plan


**Methodological Framework:** This analysis plan follows the stage-isolation approach from 2608.03501 (SCOPE), separating hypothesis testing (Steps 1–3) from configuration choices (datasets, metrics) to improve rigor.

### Primary Analysis

**Step 1: Descriptive Summary (by condition)**
  - Report Accuracy_EM, Accuracy_F1, Cost_tokens, Cost_multiplier for each condition.
  - Table: Condition × [EM%, F1%, tokens, cost ratio]

**Step 2: Null Hypothesis Test**
  - H0: Accuracy gain (multi-call vs. single-call) is ≤ 0.5 percentage points absolute.
  - Test: Two-sided paired t-test on EM scores, stratified by difficulty tier.
  - α = 0.05; report 95% confidence intervals for accuracy differences.
  - Justification: 2010.06595 sets 1-2 points as typical detectable effect in NLP; 0.5 points is 
    conservative.

**Step 3: Cost-Adjusted Hypothesis Test**
  - Test: Does Cost-per-accuracy-point ratio significantly differ from 1.0 (break-even)?
  - Method: Bootstrap confidence interval on ratio (10,000 resamples).
  - Decision rule: If 90% CI is entirely <1.0, multi-call is justified; if entirely >1.0, not justified; 
    if CI crosses 1.0, inconclusive.

**Step 4: Subgroup Analysis**
  - Repeat Step 2 separately for each difficulty tier (easy, medium, hard).
  - Hypothesis: Orchestration benefit increases with question difficulty.

**Step 5: Pareto Frontier**
  - Plot accuracy vs. cost for all 3 conditions.
  - Identify which condition (or method-backbone pairing) is Pareto-optimal (maximum accuracy 
    for given cost budget).
  - Report: For each condition, what accuracy–cost tradeoff does it offer?

### Secondary Analysis (Trajectory Quality)

**Step 6: Rubric Score Correlation**
  - Compute Pearson r between trajectory quality scores and final accuracy (EM).
  - Hypothesis: Trajectory quality predicts final accuracy; orchestration methods score higher.
  - Justification: Validates that trajectory-aware rubrics capture meaningful signal (2609.00038, 2607.09195).

**Step 7: False Positive / False Negative Rates**
  - Among trajectories where final answer is correct (true positive):
    - What % show high trajectory quality (true positive signal)?
  - Among trajectories where final answer is incorrect (true negative):
    - What % show low trajectory quality (true negative signal)?
  - Hypothesis: Step-rubric judges have >70% sensitivity and >60% specificity (per 2609.00038 baseline).

---

## 7. Power Analysis and Sample Size Justification

**Target Effect Size:** 1.5 percentage point absolute accuracy difference (e.g., 65% → 66.5%).
  - Based on 2010.06595: GLUE benchmarks require ~1,000–10,000 examples to power 1–2 point differences.

**Target Power:** 80% (1 − β = 0.8).

**Type I Error Rate:** α = 0.05 (two-sided).

**Sample Size Calculation:**
  - Assume baseline accuracy = 60%, effect size δ = 1.5 points.
  - Using paired t-test (repeated measures), SD ≈ 20% (conservative estimate from prior runs).
  - Minimum N (paired t-test): N ≈ 400 pairs (from g*power or similar).
  - Planned N: 500 questions (166 per difficulty tier) × 2 repeats = 1,000 measurements per condition.
  - Justification: Exceeds minimum by 2.5× to account for:
    - Repeated stratification by difficulty (reduces effective N if unbalanced).
    - Loss to invalid responses (e.g., refusals, malformed outputs).
    - Variance heterogeneity across difficulty tiers.

**Stopping Rule (from state.md):**
  - Stop collecting once power analysis confirms 80% power for 1.5-point difference.
  - Interim analysis after ~250 questions (stratified, similar difficulty distribution): if 
    preliminary CI for difference is tight (width <1 point), stop early.

---

## 8. Concrete Resources and Infrastructure


**Design Rationale:** Concrete resource specification follows 2608.03501 practice: all datasets, tools, and APIs named explicitly and publicly available for reproducibility.

### Datasets

**Primary Benchmark:** HotpotQA (Wikipedia open-domain multi-hop QA)
  - Version: Official test set (10,564 questions, released 2018, persistent).
  - Utility: Multi-hop reasoning is the canonical test for orchestration cost-benefit.
  - Access: Publicly available via Hugging Face (huggingface.co/datasets/hotpot_qa).
  - Baseline runs: Use prior published accuracies (e.g., from papers using HotpotQA) to estimate 
    difficulty tiers if fresh baseline runs are prohibitive.

**Retrieval Corpus:** Wikipedia dump (included with HotpotQA; or use Dense Passage Retrieval 
pre-indexed corpus from Facebook Research).

### Model Backbones

**Backbone 1: Llama-2-70B**
  - Source: Meta, available via Hugging Face or LMSYS OpenAI-compatible API (llama-2-70b-chat).
  - Rationale: Open-weights standard; allows reproducibility and ablation on model size/training.
  - Cost: ~$0.50 per 1M tokens (from LMSYS pricing) × 6,000 attempts × ~1,000 tokens avg ≈ $3,000.

**Backbone 2: GPT-3.5-Turbo**
  - Source: OpenAI API.
  - Rationale: Closed, widely-used production model; tests backbone generalization.
  - Cost: ~$0.0005 per 1K tokens (2025 pricing) × 6,000 attempts × ~1,000 tokens avg ≈ $3,000.

**Total model cost:** ~$6,000 (both backbones, all conditions and repeats).

### Retrieval Infrastructure

**Option A (Lightweight):** BM25-based sparse retrieval
  - Tool: Elasticsearch or Pyserini (open-source, free).
  - Setup: Index Wikipedia dump (~21 million articles; ~50 GB disk).
  - Runtime: <100 ms per query.
  - Pro: Reproducible, no API cost. Con: Lower quality than dense retrieval.

**Option B (Recommended):** Dense retrieval (DPR or ColBERT)
  - Pre-indexed corpus: Facebook AI Research released DPR Wikipedia index 
    (github.com/facebookresearch/DPR).
  - Tool: Hugging Face Transformers + faiss for efficient nearest-neighbor search.
  - Setup: One-time indexing (~2 hours on single GPU); queries <100 ms.
  - Cost: Single GPU rental (~$0.50/hr) × 2 hr ≈ $1.

### Evaluation and Scoring

**EM/F1 Scoring:** SQuAD evaluation script (publicly available, deterministic).
  - Tool: huggingface.co/evaluate (hosted evaluation metric).
  - Cost: Free (runs locally).

**Trajectory Quality Rubric:** Custom rubric or fine-tuned LLM scorer.
  - Option A: Hand-score ~100 trajectories per condition (10+ hours human effort).
  - Option B: Train LLM classifier on 50 hand-scored examples, then auto-score remainder 
    (lower cost, introduces model-as-rater bias; mitigate via inter-rater agreement on 10% sample).
  - Time: Option A ≈ 50 hours; Option B ≈ 10 hours (training) + 5 hours (verification).

### Compute and Storage

**Inference:** 6,000 API calls (model renting) + retrieval queries (~1 per question × 3 methods × 2 repeats 
= ~6,000 retrieval queries).
  - Total wall-clock time: ~2 weeks (parallelizable; batching reduces wall time to ~3–5 days).
  - Storage: ~500 MB for trajectories (logs of prompts, outputs, reasoning steps).

**Analysis:** Local machine (any laptop with Python + Jupyter).
  - Libraries: numpy, scipy, pandas, matplotlib, seaborn, scikit-learn.
  - Time: ~5 hours (implementation, analysis, visualization).

**Total Resource Budget:** ~$6,000 (models) + $1 (GPU) + ~100 hours human effort (experimental 
runs, rubric annotation, analysis). Wall-clock time: 3–5 weeks (including parallel inference).

---

## 9. Outcome Metrics and Uncertainty Quantification

### Primary Metrics

| Metric | Calculation | Unit | Uncertainty |
|--------|-------------|------|-------------|
| Accuracy (EM) | Prop. of exact matches vs. gold | % | 95% CI via binomial proportion test |
| Accuracy (F1) | Mean token-level F1 | 0–100 | 95% CI via t-test on per-question F1 |
| Cost (tokens) | Sum of input + output tokens | tokens | Range (min–max) + mean ± SD |
| Cost Multiplier | Cost_method / Cost_baseline | ratio | 90% bootstrap CI (10k resamples) |
| Cost-per-Acc Ratio | (Cost_mult) / (Acc_mult) | ratio | 90% bootstrap CI; break-even = 1.0 |

### Uncertainty Quantification Strategy

**Strategy 1: Frequentist Confidence Intervals**
  - For accuracy differences (EM, F1): Two-sided paired t-test, stratified by difficulty tier.
  - Report 95% CI; interpret as: "If we repeated the experiment, 95% of similar studies would 
    report a difference in this interval."

**Strategy 2: Bootstrap Resampling**
  - For cost ratio and cost-per-accuracy ratio: Resample (with replacement) questions 10,000 times 
    within each difficulty tier; recompute ratios; report 90% quantile interval.
  - Pro: Robust to non-normal distributions (cost data often right-skewed).
  - Justification: 2607.13304 uses bootstrap for variance decomposition.

**Strategy 3: Bayesian Posterior (Sensitivity)**
  - Specify weakly informative prior on accuracy gain (Normal, mean = 1%, SD = 3%).
  - Update with observed likelihood; report posterior median and 90% credible interval.
  - Use prior from 2405.14831 (HippoRAG baseline: ~5–10% accuracy gain, 10–20× cost reduction) 
    to conduct sensitivity analysis: "If prior is correct, how likely is our observed result?"

**Strategy 4: Heterogeneity by Subgroup**
  - Separately report accuracy and cost metrics for easy, medium, and hard question tiers.
  - Forest plot: Effect size (with CI) on x-axis, difficulty tier on y-axis, to visualize 
    whether orchestration benefit concentrates in a subgroup.

---

## 10. Stopping Rules and Decision Thresholds

(Detailed stopping rules also in state.md; repeated here for completeness.)

**Primary Stopping Rule:**
  - Collect at least 500 questions (stratified per difficulty tier) across 2 backbones 
    and 2 repeats.
  - Power Check: After 250 questions, compute observed SD of accuracy differences. Re-estimate 
    power to detect 1.5-point difference. If post-hoc power >= 80%, declare stopping rule met.
  - Budget Constraint: If token budget (e.g., 100 million tokens) is exhausted before 500 questions, 
    stop and report Bayesian posterior.

**Decision Rule for Research Question:**
  - Justified Orchestration: Cost-per-accuracy-point ratio < 1.0 at 90% CI (entirely below break-even).
  - Unjustified Orchestration: Ratio > 1.0 at 90% CI (entirely above break-even).
  - Inconclusive: 90% CI crosses 1.0. Recommend running a larger study or seeking additional 
    evidence (e.g., from 2405.14831).

**Falsifier Thresholds (from state.md):**
  - Main falsifier triggered: Accuracy gain < 0.5 pp and cost multiplier > 2.0 across all 
    difficulty tiers. Interpretation: Orchestration is too expensive.
  - Secondary falsifier triggered: Baseline accuracy > 85% (ceiling effect). Interpretation: 
    No room for improvement; research question is moot on this benchmark.
  - Tertiary falsifier triggered: Accuracy gain > 2 pp and cost multiplier < 1.1. 
    Interpretation: Orchestration is always justified; no trade-off to study.

---

## 11. Reporting Plan

### Figures and Tables

**Table 1: Descriptive Summary**
  - Rows: Condition (A, B, C) × Backbone (Llama, GPT) × Difficulty (Easy, Medium, Hard)
  - Columns: N (sample size), EM%, F1%, Avg Tokens, Cost Multiplier, Cost-per-Acc Ratio
  - Include 95% CI for EM%, 90% CI for Cost Ratio

**Table 2: Hypothesis Tests**
  - Accuracy difference (Condition B vs. A, Condition C vs. A)
  - Per difficulty tier; report t-statistic, p-value, 95% CI, power (post-hoc)

**Figure 1: Accuracy–Cost Pareto Frontier**
  - X-axis: Cost multiplier (log scale); Y-axis: Accuracy (EM%)
  - Scatter plot: Each point = Condition × Backbone × Difficulty
  - Overlay Pareto frontier (convex hull)

**Figure 2: Cost-per-Accuracy-Point Ratio by Difficulty**
  - X-axis: Difficulty tier (easy, medium, hard)
  - Y-axis: Ratio (log scale, break-even at 1.0)
  - Error bars: 90% bootstrap CI
  - Horizontal line at ratio = 1.0 (break-even)

**Figure 3: Trajectory Quality vs. Final Accuracy**
  - Scatter: Trajectory quality score (rubric, x-axis) vs. EM (y-axis)
  - Color by condition (A, B, C)
  - Overlay regression line + r, p-value

### Reporting Norms

- **Cite evidence:** Every design choice explicitly cites one or more evidence documents.
- **Transparency:** Report all analyses (main + secondary + ablations); do not selectively report.
- **Reproducibility:** Release anonymized trajectories (prompt, output, reasoning steps, 
  retrieved passages) and analysis code via GitHub.
- **Falsifiability:** Specify stopping rules and decision thresholds in advance (this document 
  serves as pre-registration).

---

## 12. Limitations and Sensitivities

1. **Benchmark-Specific:** Results on HotpotQA may not generalize to other reasoning tasks 
   (e.g., math word problems, legal reasoning). Consider replication on 2WikiMultiHopQA or 
   another benchmark if time permits.

2. **Model-Specific:** Results on Llama-2-70B and GPT-3.5-Turbo may not apply to newer models 
   (e.g., GPT-4, Llama-3). Recommend re-running on newest open-weights baseline as models evolve.

3. **Orchestration Implementation:** Cost and accuracy depend on the specific implementation 
   (e.g., number of retrieval cycles, prompt wording for self-correction). Design isolates 
   orchestration strategy, not implementation details; variations in implementation may shift 
   cost-benefit.

4. **Rubric Reliability:** Trajectory quality scoring is subjective. Mitigate via two raters + 
   inter-rater agreement kappa > 0.60 on 10% sample; if kappa < 0.60, retrain or use automated 
   rubric.

5. **Cost Model:** API pricing is time-sensitive; actual cost may differ from estimate if pricing 
   changes or if models are hosted on different infrastructure (e.g., on-premises vs. cloud). 
   Report in token units (reproducible) alongside USD (time-specific).

---

## 13. Connections to Prior Work and State.md

This design directly operationalizes the research state documented in state.md:

- **decision_id:** T2-orchestration-cost ↔ Research question and decision frame (§1)
- **question:** Defined in §1 and operationalized via primary metrics (§4)
- **sampling_frame:** HotpotQA multi-hop QA, stratified by difficulty (§2; explicitly cites 
  population and unit)
- **evidence_used:** Cited in-line throughout (§2, §3, §4, §5, §7; every choice traces to a 
  specific evidence document)
- **falsifier:** Operationalized as decision thresholds (§10)
- **stopping_rule:** Detailed in §10; primary rule is 500 stratified questions + power check at 250

---

## 14. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup (dataset, API keys, retrieval index) | 1 week | Ready-to-run inference pipeline |
| Data collection (inference × 3 conditions × 2 backbones × 2 repeats) | 2–3 weeks | 6,000 trajectories (logs) |
| Rubric annotation (100 trajectories per condition) | 1 week | Scored rubric dataset |
| Analysis (statistical tests, Pareto frontier, subgroup analysis) | 1 week | Analysis notebook + figures |
| Writing and reporting | 1 week | Final report + reproducible code |
| Total | ~6–7 weeks | Ready for peer review or publication |
