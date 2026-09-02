# Experimental Design: K4-optimizer-budget

## Research question
How should a benchmark prevent an optimizing agent from inflating its score through unlimited evaluations of the target, while still fairly measuring solution quality?

## Sampling frame reference
Per state.md: **Population** = hyperparameter optimization runs on a fixed validation-score target function. 
**Unit** = single agent-guided search trajectory from initialization to stopping, recording evaluation sequence, cost, best score progression, and held-out test performance. 
**Replicates** = 5–8 independent runs per condition with different random seeds.

---

## Main experimental comparison

**Factor**: Evaluation stopping rule  
**Conditions**:

1. **C1: Hard budget cap** (baseline)
   - Stop at exactly 1000 evaluations, regardless of convergence behavior
   - Agent continues evaluating even if no improvement observed for 20+ steps
   - Fixes the evaluation cost across all runs
   
2. **C2: Adaptive stopping with convergence signal**
   - Monitor improvement plateau: stop if no gain > 1e-4 in best-found score over last 15 evaluations
   - Additionally check held-out test: if test score has not moved in 5 consecutive evaluation rounds, override improvement threshold and stop
   - Allows early stopping for efficient agents; forces longer runs for agents that plateau late
   
3. **C3: Adaptive stopping with budget reserve**
   - Adaptive rule as in C2, but reserve 200 evaluations for a final validation sweep
   - Once improvement rule triggers, use reserve evals to confirm test signal
   - Stop only if test does not improve in reserve sweep

**Rationale**: C1 establishes that hard caps prevent unbounded optimization but do not measure efficiency. C2 tests whether convergence monitoring can identify when additional evals yield no generalization benefit. C3 tests whether protecting a validation budget improves the relationship between train-score progression and test generalization.

---

## Ablation: Evaluation order randomization

**Ablation condition C4**: Adaptive stopping (as C2) but with one modification:
- Shuffle the order in which candidate hyperparameters are evaluated at each step
- Forces the agent to not exploit evaluation-sequence correlations (e.g., always probing nearby points)
- Isolates whether the stopping rule itself is sound vs. whether agent strategies exploit the rule

**Hypothesis**: If C4 produces similar test scores to C2 but different train-score trajectories, the rule is robust. If C4 shows much worse test performance, agents are exploiting evaluation-order structure to game the train score.

---

## Analysis plan

### Primary analysis: Generalization curve
For each condition and replicate:
- Plot: evaluation count (x-axis) vs. best-found train score and corresponding held-out test score (y-axis)
- Metric: **Generalization gap** = max(train score) - test score at stopping
  - Computed at the point of stopping (when stopping rule triggers or budget exhausted)
  - Lower gap = better generalization
  
**Comparison**: ANOVA on generalization gap across conditions, post-hoc t-tests with Bonferroni correction (C1 vs C2, C1 vs C3, C2 vs C3).

### Secondary analysis: Efficiency
- Metric: **Eval count to 90% of best score** = number of evaluations needed to reach 0.9 × (final best score)
  - Computed for each replicate
  - Measures whether adaptive rules exit early without leaving performance on the table
  
**Comparison**: Paired t-test within replicates: C2 evals vs C1 evals; effect size (Cohen's d).

### Tertiary analysis: Test correlation
- Metric: Spearman rank correlation between best train score achieved and held-out test score, computed within each condition
  - Low correlation = train score is not predictive of test; high correlation = generalization signal is stable
  
**Comparison**: Fisher r-to-z test for equality of correlations across C1, C2, C3.

### Ablation analysis (C4 vs C2)
- Plot train-score trajectories for C4 and overlay C2 trajectories
- Compute trajectory divergence: sum of squared differences between trajectory paths (normalized by length)
- t-test on final test scores: are C4 and C2 indistinguishable (p > 0.05)?

---

## Concrete resources

### Target function
- **Source**: scikit-optimize SyntheticFunction (a simple, bounded, non-convex function over 10 dimensions)
  - Evaluation cost: ~10 ms per query (includes feature computation, model training stub)
  - Train/test split: 80 evals form the target surface (train); 20 withheld for test evaluation at the end
  - Deterministic: same hyperparameter always returns same train score; test set is noise-free
  
- **Rationale**: Controllable, reproducible, and allows metering; does not require external ML pipeline calls

### Hardware
- Single machine (CPU: 4 cores, RAM: 8 GB)
- No parallelization of evals (sequential); limits confounding from scheduling

### Agent implementation
- scikit-optimize Gaussian Process Optimizer (GPO) configured identically across conditions
  - Kernel: Matern 5/2, constant lengthscale
  - Acquisition: Expected Improvement
  - Configuration does not change per condition; only stopping rule differs
  
- **Rationale**: Standard, off-the-shelf optimizer; differences in stopping rule are isolated

### Software versions
- Python 3.11
- scikit-optimize 0.10.0
- numpy 1.26.0
- scipy 1.11.0

---

## Outcome metrics

### Primary outcome
**Generalization gap** (as defined in analysis plan)
- Collected at stopping point for each run
- Unit: points on the target function's score scale (dimensionless, bounded [0, 1] after scaling)
- Uncertainty: standard deviation across replicates; 95% CI via bootstrap (10k resamples)

### Secondary outcomes
1. **Evaluation efficiency**: Count of evals to reach 90% best-found score
   - Unit: integer count
   - Uncertainty: SD and 95% CI (bootstrap)
   
2. **Train–test correlation**: Spearman ρ between final train and test score per condition
   - Unit: correlation coefficient ∈ [-1, 1]
   - Uncertainty: 95% CI via Fisher transformation

3. **Stopping stability**: Coefficient of variation of stopping points (eval counts) within each condition
   - Lower CV = more consistent stopping rule
   - Unit: dimensionless ratio
   - Uncertainty: bootstrap resampling

---

## Uncertainty quantification

### Sources of variability
- **Seed variation**: 5–8 replicates per condition, each with different random seed (different initial sample, GP random state)
- **Stochasticity in agent**: GPO acquisition function uses random exploration; different random numbers lead to different trajectories
- **Sampling variability in test set**: Held-out test consists of 20 point evaluations; if the surface is noisy, test scores will vary

### Propagation of uncertainty
- **Bootstrap for point estimates**: All metrics (gap, efficiency, correlation) recomputed over 10,000 bootstrap resamples to derive CI
- **Paired comparisons**: Within-replicate pairing (same seed in C1 and C2) to reduce noise
- **Multiple comparisons**: Bonferroni correction for pairwise ANOVA post-hocs (3 comparisons → α = 0.05 / 3 ≈ 0.017)

### Sensitivity analysis
- Vary convergence threshold in C2 (1e-4 vs 1e-3 vs 5e-5) and re-run analysis to confirm results are robust to threshold choice
- Vary rolling window size (10 vs 15 vs 20 evals) in improvement plateau detection

---

## Validation checks (falsifiers in action)

1. **Sanity check: Train score monotonicity**
   - Best-found train score must be non-decreasing over time (within numerical precision)
   - If violated → target function or agent implementation is buggy; stop and fix
   
2. **Sanity check: Budget exhaustion in C1**
   - All C1 runs must stop at exactly 1000 evals (or within 1 eval due to rounding)
   - If violated → stopping rule not enforced correctly
   
3. **Design falsifier** (from state.md):
   - If held-out test score correlation with evaluation count is < 0.2 (Pearson r, p > 0.1), 
     the benchmark is not measuring real optimization; design premise is false
   - Action if falsified: Redesign stopping rule to incorporate test-set signals more directly
   
4. **Ablation validation (C4 vs C2)**
   - If C4 test scores are substantially worse (> 0.2 units lower) than C2 and reproducible, 
     agents are exploiting evaluation-order structure
   - Action: Add randomization to benchmark to prevent gaming

---

## Reporting and decision rule

**Interim reporting** (per condition, before comparison):
- Tabulate: Mean ± SD of generalization gap, efficiency, and test correlation for each condition

**Comparative reporting**:
- Pairwise t-test p-values (Bonferroni-corrected)
- Effect sizes (Cohen's d for gap, Hedges' g for efficiency)
- 95% CIs (bootstrap) overlaid on box plots

**Decision rule** (for benchmark design):
- If C2 or C3 shows significantly lower generalization gap than C1 (p < 0.017) AND 
  maintains comparable or higher test correlation, recommend adopting adaptive stopping
- If C3 outperforms C2 significantly (p < 0.017) on both gaps and correlation, 
  recommend adding the reserve validation budget
- If ablation C4 shows no difference from C2 (p > 0.05), conclude the stopping rule 
  is robust to evaluation order; safe to deploy
- If design falsifier triggers, conduct post-hoc root-cause analysis and redesign

---

## Timeline and stopping rule for this design itself

- **Planning**: Complete (this document)
- **Setup**: Configure target, agent, and stopping-rule implementations (3–5 hours)
- **Execution**: Run 6 replicates × 4 conditions (C1, C2, C3, C4) = 24 runs; 
  ~10 seconds per run (1000 evals × 10 ms + overhead) = ~4 minutes total; 
  plus overhead (~2 hours for serialization and logging)
- **Analysis**: Compute metrics, plots, and test statistics (~1 hour)
- **Stopping condition**: All 24 runs complete successfully (no crashes) AND 
  design falsifier check passes (test–eval correlation > 0.2)

If falsifier check fails, investigate root cause, modify target or agent, and restart.
If runs crash, use last successful checkpoint and extend run count to ensure 24 complete replicates.
