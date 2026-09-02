# Experimental Design: K4-Benchmark Stopping Rule

## Objective

To design and validate a stopping rule that prevents optimizing agents from gaming benchmark scores through unlimited evaluation calls, while preserving an agent's ability to leverage evaluations for genuine algorithmic improvement.

## Core Research Question

Given that an optimizing agent can call a target evaluation function repeatedly, how should a benchmark distinguish genuine algorithmic improvement from score inflation via exhaustive search? (Grounded in state.md, decision_id: K4-benchmark-stopping-rule)

**Sampling Frame (from state.md)**: A fixed benchmark of N evaluation problems, each with a known ground-truth optimal value. The population consists of (problem, agent run) pairs where each agent is assigned a problem and given a call budget B. The unit of analysis is a single run, and we test whether the agent's best solution plateaus (evidence saturation) before exhausting its budget.

---

## 1. Sampling Frame

**Population and Unit**: A fixed benchmark corpus of N=50 to 100 evaluation problems, sampled from optimization or decision-making domains (e.g., combinatorial optimization, hyperparameter search, constraint satisfaction, or information-retrieval ranking). Each problem has a ground-truth optimal value or a held-out validation-set rank. The unit of analysis is a single run (agent, problem) pair.

**Run Structure**: Each agent run is assigned a problem and given a call budget B=200 evaluation calls. The agent produces a trajectory consisting of:
- A sequence of K ≤ B evaluation calls c₁, c₂, ..., cₖ, each returning a scalar solution value or rank
- A terminal best-solution claim s_best = argmax_i value(cᵢ)
- (Optional) an agent reasoning trace τ that shows the agent's stated hypothesis, refinements, and stopping decision

**Sampling Rationale**: The frame units are (agent, problem) pairs because we measure whether the agent saturates *per problem*. A single agent may saturate on some problems and continue optimizing on others; the stopping rule must account for problem-level variation in signal and noise.

---

## 2. Main Comparison: Stopping Rule vs. No Stopping Rule

### Condition A: With Stopping Rule (Saturation-Based Stopping)

**Stopping Criterion**: For each run, after every call k ≥ K_min (K_min = 5), measure the marginal improvement:

```
improvement_margin(k) = max(value(c_{k-K+1}), ..., value(c_k)) - best_value_before(k - K)
```

If improvement_margin(k) < θ for three consecutive check points (k, k+5, k+10), or if k ≥ K_min and the agent has not returned a new best solution in the last K_min calls, declare the run **saturated**. Stop the trajectory at call k and record:
- Calls made: k
- Best solution: s_best
- Saturation step: k

**Noise Threshold θ**: Set θ adaptively per problem using pre-computed statistics from a warmup phase (see Analysis Plan). For synthetic problems, θ = 0.01 × (problem_max - problem_min). For ranking problems, θ = 1 rank position (i.e., no improvement in top-K).

**Rationale**: Grounded in 2608.01913 (Liu et al.), which shows that agents over-search (wasted tail) and that evidence saturation occurs well before call budgets are exhausted. The K_min=5 window is set per 2607.13304 (Zatuchin), which found that the marginal information gain from resampling drops sharply after 5 repeats.

### Condition B: No Stopping Rule (Baseline)

**Stopping Criterion**: Each agent runs its full call budget B=200 regardless of improvement. No saturation check. Runs always terminate at call 200 or when the agent halts voluntarily.

**Rationale**: This is the current default behavior, allowing agents to game via exhaustive search.

### Primary Outcome: Agent Ranking Stability

For each condition (A and B), rank the agents by their best solution values on the problem set, aggregated over problems. Report the ranking and the pairwise effect sizes (using 2605.30315 methodology: resolution ratio q = N/N*, paired McNemar power for binary accuracy, or paired-t for continuous scores).

**Hypothesis**: Under Condition A, the ranking of agents (sorted by best solution found) will be more stable and more efficient (i.e., will achieve statistical resolution with fewer problems in the benchmark) than under Condition B. Under Condition B, two agents with different algorithmic quality may be indistinguishable because the weaker one can exhaust the budget to find solutions by chance.

---

## 3. Ablation Studies

### Ablation 1: Saturation Threshold Sensitivity

**Motivation**: The threshold θ is the key control parameter. Does the ranking depend heavily on θ, or is it robust?

**Design**: Run Condition A with three values of θ:
- θ_conservative = 0.001 × problem_range (stop very early, assume problems are nearly noiseless)
- θ_moderate = 0.01 × problem_range (base case)
- θ_aggressive = 0.05 × problem_range (stop late, assume problems are very noisy)

**Analysis**: Compare the agent rankings produced under each θ. If rankings are stable (Spearman ρ > 0.90 across thresholds), conclude that the rule is robust. If rankings change dramatically, the rule is sensitive to θ and requires better prior estimation of problem noise.

**Evidence Grounding**: 2605.30315 emphasizes that resolution depends on design; this ablation measures sensitivity of the stopping rule to its one free parameter.

### Ablation 2: Trajectory-Level Inspection vs. Outcome-Only

**Motivation**: 2609.00038 (Mohammadi) shows that outcome-only evaluation misses process-level faults. Can an agent appear to satisfy Condition A (saturation) while actually violating a constraint or resampling inefficiently?

**Design**: 
- For a subset of M=10 benchmark problems, manually inspect all trajectories and classify each run as:
  - Efficient: Agent makes diverse solution attempts, each call explores new space
  - Redundant: Agent makes near-duplicate calls (resampling the same solution)
  - Constraint-violating: Agent finds good final solutions but violates problem constraints during intermediate steps (per 2609.00038)

- Run a rubric judge (a programmatic rule checker) on each trajectory to flag violations. Record the number of violations caught by the judge.

- Compare: Does the stopping rule in Condition A correlate with efficient search (fewer redundant calls, no constraint violations)? Or does it permit redundant agents to appear to satisfy the rule?

**Analysis**: Report the proportion of saturated runs that are either redundant or constraint-violating. If > 20% of saturated runs are problematic by the rubric, the stopping rule needs refinement to inspect the trajectory, not just the outcome.

**Evidence Grounding**: Extends 2609.00038's trajectory-judge framework; shows whether outcome-based stopping is blind to process faults.

### Ablation 3: Fixed Budget vs. Adaptive Budget

**Motivation**: Instead of a fixed budget B=200 for all agents, what if we allocate budget adaptively based on problem difficulty or agent performance?

**Design**: Set B(problem) = min(200, 50 + 10 × problem_difficulty), where problem_difficulty is estimated as the variance of optimal solution values across a random sample of 10 baseline agents. Harder problems get more budget.

**Analysis**: Under this adaptive Condition A, do agent rankings remain stable? Does adaptive allocation reduce the variance of best-solution values across problems? Report effect size vs. fixed budget.

**Evidence Grounding**: 2607.13304 uses decision-study allocation to optimize sample efficiency; this ablation tests adaptive allocation in the agent-benchmarking domain.

---

## 4. Analysis Plan

### Phase 1: Preprocessing and Noise Estimation (Per-Problem)

For each problem in the benchmark:
1. Run 5 baseline agents (e.g., random search, grid search, simple greedy) up to B=200 calls each.
2. Estimate problem-level noise as: σ_problem = std(best_value_at_call_100) across the 5 baselines.
3. Derive problem-specific θ = max(σ_problem, 0.01 × problem_range), ensuring a minimum signal-to-noise ratio.

**Deliverable**: A per-problem noise profile table (problem_id, σ_problem, θ).

### Phase 2: Main Comparison Analysis

1. Run N_agents ≥ 6 optimization agents on the N=50 benchmark problems.
   - N_agents candidates: evolutionary algorithm, simulated annealing, Bayesian optimization, random search with restarts, learning-based agent (e.g., a small transformer trained on similar problems), and one oracle baseline (exhaustive search up to small scale for verification).

2. Collect trajectories under Condition A (with stopping rule) and Condition B (full budget) for all agents and problems, yielding N_agents × N = 300–600 runs.

3. **Primary outcome metric: Agent ranking**. For each condition, aggregate best solutions across problems and rank agents. Compute Spearman rank correlation ρ(ranking_A, ranking_B).

4. **Secondary metrics**:
   - Call efficiency: mean calls until saturation (Condition A) vs. mean calls to reach same-quality solution (Condition B). Report ratio: calls_B / calls_A. If Condition A saves 30%+ of calls on average, conclude it is efficient.
   - Ranking resolution (2605.30315): For the top 3 pairwise comparisons (e.g., Agent1 vs Agent2), compute resolution ratio q and required sample sizes N*. Report whether the benchmark has adequate resolution to distinguish the top agents under each condition.

### Phase 3: Ablation Analyses

**Ablation 1 (Threshold Sensitivity)**:
- Run agents under Condition A with θ_conservative, θ_moderate, θ_aggressive.
- Compute pairwise Spearman ρ among the three rankings. Report ρ.

**Ablation 2 (Trajectory Inspection)**:
- Manually label M=10 representative problems.
- Tabulate (# efficient runs, # redundant runs, # constraint-violating runs) for saturated vs. unsaturated runs.
- Report: among runs flagged as saturated, % that pass trajectory rubric.

**Ablation 3 (Adaptive Budget)**:
- Re-run Condition A with B(problem) adaptive allocation.
- Compute ranking ρ vs. fixed-budget Condition A.
- Compute within-problem variance of best solution values (should decrease under adaptive allocation).
- Report effect size and 95% CI.

### Phase 4: Uncertainty Quantification and Robustness

1. **Bootstrap stratified by problem**: Resample the problem set (sample with replacement, stratified by problem difficulty tertile) 100 times. Re-compute the agent ranking under Condition A for each resample. Report:
   - 95% confidence interval on pairwise effect sizes (resolution ratio q for each adjacent pair)
   - Median rank ± quartile deviation for each agent
   - Probability that an agent's rank changes by > 1 position across resamples (if < 5%, ranking is stable)

2. **Temporal stability**: As a further robustness check, if agents are re-run, measure whether the ranking under Condition A is identical or highly correlated (ρ > 0.95) to the first run. (This is a one-time check, not part of the main analysis.)

---

## 5. Concrete Resources and Measurement Apparatus

### Benchmark Corpus
- **Source**: Combinatorial optimization track from the Black-Box Optimization Benchmarking (BBOB) suite, or a custom suite of 50–100 hyperparameter optimization tasks (from OpenML or a private collection of tuning problems). Each problem is specified by:
  - A scalar objective function f: R^d → R
  - Domain bounds
  - Ground-truth global optimum value (or top-10 held-out validation ranking)
  - Evaluation cost (to ensure feasibility of B=200 calls per run)
  
- **Identifiability**: BBOB problems are standardized and reproducible; OpenML tasks are tracked by task ID. Custom tasks will be versioned and released with reproducibility metadata.

### Agent Implementations
- **Evolutionary Algorithm**: Use the DEAP library (deap 1.4.x) with standard DE or GA settings (mutation=0.7, pop_size=20)
- **Simulated Annealing**: scipy.optimize.dual_annealing with 1000 initial points
- **Bayesian Optimization**: scikit-optimize (skopt) with GaussianProcessRegressor
- **Random Search with Restarts**: Baseline uniformly sampling from domain and re-starting every 10 calls
- **Learning-based Agent**: A small Transformer (4-layer, 64 hidden, trained on 10K synthetic optimization trajectories) that predicts the next solution from recent history
- **Exhaustive Baseline** (verification only, not ranked): For problems with d ≤ 4, exhaustive grid search to ground truth

All agents are deterministic or seeded for reproducibility.

### Evaluation Harness
- **Stopping-rule implementation**: A Python class `SaturationStopper(K_min=5, theta_adaptive=True)` that tracks value(c_t) and implements the saturation check.
- **Trajectory logging**: Every call (step, solution, value, agent_thought) is logged to a JSON file per run.
- **Rubric judge**: A programmatic rule checker (Appendix) that validates constraint satisfaction and flags redundancy (e.g., calls with identical or near-identical arguments).

### Computational Constraints
- Total evaluations: 6 agents × 50 problems × 200 calls × 2 conditions (A + B) = 120,000 objective evaluations.
- For lightweight benchmarks (synthetic objectives), this is < 1 hour on a single CPU.
- For expensive benchmarks (e.g., hyperparameter tuning), 120,000 calls would require parallelization. We recommend BBOB or synthetic tasks for the primary experiment to ensure feasibility.

---

## 6. Outcome Metrics and Success Criteria

### Primary Metrics
1. **Agent Ranking Stability**: Spearman ρ between ranking under Condition A and Condition B. If ρ > 0.85, the stopping rule does not systematically distort agent rankings. If ρ < 0.7, the stopping rule eliminates agents that were only strong due to exhaustive search.

2. **Resolution Ratio (2605.30315)**: For pairwise comparisons of top agents, compute q = N/N* where N* is the sample size needed to resolve the gap at power 0.8. Report q for at least 3 adjacent pairs (top 1 vs 2, top 2 vs 3, top 3 vs 4). If q ≥ 1 for all reported pairs under Condition A, the benchmark is adequately powered to distinguish agents.

3. **Call Efficiency**: Ratio calls_B / calls_A (mean calls in Condition B divided by mean calls in Condition A). Success criterion: calls_B / calls_A ≥ 1.2 (i.e., Condition A uses ≥ 20% fewer calls on average while maintaining ranking fidelity).

### Secondary Metrics
4. **Trajectory Cleanliness** (Ablation 2): Proportion of saturated runs that pass the constraint and redundancy rubric. Success criterion: ≥ 80% of saturated runs are trajectory-valid (non-redundant, constraint-satisfying).

5. **Threshold Robustness** (Ablation 1): Spearman ρ among rankings under θ_conservative, θ_moderate, θ_aggressive. Success criterion: ρ > 0.90 across all pairs (ranking is insensitive to θ).

6. **Bootstrap Confidence Intervals** (Phase 4): For each agent's median rank, report 95% CI. If CI width < 2 rank positions, the ranking is stable across problem resamples.

---

## 7. Falsification and Boundary Conditions

### Explicit Falsifiers (from state.md, restated here)

The design will be falsified if:

1. **Spurious Plateau**: An agent's trajectory under Condition A appears saturated at call k_sat, but when scored on a held-out independent test set, the agent continues to improve systematically beyond k_sat. 
   - Mitigation: Reserve a small held-out test set (5 problems) for post-hoc validation. Re-score all terminal solutions on the held-out set. If held-out ranking differs from in-distribution ranking by > 1 position for > 20% of agents, the saturation threshold is too loose.

2. **Indistinguishability from Noise**: An agent's best-solution trajectory exhibits chaotic oscillation (no plateau) for call counts well below the budget B. The stopping rule fails to trigger, because improvement_margin(k) alternates above and below θ randomly.
   - Mitigation: Inspect the per-problem improvement curves in Phase 1 preprocessing. If > 30% of problems show non-monotonic noise without a plateau signal, flag the problem as unsuitable for saturation-based stopping and exclude it from the benchmark (or increase θ for that problem).

### Boundary Cases

- **Trivially easy problems** (agent finds optimum in first 5 calls): Saturation rule triggers immediately. Agents will all saturate at k ≈ 5. Effect: Condition A and B are indistinguishable for easy problems. Mitigation: Ensure the benchmark includes a mix of difficulty levels (BBOB does this by design).
  
- **Highly noisy problems** (σ_problem very large): Threshold θ may become large, and saturation rule may never trigger (improvement always exceeds θ). Agents run to full budget B=200. Mitigation: Set a hard upper bound B_max = 200 and accept that for extremely noisy problems, the saturation rule cannot help. Report these cases separately.

---

## 8. Design Justification and Evidence Grounding

### Why Saturation-Based Stopping?

**From 2608.01913 (Liu et al., Diagnosing Search Behavior)**:
- Finding: "Answer accuracy is better correlated with the quality of retrieved evidence, especially cumulative retrieval recall, than with the number of searches or the amount of context consumed."
- Finding: "Useful evidence often appears early in the trajectory, yet agents tend to continue searching, producing a long tail of low-yield retrieval steps."
- Implication: Stopping when marginal improvement ceases (saturation) aligns with the observation that agents over-search after evidence is exhausted.

**From 2605.30315 (Kotawala, Resolution Diagnostics)**:
- Finding: Paired-test resolution depends on effect size and sample correlation, not on raw sample size alone.
- Finding: Minimum detectable effect (MDE) = (z_α + z_β) σ / √N.
- Implication: For a single agent on a single problem, the signal-to-noise ratio (σ) determines the minimum improvement necessary to claim progress. Our θ is set to match σ.

**From 2607.13304 (Zatuchin, Variance Components)**:
- Finding: "A repeat past the fifth reduces relative-error variance by about 0.0003" (marginal gain collapses after K=5).
- Implication: K_min = 5 is evidence-based; beyond 5 resamples, marginal information gain is negligible.

### Why Trajectory Inspection (Ablation 2)?

**From 2609.00038 (Mohammadi, trajectory-judge)**:
- Finding: "Outcome-only judge catches 84% of loud faults but 45% of silent ones."
- Finding: Outcome-only evaluation is "structurally blind to an agent that reaches the right answer the wrong way."
- Implication: Inspecting the trajectory (not just the final score) is necessary to detect whether an agent is genuinely optimizing or gambling/violating constraints. Our Ablation 2 applies this principle.

### Why Adaptive Noise Threshold?

**From 2607.13304 (Zatuchin, Variance Components)**:
- Problem-specific noise must be estimated to set θ appropriately. No single θ works for all problems.

---

## 9. Reporting Plan

### Main Experiment Report
- Agent rankings (Condition A and Condition B), with pairwise resolution ratios.
- Call efficiency plot: (Agent, Condition A calls, Condition B calls, ratio).
- Heatmap: (Agent × Problem) with best-solution values, highlighting saturated runs.

### Ablation Report
- **Ablation 1**: Ranking stability under threshold variation (ρ table).
- **Ablation 2**: Trajectory-cleanliness cross-tab (saturated vs. unsaturated runs × efficient vs. redundant).
- **Ablation 3**: Ranking correlation and within-problem variance under adaptive budget.

### Uncertainty Report
- Bootstrap 95% confidence intervals on agent ranks.
- Resolution ratio q with 95% CI for top 3 pairwise comparisons.
- Probability of rank change across resamples.

---

## 10. Summary: Main Comparison and Conditions

| Aspect | Condition A (Stopping Rule) | Condition B (Baseline) |
|--------|---------------------------|----------------------|
| Call Limit | Up to 200; stop if marginal improvement < θ for K=5 consecutive checks | Fixed 200 calls |
| Stopping Decision | Automatic, based on saturation signal | None; runs to full budget |
| Ranking | (Primary outcome) | (Comparison baseline) |
| Hypothesis | Ranking stable + efficient | Ranking inflated by search exhaustion |
| Evidence | 2608.01913, 2607.13304 | Current default |

---

## 11. Sampling Frame Reference

As recorded in state.md:
> "A fixed benchmark of N evaluation problems, each with a known ground-truth optimal value (or a held-out test-set rank). The frame is the population of (problem, agent run) pairs where an agent is assigned a problem and given a resource budget B (measured in evaluation function calls). Each run produces a trajectory of evaluation calls and a final claimed solution. The unit of analysis is a single run on a single problem."

This design operationalizes that frame through the BBOB + 6-agent × 50-problem structure, with 200-call budget and per-problem noise estimation.

---

## References to Evidence Files

- **2608.01913.txt**: Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents (Liu et al.). Motivates saturation-based stopping and trajectory inspection.
- **2605.30315.txt**: Resolution Diagnostics for Paired LLM Evaluation (Kotawala). Provides paired-test framework and MDE estimation; used for resolution analysis and threshold setting.
- **2607.13304.txt**: Variance-Components Decomposition (Zatuchin). Justifies K_min=5 for marginal-gain checking; motivates adaptive noise estimation per problem.
- **2609.00038.txt**: trajectory-judge: What Outcome-Only LLM Judges Miss (Mohammadi). Supports trajectory-level inspection as Ablation 2; informs rubric-judge design.
- **2608.03501.txt**: Can LLM Design High-Quality Experiments (Liu et al., SCOPE). Motivates inclusion of ablation experiments and multi-stage analysis.
