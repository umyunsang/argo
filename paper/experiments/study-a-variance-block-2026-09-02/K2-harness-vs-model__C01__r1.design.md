# Experimental Design: Isolating Harness Improvement from Model Improvement

## Research Question

How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

**Causal structure:** We seek to isolate the effect of harness improvements (A) from confounding by model/prompt improvements (B) on the outcome Y = agent performance.

---

## Main Comparison and Conditions

### Design Structure: Orthogonal Factorial with Held-Out Evaluation

We compare **two harness versions** (baseline H₀, candidate H₁) crossed with **two prompt regimes** (fixed-prompt P_fixed, held-constant-across-harnesses P_standard) on a held-out evaluation set.

**Four Treatment Cells:**

| Harness | Prompt Regime | Condition | Purpose |
|---------|---------------|-----------|---------|
| H₀ (baseline) | P_fixed | **A0** | Baseline: old harness, fixed prompt throughout |
| H₁ (candidate) | P_fixed | **A1** | Harness effect: new harness with the same fixed prompt as A0 |
| H₀ (baseline) | P_standard | **B0** | Confound detector: baseline harness with standard-optimized prompt |
| H₁ (candidate) | P_standard | **B1** | Combined effect: new harness with standard-optimized prompt |

**Prompt Regime Definition:**
- **P_fixed:** The exact prompt used to construct and evaluate harness H₀. It is frozen and used identically in conditions A0 and A1. This controls for prompt drift.
- **P_standard:** A "standard" version of the prompt that could plausibly be written for harness H₁ without harness-specific tuning. It must be written **before** seeing candidate harness H₁ and must be auditable (e.g., templated, human-written once, version-controlled). It is used in B0 (with old harness) and B1 (with new harness) to measure whether a prompt written for the new harness also helps the old one.

### Identification Strategy

**Effect of harness improvement, net of prompt improvement:**

ΔHarness = (A1 − A0) − (B0 − B0)
         = A1 − A0

This isolates harness improvement: we compare H₁ to H₀ **holding the prompt identical**.

**Confounding check:**

ΔPrompt_on_old_harness = B0 − A0

If B0 >> A0, the "standard" prompt already lifts the old harness significantly, which suggests the prompt may be over-fitted to new capabilities and is not a neutral standard.

**Joint effect (for completeness):**

ΔJoint = B1 − A0 = (A1 − A0) + (B1 − B0 + B0 − A0)
       = ΔHarness + ΔPrompt_cross_harness + ΔPrompt_on_old_harness

---

## Ablations

### Ablation 1: Single-Point Harness Snapshot Ablation

**Question:** Does a single snapshot of the candidate harness explain the improvement, or does the improvement depend on how the candidate harness is constructed (e.g., interaction with the evaluation set)?

**Design:** 
- Snapshot H₁ at two independent construction points (e.g., H₁^(first) and H₁^(second), created from two runs or two branches).
- Evaluate both on the same held-out set with P_fixed.
- Compute correlation of (H₁^(first), A1) and (H₁^(second), A1) to check consistency.

**Expected outcome if harness improvement is real:** The two snapshots should show similar improvement magnitude (high correlation). If they diverge, the improvement is unstable or overfitted.

**Evidence basis:** 2608.01913 shows that trajectory-level diagnosis reveals whether gains are stable across runs; we apply the same principle to harness snapshots.

### Ablation 2: Held-Out Evaluation Set Robustness

**Question:** Is the improvement specific to the evaluation set used, or does it generalize?

**Design:**
- Partition the held-out evaluation set into two disjoint subsets: **eval_set_1** and **eval_set_2** (e.g., 50-50 split or stratified by task difficulty).
- Evaluate (A0, A1) on eval_set_1 and (A0, A1) on eval_set_2 separately.
- Compute the improvement (A1 − A0) on each subset.
- Report the signed difference between subset improvements: |Δ_subset1 − Δ_subset2|.

**Expected outcome if harness improvement is real:** Improvements should be consistent across subsets (small signed difference). Large divergence suggests the improvement is an artifact of the specific evaluation set.

**Evidence basis:** 2608.03501 (stage isolation) and 2609.00038 (outcome-only blind spots) emphasize that evaluation robustness is critical; stratified recall by outcome type is the model.

---

## Analysis Plan

### Primary Analysis: Paired Hypothesis Test with Resolution Diagnostic

**Setup:** Each trial in the held-out evaluation set is a paired observation (A1_score, A0_score) on the same task/instance.

**Test:** Paired t-test (or paired McNemar for binary outcomes) under H₀: E[A1_score − A0_score] = 0.

**Resolution Diagnostic (cite 2605.30315):**
- Compute the resolution ratio **q = N / N⋆**, where:
  - N = size of the held-out evaluation set
  - N⋆ = required paired sample size to detect the observed effect δ_obs with power 1−β=0.80 at α=0.05
- **q ≥ 1** means the result is statistically resolvable at the (0.05, 0.80) target.
- **q < 1** means the evaluation set is underpowered; the observed gap may be noise.

**Minimum detectable effect (MDE)** at the current N:
- δ_MDE = (z_{0.025} + z_{0.20}) × σ_D / √N
- Report this alongside any claimed improvement to set expectations.

### Secondary Analyses

#### A. Trajectory-Level Decomposition (cite 2608.01913, 2609.00038)

Separate harness behavior into two stages:
1. **What the harness retrieves / constructs:** Evidence quality, intermediate outputs, tool choices.
2. **How the harness uses that evidence:** Final synthesis, answer formation, reasoning correctness.

**Procedure:**
- For a stratified sample of runs (e.g., 20–30% of the evaluation set), collect full trajectories from both H₀ and H₁.
- Label intermediate steps with a pre-registered rubric (e.g., evidence correctness, reasoning sound, tool selection appropriate).
- Compute the improvement in each stage separately.
- If A1 improves only in stage 1 but not stage 2, or vice versa, the harness improvement is localized and can be diagnosed precisely.

**Evidence basis:** 2608.01913 shows that a retrieval vs. utilization decomposition reveals which gaps (retrieval gaps or utilization gaps) the harness actually closes. This is stronger than outcome-only evaluation (2609.00038).

#### B. Variance-Components Decomposition (cite 2607.13304)

Identify and quantify sources of noise in the paired difference (A1 − A0):
1. Within-run stochasticity (same harness, same evaluation instance, re-run multiple times).
2. Evaluation-set variance (does H₁ improve uniformly across all instances, or only on a subset?).
3. Harness construction variance (do different snapshots of H₁ show different improvements?).

**Procedure:**
- Use a crossed random-effects (generalizability-theory) design:
  - Repeat each instance r times (e.g., r=3–5).
  - Include multiple harness snapshots s (e.g., s=2–3, from independent runs or branches).
  - Partition instances into k instance strata (e.g., by task complexity).
- Fit a variance-components model: Var(Y) = τ²_run + τ²_snap + τ²_instance + τ²_residual.
- Allocate budget (repeats, snapshots, instances) to maximize precision of the treatment effect at a target reliability.

**Expected outcome:** If harness improvement is real and stable, τ²_snap should be small relative to the treatment-effect size. If large, the harness is unstable.

**Evidence basis:** 2607.13304 decomposes brand-score variance into within-prompt, paraphrase, model, and language; we apply the same design to harness evaluation.

#### C. Judge Severity and Drift (if using LLM judging; cite 2608.29517)

If the evaluation uses LLM judges (e.g., to score trajectory quality):
- Pre-register the judge model, prompt, and rubric **before** evaluation begins.
- After evaluation, re-judge a stratified subset (e.g., 10%) with the same judge to measure test-retest reliability.
- Report judge severity (mean score) and consistency (Cronbach's α, ICC).
- If severity or consistency drifts across the evaluation window, flag it as a confound and adjust estimates via severity-adjusted scores (cite 2608.29517).

---

## Concrete Resources

### 1. Baseline Harness H₀
- **Artifact:** The current production harness snapshot.
- **Identification:** Named version tag in version control (e.g., `harness-v1.0.0`), committed hash, and frozen-state artifact.
- **Audit trail:** Commit message, date, author.
- **Reproducibility:** Containerized or lockfile-specified environment to ensure the same runtime behavior across evaluation runs.

### 2. Candidate Harness H₁
- **Artifact:** The proposed harness version.
- **Identification:** Named version tag (e.g., `harness-v1.1.0-candidate`), committed hash.
- **Construction:** Document what changed (e.g., "added hypothesis registry from 2607.09195, refactored tool routing, added evidence-tracking stage").
- **Validation before evaluation:** Sanity-check that H₁ is well-formed and does not crash on a small warm-up set (e.g., 5 tasks).

### 3. Held-Out Evaluation Set
- **Size:** N ≥ 50 instances (recommended: 100–200 to achieve reasonable power; see Resolution Diagnostic section).
- **Composition:** Stratified sample of tasks by difficulty, domain, or outcome type (e.g., 25% easy, 50% medium, 25% hard).
- **Provenance:** Must be held-out from all harness development. Document the date it was frozen and the train/test split procedure.
- **Storage:** Write-once archive (e.g., Git LFS, immutable S3 bucket, or a released dataset) with hash verification.
- **Access control:** Scoring must run outside the candidate workspace (per constraints). Use a read-only mount or a separate evaluation harness.

### 4. Fixed Prompt P_fixed
- **Artifact:** The exact prompt used to develop H₀.
- **Identification:** Version-controlled in a `prompts/` directory with a semantic version (e.g., `fixed-prompt-v1.0.0.txt`).
- **Scope:** Must be the prompt currently in production or documented as the baseline.
- **Audit:** Include a SHA-256 hash in the experimental report to prove the prompt is identical across all uses.

### 5. Standard Prompt P_standard
- **Artifact:** A candidate prompt that could plausibly be written for H₁ **without harness-specific tuning**.
- **Authorship:** Written by a team member not involved in H₁ construction (or by a separate harness team) using a templated or rule-based approach.
- **Timing:** Locked in before evaluation begins. Document the date and the authors' names.
- **Motivation:** Capture the idea that a new harness might call for a natural update to the prompt, but one that isn't hand-crafted to exploit H₁'s specific structure.
- **Verification:** Have a second person review P_standard in isolation (without seeing H₁) and attest that it is reasonable for a harness with the intended capabilities.

### 6. Evaluation Infrastructure
- **Scoring system:** An independent harness (not H₀ or H₁) that runs evaluations and collects metrics.
- **Logging:** Collect full trajectories (thoughts, tool calls, observations) for every run.
- **Metrics:**
  - Primary: Outcome accuracy / quality on the held-out set.
  - Secondary (if using rubrics or LLM judging): Rubric scores by dimension (cite 2608.03501 for stage-based rubrics).
  - Trajectory metrics (if applicable): Retrieval recall, utilization correctness, evidence quality (cite 2608.01913).
- **Reproducibility:** Use fixed random seeds for any stochastic components (model sampling, tool choice, etc.).

### 7. Statistical Analysis Tooling
- **Resolution diagnostics:** Implement or use llm-power (2605.30315) to compute q = N/N⋆ for the primary paired test.
- **Variance components:** Use a generalizability-theory package (e.g., Python: `pymc`, `stan`, or `statsmodels.mixed_linear_model`; R: `lme4`, `lavaan`).
- **Trajectory analysis:** Write custom scripts to decompose trajectories into stages and score each stage against a pre-registered rubric.
- **Judge reliability:** If using LLM judges, compute Cronbach's α, ICC(3, 1), and severity drift indices.

---

## Outcome Metrics

### Primary Metric

**Paired Improvement (A1 − A0)** on the held-out evaluation set.
- **Computation:** For each evaluation instance, compute score(H₁, instance) − score(H₀, instance).
- **Report:** Mean difference μ_Δ, standard deviation σ_Δ, 95% CI, and resolution ratio q.
- **Success criterion:** μ_Δ > 0 with q ≥ 1.0 (statistically resolvable at α=0.05, β=0.20).

### Secondary Metrics

1. **Harness Effect (A1 − A0):** Improvement when prompt is held fixed at P_fixed.

2. **Confound Check (B0 − A0):** Improvement of the old harness when prompt changes from P_fixed to P_standard.
   - **Interpretation:** If large (e.g., > 50% of μ_Δ), it suggests P_standard is not neutral and may be overfitted to new capabilities.

3. **Cross-Harness Prompt Effect (B1 − B0):** Improvement due to prompt change, holding the new harness constant.
   - **Interpretation:** Measures how much of the combined gain comes from the prompt update.

4. **Stage-Level Improvements** (if using trajectory decomposition):
   - Stage 1 (retrieval/construction): μ_Δ^(stage1)
   - Stage 2 (usage/synthesis): μ_Δ^(stage2)
   - Contribution of each stage to total improvement.

5. **Ablation 1 Consistency (H₁ snapshot stability):**
   - Correlation ρ between improvements (A1^(first) − A0) and (A1^(second) − A0).
   - **Success criterion:** ρ ≥ 0.80 (high consistency).

6. **Ablation 2 Subset Robustness:**
   - Signed difference in improvements between eval_set_1 and eval_set_2: |Δ_sub1 − Δ_sub2|.
   - **Success criterion:** |Δ_sub1 − Δ_sub2| < 0.5 × μ_Δ (subset effects are small relative to main effect).

### Uncertainty Quantification

#### Confidence Intervals

Report **95% bootstrap confidence intervals** (bias-corrected and accelerated, BCa) for:
- μ_Δ (mean paired improvement)
- μ_Δ^(stage1), μ_Δ^(stage2) (stage-level improvements)
- Each ablation metric

**Resampling strategy:** Stratified bootstrap, resampling instances (not individual runs) to preserve evaluation-set structure.

#### Resolution Ratio and Minimum Detectable Effect

For the primary paired test:
- **MDE(N):** Minimum effect size detectable at the current N with α=0.05, β=0.20.
  - Formula: δ_MDE = (z_{0.025} + z_{0.20}) × σ_Δ / √N
  - **Interpretation:** If μ_Δ < δ_MDE, the result is not statistically resolvable.

- **Resolution Ratio q = N / N⋆:**
  - N⋆ = required sample size to detect μ_Δ with power 0.80.
  - **Interpretation:** q ≥ 1 means the result is "resolved" at the target power; q = 0.5 means you have half the power you need.

**Example report:**
> "On N=120 held-out instances, H₁ improved over H₀ by μ_Δ = +3.2 percentage points (95% CI: [+1.8, +4.6]). The MDE at N=120 is δ_MDE = 2.1 pp (α=0.05, β=0.20). The resolution ratio is q = 120 / 85 = 1.41, indicating the result is statistically resolved. The paired McNemar test rejects the null with p=0.008."

#### Variance-Components Summary

Report the fitted variance components (τ²_run, τ²_snap, τ²_instance, τ²_residual) as a variance-explained table:

| Source | Variance | % of Total |
|--------|----------|-----------|
| Harness snapshot | τ²_snap | ? |
| Evaluation instance | τ²_instance | ? |
| Within-run | τ²_run | ? |
| Residual | τ²_residual | ? |
| **Total** | **σ²_Δ** | **100%** |

**Interpretation:** If τ²_snap is small compared to σ²_Δ, the harness improvement is stable. If large, improvements are driven by harness construction variance and may not be replicable.

#### Trajectory-Level Fault Attribution

If using trajectory decomposition, report fault attribution stratified by outcome survival (cite 2609.00038):

| Outcome Survival | Stage 1 Errors | Stage 2 Errors | Undetected | n |
|------------------|---|---|---|---|
| Loud (broke outcome) | 45% | 40% | 15% | 60 |
| Silent (outcome OK) | 20% | 30% | 50% | 40 |

**Interpretation:** If H₁ improves mainly on loud-outcome errors, the improvement is robust. If mainly on silent errors (not visible in outcomes), the improvement is fragile and may not persist in production.

---

## Key Considerations and Justifications

### Why This Design Isolates Harness from Model/Prompt Improvement

1. **Orthogonal conditions:** By crossing harness (H₀, H₁) with prompt regime (P_fixed, P_standard), we can estimate the harness effect independently of prompt effects.
   - **Evidence:** 2608.03501 advocates stage isolation; we isolate the harness stage (A1 vs. A0 at fixed P_fixed) from the prompt stage (B0 vs. A0 at varying P).

2. **Fixed prompt as control:** Condition A1 uses the **same prompt** as A0, so any improvement is purely harness-driven.
   - **Justification:** If you change both harness and prompt, you cannot tell which caused the improvement.

3. **Confound detector:** Condition B0 shows whether P_standard alone (without harness change) lifts performance on the old harness. If B0 >> A0, the prompt is a confound.
   - **Evidence:** 2609.00038 emphasizes stratification by outcome type to detect silent confounds; we stratify by harness version to detect prompt confounds.

### Why Ablations Are Necessary

- **Ablation 1 (snapshot stability):** Ensures the improvement is not an artifact of a specific construction run.
  - **Evidence:** 2607.13304 shows variance-components analysis; harness-construction variance (τ²_snap) must be small.

- **Ablation 2 (subset robustness):** Ensures the improvement generalizes across the evaluation set, not just on a lucky subset.
  - **Evidence:** 2608.01913 shows that wasted search effort and early evidence saturation can create spurious improvements on some tasks; stratified analysis is necessary.

### Why Held-Out Evaluation is Critical

- The held-out set must not be used during harness development, or the improvement may be overfitting to the evaluation set rather than a true harness improvement.
  - **Constraint satisfied:** The research question specifies that a held-out evaluation set exists.

- Scoring must run outside the candidate workspace (per constraints) to prevent the harness from exploiting the scoring process.
  - **Implementation:** Use a separate evaluation harness with read-only access to trajectories.

### Why Resolution Diagnostics Matter

- Underpowered comparisons are common in LLM evaluation (cite 2010.06595, 2605.30315).
- The resolution ratio q = N/N⋆ directly shows whether the result is statistically resolvable. A q < 1 signals that the observed improvement may be noise.
  - **Formula:** From 2605.30315: N⋆ = [(z_{0.025} + z_{0.20}) × σ_D / |δ_obs|]²; then q = N / N⋆.

### Why Trajectory-Level Analysis Strengthens the Claim

- Outcome-only evaluation misses silent failures—faults that don't break the final answer (2609.00038).
- Decomposing improvements into retrieval and utilization stages (2608.01913) reveals whether the harness actually fixed the root cause or just masked a symptom.
  - **Implementation:** Collect full trajectories, score them at intermediate steps, and report improvement by stage.

---

## Concrete Resources Checklist

- [ ] Baseline harness H₀ snapshot committed with version tag and hash
- [ ] Candidate harness H₁ snapshot committed with version tag and hash
- [ ] Held-out evaluation set (N ≥ 50) archived with write-once access and hash verification
- [ ] Fixed prompt P_fixed versioned and audited (SHA-256 hash recorded)
- [ ] Standard prompt P_standard written, version-controlled, dated, and independently reviewed
- [ ] Evaluation infrastructure (scoring harness, logging, trajectory collection) tested on warm-up set
- [ ] Pre-registered rubrics for trajectory stages and LLM judge prompts (if applicable)
- [ ] Resolution-diagnostic calculator (llm-power or equivalent) installed and tested
- [ ] Variance-components estimation setup (mixed-effects model, priors if Bayesian)
- [ ] Bootstrap resampling and confidence-interval code written and tested
- [ ] Analysis scripts (SCRIPTs or notebooks) version-controlled; execution is deterministic

---

## Summary of Key Methodological Principles

| Principle | Evidence Cite | Implementation |
|-----------|---|---|
| **Stage isolation** | 2608.03501 | Separate harness (A1 vs. A0) from prompt (B0 vs. A0) effects via orthogonal conditions |
| **Trajectory-level diagnosis** | 2609.00038, 2608.01913 | Decompose improvements into retrieval and utilization stages; stratify by outcome type |
| **Variance decomposition** | 2607.13304 | Allocate repeats, snapshots, and instances to maximize precision; report τ²_snap, τ²_instance, etc. |
| **Hypothesis-testing framework** | 2605.30315, 2010.06595 | Use paired McNemar/t-test; report resolution ratio q = N/N⋆ and MDE(N) |
| **Auditability** | 2607.09195 | Externalize harness state (prompts, version tags, rubrics) with immutable commit hashes |
| **Blind spots in outcome-only eval** | 2609.00038 | Avoid outcome-only judges; use step-level rubrics to catch silent failures |
| **Resolution in leaderboards** | 2605.30315 | Report the resolution ratio q for each comparison; disclose underpowered results |

---

## Expected Workflow

1. **Setup (week 1):** Commit both harnesses, freeze evaluation set, version prompts. Write evaluation scripts and trajectory-scoring rubric.
2. **Sanity check (day 1 of eval):** Run on 5–10 warm-up instances to check for crashes.
3. **Main evaluation (week 2):** Run all N instances for (H₀, P_fixed), (H₁, P_fixed), (H₀, P_standard), (H₁, P_standard). Collect full trajectories.
4. **Analysis (week 3):** Compute paired statistics, resolution ratio, variance components, and stage-level improvements. Generate plots and tables.
5. **Ablations (week 3–4):** Re-run Ablation 1 (two more snapshots of H₁) and Ablation 2 (split evaluation set).
6. **Report (week 4):** Write up results, confidence intervals, and interpretation. Publish the raw data and analysis scripts for reproducibility.

