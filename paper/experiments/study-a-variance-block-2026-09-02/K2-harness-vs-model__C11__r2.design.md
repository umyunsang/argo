# Experimental Design: Harness vs. Model Confound Isolation (K2)

## 1. Research Question and Confound Structure

**Primary Question:** How much of the measured performance gain from harness improvement 
comes from the harness itself, versus from the model receiving a better-optimized prompt 
for the new harness?

**Confound:** A harness change often requires prompt adaptation. If we observe improvement 
after a harness change, we cannot attribute it to the harness alone—some improvement might 
come from prompt re-optimization. Conversely, if we observe that harness improvements add 
value *beyond* what prompt-only improvement yields, we have evidence that the harness 
itself matters.

---

## 2. Main Comparison: 2×2 Factorial Design

### Conditions

| Condition | Harness   | Prompt                         |
|-----------|-----------|--------------------------------|
| A         | Baseline  | Baseline (original)            |
| B         | Baseline  | Optimized (for baseline)       |
| C         | Improved  | Baseline (written for baseline)|
| D         | Improved  | Optimized (for improved)       |

### Design Logic

- **Main effect of harness:** (C + D) / 2 − (A + B) / 2  
  Does the improved harness increase performance when prompts are appropriately matched?

- **Main effect of prompt:** (B + D) / 2 − (A + C) / 2  
  Does prompt optimization improve performance regardless of harness?

- **Interaction:** (D − C) − (B − A)  
  Does the prompt improvement differ between harness versions? (May reveal that new harness 
  requires different prompting strategy.)

### Hypothesis Structure

- **H₁ (Primary):** Harness effect is significantly positive when prompt is optimized for 
  that harness (C→D direction exceeds A→B direction).

- **H₂ (Secondary):** Harness effect persists even when prompt is not re-optimized (C > A), 
  indicating robustness.

- **H₃ (Ablation):** When harness is baseline, prompt-only improvement (A→B) is smaller 
  than harness improvement (A→C or A→D).

---

## 3. Sampling Frame (Explicit Reference)

From state.md:

**Population:** Distinct task instances that a system must solve (e.g., Q&A, code 
generation, retrieval-and-summarize tasks), sampled from held-out evaluation set.

**Unit:** (task instance, harness variant, prompt variant) triplet

**Scope:** Fixed model identity across all conditions; model receives no updates between 
runs. Harness and prompt vary as specified in 2×2 design. Evaluation runs entirely outside 
candidate workspace (per constraints).

**Blocking/Stratification:** Tasks stratified by:
  1. Domain (category of task: QA, code, RAG, etc.)
  2. Complexity level (easy/medium/hard), estimated using 2608.01913's retrieval-gap 
     detection for retrieval tasks, or routine vs. multi-step reasoning for others

**Allocation:** Paired allocation: each task instance receives all four (harness, prompt) 
combinations, assigned in random order. This ensures within-task correlation is captured.

---

## 4. Ablations

### Ablation 1: Harness Contribution Without Prompt Re-optimization (H₂ Test)

**Condition C isolated:** Improved harness, baseline prompt.

**Rationale:** Per 2608.03501 (stage isolation), harness quality includes task structure, 
tool configuration, and evaluation choreography. If the improved harness adds value *even 
when the prompt hasn't been re-optimized*, it demonstrates the harness contribution is 
non-trivial.

**Expected finding:** If C > A (holding prompt fixed), the harness improvement is at least 
partly intrinsic, not merely "room for better prompts."

**Failure mode:** If C ≈ A, the harness change may only work when paired with prompt 
adaptation, suggesting the harness and prompt are tightly coupled.

### Ablation 2: Variance Component Allocation (Generalizability Study)

**Design:** On a subset of tasks (~20%), perform repeated runs with prompt paraphrase 
variations (per 2607.13304: prompt paraphrase is a distinct variance component).

**Rationale:** Prompt paraphrase variance may inflate the estimated prompt effect size 
(H₂). A variance components study (generalizability theory) partitions:
  - Within-prompt resampling (n calls to model for same prompt text)
  - Prompt paraphrase (m semantic variants of prompt)
  - Harness version (k ∈ {baseline, improved})

**Analysis:** Variance component decomposition following 2607.13304 to estimate 
generalizability coefficient φ under different allocation schemes.

**Expected:** If prompt paraphrase variance is large, the prompt-only effect (B − A) may 
be less stable across prompt wordings than harness effect (C − A), suggesting harness 
improvements are more robust.

### Ablation 3: Outcome-Only vs. Step-Level Evaluation

**Design:** Evaluate a stratified subset (~40% of tasks) using both:
  1. Outcome-only scoring: Final answer only (per 2609.00038 "loud faults")
  2. Step-rubric scoring: Trajectory + answer (per 2609.00038 "silent fault" detection)

**Rationale:** 2609.00038 shows outcome-only judges miss 55% of silent faults. If harness 
improvements are mainly structural (better task decomposition, clearer tool usage), they 
may show up more clearly in trajectory scoring than outcome-only scoring.

**Expected:** Harness effect (C − A) is larger or more stable under step-rubric evaluation 
than outcome-only evaluation, suggesting harness quality shows up in *how* the model 
reasons, not just *what* it concludes.

---

## 5. Outcome Metrics

### Primary Metrics

1. **Task Success Rate (Binary):** 1 if task fully solved, 0 otherwise. Computed per task 
   instance under each (harness, prompt) condition. Aggregate to: P(success | H, P).

2. **Performance Difference:** 
   - Δ_harness = P(success | improved, optimized) − P(success | baseline, optimized)
   - Δ_prompt = P(success | baseline, optimized) − P(success | baseline, baseline)

3. **Relative Improvement Ratio:** Δ_harness / Δ_prompt  
   If >1, harness improvement exceeds prompt improvement. Per H₁.

4. **Robustness Index:** (C − A) / max(C − A, D − C)  
   What fraction of total improvement from harness (A→D) is realized without prompt 
   re-optimization (A→C)? Per H₂.

### Secondary Metrics

5. **Trajectory Quality (Step-Rubric Score):**  
   If step-level evaluation is performed (Ablation 3), measure rubric score (e.g., 0–10) 
   on correctness, reasoning clarity, and tool usage. Per 2609.00038.

6. **Evidence Utilization Gap:** (From 2608.01913)  
   For retrieval tasks: score based on whether retrieved evidence was actually *used* in 
   the reasoning, separate from whether the right evidence was retrieved. Harness 
   improvements in tool ordering or state management may improve utilization without 
   changing retrieval.

7. **Variance Component Estimates** (from Ablation 2):
   - σ²_within (within-prompt resampling)
   - σ²_paraphrase (prompt paraphrase)
   - σ²_harness (harness version)
   
   Report generalizability coefficient φ for different allocation schemes.

### Metric Justifications

- **Success rate (binary):** Concrete, interpretable. Needed for power calculation.
- **Difference metrics:** Enable comparison of effect sizes across conditions.
- **Robustness index:** Directly tests H₂; captures whether harness is robust or 
  requires prompt re-optimization.
- **Trajectory quality:** Per 2609.00038, outcome-only metrics are blind to reasoning 
  quality. Step-rubric catches silent faults.
- **Utilization gap:** Per 2608.01913, separates different failure modes. Harness may 
  improve utilization without improving retrieval.
- **Variance components:** Per 2607.13304, allocates resampling efficiently and identifies 
  which variance source (paraphrase, harness) dominates.

---

## 6. Analysis Plan

### 6.1 Primary Analysis: Paired Comparison of Differences

**Hypothesis Test (per 2605.30315 resolution framework):**

For each task instance i, compute:
  - Δ_harness[i] = (success[i, improved, optimized] − success[i, improved, baseline])
  - Δ_prompt[i] = (success[i, baseline, optimized] − success[i, baseline, baseline])

Test H₁: Does Δ_harness significantly exceed Δ_prompt?

Paired t-test (within-task design):  
  H₀: μ(Δ_harness − Δ_prompt) = 0  
  H_A: μ(Δ_harness − Δ_prompt) > 0  
  α = 0.05, two-tailed CI at 95%

**Resolution Calculation (per 2605.30315):**

Compute required sample size:  
  N* = 2 * σ²_D * (z_α/2 + z_β)² / δ²
  
  where:
  - σ²_D = variance of (Δ_harness − Δ_prompt) differences
  - δ = target effect size (5 percentage points)
  - z_0.025 = 1.96 (α=0.05 two-tailed)
  - z_0.20 = 0.84 (1−β=0.8 power)

Compute resolution ratio: q = n / N*  
Stop when q ≥ 1 (per stopping_rule in state.md).

### 6.2 Robustness (H₂) and Interaction Analysis

Test whether harness effect persists without prompt optimization:

Paired t-test:  
  H₀: μ(C − A) = 0  
  H_A: μ(C − A) > 0

Estimate interaction (harness × prompt):  
  I = (D − C) − (B − A)  
  
If I is significantly positive, the prompt must be re-optimized for the new harness 
to realize the full gain. If I ≈ 0, harness and prompt effects are additive.

### 6.3 Stratified Analysis by Task Domain and Complexity

Repeat 6.1–6.2 separately for each task domain (QA, code, RAG, etc.) and complexity 
stratum (easy/medium/hard).

**Rationale:** Harness improvements may be domain-specific (e.g., better tool ordering 
for code generation may not help open-ended QA). Complexity stratification allows detection 
of whether harness benefits concentrate in certain difficulty ranges.

### 6.4 Ablation 2: Variance Components Decomposition

Fit a linear model on the subset of repeated tasks:

  success[i,j,h,p] = μ + α_i + β_h + γ_p + ε[i,j,h,p]
  
  where:
  - i = task instance
  - j = paraphrase variant (m variants)
  - h = harness (baseline / improved)
  - p = prompt (baseline / optimized)
  - ε[i,j,h,p] is random error (within-prompt resampling)

Estimate variance components:
  - σ²_paraphrase = variance of paraphrase effects
  - σ²_harness = variance of harness effects
  - σ²_within = residual variance

Report generalizability coefficient:  
  φ = σ²_signal / (σ²_signal + σ²_error / n_resamples)

**Implication:** If σ²_paraphrase >> σ²_harness, prompt wording is unstable; harness 
effect is more consistent.

### 6.5 Ablation 3: Outcome-Only vs. Step-Rubric

For the stratified subset (40% of tasks), run both scoring methods.

Compute:
  - Δ_harness_outcome = (outcome-score | D) − (outcome-score | B)
  - Δ_harness_trajectory = (step-rubric | D) − (step-rubric | B)

Compare: Does Δ_harness_trajectory >> Δ_harness_outcome?

**Rationale:** Per 2609.00038, trajectory evaluation catches silent faults. If trajectory 
scoring shows larger harness effect than outcome-only, the harness improves *reasoning 
structure* in ways outcome-only evaluation misses.

---

## 7. Concrete Resources

### 7.1 Evaluation Set

**Source:** Held-out test set (per constraints, must exist).  
**Size:** Minimum n_min tasks to meet stopping_rule; recommend n = 30–50 task instances 
per domain to ensure stable estimates.  
**Composition:** Stratified sample covering QA, code generation, retrieval-augmented 
generation, and other relevant domains.  
**Versioning:** Snapshot fixed before any runs begin (immutable evaluation set per 
2609.00038's emphasis on closed evaluation).

### 7.2 Candidate Harness Versions

**Baseline:** Current harness in production (snapshot recorded, unchanging).  
**Improved:** Next-generation harness, fully specified in a snapshot artifact (e.g., 
YAML or JSON schema describing tool configuration, task decomposition, evaluation 
rubric). The improved harness must differ from baseline in *structural* ways (not just 
prompt text).

**Specification:** Both harnesses must be concretely versioned; a diff should clearly 
show what changed (e.g., new tool added, task breakdown reordered, evaluation step 
changed).

### 7.3 Prompt Versions

**Baseline Prompt:** Original instruction text used with baseline harness. Fixed.  
**Optimized-for-Baseline:** Prompt re-written to work optimally with baseline harness 
(may emphasize tools or steps that baseline provides). To be written during design phase.  
**Optimized-for-Improved:** Prompt re-written for improved harness. To be written during 
design phase.

**Constraint:** Prompt optimization must be done *by human expert* or *via reproducible 
method* (e.g., few-shot prompt engineering from a fixed template). Not allowed to optimize 
on the evaluation set.

### 7.4 Scoring/Judging Environment

**Location:** External to candidate workspace (per constraints).  
**Scorer:** Either deterministic (rubric applied programmatically) or LLM judge 
(pre-specified version, off-the-shelf).  
**Rubric:** For trajectory evaluation (Ablation 3), explicit rubric with categories:
  - Reasoning correctness (0–5 points)
  - Tool usage appropriateness (0–5 points)
  - Answer completeness (0–5 points)

Per 2606.07591, acknowledge that rubric scoring has a ceiling; hidden-target tasks may 
not be fully captured.

### 7.5 Statistical Tools

- **Power calculation:** Use 2605.30315's resolution framework to compute N* given observed 
  effect size and variance from prior runs or pilot data.
- **Paired t-tests:** Standard paired t-test (scipy.stats.ttest_rel or equivalent).
- **Variance components:** Fit linear mixed-effects model (e.g., statsmodels, R lme4 
  equivalent) to estimate σ²_paraphrase, σ²_harness, σ²_within.
- **Generalizability coefficient:** Compute φ = σ²_signal / (σ²_signal + σ²_error / 
  n_resamples) per 2607.13304.

---

## 8. How Uncertainty is Quantified

### 8.1 Confidence Intervals for Effect Sizes

For each effect (Δ_harness, Δ_prompt, interaction), compute 95% CI using:

  CI = estimate ± t_{α/2,n−1} * SE
  
  where SE = σ_D / √n (standard error of paired differences)

Report CI width and whether it includes zero (for null hypothesis rejection).

### 8.2 Bayesian Credible Intervals (Sensitivity Check)

As a robustness check, fit a Bayesian hierarchical model:

  success[i,h,p] ~ Bernoulli(θ[i,h,p])
  logit(θ[i,h,p]) = μ + α_harness[h] + β_prompt[p] + (αβ)_interaction[h,p] + u_i
  
  where u_i ~ N(0, σ²_task)

Prior: α_harness, β_prompt ~ N(0, 0.5²); u_i, (αβ) ~ N(0, 0.3²)

Report posterior mean and 95% credible interval for each parameter. Compare to frequentist 
CI; if posterior interval is tighter and excludes zero while frequentist CI straddles, 
the prior was informative and should be justified.

### 8.3 Minimum Detectable Effect (Resolution)

Report resolution ratio q = n / N*, where N* is the sample size required to detect 
target effect δ = 5 percentage points at (α, 1−β) = (0.05, 0.8).

If q < 1, the study is underpowered; report the smallest effect that can be detected 
with power 0.8 at current sample size (δ_detectible = δ_target * √(1/q)).

### 8.4 Stratified Uncertainty

For analysis by task domain or complexity, report CI separately per stratum. Note if 
some strata have wide CI (small n per stratum) and cannot resolve the effect.

### 8.5 Variance Component Uncertainty

For Ablation 2, report σ²_paraphrase with 95% CI (estimated via profile likelihood or 
bootstrap). If CI is wide, prompt paraphrase effect is uncertain.

### 8.6 Falsification Threshold

Specify in advance: the study will be interpreted as *falsifying* H₁ if the 95% CI for 
(Δ_harness − Δ_prompt) straddles zero with margin of error >2 percentage points, or if 
the resolution ratio q < 0.8 at final n. In either case, the experiment cannot distinguish 
harness effect from noise, and must be expanded.

---

## 9. Expected Outcomes and Interpretation Rules

### Outcome A: Harness Effect Dominates (H₁ True)

**Evidence:** Δ_harness >> Δ_prompt (95% CI excludes zero, q ≥ 1)

**Interpretation:** The improved harness adds value beyond prompt re-optimization. The 
harness is a meaningful contributor to system performance.

**Further test:** If robustness index (Ablation 2) is >0.5, the harness benefit is *robust* 
(holds even without prompt re-optimization). If <0.5, the benefit only realizes when 
prompt is re-optimized (harness-prompt coupling is tight).

### Outcome B: Prompt Effect Dominates

**Evidence:** Δ_prompt >> Δ_harness or Δ_harness ≈ 0 (CI includes zero)

**Interpretation:** The improved harness is inert; all improvement comes from better 
prompting. Per state.md falsifier, this refutes the claim that "the harness improves 
the system" in a meaningful sense.

**Action:** Either the harness change is too subtle, or it only serves to "enable" better 
prompts (a coordinator role, not a structural improver).

### Outcome C: Additive Effects (H_A: Interaction ≈ 0)

**Evidence:** Δ_harness + Δ_prompt ≈ (D − A) with no significant interaction

**Interpretation:** Harness and prompt improvements are independent; realization of full 
improvement requires both. Simpler model: improvements stack.

### Outcome D: Strong Interaction (Harness-Prompt Coupling)

**Evidence:** Interaction term (D − C) − (B − A) is large and significant

**Interpretation:** The improved harness *requires* prompt re-optimization; without it, 
the harness may even harm performance (D > C but (D − C) < (B − A)).

**Action:** Harness and prompt are tightly coupled; separate optimization is not 
appropriate.

---

## 10. Stopping Rule Operationalized

The experiment stops when ANY of the following holds:

1. **Resolution Achieved (Primary):**  
   n ≥ N*, where N* is computed as in Analysis 6.1, and the 95% CI for (Δ_harness − Δ_prompt) 
   does not straddle zero.

2. **Decision Confident Enough (Alternative):**  
   The 95% CI for (Δ_harness − Δ_prompt) straddles zero, but MoE ≤ 2 percentage points, 
   such that any true effect (if it exists) is practically small.

3. **Falsification Threshold Crossed:**  
   The 95% CI for (Δ_harness − Δ_prompt) straddles zero with MoE > 2 percentage points, 
   and budget for additional samples is exhausted. Conclude: study is underpowered; 
   harness effect cannot be resolved from noise.

4. **Interim Futility (Optional):**  
   After n = N*/2, if 90% CI for Δ_harness is entirely below 1 percentage point, 
   consider early stopping: the effect is too small to justify continued sampling.

---

## 11. Summary of Design Strengths and Limitations

### Strengths

1. **Confound Isolation:** The 2×2 design directly compares harness effect (with prompt 
   re-optimization) to prompt-only effect, allowing attribution.

2. **Robustness Tests:** Ablation 2 (H₂ test) ensures harness improvement persists without 
   perfect prompt alignment, and Ablation 3 (trajectory evaluation) catches reasoning-level 
   improvements that outcome-only evaluation misses.

3. **Paired Design:** Within-task pairing (per 2605.30315) improves power and meets 
   resolution targets with smaller n than between-subjects design.

4. **Variance Components:** Generalizability theory (Ablation 2) identifies whether prompt 
   paraphrase or harness version dominates variance, guiding future effort allocation.

5. **External Evaluation:** Scoring happens outside workspace, eliminating contamination.

### Limitations

1. **Prompt Optimization Cost:** "Optimized" prompt versions require manual writing (or 
   reproducible method). If prompts are sub-optimally tuned, the prompt-only effect 
   (Δ_prompt) may be underestimated, biasing results in favor of harness.

2. **Task Coverage:** Harness improvements may be domain-specific. A small held-out set 
   may not be representative; results may not generalize to tasks not in evaluation set.

3. **Model-Harness Fit:** Different models may interact differently with harnesses 
   (e.g., newer model may be less sensitive to harness structure). Findings are specific 
   to the model version tested.

4. **Interaction Ambiguity:** If interaction is large, it's unclear whether improved 
   harness is "good" but requires prompting expertise, or whether the harness and prompt 
   are just co-optimized artifacts.

5. **Rubric Ceiling (Ablation 3):** Per 2606.07591, explicit rubrics have hidden-target 
   limitations; some agent improvements may not be captured by the rubric.

---

## 12. Connection to Evidence

This design synthesizes insights from the evidence pack as follows:

- **2609.00038:** Justifies step-rubric evaluation (Ablation 3) to catch silent faults.
- **2608.03501:** Justifies stage isolation (separate harness design from prompt optimization) 
  and tool-augmentation focus.
- **2605.30315:** Provides resolution framework for paired sample-size calculation and 
  stopping rule.
- **2607.13304:** Provides variance-components framework (Ablation 2) for efficient 
  resampling allocation.
- **2608.01913:** Justifies stratification by complexity and retrieval-utilization gaps 
  (Ablation 3).
- **2606.07591:** Acknowledges rubric limitations; recommends explicit rubric but notes 
  ceiling.
- **2010.06595:** Motivates power calculation; study is designed to meet power ≥ 0.8.

All design choices reference concrete prior evidence; no unsupported claims are made.
