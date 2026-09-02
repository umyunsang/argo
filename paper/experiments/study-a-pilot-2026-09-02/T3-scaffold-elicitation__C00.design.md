# Experimental Design: Scaffold vs. Model Contribution to Agent Capability Scores

## Research Question

How much of a published agent capability score comes from the scaffold rather than the model?

## 1. Experimental Design Structure

### 1.1 Main Comparison
A 3 × 5 full-factorial design crossing three scaffolds with five models:
- **Factor 1: Scaffold** (3 levels)
- **Factor 2: Model** (5 levels)
- **Outcome:** Benchmark score on standardized multi-step task suite
- **Design:** Balanced, complete crossing; n = 15 cells

### 1.2 Concrete Scaffold Implementations

**Scaffold A: ReAct (Reasoning + Acting)**
- Prompting template: "Thought → Action → Observation" cycle
- Implementation: OpenAI's ReAct prompt (https://github.com/ysymyth/ReAct)
- Interaction loop: agent reasons, chooses action, receives observation, repeats
- Stop condition: agent concludes or max 10 steps

**Scaffold B: Chain-of-Thought (CoT) with few-shot**
- Prompting template: Think step-by-step before answering
- Implementation: Wei et al. (2023) standard CoT + 3 in-context examples per task type
- No tool use or external actions; purely reasoning in prompt
- Stop condition: model provides final answer

**Scaffold C: Baseline—Direct Prompting**
- Prompting template: Task statement + task input, no CoT or ReAct framing
- No intermediate reasoning steps or action cycles
- Single model response per task
- Stop condition: model provides answer

### 1.3 Concrete Model Choices

**Model 1: Claude 3.5 Sonnet (Anthropic)**
- API: claude-3-5-sonnet-20241022 via Claude API
- Context window: 200K tokens
- Training cutoff: April 2024

**Model 2: Claude 3 Opus (Anthropic)**
- API: claude-3-opus-20240229 via Claude API
- Context window: 200K tokens
- Training cutoff: August 2023

**Model 3: Claude 3 Haiku (Anthropic)**
- API: claude-3-haiku-20240307 via Claude API
- Context window: 200K tokens
- Training cutoff: August 2023

**Model 4: GPT-4 Turbo (OpenAI)**
- API: gpt-4-turbo-preview via OpenAI API
- Context window: 128K tokens
- Training cutoff: April 2024

**Model 5: Llama 3.1-70B-Instruct (Meta)**
- Hosted on Together AI (https://www.together.ai/) or via Replicate
- Context window: 128K tokens
- Training cutoff: December 2023

### 1.4 Benchmark Selection: WebArena

**Benchmark:** WebArena (Jia et al., ICML 2024)
- GitHub: https://github.com/web-arena-x/webarena
- Composition: 812 realistic web interaction tasks across 12 websites
- Task structure: multi-step instructions (e.g., "Find event date and register")
- Evaluation: binary success (task completed correctly) + partial credit (steps completed)
- Multi-step naturally suits ReAct (tool-using scaffold) vs. pure reasoning (CoT) vs. baseline
- Public, reproducible, no licensing issues

**Justification:** WebArena explicitly tests agent scaffolding effectiveness across complex tasks that no model can memorize; success requires either external action loops (ReAct advantage) or strong reasoning (CoT advantage). Baseline may fail entirely.

## 2. Ablation Studies

### Ablation 1: Scaffold × Training Cutoff
**Hypothesis:** Older models (Claude 3 Opus, Llama 3.1-70B) may rely more heavily on scaffolding to compensate for stale knowledge, inflating scaffold contribution.

**Design:** 
- Compare ReAct performance on Claude 3.5 Sonnet (cutoff April 2024) vs. Claude 3 Opus (cutoff August 2023)
- If scaffold effect size differs meaningfully by model age, report the interaction term
- This isolates whether scaffolds amplify older models' weaknesses

### Ablation 2: Scaffold Prompt Sensitivity
**Hypothesis:** Scaffold advantage may come from particular prompt choices, not the scaffold structure itself.

**Design:**
- Hold Model = Claude 3.5 Sonnet fixed
- Vary ReAct prompt wording (3 independent instantiations of the same scaffold logic, different phrasing)
- Measure score variance within Scaffold A across prompts
- If variance within scaffold > variance between scaffolds, scaffold effect is overstated by prompt artifacts

## 3. Analysis Plan

### 3.1 Primary Analysis: Two-Way ANOVA

**Model:**
```
Score ~ Scaffold + Model + Scaffold × Model + Error
```

**Outcome:**
- Main effect of Scaffold (pooled across models)
- Main effect of Model (pooled across scaffolds)
- Interaction term (does best scaffold differ by model?)

**Metrics:**
- Sum of squares, F-statistic, p-value for each term
- Partial eta-squared (effect size for each term, bounded 0–1)
- Interpretation: if Scaffold η² >> Model η², scaffold is major driver; if Model η² >> Scaffold η², model choice dominates

### 3.2 Decomposition: Variance Partition

**Goal:** Quantify "% of score variance explained by each factor"

**Method:**
1. Fit ANOVA model; extract SS_Scaffold, SS_Model, SS_Interaction, SS_Total
2. Compute proportional variance explained by each term:
   - Scaffold contribution = SS_Scaffold / SS_Total
   - Model contribution = SS_Model / SS_Total
   - Interaction contribution = SS_Interaction / SS_Total
3. Report as percentages (must sum to ~100%)

### 3.3 Pairwise Comparisons

**Within-model scaffold ranking:**
- For each model, rank the three scaffolds by mean score
- If ranking is consistent across models, scaffold superiority is robust
- If ranking flips (e.g., ReAct best for Claude, CoT best for Llama), scaffold-model interaction is strong

**Within-scaffold model ranking:**
- For each scaffold, rank the five models by mean score
- If Model ranking is robust across scaffolds, model difference is stable
- Large scaffold-specific model rankings suggest interaction

### 3.4 Best-Case Comparison
Report the highest-scoring cell (Scaffold × Model pair) and the lowest-scoring cell, and their ratio. This directly shows maximum swing attributable to design choices.

## 4. Uncertainty Quantification

### 4.1 Confidence Intervals and Resampling

**Bootstrap for Effect Sizes:**
1. Run 1000 bootstrap resamples of the 15-cell mean scores
2. For each resample, re-fit ANOVA and extract η² terms
3. Report 95% CI for each η² (percentile method)
4. CIs that overlap zero indicate uncertainty about factor importance

**Resampling Justification:** WebArena tasks are not normally distributed (binary + partial credit); bootstrap is distribution-free and appropriate.

### 4.2 Within-Cell Variance

**Measurement:**
- Run each (Scaffold, Model) cell 10 times (10 independent runs per cell)
- Compute mean and SD per cell
- Perform ANOVA on run-level data (n = 150 observations total)
- Extract residual variance; this estimates task inherent stochasticity

**Reporting:**
- For each cell, report Mean ± 95% CI (derived from 10 runs)
- Cells with high within-cell SD will have wider CIs, reducing confidence in that cell's effect size

### 4.3 Sensitivity Analysis: Outlier and Failure Mode

**Design:**
- Identify any (Scaffold, Model) cell with mean < 30% on WebArena (severe failure)
- Re-fit ANOVA with and without that cell
- If main conclusions (which factor dominates) change, report the sensitivity
- If robust, report only main analysis

## 5. Concrete Resources

### 5.1 Task Benchmark
- **WebArena:** Public GitHub repo, 812 tasks, self-contained
- **Cost:** No monetary cost; requires local deployment or Docker container
- **Runtime:** ~812 tasks × 15 cells × 10 runs = 121,800 task executions; ~1–2 min per task in parallel → ~1000–2000 compute-hours on single GPU, parallelizable

### 5.2 Model API Access
- **Claude (Anthropic):** API key via https://console.anthropic.com; pay-per-token (~$0.003–0.01 per 1k tokens)
- **GPT-4 (OpenAI):** API key via https://platform.openai.com; pay-per-token (~$0.03–0.06 per 1k tokens)
- **Llama 3.1-70B:** Via Together.ai ($2–3 per 1M tokens) or Replicate (~$0.0005 per second)
- **Budget estimate:** ~$500–2000 total across all cells (depending on token efficiency)

### 5.3 Experimental Infrastructure
- **Orchestration:** Python + asyncio + requests library for parallel API calls
- **Logging:** Store results per cell in JSON (timestamp, scaffold, model, score, steps, tokens)
- **Version control:** Git repo to track prompt versions (scaffolds A, B, C)
- **Compute:** Local machine with ~50 GB disk (WebArena artifacts + logs); no GPU required for models (all via API)

## 6. Outcome Metrics

### 6.1 Primary Outcome: Task Success Rate
- **Definition:** Percentage of WebArena tasks completed successfully (binary 1 = success, 0 = failure)
- **Granularity:** Reported per cell (Scaffold × Model) as mean success rate across 10 runs

### 6.2 Secondary Outcome: Partial Credit Score
- **Definition:** Proportion of task steps correctly completed (WebArena's built-in metric)
- **Range:** 0 (no steps) to 1 (all steps)
- **Use:** Ranks scaffolds finely when binary success is too coarse

### 6.3 Tertiary Outcome: Efficiency Metrics (optional, for interaction interpretation)
- **Steps to completion:** Average number of action steps before success or failure
- **Tokens consumed:** Total input + output tokens for the full task execution
- **Reason:** Helps diagnose whether scaffold differences come from longer reasoning chains or better direction

## 7. Summary Table (Expected Output Structure)

| Scaffold | Model | Mean Score | SD (10 runs) | 95% CI | Primary Finding |
|----------|-------|------------|--------------|--------|-----------------|
| ReAct    | Claude 3.5 Sonnet | [score] | [sd] | [ci_lo, ci_hi] | Best cell? |
| ReAct    | Claude 3 Opus | [score] | [sd] | [ci_lo, ci_hi] | ... |
| CoT      | Claude 3.5 Sonnet | [score] | [sd] | [ci_lo, ci_hi] | ... |
| ... (15 cells total) | | | | | |

**ANOVA Summary:**
- F(Scaffold=2, Residual=142) = [F_scaf], p = [p_scaf], η² = [eta_scaf]
- F(Model=4, Residual=142) = [F_model], p = [p_model], η² = [eta_model]
- F(Scaffold×Model=8, Residual=142) = [F_inter], p = [p_inter], η² = [eta_inter]

**Interpretation:** Scaffold explains [X]% of variance, Model explains [Y]%, Interaction explains [Z]%.

---

## Design Notes and Justifications

### Why WebArena over other benchmarks?
- **ARC, MMLU, HellaSwag** are static reasoning benchmarks; scaffolds (ReAct) are underutilized because there are no external tools.
- **SWE-Bench** requires real code execution and git environments; adds confounds (tool reliability).
- **WebArena** is designed for agent scaffolding evaluation; tool use (ReAct) directly applies.

### Why exactly 3 scaffolds and 5 models?
- **3 scaffolds** represent the full spectrum: no scaffold (baseline) → moderate structure (CoT) → full tool loop (ReAct).
- **5 models** span capability range (Haiku to Sonnet, Claude vs. GPT-4 vs. Llama), allowing generalization across model families.
- **Full factorial (3 × 5)** is feasible (~121,800 WebArena task runs at 10 reps each) on available compute.

### Why 10 runs per cell?
- WebArena tasks involve randomness (network behavior, page rendering, dynamic content).
- 10 runs per cell (~10 hours per cell on shared compute) balances statistical power with cost.
- Bootstrap resampling + percentile CIs mitigate non-normality.

### Why bootstrap?
- WebArena scores are binary or bounded (partial credit); not normally distributed.
- Bootstrap makes no distributional assumptions; CIs are valid even with skewed data.

---

## Expected Outcomes (Qualitative Scenarios, No Numbers)

1. **Scaffold dominates:** ReAct >> CoT >> Baseline across all models.
   - Interpretation: Structured tool use is the key driver; model choice is secondary.

2. **Model dominates:** Score ranking driven primarily by model capability; scaffold effects are modest.
   - Interpretation: Stronger models overcome weak scaffolds; model choice is the key lever.

3. **Strong interaction:** Best scaffold differs per model (e.g., ReAct for Claude, CoT for Llama).
   - Interpretation: Scaffold effectiveness depends on model architecture; no one-size-fits-all.

4. **Additive effects:** Scaffold and Model effects are independent; interaction is small.
   - Interpretation: Scaffolds and model choice provide complementary improvements.

The ANOVA and effect-size decomposition will clarify which scenario is true.
