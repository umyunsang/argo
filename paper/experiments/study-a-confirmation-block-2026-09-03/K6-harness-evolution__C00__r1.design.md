# Experimental Design: K6-Harness-Evolution

## Research Question
An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

## Overview
This design uses a train-test split strategy with nested cross-validation to separate the tasks used for harness optimization from the tasks used for evaluation, preventing overfitting while maintaining statistical rigor.

---

## Main Comparison

**Primary Research Hypothesis:** Improvements in agent performance from scaffold rewriting are generalizable to unseen tasks from the same task family, not merely fitted to the tasks used during scaffold iteration.

### Conditions

#### Condition 1: Baseline Harness (Fixed Control)
- Standard, unmodified agent scaffold (e.g., default prompt structure, tool definitions, error handling, state representation)
- No changes permitted during the study
- Applied to all tasks in both train and test sets
- Serves as the fixed reference point

#### Condition 2: Evolved Harness (Iterative Optimization)
- Initial scaffold starts from the same baseline as Condition 1
- Permitted rewrites across iterations based on performance on training tasks only
- Changes may include: prompt engineering, tool affordances, state representations, branching logic, error recovery patterns, observation formatting
- Model and inference settings remain unchanged
- Represents the agent's self-modification capability

#### Condition 3: Evolved Harness Frozen at Split (Generalization Check)
- Harness evolved against training tasks
- Frozen and applied to held-out test tasks without further modification
- This is where generalization is measured (does the evolved harness work on unseen tasks?)

---

## Task Strategy

### Task Partitioning
- **Total task family:** N related tasks from a consistent domain (e.g., API interaction, code debugging, reasoning chains—specific family TBD based on available resources)
- **Training set (Optimization):** ⌊0.7 × N⌋ tasks
  - Used only for scaffold iteration and feedback
  - Agent performance on these tasks drives harness rewrites
  - No held-out test data should be included here
  
- **Held-out test set (Generalization):** ⌈0.3 × N⌉ tasks
  - Never seen during harness optimization
  - Evaluation happens here
  - Measures whether the evolved harness generalizes

### Cross-Validation (Robustness Check)
- Perform k-fold cross-validation (k = 3 or 5, depending on task availability) over the entire task family
- In each fold:
  - Designate 30% of tasks as held-out test
  - Optimize harness on the remaining 70% (training tasks)
  - Freeze and evaluate on held-out test
- Report results across all folds (means, confidence intervals)

---

## Ablation Study

### Ablation 1: Rewrite Budget Constraint
**Hypothesis:** Unbounded rewriting can lead to overfitting even with train-test separation.

- **Variant A:** Evolved harness with no iteration limit (primary condition)
- **Variant B:** Evolved harness with fixed iteration budget (e.g., 3 rewrites maximum)
- **Variant C:** Evolved harness with early stopping (e.g., if training-set performance plateaus for 2 consecutive iterations)

**Expected finding:** If Variant A significantly outperforms Variants B and C on held-out test tasks, it suggests genuine improvement; if it degrades, it suggests the iteration budget is capturing overfitting risk.

---

## Analysis Plan

### Primary Analysis: Held-Out Test Performance

**Metric Comparison:**
- Baseline Harness: mean performance P_baseline on held-out test set
- Evolved Harness: mean performance P_evolved on held-out test set
- **Primary statistic:** ΔP = P_evolved − P_baseline

**Statistical Test:**
- Two-tailed paired t-test (if tasks are paired) or Welch's t-test (independent)
- Null hypothesis: ΔP = 0 (no generalization benefit)
- Alternative hypothesis: ΔP ≠ 0
- Significance level: α = 0.05

**Effect Size:**
- Cohen's d (standardized mean difference)
- Interpret: d > 0.2 (small), d > 0.5 (medium), d > 0.8 (large)

### Secondary Analysis: Train-Test Gap

**Within-study learning gap:**
- Δ_train = P_evolved(train) − P_baseline(train)  [gain on training tasks]
- Δ_test = P_evolved(test) − P_baseline(test)   [gain on held-out tasks]
- **Generalization ratio:** R = Δ_test / Δ_train
  - R ≈ 1.0 indicates proportional generalization (good)
  - R << 1 indicates poor generalization / overfitting (bad)
  - R > 1 (rare) indicates unexpected strong transfer

**Interpretation:**
- If R > 0.7 and Δ_test is statistically significant, conclude genuine gain
- If R < 0.3 and Δ_test is not significant, conclude overfitting

### Tertiary Analysis: Fold Consistency (k-Fold)

- For each fold k, compute Δ_test,k
- Report: mean(Δ_test,k), std(Δ_test,k), min/max
- If std is small and all folds show positive Δ_test, robustness is high
- If std is large or folds are inconsistent, the improvement may be task-dependent or fragile

### Error Propagation

- Report 95% confidence intervals on all means using bootstrap or t-distribution
- Confidence interval on ΔP: [P_evolved − P_baseline ± t_{critical} × SE_diff]
  where SE_diff = √(SE_baseline² + SE_evolved²)

---

## Concrete Resources

### Required Inputs

1. **Task Family:** N ≥ 15 related tasks (recommend N ≥ 30 for robust cross-validation)
   - Must be diverse enough to test generalization but related enough to form a family
   - Clear, deterministic success/failure criteria (binary or numeric scoring)
   - Examples: MMLU-like QA tasks, code completion tasks, reasoning puzzles, API interaction scenarios

2. **Agent Model:**
   - Fixed model (e.g., Claude 3.5 Sonnet, GPT-4o, etc.)
   - Frozen inference settings (temperature, max tokens, stop sequences, etc.)
   - Reproducible random seed if applicable

3. **Scaffold Harness:**
   - Baseline version (initial state for both conditions)
   - Rewrite tooling / interface (how does the agent modify its own prompt, state representation, tool definitions, etc.?)
   - Must be clear what constitutes a valid rewrite (to prevent arbitrary changes that break compatibility)

4. **Evaluation Environment:**
   - Consistent execution environment (isolated, repeatable)
   - Task runner / harness executor
   - Logging system to record all trials

### Compute Budget

- **Baseline condition:** N_tasks × 1 run = N runs
- **Evolved condition:** N_tasks × (E_iterations + 1) runs, where E_iterations is the average number of rewrites per training task
  - Assuming 3–5 iterations: ~(0.7N) × 5 + (0.3N) × 1 ≈ 4.2N runs
- **Ablation (budget variants):** additional 2 × 4.2N runs
- **Cross-validation (k folds):** multiply all above by k
- **Total estimate (k=3, N=30, E=5):** ~(1 + 4.2 + 2×4.2) × 3 ≈ 75–90 runs

### Hardware / Time
- Dependent on model and task complexity
- Budget 2–5 min per run × 80 runs ≈ 160–400 GPU-minutes (2.5–6.5 GPU-hours)

---

## Outcome Metrics

### Primary Metrics

1. **Success Rate (SR)**
   - % of tasks solved correctly
   - Baseline: SR_baseline (e.g., 65%)
   - Evolved: SR_evolved (e.g., 72%)
   - ΔSR = SR_evolved − SR_baseline (e.g., +7 percentage points)

2. **Efficiency (optional, if applicable)**
   - Average tokens used per task completion
   - Average steps/actions per task
   - Baseline vs. evolved comparison

### Secondary Metrics

1. **Robustness across fold (k-fold coefficient of variation)**
   - CV = std(ΔSR_k) / mean(ΔSR_k)
   - CV < 0.2 → robust
   - CV > 0.5 → fragile

2. **Task-level variance**
   - Per-task improvement distribution (histogram of per-task ΔSR)
   - Identify which task types benefit most / least

3. **Convergence trajectory on training tasks**
   - Plot SR_evolved vs. iteration count on training set
   - Assess if plateau occurs or oscillation suggests overfitting

---

## Uncertainty Quantification

### Confidence Intervals
- **95% CI on ΔSR:**
  - Method 1 (parametric): CI = ΔSR ± 1.96 × SE(ΔSR)
  - Method 2 (bootstrap): resample (task, baseline result, evolved result) tuples with replacement; recompute ΔSR for each; report 2.5th and 97.5th percentiles

### Bayesian Credible Interval (alternative)
- Treat ΔSR as a random variable with a beta-binomial prior (weak prior, e.g., Beta(1,1))
- Update with observed successes/failures
- Report 95% credible interval

### Statistical Power
- **Pre-specification:** if true effect is d = 0.5 (medium), achieve 80% power with n ≥ 0.3N (rule of thumb for paired t-test)
- **Post-hoc:** report achieved power given observed effect size

### Per-Fold Variance
- Across k folds, report ΔSR_k for each fold and 95% CI on the mean
- Check for systematic bias (e.g., does task composition affect the fold-to-fold variance?)

---

## Reporting Structure

1. **Executive Summary**
   - Primary result: ΔSR with 95% CI, p-value, effect size (d)
   - Conclusion: gains are / are not statistically significant and / or generalizable

2. **Main Results Table**
   - Condition (Baseline, Evolved) × Metric (SR, efficiency if applicable) × Split (Training, Held-out Test)
   - Include fold results if k-fold used

3. **Ablation Results Table**
   - Iteration budget constraint effect on ΔSR (held-out test)
   - Train-test gap (Generalization Ratio) for each variant

4. **Figures**
   - (A) Box plot: ΔSR per fold, with overall mean and 95% CI
   - (B) Learning curve: SR vs. iteration on training tasks (baseline flat line, evolved trajectory)
   - (C) Train-test gap: scatter plot showing training-set gain vs. test-set gain per task
   - (D) Per-task improvement: histogram of per-task ΔSR

5. **Failure Analysis**
   - Tasks where evolved harness underperforms (if any)
   - Identify task characteristics (e.g., task difficulty, type, domain) that correlate with improvement

---

## Threats to Validity & Mitigations

| Threat | Mitigation |
|--------|-----------|
| Overfitting to training tasks | Train-test split; k-fold CV |
| Task-specific optimization | k-fold rotation ensures diverse training sets per fold |
| Random variation in model outputs | Seed control, multiple runs per condition, CI reporting |
| Harness changes that break compatibility | Define and enforce harness "valid rewrite" rules |
| Insufficient task diversity | Ensure task family spans multiple difficulty/domain combinations |
| Iteration budget as a hidden hyperparameter | Ablation study explicitly varies iteration budget |

---

## Expected Outcomes

- **Positive result:** ΔSR > 0, p < 0.05, Generalization Ratio R > 0.7, consistent across folds
  - Interpretation: The evolved harness genuinely improves performance; gains generalize

- **Null result:** ΔSR ≈ 0, p > 0.05, wide CI
  - Interpretation: No evidence that harness rewriting improves performance

- **Negative result (overfitting):** ΔSR_train >> 0, ΔSR_test ≈ 0, R < 0.3
  - Interpretation: Harness changes overfit to training tasks and do not generalize

- **Iteration budget result:** Early stopping (Variant C) matches unbounded (Variant A) on test set
  - Interpretation: Conservative iteration limits suffice; full budget is unnecessary

---

## Conclusion

This design isolates the generalization capability of harness rewrites by enforcing a strict train-test separation and using k-fold cross-validation to ensure robustness. The combination of the main comparison, generalization ratio analysis, ablation on iteration budget, and comprehensive uncertainty quantification enables a high-confidence answer to whether scaffold improvements are real or fitted.
