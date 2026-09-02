# Experimental Design: Context Artifacts and Coding Agent Task Success

## Research Question
Does giving a coding agent a persistent, human-written project context artifact improve its task success on real repository tasks?

## 1. Main Comparison and Conditions

### Primary Comparison: Context vs. No-Context Condition

We compare two treatment arms across two agent products in a 2×2 within-subject design:

**Factor 1 (Context Availability):**
- **Condition A (Control)**: Agent receives only the task PR description and inline code comments. No persistent context artifact.
- **Condition B (Treatment)**: Agent receives the task PR description, inline code comments, AND a human-written project context artifact (CLAUDE.md or equivalent) that describes project structure, conventions, dependencies, testing patterns, and design decisions.

**Factor 2 (Agent Product):**
- **Agent 1**: Claude Code (primary agent capable of file editing, command execution, and multi-file reasoning)
- **Agent 2**: Codex (alternative vendor; contrasting architecture/capabilities)

### Units of Assignment
- **Task**: Each task is a merged PR from a real repository with hidden gold test(s)
- **Strategy**: Combination of (Agent Product × Context Condition)
- **Attempt**: Each strategy gets exactly 3 independent attempts per task, constrained by the given rules

---

## 2. Ablation Study

**Ablation: Artifact Scope Variation**

To isolate what components of a context artifact matter, we run a third arm on a subset (20%) of tasks:

- **Condition C (Minimal Context)**: Agent receives only a brief 100-word summary of the project (name, primary language, main module structure) but not the full CLAUDE.md artifact.

This ablation tests whether the documented benefit comes from:
1. **Mere familiarity effect** (brief priming) vs.
2. **Detailed structural and convention knowledge** (full artifact).

If Condition C and Condition B show no significant difference, the priming effect dominates. If Condition B outperforms Condition C substantially, detailed context drives the gain.

---

## 3. Task Selection and Constraints

### Task Source
- **Repository**: Real open-source or industry repositories with merged PRs
- **Gold Standard**: Each task has hidden test(s) that define success (test passes against the PR's intended changes)
- **Scope**: Mixed complexity: bug fixes, feature additions, refactors, documentation
- **Sample Size**: N = 30 tasks (minimum to achieve ~80% power to detect a 15–20% absolute success rate difference; see power analysis below)

### Attempt Allocation
Each (task, strategy) pair gets exactly 3 independent runs:
- Runs are separated in time (not consecutive) to avoid caching effects
- Different random seeds / system prompts to reflect natural LLM variability

---

## 4. Context Artifact Design

### Artifact Content Structure
The human-written context artifact (provided by domain experts or repo maintainers) must include:

1. **Project Overview** (50–200 words)
   - Purpose, primary use cases, audience

2. **Architecture & Module Layout**
   - Directory tree, key file roles, internal dependencies
   - Rationale for current structure

3. **Coding Conventions**
   - Language-specific idioms (naming, style, patterns)
   - Framework-specific design patterns
   - Performance or security constraints

4. **Testing & Verification**
   - How tests are organized and run
   - Test conventions (naming, structure, fixtures)
   - Coverage expectations

5. **Key Dependencies & Constraints**
   - External libraries and versions
   - Known technical debt or areas under refactor
   - Platform or version constraints

6. **Common Task Patterns**
   - Frequently needed edits and where to find them
   - Common pitfalls in this codebase
   - Where to add new functionality

### Artifact Consistency
All artifacts are validated by:
- A human domain expert for accuracy (checklist review, no LLM pre-generation)
- Structured format (Markdown) for consistent parsing
- Target length: 2,000–4,000 words (detailed but digestible in a single context window)

---

## 5. Outcome Metrics

### Primary Metric: Task Success Rate
- **Definition**: Proportion of (task, strategy) runs where the agent's output passes all hidden gold tests
- **Calculation**: success_rate = (# passed attempts) / (# total attempts per strategy)
- **Measurement**: Binary per attempt (pass/fail on hidden tests)

### Secondary Metrics (Process-Level; see 2609.00038.txt)

1. **Trajectory Quality** (not just outcome)
   - Human rater scores process steps on a 1–5 scale:
     - Correct diagnosis of problem?
     - Appropriate use of context artifact (if provided)?
     - Unnecessary or incorrect steps?
   - Aggregate via median and inter-rater agreement (Krippendorff's α)
   - Rationale: Outcome-only evaluation misses wrong-path-right-answer cases (2609.00038.txt)

2. **Context Utilization Rate**
   - In Condition B, count how often the agent explicitly referenced or used information from the artifact
   - Manual audit on 10% of runs (stratified by task complexity)
   - Metric: (references_to_context) / (total_reasoning_steps)
   - Purpose: Verify artifact is being utilized, not just present

3. **Confidence Intervals on Success Rate**
   - Use exact binomial 95% CIs (Wilson score interval) per condition
   - Report MDE (Minimum Detectable Effect) ex-ante; report post-hoc CI width

### Tertiary Metrics (Variance Components; see 2607.13304.txt)

1. **Variability Decomposition**
   - Use mixed-effects logistic regression: 
     - Fixed effects: Agent product, Context condition
     - Random effects: Task, Attempt (nested)
   - Extract variance components: τ²_task, τ²_attempt, σ²_residual
   - Purpose: Allocate repeats optimally for future studies

2. **Agent-by-Condition Interaction**
   - Interaction term: does context help Claude Code more than Codex (or vice versa)?
   - Estimate via logistic regression coeff + SE

---

## 6. Analysis Plan

### Pre-Analysis Protocol (to prevent HARKing)
This plan is registered before data collection:

#### Primary Analysis
1. **Hypothesis Test**: Fisher's exact test (or Cochran-Mantel-Haenszel if controlling for task complexity strata) comparing success rates:
   - H₀: success_rate(Context B) = success_rate(Control A)
   - H₁: success_rate(Context B) ≠ success_rate(Control A)
   - α = 0.05 (two-tailed)

2. **Effect Size**: Report absolute difference in success rate (Δ) with 95% Wilson score CIs

3. **Power Check**: Verify post-hoc achieved power (1 − β) given observed effect size and sample size

#### Secondary Analysis
1. **Agent Product Comparison**
   - Separate Fisher tests for Claude Code and Codex
   - Report success rates and CIs per agent × condition cell (2×2 subtable per agent)

2. **Trajectory Quality** (2609.00038.txt)
   - Ordinal regression (proportional odds): Quality ~ Context + Agent + Context × Agent
   - Report point estimates and 95% CIs for condition effects

3. **Context Utilization** (if applicable)
   - Logistic regression: utilized ~ Agent + task_complexity + Agent × task_complexity
   - Identify which agent types under-utilize the artifact

#### Ablation Analysis (Condition C)
1. Test Condition C vs. Condition B:
   - Fisher's exact test: success_rate(B) vs. success_rate(C)
   - If p < 0.05 and effect size > 5%, detailed context matters beyond priming
   - If no difference, priming is the active ingredient

#### Variance Components
1. Fit mixed logistic model to all data
2. Extract and report variance partition coefficient (VPC) for Task and Attempt levels
3. Use to inform optimal resampling for future iterations

#### Robustness Checks
1. **Sensitivity to Attempt Order**: Rerun analysis excluding the first attempt per (task, strategy) to check for ordering effects
2. **Sensitivity to Task Complexity**: Stratify primary analysis by task complexity (bug fix vs. feature vs. refactor)
3. **Judge Reliability Audit** (2608.29517.txt): 
   - For trajectory quality scores, measure inter-rater reliability (Krippendorff's α)
   - If α < 0.60, flag secondary metric as inconclusive

### Missing Data & Dropout
- Document any runs that timeout, crash, or cannot be evaluated (hidden test failures)
- Report reason for missingness per cell
- Use intention-to-treat: count unfinished/crashed runs as failures for primary metric

---

## 7. Concrete Resources

### Task Repositories
- **Source**: Merged PRs from GitHub or GitLab with automated test suites
- **Criteria**:
  - Public open-source (or industry partners with data-sharing agreement)
  - Language: Python, TypeScript, Java, or Go (languages both agents handle well)
  - Test suite: > 50 tests; hidden gold test(s) clearly marked
  - Realistic PRs: not toy examples; >5 files changed, >50 lines per PR on average
- **Candidates** (to be sourced):
  - Apache projects (Spark, Airflow)
  - High-quality GitHub repos with strong test coverage (e.g., trending repos with 10k+ stars)
  - Industry partner codebases (with anonymization)

### Agent Products
1. **Claude Code**: Anthropic's agentic coding product (file editor, bash, multi-file context)
2. **Codex**: OpenAI's GPT-based coding model (alternative vendor for robustness)

Both must support:
- File read/edit
- Test execution (bash/command line)
- Receiving context artifact as structured input (preamble, system message, or artifact block)

### Human Raters (for Trajectory Quality)
- 3 independent raters with software engineering experience (10+ years)
- Training: 1-hour calibration session on 5 example trajectories
- Evaluation: Each rates ~100 random trajectories (10% of 30 tasks × 2 conditions × 3 runs = 180 total)
- Compensation: Standard academic honorarium or vendor partnership

### Computational Budget
- Tasks: 30 × 2 agents × 2 conditions (A, B) × 3 attempts = 360 runs
- Additional: 30 × 2 agents × 1 condition (C, ablation) × 3 attempts = 180 runs
- Total: ~540 runs
- Estimated cost: ~$5,000–$15,000 (depending on agent API pricing)
- Wall-clock time: 2–4 weeks (runs can be parallelized within task batches)

### Evaluation Infrastructure
- **Test Harness**: Automated script to:
  - Clone task repos
  - Inject context artifact into agent system message
  - Run agent, capture output
  - Execute hidden tests
  - Log pass/fail and trajectory
- **Logging**: Store per-run logs including:
  - Task ID, attempt #, condition, agent product
  - Raw trajectory (prompts, edits, commands)
  - Timestamp, random seed
  - Test result (pass/fail, test suite output)

---

## 8. Uncertainty Quantification

### Confidence Intervals (Primary Metric)
- **Method**: Exact binomial CIs (Wilson score interval, mid-p correction)
- **Reported**: 95% CIs on success_rate per condition and per agent
- **Interpretation**: Minimum detectable effect (MDE) will be ~15–20% absolute at N=30 tasks, α=0.05, power=0.80

### Hypothesis Test Uncertainty
- **p-value**: Reported for primary test (Fisher's exact)
- **Interpretation**: If p > 0.05, conclude no evidence of effect; report CIs to quantify the upper bound of plausible effects
- **Citation**: Aligns with power guidance in 2010.06595.txt (power norms for NLP)

### Variance Component Uncertainty
- **Method**: Bootstrap CIs on variance partition coefficient (VPC)
- **Process**: Resample tasks (with replacement, n=30) from the 30-task pool, refit mixed model, extract VPC
- **Reported**: Mean VPC ± 95% bootstrap CI
- **Purpose**: Inform optimal allocation of repeats in future studies (2607.13304.txt)

### Judge Variability (Secondary Metric)
- **Method**: Inter-rater agreement with 95% CIs (Krippendorff's α boot)
- **Interpretation**: If lower α indicates low reliability, trajectory quality metric is tentative

### Multiple Comparisons
- **Primary test**: 1 (Context A vs. B) — no adjustment
- **Secondary tests** (Agent subgroup analysis, Ablation): Apply Bonferroni or False Discovery Rate (FDR) control
  - Adjust α to 0.05 / k, where k = # secondary tests (~5)
  - OR report adjusted p-values (FDR)

### Resolution Requirement (per 2605.30315.txt)
- **Target**: All pairwise comparisons report resolution metrics (α, 1−β)
- **Minimum**: α = 0.05, power = 0.80 desired; report if not achieved
- **Rationale**: Many LLM comparisons fail conventional resolution targets; transparency prevents false confidence

---

## 9. Assumptions and Justification

### Assumption 1: Hidden Test Validity
- **Assumption**: Hidden tests represent genuine task success (e.g., PR would be merged if tests pass)
- **Justification**: Following 2606.07591.txt (ResearchClawBench); hidden tests prevent agent overfitting
- **Risk**: If tests are noisy (e.g., flaky), some passes/failures are misclassified
- **Mitigation**: Pre-validate test suites with 3 independent runs on known-good code

### Assumption 2: Context Artifact Content Quality
- **Assumption**: Human-written artifacts are accurate and representative
- **Justification**: Artifact creation is overseen by domain experts, not auto-generated
- **Risk**: If artifacts are out-of-date or inaccurate, they may harm performance
- **Mitigation**: Audit artifact accuracy against actual repo on a sample of 5 tasks

### Assumption 3: Agent Stability Across Runs
- **Assumption**: Same prompt to agent yields similar (not identical) outputs across 3 runs; variation is due to LLM sampling, not external drift
- **Justification**: Standard in LLM evals; aligns with variance decomposition in 2607.13304.txt
- **Risk**: If agent model updates mid-study, between-attempt variance confounds the effect
- **Mitigation**: Lock agent product versions before study start; log version per run

### Assumption 4: Exchangeability of Tasks
- **Assumption**: Tasks are not ordered by difficulty; randomization protects against learning effects
- **Justification**: Each agent sees tasks in random order; minimal agent carries-over (fresh context per task)
- **Risk**: If one agent learns from tasks, later tasks become artificially easier
- **Mitigation**: Separate study into epochs (randomized task order per epoch); analyze epoch as a fixed effect

---

## 10. Stopping Rule & Plan for Inconclusive Results

### Planned Stopping
- **Stop at**: N = 30 tasks (pre-registered)
- **Rationale**: Balances feasibility (~$5–15K cost) with power (~80% at 15–20% effect size difference)
- **No peeking**: Do not run interim analyses; conduct final analysis once all 540 runs complete

### If Results Are Inconclusive (e.g., p = 0.15, CI overlaps zero)
1. **Report confidence interval width**: Even without statistical significance, report the range of plausible effects
2. **Interpret via MDE**: If CIs exclude effects < 10%, conclude "no large effect," not "no effect"
3. **Plan follow-up**: If CI width is wide (> 30%), suggest larger N for next iteration
4. **Acknowledge limitations** (see 2010.06595.txt on power norms)

---

## 11. Success Criteria & Interpretation Guide

### Criterion 1: Primary Effect
- **Success**: Context condition B shows ≥ 15% absolute improvement in success rate vs. Control A, p < 0.05, CIs do not overlap zero
- **Interpretation**: Persistent context artifacts meaningfully improve coding agent task success
- **Publication**: Positive, reportable result

### Criterion 2: Heterogeneous Effects
- **Secondary Finding**: Differential effects across agent products (Agent 1 benefits from context; Agent 2 does not)
- **Interpretation**: Context effectiveness depends on agent architecture; one size does not fit all
- **Publication**: Noteworthy for vendor-specific guidance

### Criterion 3: Ablation Insight
- **Finding**: Condition C (minimal context) performs as well as Condition B
- **Interpretation**: Brief priming is the active ingredient; detailed context not necessary
- **Impact**: Simpler intervention; cost-saving implication

### Criterion 4: Null or Opposite Result
- **Finding**: Context condition performs worse or shows no difference
- **Interpretation**: Context artifacts may distract or confuse the agent; RAG is not a universal win (aligns with evidence from 2608.01913.txt on saturation)
- **Publication**: Negative result; valuable for literature

---

## 12. Ethical & Practical Considerations

### Reproducibility
- **Preregistration**: This design is pre-registered (before data collection) to prevent HARKing
- **Code & Data Sharing**: Agent trajectories, task descriptions, and analysis code will be released (scrubbed of proprietary data)
- **Replication**: Design enables replication by other research groups

### Fairness to Agent Vendors
- **Symmetric Treatment**: Both agents see same tasks, same context artifact, same randomization
- **Public Disclosure**: Results will be reported for both agents; no cherry-picking
- **No Vendor Bias**: Artifact content is vendor-agnostic; both agents access it identically

### Informed Consent (if applicable)
- If using industry partner codebases, data-sharing agreement must allow publication of anonymized results
- Repo maintainers should be aware of study

---

## 13. Reporting Plan

### Main Report
- Report primary and secondary results per §8 (uncertainty quantification)
- Include 2×2 table of success rates by Agent × Context condition
- Forest plot of effect sizes across subgroups (if applicable)

### Supplementary Materials
- Variance component estimates and bootstrap CIs
- Full trajectory logs for 10% random sample (to enable process audits per 2609.00038.txt)
- Artifacts used (anonymized if necessary)
- R/Python analysis code (fully reproducible)
- Pre-registration document (this design)

### Limitations
- Limited to 30 tasks; may not generalize to other domains
- Only 2 agent products; results may not hold for other LLM vendors
- Hidden tests may not capture all aspects of PR quality
- Trajectory quality ratings subjective (interrater agreement documented but not perfect)

---

## 14. References to Evidence Consulted

This design draws on the following released evidence excerpts (evidence/ directory):

1. **2010.06595.txt**: Statistical power norms for NLP experiments; justifies power analysis and significance testing framework
2. **2310.11511.txt & 2403.14403.txt**: RAG and adaptive retrieval effectiveness; motivates context artifact as an intervention
3. **2405.14831.txt**: Persistent structured memory for LLMs; supports hypothesis that context artifacts can improve performance
4. **2605.30315.txt**: Paired resolution targets for LLM evaluation; informs uncertainty quantification and power requirements
5. **2606.07591.txt**: Hidden-target task benchmarking; justifies use of merged PRs with gold tests and rubric-based evaluation
6. **2607.09195.txt**: Auditable agent reasoning; motivates trajectory-level analysis and externalized belief state
7. **2607.13304.txt**: Variance components in LLM variability; guides optimal attempt allocation and variance decomposition
8. **2608.01913.txt**: Retrieval vs. utilization gaps; cautions against assuming all context is equally useful (ablation needed)
9. **2608.03501.txt**: Stage isolation in experimental design; supports clear redline metrics and outcome definitions
10. **2608.29517.txt**: Judge reliability; informs inter-rater agreement assessment for trajectory quality metric
11. **2609.00038.txt**: Outcome-only evaluation blind spots; justifies trajectory-level auditing beyond pass/fail

---

## 15. Summary Table

| Aspect | Design Decision | Justification |
|--------|-----------------|---------------|
| **Sample Size** | N = 30 tasks | ~80% power to detect 15–20% absolute effect (per 2010.06595.txt) |
| **Primary Comparison** | Fisher's exact test, Context A vs. B | Standard for binary outcomes; aligns with 2605.30315.txt resolution targets |
| **Ablation** | Minimal context (20% of tasks) | Tests priming vs. detailed knowledge (per 2608.01913.txt saturation question) |
| **Uncertainty** | Exact binomial 95% CIs + bootstrap | Addresses underpowering warning (2010.06595.txt); transparent MDE reporting |
| **Process Audit** | Trajectory quality ratings (2609.00038.txt) | Outcome-only evaluation misses wrong-path-right-answer cases |
| **Judge Reliability** | Krippendorff's α (2608.29517.txt) | Accounts for rater severity, halo, drift |
| **Variance Components** | Mixed logistic + bootstrap (2607.13304.txt) | Informs optimal repeat allocation for future studies |
| **Agents** | Claude Code + Codex | Contrasting architectures; two-vendor comparison prevents single-vendor bias |
| **Context Artifact** | Human-authored, domain-expert validated | Ensures quality; avoids auto-generated artifacts (per design principles) |
| **Reporting** | Preregistration + full transparency | Prevents HARKing (2608.03501.txt); enables replication |

---

**Study Status**: This is an experimental design document, not a results report. No data has been collected; all recommendations are prospective.

**Date Prepared**: [To be filled by investigator]

**Preregistration**: [Design should be preregistered at OSF Registries or equivalent before data collection]
