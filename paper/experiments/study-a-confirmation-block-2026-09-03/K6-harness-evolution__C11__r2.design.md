# Experimental Design: Distinguishing Real Harness Gains from Task-Specific Overfitting

## Research Question
An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

## Sampling Frame
**Population & Units:** A family of related multi-step agent tasks within a single domain (e.g., software engineering, knowledge work, or technical operations). The unit of analysis is the individual task instance.

**Sampling Design:** Stratified random partition of the task family into three mutually exclusive cohorts:
- **Development cohort (40%):** Used to generate trajectories, diagnose scaffold weaknesses, and iteratively rewrite the scaffold
- **Evaluation cohort A (30%):** Held-out evaluation set, never seen during scaffold development, drawn from the primary task distribution
- **Evaluation cohort B (30%):** Held-out evaluation set from an independent sub-distribution within the same domain, stress-testing robustness to task variation

The two evaluation cohorts must differ on dimensions likely to expose overfitting (e.g., task difficulty, interaction patterns, error type prevalence, required tool combinations). This design guards against implicit curriculum effects that favored the development set (2608.18066).

---

## Main Comparison: Development vs. Generalization

### Conditions

**Condition 1: Baseline Harness (Original)**
- The agent uses the original, unmodified scaffold
- Same model configuration and inference settings throughout
- Evaluated on both Evaluation cohort A and Evaluation cohort B

**Condition 2: Improved Harness (After Rewriting)**
- The agent uses the scaffold after iterative rewriting
- Model and inference settings remain unchanged
- Evaluated on both Evaluation cohort A and Evaluation cohort B
- (Rewriting occurs only during development cohort; evaluation harness is frozen)

### Primary Outcome
**Pass rate (% of tasks solved)** computed separately for each evaluation cohort and each run.

Formally:
- PassRate_Baseline_CohortA = (# tasks solved / N_CohortA) × 100
- PassRate_Improved_CohortA = (# tasks solved / N_CohortA) × 100
- PassRate_Baseline_CohortB = (# tasks solved / N_CohortB) × 100
- PassRate_Improved_CohortB = (# tasks solved / N_CohortB) × 100

Each is computed across multiple independent runs to quantify variance.

---

## Ablation Studies

### Ablation 1: Isolate Task-Specific Overfitting
**Question:** Did improvements genuinely improve core capabilities, or only fit development cohort idiosyncrasies?

**Design:** 
- Measure the gain separately on Evaluation cohort A and Evaluation cohort B
- Compute: Gain_A = PassRate_Improved_CohortA - PassRate_Baseline_CohortA
- Compute: Gain_B = PassRate_Improved_CohortB - PassRate_Baseline_CohortB

**Interpretation:**
- If Gain_A ≈ Gain_B (within confidence intervals), scaffolds learned domain-general improvements
- If Gain_A >> Gain_B (or Gain_B < 0), scaffolds overfit the development cohort; gains are not real
- This ablation is critical because it directly tests the falsifier criterion (see state.md)

**Evidentiary basis:** 2608.18066 showed that task order and distribution matter substantially, with a 10 percentage point swing (+1.5% to -4.5%) when task order changed. Separate evaluation cohorts operationalize that finding.

### Ablation 2: Variance Amplification Check
**Question:** Does the improved harness amplify variance across runs compared to baseline?

**Design:**
- Compute standard deviation (SD) and best-worst gap for both baseline and improved harness on each cohort
- Baseline SD_A, Improved SD_A; Baseline SD_B, Improved SD_B
- Measure: ΔSD = SD_Improved - SD_Baseline for each cohort

**Interpretation:**
- If ΔSD > 0 consistently, the improved harness is introducing instability (concerning; see 2608.18066)
- If ΔSD ≤ 0, the improved scaffold reduced variance or maintained it
- If variance increases substantially (e.g., >50% relative increase), this is red flag for overfitting to fragile patterns

**Evidentiary basis:** 2608.18066 found variance increased in 71% of cases when self-improving methods were applied, suggesting that apparent improvements can mask underlying instability.

---

## Analysis Plan

### Primary Analysis: Generalization Index

**Step 1: Estimate point estimates and confidence intervals**

For each cohort (A and B) and each run r ∈ {1, 2, 3}, compute:
- PassRate_Improved_A,r
- PassRate_Baseline_A,r
- PassRate_Improved_B,r
- PassRate_Baseline_B,r

**Step 2: Compute per-cohort gains with uncertainty**

Aggregate across runs using a mixed-effects model or simple bootstrap:
- Mean gain for cohort A: μ_gain_A = mean(PassRate_Improved_A,r - PassRate_Baseline_A,r)
- 95% CI for cohort A gain: [CI_lower_A, CI_upper_A]
- Same for cohort B

**Step 3: Construct Generalization Index (GI)**

$$	ext{GI} = rac{\min(\mu\_gain\_A, \mu\_gain\_B)}{\max(\mu\_gain\_A, \mu\_gain\_B)}$$

Interpretation:
- GI = 1.0: Gains are identical across cohorts (perfect generalization)
- GI = 0.8–1.0: Gains are similar; modest evidence of real improvement
- GI = 0.5–0.8: Significant divergence; risk of task-specific overfitting
- GI < 0.5: Strong evidence of overfitting; improvements do not generalize

**Falsification rule:** If GI < 0.7 AND the 95% CIs for cohort A and B gains do not overlap substantially (>50% overlap), **reject** the hypothesis that improvements are real; conclude overfitting.

### Secondary Analysis: Stability & Consistency

**Step 4: Variance signatures**

For each condition (baseline and improved) on each cohort:
- Compute standard deviation across runs: SD_Baseline_A, SD_Improved_A, SD_Baseline_B, SD_Improved_B
- Compute best-worst gap (max run result – min run result)
- Report these as part of transparency; flag if improved harness shows much higher variance

**Step 5: Statistical significance**

Perform paired t-tests (baseline vs. improved) for each cohort separately:
- Test on cohort A: t-test over runs
- Test on cohort B: t-test over runs
- Report t-statistics, p-values, and effect sizes (Cohen's d)

Decision rule: Require p < 0.05 for each cohort to claim significance; if only one cohort reaches p < 0.05, conclude weak evidence.

### Reporting

**Report as a table:**

| Metric | Baseline (A) | Improved (A) | Gain (A) | Baseline (B) | Improved (B) | Gain (B) | GI |
|--------|------|---------|---------|---------|---------|---------|------|
| Mean Pass Rate (%) | — | — | — | — | — | — | — |
| SD (%) | — | — | — | — | — | — | — |
| 95% CI (Gain) | — | — | [—, —] | — | — | [—, —] | — |
| Best-Worst Gap (%) | — | — | — | — | — | — | — |

---

## Outcome Metrics

1. **Primary Metric:** Pass rate (% of task instances solved) on held-out evaluation cohorts
   - Measured separately for Evaluation cohort A and Evaluation cohort B
   - Aggregated across 3 independent runs per condition per cohort

2. **Secondary Metrics:**
   - Standard deviation of pass rate across runs (quantifies variance/instability)
   - Best-worst performance gap across runs (identifies outlier runs)
   - Generalization Index (GI): ratio of smaller to larger cohort gains
   - Per-cohort effect sizes (Cohen's d for baseline vs. improved)

3. **Diagnostic Metrics** (for interpretation, not decision):
   - Task-level success correlation between cohort A and B (for both baseline and improved)
   - Interaction analysis: Are certain task types disproportionately improved or degraded?

---

## Quantifying Uncertainty

### Variance Quantification
- **Across-run variance:** Report SD and 95% CI for each condition × cohort combination across N=3 runs
- **Bootstrap:** For each condition × cohort, resample task instances (with replacement) and re-estimate pass rate; repeat 10,000× to get bootstrap CIs
- Following 2608.18066, also report the best-worst gap; gaps >3% are concerning

### Confidence Intervals
- Use two-sided 95% CIs for all point estimates
- Use Wilson score interval for proportions (pass rate) to avoid edge-case artifacts
- For gains, use bootstrap CIs on the difference of proportions

### Multiple Comparisons Correction
- Two primary tests (cohort A and cohort B)
- Use Bonferroni correction: α_per_test = 0.05 / 2 = 0.025
- Require both tests to pass this threshold for joint significance

### Sample Size Justification
- N ≥ 30 tasks per evaluation cohort ensures reliable proportion estimation (SE ≤ ~2%)
- N=3 runs per condition per cohort balances computational cost against precision; follows 2608.18066 practice
- Total dataset size: ≥60 evaluation tasks × 3 runs × 2 conditions = ≥360 task evaluations

---

## Concrete Resources

### Task Family & Cohorts
- **Assumption:** A domain-specific task family is available with ≥100 task instances
- **Development:** 40 tasks (used for scaffold rewriting, never evaluated)
- **Evaluation cohort A:** 30 tasks (held-out from development, primary generalization test)
- **Evaluation cohort B:** 30 tasks (held-out from development, independent sub-distribution to stress test)

### Computational Resources
- **Model:** GPT-5.5 or GPT-o (unchanged throughout all conditions)
- **Runs:** 3 independent runs per condition per cohort = 3 × 2 × 2 = 12 full evaluations
- **Estimated tokens per evaluation:** Domain-dependent; assume ~100K tokens per task × 30 tasks × 2 conditions × 3 runs = ~18M tokens for the full experimental run (post-development phase)

### Human Oversight
- **Development phase (off-critical path):** Engineers iteratively rewrite scaffold, evaluate diagnostics on development cohort trajectories, decide when to freeze
- **Evaluation phase (critical path):** Automated; graders evaluate task solutions objectively
- **Analysis phase:** One researcher to compute metrics, report results, and interpret Generalization Index

---

## Evidence Alignment

**Design choice: Held-out evaluation cohorts**
- **Evidence:** 2606.05922 (Pan et al., RHO) demonstrated this is feasible and effective. They split SWE-Bench Pro, Terminal-Bench 2, and GAIA-2 into trajectory and test sets, then optimized on trajectories and validated on the held-out test set. This established the gold standard for avoiding ground-truth leakage.

**Design choice: Multiple evaluation cohorts within domain**
- **Evidence:** 2608.18066 (Ye et al.) showed task order induces implicit curricula; improvements of +1.5% collapsed to -4.5% degradation under task shuffling. By splitting evaluation into two independent sub-distributions (cohorts A and B), we force the improved scaffold to generalize across distribution shifts, not just memorize the development pattern.

**Design choice: Multiple runs and variance reporting**
- **Evidence:** 2608.18066 documented that single-run evaluations are unreliable; best-worst gaps reached 10 percentage points. They advocate N=3 runs with variance reporting. This design follows that recommendation.

**Design choice: Falsification threshold (Generalization Index < 0.7)**
- **Evidence:** 2608.18066 showed a 6 percentage point swing (-4.5% vs. +1.5%) under task reordering. We set GI < 0.7 to flag improvements that lose >30% of their magnitude under distribution shift, as this would indicate overfitting rather than real capability gain.

---

## Feasibility & Limitations

### Feasibility
- **Separating development and evaluation cohorts:** Straightforward if ≥100 tasks available
- **Multiple runs:** Computationally feasible (3 runs at ~100K tokens/task)
- **Automated grading:** Assume objective task-success criteria (e.g., tests pass, output matches ground truth)

### Limitations
- **Domain-specificity:** Design is tailored to a single task family; generalization to other domains requires separate experiments
- **Model fixation:** Design assumes model is held constant; if model changes, cannot isolate scaffold contribution
- **Implicit assumptions:** Assumes task family is well-specified and graders are reliable (if unclear task specs, agents may generate inapplicable strategies, per 2608.18066)
- **Sample size:** N=30 per cohort is minimum; larger N would improve precision

---

## Decision Rule

**Claim success (real improvement) if:**
1. Generalization Index GI ≥ 0.7, AND
2. 95% CIs for cohort A and B gains overlap by ≥50%, AND
3. Both cohort A and cohort B show p < 0.025 (Bonferroni-corrected) improvement vs. baseline, AND
4. Improved harness does not amplify variance by >50% relative to baseline

**Claim failure (overfitting/no real gain) if:**
- Any of the above conditions fail

**Unclear/borderline if:**
- GI is 0.65–0.75 with overlapping CIs; recommend extended evaluation or closer post-hoc analysis of failure modes to understand what differed between cohorts

---

## Summary

This design operationalizes the principle that **real harness improvements must generalize beyond the tasks used for development.** By evaluating on two independent task cohorts and requiring consistent gains across both (high GI, overlapping CIs, dual significance), we distinguish genuine capability enhancements from artifacts of task-specific overfitting. The multi-run design and variance reporting follow the methodological lessons of 2608.18066, and the held-out test methodology follows the proven approach of 2606.05922.
