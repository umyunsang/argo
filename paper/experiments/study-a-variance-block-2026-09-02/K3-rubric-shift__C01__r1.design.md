# Experimental Design: Detecting Rubric Change vs. Noise in Human-Automatic Rater Agreement

## Executive Summary

This design distinguishes whether editing a scoring rubric changed agreement between human raters and an automatic rater, or merely changed the noise profile. It uses the same set of items scored under both rubric variants and isolates rubric effects from five concurrent sources of variance: within-rater resampling, rater severity drift, rater halo, automatic-rater version instability, and measurement error. 

The approach decomposes observed agreement changes into signal (true difference in the rubric's fit to automatic-rater performance) and noise (variance attributed to the sources above), using paired variance-component analysis and a resolution-diagnostic workflow. A minimum detectable effect (MDE) calculation gates the design to ensure adequate power. Two pre-registered ablations isolate rubric effects from automatic-rater instability and human rater drift.

---

## 1. Research Question and Hypotheses

**Primary Research Question:**  
Does editing the rubric change agreement between human raters and the automatic rater, or is the observed change in agreement attributable to measurement noise?

**Operationalization:**  
- **Signal:** A stable, rubric-specific shift in the correlation (or intra-class agreement coefficient) between human consensus and automatic scores, conditioned on rater-effect correction.
- **Noise:** Variance from rater severity, halo, within-prompt resampling, automatic-rater version drift, and random fluctuation.

**Hypotheses:**

- **H1 (Rubric Specificity):** Agreement change is larger when comparing rubric A vs. rubric B on the same items than when comparing rubric A vs. a resampled variant of rubric A (internal consistency check).
- **H2 (Effect Persistence):** The agreement difference survives correction for rater severity and halo (testing that we are not confounding rubric effects with rater effects).
- **H3 (Automatic-Rater Stability):** The automatic rater's scores are stable across the experimental period (testing that version drift is not masking or inflating rubric effects).

**Null Hypotheses (Pre-registered):**
- **N1:** Agreement under rubric A = agreement under rubric B after severity correction.
- **N2:** Agreement change is entirely attributable to within-rater resampling variance.

---

## 2. Main Comparison and Experimental Conditions

### 2.1 Design Structure

**Design Type:** Fully paired, crossed, repeated-measures design.

**Factors:**
1. **Rubric** (2 levels: A, B) — the primary factor of interest.
2. **Item** (n levels: 20–50 items recommended, see §3 for allocation reasoning) — sampled randomly without replacement from a corpus.
3. **Human Rater** (k levels: 3–5 raters) — a fixed, limited panel of trained raters.
4. **Replication Within Rater** (r = 3–5 times per rater-rubric-item cell) — to estimate within-rater resampling variance.
5. **Automatic Rater Call** (1 per condition) — a single frozen version of the automatic system scored on each item under each rubric.

### 2.2 Cells and Data Collection

- **Total Scoring Events:** (Items) × (Rubrics) × (Raters) × (Replications) = n × 2 × k × r.
  - For n=30, k=4, r=3: 720 human-rater scoring events.
  - Each item is also scored once under each rubric by the frozen automatic rater (2 automatic scores per item).

### 2.3 Item Corpus

- **Source:** A set of publicly-available, benchmark-grounded items with clear, fixed ground truth or high inter-annotator agreement at baseline. Examples: ASAP essay prompts (Hewlett Foundation, 2012, as referenced in evidence 2608.29517), or a curated subset of writing samples with existing human-consensus scores.
- **Size:** 30 items minimum, 50 preferred (see power calculation in §3).
- **Stratification:** If possible, stratify by quality quartile (low, mid-low, mid-high, high) to ensure rubric changes are tested across the performance range.
- **Justification:** Ensures items are stable references; eliminates item-level confounds (e.g., items that are inherently easy or hard to score).

### 2.4 Rubric Variants

- **Rubric A (Baseline):** The original rubric.
- **Rubric B (Experimental):** The edited rubric.
- **Version Control:** Both frozen before data collection; versions, edit dates, and edit rationale logged in a pre-registered protocol.
- **Blinding:** Raters blind to which rubric is which during scoring, to prevent expectancy effects. (Label the rubrics as "Variant 1" and "Variant 2.")

### 2.5 Rater Training and Anchoring

- **Anchor Essays:** Prepare 10–15 essays (disjoint from the 30–50 evaluation items) scored with both rubrics and achieving high human agreement (ICC ≥ 0.75 at baseline).
- **Training Protocol:** Each rater independently scores all anchor essays under both rubric variants, then discusses disagreements with a facilitator to align on rubric interpretation. (Evidence 2608.29517 confirms that 30–100 anchor essays recover most recoverable calibration error.)
- **Baseline Severity:** Use anchor-score distributions to establish a severity reference for each rater under each rubric. This allows pre-registered severity-correction analysis.

---

## 3. Sample Size and Power Calculation

### 3.1 Minimum Detectable Effect (MDE) and Required N

**Framework:** Based on evidence 2605.30315 (resolution diagnostics for paired evaluation), we compute the required paired sample size for a given target effect size using:

$$N^* = \left(rac{z_{1-lpha/2} + z_{1-eta}}{\delta}
ight)^2 \sigma_D^2$$

where:
- $\delta$ = target rubric-effect size (standardized agreement change).
- $\sigma_D^2$ = paired variance of agreement scores under the two rubrics.
- $lpha$ = 0.05 (Type I error rate, two-tailed).
- $eta$ = 0.20 (Type II error rate; target power 1 − β = 0.80).
- $z_{1-lpha/2} pprox 1.96$, $z_{1-eta} pprox 0.84$.

**Reasonable Assumptions for Rubric Change:**
- Rubric edits typically shift agreement correlations by 0.05–0.15 (based on educational measurement norms; evidence 2010.06595 documents that underpowered NLP evaluation is widespread, recommending power ≥ 0.80).
- Paired variance $\sigma_D pprox 0.10–0.12$ (conservative estimate for essay-scoring contexts; evidence 2608.29517 reports agreement SDs of 8–15% of scale range).
- For δ = 0.10 and σ_D = 0.11, solving gives **N* ≈ 19 items**.
- **Conservative target: 30 items** (1.6× the theoretical N*) to account for clustering and finite-sample residual.

### 3.2 Rater Replications

- **Within-Rater Repeats:** r = 3 repeats per rater-rubric-item cell.
- **Rationale:** Evidence 2607.13304 (variance components for LLM responses) shows that beyond r = 5, marginal variance reduction drops to ~0.0003 per additional repeat. Three repeats buys stability without over-sampling.
- **Rater Panel Size:** k = 4 raters (minimum; 5 preferred for robustness against rater dropout).

**Total Events:** 30 items × 2 rubrics × 4 raters × 3 repeats = **720 human-rating events**.

### 3.3 Automatic Rater Sampling

- **Automatic Rater Calls:** One call per (item, rubric) pair under a frozen model version. Total: 30 items × 2 rubrics = 60 automatic scores.
- **Version Pinning:** Pin the automatic rater version (model, serving environment, temperature, prompt template) and freeze it before data collection. (Evidence 2608.29517 documents version shifts up to 133 points on a 1000-point scale; controlling this is critical.)

---

## 4. Ablation Studies

### 4.1 Ablation 1: Rubric Specificity vs. Resampling Noise (Robustness Check)

**Hypothesis H1 Test:**

- **Design:** On 10 items selected randomly from the 30, ask one rater to score the same item under rubric A a second time (resampling under the same rubric).
- **Comparison:**
  - Within-rubric resampling variance: variance(Rubric A, Sample 1 vs. Sample 2) for the same rater and item.
  - Across-rubric variance: variance(Rubric A vs. Rubric B) for the same rater and item.
- **Prediction (H1):** Across-rubric variance > within-rubric resampling variance (e.g., ratio ≥ 1.5).
- **Falsification:** If across-rubric variance < within-rubric variance, rubric differences are not the dominant source.
- **Cost:** 10 items × 1 rater = 10 additional scoring events.

**Citation:** Evidence 2607.13304 documents the variance-components decomposition methodology used here.

### 4.2 Ablation 2: Automatic-Rater Stability and Version Drift

**Hypothesis H3 Test:**

- **Design:** Re-score 20 items (a subset of the 30) with the frozen automatic rater at the end of the study, separated by ≥2 weeks from the initial automatic scoring.
- **Comparison:** Correlation between initial and repeated automatic scores on the 20 items.
- **Prediction (H3):** Correlation ≥ 0.95 (allowing ≤5% score drift; evidence 2608.29517 observed version shifts of up to 13% of scale).
- **Falsification:** If correlation < 0.90, automatic-rater instability is confounding the comparison.
- **Cost:** 20 items × 2 rubrics = 40 automatic-rater calls.

**Citation:** Evidence 2608.29517 and 2605.30315 establish the importance of monitoring automatic-rater stability.

### 4.3 Ablation 3: Severity and Halo Correction (Rater Effects)

**Hypothesis H2 Test:**

- **Design:** Fit a many-facet Rasch model (MFRM) to the full data, extracting rater severity and halo parameters for each rater under each rubric.
- **Comparison:**
  - Unadjusted agreement: correlation(human consensus, automatic score) on original scale.
  - Severity-adjusted agreement: correlation(severity-corrected human consensus, automatic score).
  - Halo-adjusted agreement: as above, but removing the halo component from analytic sub-scores (if applicable).
- **Prediction (H2):** Adjusted agreement change ≈ unadjusted agreement change (i.e., rater effects do not confound the rubric comparison).
- **Falsification:** If adjusted agreement change is much smaller than unadjusted (e.g., >50% reduction), rater effects are masking or inflating the rubric difference.

**Citation:** Evidence 2608.29517 introduces MFRM for isolating severity, halo, and rater-by-context interactions in essay scoring.

---

## 5. Analysis Plan

### 5.1 Primary Outcome: Paired Agreement Change

**Estimand:**  
$$\Delta_{agreement} = r(H_B, A_B) - r(H_A, A_A)$$

where:
- $r(H_A, A_A)$ = correlation between human consensus (under rubric A) and automatic score (under rubric A).
- $r(H_B, A_B)$ = correlation between human consensus (under rubric B) and automatic score (under rubric B).
- Consensus is the median or mean of the k raters' replications, averaged over replications.

**Test Statistic:**  
Fisher-transformed paired z-test on the correlations; or paired t-test on per-item agreement residuals. (Justification: Evidence 2605.30315 shows that paired tests are 2–3× more efficient than unpaired tests on leaderboard comparisons; the same efficiency gain applies here.)

**Multiplicity Control:**  
Bonferroni correction for H1, H2, H3, and the primary test (4 tests) at family-wise α = 0.05, yielding per-test α = 0.0125.

### 5.2 Secondary Outcomes: Variance Components and Resolution Diagnostic

**Variance Decomposition** (Evidence 2607.13304):  
Fit a crossed random-effects model:

$$Y_{ijlm} = \mu + R_i + I_j + (RI)_{ij} + L_l + E_{ijlm}$$

where:
- $Y_{ijlm}$ = score by rater i, item j, rubric l (or automatic), replication m.
- $R_i$ = rater effect (severity).
- $I_j$ = item difficulty/quality effect.
- $(RI)_{ij}$ = rater-by-item interaction (halo/idiosyncratic fit).
- $L_l$ = rubric effect (main estimand).
- $E_{ijlm}$ = residual (within-rater resampling variance).

**Intra-Class Correlations (ICCs):**  
Report ICC(2,1) (consistency) and ICC(3,k) (absolute agreement with k raters), separately for each rubric and pre/post severity correction.

**Resolution Ratio** (Evidence 2605.30315):  
For the primary outcome (agreement change), compute:

$$q = rac{N}{N^*(\Delta_{agreement})}$$

where N* is the required sample size to detect $\Delta_{agreement}$ at (α, 1−β) = (0.05, 0.80). If q < 1, the experiment is underpowered to resolve that effect.

### 5.3 Severity and Halo Analysis

**Many-Facet Rasch Model** (Evidence 2608.29517, §2–3):

Fit MFRM separately for each rubric:
- **Rater Severity Calibration:** Estimate rater-by-rubric severity shifts (logits, then back-scaled to score units).
- **Halo Detection:** Compute residual correlations between item-level ratings and a global impression (mean across all raters), stratified by rater. Halo present if residual correlation is substantial.
- **Re-equating:** Apply severity adjustments to human consensus scores; recompute agreement correlations.

**Validity Check (H2):**  
Compare the original-scale and severity-adjusted agreement changes:

$$rac{\Delta_{agreement}^{adjusted}}{\Delta_{agreement}^{unadjusted}}$$

Threshold for H2 acceptance: ratio ∈ [0.8, 1.2] (i.e., rater effects do not alter the rubric conclusion by >20%).

### 5.4 Uncertainty Quantification

**Confidence Intervals:**
- **Agreement Change:** 95% CI via Fisher transformation (parametric) or percentile bootstrap (1000 resamples, stratified by item).
- **Variance Components:** Bootstrap CI on ICC and variance-component ratios (Satterthwaite or permutation method).
- **Minimum Detectable Effect:** Report the smallest true rubric effect the design can resolve at 80% power given observed variance ($\delta_{MDE}$).

**Power Assessment:**
- Post-hoc power calculation for the observed effect size using the observed variance from the paired data.
- If observed power < 0.60, flag as underpowered; recommend larger sample or tighter control of rater variance.

---

## 6. Concrete Resources and Data Provenance

### 6.1 Item Corpus

**Source:** ASAP (Automated Student Assessment Prize) Corpus  
- **Reference:** Hewlett Foundation (2012), via Kaggle. <https://www.kaggle.com/c/asap-aes/data>
- **Why:** Public, benchmark-standard, reproducible; essays have published human-consensus scores; established baseline rubrics.
- **Alternative:** Essay-BR corpus (Marinho et al., 2021) if Portuguese-language work is needed; also public and cited in evidence 2608.29517.
- **Sampling:** Select 30–50 essays stratified across the score range from one of ASAP's eight essay sets (each with 1,200–4,100 essays).

### 6.2 Rubric Variants

- **Rubric A:** A published, baseline rubric (e.g., the original ASAP task rubric for that essay set, or a simplified version used in prior work).
- **Rubric B:** An edited version of Rubric A, with documented changes:
  - Document the specific criteria added, removed, or reworded.
  - Provide a change log with rationale (e.g., "Criterion 2.1 clarified to distinguish X from Y based on pilot findings").

### 6.3 Automatic Rater (Baseline)

- **Model:** A publicly available, fixed-version essay scoring model. Options:
  - **Claude-3.5-Sonnet** (Anthropic, 2024) — pinned to a specific version, scored via API with temperature=0.
  - **GPT-4o** (OpenAI, 2024) — pinned to a specific release.
  - **Llama-3-70B** (Meta, 2024) — via a cloud provider with fixed weights.
  - **Choice Rationale:** The specific model is less important than **version pinning** and **prompt template freezing**. (Evidence 2608.29517 documents that version upgrades (e.g., Claude Sonnet 4.0 → 4.5) shift essay scores by up to 133 points, and one model was legacy-gated mid-study.)
- **Prompt Template:** Freeze a single prompt that instructs the model to score an essay under the given rubric, returning a structured output (score, sub-scores, confidence). Log the prompt verbatim.
- **Implementation Detail:** No in-context examples in the prompt (to avoid confounding rubric effects with example order). If examples are necessary, keep them constant across rubrics.

### 6.4 Analysis Software

- **Variance Components & MFRM:** Use `facetwise` (R/Python), `lavaan` (R SEM), or `lme4` (R linear mixed models) for random-effects estimation. MFRM software: Linacre's **WINSTEPS** (standalone, commercial but widely licensed in universities) or **eRm** (R package, free).
  - **Evidence:** Evidence 2607.13304 uses REML fits; evidence 2608.29517 uses Linacre's MFRM.
- **Power & Resolution Diagnostics:** `statsmodels` (Python) or `pwr` (R) for power curves. For the resolution ratio q (evidence 2605.30315), implement the inversion formula directly or use the authors' reference Python package: `llm-power` (available at <https://github.com/ananykotawala/llm-power>).
- **Visualization & Reporting:** R/Python (ggplot2, matplotlib) for plots of variance components, severity-by-rubric, and agreement-by-item.

---

## 7. Outcome Metrics and Acceptance Criteria

### 7.1 Primary Outcome Metric

**Name:** Rubric-Adjusted Agreement Change (Severity-Corrected)

**Definition:**  
$$\Delta_{agreement}^{adj} = r(H_B^{adj}, A_B) - r(H_A^{adj}, A_A)$$

where $H^{adj}$ denotes severity-corrected human consensus.

**Acceptance Criterion (H1):**  
- **Primary:**  $|\Delta_{agreement}^{adj}| > \delta_{MDE}$ (minimum detectable effect, computed in §3).
- **Success:** If $\Delta_{agreement}^{adj} > 0$ and statistically significant at α = 0.0125 (Bonferroni-corrected), conclude that Rubric B increases agreement with the automatic rater.
- **Failure (Null Confirmed):** If $\Delta_{agreement}^{adj}$ is not significantly different from zero at α = 0.0125, or if |$\Delta_{agreement}^{adj}$| < (noise estimate from Ablation 1), conclude that agreement change is attributable to noise.

### 7.2 Ablation 1 Outcome: Rubric Specificity

**Definition:**  
$$	ext{Ratio} = rac{	ext{Var}(	ext{Rubric A vs. B})}{	ext{Var}(	ext{Rubric A resample})}$$

**Acceptance Criterion (H1):**  
- **Success:** Ratio > 1.5, indicating that rubric differences dominate within-rubric resampling variance.
- **Falsification:** Ratio ≤ 1.0, indicating rubric change is smaller than resampling noise.

### 7.3 Ablation 2 Outcome: Automatic-Rater Stability

**Definition:**  
$$r(	ext{Automatic scores at t=0}, 	ext{Automatic scores at t=end})$$

**Acceptance Criterion (H3):**  
- **Success:** r > 0.95 (≤5% drift over study duration).
- **Falsification:** r < 0.90 (>10% drift; confounds the analysis).
- **Note:** If r ∈ [0.90, 0.95], flag as "caution"; report drift as a sensitivity analysis.

### 7.4 Ablation 3 Outcome: Rater-Effect Correction

**Definition:**  
$$	ext{Severity Confounding Ratio} = rac{\Delta_{agreement}^{adjusted}}{\Delta_{agreement}^{unadjusted}}$$

**Acceptance Criterion (H2):**  
- **Success:** Ratio ∈ [0.8, 1.2], indicating rater effects do not materially change the conclusion.
- **Falsification:** Ratio < 0.5 or > 2.0, indicating rater effects or halo are confounding the rubric comparison.

### 7.5 Secondary Metrics

**Variance Allocation:**
- Fraction of total variance attributable to: items, raters, rater-by-item, rubric, and residual.
- Interpretation: If rubric variance is <5% of total, rubric change is minor relative to other sources.

**Rater Severity Spread** (Evidence 2608.29517):
- Range of rater severity estimates (in score units or logits) under each rubric.
- Interpretation: If severity spread widens dramatically under Rubric B (e.g., doubles), rubric clarity may be degraded.

---

## 8. Research Protocol and Pre-Registration

### 8.1 Pre-Registration Checklist

Before any data collection or scoring:
1. **Freeze Rubric Wording:** Finalize Rubric A and Rubric B; document all changes.
2. **Freeze Item List:** Specify the 30–50 items by ID; log the corpus source.
3. **Freeze Automatic-Rater Version:** Document model name, version, API endpoint, prompt template, and temperature setting.
4. **Register Hypotheses & Acceptance Criteria:** File a pre-registration (e.g., on OSF Registries or the AsPredicted template) specifying:
   - The three hypotheses (H1, H2, H3) and their tests.
   - Multiplicity control (Bonferroni, 4 tests).
   - Per-test α threshold (0.0125).
   - Sample size justification (power calculation from §3).
   - The three ablations and their acceptance criteria.
5. **Data Dictionary & Codebook:** Specify the exact format of all recorded variables (rater ID, item ID, rubric, score, replication number, timestamp).
6. **Analysis Code Template:** Pre-register the R/Python scripts for variance decomposition, MFRM fitting, and resolution diagnostics (pseudocode or skeleton; specific parameters to be filled in once data is received).

### 8.2 Deviations Log

If the data collection deviates from the pre-registered plan (e.g., one rater drops out, one item is withdrawn), document the deviation:
- **Date of Deviation:** When was it discovered?
- **Reason:** Why the deviation occurred.
- **Impact:** Which hypotheses or analyses are affected?
- **Mitigation:** How will the analysis be adjusted? (e.g., imputation, subgroup analysis, sensitivity check.)

**Evidence Support:** Evidence 2608.29517 reports their deviations log transparently; evidence 2608.03501 emphasizes the importance of stage isolation and explicit protocol deviations.

---

## 9. Threat to Validity and Mitigation Strategies

### 9.1 Threat: Rater Expectancy Effects

**Risk:** Raters unconsciously produce different severity under different rubrics because they expect one rubric to produce higher/lower scores.

**Mitigation:** Blind raters to the rubric identity (label as "Variant 1" and "Variant 2"). Randomize the order in which each rater encounters the two rubrics across items.

### 9.2 Threat: Item-by-Rubric Interaction

**Risk:** Some items may be inherently more sensitive to the rubric change than others, confounding the overall comparison.

**Mitigation:** In the analysis (§5.2), estimate the (rubric-by-item) interaction variance. If substantial (>20% of total variance), report item-stratified effects and recommend larger sample for precise estimation.

### 9.3 Threat: Automatic-Rater Instability

**Risk:** Version drift or API changes mid-study confound the comparison (evidence 2608.29517 documents this risk empirically).

**Mitigation:** Ablation 2 (§4.2) monitors this directly. Additionally, version-pin the automatic rater and re-score the stability set every 1–2 weeks.

### 9.4 Threat: Limited Rater Generalization

**Risk:** The k raters used are not representative of a broader population of expert scorers; findings may not generalize.

**Mitigation:** Report the rater variance component separately. Conduct a generalizability study (evidence 2608.29517 §5 and evidence 2607.13304 §4) projecting the reliability of the agreement estimate under different numbers of raters.

### 9.5 Threat: Low Absolute Agreement

**Risk:** Even if agreement improves under Rubric B, the absolute level remains too low for practical use (e.g., r < 0.60 with automatic raters).

**Mitigation:** Report both $\Delta_{agreement}$ and the absolute agreement levels under each rubric. Interpret the rubric effect in context of whether agreement is above a predefined threshold (e.g., ICC ≥ 0.65 for practical deployment).

---

## 10. Reporting and Output Artifacts

### 10.1 Pre-Registration Document

- **Format:** OSF Registries or AsPredicted template.
- **Contents:** Hypotheses, acceptance criteria, sample size justification, planned analyses, deviations protocol.
- **Public URL:** Register publicly before any scoring begins.

### 10.2 Data and Analysis Report

- **Main Report** (journal-style):
  - Results of H1, H2, H3 hypothesis tests, with α values and confidence intervals.
  - Variance-component table (ICC by rubric, rater severity ranges).
  - Resolution diagnostic (q ratio for the primary outcome).
  - Interpretation: Is agreement change signal or noise?

- **Supplementary Materials:**
  - Full MFRM parameter estimates (rater severity, fit residuals).
  - Severity-adjusted agreement by item.
  - Bootstrap CI plots for key estimates.
  - Sensitivity analyses (e.g., agreement under different ICC definitions, agreement with different subsets of raters).

- **Reproducibility Artifacts:**
  - Cleaned dataset (with item IDs, rater IDs, rubrics, scores, timestamps).
  - Analysis code (R/Python scripts, version-pinned).
  - Pre-registration document and deviations log.
  - All raw outputs (variance components, model fits, plots).

### 10.3 Evidence Citations in Reporting

When reporting, cite the evidence base:
- **On Rater Effects & Severity:** Evidence 2608.29517 (Sunkavalli) for the MFRM framework and rater-effects decomposition.
- **On Power & Resolution:** Evidence 2605.30315 (Kotawala) for paired-test power calculation and resolution diagnostics.
- **On Variance Components:** Evidence 2607.13304 (Zatuchin) for the generalizability-theory allocation.
- **On Experimental Design Methodology:** Evidence 2608.03501 (Liu et al.) for the structure of main/ablation/analysis experiments and redline mechanisms.
- **On Fundamental Power Norms:** Evidence 2010.06595 (Card et al.) for the baseline power-analysis framework and common pitfalls in NLP evaluation.

---

## 11. Timeline and Resource Plan

### 11.1 Pre-Study Phase (1–2 weeks)

1. Finalize and register rubrics A and B. (Days 1–2)
2. Assemble 30–50 items and confirm automatic-rater version. (Days 3–5)
3. Prepare anchor essays and create rater training materials. (Days 6–8)
4. Register hypotheses and analysis plan on OSF or AsPredicted. (Days 9–10)
5. Pilot test: 1–2 raters score 5 pilot items under both rubrics; assess anchor-agreement quality. (Days 11–14)

### 11.2 Data Collection Phase (2–4 weeks)

1. Rater training on anchors (Day 1–2).
2. Raters score all 30 items under Rubric A, r=3 replications. (Days 3–7)
3. Raters score all 30 items under Rubric B, r=3 replications. (Days 8–12)
4. Automatic rater: score all 30 × 2 rubric combinations in parallel (Day 2–12, overnight runs).
5. Ablation 1: one rater resamples 10 items under Rubric A (Days 13–14).
6. Stability check (Ablation 2): store automatic rater outputs; plan re-scoring in 2–3 weeks.

### 11.3 Analysis Phase (1–2 weeks)

1. Data cleaning, codebook, and QA checks. (Days 1–3)
2. Compute consensus scores, inter-rater agreement baselines. (Days 4–5)
3. Variance-component estimation (REML fit). (Days 6–7)
4. MFRM fitting and severity correction. (Days 8–9)
5. Hypothesis tests, ablation analyses, visualization. (Days 10–12)
6. Sensitivity checks and interpretation. (Days 13–14)

### 11.4 Resources

- **Estimated Budget:** ~$1,000–$3,000 USD (depending on labor costs and automatic-rater API charges).
  - Human rater compensation: ~$500–$1,500 (4 raters × 720 scoring events ÷ ~20 events/hour × $15–$25/hour).
  - Automatic-rater API calls: ~$60–$200 (60 + 40 + 20 retest calls, depending on model/pricing).
  - Software: Free (R, Python, open-source packages) or university-licensed (WINSTEPS for MFRM, ~$500 if not already available).
  - Data storage & analysis time: Included in labor.

- **Personnel:** 1–2 analyst/researchers (design, data management, analysis) + 1 coordinator (rater recruitment, training).

---

## 12. Expected Outcomes and Implications

### 12.1 Interpretation Table

| Primary Outcome ($\Delta_{agreement}^{adj}$) | Ablation 1 (Specificity) | Ablation 3 (Rater Effects) | Conclusion |
|---|---|---|---|
| Δ > 0, significant | Ratio > 1.5 | Ratio ∈ [0.8, 1.2] | **Rubric B improves agreement.** Signal > noise. |
| Δ ≈ 0, not significant | Ratio < 1.5 | Any | **Rubric change does not affect agreement.** Null H1 confirmed. |
| Δ < 0, significant | Ratio > 1.5 | Ratio ∈ [0.8, 1.2] | **Rubric B degrades agreement.** Signal > noise; reconsider Rubric B. |
| Δ > 0, not significant; resolution q < 1 | Ratio > 1.5 | Any | **Underpowered.** Rubric effect unresolved; recommend larger sample. |
| Δ > 0, significant | Any | Ratio ∉ [0.8, 1.2] | **Confounded by rater effects.** Severity or halo changes, not rubric fit. Recommend rubric clarification. |

### 12.2 Dissemination

- Publish in a venue accepting methodological papers on evaluation (e.g., *ACL Findings*, *EMNLP Findings*, *Journal of Learning Analytics*, or a specialized rubric-and-assessment venue).
- Cite evidence base (evidence 2608.29517, 2605.30315, 2607.13304, 2010.06595, 2608.03501) prominently.
- Release data, code, and pre-registration publicly (OSF, GitHub).
- Present rubric-editing best practices derived from findings.

---

## Summary Checklist

- [ ] **Design frozen:** Rubrics A, B; item list (n=30–50); automatic-rater version pinned.
- [ ] **Pre-registration filed:** Hypotheses, acceptance criteria, sample size, analysis plan, deviations protocol.
- [ ] **Sample size justified:** Power calculation (N* ≈ 19, target 30); MDE reported.
- [ ] **Variance sources decomposed:** Within-rater resampling, rater severity, halo, automatic-rater stability, residual.
- [ ] **Ablations planned:** Rubric specificity (Ablation 1), automatic-rater stability (Ablation 2), severity correction (Ablation 3).
- [ ] **Analysis tools identified:** MFRM software, variance-component estimation, resolution diagnostics.
- [ ] **Uncertainty quantified:** Confidence intervals (Fisher transform, bootstrap), power assessment, MDE.
- [ ] **Threats mitigated:** Rater blinding, item stratification, version pinning, generalizability study.
- [ ] **Reporting artifacts specified:** Pre-registration, main report, supplementary analyses, reproducibility artifacts, code and data.
- [ ] **Evidence citations logged:** All references to evidence files (2608.29517, 2605.30315, 2607.13304, 2010.06595, 2608.03501) documented.

---

## Evidence Sources Cited

1. **2608.29517** (Sunkavalli, 2026): LLM judges as raters; rater severity, halo, MFRM framework, version instability.
2. **2605.30315** (Kotawala, 2026): Resolution diagnostics for paired evaluation; minimum detectable effect, paired vs. unpaired power, resolution ratio q.
3. **2607.13304** (Zatuchin, 2026): Variance components for LLM responses; crossed random-effects decomposition, generalizability theory, allocation decision studies.
4. **2010.06595** (Card et al., 2020): Statistical power norms in NLP; power analysis methodology, simulation-based approach, Type-M and Type-S errors.
5. **2608.03501** (Liu et al., 2026): Experimental design for AI research; high-level planning (main, ablation, analysis experiments), low-level configuration, stage isolation, redline scoring.

Additional supporting references (consulted but not the primary foundation):
- **2609.00038** (Mohammadi, 2026): Outcome-only evaluation blind spots; warns against measuring only final outcomes without process tracing.
- **2606.07591** (Shanghai AI Lab, 2026): Rubric-based scoring in autonomous research; illustrates the importance of clear, validated rubrics for evaluation.

---

*Design Document Version: 1.0*  
*Date: [Today's Date]*  
*Status: Ready for Pre-Registration*
