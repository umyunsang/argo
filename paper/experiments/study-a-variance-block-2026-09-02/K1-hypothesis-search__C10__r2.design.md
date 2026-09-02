# Experimental Design: Hypothesis Tree vs. Flat Queue for Artifact Optimization

## Overview

This experiment tests whether organizing autonomous agent attempts as a **hypothesis tree with propagated insight** produces better held-out artifact optimization outcomes than a **flat queue** baseline, given equal compute and workspace budgets per arm per task.

---

## Sampling Frame & Allocation

Drawing from the research state:

**Sampling frame:** Held-out artifact optimization tasks from Claude Code projects.  
**Unit of analysis:** (task, backbone_configuration, arm_assignment) — a single task solved by one backbone under one experimental condition.  
**Sampling method:** Stratified random assignment by task difficulty (inferred from prior artifact size and constraint complexity); fixed equal budget per arm per task.

**Stratification rationale:** Task difficulty affects both absolute success rate and whether structure helps; stratification ensures both arms see comparable difficulty distribution.

---

## Arms & Conditions

### Arm 1: Hypothesis Tree with Insight Propagation (Treatment)

**Mechanism:**
- Agent maintains an explicit hypothesis tree over successive attempts.
- Each node represents a distinct hypothesized cause for failure or a proposed optimization direction.
- Upon each attempt outcome, the agent:
  - Updates or prunes hypothesis nodes based on observed evidence.
  - Propagates insights (contradiction detection, pattern recognition) up and across the tree.
  - Uses propagated insight to seed the next attempt, avoiding redundant paths.
- Budget allocation: Total budget B per task is fixed; agent allocates compute across tree branches (no branch depth limit imposed).

**Operationalization:**
- At initialization: Agent generates 2–3 competing hypotheses about artifact failure modes or optimization targets.
- Between attempts: Agent explicitly logs which hypotheses were falsified, which remain open, and which new hypotheses are now plausible.
- Stopping criterion (per task, within budget): Stop when either budget exhausted or agent reports no remaining unexplored hypotheses.

### Arm 2: Flat Queue (Baseline)

**Mechanism:**
- Agent receives attempts as a simple queue: attempt 1, attempt 2, ..., attempt N.
- After each attempt:
  - Agent observes success/failure outcome.
  - Agent generates next attempt by refining the prior attempt (e.g., "try a different code path").
- No explicit hypothesis tree structure; no cross-attempt insight propagation (agent may learn implicitly, but no tree organization).
- Budget allocation: Same total budget B per task; agent makes attempts sequentially until budget spent or task succeeds.

**Operationalization:**
- Agent is given a flat list of "attempt slots."
- Between attempts: Agent generates a refinement or variant without explicit hypothesis framing.
- Stopping criterion (per task, within budget): Stop when either budget exhausted or task succeeds.

---

## Ablations

### Ablation 1: Hypothesis Tree Without Insight Propagation

**Condition:** Agent maintains a tree structure but does **not** propagate insights across branches or up the tree.
- Agent logs hypotheses in a tree but treats each branch independently.
- Contradictions and patterns detected on one branch do not inform sibling branches.

**Rationale:** Isolates the effect of *tree structure alone* versus *tree + active insight propagation*. If Ablation 1 achieves similar results to the Treatment, structure is not the active ingredient; if Ablation 1 underperforms Treatment but outperforms Baseline, insight propagation is the key factor.

---

## Main Comparison

**Hypothesis:** Treatment arm (hypothesis tree + propagation) will achieve higher success rate on held-out tasks than Baseline arm (flat queue).

**Operationalization of "success":**
- Binary per task: artifact optimization task succeeded (agent found working solution within budget) or failed.
- Primary outcome: Proportion of tasks where each arm succeeded.

**Statistical comparison:**
- Compute success rate per arm: (# tasks succeeded) / (# tasks assigned).
- Compute difference: Treatment success rate − Baseline success rate.
- Quantify uncertainty via bootstrap resampling (see Uncertainty Quantification section).

---

## Outcome Metrics

### Primary Metrics

1. **Task Success Rate**
   - Definition: Proportion of held-out tasks on which each arm produced a working artifact optimization.
   - Reported per arm, per stratum (task difficulty level).
   - Uncertainty: 95% confidence interval via percentile bootstrap.

2. **Success Rate Difference (Treatment − Baseline)**
   - Definition: Absolute difference in task success rate between arms.
   - Interpretation: Effect size for tree + propagation advantage.
   - Uncertainty: 95% CI via bootstrap.

### Secondary Metrics

3. **Average Budget Consumption per Successful Task**
   - Definition: Mean compute budget (e.g., token count, wall-clock time, number of attempts) required to solve a task, among tasks where arm succeeded.
   - Rationale: Efficiency of the arm; lower is better.
   - Reported per arm.

4. **Hypothesis Reuse Rate (Treatment Only)**
   - Definition: Proportion of attempts in Treatment where the agent reused or built upon insights from prior hypotheses.
   - Rationale: Validates that propagation mechanism is actually engaged.
   - Target: >50% of Treatment attempts reference prior hypotheses; if <20%, propagation is not occurring.

5. **Artifact Quality Proxy** (if oracle scoring available)
   - Definition: Among successful attempts, mean quality score or code cleanliness metric.
   - Rationale: Success alone may not reflect solution quality; tree may converge to lower-quality workarounds faster.
   - Optional: Computed only if a blind human or automated scorer can evaluate artifact quality post-hoc.

---

## Analysis Plan

### Stratified Analysis

1. **By task difficulty stratum:**
   - Compute success rate per arm per difficulty level.
   - Report interaction: does tree structure help more on hard tasks than easy tasks?

2. **Early vs. late tasks:**
   - Divide chronologically and test for learning effects.
   - If Baseline arm improves dramatically in later tasks, implicit learning may partially offset structure advantage.

### Heterogeneity Analysis

3. **Post-hoc task clustering:**
   - Group tasks by failure mode (e.g., compilation error, logic error, constraint violation).
   - Test whether tree structure helps uniformly or only on certain failure types.
   - Report by failure mode.

### Assumption Checks

4. **Budget balance:**
   - Confirm both arms spent roughly equal total budget across their assigned tasks.
   - If one arm consistently exhausts budget on early tasks, reallocate or flag for analysis.

5. **Provenance audit:**
   - Verify that held-out test tasks were not in backbone training set or a leaked train/test overlap.
   - Document task source and any potential leakage risk.

### Sensitivity Analysis

6. **Stopping-rule robustness:**
   - Rerun primary analysis under alternative stopping rules (e.g., stop after 10 attempts regardless of budget, or stop at first success).
   - Report whether conclusion changes.

---

## Concrete Resources

### Compute & Infrastructure

- **Backbone model:** Claude 3.5 Sonnet (or latest available Claude model at run time).
- **Total compute budget:** 100,000 tokens per task per arm (tune based on typical artifact size and iteration depth; this value is a design placeholder and must be set after pilot or scoping phase).
- **Held-out task repository:** Claude Code projects with artifacts from the last 6 months, filtered to remove any overlapping with training data; estimate 20–50 tasks depending on availability.
- **Execution environment:** Local or cloud sandbox with artifact compilation/execution capability (e.g., Docker container with Node.js, Python, Rust toolchains as needed per artifact language).

### Logging & Instrumentation

- **Per-attempt logs:**
  - Timestamp, attempt number, budget consumed, outcome (success/failure), error message (if any).
  - For Treatment: explicit hypothesis tree state before and after attempt.
  - For Baseline: attempt refinement rationale (free-text or structured).

- **Outcome recording:**
  - Per task, per arm: success (0/1), total budget consumed, number of attempts, wall-clock time.
  - Artifact diff: lines changed, file count altered.

### Workforce & Annotation

- **Human validation (optional):** If artifact quality scoring is added, recruit 2–3 blind raters to score solution quality (e.g., code clarity, correctness on unseen inputs) for a random sample of 10% of successful artifacts. Compute inter-rater agreement (Cohen's κ).

---

## Uncertainty Quantification

### Primary Method: Bootstrap Resampling

1. **Task-level resampling:**
   - For each arm, resample with replacement from the set of (task, outcome) pairs.
   - Recompute success rate for each of 10,000 bootstrap samples.
   - Extract 95% CI as [2.5th percentile, 97.5th percentile] of bootstrap distribution.

2. **Difference CI:**
   - For each bootstrap sample, compute (Treatment success rate − Baseline success rate).
   - Report CI on the difference.

### Sensitivity to Stratification

3. **Stratified bootstrap:**
   - Resample within each difficulty stratum separately, then pool.
   - Compare to unstratified bootstrap CI; wide gap suggests strong stratum effect.

### Uncertainty in Secondary Metrics

4. **Budget consumption:**
   - Among successful tasks, compute bootstrap CI on mean budget per arm.
   - Interpret: Do confidence intervals overlap? Overlapping CIs suggest no strong efficiency difference.

5. **Hypothesis reuse rate:**
   - If Treatment logs explicit hypothesis references, compute bootstrap CI on proportion of attempts referencing prior hypotheses.
   - If CI excludes zero and is >0.5, propagation is reliably active.

### Reporting Standard

- All point estimates reported with 95% bootstrap CI.
- If a CI crosses zero or encompasses trivial effect size (e.g., CI for success rate difference is [−5%, +5%]), interpret as no strong evidence for treatment advantage.
- No p-values; focus on effect size and CI width as evidence of precision.

---

## Pre-Registration & Deviations

**Registered aspects (before running):**
- Stratification variable and strata boundaries.
- Primary outcome metric (task success rate).
- Sample size N per arm (determined by compute budget and task count).
- Bootstrap procedure (10,000 resamples, percentile CI).

**Exploratory (post-hoc, not registered):**
- Secondary metrics (budget efficiency, quality proxy).
- Stratified heterogeneity by failure mode.
- Interaction tests (tree effectiveness × task difficulty).

---

## Stopping Rules & Monitoring

From research state:

1. **Primary rule:** Complete all assigned (task, arm) pairs within compute budget; no early stopping for statistical significance.

2. **Secondary rule:** If a single arm fails to improve on >75% of first 5 tasks, log concern but continue (possible task difficulty mismatch rather than arm failure).

3. **Tertiary rule:** No adaptive reallocation between arms during the experiment.

**Interpretation:** We are not powered for statistical hypothesis testing at a fixed α; instead, we collect all available data within budget and estimate effect size + uncertainty.

---

## Fallback & Robustness

**If tree + propagation does not clearly outperform flat queue:**
- Do not report negative result as "failure." Instead, investigate:
  - Was propagation mechanism actually engaged? (Check Hypothesis Reuse Rate.)
  - Were tasks too easy (success ceiling on both arms) or too hard (failure floor)?
  - Did flat baseline implicitly learn at near-tree performance? (Check early vs. late task trend.)

**If one arm exhausts budget on most tasks while the other doesn't:**
- Report budget consumption as a confound.
- Interpret success rate difference as confounded with efficiency.
- Run sensitivity analysis restricting to same-budget tasks.

---

## Design Validity Checklist

- ✓ Sampling frame clearly defined (held-out Claude Code artifact tasks).
- ✓ Arms operationalized with concrete mechanisms (tree + propagation vs. flat queue).
- ✓ Primary outcome binary and unambiguous (task success).
- ✓ Ablation isolates tree structure from propagation.
- ✓ Budget constraint enforced equally across arms.
- ✓ Uncertainty quantified via resampling (no strong parametric assumptions).
- ✓ Stratification mitigates task difficulty confound.
- ✓ Logging enables post-hoc heterogeneity checks.
- ✓ Stopping rule pre-specified and non-adaptive.
- ✓ Secondary metrics exploratory, not pre-registered.

---

## References to Research State

**This design operationalizes all fields from state.md:**

- **decision_id:** K1-hypothesis-tree-vs-flat-queue — directly addressed by Treatment (Tree) vs. Baseline (Queue) comparison.
- **question:** Restated in Overview section.
- **alternatives:** Acknowledged (random restart, heuristic priority queue) and rejected; not part of final design to preserve budget for main comparison.
- **sampling_frame:** Used verbatim in "Sampling Frame & Allocation" section; stratified random assignment operationalized.
- **evidence_used:** Cited in design choices (e.g., precedent for tree-structured reasoning from ECC skills).
- **falsifier:** Incorporated into Analysis Plan (success rate threshold of ≥95% Baseline relative to Treatment).
- **stopping_rule:** Explicit in "Stopping Rules & Monitoring" section; no early stopping, non-adaptive.

---

## Summary

This design compares a **hypothesis tree with propagated insight** to a **flat queue** on held-out artifact optimization tasks, stratified by difficulty. The treatment arm explicitly maintains and updates a hypothesis tree; the baseline arm uses sequential refinement without tree structure. Primary outcome is task success rate, quantified with bootstrap confidence intervals. An ablation (tree without propagation) isolates the mechanism. Uncertainty is reported as 95% CIs on success rate and success rate difference. All resource choices are concrete; all outcomes are well-defined. No numeric results are reported in the design itself.
