# Experimental Design: Scaffold Rewriting Generalization

## Overview

This design tests whether improvements from iterative agent scaffold rewriting reflect genuine capability gains or are artifacts of fitting to the particular task distribution used during rewriting. The core method uses a train/test split at the task level: observe improvement on tasks used during rewriting (training set), then measure improvement on independent held-out tasks (test set). A significant generalization gap indicates overfitting.

---

## Research Question

Do improvements in agent task performance from iterative scaffold rewriting generalize to held-out tasks from the same family, or are they artifacts of fitting to the particular task distribution used during rewriting?

---

## Main Comparison: Generalization Gap Design

### Sampling Frame

Independent task instances from a documented family of related agent tasks. The unit is a single task instance. The sampling frame is partitioned into:

1. **Training set**: tasks available during scaffold iteration and rewriting (observed by the experimenter during design decisions)
2. **Held-out evaluation set**: tasks invisible to the rewriting process and revealed only at final evaluation

Both sets are:
- Sampled via a pre-committed, documented sampling strategy (e.g., stratified random sampling by task complexity, context length, or goal type)
- Representative of the same underlying task family
- Drawn before rewriting begins to avoid selection bias

**Example instances**: if the family is "code generation tasks," instances could be functions to implement with varying signature complexity, docstring detail, and context length. If the family is "multi-step reasoning," instances could be planning problems with varying state spaces and goal depths.

### Conditions

#### Condition A: Baseline (Fixed Scaffold)
- Use an initial, fixed agent scaffold (e.g., standard prompt structure, default tool set, action space)
- Evaluate on both training and held-out task sets
- No modification between iterations

#### Condition B: Rewritten Scaffold
- Start with the same initial scaffold as Condition A
- Iteratively rewrite the scaffold (prompt, tools, action space structure, reasoning steps, etc.) based on performance on the **training set tasks only**
- Track all scaffold versions and the rationale for changes
- Stop after ≤5 iterations or when training-set improvement plateaus for 2 consecutive iterations
- Evaluate the final scaffold on both training and held-out task sets

### The Comparison

For each set (training and held-out):

$$	ext{Improvement}_{	ext{set}} = 	ext{Performance}_{	ext{final}} - 	ext{Performance}_{	ext{baseline}}$$

Compute the **generalization gap**:

$$	ext{Generalization Gap} = 	ext{Improvement}_{	ext{training}} - 	ext{Improvement}_{	ext{held-out}}$$

A **positive, statistically significant gap** indicates overfitting (improvement is larger on training tasks, suggesting the rewrite fitted the training distribution). A gap indistinguishable from zero or negative suggests improvements generalize.

---

## Ablations

### Ablation 1: Limited Training Set Size

**Rationale**: Overfitting risk increases with limited training data. A smaller training set allows the scaffold to overfit more easily.

**Conditions**:
- Rewrite using only the first 5 tasks from the training set (vs. the full training set in Condition B)
- All other parameters identical
- Evaluate on the same held-out set

**Expected outcome**: If overfitting is the mechanism, the generalization gap should increase (improvement is larger on the few training tasks, smaller on held-out tasks). If improvements are robust to sample size, the gap should be similar.

### Ablation 2: Cross-Validation / Task-Based Generalization

**Rationale**: To isolate whether improvements depend on memorizing specific task instances vs. generalizing to task structure, use a cross-validation approach within the training set.

**Conditions**:
- Partition the training set into 3 equal folds
- For each fold: rewrite the scaffold using the other two folds (never the held-out fold)
- Evaluate the rewritten scaffold on the held-out fold
- Average results across folds

**Expected outcome**: If improvements generalize to unseen task *instances* but within the same task family, cross-validation scores should be similar across folds and should match the held-out evaluation. If the improvement is brittle or relies on memorization, CV scores will vary widely or diverge from held-out scores.

---

## Analysis Plan

### Primary Analysis: Generalization Gap Hypothesis Test

1. **Compute performance for each task instance**:
   - Baseline: run Condition A on all tasks, record success metric per task
   - Final rewritten: run Condition B on all tasks, record success metric per task

2. **Compute per-set improvements**:
   - Training set: $ar{I}_{	ext{train}} = rac{1}{n_{	ext{train}}} \sum_i (	ext{Final}_i - 	ext{Baseline}_i)$ for training tasks
   - Held-out set: $ar{I}_{	ext{held-out}} = rac{1}{n_{	ext{held-out}}} \sum_j (	ext{Final}_j - 	ext{Baseline}_j)$ for held-out tasks

3. **Estimate the generalization gap and confidence interval**:
   - $\hat{G} = ar{I}_{	ext{train}} - ar{I}_{	ext{held-out}}$
   - Bootstrap 95% CI: resample tasks with replacement within each set 10,000 times, compute the CI
   - **Decision rule**: if 95% CI does not include zero, reject the null hypothesis (no gap) at α=0.05

4. **Interpret**:
   - If $\hat{G} > 0$ and CI excludes zero: overfitting detected; improvements on training tasks do not generalize
   - If $\hat{G} ≈ 0$ and CI includes zero: improvements generalize; no evidence of task-distribution overfitting
   - If $\hat{G} < 0$ and CI excludes zero: generalization gain (held-out improvement exceeds training improvement); indicates robustness

### Secondary Analyses

1. **Effect size**: report Cohen's d for the gap (how large is the overfitting signal relative to within-set variance?)

2. **Sensitivity to threshold**: repeat the analysis with different definitions of "success" on each task (e.g., partial credit, success rate)

3. **Per-task correlation**: scatter plot of baseline performance vs. training-set improvement; check for correlation that might suggest easier tasks drive the training improvement

4. **Scaffold change audit**: catalog all changes made during rewriting; manually assess whether changes are task-specific heuristics (high overfitting risk) or general improvements (low overfitting risk)

---

## Concrete Resources

### Task Family and Sampling

- **Task family**: [specify, e.g., "coding tasks from a standard benchmark (HumanEval, MBPP, etc.)"]
- **Training set size**: $n_{	ext{train}} = 20$ task instances
- **Held-out set size**: $n_{	ext{held-out}} = 30$ task instances
- **Sampling strategy**: stratified random by task complexity quartile (see sampling_frame definition); draw training and held-out sets independently before rewriting begins

### Model and Inference

- **Model**: [fixed; e.g., Claude 3 Sonnet]
- **Inference settings**: [fixed; e.g., temperature=0, max_tokens=4096]
- **Modification restriction**: only the scaffold may change; model weights, quantization, and inference hyperparameters remain constant

### Scaffold Rewriting Setup

- **Initial scaffold**: [specify baseline version; e.g., standard few-shot prompt + tool definitions]
- **Rewriting iterations**: maximum 5 cycles
- **Rewriting input**: performance on training set tasks only; held-out results are hidden until final evaluation
- **Rewriting output**: documented scaffold versions with change logs

### Computational and Temporal Resources

- **Baseline evaluation**: 20 (training) + 30 (held-out) = 50 task runs
- **Rewritten evaluation**: 50 task runs at final scaffold version; optionally 50 runs per iteration for monitoring (optional)
- **Total evaluations**: ≈50–300 task runs depending on monitoring frequency (conservative estimate: 150 runs)
- **Time per task**: [estimated, e.g., 30 seconds per inference + scoring]
- **Total compute**: ≈75–150 GPU-minutes (or equivalent)

---

## Outcome Metrics

### Primary Metric: Success Rate

**Definition**: binary success on each task (agent achieves goal / solves task correctly)

**Measurement**:
- Baseline condition: proportion of training and held-out tasks solved
- Rewritten condition: proportion of training and held-out tasks solved
- Report per-condition, per-set means and 95% CIs

### Secondary Metrics

1. **Generalization gap** (primary outcome of interest)
   - Definition: $\hat{G} = ar{I}_{	ext{train}} - ar{I}_{	ext{held-out}}$ where $I$ is success rate improvement
   - Interpretation: positive gap = overfitting evidence

2. **Training-set vs held-out task performance** (scatter and correlation)
   - Definition: baseline performance on each task vs. improvement from rewriting
   - Purpose: detect if rewriting helps only on easier or harder tasks

3. **Generalization efficiency** (robustness metric)
   - Definition: ratio of held-out improvement to training improvement
   - Interpretation: ratio near 1 = good generalization; ratio near 0 = poor generalization

4. **Variance across tasks** (within-set variability)
   - Definition: standard deviation of improvement across tasks within training and held-out sets
   - Purpose: high variance suggests task-specific overfitting; low variance suggests general improvements

---

## Uncertainty Quantification

### Confidence Intervals

- **Bootstrap 95% CI** on all metrics (gap, improvements, ratios):
  - Resample tasks with replacement within each set
  - Recompute statistics 10,000 times
  - Report the 2.5th and 97.5th percentiles

### Hypothesis Test

- **Generalization gap test**:
  - $H_0$: $G = 0$ (no gap; improvements generalize equally)
  - $H_1$: $G 
eq 0$ (gap exists; improvements are task-distribution-specific)
  - **Test statistic**: $\hat{G}$ / SE($\hat{G}$) ~ t-distribution (or use bootstrap)
  - **Decision**: reject $H_0$ if 95% CI excludes 0

### Effect Size and Power

- **Sample size justification**: $n_{	ext{held-out}} = 30$ provides ≈80% power to detect a medium effect (gap = 0.15 success rate, SD ≈ 0.20) with two-sample t-test at α=0.05
- **Sensitivity analysis**: repeat with different thresholds or partial-credit scoring; gap should be robust

---

## Stopping Rule

**Collect results until**:
  1. Held-out evaluation sample size reaches $n = 30$ task instances, **OR**
  2. The generalization gap (training – held-out improvement) is detected with 95% CI not crossing zero, whichever comes first

**Stop scaffold rewriting after**:
  - ≤5 iterations of scaffold changes, **OR**
  - Improvement plateaus on the training set for 2 consecutive iterations (i.e., two successive iterations yield <1% improvement in success rate)

---

## Interpretation Guide

### Evidence of Real Improvement (Desired Outcome)

- **Condition**: 95% CI on generalization gap includes zero or is negative
- **Interpretation**: Improvements from rewriting generalize to held-out tasks; no evidence of task-distribution overfitting
- **Conclusion**: Scaffold rewriting improved genuine agent capability

### Evidence of Overfitting (Risk Scenario)

- **Condition**: 95% CI on generalization gap is positive and excludes zero
- **Interpretation**: Improvements are significantly larger on training tasks; do not generalize to held-out tasks
- **Conclusion**: Rewriting fitted the training task distribution; improvements are not reliable

### Ambiguous Outcome

- **Condition**: 95% CI on generalization gap is wide, includes zero, or results are mixed across metrics
- **Interpretation**: Sample size insufficient or effect is small
- **Action**: increase held-out sample size, or run cross-validation ablation to clarify

---

## Summary Table

| Component | Specification |
|-----------|---|
| **Sampling frame** | Independent task instances from a documented family; training set (n=20) and held-out set (n=30) drawn via pre-committed sampling strategy; both representative of the family |
| **Main comparison** | Baseline (fixed scaffold) vs. Rewritten scaffold; measure improvement on training and held-out sets separately |
| **Primary outcome** | Generalization gap: training improvement – held-out improvement; 95% CI should include zero for real improvement |
| **Ablations** | (1) Limited training set to test overfitting risk; (2) cross-validation to isolate task-instance vs. task-family generalization |
| **Metrics** | Success rate (primary); generalization gap, efficiency ratio, within-set variance (secondary) |
| **Uncertainty** | Bootstrap 95% CIs on all metrics; hypothesis test on gap with two-tailed α=0.05 |
| **Resources** | ~150 total task runs; ~75–150 GPU-minutes; model and inference fixed |
| **Stopping rule** | Stop collecting when n_held-out=30 OR gap CI excludes zero; stop rewriting at ≤5 iterations OR plateau |

