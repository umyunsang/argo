# Experimental Design: K4-Optimizer-Budget Detection

## 1. Research Objective

Demonstrate that a cost-metered evaluation budget combined with trajectory-level inspection
can reliably distinguish agents that game a benchmark (maximize score via repeated eval 
queries) from agents that legitimately refine solutions, while quantifying statistical 
power and practical overhead at fixed total eval cost.

**Sampling frame**: Agents × Problem instances, stratified by problem difficulty (tractable 
vs. hard) and evaluation budget regime, with 12 repeated trials per cell.

---

## 2. Main Comparison: Budget Regime × Inspection Depth

### 2.1 Budget Regimes (Primary Factor)

Four nested evaluation budgets per agent-problem trial:

1. **STRICT** (B=10 evals max per trial)
   - Agents must solve in ≤10 eval calls or admit defeat
   - Simulates high-cost settings (e.g., medical/legal domains)
   - Baseline for detecting forced strategy change

2. **MODERATE** (B=50 evals max per trial)  
   - Typical "development" budget; allows refinement
   - Threshold where gaming begins to look rational
   - References 2606.07591: budget zone before re-discovery plateau

3. **PERMISSIVE** (B=200 evals max per trial)
   - Agent can explore extensively; gaming is dominant strategy
   - 200 calls ≈ exhaustive search on moderate-size spaces
   - Control for effort-dependent gaming likelihood

4. **UNLIMITED-CONTROL** (B=5000 evals max per trial; metered but logged)
   - Upper bound where no agent should hit the limit legitimately
   - Establishes asymptotic gaming behavior for comparison
   - Confirms that budget is non-trivial constraint for STRICT/MODERATE

**Hypothesis**: Power to detect gaming increases from STRICT → PERMISSIVE 
(more evidence accumulates) then plateaus at UNLIMITED-CONTROL (ceiling effect).

### 2.2 Trajectory Inspection Depth (Ablation Factor)

Two levels:

1. **COARSE**: Final output score only (outcome-only)
   - Records: final score, total eval count
   - Baseline control (equivalent to 2609.00038 outcome-only judges)
   - Expected: low power to detect gaming, high false-negative rate

2. **DETAILED**: Trajectory + query audit + belief log
   - Records: step-by-step score, eval query sequence, claimed reasoning
   - Extracted from agent logs (per 2607.09195 Hypothesis Evolution Protocol)
   - Enables gap detection (2608.01913): are query results actually used downstream?
   - Expected: high power to detect gaming, low false-positive rate

**Hypothesis**: DETAILED inspection at MODERATE budget ≈ COARSE inspection at PERMISSIVE 
budget in terms of power (tradeoff between inspection depth and evidence quantity).

### 2.3 Problem Stratification

**Class A (Tractable)**: 
  - 8 benchmark problems solvable in 5–20 legitimate refinement steps
  - Examples: sorting, arithmetic optimization, structured puzzles
  - Expected gaming behavior: agent repeats same queries or explores nearby scores

**Class B (Hard)**:
  - 8 benchmark problems requiring >20 steps or external knowledge
  - Examples: open-ended search, multi-stage reasoning, retrieval problems  
  - Expected gaming behavior: agent samples uniformly across eval space (less obvious pattern)

**Design choice justification** (2606.07591 ResearchClawBench): 
  Separates strategy effects (gaming vs. solving) from problem difficulty effects.

---

## 3. Experimental Conditions

Full factorial design:

| Factor | Levels | Replicates |
|--------|--------|-----------|
| Problem Class | 2 (A, B) | 8 problems each |
| Budget Regime | 4 (STRICT, MODERATE, PERMISSIVE, UNLIMITED) | 12 trials per cell |
| Inspection Depth | 2 (COARSE, DETAILED) | built into scoring |
| **Total Cells** | 2 × 4 × 2 | 16 cells |
| **Total Trials** | | 16 × 12 = 192 trials |

**Randomization**: Within each cell, randomize trial order and random seed for agent.
**Blocking**: Run all 12 replicates of a (Problem Class, Budget, Inspection) cell 
  consecutively to minimize drift in agent behavior or environment state.

---

## 4. Agents and Baselines

### 4.1 Test Agents

**RefineMax** (legitimate solver):
  - Iterative hill-climbing: query eval, improve solution by perturbation, repeat
  - Target strategy: use budget for genuine optimization
  - Expected eval sequence: monotonically improving scores

**RandomSampler** (canonical gamer):
  - Generates random solutions, queries all evals upfront, submits highest-scoring one
  - Target strategy: exploit budget to brute-force
  - Expected eval sequence: no correlation between query order and score improvement

**AdaptiveExplorer** (hybrid):
  - Queries evals, updates internal model, then queries evals on candidate solutions
  - May or may not use results; trajectory inspection reveals utilization gap
  - Expected eval sequence: has structure but may include wasteful queries
  - **Critical for design validation**: if detection fails on this agent, design lacks power

### 4.2 Ground Truth Labels

  - RefineMax → SOLVER (assigned before trial; not revealed to inspector)
  - RandomSampler → GAMER
  - AdaptiveExplorer → AMBIGUOUS (intentionally hard case)

Classification accuracy is primary outcome metric.

---

## 5. Measurement Model: Detecting Gaming

### 5.1 Scoring Rules

#### Score A: Outcome-Only (COARSE inspection)

S_A = final_score

where final_score is the score of the agent's submitted solution.

**Interpretation**: If S_A is high, agent found a good solution (uninformative about method).

#### Score B: Trajectory Audit (DETAILED inspection)

Construct a **Gaming Likelihood Index (GLI)** from agent logs:

  GLI = 0.5 * CorrScore + 0.3 * UtilGap + 0.2 * ReusePenalty

Where:
- **CorrScore**: Pearson correlation between eval query position and score
  - Gaming (RandomSampler): r ≈ 0 (no ordering effect)
  - Solving (RefineMax): r ≈ 0.7 (later queries yield better scores)
  - Justified by 2608.01913 (search diagnostics)

- **UtilGap**: Fraction of queried solutions NOT used in subsequent refinements
  - Gaming: ≈ 1.0 (all queries discarded except final max)
  - Solving: ≈ 0.1–0.3 (use results iteratively)
  - Justified by 2608.01913 (utilization gap definition)

- **ReusePenalty**: Binary indicator (1 if agent re-queries the same solution)
  - Justified by 2607.09195 (hypothesis evolution protocol)

**Weights** (equal-variance standardization; adjust post-hoc): 0.5, 0.3, 0.2

GLI is NOT given to agent; computed post-hoc for evaluation only.

#### Primary Outcome: Classification Accuracy

  Accuracy = (# Correct Predictions Gaming vs. Solving) / n

**Predictions** based on:
- COARSE: threshold on S_A (tuned on pilot data)
- DETAILED: threshold on GLI (similarly tuned)

Compare accuracy between COARSE and DETAILED at each (Budget, ProblemClass) cell.

**Hypothesis**: Accuracy_DETAILED - Accuracy_COARSE > 0.15 
  (15 percentage points, justified by 2609.00038 finding 45% vs 77% silent recall).

---

## 6. Ablation: Trajectory Inspection Depth

### Rationale (from evidence)

**2609.00038 (trajectory-judge)**: Outcome-only judges achieve 45% silent-fault recall; 
  step-rubric judges achieve 77% with zero false alarms at 3× cost.

**2608.01913 (Search Agent Diagnosis)**: Step-wise gap analysis (retrieval vs utilization) 
  enables precise failure localization.

### Ablation Design

Run each trial under TWO scoring regimes:
  1. Outcome-only (COARSE): agent sees final score and eval count
  2. Detailed trajectory (DETAILED): inspector post-processes logs to compute GLI

**Comparison**: Accuracy and confidence interval of classification at each (Budget, Class).

**Expected result**: DETAILED significantly improves accuracy. If not, conclude that gaming 
behavior is indistinguishable from refinement even with detailed logs (falsifier, §9).

---

## 7. Concrete Resources

### 7.1 Problem Set

Use 16 benchmark problems (existing, all deterministic, scalar score 0-100):

**Class A (Tractable)**, 8 problems:
  1. Integer linear programming (small LP from CVXPY examples)
  2. Knapsack optimization (25 items)
  3. Traveling salesman problem (15 cities)
  4. Quadratic assignment (10×10)
  5. Portfolio optimization (15 assets, CVXPY)
  6. Bin packing (25 items)
  7. Graph coloring (10 nodes)
  8. Constraint satisfaction (SAT instance, 20 vars, 40 clauses)

**Class B (Hard)**, 8 problems:
  1. Long-horizon reasoning (multi-step logic puzzle, 10 steps)
  2. Open-ended optimization (neural architecture search, simplified)
  3. Retrieval-based QA (5 documents, 3-hop reasoning)
  4. Theorem proving (formal logic, 5-goal proof)
  5. Inverse design (parametric optimization, 50D)
  6. Open-ended planning (blocks world, 8 blocks)
  7. Puzzle combination (Sudoku-like but parametric)
  8. Synthesis task (generate code to pass 3 test cases)

**Justification**: 
  - All are deterministic (evaluator is consistent)
  - All have a scalar score 0–100 (normalized)
  - All support ≤5000 evaluations without resource exhaustion
  - A-class: solvable in ≤20 steps by reference algorithm
  - B-class: require >20 steps or external knowledge by design
  - Reference: ResearchClawBench (2606.07591) uses similar cross-domain problem sets

### 7.2 Agents

Implement three agents as Python classes:

**RefineMax**: 
  - Hill-climbing with 1-Lipschitz step (scipy.optimize.minimize)
  - Deterministic given seed

**RandomSampler**: 
  - numpy.random sample uniformly, collect evals, return max
  - Deterministic given seed

**AdaptiveExplorer**: 
  - Gaussian process model trained on initial samples
  - EI acquisition, iteratively refine (GPy library)
  - Deterministic given seed

All agents:
  - Log all queries (solution, score, timestamp)
  - Support arbitrary scalar-valued problems
  - Run within budget limits (halt when exhausted)

### 7.3 Evaluation Infrastructure

**Query Logger**:
  Maintain ordered log of (trial_id, solution, score, timestamp) for each agent trial.
  Support retrospective trajectory reconstruction.

**Compute requirements**:
  - 192 trials × (max 5000 evals per trial) = up to 960K evaluations
  - Class A problems: ~0.01 sec per eval (LPs, combinatorics)
  - Class B problems: ~0.1 sec per eval (NN-based, search)
  - **Total wall-clock**: 10–20 hours on 1 CPU (parallelizable by trial)
  - Storage: ~100 MB for logs (16 bytes per query × 960K queries)

All resources are standard (Python, scipy, GPy, numpy).

---

## 8. Analysis Plan

### 8.1 Primary Comparison: ANOVA on Classification Accuracy

**Outcome variable**: Binary classification accuracy (% of trials correctly labeled Gaming vs. Solving)

**Factors**:
  - Budget Regime: STRICT, MODERATE, PERMISSIVE, UNLIMITED (fixed effect)
  - Problem Class: A, B (fixed effect)
  - Inspection Depth: COARSE, DETAILED (fixed effect)
  - Trial replicate (random effect, nested within cell)

**Model** (following 2607.13304 crossed generalizability framework):

  Accuracy = mu + alpha_i + beta_j + gamma_k 
             + (alpha-beta)_ij + (alpha-gamma)_ik + (beta-gamma)_jk
             + (alpha-beta-gamma)_ijk + epsilon_ijkr

where:
  - mu = overall accuracy
  - alpha_i = Budget effect (main)
  - beta_j = Problem Class effect
  - gamma_k = Inspection Depth effect
  - interaction terms capture two-way effects
  - epsilon_ijkr = trial-level residual

**Inference**:
  - F-tests for main effects and two-way interactions
  - Effect sizes (standardized mean differences) between inspection depths
  - Confidence intervals on accuracy via Agresti–Coull binomial method (n=12 per cell)

### 8.2 Secondary: Utility of Classification Scores

Compute ROC curves and AUC for GLI and outcome scores as continuous classifiers:

  AUC_DETAILED vs. AUC_COARSE

Expected: DETAILED AUC > 0.85; COARSE AUC < 0.65 (near random for hard problems).

### 8.3 Power Analysis (Post-Hoc)

**Reference**: 2010.06595 (power norms), 2605.30315 (paired resolution diagnostics)

For each cell, compute achieved power:

  Power = P(Reject H0 | True Effect Exists)

where H0 is "Gaming and Solving agents are indistinguishable in accuracy."

Effect size interpretation per typical Cohen's d:
  - d = 0.2 (small): power ≈ 0.35 at n=12 (underpowered)
  - d = 0.5 (medium): power ≈ 0.80 at n=12
  - d = 0.8 (large): power ≈ 0.95 at n=12

**Interpretation**: If observed effect is small, 12 trials may be insufficient. 
Report this as a study limitation.

---

## 9. Outcome Metrics and Uncertainty

### 9.1 Primary Metrics

**Metric 1: Classification Accuracy (%)**
  - Definition: % of trials correctly labeled Gaming vs. Solving
  - Reported by: Inspection depth (COARSE vs. DETAILED) × Budget regime
  - Uncertainty: 95% Agresti–Coull confidence interval (n=12 replicates)
  - Threshold for success: Acc_DETAILED > 80% at MODERATE budget

**Metric 2: Detection Power Gain (percentage points)**
  - Delta_Power = Acc_DETAILED - Acc_COARSE
  - Reported by Budget regime × Problem Class
  - Uncertainty: 95% bootstrap CI on difference of proportions
  - Threshold for success: Delta_Power > 15 pts at all budgets

**Metric 3: Confidence Calibration**
  - Classifier outputs confidence score [0, 1] for each trial
  - Compute: Brier score = mean squared error between predicted probability and true label
  - Expected: DETAILED Brier score < 0.1 at MODERATE budget

### 9.2 Secondary Metrics

**Metric 4: Cost per Classification**
  - Total evaluations used / accuracy per trial
  - Useful for comparing MODERATE vs. PERMISSIVE
  - Reported: mean cost × inspection depth

**Metric 5: Sensitivity & Specificity per Budget**
  - Sensitivity = true-positive rate (gaming agents correctly identified)
  - Specificity = true-negative rate (solving agents correctly identified)
  - Compute for DETAILED vs. COARSE at each budget
  - Expected per 2609.00038: DETAILED sensitivity > 0.77, specificity ≈ 1.0

**Metric 6: Variance Component Estimates** (following 2607.13304)

Partition total accuracy variance into:
  - Problem effect (does problem class drive differences?)
  - Budget effect (does budget matter most?)
  - Inspection-depth effect (is trajectory data valuable?)
  - Residual (irreducible noise)

Report variance components and their proportions.

---

## 10. Falsifier and Stopping Rule

### 10.1 Falsifying Observation

The design premise fails if:

**After inspection, Acc_DETAILED does NOT exceed Acc_COARSE by >10 percentage points at 
MODERATE budget.**

This would indicate that auditable trajectory state does not contain signal distinguishing 
gaming from refinement, contradicting evidence from 2609.00038.

**Interpretation**: Trajectory inspection may be infeasible or insufficient; the benchmark 
may require fundamentally different mechanisms (e.g., sandboxing eval calls, enforcing 
solution commitment before eval access).

### 10.2 Primary Stopping Rule

Collect all 192 trials (2 classes × 4 budgets × 2 depths × 12 replicates) before analysis.

**Rationale**: Balanced factorial design is required for variance component estimation 
(2607.13304); early stopping would confound budget effects with trial order effects.

### 10.3 Early Stopping (Secondary)

If after 72 trials (1 problem class × 3 budgets × 1 inspection depth × 8 replicates), 
the variance explained by Inspection Depth is estimated to be <5% of total variance, 
halt and report null result (trajectory inspection offers no practical benefit).

**Justification**: Allows early detection of failed hypothesis without wasting 3× more compute.

### 10.4 Cost Boundary

Total eval budget across all trials: B_total = 2M evals 
(roughly: 192 trials × 10 evals avg per STRICT, or 192 × 50 per MODERATE).

If forecast overage (sum of observed eval usage × remaining trials) exceeds B_total:
  - Reduce trials per cell from 12 → 10 or 12 → 8 (keep total under budget)
  - Re-fit model with variable cell sizes using weighted generalized least squares
  - Document trade-off in limitations section

---

## 11. Concrete Experimental Workflow

### Phase 1: Setup (Day 1)
  - Instantiate 16 problems, verify each evaluates correctly
  - Implement RefineMax, RandomSampler, AdaptiveExplorer agents
  - Verify agent + evaluator logging: run 2 smoke tests per agent, inspect logs

### Phase 2: Pilot (Days 2–3)
  - Run 24 trials (1 cell × 2 budgets × 2 depths × 6 replicates)
  - Estimate effect size and variance (2010.06595 power norms)
  - Adjust GLI weights if components have unexpected distributions
  - Pre-register thresholds for classification (COARSE cutoff, GLI cutoff) on pilot

### Phase 3: Main Study (Days 4–14)
  - Run 192 trials in randomized order (or blocked by cell if drift is concern)
  - Stream logs to disk; compute running diagnostics
  - Monitor: any agent hitting eval budget? any evaluator failure?

### Phase 4: Analysis (Day 15)
  - Fit mixed-effects ANOVA model
  - Compute accuracy, power, metrics per §8–9
  - Sensitivity analysis: vary GLI weights ±25%, recompute accuracy (robustness check)
  - Produce figures: accuracy by budget and depth, ROC curves, variance components

---

## 12. Justification of Design Choices via Evidence

| Design Choice | Evidence | Rationale |
|---|---|---|
| Trajectory inspection depth ablation | 2609.00038 | Outcome-only judges miss 55% of silent faults; step-rubric reaches 77% |
| Hidden-target scoring (GLI computed post-hoc) | 2606.07591 | Prevents agents from gaming the rubric metric itself |
| Paired budget regimes (STRICT/MODERATE/PERMISSIVE) | 2608.01913 | Enables step-wise diagnosis of when gaming becomes dominant strategy |
| Variance components framework | 2607.13304 | Generalizability theory efficiently allocates 12 replicates across factors |
| Query correlation & utilization gaps | 2608.01913, 2607.09195 | Separates legitimate refinement (use results) from gaming (discard) |
| Class A vs. Class B stratification | 2606.07591 | Controls for problem difficulty independent of strategy effects |
| Early stopping on variance explained <5% | — | Practical boundary to avoid wasting compute on null signal |
| Thresholds set on pilot data | 2010.06595 | Prevents overfitting classification rule to training set |

---

## 13. Limitations & Open Questions

1. **Effect Size Unknown**: 
   Design assumes gaming agents produce visibly different eval trajectories.
   If effect size is small (<0.3 Cohen's d), 12 replicates may be underpowered. 
   Pilot data will clarify (2010.06595).

2. **Agent Sophistication**: 
   Test agents are relatively simple (hill-climbing, random, GP). 
   A sophisticated agent might masquerade as a solver.
   AdaptiveExplorer is a partial test; more research needed on adversarial agents.

3. **Generalization Across Problem Domains**: 
   16 problems are a sample; effect of budget regime may vary by problem type.
   Stratification into Class A vs. B is coarse.

4. **Overhead of Logging**: 
   Trajectory logging adds compute cost.
   Design does not budget for logging overhead explicitly; treat as sensitivity analysis.

5. **Threshold Calibration**: 
   GLI thresholds set on pilot data may not generalize. 
   Production use would require cross-validation or held-out calibration set.

---

## 14. Data Deliverables

Upon completion, produce:

1. **Trial results table** (192 rows):
   - trial_id, problem_id, agent_id, budget_regime, class, 
     coarse_accuracy, detailed_accuracy, gli_score, final_score, 
     corr_score, util_gap, reuse_count, total_evals_used, duration_sec

2. **Query logs** (up to 960K rows):
   - trial_id, query_sequence_number, solution_repr, score, timestamp

3. **Mixed-effects model output**:
   - ANOVA table (F-statistics, p-values, effect sizes)
   - Variance component estimates
   - 95% CI on all metrics

4. **Figures**:
   - Accuracy by Budget × Inspection Depth (bar chart with error bars)
   - ROC curves (COARSE vs. DETAILED)
   - Variance component pie chart
   - Agent trajectory examples (heatmap of scores over eval sequence per agent)

---

## 15. Research Question Interpretation & Conclusion Pathway

**Research Question**: "How should a benchmark stop an optimizing agent from buying its score 
with unlimited evaluations?"

**Answer Pathway**: 

1. If Acc_DETAILED > 80% and Delta_Power > 15 pts, 
   conclude: **Trajectory inspection + budget metering is sufficient**.
   Recommendation: Implement hidden-target rubric + eval logging in benchmark.

2. If Acc_DETAILED ≈ Acc_COARSE (no gain), 
   conclude: **Trajectory inspection alone is insufficient**. 
   Recommendation: Explore alternative mechanisms (commitment phases, gradient masking, etc.).

3. If Acc_DETAILED > 80% but Delta_Power small, 
   conclude: **Trajectory inspection helps, but effect is modest**. 
   Recommendation: Combine with additional safeguards (eval cost penalties, commit-before-eval).

---

## 16. References (Evidence Pack Excerpts)

- **2010.06595**: "With Little Power Comes Great Responsibility" 
  (power analysis norms for NLP; used for effect-size interpretation)

- **2605.30315**: "Resolution Diagnostics for Paired LLM Evaluation" 
  (paired testing resolution; justifies power computation methodology)

- **2606.07591**: "ResearchClawBench" 
  (hidden-target task packaging, re-discovery threshold, problem diversity; 
  CORE EVIDENCE for rubric design and problem stratification)

- **2607.09195**: "Hypothesis Evolution Protocol" 
  (auditable hypothesis-test-evidence cycle; 
  CORE EVIDENCE for detecting circular reasoning / query reuse)

- **2607.13304**: "Where Does the Noise Come From? A Variance-Components Decomposition" 
  (generalizability theory, crossed designs, variance allocation; 
  CORE EVIDENCE for sample sizing and ablation structure)

- **2608.01913**: "Diagnosing Search Behavior in Long-Horizon Agents" 
  (retrieval vs. utilization gap diagnosis; 
  CORE EVIDENCE for step-wise trajectory analysis and GLI components)

- **2608.03501**: "Can LLM design high-quality experiments? SCOPE Benchmark" 
  (stage isolation: planning vs. configuration; supports separating budget decisions from task framing)

- **2609.00038**: "trajectory-judge" 
  (outcome-only vs. step-rubric; 45% vs 77% recall on silent faults; 
  CORE EVIDENCE for ablation hypothesis and trajectory inspection value)

---

**Design Status**: Ready for pilot. 
**Estimated Runtime**: 14 days (pilot + main + analysis).
**Sample Size Justification**: 12 trials per cell per 2607.13304; pilot will confirm adequacy.
