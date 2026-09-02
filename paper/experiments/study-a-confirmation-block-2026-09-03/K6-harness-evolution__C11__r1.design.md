# Experimental Design: Harness Generalization Under Scaffold Rewriting

## 1. Research Question and Context

**Core Question:** An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

**Motivation:** Retrospective Harness Optimization (2606.05922.txt) demonstrates within-benchmark held-out improvements (SWE-Bench Pro 59%→78%), but does not test whether such gains generalize to disjoint task families. Concurrently, "On the Fragility of Self-Improving Agents" (2608.18066.txt) shows that memory-based improvements are fragile: variance increases in 71% of cases, task order effects induce -4.5% swings, and improvements vanish under task reordering. This design measures whether scaffold rewriting produces genuine domain-level gains or merely fits the optimization tasks' idiosyncrasies.

---

## 2. Main Comparison and Conditions

### 2.1 Conditions

**Baseline (B0):** Vanilla scaffold with default harness configuration, fixed for the entire study.

**Optimized (B1):** Scaffold rewritten via self-supervised optimization on Task Family A (optimization set), following the RHO algorithm (2606.05922.txt). The model and inference settings remain unchanged; only harness artifacts (instructions, tools, workflow configuration) are modified.

### 2.2 Main Comparison

Measure pass rate and task success rate on **Task Family B** (held-out, disjoint from Family A) for both B0 and B1.

$$\Delta_{	ext{Family B}} = 	ext{PassRate}_{B1}(	ext{Family B}) - 	ext{PassRate}_{B0}(	ext{Family B})$$

**Primary Hypothesis:** $\Delta_{	ext{Family B}} > 0$ (optimized harness generalizes to unseen family). If $\Delta_{	ext{Family B}} \leq 0$, the harness improvements reflect overfitting to Family A's task structure, not genuine capability gain.

---

## 3. Sampling Frame (Operationalized)

Drawn from the research state (state.md):

**Population:** Code generation tasks in a single domain (e.g., software engineering, terminal commands, or QA systems).

**Sampling Units (Task Families):**
- **Task Family A (Optimization):** SWE-Bench Pro (or equivalent: 500+ diverse repository-level tasks). This is the family on which the harness is rewritten.
- **Task Family B (Held-Out):** Terminal-Bench 2 or an independent, stratified sample of GAIA-2 (100+ tasks), ensuring no overlap with Family A.
- **Justification:** Families must differ in task structure and distribution (A: repository refactoring, software engineering; B: shell commands, system operations or knowledge QA) to test cross-domain robustness. No task instance may appear in both families.

---

## 4. Ablations

### 4.1 Ablation 1: Optimization Epoch Overfitting
**Design:** Measure whether the harness converges to Family A or continues improving on Family B with further optimization.

- **Condition A1a:** One round of scaffold optimization on Family A (as B1 main condition).
- **Condition A1b:** Apply the same optimization procedure to Family B, using the same algorithm, and measure the within-family held-out improvement.

**Expected Result:** If A1b shows $\Delta_{	ext{Family B | optimized on B}} > \Delta_{	ext{Family A | optimized on A}}$, this suggests the optimization algorithm is not family-specific and is genuinely learning reusable harness improvements. Conversely, if $\Delta_{	ext{Family B | optimized on A}}$ is near zero while $\Delta_{	ext{Family B | optimized on B}} > \Delta_{	ext{Family A | optimized on A}}$, overfitting to Family A's task distribution is indicated.

### 4.2 Ablation 2: Coreset Composition
**Design:** Test whether the improvement derives from hard-task selection or from optimizing against the specific failures in Family A.

- **Condition A2a (Main):** Coreset selected via Determinantal Point Process (DPP) on difficulty + diversity, as in 2606.05922.txt.
- **Condition A2b:** Random coreset of the same size, sampled uniformly from Family A's trajectory set.

**Expected Result:** If A2a yields $\Delta_{	ext{Family B}} \gg \Delta_{	ext{A2b, Family B}}$, targeted task selection (difficulty + diversity) generalizes better than random selection, suggesting the optimization targets genuine weak spots rather than artifacts. If both are similar and non-positive, overfitting is more likely.

---

## 5. Experimental Procedures

### 5.1 Setup Phase

1. **Acquire task families:**
   - Task Family A: SWE-Bench Pro (full set, 500+ tasks).
   - Task Family B: Terminal-Bench 2 or GAIA-2 held-out (100+ tasks, disjoint from A).
   - Baseline runs: Execute B0 (vanilla harness) on both families, 10 independent runs per family.

2. **Establish baseline:**
   - Record pass rate and per-task metrics (time, tokens, error type) for B0 on Family A and Family B.
   - Quantify variance across runs for subsequent comparison (2608.18066.txt concern).

### 5.2 Optimization Phase (Main Condition B1)

1. **Trajectory collection:** Execute B0 on Family A, collecting trajectories (task prompts, actions, outcomes).
2. **Coreset selection:** Apply DPP to select 10 challenging, diverse tasks from Family A (matching 2606.05922.txt Appendix C hyperparameter G=3 for parallel re-solves).
3. **Harness proposal:** Generate 3 candidate harness modifications via the LLM (solver + optimizer), each re-solving the coreset with updated scaffold instructions/tools.
4. **Self-validation:** LLM evaluates pairwise preferences across the 3 candidates using self-consistency (2606.05922.txt method). Select the highest-scoring candidate if score > 0, else retain B0.
5. **Deploy:** Test the selected optimized harness (B1) on Family A held-out, then on Family B held-out.

### 5.3 Evaluation Phase

**On Family A (Optimization Family):**
- Run B1 10 times on Family A held-out tasks.
- Record pass rate, success rate, token count, task categories affected.

**On Family B (Held-Out Family):**
- Run B1 10 times on Family B tasks (no further tuning).
- Record the same metrics.

**Comparison:**
- Compute $\Delta_{	ext{Family A}} = 	ext{PassRate}_{B1}(	ext{Family A}) - 	ext{PassRate}_{B0}(	ext{Family A})$.
- Compute $\Delta_{	ext{Family B}} = 	ext{PassRate}_{B1}(	ext{Family B}) - 	ext{PassRate}_{B0}(	ext{Family B})$.
- Primary claim: Harness improvements generalize if $\Delta_{	ext{Family B}} > 0$ with 95% CI excluding zero.

### 5.4 Ablation Procedures

**Ablation 1 (Optimization Epoch):** Repeat optimization phase on Family B using condition A1b. Compare within-family improvements on both families.

**Ablation 2 (Coreset):** Repeat optimization phase with random coreset (A2b) instead of DPP. Compare resulting pass rates on Family B.

---

## 6. Outcome Metrics

### 6.1 Primary Metrics

| Metric | Definition | Rationale |
|--------|-----------|-----------|
| $\Delta_{	ext{Family B}}$ (pass rate delta) | PassRate_{B1}(Family B) − PassRate_{B0}(Family B) | Core test of generalization; positive means harness gains translate to unseen family |
| 95% CI on $\Delta_{	ext{Family B}}$ | Binomial exact confidence interval across 10 runs | Quantifies uncertainty; must exclude zero for claim of positive generalization |
| Variance ratio: $	ext{Var}_{B1}(	ext{Family B}) / 	ext{Var}_{B0}(	ext{Family B})$ | Ratio of run-to-run variance, Family B | Tests fragility concern (2608.18066.txt); ratio > 1.5 suggests increased noise, ratio > 2.0 suggests overfitting |

### 6.2 Secondary Metrics

| Metric | Definition | Interpretation |
|--------|-----------|-----------------|
| $\Delta_{	ext{Family A}}$ (within-optimization family) | PassRate_{B1}(Family A) − PassRate_{B0}(Family A) | Magnitude of optimization target gain; if >> $\Delta_{	ext{Family B}}$, suggests overfitting to Family A structure |
| Transfer ratio | $\Delta_{	ext{Family B}} / \Delta_{	ext{Family A}}$ | Fraction of gain retained on held-out family; close to 1.0 is ideal, < 0.5 suggests degradation of generalization |
| Task category breakdown | Pass rates by task type (e.g., "unit testing" vs. "refactoring" in SWE-Bench Pro; "file I/O" vs. "process management" in Terminal-Bench) | Identifies whether optimization is category-specific or domain-general |
| Token efficiency | Median token count per successful task (B1 vs. B0) | Evaluates whether harness improves both pass rate and efficiency or trades off |

### 6.3 Falsifiers (from state.md)

1. **Generalization Failure:** $\Delta_{	ext{Family B}} \leq 0$ (harness gains do not transfer).
2. **Increased Fragility:** Variance on Family B increases by > 50% under B1, suggesting optimization trades accuracy for brittleness.

---

## 7. Analysis Plan

### 7.1 Primary Analysis

1. **Generalization test:**
   ```
   Compute PassRate_B1(Family B) and PassRate_B0(Family B) across 10 runs.
   Compute 95% exact binomial CI for Δ_Family_B.
   Primary claim: Generalization confirmed if 95% CI excludes zero and is positive.
   ```

2. **Variance analysis (Fragility check, motivated by 2608.18066.txt):**
   ```
   Compute Var_B0(pass rate, Family B) and Var_B1(pass rate, Family B) across 10 runs.
   Report ratio: Var_B1 / Var_B0.
   If ratio > 1.5, flag as increased fragility; if > 2.0, flag as severe overfitting risk.
   ```

3. **Transfer quality:**
   ```
   Compute transfer ratio = Δ_Family_B / Δ_Family_A.
   If transfer ratio ≥ 0.5, conclude moderate-to-strong generalization.
   If transfer ratio < 0.2, conclude weak generalization (overfitting likely).
   If transfer ratio < 0, conclude negative transfer (harness harms held-out family).
   ```

### 7.2 Ablation Analysis

**Ablation 1 (Optimization Epoch):**
```
Compare Δ_Family_B (optimized on A) vs. Δ_Family_B (optimized on B).
If both are > 0 and similar, algorithm is not family-specific.
If Family_A optimized gets < 0 on B but Family_B optimized gets > 0 on B, 
  conclude Family_A optimization is task-specific overfitting.
```

**Ablation 2 (Coreset):**
```
Compare Δ_Family_B under DPP coreset vs. random coreset.
If DPP >> random, targeted selection adds value and improves generalization.
If both are ≤ 0, neither coreset strategy recovers transferable gains.
```

### 7.3 Robustness Checks

- **Task order sensitivity:** Shuffle order of Family B tasks and re-run B1 on a subset (3 runs); check if pass rate variance increases (following 2608.18066.txt protocol).
- **Task category balance:** Stratify Family B evaluation by task category; report per-category $\Delta$ to identify generalization bottlenecks.

---

## 8. Concrete Resources and Infrastructure

### 8.1 Task and Benchmark Data

| Resource | Source | Size | Purpose |
|----------|--------|------|---------|
| SWE-Bench Pro | Established benchmark | 500+ tasks | Family A (optimization) |
| Terminal-Bench 2 or GAIA-2 held-out | Established benchmark | 100+ tasks | Family B (held-out test) |
| Trajectories from B0 runs | Generated via Codex baseline | ~500 trajectories | Input to RHO optimization algorithm |

### 8.2 Computational Infrastructure

- **Model:** Single fixed Codex model (e.g., gpt-4o or equivalent), with inference settings locked (temperature, max_tokens, etc.).
- **Parallelization:** 3 candidate harnesses in parallel per optimization round (2606.05922.txt: G=3).
- **Run count:** 10 independent runs per condition (B0, B1) per family to quantify variance (2608.18066.txt concern).
- **Wall-clock:** ~1–2 days for B0 baseline (10 runs × 2 families), ~2–3 days for optimization on Family A, ~1–2 days for B1 evaluation on both families. Total: ~1 week at full parallelization.

### 8.3 Harness Representation

Per 2606.05922.txt Appendix D.1, harness is a directory of files (prose instructions, scripts, configuration). Representation includes:
- Instruction text (system prompts, task-specific guidance).
- Tool definitions and skill APIs.
- Workflow configuration (e.g., tool use order, error handling).

---

## 9. Uncertainty Quantification

### 9.1 Confidence Intervals

- **Primary metric** ($\Delta_{	ext{Family B}}$): Exact binomial 95% CI (Wilson score interval), computed from 10 pass/fail runs.
  - Formula: CI = [p - z_{0.975} * sqrt(p(1-p)/n), p + z_{0.975} * sqrt(p(1-p)/n)] (with continuity correction).
  - Example: If 7 out of 10 runs pass under B1 vs. 5 out of 10 under B0, then Δ = 0.2, 95% CI ≈ [−0.05, 0.45]. If CI excludes zero, generalization is supported (α=0.05).

### 9.2 Variance Quantification

- **Run-to-run variance:** Compute Var and SD of pass rate across 10 runs per condition.
  - Report: mean ± SD and coefficient of variation (SD / mean).
  - Flag if CV > 0.15 (>15% variance), per 2608.18066.txt findings.

### 9.3 Power and Sample Size

- **Sample size rationale:** 10 runs per condition provides ~80% power to detect a true effect size of Δ=0.2 (10 percentage points) at α=0.05 (two-sided), assuming binomial variance.
- **Sensitivity:** With N=10, we can detect Δ ≥ 0.2 with reasonable confidence; smaller effects (Δ < 0.1) require larger N but are not the threshold of interest for this design.

### 9.4 Multiple Comparisons

- **Primary test:** $\Delta_{	ext{Family B}}$, no correction (single pre-registered hypothesis).
- **Ablations:** Treated as secondary exploratory analyses; Bonferroni correction applied if making post-hoc family-wise claims (e.g., "coreset method significantly outperforms random").

---

## 10. Success Criteria and Interpretation

### 10.1 Generalization Confirmed
- **Condition:** $\Delta_{	ext{Family B}} > 0$ and 95% CI excludes zero.
- **Interpretation:** Harness improvements gained during Family A optimization transfer to Family B, suggesting domain-level gains rather than task-specific overfitting.
- **Claim:** "Scaffold rewriting produces generalizable improvements; measured gains are not mere artifacts of optimization-set tuning."

### 10.2 Generalization Uncertain (Gray Zone)
- **Condition:** $\Delta_{	ext{Family B}}$ near zero or 95% CI overlaps zero.
- **Interpretation:** Insufficient evidence to conclude robust generalization; improvements may be Family A-specific or masked by variance.
- **Claim:** "Harness improvements do not reliably generalize; larger sample or different task families required."

### 10.3 Generalization Refuted
- **Condition:** $\Delta_{	ext{Family B}} < 0$ or transfer ratio < 0.2.
- **Interpretation:** Optimized harness underperforms baseline on held-out family, contradicting the generalization hypothesis.
- **Claim:** "Scaffold optimization overfits to Family A's task structure; improvements do not transfer to disjoint task families."

### 10.4 Fragility Detected
- **Condition:** Variance ratio (B1/B0) > 1.5 on Family B.
- **Interpretation:** Optimization increases noise, consistent with 2608.18066.txt findings on self-improving agent fragility.
- **Claim:** "While point estimates may show gain, run-to-run variance increases, suggesting brittle improvements."

---

## 11. Methodological Safeguards

### 11.1 Train/Test Separation
- Harness is rewritten only on Family A; Family B is never used during optimization, ensuring true held-out evaluation.
- Stopping rule (from state.md): Do not re-tune or re-optimize after Family B results are observed.

### 11.2 Model Integrity
- Model and inference parameters (temperature, max_tokens, seed) are fixed throughout. Only the harness scaffold changes.
- Verification: Log model calls and config to confirm consistency across all runs.

### 11.3 Reproducibility
- Seed control: Set random seed for Codex sampling within each run to enable replication.
- Harness versioning: Version control all scaffold updates; document changes between B0 and B1.
- Hyperparameters: Report all RHO hyperparameters (coreset size k=10, DPP weight θ=0.7, G=3 parallel rollouts) per 2606.05922.txt Appendix C.

### 11.4 Variance Monitoring (Fragility Guard)
- Following 2608.18066.txt methodology, report variance and task-order sensitivity for Family B to flag brittleness early.
- If Var_B1 >> Var_B0, interpret pass-rate gains with caution.

---

## 12. References to Evidence

- **2606.05922.txt** (RHO): Wenbo Pan et al., "Evolving Agents in the Dark: Retrospective Harness Optimization via Self-Preference." Defines the optimization algorithm, held-out evaluation protocol, and hyperparameter settings (k=10, G=3, DPP weight θ=0.7).
  
- **2608.18066.txt** (Fragility): Qinyuan Ye et al., "On the Fragility of Self-Improving Agents: Variance, Task Order, and Underspecification." Motivates variance measurement, task-order sensitivity analysis, and the risk of improvement metrics being brittle across runs and orderings.

---

## 13. Summary

This design tests whether harness improvements generalize beyond the tasks used during rewriting, directly addressing the risk of overfitting in scaffold optimization. By evaluating on a disjoint task family (Family B), quantifying variance, and ablating coreset selection, the design isolates genuine capability gains from task-specific tuning artifacts. Success (positive $\Delta_{	ext{Family B}}$ with 95% CI excluding zero) would demonstrate that scaffold rewriting delivers transferable improvements. Failure or gray-zone results flag the need for larger samples, different task families, or fundamentally different optimization approaches.

The sampling frame (disjoint task families within a domain) and variance-aware analysis (motivated by 2608.18066.txt) provide robustness against the fragility concerns raised in prior work.
