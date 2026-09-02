# Experimental Design: Measuring Harness Improvement vs. Model Improvement

## Research Question
How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

## Core Problem
When a system's performance improves, the gain could come from:
- **Harness improvement**: better skills, rules, memory, observation format, tool design, etc.
- **Model improvement**: better native capability or better prompting by the model itself
- **Both**

This design isolates harness contribution from model contribution.

---

## Main Experimental Comparison

### Conditions

**Condition A: Baseline (Harness₀ + Model_v)**
- Harness snapshot: current/committed configuration (skills, rules, memory, prompt notes, observation format)
- Model: single pinned model version (e.g., claude-3-5-sonnet-20241022)
- Task execution: use held-out evaluation set (no training/optimization inside this run)
- Scoring: external to candidate workspace, deterministic

**Condition B: Improved Harness (Harness₁ + Model_v)**
- Harness snapshot: refined configuration with improvements (new skill, refined rule, curated memory, better observation format, etc.)
- Model: **identical pinned version** as Condition A
- Task execution: same held-out evaluation set
- Scoring: same external process, deterministic

**Condition C: Repeat Baseline (Harness₀ + Model_v, rerun)**
- Identical to Condition A, executed independently
- Purpose: measure variance and confirm reproducibility
- Harness and model held constant; only randomness is task distribution and model sampling

### Comparison Metric
**Primary: ΔPerf(harness) = Perf(Condition B) - Perf(Condition A)**
- Positive ΔPerf → harness improvement contributed
- Measured as point estimate ± confidence interval (see Uncertainty Quantification below)
- Controlled for: model version, task distribution (held-out set), evaluation scoring process

### Why This Isolates Harness from Model Improvement
- Model version is pinned → no native model capability drift
- Identical task distribution → no distribution shift explaining gain
- External scoring → no model-side prompting improvements can influence the measurement
- If Model_v had internally improved its prompting strategy, it would appear in both Condition A and B equally
- Only harness-level changes (observation format, skills, rules, memory) can cause ΔPerf

---

## Ablation: Component Contribution

### Ablation A: Harness₁ with single key component removed

**Condition D: Improved Harness minus one component (Harness₁-ⱼ + Model_v)**
- Harness snapshot: Harness₁ with one specific improvement reverted
  - Example: if Harness₁ added a skill, remove that skill only
  - Or: if Harness₁ added a rule, remove that rule only
  - Or: if Harness₁ curated a memory entry, remove that entry only
- Model: identical pinned version
- Task execution: same held-out evaluation set
- Scoring: same external process

### Ablation Metric
**ΔPerf(component) = Perf(Condition B) - Perf(Condition D)**
- Shows how much the specific component contributed to ΔPerf(harness)
- If ΔPerf(component) ≈ 0 → component had little effect
- If ΔPerf(component) ≈ ΔPerf(harness) → component explains most of the gain
- Repeat for additional key components if feasible

---

## Analysis Plan

### 1. Primary Hypothesis Test
- **Null**: ΔPerf(harness) = 0 (harness changes made no difference)
- **Alternative**: ΔPerf(harness) > 0 (harness changes improved performance)
- **Test**: One-sided t-test or Wilcoxon signed-rank (depending on metric type and normality)
  - Use Condition A vs. Condition B paired results (if same task instances reused, adjust for dependence)
  - Effect size: Cohen's d or rank-biserial correlation
- **Significance level**: α = 0.05

### 2. Confidence Intervals
- Compute 95% CI on ΔPerf(harness) using:
  - Paired t-test CI if metric is continuous and approximately normal
  - Bootstrap percentile CI (10,000 resamples) if metric is discrete or distribution is unknown
- Interpretation: if CI excludes 0, effect is statistically significant at α = 0.05

### 3. Ablation Analysis
- For each ablated component, compute ΔPerf(component)
- Rank components by contribution size
- Test whether ΔPerf(component) is significantly different from 0
- Visualize as bar chart with error bars (CIs)

### 4. Robustness Checks
- **Repeat Baseline (Condition C)**: Confirm |Perf(A) - Perf(C)| is small relative to |ΔPerf(harness)|
  - Ratio: |ΔPerf(harness)| / |Perf(A) - Perf(C)| should be ≥ 2 (harness effect is larger than noise)
- **Variance estimate**: σ(A, C) from Conditions A and C, used in denominator for effect size
- **Sensitivity to eval set**: If feasible, split held-out set into two sub-sets; run Conditions A & B on both and check consistency

---

## Concrete Resources

### Harness Snapshots
- **Harness₀** (Baseline): 
  - Source: last committed `.claude/` state + CLAUDE.md + current continual harness (memory, skills, rules, prompt notes)
  - Store as: `design_workspace/harness_baseline.tar.gz` (timestamped, git hash noted)
  - Contents: all prompt_note/*.md, memory/*.md, skill/*.md, rule files, settings.json state
  
- **Harness₁** (Improved):
  - Source: refined `.claude/` state reflecting one or more deliberate improvements
  - Store as: `design_workspace/harness_improved.tar.gz` (timestamped, git hash noted)
  - Diff: `design_workspace/harness_diff.txt` (explicit list of what changed between Harness₀ and Harness₁)

- **Harness₁-ⱼ** (Ablated):
  - Source: Harness₁ with component j reverted
  - Store as: `design_workspace/harness_ablated_component_j.tar.gz`

### Evaluation Set
- **Location**: `/private/tmp/study-a-conf/K2-harness-vs-model__C00__r2/eval_set.jsonl` (if exists)
- **Specification**:
  - If it does exist: format (schema), size (N tasks), task distribution (categories/types)
  - If it does not exist: describe what "held-out" means for this project (e.g., test cases, synthetic tasks, human-authored examples)
  - Constraint: must not be accessed by candidate workspace during execution
  
### Model and Execution Environment
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Execution**: Claude Code sessions run in isolated sessions, one per condition
  - Session A for Condition A (Harness₀)
  - Session B for Condition B (Harness₁)
  - Session C for Condition C (Harness₀, rerun)
  - Session D for Condition D (Harness₁-j) if ablation runs
- **Tool prohibition**: No tool calls that access the eval set *from within the candidate workspace*
  - Eval set must be served to the workspace as read-only input, or results collected externally

### Scoring Infrastructure
- **Location**: External, separate from candidate workspace
  - Script: `design_workspace/score_results.py` (deterministic, no LLM in the loop)
  - Metrics computed: accuracy, pass rate, cost (tokens), latency, task-specific metrics
- **Input**: results from each condition (structured output from candidate workspace runs)
- **Output**: `design_workspace/results/condition_a_metrics.json`, `condition_b_metrics.json`, etc.

---

## Outcome Metrics

### Primary Metric
**Task Success Rate (%)**: Fraction of tasks in the held-out eval set on which the system produced a correct/successful outcome
- Justification: Most direct measure of system improvement
- Computation: (# successful tasks) / (total # tasks) × 100
- Type: Discrete / Proportion
- Analysis: Paired comparison of success counts across conditions

### Secondary Metrics
1. **Accuracy (if task allows partial credit)**: e.g., BLEU, exact match on code, semantic similarity
   - Type: Continuous or ordinal
   - Analysis: Same paired comparison

2. **Token Cost per Task**: Mean tokens (input + output) per task
   - Justification: Harness may trade accuracy for efficiency
   - Computation: Total tokens used / # tasks
   - Type: Continuous
   - Caution: Do not interpret as model improvement; document any cost tradeoffs

3. **Latency (wall-clock time per task)**: Mean seconds per task completion
   - Justification: Harness quality may affect iteration count and speed
   - Type: Continuous
   - Analysis: Paired comparison

4. **Task Category Breakdown (if applicable)**:
   - If eval set has categories (e.g., "arithmetic," "code," "reasoning"):
     - Compute success rate per category
     - Test whether harness improvement is uniform or category-specific
     - Helps interpret what the harness improved at

### Null-model Baselines (for sanity checks)
- **Random baseline**: Success rate if the system always chose randomly
  - Interpretation: Harness improvement must exceed random chance
- **Trivial baseline** (if applicable): e.g., "always output the first option"
  - Interpretation: Harness improvement must outperform naive strategies

---

## Uncertainty Quantification

### 1. Statistical Testing
- **Method**: Paired t-test (if success counts are continuous or large N) or Wilcoxon signed-rank test (if counts are discrete)
- **Assumption check**: 
  - If metric is success rate on N tasks, report normality test (Shapiro–Wilk on ΔPerf per task or across runs)
  - If N is large (N > 30), t-test is robust even if non-normal
- **Output**: t-statistic, p-value, degrees of freedom
- **Example**: 
  - H₀: μ(ΔPerf) = 0
  - H₁: μ(ΔPerf) > 0
  - Report: t(N-1) = ___, p = ___, two-tailed or one-tailed as specified

### 2. Confidence Intervals
- **95% CI on ΔPerf(harness)**:
  - Paired t-test CI: ΔPerf ± t(0.975, N-1) × SE(ΔPerf)
  - Bootstrap CI: Resample task pairs with replacement, recompute ΔPerf, extract [2.5th, 97.5th] percentiles
  - Interpretation: 95% probability that true effect lies in this range (under model assumptions or empirically)

### 3. Effect Size
- **Cohen's d**: d = ΔPerf / σ(Condition A, C pooled)
  - Interpretation: d > 0.2 is small, d > 0.5 is medium, d > 0.8 is large
- **Percent improvement**: 100 × ΔPerf / Perf(A)
  - Interpretation: Intuitive scale of relative improvement

### 4. Variance Estimation
- **Variance from Condition C**:
  - σ²_C = Var(Condition A, Condition C paired differences)
  - This estimates the measurement noise in the system
  - Used in denominator for Cohen's d and in CI calculations

### 5. Sensitivity Analysis
- **Replication across eval-set splits**:
  - Split held-out set into two halves
  - Run Conditions A & B on both halves
  - Compute ΔPerf on each half; check if consistent
  - Report: ΔPerf_half1, ΔPerf_half2, whether signs and magnitudes agree
  - Interpretation: If ΔPerf flips sign or magnitude between halves, effect may not be robust

### 6. Ablation Uncertainty
- Compute CI on ΔPerf(component) for each ablated component
- Compare CIs to check if components' contributions overlap
- If CIs overlap, conclude components' effects are not significantly different

---

## Summary: Decision Rule

| Result | Interpretation |
|--------|-----------------|
| ΔPerf(harness) > 0, 95% CI excludes 0, |ΔPerf| > noise | Harness improvement is statistically significant and likely real. |
| ΔPerf(harness) > 0, 95% CI includes 0, or |ΔPerf| ≈ noise | Harness change is not distinguishable from random variation. |
| ΔPerf(harness) < 0, 95% CI excludes 0 | Harness change harmed performance. |
| Ablation: ΔPerf(component_j) ≈ ΔPerf(harness) | Component j is the primary driver. |
| Ablation: ΔPerf(component_j) ≈ 0 | Component j contributed little; may be removable. |

---

## Implementation Checklist

- [ ] Snapshot Harness₀ with timestamp and git hash
- [ ] Design Harness₁ improvements; snapshot with timestamp and git hash
- [ ] Document Harness₀ → Harness₁ diff explicitly
- [ ] Confirm eval set exists, is held-out, and cannot be accessed from candidate workspace
- [ ] Set up external scoring script (no LLM in the loop)
- [ ] Run Condition A (Harness₀ + Model_v)
- [ ] Run Condition B (Harness₁ + Model_v)
- [ ] Run Condition C (Harness₀ + Model_v, rerun)
- [ ] Collect metrics from all conditions into JSON files
- [ ] Compute ΔPerf(harness) and 95% CI
- [ ] Perform hypothesis test (t-test, Wilcoxon)
- [ ] Compute Cohen's d and percent improvement
- [ ] Run ablation (if applicable): Condition D (Harness₁-j + Model_v)
- [ ] Perform sensitivity check: split eval set, rerun on halves
- [ ] Visualize results: bar plots with error bars, ablation breakdown
- [ ] Write interpretation: what harness improvements drove the gain? Are they reproducible?

---

## Notes on Validity

### Threats to Validity

1. **Model stochasticity**: Even with pinned model version, there is sampling variation.
   - Mitigation: Run multiple replicates (Condition C measures this); use CIs and statistical tests.

2. **Eval set contamination**: If the candidate workspace somehow accesses the eval set during training/development, results are invalid.
   - Mitigation: Scoring is external; candidate workspace receives only task inputs, not solutions.

3. **Harness snapshot incompleteness**: If some harness state is not captured (e.g., environment variables, .claude settings applied dynamically), snapshots may not be reproducible.
   - Mitigation: Document all harness state sources (CLAUDE.md, continual-harness entries, settings.json, rules files); include in tar.gz.

4. **Multiple comparisons**: If testing many ablations, p-value thresholds should be adjusted (Bonferroni or FDR).
   - Mitigation: Prioritize one or two key ablations as primary; others as exploratory.

### Construct Validity
- Does "success rate" capture what we mean by harness improvement?
  - If tasks are open-ended or subjective, consider qualitative review in addition to automated scoring.
  - If tasks have multiple correct answers, scoring logic must handle equivalence.

---

## Deviations and Justifications

- **Why measure at the harness level, not the model level?**
  - The research question asks how to measure harness improvement *independent* of model improvement.
  - By pinning the model version, we isolate harness.

- **Why include Condition C (repeat baseline)?**
  - To measure system noise and confirm reproducibility.
  - Justifies using t-test or bootstrap CI.

- **Why ablate?**
  - To understand *which* harness components drove improvement.
  - Without ablation, we know the harness improved but not why.

- **Why external scoring?**
  - To prevent candidate workspace from gaming or contaminating the eval set.
  - To ensure scoring is deterministic and not influenced by model state inside the workspace.
