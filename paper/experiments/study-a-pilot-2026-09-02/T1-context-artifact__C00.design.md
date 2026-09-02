# Experimental Design: Project Context Artifacts and Coding Agent Success

## Research Question
Does giving a coding agent a persistent, human-written project context artifact improve its task success on real repository tasks?

## Main Comparison and Conditions

### Primary Comparison: Context-with-Artifact vs. Context-without-Artifact

**Treatment (T1):** Agent receives access to a persistent human-written CLAUDE.md-style project context artifact that includes:
- Architecture overview
- Key entry points and module relationships
- Naming conventions and project idioms
- Known anti-patterns to avoid
- Setup, test, and verification procedures

**Control (C0):** Agent receives only the default minimal context available from repository surface inspection (README, CONTRIBUTING, etc.) without a pre-authored project artifact.

### Factor Levels

**Agent Products (Crossed Factor):**
- Agent A: Claude Code (Anthropic)
- Agent B: Aider (Anthropic-compatible fork)

Both agents will run against both T1 and C0 conditions.

**Repository Task Set:**
- Tasks sourced from merged pull requests in established open-source repositories with test coverage
- Each task includes hidden gold-standard tests (from original PR) to verify correctness
- Minimum 24 tasks to support stratification and power

---

## Ablation Studies

### Ablation 1: Artifact Granularity (if primary effect is positive)

If T1 outperforms C0, test whether a **minimal artifact** performs as well as a **comprehensive artifact**:

- **Minimal (A1):** One-paragraph summary: project scope, key files, one convention rule
- **Comprehensive (A2):** Full CLAUDE.md as in T1

This isolates whether the effect is driven by architecture overview alone or by cumulative detail.

### Ablation 2: Artifact Timing (within treatment group)

Among tasks receiving T1, compare:
- **Artifact-at-start (T1-start):** Agent given artifact before any task context
- **Artifact-after-attempt-1 (T1-delayed):** Agent given artifact only after failed first attempt

This tests whether context artifact helps with cold-start reasoning or post-failure recovery.

---

## Experimental Design Structure

### Task Assignment

1. **Stratified random assignment** (stratification by repository and task difficulty tier estimated from PR size + test count)
2. Each of 24+ tasks assigned to:
   - Agent A × T1 (with artifact)
   - Agent A × C0 (without artifact)
   - Agent B × T1 (with artifact)
   - Agent B × C0 (without artifact)
3. Within each cell: up to 3 independent attempts per task (constraint from instructions)

### Expected Sample Size

- 24 tasks × 2 agents × 2 conditions = 96 primary cells
- With 3 attempts per cell (failure recovery): 288 total agent runs
- Ablation 1 (if pursued): +48 ablation runs
- Ablation 2 (if pursued): +24 targeted re-attempts

### Task Selection Criteria

**Source repositories:**
- Open-source Python projects with 50+ merged PRs and 80%+ test coverage
- Examples: requests, django-rest-framework, pandas (if public PR history available), or similar
- Exclude tasks that require external API keys, large downloads, or cluster access

**Task criteria:**
- Each task: fix a real bug or add a feature from a merged PR
- Hidden test suite: the full test suite from original PR (not visible to agent)
- Difficulty distribution: 8 small (1-50 LOC), 8 medium (50-200 LOC), 8 large (200+ LOC)
- Time budget: 10 minutes per attempt per task (enforced timeout)

---

## Concrete Resources

### Repositories for Task Sourcing
1. **pallets/flask** (tested against git tags for PR history)
2. **sqlalchemy/sqlalchemy** (established test suite)
3. **encode/httpx** (clear API surface)
4. **facelessuser/pymdown-extensions** (moderate size, good test coverage)
5. **getredash/redash** (real-world task complexity)

Rationale: All are public, have merged PR history, stable test suites, and do not require external credentials for local verification.

### Agent Products
1. **Claude Code** (via claude CLI or API, with default settings)
   - Model: claude-3-5-sonnet (latest stable)
   - Context window: 200K tokens
   - Tool use: enabled

2. **Aider** (open-source, claude backend)
   - Model: claude-3-5-sonnet
   - Same context window and tool settings for fair comparison

### Context Artifacts (Human-Written)
- **Source:** One artifact per repository, authored by one human reviewer familiar with the codebase
- **Format:** Markdown file (e.g., CLAUDE.md) placed in repository root
- **Content elements:**
  - 100-150 word architecture summary
  - 5-10 key file paths and their roles
  - 3-5 project-specific conventions (naming, import patterns, test structure)
  - 2-3 common mistakes to avoid
  - One-line verification command
- **Consistency check:** Artifact reviewed for accuracy by second reviewer before use

### Verification Infrastructure
- **Golden test sets:** Extracted from original PR's test suite before merge
- **Test execution:** `pytest` or project-native test runner with isolated venv per attempt
- **Pass criterion:** All golden tests pass, agent-introduced code passes linting (flake8 or project default)

---

## Outcome Metrics

### Primary Outcome: Task Success Rate

**Definition:** Percentage of tasks completed successfully within 3 attempts, per agent-condition cell.
- Success: All gold-standard tests pass + no new linting violations introduced
- Tracking: Success after 1st attempt, after 2nd attempt, after 3 attempts (cumulative)

**Analysis:** Chi-square test for independence; report success rate with 95% CI (binomial exact or Wilson score).

### Secondary Outcomes

1. **Attempts-to-success:** Median attempts per task by condition (Mann-Whitney U test if non-normal)

2. **Time-to-success:** Total wall-clock time from task start to passing all golden tests (geometric mean, log-transformed for skew)

3. **Agent-specific effect:** Interaction between agent product and context condition
   - Does the artifact help Claude Code and Aider equally?
   - Reported via logistic regression: success ~ condition + agent + condition:agent

4. **Task difficulty modulation:** Does artifact benefit scale with task size?
   - Small, medium, large tasks analyzed separately
   - Reported via stratified success rates

### Uncertainty Quantification

1. **Confidence intervals (primary):** 95% binomial exact CI (Clopper-Pearson) for each success rate

2. **Effect size:** Relative risk or odds ratio (T1 vs. C0) with 95% CI, not just p-value

3. **Power sensitivity:** Report the number of tasks N required to detect a 15% difference in success rate (assumed meaningful effect) with 80% power and α=0.05 (two-tailed).

4. **Ablation uncertainty:** If Ablation 1 is run, report artifact-granularity effect with same CI approach

---

## Analysis Plan

### Primary Analysis

```
Outcome: Task success (binary: pass/fail after ≤3 attempts)
Model: Logistic regression with fixed effects
  success ~ condition (T1 vs. C0) + agent (A vs. B) + stratification_block + error

Hypothesis test:
  H0: success_rate(T1) = success_rate(C0)
  H1: success_rate(T1) ≠ success_rate(C0)
  
Test: Two-tailed chi-square; reject H0 if p < 0.05
Report: Success rate per condition (%), odds ratio (T1/C0), 95% CI, p-value
```

### Secondary Analyses

1. **Attempts-to-success:** Mann-Whitney U test; report median and IQR per condition
2. **Agent × Condition interaction:** Include interaction term in logistic model; test coefficient significance
3. **Difficulty stratification:** Repeat primary analysis within each task-size stratum; report heterogeneity
4. **Time analysis:** Log-transform times; ANCOVA with task size and repository as covariates

### Robustness Checks

- **Missingness:** Document any task timeouts or incomplete attempts; sensitivity analysis under missing-data mechanisms (MCAR vs. MAR assumptions)
- **Outliers:** Flag tasks with >10-min completion time or repeated failures across both conditions (possible task mislabeling)
- **Multiple comparisons:** Bonferroni correction if ablations are pre-specified; otherwise report as exploratory

### Reporting Thresholds

- Report exact p-values (not p < 0.05 vs. p ≥ 0.05)
- Treat effect as modest if 0.05 < p < 0.10; report as evidence of effect in discussion
- Prioritize 95% CIs and effect sizes over p-values in main results table

---

## Data and Assumptions

### Assumptions

1. **Independence:** Each task-attempt is independent (reasonable given 3-attempt limit and task reset between attempts)
2. **Exchangeability:** Tasks within stratification block are exchangeable (justification: tasks selected on merged PR basis, not cherry-picked)
3. **No interference:** Artifact for one task does not leak to another task (enforced by isolated agent instances)

### Data Collection

- **Metadata per run:** task_id, agent, condition, attempt_number, timestamp_start, timestamp_end, success (boolean), errors_log, test_output
- **Artifact version:** Store hash of CLAUDE.md used; verify consistency across all runs
- **Agent configuration:** Log agent version, model, temperature, tools enabled—for reproducibility

### Handling Incomplete Data

- **Timeout (≥10 min):** Mark as failure; do not penalize agent (counts toward attempt limit)
- **Infrastructure crash:** Retry once; if repeated, exclude task from analysis and report in limitations
- **Test harness ambiguity:** Re-run golden tests independently; if still ambiguous, classify as censored (not included in success metric, included in denominator for rate calculation)

---

## Sample Size and Statistical Power

### Justification

With 24 tasks per agent-condition cell:
- Assuming base success rate 50% in C0 and 65% in T1 (a 15% absolute difference, moderate effect)
- Power to detect this difference: ~80% (two-tailed, α=0.05, binomial test)
- Total N = 24 tasks × 2 agents × 2 conditions = 96 primary comparisons across cells

If artifacts show promise in ablation, expand to 36–48 tasks per cell to detect smaller effect sizes (8–10% difference).

### Stopping Rule

- **Interim checkpoint:** After 16 tasks (first third), evaluate whether primary effect direction is consistent; if opposite sign observed, discuss with team before proceeding (not a formal stopping rule; reported for transparency)
- **Final analysis:** Run all 24 tasks; do not stop early

---

## Reporting and Interpretation

### Primary Table

| Agent | Condition | N Tasks | Success Rate (%) | 95% CI | Odds Ratio | p-value |
|-------|-----------|---------|------------------|--------|------------|---------|
| A     | T1        | 24      | — | — | — | — |
| A     | C0        | 24      | — | — | — | — |
| B     | T1        | 24      | — | — | — | — |
| B     | C0        | 24      | — | — | — | — |
| **Overall** | **T1 vs. C0** | **96** | **—** | **—** | **—** | **—** |

### Interpretation Guidance

- **Effect found (p < 0.05, T1 > C0):** Context artifacts causally improve agent success; estimate benefit magnitude from odds ratio and discuss practical significance
- **Trend but not significant (0.05 ≤ p < 0.10):** Moderate evidence of benefit; use CI and effect size to guide next-stage design (larger N or refined artifact)
- **No effect (p ≥ 0.10):** Context artifacts do not significantly improve success on these tasks; report as null result; discuss possible mechanisms (e.g., agents already optimized for surface inspection, or artifact poorly written)

### Limitations Section

- Sample size: 24 tasks per cell is modest; generalization to other codebases uncertain
- Agent scope: Limited to Claude-family models; Copilot, GPT-4, or other architectures may respond differently
- Artifact design: Single human author per repo; inter-rater variability not assessed
- Ecology: Artifact may reflect reviewer expertise; real-world impact depends on artifact quality and update frequency

---

## Conclusion

This design isolates the causal effect of human-written project context artifacts on coding agent success using a factorial structure (agent × condition), stratified task assignment, and rigorous gold-standard evaluation. Ablations test mechanism (granularity and timing). Analysis combines hypothesis testing with effect estimation and confidence intervals. Resources are all concrete and accessible. The design is powered to detect a meaningful (15%) improvement and disciplined about reporting uncertainty.
