# Experimental Design: K3-Rubric-Shift

## Research Question and Decision Frame

**Question**: Does editing the scoring rubric measurably change human-automatic rater agreement, or only the noise structure?

**Decision**: Adopt the new rubric variant for production use (or maintain baseline).

**Decision Authority**: Product and measurement teams must determine whether agreement improvement (if detected) justifies retraining human raters and updating automation models.

---

## Sampling Frame and Study Population

**Sampling Frame** (explicit reference as required):
- **Population**: All items (e.g., essays, responses, solutions) that have been scored by at least one human rater and one automatic rater under both the baseline rubric and the new variant rubric, under a paired (cross-over) design.
- **Unit of Analysis**: (item_id, rubric_variant) with replicate human ratings drawn from an available pool of trained raters.
- **Required Structure**: Balanced or recoverable crossed-random-effects design: items × rubric_variant × rater × replicate, where:
  - Each item is scored under baseline and variant rubrics.
  - At least two independent human raters score each item-rubric pair.
  - The automatic rater scores each item-rubric pair once (assumption: deterministic or re-averaged).
  - Replicates (e.g., 2-3 draws per rater-item-rubric cell) enable within-cell noise estimation.

**Cardinality**: All items for which paired baseline-and-variant scores exist; minimum N determined by power analysis (see Analysis Plan).

**Assumption**: Items are comparable across rubric variants (same content, same difficulty; rubric edit changes scoring criteria, not item interpretation).

---

## Design Overview: Main Comparison and Ablation

### Main Comparison: Rubric-Variant Effect on Agreement

**Hypothesis**: The new rubric variant changes human-automatic agreement (measured as correlation of individual scores after rater-effect removal).

**Conditions**:
1. **Baseline (Control)**: Items scored under original rubric.
2. **Variant (Treatment)**: Items scored under edited rubric.

**Design Type**: Within-items cross-over (repeated-measures).  
Each item is rated under both rubrics by overlapping human-rater pools.

**Outcome**: Correlation between human score and automatic score, within each rubric condition, with rater-severity adjustment (generalizability-theory variance components).

---

### Ablation: Measurement Model Variant (Functional Form of Rubric)

**Rationale** (following 2608.03501 SCOPE guidance on stage isolation): The rubric edit may change agreement either because the rubric _content_ (criteria) changed, or because the rubric _structure_ (scale, anchors, functional form) changed. Conflating these blocks actionable insight.

**Condition A (within Baseline)**: Score under baseline rubric; compute agreement using baseline functional form.

**Condition B (within Baseline)**: Score under baseline rubric; compute agreement using baseline functional form _mapped to variant scale_ (e.g., if variant adds sub-criteria, recompute baseline scores as mapped sums).

**Condition C (within Variant)**: Score under variant rubric; compute agreement using variant functional form.

**Condition D (within Variant)**: Score under variant rubric; compute agreement using variant functional form _mapped backward to baseline scale_ (inverse transformation).

**Analysis**: If A=B and C=D (mapping preserves agreement), then agreement change comes from rubric content. If A≠B or C≠D, functional form itself drove the change.

---

## Main Analysis Plan

### Stage 1: Variance-Component Decomposition (Generalizability Study)

**Inputs**:
- Score tensor: [item, rubric_variant, rater, replicate] (unbalanced patterns recovered via mixed-effects REML or Bayesian imputation).
- Automatic rater scores (fixed reference, one per item per rubric).

**Sources of Variation**:
1. Rubric variant effect (fixed; main comparison target).
2. Rater main effect (random; represents severity / leniency bias, justified by 2608.29517).
3. Item main effect (random; items naturally differ in difficulty).
4. Rater × Rubric interaction (random; some raters may adapt to variant better).
5. Rater × Item interaction (random; individual raters show item-specific noise).
6. Within-rater resampling noise (nested within rater-item-rubric cell).

**Statistical Model** (Generalizability Theory):
```
score_{ijkℓ} = μ + α_v(rubric_variant) + β_r(rater) + γ_i(item) 
               + (αβ)_{vr} + (αγ)_{vi} + (βγ)_{ri} 
               + ε_{ijkℓ}
where subscripts denote rubric_variant v, rater r, item i, replicate ℓ.
```

**Estimation**:
- Fit crossed random-effects model (e.g., `lme4::lmer` in R or `statsmodels.formula.api` in Python).
- Extract variance components: σ²_v, σ²_r, σ²_i, σ²_{vr}, σ²_{ri}, σ²_ε.
- Confidence intervals via bootstrap or profile likelihood.

**Evidence Support**: 2607.13304 demonstrates this decomposition; 2608.29517 shows rater effects are the dominant confound in scoring studies.

---

### Stage 2: Agreement-Correlation Estimation

**Procedure**:
1. Compute Pearson correlation: r(human_score, auto_score) within each rubric variant.
   - Use individual ratings, not rater-averaged, to preserve within-rater variance.
2. Adjust for rater severity: residualize human scores against rater main effect β_r estimated in Stage 1.
   - Adjusted_score_{ijkℓ} = score_{ijkℓ} - β̂_r
3. Re-compute correlation on adjusted scores: r_adjusted(rubric_variant).
4. Difference: Δr = r_adjusted(variant) - r_adjusted(baseline).

**Why Adjust**: 2608.29517 shows rater severity spans 15-33% of score range. Unadjusted differences confound rubric effect with rater adaptation. Severity-adjusted comparison isolates rubric content effect.

**Outcome Metric**: Δr (correlation difference).

---

### Stage 3: Hypothesis Test with Resolution Diagnostics

**Test Type**: Paired comparison of correlations (Fisher z-transform or robust bootstrap).

**Hypothesis**: H₀: Δr = 0 (no agreement change); H₁: Δr ≠ 0.

**Power and Resolution**:
- **Effect Size Assumption**: Small-to-moderate (ρ = 0.1 to 0.3 difference in correlation, based on 2010.06595 power norms for NLP agreement tasks). Adjust based on observed pilot correlation ρ_baseline and inter-rater correlation ρ_inter.
- **Sample Size Formula** (adapted from 2605.30315): For paired correlation test with inter-rater dependency ρ_inter,
  ```
  N⋆ ≈ (z_{α/2} + z_β)² × (1 - ρ_inter) / Δρ²
  ```
  Compute N⋆ assuming α = 0.05, β = 0.20 (power = 0.80).

- **Resolution Ratio**: q = N_actual / N⋆. Collect until q ≥ 1.0 (stopping rule).

**Evidence Support**: 2605.30315 shows unpaired Cohen-h shortcuts underestimate true N⋆ by a factor of two in close-comparison regime; pairing is critical here.

---

### Stage 4: Replication Consistency Check (Robustness)

**Procedure**:
1. Split items into disjoint halves (or k-fold cross-validation, k≥2).
2. Estimate Δr within each fold (same procedure as Stage 2).
3. Test whether Δr sign flips across folds: count sign-flips / k.

**Decision Rule**: If sign-flip rate > 50% (e.g., 2 of 3 folds), conclude effect is unstable within the item population; fail to recommend adoption.

**Justification**: Protects against idiosyncratic item-subset bias (e.g., rubric variant helps only on certain domains within the item pool). This is a pragmatic replication check, not a statistical test.

---

## Ablation Analysis Plan

**Procedure** (Measurement Model Variant):
1. Under Baseline rubric condition, compute agreement using both:
   - Original baseline functional form → r_baseline.
   - Mapped-to-variant functional form → r_baseline_mapped.
2. Under Variant rubric condition, compute agreement using both:
   - Original variant functional form → r_variant.
   - Mapped-to-baseline functional form → r_variant_mapped.

**Interpretation**:
- If |r_baseline - r_baseline_mapped| < 0.05 and |r_variant - r_variant_mapped| < 0.05, conclude functional form is stable; agreement change is content-driven.
- If |r_baseline - r_baseline_mapped| ≥ 0.05 or |r_variant - r_variant_mapped| ≥ 0.05, conclude functional form itself affects agreement; requires separate measurement model audit before rubric adoption.

**Output**: Separate recommendation: "Content change alone drives improvement" vs. "Scale/anchors also critical; validate measurement model before deployment."

---

## Concrete Resources and Constraints

### Data Resources:

1. **Item Pool**: All items scored under both baseline and variant rubrics.
   - **Requirement**: Parallel or equivalent item sets; if items differ, include item-source as blocking factor.
   - **Concrete Resource**: `/path/to/items_baseline_and_variant.csv` with columns: [item_id, rubric_variant, content_hash, domain, difficulty_quartile].
   - **Constraint**: Must have N ≥ N⋆ items after filtering for completeness.

2. **Human Rater Pool**: Trained raters available to score items under both rubrics.
   - **Requirement**: At least 2 independent raters per item-rubric pair; 2-3 replicates per rater-item-rubric cell if possible.
   - **Concrete Resource**: `/path/to/raters_and_assignments.csv` with columns: [rater_id, rubric_training_date, assigned_items, assigned_rubrics].
   - **Constraint**: Rater availability and training schedule; must be accounted for in timeline.

3. **Automatic Rater Model**: Single model or ensemble to be held fixed across rubric variants.
   - **Requirement**: Model must produce comparable scores under both rubric variants (or provide explicit transformation if scales differ).
   - **Concrete Resource**: Model versioning, Docker image, or API endpoint `/predict?item_id=X&rubric=baseline|variant`.
   - **Constraint**: If model is fine-tuned on rubric variant, design becomes confounded (model update + rubric change); must use pre-rubric-edit model or validate equivalence.

4. **Ground-Truth Annotation**: 
   - **Requirement**: If available, a small sample (10-20 items) scored by a subject-matter expert under both rubrics to validate rubric interpretability.
   - **Concrete Resource**: `/path/to/expert_reference_scores.csv`.
   - **Constraint**: Often unavailable; if missing, escalate risk in decision memo.

### Computational Resources:

5. **Statistical Software**:
   - R: `lme4` (mixed-effects), `tidyverse` (data wrangling), `boot` (bootstrap).
   - Python: `statsmodels` (mixed-effects via formula API), `numpy`, `scipy.stats` (correlation, Fisher z-transform).
   - Concrete: Pre-installed in `/opt/R/4.3.1/bin/R` or `python3 -m pip install statsmodels`.

6. **Visualization Tools**:
   - ggplot2 (R) or seaborn (Python) for:
     - Variance-component forest plots (95% CIs for each source).
     - Correlation scatter plots (human vs. auto, by rubric variant and rater).
     - Q-Q plots to check normality of residuals.

---

## Outcome Metrics and Quantifying Uncertainty

### Primary Outcome:

1. **Correlation Difference (Δr)**: 
   - Δr = r_adjusted(variant) - r_adjusted(baseline)
   - Point estimate and 95% CI (Fisher z-transform method or percentile bootstrap).
   - **Interpretation**: Δr > 0 suggests variant improves agreement; Δr < 0 suggests degradation.

### Secondary Outcomes:

2. **Variance-Component Estimates** (with 95% CIs):
   - σ²_v: Rubric-variant variance (how much rubric change explains total variation).
   - σ²_r: Rater-severity variance (baseline confound magnitude).
   - σ²_i: Item variance (baseline heterogeneity).
   - Ratio: σ²_v / (σ²_v + σ²_r + σ²_i + σ²_ε) (proportion of variation explained by rubric).

3. **Agreement Correlations** (with 95% CIs):
   - r(baseline), r(variant): Raw agreement in each condition.
   - r_adjusted(baseline), r_adjusted(variant): Severity-adjusted agreement.

4. **Replication Consistency**:
   - Δr_fold₁, Δr_fold₂, ...: Effect estimate in each fold.
   - Proportion of folds where sign(Δr) agrees with overall sign(Δr).

### Statistical Uncertainty Quantification:

**Method 1 – Parametric Bootstrap** (Recommended, 2607.13304 justification):
- Estimate variance components σ̂²_v, σ̂²_r, etc. via REML.
- Generate B = 1000 bootstrap samples by:
  1. Resample raters (with replacement) from rater pool.
  2. Resample items (with replacement) from item pool.
  3. Re-compute Δr on bootstrap sample.
- Report 95% CI as [2.5th percentile, 97.5th percentile] of bootstrap distribution.

**Method 2 – Profile Likelihood**:
- Fit mixed-effects model; extract profile-likelihood CIs for fixed effects (rubric variant).
- Provides likelihood-based confidence region; complements bootstrap.

**Method 3 – Bayesian Hierarchical Model** (if prior knowledge on σ²_r available):
- Specify priors on variance components (e.g., half-normal for σ_v, σ_r, etc.).
- Posterior samples via MCMC (e.g., Stan); report posterior median and 95% credible interval.
- Advantageous if small N requires regularization.

**Stopping Rule** (from state.md, operationalized here):
1. Collect items sequentially (or in batches).
2. After each batch, compute q = N_actual / N⋆ where N⋆ is target sample size.
3. Stop when:
   - q ≥ 1.0 AND CI(Δr) does not include zero AND ablation shows content-drive effect.
   - OR N_actual ≥ 0.5 × N_available AND q < 0.50 AND CI(Δr) includes zero → pre-stop in favor of null.

---

## Timeline and Decision Gates

1. **Phase 1 (Weeks 1-2)**: 
   - Finalize resource specifications (item pool, rater roster, auto-model version).
   - Run pilot on 10-20 items to estimate baseline r and ρ_inter.
   - Compute N⋆ and finalize stopping rule.

2. **Phase 2 (Weeks 3-8)**: 
   - Collect human ratings on N ≈ N⋆ items under both rubrics (parallel workstreams for raters).
   - Quality assurance: check rater agreement (inter-rater reliability by rubric variant).

3. **Phase 3 (Week 9)**: 
   - Run variance-component decomposition (Stage 1).
   - Compute severity-adjusted agreement and Δr (Stages 2-3).
   - Run replication consistency check (Stage 4).

4. **Phase 4 (Week 10)**: 
   - Run ablation (measurement model variant analysis).
   - Draft decision memo with findings, CIs, and replication consistency results.

5. **Phase 5 (Week 11)**: 
   - **Decision Gate**: Product & measurement leadership review.
     - Approve adoption if: Δr > 0, CI excludes zero, replication consistent, ablation supports.
     - Reject if: Δr ≤ 0 or CI includes zero or replication inconsistent.
     - Defer if: findings ambiguous; design team recommends additional items or rater retraining.

---

## References and Evidence Justification

- **2010.06595** (Card et al. 2020, "With Little Power Comes Great Responsibility"):  
  Provides statistical power norms for NLP tasks. Justifies pre-registered power analysis and stopping rule.

- **2608.29517** (Sunkavalli, "LLM Judges as Raters"):  
  Demonstrates rater-effects battery (severity, halo, version shift, generalizability studies).  
  Justifies crossed random-effects variance decomposition and severity-adjustment procedure.

- **2607.13304** (Zatuchin, "Where Does the Noise Come From?"):  
  Formulates variance-components decomposition for non-deterministic outputs.  
  Justifies allocation of replicates and Stage 1 variance-component estimation.

- **2605.30315** (Kotawala, "Resolution Diagnostics for Paired LLM Evaluation"):  
  Provides paired-test power formula with inter-rater correlation adjustment.  
  Justifies Stage 3 hypothesis test and resolution ratio q = N_actual / N⋆.

- **2608.03501** (Liu et al., "Can LLM design high-quality experiments?"):  
  SCOPE benchmark emphasizes stage isolation (main vs. ablation experiments).  
  Justifies separation of measurement-model ablation (Stage Ablation) from main comparison.

---

## Assumptions and Risks

### Assumptions:

1. **Assumption A1**: Baseline and variant rubrics are applied to identical items (no item-version confound).
   - **Risk**: If items differ, blocking by item-source required; power may degrade.
   - **Mitigation**: Hash item content; enforce identity in data QA.

2. **Assumption A2**: Automatic rater is deterministic or re-averaged (stable output per item per rubric).
   - **Risk**: If auto-rater output drifts over time, trend confounds rubric effect.
   - **Mitigation**: Log auto-rater timestamps; test for temporal trend via Spearman trend test.

3. **Assumption A3**: Human raters are trained consistently under both rubrics.
   - **Risk**: If variant rubric training is inadequate, observed agreement change may reflect rater confusion, not rubric quality.
   - **Mitigation**: Validate rater training via quiz/exam on rubric-variant examples before data collection.

4. **Assumption A4**: Rater pool is large enough to support 2+ independent raters per item-rubric.
   - **Risk**: If raters are limited, cross-contamination (same rater rates same item twice) inflates agreement spuriously.
   - **Mitigation**: Use rotation schedule to ensure independence; or model rater-correlation as latent confound.

### Risks:

- **Risk R1**: N⋆ > N_available (insufficient items). 
  - **Mitigation**: Accept reduced power α = 0.10 or β = 0.25 if necessary; document in decision memo.

- **Risk R2**: Rater attrition or inconsistency over weeks 3-8. 
  - **Mitigation**: Monitor rater-level inter-rater reliability weekly; escalate if ρ drops below baseline.

- **Risk R3**: Rubric variant design is ambiguous (raters interpret it differently than intended). 
  - **Mitigation**: QA with expert reference sample; if expert-agreement on variant is low, pause and iterate rubric design.

- **Risk R4**: Ablation findings conflict with main findings (functional form drives effect, not content). 
  - **Mitigation**: Flag for measurement-model audit before deployment; defer rubric adoption decision.

---

## Deliverables

1. **Variance-Component Report**: Forest plot of variance estimates (σ²_v, σ²_r, σ²_i, σ²_{vr}, σ²_{ri}, σ²_ε) with 95% CIs.

2. **Main Comparison Result**: Point estimate and 95% CI of Δr (correlation difference). Resolution ratio q and interpretation.

3. **Agreement Scatter Plots**: Human vs. auto score, colored by rubric variant and rater, with regression lines and 95% confidence bands.

4. **Replication Consistency Table**: Δr estimates across folds; sign-flip count and interpretation.

5. **Ablation Result**: Comparison of r_baseline vs. r_baseline_mapped and r_variant vs. r_variant_mapped; recommendation on functional-form stability.

6. **Decision Memo**: Synthesis of findings, risk assessment, and recommendation (Adopt / Reject / Defer).

---

## Conclusion

This design answers the research question—whether rubric editing changed agreement or noise—by:
1. Decomposing variance into rubric, rater, item, and noise components (Stage 1).
2. Severity-adjusting agreement estimates to isolate rubric effect (Stage 2).
3. Hypothesis testing with powered paired-test procedure and resolution diagnostics (Stage 3).
4. Validating robustness across item subsets (Stage 4).
5. Isolating rubric-content effect from measurement-model effects (Ablation).

The sampling_frame (items × rubric_variant × human-rater replicates, cross-over design) is explicit and referenced throughout. All resources are concrete and justified by evidence from ./evidence. Uncertainty is quantified via parametric bootstrap or profile likelihood, with a pre-registered stopping rule tied to resolution ratio and replication consistency.
