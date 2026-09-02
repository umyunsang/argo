# Experimental Design: Hypothesis Tree vs. Flat Queue for Artifact Optimization

## Research Question

Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

## Design Overview

This is a **comparative randomized controlled trial with a fixed compute budget per arm**, using held-out artifact optimization tasks to decide promotion between two organizational strategies for agent exploration.

### Core Comparison

**Hypothesis-Tree Arm (Treatment)**: Agent maintains an explicit hypothesis-evidence-belief state tree over attempts. Each node in the tree represents a distinct hypothesis about the artifact optimization problem. When an attempt yields evidence, the agent updates the belief state and uses it to prune the search space and prioritize new hypotheses. Hypothesis nodes can spawn child hypotheses or be marked terminal. Insight propagates upward in the tree (e.g., "hypothesis A and B both failed for reason X, so don't explore Y").

**Flat-Queue Arm (Control)**: Agent maintains an ordered queue of optimization attempts with no explicit hypothesis structure. Decisions about which attempt to try next are made based solely on previous outcomes (greedy or FIFO), with no propagation of abstract insight across attempts.

Both arms use the **same backbone LLM** and receive **identical compute budgets** (token limit, number of inference calls, or wall-clock time). The only difference is the internal organization of exploration state.

---

## Sampling Frame (Per Recorded State)

**Population**: Artifact optimization problems requiring iterative refinement with:
  - Clear ground-truth success metrics (e.g., test accuracy, code execution time, benchmark score)
  - Multiple solution paths (not a single obvious fix)
  - Realistic complexity (not trivial, not intractable within budget)
  - Examples: hyperparameter tuning, prompt optimization, code performance profiling, machine learning model tweaking

**Unit of Analysis**: A single held-out optimization task

**Sampling Strategy**: 
  - **Exploration set (70%)**: Tasks used to train and run both arms; compute budget is spent here. Tasks are randomly assigned to arms without replacement.
  - **Held-out evaluation set (30%)**: Held-out tasks evaluated identically by both arms to determine which arm's learned strategy generalizes better. These tasks are **not used to train either arm**.
  - The 30/70 split ensures held-out generalization is tested independently of training.

---

## Experimental Conditions

### Main Conditions

| Arm | Organization | Hypothesis Tracking | Insight Propagation | Exploration Strategy |
|-----|--------------|-------------------|---------------------|----------------------|
| A (Treatment) | Hypothesis Tree | Explicit, auditable tree structure (per 2607.09195) | Yes: parent-to-child and sibling-to-sibling pruning rules | Prioritize hypotheses with highest expected value given current beliefs |
| B (Control) | Flat Queue | None | No: each attempt treated independently | Sequential or greedy based on immediate outcome |

### Equality Constraints

- **Same backbone**: Both arms use the same LLM model (e.g., Claude 3.5 Sonnet, or other specified model).
- **Same budget**: Both arms receive T total tokens (or N inference calls, or C wall-clock hours). Budget is spent during exploration phase; held-out evaluation uses a small fixed allocation per task.
- **Same artifact domain**: Both arms tackle the same population of optimization tasks.
- **Deterministic seed control**: Randomness seeded identically at the start of each task to ensure independent draws, not correlated noise.

---

## Ablation Experiments

### Ablation 1: Hypothesis Tree vs. Naive Tree (No Propagation)

**Purpose**: Test whether the insight-propagation mechanism (parent-to-child pruning, sibling comparison) is the driver of any observed gain, or whether simply organizing attempts hierarchically is sufficient.

**Condition**: Hypothesis-Tree-No-Propagation arm. Same explicit tree structure as the Treatment arm, but pruning rules are **disabled**: each node is explored independently, and no insight from one branch affects sibling selection.

**Expected outcome**: If propagation is the mechanism, this ablation should perform worse than the full hypothesis-tree arm but possibly better than flat-queue (if hierarchy alone provides some benefit). If this ablation matches the treatment arm, hierarchy without propagation drives the effect.

### Ablation 2: Compute Redistribution (Constant Budget, Varied Allocation)

**Purpose**: Test whether the tree arm's gains come from better **allocation of compute to high-value attempts**, rather than from the tree structure itself.

**Condition**: Within a fixed total budget, randomly allocate more compute to attempts that happen to be high-reward (oracle allocation, or simulated via post-hoc analysis). Compare against equal allocation.

**Expected outcome**: If the tree arm's gain matches oracle allocation, the mechanism is compute efficiency, not insight propagation. If the tree arm outperforms oracle allocation, tree-based insight adds value beyond greedy compute allocation.

---

## Outcome Metrics

### Primary Metric: Held-Out Task Performance (Task-Level)

For each held-out task $t$, both arms are given a small evaluation budget and run to completion (or budget exhaustion). Outcome is the **final artifact quality** at the end of the run, measured by the ground-truth success metric for that task (e.g., accuracy, latency percentile, test pass rate).

**Metric**: $	ext{Performance}_{arm,t} = f_t(	ext{final artifact})$ where $f_t$ is the task-specific scoring function.

**Comparison**: Paired t-test on held-out tasks: $H_0: E[P_{	ext{tree},t} - P_{	ext{queue},t}] = 0$ vs. $H_1: E[P_{	ext{tree},t} - P_{	ext{queue},t}] 
eq 0$.

### Secondary Metrics: Trajectory-Level Analysis (Per 2609.00038)

For each task, record the **full trajectory** of the agent's attempts (hypothesis generated, tests run, evidence observed). Evaluate trajectories using a **step-level rubric** (not outcome-only):

1. **Retrieval-Utilization Decomposition** (per 2608.01913): For each attempt, mark whether:
   - The agent successfully retrieved relevant information / generated relevant hypothesis
   - The agent correctly used that information in the next attempt
   - Decompose failures into retrieval gaps (hypothesis was unhelpful) vs. utilization gaps (good hypothesis was not acted on)

2. **Redundancy Score**: Measure the fraction of attempts that cover hypothesis space already explored (lower is better; tree arm should have lower redundancy due to pruning).

3. **Belief Update Quality**: For the tree arm, audit whether each belief update is justified by evidence (per 2607.09195 auditable-protocol standard). For the queue arm, quantify how often the agent makes decisions despite contradictory evidence.

### Tertiary Metrics: Compute Efficiency

1. **Tokens per performance unit**: $rac{	ext{Total tokens spent}}{	ext{Final artifact quality}}$ (lower is better; measures efficiency).
2. **Wall-clock time to convergence**: Time to reach 80% of final performance (tree arm should reach convergence faster if insight propagates).
3. **Hypothesis reuse rate**: For the tree arm, fraction of nodes whose descendants inherit and refine the parent hypothesis (should be >50% for tree to be effective).

---

## Evaluation Protocol (Trajectory-Level Rubric)

Per 2609.00038, outcome-only evaluation misses silent failures. Evaluation uses a **hybrid rubric**:

1. **Final outcome score** (40% weight): Quality of final artifact per ground-truth metric.
2. **Trajectory audit score** (60% weight): Step-level rubric evaluated by human reviewers (blinded to arm assignment):
   - Logical coherence of hypothesis → test → update cycle (per 2607.09195)
   - Correct parsing and utilization of evidence (per 2608.01913)
   - Absence of contradictory or cyclic reasoning
   - For tree arm specifically: explicit hypothesis marking, pruning decisions auditable

Score is normalized to 0–100 per task. Final metric is the mean trajectory score across held-out tasks, with outcome score as tiebreaker.

---

## Statistical Analysis Plan

### Primary Analysis: Paired Hypothesis Test

Data: Paired measurements $(P_{	ext{tree},t}, P_{	ext{queue},t})$ for each held-out task $t \in \{1, \ldots, n_{	ext{held-out}}\}$.

Test: Two-tailed paired t-test at $lpha = 0.05$.

Hypothesis: $H_0: \mu_D = 0$ (no difference in mean performance) vs. $H_1: \mu_D 
eq 0$ (tree arm differs from queue).

Test statistic: $t = rac{ar{D}}{s_D / \sqrt{n}}$ where $ar{D}$ is mean difference, $s_D$ is sample SD of differences, $n$ is number of tasks.

**Justification**: Per 2605.30315, paired designs are more powerful than unpaired when within-task correlation is high (which it is: the same backbone and problem structure are shared). This design avoids the 2× underestimation of sample size that occurs in unpaired Cohen-h calculations.

### Secondary Analysis: Effect Size and Confidence Interval

Report 95% confidence interval on the mean difference $\mu_D$ and standardized effect size (Cohen's $d$).

Per 2010.06595, most NLP experiments are underpowered. We pre-register a **minimum detectable effect (MDE)** before data collection:

- **MDE Definition**: A practical difference of $\Delta = 0.05$ on the final performance metric (e.g., 5 percentage points on accuracy, or equivalent on other metrics).
- **Justification**: What counts as "beats" in artifact optimization? Without a prior, we assume a 5% gain is material and practically significant. Justify or update this threshold based on domain feedback before launch.

### Sample Size Calculation

Per 2605.30315, the correct sample size for paired designs under the true paired test is:

$$N^* = 2 \left( rac{z_{lpha/2} + z_eta}{\Delta / \sigma} 
ight)^2 (1 - 
ho)$$

where:
- $z_{lpha/2} = 1.96$ (α = 0.05, two-tailed)
- $z_eta = 0.84$ (power = 1 − β = 0.80)
- $\Delta = 0.05$ (MDE)
- $\sigma$ = assumed standard deviation of performance metric on held-out tasks (to be estimated from domain literature or pilot)
- $
ho$ = within-task correlation (tree arm applied to same task should be highly correlated; assume $
ho = 0.7$ conservatively)

**Calculation**: Assuming $\sigma = 0.10$ (reasonably variable task performance):
$$N^* = 2 \left( rac{1.96 + 0.84}{0.05 / 0.10} 
ight)^2 (1 - 0.7) = 2 \left( rac{2.80}{0.5} 
ight)^2 (0.3) pprox 2 	imes 31.36 	imes 0.3 pprox 19 	ext{ tasks}$$

**Decision rule**: Use $n_{	ext{held-out}} = 20$ held-out tasks minimum to achieve 80% power. If actual $\sigma$ from pilot is larger, increase sample size proportionally.

### Addressing Multiplicity

We pre-register one primary test (paired t-test on held-out performance) and four secondary tests (trajectory metrics). Control family-wise error at α = 0.05 using:
- **Bonferroni correction** if exploratory (divide α by 5), OR
- **Pre-register only the primary test as confirmatory**, treat secondaries as descriptive.

Recommend the latter: report secondaries for insight, but reserve judgment until primary test concludes.

---

## Concrete Resources

### Backbone Model

**Specification**: Claude 3.5 Sonnet (or equivalent LLM to be specified). Must be the same model instance for both arms. If model is updated during the study, both arms receive the update simultaneously.

**Justification**: A fixed backbone ensures the only difference between arms is the exploration strategy, not model capability.

### Compute Budget

**Per-arm allocation**:
- **Exploration phase**: 50,000 tokens per arm per task in the 70% exploration set (70% of all tasks). Total exploration budget = 50,000 × (0.7 × total task count).
- **Held-out evaluation phase**: 10,000 tokens per arm per held-out task (fixed, not part of training budget).

**Rationale**: 50,000 tokens per task allows ~8–12 iterative refinement attempts (depending on task complexity) for both arms, enough to test insight propagation without infinite loops. Held-out budget is small and equal to ensure held-out scores are comparable.

**Budget enforcement**: Implement hard token limit per task; truncate trajectories that exceed budget and report as "incomplete."

### Artifact Optimization Task Pool

**Source**: Composite pool from existing benchmarks plus custom tasks:
  1. **HumanEval** (code completion / optimization): 50% of tasks. Metric: pass@1 on hidden test cases.
  2. **Hyperparameter tuning** (e.g., simple neural network on a standard dataset, or random-forest on UCI dataset): 30% of tasks. Metric: validation accuracy.
  3. **Prompt optimization** (e.g., optimize a prompt to improve LLM performance on a classification task): 20% of tasks. Metric: accuracy on held-out test set.

**Stratification**: Randomly split each sub-pool 70/30 (exploration/held-out) to ensure balanced coverage of all domains in held-out set.

**Example task format**:
```
Problem: Optimize the following Python function to reduce latency on benchmark X while maintaining correctness on test suite Y.
Initial artifact: [code]
Success metric: [latency threshold and test pass rate]
Exploration budget: 50,000 tokens
```

### Human Evaluation Infrastructure

**Step-level rubric evaluation** (per 2609.00038):
  - Two independent human raters per trajectory (inter-rater agreement measured with Krippendorff's α).
  - Raters are blinded to arm assignment.
  - Rubric items (5-point Likert scale):
    1. Hypothesis clarity (tree arm: Is the hypothesis well-articulated? Queue arm: Are decisions explicit?)
    2. Evidence use (Does the agent correctly parse and utilize evidence?)
    3. Logical coherence (Are updates consistent with prior beliefs?)
    4. Efficiency (Does the strategy avoid obvious redundancy?)
  - Rubric scores aggregated per task as the mean across raters and items.

### Logging and Reproducibility

**Mandatory logs**:
  - Full conversation / trajectory for each attempt (LLM input, output, intermediate steps).
  - Timestamp and token count for each LLM call.
  - For tree arm: explicit hypothesis tree structure (serialized as JSON) at each step.
  - For queue arm: queue state (ordered list of attempted optimizations) at each step.
  - Final artifact and ground-truth metric score.

**Reproducibility**: Seed all randomness (model temperature, sampling order, initial queue shuffling) with a task-specific seed. Enable deterministic reruns of any task's trajectory.

---

## Ablation Implementation

### Ablation 1: Hypothesis-Tree-No-Propagation

**Modification**: Same tree structure and hypothesis generation as the treatment arm, but:
  - Remove all pruning rules: each node is explored fully, siblings are not compared, parent failures do not prune children.
  - Exploration order is still hierarchical (breadth-first or depth-first through tree), but decisions do not account for prior evidence.

**Run**: Execute on a stratified subsample of exploration tasks (e.g., 25% of exploration set). Pair this arm against the flat-queue arm on the same task subset.

**Analysis**: Report effect size of (Tree-No-Propagation − Queue) and compare to (Tree-Full − Queue). If the two effects are equal, the propagation mechanism is inert. If Tree-Full >> Tree-No-Propagation, propagation is the mechanism.

### Ablation 2: Compute Redistribution (Oracle Allocation)

**Design**: Conduct a post-hoc, simulated analysis on completed exploration runs:
  1. For each task in the exploration set, identify which attempts were highest-reward (oracle knowledge).
  2. Re-simulate the flat-queue arm, but allocate 2× tokens to the top-quartile reward attempts (keeping total budget constant).
  3. Compare oracle-allocated queue against the original flat-queue arm on held-out tasks.

**Rationale**: If tree arm's advantage is purely from allocating more compute to better attempts, then oracle allocation (offline) should match the tree arm's online advantage. If tree arm outperforms oracle allocation, it discovers novel structure beyond greedy compute allocation.

**Limitation**: This is post-hoc and not a new experimental arm, so it cannot be pre-powered. Treat as exploratory.

---

## Explicit Hypothesis-Tree Structure (Per 2607.09195)

The treatment arm operates under the Hypothesis Evolution Protocol (HEP) framework:

1. **Hypothesis Generation**: At each step, agent generates a written hypothesis about what aspect of the artifact should be optimized and why (e.g., "The bottleneck is the inner loop; I hypothesize that vectorizing it will reduce latency by >20%.").

2. **Test Design**: Agent proposes a specific test of this hypothesis (e.g., "Run the original and vectorized versions on benchmark X and compare latency.").

3. **Evidence Collection**: Agent runs the test and records the outcome (pass/fail, effect size).

4. **Belief Update**: Agent updates its tree state: mark the hypothesis as confirmed, refuted, or inconclusive. If confirmed, mark child hypotheses as higher-priority. If refuted, mark siblings as lower-priority.

5. **Transparency**: The entire hypothesis-evidence-belief cycle is logged in a serialized tree structure (JSON), enabling audit trails per 2607.09195.

**Comparison**: The control arm does not maintain explicit hypotheses; it simply records attempted changes and outcomes, and greedily selects the next attempt based on immediate reward.

---

## Falsification Criteria

Per recorded state, the design is falsified if:

1. **Primary null result**: Paired t-test fails to reject $H_0$ at α = 0.05 on the held-out evaluation set (i.e., no significant difference in final performance).

2. **Effect size below MDE**: Observed effect size (Cohen's $d$) is less than the pre-registered MDE (0.05 on the performance metric), or confidence interval includes zero.

3. **Underpowered study**: If compute budget exhausted before reaching target sample size, and the obtained sample size is insufficient for 80% power, study is flagged as inconclusive rather than negative.

---

## Stopping Rules (Per Recorded State)

**Primary stopping rule**: Stop exploration and move to held-out evaluation when:
  - All 70% exploration-set tasks have been completed by both arms (compute budget fully allocated), AND
  - At least $n_{	ext{held-out}} = 20$ held-out tasks have been evaluated.

**Secondary stopping rule (Early Futility)**: If after 50% of held-out tasks have been evaluated, a interim analysis shows:
  - The observed mean difference is opposite in sign to the hypothesized direction (tree arm worse than queue), or
  - The 95% confidence interval for the true effect excludes the pre-registered MDE,
  then **stop for futility** and report negative result.

**Tertiary stopping rule (Early Efficacy)**: If after 50% of held-out tasks, the one-sided p-value for the pre-registered direction (tree beats queue) is < 0.01, consider stopping for efficacy (optional early success), but require pre-approval to avoid α-inflation.

---

## Summary: Key Claims and Justifications

| Claim | Evidence | Verification |
|-------|----------|--------------|
| Explicit hypothesis tracking improves optimization | 2607.09195 (HEP agents generalize across tasks) | Trajectory-level audit score; hypothesis tree structure logged |
| Paired design is appropriate | 2605.30315 (paired designs more powerful than unpaired) | Same backbone and problem structure → high correlation; justifies reduced sample size |
| Outcome-only evaluation is insufficient | 2609.00038 (45% of silent failures missed by outcome-only judges) | Implement trajectory-level rubric in evaluation; report inter-rater agreement |
| Proposed sample size is realistic | 2010.06595 (most NLP experiments underpowered) | Pre-register MDE and power target; report achieved power in final analysis |
| Hypothesis-tree structure is auditable | 2607.09195 (HEP provides explicit, auditable cycles) | Serialize tree to JSON; enable independent audit of belief-update logic |

---

## Limitations and Assumptions

1. **Unverified assumption**: Propagated insight actually reduces redundant exploration under realistic budgets. Tree structure may impose overhead (articulating hypotheses takes tokens) that negates gains. Ablation 1 and trajectory-level metrics test this.

2. **Population scope**: Design is tested on artifact optimization tasks (code, hyperparameters, prompts). Generalization to other agent-search domains (e.g., theorem proving, molecular design) is unknown.

3. **Backbone specificity**: Results are specific to the chosen LLM backbone. Different models may have different capacity to maintain hypothesis trees.

4. **Compute budget fixation**: Both arms receive fixed budgets, but tree arm might make use of budget qualitatively differently (e.g., longer trajectories, fewer deep dives). Observed differences might reflect budget misalignment rather than strategy superiority.

---

## Reproducibility Artifacts

- **Task pool**: Release 20 held-out evaluation tasks with ground-truth metric implementations.
- **Backbone specification**: Pinned model version and inference configuration (temperature, top-p, max_tokens).
- **Trajectory logs**: Full conversation transcripts for all N=20 held-out tasks for both arms.
- **Statistical analysis code**: R or Python script implementing paired t-test, confidence interval, and MDE calculation. Source code is version-controlled and reproducible.
- **Human rubric**: Full rubric used for trajectory evaluation, inter-rater agreement scores, and individual rater judgments.

---

## Conclusion

This design tests the hypothesis that organizing an agent's artifact-optimization attempts as an explicit hypothesis tree with propagated insight outperforms a flat queue on held-out tasks. The core comparison is powered for an MDE of 0.05 on the performance metric, uses paired statistics to account for high within-task correlation, and employs trajectory-level evaluation (per 2609.00038) to detect silent failures and validate the mechanism. Two ablations test whether hierarchy alone or compute redistribution account for any observed gains. The sampling frame is explicit: optimization tasks sampled from the intersection of HumanEval, hyperparameter tuning, and prompt optimization. Results are falsifiable and stopping rules are pre-registered to avoid α-inflation.
