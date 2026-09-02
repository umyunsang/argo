# Experimental Design: Hypothesis-Tree Organization vs. Flat-Queue Attempts

**Decision ID:** K1-hypothesis-search-design  
**Research Question:** Does organizing an autonomous agent's attempts as a hypothesis tree with 
propagated insight beat a flat queue of attempts on held-out artifact optimization?

---

## 1. Main Comparison: Treatment and Control Conditions

### 1.1 Sampling Frame (from state.md)
**Population:** Autonomous agent artifact optimization tasks grounded in real published work, 
spanning diverse scientific domains (≥5 domains from ResearchClawBench or similar: materials 
science, computational chemistry, machine learning, neuroscience, physics).

**Unit of analysis:** Single agent run on a single task, constrained by fixed compute and 
workspace budget (identical budget for all arms). Each unit consists of:
- One hidden-target task prompt (target known to evaluator only)
- One attempt sequence (tree-organized or queue-organized)
- One final artifact (code, report, figure, or prediction)
- Outcome judgment via held-out rubric

**Sample size:** N=30 runs per arm per task (30 × 2 arms × 5 tasks = 300+ total runs minimum) 
to meet paired resolution targets (α=0.05, power=0.8) for small-to-medium effects, following 
guidance in 2605.30315.

### 1.2 Treatment Arm: Hypothesis-Tree-Organized Attempts (HTree)

**Definition:** Agent organizes all attempts as nodes in an explicit hypothesis tree with 
propagated belief state and evidence tracking. Adapted from HEP protocol (2607.09195).

**Core components:**
1. **Hypothesis registry:** Each attempt is registered as a hypothesis with a unique ID, 
   natural-language description, initial belief estimate P(H), and lifecycle state 
   (proposed, under_test, supported, refuted, or dormant).
   
2. **Evidence attachment:** After each attempt, the agent (with LLM assistance) attaches 
   observed evidence (query result, test outcome, artifact quality metric) and updates P(H) 
   based on that evidence. Evidence attachment is logged with timestamp and justification.
   
3. **Hypothesis evolution:** New hypotheses are generated via four mechanisms:
   - De novo: independent new attempt
   - Inspired-by: refine prior attempt based on feedback
   - Refine: narrow down a prior hypothesis
   - Merge: combine insights from multiple prior attempts
   
4. **Belief rules:** P(H) moves only on attached evidence passing a validation gate (auto 
   or LLM-judged). Lifecycle transitions enforce thresholds: support at P(H)≥0.8, 
   refutation at P(H)≤0.2, dormant if untestable.

5. **Query budget management:** Tree arm gets the same total compute budget as flat arm. 
   Belief propagation and tree updates count toward budget. Log all belief updates and 
   hypothesis merges so overhead can be measured.

**Backbone:** Same backbone LLM and tools serve the tree arm (e.g., Claude-3.5-Sonnet, 
gpt-4o, or pinned open-weights model). Backbone is held constant across arms.

### 1.3 Control Arm: Flat-Queue-Organized Attempts (FQueue)

**Definition:** Agent organizes all attempts as an unordered flat queue with no explicit 
structure, no belief tracking, and no merge/refine logic. Each attempt is independent; 
outcomes are logged but not used to update a belief state or influence hypothesis generation.

**Core components:**
1. **Attempt logging:** Each attempt is logged with attempt ID, time, query/action, 
   outcome, and artifact quality metric. No belief field, no lifecycle state.
   
2. **Query strategy:** Agent must generate next attempt using only the flat log of prior 
   outcomes (no structured insight propagation). Agents may re-run similar queries, merge 
   ideas informally, or try independent paths; no formal mechanism guides these decisions.
   
3. **Budget management:** Same total compute budget as tree arm. No overhead for belief 
   bookkeeping, but also no structured scaffolding to prioritize.

4. **Backbone:** Same LLM and tools as tree arm.

### 1.4 Randomization and Stratification

- **Allocation:** Simple 1:1 randomization of runs to HTree vs. FQueue, stratified by task 
  to ensure balanced allocation across the 5+ tasks.
- **Blinding:** Evaluators who score final artifacts and attempt sequences are blind to 
  arm assignment (randomized rubric presentation order).
- **Seed management:** Fix random seeds for LLM sampling (temperature, top-p) within runs; 
  randomize seeds across runs to avoid implicit dependencies.

---

## 2. Ablation Study: Belief Updates Without Tree Structure

**Motivation:** Isolate the value of explicit tree structure (merging, refining, lifecycle 
rules) from the value of belief tracking alone. If belief tracking alone drives improvements, 
the tree structure may be unnecessary overhead.

### 2.1 Ablation Arm: Flat-Queue with Belief Tags (FQueue+B)

**Definition:** Flat queue (no merging, refining, or lifecycle) augmented with belief 
estimates (P(H)) attached to each attempt, but no state transitions or rules.

**Core changes from FQueue:**
- Each logged attempt gets a belief estimate P(H) (0–1) assigned by the agent post-hoc 
  (not enforced by rules).
- Belief is informational only; does not gate lifecycle or merge decisions.
- No hypothesis refinement, merging, or lifecycle transitions.

**Hypothesis:** If FQueue+B performs as well as HTree, it suggests that structured tree 
operations (merge, refine) are overhead. If HTree remains superior, it suggests the rules 
and structure matter beyond point estimates.

**Sample size:** N=15 runs per task (15 × 1 arm × 5 tasks = 75 runs), stratified. Smaller 
sample sufficient because this ablation is not primary; primary comparison is HTree vs. FQueue.

---

## 3. Primary Outcome Metrics

### 3.1 Artifact Quality (Hidden-Target Rubric-Based)

**Method:** Each final artifact (code, report, prediction) is scored by a trained LLM judge 
against an expert-curated rubric grounded in the hidden target paper or solution.

**Rubric structure (adapted from 2606.07591, 2608.03501):**
1. **Conceptual alignment:** Does the artifact address the research question and domain 
   correctly? (0–5 points)
2. **Methodological soundness:** Are the methods, baselines, and evaluation appropriate? 
   (0–5 points)
3. **Evidence quality:** Does the artifact present sufficient evidence for its claims? 
   (0–5 points)
4. **Completeness:** Are all major components (e.g., main results, ablations, error analysis) 
   present? (0–5 points)
5. **Novelty/Discovery:** Does the artifact go beyond re-discovery to novel insights? (0–5 points)
6. **Reproducibility:** Are details sufficient to reproduce the artifact? (0–5 points)

**Scoring:** Total 0–30 points per artifact. Rubric is task-specific (adapted for each domain 
e.g., materials science, ML, neuroscience). Same rubric applied to all arms.

**Redline mechanism (from 2608.03501):** If rubric detects critical flaws (e.g., hallucinated 
baselines, impossible metrics, misaligned methodology), automatic score is zeroed, with explicit 
flaw noted. Prevents averaging-out of catastrophic errors.

**Judge pinning (from 2608.29517):** One LLM judge version is pinned for the entire study. 
Before and after data collection, run calibration step: score a 20-essay anchor set from prior 
studies, verify judge severity is stable (inter-rater correlation κ≥0.65 vs. anchor).

### 3.2 Attempt Sequence Quality (Trajectory Rubric)

**Motivation:** Following 2609.00038, outcome-only evaluation is structurally blind to 
trajectory quality. Tree structure may improve reasoning (e.g., better hypothesis formation, 
evidence consideration) without always improving final artifact. Trajectory rubric catches this.

**Method:** Each attempt sequence (full log of hypotheses, queries, belief updates) is scored 
by the judge on a separate trajectory rubric.

**Rubric structure:**
1. **Hypothesis clarity:** Are hypotheses stated explicitly, with clear predictions? (0–4 points)
2. **Evidence integration:** Does the agent attach evidence to hypotheses and update beliefs? 
   (0–4 points)
3. **Strategic pivot:** When evidence refutes a hypothesis, does the agent pivot to a new 
   direction or persist unproductively? (0–4 points)
4. **Query efficiency:** Do queries target high-uncertainty hypotheses, or are many redundant? 
   (0–3 points)
5. **Audit trail:** Is the sequence transparent and reproducible from logs? (0–3 points)

**Scoring:** Total 0–18 points per trajectory.

**Key difference from artifact rubric:** Trajectory rubric is blind to the final answer; 
it scores the *reasoning process*. A correct answer via poor reasoning gets low trajectory 
score; a wrong answer via excellent reasoning (just unlucky) gets high trajectory score.

### 3.3 Evidence Saturation (Secondary Outcome)

**Motivation:** From 2608.01913, useful evidence often appears early; agents often waste time 
searching afterward. Measure at what point in the attempt budget the agent has retrieved all 
major evidence lines (as judged ex-post by human expert).

**Method:** 
1. Expert annotator (domain expert, blind to arm) reviews final artifact and identifies all 
   key pieces of evidence (citations, data insights, experimental designs) that justified 
   the conclusions.
2. Annotator then reviews the attempt log and marks the first appearance of each evidence 
   piece (which query/test brought it in).
3. "Saturation point" = earliest step at which all evidence appeared. Expressed as percentage 
   of total budget consumed.

**Hypothesis:** Tree arm should saturate earlier (e.g., 40% of budget) than flat arm (e.g., 60%) 
because tree structure guides focused evidence-gathering. However, if overhead is high, tree 
might saturate later.

---

## 4. Analysis Plan

### 4.1 Primary Comparison: HTree vs. FQueue on Artifact Quality

**Design:** Paired comparison (same tasks, stratified randomization). Metric is mean artifact 
rubric score (0–30 points).

**Statistical method:**
1. For each task k ∈ {1, ..., 5}:
   - Compute mean artifact score μ_HTree,k and μ_FQueue,k (N_k=30 per arm)
   - Compute difference Δ_k = μ_HTree,k - μ_FQueue,k
   - Compute 95% confidence interval (CI) via paired t-test (or non-parametric Wilcoxon 
     if normality fails)
   
2. Across tasks, compute grand mean Δ = mean(Δ_k) and 95% CI via meta-analytic fixed effects.
   
3. Compute resolution ratio q = N / N* where:
   - N = 30 (actual runs per arm per task)
   - N* = minimum N to achieve (α, 1−β)=(0.05, 0.8) given observed effect size
   - q<0.5 signals underpowered study; q>1.0 signals overpowered
   
   (Following 2605.30315 inversion method.)

4. **Primary inference:** If 95% CI for Δ excludes 0, conclude HTree improves artifact 
   quality at (α, 1−β)=(0.05, 0.8) threshold, contingent on q>0.5.

### 4.2 Secondary Comparison: Artifact Quality + Trajectory Synergy

**Motivation:** Artifact quality alone might not reveal tree benefits if tree improves reasoning 
without proportionally improving final answer. Test if tree arm has higher trajectory scores 
even when artifact scores are similar.

**Method:**
1. Compute trajectory score difference Δ_traj = μ_HTree,traj - μ_FQueue,traj (0–18 scale)
2. If Δ_artifact ≈ 0 (no artifact difference) but Δ_traj > 0 (better trajectories in tree), 
   conclude tree improves reasoning without immediate artifact payoff (potential for downstream 
   value or scaling).

### 4.3 Ablation: HTree vs. FQueue+B

**Method:** Same paired comparison as primary, but N=15 per arm per task (smaller sample). 
Compute Δ_ablation = μ_HTree - μ_FQueue+B.

**Interpretation:**
- If Δ_ablation ≈ Δ_primary (HTree vs. FQueue), tree structure adds little beyond belief 
  tracking; overhead may not be justified.
- If Δ_ablation > Δ_primary, tree structure (merge, refine, lifecycle rules) is responsible 
  for gains; belief tracking alone is insufficient.

### 4.4 Variance Decomposition (Post-Hoc)

**Motivation:** Understand noise sources following 2607.13304. Allocate K=2 or K=3 repeats 
per cell (same arm, same task, new random seed) for at least a subset (e.g., 10 runs per arm 
per task, repeated K=2 times).

**Method:** Fit mixed model:
  Score_ijk = μ + α_i (arm) + β_j (task) + γ_ij + ε_k(ij)
  where ε_k is within-cell variance (replication), γ_ij is arm×task interaction.
  
Compute variance components σ²_arm, σ²_task, σ²_arm×task, σ²_within.

**Purpose:** Determine whether task drives most variance (tree may not matter on all tasks) 
or arm does (tree effect is generalizable).

### 4.5 Falsifier Detection

**Early stop condition (informational, non-binding):** After N≈150 runs (50% of target), 
compute provisional Δ and 95% CI. If CI includes 0 *and* trajectory rubric also shows no 
HTree advantage, alert investigator that falsifier may be emerging. Investigator may choose 
to stop and report null result, noting underpowered design. Decision is documented and published.

---

## 5. Concrete Resources

### 5.1 Tasks (from sampling frame)

**Source:** ResearchClawBench (2606.07591) or equivalent curated benchmark. Select 5 tasks 
spanning:
1. **Materials Science:** Materials property prediction (e.g., crystal structure polymorph 
   prediction)
2. **Computational Chemistry:** Molecular design or reaction optimization
3. **Machine Learning:** Hyperparameter tuning or architecture search (simplified)
4. **Neuroscience:** Brain imaging analysis or neural model fitting
5. **Physics:** Simulation parameter inference or theoretical prediction

**Requirements per task:**
- Real published target (paper, dataset, ground-truth solution)
- Clear research question (not just classification)
- Hidden during data collection (revealed only to evaluators)
- Related literature and raw data provided to agent
- Estimated difficulty (for stratification)

**Availability:** ResearchClawBench provides 40 such tasks, cross 10 domains; we select 5.

### 5.2 Backbone LLM and Tools

**Model:** Single pinned version throughout study (e.g., Claude-3.5-Sonnet, GPT-4o, or 
Qwen-32B).
- Rationale: Avoids confounding with model version shifts (2608.29517 shows shifts up to 
  133 points in severity).
- Temperature: 0.7 (or fixed seed for reproducibility)
- Max tokens: Set to match prior benchmarks (e.g., 8000 per query)

**Tools provided to agent (both arms):**
- Search tool (e.g., BrowseComp corpus or ArXiv API)
- Code execution (sandboxed, bounded by timeout + memory)
- Data loading (upload CSV, read HDF5, etc.)
- Visualization (matplotlib, plotly)
- Literature fetching

**Same for both arms:** Ensures confound-free comparison.

### 5.3 Evaluation Infrastructure

**Judge:** One LLM instance (e.g., Claude-3.5-Sonnet, pinned version) or ensemble of 2–3 
judges with output averaging (following 2608.29517). Calibrated against anchor set (20 essays) 
before and after experiment.

**Rubric templates (task-specific):**
- Domain experts author rubric for each task (e.g., materials-science rubrics differ from 
  neuroscience). Rubric is fixed before data collection (pre-registered).

**Storage & versioning:**
- All attempt logs, artifacts, and rubric scores stored in versioned artifact store (e.g., 
  OSF, GitHub + artifact registry).
- Timestamped snapshots for audit trail.

### 5.4 Budget Allocation

**Compute per run:**
- Token budget: ~50k tokens per run (search queries, code execution, artifact writing)
- Wallclock time: ~15 minutes per run (assuming API + sandboxed execution)
- Total: 300 runs × 15 min ≈ 75 CPU-hours (parallelizable to ~6 hours wallclock with 12 cores)

**Evaluator time (human):**
- Rubric refinement: 16 hours (2 hours per task)
- Evidence annotation (secondary): 20 hours (expert, ~4 hours per task × 5)
- Total: 36 hours

**LLM judge calls:**
- Each run: 1 artifact rubric call + 1 trajectory rubric call = 2 calls
- 300 runs × 2 calls = 600 calls × ~5k input tokens + 500 output tokens ≈ 3M tokens
- Cost (via API): ~$30–50 USD (at current Claude pricing)

---

## 6. Outcome Metrics and Uncertainty Quantification

### 6.1 Primary Outcome: Artifact Quality (0–30 scale)

**Estimand:** E[Artifact_HTree] - E[Artifact_FQueue], pooled across tasks.

**Uncertainty:**
- **95% Confidence Interval** via paired t-test (or Wilcoxon signed-rank + bootstrap if 
  non-normal):
  - Compute difference d_i = score_HTree,i - score_FQueue,i for each task i
  - SE = SD(d) / sqrt(N), where N = 30
  - 95% CI = mean(d) ± 1.96 × SE
  
- **Effect size:** Cohen's d = mean(d) / SD(d) (standardized)

- **Resolution ratio:** q = N / N*, where N* is minimum N to achieve power 0.8 for observed 
  effect size (2605.30315). Report as primary diagnostic of statistical power.

### 6.2 Secondary Outcome: Trajectory Quality (0–18 scale)

**Estimand:** E[Trajectory_HTree] - E[Trajectory_FQueue]

**Uncertainty:** Same approach as artifact quality (95% CI, Cohen's d, q).

### 6.3 Evidence Saturation (Percentage of Budget)

**Estimand:** Mean saturation point HTree vs. FQueue (e.g., HTree saturates at 45% of budget, 
FQueue at 62%).

**Uncertainty:** 95% CI via bootstrap (resample runs with replacement, recompute saturation 
for each bootstrap sample).

### 6.4 Budget Overhead (HTree Computation Cost)

**Estimand:** Fraction of budget consumed by belief updates and tree bookkeeping in HTree 
(vs. FQueue baseline = 0% overhead).

**Measurement:** 
- Log all LLM calls: categorize as "search query", "evidence judgment", "belief update", 
  "artifact writing".
- Overhead = (sum of tokens for "belief update" calls) / (total tokens in run) × 100%

**Purpose:** Understand whether HTree's gains outweigh its bookkeeping cost.

---

## 7. Comparison of Arms

| Aspect | HTree | FQueue | FQueue+B | Measurement |
|--------|-------|--------|----------|-------------|
| **Belief tracking** | Yes (enforced) | No | Yes (informational) | Artifact rubric |
| **Hypothesis refining** | Yes | No | No | Trajectory rubric |
| **Hypothesis merging** | Yes | No | No | Trajectory rubric |
| **Lifecycle transitions** | Yes (enforced) | No | No | Attempt logs |
| **Query guidance** | Belief-driven | Unstructured | Belief-informed | Evidence saturation |
| **Compute budget** | Same as FQueue | — | Same as HTree+FQueue | Token counting |
| **Sample size** | 30 per task | 30 per task | 15 per task | Stratification |

---

## 8. Pre-Registration and Transparency

**Pre-registered elements:**
1. Rubric templates (task-specific, fixed before data collection)
2. Judge version (pinned LLM checkpoint)
3. Sample size: N=30 per arm per task
4. Primary analysis: paired t-test on artifact quality, 95% CI
5. Falsifier criteria (stated above)
6. Stopping rule (fixed N, quality gates, interim monitoring)

**Post-hoc elements (acceptable):**
1. Variance decomposition methods (due to unknown error distributions)
2. Remedies if judge agreement drops below threshold (e.g., re-calibration)
3. Additional exploratory analyses (e.g., per-domain breakdown) if data permit

**Transparency:**
- All attempt logs, rubric scores, and raw LLM judge calls published in anonymized form
- Code for data analysis released (reproduce all reported numbers)
- Pre-registration document filed before first run (e.g., OSF, AsPredicted.org)

---

## 9. Decision Rule and Interpretation

### 9.1 Success Criteria for HTree

HTree is judged successful if *both*:
1. **Artifact quality:** E[Artifact_HTree] > E[Artifact_FQueue] with 95% CI excluding zero 
   AND resolution ratio q > 0.5 (powered adequately for observed effect).
2. **Trajectory quality:** E[Trajectory_HTree] > E[Trajectory_FQueue] with 95% CI excluding 
   zero (confirming process improvement, not just luck).

If only artifact improves but trajectory does not, success is partial (outcome is better, 
but process improvement unclear; may indicate confounding). If only trajectory improves, 
further investigation warranted (reasoning better but not translating to artifact).

### 9.2 Ablation Interpretation

- If Δ_ablation ≈ Δ_primary: Tree structure is unnecessary overhead; belief tracking alone 
  suffices.
- If Δ_ablation >> Δ_primary: Tree structure (merging, refining) is critical; belief alone 
  is not.
- If Δ_ablation << 0 (FQueue+B worse than HTree): Unstructured belief is harmful; structure 
  is essential.

### 9.3 Falsifier Detection

If after 50% of runs (N≈150), 95% CI for artifact quality Δ includes zero *and* trajectory 
rubric shows no HTree advantage, hypothesis is falsified. Report null result prominently, 
with discussion of possible reasons (e.g., task domain does not benefit from tree structure, 
overhead dominates, or design flaw).

---

## 10. References to Evidence

This design is grounded in seven prior studies from ./evidence:

- **2607.09195**: HEP protocol demonstrates explicit hypothesis-test-evidence-belief cycles 
  improve reasoning on open-ended tasks. Justifies tree-based treatment arm.
  
- **2608.01913**: Search agent diagnosis shows evidence quality and saturation matter more 
  than effort; early stopping signals are important. Justifies secondary outcome on evidence 
  saturation.
  
- **2606.07591**: ResearchClawBench establishes multi-domain rubric design and redline 
  mechanisms for open-ended research outputs. Informs artifact quality rubric structure.
  
- **2608.03501**: Experimental design benchmark (SCOPE) decomposes planning into high-level 
  and low-level components with stage isolation. Justifies redline mechanism and trajectory 
  rubric.
  
- **2608.29517**: LLM judge audit quantifies severity effects, version instability, and 
  remedies (calibration, pinning, per-dimension calls). Informs judge setup and quality gates.
  
- **2609.00038**: Trajectory-level judge blind spots show outcome-only evaluation misses 
  silent faults. Justifies trajectory rubric as complement to artifact rubric.
  
- **2605.30315**: Paired resolution diagnostics show many LLM comparisons are unresolved; 
  inversion of hypothesis-testing yields resolution ratio q=N/N*. Informs stopping rule and 
  power analysis.
  
- **2607.13304**: Variance components for LLM non-determinism identify within-prompt, 
  paraphrase, model, and language sources. Justifies sample-size design and variance decomposition.

---

## 11. Sampling Frame (Explicit Reference)

**Sampling frame from state.md, referenced explicitly here:**

The experiment samples from the population of autonomous agent artifact optimization tasks 
grounded in real published work, spanning diverse scientific domains (≥5 domains from 
ResearchClawBench or similar, e.g., materials science, computational chemistry, machine 
learning, neuroscience, physics).

The **unit of analysis** is a single agent run on a single task, consisting of:
1. One hidden-target task prompt (target known to evaluator only)
2. One attempt sequence (organized as tree [HTree] or flat queue [FQueue])
3. One final artifact (code, report, figure, or prediction)
4. Outcome judgment via held-out rubric-based evaluation

**Sample allocation** across this sampling frame:
- **N=30 runs per arm per task** (30 HTree + 30 FQueue per task)
- **5 tasks minimum** (300 + 300 = 600 total runs across two main arms; 75 additional for ablation)
- **Stratified randomization** by task to ensure balanced allocation

This design samples evenly across the sampling frame (no task bias) and holds backbone, tools, 
and budget constant across arms. The paired structure (same tasks, stratified allocation) 
exploits the sampling frame's structure to improve power for the comparison.

---

## 12. Summary: What is being measured and why

| What | Why | Evidence Base |
|------|-----|---|
| **Artifact quality** | Final outcome that matters; hidden-target rubric avoids teaching to the test | 2606.07591, 2608.03501 |
| **Trajectory quality** | Process improvement not visible in outcome alone; catches silent faults | 2609.00038 |
| **Evidence saturation** | Efficient search is undervalued; tree may help prioritize | 2608.01913 |
| **Judge stability** | LLM judges are unstable instruments; pinning + calibration required | 2608.29517 |
| **Resolution ratio (q)** | Many LLM comparisons are underpowered; q diagnostic avoids false confidence | 2605.30315 |
| **Variance decomposition** | Multiple noise sources exist; task vs. arm breakdown clarifies effect size | 2607.13304 |
| **Falsifier detection** | Plan for null result upfront; increases credibility of positive result | 2608.03501 (redline), 2609.00038 (stratified recall) |

---

**End of design document.**
