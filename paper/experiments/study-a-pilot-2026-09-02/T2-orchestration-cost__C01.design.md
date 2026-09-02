# Experimental Design: Multi-Call Orchestration Accuracy vs. Inference Cost

## Research Question

Do multi-call orchestrations improve accuracy enough to justify the additional inference they consume?

---

## Main Comparison

**Comparison axis:** Single-pass inference (1 call) vs. multi-call orchestrations (adaptive multiple calls)

**Conditions:**

1. **Single-pass baseline (1-call):** Prompt directly for the answer in one model call. No feedback, iteration, or retrieval.

2. **Multi-call orchestration (N-call):** An adaptive chain-of-thought orchestration where:
   - The model can issue up to 5 planned calls (or a per-task budget based on difficulty estimate)
   - Calls may retrieve evidence, verify assumptions, or revise reasoning
   - The agent decides stopping based on confidence or evidence saturation
   - Prompt structure, example selection, and instruction clarity held constant between conditions (controlling for "prompt optimization effort")

**Constraint on prompt effort:** Both conditions use identical base prompts, system instructions, and few-shot examples. The orchestration difference is in **call topology**, not prompt tuning. This ensures cost-accuracy tradeoff reflects the multi-call strategy, not differential prompt engineering.

---

## Ablations

### Ablation 1: Orchestration Stopping Criteria

**Rationale:** Multi-call value depends on when agents stop. Per 2608.01913, "useful evidence often appears early in the trajectory, yet agents tend to continue searching, producing a long tail of low-yield retrieval steps."

**Variants:**

- **A1a. Fixed-N:** Always use exactly 5 calls (or the difficulty-based budget), regardless of confidence or evidence arrival.
- **A1b. Confidence-stop (default multi-call):** Agent stops when self-reported confidence exceeds a threshold (e.g., 0.85) or max calls reached.
- **A1c. Evidence-saturation-stop:** Agent stops when newly retrieved evidence (detected via shallow redundancy check) adds < 5% semantic novelty to prior steps, or max calls reached.

**Expected pattern:** A1b and A1c should outperform A1a on cost-accuracy plots; the comparison reveals whether the orchestration's value comes from structured reasoning (fixed-N vs 1-call) or from adaptive stopping.

### Ablation 2: Retrieval vs. Pure Reasoning Orchestrations

**Rationale:** Per 2608.01913, failures decompose into "retrieval gaps" (necessary evidence never found) and "utilization gaps" (evidence retrieved but misused). This ablation isolates the failure type multi-calls address.

**Variants:**

- **A2a. No-retrieval multi-call:** Orchestrated reasoning (planning, verification, step-by-step refinement) but no external retrieval. Uses only context already in the model.
- **A2b. Retrieval-only multi-call (default):** Standard orchestration with retrieval calls but no refinement step. Single answer generation after gathering evidence.
- **A2c. Retrieval + reasoning orchestration:** Full multi-call with both retrieval and reasoning refinement (default).

**Expected pattern:** A2c should exceed both A2a and A2b, revealing whether gains come from retrieval, from reasoning structure, or from both. If A2a ≈ A2c, then retrieval is the dominant factor and execution cost is unjustified.

---

## Analysis Plan

### Primary Outcome: Paired Accuracy Gain vs. Cost

**Metric:** For each task i, compute:

- **Accuracy Δ_i:** (accuracy of multi-call on task i) − (accuracy of 1-call on task i)
  - Binary: 1 if multi-call correct and 1-call wrong; −1 if vice versa; 0 if concordant
- **Cost ratio γ_i:** (total tokens in multi-call) / (tokens in 1-call)

**Paired statistical test (per 2605.30315):**

Use paired McNemar's test on the discordant pairs (where multi-call and 1-call disagree). 
- H₀: P(multi-call correct | disagreement) = 0.5
- Test at (α, 1−β) = (0.05, 0.80)
- Report resolution ratio q = N / N⋆ from 2605.30315's framework

**Justification threshold:** If multi-call wins on > 50% of discordant pairs AND is statistically powered (q ≥ 1 at target power), the method is justified **only if median cost ratio γ ≤ 2**. If γ > 2 and accuracy gain is < 5 percentage points, the cost is not justified.

### Secondary Analysis: Failure Mode Decomposition (per 2608.01913)

For each task where 1-call is wrong:

1. **Can a retrieval step help (retrieval gap)?**
   - Would external information resolve the error? (yes/no; binary annotation)
   - Did the multi-call method retrieve that information? (yes/no)
   
2. **Is the evidence present but misused (utilization gap)?**
   - Is relevant information in the model's context but incorrectly applied? (yes/no)
   - Does the multi-call orchestration fix this via reasoning refinement? (yes/no)

**Tabulation:** Build a 2×2 contingency table:
```
              Retrieval gap | Utilization gap
1-call fails             Y  |               Y
1-call fails             Y  |               N
1-call fails             N  |               Y
```

If the majority of 1-call failures are utilization gaps, multi-call retrieval orchestrations may not improve enough to justify cost. If retrieval gaps dominate, justify higher cost.

### Tertiary Analysis: Trajectory-Level Evaluation (per 2609.00038)

**Rationale:** Outcome-only metrics miss agent failures that happen to produce the right answer through wrong reasoning. 

**Approach:**

For a stratified sample of tasks (n = 50), use a step-rubric judge (not outcome-only) to evaluate:
- Quality of intermediate steps (not just final answer)
- Whether multi-call agent follows the intended orchestration protocol
- Correctness of evidence use at each step

**Metrics:**
- Silent failure rate: fraction of wrong intermediate steps whose incorrect reasoning does not affect final correctness (should be << 1%)
- Trajectory fidelity: fraction of steps matching the orchestration design intent

**Blind-spot test (per 2609.00038):** Inject one deliberate flaw into a clean multi-call trajectory (e.g., hallucinated evidence, skipped validation), keep final answer correct. Count how many step-based judges flag it. If < 50%, the evaluation itself is too weak and outcome-level only.

### Uncertainty and Statistical Power

**Sample size justification:**

From 2010.06595: "underpowered experiments make it more difficult to discern the difference between statistical noise and meaningful model improvements."

- **Minimum detectable effect (MDE)** for paired McNemar: δ_MDE = (z_{1−α/2} + z_{1−β}) * σ_D / √N
- Use prior benchmarks to estimate σ_D (variance of paired differences)
- Solve for N to achieve δ_MDE ≤ 3 percentage points at (α, 1−β) = (0.05, 0.80)

**Variance decomposition (per 2607.13304):**

The total variance in task performance has four sources:
1. Within-prompt sampling (model stochasticity)
2. Prompt paraphrase (phrasing variation)
3. Model backbone choice
4. Task difficulty

Run 3 random seeds × 3 baseline models × 2 prompt paraphrases per task to partition variance and adjust N if needed.

**Multi-model validation:**

Test the main result on at least 2 independent model backbones (e.g., Claude 3.5 Sonnet + Gemini 2.0 Flash) to confirm the cost-accuracy tradeoff is not an artifact of a single model.

---

## Concrete Resources

### Benchmarks

**Primary benchmark:** Use a subset of **SCOPE** (2608.03501) or similar task set with explicit item-level difficulty annotations. SCOPE has 300 tasks across 19 research domains; use 150–200 for main experiment, reserve 50 for trajectory evaluation.

**Why SCOPE:** Difficulty annotations (Low/Medium/High) allow adaptive call budgets: low-difficulty tasks get max 1 call; medium get max 3; hard tasks get max 5. This reflects real practice and controls for ceiling effects.

**Fallback:** If SCOPE not available, use **MMLU-Pro** (referenced in 2605.30315) with BrowseComp-style difficulty estimates or hand-annotated complexity labels.

### Models

- **Backbone 1:** Claude 3.5 Sonnet (a capable, stable baseline)
- **Backbone 2:** Gemini 2.0 Flash or equivalent (demonstrates generality)
- **Judge model:** Use a step-rubric judge (Claude 3.5 or Gemini; see 2609.00038 for criteria)

### Orchestration System

- **Single-pass baseline:** Direct prompt → answer → cost count
- **Multi-call orchestrator:** A deterministic orchestration script (e.g., JSON-based plan):
  ```
  {
    "step": 1,
    "action": "retrieve",
    "query": "...",
    "confidence": 0.6,
    "rationale": "..."
  }
  ```
  Operator logs all tokens consumed, all intermediate steps, and final answer.

### Difficulty Estimates

From SCOPE or benchmark metadata: each task has a pre-assigned difficulty (Low/Medium/High). Use this to set per-task call budgets without tuning on the experimental data.

---

## Outcome Metrics

### Primary Metrics

1. **Paired accuracy gain (%):** McNemar p-value and resolution ratio q (2605.30315)
   - Resolution: q ≥ 1.0 at (α=0.05, power=0.80)

2. **Cost efficiency ratio:** 
   - Gain per token: (accuracy_multi − accuracy_single) / (cost_multi − cost_single)
   - Accept multi-call only if this ratio exceeds a pre-specified threshold (e.g., 0.05 pp gain per 1000 tokens)

3. **Failure mode attribution (%):**
   - % of 1-call failures that are retrieval gaps
   - % of 1-call failures that are utilization gaps
   - % of multi-call fixes that close retrieval vs. utilization gaps

### Secondary Metrics

4. **Evidence saturation curve:** Plot cumulative accuracy gain vs. call number (1, 2, 3, 4, 5). Identify the "useful plateau" where marginal benefit drops below 1 pp per call.

5. **Silent failure rate:** % of multi-call trajectories with intermediate errors that don't affect final correctness (should be ≤ 5%).

6. **Per-model generality:**
   - Repeat main comparison on two models
   - Report correlation of cost-accuracy gains across models (should be ≥ 0.70 for generality claim)

---

## Specification of Uncertainty

### Confidence Intervals and Reporting

**Paired confidence interval on accuracy difference:**
- Use paired bootstrap (stratified by difficulty) to estimate 95% CI on Δ_accuracy
- Report per-difficulty stratum (Low/Medium/High) to show if orchestration helps more on hard tasks
- Per 2605.30315, include design-effect correction if tasks cluster by domain

**Cost ratio CI:**
- 95% bootstrap CI on γ (cost_multi / cost_single)
- Separately report mean, median, and interquartile range (IQR)
- Highlight if cost ratio variance is high (high-variance tasks may benefit from selective orchestration)

**Multiplicity control:**
- Run three statistical tests: main McNemar (multi-call vs. 1-call), ablation 1 (stopping criteria), ablation 2 (retrieval vs. reasoning)
- Use Holm–Bonferroni correction at family-wise α = 0.05
- Report adjusted p-values

### Sensitivity Analysis

**Threshold robustness:**
- Vary the cost-justification threshold (γ_threshold) from 1.5 to 3.0
- Re-report the "recommended" method for each threshold
- This shows whether conclusions hinge on a single cost assumption

**Judge agreement:**
- Run step-rubric evaluation on 50 tasks using two independent judges (different LLM providers or prompts)
- Report inter-judge Fleiss' κ on failure-mode categories
- If κ < 0.60, uncertainty in human annotation is a limitation

---

## Hypothetical Outcome Interpretation

### Scenario 1: Multi-Call Wins (Justified Cost)
If paired McNemar: p < 0.05 (q ≥ 1), accuracy gain > 5 pp, and γ ≤ 2:
- **Conclusion:** Multi-call orchestration is statistically justified and cost-effective
- **Recommendation:** Deploy multi-call for all tasks (or, per ablation 1c, selectively using evidence-saturation stopping)

### Scenario 2: Multi-Call Wins but Unjustified Cost (γ > 2)
If accuracy gain > 5 pp but γ > 2:
- **Conclusion:** Multi-call is more accurate but prohibitively expensive
- **Recommendation:** Reserve multi-call for high-difficulty tasks only (per SCOPE difficulty tiers)

### Scenario 3: Multi-Call Fails to Win (p > 0.05 or q < 1)
If McNemar: p > 0.05 or q < 1:
- **Conclusion:** Accuracy difference is not statistically detectable at this sample size
- **Recommendation:** Increase N or abandon multi-call as a general strategy
- **Failure mode analysis:** Check ablations—if A2a ≈ A2c, pure reasoning is sufficient; if A2b >> A2a, retrieval helps but orchestration framing does not

### Scenario 4: Retrieval Gaps Dominate (Ablation 2 Results)
If most 1-call failures are retrieval gaps (not utilization gaps):
- **Conclusion:** Multi-call gains justify cost because retrieval is the bottleneck
- **Design implication:** Focus future work on query formulation and retrieval ranking, not reasoning refinement

### Scenario 5: Utilization Gaps Dominate
If most 1-call failures are utilization gaps (evidence present but misused):
- **Conclusion:** Multi-call orchestration (which adds retrieval) does not target the real problem
- **Implication:** Better in-context learning or few-shot examples may be more cost-efficient

---

## Research Integrity and Transparency

### Pre-registration
- Register the hypothesis, sample size N, primary test (McNemar at α=0.05, power=0.80), and cost threshold (γ ≤ 2) before running the full experiment.
- Publish the registration to avoid HARKing (hypothesizing after results are known).

### Reporting Standards (per 2608.03501)
- Report all experiments run, not just the ones that passed statistical thresholds.
- Use redline scoring: if a task violates the orchestration protocol (e.g., exceeds call budget), flag it explicitly rather than averaging it away.

### Reproducibility (per 2609.00038)
- Release raw trajectories, verdicts, and all intermediate steps as a downloadable artifact.
- Include a reproduction script so future work can regenerate every table and figure without re-running the models.

---

## Evidence Citations

This design draws on the following released excerpts:

1. **2010.06595** (Card et al., 2020, Stanford): Underpowered NLP experiments are common; statistical power must be planned and reported.

2. **2605.30315** (Kotawala, 2026): Paired resolution diagnostics for LLM evaluation, including resolution ratio q and the paired McNemar required-N formula.

3. **2608.01913** (Liu et al., 2026): Retrieval vs. utilization gap decomposition for diagnosing long-horizon search agent failures.

4. **2608.03501** (Liu et al., 2026): SCOPE benchmark with difficulty annotations, stage isolation methodology, and redline scoring for experimental design quality.

5. **2609.00038** (Mohammadi, 2026): Trajectory-level evaluation showing outcome-only judges miss silent faults; step-rubric judges detect them but at higher cost.

6. **2607.13304** (Zatuchin, 2026): Variance components decomposition to isolate sources of non-determinism (within-prompt resampling, prompt paraphrase, model identity, task difficulty).

7. **2310.11511** (Asai et al., 2020+): Self-RAG framework showing adaptive retrieval on-demand can improve both accuracy and reduce unnecessary inference.

8. **2403.14403** (Jeong et al., 2024): Adaptive-RAG using question complexity to dynamically select retrieval strategy, motivating our difficulty-based call budgets.
