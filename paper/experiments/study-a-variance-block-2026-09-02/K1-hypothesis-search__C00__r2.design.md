# Experimental Design: Hypothesis Tree vs. Flat Queue for Autonomous Agent Optimization

## Research Question
Does organizing an autonomous agent's optimization attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

## Primary Hypothesis
A hypothesis tree structure, where insights from related attempts propagate upward and inform subsequent attempts, will achieve higher artifact optimization scores on held-out test tasks compared to a baseline flat queue, given the same compute and workspace budget.

---

## Main Comparison: Two Arms

### Arm 1: Hypothesis Tree (Treatment)
**Organization:** Attempts are structured as a directed acyclic graph (DAG) where:
- Each node represents a versioned hypothesis about the artifact and how to optimize it
- Nodes record: hypothesis statement, supporting evidence, failed assumptions, propagated insights
- Parent-to-child edges indicate refinement relationships (e.g., "simplify optimization target," "add constraint")
- Shared context and learnings from related branches propagate to inform new attempt selection
- Tree traversal uses a depth-first strategy with backtracking on plateau detection

**Backbone:** Claude (3.5 Sonnet) with access to the artifact and prior attempt history
**Budget per agent:** Fixed 100 API calls (each call includes up to 200k context window)

### Arm 2: Flat Queue (Control)
**Organization:** Attempts are stored in an ordered queue with:
- Each attempt records: input parameters, result metrics, timestamp
- No explicit structure linking attempts or propagating insights
- Next attempt selection uses random sampling or round-robin from parameter space
- History is available but not explicitly summarized or analyzed

**Backbone:** Claude (3.5 Sonnet) with access to the artifact and prior attempt history
**Budget per agent:** Fixed 100 API calls (matching treatment arm)

---

## Held-Out Tasks

Three held-out artifact optimization tasks (distinct from training/exploration):

1. **Task A (Code Optimization):** Given a Python function, optimize for latency while maintaining correctness on a fixed test suite
2. **Task B (Data Structure):** Design and optimize a data structure for memory efficiency across a workload pattern
3. **Task C (Configuration):** Tune hyperparameters of a simulation model to maximize output quality metric

Each task has:
- A ground-truth optimality frontier (computed independently)
- A held-out test suite to verify constraint satisfaction
- A quantitative score function (latency, memory, or quality metric)

---

## Ablations

### Ablation 1: Insight Propagation Disabled
**Condition:** Hypothesis tree structure without insight propagation
- Same DAG structure as Arm 1
- No explicit summaries of insights across branches
- Each node re-analyzes from scratch
- **Purpose:** Isolates the value of insight propagation from the value of structured organization

### Ablation 2: Limited Budget Scenario
**Condition:** Reduce budget to 50 API calls for both arms
- **Purpose:** Tests whether tree structure scales gracefully under resource constraints or becomes overhead

---

## Analysis Plan

### Primary Outcome
**Optimization Score Improvement:** 
- For each held-out task, compute the best achieved score across all attempts in each arm
- Express as: `(final_score - baseline) / (optimal - baseline)`
- Baseline = score of the artifact at task start (no optimization)
- Optimal = known ground truth (or best achieved across all arms if ground truth unavailable)

**Statistical Test:**
- One-tailed t-test on held-out task scores (Arm 1 vs. Arm 2)
- Null hypothesis: μ_tree ≤ μ_queue
- Alternative: μ_tree > μ_queue
- α = 0.05, power = 0.80

### Secondary Outcomes
1. **Efficiency:** Total computational cost (API calls) to reach a given score threshold
   - Measure: calls-to-80%-optimal, calls-to-90%-optimal
   - Compare arms on cost per unit improvement

2. **Convergence:** Rate of score improvement over attempt sequence
   - Fit a learning curve (e.g., power law) to each arm's trajectory
   - Compare slopes and asymptotes

3. **Constraint Satisfaction:** Fraction of final solutions meeting hard constraints
   - Count solutions passing held-out test suite
   - Measure as: (passing_solutions / total_attempts) per arm

4. **Exploration vs. Exploitation:** 
   - Measure diversity of attempted solutions (using L2 distance in parameter space)
   - Hypothesis: tree arm explores more coherently due to structured navigation

### Uncertainty Quantification
1. **Confidence Intervals (95%):** Bootstrap resampling of task-level scores
   - Resample tasks with replacement (N=1000 iterations)
   - Report CI for each arm and the difference

2. **Effect Size:** Cohen's d on normalized scores
   - Cohen's d = (μ_tree - μ_queue) / pooled_σ
   - Interpret: d ≥ 0.2 is small, d ≥ 0.5 is medium, d ≥ 0.8 is large

3. **Variability Across Tasks:** Report standard error of the mean score improvement
   - SE = σ / sqrt(n_tasks) where n_tasks = 3

---

## Concrete Resources

### Compute
- **Model:** Claude 3.5 Sonnet via Anthropic API (https://api.anthropic.com)
- **Budget:** 100 API calls × 2 arms × 3 tasks = 600 calls total
- **Cost:** ~$60 USD (at $0.003/input-K-token, $0.015/output-K-token with 200k context window)
- **Walltime:** ~4–6 hours per arm (sequential) or 2–3 hours per arm (parallel)

### Artifacts & Tasks
- **Source:** Use 3 existing programming challenges (e.g., from LeetCode hard, or HackerRank optimization problems)
- **Baseline implementations:** Commit suboptimal reference implementations (publicly available)
- **Ground truth:** Pre-computed optimal or near-optimal solutions with verified test suites

### Storage & Logging
- **Experiment tracking:** Local JSON logs (one per arm per task)
- **Schema:** `{ attempt_id, timestamp, hypothesis, action, result_score, budget_used, constraints_met }`
- **Artifact versions:** Stored in timestamped local directory structure

### Infrastructure
- **Local Python environment:** Python 3.11+, requests library, standard JSON
- **No external databases:** All state written to flat files and git-tracked
- **Reproducibility:** Full prompts, attempt histories, and results committed to version control

---

## Outcome Metrics (No Numeric Results—Design Only)

### Primary Metric
- **Held-Out Optimization Improvement (%):** Percentage of gap to optimality closed by each arm on each task

### Secondary Metrics
1. Efficiency: Calls-to-threshold (calls required to reach 80% and 90% of optimal)
2. Convergence rate: Exponent in power-law fit to learning curve
3. Constraint satisfaction: Fraction of attempts meeting hard test suite
4. Solution diversity: Average pairwise distance between attempted solutions

### Uncertainty Reporting
- 95% confidence intervals (bootstrap)
- Effect sizes (Cohen's d)
- Standard error of mean improvement across tasks

---

## Sample Size & Power Calculation
- **Arms:** 2 (tree vs. queue)
- **Ablations:** 2 (insight propagation disabled, limited budget)
- **Held-out tasks:** 3 (fixed; no sampling variation)
- **Replicates per condition:** 1 per task (deterministic arm behavior given fixed budget and random seed control)
- **Power analysis:** With N=3 tasks, effect size d ≥ 0.8, α=0.05, power ≈ 0.70 (exploratory; replication recommended)

---

## Control & Reproducibility

1. **Random seed:** Fixed seed for model sampling (temperature=0 for deterministic outputs, or fixed seed for temperature>0)
2. **API call limit:** Enforced hard limit of 100 calls per arm per task
3. **Model version:** Claude 3.5 Sonnet (API version pinned to a specific release)
4. **Baseline:** All arms start from identical artifact snapshot and test suite
5. **Isolation:** Each arm runs independently; no cross-contamination of history

---

## Reporting & Interpretation

### Null Case (No Difference)
If Arm 1 (tree) and Arm 2 (queue) show no significant difference in held-out scores:
- Conclude that structured organization does not improve optimization within the fixed budget
- Hypothesis tree adds overhead without sufficient compensating benefit
- Recommend simplifying to flat queue approach

### Alternative Case (Arm 2 Beats Arm 1)
If Arm 2 (flat queue) outperforms Arm 1:
- Conclude that flat exploration is more efficient for this task set
- Possible explanation: tree structure constrains search space unnecessarily
- Recommend investigating why propagated insight does not help

### Primary Case (Arm 1 Beats Arm 2)
If Arm 1 (tree) achieves significantly higher scores:
- Conclude that hypothesis trees with insight propagation improve artifact optimization
- Effect size interpretation: small (d ≥ 0.2), medium (d ≥ 0.5), or large (d ≥ 0.8)
- Secondary outcomes (efficiency, convergence) determine whether improvement is due to better navigation or more attempts

### Ablation Interpretation
- **Ablation 1 (no insight propagation):** If tree structure without insight performs like flat queue, propagation is the active ingredient
- **Ablation 2 (limited budget):** If tree degrades more than queue under constraint, tree has higher overhead; if tree preserves advantage, tree scales better

---

## Limitations & Future Work

1. **Small task set (N=3):** Limited generalization to other artifact types; replication on larger task set needed
2. **Deterministic backbone:** Results may not extend to stochastic models or different architectures
3. **Fixed budget:** Optimal budget and its allocation unknown; sensitivity analysis needed
4. **No human-in-the-loop:** Assumes fully autonomous optimization; interactive loops may change dynamics
5. **Single budget level:** Ablation 2 (50 calls) is exploratory; full budget scaling curve needed

