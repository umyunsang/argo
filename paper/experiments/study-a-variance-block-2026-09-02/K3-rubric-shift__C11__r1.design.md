# Complete Experimental Design: Rubric-Shift Effect Detection

## Research Question
How do you tell whether editing a scoring rubric changed the agreement between human raters and an automatic rater, rather than changing noise?

## Premise
Two rubric variants (A and B) exist. Human raters have already rated a set of items under one or both variants. An automatic rater (e.g., an LLM-based judge) will score the same items under both variants. The task is to determine whether the rubric edit shifted the automatic rater's systematic agreement with humans, or merely introduced variance (random or systematic but not signal-altering).

---

## 1. Main Comparison: Paired Rubric Agreement Test

### Design Structure
A paired design (not an unpaired one) that follows the sampling_frame defined in state.md: the same set of N items, scored by the same human raters, evaluated by the automatic rater twice (once per rubric).

**Sampling frame (from state.md):**  
The population is the set of scoreable items under both rubric variants. The unit of observation is (item, human rater, automatic rater, rubric variant, replicate). The sample is a fixed set of N items, each scored by the same pool of human raters under rubric A and rubric B (paired on items, independent on rubric), each paired rating episode scored by the automatic rater K=3 or 5 times to separate within-rater variance from systematic effects. Human ratings are singleton. This sampling_frame structure—pairing on items, replicating automatic-rater calls, holding human raters constant—enables the design to separate systematic agreement changes from random noise.

### Primary Hypothesis
**H1 (two-sided):** The automatic rater's agreement with humans is the same under rubric A and rubric B.

**Test:** Paired t-test on the correlation (Pearson r, or Fisher-z-transformed correlations) between automatic and human scores, computed per item and rubric variant, then paired across rubrics.

Alternatively: paired t-test on quadratically-weighted kappa (QWK) if scores are ordinal; or permutation test on Spearman rank correlation if normality is violated.

### Outcome Metrics: Primary

1. **Agreement correlation (Rubric A):**  
   Pearson r between automatic and human scores across all N items, under rubric A. Reported as point estimate + 95% CI (bootstrap or normal approximation).

2. **Agreement correlation (Rubric B):**  
   Pearson r between automatic and human scores across all N items, under rubric B. Reported as point estimate + 95% CI.

3. **Paired difference in agreement:**  
   δ_r = r_B − r_A, reported as point estimate + 95% CI. P-value from paired t-test or permutation test, two-sided, α=0.05 (family-wise).

4. **Resolution ratio (q):**  
   Compute q = N / N^* where N^* is the required paired sample size to detect δ_r at power 0.80 and α=0.05. Per 2605.30315 (Kotawala 2026), q ≥ 1 means the study is adequately powered. Report q explicitly; if q < 1, acknowledge underpowering.

5. **Quadratically-weighted kappa (QWK) under each rubric:**  
   Report QWK_A and QWK_B as location-blind check. These will likely remain stable even if severity shifts; this is expected and documented (per 2608.29517: Sunkavalli 2026 shows kappa is insensitive to 219-point severity differences).

---

## 2. Severity Analysis: Separating Systematic Shift from Noise

### Rationale
Per 2608.29517 (Sunkavalli 2026), LLM judges differ in severity (mean score) independent of agreement. A rubric change might push the automatic rater to score higher or lower overall, a systematic shift orthogonal to agreement structure. This is "noise" in the sense that it does not affect rank correlation but is systematic in magnitude. Severity shifts must be quantified and separated from agreement changes.

### Severity Metrics

1. **Mean score (automatic rater) under each rubric:**  
   μ_auto_A = mean of automatic rater scores, rubric A.  
   μ_auto_B = mean of automatic rater scores, rubric B.  
   Δμ = μ_auto_B − μ_auto_A. Report 95% CI via bootstrap or paired t-test.

2. **Mean score (human raters) under each rubric:**  
   μ_human_A and μ_human_B. If human ratings exist for both rubrics, report paired Δμ_human. If only one rubric has human ratings, this becomes a confound check (is human severity constant across rubrics? If not, rubric legitimately changes the task).

3. **Many-Facet Rasch Measurement (MFRM) severity parameter:**  
   Optional but recommended: fit an MFRM model (per 2608.29517) with facets: items, humans, automatic rater, and rubric variant. Extract the automatic rater's severity parameter (logit offset) under each rubric. Report the paired difference in severity logits and whether it exceeds the permutation-test threshold (family-wise α=0.05).

### Interpretation Rule
- **If δ_r ≈ 0 and Δμ > 0:** Rubric change shifted automatic rater's calibration (severity) but not structure (agreement). Conclude: **noise only**, not signal.
- **If δ_r > 0.05 (or > one small-effect size, d=0.2) and Δμ ≈ 0:** Rubric change improved agreement structure without shifting severity. Conclude: **signal**, rubric helps agreement.
- **If δ_r > 0.05 and Δμ > 0:** Both agreement and severity shifted. Investigate whether they co-vary (rubric change is holistic improvement) or are independent (rubric change hits some dimensions but not others). Use ablation (§3) to narrow down.
- **If both δ_r ≈ 0 and Δμ ≈ 0:** No detectable change under either metric. Conclude: rubric edit was null or below detection limit.

---

## 3. Ablation: Single Rubric Dimension Held Constant

### Rationale
To narrow down which rubric dimensions drive any observed agreement or severity shifts, run an ablation where the two rubric variants are forced to agree on one key dimension (e.g., both use the same definition of "clarity," but differ on "evidence weight"), or where a sub-rubric (e.g., only evaluating clarity, ignoring evidence) is scored separately.

### Ablation Design
1. **Subset of items:** All N items, or a representative subsample.
2. **Dimension held constant:** Choose one critical rubric facet (e.g., clarity is rated on a fixed scale in both rubrics A and B; evaluate agreement on the clarity sub-score alone).
3. **Dimension allowed to vary:** The other rubric differences remain.
4. **Automatic rater call:** Score the items under both rubrics, extract the constant-dimension sub-score, compute agreement on that sub-score only.

### Expected Outcome
- If agreement on the constant dimension is similar under both rubrics, the dimension is not a driver of change. Conclude: the observed effect (if any) is in the *other* dimension.
- If agreement on the constant dimension shifts, the dimension is either confounded with rubric or the rubric change affected the rater's interpretation of that dimension too. Investigate further (e.g., is severity of the constant dimension also shifting?).

### Ablation Metrics
1. Correlation of human and automatic scores on the focal dimension, under both rubrics.
2. Paired difference in that correlation; q ratio for adequacy.
3. Severity of automatic rater on that dimension alone.

---

## 4. Variance Decomposition: Where Does the Noise Come From?

### Rationale
Per 2607.13304 (Ẑatuchin 2026), variance can be partitioned into sources: within-rater resampling, rubric-variant effects, item-by-rater interactions, etc. This decomposition reveals whether noise is random (within-rater) or systematic (e.g., item-rubric interaction, where some items respond to the rubric change and others do not).

### G-Theory Model
Fit a crossed random-effects model (generalizability theory) with facets:
- **Objects:** N items  
- **Raters:** Pool of human raters (fixed or random, depending on inference target)  
- **Rubric variant:** 2 levels (A, B)  
- **Automatic-rater replicate:** K levels (k=1, 2, 3 or 5)  

Outcome: residual agreement (e.g., Fisher-z-transformed r, or QWK residuals).

### Variance Components to Report
1. **σ²_item:** Variance explained by items (do some items have inherently higher or lower agreement?).
2. **σ²_rubric:** Variance explained by rubric variant (is there a main effect of rubric?).
3. **σ²_item×rubric:** Interaction (do items respond heterogeneously to the rubric change?).
4. **σ²_replicate:** Variance explained by within-rater replication (random fluctuation per automatic-rater call).
5. **σ²_rater:** Variance explained by human-rater identity (do some humans agree better with the automatic rater?).
6. **σ²_residual:** Unexplained.

### Intraclass Correlations (ICC)
Report ICC(item, rubric, replicate | humans, automatic rater) to quantify the proportion of variance attributable to each facet. Per 2607.13304, if replication variance dominates, the noise is random; if item×rubric interaction dominates, the rubric change affects items heterogeneously.

### Decision-Study Projection
Simulate: if the study were run again with K'=1 replicate (single call, no averaging), how much would reliability drop? If it drops sharply, replication is critical; if not, noise is systematic not random.

---

## 5. Analysis Plan

### Stage 1: Data Preparation
1. Collect N items, each with human ratings under rubric A and/or B.
2. Specify the automatic-rater interface: exact prompt, system message, temperature, response format.
3. Score each (item, rubric) pair K times via the automatic rater. Log all raw responses, extracted scores, and timestamps.
4. Align scores: extract numeric or ordinal scores from automatic rater outputs; ensure rubric A and B scores are on comparable scales (e.g., both 1–5, or both percentiles).

### Stage 2: Primary Agreement Comparison
1. Compute Pearson r between automatic and human scores, per rubric, per item.
2. Aggregate: mean r across items under rubric A; mean r across items under rubric B.
3. Paired t-test: H1 vs. H_alt. Report t, df, p, effect size (Cohen's d on Fisher-z transforms).
4. Compute 95% CI on δ_r (bootstrap with 10,000 resamples, reporting bias-corrected accelerated CI).
5. Compute resolution ratio q = N / N^*. If q < 1, flag as underpowered and report the N^* needed for q=1.

### Stage 3: Severity and Rater Effects
1. Compute μ_auto_A, μ_auto_B, and Δμ. Report 95% CI via paired t-test and bootstrap.
2. If replicates available: fit MFRM model (software: Facets, R rater packages, or Python rater-effects libraries). Extract severity logits for automatic rater under each rubric.
3. Permutation test on severity shifts: shuffle rubric labels 10,000 times; compute the null distribution of Δ(severity logits). Compare observed Δ to null; report 99% permutation p-value (two-sided, family-wise).

### Stage 4: Ablation Analysis
1. Extract sub-scores for the focal dimension from automatic and human ratings.
2. Compute correlation on the sub-scores under each rubric.
3. Paired comparison and CI as in Stage 2.
4. Interpret: if ablation shows no difference (δ_r_ablation ≈ 0) but full design showed δ_r > 0, the effect is in the *other* dimensions.

### Stage 5: Variance Decomposition
1. Fit crossed REML model: outcome ~ (1 | item) + (1 | rubric) + (1 | replicate) + (1 | item:rubric) + (1 | rater) + error.
2. Extract variance components and ICC.
3. Conduct D-study: report the projected agreement correlation G if study were rerun with K'=1 (single call) instead of K.

### Stage 6: Sensitivity and Robustness
1. **Exclusion sensitivity:** Refit all Stage 2–5 analyses after removing each item in turn (jackknife). Report whether conclusions are stable.
2. **Outlier check:** Identify items with |r| > 0.99 or with extreme mean scores; refit excluding them. If conclusions are robust, report as robustness check; if not, investigate outlier cause (e.g., ambiguous rubric leading to automatic rater default behavior).
3. **Parametric vs. non-parametric:** Rerun primary test using Spearman rank correlation and permutation test (1,000 permutations) in addition to Pearson t-test. Report both; if they disagree, investigate the cause (e.g., non-linearity, heteroskedasticity).

---

## 6. Concrete Resources

### Human Ratings
**Available resource:** Existing human-rated items from prior work. Concrete: [Specify the dataset or corpus name, the number of items N, the number of human raters in the pool, the rating scale (e.g., 1–5 Likert), and which rubric(s) they used]. Example: "Essay corpus with 200 essays rated by 10 trained raters on a 6-point rubric (ENEM competencies)."

**Rationale for reuse:** Reusing existing human ratings economizes time and reduces inter-rater agreement variability introduced by untrained new raters. Per 2608.29517, trained raters have severity SD ~1/15 that of LLM judges.

### Rubric Variants
**Variant A (Baseline):** [Specify the original rubric: its dimensionality, scale, example descriptors]. Example: "5 competencies × 6 points (0–5), each dimension with level descriptors."

**Variant B (Modified):** [Specify the edits: which dimensions changed, in what way]. Example: "Competency 2 (evidence weight) descriptor clarified to exclude secondary sources; all other dimensions unchanged."

**Concrete justification:** Document why the edit was made (e.g., pilot feedback, literature, prior disagreement). Per 2606.07591 (ResearchClawBench), rubric changes must be motivated and their impact measurable.

### Automatic Rater
**Model:** Specify the LLM (e.g., "Claude-Opus-4.7," "GPT-5.4," "Gemini 3.5-Flash"). Fixed version, pinned by date and API version.

**Prompt template:** Provide the exact prompt fed to the automatic rater. Example:
```
You are an expert essay evaluator. Rate the following essay on the {RUBRIC} rubric.
Essay: {ESSAY_TEXT}
Rubric: {RUBRIC_DESCRIPTION}
Output your score on each dimension (1–5) and a brief justification.
```

**Replication:** K=3 or K=5 independent calls per (item, rubric) pair, with distinct random seeds or temperature settings to ensure variance in responses is captured.

**Cost estimate:** If using a pay-per-token API: compute tokens per item × N items × 2 rubrics × K replicates + markup. Report budget and whether it is feasible.

### Computational Environment
**Software:** Python (for analysis) or R (for MFRM). Specific packages:
- `scipy.stats` for t-tests and correlations.
- `numpy` for bootstrap (or `bootstrap` package in R).
- `statsmodels` for mixed-effects models.
- `facets` software or R `rater` packages for MFRM.

**Data storage:** CSV or JSON for all raw automatic-rater outputs; SQLite or parquet for aligned (item, human score, auto score, rubric, replicate) tuples.

---

## 7. Uncertainty Quantification

### Primary Test
**Point estimate (δ_r):** Point estimate + 95% CI (bias-corrected bootstrap, 10,000 resamples) on the paired difference in agreement correlations.

**p-value:** Two-sided t-test or permutation test (1,000 permutations). Report both if n is small (<30 items); permutation test is more robust to non-normality.

**Resolution ratio (q):** Report q and the required N^* at the target effect size. Per 2605.30315 (Kotawala 2026), if q < 1, acknowledge the design is underpowered and report the N^* + extra items needed to reach q=1.

### Severity Shift
**Point estimate (Δμ):** Difference in automatic-rater mean score between rubrics. Report 95% CI via paired t-test and bootstrap.

**Permutation p-value:** Test whether Δμ (or Δ severity logits from MFRM) exceeds the 99th percentile of the null distribution (10,000 random shuffles of rubric labels). Report as permutation p-value, family-wise α=0.05.

### Ablation
**Same metrics as primary test, for the focal dimension sub-score.**

### Variance Components
**95% CI on each ICC:** Report confidence intervals (bootstrap or likelihood-profile) on the intraclass correlations. Per 2607.13304, when data are replicated, standard errors can be computed; when data are singly replicated, use bootstrap.

**D-study projection:** Report the projected G-coefficient if K'=1 (single call) instead of K=3 or 5. Quantify the loss in reliability.

---

## 8. How to Detect and Report Uncertainty

### Underpowering
If q < 1, the design is underpowered for the observed effect size. Report:
- The observed δ_r and its 95% CI.
- The N^* required to achieve q=1 at the observed δ_r.
- The sample N actually used.
- A statement: "This design has q = [value] < 1; the true effect may be smaller than observed, and a replication with N^* = [value] items would be needed to confirm at 80% power."

### Non-normality or Heteroskedasticity
- Always report both Pearson r (parametric) and Spearman ρ (non-parametric) correlations.
- If they differ by >0.05, report both and investigate the cause (e.g., plot residuals, check for outliers).
- Use permutation test as secondary validation.

### Rater-Effect Confounds
- Report the ICC for human-rater identity. If high (>0.1), indicate that some human raters agree better with the automatic rater; this is a rater effect, not a rubric effect. Investigate whether rubric change affects all raters equally or heterogeneously.

### Missing Data
- If human ratings exist for only one rubric variant for some items, note the missing-data pattern. Impute via predictive mean matching (PMM) or report results on the complete-pairs subset only. Sensitivity-check by rerunning both ways.

### Halo and Dimension Leakage
- Per 2608.29517 (Sunkavalli 2026), LLM judges show halo (analytic sub-scores share a holistic impression). If ablation dimension shows agreement change even when rubric for that dimension is held constant, suspect halo leakage from other dimensions. Document this as a limitation; remedy via separate LLM calls per dimension (at higher cost).

---

## 9. Interpretation Rules and Conclusions

### Scenario A: δ_r ≈ 0, Δμ ≈ 0
**Conclusion:** Rubric edit changed neither agreement nor severity. The observed variance in automatic rater scores is consistent with random fluctuation or item-rater interactions unrelated to rubric wording.

**Implication:** Rubric edit was ineffective or null. Investigate:
- Is the automatic rater sensitive to rubric wording at all? (e.g., does it read the prompt or use defaults?).
- Were the items too easy/hard (ceiling/floor effects)?

### Scenario B: δ_r > 0.05 (small effect), Δμ ≈ 0
**Conclusion:** Rubric edit improved agreement structure without shifting overall calibration. Automatic rater now agrees better with humans on this rubric.

**Implication:** Rubric edit was successful. Identify which dimensions (via ablation) drove the improvement. Recommend adoption of rubric B.

### Scenario C: δ_r ≈ 0, Δμ > 0.1 SD (moderate severity shift)
**Conclusion:** Rubric edit shifted automatic rater's calibration but not structure. Rater became systematically more lenient or harsh, but agreement rank correlation unchanged.

**Implication:** Rubric edit is a "noise" intervention. If the severity shift is undesirable (e.g., pushing scores toward ceiling), rubric should be recalibrated. If calibration is inconsequential (e.g., for ranking, not absolute thresholds), accept the rubric change; otherwise reject or modify.

### Scenario D: δ_r > 0.05 and Δμ > 0.1 SD
**Conclusion:** Rubric edit affected both agreement and severity. Investigate whether the shifts are coupled or independent (e.g., via item×rubric interaction variance).

**Implication:** Rubric change is holistic (likely legitimate improvement) or fragmented (some aspects improved, others regressed). Use ablation to decompose. Recommend conditional adoption or targeted refinement.

### Scenario E: q < 1 (underpowered)
**Conclusion:** The observed effect size is too small to confirm at the current sample size.

**Implication:** Do not claim a decisive answer. Report the effect size with CI; indicate the N^* required for definitive conclusion. Recommend either (i) collect more items, or (ii) accept the uncertainty and treat the result as evidence favoring a future confirmatory study.

---

## 10. Report Deliverables

1. **Pre-registration document:** Frozen hypothesis, analysis plan, and decision rules, time-stamped before data collection.
2. **Raw data:** All automatic-rater responses, extracted scores, human ratings, aligned tuples.
3. **Analysis notebook:** Executable code (Python or R) reproducing all analyses, with inline commentary.
4. **Summary table:** Primary results (δ_r, Δμ, q, p-values, 95% CIs) in a standard format.
5. **Figures:**
   - Scatter plot: human vs. automatic scores, separate panels for rubrics A and B.
   - Box plot: automatic-rater score distributions under each rubric.
   - Variance-component bar chart: ICC for each facet (item, rubric, replicate, rater).
   - D-study frontier: projected G-coefficient as a function of K (replicates).
6. **Written report:** Interpretation of results, limitations, and recommendations. Cite evidence files (2605.30315, 2608.29517, 2607.13304, 2010.06595, 2608.03501, 2606.07591, 2609.00038) for design choices and interpretation norms.

---

## 11. Limitations and Assumptions

### Assumption: Rubric Operationalization
The rubric variants A and B are sufficiently different to be detectable by the automatic rater. If differences are cosmetic (e.g., rewording descriptors while preserving meaning), the study may be underpowered regardless of sample size. Validate rubric distinctness via expert review or pilot.

### Assumption: Human Ratings Ground Truth
Human ratings are treated as ground truth. If human ratings themselves are low-quality or biased, the comparison will be noisy. Recommend human-rater training and inter-rater-agreement checks prior to main study.

### Assumption: Automatic Rater Consistency
The automatic rater is assumed to be a single, fixed model. Version changes (e.g., API updates, fine-tuning) invalidate the comparison. Pin the model version and monitor for drift via identity canaries (e.g., score a fixed 5-item reference set weekly).

### Assumption: Item Sample Representativeness
The N items are assumed to be representative of the target population. If items are cherry-picked (e.g., only easy items), generalization is limited. Randomize item selection or use stratified sampling on item difficulty/domain.

### Assumption: Stability Under Rubric Scaling
If rubric A and B use different scales (e.g., A is 1–5, B is 1–10), alignment is needed (e.g., normalization, z-scoring). Document any scale transformation and validate that it does not introduce artifacts (e.g., proportional scaling introduces artificial correlation).

---

## 12. Time and Resource Feasibility

### Time Estimate
- **Setup (rubric specification, prompt design):** 1–2 weeks.
- **Automatic rater calls:** 1 week (depends on API rate limits; K=3 × N × 2 calls).
- **Data curation and cleaning:** 1 week.
- **Analysis:** 1–2 weeks (Stage 1–6, including MFRM fitting).
- **Writing and reporting:** 1 week.
- **Total:** ~6–9 weeks (assumes no major delays or model unavailability).

### Cost Estimate
- **API calls:** K × N × 2 × cost-per-1k-tokens. Example: if K=3, N=100, cost is $0.01 per 1k tokens, and average response is 500 tokens, cost ≈ $3 per item; $600 total for 100 items.
- **Human time (analysis):** ~5–10 person-days.
- **Compute (MFRM, bootstrap):** Negligible (minutes to hours).

### Critical Path Dependency
- **Blocker:** Availability of existing human-rated items. If no data exist, collect via crowdsourcing (Mechanical Turk, Prolific) or hire trained raters (~$5–15 per essay, depending on complexity).
- **Blocker:** Automatic-rater API access and stability. Ensure account has sufficient quota and that API is stable during collection window.

---

## Summary

This design detects whether a rubric edit changed the **systematic agreement** between human and automatic raters, disentangling such changes from **noise** (variance without signal). It uses a **paired design** (per 2605.30315, 2–3× more efficient than unpaired) on the same items, **replicates** automatic-rater calls (per 2607.13304) to separate random from systematic variance, **decomposes rater effects** via MFRM and G-theory (per 2608.29517, 2607.13304) to identify severity and halo, includes an **ablation** (per 2608.03501) to narrow down which rubric dimensions drive changes, and reports **power and resolution ratios** (per 2010.06595, 2605.30315) to quantify uncertainty. The sampling frame is explicit: (item, human rater, automatic rater, rubric variant, replicate), enabling transparent reconstruction and replication.
