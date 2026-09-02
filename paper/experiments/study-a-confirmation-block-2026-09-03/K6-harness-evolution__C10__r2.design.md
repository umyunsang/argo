# Experimental Design: K6-Harness-Evolution Generalization Test

## Research Objective

Determine whether agent-driven scaffold rewriting produces generalizable improvements in task performance, or whether gains reflect overfitting to the particular task family used during rewriting.

---

## 1. Main Comparison: Baseline Scaffold vs. Rewritten Scaffold

### Condition A: Baseline Scaffold
- The original, unmodified executable scaffold provided at the start of the experiment.
- Model: fixed, no weights changed.
- Inference settings: fixed (temperature, top-p, max tokens, etc.).
- Agent: does not rewrite the scaffold under this condition; runs fixed iterations on tasks.

### Condition B: Iteratively Rewritten Scaffold
- The agent is permitted to rewrite the executable scaffold between task attempts.
- The rewritten scaffold is saved and persists across iterations.
- Model and inference settings remain identical to Condition A.
- Agent runs the same number of iterations on the same task family as Condition A.

### Evaluation on Held-Out Test Set
Both scaffolds are evaluated on a held-out test set *not* used during the rewriting process. The test set is stratified into two layers (see Sampling Frame, below).

---

## 2. Sampling Frame

**Population:** The space of tasks that the agent + model can meaningfully attempt, defined by a structured task family (e.g., code generation, planning, reasoning, or document-based QA).

**Unit of observation:** A single (task, scaffold_variant) pair, with fixed random seed and model temperature.

**Stratified sampling into three pools:**

1. **Training/Rewriting Pool (Primary Family)**
   - ~50–60 tasks from the primary family used during Condition B rewriting.
   - Agent is allowed to iterate, observe output, and modify the scaffold.
   - These tasks inform the scaffold rewrites and are *not* used for statistical comparison.

2. **Held-Out Test Pool A (Primary Family, Held-Out Tasks)**
   - ~30 structurally similar tasks from the same family as the Training Pool.
   - Never shown to the agent during rewriting; reserved for final evaluation.
   - Used to measure whether improvements transfer within the family.

3. **Held-Out Test Pool B (Adjacent-Domain Family)**
   - ~15 tasks from a structurally related but distinct domain (e.g., if Primary is code-to-AST parsing, Adjacent is code-to-type-annotation).
   - Never used during rewriting; reserved for testing out-of-distribution generalization.
   - Used to measure whether scaffold improvements are robust to domain shift.

**Randomization:**
- Task order within each pool is randomized per scaffold variant to prevent ordering bias.
- Model random seed is fixed per task to ensure reproducibility.

---

## 3. Main Analysis: Generalization Test

### 3.1 Primary Comparison (Test Pool A: Held-Out Primary Family)

**Null Hypothesis (H₀):** The rewritten scaffold produces no improvement on held-out primary-family tasks compared to the baseline scaffold.

**Alternative Hypothesis (H₁):** The rewritten scaffold improves performance on held-out primary-family tasks.

**Test Statistic:** For each task, record a success indicator (1 = correct completion, 0 = failure) or a continuous metric (e.g., solution quality score 0–100). Compute:
- Mean performance under Baseline Scaffold: P_baseline
- Mean performance under Rewritten Scaffold: P_rewritten
- Difference: Δ = P_rewritten − P_baseline

**Statistical Test:**
- **If metric is binary (success/failure):** Paired binomial test (McNemar's test) or Fisher's exact test if sample size is small; report 95% confidence interval (Agresti–Coull).
- **If metric is continuous:** Paired t-test with equal variance assumption; report 95% confidence interval and effect size (Cohen's d).
- **Significance threshold:** p < 0.05 (two-tailed).

**Decision Rule:**
- If Δ is statistically significant and positive (p < 0.05), the improvement is real on held-out primary-family tasks.
- If Δ is not significant or negative, the design's premise is falsified; rewritten scaffold does not generalize within the family.

### 3.2 Transfer Test (Test Pool B: Adjacent-Domain Family)

**Purpose:** Assess whether the scaffold improvements are robust to domain shift or primarily tuned to the primary family's structure.

**Null Hypothesis (H₀ Transfer):** The rewritten scaffold produces no improvement on adjacent-domain tasks; improvements in Pool A do not transfer.

**Alternative Hypothesis (H₁ Transfer):** The rewritten scaffold improves adjacent-domain performance.

**Test Statistic:** Δ_adjacent = P_rewritten,adjacent − P_baseline,adjacent

**Statistical Test:** Same as 3.1, using the 15 adjacent-domain tasks.

**Generalization Criterion:**
- Compute the ratio: Transfer Ratio = Δ_adjacent / Δ_primary
- **If Transfer Ratio ≥ 0.50:** Scaffold improvements show robust transfer; design premise is supported.
- **If Transfer Ratio < 0.50:** Improvements are partially domain-specific; interpret as weak support (scaffold changes help structure the primary domain but are not universally robust).
- **If Δ_adjacent is negative or null:** Improvements do not transfer; design premise is falsified.

---

## 4. Ablation Study: Disentangling Scaffold Components

To isolate which scaffold rewrites drive performance gains, implement a **component ablation**:

### Ablation Variants

**Condition B1: Rewritten Scaffold – Logic Component Only**
- Agent is permitted to rewrite only the core task-solving logic (e.g., reasoning steps, search strategy).
- Output formatting and error-handling scaffolds remain from the baseline.

**Condition B2: Rewritten Scaffold – Formatting Component Only**
- Agent is permitted to rewrite only the output formatting and structure (e.g., prompt templates, response parsing).
- Core logic remains from the baseline.

**Condition B3: Rewritten Scaffold – Full (as in main comparison)**
- Agent rewrites both logic and formatting (control for comparison).

### Ablation Analysis

For each ablation variant, evaluate on the same held-out Test Pool A (30 primary-family tasks):
- Δ_B1 = P_logic_only − P_baseline
- Δ_B2 = P_formatting_only − P_baseline
- Δ_B3 = P_full − P_baseline

**Interpretation:**
- If Δ_B1 >> Δ_B2: Core logic changes are the primary driver.
- If Δ_B2 >> Δ_B1: Formatting/prompt improvements are dominant.
- If Δ_B3 ≈ Δ_B1 + Δ_B2: Components have additive effects.
- If Δ_B3 > max(Δ_B1, Δ_B2): Components interact synergistically.

**Statistical Testing:** Apply the same paired statistical test (binomial or t-test) to each ablation variant; report 95% CIs to visualize effect magnitudes.

---

## 5. Outcome Metrics

### Primary Metric
- **Task Success Rate (%):** Percentage of held-out tasks for which the agent produces a correct or acceptable solution, judged by a deterministic verifier or human evaluation rubric.
- Computed separately for Baseline and Rewritten scaffolds.
- Difference Δ reported with 95% CI and p-value.

### Secondary Metrics (to understand mechanism)
1. **Solution Quality Score (0–100):** If a task admits partial credit, score solution quality on a predefined scale.
2. **Reasoning Step Count:** Number of logical steps the agent takes before arriving at an answer. (Proxy for scaffold efficiency.)
3. **Semantic Validity:** For code or structured output, fraction of solutions that parse and execute without errors. (Proxy for formatting scaffold quality.)
4. **Inference Token Count:** Total tokens used per task. (Proxy for scaffold conciseness.)

### Robustness Checks
- **Early Stopping Metrics:** Evaluate performance on the first 10, 20, and 30 held-out tasks separately to check for bias in task ordering or sampling.
- **Effect Size:** Report Cohen's d (for continuous metrics) or odds ratio (for binary metrics) to distinguish statistical significance from practical magnitude.

---

## 6. Concrete Resources and Procedures

### Task Sources
- **Primary Family (60 train + 30 test):** [Specify concrete dataset, e.g., "LeetCode Easy problems (categories: arrays, strings, trees); task IDs: [range]"]
- **Adjacent Domain (15 test):** [Specify, e.g., "SQL query writing tasks from existing benchmarks; source: [dataset name]; task IDs: [range]"]
- All tasks must have deterministic, verifiable correct answers.

### Computational Setup
- **Model:** Fixed, named variant (e.g., "Claude 3.5 Sonnet, June 2024 release").
- **Inference settings:** temperature=0.7, top_p=1.0, max_tokens=2048 (or equivalent; must be fixed across all conditions).
- **Runs:** Each (task, scaffold_variant) pair is evaluated **once** per ablation condition (Condition A, B1, B2, B3), with fixed random seed per task.
- **Runtime per task:** Estimate [X] seconds per task on average. Total budget: ~500–1000 task evaluations across all conditions and ablations.

### Scaffold Management
- **Baseline Scaffold:** Store version A at commit/tag for reproducibility (e.g., `baseline_scaffold_v1.0`).
- **Rewritten Scaffold:** Store the final rewritten version at commit/tag after the rewriting phase is complete (e.g., `rewritten_scaffold_v1.0`).
- **Ablation Variants:** Store logic-only and formatting-only variants separately with clear names and comments documenting which components were modified.
- **Audit Trail:** Log all scaffold edits during the rewriting phase (timestamp, edit description, task context) to document how the agent modified the scaffold.

### Evaluation Procedure
1. **Phase 1 – Rewriting (Condition B only):** Agent iterates on the training pool (50–60 primary-family tasks) and rewrites the scaffold. Duration: 3–5 days (or until improvement plateaus). Scaffold is frozen after this phase.
2. **Phase 2 – Evaluation:** Both Condition A (baseline) and Conditions B1, B2, B3 (ablations) are evaluated on held-out Test Pools A and B. All evaluations are run under identical settings (same model, temperature, random seed per task).
3. **Phase 3 – Analysis:** Compute success rates, effect sizes, CIs, and p-values. Produce a comparison table and visualization (bar plots with error bars).

---

## 7. Uncertainty Quantification

### Statistical Inference
- **Confidence Intervals:** Report 95% CIs for all effect sizes (Δ, Cohen's d, odds ratio).
  - For binary metrics: Use Agresti–Coull (exact Clopper–Pearson if n < 30 per cell).
  - For continuous metrics: Use t-distribution-based CIs with Welch's correction if variance is unequal.
- **P-values:** Use two-tailed tests; report exact p-values (not stars).
- **Multiple Comparisons:** If running many ablation tests, apply Bonferroni correction or false-discovery-rate control to maintain family-wise error rate at α = 0.05.

### Sensitivity Analysis
1. **Task Difficulty:** Stratify held-out test tasks by estimated difficulty (e.g., easy/medium/hard). Re-run analysis on each stratum to check whether improvements are consistent across difficulty levels.
2. **Robustness to Metric Choice:** If switching from success rate to solution quality score changes the conclusions, report both results prominently.
3. **Robustness to Ablation Design:** If the definitions of "logic-only" and "formatting-only" are ambiguous, run two alternative ablation partitions and report results for each.

### Uncertainty in Sampling Frame
- **Task Sample Size:** The design calls for ≥30 held-out primary-family tasks and ≥15 adjacent-domain tasks. With these sample sizes, a true effect of Δ = 10 percentage points can be detected with ~80% power (assuming binomial test, n=30, p_baseline ≈ 0.5). Report post-hoc power analysis.
- **Population Validity:** Held-out tasks are sampled from the same family as the training pool; improvements may not generalize to **other** task families not represented. Acknowledge this limitation explicitly.

---

## 8. Falsification Criteria (from state.md)

The design's core premise (scaffold rewriting produces generalizable improvements) is **falsified** if either of these observations occur:

1. **Lack of Within-Family Generalization:** The improvement measured on held-out primary-family tasks (Pool A) is not statistically significant (p > 0.05) or the 95% CI includes zero.

2. **Lack of Out-of-Domain Transfer:** The improvement on adjacent-domain tasks (Pool B) is less than 50% of the improvement on primary-family tasks (Transfer Ratio < 0.50).

If either condition holds, conclude that scaffold rewriting produces task-specific overfitting rather than robust improvements.

---

## 9. Stopping Rule (from state.md)

- **Primary Evaluation:** Stop after ≥30 held-out primary-family tasks have been evaluated per scaffold variant.
- **Early Stopping – Null Case:** If after 30 primary-family tasks, Δ is trending toward zero and CI includes zero, stop early; do not proceed to adjacent-domain evaluation.
- **Continuation – Success Case:** If Δ ≥ 10 percentage points and p < 0.01 after primary-family evaluation, proceed to evaluate ≥15 adjacent-domain tasks to assess transfer.
- **Time Limit:** If evaluation is not complete within [X days], halt and report interim results.

---

## 10. Reporting and Interpretation

### Results Table
| Condition | Pool | n_tasks | Success Rate (%) | 95% CI | Effect Size (Cohen's d or OR) | p-value |
|-----------|------|---------|------------------|--------|-------------------------------|---------|
| Baseline A | Primary (A) | 30 | [P_baseline] | [CI_A] | – | – |
| Rewritten B | Primary (A) | 30 | [P_rewritten] | [CI_B] | [d or OR] | [p] |
| Logic-Only B1 | Primary (A) | 30 | [P_B1] | [CI_B1] | [d or OR] | [p] |
| Format-Only B2 | Primary (A) | 30 | [P_B2] | [CI_B2] | [d or OR] | [p] |
| Baseline A | Adjacent (B) | 15 | [P_baseline_B] | [CI_A_B] | – | – |
| Rewritten B | Adjacent (B) | 15 | [P_rewritten_B] | [CI_B_B] | [d or OR] | [p] |

### Interpretation Logic
- **If p_main < 0.05 AND Transfer Ratio ≥ 0.50:** ✓ Premise supported. Scaffold rewriting produces generalizable improvements.
- **If p_main < 0.05 BUT Transfer Ratio < 0.50:** Partial support. Improvements are real but partially domain-specific.
- **If p_main ≥ 0.05:** ✗ Premise falsified. No evidence of generalization within the family.

### Transparency
Document any deviations from this plan (e.g., tasks removed due to errors, metric definitions adjusted). Report all results (positive, negative, and null), not just statistically significant findings.

---

## 11. References to Sampling Frame

This design explicitly operationalizes the sampling_frame defined in state.md:

> "The population is the space of tasks that the agent model + scaffold can meaningfully attempt. The unit is a single (task, scaffold_variant) pair. We sample tasks stratified by source family (primary family used during scaffold rewriting, held-out variant family with same structure, adjacent-domain family to test transfer)."

- **Test Pool A (§6 Primary Family)** realizes the "held-out variant family with same structure" stratum.
- **Test Pool B (§6 Adjacent Domain)** realizes the "adjacent-domain family" stratum.
- **Stratified Sampling (§2)** ensures each stratum is represented proportionally and allows analysis of transfer across the sampling frame's strata.
- **Ablation Study (§4)** isolates which components of the scaffold rewrite drive improvements across the sampling frame.
- **Statistical Testing (§7)** quantifies whether observed differences generalize across the entire sampling frame or are artifacts of task-specific overfitting.

---

## Summary

This experimental design addresses the core risk—overfitting—by:
1. **Holding out tasks** used during rewriting from the final comparison.
2. **Testing transfer** across a related domain to check robustness.
3. **Ablating components** to isolate which scaffold changes matter.
4. **Quantifying uncertainty** with confidence intervals and significance tests.
5. **Defining falsification criteria** so the premises can be rejected if transfer fails.

The sampling_frame is the central constraint: all comparisons are conducted on tasks sampled from the defined population strata, and all inference is scoped to the generality claimed by that frame.
