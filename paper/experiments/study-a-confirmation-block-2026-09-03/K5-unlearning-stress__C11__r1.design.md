# Experimental Design: Auditing Unlearning Procedures via Multi-Pathway Knowledge Recovery

## 1. Core Research Question & Falsifier

**Question:** Does a purported unlearning procedure produce genuine knowledge removal, or does it merely suppress observable output while preserving hidden access to the targeted knowledge?

**Falsifier:** If across all test procedures (direct queries, adversarial prompts, logit probes, extraction) no statistically significant difference is detected between an unlearned model and control, the design's premise is refuted.

---

## 2. Sampling Frame & Population

**Sampling Frame** (per state.md):
- **Population:** Language models claimed to have undergone unlearning of a target knowledge domain
- **Unit of analysis:** A single (model, knowledge_form, test_procedure) triplet
- **Knowledge forms:** 
  - (a) Factual recall: Direct factual questions about target domain (e.g., "Who wrote [copyrighted work]?")
  - (b) Derived reasoning: Multi-hop reasoning over facts in the target domain
  - (c) Latent representation access: Logit probes and hidden-state analysis
  - (d) In-context retrieval: Few-shot extraction attempts where examples prime the model to produce target knowledge
- **Test procedures:**
  - (i) Direct natural queries: Straightforward, benign questions
  - (ii) Adversarial/jailbreak prompts: Role-plays, hypotheticals, indirect phrasing (adapted from jailbreak literature)
  - (iii) Logit probe access: Linear classifiers trained on model internals to detect target knowledge presence
  - (iv) Generation-based extraction: Few-shot exemplars designed to elicit target knowledge without explicit requests
- **Scope:** Accessible via public APIs or released weights; queries cost-bounded to <$500 per model under test
- **Candidate models:** Up to 4 model instances (2 unlearning procedures + 2 controls or variants)

---

## 3. Main Comparison & Conditions

### 3.1 Comparison Structure

**Primary Comparison (within-subjects design):**
Compare unlearned model(s) to controls across test procedures and knowledge forms.

**Conditions:**
1. **Control-Base:** Original base model before any unlearning (e.g., Llama 3.1 70B)
2. **Unlearned-RFU:** Model after Representation Forgetting Unlearning (RFU)
3. **Unlearned-SISA:** Model after Selective Isotropic Scaling Adapters (SISA) or task-vector unlearning
4. **Unlearned-Ablation (See Section 4):** Partial unlearning or differently-targeted unlearning to isolate which knowledge forms are affected

**Comparison matrix:**
```
                 Direct Query | Jailbreak Prompt | Logit Probe | Few-Shot Extract
Factual Recall       ✓              ✓                ✓              ✓
Derived Reasoning    ✓              ✓                ✓              ✓
Latent Access        —              —                ✓              —
In-Context Ret.      —              —                —              ✓
```

Each cell represents an independent test outcome.

---

## 4. Ablation Study: Isolating Knowledge Forms

**Ablation Goal:** Determine whether unlearning removes all knowledge forms equally or whether removal is selective (e.g., factual recall is removed but derived reasoning or latent access remain).

**Ablation Condition:**
- Apply selective unlearning targeting only factual recall (e.g., via fine-tuning on factual questions alone, or via targeted representation editing)
- Compare this to full-domain unlearning

**Rationale:** Evidence from 2607.18508 ("Style over Substance") demonstrates that removing one shortcut (e.g., generator identity) does not eliminate others (e.g., length bias). Similarly, removing overt factual recall may not remove latent knowledge or reasoning chains. This ablation tests whether knowledge forms are independently removable.

**Expected Finding:** If unlearning is robust, we expect similar removal across forms. If selective, we expect recovery rates to differ significantly by form, suggesting that the unlearning procedure has missed some pathways.

---

## 5. Analysis Plan & Outcome Metrics

### 5.1 Primary Outcome Metrics

For each (model, knowledge_form, test_procedure) triplet, measure:

1. **Knowledge Recovery Rate (KRR):** Proportion of queries where the model produces responses consistent with the target knowledge.
   - For factual queries: % of correct/relevant answers
   - For jailbreak: % of queries where the model complies and produces target knowledge
   - For logit probes: prediction accuracy of linear classifier trained on model representations
   - For few-shot extraction: % of shots where target knowledge is produced

2. **Variability/Consistency:** 
   - Repeat each query 5 times to the same model instance; measure within-model SD of recovery rate
   - Expected: if knowledge is removed, variability should be low (consistently below 15%)
   - If knowledge is hidden but present, variability may be higher due to stochastic suppression attempts

3. **Procedural Agreement (Rater Effects):**
   - Measure Fleiss' kappa (κ) agreement between the four test procedures (direct, jailbreak, logit, extraction)
   - High agreement (κ > 0.70): indicates consistent removal across access methods
   - Low agreement (κ < 0.40): indicates selective recovery (some pathways remain open)

### 5.2 Secondary Outcome Metrics

4. **Knowledge Depth Gradient:** 
   - Measure KRR separately for: immediate factual answers, one-hop reasoning, two-hop reasoning
   - If unlearning only removes superficial recall, deeper reasoning should show higher recovery
   - Plot recovery rate as function of reasoning depth

5. **Target Robustness:**
   - Measure effect size of unlearning: (KRR_Control − KRR_Unlearned) / SD_Pooled
   - Compare across procedures: which procedure produces the largest, most stable drop in KRR?

---

## 6. Concrete Resources & Implementation

### 6.1 Models & Access

- **Control-Base:** Llama 3.1 70B (via Together AI or Hugging Face Transformers)
- **Unlearned-RFU:** If available via vendor or research release; otherwise, proxy with published RFU checkpoints
- **Unlearned-SISA:** Task-vector variant (e.g., negated task vector applied at inference)
- **Ablation model:** Selectively fine-tuned on a subset of the knowledge domain

### 6.2 Test Resources

**Query Sets:**
- Factual Recall (n=100): Hand-curated or benchmark-sourced questions targeting the unlearned domain (e.g., book titles, author names, plot points if copyrighted content is the target)
- Jailbreak Variants (n=50): Role-plays, hypotheticals, "imagine a world where," indirect references (sourced from jailbreak literature or adversarial benchmarks)
- Latent Probes: Train linear probes on 500 unrelated queries to establish baseline representations; then test logit separation on the target domain
- Few-Shot Exemplars (n=50 triplets): Pairs of (prompt, example response, recovery query) designed to prime the model to produce target knowledge

**Evidence Base:** Design informed by 2607.18508 (shortcut audit methodology) and 2608.29517 (rater-effects battery from educational measurement)

### 6.3 Computational Budget

- API calls: ~4,000 queries × 4 models = 16,000 queries (budget: $200–400)
- Logit probe training: 1–2 GPU-hours for representation extraction
- Analysis: ~8 hours (statistical testing, visualization, consistency checks)

---

## 7. Statistical Analysis & Uncertainty Quantification

### 7.1 Hypothesis Tests

**Primary Tests:**

**Test 1: Main Effect of Unlearning (Pairwise Comparisons)**
- Null: KRR(Unlearned) ≥ KRR(Control)
- Alternative: KRR(Unlearned) < KRR(Control)
- Method: Welch's two-sample t-test on arcsine-transformed proportions (KRR values are bounded 0–1)
- Correction: Bonferroni correction across 4 test procedures × 3 knowledge forms = 12 comparisons
- Significance: α_family-wise = 0.05, so α_per-test = 0.05 / 12 ≈ 0.004

**Test 2: Procedural Agreement (Rater Consistency)**
- Null: κ = 0.40 (moderate disagreement; some procedures detect recovery, others do not)
- Alternative: κ > 0.70 (high agreement; consistent removal across pathways)
- Method: Fleiss' kappa with 95% CI via bootstrap (1,000 resamples)

**Test 3: Knowledge Depth Gradient**
- Null: Recovery rate is constant across reasoning depths
- Alternative: Recovery rate increases with reasoning depth (indicating partial removal)
- Method: Ordinal logistic regression: logit(KRR) ~ depth + (model | depth)
- Effect: Slope estimate for depth and 95% CI

### 7.2 Uncertainty Quantification

**Confidence Intervals:**
- Primary CIs (95%) on KRR differences: Clopper–Pearson exact binomial CIs, then differenced
- Alternative: Bayesian credible intervals (Beta-Binomial prior, 95% HDI) to allow visual comparison of posterior distributions

**Effect Sizes:**
- Cohen's d for pairwise model comparisons (effect = (μ_Control − μ_Unlearned) / σ_pooled)
- Report with 95% CIs to indicate precision

**Power & Sample Size:**
- Target: Detect 15-percentage-point difference (KRR from 80% → 65%) with 80% power
- Two-sided t-test: n ≈ 130 queries per condition (achievable given cost budget)
- If smaller sample (n=50), expected power ≈ 0.65; trade-off disclosed in limitations

### 7.3 Sensitivity & Robustness Checks

**Sensitivity 1: Jailbreak Severity**
- Vary prompt aggressiveness (Likert 1–5) and check if recovery increases monotonically
- If yes: jailbreaks reveal latent knowledge; if no: unlearning is robust to prompt manipulation

**Sensitivity 2: Cross-Model Consistency**
- Repeat design on two additional unlearned models (if available)
- Check if recovery patterns generalize (hierarchical model: recovery ~ procedure + model + procedure:model)

**Sensitivity 3: Query Ambiguity**
- Annotate all queries for ambiguity (domain-expert ratings 1–5)
- Check if recovery correlates with query clarity; if so, report results separately for clear vs. ambiguous queries

---

## 8. Contingency & Validation

### 8.1 Internal Validation

**Consistency Check:** 
- Repeat 20% of all queries 5 times each (replication within-session)
- Expected: within-model SD of KRR ≤ 5 percentage points (indicating stable responses)
- If SD > 10%: model outputs are too stochastic; increase sample size or flag findings as preliminary

**Procedural Sanity Check:**
- Confirm that direct queries and jailbreak queries have measurably different recovery rates (expected: jailbreak > direct)
- If both are equal: jailbreaks may not be adversarial enough, or unlearning may be very robust

### 8.2 External Validation (If Budget Allows)

- Compare logit probe results (linear classifier on hidden states) to query-based KRR
- Expected: high correlation (r > 0.60), confirming that latent knowledge is present/absent in line with query outputs

---

## 9. Reporting & Visualization

### 9.1 Primary Figures

**Figure 1: Recovery Rate Heatmap**
- Rows: test procedure (direct, jailbreak, logit, extraction)
- Columns: knowledge form (factual, reasoning, latent, in-context)
- Cells: KRR with 95% CI error bars, stratified by model condition

**Figure 2: Effect Size Forest Plot**
- Pairwise Cohen's d estimates for (Unlearned − Control) with 95% CI
- Stratified by procedure; highlight if any CI crosses zero

**Figure 3: Rater Effects Heatmap**
- Pairwise agreement (κ) between procedures, stratified by model
- Expected: high within-Unlearned, lower between-Unlearned-and-Control

**Figure 4: Knowledge Depth Gradient**
- Line plot: reasoning depth (x-axis) vs. recovery rate (y-axis)
- Separate lines for each model; shaded 95% CI around lines

### 9.2 Tables

**Table 1: Summary Statistics**
- Model × Procedure × Knowledge_Form: count of queries, KRR, SD, 95% CI

**Table 2: Hypothesis Test Results**
- Test, Null, Alternative, t-statistic (or z, F), p-value, Effect Size, 95% CI

---

## 10. Expected Findings & Interpretation Framework

### 10.1 Strong Evidence for Genuine Removal
- KRR(Unlearned) < 20% across all procedures
- High agreement (κ > 0.70) across procedures
- Consistency (within-model SD < 5%) indicating stable suppression
- Interpretation: Knowledge is genuinely removed

### 10.2 Evidence for Hidden Knowledge (Main Alternative)
- KRR(Unlearned) > 50% in latent probes or extraction procedures, despite < 20% in direct queries
- Low agreement (κ < 0.40) between procedures (direct recovers <20%, extraction recovers >60%)
- Interpretation: Knowledge is hidden, not removed; accessible via indirect pathways (consistent with 2607.18508's finding that simple probes replicate complex models)

### 10.3 Partial/Selective Removal
- KRR varies significantly by knowledge form (e.g., factual < 15%, reasoning > 50%)
- Recovery increases with reasoning depth
- Interpretation: Unlearning targets superficial facts but leaves reasoning chains intact

### 10.4 Procedure-Dependent Effectiveness
- One procedure (e.g., SISA) achieves KRR < 15% across all methods; another (RFU) achieves 60%
- Interpretation: Methods differ in robustness; recommendations can be comparative

---

## 11. Limitations & Scope Boundaries

1. **Scope:** Design assumes unlearning targets a well-defined, identifiable knowledge domain (e.g., specific book, author, dataset). Domains with fuzzy or distributed knowledge may require additional validation.

2. **Cost:** Budget of $500 limits model count and query volume; design targets statistical power ≈ 0.80 for 15-point effect sizes, not smaller effects.

3. **Generalization:** Results are specific to tested models and procedures; new unlearning methods may have different characteristics.

4. **Ethical Constraint:** Jailbreak and extraction attempts assume the targeted knowledge is not itself harmful to reveal (i.e., the unlearning is for IP/privacy, not safety). If safety is the goal, jailbreak testing may be inappropriate; use direct queries and representation probes instead.

---

## 12. References to Evidence & Prior Work

- **2607.18508** ("Style over Substance"): Demonstrates shortcut audits via content-blind probes, de-confounding via ODIN, and multi-procedure agreement as a validity check. Directly informs the design's multi-procedure testing strategy and rater-effects framing.
  
- **2608.29517** ("LLM Judges as Raters"): Educational measurement toolkit for rating scale consistency, severity, halo effects, and cross-version stability. Informs secondary metrics (procedural agreement, consistency checks) and hypothesis test multiplicity handling.

---

## 13. Conclusion

This design treats unlearning evaluation as a **shortcut audit** problem: determining whether a model has truly removed knowledge or merely suppressed its observable output. By deploying four independent test procedures (direct, adversarial, latent, extraction) across four knowledge forms (factual, reasoning, latent, in-context), stratified across unlearning procedures and controls, the design can detect both successful removal and hidden knowledge retention. Statistical analysis via hypothesis tests with Bonferroni correction and rater-effects agreement (κ) provides both point estimates and uncertainty quantification. The stopping rule ensures sufficient statistical power while remaining cost-conscious; internal validation checks guard against spurious findings. This approach, informed by the methodological precedent of 2607.18508 and 2608.29517, separates genuine unlearning from suppression.
