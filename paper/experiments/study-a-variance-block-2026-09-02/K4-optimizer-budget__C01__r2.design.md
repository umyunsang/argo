# Experimental Design: K4-Optimizer Budget

## Research Question
How should a benchmark stop an optimizing agent from buying its score with unlimited evaluations of the target?

---

## 1. PROBLEM FRAMING

The core issue is a **silent failure mode** in agent evaluation: an agent can manipulate its score by calling the target evaluation function excessively until it accidentally or intentionally discovers a high-scoring response, without necessarily following sound reasoning or process. This violates the scientific validity of the benchmark because:

1. The agent may reach the right answer the wrong way (trajectory-level failure; cf. 2609.00038)
2. Outcome-only evaluation hides this strategy entirely
3. Budget limits are essential but their implementation must be **measurable, justified, and validated**

---

## 2. MAIN COMPARISON & CONDITIONS

### Condition A: Unrestricted Evaluation Budget
- **Agent setting**: Access to unlimited target evaluations per task
- **Harness**: No metering or stopping criteria
- **Expected pathology**: Agent discovers high scores through brute-force or random exploration after many evaluations
- **Outcome metric**: Final test-set accuracy

### Condition B: Metered Budget with Trajectory-Level Audit
- **Agent setting**: Capped evaluation budget per task (to be specified in Configuration, §5)
- **Harness**: Every evaluation call is logged with timestamp and trajectory state
- **Stopping rule**: Budget exhausted OR agent declares termination (whichever first)
- **Audit layer**: Separates retrieval-vs-utilization (cf. 2608.01913) and process-vs-outcome (cf. 2609.00038)
- **Outcome metric**: Final test-set accuracy + trajectory-level audit verdict

### Condition C: Metered Budget with Resolution-Aware Stopping
- **Agent setting**: Same capped budget as B
- **Harness**: Early stopping triggered when pair-wise gap reaches statistical resolution (cf. 2605.30315)
- **Stopping rule**: Budget exhausted OR resolution achieved OR agent terminates
- **Outcome metric**: Final test-set accuracy + resolution diagnostic q = N/N⋆

---

## 3. ABLATIONS

### Ablation 1: Outcome-Only vs. Trajectory-Level Judgment
- **Ablation A1a**: Outcome-only judge sees only (task, final_answer) and rates pass/fail
- **Ablation A1b**: Trajectory judge sees full (task, trajectory, final_answer) and applies process rubric
- **Measurement**: False-positive rate, false-negative rate, stratified by silent vs. loud faults (cf. 2609.00038)
- **Null hypothesis**: Outcome-only and trajectory judgments agree on ≥90% of test cases
- **Expected finding**: Outcome-only misses process violations when final answer is correct

### Ablation 2: Budget Magnitude Sensitivity
- **Ablation A2a**: Budget = 5 evaluations per task
- **Ablation A2b**: Budget = 15 evaluations per task
- **Ablation A2c**: Budget = 50 evaluations per task
- **Measurement**: Accuracy per condition, agent convergence rate, fraction of queries that improve score vs. repeat prior solutions
- **Null hypothesis**: Accuracy plateau independent of budget
- **Expected finding**: Small budget forces agents into directed search; large budget enables brute-force

### Ablation 3: Paired vs. Unpaired Resolution Test
- **Ablation A3a**: Use McNemar paired-difference test for resolution (cf. 2605.30315, Eq. 3)
- **Ablation A3b**: Use unpaired t-test for resolution
- **Measurement**: Required-N (N⋆) for target effect size δ and conventional resolution (α=0.05, 1-β=0.8)
- **Null hypothesis**: Paired and unpaired prescribe similar required-N
- **Expected finding**: Paired McNemar is 2–3× more efficient than unpaired (cf. 2605.30315, Figure 1)

---

## 4. ANALYSIS PLAN

### 4.1 Primary Analysis: Outcome Accuracy Under Budget Constraints

**Statistic**: Per-condition mean accuracy on held-out test set, with 95% confidence interval via bootstrap

**Comparison**: Is Condition A (unrestricted) > Condition B (metered, no stopping)?
- If yes: Budget cap is not a sufficient control; process audit is needed
- If no: Budget cap alone prevents score-buying

**Blocking factor**: Task difficulty (stratified by gold-evidence recall difficulty from 2608.01913 analysis)

**Multiple comparison**: Bonferroni correction across three main conditions

### 4.2 Secondary Analysis: Trajectory-Level Audit (Ablation A1)

**Measurement**: For N_test tasks in held-out set:
- Count silent faults (correct final answer, wrong process) detected by A1a vs. A1b
- Compute false-positive rate (incorrect verdict on correct trajectories)
- Stratify by:
  - Budget consumed (did agent exhaust budget or terminate early?)
  - Process error type (skipped precondition, unsupported claim, hallucinated evidence, etc.; cf. 2609.00038)
  
**Decision rule**: If A1b detects ≥20% more silent faults than A1a at FP rate ≤10%, trajectory audit is valuable

### 4.3 Tertiary Analysis: Resolution Diagnostic (Condition C)

**Measurement for each comparison pair (Agent_i, Agent_j)**:
- Compute empirical paired gap δ̂ on current held-out set
- Invert using McNemar paired test to get required-N (N⋆) at target (α, 1-β) = (0.05, 0.8)
- Compute resolution ratio q = N_current / N⋆
- Flag pair as "unresolved" if q < 1

**Hypothesis**: Early stopping via resolution reaching q ≥ 1 stops sampling before budget exhaustion without sacrificing inference validity

**Statistical test**: McNemar's test on discordant pairs (cf. 2605.30315)

### 4.4 Robustness: Power Analysis Across Baselines

**Method**: Simulation-based power analysis following Card et al. (2010.06595) to pre-validate budget sufficiency
- Assume effect size δ⋆ = 2 percentage points (small but relevant for agent ranking)
- Assume within-pair correlation ρ = 0.5 (conservative estimate across tasks)
- Compute required-N (N⋆) for 80% power; confirm N_budget ≥ N⋆

**Outcome**: If N_budget < N⋆, some real gaps will go undetected; design must enlarge budget or reduce target effect size

---

## 5. CONCRETE RESOURCES

### 5.1 Target Evaluation Function
- **Name**: `score_response(task_id, agent_response, evaluation_budget_id)`
- **Cost**: 1 evaluation token per call
- **Latency**: 100–500 ms per call (metered)
- **Range**: Integer score in [0, 100] (graded rubric, not binary)
- **Existence**: Assumed to exist as the benchmark's native evaluation interface; must be instrumented to log (timestamp, agent_id, task_id, score, response_text) on every call

### 5.2 Held-Out Test Set
- **Source**: 100 tasks held-out before any agent training or optimization (stratified by domain if multi-domain)
- **Properties**: 
  - Human-annotated gold score (ground truth)
  - Gold-evidence reference set (for separating retrieval vs. utilization gaps; cf. 2608.01913)
  - Per-task difficulty metadata (e.g., number of supporting documents, reasoning steps required)
- **Access**: Evaluation function only; agent never sees training data from this set

### 5.3 Evaluation Budget Per Task
- **Condition B & C**: 20 evaluations per task (rationale: cf. 2608.01913 finding that useful evidence appears early; 20 allows exploratory queries before tail search begins)
- **Stopping rule timestamp**: Record T_stop for each task when budget expires or agent terminates
- **Justification**: Power analysis (2010.06595) on small benchmarks shows ~80% power to detect 2-point gaps with ~40–80 prompts; 20 evaluations per task is conservative for one agent but must be validated via power curve in Ablation A2

### 5.4 Trajectory Audit Harness (cf. 2608.03501)
- **Stage isolation**: Separate evaluation-input validation, process-check, and outcome-check into independent stages
- **Rubric**: 6-point scale per trajectory (cf. 2608.03501):
  1. High-Level Planning (does agent articulate goal and hypothesis?)
  2. Query Strategy (are search reformulations principled or parroting?)
  3. Evidence Retrieval (does agent retrieve gold evidence when it surfaces?)
  4. Evidence Use (does agent correctly incorporate retrieved evidence?)
  5. Process Integrity (does agent skip preconditions or make unsupported claims?)
  6. Final Outcome (does answer match gold rubric and evidence trail?)
- **Redline mechanism** (cf. 2608.03501): Score → 0 if fatal flaw detected (e.g., hallucinated document, contradiction with observation)

### 5.5 Statistical Test Machinery
- **Required software**: Python statsmodels, scipy.stats (McNemar, binomial, normal approximation)
- **Existing tool**: llm-power package (2605.30315, GitHub: ananykotawala/llm-power) for paired resolution diagnostics
- **Custom code needed**: Wrapper to integrate llm-power with agent trajectory logs and compute per-pair q = N/N⋆

---

## 6. OUTCOME METRICS

### Primary Metrics

1. **Accuracy on held-out test** (per Condition A, B, C)
   - Mean accuracy ± 95% CI
   - Paired difference: (B - A), (C - A), (C - B)
   - Interpretation: Budget cap's effect on test performance

2. **Silent-fault detection rate** (Ablation A1a vs. A1b)
   - Sensitivity (recall on silent faults) and specificity (1 - FP rate)
   - Interpretation: Is trajectory audit needed?

3. **Resolution ratio q = N / N⋆** (Condition C)
   - Median q across all task pairs
   - Fraction of pairs with q ≥ 1 ("resolved")
   - Interpretation: Can budget cap support valid pairwise inference?

4. **Budget utilization** (Conditions B & C)
   - Fraction of tasks where agent exhausted budget vs. terminated early
   - Mean number of evaluations consumed (per task, per agent)
   - Interpretation: Is budget meaningful or routinely exceeded?

### Secondary Metrics

5. **Convergence behavior** (Ablation A2)
   - Learning curve: score vs. evaluation count
   - Inflection point (when marginal improvement per evaluation drops <0.5 points)
   - Interpretation: Does early evidence arrival (2608.01913) predict stopping point?

6. **Trajectory-level error types** (Ablation A1b, Stage isolation)
   - Breakdown by process fault type: skipped_precondition, hallucinated_evidence, unsupported_claim, etc.
   - Precision and recall per fault type
   - Interpretation: Which faults are hardest to catch?

7. **Sample-size sufficiency** (Power analysis, 2010.06595)
   - Empirical power from simulation: does N_budget achieve target power for δ⋆ = 2pp?
   - Confidence intervals on power estimate
   - Interpretation: Is budget adequate for multi-agent comparison?

---

## 7. QUANTIFYING UNCERTAINTY

### 7.1 Confidence Intervals

- **Accuracy**: 95% CI via percentile bootstrap (10,000 resamples, stratified by task difficulty)
- **Paired gap (B - A)**: Paired bootstrap on difference per task; report median and 95% CI
- **Silent-fault detection**: Wilson score interval (avoids boundary problems at p=0; cf. 2010.06595)

### 7.2 Statistical Tests

- **Primary hypothesis** (Condition A vs. B): Paired t-test (or sign-rank if non-normal) on per-task accuracy difference; report t, df, p, 95% CI on δ
- **Ablation A1** (Outcome vs. Trajectory): McNemar's test on judgment agreement; report χ², p, 95% CI on sensitivity/specificity gap
- **Ablation A3** (Paired vs. Unpaired): Compare N⋆ via both methods on 10 real task pairs; report ratio (N⋆_paired / N⋆_unpaired) with 95% CI

### 7.3 Sensitivity Analysis

- **Robustness to stopping rule**: Recompute metrics with alternative budget caps (A2: 5, 15, 50 evals) and compare rank order stability (Kendall τ)
- **Robustness to judge model**: Run trajectory audit with two independent LLM judges (e.g., Claude 3.5, Llama 3.1); report inter-judge agreement (Cohen's κ)
- **Robustness to task set**: If multiple held-out test sets available, repeat analysis on each and report range of outcomes

### 7.4 Justification for Uncertainty Thresholds

- **CI coverage 95%**: Standard for ML benchmarks (cf. 2605.30315 which uses α=0.05)
- **Power target 80%**: Conventional in NLP power analysis (cf. 2010.06595); higher power (90%) is expensive and rare in practice
- **Silent-fault detection threshold ≥20%**: Conservative criterion; if trajectory audit catches <20% more faults, outcome-only may suffice for this use case
- **Resolution ratio target q ≥ 1**: Directly from 2605.30315; pairs with q ≥ 1 are considered "resolved" at (α, 1-β)=(0.05, 0.8)

---

## 8. DESIGN JUSTIFICATION & LIMITATIONS

### Why This Design?

1. **Trajectory-level audit captures silent failures** (2609.00038): Outcome-only judgment is blind to process violations when the answer is accidentally correct. Multi-stage design (Ablation A1) exposes this.

2. **Resolution diagnostic gates inference** (2605.30315): Many leaderboards report rankings that are unresolved at the paired-test power target. Early stopping via resolution prevents false claims downstream.

3. **Retrieval vs. utilization separation** (2608.01913): Budget controls search effort, but agents can waste budget on redundant queries after gold evidence arrives. Audit harness (stage 3: evidence use) distinguishes these.

4. **Statistical power planning precedes execution** (2010.06595): Power analysis is not post-hoc; N_budget is chosen before running to ensure 80% power for target effect size.

5. **Stage isolation prevents entanglement** (2608.03501): Breaking trajectory audit into six independent rubric scales prevents high-level planning failures from masking low-level config errors and vice versa.

### Limitations & Open Questions

1. **Rubric validity**: The 6-point trajectory rubric is intuitive but not validated on prior benchmarks. **Mitigation**: Inter-judge agreement (κ ≥ 0.60) is required before main analysis; if κ < 0.60, rubric must be refined or replaced.

2. **Test-set size**: 100 tasks may be insufficient to resolve small gaps with high confidence. **Mitigation**: Power analysis (Ablation A2) will reveal whether N_budget must grow; if so, design must enlarge test set or accept lower power.

3. **Generalization across agent architectures**: Design assumes ReAct-style agents with explicit search steps. Agents with implicit search or no tool use may not produce loggable trajectories. **Mitigation**: Design focuses on metered, instrumented evaluations; agents must provide trajectory logs or fail design gate.

4. **Causality**: High budget utilization does not prove score-buying; agent may simply be doing legitimate additional search. **Mitigation**: Trajectory audit (stage 5: process integrity) catches redundant queries and unsupported claims; combined with budget consumption, it triangulates strategy.

5. **Correlation vs. resolution**: Early evidence arrival (2608.01913) predicts stopping, but resolution target q ≥ 1 may be reached before evidence arrives (false confidence). **Mitigation**: Tertiary analysis (4.3) examines whether stopping-via-resolution occurs at steps with high cumulative retrieval recall; if not, decision rule needs revision.

---

## 9. EXPECTED OUTCOMES & DECISION RULES

### If Condition A >> Condition B (Unrestricted >> Metered)
- **Interpretation**: Budget cap alone prevents score-buying and maintains valid test-set evaluation
- **Decision**: Deploy Condition B on future benchmarks; trajectory audit optional but recommended for transparency
- **Next step**: Validate via Ablation A2 to find minimum-sufficient budget

### If Condition A ≈ Condition B (Unrestricted ≈ Metered)
- **Interpretation**: Either agents rarely over-call evaluation, or silent failures are common and net out
- **Decision**: Condition B is safe; trajectory audit critical to detect silent failures and redline them
- **Next step**: Implement Condition B with mandatory trajectory stage isolation (Ablation A1b)

### If Condition B > Condition C (Metered > Metered + Resolution)
- **Interpretation**: Early stopping via resolution is premature and cuts off legitimate search
- **Decision**: Do not use resolution-based stopping; stick with budget-based stopping (Condition B)
- **Next step**: Adjust resolution target or accept that test-set size does not support high-confidence pairwise inference

### If Condition B ≈ Condition C (Metered ≈ Metered + Resolution)
- **Interpretation**: Resolution-based stopping is efficient and safe
- **Decision**: Deploy Condition C; agents can terminate early when gaps become statistically meaningful
- **Next step**: Publish resolution diagnostics alongside all benchmark rankings (following 2605.30315)

---

## 10. EVIDENCE CITATIONS

This design draws on four key evidence sources:

- **2605.30315**: Paired evaluation, resolution diagnostics, and the factor-of-two efficiency gain of paired McNemar over unpaired tests
- **2608.01913**: Separation of retrieval gaps from utilization gaps; finding that search effort does not correlate with accuracy
- **2608.03501**: Stage isolation, redline mechanism, and rubric-based LLM-as-judge for experimental design quality
- **2609.00038**: Ground-truth-by-construction testbed, silent vs. loud fault distinction, trajectory-level evaluation blind spots in outcome-only judges
- **2010.06595**: Statistical power analysis, simulation-based power curves, and NLP-specific power design guidance

---

## 11. TIMELINE & DELIVERABLES

### Pre-Experiment (2 weeks)
- Instrument evaluation function and trajectory logger
- Validate test-set stratification
- Draft trajectory audit rubric; conduct inter-judge pilot (κ ≥ 0.60)
- Run power analysis simulation to finalize N_budget

### Main Experiment (4 weeks)
- Run agents under Conditions A, B, C
- Collect trajectories and evaluation logs
- Apply trajectory audit harness in parallel

### Analysis (2 weeks)
- Compute accuracy, CI, and paired differences
- Run ablations (A1, A2, A3)
- Apply resolution diagnostic (llm-power) to condition C pairs
- Sensitivity analysis (alternative budgets, judge models, task sets)

### Writeup (1 week)
- Report metrics and decision rules
- Discuss implications for benchmark design

---

**END OF DESIGN**
