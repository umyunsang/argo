# Experimental Design: Harness Evolution Generalization

## Research Question
An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

## Experimental Overview
This design tests whether improvements from harness evolution generalize beyond the task distribution used during optimization, ruling out overfitting to specific task features.

## 1. Main Comparison & Conditions

### Condition A: Optimized Harness (In-Distribution Test)
- Agent with evolved scaffold, evaluated on tasks from the **same family** used during harness iteration
- Represents the "fitted" or potentially overfitted state
- Baseline: initial generic harness with same model

### Condition B: Optimized Harness (Out-of-Distribution Test)
- **Same evolved scaffold** as Condition A, evaluated on **related but distinct tasks** not seen during harness optimization
- Directly tests generalization: does the improvement transfer?
- If gains disappear here, overfitting is demonstrated
- If gains persist, real scaffold improvements are supported

### Condition C: Random Harness Modifications (Control)
- Same task splits and evaluation setup as Conditions A & B
- Apply random mutations to the scaffold parameters/rules instead of learned changes
- Establishes whether the **particular harness changes matter** vs. noise
- Should show near-baseline performance, validating the optimization signal

## 2. Task Family Design

### Training Task Set (Used During Harness Iteration)
- 10–15 tasks from primary category (e.g., "multi-step reasoning" or "tool use")
- Examples: task variants with increasing complexity, different domains within the category

### Test Task Sets
**In-distribution validation set (Condition A):**
- 5–8 additional tasks from the same category as training
- Drawn from the same source/generator but not exposed during harness tuning

**Out-of-distribution test set (Condition B):**
- Related but structurally distinct tasks:
  - Same reasoning type but in a new domain
  - Same problem class but higher or lower complexity tier
  - Same model-interaction pattern but different task surface (e.g., if training was code generation, test is structured query generation; if training was planning, test is constraint satisfaction)
- **20–25 tasks** to ensure robust OOD measurement
- Curated to require the *same harness capabilities* but test transfer, not memorization

### Control Task Set (Condition C)
- Same split as Conditions A & B
- Used to evaluate harness mutations that are intentionally *not* optimized

## 3. Ablations

### Ablation 1: Harness Component Importance
Selectively disable key evolved components:
- Disable the highest-impact rule/tool/format change from the optimized harness
- Evaluate on both in-distribution and OOD task sets
- If in-distribution performance drops but OOD performance is unchanged, the component is overfit
- If both drop equally, the component is genuinely useful for the task family

### Ablation 2: Harness Variation Sensitivity
Introduce small stochastic variations of the evolved harness (±5–10% parameter perturbation):
- Apply to OOD test set only
- If performance is brittle (high variance), suggests overfitting to specific task quirks
- If robust (low variance), suggests a stable, generalizable improvement

## 4. Analysis Plan

### Primary Analysis
**Condition Comparison (Generalization Test):**
1. Measure performance gain from baseline → optimized harness on in-distribution tasks (A)
2. Measure the **same gain metric** on OOD tasks (B)
3. Calculate **generalization ratio**: `(OOD improvement) / (In-distribution improvement)`
   - Ratio near 1.0 → generalizable improvement (good)
   - Ratio < 0.5 → significant overfitting (bad)
   - Ratio 0.5–0.8 → partial transfer, context-dependent

4. Control check: Random harness mutations (C) should show near-zero improvement on both sets

### Secondary Analysis (Ablation 1: Component Importance)
- For each disabled component:
  - Measure performance drop on in-distribution tasks
  - Measure performance drop on OOD tasks
  - Identify components that matter for generalization vs. those that only help in-distribution

### Tertiary Analysis (Ablation 2: Robustness)
- Plot performance vs. perturbation magnitude
- Estimate 95% confidence band on OOD performance under variations
- Smooth harnesses should show tight bands; overfit harnesses show wide variance

### Statistical Summary
- Report 95% CIs for all improvements using bootstrap (n=1000 resamples over tasks)
- Perform paired t-tests: baseline vs. optimized on OOD tasks (α=0.05)
- Report effect size (Cohen's d or equivalent)

## 5. Concrete Resources

### Required Artifacts
1. **Task repositories:**
   - In-distribution training set: 10–15 tasks (Condition A source)
   - In-distribution validation set: 5–8 tasks (Condition A test)
   - OOD test set: 20–25 structurally distinct tasks (Condition B test)
   - Random-mutation validation: reuse same test splits

2. **Harness codebases:**
   - Baseline scaffold (generic, model-compatible)
   - Evolved scaffold (optimized on training set during iteration)
   - Mutated scaffolds for Ablation 1 (component deletions)
   - Perturbed scaffolds for Ablation 2 (stochastic variants)

3. **Evaluation infrastructure:**
   - Pass/fail and metric-based scoring system (defined per task)
   - Automated harness swapping (no model inference changes)
   - Logging of harness state and task-level results

4. **Computational budget:**
   - ~60–100 task runs per condition (3 conditions × ~30 tasks average)
   - Ablation 1: +5–10 harness variants × ~30 tasks = +150–300 runs
   - Ablation 2: +10 perturbed variants × ~25 OOD tasks = +250 runs
   - **Total: ~800–1000 task evaluations**
   - Wall time depends on task complexity; assume 30s–5min per task

## 6. Outcome Metrics

### Primary Metrics
1. **Task completion rate (%)**: Proportion of tasks solved correctly
   - Reported per condition (baseline, optimized, random)
   - Stratified by in-distribution vs. OOD

2. **Generalization ratio** (dimensionless):
   - Defined as: `(OOD improvement %) / (In-distribution improvement %)`
   - Threshold for "real generalization": ratio ≥ 0.6 (at least 60% of gain transfers)

3. **Absolute improvement on OOD** (percentage points):
   - Primary evidence: if evolved harness meaningfully outperforms baseline on held-out tasks

### Secondary Metrics
1. **Component ablation impact**: For each component, `Δ(in-dist) – Δ(OOD)`
   - Identifies which harness changes are task-specific vs. general

2. **Robustness score**: Standard deviation of OOD performance under perturbation
   - Lower is better; indicates a stable, generalizable harness

3. **Effect size** (Cohen's d): Baseline vs. optimized on OOD tasks
   - Practical significance, not just statistical

## 7. Uncertainty Quantification

### Bootstrap Confidence Intervals
- For each condition (A, B, C) and each metric:
  - Resample tasks with replacement (n=1000 bootstrap samples)
  - Compute metric for each sample
  - Report 95% CI: [2.5th percentile, 97.5th percentile]
  - Visualize as error bars on all condition comparisons

### Statistical Tests
1. **Paired t-test**: Baseline vs. optimized on OOD tasks
   - Null: no difference in completion rate
   - Alternative: optimized > baseline
   - Report t-statistic, p-value, and effect size

2. **One-way ANOVA**: Baseline vs. optimized vs. random control
   - Null: all three have equal means
   - Confirms that optimization signal is not noise

3. **Generalization ratio CI**: Bootstrap the ratio itself
   - Compute ratio for each bootstrap sample
   - Report 95% CI around ratio estimate
   - Determine if ratio is significantly > 0.6 (or another threshold)

### Uncertainty Sources
- **Task sampling variability**: Tasks are sampled from families; different subsets may vary
  - Mitigation: use stratified sampling or ensure balanced task difficulty
  
- **Stochasticity in agent behavior**: If the model or harness includes randomness
  - Mitigation: report across multiple runs (5–10 per task/condition) and compute variance
  
- **OOD task definition ambiguity**: "Related but distinct" is qualitative
  - Mitigation: a priori define OOD criteria (domain shift, complexity tier, structure); have external reviewer confirm classification

## 8. Success Criteria

### Strong Evidence of Real Improvement (Not Overfitting)
✓ Significant improvement on in-distribution tasks (Condition A) vs. baseline  
✓ Statistically significant improvement on OOD tasks (Condition B) vs. baseline (p < 0.05)  
✓ Generalization ratio ≥ 0.6 (at least 60% transfer)  
✓ Random harness mutations (Condition C) show no improvement  
✓ Ablation 1: Core components impact both in-dist and OOD similarly  
✓ Ablation 2: OOD performance robust to harness perturbations (low variance)

### Weak or No Evidence
✗ Large in-distribution gain but flat or negative OOD gain  
✗ Generalization ratio < 0.4 (less than 40% transfer)  
✗ No significant OOD improvement (p ≥ 0.05)  
✗ Random mutations perform similarly to optimized harness  
✗ Single ablated component collapses in-dist but not OOD performance

## 9. Reporting

### Figures
1. Bar chart: Completion rate (baseline, optimized, random) × (in-dist, OOD) with 95% CIs
2. Line plot: Generalization ratio and its 95% CI, with reference line at 0.6
3. Heatmap: Ablation 1 component impacts on in-dist vs. OOD
4. Scatter: OOD performance vs. perturbation magnitude (Ablation 2)

### Tables
1. Summary table: Completion %, improvement %, generalization ratio, effect size per condition
2. Ablation summary: Component name, in-dist drop, OOD drop, interpretation
3. Statistical tests: t-statistic, p-value, 95% CI for all key comparisons

### Narrative
- Interpret each result in context of the research question
- Discuss plausibility of OOD vs. in-dist differences
- Acknowledge limitations (task diversity, harness complexity)
- Conclude whether the harness improvements are generalizable

---

## Appendix: Task Family Examples

*For concreteness, this design applies to any task family. Example instantiations:*

**Example 1: Code Generation**
- Training tasks: Simple function writing (string manipulation, math)
- In-distribution validation: More complex functions, same problem types
- OOD test: Code generation in a different language or domain (e.g., SQL, configuration)

**Example 2: Multi-step Reasoning**
- Training tasks: 3–5 step logical deduction puzzles
- In-distribution validation: Similar puzzles, different scenarios
- OOD test: Multi-step planning tasks, constraint satisfaction problems

**Example 3: Tool Use**
- Training tasks: Sequential tool calls for data retrieval
- In-distribution validation: Similar workflows, different data sources
- OOD test: Tool composition for a new task type (e.g., shift from Q&A to summarization)

---

*Design complete. This design isolates generalization from overfitting by comparing performance across in-distribution and structurally distinct out-of-distribution tasks, with ablations and robustness checks to confirm that observed improvements reflect real scaffold enhancements.*
