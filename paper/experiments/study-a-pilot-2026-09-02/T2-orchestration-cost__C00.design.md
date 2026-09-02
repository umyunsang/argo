# Experimental Design: Multi-Call Orchestrations vs. Single-Call Accuracy-to-Cost Justification

## Research Question

Do multi-call orchestrations improve accuracy enough to justify the additional inference they consume?

---

## 1. Main Comparison and Conditions

### Primary Contrast
**Treatment Factor**: Execution strategy (within-subjects, per task)

#### Condition 1: Single-Call Baseline (Baseline)
- One-shot prompt sent to the model with full context and task specification.
- Prompt: Standard task instruction + context, optimized once per task type.
- Output: Direct model response, one turn.
- Cost: Single forward pass.

#### Condition 2: Multi-Call Orchestration (Treatment)
- Task execution via the orch-* pipeline pattern (research-plan-TDD-review):
  1. **Research phase**: Agent searches for prior work, examples, and related patterns.
  2. **Plan phase**: Agent produces a detailed plan before implementation.
  3. **TDD phase**: Agent writes tests, then implementation to pass them.
  4. **Review phase**: Independent review of implementation.
  5. **Commit gate**: Final human or automated validation.
- Prompt: Same baseline task instruction (no differentiation in prompt optimization effort per constraint).
- Output: Final artifact after 4–5 model calls + tool invocations.
- Cost: Multiple forward passes + tool overhead.

---

## 2. Ablations

### Ablation 1: Model Backbone Effect
**Factor**: Model choice (between-subjects, randomized per task batch)

- **Claude 3.5 Sonnet** (primary baseline—fast, capable on coding and planning)
- **Claude 3 Opus** (slower, higher reasoning capability; tests whether orchestration helps more with weaker baselines)

**Rationale**: Different models may benefit differently from orchestration structure. Opus may have higher single-call accuracy (reducing orchestration's margin), or Sonnet may benefit more from structured planning.

### Ablation 2: Task Difficulty Effect
**Factor**: Item-level difficulty from benchmark (within-subjects; tasks stratified)

- **Easy items** (bottom quartile of difficulty estimate): Single-call may already saturate; orchestration overhead may not be justified.
- **Medium items** (middle quartiles): Expected sweet spot for orchestration benefit.
- **Hard items** (top quartile of difficulty estimate): Orchestration's structured reasoning may provide largest gains.

**Rationale**: Justification for cost depends on where accuracy gains appear. If gains concentrate in hard items only, justification is weaker (limited scope). If uniform or concentrated in medium, stronger.

### Ablation 3: Orchestration Depth
**Factor**: Number of loops in the multi-call strategy (within-subjects, ordered)

- **Shallow orchestration**: Plan + Direct implementation (2 calls, no TDD loop).
- **Full orchestration**: Research + Plan + TDD loop (4–5 calls with possible iterations).

**Rationale**: Helps isolate whether the benefit comes from *structured thought* (plan phase) or *iterative refinement* (TDD + review loops). If shallow wins, the justification changes.

---

## 3. Concrete Resources

### Benchmarks
- **LeetCode / coding contest dataset** (e.g., a curated subset with difficulty tags; must include item-level difficulty estimates)
  - Why: Concrete, difficulty labeled, measurable outputs (pass test suite), consistent evaluation.
  - Concrete source: Can use datasets from LLM evaluation papers (e.g., LiveCodeBench, HumanEval-style benchmarks) or contest archives.
  
- **Alternative: Open-source evaluation suite** (e.g., SWE-bench, APPS, or ECC's own test suite if available)
  - Why: Ensures task consistency and automated grading.

### Models
- **Claude 3.5 Sonnet** (via Anthropic API)
- **Claude 3 Opus** (via Anthropic API)

### Orchestration Tools & Patterns
- **orch-* skill family** (from ECC): orch-add-feature, orch-fix-defect, orch-change-feature
  - These are production-ready implementations of research-plan-TDD-review pipelines.
  - Concrete reference: `/Users/um-yunsang/.agents/skills/orch-fix-defect/SKILL.md` (or equivalent in local skill directory)

- **Research capabilities**: exa-research, parallel-research, research-router (for "research" phase)
- **Code generation & testing**: standard Claude code generation in the plan/TDD phases.

### Baseline Prompts
- **Single-call prompt template**: Task instruction + examples + constraints, optimized once for clarity (e.g., 200–400 tokens).
- **Multi-call prompts**: Reuse the same base instruction; orchestration structure is added by the pipeline, not prompt complexity.

---

## 4. Outcome Metrics

### Primary Metrics

#### 4.1 Accuracy
- **Definition**: Fraction of tasks on which the final output is correct (as measured by automated test suite or human judgment).
- **Calculation**: 
  ```
  Accuracy = (# correct outputs) / (# total tasks)
  ```
- **Resolution**: Pass/fail per task (binary outcome).

#### 4.2 Token Cost
- **Definition**: Total tokens consumed (input + output) across all calls for a single task.
- **Single-call cost**: Tokens for one query + one response.
- **Multi-call cost**: Sum of tokens across all model calls in the orchestration pipeline (including research, planning, TDD, review).
- **Tool cost**: Count separately (tool invocations do not always cost tokens, but track them for context).

#### 4.3 Accuracy-to-Cost Ratio (Justification Metric)
- **Definition**: The efficiency of accuracy gain per unit cost.
  ```
  Efficiency = (Accuracy_multi - Accuracy_baseline) / (Cost_multi - Cost_baseline)
  ```
  - If negative numerator: orchestration is not justified (lower accuracy + higher cost).
  - If positive but low: marginal improvement, justification weak.
  - If positive and substantial: strong justification.

### Secondary Metrics

#### 4.4 Latency
- **Definition**: Wall-clock time from task submission to final output (useful for practical deployment, though not the primary measure of token efficiency).

#### 4.5 Failure Modes
- **Definition**: Categorization of failure cases (e.g., timeout, error in middle of orchestration, incorrect plan, failed test suite).
- **Rationale**: Understand whether orchestration introduces new failure modes (e.g., tool errors in research phase) or reduces them.

---

## 5. Analysis Plan

### 5.1 Descriptive Analysis
1. **Condition-level summaries** (mean ± SD for accuracy, cost):
   - Single-call baseline: Accuracy, Cost, Ratio.
   - Multi-call orchestration: Accuracy, Cost, Ratio.
   
2. **Stratified by difficulty**:
   - For each difficulty quartile, report accuracy and cost separately.
   - Visualize: Accuracy gains (y-axis) vs. task difficulty (x-axis) to assess where justification is strongest.

3. **Stratified by model**:
   - Claude Sonnet: Baseline vs. orchestration.
   - Claude Opus: Baseline vs. orchestration.
   - Compare interaction: does orchestration benefit one model more than the other?

### 5.2 Inference: Hypothesis Tests
1. **Primary hypothesis test**: Does orchestration significantly improve accuracy?
   - **Null**: Accuracy_multi ≤ Accuracy_baseline.
   - **Test**: Within-subjects paired t-test (or binomial test for binary accuracy) across all tasks.
   - **Alternative**: One-sided t-test (H1: Accuracy_multi > Accuracy_baseline).
   - **Significance level**: α = 0.05.

2. **Cost justification test**: Does the accuracy gain outweigh cost?
   - **Metric**: Accuracy-to-cost ratio (Efficiency).
   - **Null**: Efficiency ≤ 0 (no net gain per token).
   - **Test**: Compute Efficiency as above; report 95% CI. If CI excludes 0 on the positive side, cost is justified.

3. **Difficulty interaction**: Does orchestration benefit differ across difficulty tiers?
   - **Test**: ANOVA or mixed-effects model with Difficulty × Method as factors.
   - **Interpretation**: If interaction is significant, orchestration justification is conditional on task difficulty.

### 5.3 Secondary Analyses
1. **Model interaction**: Does Claude Opus vs. Sonnet respond differently to orchestration?
   - **Test**: Three-way ANOVA: Model × Method × Difficulty.
   - **Interpretation**: If Method × Model interaction is significant, one model benefits more; this affects deployment strategy.

2. **Ablation on orchestration depth**:
   - **Comparison**: Shallow (Plan + Direct) vs. Full (Research + Plan + TDD + Review).
   - **Analysis**: Which phase contributes most to accuracy gain? Plot accuracy gain vs. number of calls.

3. **Failure mode distribution**:
   - **Categorize** each failure (timeout, tool error, logic error, etc.).
   - **Test**: Chi-square test for independence of failure type and method.
   - **Interpretation**: Does orchestration introduce fragility?

### 5.4 Visualization
- **Main plot**: Accuracy (y-axis) vs. Token Cost (x-axis), with points colored by method and sized by difficulty.
- **Difficulty stratification plot**: Accuracy gain (y-axis) vs. Difficulty quartile (x-axis), separate facets for each model.
- **Cost breakdown**: Stacked bar chart showing token cost allocation across research, plan, TDD, review phases for multi-call.
- **Failure mode heatmap**: Methods × Failure types, shaded by count.

---

## 6. Design Details: Sample, Conditions, and Replication

### 6.1 Sample
- **Task universe**: Benchmark subset (e.g., 100–200 tasks from LeetCode or HumanEval).
- **Stratification**: Ensure balanced representation of difficulty levels (target: 25–30 tasks per quartile).
- **Sample size justification**: 
  - With 100–200 tasks and within-subjects design, detectable effect size (Cohen's d ≈ 0.3–0.4) is achievable at α=0.05, 1−β≥0.80.
  - (Do not compute exact N: this is a design specification only.)

### 6.2 Randomization and Blocking
- **Within-subjects**: Each task is solved by both single-call and multi-call methods.
- **Order counterbalancing**: Randomize which method is applied first per task to avoid learning/ordering effects.
- **Model assignment**: Randomly assign half of tasks to Claude Sonnet, half to Opus (ensures model effects are orthogonal to method effects).

### 6.3 Replication and Reproducibility
- **Fixed prompts**: Commit baseline prompts to version control (PROMPT.md).
- **Fixed random seeds**: Set seeds for any stochastic elements (e.g., model sampling temperature = 0 for determinism; if sampling, document the temperature).
- **Task IDs**: Log task ID, difficulty estimate, model, method, and outcome for every trial.
- **Artifact storage**: Save model responses (JSON or markdown) for post-hoc analysis and debugging.

---

## 7. Uncertainty Quantification

### 7.1 Confidence Intervals
- **Accuracy**: Wilson score interval (handles small counts and extreme proportions better than normal approximation).
  - Report 95% CI for each condition, stratified by difficulty and model.
  
- **Cost**: Bootstrap CI (since token cost distributions may be non-normal).
  - Resample tasks 10,000 times with replacement; compute cost percentiles.

- **Efficiency ratio**: Propagate uncertainty from accuracy and cost using the delta method or bootstrap.
  - (Do not compute point estimate: design only.)

### 7.2 Sensitivity Analysis
1. **Threshold sensitivity**: How does justification change if we vary the "acceptable cost increase"?
   - E.g., if we tolerate only 10% cost increase, is orchestration still justified by accuracy gains?
   - Report Efficiency ratio across a range of cost budgets.

2. **Difficulty re-estimation**: If difficulty labels are noisy, how robust is the difficulty interaction?
   - Strategy: Reorder tasks by hand (or by alternative difficulty metric) and recompute.

3. **Orchestration failure recovery**: What if 5% of orchestration runs fail mid-pipeline?
   - Compute cost and accuracy under a pessimistic scenario where failed runs default to single-call fallback.

### 7.3 Effect Size Reporting
- **Primary**: Cohen's d for accuracy difference (Method: multi-call vs. baseline).
- **Secondary**: Partial η² for interactions (Difficulty × Method).
- **Interpretation**: Report both point estimate and 95% CI (via bootstrap if necessary).

---

## 8. Resource and Cost Estimate (Qualitative)

### Computational
- **Model calls**: 100–200 tasks × 2 methods × 2 models ≈ 400–800 full task executions.
- **Tokens per single-call**: ~500–2000 tokens (task + response).
- **Tokens per multi-call**: ~3000–10,000 tokens (research + plan + TDD + review).
- **Estimated total**: 200k–2M tokens (depends on benchmark complexity and model efficiency).

### Human Effort
- **Prompt engineering**: Minimal (reuse same base prompt per constraint; orchestration is structured, not prompt-engineered).
- **Manual difficulty estimates** (if benchmark lacks them): ~2–4 hours for 100–200 tasks.
- **Analysis & writeup**: ~10–20 hours.

### Timeline (Indicative)
- Setup & data preparation: 1–2 days.
- Execution (running 400–800 tasks): 2–5 days (parallelizable).
- Analysis & reporting: 3–5 days.
- **Total**: ~1–2 weeks (wall-clock, with parallelization).

---

## 9. Interpretation Framework & Decision Rule

### Success Criteria
An orchestration strategy is **justified** if:
1. **Accuracy improvement** is statistically significant (t-test, α=0.05) **and**
2. **Efficiency (accuracy gain per extra token)** is positive and practically meaningful (e.g., ≥ 0.01 percentage-point accuracy per 100 tokens).

### Conditional Justification
- If accuracy improvement exists **only for hard items** (top quartile): Justification is conditional on deployment to hard-problem workloads.
- If orchestration is more beneficial for **Opus than Sonnet**: Deployment strategy is model-dependent.
- If **ablation shows plan phase alone** drives the gain (not TDD loops), justification is stronger (cheaper orchestration variant exists).

### Non-Justification Cases
- If accuracy gain is negligible (< 1 percentage point) or non-significant: Cost increase is not justified.
- If failure rate in orchestration is substantially higher (e.g., > 10% vs. < 2%): Reliability cost offsets efficiency gain.

---

## 10. Reporting Requirements

Final report will include:
1. **Descriptive tables**: Accuracy, cost, and efficiency metrics by condition, difficulty, and model.
2. **Inferential statistics**: Hypothesis test results (t-tests, ANOVA) with p-values and effect sizes.
3. **Visualizations**: Plots as described in Section 5.4.
4. **Failure mode analysis**: Distribution and breakdown of failure types.
5. **Ablation results**: Shallow vs. full orchestration comparison.
6. **Sensitivity analyses**: Thresholds, difficulty re-estimation, failure recovery scenarios.
7. **Conclusion**: Whether multi-call orchestrations are justified; under what conditions; for which models/difficulty levels.
8. **Code & reproducibility**: Link to versioned prompts, task list, and analysis scripts (in separate artifact repository).

---

## End of Design
