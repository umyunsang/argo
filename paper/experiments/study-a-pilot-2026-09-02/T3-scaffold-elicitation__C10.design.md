# Experimental Design: Scaffold vs. Model Attribution in Agent Capability Scores

## 1. Research Question and Objective

**Primary question**: How much of the variance in published agent capability scores comes from the choice of scaffold (prompt, reasoning structure, planning method) versus the choice of model (LLM provider, parameter count, training data)?

**Objective**: Quantify the main effects of scaffold and model independently, and detect any significant interaction between them, using a factorial design with full Cartesian product coverage.

---

## 2. Main Comparison and Conditions

### 2.1 Factorial Design Structure

**Factors**:
- **Factor A (Scaffold)**: 3 levels (e.g., chain-of-thought, tree-of-thought, zero-shot)
- **Factor B (Model)**: 5 levels (e.g., GPT-4, Claude 3 Opus, Llama 70B, Gemini 2.0, Grok 3)

**Design**: 3 × 5 factorial, fully crossed, resulting in **15 treatment cells** (all combinations).

### 2.2 Sampling Frame

As specified in state.md:

> The population is all (scaffold, model) pairings from the Cartesian product of {3 scaffolds} × {5 models}. The sampling unit is a single (scaffold, model, task) trial where a task is one problem instance from the public multi-step task benchmark. Each task instance produces one performance score. The frame covers all 15 scaffold-model combinations, all available task instances from the benchmark (treating all instances as the replication unit), with all conditions held constant (identical task text, identical evaluation metrics, identical time budgets).

**Operationalization**:
- **Scaffold instantiation**: Implement each of the 3 scaffolds as separate prompt templates or reasoning chains that can be paired with any model without retraining. Validate that each scaffold represents a distinct architectural choice (e.g., explicit step labels, tree expansion, vs. single-pass reasoning).
- **Model instantiation**: Access each of the 5 models via their public APIs or local weights, ensuring identical sampling parameters (temperature, max_tokens, top_p) across all scaffolds.
- **Task population**: Use all task instances available from the chosen public multi-step benchmark (expected ≥10 instances; examples: GPQA, ARC-Challenge, or StrategyQA).
- **Replication unit**: Each task instance is a complete replication of the design; running all instances provides confidence intervals and power to detect scaffold effects.

### 2.3 Conditions Held Constant

- **Task text and format**: Identical for all 15 cells and all task instances.
- **Evaluation metric**: Single-valued performance score per task (e.g., accuracy, F1, or benchmark-defined reward) applied identically to all cells.
- **Time budget**: Same maximum runtime or token limit per task across all cells (if applicable).
- **Randomness**: Fixed random seed (if applicable) to allow replication; or report variance across seed values.
- **Input/output format**: Identical parsing rules for all cells to extract answers and compute scores.

---

## 3. Ablations

### 3.1 Primary Ablation: Scaffold Effect Within Each Model

**Rationale**: Isolate scaffold variance by holding model constant.

**Design**: For each of the 5 models, compare performance across the 3 scaffolds.
- **Condition A**: Model M with Scaffold 1, Scaffold 2, Scaffold 3 → three score distributions.
- **Statistical test**: One-way ANOVA within each model, or paired tests if using the same task set across scaffolds.
- **Expected outcome**: If scaffolds matter, at least one model will show p < 0.05 in the ablation; if no model shows a significant scaffold effect, the main research question's premise is weakened.

### 3.2 Secondary Ablation: Model Effect Within Each Scaffold

**Rationale**: Isolate model variance by holding scaffold constant.

**Design**: For each of the 3 scaffolds, compare performance across the 5 models.
- **Condition B**: Scaffold S with Model 1, Model 2, Model 3, Model 4, Model 5 → five score distributions.
- **Statistical test**: One-way ANOVA within each scaffold.
- **Expected outcome**: If models vary in capability (well-established), all 3 scaffolds will show significant model effects (p < 0.05). If some scaffolds show no model differentiation, scaffold choice may mask or amplify model differences.

### 3.3 Tertiary Ablation: Direct Comparison of Best- and Worst-Performing Cells

**Rationale**: Verify that the highest-scoring (scaffold, model) pair outperforms the lowest-scoring pair, and estimate the practical magnitude of scaffold effects.

**Design**: Identify the max and min cells after full data collection.
- Compare via t-test or bootstrap confidence interval on the difference in mean scores.
- Report Cohen's d or similar effect size to quantify practical significance.

---

## 4. Analysis Plan

### 4.1 Primary Analysis: Two-Way ANOVA

**Model**: 
```
Score ~ Scaffold + Model + Scaffold:Model + ε
```

**Outcomes**:
- **Main effect of Scaffold** (F-statistic, p-value, partial η² effect size).
- **Main effect of Model** (F-statistic, p-value, partial η²).
- **Interaction term Scaffold:Model** (F-statistic, p-value, partial η²).

**Assumptions to check**:
- Normality of residuals (Shapiro-Wilk test on residuals).
- Homogeneity of variance across cells (Levene's test).
- Independence of observations (by design, since each task is independent).

**Interpretation**:
- If Scaffold main effect p < 0.05: Scaffold choice significantly influences capability scores.
- If Scaffold:Model interaction p < 0.05: Some scaffolds are more beneficial for certain models; scaffold utility is model-dependent.
- Estimate effect size (partial η² ≥ 0.01 is small, ≥ 0.06 is medium, ≥ 0.14 is large).

### 4.2 Secondary Analysis: Mean Performance by Cell

**Procedure**:
- For each of the 15 (Scaffold, Model) cells, compute:
  - Mean score across all task instances.
  - Standard error (SE) and 95% confidence interval (CI).
  - Minimum and maximum score (to identify outlier tasks).

**Visualization**:
- Heatmap of mean scores with SE as cell annotations.
- Line plot showing score trajectories across models within each scaffold.
- Box plots or violin plots showing score distributions by cell.

### 4.3 Tertiary Analysis: Power and Minimum Detectable Effect Size

**Procedure**:
- Post-hoc power calculation based on observed effect sizes.
- Report: "With N task instances and the observed variance, the design has power 1 - β to detect a Scaffold main effect of magnitude d = [effect size]."
- Identify cells with low replication (if any tasks fail) and note any loss of power.

### 4.4 Sensitivity Analysis

**Procedure**:
- Repeat all analyses excluding the single highest-scoring and single lowest-scoring task instances (if extreme outliers exist).
- Re-report effect sizes and p-values to verify robustness.
- If removing outliers materially changes conclusions, report both.

---

## 5. Concrete Resources

### 5.1 Benchmark

**Resource**: Public multi-step task benchmark
- **Examples**: 
  - GPQA (https://huggingface.co/datasets/Idavidrein/gpqa) — 198 graduate-level STEM questions; ~3000 words per question; public evaluation harness available.
  - ARC-Challenge (https://allenai.org/arc/) — 1,172 challenging science exam questions; publicly released dataset and leaderboard.
  - StrategyQA (https://allenai.org/strategyqa/) — 2,290 yes/no questions requiring multi-step reasoning; publicly released with solver code.
- **Choice justification**: Select one of the above based on availability and multi-step reasoning requirements. GPQA is preferred for this design (few publicly-available models score well, ensuring variance across the 5 models; requires multi-step reasoning, enabling scaffold differentiation).
- **Task instance count**: Use all available instances; expect ≥100 instances for stable effect estimation.

### 5.2 Scaffolds

**Resource 1: Chain-of-Thought (CoT)**
- **Implementation**: Append "Let's think step by step." to each prompt.
- **Reference**: Wei et al., 2022, "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (arXiv:2201.11903).
- **Operationalization**: Extract reasoning text and final answer from model output using a regex pattern for "[ANSWER: ...]" or similar delimiter.

**Resource 2: Tree-of-Thought (ToT)**
- **Implementation**: Use a tree search with up to 3 levels and 3 branches per node; evaluate each node with a binary classifier ("is this intermediate state on a path to the answer?").
- **Reference**: Yao et al., 2024, "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (arXiv:2305.10601).
- **Operationalization**: Implement via a loop of LLM calls generating candidate next steps, a separate evaluation call, and pruning logic. Expected total cost: ~3–5× the cost of CoT per task.

**Resource 3: Zero-Shot (Baseline)**
- **Implementation**: Prompt with the task question alone, no reasoning instruction.
- **Rationale**: Provides a lower-variance baseline for statistical comparison; standard practice in capability measurement.
- **Operationalization**: Single LLM call per task.

### 5.3 Models

**Resource 1**: OpenAI GPT-4 (or GPT-4o)
- **Access**: OpenAI API (https://platform.openai.com/) with valid API key.
- **Model ID**: "gpt-4" or "gpt-4-turbo".
- **Cost**: ~$0.03 per 1K input tokens + $0.06 per 1K output tokens (as of early 2024).

**Resource 2**: Anthropic Claude 3 Opus
- **Access**: Anthropic API (https://www.anthropic.com/api).
- **Model ID**: "claude-3-opus-20240229".
- **Cost**: ~$0.015 per 1K input tokens + $0.075 per 1K output tokens.

**Resource 3**: Meta Llama 2 70B (or Llama 3 70B)
- **Access**: HuggingFace Hub (https://huggingface.co/meta-llama/) with HF token; or modal (https://modal.com/) for serverless hosting.
- **Model ID**: "meta-llama/Llama-2-70b-chat-hf" or "meta-llama/Meta-Llama-3-70B-Instruct".
- **Cost**: Free (local compute or free tier HF) or ~$0.001 per 1K tokens (modal).

**Resource 4**: Google Gemini 2.0 (or Gemini 1.5 Pro)
- **Access**: Google AI Studio / Vertex AI (https://ai.google.dev/).
- **Model ID**: "gemini-2.0-pro-exp" or "gemini-1.5-pro".
- **Cost**: ~$0.01–0.025 per 1K tokens (pricing varies by tier).

**Resource 5**: Grok 3 (or Grok 2)
- **Access**: xAI API or x.ai (https://x.ai) once released.
- **Model ID**: "grok-3" or "grok-2" (TBD upon release).
- **Cost**: Pricing not yet public; assume $0.01–0.05 per 1K tokens for planning.

### 5.4 Compute and Software Infrastructure

**Hardware**:
- Any system with internet access and ~50 GB free disk (for logging output; tree-of-thought may generate many intermediate traces).

**Software Stack**:
- **Language**: Python 3.10+.
- **Benchmark loading**: `huggingface_hub` or direct download from benchmark websites.
- **API clients**: 
  - `openai` (pip install openai)
  - `anthropic` (pip install anthropic)
  - `transformers` (pip install transformers torch) for Llama access.
  - `google-generativeai` (pip install google-generativeai) for Gemini.
  - Custom HTTP client or xAI SDK for Grok.
- **Orchestration**: 
  - `asyncio` or `concurrent.futures` for parallel API calls.
  - `json` for logging all prompts, outputs, and scores.
- **Statistical analysis**: 
  - `scipy.stats` for ANOVA, t-tests, effect sizes.
  - `pandas` for aggregation and summaries.
  - `matplotlib` or `seaborn` for visualization.
- **Evaluation**:
  - Custom parsing logic to extract answers from free-form text.
  - Benchmark-provided evaluation scripts (e.g., exact-match or token-overlap for answers).

### 5.5 Expected Cost Estimate

**Assumptions**:
- 100 task instances in benchmark.
- Average task: 1000 input tokens + 500 output tokens.
- Scaffold cost multiplier: CoT = 1.5×, ToT = 4×, Zero-shot = 1×.

**Cost per model for all 3 scaffolds and 100 tasks**:
- GPT-4: ~$30 (most expensive).
- Claude 3 Opus: ~$20.
- Llama 70B (modal): ~$1.
- Gemini 1.5: ~$10.
- Grok: ~$10 (TBD).
- **Total**: ~$70–100 (assuming commercial APIs dominate).

---

## 6. Outcome Metrics

### 6.1 Primary Outcome: Task Performance Score

**Metric**: Accuracy or benchmark-defined score (e.g., GPQA uses exact-match correctness; ARC uses multiple-choice accuracy).

**Unit**: Binary (1 = correct, 0 = incorrect) or continuous [0, 1] depending on benchmark.

**Aggregation**: 
- Per-cell mean score = sum of correct answers in cell / total task instances in cell.
- Per-cell standard error = sqrt(variance / N).

### 6.2 Secondary Outcomes

**Outcome 2a: Main Effect Size (Scaffold)**
- Partial η² for scaffold factor in two-way ANOVA.
- Interpretation: Proportion of total variance explained by scaffold (independent of model).
- Threshold for "practical significance": η² ≥ 0.01 (small effect, worth noting).

**Outcome 2b: Main Effect Size (Model)**
- Partial η² for model factor.
- Expected: large (models are known to differ significantly).

**Outcome 2c: Interaction Effect Size**
- Partial η² for Scaffold:Model interaction.
- Interpretation: Whether scaffold benefit depends on model choice.
- Threshold: η² ≥ 0.01 indicates model-dependent scaffolds.

### 6.3 Tertiary Outcomes

**Outcome 3a: Confidence Intervals**
- 95% CI on each cell mean, reported as [lower, upper] bounds.
- Used to assess overlap and identify non-overlapping pairs.

**Outcome 3b: Ranking Stability**
- Rank each cell by mean score; identify whether top and bottom cells remain the same across ablation subsets (e.g., excluding outlier tasks).

---

## 7. Uncertainty Quantification

### 7.1 Standard Errors and Confidence Intervals

**Method**:
- For each cell (Scaffold S, Model M), compute mean score μ and standard error SE = σ / sqrt(n), where σ is the sample standard deviation and n is the number of task instances.
- Report 95% CI as [μ - 1.96·SE, μ + 1.96·SE] assuming normal approximation (valid if n ≥ 30; use t-distribution if n < 30).

### 7.2 Effect Sizes

**Method**:
- Report partial η² for each main effect and interaction in ANOVA.
- Compute 95% confidence interval for each effect size using bootstrap resampling (1000 resamples of task instances within each cell).

### 7.3 p-Values and Hypothesis Tests

**Method**:
- Two-way ANOVA: Report p-values for main effects and interaction. Use Bonferroni correction if multiple planned comparisons (e.g., p' = p / 3).
- Pairwise comparisons (ablation analyses): Report Tukey-adjusted p-values to control family-wise error rate.

### 7.4 Bootstrap Confidence Intervals for Non-Parametric Estimates

**Method**:
- Resample task instances with replacement within each cell (1000 bootstrap samples).
- For each resample, recompute the 15-cell means and the difference between max and min cells.
- Report 95% CI of the difference as the 2.5th and 97.5th percentiles of the bootstrap distribution.

### 7.5 Sensitivity to Assumptions

**Method**:
- If ANOVA assumptions (normality, homogeneity of variance) are violated:
  - Report non-parametric alternative: Kruskal-Wallis test (ordinal rank-based).
  - Verify that conclusions remain unchanged.
- If any cell has < 10 task instances due to failures:
  - Report "power-adjusted" conclusions and note that effect sizes may be underestimated.

---

## 8. Concrete Workflow and Timeline

### Phase 1: Setup and Validation (Days 1–3)
- Implement all 3 scaffolds and validate instantiation with 1 test task per model.
- Verify API authentication and rate limits.
- Download and parse the benchmark task instances.
- **Deliverable**: Scaffold code, model client wrapper, task parser.

### Phase 2: Data Collection (Days 4–14)
- Run all 15 (Scaffold, Model) cells across all task instances (batched, parallel where possible).
- Log all prompts, model outputs, parsed answers, and computed scores to a JSON file per cell.
- Monitor for failures; retry failed tasks once, then document failures.
- **Deliverable**: 15 result files (one per cell) with complete trace.

### Phase 3: Analysis (Days 15–17)
- Load all result files and construct a single DataFrame (columns: Scaffold, Model, TaskID, Score).
- Run two-way ANOVA; check assumptions (Shapiro-Wilk, Levene's test).
- Compute cell means, SEs, and 95% CIs.
- Perform ablation analyses (one-way ANOVAs within each model and scaffold).
- Generate visualization heatmap and summary tables.
- Run bootstrap resampling for non-parametric CIs on effect sizes.
- **Deliverable**: Statistical tables, figures, and interpretation document.

---

## 9. Success Criteria and Falsification

**Affirmative criterion**: 
- Scaffold main effect is statistically significant (p < 0.05) and effect size is ≥ small (partial η² ≥ 0.01).
- Conclusion: Scaffold choice materially affects published capability scores, independent of model selection.

**Falsification criterion** (from state.md):
- Scaffold main effect is not significant (p ≥ 0.05) AND Scaffold:Model interaction is not significant (p ≥ 0.05).
- Conclusion: Scaffold choice has negligible impact; capability scores are almost entirely model-driven. The premise of the research would be contradicted.

**Neutral outcome**:
- Significant Scaffold:Model interaction but weak main effect of Scaffold.
- Conclusion: Scaffold utility is highly model-dependent; no universal scaffold recommendation is possible.

---

## 10. References to Sampling Frame

The **sampling frame**, as recorded in state.md, is operationalized as follows:

1. **Population**: All (Scaffold, Model) pairings from {3 scaffolds} × {5 models}.
2. **Sampling unit**: A single (Scaffold, Model, Task) trial (15 cells × N task instances total observations).
3. **Replication**: Each task instance is a complete replication of the factorial design, providing N independent observations per cell.
4. **Constant conditions**: Identical task text, evaluation metric, and time budget across all cells, ensuring that any observed score differences are attributable to the (Scaffold, Model) treatment, not confounds.

This design ensures that the sampling frame's full coverage (all 15 cells, all task instances, constant conditions) is materialized in the execution plan, enabling the two-way ANOVA and ablation analyses to address the primary research question with adequate power and precision.

---

## 11. Limitations and Open Questions

1. **Cannot verify concrete identities**: The specific benchmark, scaffolds, and models are assumed to exist; their exact definitions await selection.
2. **Scaffold orthogonality**: The design assumes the 3 scaffolds are sufficiently distinct (not redundant). This should be validated by inspection before data collection.
3. **Model heterogeneity in API reliability**: If some models have higher failure rates or latency outliers, cells may have unequal N, reducing power. Mitigation: retry failures and document.
4. **Generalization**: Results apply only to the chosen benchmark; scaffold effects may differ for other task types (e.g., code generation vs. reasoning).
5. **Publication bias**: This design measures published scores; it does not isolate whether published benchmarks themselves are biased toward particular models or scaffolds.

---

## Conclusion

This experimental design uses a 3 × 5 factorial structure to isolate and quantify the main effects of scaffold and model on agent capability scores, with ablations to confirm the statistical significance of these effects within each level of the other factor. The sampling frame covers all 15 (Scaffold, Model) pairings with full replication across task instances, enabling two-way ANOVA with appropriate uncertainty quantification (CIs, effect sizes, bootstrap resampling) and a clear falsification criterion to evaluate whether scaffold choice meaningfully contributes to published capability scores.
