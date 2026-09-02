# Experimental Design: K4 Optimizer Budget Constraint Study

## Research Question
How should a benchmark stop an optimizing agent from buying its score with unlimited evaluations of the target? That is: what evaluation budget constraint, combined with what score-accounting mechanism, best prevents overfitting-via-evaluation while preserving the agent's ability to find good solutions?

## Conceptual Framing
An agent optimizes a target function and can call it many times. Without a budget constraint, it can reduce target variance to near-zero through repeated evaluations of the same point, inflating its apparent score. The benchmark must choose:
- An **evaluation budget cap** (e.g., number of target calls allowed)
- A **score accounting rule** (e.g., how to penalize or credit multiple evals of the same point)
- A **test protocol** (e.g., which evals count toward reported score; which are held out)

This design tests whether and how these choices interact to prevent gaming while preserving valid optimization progress.

---

## Main Comparison: Evaluation Budget x Accounting Rule

### Hypothesis
A score-accounting rule that **amortizes repeated evaluations** (e.g., counts only the first eval of a unique point, or averages across repeats at a cost) will prevent score gaming more effectively than a **naive rule** (e.g., reports the best single evaluation regardless of repetition count), while still permitting agents that explore efficiently to score well.

### Conditions (2 x 3 factorial)

#### Factor A: Evaluation Budget Cap
- **Unconstrained (Baseline)**: Agent may call the target function unlimited times.
- **Moderate (30 calls)**: Agent may make at most 30 target evaluations total.
- **Tight (10 calls)**: Agent may make at most 10 target evaluations total.

#### Factor B: Score Accounting Rule
1. **Naive Best-Ever**: Score = best f(x) observed across all evaluations, regardless of repetition.
2. **Unique-Point Averaging**: Score = average of all unique points evaluated. If the agent evaluates point x twice, only the unique x counts; repeats do not improve the average.
3. **Budget-Aware Averaging**: Score = (sum of all unique-point evaluations) / (number of unique points), with an explicit penalty: report only the top 80% of unique evals. This prevents the agent from evaluating the same point many times to reduce variance in the reported score.

### Prediction
- Unconstrained + Naive Best-Ever will show the **highest apparent agent scores** because the agent can game by repeated local evaluation.
- Tight budget + Unique-Point Averaging or Budget-Aware Averaging will show **lower apparent scores but more honest ranking** of solution quality.
- Moderate budget acts as an intermediate condition.

---

## Ablation 1: Role of Test/Train Split

### Design
Within the Moderate budget (30 calls) condition:
- **Split A (No held-out test)**: All 30 evals count toward the reported score. Test performance is not measured separately.
- **Split B (Held-out test, 20/10)**: First 20 evals are "training" (used to optimize and report score). Final 10 evals are held-out test; agent does not see test results until benchmark reporting.

### Rationale
This ablation isolates whether explicit separation of training and test evaluations reduces overfitting-via-evaluation. If an agent can apply only 10 evals "blindly" (test set), its ability to game through repeated local search is constrained.

### Prediction
Split B will show lower reported scores (because 10 test evals are genuinely held out) but **better generalization** to the true Pareto frontier, whereas Split A may show inflated scores because the agent can bias its 30 evals toward exploiting noise.

---

## Analysis Plan

### Primary Analysis: Score Inflation and Generalization
For each condition (Budget × Accounting Rule), measure:

1. **Reported Score** (as reported by the agent's score-accounting rule)
2. **True Score** (independently computed by evaluating the agent's best recommended point on an untouched copy of the target, using only one evaluation per unique point)
3. **Inflation Gap** = Reported - True Score
   - Hypothesis: Naive Best-Ever will show large positive inflation; Unique-Point Averaging will show minimal inflation.
   
4. **Solution Quality Rank** (how does the agent's best point rank among a curated set of known good solutions on the target?)
   - Computed post-hoc via a reference evaluation on a separate test set.

### Secondary Analysis: Budget Efficiency
For Moderate and Tight conditions:
- **Evals-to-Good-Solution**: How many target calls until the agent found a solution in the top 50% of known quality?
  - Hypothesis: Tighter budgets will reduce this; agents will exploit repeats to mask slow progress.
  
- **Unique-Point Count**: How many distinct points did the agent evaluate?
  - Hypothesis: Under Unique-Point Accounting, agents will evaluate more distinct points; under Naive Best-Ever, they will converge and repeat locally.

### Tertiary Analysis: Variance and Noise Behavior
- **Repeat Count Distribution**: For each agent, histogram of how many times it evaluated the same point.
- **Variance in Repeats**: Did repeated evals at the same point show high variance (suggesting the agent is using repeats to average noise)?
  - Hypothesis: Naive Best-Ever agents will show high repeat counts and high variance.

---

## Concrete Resources

### Target Function
**Hartmann 6D Benchmark** (scipy.optimize.rosen would be simpler but Hartmann includes multiple local optima and noise-like structure)
- Well-studied, deterministic, free to evaluate.
- Bounds: x ∈ [0, 1]^6.
- Known global optimum and landscape.

**Reference Test Set**: 1000 random points sampled uniformly on [0,1]^6, pre-evaluated on Hartmann 6D. Used for post-hoc ranking of agent solutions.

### Agent Implementation
A baseline **Random Search agent**:
- Samples points uniformly at random from [0, 1]^6.
- Spends its budget linearly: either explores new random points or repeats promising ones (behavior will differ by rule).
- No learned model; no adaptive search.
- Concrete implementation: Python + NumPy, ~50 lines.

### Benchmark Infrastructure
- A **Budget Tracker**: Intercepts all target evaluations, counts them, enforces caps.
- A **Score Recorder**: Logs each eval (x, f(x)), applies the accounting rule, reports final score.
- A **Test Harness**: Runs each (Budget, Rule) condition 10 times with different random seeds.
- No external service; all local computation.

### Computational Cost
- Per trial: ~10 seconds (evaluating Hartmann 6D 30 times and computing statistics).
- Total trials: 2 (Budget: Unconstrained, Moderate, Tight) × 3 (Rules) × 10 seeds + Ablation (2 splits × 10 seeds) = 80 trials.
- Total runtime: ~13 minutes (parallelizable).

---

## Outcome Metrics

### Primary Metrics
1. **Inflation Gap** (Reported - True Score)
   - For each condition, report mean and 95% confidence interval across 10 seeds.
   - Expected unit: points on the Hartmann scale (0 to 1, higher is better).

2. **True Score Variance** (standard deviation of evaluated solutions)
   - Hypothesis: Higher under tight budget (less exploration); lower under moderate budget with good rules.

3. **Solution Quality Percentile Rank**
   - Using the reference test set: what percentile is the agent's best point on the Hartmann landscape?
   - Hypothesis: Naive Best-Ever will show inflated rank; Unique-Point Averaging will show honest rank.

### Secondary Metrics
4. **Unique-Point Efficiency** = (Reported Score) / (Number of Unique Points Evaluated)
   - Hypothesis: Rules that force unique-point averaging will encourage more exploration.

5. **Generalization Gap** = |Reported Score - True Score| (unsigned)
   - Diagnostic: Do some rules generalize better than others?

---

## Uncertainty Quantification

### Bootstrap Confidence Intervals
- For each (Budget, Rule) condition, collect 10 replicate runs (different random seeds).
- Compute the empirical distribution of each metric across the 10 replicates.
- Report 95% CI (2.5th and 97.5th percentiles of the bootstrap distribution).

### Bayesian Hierarchical Model (Optional, if data are sparse)
If 10 replicates are insufficient:
- Assume each condition's Inflation Gap ~ Normal(μ, σ²).
- Place weak priors on μ and σ per condition.
- Fit a hierarchical model to borrow strength across conditions.
- Report posterior credible intervals (95% HDI) for each condition.

### Statistical Tests
- **Pairwise comparisons**: For each pair of rules under a fixed budget, test the null hypothesis that Inflation Gap is equal.
  - Test: permutation test or Mann–Whitney U (rank-based, non-parametric).
  - Significance level: α = 0.05, but interpret as evidence, not proof, given the exploratory nature.

---

## Interpretive Framework

### Success Criterion
The main comparison **succeeds** if:
- Unconstrained + Naive Best-Ever shows a **large Inflation Gap** (e.g., ≥ 0.1 on the Hartmann scale).
- Unique-Point Accounting or Budget-Aware Accounting reduces this gap to **near zero** (< 0.05).
- The agent's True Score and Percentile Rank are **comparable across rules**, indicating that rules prevent gaming without eliminating real optimization.

### Ablation Success Criterion
The train/test split ablation **succeeds** if:
- Reported and True Scores are **much closer in Split B** (held-out test) than in Split A.
- This would indicate that explicit test separation is effective for preventing gaming.

### Failure Modes and Sensitivity
- If all rules perform similarly, the conclusion is that the **random search agent is inherently honest** and does not game evaluations; the main hypothesis is not supported. This is still a valid outcome.
- If Unique-Point Accounting severely **penalizes legitimate exploration**, reported scores under that rule will be unrealistically low. This would suggest the rule is too strict.
- If results are **highly sensitive to the choice of target function**, generalizability is questionable; recommend testing on 3–5 targets (not included in current design to keep scope bounded).

---

## Design Justification

### Why This Design?
1. **Directness**: Directly addresses the research question by comparing accounting rules head-to-head.
2. **Concreteness**: Uses a real, free optimization target (Hartmann 6D) and a simple agent (random search) to isolate the effect of accounting rules.
3. **Interpretability**: Metrics (Inflation Gap, True Score, Percentile Rank) directly measure what the rules are meant to prevent (gaming) and enable (honest ranking).
4. **Feasibility**: Entire study is runnable in < 30 minutes on a laptop; no GPU, no external APIs required.

### Limitations Acknowledged
1. **Simple Agent**: Random search is not realistic for many optimization scenarios. A Bayesian optimization or evolutionary agent might show different gaming patterns.
2. **Single Target**: Hartmann 6D is well-behaved. Noisier or higher-dimensional targets might expose different rule strengths.
3. **Fixed Budget Levels**: The choice of 10 and 30 evals is arbitrary. Sensitivity analysis across budgets (5, 15, 30, 100) would be more complete.
4. **No Learned Model**: No test of rules' robustness to learned surrogates (which could enable more sophisticated gaming).

These limitations are acceptable for a **proof-of-concept design** and can inform future work.

---

## Summary: What Gets Reported

1. **A table** of Inflation Gap (mean ± 95% CI) for all 3 Budget × 3 Rule combinations (9 rows).
2. **A table** of True Score and Percentile Rank for comparison.
3. **A plot** (Budget on x-axis, Inflation Gap on y-axis, Rule as color/line type) showing how rules differ under each budget.
4. **An ablation summary** comparing Split A (no held-out test) vs. Split B (held-out test) on Inflation Gap and True Score.
5. **Qualitative discussion**: Which rule best prevents gaming? At what cost to solution quality? Are there trade-offs?

No numeric results are computed in this design document; all metrics and analyses are specified but not executed.
