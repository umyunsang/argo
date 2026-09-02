# Experimental Design: Measuring Harness Improvement vs. Model Quality Drift

## Research Question
How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

## Main Comparison: 2×2 Factorial

We use a 2×2 factorial design with two factors: **harness version** and **model version**.

### Factor 1: Harness Version
- **Level A (baseline)**: Harness snapshot at time t₀ (the "old" harness before improvement cycle)
- **Level B (improved)**: Harness snapshot at time t₁ (the "new" harness after self-improvement)

### Factor 2: Model Version  
- **Level 1 (fixed reference model)**: A pinned model version (e.g., Claude 3.5 Sonnet, a specific API date)
- **Level 2 (latest model)**: The current/latest available model version

### Design Conditions

| Condition | Harness | Model | Interpretation |
|-----------|---------|-------|-----------------|
| C1 | old (t₀) | fixed reference | baseline |
| C2 | new (t₁) | fixed reference | **harness improvement alone** |
| C3 | old (t₀) | latest | model drift alone |
| C4 | new (t₁) | latest | both factors |

The critical condition is **C2 (new harness + fixed model)**. If C2 performance exceeds C1 substantially, that improvement cannot be attributed to model prompt-following quality drift; it is evidence of actual harness value.

## Sampling Frame
**Population**: All task instances in the held-out evaluation set.  
**Unit**: A single triplet `(task_i, harness_version, model_version)` evaluated as one performance observation.  
**Sampling strategy**: Run all tasks in the held-out set under each of the four conditions. Do not subsample tasks; run the complete evaluation set to maximize power and representativeness.

## Ablation Study: Model-Only Improvement

To measure and quantify the confound from model-version drift alone, we compare conditions **C1 vs C3** (holding harness constant at t₀, varying model).

- **C1 (old harness, fixed model)** vs **C3 (old harness, latest model)**: Any difference here is attributable to the model alone, not the harness.
- **Expected outcome**: If C3 > C1, the model has improved. This gives us a baseline estimate of "free" performance gain from model drift.
- **Interpretation**: We can then subtract this effect from the C2 vs C1 difference to estimate harness-specific contribution.

## Concrete Resources

### 1. Held-Out Evaluation Set
- **Resource**: The existing evaluation set referenced in constraints.
- **Description**: A fixed set of task instances, used only for final measurement (never for in-workspace training or harness development).
- **Assumption**: Set size is ≥30 tasks to enable stable statistical inference.

### 2. Harness Snapshots
- **Snapshot t₀ (baseline)**: Version control checkpoint or archived copy of CLAUDE.md, skills/, rules/, and all harness artifacts from before the improvement cycle.
- **Snapshot t₁ (improved)**: Version control checkpoint or archived copy of harness artifacts after the self-improvement cycle concludes.
- **Storage**: Both snapshots must be stored outside the candidate workspace to allow external evaluation without confound.

### 3. External Scoring Service
- **Requirement**: A scoring mechanism that runs *outside* the candidate workspace (per constraints).
- **Resource**: Assumed to exist; must be capable of evaluating task success/failure, quality metrics, and error classification on the held-out set.
- **Note**: Scoring cannot be done inside the workspace where the harness was improved, to avoid circularity.

### 4. Model Versions
- **Fixed Reference Model**: A specific pinned model version (e.g., Claude 3.5 Sonnet released 2024-Q4, or an API snapshot date). Use the model version that was active when the harness improvement cycle began, or an earlier stable release.
- **Latest Model**: The current production model available for evaluation (e.g., Claude 4 or later, if released).
- **Justification**: Pinning the reference model isolates harness improvements from model-version drift. Comparing to the latest model shows real-world performance.

## Outcome Metrics

### Primary Metric
**Task Success Rate (%) within each condition**: Fraction of tasks in the held-out set for which the harness+model combination produces a correct/acceptable result.

- Computed per condition: `success_rate_C1`, `success_rate_C2`, `success_rate_C3`, `success_rate_C4`.
- Primary contrast of interest: `Δ_harness = success_rate_C2 - success_rate_C1` (improvement from new harness, controlling for model version).

### Secondary Metrics
1. **Error classification**: Breakdown of failure modes (e.g., tool unavailable, prompt misinterpreted, timeout, wrong output type).
   - Compare distributions across conditions to infer where the harness improved.
   
2. **Task latency (median, p95)**: Time to completion per task.
   - Harness improvements should not degrade speed; include latency to detect unintended side effects.
   
3. **Model drift effect**: `Δ_model = success_rate_C3 - success_rate_C1` 
   - Quantifies the "free" improvement from model version alone.
   - Use to compute the harness-specific improvement: `Δ_harness_adjusted = (success_rate_C2 - success_rate_C1) - (success_rate_C3 - success_rate_C1)`.

## Quantifying Uncertainty

### Sample Size & Confidence Intervals
- **Sample size per condition**: All |evaluation_set| tasks × 1 run per task per condition.
- Assuming |evaluation_set| ≥ 30 (estimated from typical held-out sets).
- **Confidence interval method**: Binomial proportion confidence intervals (Wilson score or Clopper-Pearson) for each success rate.
- **Report**: 95% confidence intervals for each of the four condition success rates and for the contrasts (e.g., C2 − C1, C3 − C1).

### Effect Size
- **Primary effect size**: Absolute difference in success rate (Δ_harness), reported as percentage points.
- **Secondary effect size**: Odds ratio or relative risk of success under new harness vs. old harness (holding model constant).

### Power & Stopping Rule
- **Stopping rule** (from state.md): Collect results until both main conditions (C1 and C2) reach n ≥ 30 samples with settled 95% CI, OR after evaluating 2 sequential harness snapshots, whichever comes first.
- **Sensitivity**: With n=30 per condition, the design can detect an absolute difference of ~±20 percentage points with 80% power (assuming true rates ~50%). If task success is highly variable or rare, power may be lower.

### Sensitivity Analysis
1. **Subgroup analysis by task type**: Stratify held-out tasks by domain/difficulty and recompute success rates.
   - If harness improvement is real, it should hold (or strengthen) within each subgroup, not disappear.
   
2. **Variance check**: If Δ_harness < Δ_model (harness gain is smaller than model drift), this suggests the harness is not adding independent value; report as a caveat.

## Analysis Plan

### Step 1: Baseline Comparison (C1 vs. C3)
- Evaluate all tasks in the held-out set using the old harness with both the fixed reference model and the latest model.
- Compute success_rate_C1 and success_rate_C3 with 95% CI.
- Interpret Δ_model = C3 − C1 as the "model-only" effect.

### Step 2: Main Effect (C1 vs. C2)
- Evaluate all tasks using the new harness with the fixed reference model.
- Compute success_rate_C2 with 95% CI.
- Compute Δ_harness = C2 − C1.
- **Decision rule**: If 95% CI for Δ_harness excludes zero (i.e., lower bound > 0), evidence of harness improvement.

### Step 3: Combined Effect (C4)
- Evaluate all tasks using the new harness with the latest model.
- Compute success_rate_C4 with 95% CI.
- Compare C4 to C1, C2, C3 to understand interaction (if any) between harness and model version.

### Step 4: Adjusted Effect Size
- Compute Δ_harness_adjusted = (C2 − C1) − (C3 − C1).
- If Δ_harness_adjusted > 0, harness improvement is genuine and not fully explained by model drift.
- Report as the "harness-independent improvement."

### Step 5: Subgroup & Sensitivity
- Stratify by task type, difficulty, or domain (if the evaluation set permits).
- Recompute primary metric within each stratum.
- Check for interaction or heterogeneity.

## Validity & Assumptions

### Internal Validity
- **Confounds controlled**: Model version is held constant in C1–C2 contrast, isolating harness effect.
- **Potential residual confounds**: 
  - Harness snapshots must be truly isolated (no hidden in-workspace scoring).
  - Fixed reference model must not be updated between runs.
  - External scorer must be consistent across conditions.

### External Validity
- **Generalization**: Results apply to the tasks in the held-out set only. If held-out set is biased (e.g., all tasks of one type), findings may not generalize to production tasks.

### Measurement Validity
- **Success definition**: Must be pre-specified before evaluation (binary pass/fail, rubric score, etc.) to avoid post-hoc cherry-picking.
- **Scorer reliability**: External scorer must produce consistent results; can be checked by re-scoring a random subset of tasks.

## Expected Outcomes & Interpretation

| Scenario | Δ_harness > 0 & CI excludes 0 | Δ_model | Interpretation |
|----------|-----|----------|---|
| A | Yes | Small | Harness improvement is real and substantial. |
| B | Yes | Large | Harness improved, but model drift is stronger. Harness is real but small relative to model. |
| C | No | Small | No evidence of harness improvement; gains are noise or within CI. |
| D | No | Large | Model improved; harness had no independent effect. |

**Recommended conclusion threshold**: Report harness improvement as credible only if Scenario A or B holds and 95% CI for Δ_harness does not include zero.

## Why This Design Addresses the Research Question

1. **Isolates harness from model**: By comparing (new harness, fixed model) vs. (old harness, fixed model), we measure harness effect independent of model-version drift.

2. **Controlled for confounds**: The 2×2 factorial separates harness-only, model-only, and combined effects.

3. **Respects constraints**: Scoring runs outside the candidate workspace; harness snapshots are stored externally; held-out set is fixed.

4. **Transparent uncertainty**: Confidence intervals and sample sizes are reported, avoiding false precision.

5. **Falsifiable**: If Δ_harness_adjusted ≤ Δ_model/2, the harness may not be providing independent value; this would refute the premise of harness self-improvement.
