# Experimental Design: Rubric Shift and Rater Agreement

## Research Question
How do you tell whether editing a scoring rubric changed the agreement between human raters and an automatic rater, rather than changing noise?

## Core Hypothesis
A meaningful rubric change will produce a statistically significant and effect-sized shift in agreement metrics (human–automatic rater concordance), distinguishable from random variation in human rating noise.

---

## Main Comparison and Conditions

### Factorial Structure
A **2 × 1 × N** within-subjects design:
- **Rubric condition** (2 levels): Original rubric (A) vs. Edited rubric (B)
- **Rater type** (2 levels, implicit): Human raters (multiple judges) vs. Automatic rater (single deterministic or probabilistic algorithm)
- **Scoring items** (N items, same across both rubric conditions)

### Specific Conditions

**Condition 1: Original Rubric (A)**
- Items scored by human panel (all human raters independently assess all items under rubric A)
- Items scored by automatic rater using rubric A's implementation
- Compute agreement: human–automatic correlation

**Condition 2: Edited Rubric (B)**
- Same items scored by human panel under rubric B
- Same items scored by automatic rater using rubric B's implementation
- Compute agreement: human–automatic correlation

### Key Constraint
The automatic rater must be re-implemented or re-calibrated for rubric B to reflect the rubric change faithfully (not held constant).

---

## Ablation Study

### Ablation 1: Human Agreement Only (No Automatic Rater Reference)
**Rationale**: Distinguish whether a rubric change affects human interrater agreement (signal) independently, or only affects human–automatic agreement due to algorithmic drift.

- Compute interrater reliability (e.g., ICC(3,k) or Krippendorff's α) for human raters in rubric A
- Compute interrater reliability for human raters in rubric B
- Test whether human interrater agreement shifts significantly
- **Interpretation**: If human agreement is stable but human–automatic agreement shifts, the rubric change may have altered automatic rater calibration rather than human judgment clarity. If both shift, the rubric change likely affected judgment itself.

### Ablation 2: Automatic Rater Consistency Check
**Rationale**: Verify that automatic rater produces deterministic outputs (if deterministic) or stable empirical distributions (if stochastic).

- Re-score a random subset of 10–20% of items with the automatic rater using the same rubric variant
- Compute perfect agreement (Cohen's kappa = 1 for deterministic; high ICC for stochastic)
- **Interpretation**: If automatic rater shows drift or noise, attribute some human–automatic disagreement to algorithmic instability rather than rubric clarity.

---

## Concrete Resources

### Human Raters
- **Pool**: [Specify available rater pool—e.g., "4 trained annotators from internal team" or "crowdsourced via Mechanical Turk with qualification test"]
- **Training**: All raters receive written rubric + examples for both rubric A and B
- **Counterbalancing**: Raters score items in random order within each rubric condition to avoid fatigue order effects; condition order (A then B, or B then A) randomized across raters

### Items to Rate
- **Source**: [E.g., "100 held-out items from dataset X" or "benchmark corpus Y"]
- **Criteria**: Representative of the domain; variance in true underlying quality (to avoid floor/ceiling effects)
- **Sample size justification**: Minimum *n* = 50 items to detect medium effect sizes (Cohen's d ≈ 0.5) in agreement shifts with typical reliability and power = 0.80

### Automatic Rater
- **Algorithm**: [E.g., "BERT-based fine-tuned classifier trained on labeled rubric A data" or "rule-based scoring system"]
- **Implementation for rubric A**: [Describe current version, training data, hyperparameters]
- **Implementation for rubric B**: [Describe how the algorithm is adapted—retrained, rules rewritten, prompt adjusted, etc.]
- **Output format**: Numeric score(s) or class label(s) that map to the same scale as human ratings

### Rubric Variants
- **Rubric A**: [Provide text or pointer to current rubric document]
- **Rubric B**: [Provide text or pointer to edited rubric document]
- **Difference**: [Briefly describe the change—e.g., "clarity level descriptor redefined," "weight categories shifted"]

---

## Analysis Plan

### Primary Analysis: Test for Rubric Effect on Human–Automatic Agreement

**Step 1: Compute agreement for each condition**
- Condition A: Pearson *r*, Spearman *ρ*, or ICC(2,1) for human mean rating vs. automatic rating across *n* items
- Condition B: Same metrics for human mean rating vs. automatic rating
- *Justification*: Mean human rating (averaged across raters) is a standard summary; ICC(2,1) is robust to rating scale and allows generalization to a "typical" human rater

**Step 2: Test for difference in agreement**
- **Method 1 (Frequentist)**: Fisher *z*-transform correlations (A and B); compute difference in *z*-values; bootstrap resample to estimate confidence interval and *p*-value for difference
- **Method 2 (Bayesian, more robust to small N)**: Fit Bayesian correlation model separately for each condition; compute posterior difference in correlation; compute 95% highest-density interval (HDI)
- **Criterion**: Reject null (no effect) if confidence interval excludes zero or HDI excludes zero, at *p* < 0.05 or credible posterior probability > 0.95

**Step 3: Quantify effect size**
- Compute Cohen's *h* for proportional change: *h* = 2 × (arcsin√*r*_B − arcsin√*r*_A)
- Interpret: *h* > 0.2 is small; *h* > 0.5 is medium; *h* > 0.8 is large
- *Rationale*: Standardized difference isolates rubric effect from absolute agreement level

### Secondary Analysis: Interrater Reliability (Ablation 1)

- Compute ICC(3, *k*) for each rubric condition (two-way mixed-effects, consistency)
- Test for difference: Use the approach in Koo & Li (2016) or bootstrap
- Interpretation: Difference in human ICC supports hypothesis that rubric change affected human consensus, not just automatic rater alignment

### Tertiary Analysis: Automatic Rater Stability (Ablation 2)

- Retest subset: Cohen's κ or ICC for automatic rater on repeated items
- If κ or ICC < 0.95, note in report; flag as potential confound
- Interpretation: Low consistency suggests automatic rater noise; high consistency supports valid implementation

### Exploratory: Item-Level Effects
- Fit logistic or linear mixed model with item random intercept, rubric condition fixed effect
- Identify whether certain items show large agreement shifts (outliers)
- Interpretation: Rubric changes that improve agreement uniformly across items are stronger evidence of rubric clarity vs. changes that benefit only a few items

---

## Outcome Metrics

### Primary Metric
**Change in Correlation Between Human Mean Rating and Automatic Rating**
- *r*_A: Correlation in Condition A
- *r*_B: Correlation in Condition B
- **Outcome**: *r*_B − *r*_A (if positive, rubric B improved human–automatic agreement)
- **Interpretation**: 
  - Δ*r* > 0.15 with narrow CI: strong evidence rubric change improved interpretability
  - Δ*r* ≈ 0 with wide CI: rubric change had no clear effect (or noise dominated)
  - Δ*r* < −0.15: rubric change may have decreased interpretability

### Secondary Metrics

1. **Human Interrater Reliability (ICC(3,*k*) for Ablation 1)**
   - ICC_A vs. ICC_B: Measures whether human raters agree with each other better under rubric B
   - Large increase in ICC_B suggests rubric B is clearer

2. **Automatic Rater Consistency Coefficient (for Ablation 2)**
   - Cohen's κ or ICC for repeated items: Should be ≥ 0.95 if deterministic
   - If < 0.95, note as a limitation on agreement interpretation

3. **Mean Absolute Error (Human vs. Automatic)**
   - MAE_A = mean |human − automatic| under rubric A
   - MAE_B = mean |human − automatic| under rubric B
   - Complementary to correlation; captures magnitude of disagreement

4. **Agreement Variance by Rater**
   - Compute per-rater correlation with automatic rater in each condition
   - Some raters may align better with automatic rater under one rubric
   - Flag if variance increases (rubric B is less clear to some raters)

---

## Uncertainty Quantification

### Confidence Intervals
- **Bootstrap resampling** (1000 or 10,000 iterations, sample items with replacement):
  - Resample items; recompute Pearson *r* for each resample
  - 95% CI = [2.5th, 97.5th percentile] of bootstrap distribution
  - **Advantage**: Makes no distributional assumptions; valid for small *n* and non-normal data

### Statistical Significance
- **Permutation test**: Under null (no rubric effect), shuffle rubric labels; recompute Δ*r*; compare observed Δ*r* to permutation null distribution
- **Rationale**: Valid without normality; does not require large sample sizes; directly tests null of no difference
- **α = 0.05**: One-tailed (predict direction of effect) or two-tailed (agnostic)

### Bayesian Credible Intervals
- Fit Bayesian correlation models using priors on Fisher-transformed correlations
- Report 95% HDI for Δ*r*
- **Advantage**: Directly quantifies probability that Δ*r* > 0 (or > some minimum effect size), which is often the question of interest

### Sensitivity Analysis
- **Robustness to rater dropout**: Refit primary analysis excluding each rater one at a time (leave-one-rater-out); check whether Δ*r* and CI remain stable
- **Robustness to item outliers**: Remove items with extreme automatic rater scores or extreme human–automatic disagreement; recompute Δ*r*; compare to main result
- **Robustness to correlation choice**: Compute Δ*r* using Pearson, Spearman, and Kendall tau; check consistency

### Sample Size and Power
- **Planned precision**: For a hypothesized Δ*r* = 0.15 (small to medium effect), with α = 0.05 and correlation noise typical in annotation tasks (r ≈ 0.6–0.8), *n* ≈ 50–100 items provides 80% power
- **Interim monitoring**: If feasible, assess CI width after 50 items; continue to *n* = 100 if CI is wide (>±0.20)

---

## Concrete Workflow and Deliverables

### Pre-registration
- Write and register this design on [OSF Registries](https://osf.io/registries) or [Aspredicted.org](https://www.aspredicted.org) before collecting human ratings
- Locks analysis plan; reduces bias from post-hoc changes

### Data Collection
1. Recruit and train human raters (instructions provided separately)
2. Assign items and conditions (randomized order)
3. Collect human ratings in structured format (CSV: item_id, rater_id, rubric_version, score)
4. Run automatic rater on same items (output: item_id, rubric_version, auto_score)
5. Repeat test subset for automatic rater consistency (Ablation 2)

### Analysis Output
1. **Summary statistics table**: Mean, SD, ICC, Pearson *r* for each condition
2. **Primary result visualization**: Scatter plot (human vs. automatic) for Condition A and B side-by-side; overlay linear fit and CI
3. **Difference plot**: Δ*r* with 95% bootstrap CI and permutation *p*-value
4. **Ablation results**: ICC(3,*k*) comparison and automatic rater consistency coefficient
5. **Sensitivity analyses**: Robustness to rater dropout, item outliers, correlation metric choice
6. **Interpretation table**: Effect size, interpretation, and caveats

### Reporting
- Manuscript follows [STROBE](https://www.strobe-statement.org/) or domain reporting guidelines
- Report Δ*r* with 95% CI, permutation *p*-value, and effect size *h*
- Discuss whether observed Δ*r* is practically meaningful (depends on domain; typically >0.15 is noticeable)

---

## Assumptions and Limitations

### Assumptions
1. **Human raters can apply rubric consistently**: Training and clear rubric text assumed sufficient
2. **Automatic rater faithfully implements rubric logic**: Implementation quality not independently validated; see Ablation 2
3. **Same items in both conditions**: Carry-over effects possible (e.g., raters remember prior scores); mitigated by randomization and sufficient time between conditions
4. **Items are representative**: Generalizability depends on sample composition

### Limitations and Mitigations
- **Small *n* of raters** (common in annotation): Use ICC(3,*k*) to generalize to population; bootstrap to estimate uncertainty
- **Potential rater drift**: Randomize item order and distribute across raters; use mixed-effects model to account for rater effects
- **Automatic rater bias**: If algorithm is deterministic and well-tested, bias is systematic but not random; report separately
- **Rubric complexity**: Very complex rubrics may produce low agreement regardless; consider piloting on a small subset

---

## Example Result Interpretation

*(Illustrative; no actual numbers reported per task rules)*

**Hypothetical Outcome**: Δ*r* = +0.18 [95% CI: 0.05 to 0.31], permutation *p* = 0.012, effect size *h* = 0.37.

**Interpretation**: 
- Rubric B increased human–automatic agreement by ~0.18 correlation points (small to medium effect).
- Effect is significant at *p* < 0.05 and CI excludes zero, providing evidence against null of no effect.
- Ablation 1 (human ICC): If ICC_B > ICC_A, rubric B is also clearer to humans themselves, supporting rubric improvement hypothesis.
- Ablation 2 (automatic consistency): If Cohen's κ ≥ 0.95, automatic rater is stable; effect is genuine rubric-level improvement, not algorithmic drift.

**Conclusion**: Rubric B meaningfully improved interpretability relative to Rubric A, distinguishable from noise.

---

## References

- Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine*, 15(2), 155–163.
- Krippendorff, K. (2011). *Computing Krippendorff's Alpha-Reliability*. University of Pennsylvania.
- Perkins, R., Gupta, N., Tong, Y. (2020). Pitfalls of Agreement: A case study of inter-rater disagreement in peer assessment. *Computers & Education*, 148, 103805.
