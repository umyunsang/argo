# Experimental Design: K2-Harness-vs-Model

## Research Question
How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

## Hypothesis
A harness optimization loop produces measurable performance gains on a held-out evaluation set that exceed the gains from prompt engineering alone, and these gains are attributable to harness structure rather than better prompting.

---

## Main Experimental Comparison

### Three Core Conditions

1. **Baseline Control (BC)**: Original harness + Original prompt
   - Baseline model receives the original harness configuration and original prompt template
   - All other variables held constant

2. **Harness-Optimized (HO)**: Self-improved harness + Original prompt
   - Model receives the same original prompt template
   - Harness has been iteratively optimized (skills, tools, rules, memory structure, etc.)
   - Harness snapshots are used; scoring occurs outside the candidate workspace

3. **Prompt-Optimized (PO)**: Original harness + Improved prompt
   - Harness structure unchanged from baseline
   - Prompt has been independently improved through standard prompt engineering
   - Controls for the "better prompt explains all gains" alternative hypothesis

### Design Rationale

- **BC vs HO**: Tests whether harness self-improvement produces gains
- **HO vs PO**: Tests whether harness improvement outperforms prompt improvement
- **BC vs PO**: Baseline measure of prompt-engineering effectiveness
- Separating harness and prompt changes allows causal attribution

---

## Ablation Study: Negative Control

### Condition: Random Harness Perturbation (RHP)
- Take the original harness and apply random modifications (e.g., shuffle skill ordering, randomly disable some tools, randomize rule text)
- Keep the original prompt
- If harness improvement is real, BC and RHP should show no significant difference
- If random changes hurt performance, this validates that harness structure matters at all
- If random changes help, the evaluation set may be too easy or the model too robust

---

## Concrete Resources

### Evaluation Set
- **Name**: K2 held-out evaluation dataset
- **Source**: Pre-constructed, exists in project directory
- **Characteristics**: 
  - Size must be sufficient for statistical significance (propose minimum n=100 test cases)
  - Constructed before any harness optimization begins (pre-registered to prevent overfitting to specific test cases)
  - Representative of the task domain that the system is optimizing for

### Harness Snapshots
- **Original Harness (BC, PO, RHP)**: Baseline version prior to self-optimization
  - Stored at: `./harness/baseline/`
  - Contains: skills, tools, rules, memory entries, prompts, MCP server definitions, hooks
  
- **Self-Optimized Harness (HO)**: Result of iterative harness improvement
  - Stored at: `./harness/optimized/`
  - All versions must be snapshot-immutable during evaluation
  - Optimization history logged separately (not evaluated)

- **Random Perturbation Harness (RHP)**: Procedurally generated from baseline
  - Stored at: `./harness/random_perturb/`
  - Random seed recorded for reproducibility

### Prompt Templates
- **Original Prompt (BC, HO, RHP)**: Baseline task prompt
  - Stored at: `./prompts/original.txt`
  
- **Improved Prompt (PO)**: Prompt independently optimized (via prompt engineering best practices, not via harness feedback)
  - Stored at: `./prompts/improved.txt`
  - Optimization should be orthogonal to harness changes (use a separate prompt-only optimization pass)

### Model Configuration
- **Model**: Claude 3.5 Sonnet (or specify exact model identifier)
- **Temperature/sampling**: Fixed across all conditions (propose temperature=0 for determinism, or 1.0 with seed for reproducibility)
- **Context window**: Specified and consistent

### Scoring Environment
- **Location**: External harness-free evaluation runner
  - Must not execute within candidate harness workspace
  - Prevents harness side effects (hooks, memory mutations, etc.) from affecting scoring
  - Proposal: `./eval/external_scorer.py` — standalone Python script that loads harness snapshots, invokes model with fixed prompts, and records raw outputs
  
- **Metrics computed**: see Outcome Metrics section

---

## Outcome Metrics

### Primary Metric: Task Success Rate
- **Definition**: Proportion of test cases where model output satisfies task success criterion
- **Computation**: Count correct outputs / total test cases
- **Unit**: Percentage (0–100%)

### Secondary Metrics

1. **Latency per test case**
   - Measures harness overhead (tool lookup, rule execution, memory access)
   - If HO reduces latency, harness optimization made things faster
   - If HO increases latency but improves accuracy, trade-off is explicit

2. **Token efficiency**
   - Total tokens used per test case (input + output)
   - Harness improvements may reduce verbosity or redundant context

3. **Consistency score**
   - Variance in performance across test cases within each condition
   - Lower variance suggests harness improvements are robust

---

## Analysis Plan

### 1. Descriptive Statistics
- Report mean, standard deviation, median, min, max for each metric × condition
- Visualize distributions (histograms or box plots)

### 2. Hypothesis Tests
- **Comparison BC vs HO**: One-tailed test (HO ≥ BC)
  - Null: Harness optimization provides no benefit
  - Test: Welch's t-test (unequal variance) or Mann-Whitney U (non-parametric alternative)
  
- **Comparison HO vs PO**: Two-tailed test (HO ≠ PO)
  - Null: Harness and prompt improvements are equivalent
  - Test: Welch's t-test
  
- **Comparison BC vs RHP**: Two-tailed test (BC ≈ RHP)
  - Null: Random harness changes have no effect
  - Test: Welch's t-test; expect p > 0.05 (fails to reject null)

### 3. Effect Size
- Report Cohen's d (standardized difference) for all pairwise comparisons
- Interpret: small (0.2), medium (0.5), large (0.8)

### 4. Confidence Intervals
- 95% CI on mean success rate for each condition (binomial CI, e.g., Clopper-Pearson)
- 95% CI on difference in means (BC vs HO, HO vs PO)

### 5. Robustness Checks
- **Bootstrap resampling**: Resample test cases with replacement, recompute metrics
  - Report 95% CI on bootstrap estimate of mean difference
- **Leave-one-group-out**: Remove one "category" of test cases, recompute to check whether gains are domain-specific
  - (Requires categorized evaluation set; if not available, note as limitation)

---

## Quantifying Uncertainty

### 1. Statistical Error
- **α (Type I error)**: Set to 0.05 for all hypothesis tests
- **Power analysis**: For a medium effect size (d=0.5), minimum sample size for 80% power
  - For proportions: use power.prop.test or equivalent
  - Current evaluation set size must be checked against power calculation
  
### 2. Confidence Intervals
- All point estimates accompanied by 95% CIs
- Overlapping CIs between conditions indicate insufficient evidence for difference

### 3. Multiple Comparisons
- Three main pairwise comparisons (BC-HO, HO-PO, BC-RHP)
- Apply Bonferroni correction: α_adj = 0.05/3 ≈ 0.017
  - Or report uncorrected p-values and note multiple comparisons

### 4. Measurement Error / Task Ambiguity
- If task scoring is subjective, estimate inter-rater reliability
  - Proposal: have a second rater score a random subset (e.g., 10–20%) of outputs
  - Compute Cohen's κ (agreement)
  - Propagate uncertainty into final metric CIs

### 5. Model Randomness
- If model temperature > 0, run each condition multiple times
  - Proposal: 3–5 independent runs per condition
  - Report mean and SD across runs

### 6. Finite Evaluation Set
- Held-out test set is fixed and finite
- Uncertainty in performance estimates stems from test set sampling variability
- Report this via binomial CIs (not asymptotic normal)

---

## Concrete Workflow

1. **Initialization**
   - Confirm evaluation set exists and is locked (hash recorded)
   - Confirm all three harness snapshots are ready and immutable
   - Confirm original and improved prompt templates are ready

2. **Condition 1: Baseline Control (BC)**
   - Load original harness snapshot
   - Load original prompt
   - Invoke model on all n test cases
   - Record: success/fail, latency, tokens, raw output

3. **Condition 2: Harness-Optimized (HO)**
   - Load optimized harness snapshot
   - Load original prompt (unchanged)
   - Invoke model on all n test cases (same test set as BC)
   - Record metrics

4. **Condition 3: Prompt-Optimized (PO)**
   - Load original harness snapshot
   - Load improved prompt
   - Invoke model on all n test cases (same test set as BC)
   - Record metrics

5. **Condition 4: Random Perturbation (RHP)**
   - Load random perturbation harness snapshot
   - Load original prompt
   - Invoke model on all n test cases (same test set as BC)
   - Record metrics

6. **Analysis**
   - Compute descriptive statistics for each condition
   - Run hypothesis tests (BC-HO, HO-PO, BC-RHP)
   - Compute effect sizes and confidence intervals
   - Perform robustness checks (bootstrap, LOGO, inter-rater if applicable)
   - Summarize findings with uncertainty quantification

7. **Reporting**
   - Present means and CIs for each condition
   - Report test statistics, p-values, and effect sizes
   - Visualize comparisons (bar plots with error bars or forest plots)
   - Discuss whether harness improvements exceed prompt improvements
   - Acknowledge limitations (finite test set, potential model-specific effects, etc.)

---

## Justification and Limitations

### Justification
- **Why three conditions?** Separating harness and prompt isolates the causal effect of harness improvement. PO is necessary to establish that prompt engineering alone is not responsible for any gains in HO.
- **Why a random perturbation ablation?** Validates that the evaluation framework is sensitive (random changes should not help), and that harness structure matters.
- **Why external scoring?** Prevents harness-internal side effects (hooks, state mutations) from contaminating the evaluation.
- **Why binomial CIs?** Task success is a binary outcome; binomial confidence intervals are appropriate.
- **Why Bonferroni correction?** Three comparisons increase the family-wise error rate; correction maintains overall α = 0.05.

### Limitations & Future Work
1. **Evaluation set size**: If the held-out set is small (n < 50), statistical power is limited. Recommendation: conduct a power analysis before starting.
2. **Model-specific effects**: Improvements may not generalize to other models. Repeating the experiment with a different model would strengthen claims.
3. **Harness complexity**: If the optimized harness is substantially more complex, any performance gain may be confounded with complexity. Consider reporting a harness complexity metric (e.g., number of skills, rules, memory entries) to audit this.
4. **Prompt engineering baseline**: The "improved prompt" in condition PO should be optimized in a way that is truly orthogonal to harness work. If the same agent/human did both, implicit coupling may exist.
5. **Evaluation set representativeness**: Gains on the held-out set may not reflect real-world task diversity. Evaluate on multiple task categories if possible.

---

## Expected Outcome Structure

The experiment will produce:
- A table of results (mean ± 95% CI for each condition)
- Pairwise statistical tests with p-values and effect sizes
- A conclusion statement: "Harness self-improvement produced a [small/medium/large] effect (d=X) on task success rate compared to baseline (p=Y), exceeding the gain from prompt engineering alone (HO vs PO: d=Z, p=W)."
- Caveats on uncertainty, sample size, and generalization
