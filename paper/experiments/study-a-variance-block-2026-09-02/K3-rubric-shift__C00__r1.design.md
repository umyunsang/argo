# Experimental Design: K3-Rubric-Shift

## 1. Research Question

**Primary**: Does editing a scoring rubric produce a **genuine change in agreement** between human raters and an automatic rater, or does the observed change reflect noise?

**Distinction**: This design assumes that rubric edits can affect agreement through two mechanisms:
- **Substantive**: The rubric clarification changes what human and automatic raters actually converge on (reduces ambiguity, realigns incentives)
- **Noise**: Random measurement variation or sampling fluctuation in the limited human-rating pool masks or exaggerates the true effect

## 2. Main Comparison: Two-Condition Within-Items Design

### Condition A: Original Rubric (Baseline)
- All items rated by human rater pool under original rubric
- All items scored by automatic rater under original rubric

### Condition B: Edited Rubric (Treatment)
- **Same items** rated by human rater pool under edited rubric
- **Same items** scored by automatic rater under edited rubric

### Key constraint: Limited pool of humans
- Human raters must rate the same item set twice (once per rubric)
- This is within-items; the human and automatic raters are paired per item

### Blocking / sequencing:
- Items are presented in random order within each rubric condition
- Rubric A and Rubric B trials are separated by at least one week to minimize carryover and memory effects
- Rater identity is recorded for each rating to detect drift or fatigue

## 3. Primary Outcome Metric: Inter-Rater Agreement (Human–Auto)

### Definition
For each rubric variant, compute **Krippendorff's α** (ordinal variant if scores are ordinal; interval if continuous) between:
- **Human ratings** (aggregate or per-rater, see analysis plan)
- **Automatic rater scores**

Rationale: Krippendorff's α is robust to missing data, accounts for chance agreement, and handles small sample sizes better than Cohen's κ or Fleiss' κ.

### Result: Two agreement coefficients
- α_original = agreement under original rubric
- α_edited = agreement under edited rubric

**Effect size**: Δα = α_edited − α_original

## 4. Uncertainty Quantification: Permutation Test

To distinguish **genuine shifts from noise**, use a permutation test:

### Null hypothesis
The observed difference Δα arises from random reassignment of rubric labels to ratings, not from a property of the rubric.

### Procedure
1. Compute Δα on the observed data (α_edited − α_original)
2. Randomly permute the rubric assignments (i.e., randomly relabel each item's ratings as "original" or "edited")
3. Recompute Δα on each permuted dataset (10,000 permutations)
4. Construct the null distribution of Δα_permuted
5. Compare observed Δα to this distribution; two-tailed p-value = proportion of |Δα_permuted| ≥ |Δα_observed|

### Interpretation
- **p < 0.05**: The observed agreement shift is unlikely under random rubric assignment; supports genuine rubric effect
- **p ≥ 0.05**: The observed shift is consistent with noise; insufficient evidence for rubric effect

### Confidence interval on Δα
Bootstrap the agreement difference:
1. Resample items with replacement (stratified by difficulty or automatic-rater confidence, if available)
2. Recompute α_original, α_edited, and Δα for each resampled dataset (10,000 samples)
3. Report the 95% CI as the 2.5th and 97.5th percentiles of the bootstrap Δα distribution

## 5. Ablation Study: Rubric Component Sensitivity

To test which aspects of the rubric edit drove any observed change, implement a **minimal-change ablation**.

### Design
Create **Rubric C: Partial Edit**
- Include only one of the key changes from rubric A → B (e.g., clarification of a single criterion, removal of one ambiguous term, addition of one anchor example)
- Rate all items under Rubric C with the same human and automatic raters

### Analysis
Compute α_partial for Rubric C, then compare:
- α_partial vs α_original: Did the minimal change alone shift agreement?
- α_partial vs α_edited: Is the full edit effect larger than the partial effect?

### Interpretation
If α_edited >> α_partial, the full rubric contains interacting changes that matter.
If α_partial ≈ α_edited, one component dominates the agreement change.

## 6. Concrete Resources Required

### Human raters
- **Count**: 3–5 raters (limited pool as specified)
- **Selection**: Domain experts or trained annotators with rubric fluency
- **Documentation**: Record each rater's background, training date, and any guidance drift between rubric conditions

### Items
- **Count**: 50–100 items (balanced across difficulty if automatic-rater scores vary)
- **Domain**: Specified by the scoring task (e.g., essay quality, classification, translation)
- **Provenance**: Must be the same items rated under both rubrics (within-items constraint)

### Automatic rater
- **Implementation**: A single, deterministic algorithm or model (version-pinned)
- **Documentation**: Model name, version, hyperparameters, and date of last update
- **Reproducibility**: All inputs (item texts, preprocessing) must be preserved

### Rubric artifacts
- **Rubric A (original)**: Plain-text or structured document of all criteria, scoring scales, and anchor examples
- **Rubric B (edited)**: Clearly marked diff against Rubric A (e.g., strikethrough and bold for changes)
- **Rubric C (partial edit)**: Specification of which single change was applied

### Ancillary data
- Per-item automatic-rater confidence or uncertainty (if available)
- Difficulty ratings or metadata (e.g., item word count, category)
- Rater training logs (date, duration, feedback received)

## 7. Analysis Plan

### Primary analysis
1. **Compute agreement**:
   - For each rubric, compute Krippendorff's α (human vs. automatic rater)
   - Report both raw agreement and chance-adjusted agreement

2. **Test effect**:
   - Compute Δα = α_edited − α_original
   - Run permutation test (10,000 permutations, two-tailed, α = 0.05)
   - Report p-value and 95% CI on Δα via bootstrap

3. **Effect size interpretation**:
   - Report Δα in original units (e.g., α difference of 0.10)
   - Qualify as negligible (|Δα| < 0.05), small (0.05–0.15), medium (0.15–0.30), large (> 0.30)
   - Interpretation depends on domain conventions and practical significance threshold

### Secondary analysis (ablation)
1. Compute α_partial for Rubric C
2. Compare α_partial to α_original and α_edited with permutation tests
3. Assess whether the partial change explains most of the Δα from full edit

### Sensitivity analysis
1. **Per-rater agreement**: Compute Krippendorff's α separately for each human rater vs. automatic rater; report the range and mean
2. **Item-wise analysis**: For each item, compute agreement change Δα_item and identify items that drive the overall effect
3. **Exclude-one-rater**: Recompute all tests excluding each human rater one at a time; check whether results are robust to any single rater

### Handling missing data
- If a rater is absent for some items, use pairwise deletion within Krippendorff's α
- Report the number of items with complete ratings and the proportion of missing data

## 8. Outcome Metrics Summary

| Metric | Definition | Reported as |
|--------|-----------|-------------|
| α_original | Krippendorff's α, original rubric | Point estimate + 95% CI |
| α_edited | Krippendorff's α, edited rubric | Point estimate + 95% CI |
| Δα | α_edited − α_original | Point estimate + 95% CI + permutation p-value |
| α_partial | Krippendorff's α, partial edit rubric | Point estimate + 95% CI |
| p-value (permutation) | Two-tailed, 10,000 permutations | p-value |
| p-value (ablation) | Permutation test for α_partial vs α_original | p-value |
| Range of per-rater Δα | Agreement shift by individual rater | Min, mean, max, SD |

## 9. Decision Rule for Rubric Adoption

**Adopt the edited rubric if**:
1. Δα ≥ [practical threshold, e.g., 0.05] AND
2. Permutation p-value < 0.05 AND
3. 95% CI on Δα does not include zero

**Do not adopt if**:
- p-value ≥ 0.05, indicating the shift is consistent with noise
- 95% CI spans zero, indicating uncertainty that overlaps the null effect
- Ablation shows the effect is driven by a single ambiguous or arbitrary rubric change

**Consider conditional adoption if**:
- Δα is positive and practically meaningful but p ≥ 0.05 (insufficient power; recommend collecting more ratings)
- Per-rater results are inconsistent (indicates a rater-specific effect; investigate training or rubric fit)

## 10. Statistical Assumptions and Limitations

### Assumptions
1. **Independence**: Ratings are independent conditional on item and rater (no collusion, separate raters)
2. **Exchangeability under permutation**: Under the null, all permutations of rubric labels are equally likely
3. **Ordinal or interval data**: Rubric scores are at least ordinal (required for Krippendorff's α)
4. **Stationary raters**: Rater skill and consistency do not systematically drift between rubric conditions (mitigated by randomized order and temporal separation)

### Limitations
1. **Small sample**: With 3–5 human raters and 50–100 items, power is limited (typically 60–75% for medium effects)
   - **Mitigation**: Use permutation test (more robust to small samples than asymptotic tests); report CIs and effect size, not only p-value
2. **Single automatic rater**: Results generalize only to the specific algorithm tested
   - **Mitigation**: Test alternative algorithms as a separate robustness check (future work)
3. **No ground truth**: Agreement with an automatic rater is not the same as accuracy; agreement may be high but both raters wrong
   - **Mitigation**: If ground truth labels exist, also report human–ground and auto–ground agreement separately
4. **Carryover**: Even with temporal separation, raters may remember prior rubrics and bias later ratings
   - **Mitigation**: Mask rubric identity and randomize item order; ask raters to re-read the rubric before each condition

## 11. Reporting Checklist

- [ ] Rubric A and B are included as appendices, with diff highlighted
- [ ] Human rater demographics and training dates are reported
- [ ] Automatic rater algorithm version and hyperparameters are documented
- [ ] Number of items and per-item completion rates are reported
- [ ] Krippendorff's α values with 95% CIs for all three rubrics
- [ ] Permutation test p-values and effect sizes (Δα)
- [ ] Bootstrap CIs on Δα
- [ ] Per-rater agreement breakdown (range and mean)
- [ ] Item-wise agreement changes (identify outliers)
- [ ] Ablation test results
- [ ] Sensitivity analysis (exclude-one-rater results)
- [ ] Any missing data patterns and handling approach
- [ ] Plain-language interpretation: Does the rubric change shift agreement, or is the observed change consistent with noise?

---

## Summary

This design tests a **specific, falsifiable claim**: whether editing a rubric genuinely shifts human–automatic rater agreement or produces noise-like variation. By using:
- **Permutation tests** to quantify uncertainty under the null
- **Bootstrap CIs** to characterize the observed effect
- **Ablation** to isolate which rubric components matter
- **Sensitivity checks** to confirm robustness across raters

the design separates true rubric effects from sampling noise. The decision rule ensures adoption or rejection is grounded in statistical evidence and practical significance, not point estimates alone.
