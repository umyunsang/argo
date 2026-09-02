# Experimental Design: Scaffolding vs. Model Contribution to Agent Capability Scores

## Research Question
How much of a published agent capability score comes from the scaffold rather than the model?

---

## 1. Main Comparison and Conditions

### Factorial Structure
**3 Scaffolds × 5 Models = 15 Cells**

#### Scaffold Factor (3 levels)
This experiment can only make sense of "scaffold" if three distinct, publicly instantiated agent harnesses are available. For design purposes, the scaffolds are placeholders; they must be identified empirically. The SCOPE evidence (2608.03501) distinguishes High-Level planning (main, ablation, analysis experiments) and Low-Level configuration (datasets, baselines, metrics). Three scaffolds could differ in, for example:

1. **Minimalist scaffold**: No externalized state beyond standard tool calls. Model receives task description, tool access, and terminal stdout.
2. **Structured scaffold**: Explicit phases (plan → code → execute → analyze) with gated transitions and formatted outputs at each step.
3. **Hypothesis-Evolution scaffold**: Based on HEP (2607.09195) — externalized hypothesis, evidence, and belief state; explicit test-evaluate-revise cycle with human-readable state logs.

These are illustrative; the actual scaffolds must be concrete, existing systems (e.g., Claude Code, OpenClaw, Codex with different harness configurations, or published agent frameworks).

#### Model Factor (5 levels)
Five LLM models spanning capability tiers. Example candidates:
- Claude Opus 4.7 (frontier)
- Claude Opus 4.6
- Claude Sonnet 4.5
- GPT-4.5 (or available comparable)
- Gemini 3.5-Flash (budget tier)

**Constraint**: Models must remain constant across all 15 cells. No fine-tuning or in-context adaptation specific to a scaffold (this confounds model identity with adaptation effects).

---

## 2. Task Benchmark and Conditions

### ResearchClawBench (2606.07591)
Use ResearchClawBench as the benchmark. Justification:
- 40 real scientific discovery tasks across 10 domains
- Spans Astronomy, Chemistry, Earth Science, Information Science, Life Science, Material Science, Mathematics, Neuroscience, Physics
- Each task grounded in a real published paper, with raw data and hidden target paper
- Expert-curated multimodal rubrics with weighted sub-criteria
- Hidden-target design prevents "target leak" during evaluation
- Rubric decomposes outputs into verifiable criteria (not single outcome-only judgment)

### Task Subset Selection
Do not attempt all 40 tasks in a first run (budget constraint). Select a **stratified subset of 12 tasks** (1–2 per domain) with the following criteria:
- Represent diverse domains
- Include both diagnostic analysis and metric optimization task types
- Vary in complexity (3 low, 4 medium, 5 high) based on expert difficulty rating in the benchmark
- Ensure raw data and rubric clarity to avoid interpretation drift

### Identity Conditions (Uniform Across All Cells)
- **Time budget**: Fixed wall-clock time per task (e.g., 30 minutes) or fixed interaction budget (e.g., max 50 tool calls); all model–scaffold pairs operate under the same constraint
- **Information access**: All cells receive the task description, related literature list, and raw data in identical form
- **Tool access**: Identical tool set (code execution, file I/O, basic computation) available to all cells
- **Target hiding**: Target papers remain hidden during task execution for all cells
- **No mid-task adaptation**: Scaffold behavior frozen once a model begins a task; no human intervention or guidance

---

## 3. Main Effect Isolation: Ablation Design

### Ablation 1: Model-Only Baseline
Run each of the **5 models in a "no-scaffold" condition**: expose the model to task text and data directly, with minimal tool access (standard API inference, no agentic loop). This is typically called a "ResearchHarness baseline" (2606.07591).

**Rationale**: The difference between (model in full scaffold) and (model with no scaffold) is the *marginal contribution of the scaffold to that specific model*. The model-only baseline isolates model intrinsic capability.

### Ablation 2: Scaffold-Only Substitution
Run each scaffold with a **single reference model** (e.g., Claude Opus 4.7) on a subset of tasks (6 of the 12). This tests whether scaffold benefits generalize across different conditions or whether they are model-dependent.

**Rationale**: If a scaffold's contribution is fixed across models, the scaffold–by–model interaction will be small. If the interaction is large, scaffold design is tightly coupled to the underlying model.

---

## 4. Outcome Metrics and Scoring

### Primary Outcome: Expert-Curated Rubric Score
Use ResearchClawBench's built-in rubric scoring for each task output:
- **Scale**: 0–100 points per task (ResearchClawBench uses hierarchical sub-criteria that sum to this range)
- **Anchoring**: 50 points = target-paper-level re-discovery; >50 = novel discovery
- **Rubric**: Same rubric applied to all 15 scaffold–model pairs for each task (no judge adaptation)

### Secondary Outcomes
1. **Task completion rate**: Proportion of tasks on which the model-scaffold pair produced a scoreable output (not errors, timeouts, or null responses)
2. **Rubric sub-dimension breakdown**: Score by each weighted sub-criterion (e.g., hypothesis accuracy, evidence appropriateness, output clarity) to detect whether scaffold effects are uniform across dimensions or concentrated in specific stages
3. **Trajectory quality** (from 2609.00038 evidence): Beyond outcome-only judging, log and score the step-by-step reasoning trajectory. A trajectory judge (step-level rubric) should evaluate:
   - Hypothesis-generation quality
   - Evidence-retrieval appropriateness (did the agent seek relevant sources?)
   - Integration of evidence into conclusions
   
   This separates loud failures (wrong answer) from silent failures (right answer via wrong reasoning).

### Non-Outcomes (Explicitly Avoided)
- **Raw token count or cost**: Do not report model efficiency trade-offs as part of capability measurement; they confound cost with competence
- **Human agreement alone**: Avoid agreement-only metrics (correlation, kappa); these cannot detect severity drift (2608.29517) or silent failures (2609.00038)
- **Single-judge LLM scores**: If LLM-as-judge is used for any secondary evaluation, use a panel (at least 3 independent judges, possibly different models) and report judge variance; do not average without reporting disagreement (2608.29517)

---

## 5. Analysis Plan

### 5.1 Main Factorial ANOVA
Conduct a **two-way mixed-model ANOVA** (or linear mixed-effects regression):
- **Fixed effects**: Scaffold (3 levels), Model (5 levels), Scaffold × Model interaction
- **Random effects**: Task (12 levels, crossed; tasks are generalizable targets, not fixed effects)
- **Outcome**: Rubric score per observation (model-scaffold-task triplet)

**Expected output**:
```
Effect                  Sum of Squares    df    F       p
Scaffold                [SS_sc]           2     F_sc    p_sc
Model                   [SS_md]           4     F_md    p_md
Scaffold × Model        [SS_int]          8     F_int   p_int
Task                    [SS_tk]           11    F_tk    p_tk
Residual                [SS_res]          [df]
```

**Interpretation**:
- If p_sc << 0.05 and F_sc is large, scaffold effects are substantial
- If p_md << 0.05 and F_md is large, model effects are substantial
- If p_int is large, scaffold choice matters more for some models than others

### 5.2 Variance Decomposition (Generalizability Theory)
Following the method in 2607.13304, decompose total score variance into:
- Variance due to **Scaffold** (effect size: σ²_scaffold / σ²_total)
- Variance due to **Model** (effect size: σ²_model / σ²_total)
- Variance due to **Scaffold × Model interaction** (confounding; interpretation depends on design intent)
- Variance due to **Task** (background heterogeneity across tasks)
- Residual variance

**Output**: Intraclass correlations (ICCs) for each facet, showing what proportion of observed score variance stems from each source. This directly answers the research question: *What percentage of score variance is attributable to scaffold vs. model?*

### 5.3 Ablation Effect Size
For each model *m*, compute the **marginal contribution of scaffold to model m**:
```
ΔScore(m, s) = Score(m with scaffold s) − Score(m with no scaffold)
```

Aggregated across tasks:
```
MarginalEffect_scaffold = Mean over models of [ΔScore(m, s1) − ΔScore(m, s2)]
MarginalEffect_model = Mean over scaffolds of [ΔScore(m1, s) − ΔScore(m2, s)]
```

Compare via t-tests on the differences to assess whether scaffold or model contributes larger absolute gains.

### 5.4 Interaction Interpretation
Plot a **Scaffold × Model heatmap** showing mean rubric score in each cell. Examine:
- Are the lines parallel (no interaction) → effects are additive
- Do the lines cross (strong interaction) → one scaffold works best only for certain models
- Which model-scaffold pair achieves the highest score? Does the winner scaffold change when you swap the model?

If the best-performing pair involves a specific (scaffold, model) combination, report this as evidence that they are synergistic or co-optimized.

### 5.5 Task-Level Heterogeneity
Conduct a **stratified analysis by task domain** (Astronomy, Chemistry, …):
```
For each domain d:
  ANOVA(Score ~ Scaffold + Model + Scaffold:Model | domain = d)
  Report F-statistics and effect sizes for each domain
```

**Rationale** (from 2608.03501 evidence): Agent behavior on experimental design was highly bottleneck-dependent, not uniform. Scaffold and model may interact differently on analytical vs. optimization tasks, or on data-heavy vs. reasoning-heavy domains.

### 5.6 Trajectory-Level Ablation
Score a **random sample of 20–30 trajectories** (from the 12 × 15 = 180 model-scaffold-task runs, select ~20 from high-performing and low-performing pairs) using the step-level rubric (2609.00038):
- Outcome-only judge: score based on final result alone
- Trajectory judge: score based on reasoning steps and evidence integration
- **Report disagreement**: For what fraction of tasks does the trajectory judge change the quality verdict? This flags silent failures and points to whether scaffold effects are visible in reasoning or only in outcomes.

---

## 6. Uncertainty Quantification

### 6.1 Statistical Power and Resolution
Use the framework from 2605.30315 (paired resolution diagnostics).

**Setup**: For any pairwise comparison of two conditions (e.g., Scaffold A vs. Scaffold B, aggregated over all models and tasks), treat the 12 tasks as a paired sample.

```
Δ = Score(A) − Score(B), per task
N = 12 (number of tasks in the paired sample)
σ_D = Std(Δ)
```

Compute the **resolution ratio**:
```
q = N / N_star(Δ_observed; α=0.05, power=0.80)
```

- If q ≥ 1, the gap is "resolved" at the 0.05 significance level with 80% power
- If q < 1, the observed gap is underpowered; the true difference cannot be distinguished from sampling noise

**Report for all main comparisons**: Scaffold A vs. B, Scaffold A vs. C, Scaffold B vs. C, and each Model pair. This flags which comparisons have adequate power.

### 6.2 Variance Components with Confidence Intervals
Fit the generalizability-theory model (Section 5.2) and report:
- **Point estimates** of variance components (σ²_scaffold, σ²_model, σ²_int, σ²_task, σ²_res)
- **95% Confidence intervals** via cluster bootstrap (resample tasks, refit model, re-estimate components) or via residual bootstrap (following 2607.13304 methods)
- **Marginal ICC for scaffold** (proportion of total variance explained by scaffold, with CI)
- **Marginal ICC for model** (proportion of total variance explained by model, with CI)

### 6.3 Non-Determinism and Repeat Allocation
Run each of the **highest-impact cell pairs** (top 3 Scaffold-Model combinations by mean score and the bottom 3) a total of **K=3 times each** (i.e., 3 runs per model-scaffold-task triplet on these 6 cells).

**Rationale** (from 2607.13304): A single run per cell has noise (temperature, internal sampling). By replicating a subset, you can estimate within-cell variance and derive a tighter confidence interval on the marginal effects.

```
Variance breakdown for replicated cells:
σ²_total = σ²_cell + σ²_residual_within
```

Use this to **correct the main ANOVA**: include cell-level random effects to account for run-to-run variation within the model-scaffold condition.

### 6.4 Judge Severity and Stability
Since rubric scores will be assigned (manually by experts or via LLM-as-judge), audit the scoring process:

**If LLM-as-judge is used** (2608.29517 framework):
- Have **multiple judges** (at least 3 different models or human experts) score a 10% random sample (2 tasks × 15 cells = 30 triplets)
- Compute intraclass correlations (ICC) and rank-order agreement among judges
- Report **judge severity** (mean score per judge) and whether judges agree on which model-scaffold pairs are best
- Flag if any judge is a "stray" outlier in severity; if so, flag those scores and conduct a sensitivity analysis (rerun main analysis excluding that judge)

**If human expert judges**: 
- Use a **double-blind design**: judges score outputs without knowing which model or scaffold produced them
- Have **at least 2 independent raters** score each output; report inter-rater reliability (Kendall's τ or ICC)
- Track **rater drift** (do scores drift over time as judges become fatigued?); use a paired anchor set (5 reference outputs scored by all raters at the start and end)

### 6.5 Sensitivity Analysis: Effect of Rubric Interpretation
Run the same analysis twice:
1. **Strict rubric**: Score only if output exactly matches rubric criteria (zero if ambiguous)
2. **Loose rubric**: Give partial credit and the benefit of the doubt

Report whether conclusions change (e.g., model and scaffold rankings flip). If they do, report this as sensitivity to rubric interpretation.

---

## 7. Concrete Resources

### 7.1 Benchmark
- **ResearchClawBench**: Available at https://github.com/InternScience/ResearchClawBench
  - Download dataset from HuggingFace: https://huggingface.co/datasets/InternScience/ResearchClawBench
  - Use 12 stratified tasks (not all 40, for budget reasons)

### 7.2 Scaffolds
**Placeholder identities; must be finalized empirically:**
1. Scaffold A: Name, GitHub link, reference paper
2. Scaffold B: Name, GitHub link, reference paper
3. Scaffold C: Name, GitHub link, reference paper

Each must be:
- Publicly available and installable
- Documented enough to run identically across model choices
- Capable of accepting a ResearchClawBench task description and returning a structured output

### 7.3 Models
- **Claude Opus 4.7**: Access via Anthropic API (requires API key; costs apply)
- **Claude Opus 4.6**: Access via Anthropic API
- **Claude Sonnet 4.5**: Access via Anthropic API
- **GPT-4.5 or comparable**: OpenAI API (alternative: LLaMA-405B or other open-weights model if cost is prohibitive)
- **Gemini 3.5-Flash**: Google AI Studio API (free tier available)

### 7.4 Judge Panel (if LLM-as-judge)
- Claude Opus 4.7 (primary judge)
- Gemini 3.5-Pro or similar (secondary judge)
- Human expert (1 researcher with domain expertise in the task domains, or rotating experts per domain)

### 7.5 Software & Analysis
- **ANOVA & mixed models**: R (lme4 package), Python (statsmodels, scipy), or SPSS
- **Variance components**: R (ICC package, lme4), or Python (statsmodels.MixedLM)
- **Confidence intervals**: cluster-bootstrap (R: boot package; Python: np.random.choice resampling)
- **Visualization**: Heatmaps (seaborn, ggplot2), forest plots for effect sizes and CIs
- **Tracking**: Spreadsheet or database to log all 180+ runs (12 tasks × 15 cells, plus repeats), with timestamps, model version, scaffold hash/commit, and raw scores

---

## 8. Expected Outcomes & Interpretation

### Scenario A: Model Dominates
**If F_md >> F_sc and σ²_model >> σ²_scaffold:**
- Conclusion: Agent capability is primarily driven by the underlying LLM, not the scaffold choice
- Implication: Research should prioritize better models; scaffold engineering has lower leverage
- Report: "Scaffold contributes X% of variance; model contributes Y%."

### Scenario B: Scaffold Dominates
**If F_sc > F_md and σ²_scaffold > σ²_model:**
- Conclusion: Architecture and task orchestration matter more than model capacity
- Implication: Scaffold innovations (planning, reflection, explicit state) can unlock capability in weaker models
- Report the rank order of scaffolds by mean score; identify which mechanisms (planning structure, state externalization, etc.) correlate with success

### Scenario C: Synergy (Interaction Effects)
**If the Scaffold × Model interaction F-stat is large and p_int < 0.05:**
- Conclusion: Scaffold effectiveness is model-dependent; no one scaffold is universally best
- Implication: Practitioners should match scaffolds to their chosen model
- Report: Which (scaffold, model) pairs are most synergistic? Does a cheap model + great scaffold outperform a great model + minimal scaffold?

### Scenario D: Additive Effects (No Interaction)
**If lines are parallel in the Scaffold × Model heatmap:**
- Conclusion: Scaffold and model effects are independent; improvements stack
- Implication: Both matter; optimize both independently for maximum capability

---

## 9. Timeline & Milestones

| Phase | Duration | Deliverable |
|-------|----------|------------|
| Scaffold identification & setup | 2 weeks | Confirm 3 scaffolds; set up execution environment |
| Model access & environment setup | 1 week | Verify API keys, rate limits, cost budgets |
| Task subset selection & validation | 1 week | Choose 12 tasks; pilot on 1 task with all 15 cells |
| Pilot run (1 task, all 15 cells) | 1 week | Confirm rubric scoring, identify bottlenecks, adjust time budgets |
| Main run (12 tasks × 15 cells = 180 runs) | 4–6 weeks | Execution; log outputs; store raw responses |
| Repeat runs (6 high-impact cells × K=3) | 1 week | Run repeats; estimate within-cell variance |
| Trajectory scoring (20–30 samples) | 1 week | Step-level rubric annotation; outcome vs. trajectory comparison |
| Analysis & statistical testing | 2 weeks | ANOVA, variance components, CIs, sensitivity analysis |
| Report writing | 1 week | Synthesis, figures, interpretation, and final draft |

**Total**: ~15–17 weeks (≈4 months)

---

## 10. Key Reporting Requirements

1. **Primary claim**: State as a single percentage decomposition:
   - "Scaffold effects account for X% of total score variance (95% CI: [a%, b%])"
   - "Model effects account for Y% of total score variance (95% CI: [c%, d%])"
   - "Residual (interaction + task heterogeneity) accounts for Z% (95% CI: [e%, f%])"

2. **Power summary table**: For each pairwise comparison, report:
   - Observed gap (Δ)
   - Resolution ratio (q)
   - Whether resolvable at (α=0.05, power=0.80)

3. **Rubric sub-dimension breakdown**: For each of the 5–7 weighted sub-criteria in ResearchClawBench, report effect sizes separately. Indicate whether scaffold and model effects are uniform across dimensions or concentrated (e.g., scaffold helps with planning but not evidence retrieval).

4. **Trajectory findings**: Report the fraction of tasks on which outcome-only judges and trajectory judges disagree; describe the types of silent failures that trajectory-level evaluation catches.

5. **Judge audit** (if applicable): Intraclass correlation among judges, severity coefficients, and any drift detected. Flag cells with low inter-judge agreement.

6. **Interaction heatmap**: Publication-quality figure showing mean score in each Scaffold × Model cell, with overall annotations and call-outs to the highest- and lowest-performing pairs.

7. **Sensitivity analysis**: Report whether conclusions remain stable under strict vs. loose rubric scoring and under different judge panels.

---

## 11. Limitations & Open Questions

### Limitations
- **Task generalization**: Results are specific to ResearchClawBench. Findings may not transfer to other multi-step benchmarks (e.g., coding tasks, dialogue, open-ended writing).
- **Scaffolds as implemented**: We measure specific instantiations of scaffolds; another implementation of the same scaffold design might yield different results.
- **Cost confounding**: If models vary in cost, high-cost models may have unfair advantages from higher query budgets or different service tiers; time/token budgets must be strictly controlled.
- **Time-to-performance trade-off**: A scaffold might enable longer reasoning chains, which could favor test sets where reasoning time is beneficial; this is a feature, not a bug, but should be acknowledged.

### Open Questions
1. **Do scaffolds transfer?** If Scaffold A wins on ResearchClawBench, does it also win on code generation or dialogue tasks? (Design would need to add additional benchmarks.)
2. **Can weaker models match stronger ones with better scaffolds?** E.g., can Gemini Flash + HEP scaffold outperform Claude Opus 4.7 + minimal scaffold? (Interact effect analysis will partly answer this.)
3. **Is the scaffold contribution model-specific?** Do the same three scaffolds rank identically for all five models? (Interaction analysis addresses this.)

---

## 12. References to Cited Evidence

The following evidence excerpts from ./evidence/ informed this design:

1. **2606.07591** (ResearchClawBench): Task benchmark selection, rubric design, and hidden-target evaluation protocol
2. **2608.03501** (SCOPE): Experimental design methodology, stage isolation, redline scoring, and ablation structure
3. **2607.13304** (Variance components): Generalizability theory, decision-study allocation, and crossed-effects decomposition
4. **2605.30315** (Resolution diagnostics): Paired statistical testing, minimum detectable effects, and resolution ratio calculation
5. **2608.29517** (LLM judges as raters): Judge severity audit, pre-registered protocols, and rater-effects quantification
6. **2609.00038** (Trajectory-level judging): Outcome-only vs. step-level evaluation, silent failures, and comprehensive trajectory rubrics
7. **2607.09195** (Hypothesis Evolution Protocol): Example of an externalized-state scaffold and its effects on agent behavior

---

## Conclusion

This design isolates the contributions of **scaffold** and **model** to published agent capability scores by:

1. Treating them as crossed factors in a factorial experiment (3 scaffolds × 5 models)
2. Using a validated benchmark with expert rubrics (ResearchClawBench, 12 stratified tasks)
3. Applying a pre-registered analysis plan that decomposes variance into sources
4. Quantifying uncertainty via power diagnostics, confidence intervals, and sensitivity checks
5. Examining interaction effects to assess whether their contributions are additive or synergistic

The experiment directly answers the research question: **How much of published agent capability comes from scaffold vs. model?** with a precise variance-components answer, confidence intervals, and actionable implications for agent research and practice.
