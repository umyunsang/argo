# Experimental Design: Evaluation Budget Constraints for Optimizing Agents

## Research Question

How should a benchmark stop an optimizing agent from buying its score with unlimited evaluations of the target?

## Hypothesis

Evaluation budget constraints that bound the **number of target function calls** during optimization are necessary but insufficient. The key insight is that an agent can still "buy" its score by using evaluations strategically—concentrating them late in optimization to find superficially good solutions that overfit to the evaluation set. A principled budget constraint must couple evaluation limits with **temporal or structural restrictions** on when and how evaluations can be used.

---

## Main Comparison

### **Primary Experimental Condition: Bounded Evaluation Budget with Temporal Gating**

Three conditions are compared to test whether temporal structure prevents score-buying:

#### **Condition A: Unrestricted Evaluations (Baseline)**
- Agent receives unlimited calls to the target evaluation function
- No constraints on timing or concentration
- **Expected outcome**: Agent achieves superficially high scores on the target but poor generalization to held-out test

#### **Condition B: Evaluation Budget Only (Quantity Control)**
- Agent receives a fixed budget of **K target evaluations** (K = 50, consistent across all instances)
- Evaluations can be spent at any time and in any concentration
- No restrictions on temporal clustering
- **Expected outcome**: Agent achieves better scores than unlimited via selective querying, but still overfits through late-stage concentrated probing

#### **Condition C: Evaluation Budget + Temporal Gating (Budget + Structure)**
- Agent receives a fixed budget of **K target evaluations** (K = 50, same as Condition B)
- Evaluations are partitioned into **M phases** (M = 5 phases of 10 evaluations each)
- Each phase spans a **fixed optimization interval** (e.g., 20% of total optimization time)
- Agent cannot carry unused budget forward; unused evaluations in a phase are forfeited
- **Expected outcome**: Forces distributed exploration; reduces overfitting; better generalization to held-out test

---

## Ablation Study

### **Ablation A1: Phase Structure Sensitivity**

Testing whether the benefit of Condition C depends on the phase granularity:

#### **Condition C1: Coarse Gating (M=3 phases)**
- Same as Condition C but with 3 phases of ~17 evaluations each
- Larger "windows" allow more flexibility

#### **Condition C2: Fine Gating (M=10 phases)**
- Same as Condition C but with 10 phases of 5 evaluations each
- Smaller "windows" force tighter temporal distribution

**Hypothesis**: Intermediate granularity (M=5) balances exploration and overfitting prevention. Too coarse (M=3) reverts to late-stage concentration; too fine (M=10) may over-constrain exploration.

---

## Problem Instances and Resources

### **Benchmark Problem: High-Dimensional Black-Box Optimization**

We use the **BBOB (Black-Box Optimization Benchmarking) Suite** as the evaluation target, which is freely available and reproducible.

#### **Specific BBOB Functions:**
1. **Sphere (f1)**: Separable, convex. Baseline easy problem.
2. **Ellipsoid (f2)**: Ill-conditioned quadratic. Tests scaling.
3. **Rastrigin (f8)**: Highly multimodal, deceptive. Tests local optima avoidance.
4. **Schwefel (f20)**: Multimodal with deep local basins. Tests exploration–exploitation tradeoff.

#### **Problem Dimensionality:** 10 dimensions (d=10, widely used in BBOB studies)

#### **Budget Justification:**
- K=50 evaluations is realistic for expensive simulation/experiment budgets in engineering (e.g., CFD, material testing)
- Large enough to permit meaningful optimization but small enough to make score-buying a tangible concern
- Consistent with prior work on constrained optimization (e.g., CMA-ES benchmarks at 50–100 evaluations)

#### **Agent Runtime:** 1000 seconds per trial (wall-clock limit, independent of evaluation count)

#### **Held-Out Test Set:** Each BBOB function is evaluated at a fixed set of 1000 random points in the feasible domain. The final agent solution is scored against this held-out set to measure generalization.

---

## Experimental Factors and Levels

| Factor | Levels |
|--------|--------|
| **Evaluation Budget Constraint** | None (Baseline), Budget Only (50), Budget + Temporal Gating (50 + 5 phases) |
| **Phase Granularity** (Ablation) | 3 phases, 5 phases, 10 phases |
| **BBOB Function** | f1 (Sphere), f2 (Ellipsoid), f8 (Rastrigin), f20 (Schwefel) |
| **Replication** | 30 independent runs per condition–function pair |

**Total Trials:** 3 conditions × 4 functions × 30 replicates = 360 trials; plus ablation: 3 × 4 × 30 = 360 trials. **Total: 720 trials.**

---

## Outcome Metrics

### **Primary Metrics:**

1. **Target Score at Budget Limit** (during optimization)
   - Best objective value found by the agent after consuming all K evaluations (or unlimited in Condition A after similar time)
   - Directly measures whether the agent found a good solution on the training target

2. **Held-Out Generalization Gap**
   - Defined as: `Held-Out Score - Target Score at Budget Limit`
   - Positive gap indicates overfitting
   - Measures whether the solution generalizes beyond the evaluations seen during optimization

3. **Held-Out Test Score**
   - Objective value of the final solution when evaluated on 1000 held-out random points (averaged)
   - Direct measure of generalization quality

4. **Evaluation Efficiency**
   - Defined as: `(Target Score at Budget Limit) / (Number of Evaluations Used)`
   - For Condition A, use a proxy: evaluations used within the same time limit as constrained conditions
   - Measures how many "good results per evaluation" the agent achieved

### **Secondary Metrics:**

5. **Evaluation Concentration Index** (for Conditions B and C)
   - Entropy of evaluation spending across time intervals
   - Low entropy → concentrated spending (score-buying behavior); high entropy → distributed spending
   - Calculated as Shannon entropy of the fraction of evaluations per phase

6. **Time-to-Target** (cost-aware)
   - Wall-clock time to reach 90% of the best final solution quality
   - Measures exploration speed

---

## Analysis Plan

### **Stage 1: Descriptive Analysis**
- Report median, quartiles, and standard deviation of each metric by condition and function
- Visualize distributions as violin plots (target score, generalization gap, held-out score)
- Plot evaluation concentration indices to confirm intended behavior differences

### **Stage 2: Hypothesis Tests**

#### **Primary Hypothesis: Condition C outperforms Condition B on held-out generalization**
- **Test**: Paired Wilcoxon signed-rank test (non-parametric, robust to outliers)
- **Null**: Condition C and Condition B have equal held-out test scores
- **Alternative**: Condition C has significantly better held-out test scores
- **α = 0.05, two-tailed**
- **Stratified by function** (separate tests for each BBOB function)

#### **Secondary Hypothesis: Temporal gating reduces overfitting without sacrificing target score**
- Compare `(Target Score, Generalization Gap)` for Conditions B vs. C using a 2D paired test
  - Condition C should have **larger** target score (or similar) AND **smaller** generalization gap
- **Test**: For each replicate, compute the signed difference in generalization gap (B minus C). Test if the median difference is positive (overfitting is worse in B) using Wilcoxon signed-rank.
- **α = 0.05, one-tailed**

### **Stage 3: Effect Size and Confidence Intervals**
- Compute effect size (rank-biserial correlation) for each pairwise comparison
- Report 95% bootstrap confidence intervals on the median difference in held-out score (10,000 resamples, percentile method)

### **Stage 4: Ablation Analysis (Phase Granularity)**
- Perform Kruskal-Wallis test across Condition C1, C2, C (M=3, 10, 5)
  - **Null**: No difference in held-out score across phase granularities
  - **α = 0.05**
- If significant, perform pairwise Wilcoxon tests with Bonferroni correction (α = 0.05/3)
- Plot held-out score vs. phase granularity (M) to visualize the trend

### **Stage 5: Interaction Analysis**
- Does the benefit of temporal gating depend on function difficulty?
- Perform a two-way ANOVA (or Kruskal-Wallis if assumptions violated) with factors: Condition (B vs. C), Function (f1, f2, f8, f20), and their interaction
- **α = 0.05**

### **Stage 6: Robustness Checks**
- Sensitivity to K: Rerun Conditions B and C with K = 30 and K = 75 (on a subset of 2 functions, 10 replicates each) to confirm that benefits generalize across budgets
- Runtime sensitivity: Confirm that the 1000-second runtime limit is consistently binding; report wall-clock time used

---

## Uncertainty Quantification

### **Approach: Bootstrap Confidence Intervals and Bayesian Posterior Credible Intervals**

1. **Bootstrap CI for Median Held-Out Score**
   - For each condition–function pair, resample with replacement (1000 resamples)
   - Compute median and 2.5th/97.5th percentile points
   - Report 95% CIs alongside point estimates

2. **Bayesian Posterior for Effect Size**
   - Model held-out score difference (Condition C minus Condition B) as drawn from a Student-t distribution (robust to outliers)
   - Prior: flat (Jeffreys prior on location and scale)
   - Posterior: computed via MCMC (e.g., No-U-Turn Sampler, 2000 samples, 1000 burn-in)
   - Report 95% credible interval and posterior probability that Condition C > Condition B

3. **Replication Variability**
   - Run 30 replicates per condition–function pair specifically to quantify trial-to-trial variability
   - Compute standard error of the mean held-out score
   - Report sample size justification: n=30 is sufficient to detect a medium effect (Cohen's d ≈ 0.5) with 80% power at α=0.05 for a two-sample t-test, even with moderate non-normality

4. **Multiple Comparisons Correction**
   - Since ablation involves 3 pairwise comparisons (C1 vs. C2, C1 vs. C, C2 vs. C), apply Bonferroni correction: α = 0.05/3 ≈ 0.017
   - Report both corrected and uncorrected p-values

### **Sensitivity Analysis**
- Vary the budget K: Does the effect of temporal gating persist?
- Vary phase granularity M (ablation study): What M value optimizes generalization?
- Vary held-out test set size: Does the gap grow or shrink with larger test sets?

---

## Implementation and Reproducibility

### **Software & Toolchain:**
- **BBOB Suite**: Available via https://github.com/numbbo/coco (open-source, C/Python)
- **Optimization Agent**: Use CMA-ES (Covariance Matrix Adaptation Evolution Strategy) as the baseline agent
  - **Rationale**: CMA-ES is well-established, deterministic (except random initialization), and widely available
  - **Reference Implementation**: `pycma` Python package (https://github.com/CMA-ES/pycma)
  - **Justification for choice**: CMA-ES does not inherently prevent score-buying; it is agnostic to when evaluations are queried. This makes it a neutral agent for testing the effectiveness of budget and gating mechanisms.

### **Modification for Conditions:**
- **Baseline (Condition A)**: Standard CMA-ES with unlimited evaluations; stop after 1000 seconds
- **Budget Only (Condition B)**: CMA-ES with evaluation count capped at K; stop early if budget exhausted
- **Temporal Gating (Condition C)**: CMA-ES modified to track wall-clock time and halt optimization after each phase; a custom wrapper enforces phase-based budget carryover rules

### **Held-Out Test Evaluation:**
- After the agent terminates, retrieve its final solution vector
- Evaluate this solution at each of the 1000 held-out points (pre-generated, fixed across all trials)
- Report the mean objective value on held-out points

### **Reproducibility:**
- Fix random seeds for BBOB function instance generation, CMA-ES initialization, and held-out test point sampling
- Log all configuration parameters (K, M, function ID, seed) and results to a structured CSV file
- Version control: use a tagged commit in a GitHub repository with full experimental code

---

## Expected Outcomes and Interpretations

### **If Condition C performs better on held-out score:**
- **Interpretation**: Temporal gating successfully reduces overfitting to the evaluation budget. Practical implication: benchmarks should enforce phase-based evaluation limits, not just total budgets.
- **Next step**: Optimize phase granularity (M) through ablation; explore automatic phase scheduling.

### **If Condition B (budget only) matches Condition C:**
- **Interpretation**: Simple budget caps are sufficient; temporal structure adds no value. Practical implication: total evaluation count is the binding constraint, not timing.
- **Next step**: Investigate whether agents naturally distribute evaluations, or if the BBOB suite's landscape properties make temporal gating moot.

### **If Condition A (unlimited) outperforms all budgeted conditions:**
- **Interpretation**: This is expected and validates the benchmark design—unlimited evaluations should find better solutions. The comparison of interest is between B and C.
- **Next step**: Confirm that the held-out test set is sufficiently large and independent; adjust if necessary.

---

## Summary Table: Experimental Design Overview

| Component | Specification |
|-----------|---|
| **Research Question** | How should a benchmark prevent evaluation budget exploitation? |
| **Main Conditions** | Unrestricted (A), Budget Only (B), Budget + Temporal Gating (C) |
| **Ablation** | Phase Granularity (M = 3, 5, 10) |
| **Problems** | BBOB f1, f2, f8, f20; d=10 |
| **Budget K** | 50 evaluations (and sensitivity to 30, 75) |
| **Replicates** | 30 per condition–function pair |
| **Total Trials** | 720 (360 main, 360 ablation) |
| **Primary Metrics** | Target Score, Held-Out Score, Generalization Gap, Evaluation Efficiency |
| **Analysis** | Wilcoxon tests, bootstrap CIs, Bayesian credible intervals, interaction analysis |
| **Uncertainty** | 95% CIs, posterior credible intervals, Bonferroni correction for multiple comparisons |
| **Software** | BBOB (Coco), CMA-ES (pycma), Python 3.9+ |
| **Reproducibility** | Fixed seeds, versioned code, logged parameters |

---

## Justification of Design Choices

1. **Why BBOB?**
   - Open, standardized, and independent of the agent design
   - Functions span diverse landscapes (convex, multimodal, deceptive)
   - Widely used in optimization research; results are comparable to literature

2. **Why K=50?**
   - Realistic for expensive evaluations (engineering, science)
   - Large enough to optimize but small enough that wasting evaluations is costly
   - Common budget in constrained optimization studies

3. **Why M=5 phases (default)?**
   - Balances exploration diversity (5 distinct time windows) with flexibility
   - Cannot be directly justified a priori; ablation is needed
   - Aligned with classic staged optimization (e.g., multi-start local search stages)

4. **Why CMA-ES?**
   - Deterministic, well-understood, no built-in anti-gaming mechanisms
   - Neutral testbed for evaluation budget mechanisms
   - Does not conflate agent strategy with budget enforcement

5. **Why Wilcoxon + Bootstrap CIs?**
   - Non-parametric; robust to outliers and skewness
   - Replication count (n=30) may not guarantee normality even with Central Limit Theorem for non-standard metrics
   - Bootstrap CIs are distribution-free and interpretable

6. **Why held-out test set of 1000 points?**
   - Large enough to provide stable generalization estimate
   - Cannot be directly justified without domain knowledge; sensitivity analysis warranted
   - Random sampling ensures independence from the optimization landscape

---

## Limitations and Assumptions

1. **Assumption: CMA-ES is representative**
   - Results may not generalize to other optimizers (e.g., Bayesian optimization, gradient-free evolutionary algorithms)
   - Mitigation: Future work should repeat with alternative agents

2. **Assumption: Random held-out points are relevant**
   - BBOB functions have known structure; random evaluation points may not reflect realistic test distributions
   - Mitigation: Conduct secondary analysis using grid-based or importance-sampled held-out sets

3. **Limitation: Wall-clock time is not controlled**
   - Conditions B and C may terminate early (budget exhausted) while Condition A still optimizes
   - Mitigation: Use "time-normalized" secondary analysis (rescale scores to account for runtime differences)

4. **Limitation: No real-world optimization tasks**
   - BBOB is synthetic; score-buying behavior may differ on real engineering/ML problems
   - Mitigation: Validation experiments with real-world surrogates (e.g., hyperparameter optimization on a neural network)

---

## Deliverables

1. **Experimental results table** (CSV): condition, function, replicate ID, target score, held-out score, generalization gap, evaluation efficiency, evaluation concentration index
2. **Visualization suite**: violin plots (scores by condition), scatter plots (target vs. held-out), trend plots (phase granularity sensitivity)
3. **Statistical report** (LaTeX/Markdown): hypothesis tests, effect sizes, confidence intervals, interaction analysis
4. **Code repository**: BBOB setup, CMA-ES wrapper with budget/gating logic, analysis scripts (Python + R)
5. **Replication instructions**: Exact commands to download data, install dependencies, and reproduce all figures and tests
