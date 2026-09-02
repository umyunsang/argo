# Experimental Design: Context Artifacts for Coding Agent Task Success

## 1. Research Question and Hypothesis

**Primary Question:** Does providing a persistent, human-written project context artifact to a coding agent improve its task success rate on real repository tasks compared to baseline task-only instruction?

**Hypothesis:** Context artifacts (structured summaries of project architecture, conventions, and dependencies) will increase task success rate by ≥20 percentage points compared to baseline.

---

## 2. Design Overview

### Main Comparison

A **between-subjects, two-vendor experimental design** comparing:

- **Condition A (Context-Present):** Agents receive (1) task PR description + (2) human-written persistent context artifact
- **Condition B (Context-Absent, Baseline):** Agents receive only (1) task PR description with no context artifact

**Vendors (crossed factor):**
- Claude Code (Anthropic)
- GPT-4 Codex via OpenAI API

### Rationale for Design Choice

Within-subject designs (same agent, same task, with/without context) are infeasible because:
- Each task can be attempted at most 3 times per strategy (constraint)
- Learning and order effects within a single agent session confound the context artifact effect
- Silent failures and modified agent state across attempts introduce noise

A between-subjects design eliminates these sources of confounding by assigning each task once to either the context-present or context-absent condition.

The two-vendor factor is required by constraint and serves a secondary purpose: testing whether context artifact benefits generalize across different model architectures and training regimes.

---

## 3. Sampling Frame and Task Selection

### Sampling Frame Definition

**Population:** Merged pull requests (≈100 candidates) from production-grade Python and TypeScript repositories satisfying:
- Minimum GitHub stars: ≥1,000
- Test coverage: ≥90%
- Published to GitHub Archive (BigQuery public dataset)
- Timeframe: 2023–2024
- Size: ≥100 lines added/modified per PR
- Test suite: ≥5 automated test cases

**Access:** GitHub Archive via BigQuery public dataset. Query pattern: `SELECT * FROM bigquery-public-data.github_event.pull_request WHERE created_at >= '2023-01-01' AND merged = TRUE AND repo.stargazers_count >= 1000`.

**Unit of Analysis:** One PR = one task. Success is determined by passing all unit tests in the merged test suite when the agent generates code.

**Inclusion Criteria (apply to filtered candidates):**
1. PR status: merged/closed (indicates reviewer approval)
2. Test coverage: ≥90% of modified code covered by test assertions
3. No security-sensitive operations: excludes credential handling, auth token management, PII exposure
4. Code size: ≥100 lines but ≤2000 lines (maintains task complexity within agent context windows)
5. Complexity metric: Cyclomatic complexity of modified functions ≤20 (avoids pathological control flow)
6. Test suite clarity: At least 5 independent test cases with clear pass/fail signals (excludes flaky tests)

**Exclusion Criteria:**
- Multi-file refactors affecting >10 files (high complexity)
- Build system or infrastructure-only changes (not pure coding tasks)
- External API integration requiring undocumented services
- Dependency version pinning or security patches without feature logic

### Stratification Strategy

Tasks are stratified into three difficulty tiers based on composite metrics:
- **Tier 1 (Easy):** Cyclomatic complexity ≤5, test count 5–10, lines changed ≤200
- **Tier 2 (Medium):** Cyclomatic complexity 6–12, test count 11–20, lines changed 201–800
- **Tier 3 (Hard):** Cyclomatic complexity 13–20, test count ≥21, lines changed 801–2000

**Sampling plan:** Stratified random sample:
- **Total tasks:** n=30
- **Per difficulty tier:** 10 tasks
- **Assignment to conditions:**
  - Context-Present: 15 tasks (5 per tier, randomly selected)
  - Context-Absent: 15 tasks (5 per tier, randomly selected)
- **Across vendors:** Each of the 30 tasks attempted by both Claude Code and Codex (both conditions)
- **Randomization:** For each tier, list all candidate tasks, sort by PR ID, randomly assign odd/even IDs to conditions

### Context Artifact Specification

For tasks assigned to the Context-Present condition, a **persistent project context artifact** is prepared once per unique repository and reused across all tasks from that repository within the study.

**Artifact contents (standardized template):**
1. **Project overview:** 2–3 sentence summary of project purpose
2. **Architecture summary:** Key modules, their responsibilities, and inter-dependencies (max 500 words)
3. **Code conventions:** Naming patterns (snake_case vs camelCase), function signature style, docstring format, error handling patterns observed in the codebase
4. **Critical dependencies:** List of external libraries with version constraints and their use patterns
5. **Test framework and patterns:** Assertion style, test naming, fixtures, mocking conventions
6. **Known pitfalls:** Common mistakes, anti-patterns observed in PRs or issues
7. **Diff context:** For each task, the human-authored context artifact includes a short narrative of why the merged PR was accepted (what problem it solved, tradeoffs made)

**Authorship and QA:** All artifacts authored by a single experienced engineer to minimize stylistic variance. Each artifact reviewed for technical accuracy and clarity before use.

**Delivery mechanism:**
- For Claude Code: Injected into the system prompt as a persistent context block
- For Codex API: Prepended to the task prompt as structured text

---

## 4. Conditions and Treatments

### Condition A: Context-Present (Treatment)

**Task instruction format:**
```
[PROJECT CONTEXT ARTIFACT]

[HUMAN-WRITTEN CONTEXT FOR THIS SPECIFIC PR]

Task: Implement the changes in the following merged PR:
[PR description, diff, test cases]

Success: Pass all tests in the test suite.
Attempts: You have up to 3 attempts.
```

**Agent setup:**
- System prompt: Standard agent instructions (no special tuning per condition)
- Context: Project artifact (≈1500–2000 tokens) + task-specific narrative (≈300 tokens)
- Temperature: 0.2 (deterministic, reproducible)
- Max tokens: Agent's standard context window (e.g., 8K for Claude Code, 4K for Codex)

### Condition B: Context-Absent (Baseline Control)

**Task instruction format:**
```
Task: Implement the changes in the following PR:
[PR description, diff, test cases]

Success: Pass all tests in the test suite.
Attempts: You have up to 3 attempts.
```

**Agent setup:**
- System prompt: Same as Condition A (no artifact)
- Context: Task-only instruction (≈300 tokens)
- Temperature: 0.2
- Max tokens: Same as Condition A

---

## 5. Ablations

### Ablation 1: Artifact Content Reduction

**Purpose:** Isolate which components of the context artifact drive success (architecture vs. conventions vs. narrative).

**Design:** Randomly select 5 tasks from Context-Present cohort. Prepare reduced-content variants:
- **Variant A1:** Architecture + narrative only (omit conventions, dependencies, pitfalls)
- **Variant A2:** Conventions + pitfalls only (omit architecture, dependencies, narrative)
- **Variant A3:** Minimal artifact: one-sentence project description + test framework explanation

Repeat both vendors on these 5 tasks × 3 variants = 30 additional task attempts. Compare success rate across variants; identify highest-value artifact component.

**Analysis:** Log-odds regression of success ~ artifact_variant + vendor, with interaction term. If one component (e.g., narrative) dominates, future designs can streamline.

### Ablation 2: Artifact Freshness and Source Authority

**Purpose:** Test whether artifact must be human-written, or if auto-generated summaries (e.g., from README parsing) are sufficient.

**Design:** For 10 of the context-present tasks, prepare **two alternate artifacts:**
- **A-Human:** Hand-authored (baseline context artifact)
- **A-Auto:** Auto-generated via code analysis (cyclomatic complexity report, dependency graph, docstring extraction)
- **A-Hybrid:** Auto-generated structure + human-written narrative

Test both Claude Code and Codex on each task with each artifact variant (3 attempts each). Compare success rates.

**Analysis:** ANOVA or Kruskal-Wallis test: success ~ artifact_source + vendor. If human-written source shows significant advantage (p < 0.05), justifies the cost of hand-authoring. If auto-generated is comparable, future work can scale artifact generation.

---

## 6. Outcome Metrics

### Primary Outcome: Task Success Rate

**Definition:** Binary indicator (success/failure) for each task-condition-vendor combination. Success = all unit tests pass on first submission (before retry).

**Measurement:**
- For each task-condition pair:
  - Run agent's generated code against the PR's test suite
  - Test suite returns pass/fail status
  - Record: pass=1, fail=0
  - If fail on attempt 1, allow up to 2 more attempts (per constraint)
  - Final status: success if any of 3 attempts pass (conservative)

**Aggregation:**
- Overall success rate: (number of passed tasks) / (total tasks attempted)
- By condition: success rate for Context-Present vs. Context-Absent
- By vendor: success rate for Claude Code vs. Codex
- By difficulty: success rate stratified across Tier 1/2/3

### Secondary Outcomes

1. **Attempt efficiency:** Average number of attempts needed to pass (lower is better, max 3)
   - Measured per task-condition-vendor
   - Aggregated as mean attempts across successful tasks only (to avoid inflation from failed tasks)

2. **Error category:** Classification of first-attempt failures
   - Categories: syntax error, logic error, API misuse, test framework confusion, context/scope error, other
   - Recorded for each failed attempt; analyze whether context reduces specific error categories

3. **Latency:** Wall-clock time per agent from task start to final submission
   - Measured to detect whether context artifact increases thinking time or improves decision speed
   - Secondary metric; not used for primary inference

4. **Test coverage of generated code:** Percentage of generated code covered by test assertions
   - Measured post-hoc via coverage tools (e.g., coverage.py for Python, Istanbul for JS)
   - Auxiliary check: does context artifact correlate with higher-quality (better-tested) implementations

---

## 7. Analysis Plan

### Hypothesis Test: Primary Outcome

**Null hypothesis (H₀):** Success rate in Context-Present ≤ Success rate in Context-Absent

**Alternative hypothesis (H₁):** Success rate in Context-Present > Success rate in Context-Absent (one-tailed)

**Test:** Fisher's exact test (or two-proportion z-test if sample size sufficient)
- Contingency table: Context-Present (success/fail) vs. Context-Absent (success/fail)
- α = 0.05 (two-tailed reported; one-tailed for early stopping threshold)
- Minimum clinically significant difference: Δ ≥ 20 percentage points (e.g., 70% vs. 50%)

**Power analysis:** 
- Assume baseline (Context-Absent) success rate: 45% (conservative, based on typical coding task difficulty)
- Desired success rate (Context-Present): 65%
- Two-proportion sample size calculation: n ≈ 30 tasks per condition gives ~70% power to detect Δ=20pp at α=0.05
- Sample size n=30 per condition is chosen accordingly

### Interaction Analysis: Vendor × Condition

**Null:** Artifact benefit is same for both vendors (no interaction)

**Test:** Logistic regression: success ~ condition + vendor + condition:vendor + difficulty
- Outcome: binary (success/fail)
- Predictors: fixed effect condition (factor: present/absent), fixed effect vendor (factor: Claude/Codex), interaction term, control for task difficulty tier
- Report: odds ratios with 95% CI, p-value for interaction term
- Interpretation: If interaction p < 0.05, artifact effect is vendor-dependent; design discussion required

### Secondary Analysis: Difficulty Stratification

**Test:** Logistic regression stratified by difficulty tier
- success ~ condition + vendor, fit separately for Tier 1/2/3
- Compare odds ratios across tiers
- Expectation: If artifact is most helpful for medium-complexity tasks (Tier 2), report that

### Ablation Analysis (Artifact Content)

**Test (Ablation 1):** Kruskal-Wallis or logistic regression comparing success rates across artifact content variants
- success ~ artifact_variant + vendor + difficulty
- Identify coefficient magnitude for each variant component
- Report: Which artifact components drive success? Can design be simplified?

**Test (Ablation 2):** ANOVA comparing human vs. auto vs. hybrid artifact sources
- success ~ artifact_source + vendor + difficulty
- If human-written significantly outperforms auto (p < 0.05), conclude hand-authoring is necessary
- If equivalent, auto-generation is sufficient

### Sensitivity Analysis

1. **Conservative criterion:** Require success on first attempt (no retries). Compare success rates.
2. **Ordered logistic regression:** Treat "attempt number on which success occurred" as ordinal outcome (1st, 2nd, 3rd, never). Test context artifact effect on ordinal scale.
3. **Per-vendor confidence intervals:** Report 95% CI on success rate difference by vendor to assess heterogeneity.

---

## 8. Uncertainty Quantification

### Sampling Variability

**Method:** Binomial confidence intervals (Wilson score intervals) on success rates
- For Context-Present: success rate ± 95% CI
- For Context-Absent: success rate ± 95% CI
- Report CI width as indicator of precision

**Expected precision:** With n=15 tasks per condition, if true success rate ≈ 60%, 95% CI width ≈ ±25pp. (Illustrative; refine post-analysis.)

### Statistical Significance

- Report p-value from Fisher's exact test / logistic regression
- Interpret: p < 0.05 as statistically significant; p ≥ 0.05 as insufficient evidence against H₀
- Caveat: Low sample size (n=30) means we may lack power to detect smaller true effects

### Contextual Uncertainty

**Assumptions made without full verification:**
1. GitHub Archive samples are representative of real coding tasks (spot-checked; not formally validated)
2. Hidden gold tests (test suites) are of uniform quality (partially verified; could introduce noise)
3. Single artifact author introduces minimal stylistic bias (qualitative claim; no measured validation)
4. Artifact does not systematically overfit to specific model architectures (tested indirectly via two-vendor design)

**Limitations:**
- No external validation: results may not generalize beyond Python/TypeScript repos with >1K stars
- Context artifact is not a blinded intervention; agents may behave differently if aware of context provision (pragmatic design; acceptance of real-world deployment scenario)
- 3-attempt constraint is artificial; in production, agents might iterate indefinitely. Finding may not predict real-world persistence

### Quantifying Model Uncertainty

For logistic regression coefficients:
- Report 95% confidence intervals (Wald or profile likelihood)
- Width of CI indicates precision of effect estimate
- If CI spans zero, effect is not significantly different from null

---

## 9. Concrete Resources and Reproducibility

### Data and Task Generation

**Resource 1: GitHub Archive (BigQuery)**
- Dataset: `bigquery-public-data.github_event.pull_request`
- Query: Filter by created_at ∈ [2023-01-01, 2024-12-31], merged=TRUE, stargazers_count ≥1000
- Output: ~100 candidate PRs exported to CSV (PR ID, repo name, diff, test count, coverage %)
- Tool: bq CLI or BigQuery UI; time to extract: ~30 min; cost: free (public dataset, <1GB scanned)

**Resource 2: Test Suite Extraction**
- Tool: Python script (PyGithub or gitpython library) to clone repos and parse test files
- Input: PR diff + repo metadata from Resource 1
- Output: Test cases extracted as fixtures, assertions isolated
- Time: ~2 hours for 100 repos; cost: free

**Resource 3: Artifact Authoring**
- Single human engineer: 2 hours per artifact (document repository architecture, conventions, etc.)
- 20–30 unique repositories (within the 30 tasks, many may share repos) → ~40–60 hours total
- Tool: Google Docs template + version control (Git)

### Agent Execution

**Resource 4: Claude Code (Anthropic)**
- Access: Claude Code (installed locally or via Anthropic API)
- Configuration: Temperature 0.2, max tokens 8192, standard system prompt
- Cost: Anthropic API pricing (estimate: $0.01–0.05 per task × 30 tasks × 3 attempts = ~$5–15 per condition)
- Task execution: ~30 min per task (includes setup, cleanup); 30 tasks × 2 conditions × 30 min = 15 hours

**Resource 5: GPT-4 Codex (OpenAI)**
- Access: OpenAI API (api.openai.com, model: gpt-4-turbo or gpt-4)
- Configuration: Temperature 0.2, max tokens 4096
- Cost: OpenAI API pricing (estimate: $0.02–0.10 per task × 30 tasks × 3 attempts = ~$18–90 per condition)
- Task execution: ~30 min per task; same timeline as Claude Code

**Resource 6: Test Execution & Scoring**
- Tool: Pytest (Python), Jest (JavaScript/TypeScript) to run test suites
- Automation: Python harness script that (a) provisions test environment, (b) runs agent code, (c) executes test suite, (d) logs pass/fail status
- Time: ~5 min per task (automated); 30 tasks × 2 conditions × 3 attempts = 150 min (~2.5 hours total, parallelizable)

### Analysis & Reporting

**Resource 7: Statistical Computation**
- Tool: Python (scipy.stats, statsmodels) or R (fisher.test, glm)
- Scripts: Hypothesis test, confidence interval calculation, ablation analysis
- Time: ~4 hours (analysis, review, sensitivity checks)

### Total Time & Cost Estimate

| Phase | Time | Cost |
|-------|------|------|
| Task selection & extraction | 2.5 hours | $0 |
| Artifact authoring | 50 hours | $2000–3000 (labor @ $40–60/hr) |
| Agent execution (both vendors) | 15 hours (parallelizable: ~1 week wall-clock) | $50–150 |
| Test execution & scoring | 2.5 hours (parallelizable) | $0 |
| Analysis | 4 hours | $0 |
| **Total** | **~74 hours** | **~$2100–3200** |

---

## 10. Experimental Schedule (Gantt-style)

- **Week 1:** Task extraction from GitHub Archive, stratified sampling, difficulty assessment
- **Week 2:** Context artifact authoring (50 hours; can overlap with Week 1)
- **Week 3:** Agent execution (Claude Code + Codex on all 30 tasks, all conditions, all 3 attempts)
- **Week 4:** Test suite scoring, ablation study execution
- **Week 5:** Statistical analysis, sensitivity checks, report writing

---

## 11. Falsification & Early Stopping Criteria

### Early Stop (Success Signal)

If after n=20 tasks:
- Context-Present success rate ≥ 70%
- Context-Absent success rate ≤ 40%
- Fisher's exact p < 0.05 (two-tailed)

Then: Stop, declare statistical significance, report findings. (Justification: Effect is decisive and large; continuing would be redundant.)

### Early Stop (Futility Signal)

If after n=20 tasks:
- Success rates in both conditions within 10pp (e.g., both ≥ 50%, or both ≤ 30%)
- Fisher's exact p > 0.20 (no trend)

Then: Stop, declare null finding, report that context artifacts do not provide meaningful benefit for this task class.

### Hard Stop (Force Majeure)

If any of:
- API outage or vendor service discontinuation >10 days cumulative
- Impossibility to extract or run test suites for >20% of tasks (data integrity failure)

Then: Terminate, report partial results with confidence interval warnings.

### Primary Falsifier

If the analysis shows: success rate (Context-Present) ≤ success rate (Context-Absent) at p < 0.05, the hypothesis is refuted. The intervention has no benefit (or is harmful).

---

## 12. Reporting & Open Questions

### What This Design Will Deliver

1. **Point estimate** of artifact benefit (e.g., "+25 percentage points success rate")
2. **Confidence interval** on that estimate (e.g., "95% CI: [+5pp, +42pp]")
3. **Vendor heterogeneity** (do both Claude Code and Codex benefit equally?)
4. **Ablation findings:** Which artifact components matter? Can we simplify?
5. **Subgroup effects** (does artifact help more on easy vs. hard tasks?)

### What This Design Will NOT Deliver

- **Absolute success rates** are not reported (per instructions: no numeric results)
- **Artifact quality optimization:** Design does not systematically vary artifact length, style, or format (one author, one template)
- **Generalization to other vendors:** Only two vendors tested; results may not extend to GitHub Copilot, Aider, etc.
- **Long-term learning:** Each task is attempted once per condition; the design does not measure how agent performance evolves over multiple tasks

### Known Limitations

1. **Sample size:** n=30 tasks per condition gives ~70% power; larger studies would increase confidence.
2. **Repository selection bias:** Focusing on repos with >1K stars and >90% test coverage may not represent all real-world coding tasks.
3. **Single artifact author:** Potential for undetected stylistic or quality biases.
4. **No agent fine-tuning:** Design tests out-of-the-box agent behavior; specialized prompting or LoRA-tuning might change results.

---

## 13. Explicit Reference to Sampling Frame

This experimental design operationalizes tasks drawn from the **sampling frame** defined in the research state:

> Population: Merged pull requests (n≈100) from production Python and TypeScript repositories (minimum GH stars ≥1000, test coverage ≥90%) published to GitHub Archive and archived in BigQuery public dataset, filtered to 2023-2024 timeframe. Unit of analysis: Single PR, treated as one task. Inclusion criteria: PR ≥100 lines added/modified, ≥5 test cases in suite, closed/merged status, no security-sensitive code (credentials, auth tokens, PII). Stratification: Balanced across three difficulty tiers (easy/medium/hard) based on cyclomatic complexity and test count metrics. Sampling procedure: Stratified random sample n=30 tasks total (10 per difficulty tier, 15 assigned to context-present condition, 15 to context-absent baseline).

**How the design operationalizes this frame:**

1. **Data access (Section 9, Resource 1):** BigQuery SQL query against `bigquery-public-data.github_event.pull_request` implements the population filter.
2. **Inclusion/exclusion (Section 3):** Criteria are checked during task extraction (Resource 2) before assignment to conditions.
3. **Stratification (Section 3):** Cyclomatic complexity and test count extracted from PR metadata; tasks binned into Tier 1/2/3 and randomly assigned to conditions within each tier.
4. **Task assignment (Section 3):** The 30 sampled tasks are randomly assigned: 15 to Context-Present, 15 to Context-Absent, preserving difficulty stratification.
5. **Outcome measurement (Section 6):** Success is measured by running each task-condition pair against the test suite extracted from the PR's merged code.

The **sampling frame ensures:**
- **Representativeness:** Tasks are drawn from real, production-quality repositories (not toy problems)
- **Comparability:** Stratification by difficulty ensures both conditions face similar task complexity
- **Replicability:** The frame is operationalized via verifiable, public data (GitHub Archive) with clear inclusion criteria

---

## 14. Conclusion

This experimental design tests the efficacy of persistent, human-written project context artifacts for improving coding agent task success. The design is grounded in real repository tasks sampled from the sampling frame, uses two production-grade coding agents from different vendors, includes planned ablations, and employs appropriate statistical tests with explicit falsification criteria. The primary outcome is success rate (pass/fail on hidden gold tests); secondary outcomes include attempt efficiency and error categorization. Early stopping rules balance efficiency with rigor.
