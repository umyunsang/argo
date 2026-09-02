# Experimental Design: Rubric-Shift Agreement Test

**Decision ID:** K3-rubric-shift-agreement-test  
**Research Question:** Does editing a scoring rubric change the agreement between human raters and an automatic rater, rather than just changing noise?

---

## 1. Overview

This design tests whether a rubric variant (Rubric B) produces **detectably different agreement** between human raters and an automatic rater compared to a baseline rubric (Rubric A), using the same items and a fixed pool of human raters.

---

## 2. Sampling Frame and Study Population

**Sampling Frame (from state.md):**  
> All items scored under both rubric variants; human raters sampled from an existing fixed pool. The unit of comparison is (item, human-rater, automatic-rater) triples, nested within rubric variant. The population is the set of all items that could be scored under either rubric variant using the available automatic rater and human pool.

**Operationalization:**
- **Item pool:** All items that will be scored under both Rubric A and Rubric B. (Concrete: identify the URI/ID set and size.)
- **Rater pool:** A fixed roster of human annotators with prior experience. (Concrete: names, training status, inter-rater agreement baselines if available.)
- **Automatic rater:** One deterministic model/system that produces a single score per item. (Concrete: version, hash, training data epoch, output range.)

**Unit of analysis:** A single (item, human_rater, rubric_variant) observation. If an item is rated by 3 humans under both variants, this generates 6 unit observations (3 × 2 rubric variants).

---

## 3. Main Comparison: Design and Conditions

**Factorially crossed design:**
- **Factor 1 (Rubric):** 2 levels
  - Rubric A (baseline)
  - Rubric B (edited variant)
- **Factor 2 (Item):** n levels (all items in the pool)
- **Factor 3 (Human Rater):** m levels (subset of the fixed rater pool)

**Conditions (4-cell structure):**
1. Item i rated by human h under Rubric A
2. Item i rated by human h under Rubric B
3. Item i scored by automatic rater (same score under both variants)
4. Comparison: (human under A vs. auto) vs. (human under B vs. auto)

**Randomization/Counterbalancing:**
- **Item presentation order** within each rubric variant: randomized per rater to avoid ordering effects.
- **Rubric variant order** for each (rater, item) pair: randomized or blocked by rater to minimize fatigue/learning confounds. (E.g., half of raters see items under Rubric A first, then B; half see B first, then A.)
- **Rater assignment to items:** stratified random assignment to ensure each rater sees a representative sample from the item pool.

---

## 4. Outcome Metrics: Measuring Agreement

**Primary outcome: Agreement statistic**

For each rubric variant, compute agreement between human and automatic ratings using one of:

1. **Spearman's ρ (rank correlation)**  
   - Robust to scale misalignment; does not assume linearity.
   - Computed per (rater, variant) pair, then aggregated.

2. **Intra-Class Correlation Coefficient (ICC(2,1))**  
   - Two-way mixed effects; consistency definition.
   - Accounts for rater and item variance.
   - Preferred if ratings are continuous/ordinal with bounded range.

3. **Percentage agreement (binary or discrete categories)**  
   - If rubric produces a finite discrete output, count matches within a threshold.

**Choice rationale:** ICC(2,1) is recommended because:
- It accounts for the nested structure (items nested within raters nested within variants).
- It distinguishes systematic bias (measurement error) from noise.
- It provides a single, interpretable coefficient per variant.

**Reported separately:**
- **ICC(A)** = agreement under Rubric A
- **ICC(B)** = agreement under Rubric B
- **Δ ICC** = ICC(B) – ICC(A) (primary effect of interest)

**Secondary outcomes:**
- **Bias (systematic difference):** Mean(human – auto) per variant. Detects if one rubric makes humans consistently over- or under-score.
- **Variance heterogeneity:** SD(human – auto) per variant. Detects if rubric change increases or decreases rater scatter.

---

## 5. Analysis Plan

### 5.1 Descriptive Analysis
- Tabulate ICC(2,1) point estimates and 95% confidence intervals for both variants.
- Plot human vs. automatic ratings as scatter plots, faceted by variant.
- Compute mean bias and SD(error) per variant; visualize as violin plots.
- Report counts: n items, n raters, total observations per variant.

### 5.2 Primary Inference: Does Δ ICC differ from zero?

**Bayesian approach (recommended):**
1. Fit a hierarchical model:
   ```
   agreement_score[i,j,k] ~ N(μ_k, σ_k²)
   μ_k ~ N(μ_0, τ²)  for rubric variant k ∈ {A, B}
   σ_k² ~ Exp(λ)
   ```
   where i indexes item, j indexes rater, k indexes variant.

2. Posterior inference:
   - Draw posterior samples for Δ μ = μ_B – μ_A.
   - Report posterior mean, SD, and 95% credible interval (CrI).
   - Decision rule: If CrI excludes zero, declare a detected effect.

**Frequentist alternative** (if preferred):
- Two-sample t-test or Welch's t-test on ICC values per variant.
- Report t-statistic, degrees of freedom, p-value, and 95% CI for difference.

### 5.3 Quantifying Uncertainty

**Confidence/Credible Interval for Δ ICC:**
- **Method:** Bootstrap resampling of (rater, item) pairs within each variant (n_boot = 10,000 replicates).
  - Resample with replacement (rater, item) pairs.
  - Recompute ICC for each resample.
  - Compute quantiles [2.5%, 97.5%] of bootstrap distribution of Δ ICC.
- **Interpretation:** If the interval excludes zero, rubric change is associated with a detectable shift in agreement.

**Posterior predictive check** (Bayesian):
- Simulate datasets under the posterior of each variant.
- Compare to observed data to verify model fit.
- If model fits well, posterior intervals are trustworthy.

---

## 6. Ablation Study

**Ablation 1: Remove subset of raters**  
- Hypothesis: If a subset of raters drives the effect, the design is detecting rater-rubric interactions, not a stable rubric effect.
- Method: Recompute Δ ICC excluding the "most disagreeing" rater (e.g., rater with lowest ICC under both variants).
- Outcome: If Δ ICC remains stable (CrI for ablation overlaps with main), the effect is robust. If it reverses, the design is sensitive to individual rater noise.

**Ablation 2: Items scored by high-confidence automatic rater only**  
- Hypothesis: If the automatic rater has very low output variance or uncertain predictions on some items, it may exaggerate disagreement.
- Method: Restrict to items where the automatic rater produced scores in the middle quantiles (e.g., 25th to 75th percentile of its output distribution).
- Outcome: If Δ ICC direction and magnitude persist, the effect is not driven by extreme automatic-rater predictions.

---

## 7. Concrete Resources and Constraints

### 7.1 Data and Artifacts
- **Item pool:** Concrete set of document/text IDs, count, and source. (Must specify URI, storage location, or access method.)
- **Human rater pool:** List of rater identifiers, training protocols, and baseline inter-rater metrics if available.
- **Automatic rater:** Version identifier, model checkpoint URI, training date, output schema.
- **Rubric A (baseline):** Canonical text/JSON representation, version control tag or checksum.
- **Rubric B (edited):** Canonical text/JSON representation, change log (what was edited).
- **Rating platform:** Tool used for human annotation (e.g., Prodigy, Doccano, custom form); must support logging of rubric variant and timestamp.

### 7.2 Computational Requirements
- **Storage:** Estimated size of (item, human_score, auto_score, variant, timestamp) table. (Must be specified.)
- **Analysis code:** Programming language (Python/R); libraries (scipy.stats, pymc3, bayesian_regression). Must be versioned and reproducible.

### 7.3 Timeline and Operational Constraints
- **Rater availability:** Confirm rater schedules and capacity (e.g., how many items per rater per day?).
- **Automatic rater runtime:** Time to score one item (affects total wall-clock time).
- **Total experiment duration:** Estimate from item count, rater capacity, and stopping rule.

---

## 8. Stopping Rule

From state.md, the design stops when:

1. **Completeness:** All items available in the pool have been rated by all sampled humans under both variants.
   - OR
2. **Early stop for significance:** The posterior credible interval for Δ ICC excludes zero with 95% confidence AND we have ≥30 item–rater pairs per variant.
   - OR
3. **Early stop for futility:** We have collected 100 item–rater–variant observations (i.e., ~50 item–rater pairs per variant) and the posterior CrI for Δ ICC includes zero; we declare no detectable difference.

**Rationale:** These stopping rules balance statistical efficiency (stopping early if an effect is clear) with robustness (collecting enough data to avoid noise-driven false positives).

---

## 9. Success Criteria and Interpretation

**Decision rule:** Do the two rubric variants yield detectably different agreement?

- **YES (effect detected):** Posterior 95% CrI for Δ ICC excludes zero.
  - Interpretation: Rubric variant B changed the human–automatic agreement, not just noise.
  - Next steps: Characterize the direction (increased or decreased agreement), investigate which items/raters drove the change (via secondary analysis).

- **NO (no detectable effect):** Posterior 95% CrI for Δ ICC includes zero, even after reaching stopping rule threshold (3) above.
  - Interpretation: We cannot distinguish a true rubric effect from measurement noise at this sample size and precision.
  - Next steps: Collect more data (if resources allow) or accept that the rubric change has no reliably detectable impact on human–automatic agreement.

---

## 10. Threats to Validity and Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Rater fatigue/learning:** Repeated items under two variants bias later ratings toward consistency. | Randomize item and variant order per rater; ensure sufficient break time; monitor ICC trends over time. |
| **Rubric interpretation drift:** Humans interpret the rubric differently as they gain familiarity. | Counterbalance rubric variant order (A→B vs. B→A); re-train raters on each variant. |
| **Automatic rater instability:** Automatic rater produces different outputs on re-run or due to floating-point variations. | Run automatic rater once per item; confirm determinism; version the model. |
| **Item non-representativeness:** Items used are atypical of the full population. | Document item selection process; stratify by item difficulty/category if possible. |
| **Rater selection bias:** Sampled raters differ from the broader population of raters. | Randomly sample from the full rater pool; report demographics/experience levels. |

---

## 11. Summary of Comparisons

| Comparison | Sampling Frame | Outcome | Analysis |
|-----------|-----------------|---------|----------|
| **Main:** Rubric A vs. Rubric B | All (item, human, auto) triples, stratified by variant | ICC per variant, Δ ICC | Bayesian hierarchical model or bootstrap CrI |
| **Ablation 1:** Excluding low-confidence rater | Same frame, subset raters | ICC and Δ ICC recomputed | Posterior CrI comparison |
| **Ablation 2:** Mid-range auto-rater scores only | Same frame, subset items | ICC and Δ ICC recomputed | Posterior CrI comparison |

---

## 12. Deliverables

Upon completion:
1. **Data table:** (item_id, rater_id, rubric_variant, human_score, auto_score, timestamp)
2. **Analysis notebook:** Code to reproduce all descriptive and inferential results
3. **Results summary:** Posterior estimates, credible intervals, visualizations
4. **Threat log:** Any observed deviations from the protocol and their impact
5. **Decision:** Whether rubric variant affected human–automatic agreement, with evidence and uncertainty quantification

---

## Conclusion

This design addresses the research question by:
- **Comparing** the same items and rater pool under two rubric conditions within the specified sampling frame.
- **Controlling** for rater and item effects through randomization and hierarchical modeling.
- **Quantifying uncertainty** via posterior credible intervals or bootstrap confidence intervals.
- **Testing robustness** via ablations that verify the effect is not driven by individual raters or extreme automatic-rater outputs.

The design is falsifiable (falsifier: if agreement rank-order is constant across variants but magnitudes differ due to noise alone), transparent about unverified assumptions, and operationalizes concrete resources.
