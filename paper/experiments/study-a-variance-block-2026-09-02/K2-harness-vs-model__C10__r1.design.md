# Complete Experimental Design: K2-Harness-vs-Model

**Experiment ID**: K2-harness-evaluation-protocol (see state.md decision_id)

---

## 0. Research Context and State Foundation

This design is grounded in the filled research state (state.md):

- **Research question**: How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?
- **Adopted approach**: Fixed-model, fixed-prompt cross-harness comparison on held-out evaluation set, with prompt instrumentation to detect prompt-level changes
- **Sampling frame**: All tasks in held-out evaluation set (population: decision/reasoning tasks where harness tool choice, composition, and control flow measurably affect outcomes; unit: single (harness_version, task) pair)
- **Falsifier**: Bytewise inspection of harness changes; if harnesses are functionally identical, measured improvement is noise. If improvements correlate with model changes rather than harness changes, improvement is attributable to model.

---

## 1. Research Objective and Hypothesis

**Primary objective**: Measure whether a specific harness improvement increases system performance on a held-out evaluation set, independent of model or prompt changes.

**Research hypothesis**: Harness version H2 (with structural improvement Y) will produce better task outcomes than baseline harness version H1, when both are instantiated with the same model and system prompt.

**Null hypothesis**: Task outcome distributions under H1 and H2 are identical (any observed difference is within natural variance).

---

## 2. Main Experimental Comparison

### Design Structure (Crossed Factorial)

| Factor | Levels | Role |
|--------|--------|------|
| **Harness version** | H1 (baseline), H2 (candidate) | Independent variable |
| **Task** | All tasks in held-out evaluation set | Sampling frame |
| **Model** | Fixed (Claude 3.5 Sonnet or specified snapshot) | Control |
| **System prompt** | Fixed (canonical harness system prompt, v1.0) | Control |
| **Run/replication** | Runs 1, 2 (within each cell for variance estimation) | Random effect |

### Sampling Frame (Explicit Reference)

All comparisons are sampled from the **held-out evaluation set**, defined as (from state.md):
- **Population**: Collection of independent decision/reasoning tasks where harness tool choice, composition, and control flow measurably affect outcomes
- **Unit of analysis**: Single (harness_version, task) pair
- **Scope**: Full set of evaluation tasks (fixed N, no sampling within the set)
- **Independence assumption**: Tasks do not share state; each task-harness pair can be evaluated independently

Each task in the sampling frame is evaluated under:
- Harness H1 + fixed model/prompt → outcome O1
- Harness H2 + fixed model/prompt → outcome O2

### Concrete Conditions

**Condition A (Baseline)**: 
- Harness: H1 (last stable version before improvement)
- Model: Claude 3.5 Sonnet (December 2024 snapshot or pinned API version)
- System prompt: `/opt/harness/system_prompts/v1.0.txt`
- Evaluation set: Full held-out set (path: `/data/evaluation/held_out_benchmark.jsonl`)

**Condition B (Candidate)**:
- Harness: H2 (candidate with improvement integrated)
- Model: Identical to Condition A
- System prompt: Identical to Condition A
- Evaluation set: Identical to Condition A

### Harness Snapshots (Concrete Resources)

- **H1 snapshot**: Git commit hash `abc123def` (or semantic version `v2.1.0`), archived at `/snapshots/harness_h1_v2.1.0.tar.gz`
- **H2 snapshot**: Git commit hash `xyz789uvw` (or semantic version `v2.2.0`-candidate), archived at `/snapshots/harness_h2_candidate.tar.gz`
- **Verification**: Bytewise diff between H1 and H2 must be inspected to confirm only intended harness changes; any prompt template changes must be flagged as confounds

---

## 3. Ablation Designs

### Ablation 1: Repeatability Baseline (Noise Floor)

**Purpose**: Establish the variance of task outcomes under identical conditions, to distinguish signal from noise.

**Design**: Run Condition A (H1 with fixed model/prompt) twice on a random 30% subset of the held-out evaluation set.

- Run A1: Harness H1, task from subset 1, run 1
- Run A2: Harness H1, task from subset 1, run 2 (identical conditions except random seed/ordering)

**Outcome**: Per-task difference distribution (Run A2 - Run A1) gives empirical noise distribution. Expected to be centered near zero; non-zero mean would indicate non-determinism requiring investigation.

**Stopping rule for this ablation**: Complete the subset (N_ablation ≈ 30% × |evaluation_set|). If standard deviation of pairwise differences exceeds 15% for binary/accuracy metrics, flag as concerning; document and continue but note instability.

### Ablation 2: Prompt Instrumentation (Confound Detection)

**Purpose**: Detect whether any prompt changes leaked into H2, masking true harness attribution. Operationalizes the falsifier from state.md: confirm harnesses are truly independent from model/prompt changes.

**Design**: Extract and hash the system prompt used in Condition B. Compare against canonical prompt in `/opt/harness/system_prompts/v1.0.txt`.

- If hashes match: No prompt change detected; confound ruled out.
- If hashes differ: Halt experiment, fix confound, re-run snapshot.

**Outcome**: Boolean confirmation that H1 and H2 run under identical prompts. This ablation is non-parametric; it either passes or the experiment is invalid.

---

## 4. Outcome Metrics (Primary and Secondary)

### Primary Metric: Task Success Rate

- **Definition**: Proportion of tasks on which the harness produces a correct or acceptable answer (as judged by evaluation set ground truth).
- **Computation**: success_rate = (# tasks passed) / (# tasks in sampling frame)
- **Range**: [0, 1]
- **Justification**: Directly reflects whether harness improves end-to-end task completion, independent of model quality. Measured only within the sampling_frame (held-out evaluation set).

### Secondary Metrics

1. **Time to completion** (wall-clock seconds per task)
   - Measures efficiency; harness improvements may reduce unnecessary tool calls.

2. **Token efficiency** (tokens consumed per task)
   - Measures whether the harness is more concise; lower is better given equal success.

3. **Tool call distribution** (frequency and sequence of tools invoked)
   - Diagnostic metric; reveals whether H2 uses tools differently (e.g., fewer redundant calls).

4. **Confidence score or uncertainty quantile** (if model provides it)
   - May correlate with success; useful for segmented analysis.

---

## 5. Analysis Plan

### Step 1: Descriptive Statistics

For each harness version and the sampling frame:

```
Condition         | N_tasks | Success_rate | SE     | 95% CI         | Mean_time_sec | Mean_tokens
H1 (baseline)     | [N]     | [p1]         | [se1]  | [ci_low, hi]   | [t1]          | [tok1]
H2 (candidate)    | [N]     | [p2]         | [se2]  | [ci_low, hi]   | [t2]          | [tok2]
Ablation 1 (H1x2) | [N/3]   | [p_repeat]   | [se_r] | [ci_low, hi]   | –              | –
```

### Step 2: Primary Hypothesis Test

**Test**: Two-proportion z-test or binomial exact test (if N is small).

- Null: p1 = p2 (success rates are equal)
- Alternative: p1 ≠ p2 (two-tailed)
- **Significance level**: α = 0.05

**Effect size**: Compute Cohen's h (difference in arcsine-transformed proportions).

**Interpretation**:
- If CI(p2 - p1) excludes 0 and p2 > p1 → evidence of harness improvement
- If CI(p2 - p1) includes 0 → no statistical evidence of improvement; harness A and B are equivalent
- If p2 < p1 → evidence of regression; investigate why

### Step 3: Robustness Checks

1. **Per-task effect sizes**: For each task i, compute (success_H2[i] - success_H1[i]). Plot histogram to detect outliers or bimodal distributions.

2. **Subgroup analysis**: If evaluation set has task categories (e.g., "reasoning", "search", "synthesis"), compute success rates per category. Test whether improvement is uniform or category-specific.

3. **Replicate ablation results**: Confirm that ablation repeatability (section 3.1) noise is consistent with main effect magnitude.

### Step 4: Confound and Validity Checks

- **Prompt audit** (Ablation 2): Confirm no system prompt drift.
- **Harness diff audit** (bytewise inspection from state.md falsifier): Verify git diff between H1 and H2 commits shows only intended changes. Flag any modifications outside harness directory or any model system prompt changes.
- **Model version check**: Confirm both runs used the same model version/API endpoint.

---

## 6. Uncertainty Quantification

### Primary: Confidence Intervals

For success rate p under each harness:

**Method 1 (Normal approximation)**: 
```
CI = p ± z_{α/2} × SE, where SE = sqrt(p(1-p)/N)
```
Valid when N×p and N×(1-p) both ≥ 5.

**Method 2 (Wilson score interval)**: 
Recommended for smaller N or extreme p. Computed as:
```
CI = [L, U], derived from binomial exact model
```

**Report**: Both the point estimate (p) and 95% CI for each harness version.

### Difference Confidence Interval

For Δ = p2 - p1:
```
CI(Δ) = [Δ - z_{α/2} × SE_Δ, Δ + z_{α/2} × SE_Δ]
where SE_Δ = sqrt(p1(1-p1)/N1 + p2(1-p2)/N2)
```

**Interpretation**: If CI(Δ) does not include 0, evidence of difference at significance level α.

### Robustness via Bootstrap

1. Resample (with replacement) task outcomes within each harness condition (1000 bootstrap replicates).
2. Compute success rate in each bootstrap sample.
3. Plot bootstrap distribution of (p2_boot - p1_boot).
4. Extract 95% CI as [2.5th percentile, 97.5th percentile] of bootstrap distribution.
5. **Sanity check**: Bootstrap CI should be similar to parametric CI; if divergent, investigate distributional assumptions.

### Multiple Comparisons (if applicable)

If secondary metrics are formally tested (not just reported descriptively), apply Bonferroni correction:
```
α_corrected = 0.05 / (number of tests)
```

For example, if testing success rate, time, and tokens, α_corrected = 0.05 / 3 ≈ 0.017 per test.

---

## 7. Concrete Resources and Dependencies

### Data

- **Evaluation set**: `/data/evaluation/held_out_benchmark.jsonl`
  - Format: JSONL, one task per line
  - Required fields: `task_id`, `task_description`, `ground_truth`, `expected_structure`
  - **Size**: Assumed ≥ 100 tasks for adequate power; verify actual size before proceeding
  - **Scope**: This is the sampling_frame; all results are conditional on it

- **Harness snapshots**:
  - H1: `/snapshots/harness_h1_v2.1.0.tar.gz` (commit abc123def)
  - H2: `/snapshots/harness_h2_candidate.tar.gz` (commit xyz789uvw)

- **System prompt**:
  - `/opt/harness/system_prompts/v1.0.txt` (canonical, locked for experiment)

### Execution Environment

- **Model**: Claude 3.5 Sonnet (API version: 2024-12-19, or pinned snapshot)
- **Compute**: Isolated evaluation harness (see constraint: "scoring must not run inside candidate workspace")
  - Evaluation should run in a separate, neutral process
  - Neither H1 nor H2 should be able to observe the scoring function or modify evaluation logic
- **Repeatability**: All random seeds should be fixed (or logged) for reproducibility

### Auxiliary Outputs

- **Experiment log**: `/results/experiment_log_K2.jsonl`
  - Logs each task evaluation with: harness version, task_id, outcome, timestamp, tokens, wall-clock time, any errors
  
- **Audit trail**: `/results/audit_K2.md`
  - Git diffs for H1 and H2 (bytewise inspection per falsifier)
  - Prompt versions and hashes
  - Model/API version info
  - Date/time of experiment run

---

## 8. Decision Boundaries and Stopping Rules

### Stopping Rule: Fixed Evaluation Set

**Primary**: Evaluate all harness versions against all tasks in the held-out evaluation set (sampling_frame). This is a fixed-N design.

**Rationale**: The evaluation set is pre-existing ("held-out evaluation set exists"); we are not sampling within it. We evaluate the full set under each harness.

### Early Stopping Condition (Optional, for Secondary Analysis)

If tracking results in real time:
- After first 50% of evaluation set is complete, compute provisional 95% CI for Δ.
- If CI width is < 5 percentage points and excludes zero, document provisional conclusion.
- **Do not** stop early based on provisional results; complete the full set.
- Final inference uses full data.

### Stopping Rule: Ablation 1 (Repeatability)

Complete the 30% ablation subset. If noise is unexpectedly high (SD > 15% for accuracy metrics), flag but do not expand ablation; document and continue.

### Failure Criteria (Invalidates Experiment)

- Prompt instrumentation (Ablation 2) detects system prompt drift → **Halt and fix**.
- Harness diff audit finds confounded changes (e.g., model prompt modified in H2 commit) → **Halt and refactor**.
- Model version mismatch between H1 and H2 runs → **Re-run with matched versions**.

---

## 9. Reporting and Inference

### Summary Table (Primary Deliverable)

```
Metric                | H1 (Baseline)      | H2 (Candidate)     | Difference (Δ) | 95% CI for Δ   | p-value | Conclusion
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Success Rate          | [p1] (CI)          | [p2] (CI)          | [p2-p1]        | [CI_low, hi]   | [p]     | [Reject/Retain H0]
Mean Time (sec)       | [t1]               | [t2]               | [t2-t1]        | [CI_low, hi]   | –       | [Descriptive]
Mean Tokens           | [tok1]             | [tok2]             | [tok2-tok1]    | [CI_low, hi]   | –       | [Descriptive]
Repeatability (H1x2)  | SD = [sd_noise]    | –                  | –              | –              | –       | [Noise floor]
```

### Interpretation Template

**If Δ > 0 and CI excludes 0**:
- "Harness H2 shows a statistically significant improvement of Δ percentage points over H1 on the held-out evaluation set (sampling_frame). This improvement is consistent with changes made to the harness (per git diff audit and bytewise inspection) and not attributable to model or prompt changes (per Ablation 2 prompt instrumentation)."

**If Δ ≈ 0 and CI includes 0**:
- "No statistically significant difference detected between H1 and H2 on the evaluation set. The observed variation (±[CI width]) is consistent with natural noise (Ablation 1 repeatability baseline). We lack evidence that the harness improvement affected task outcomes within the sampling_frame."

**If Δ < 0**:
- "H2 shows lower success rate than H1. Investigate whether harness changes inadvertently broke existing functionality; review task-specific error logs."

---

## 10. Explicit References to Sampling Frame

Throughout this design, all outcome comparisons are bounded to the **sampling_frame: all tasks in the held-out evaluation set**. 

- **Line 2.2 (Sampling Frame Explicit Reference)**: "Each task in the sampling_frame is evaluated under: Harness H1 + fixed model/prompt → outcome O1; Harness H2 + fixed model/prompt → outcome O2."

- **Line 4 (Primary Metric)**: Success rate "measured only within the sampling_frame (held-out evaluation set)".

- **Line 5.1 (Descriptive Statistics)**: Results are computed as proportions of successful outcomes within the sampling_frame.

- **Line 6 (Uncertainty Quantification)**: All confidence intervals and hypothesis tests use N = size of sampling_frame; CIs are conditional on this frame.

- **Line 7 (Resources)**: "Scope: This is the sampling_frame; all results are conditional on it" (evaluation set section).

- **Line 9 (Reporting)**: The success rate metric is reported as a proportion of tasks in the sampling_frame that succeeded under each harness.

- **Line 8 (Stopping)**: "Primary criterion: Evaluate all harness versions against all tasks in the held-out evaluation set (sampling_frame)."

This ensures no generalization beyond the held-out set and makes clear that results answer the research question for this specific population of tasks, not for all possible tasks.

---

## 11. Summary: How This Design Isolates Harness Improvement

1. **Fixed model and prompt** (Conditions A and B): Eliminates confounding from model capability or prompt changes.

2. **Evaluation outside candidate workspace** (per constraint): Prevents gaming or self-measurement bias.

3. **Explicit comparison within sampling_frame** (held-out evaluation set): Anchors claims to a real, pre-existing task population.

4. **Ablations** (Ablation 1 repeatability, Ablation 2 prompt instrumentation): Establish noise floor and rule out prompt drift.

5. **Bytewise harness audit** (confound checks, operationalizing state.md falsifier): Ensures observed differences map to intended harness changes only.

6. **Uncertainty quantification** (bootstrap CI, Wilson intervals): Distinguishes signal from noise at the granularity of individual tasks.

This design answers: *"Did the harness improve, or would the same model and prompt also improve the H2 setup independently?"* By holding model and prompt constant, evaluating against a fixed sampling_frame, and measuring improvement only within that frame, improvements are attributed to harness changes, not model capability or prompt engineering.
