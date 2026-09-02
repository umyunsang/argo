# Experimental Design: K4 Optimizer Budget Constraint

## 1. Research Question

How should a benchmark bound an optimizing agent's evaluation budget for the target to prevent overfitting while still allowing meaningful optimization work?

The challenge: An agent can artificially inflate its score on a training/validation target by simply calling the target function many times, without learning anything generalizable to the held-out test set. We need a stopping rule or budget allocation strategy that prevents this "buying the score" behavior while not crippling legitimate optimization.

---

## 2. Comparison Design

### Main comparison: Two candidate budget-management strategies

**Condition A (Static Budget + Early Stopping):**
- Fixed initial allocation of 500 target evaluations
- Early stopping rule: halt if no improvement >1% over the last 50 consecutive evaluations
- No adaptive checkpoints; allocation is set once
- Used for: all agent types and target functions

**Condition B (Tiered Budget + Held-Out Validation):**
- Base allocation of 300 target evaluations (40% smaller initial budget)
- After reaching 300 evaluations, agent checkpoint is validated against a held-out validation split
- If test-set generalization gap exceeds 0.15 (in normalized loss space), deny further allocation and stop
- If gap is acceptable (<0.15), grant 200 additional evaluations; re-validate at the second tier
- Maximum total: 500 evaluations (same ceiling as A, but conditional on passing validation gates)

**Control Condition (Unrestricted):**
- No evaluation budget limit; agent runs for a fixed 1000 evaluations or until manual convergence (whichever first)
- No early stopping applied
- Baseline to measure whether either A or B reduces overfitting relative to unbounded consumption

### Rationale for two rejected alternatives

1. **Unlimited evaluations + post-hoc gap analysis** (rejected)
   - Only diagnoses overfitting after the fact; does not prevent it
   - Fails to address the core problem: the agent has already wasted evaluations and distorted its own performance metrics

2. **Fixed budget with no adaptation** (rejected)
   - Uniform 1000-evaluation ceiling, no checkpointing
   - Cannot distinguish between aggressive optimization and overfitting in real time
   - May waste budget on already-converged solutions on easy functions

---

## 3. Ablation

**Ablation: Sensitivity to validation gap threshold**

We systematically vary the generalization-gap threshold in Condition B:
- Threshold = 0.10 (strict, less likely to grant tier-2 budget)
- Threshold = 0.15 (base design)
- Threshold = 0.20 (permissive, more likely to grant tier-2 budget)

For each threshold level, repeat 5 seeds on a representative subset (2 functions: Rosenbrock and one hyperparameter landscape).

**Purpose:** Demonstrate that the design's robustness does not hinge on a single arbitrary threshold value. If performance degrades sharply when threshold changes, the design is brittle; if it is stable across thresholds, it is more principled.

---

## 4. Sampling Frame (Population & Units)

Copied from state.md; this is the explicit population and sampling strategy:

**Population:** Optimization benchmark tasks and optimizing agent architectures  
**Unit of analysis:** (agent_type, target_function, budget_rule) triples

**Agent types** (3 levels):
- `nevergrad-es`: Nevergrad Evolution Strategy (gradient-free, population-based)
- `botorch-bayesian`: BoTorch with Expected Improvement acquisition (model-based Bayesian optimization)
- `greedy-sa`: Simple simulated annealing with greedy hill-climbing (baseline)

**Target functions** (4 levels):
- `rosenbrock`: 10-dimensional Rosenbrock function (synthetic, moderately hard)
- `sphere`: 10-dimensional sphere function (synthetic, easy—fast convergence)
- `rastrigin`: 10-dimensional Rastrigin function (synthetic, highly multimodal)
- `hpo-mlp`: Hyperparameter optimization landscape for a small neural network on CIFAR-10 (real ML task; 8-dimensional space: learning rate, batch size, depth, width, dropout, momentum, weight decay, activation)

**Budget rules** (3 levels):
- Condition A: Static 500 evals + early stopping (1% threshold, 50-eval window)
- Condition B: Tiered 300→500 evals with gap validation (0.15 threshold)
- Control: Unrestricted 1000 evaluations

**Experimental design:**
- Full factorial: 3 agents × 4 functions × 3 budget rules = 36 conditions
- 10 random seeds per condition
- **Total runs: 360**

Each run produces: (final training loss, final test loss, total evaluations used, convergence time, overfitting gap)

---

## 5. Concrete Resources

### Target functions
- **Rosenbrock, Sphere, Rastrigin:** Use standard scipy.optimize function definitions, normalized to [−5, 5]^10 input space. Public reference implementations in scipy.optimize and pymoo
- **HPO-MLP landscape:** CIFAR-10 training with configurable MLP and hyperparameters. Use a cached lookup table (precomputed for 100 random seeds with different HP combinations) to avoid retraining 360+ models; ensures reproducibility and reasonable compute cost. Store at `./hpo_landscape.pkl` (precomputed, 50 MB estimated)

### Optimizer implementations
- **Nevergrad:** v0.13.0+ via `pip install nevergrad`. Uses CMA-ES by default
- **BoTorch:** v0.9.0+ via `pip install botorch`. Uses `qExpectedImprovement` with `RandomSampler` for 64 initial points, then EI-based acquisition for 50 iterations per seed
- **Simulated Annealing:** `scipy.optimize.anneal` or custom implementation (provided; ~50 lines Python)

### Validation splits
- **For synthetic functions:** Generate 500 random evaluation points (held-out test set) per function; freeze for all 360 runs to ensure consistency
- **For HPO-MLP:** Reserve 20 of 100 cached seeds as held-out test set; training optimization uses remaining 80 seeds' cached values

### Computing environment
- Laptop or small cloud instance (AWS t3.xlarge or equivalent)
- Python 3.10+, scipy, nevergrad, botorch, numpy, matplotlib, pandas
- Estimated runtime: 2–4 hours for all 360 runs (sequential or 4–8 parallel workers)
- Storage: ~500 MB for results CSV, visualizations, checkpoint logs

---

## 6. Outcome Metrics

### Primary outcome: Test-set generalization gap

For each run, compute:
$$	ext{Gap} = 	ext{TestLoss} - 	ext{TrainingLoss}$$

(Lower gap = better generalization; gap near zero = memorization/overfitting)

Report: Mean gap per (agent, function, budget_rule), 95% CI via t-distribution (10 seeds per condition)

### Secondary outcomes

1. **Training loss achieved** (how well the agent optimized the target)
   - Measure: final training loss value
   - Report: mean ± 95% CI per condition

2. **Evaluations consumed** (how efficiently each budget rule uses its allocation)
   - Measure: actual number of function evaluations until stopping, as % of allocated budget
   - Report: mean utilization per condition (e.g., "Condition A used 87% of 500 budget on average")

3. **Convergence time** (wall-clock seconds to stopping criterion)
   - Measure: elapsed time
   - Report: median ± IQR (since outliers are likely)

4. **Ablation outcome: Gap stability across thresholds** (for Condition B variant)
   - Measure: mean test gap for threshold = 0.10, 0.15, 0.20
   - Report: plot + ANOVA F-statistic to test if threshold has a significant effect

---

## 7. Analysis Plan

### Primary analysis: Does Condition B reduce generalization gap relative to Control?

**Hypothesis:** Tiered validation (B) yields smaller test-set gaps than unrestricted evals (Control), across most functions and agents.

**Test:** 
- Two-sample t-tests (B vs. Control) on mean gap per (agent, function) pair; 36 tests total
- Bonferroni-corrected α = 0.05 / 36 ≈ 0.0014 for significance
- Report effect size (Cohen's d) and 95% CIs for each test

### Secondary analysis: Is Condition A sufficient?

**Hypothesis:** Static early-stopping (A) is simpler but nearly as effective as B (within 10% on average gap).

**Test:**
- Two-sample t-test (A vs. B) on mean gap per (agent, function) pair; 36 tests
- Same Bonferroni correction
- Report whether A is significantly worse than B, and by how much (Cohen's d)

### Ablation analysis: Robustness to gap threshold

**Hypothesis:** Condition B's performance is stable across threshold values (0.10, 0.15, 0.20).

**Test:**
- ANOVA (or Kruskal–Wallis if non-normal) across three threshold levels for the 2-function, 3-agent subset (30 runs)
- If p > 0.05, threshold is not a significant factor; design is robust
- Plot mean gap vs. threshold with 95% CIs

### Exploratory analysis: Agent × Function interactions

**Plot:** Heatmap of mean gap (rows = agents, columns = functions, color = gap) for each condition
- Look for functions where some agents overfit more than others
- Informs whether the design generalizes uniformly

---

## 8. Uncertainty Quantification

### Standard error and confidence intervals
- All reported means include 95% confidence intervals computed via t-distribution (with Welford's online algorithm for robustness)
- For 10 seeds per condition, df = 9; t_0.025 ≈ 2.262

### Sensitivity to random seeds
- 10 seeds per condition chosen to balance statistical power with runtime
- Power analysis: with 10 seeds, we have ~80% power to detect an effect of d = 1.0 (large) on two-sample t-test (α = 0.05, two-tailed)
- Smaller effects (d ≈ 0.5) require more seeds; note this limitation

### Non-parametric fallback
- If normality assumption fails (Shapiro–Wilk p < 0.05), use Mann–Whitney U test instead of t-test
- Report both parametric and non-parametric results

### Simulation-based uncertainty (optional if budget permits)
- Resample (with replacement) 1000 bootstrap samples from the 10 seeds
- Recompute t-test statistics on each bootstrap sample
- Report 95% percentile CI directly; robust to non-normality

---

## 9. Success Criteria & Falsifiers

The experiment confirms that a budget-management strategy is worthwhile **if and only if** it avoids all three falsifiers:

**Falsifier 1: Condition A is wasteful**
- If A causes >15% higher test gap than B on average (across all functions and agents), it is too conservative and does not justify its simplicity

**Falsifier 2: Condition B is ineffective**
- If B exhibits >10% mean test-set gap relative to training loss (i.e., gap / training_loss > 0.10), the held-out validation checkpoints are not catching overfitting

**Falsifier 3: Neither A nor B beats Control**
- If neither A nor B shows significantly lower gap than unrestricted evals (p > 0.05 after Bonferroni), the budget strategies are pointless; agents don't overfit in the tested settings

**If any falsifier holds:**
- Conclude that the current designs are flawed; recommend redesign (e.g., tighter validation thresholds, different budget split, or domain-specific stopping rules)

**If all falsifiers are avoided:**
- Conclude that one of A or B can be recommended for use in the benchmark; report which is superior and by how much, with caveats for functions or agents where it underperforms

---

## 10. References to State.md

This design explicitly operationalizes the **sampling_frame** from state.md:

- **Sampling frame:** (agent_type, target_function, budget_rule) triples sampled over {nevergrad-es, botorch-bayesian, greedy-sa} × {rosenbrock, sphere, rastrigin, hpo-mlp} × {Static (A), Tiered (B), Unrestricted (Control)}, with 10 random seeds per cell
- **Population:** Optimization benchmark tasks and agent architectures
- **Unit of analysis:** Each run is one triple with one random seed
- **Generalization:** If the design is validated on this sampling frame, it informs how to bound evaluation budgets in benchmark scenarios with similar properties (black-box optimization, held-out test sets, resource metering)

---

## 11. Contingencies

- **If HPO-MLP precomputed lookup table is unavailable:** Use a simpler surrogate (e.g., a Gaussian process fit to 50 precomputed points), or remove HPO-MLP and use only 3 synthetic functions (reducing sampling frame to 3 agents × 3 functions × 3 rules = 27 conditions, 270 runs)
- **If runtime exceeds 4 hours:** Reduce seeds to 5 per condition (total ~180 runs, ~1 hour); recompute confidence intervals with df = 4
- **If results are ambiguous (overlapping CIs):** Increase seeds to 15 per condition on the most uncertain conditions and re-test after stopping-rule check
- **If an agent fails to converge:** Re-run with different random seed; if repeated, flag as an implementation bug and exclude from analysis

---

**End of Design**
