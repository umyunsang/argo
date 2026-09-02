# Experimental Design: Detecting Rubric-Driven Agreement Changes vs. Noise

**Decision ID**: K3-rubric-shift-agreement-signal-v1

---

## 1. Research Question & Hypothesis

**Primary question**: Does the revised rubric variant produce a statistically meaningful 
increase in human-automatic rater agreement compared to the baseline rubric, or is the 
observed agreement change attributable to random noise in a small sample?

**Hypothesis**: The revised rubric improves clarity of scoring criteria in a way that 
increases agreement between human judges and the automatic system beyond what would 
occur by random chance.

---

## 2. Sampling Frame

**Population**: Scoreable items (documents, essays, media segments, or other scorable units) 
that can be independently rated by both human raters and an automatic scoring system.

**Unit of analysis**: (item, human_rater_1, human_rater_2, automatic_rater) tuples, 
each scored under both the baseline rubric variant and the revised rubric variant.

**Concrete sampling frame**:
- A repository of items (n ≥ 20) previously scored under the **baseline rubric** by:
  - Two independent human raters (human_1, human_2)
  - One automatic system instance
- These same items are re-scored under the **revised rubric** by:
  - The same automatic system (deterministically or stochastically, depending on system)
  - A subset of the original human raters (likely 2–4 individuals due to budget constraints)
- Human raters who re-score under the revised rubric receive brief training on the 
  revised rubric to ensure understanding, but are otherwise naive to their prior scores 
  to minimize bias.

**Justification**: Using the same items and mostly the same raters reduces between-item 
and between-rater variance, increasing power to detect rubric effects within a limited sample.

---

## 3. Main Comparison: Conditions & Design

### 3.1 Conditions

**Condition A (Baseline)**: Items scored under baseline rubric
- Human raters (H1, H2) scored items under baseline rubric variant
- Automatic system (AS) scored items under baseline rubric variant
- Outcome: Baseline human-automatic agreement (e.g., overlap, kappa, correlation)

**Condition B (Revised)**: Same items scored under revised rubric
- Human raters (subset of {H1, H2, …}) score items under revised rubric variant
- Automatic system (same instance) scores items under revised rubric variant
- Outcome: Revised human-automatic agreement

**Primary contrast**: 
$$\Delta_{	ext{agreement}} = 	ext{Agreement}_{B} - 	ext{Agreement}_{A}$$

A *positive* contrast suggests the revised rubric improves human-automatic alignment.

### 3.2 Design Structure

**Paired repeated-measures design**:
- Within each item, compute agreement under both rubric variants
- Account for the dependence of measurements (same item, same automatic system, overlapping human raters)
- Use paired statistical tests to increase power

**Practical workflow**:
1. Retrieve all items with complete baseline scores (human_1, human_2, automatic)
2. Have selected human raters re-score all items under revised rubric (single pass, 
   with rubric training)
3. Re-score all items with automatic system under revised rubric
4. Compute agreement metrics for both conditions
5. Compare agreement distributions and test for meaningful shift

---

## 4. Ablation: Isolating Rubric Effect from Rater Adaptation

### 4.1 Design

**Ablation condition (C)**: Revised rubric, *baseline* rater training/context

This condition tests whether agreement improvement is due to the revised rubric 
itself or merely to human raters adapting to the rubric during a second scoring pass.

- Same human raters and automatic system as Condition B (revised rubric scores)
- BUT: Before re-scoring, briefly remind raters of the baseline rubric criteria 
  (without explicit retraining on the revised rubric)
- Record how often raters refer to baseline vs. revised rubric materials

**Interpretation**:
- If $\Delta_{	ext{agreement}}^{B-C} pprox 0$ (Revised ≈ Revised-with-baseline-training), 
  then agreement improvement is driven by practice/adaptation, not the rubric change.
- If $\Delta_{	ext{agreement}}^{B-C}$ is substantial (Revised >> Revised-with-baseline-training), 
  the rubric itself (not rater adaptation) drives the signal.

**Practical constraint**: This ablation requires at least one subset of raters to score 
items twice under slightly different training regimens, which increases cost and risks 
practice effects. A simpler variant: randomly split items in half; use revised training 
for one half, baseline-reminder for the other; compare agreement by group.

---

## 5. Analysis Plan

### 5.1 Outcome Metrics

**Primary metrics** (choose one or more based on rubric structure):

1. **Overlap rate**: Proportion of items where human and automatic scores agree exactly 
   (or within a tolerance band, e.g., ±0.5 on a scale)
   - Computed per condition; paired difference tested with McNemar's test or binomial test

2. **Cohen's kappa (human-automatic)**: Accounts for chance agreement
   - Compute per condition; test difference via bootstrap confidence interval

3. **Correlation (Pearson or Spearman)**: If scores are continuous
   - Compare correlation coefficients via Fisher z-transformation

4. **Rank agreement**: Proportion of item pairs with human and automatic scores 
   in the same rank quartile (more robust to scale differences)
   - Compute per condition; test difference via permutation test

**Selection criterion**: Use metrics appropriate to the rubric's score structure 
(categorical vs. continuous, ordinal vs. ratio). If unsure, compute all and report 
the most conservative (i.e., largest p-value or confidence interval).

### 5.2 Null Distribution & Uncertainty Quantification

**Null hypothesis**: The revised rubric does not change human-automatic agreement; 
any observed change is due to random noise.

**Method: Permutation-based bootstrap for paired data**

1. **Baseline agreement null**: 
   - Compute baseline human-human agreement as a reference null distribution 
     (raters can disagree; any human-automatic agreement above human-human agreement 
     is already "noisy").
   - Bootstrap the baseline agreement by resampling items with replacement (1,000–10,000 iterations).
   - Compute 95% confidence interval for baseline agreement.

2. **Revised agreement null**:
   - Under the null (no rubric effect), the revised agreement should have a similar 
     distribution to baseline (modulo sampling variability).
   - Permutation test: Shuffle the rubric labels (baseline/revised) within paired items 
     and recompute the agreement difference 1,000 times.
   - Compute the permutation p-value: proportion of permutations where 
     $|\Delta_{	ext{perm}}| \geq |\Delta_{	ext{observed}}|$.

3. **Bootstrap confidence interval**:
   - Resample items with replacement; compute agreement difference for each sample.
   - Report 95% CI for $\Delta_{	ext{agreement}}$.
   - If CI excludes zero, reject null at α = 0.05; if CI includes zero, fail to reject.

### 5.3 Effect Size & Meaningfulness

**Minimal meaningful effect**:
- Determine a priori (e.g., "a 5 percentage point increase in overlap rate is meaningful").
- If available, base on prior literature or domain expert judgment.
- If CI for effect is small (e.g., [0.01, 0.04]) even if excluding zero, result is 
  statistically significant but not practically meaningful.

### 5.4 Subgroup Analysis (Optional)

- **By item difficulty** (e.g., baseline human-human agreement): Does rubric help 
  more on ambiguous items?
- **By automatic system confidence** (if available): Does rubric help more on 
  high-confidence or low-confidence predictions?
- Report these exploratory; do not correct for multiple comparisons (acknowledge as post-hoc).

---

## 6. Resources

### 6.1 Data / Material Resources

1. **Baseline item repository**: A set of n ≥ 20 items with complete scores 
   (human_1, human_2, automatic, baseline rubric)
   - Source: Prior scoring effort or annotated corpus
   - Format: Structured data (CSV, JSON, database) with item ID, text/media, and scores
   - Access: Must be retrievable and re-scorable by human raters

2. **Automatic scoring system**: A trained model or rule-based system capable of 
   scoring items under both rubric variants
   - Requirement: Deterministic (or reproducible stochastic) scoring
   - Input: Item + rubric variant
   - Output: Score or confidence values

3. **Baseline and revised rubric documents**:
   - Baseline: Original rubric variant (assumed to exist)
   - Revised: Edited rubric variant (scope of changes to be documented)
   - Format: Text or structured rubric (e.g., scoring grid with descriptors)

### 6.2 Human Resources

1. **Human raters**: n_h = 2–4 raters for re-scoring under revised rubric
   - Recruitment: From the pool of baseline raters if available; otherwise, 
     new raters trained on both rubrics
   - Training: ~30–60 min briefing on revised rubric + scoring system; 
     practice scoring 2–3 items
   - Time commitment: ~2–4 hours per rater (depends on item complexity and count)
   - Cost: Varies (volunteers, paid annotators, or staff time)

2. **Expert (optional)**: A rubric domain expert to assess whether changes are 
   substantial and to validate ablation design choices

### 6.3 Computational Resources

- Statistical software: Python (scipy, statsmodels) or R (e.g., boot, irr packages)
- Minimum: Laptop; no HPC needed for n ≤ 100 items
- Time: ~2–4 hours for analysis (scoring excluded)

---

## 7. Conditions for Valid Inference

### 7.1 Assumptions

1. **Independence of items** (mostly): Items are not redundant; scoring one item does not strongly inform another. If items are clustered (e.g., multiple essays from the same student), account for item clustering in bootstrap/permutation procedure.

2. **Rater consistency**: Human raters follow the rubric consistently. (Monitored by comparing human-human agreement.)

3. **Automatic system stability**: The automatic system produces reproducible (or statistically consistent) scores under the revised rubric.

4. **No confounding interventions**: Raters do not receive additional training, feedback, or context between baseline and revised scoring that could artificially inflate agreement.

### 7.2 Threats to Validity

| Threat | Mitigation |
|--------|-----------|
| **Practice effects** | Raters score same items twice → may learn scoring patterns. Mitigate: Ablation condition (revised rubric with baseline training cues) isolates learning effects. |
| **Rater attrition** | Some baseline raters unavailable for re-scoring. Mitigate: Recruit new raters if needed; track rater identity in analysis to account for rater-level variance. |
| **Automatic system drift** | System behaves differently under revised rubric (e.g., software update, model retrain). Mitigate: Version control automatic system; if retrained, report training data and date. |
| **Rubric ambiguity** | Revised rubric is also poorly written. Mitigate: Have domain expert review revised rubric for clarity and logical consistency before use. |
| **Small sample (n ≤ 20)** | Low power to detect small effects; high variance. Mitigate: Report effect size with 95% CI, not just p-value. Use permutation tests (more conservative than t-tests for small n). |

---

## 8. Outcome Metrics & Quantifying Uncertainty

### 8.1 Reported Metrics (for each condition, baseline & revised)

| Metric | Definition | Uncertainty Quantifier |
|--------|-----------|------------------------|
| Overlap rate | % items where human and automatic agree | 95% bootstrap CI |
| Cohen's kappa | Chance-corrected agreement | 95% bootstrap CI + p-value (permutation test) |
| Mean absolute error (MAE) | Mean \|human – automatic\| score difference | 95% bootstrap CI |
| Effect size (Cohen's d or similar) | Standardized difference in agreement | 95% bootstrap CI |

### 8.2 Primary Result Summary

Report the main finding as:

$$\Delta_{	ext{agreement}} = 	ext{Agreement}_{	ext{revised}} - 	ext{Agreement}_{	ext{baseline}}$$

With 95% CI and permutation p-value. Interpret as:
- **Positive, CI excludes zero**: Revised rubric improves agreement (reject null)
- **Positive, CI includes zero**: Weak evidence for improvement; result inconclusive
- **Negative, CI excludes zero**: Revised rubric worsens agreement (rubric change is problematic)
- **Negative, CI includes zero**: No evidence for degradation

### 8.3 Ablation Result

Report $\Delta_{	ext{agreement}}^{B-C}$ (Revised vs. Revised-with-baseline-training):
- **Large positive**: Rubric change itself drives improvement (not just rater adaptation)
- **Near zero**: Rater adaptation explains the improvement; rubric may not be the source

---

## 9. Workflow & Timeline

1. **Preparation (1–2 weeks)**:
   - Assemble baseline item repository
   - Document baseline and revised rubrics
   - Recruit / brief human raters
   - Set up automatic system for revised rubric scoring

2. **Data collection (1–2 weeks)**:
   - Human raters score items under revised rubric
   - Automatic system scores items under revised rubric
   - Collect metadata (time, confidence, ambiguity flags)

3. **Analysis (1 week)**:
   - Compute agreement metrics for both conditions
   - Run permutation tests and bootstrap CI
   - Generate ablation results
   - Produce summary report with figures

4. **Reporting (1 week)**:
   - Write up findings, interpretation, and limitations
   - Document all design deviations and post-hoc decisions

---

## 10. Decision Rule & Interpretation

**Successful design outcome** (designs can distinguish signal from noise if):
- The 95% CI for $\Delta_{	ext{agreement}}$ is narrow (e.g., width < 10 percentage points) 
  AND excludes zero OR clearly includes zero
- The permutation p-value is interpretable (p < 0.05 for signal, p > 0.20 for noise)
- The ablation result clarifies whether rubric or rater adaptation drove the change

**Design failure** (cannot distinguish signal from noise if):
- The 95% CI is very wide (e.g., width > 20 percentage points)
- Permutation p-value is near 0.05 (inconclusive border)
- Ablation is uninterpretable (e.g., too few items in ablation arm)

**In case of design failure**: Recommend collecting more items (n → 40+) or 
simplifying the rubric dimensions to increase signal-to-noise ratio.

---

## 11. References to Sampling Frame

This design **directly operationalizes the sampling_frame** defined in the research state:

> **Sampling frame**: A set of items scored in prior work under the baseline rubric 
> by two independent human raters and one automatic system. The *same items* 
> are re-scored by the same automatic system under the revised rubric. 
> Human raters re-score under the revised rubric only (to avoid practice effects).

Each of the main comparison conditions (A: baseline, B: revised) and the ablation 
condition (C: revised-with-baseline-training) draws from this same sampling frame. 
The unit of analysis is the (item, human, automatic) tuple, and the design ensures 
that:

- **Items are the same across conditions** (paired design, reducing noise)
- **Automatic system is the same instance** (controls for system variance)
- **Human raters partially overlap** (balances control with practical constraints)
- **All conditions respect the population definition** (scoreable items independently 
  ratable by humans and automatic systems)

By grounding the design in this concrete sampling frame, we ensure that any detected 
agreement change is attributable to the rubric variant, not to differences in items, 
raters, or the automatic system.

---

## Appendix: Example Analysis Pseudocode

```
# Pseudocode for primary analysis

for iteration in 1:10000:
    # Bootstrap resample items with replacement
    sample_items = resample(items, size=n, replace=True)
    
    # Compute agreement for each condition
    agreement_baseline = compute_overlap(sample_items, rubric='baseline')
    agreement_revised = compute_overlap(sample_items, rubric='revised')
    
    # Store difference
    delta_samples[iteration] = agreement_revised - agreement_baseline

# Compute CI and p-value
ci_lower = quantile(delta_samples, 0.025)
ci_upper = quantile(delta_samples, 0.975)
p_value = mean(abs(delta_samples) >= abs(delta_observed))

# Report result
print(f"Δ Agreement = {delta_observed:.3f}, 95% CI = [{ci_lower:.3f}, {ci_upper:.3f}], p = {p_value:.3f}")
```

---

**End of Design Document**
