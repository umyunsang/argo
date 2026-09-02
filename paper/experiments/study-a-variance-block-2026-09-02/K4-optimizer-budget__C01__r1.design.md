# Experimental Design: K4 Optimizer Budget Control

## Research Question

How should a benchmark stop an optimizing agent from buying its score with unlimited evaluations of the target?

**Problem Context**: When an agent can repeatedly call a target evaluation function (learning signal), it can trivially improve its reported performance by pure memorization or curve-fitting, decoupled from genuine capability improvement. A benchmark must budget evaluation calls such that: (a) the agent cannot achieve high scores through brute-force optimization, (b) meaningful performance differences on held-out data reflect real generalization, and (c) the distinction between target-set overfitting and held-out improvement is statistically detectable.

---

## Main Comparison: Evaluation Budget Regimes

### Condition A: Unlimited Target Evaluation (Baseline)
- Agent receives **unbounded access** to target-set evaluation calls
- No penalty for excessive queries
- Represents the pathological case where the agent can memorize the target set

### Condition B: Metered Evaluation (K=100 calls)
- Agent receives **exactly 100 evaluations** of target set
- Evaluated via a call counter; reaching limit stops all further queries
- Represents a conservative, resource-limited regime

### Condition C: Metered + Complexity-Weighted (K-adaptive)
- Agent receives **budget of 100 weighted evaluations**, where weight depends on query complexity
- Simple queries (e.g., single-sample gradient checks) cost 0.5 budget units
- Complex queries (e.g., bootstrap validation, ensemble evals) cost 2.0 budget units
- Implements adaptive allocation following Jeong et al. (2403.14403): *Adaptive-RAG learns to adapt retrieval-augmented LLMs through question complexity*
- Allows smarter agents to get more effective evaluations within the same total budget

### Condition D: Metered + Trajectory Audit (K=100 + audit)
- Agent gets K=100 evaluations as in Condition B
- **Additionally**: offline audit of the agent's trajectory following Liu et al. (2608.01913)
  - Classify each evaluation call as: exploratory, hypothesis-testing, or verification
  - Measure evidence-saturation: does new evaluation reveal new information?
  - Detect utilization gaps: is the agent using returned signals or simply calling repeatedly?
- Audit feeds into interpretation of results but does not gate the experiment

---

## Ablations

### Ablation 1: Evaluation Queue Opacity
- **Sub-condition B-opaque**: Agent receives budget K=100 but does NOT know remaining budget
  - Cannot strategically save calls
  - Tests whether budget awareness matters for behavior
- **Sub-condition B-transparent**: Agent receives budget K=100 and sees running tally
  - Can plan evaluation sequence knowing the limit
  
**Hypothesis**: Transparent budgets lead to more focused, less wasteful evaluation strategies, and higher held-out performance for the same K (evidence from Asai et al. 2310.11511: agents with explicit reflection tokens achieve better calibration).

### Ablation 2: Held-Out Test Set Informativeness
- **Sub-condition (weak test)**: Held-out test is drawn from the same distribution as target, but only N=100 prompts
  - Low statistical resolution per Kotawala (2605.30315): paired resolution ratio q = N/N* will be <1
  - May not reliably distinguish genuine improvement from noise
- **Sub-condition (strong test)**: Held-out test is N=500 prompts, same distribution
  - Higher resolution; follows Kotawala's recommendation for (α, 1−β) = (0.05, 0.8)
  
**Hypothesis**: Weak test will show high variance across runs; strong test will show clearer separation between budget conditions if the difference is real.

### Ablation 3: Evaluation Rubric Stability
- **Sub-condition (unstable judge)**: Scoring is performed by an LLM judge (e.g., Claude), which may drift across invocations
  - Each target-set evaluation uses a fresh judge call
  - Introduces judge drift and severity variance (Sunkavalli 2608.29517)
- **Sub-condition (stable rubric)**: Scoring is computed by a deterministic, rule-based rubric with no model variance
  - All evaluations use the same fixed logic
  
**Hypothesis**: Judge drift adds noise that can hide true differences and may reward agents for exploiting judge inconsistency. Stable rubric will show clearer budget-regime separation.

---

## Study Conditions (Factorial Snapshot)

```
Main Comparison (Conditions A–D): 4 levels
├─ Ablation 1 (Budget Transparency): 2 levels (B-opaque, B-transparent)
├─ Ablation 2 (Test Informativeness): 2 levels (weak N=100, strong N=500)
└─ Ablation 3 (Judge Stability): 2 levels (unstable LLM judge, stable rule-based)

Total unique configurations:
- Conditions A, C, D + Condition B split into B-opaque and B-transparent = 5 main branches
- Each tested under (2 test sizes) × (2 judge types) = 4 variants
- Partial factorial: prioritize (B-opaque vs transparent) and (judge stability) for main comparison
- Full factorial on strong-test subset only (to save budget)

Primary design: Main Comparison A–D × Judge Stability (8 cells)
Secondary design (strong test only): A–D × Transparency × Judge (8 cells, for B-variants)
```

---

## Experimental Procedure

### Setup and Task

1. **Target domain**: Open-ended optimization task (e.g., neural architecture search, hyperparameter tuning, prompt engineering)
   - Must have a well-defined evaluation function: target_eval(solution) → score ∈ [0, 100]
   - Must have a distribution of held-out test cases
   
2. **Agents**:
   - Replicate ≥2 distinct agent architectures (e.g., Claude-based, LLaMA-based) to avoid single-model confounds
   - Each agent runs the same optimization task across all conditions
   - All agents use identical tools: the evaluation function and a solution-generation model

3. **Randomization**:
   - Randomize: agent architecture, condition order, random seed for solution initialization
   - Stratify by condition to ensure balanced replication (see sample size section)

### Execution Protocol (per agent–condition pair)

1. **Phase 1: Optimization (fixed wall-clock time or step limit)**
   - Agent proposes solutions iteratively
   - Each solution proposal triggers an evaluation call (consumes budget in metered conditions)
   - Agent receives score and can update its model
   - Phase ends when: (a) budget exhausted, (b) time limit reached, or (c) agent-declared convergence
   - **Log all evaluation calls** with:
     - Input (solution description)
     - Output (score)
     - Timestamp
     - Agent-provided reasoning (hypothesis, why this evaluation was chosen)

2. **Phase 2: Trajectory Audit (offline)**
   - Extract trajectory of all evaluation calls
   - For each call, classify:
     - Query type: hypothesis-testing, verification, or exploratory (following Takahara & Mizoguchi 2607.09195)
     - Information gain: does returned score update agent's belief significantly? (measure via KL divergence between prior and posterior model state, or simpler: "first observation of this solution class?")
     - Redundancy: is this call similar to prior calls? (measure via embedding distance in solution space)
   - Compute trajectory metrics:
     - Total calls N_eval
     - Cumulative information gain (sum of info gains per call)
     - Redundancy ratio (fraction of calls in redundant clusters)
     - Call rate decay (do calls cluster early or spread throughout?)

3. **Phase 3: Held-Out Evaluation**
   - Freeze agent's final solution (from Phase 1)
   - Evaluate on held-out test set (N=100 or N=500, depending on variant)
   - Scoring uses same rubric as Phase 1 evaluations
   - **If judge is LLM (unstable)**: use a fixed model version for entire run; re-score a calibration anchor set (30 examples) at the end to detect drift

4. **Phase 4: Test-Set Informativeness Check**
   - To validate Ablation 2's hypothesis, measure resolution of held-out test:
     - Fit a paired bootstrap to target-set scores vs. test-set scores per agent
     - Compute resolution ratio q = N_test / N*(delta_obs) (Kotawala 2605.30315)
     - q >= 1 → resolvable; q < 1 → underpowered
   - Document q for each condition

---

## Outcome Metrics

### Primary Metrics (per agent–condition)

1. **Held-Out Performance**: mean score on test set (averaged over multiple runs with different random seeds)
   - **Interpretation**: Does the agent generalize beyond the target set? Unlimited budget should show highest test score if memorization works best.

2. **Target-Set Inflation**: 
   - target_score_on_holdout_set / test_set_score
   - Measures overfitting ratio
   - **Interpretation**: High inflation → heavy memorization; ratio ~1 → genuine improvement

3. **Efficiency Ratio**:
   - (test_set_score - baseline_score) / N_eval
   - Performance gain per evaluation call
   - **Interpretation**: Metered conditions should show higher efficiency if budget discipline forces smarter search

4. **Information Density** (from trajectory audit):
   - cumulative_info_gain / N_eval
   - **Interpretation**: Do metered agents learn to choose higher-signal evaluations?

### Secondary Metrics (for interpretation)

5. **Budget Saturation Curve**:
   - Plot held-out score vs. N_eval (capped at 100 for Condition B)
   - Fit a power-law or log model: score ~ log(N_eval)
   - **Interpretation**: Asymptotic behavior tells us if marginal gains diminish sharply or linger

6. **Call Clustering**:
   - Fraction of evaluations in first 50% of run duration
   - **Interpretation**: Do agents hoard information early or spread queries?

7. **Judge Agreement** (if judge is LLM):
   - Pearson r between two independent judge runs on same solution set
   - **Interpretation**: Low agreement indicates judge drift; high agreement validates stability ablation

---

## Analysis Plan

### Hypothesis 1: Budget Prevents Overfitting
**Prediction**: 
- Condition A (unlimited) shows highest target-set score but lowest generalization (high inflation ratio)
- Conditions B, C, D show lower target-set scores but higher (or equal) test-set scores
- **Test**: ANOVA on test-set score across Conditions A–D; pairwise t-tests (Bonferroni-corrected, α=0.05)
- **Effect size**: Report Cohen's d for A vs. B, C, D

### Hypothesis 2: Transparency Aids Efficient Search (Ablation 1)
**Prediction**:
- B-transparent > B-opaque on both test score and efficiency ratio
- **Test**: Paired t-test within Condition B: transparent vs. opaque; block by judge type
- **Effect size**: Cohen's d

### Hypothesis 3: Complexity Weighting Outperforms Fixed Budget (Condition C vs. B)
**Prediction**:
- Condition C achieves higher test score than Condition B despite same total budget
- Trajectory audit of C shows lower redundancy ratio than B
- **Test**: t-test C vs. B on test score and redundancy; may not reach significance if budget efficiency is small
- **Caveat**: This tests whether adaptive weighting is *feasible*; may require larger N or longer runs to show meaningful edge

### Hypothesis 4: Trajectory Audit Reveals Overfitting Signature (Condition D adds clarity)
**Prediction**:
- Condition D audit detects higher utilization gaps in unlimited (A) vs. metered (B, C, D)
- Audit metrics (info density, call clustering) correlate with test-set score across all conditions
- **Test**: Spearman correlation of trajectory metrics (info density, clustering) with test score; block by condition
- **Effect size**: Spearman ρ

### Hypothesis 5: Judge Drift Obscures Condition Differences
**Prediction**:
- Unstable-judge variant shows larger variance in results and weaker separation between conditions A–D
- Stable-rubric variant shows sharper separation
- **Test**: Levene's test for equal variances across conditions; Report SD of test scores under each judge type

### Hypothesis 6: Weak Test Lacks Resolution (Ablation 2)
**Prediction**:
- N=100 test: resolution ratio q < 1 for most pairs; high variance in test scores
- N=500 test: resolution ratio q >= 1; lower variance, clearer trends
- **Test**: Report q values; plot bootstrap CI width for N=100 vs. N=500

---

## Concrete Resources & Materialization

### Task and Datasets

**Recommended task**: Prompt optimization for a fixed QA task (e.g., MMLU or a held-out generalization benchmark)
- **Existing resource**: Use MMLU-Pro (Huang et al. 2024) as the domain
  - Target set: 100 example prompts from a held-out MMLU subject (e.g., college physics)
  - Agent's goal: refine a system prompt to maximize accuracy on this domain
  - Test set: 500 prompts from a different subject (e.g., college chemistry)
  - Evaluation function: eval(candidate_prompt, example_set) = fraction of test queries answered correctly
  
**Alternative resource**: Use BrowseComp (Liu et al., cited in 2608.01913) for multi-step search optimization
- Fixed corpus, human qrels, deterministic feedback
- Cited as a controlled environment in Liu et al. 2608.01913: *Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents*

### Agents

**Requirement**: ≥2 distinct agent architectures
- Agent 1: Claude-based (e.g., Claude-3-Opus with tool use)
- Agent 2: Open-weights model (e.g., Qwen-3.5-35B with same tool interface)
- Both agents run under identical conditions; replicate each agent × condition combination ≥5 times with different random seeds

### Judge/Rubric

**Stable rubric**: For MMLU prompt optimization, use exact-match accuracy on a fixed reference answer key. No LLM judge.

**Unstable judge** (for ablation): Have an LLM (e.g., Claude) score subjective response quality on a rubric. Invoke once per evaluation in Phase 1. In Phase 4, re-invoke on anchor set to measure drift.

### Evaluation Infrastructure

- **Evaluation counter**: Track all calls; halt condition B/C/D when budget exhausted
- **Trajectory logger**: Record each call with timestamp, input, output, agent state
- **Call-classifier tool**: Rule-based (or fine-tuned on label examples) classifier to tag call type and compute info gain
  - Cite: Takahara & Mizoguchi 2607.09195 for hypothesis-testing taxonomy
  
### Computational Budget

- Agent runs: 2 architectures × 5 conditions × 2 ablation-2 levels × 2 ablation-3 levels × 5 random seeds
  - Partial factorial (prioritize judge stability for main Conditions A–D, add transparency for Condition B only, and only on strong test)
  - Minimum: 2 agents × 5 conditions × 2 judge types × 5 seeds = **100 runs**
  - Each run: ~1–2 hours (depending on task complexity and phase length)
  - Total: ~100–200 GPU/CPU hours or ~50–100 wall-clock hours on parallel infrastructure

### Analysis Tools

- **Power analysis**: Use llm-power package (Kotawala 2605.30315) to compute resolution ratio q for paired differences
- **Variance components**: Use generalizability-theory decomposition (Zatuchin 2607.13304) to partition variance across agent, random seed, and condition
- **Trajectory audit**: Custom script following Liu et al. 2608.01913 to score trajectories on retrieval gaps, utilization gaps, and information density
- **Multiple comparison correction**: Bonferroni or Holm–Bonferroni for pairwise tests

---

## Quantifying Uncertainty

### Uncertainty Sources & Mitigation

1. **Random seed variance**
   - **Source**: Stochastic optimization; different random initializations lead to different trajectories
   - **Mitigation**: Run each agent–condition ≥5 times with distinct seeds; report mean ± SD and 95% bootstrap CI
   - **Analysis**: Multilevel model with random intercepts per seed and per agent architecture

2. **Judge drift** (if LLM judge used)
   - **Source**: LLM responses vary across invocations and model versions
   - **Mitigation**: Pin model version; re-score anchor set in Phase 4 to quantify drift; report judge agreement (intraclass correlation)
   - **Analysis**: Following Sunkavalli 2608.29517, pre-register anchor-set check; if drift detected, reweight scores or report results separately

3. **Held-out test variance**
   - **Source**: Finite test set; results depend on which test examples are chosen
   - **Mitigation**: Ensure test set is large (N=500 for main analysis) and representative; use resampling to compute bootstrap CI
   - **Analysis**: Report 95% bootstrap CI on test score; if CI is wide, flag as low-resolution test (q < 1)

4. **Trajectory-audit coding uncertainty**
   - **Source**: Manual/algorithmic classification of evaluation types and info gain may be imperfect
   - **Mitigation**: Use rule-based classifier trained/validated on hand-labeled subset; measure inter-rater agreement if humans label a sample
   - **Analysis**: Report classifier accuracy; sensitivity analysis on audit thresholds

### Planned Comparisons and Confidence Intervals

- **Primary contrasts** (A–D × judge type):
  - Report 95% bootstrap CI on held-out score, inflation ratio, efficiency ratio
  - Test for difference using t-test; report t-statistic, p-value, Cohen's d
  
- **Secondary contrasts** (transparency, test size):
  - Use Bonferroni correction: α = 0.05 / (number of contrasts)
  - Report 95% CI; may have wider intervals due to smaller subsample sizes
  
- **Trajectory audit correlations**:
  - Report Spearman ρ with 95% CI; flag if CI contains 0

---

## Potential Failure Modes & Escape Clauses

### If Condition A (Unlimited Budget) Does Not Memorize
- **Issue**: Assumption that unlimited evaluations enable high target-set scores may be false if the optimization problem is hard
- **Escape**: Lower task difficulty (simpler prompt, smaller solution space) or allow longer Phase 1 (relax wall-clock time limit)
- **Re-test Hypothesis 1** with adjusted task

### If Conditions B and C Show No Difference
- **Issue**: Complexity weighting may not provide an advantage for this task/agent pair
- **Escape**: Hypothesis 3 is falsified; report as null result. Qualitative finding: *adaptive complexity weighting is infeasible or ineffectual for prompt optimization*
- **Interpretation**: K=100 is sufficient; optimization scales sub-linearly with budget by design

### If Judge Drift Swamps All Differences
- **Issue**: LLM judge unstable enough that condition means have overlapping 95% CIs
- **Escape**: Revert to stable rule-based rubric (Ablation 3, stable variant only); report results under deterministic scoring
- **Caveat**: Limits generalization to subjective evaluation tasks

### If Held-Out Test Has Resolution q < 1
- **Issue**: N=100 or N=500 test set is too small; differences cannot be resolved from noise
- **Escape**: Increase test set size to N=1000 or use meta-analysis across multiple held-out sets (e.g., different MMLU subjects)
- **Note**: Must be pre-registered or reported as post-hoc sensitivity analysis

---

## Expected Output & Dissemination

### Deliverables

1. **Main results paper**:
   - Figure 1: Mean held-out score (± 95% CI) across Conditions A–D, stratified by judge type
   - Figure 2: Overfitting inflation ratio vs. budget (Condition A vs. B/C/D)
   - Figure 3: Efficiency ratio and trajectory-audit metrics (info density, clustering)
   - Table 1: Full results matrix (all conditions, all metrics, all agents)
   - Table 2: Power analysis (resolution ratio q for all key contrasts)

2. **Analysis artifacts**:
   - Trajectory audit logs (per run)
   - Trajectory classifier code and validation metrics
   - Bootstrap resampling code and CI estimates
   - Judge drift detection results (if applicable)

3. **Reproducibility**:
   - Full code for experiment (Phase 1–4), analysis, and figures
   - Exact agent prompts and tool definitions
   - Hyperparameters for all models and runs
   - Random seed list for replication

---

## Citations to Evidence Pack

This design is grounded in the following excerpts from the evidence directory:

- **2010.06595**: Statistical power norms; justifies need for pre-registered power analysis
- **2310.11511**: On-demand retrieval with self-critique (Asai et al. Self-RAG); supports reflection-token idea for trajectory audit
- **2403.14403**: Complexity-conditioned retrieval routing (Adaptive-RAG); motivates Condition C (complexity weighting)
- **2605.30315**: Paired resolution targets and MDE (Kotawala); provides resolution ratio q for test-set sizing
- **2608.01913**: Retrieval vs. utilization gaps in search agents (Liu et al.); framework for trajectory audit (Condition D)
- **2608.03501**: Stage isolation and redline scoring in experimental design (Liu et al.); supports Phase separation (setup, optimization, audit, held-out)
- **2608.29517**: Judge severity, halo, and drift (Sunkavalli); motivates Ablation 3 (stable vs. unstable judge)
- **2609.00038**: Outcome-only judging blind spots (Mohammadi trajectory-judge); supports trajectory-level evaluation beyond final score

---

## Design Rationale Summary

**Core Logic**:
1. **Main Comparison (A–D)** isolates the effect of budget constraints and audit on overfitting, answering the research question directly.
2. **Ablation 1 (Transparency)** tests whether agents need budget awareness to optimize effectively.
3. **Ablation 2 (Test Size)** validates that resolution is sufficient to detect real differences (avoids false negatives).
4. **Ablation 3 (Judge Stability)** isolates the noise floor introduced by evaluation itself.
5. **Trajectory Audit (Condition D & ablation)** provides a mechanistic window into whether agents are genuinely improving or just curve-fitting.

**Why This Answers the Question**:
- If unlimited evaluation (A) yields high target scores but *low* test scores, and metered conditions (B/C/D) yield lower target but *higher* test scores, then budgeting is effective.
- If target and test scores diverge, trajectory audit (D) reveals *why*: overfitting signature (many redundant calls, low info gain) vs. genuine improvement (early evidence discovery, stable performance).
- If complexity weighting (C) outperforms fixed budget (B), then adaptive allocation is feasible for benchmarks.
- If stable judge makes differences clear but unstable judge obscures them, then rubric design is critical.

This design produces both an answer (budget constraints work / don't work) and a principled framework for designing evaluation budgets in future agent benchmarks.
