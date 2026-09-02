# Experimental Design: Rubric-Shift Detection in Human-Automatic Rater Agreement

## Research Question
How do you tell whether editing a scoring rubric changed the agreement between human raters and an automatic rater, rather than changing noise?

## Design Overview

This design distinguishes a genuine shift in human-automatic rater agreement (a signal) from uncontrolled drift in either the human rater or the automatic rater (noise). The core strategy is:
1. Score the same items under both rubric variants
2. Apply rater-effects decomposition to separate severity shifts from correlation shifts
3. Use a paired resolution framework to determine whether observed agreement differences exceed the noise ceiling
4. Include explicit variance-component ablations to isolate the source of change

---

## Main Comparison: Paired Rubric Contrast

### Condition A: Original Rubric
- Human rater: scores N items on the original rubric
- Automatic rater: scores the same N items on the original rubric
- Outcome: pair-wise agreement (Spearman correlation, quadratic weighted kappa, or per-item disagreement count, depending on scale type)

### Condition B: Revised Rubric
- Human rater: scores the same N items on the revised rubric
- Automatic rater: scores the same N items on the revised rubric (using identical prompt/model)
- Outcome: pair-wise agreement on revised rubric

### Why This Is Paired
Both the human and automatic rater evaluate the identical set of items twice (once per rubric). This pairing exploits the fact that item difficulty is fixed across conditions, reducing variance and increasing power to detect a rubric effect (per evidence from 2605.30315 on paired vs. unpaired test resolution).

---

## Outcome Metrics: Three Layers

### Layer 1: Agreement Correlation (Primary)
Report the **paired correlation of human and automatic rater scores** within each rubric condition:
- Spearman ρ or Pearson r (if scores are interval/normal)
- Quadratic Weighted Kappa (if scores are ordinal, per 2608.29517 precedent)
- Confidence intervals via bootstrap or analytical standard error

**Null Hypothesis (H0):** The observed difference in correlation between Rubric A and Rubric B is within the noise band of repeated scoring of the same item pool.

### Layer 2: Rater Severity Shift (Secondary)
Report the **average score shift for each rater** between rubrics:
- Human rater mean change: $ar{x}_{	ext{human, B}} - ar{x}_{	ext{human, A}}$
- Automatic rater mean change: $ar{x}_{	ext{auto, B}} - ar{x}_{	ext{auto, A}}$
- Estimate whether the shifts are aligned (both raters stricter, or both more lenient) or anti-correlated (one stricter, one more lenient)

**Justification:** Rubric edits can shift both raters' severity without changing their agreement (e.g., both become stricter, but maintain the same pairing rank). This metric distinguishes a severity-only shift from an alignment shift.

### Layer 3: Interaction: Item-Level Disagreement Patterns (Tertiary)
Report the **distribution of item-level disagreement**:
- Per-item signed error: $(x_{	ext{human}} - x_{	ext{auto}})$ within each rubric
- Item-by-rubric heatmap: which items show larger disagreement under which rubric?
- Permutation test: do disagreement-prone items stay the same across rubrics, or does the disagreement pattern shift?

**Justification:** If the rubric rewording changes the items that the automatic rater misunderstands (e.g., by clarifying a criterion that it previously missed), the set of high-disagreement items should shift. If the shift is arbitrary (pure noise), the disagreement patterns should be uncorrelated between rubrics.

---

## Ablations

### Ablation 1: Automatic Rater Determinism
**Question:** How much of the within-rubric noise comes from the automatic rater's non-determinism, vs. genuine rating disagreement?

**Design:**
- Condition A1: Score each of N items **k times** (k ≥ 3) with the automatic rater on the original rubric, holding the human rater fixed.
- Compute the within-prompt variance component (variance across k repeated calls to the same automatic rater on the same item).
- Condition B1: Repeat on the revised rubric.

**Analysis:** Estimate the intraclass correlation (ICC) for the automatic rater's k-fold resampling (per 2607.13304 generalizability-theory framework). If the ICC is low (< 0.70), the automatic rater's non-determinism is a major noise source, and observed agreement shifts must be discounted by the noise ceiling.

**Minimum Resources:** k = 3 repeats × N items × 2 rubrics = 6N automatic rater calls. (If k = 5, as per convention in 2607.13304, then 10N calls.)

### Ablation 2: Human Rater Drift
**Question:** Does the human rater's scoring change between the two rating sessions (Rubric A → Rubric B), and does this drift correlate with the automatic rater's shift?

**Design:**
- Insert a **re-test set of R items** (R ≤ N) that the human rater scores twice: once under Rubric A and once under Rubric B, but separated by other items to minimize carry-over.
- Compute the human rater's retest correlation on this R-item subset.
- Compute whether the human rater's severity shift on R overlaps with the shift on the full set.

**Analysis:** If the retest ICC < 0.80, the human rater is drifting or the rubric change induced genuine inconsistency in the human's interpretation. This drift is confounded with the rubric effect and must be reported separately.

**Minimum Resources:** R = 10–20 items, each rated twice by the human rater.

### Ablation 3: Rubric Wording Stability
**Question:** Is the observed agreement shift due to the new rubric wording, or due to the human rater or automatic rater interpreting the words inconsistently?

**Design:**
- Condition C: Paraphrase the revised rubric into an **alternate wording** that preserves the intended meaning (e.g., rephrase criteria using different vocabulary, reorder examples, but keep the scoring levels identical).
- Have both human and automatic rater score a subset of M items (M ≤ N) under Rubric B (original revised) and the paraphrased variant.
- Compute the correlation of agreement under the two wordings.

**Analysis:** If agreement differs substantially between the two paraphrased versions, the effect is not stable and may reflect reading-comprehension noise rather than a genuine rubric improvement. If agreement is stable (ρ > 0.85), the effect is robust to wording variation.

**Minimum Resources:** M = 10–20 items × 2 human and 1 automatic rater × 2 rubric wordings.

---

## Statistical Analysis Plan

### Hypothesis Test: Paired Resolution Diagnostic
Apply the **paired resolution framework** from evidence 2605.30315 to test whether the observed agreement difference is statistically resolvable.

**Test Statistic:**
If agreement is measured as a correlation (ρ):
$$t = rac{
ho_B - 
ho_A}{SE(
ho_B - 
ho_A)}$$

where $SE(
ho_B - 
ho_A) = \sqrt{	ext{SE}(
ho_B)^2 + 	ext{SE}(
ho_A)^2 - 2 	ext{Cov}(
ho_B, 
ho_A)}$ (the covariance is positive because both correlations are computed on the same N items).

Alternatively, use the **paired-correlation difference test** (Steiger, 1980):
$$z = rac{(
ho_B - 
ho_A) \sqrt{N-3}}{2(1 - 
ho_B 
ho_A)}$$
valid under normality.

**Resolution Ratio (q):**
Compute $q = N / N^*(\hat{\delta}, lpha, eta)$, where:
- $\hat{\delta}$ = observed agreement difference
- $N^*$ = required sample size to detect $\hat{\delta}$ at significance level α = 0.05 and power 1 − β = 0.80
- $N$ = actual sample size

**Decision Rule (from 2605.30315):**
- If $q ≥ 1$: the observed difference is **resolvable**; reject the null of no rubric effect.
- If $q < 1$: the observed difference is **unresolved**; fail to reject the null; the difference may be noise.

### Secondary: Many-Facet Rasch Measurement (MFRM)
Apply MFRM (per 2608.29517 methodology) to separate:
- **Item difficulty** (which items are harder to agree on)
- **Rater severity** (how strict each rater is)
- **Rubric-by-rater interaction** (does the rubric change affect the human and automatic rater asymmetrically?)

Report the residuals to detect **halo effects** (systematic overestimation of agreement due to shared impression) and **drift** (systematic change in the rater's scale over the rating session).

### Tertiary: Variance Components via Generalizability Theory
Decompose the total variance of agreement into components (per 2607.13304):
$$\sigma^2_{	ext{total}} = \sigma^2_{	ext{rubric}} + \sigma^2_{	ext{item}} + \sigma^2_{	ext{rater}} + \sigma^2_{	ext{automatic rater non-determinism}} + 	ext{(interactions and residual)}$$

Report the intraclass correlations (ICCs) for each component:
$$	ext{ICC}_{	ext{rubric}} = rac{\sigma^2_{	ext{rubric}}}{\sigma^2_{	ext{total}}}$$

This quantifies the **proportion of observable variance** attributable to the rubric change.

---

## Minimum Sample Size and Resources

### Core Design (Main Comparison Only)

**Items (N):**
- Power analysis (per 2010.06595): To detect a medium-sized difference in correlation (e.g., ρ changes from 0.60 to 0.70), with α = 0.05, 1 − β = 0.80, and assuming a typical effect-size estimate, N ≥ 40–60 items is a reasonable start.
- Adjust upward if correlation differences are expected to be small (ρ_A = 0.65, ρ_B = 0.68): N ≥ 100–150 items.

**Human Rater:**
- 1 human rater × 2 rubrics × N items = 2N ratings (e.g., 80–300 ratings total).

**Automatic Rater:**
- 1 automatic rater (same model, prompt template, across both rubrics) × 2 rubrics × N items = 2N automatic-rater calls.

### With Ablations

**Automatic Rater Determinism (Ablation 1):**
- k repeats per item (k = 3 or 5) × N items × 2 rubrics = 2kN additional calls (60–500 calls).

**Human Rater Drift (Ablation 2):**
- R retest items (R = 10–20) × 2 ratings (Rubric A and B) = 2R additional human ratings (20–40 ratings).

**Rubric Wording Stability (Ablation 3):**
- M items (M = 10–20) × 2 wordings of Rubric B × 2 raters (human + automatic) = 4M additional ratings (40–80 ratings + 40–80 automatic calls).

**Total Resource Estimate:**
- Human rater: 2N + 2R ≈ 100–350 ratings (depending on N and whether Ablation 2 is run)
- Automatic rater: 2N + 2kN + 4M ≈ 150–700 API calls (depending on N, k, and whether ablations are run)

---

## Concrete Resources

### Datasets
- **Item pool:** Must include the same N items scored under both rubric variants. Source: existing corpus, hand-annotated dataset, or sampled from a larger body (e.g., student essays, customer feedback, model outputs).
- **Rubric definition:** Two variants (original and revised), provided in written form (prose criteria, score levels, examples, and anchoring statements).

### Human Rater
- **Qualification:** 1 expert human rater familiar with the domain and scoring practice. (A single rater is sufficient for agreement measurement vs. an automatic rater; inter-human agreement is a separate, orthogonal question not addressed here.)
- **Instructions:** Detailed rubric, scoring guidelines, and a training set of 5–10 items (scored once, per rubric) to validate understanding before main rating begins.
- **Time:** ~2–5 hours total (depending on item complexity and rubric length). Assume 3–5 minutes per item × N items × 2 rubrics ÷ 60.

### Automatic Rater
- **Specification:** A fixed LLM or rule-based system (e.g., GPT-4 with a specific system prompt, or a fine-tuned classifier). Must be held constant across both rubric conditions to isolate the rubric effect.
- **Prompt template:** A single template that embeds the relevant rubric and item text, used for both rubric variants. Example:
  ```
  [System prompt with rubric and scoring instructions]
  Item: [item text]
  Score: [0–5, for example]
  Reasoning: [optional]
  ```
- **Implementation:** Use a fixed API call (e.g., OpenAI API, Anthropic API) with temperature = 0 (or a low fixed value) to minimize non-determinism.
- **Cost:** Depends on model and N. For GPT-4, expect ~$0.01–$0.10 per item at scale.

### Reproducibility Artifacts
Freeze and archive:
1. The original and revised rubrics (prose, with no changes post-data-collection).
2. The item corpus (input text for each item).
3. The system prompt and prompt template.
4. All human ratings and automatic rater outputs (raw, before any post-hoc filtering).
5. Random seed (if using stochastic sampling) and date/timestamp of each rating.

---

## Analysis Workflow

### Step 1: Descriptive Statistics
- Report the distribution of scores (mean, SD, range) for both raters under each rubric.
- Identify any rating-range compression (e.g., if the automatic rater uses only 2 of 5 scale levels).

### Step 2: Rater-Effects Audit (per 2608.29517 method)
- Fit an MFRM model: `Score ~ Rubric + Item + Rater + Rubric:Rater + error`
- Report severity parameters for each rater and each rubric.
- Test for significant rubric-by-rater interaction using a permutation test (e.g., family-wise 5% α).

### Step 3: Main Hypothesis Test
- Compute the correlation (ρ) of human vs. automatic rater scores within each rubric.
- Test the difference using the paired correlation test (Steiger or Fisher z-difference).
- Compute the resolution ratio q.
- Report 95% CIs on the correlations (bootstrap or analytical).

### Step 4: Ablation Analyses
- **Ablation 1:** Compute ICC for automatic rater resampling. If ICC < 0.70, adjust the CI on ρ to account for measurement error.
- **Ablation 2:** Compare the human rater's retest ICC on R items. If ICC < 0.80 and the retest shift differs significantly from the full-set shift, flag as confound.
- **Ablation 3:** Correlate agreement across the two paraphrased Rubric B wordings. If ρ < 0.85, flag the rubric effect as unstable.

### Step 5: Variance Decomposition
- Fit a generalizability model: `Score ~ Rubric + Item + (1 | Item × Rubric) + (1 | Rater) + ... + error`
- Report variance components and ICCs.
- Compute how much of the total variance is explained by the rubric vs. other sources.

### Step 6: Sensitivity and Robustness Checks
- Recompute all tests using alternative agreement metrics (e.g., ordinal vs. Pearson if scale allows).
- Exclude outlier items (e.g., bottom 5% by agreement) and recompute.
- Repeat the main test using a subset of the highest-confidence items (if uncertainty annotations are available).

---

## Decision Rules and Interpretation

### Condition 1: Agreement Improves, High Resolution
**Observation:** ρ_B > ρ_A, q ≥ 1, and the 95% CI on the difference does not include zero.

**Interpretation:** The rubric change **improved agreement between human and automatic rater** in a statistically resolvable way. The improvement is unlikely to be noise.

**Action:** Report the rubric revision as successful. (Caveat: confirm that severity shifts are not confounded, per Ablation 2.)

### Condition 2: Agreement Changes, Low Resolution
**Observation:** ρ_B > ρ_A (or < ρ_A), but q < 1.

**Interpretation:** The observed change is **unresolved**; it may be noise or a true effect too small to detect with the current sample size. The direction is suggestive but not confirmatory.

**Action:** Report as ambiguous. Recommend increasing N (compute N^* from the observed difference), or collect additional data to improve resolution.

### Condition 3: No Detectable Difference
**Observation:** ρ_B ≈ ρ_A, 95% CI on the difference includes zero.

**Interpretation:** The rubric revision **did not change human-automatic agreement** within the noise band. Either the revision had no effect, or any effect is too small to measure.

**Action:** Report as null. If ablations reveal large automatic-rater non-determinism (ICC < 0.70) or human-rater drift, recommend replication with larger N or tighter controls.

### Condition 4: Severity Shift, Correlation Stable
**Observation:** Both raters shift severity (e.g., ρ_B > ρ_A in average score), but the **correlation** remains unchanged.

**Interpretation:** The rubric revised the **scale level** (both raters scored more stringently), but did not improve **alignment**. This is a rating-scale artifact, not an improvement in mutual understanding.

**Action:** Adjust for severity using z-score normalization or MFRM residuals, then recompute correlation. Report both raw and adjusted metrics.

---

## Outcome Metrics: Concrete Reporting Format

### Main Result Table
| Metric | Rubric A (Original) | Rubric B (Revised) | Difference | 95% CI | q (Resolution Ratio) | Interpretation |
|---|---|---|---|---|---|---|
| Human-Automatic Correlation (ρ) | [value] | [value] | Δ = [value] | [CI_low, CI_high] | [q value] | Resolved? Yes/No |
| Human Mean Score | [μ_A] | [μ_B] | Δμ_human | [CI] | — | Severity shift |
| Automatic Mean Score | [μ_A] | [μ_B] | Δμ_auto | [CI] | — | Severity shift |
| Judge Severity (MFRM) — Human | [severity param] | [severity param] | — | — | — | Leniency/Harshness |
| Judge Severity (MFRM) — Automatic | [severity param] | [severity param] | — | — | — | Leniency/Harshness |
| Automatic Rater ICC (k repeats) | [ICC_A] | [ICC_B] | — | — | — | Non-determinism |
| Human Rater Retest ICC | [ICC_retest] | — | — | — | — | Drift |
| Rubric Wording Stability (ρ paraphrase) | [ρ] | — | — | — | — | Effect stability |

### Supplementary Output
- Item-by-rubric heatmap of disagreement.
- Variance-component breakdown (bar plot or table).
- Bootstrap distributions of correlation differences (density plot).
- Pre-/post-rubric scatter plots (human vs. automatic scores, one plot per rubric).

---

## Evidence Basis and Citations

The design integrates methodologies from the following released evidence excerpts:

1. **Statistical Power and Underpowered Experiments (2010.06595):**
   - Simulation-based power analysis for NLP tasks, adjusted for paired designs.
   - Recognition that underpowered experiments fail to distinguish signal from noise.

2. **Judge Severity, Halo, and Rater Effects (2608.29517):**
   - Many-facet Rasch measurement (MFRM) to isolate rater severity from correlation.
   - Pre-registered battery of rater-effects audits (severity, halo, drift, version instability).
   - Generalizability theory (G-theory) to estimate retest ICC and decision-study allocations.

3. **Paired Resolution Targets for LLM Evaluation (2605.30315):**
   - Paired hypothesis-testing framework for comparing two conditions on shared items.
   - Resolution ratio (q = N / N^*) as a diagnostic for whether observed differences are resolvable.
   - Correction for small-effect expansions in paired power calculations.

4. **Variance Components and Noise Decomposition (2607.13304):**
   - Generalizability-theory decomposition of variance sources (facets: rubric, item, rater, within-prompt resampling, etc.).
   - Decision-study allocation to minimize variance at a fixed query/rating budget.
   - Intraclass correlation (ICC) reporting for each component.

---

## Limitations and Open Questions

1. **Single Human Rater:** The design uses one human rater to minimize cost, but this sacrifices inter-rater agreement as a metric. If multiple human raters are available, extend the design to a multi-rater panel and use Fleiss κ or Krippendorff's α.

2. **Automatic Rater Stability:** The design assumes the automatic rater is deterministic (or has low non-determinism, ICC ≥ 0.70). If Ablation 1 reveals high non-determinism, the agreement metric itself becomes unreliable. Recommend repeating with a lower-temperature or deterministic system.

3. **Rubric Interpretation:** Both raters may interpret the rubric differently even after revision. The design isolates whether the rubric *as presented* improved agreement, but does not measure whether the rubric was ambiguous in either version. A post-rating debrief (asking both raters to explain their scoring) could illuminate this.

4. **Generalization:** The effect of the rubric revision may depend on the item corpus, the specific human rater, or the automatic rater system. This design measures the rubric effect in one configuration; replication across different raters or item sets is recommended before generalizing.

5. **Direction of Effect:** The design is symmetric with respect to the rubric variants (Rubric A vs. Rubric B) and does not assume which revision is "better." The outcome is agnostic: it reports whether agreement changed, not whether the change is an improvement. Defining "improvement" requires additional domain judgment (e.g., does the revised rubric align better with expert consensus? Does it improve fairness?).

---

## Summary

This design answers the research question by:
1. **Pairing:** Scoring identical items under both rubric variants to reduce noise and increase power.
2. **Quantifying Noise:** Measuring automatic-rater determinism (Ablation 1) and human-rater drift (Ablation 2) to establish baselines for noise.
3. **Testing Resolution:** Using the paired resolution framework (q) to determine whether the observed agreement difference is statistically distinguishable from noise.
4. **Decomposing Rater Effects:** Using MFRM and variance-component analysis to isolate severity shifts from correlation shifts, preventing severity-only changes from being misinterpreted as agreement improvements.
5. **Validating Stability:** Testing whether the effect is robust to rubric-wording paraphrasing (Ablation 3).

The outcome is a concrete, verifiable answer to whether the rubric change improved human-automatic agreement, or whether the observed change is within the noise band of a standard rating experiment.
