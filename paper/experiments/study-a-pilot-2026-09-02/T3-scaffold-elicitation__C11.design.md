# Complete Experimental Design: Scaffold Contribution to Agent Capability Scores

## Executive Summary

This design measures how much of a published agent capability score comes from the evaluation scaffold (harness design, task structure, rubric composition) versus the underlying model capability. We employ a 3×5 factorial crossing three scaffolds and five language models on the ResearchClawBench benchmark (40 real scientific discovery tasks across 10 domains). The sampling frame samples from 600 (scaffold, model, task) triplets. Analysis decomposes total score variance into scaffold main effects, model main effects, interaction effects, and task-stratified signal.

---

## 1. Research Question and Design Structure

**Research Question** (from state.md): How much of a published agent capability score on scientific discovery tasks comes from the evaluation scaffold versus the underlying model capability?

**Design Type**: Crossed 3×5 factorial on shared benchmark.

**Sampling Frame** (from state.md): ResearchClawBench 40-task corpus spanning 10 scientific domains (Astronomy, Chemistry, Earth Science, Energy Science, Information Science, Life Science, Material Science, Mathematics, Neuroscience, Physics). Each (scaffold, model) pair is evaluated on all 40 tasks, yielding 3×5×40 = 600 observations total.

---

## 2. Scaffolds (Three Levels)

### 2.1 Scaffold A: ResearchHarness (Lightweight Baseline)

**Source**: 2606.07591 (ResearchClawBench paper)

**Description**: ResearchHarness is the reference-implementation lightweight evaluation harness for native LLM baselines in ResearchClawBench. It provides:
- Unified tool-use interface (file I/O, code execution, literature search)
- Minimal instruction structure: task description + success criteria + output format
- No explicit planning, hypothesis evolution, or reflection scaffolding
- Single-turn or few-turn interactions (not multi-step agentic loops)

**Rationale**: Establishes the lower-complexity baseline. Differences from the other scaffolds directly measure the value of additional structure.

### 2.2 Scaffold B: HEP Protocol (Hypothesis Evolution Harness)

**Source**: 2607.09195 (Toward Auditable AI Scientists)

**Description**: The Hypothesis Evolution Protocol (HEP) is an agent harness that structures the research process around explicit, auditable hypothesis generation, testing, and belief revision:
- Externalizes hypothesis state as a timestamped log entry
- Requires model to evaluate hypotheses against evidence in a structured form
- Implements belief-update cycles (hypothesis → test → evidence → belief revision)
- Provides checkpoints for human or automated audit of reasoning
- Generalizes across research questions in materials science and related domains

**Rationale**: Adds explicit structure to reasoning without full pipeline scaffolding. Tests whether hypothesis-aware reasoning improves scores independently of tool availability.

### 2.3 Scaffold C: OptED Workflow (Stage Isolation + Rule-Based Constraints)

**Source**: 2608.03501 (SCOPE: Can LLM Design High-Quality Experiments?)

**Description**: OptED is an agentic workflow that addresses the "configuration bottleneck" by:
- Decomposing experimental design into high-level planning (main, ablation, analysis experiments) and low-level configuration (dataset, baseline, metric selection)
- Stage isolation: forcing sequential completion of planning before configuration
- Tool augmentation: providing LLM-accessible constraint libraries (e.g., "valid datasets for domain X")
- Rule-based constraint enforcement: blocking invalid configurations (e.g., baseline must be older than target model date)

**Rationale**: Adds domain-specific constraints and decomposition. Tests whether forced structure and rule checking improve score, accounting for planning vs. configuration depth.

---

## 3. Models (Five Levels)

Models are selected from ResearchClawBench leaderboard results to span capability range and representation:

1. **Claude-Opus-4.7**: Highest-capability LLM in ResearchClawBench (20.7 points, 2606.07591)
   - Dense capabilities across domains
   - Established tool-use and reasoning baseline
   - Sufficient capability to show ceiling effects with strong scaffolds

2. **Qwen-3.7-Max**: Mid-high capability (18.7 points in ResearchClawBench, 2606.07591)
   - Represents non-Claude frontier capability
   - Good domain coverage
   - Different model family to test generalization

3. **Gemini-3.5-Flash**: Mid-capability, speed-optimized (17.0 points in ResearchClawBench, 2606.07591)
   - Designed for latency; tests scaffold effect on fast-turn models
   - Lower inherent capability to show floor effects with weak scaffolds

4. **DeepSeek-V4-Pro**: Alternative high-capability model (position unspecified in RCBench, mentioned in Figure 1a)
   - Different training approach (claimed efficiency focus)
   - Potential for scaffold × model interaction effects

5. **Kimi-K2.6**: Mid-high capability (18.2 points in ResearchClawBench, 2606.07591)
   - Good task coverage
   - Establishes model diversity (Chinese-trained foundation)

**Selection Rationale**: Range from 17–20.7 base points (ResearchHarness scores from 2606.07591). This variance ensures detection of scaffold effects across capable and less-capable models. All five have published scores on ResearchClawBench, enabling comparison to prior results.

---

## 4. Benchmark and Tasks

**Benchmark**: ResearchClawBench (2606.07591)

**Task Corpus**: 40 end-to-end scientific discovery tasks grounded in real published papers:
- 10 scientific domains (Astronomy, Chemistry, Earth Science, Energy Science, Information Science, Life Science, Material Science, Mathematics, Neuroscience, Physics)
- 4 tasks per domain
- Each task provides: research question, related literature, raw experimental data
- Target paper is hidden during evaluation to prevent memorization

**Rubric Design**: Expert-curated multimodal rubrics decompose scientific artifacts into weighted criteria. Scoring is anchor-based:
- Score ≥ 50: target-paper-level re-discovery (matches published results)
- Score > 50: novel discovery beyond target paper
- Score < 50: partial or incomplete results

**Why ResearchClawBench**: 
- Sufficient task count (40 tasks) to enable stratified analysis by domain
- Published rubrics and domain expertise embedded
- Real grounding (tasks from published papers) reduces design-artifact risk
- Existing baseline scores (autonomous agents 13.6–21.5, native LLMs 14.0–20.7) provide calibration

---

## 5. Main Comparison and Ablations

### 5.1 Main Comparison: Factorial Effects

**Primary Analysis**: Decompose total score variance via crossed random-effects ANOVA:

```
Score(i,j,k) = μ + Scaffold(i) + Model(j) + Task(k) + 
                Scaffold×Model(i,j) + Scaffold×Task(i,k) + 
                Model×Task(j,k) + ε(i,j,k)
```

where:
- i ∈ {1,2,3} for scaffolds
- j ∈ {1,2,3,4,5} for models  
- k ∈ {1,2,...,40} for tasks

**Outcome**: Variance components and intraclass correlations for each term. The question "how much comes from scaffold?" is answered by comparing:
- σ²(Scaffold) / [σ²(Scaffold) + σ²(Model) + σ²(Interaction) + σ²(Residual)]

### 5.2 Ablation 1: Scaffold Contribution Across Model Capability Tiers

**Design**: Stratify results by model-performance tier:
- High: Claude-Opus-4.7, Qwen-3.7-Max, DeepSeek-V4-Pro (base scores ~18–20.7)
- Mid: Kimi-K2.6 (base score ~18)
- Low: Gemini-3.5-Flash (base score ~17)

**Hypothesis**: Scaffold effects may interact with model capability (weak models may benefit more from scaffolding structure; strong models may show ceiling effects). ANOVA within each tier measures whether scaffold main effects are consistent.

### 5.3 Ablation 2: Scaffold Effect by Domain

**Design**: Within each of the 10 scientific domains, measure scaffold contribution:
- Astronomy (4 tasks), Chemistry (4 tasks), ... Physics (4 tasks)

**Hypothesis**: Some domains may rely more on task structure (e.g., experimental design in Chemistry benefits more from OptED constraints) while others may rely more on model reasoning (e.g., theoretical prediction in Physics).

**Analysis**: F-test for Scaffold × Domain interaction. If significant, report domain-stratified effect sizes (Cohen's d or partial η²).

### 5.4 Ablation 3: Outcome-Only vs. Trajectory-Aware Scoring

**Design** (informed by 2609.00038): Two scoring modes for all 600 (scaffold, model, task) combinations:
- Outcome-only: Score final research output against rubric (baseline, matches ResearchClawBench)
- Trajectory-aware: Score process and output together (e.g., did model follow valid research steps? Did it correct errors after evidence?)

**Hypothesis**: HEP and OptED scaffolds may improve trajectory quality (structured reasoning) without improving final outcomes. Outcome-only scoring would underestimate their value.

**Analysis**: Correlation between outcome-only and trajectory scores; separate variance components for each. Measure whether scaffold effects on trajectory differ from effects on outcomes.

---

## 6. Outcome Metrics

### 6.1 Primary Metric: Rubric Score (0–100)

**Definition**: Score assigned by ResearchClawBench expert rubric for each (scaffold, model, task) triplet.

**Anchor**: Score 50 = target-paper re-discovery; <50 = incomplete; >50 = novel discovery.

**Properties**: Interval-scale, bounded [0, 100], multimodal (assessor-dependent, see 2608.29517).

### 6.2 Secondary Metrics

**6.2.1 Re-discovery Rate (RDR)**
- Proportion of tasks where score ≥ 50 (target-paper level or better)
- Binary metric; directly interpretable ("system reliably achieved published result")
- Calculated per (scaffold, model) pair: RDR(i,j) = (# tasks with score ≥ 50) / 40

**6.2.2 Score Variance (Per Model)**
- SD of scores across all 40 tasks for a given scaffold-model pair
- Indicates consistency; high variance = inconsistent performance across domains
- May indicate poor generalization of scaffold effect

**6.2.3 Threshold Hit Rate (Stratified)**
- Proportion of tasks where 40 ≤ score < 60 (threshold zone)
- These are high-stakes cases where rubric judgment is most critical
- Measured to monitor scoring reliability in the "hardest to judge" region

**6.2.4 Trajectory Fidelity (if trajectory-aware scoring implemented)**
- Subset of trajectory checkpoints (e.g., "model proposed hypothesis") achieved
- Measured via step-rubric from 2609.00038 approach
- Intended to separate reasoning-process improvements from outcome improvements

### 6.3 Uncertainty Quantification

See Section 7 for detailed statistical methods.

---

## 7. Analysis Plan and Uncertainty Quantification

### 7.1 Variance Decomposition

**Method**: Crossed random-effects ANOVA with generalizability theory (informed by 2607.13304).

**Data Structure**: 
- 600 observations (3 scaffolds × 5 models × 40 tasks)
- Each observation is a single rubric score
- To estimate resampling variance (if models are non-deterministic), plan ≥2 runs per (scaffold, model, task) triplet if computational budget allows; treat as nested within-cell replicates

**Model Fitted**:
```R
lmer(score ~ 1 + (1|scaffold) + (1|model) + (1|task) + 
       (1|scaffold:model) + (1|scaffold:task) + 
       (1|model:task) + (1|residual), 
     data = design_data)
```

**Output**: Variance components, confidence intervals (REML-based), intraclass correlations (ICC) per component.

**Interpretation of Main Comparison**:
- Partition variance: σ²_total = σ²_S + σ²_M + σ²_SM + σ²_ST + σ²_MT + σ²_e
- Scaffold contribution: η²_S = σ²_S / σ²_total
- Model contribution: η²_M = σ²_M / σ²_total
- If η²_S > η²_M, scaffold matters more; if η²_M > η²_S, model matters more

**Confidence Intervals**: Report 95% CIs for each η² via bootstrap (10,000 iterations over tasks and models, holding scaffolds constant, then averaging).

### 7.2 Moderation Analysis (Ablation 1: Model Tier)

**Method**: Separate ANOVA per tier (High, Mid, Low capability models).

**Analysis**:
- Fit the same factorial model separately for each tier
- Compare η²_S across tiers via chi-square test for homogeneity of variance
- If η²_S differs significantly across tiers, report effect size per tier

**Interpretation**: If high-capability models show smaller scaffold effects, indicates ceiling effect (scaffold matters less when model is already strong).

### 7.3 Domain Stratification (Ablation 2)

**Method**: Nested ANOVA with domain as a blocking factor.

**Model**:
```R
lmer(score ~ 1 + scaffold + model + scaffold:model + 
       (1|domain) + (1|domain:scaffold) + 
       (1|domain:model) + ..., 
     data = design_data)
```

**Test**: Significance of Scaffold × Domain interaction (F-test, α = 0.05 after Bonferroni correction for 10 domains).

**Visualization**: Plot scaffold effect size (Cohen's d relative to ResearchHarness baseline) on the y-axis, domains on the x-axis, separate lines per scaffold.

### 7.4 Scoring Reliability (Informed by 2608.29517, 2609.00038)

**Multiple Validation Checkpoints**:

1. **Human Consensus Check** (stopping rule, per state.md):
   - Recruit ≥2 independent human raters (domain experts) to score ≥80% of tasks in the "threshold zone" (score 40–60)
   - Calculate inter-rater reliability: Fleiss' κ on task-level scoring (3-point outcome scale: incomplete, re-discovery, discovery)
   - Require κ ≥ 0.65 (substantial agreement); rescore and adjudicate if lower

2. **Judge Severity Audit** (informed by 2608.29517):
   - If using LLM judges (e.g., Claude as secondary scorer), pin model version and run replicates (≥5 independent runs) on a fixed validation subset (10 tasks, 2 models)
   - Measure judge severity drift: does the model's score shift by >10 points across runs?
   - If drift > 10 points, use ensemble average of runs and report uncertainty in main results

3. **Outcome-Only Blind Spot Check** (informed by 2609.00038):
   - For a random subset (10 tasks × 3 scaffolds), have human reviewers independently score using:
     a) Outcome-only judgment (final report only)
     b) Trajectory-aware judgment (intermediate steps + final output)
   - Compare outcomes: does trajectory-aware judgment surface failures missed by outcome-only?
   - If |correlation| < 0.7, report discrepancy and reweight analysis toward trajectory-aware scoring

### 7.5 Missing Data and Sensitivity

**Handling**: If a (scaffold, model, task) cell fails (e.g., model crashes, timeout), impute via:
- Mean imputation from same model, different scaffold (assumes scaffold is missing at random given model and task)
- Report number of imputations; refrain from claiming complete data

**Sensitivity Analysis**:
- Fit model twice: once with imputations, once with complete-case analysis
- Compare conclusions (e.g., rank order of scaffolds); if rank order flips, flag as sensitivity-dependent result

### 7.6 Multiple Comparison Correction

**Method**: For follow-up comparisons (e.g., pairwise t-tests between scaffolds), apply Benjamini-Hochberg FDR correction (α = 0.05 adjusted).

**Rationale**: Controls expected proportion of false discoveries while preserving power (motivated by 2010.06595 on statistical power norms for NLP).

---

## 8. Concrete Resources

### 8.1 Tasks and Benchmark

- **Benchmark**: ResearchClawBench v2606.07591 (40 tasks, 10 domains)
- **Data source**: https://huggingface.co/datasets/InternScience/ResearchClawBench (per 2606.07591)
- **Rubrics**: Provided in ResearchClawBench; expert-curated scoring guidelines per domain
- **Computation**: Each task requires ~5–30 minutes per (scaffold, model) pair (estimated from 2606.07591 agent run times). Total compute budget: ~450–2,700 core-hours for 600 evaluations (parallelizable)

### 8.2 Scaffolds

**Scaffold A: ResearchHarness**
- Reference implementation: ResearchClawBench GitHub repository (https://github.com/InternScience/ResearchClawBench)
- Tool set: file I/O, code execution (Python), literature search (arXiv API)
- License: Open-source (per 2606.07591)

**Scaffold B: HEP Protocol**
- Source: 2607.09195 (Toward Auditable AI Scientists)
- GitHub: https://github.com/InternScience/HEP-Protocol (if public; note: paper provides pseudocode and conceptual description)
- Implementation strategy: Adapt ResearchHarness + add hypothesis-log data structure and belief-update enforcement
- **Limitation**: Paper does not provide reference code; implementation requires engineering

**Scaffold C: OptED**
- Source: 2608.03501 (SCOPE paper)
- GitHub: Claimed available upon publication (per paper)
- Core components: Stage-separation logic, constraint library (domain-specific rule sets), LLM-accessible lookup function
- **Limitation**: OptED is described for experimental-design tasks; adaptation to full ResearchClawBench may require domain customization (e.g., constraint sets for Astronomy tasks)

### 8.3 Models

All five models are cloud-hosted via standard APIs (OpenAI, Google Cloud, Alibaba Damo Academy, DeepSeek, Moonshot AI):

1. **Claude-Opus-4.7**: Anthropic API (claude-opus-4.7 identifier, if available; fall back to latest Opus)
2. **Qwen-3.7-Max**: Alibaba Damo Academy (qwen-3.7-max via Dashscope API or equivalent)
3. **Gemini-3.5-Flash**: Google Cloud AI (google/gemini-3.5-flash)
4. **DeepSeek-V4-Pro**: DeepSeek API (deepseek-chat-v4-pro or latest)
5. **Kimi-K2.6**: Moonshot AI (moonshot-v2.6 or kimi-k2.6)

**Cost Estimate**: Assuming ~$0.01–0.10 per task-run (model-dependent), total inference cost: ~$60–600 for 600 runs (includes retries).

### 8.4 Evaluation and Scoring

- **Primary Scoring**: Rubrics from ResearchClawBench + human-consensus checkpoint (stopping rule)
- **Human Raters**: ≥2 domain experts per domain (10 domains × 2 = 20 person-task-allocations). Each expert scores ~20 high-stakes tasks (40–60 zone)
- **Tool Stack**: ResearchClawBench evaluation harness (Python) + Hugging Face Datasets API + analysis in R (lme4 package) or Python (scipy, statsmodels)

---

## 9. Quality Assurance and Robustness

### 9.1 Preregistration

**Action**: Register this design on OSF (Open Science Framework) or Zenodo before running any scaffold-model evaluation. Include:
- Sampling frame (3×5×40)
- Variance decomposition model
- Definition of η² (scaffold contribution)
- Threshold for falsification (η²_S < 5% = null result)

**Rationale**: Prevents p-hacking and post-hoc hypothesis adjustment (motivated by 2010.06595 on statistical power).

### 9.2 Model Version Pinning

(Informed by 2608.29517 judge-drift finding)

**Action**:
- Pin model API versions at trial start (e.g., "claude-opus-4.7, as of 2026-Q3")
- Run replicates on a fixed validation set (5 tasks, 3 scaffolds) monthly to detect version drift
- If model provider updates the API mid-trial, update the registry and refit all prior analyses with the new version on a validation subset

### 9.3 Task Ordering and Randomization

**Action**:
- Randomize task order per (scaffold, model) pair to avoid order effects
- Use a fixed random seed (e.g., seed=42) to ensure reproducibility
- Log the seed in all reports

---

## 10. Expected Outcomes and Decision Boundaries

### 10.1 Plausible Scenarios

**Scenario A: Model Dominates** (η²_M >> η²_S)
- Outcome: Model capability accounts for >70% of variance; scaffold <10%
- Interpretation: Agent capability is primarily determined by base model; scaffolding is secondary
- Follow-up: Invest in model pretraining, not harness engineering

**Scenario B: Scaffold and Model Balanced** (η²_S ≈ η²_M ≈ 30–40%)
- Outcome: Both factors contribute substantially
- Interpretation: Harness design and model capability are both critical
- Follow-up: Co-optimize both; avoid narrow focus on either

**Scenario C: Scaffold Dominates** (η²_S >> η²_M)
- Outcome: Scaffold accounts for >50% of variance; model <20%
- Interpretation: Structure and task design are the primary performance drivers
- Follow-up: Invest in harness-engineering and domain-specific scaffolds
- Concern: If true, published agent scores may be artificially inflated by scaffolds; reframe capability claims

**Scenario D: Falsified** (Interaction effects dominate)
- Outcome: Scaffold × Model interaction variance > main-effect variance
- Interpretation: Factorial structure is invalid; effects are non-additive
- Follow-up: Redesign as pairwise comparisons; study specific (scaffold, model) synergies rather than main effects

### 10.2 Decision Rules

| η²_S (Scaffold) | η²_M (Model) | Decision |
|---|---|---|
| < 5% | > 50% | Model dominates; scaffold is minimal |
| 5–20% | 40–50% | Model leads; scaffold is modulator |
| 20–40% | 20–40% | Balanced contributions |
| > 40% | < 20% | Scaffold leads; model is enabler |
| Interaction > 50% | — | Design is non-additive; requires reanalysis |

---

## 11. Reporting and Transparency

### 11.1 Deliverables

1. **Preregistration report** (before running)
2. **Main results table**: Variance components, η² per factor, 95% CIs
3. **Ablation results**: Moderation by model tier, domain stratification, trajectory-aware scoring comparison
4. **Visualization**: 
   - Heatmap of mean scores (rows = models, columns = scaffolds; cells shaded by score)
   - Forest plot of η² confidence intervals (one per factor)
   - Interaction plot (if Scaffold × Model is significant)
5. **Sensitivity analysis**: Complete-case vs. imputation, effect-size comparisons
6. **Code and data**: All R/Python scripts, cleaned data (anonymized if human raters), rubrric definitions, provided on GitHub

### 11.2 Transparency Notes

- Report all statistical tests and p-values (Bonferroni-corrected where applicable)
- Disclose judge-severity audits and any model-version drift detected during the trial
- Acknowledge limitations: HEP and OptED scaffolds lack reference implementations; domain-specific rule sets for OptED are post-hoc engineering
- Separate "planned" analyses (registered) from "exploratory" (post-hoc); clearly label the latter

---

## 12. Summary: How This Design Answers the Research Question

**Question**: How much of a published agent capability score comes from the scaffold versus the model?

**Approach**:
1. Use ResearchClawBench (40 tasks, 10 domains) as the shared benchmark—identical conditions across all (scaffold, model) cells
2. Combine three scaffolds (ResearchHarness, HEP, OptED) and five models (Claude-Opus-4.7, Qwen-3.7-Max, Gemini-3.5-Flash, DeepSeek-V4-Pro, Kimi-K2.6) in a crossed 3×5 factorial
3. Collect 600 rubric scores (3×5×40)
4. Decompose total variance into Scaffold, Model, Interaction, and residual components via ANOVA
5. Answer the question numerically: η²_S (scaffold contribution) vs. η²_M (model contribution)

**Explicit Reference to Sampling Frame**: The factorial crosses three scaffolds and five models over the ResearchClawBench sampling frame of 40 tasks across 10 scientific domains (Astronomy, Chemistry, Earth Science, Energy Science, Information Science, Life Science, Material Science, Mathematics, Neuroscience, Physics). Each (scaffold, model, task) triplet is a unit of analysis in the 3×5×40 = 600-observation design. This ensures that tasks and conditions are identical across cells, enabling clean attribution of score variance to scaffold and model factors.

**Ablations** (Sections 5.2–5.4):
- Model-tier stratification tests whether scaffold effects generalize across model capabilities
- Domain stratification tests whether some domains rely more on scaffolding
- Trajectory-aware scoring tests whether process improvements (from structure) are hidden by outcome-only measurement

**Uncertainty**: Confidence intervals on η² via bootstrap; inter-rater reliability checks (κ ≥ 0.65); judge-severity audits (drift < 10 points); complete-case sensitivity analysis.

---

## 13. References to Evidence

This design is grounded in the following evidence excerpts:

- **2606.07591**: ResearchClawBench benchmark, autonomous agents vs. native LLMs, 40 tasks, rubric anchor at 50 points
- **2607.09195**: HEP protocol scaffold; hypothesis-evolution harness improving task generalization
- **2608.03501**: SCOPE experimental-design benchmark; OptED workflow with stage isolation and rule-based constraints
- **2609.00038**: Trajectory-judge findings; outcome-only evaluation blindness; step-rubric superiority
- **2608.29517**: LLM judge severity drift; version instability; need for version pinning and calibration
- **2607.13304**: Variance-components decomposition; guidance on resampling and model-identity variance
- **2010.06595**: Statistical power norms for NLP; warnings on underpowered comparisons

---

**Design Status**: Complete. Ready for preregistration and execution.
