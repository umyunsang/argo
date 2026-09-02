# Experimental Design: K1-Hypothesis-Search

## Executive Summary

This design tests whether hypothesis-tree organization of autonomous agent optimization attempts (with cross-branch insight propagation) outperforms a flat queue baseline on held-out artifact optimization tasks, within a fixed compute budget per task. The experiment uses a within-subjects design across 12–16 held-out tasks, comparing two agent orchestration arms under balanced compute constraints and measuring promotion accuracy and artifact quality.

## Research Question

Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

---

## Main Comparison Design

### Contrast Arms

**Arm 1: Hypothesis-Tree (Treatment)**
- Agent orchestration: Structures optimization attempts as a tree, where each node represents an attempt and branches represent alternative hypotheses or parameter variations.
- Insight propagation: Failed branches inform sibling and parent nodes; learned constraints and patterns flow upward and across the tree via the continuous-learning mechanism.
- Decision rule: At each tree level, promote the most promising child node(s) to the next level, guided by held-out validation performance.
- Implementation: Uses ECC's multi-agent dispatch (via `rlm()` and agent_message) to coordinate tree branches, with a shared memory layer (via continual harness) storing cross-branch insights.
- Backbone: Same inference and action backend as Arm 2.

**Arm 2: Flat Queue (Control)**
- Agent orchestration: Structures optimization as a sequence of independent attempts, with no cross-attempt learning or branching.
- Scheduling: Each attempt is launched with identical compute allocation; no attempt sees results from previous attempts in its decision logic.
- Decision rule: Rank attempts by held-out validation score; treat the best-ranking attempt as the final artifact.
- Implementation: Each attempt is an isolated subagent spawn with no inter-attempt memory sharing.
- Backbone: Same inference and action backend as Arm 1.

### Sampling Frame (from state.md)

**Population:** Held-out artifact optimization problems from the OpenResearch/evaluation benchmark suite.

**Unit:** A single (task, agent_arm, budget_allocation) tuple.

**Sample:** 12–16 held-out tasks, stratified by problem class:
  1. **Gradient-free tuning** (e.g., hyperparameter optimization for a fixed model): 4–5 tasks
  2. **Code generation artifact quality** (e.g., optimizing generated solver or compiler output): 4–5 tasks
  3. **Architecture search or configuration search** (e.g., prompt template tuning or sub-agent team composition): 4–5 tasks

Each task is independently evaluated on both arms (tree vs. flat-queue) under identical compute budgets. Expected minimum N = 24 observations (12 tasks × 2 arms).

---

## Ablation Study

### Ablation: Insight Propagation Disabled (Hypothesis-Tree without Cross-Branch Learning)

**Arm 3: Tree-Structure, No Propagation (Ablation)**
- Uses the same tree orchestration as Arm 1 (branching, hierarchy, promotion rules).
- **Disabled:** Cross-branch insight sharing and memory propagation; each branch learns independently.
- Purpose: Isolates whether observed gains come from tree structure (implicit load-balancing, hierarchical pruning) or from explicit insight propagation (what continuous-learning-v2 mechanisms add).
- Implementation: Tree-based dispatch (same as Arm 1) but with all continual harness memory writes isolated per branch, no shared notes or instincts across branches.
- Analysis: Compare Arm 1 (full tree + propagation) vs. Arm 3 (tree-structure only). If Arm 1 >> Arm 3, propagation matters. If Arm 1 ≈ Arm 3, tree structure is the active ingredient.

---

## Concrete Conditions and Resource Allocation

### Per-Task Budget

Each task receives a fixed compute budget:
- **Wall-clock time:** 4 GPU-hours (single H100 or equivalent)
- **Token budget (per subagent):** 100k tokens (conservative estimate for artifact optimization)
- **Subagent concurrency:** Maximum 4 simultaneous branches/attempts (to fit within queue constraints)
- **Held-out validation set:** 3–4 examples per task, reserved for arm-level comparison

### Infrastructure

- **Execution platform:** OpenResearch (orx) via Prime Intellect GPU pods
- **Compute nodes:** H100 GPUs, 80 GB memory each (resource-constrained optimization workloads do not require A100-plus)
- **Storage:** OpenResearch artifacts directory (persisted per run)
- **Experiment management:** `orx` CLI with frozen branches for Arm 1, Arm 2, and Arm 3

### Experiment Orchestration

- **Control plane:** ECC agent (prime-agent instance) coordinates task scheduling, arm assignment, and result collection
- **Subagent coordination:** Via `agent_message.send()` and shared continual harness entries
- **Data flow:**
  - Task definitions → distributed to all arms
  - Arm results → collected to local artifacts/ directory
  - Held-out validation scores → indexed for cross-arm comparison

---

## Outcome Metrics

### Primary Metrics

1. **Promotion Accuracy** (held-out)
   - Definition: For each held-out task, measure the arm's ability to select an artifact in the top-2 performers (by held-out validation score) after all budget is consumed.
   - Measurement: Binary: 1 if arm's selected artifact ranks ≤2 on held-out set; 0 otherwise.
   - Aggregation: Mean promotion accuracy across all tasks (percentage).
   - Justification: Directly measures whether the arm's decision-making (tree propagation vs. flat queueing) picks better final artifacts under budget constraint.

2. **Artifact Quality Score** (held-out)
   - Definition: The held-out validation score of the final artifact selected by each arm.
   - Measurement: Task-specific metric (e.g., test accuracy for model tuning, test coverage for code generation). Normalized to [0, 100] for cross-task comparison.
   - Aggregation: Mean and median across all tasks; stratified by problem class.
   - Justification: Complements promotion accuracy; measures absolute quality, not just relative ranking.

### Secondary Metrics

3. **Compute Efficiency**
   - Definition: Number of attempts (subagent launches) per arm before budget exhaustion.
   - Measurement: Integer count of completed subagent runs.
   - Aggregation: Mean attempts per task, by arm.
   - Justification: Reveals whether tree pruning reduces wasted attempts or whether flat queue converges faster.

4. **Insight Utilization** (Arm 1 and Arm 3 only)
   - Definition: Number of cross-branch memory updates in continual harness per task (Arm 1 only).
   - Measurement: Count of instinct/note entries created in shared memory per task.
   - Aggregation: Mean per task.
   - Justification: Validates that propagation mechanism is actually firing.

---

## Analysis Plan

### Hypothesis Testing

**Primary hypothesis:** Arm 1 (tree + propagation) achieves higher promotion accuracy than Arm 2 (flat queue) on the held-out task set.

**Test:** Paired t-test, with task as the unit (12–16 observations).
- Null: μ(Arm 1 promotion accuracy) = μ(Arm 2 promotion accuracy)
- Alternative (two-sided): μ(Arm 1) ≠ μ(Arm 2)
- Significance level: α = 0.05
- Minimum detectable effect size: 2 percentage points (e.g., 75% → 77%)

**Secondary hypothesis:** Arm 1 achieves higher held-out artifact quality than Arm 2.

**Test:** Paired t-test on artifact quality scores.
- Same structure as above.

### Stratified Analysis

1. **By problem class:** Repeat the paired t-test within each problem class (tuning, code generation, architecture search) to identify whether the tree advantage generalizes or concentrates in specific task types.

2. **By compute utilization:** Stratify by number of attempts completed (e.g., tasks where both arms completed ≥3 attempts). Justification: shallow trees may not have propagation advantage.

### Ablation Analysis

**Ablation hypothesis:** Arm 1 (full tree + propagation) outperforms Arm 3 (tree-structure only).

**Test:** Paired t-test on promotion accuracy and artifact quality, Arm 1 vs. Arm 3.
- If Arm 1 >> Arm 3: Propagation is the active ingredient.
- If Arm 1 ≈ Arm 3: Tree structure alone (branching, pruning) explains gains; propagation is not independently valuable.
- If Arm 3 >> Arm 1: Tree structure without propagation is actually harmful (suggests propagation prevents exploration).

---

## Uncertainty Quantification

### Primary Approach: Confidence Intervals

For each arm on each task, compute the 95% confidence interval on promotion accuracy using exact binomial CI (since the metric is binary: promoted vs. not promoted).

Aggregate across tasks using Clopper–Pearson intervals on the aggregated count, or report the mean CI across tasks.

### Secondary Approach: Effect Size and Non-Centrality

Report Cohen's d (effect size) for the paired t-test, along with the 95% CI on d itself. This frames the result as "we observed a Δ of [X% ± Y% confidence] in promotion accuracy."

### Stratified Uncertainty

Repeat CI calculations within each problem class. If N per class < 4, note that stratified inference is underpowered and report descriptive statistics only.

### Robustness Check: Median Difference

Since artifact quality scores may be non-normal (especially if they cluster at ceiling or floor), also report the Hodges–Lehmann median difference (median difference in paired scores) and its 95% CI via permutation resampling.

### Missing Data Handling

If any arm fails to complete a task (e.g., compute timeout, crash), report it as missing and proceed with the remaining N-1 observations. Sensitivity analysis: re-run the test assuming the missing observation favors the other arm (conservative imputation). If qualitative conclusion changes, highlight this.

---

## Concrete Resources and Dependencies

### Data Resources

- **OpenResearch benchmark tasks:** Assumed available at `/openresearch/benchmarks/evaluation/held-out/` (or similar public path in Prime Intellect).
- **Validation split:** Pre-defined within each task (3–4 examples reserved per task).
- **Baseline results:** No external baseline required; Arm 2 (flat queue) serves as the control.

### Code and Tooling

- **Agent orchestration:** ECC Prime Agent (python kernel, rlm subagent dispatch, agent_message, continual harness)
- **Experiment runner:** `orx` CLI via Prime Intellect
- **Analysis:** Python (scipy.stats for paired t-tests, numpy for aggregation; no specialized ML frameworks required)
- **Visualization:** Pandas + matplotlib for result tables and plots (optional; not required for statistical report)

### Verification Steps (Concrete)

1. **Task loading:** Confirm all 12–16 held-out tasks load and have valid validation splits before experiment starts.
2. **Budget isolation:** Verify that each arm's compute usage is isolated; spot-check 2–3 runs to confirm Arm 1 uses only shared memory updates (no additional API calls) vs. Arm 2.
3. **Artifact collection:** Verify that final artifacts from each arm are persisted to artifacts/ with metadata (task ID, arm ID, attempt count, quality score).

---

## Stopping Rule (from state.md)

Stop data collection when **any** of the following holds:

1. N ≥ 24 observations collected (minimum: 12 tasks × 2 arms).
2. One arm shows consistent superiority: Paired t-test p < 0.05, effect size ≥ 2 percentage points on promotion accuracy, across ≥2 stratified problem classes.
3. Compute budget exhausted: Estimated at 4 GPU-hours/task × 16 tasks × 2 arms = 128 GPU-hours ≈ 16 wall-clock hours on available infrastructure (assuming 8× parallelism).

---

## Falsification Condition (from state.md)

The design's premise is **refuted** if:

- The flat-queue arm (Arm 2) outperforms the hypothesis-tree arm (Arm 1) by ≥3 percentage points on promotion accuracy, AND
- This difference is robust across ≥60% of held-out tasks (i.e., observed in ≥10 of 16 tasks).

If both conditions hold, conclude that flat-queue is superior; discontinue hypothesis-tree development for this workload.

---

## Expected Outcomes and Interpretations

### Scenario 1: Arm 1 (Tree + Propagation) Wins
- **Finding:** Hypothesis-tree with insight propagation beats flat queue by 2–5 percentage points on promotion accuracy.
- **Interpretation:** Organizing search as a directed tree with cross-branch learning is valuable; recommend deploying tree-based agent orchestration for held-out optimization tasks.
- **Implication for Arm 3:** If Arm 1 >> Arm 3, then propagation (via continual-learning instincts) is the active ingredient; if Arm 1 ≈ Arm 3, tree structure alone suffices.

### Scenario 2: No Significant Difference
- **Finding:** Promotion accuracy and artifact quality are statistically indistinguishable between Arm 1 and Arm 2 (p > 0.05, |Δ| < 2 pp).
- **Interpretation:** Tree structure and propagation confer no advantage within the observed budget and task distribution. Flat queue is simpler and should be preferred (parsimony).
- **Next steps:** Re-examine whether propagation delays are masking tree benefits, or whether tasks are too simple to warrant hierarchy.

### Scenario 3: Arm 2 (Flat Queue) Wins (Refutation)
- **Finding:** Flat queue outperforms tree by ≥3 percentage points on ≥60% of tasks.
- **Interpretation:** Independence and sequential attempts beat hierarchical search for this class of tasks; hypothesis-tree premise is false.
- **Conclusion:** Discontinue tree-based development; invest in flat-queue efficiency improvements.

---

## Notes on Design Justification

1. **Sampling frame justification:** Stratified by problem class to detect whether tree advantage is task-type-specific (e.g., valuable for architecture search but not hyperparameter tuning). Minimum N=24 is typical for paired t-tests with medium effect sizes (power ≥0.8 at α=0.05).

2. **Ablation scope:** Arm 3 isolates propagation from tree structure. If both matter, the full Arm 1 will win; if only structure matters, Arm 3 will match Arm 1; if propagation hurts, Arm 3 >> Arm 1.

3. **Metric choice:** Promotion accuracy (top-2 ranking) is more robust than absolute quality scores (which may saturate). Artifact quality is included for completeness and to detect ceiling/floor effects.

4. **Budget constraint:** Fixed compute budget per task reflects real-world constraints; the experiment does not ask "which is best with unlimited compute?" but "which is best with a tight budget?"

5. **Falsifier specificity:** The 3 percentage point + 60% task threshold is chosen as a conservative, meaningful margin (often the difference between "publishable improvement" and "noise").

6. **Analysis plan completeness:** Paired t-tests are standard for within-subjects designs. Stratified analysis catches task-class interactions. Ablation isolates the proposed mechanism (propagation). CIs and effect sizes provide full uncertainty picture beyond p-values alone.

---

## Deliverables

1. **state.md:** Filled with decision ID, research question, rejected alternatives, sampling frame, evidence status, falsifier, and stopping rule.
2. **design.md (this file):** Complete experimental design including main comparison, ablation, resource specifications, outcome metrics, analysis plan, and uncertainty quantification.
3. **Result artifacts** (to be produced after execution): Persisted to OpenResearch artifacts/ directory, indexed by task ID and arm ID. Summary statistics and test results to be published in a results markdown file (not part of this design phase).
