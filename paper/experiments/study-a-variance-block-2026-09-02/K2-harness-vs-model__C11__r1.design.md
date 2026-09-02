# Experimental Design: K2 Harness vs Model

## Research Question
How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

## Design Rationale and Confounding Strategy

The core threat to validity is **confounding between harness structure improvements and prompt engineering**. To isolate harness effect from model prompt improvements, the design holds the base model and its prompt instructions constant across all conditions, and varies only the candidate harness structure (e.g., agent architecture, tool definitions, workflow branching, memory layout). Outcome improvements in harness B vs. harness A are attributed to structure, not model capability or prompt choice.

However, outcome-only measurement misses silent harness failures—tasks that reach the correct final answer but violate process checks that the harness was designed to enforce. We rely on evidence from **2609.00038 (trajectory-judge)** which demonstrates that step-level rubric judges catch 77% of silent faults while outcome-only judges catch only 45%, and from **2608.29517 (LLM rater effects)** which quantifies judge severity drift and provides calibration methods. Therefore, measurement occurs at the **trajectory level**, scoring intermediate steps and process compliance as well as outcome.

## Sampling Frame

**Population**: Task instances drawn from the held-out evaluation set (the finite, designated evaluation corpus provided for this study).

**Unit of analysis**: A single (task, harness-version, base-model, judge) triplet. Each unit is a trajectory produced by running a fixed base model with a candidate harness version on a held-out task, then scored by a calibrated LLM judge against a step-level rubric.

**Sampling strategy**:
- Tasks are sampled from the evaluation set without replacement.
- Base model is held constant (one version, pinned, frozen, used identically across all harness conditions).
- Harness version is the main experimental variable (two versions: Harness A, Harness B).
- Each (task, harness-version) pair is run multiple times (repeats) to account for within-task stochasticity in the model's generation, following the variance-components allocation strategy in **2607.13304 (Zatuchin)**.

## Main Comparison

**Condition A**: Baseline harness version (candidate A).

**Condition B**: Candidate harness version (candidate B), expected to improve process structure.

**Null hypothesis**: No difference in trajectory-level rubric scores between harness A and harness B, holding base model and prompt constant.

**Paired structure**: The same task instances are run in both harness versions (paired by task), enabling a **paired hypothesis test** (McNemar-style for ordinal/categorical rubric outcomes, or paired t-test if rubric scores are treated as continuous). Pairing increases power to detect harness effects by leveraging between-task variance (per **2605.30315**, paired tests account for correlation structure and reduce sample-size requirements by factor of 2 compared to naive unpaired shortcuts).

## Ablation Study

**Ablation: Judge severity calibration**

Run both harness versions (A and B) on the same task set, but score trajectories using:

1. **Uncalibrated judge**: LLM judge applied directly to rubric without severity adjustment.
2. **Calibrated judge**: Same LLM judge, pre-anchored on a held-out anchor set (~30–50 reference essays per rubric, hand-annotated or expert-scored), with severity adjustment applied post-hoc.

**Prediction**: If harness effect is genuine, calibrated scores should preserve rank ordering (A vs B) and significance. If judge severity dominates, uncalibrated vs calibrated scores may reverse orderings (per **2608.29517 permutation null**), signaling that improvement is an artifact of judge calibration rather than harness design.

**Justification**: This ablation isolates measurement error (judge severity) from harness effect, addressing the falsifier "severity-adjusted scores reverse rank ordering."

## Comparison Conditions and Operationalization

### Scoring Layer: Step-Level Rubric

Define a **multi-dimensional trajectory rubric** scoring intermediate steps, not just final outcome. Rubric dimensions include (non-exhaustive):

- **Tool retrieval quality**: Did the agent call the correct tool at each step? Score per step.
- **Evidence utilization**: Did the agent correctly interpret and apply information returned by tools? Score per step.
- **Process compliance**: Did the agent complete required pre-checks or post-checks that the harness mandates (e.g., validation steps, backtracking on error)? Binary or ordinal per step.
- **Final outcome accuracy**: Did the agent produce the correct final answer? Binary or continuous.

Each rubric dimension is scored at the **step level** (trajectory granularity), not outcome-only, per guidance in **2609.00038**.

### Judge Procedure

1. **Judge version pinning**: Pin LLM judge version (model identifier, serving date, parameters). Record version in all scoring runs.
2. **Anchor set calibration** (pre-run): Before any experimental scoring, run the judge on a held-out anchor set (30–50 reference trajectories, expert-annotated or independently verified). Measure judge severity on each dimension (mean score, SD). Compute severity offset per dimension.
3. **Experimental scoring**: Score all experimental task trajectories using the same judge instance. Apply severity adjustment post-hoc using anchor-set offsets.
4. **Drift monitoring** (during run): On a fixed monitor set (20–30 trajectories, re-scored on a schedule, e.g., every N runs), measure judge calibration drift. If drift exceeds permutation null (per **2608.29517**), flag, re-calibrate, or halt.

### Repeat Allocation

Based on **2607.13304 variance-components decomposition**:

- Identify separable noise facets in LLM trajectories: within-task (model sampling temperature), within-task paraphrase (rephrase the same prompt), between-task (different evaluation questions).
- Allocate repeats to maximize precision of target estimand (harness A vs B comparison). If within-task variance dominates, buy more repeats per task. If between-task variance dominates, buy more distinct tasks.
- Crossed random-effects design (generalizability theory): each task × harness × repeat is a cell in a crossed design, enabling variance-component estimation via REML or simulation.

Allocation rule: Start with preliminary sample (e.g., 5–10 tasks × 2 harnesses × 3 repeats = 30–60 trajectories). Estimate variance components. Recompute required sample size for target power (α=0.05, 1−β=0.80, minimum detectable effect per 2605.30315). Re-allocate repeats to optimal task × repeat ratio.

## Analysis Plan

### Primary Analysis: Paired Hypothesis Test

**Test**: Paired t-test (if rubric scores are treated as continuous aggregates) or McNemar test (if outcomes are binary or ordinal).

**Test statistic**: Difference in mean rubric score between harness B and harness A, over the paired task sample. (Per **2605.30315**, explicitly compute N* for paired test accounting for within-pair correlation ρ; use N_unpaired / (1 − ρ) adjustment, not naive Cohen-h shortcut.)

**Inference**: Report point estimate (mean difference), 95% CI (or exact binomial CI for categorical outcomes), and p-value under permutation null. Reject null hypothesis if p < 0.05 and CI does not include zero.

**Secondary analysis**: Stratify by task complexity, task domain, or harness dimension (e.g., if harness B changes tool retrieval vs. memory layout, separate these effects).

### Ablation Analysis: Calibration Effect

**Comparison**: Rank orderings and significance (p-values, CIs) from uncalibrated vs. calibrated judge scores. If calibrated and uncalibrated order harnesses the same way with overlapping CIs, judge calibration is not a confound. If orderings reverse or CIs no longer include zero after calibration, judge severity dominated the effect (falsifier triggered).

### Variance-Components Fit

Fit generalizability-theory crossed random-effects model (task, harness, repeat, judge) to trajectory scores. Extract variance components:
- σ²_within-task-repeat (model sampling stochasticity)
- σ²_task (between-task heterogeneity)
- σ²_task:harness (task-by-harness interaction, i.e., harness effect varies by task)
- Residual (measurement noise)

**Interpretation**: If σ²_task >> σ²_within-task, design should prioritize task sample size; if vice versa, prioritize repeats. If σ²_task:harness is large, harness effect is not stable across tasks (potential falsifier or boundary condition).

### Judge Drift Monitoring

On the fixed monitor set (20–30 trajectories), re-score every N experimental runs. Fit linear trend in monitor-set scores over time (run index). Test slope ≠ 0 at α=0.05. If significant drift, re-calibrate or halt (per stopping rule, falsifier 2).

## Outcome Metrics

### Primary Outcome

**Harness effect (Δ)**: Mean trajectory-level rubric score in Harness B minus mean score in Harness A, paired by task. Aggregated across all rubric dimensions (or separately per dimension if prespecified).

Interpretation: Δ > 0 favors Harness B; Δ < 0 favors Harness A. Magnitude and CI inform effect size and certainty.

### Secondary Outcomes

1. **Dimension-specific effects**: Repeat primary analysis separately for each rubric dimension (tool retrieval, evidence utilization, process compliance, outcome). Identify whether harness improvement is concentrated in process compliance (expected for harness-level improvements) or dilute across dimensions (suggesting outcome-only measurement noise).

2. **Silent failure recall**: On the subset of task instances where final outcome is correct but trajectory has process violations, compare Harness A vs B on rubric score (focusing on process dimensions). This tests the mechanism by which harness improvement operates (improved process adherence even when outcome is correct).

3. **Severity-adjusted vs. unadjusted effect**: Report point estimate of Δ before and after severity adjustment. If they differ by more than the CI width, judge calibration is a material confound.

4. **Between-task variance in harness effect**: Report task-by-harness interaction variance component (σ²_task:harness). If large relative to main effect variance, harness improvement is not robust across task types.

## Uncertainty Quantification

### Statistical Uncertainty (Hypothesis Testing)

- **Paired test p-value**: Exact binomial (if outcome binary) or t-test p-value. Two-tailed, α=0.05.
- **95% Confidence Interval**: Computed via percentile bootstrap (if rubric scores non-normal) or t-distribution (if approximately normal). Include unequal-variance adjustment if task-pairing is imperfect (e.g., some tasks appear in only one harness due to failure/crash).
- **Power analysis post-hoc**: Compare achieved sample size (task count × repeat count) to target N* (computed via 2605.30315 paired-test resolution formula). Report whether design achieved 80% power for observed minimum detectable effect.

### Measurement Uncertainty (Judge Calibration and Drift)

- **Severity offset CI**: Report 95% CI on each judge-severity parameter (anchor-set mean per dimension). Measure precision of severity calibration.
- **Drift p-value**: Linear regression of monitor-set scores over run index. Report slope point estimate, 95% CI, and p-value. If p < 0.05, conclude judge drift; adjust scores or flag.
- **Reproducibility**: Record all judge versions, anchor set, and monitor set. Publish judge prompts and rubric wording. Compute inter-rater agreement (if second judge is available) on a subsample, or replication agreement (same judge, same rubrics, independent re-scoring of 20–30 trajectories) on a held-out set.

### Between-Trial Variability (Repeatability)

- **Repeat-level variability**: Report σ_within-task (standard deviation of trajectory score for the same task, harness, across repeats) and relative standard error (RSE = σ / N_repeats^0.5). If RSE is large (>0.15), repeats are unreliable and additional repeats or process standardization is needed.
- **Generalizability coefficient**: Fit crossed random-effects model and compute generalizability coefficient G^2 for the (task, harness) universe, interpreting as "if we run this comparison again on a new task sample, what is the probability we'd get the same conclusion?" Report G^2 ≥ 0.80 as a target; if lower, design is not generalizable.

## Concrete Resources

### Evaluation Corpus
- **Held-out evaluation set**: The designated evaluation set provided for this study (finite, known corpus of task instances, with ground-truth answers or process-level annotations if available).
- **Task sample size**: TBD pending power analysis. Minimum 20 tasks recommended (per 2010.06595 power norms for NLP), up to 50 tasks if between-task variance is high.
- **Anchor set**: 30–50 reference trajectories, either existing or newly generated, with expert annotations or independent verification of rubric scores. Kept separate from experimental task sample.
- **Monitor set**: 20–30 trajectories, fixed and re-scored throughout experimental run on a schedule (e.g., every 10 experimental runs). Separate from anchor and task sets.

### Base Model and Harness Versions
- **Base model**: One pinned version, identical across all conditions (model name, version, temperature, other hyperparameters frozen). Recorded explicitly.
- **Harness A (baseline)**: Snapshot of current/baseline harness. Architecture, tool definitions, workflow structure, memory schema, and system prompt recorded and versioned.
- **Harness B (candidate)**: Snapshot of improved harness. Documented differences from Harness A (e.g., added tool validation step, changed memory schema).

### Judge
- **LLM judge**: Pinned model and version (e.g., Claude-Opus-4.7, serving date 2026-01-15, temperature 0.0). Judge is external to the evaluated harnesses (scoring layer outside the candidate workspace, per constraint: "scoring must not run inside candidate workspace").
- **Rubric**: Multi-dimensional step-level rubric with explicit scoring instructions. Dimensions: tool retrieval quality, evidence utilization, process compliance, outcome accuracy (or domain-specific equivalents). Ordinal or continuous scales per dimension. Rubric wording finalized and frozen before experimental runs.

### Computation and Logging
- **Logging infrastructure**: Each (task, harness, repeat) trajectory is logged with:
  - Task ID, harness ID, repeat index
  - Full trajectory (step-by-step prompts, model outputs, tool calls, tool returns)
  - Judge scores (per dimension, per step, and aggregate)
  - Timestamp, model version, temperature, other hyperparameters
  - Judge version and severity offset applied
- **Analysis code**: Paired t-test (scipy.stats.ttest_rel or equivalent), McNemar test (statsmodels), REML variance-component fitting (R lme4 or Python statsmodels), permutation test for drift (scipy.stats.permutation_test). Code versioned and reproducible.

## Assumptions and Sensitivity

### Key Assumptions
1. **Rubric validity**: Rubric dimensions measure harness quality and not model capability or prompt engineering quality. Assumption justified by prior literature (2607.09195 hypothesis evolution, 2608.03501 stage isolation) but not validated in this study. Tested via falsifier: if A and B indistinguishable under rubric, rubric is insensitive to relevant harness variation.

2. **Judge stability**: LLM judge scores are stable under repeated scoring of the same trajectory and across the experimental time window. Tested via monitor set and drift analysis.

3. **Harness isolation**: Base model prompt and generation parameters are truly held constant and do not drift between conditions. Verified by recording prompt and parameters in every run and checking for differences post-hoc.

4. **Independence of repeats**: Trajectory outcomes (e.g., tool calls) are not deterministically repeated; each repeat explores different paths due to sampling temperature or stochasticity in tool environments. If repeats are deterministic copies, variance-component estimates are invalid.

### Sensitivity Analysis (If Design Assumptions Are Violated)

- If rubric is insensitive (A and B indistinguishable): Report null finding; do not claim harness effect. Consult rubric against prior literature and task-domain experts.
- If judge drift is detected: Re-fit analysis excluding drifted runs; report effect size both with and without re-equating.
- If base model prompt accidentally differs between conditions: Post-hoc check via prompt string comparison. If differences found, conduct sensitivity analysis: re-estimate effect holding only identical-prompt runs.
- If repeats are highly correlated (within-repeat variance ≈ 0): Reduce effective sample size in power and CI calculations; report design is overpowered (fewer independent measurements than intended).

## Stopping Rule

Halt data collection and proceed to analysis when **any** of the following is satisfied:

1. **Minimum detectable effect threshold crossed** (per 2605.30315 paired-test resolution):
   - Compute N* for α=0.05, 1−β=0.80, minimum detectable effect δ (smallest effect size considered meaningful, TBD in protocol). If achieved task sample size ≥ N*, stop.

2. **Judge calibration is stable** (per 2608.29517 drift monitoring):
   - Monitor-set p-value for drift slope ≥ 0.05 (no significant drift). Drift monitor re-scored on every Nth experimental run (N TBD, e.g., N=10).

3. **Variance components estimated to target precision** (per 2607.13304 generalizability theory):
   - Within-task variance component σ_within-task estimated with relative standard error (RSE) < 0.15. If RSE acceptable, further repeats do not improve precision materially.

4. **Harness versions are indistinguishable** (falsifier 1):
   - Paired t-test p > 0.10 (fail to reject at a weak threshold) and 95% CI for Δ fully contains [−δ, +δ] (minimal effect uncertainty). Halt and report null.

5. **Judge drift exceeds tolerance** (falsifier 2):
   - Drift-monitor p < 0.05 and severity shift magnitude > 0.5 SD of the experimental score distribution. Halt, re-calibrate, and restart experimental-scoring phase.

**Maximum sample size cap** (soft upper bound): 200 trajectories total (e.g., 50 tasks × 2 harnesses × 2 repeats). If this cap is reached before early stopping, terminate and analyze with achieved sample.

## Reporting Plan

Report will include:

1. **Filled research state** (decision_id, question, alternatives, sampling_frame, evidence_used, falsifiers, stopping_rule).

2. **Main comparison result**: Point estimate of Δ (mean rubric score difference, Harness B − A), 95% CI, p-value, effect size (Cohen's d or equivalent). Interpretation: statistical significance, practical magnitude, and uncertainty.

3. **Ablation result**: Comparison of uncalibrated vs. calibrated judge scores; any evidence of severity-driven spurious effects.

4. **Variance components**: Fitted REML model with point estimates and CIs for σ²_task, σ²_within-task, σ²_task:harness, and residual. Interpretation: which noise source dominates.

5. **Judge calibration report**: Severity offset per dimension (anchor-set mean and CI), drift trajectory (slope and p-value), reproducibility check (if applicable).

6. **Dimension-specific effects**: Harness effect on each rubric dimension separately. Identify whether improvement concentrates in process dimensions (supporting harness effect) or scatters across dimensions (suggesting noise or rubric insensitivity).

7. **Falsifier assessment**: Did any falsifier trigger? If yes, report which, evidence, and implications for validity.

8. **Limitations and threats to validity**: Rubric validity, judge stability, scope (one base model, one evaluation corpus, one harness pair).

9. **Pre-registered protocol and reproducibility artifacts**: Full rubric text, judge prompt, anchor-set annotations, monitor-set IDs, code for analysis, data-integrity checks.

---

## References to Evidence

This design relies on specific methodological findings from the released evidence pack:

- **2010.06595** (Card et al.): Statistical power norms and minimum sample-size guidance for NLP experiments.
- **2605.30315** (Kotawala): Paired resolution diagnostics and minimum-detectable-effect calculation for paired LLM evaluations.
- **2607.13304** (Zatuchin): Variance-components decomposition (generalizability theory) to optimize repeat allocation in LLM measurement.
- **2608.03501** (Liu et al., OptED): Stage isolation for experimental design to separate high-level comparison structure from low-level metric configuration.
- **2608.29517** (Sunkavalli): LLM judge severity, halo, drift, and calibration methods; pre-registration and remedies for judge instability.
- **2609.00038** (Mohammadi, trajectory-judge): Outcome-only judging blind spots and superiority of step-level rubric judging for silent-failure detection.

All design choices (sampling, judge procedure, repeat allocation, ablation) are grounded in these evidence sources.
