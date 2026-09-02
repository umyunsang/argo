# Experimental Design: T1-Context-Artifact

## Research Question

Does giving a coding agent a persistent, human-written project context artifact 
improve its task success on real repository tasks? (See state.md decision_id: 
T1-context-artifact__decision-on-context-provision-strategy)

---

## 1. Main Comparison: With vs. Without Artifact

### Design Structure

**Comparison:** Agent task success rate with human-written project context artifact 
(henceforth "WITH") vs. without artifact (henceforth "WITHOUT").

**Primary outcome:** Binary pass/fail on hidden gold tests for each task.

**Agents:** Two agents from different vendors (e.g., Claude Code, Codex) to estimate 
generalization across agent products. Each agent receives the same task set.

**Sampling frame** (from state.md):  
Population: Pull requests merged into public GitHub repositories, drawn from the 
hidden test set accompanying the two agent products.  
Unit: (repository_id, task_id, strategy) triplets.  
Scope: All tasks in the hidden test set; no random sampling within the set.

### Conditions (Factors)

| Factor | Levels | Role |
|--------|--------|------|
| Context artifact | WITH, WITHOUT | Primary comparison |
| Agent product | Agent A, Agent B | Blocking factor / stratification |
| Attempt number | 1, 2, 3 | Repeat allocation |

**Full factorial (incomplete):**
- Agent A × WITH condition × Attempts 1–3
- Agent A × WITHOUT condition × Attempts 1–3
- Agent B × WITH condition × Attempts 1–3
- Agent B × WITHOUT condition × Attempts 1–3

Each (agent, condition) combination applied to all tasks in the hidden test set.

### Context Artifact Definition

**WITH artifact:** Each agent is provided a human-written CLAUDE.md-style project 
context document (or equivalent per-agent format) describing:
  - Repository architecture and module organization
  - Key entry points and conventions
  - Known gotchas or project-specific patterns
  - Relevant tool or dependency versions
  
Artifact authored once per repository; same artifact used for all attempts and 
both agents.

**WITHOUT artifact:** Agent receives only the task description (e.g., "Fix failing 
test X in repo Y") with no supplementary context document.

---

## 2. Ablation Experiments

### Ablation A: Task Complexity Stratification

**Rationale:** Evidence 2608.01913 ("Diagnosing Search Behavior") distinguishes 
retrieval gaps from utilization gaps. Artifact utility may depend on task complexity: 
simple tasks may not need artifact; complex multi-module refactors may benefit most.

**Implementation:**
Stratify hidden test set tasks into complexity tiers using available metadata 
(e.g., # changed files, # modules touched, test-failure depth, PR title/description tags):
  - Tier 1 (Simple): Single-file edits, clear failing test
  - Tier 2 (Medium): Multi-file within one module, moderate refactoring
  - Tier 3 (Complex): Cross-module changes, architectural implications

**Measurement:** Estimate treatment effect (WITH vs. WITHOUT) separately within 
each tier. Expected outcome: artifact effect size increases from Tier 1 → Tier 3.

**Falsifier for ablation:** Effect is reversed in any tier (artifact hurts complex 
tasks), or non-monotonic across tiers.

### Ablation B: Silent vs. Loud Failures

**Rationale:** Evidence 2609.00038 ("trajectory-judge") shows outcome-only judges 
miss "silent" failures (wrong reasoning, right answer). Artifact may prevent wrong-path 
exploration without changing final outcome.

**Implementation:**
For each task, collect trajectory-level signals:
  - Attempt succeeded on gold test (loud pass/fail)
  - Attempt visited correct modules/files (silent correctness)
  - Number of search/exploration steps (agent effort)
  - Evidence: agent cited or correctly interpreted relevant context (if WITH)

**Measurement:** Report:
  - Success rate on gold tests (primary, loud signal)
  - "Silent failure" rate (correct approach, failed execution)
  - Effort efficiency (success per step)

**Expected outcome:** Artifact may reduce silent failures even if gold success is similar.

---

## 3. Analysis Plan

### Primary Analysis: Paired Comparison

**Unit of analysis:** Task (not attempt). For each task under each condition:
  - Count successes across 3 attempts (range: 0–3)
  - Compute binary success = (≥1 success out of 3 attempts)
  
**Null hypothesis (H₀):** P(success | WITH) = P(success | WITHOUT)

**Test:** Matched-pairs proportion test (McNemar's test or binomial paired test).
  - Pair within task: successes WITH vs. successes WITHOUT, per agent.
  - Repeat for each agent separately, then meta-estimate across agents.
  
**Effect size:** 
  - Point estimate: P(success | WITH) − P(success | WITHOUT)
  - 95% confidence interval using binomial/score method (Wilson) or 
    exact Clopper–Pearson for small samples.
  
**Minimum detectable effect:** Given hidden test set size N (fixed, not designed), 
compute power post-hoc. If N < 50 tasks, report q = N/N* (resolution ratio from 
2605.30315) to flag whether design is powered.

### Secondary Analysis: Stratified Effect

**By complexity tier (Ablation A):**
  - Repeat primary analysis separately within Tier 1, 2, 3.
  - Test interaction: H₁: effect(Tier 1) ≠ effect(Tier 2) ≠ effect(Tier 3)
  - Method: logistic regression with task-complexity interaction term:
    ```
    logit(P(success)) ~ condition + complexity_tier + condition:complexity_tier
    ```
  - Report effect sizes per stratum with 95% CIs.

**By agent product (blocking factor):**
  - Repeat primary analysis separately for Agent A and Agent B.
  - Test consistency: H₁: effect(Agent A) ≠ effect(Agent B)
  - If effects differ, discuss agent-specific design implications.

### Tertiary Analysis: Trajectory-Level Diagnosis

**Per attempt, record:**
  - Gold test pass/fail (loud outcome, binary)
  - Visited correct module/file (silent correctness, binary)
  - Attempt trajectory length (steps taken, integer)
  - Context usage (if WITH: count citations or correct retrievals of artifact info)

**Analysis:**
  - Stratify attempts by (loud outcome, silent correctness) → 4 cells:
    (Pass/Correct, Pass/Incorrect, Fail/Correct, Fail/Incorrect)
  - Compare cell distributions (WITH vs. WITHOUT) using χ² or Fisher's exact.
  - Expected: WITH reduces (Fail/Correct) and (Pass/Incorrect) relative frequencies.

---

## 4. Outcome Metrics

### Primary Metric: Task Success Rate (Binary)

**Definition:** Task succeeds if ≥1 of 3 attempts passes hidden gold tests.

**Reporting:**
  - Proportion (0.0–1.0, percentage)
  - 95% CI (Wilson binomial or exact)
  - Count of successes (numerator) and tasks (denominator)

**Per agent, per condition, and difference (WITH − WITHOUT).**

### Secondary Metrics

| Metric | Definition | Unit | Notes |
|--------|-----------|------|-------|
| Success rate (all attempts) | Proportion of all attempts (not tasks) that pass | Per-attempt rate | Accounts for replication value |
| Silent failure rate | Attempts reaching correct module but not passing gold test | Proportion | From trajectory analysis |
| Exploration effort | Mean trajectory length (steps) per attempt | Steps | Proxy for agent efficiency |
| Failure mode breakdown | Categorized failure reasons (test timeout, import error, logic error, etc.) | Count, per category | Qualitative insight |
| Inter-rater agreement on gold tests | Cronbach's α or Cohen's κ for duplicate gold-test runs (if feasible) | [0, 1] | Validates scoring reliability |

---

## 5. Concrete Resources

### Task Source

**Hidden test set:** Provided by the two agent products. No external data collection.  
**Expected volume:** Unknown (not yet fixed in this design). If <50 tasks: note 
resolution ratio q = N/N* and interpret confidence intervals with caution.

**Metadata required from test set:**
  - Repository ID and name
  - Task description (PR title + description or requirements)
  - Gold test(s) for success evaluation
  - Optional: complexity tier, language, module count, lines changed in reference PR

### Context Artifacts

**Source:** Human authors (e.g., research team, repository maintainers).  
**Effort:** One CLAUDE.md or equivalent per repository in the hidden test set.  
**Format:** Plain text, ~500–2000 words per repository (typical project summary).  
**Reuse:** Same artifact used for both agents and all attempts (not regenerated per attempt).

### Agents

**Agent A:** Claude Code (Anthropic)  
**Agent B:** Codex (OpenAI) or equivalent from different vendor  
**Assumptions:**  
  - Both agents can accept task description + optional context artifact input
  - Both agents have equivalent max-attempts and time budgets
  - Both agents use the same hidden test set for evaluation

### Evaluation Infrastructure

**Gold test execution:** Use each test set's native harness (pytest, npm test, etc.).  
**Success criterion:** Test process exits with zero status code.  
**Trajectory logging:** Capture full agent execution log (tool calls, LLM outputs, errors).  
**Judge for trajectory inspection:** Trained human or rule-based system (not LLM, 
to avoid judge severity/drift from 2608.29517). Or: use deterministic, domain-specific 
rules (e.g., "correct module visited = True iff commit diff touches intended file").

---

## 6. Uncertainty Quantification

### Confidence Intervals (Primary)

All proportions reported with **95% binomial Wilson or Clopper–Pearson confidence intervals** 
(not normal approximation, to handle small sample counts and boundary values).

**Example reporting:**
```
WITH condition: 28/45 tasks succeeded (62%, 95% CI [48%, 74%])
WITHOUT condition: 22/45 tasks succeeded (49%, 95% CI [34%, 64%])
Difference (WITH − WITHOUT): 13 percentage points (95% CI [−2%, +28%])
```

### Power Analysis & Resolution Diagnostics (Post-Hoc)

If N (task count) is fixed by the hidden test set size:

1. **Compute minimum detectable effect:**
   - Given N, α=0.05, power=0.80, paired-test design
   - Report MDE as absolute percentage-point difference (e.g., "MDE = ±8%")
   
2. **Resolution ratio (from 2605.30315):**
   - q = N_observed / N_required
   - If q < 1.0: design is underpowered; interpret CIs conservatively
   - If q ≥ 1.0: design is powered at 80% (or higher with larger N)

3. **Post-hoc power:**
   - Report observed power given actual effect size, N, and α=0.05

### Robustness Checks

1. **Stratified CIs (Ablation A):** Report separate 95% CIs for effect within each 
   complexity tier. If CIs do not overlap and are monotonic (Tier 1 < Tier 2 < Tier 3), 
   effect is robust to complexity.

2. **Per-agent consistency (Ablation B):** Report effect size and CI for each agent 
   separately. If CIs overlap or effects have same sign, generalization is supported.

3. **Sensitivity to attempt allocation:** Recompute success rate using alternative 
   definitions (any of 3 attempts pass vs. majority of 3 pass) and report ranges.

---

## 7. Study Design Summary Table

| Aspect | Specification |
|--------|---------------|
| **Design type** | Matched-pairs, two-arm (WITH vs. WITHOUT), nested by agent and task complexity |
| **Unit** | Task (binary success across 3 attempts per condition) |
| **Blocking factors** | Agent product (A, B) |
| **Stratification** | Task complexity tier (Simple, Medium, Complex) |
| **Replication** | 3 attempts per condition per task |
| **Sample size** | N = # tasks in hidden test set (fixed, not power-designed) |
| **Primary outcome** | P(success ≥ 1 of 3) | 
| **Comparison** | McNemar's paired proportion test |
| **α level** | 0.05 (two-tailed) |
| **Confidence level** | 95% (binomial Wilson or exact) |
| **Effect size** | Absolute percentage-point difference, with CI |
| **Power** | To be computed post-hoc; report resolution ratio q if underpowered |

---

## 8. Evidence Dependencies

This design is grounded in the following evidence excerpts:

- **2010.06595** ("With Little Power Comes Great Responsibility"): 
  Justifies formal power analysis and warns against underpowered comparisons in NLP/ML.

- **2605.30315** ("Resolution Diagnostics for Paired LLM Evaluation"): 
  Paired-test resolution metric q = N/N*; unpaired Cohen-h approximation is inaccurate 
  for correlated outcomes (paired design used here).

- **2606.07591** ("ResearchClawBench"): 
  Precedent for hidden-target task packaging, rubric scoring, and agent evaluation on 
  merged-PR datasets.

- **2608.03501** ("SCOPE"): 
  High-level planning requirement: main experiment + ablations + analysis stages. 
  Stage isolation (separate analyses for strata) improves design.

- **2608.01913** ("Diagnosing Search Behavior"): 
  Decomposition of retrieval vs. utilization gaps motivates complexity stratification 
  to explore whether artifact helps retrieval (find right file) vs. utilization (write correct code).

- **2608.29517** ("LLM Judges as Raters"): 
  LLM judges exhibit large severity, halo, and drift. Design uses gold tests (deterministic) 
  or trained human raters (with inter-rater agreement checks), not LLM judging.

- **2609.00038** ("trajectory-judge"): 
  Outcome-only judges miss 55% of silent faults. Ablation B includes trajectory-level 
  inspection (correct-module visits, not just pass/fail) to detect artifact effects 
  on intermediate steps, even if final outcome is the same.

---

## 9. Pre-Registration and Deviations

To ensure transparency and reduce P-hacking (implicitly endorsed by 2608.29517 and 
2609.00038 on rater drift), the following should be pre-registered:

1. **Primary hypothesis:** Artifact improves success rate; one-tailed or two-tailed test.
2. **Stratification strategy:** If complexity tiers exist, report effect per tier (not 
   data-driven re-stratification post-hoc).
3. **Secondary metrics:** Fix trajectory-level definitions (e.g., "correct module" = 
   agent edited a file in the intended module) before analysis.
4. **Multiple comparison adjustment:** If stratified tests are planned (not exploratory), 
   adjust α using Bonferroni or similar (e.g., α_per_stratum = 0.05/3).

**Any deviations from pre-registered plan** (e.g., post-hoc stratification, additional 
outcome metrics, or exploration-driven re-analysis) should be labeled as exploratory.

---

## 10. Constraints and Limitations

### Fixed Sample Size

The hidden test set size is fixed (not power-designed). If N < 50 tasks:
  - Design will be underpowered to detect effects <8% absolute (typical MDE).
  - Confidence intervals will be wide; interpret with caution.
  - Report resolution ratio q to quantify power deficit.

### Unknown Effect Size

No prior work evaluates context artifacts (CLAUDE.md style) for coding agents. 
Effect direction and magnitude are unknown. Design assumes artifact may help but 
prepares for null findings.

### Attempt Budget

Three attempts per condition is fixed by the problem statement. This limits the 
recovery from transient agent failures (e.g., network timeouts, stochastic LLM outputs).
Analysis should distinguish systematic failures (artifact-dependent) from noise.

### Generalization

Findings generalize to the two agents and repositories in the test set. External 
generalization (other agents, domains, or repository types) is not addressed here.

### Artifact Quality and Consistency

Context artifacts are human-authored and may vary in quality. Design assumes artifacts 
are authored following a consistent template (CLAUDE.md standard), but does not 
validate quality or measure artifact informativeness. A secondary analysis comparing 
artifact length/readability/accuracy would address this.

---

## 11. Timeline and Milestones

| Phase | Deliverable | Notes |
|-------|-------------|-------|
| **Phase 1: Setup** | Collect hidden test set metadata; confirm task count & complexity tiers | ~1 week |
| **Phase 2: Artifacts** | Draft and refine context artifacts for each repository; author consensus | ~2 weeks |
| **Phase 3: Execution** | Run all (agent, condition) combinations on hidden test set | 2–4 weeks (depends on test set size & agent run time) |
| **Phase 4: Logging** | Collect and organize trajectory logs, gold test results, manual annotations | ~1 week |
| **Phase 5: Analysis** | Primary + stratified + trajectory analyses; produce tables and figures | ~2 weeks |
| **Phase 6: Reporting** | Write results, interpret findings relative to research question, pre-registered deviations | ~1 week |

---

## 12. Success Criteria & Acceptance

The design is ready for execution when:

1. ✓ State.md filled completely (all fields defined)
2. ✓ Hidden test set size and metadata confirmed (complexity tiers available or derivable)
3. ✓ Context artifacts authored and reviewed (ready to provide agents)
4. ✓ Both agent products can accept (task description + optional artifact) input
5. ✓ Gold test harness and logging infrastructure operational
6. ✓ Primary hypothesis and stratification plan pre-registered

The study is interpretable if:

1. Resolution ratio q ≥ 0.5 (at minimum, 50% powered; q=1.0 is ideal)
2. Inter-rater agreement (if human evaluation used) ≥ 0.60 (Cronbach's α)
3. No reversal of effect direction in any stratum (Simpson's paradox not present)
4. Trajectory-level analysis is consistent with gold-test outcomes (no contradictions)

---

*Design prepared: [Date]. Pre-registered plan published: [Link]. Deviations will be 
noted in final report.*
