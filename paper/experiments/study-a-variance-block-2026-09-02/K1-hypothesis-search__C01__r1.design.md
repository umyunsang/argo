# Experimental Design: Hypothesis Tree vs Flat Queue for Autonomous Agent Optimization

## Research Question

Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

## Design Overview

A two-arm randomized comparison of search strategies, holding compute budget and backbone model constant, with held-out task performance as the primary outcome and process-level ablations to isolate the mechanism.

---

## 1. Main Comparison

### 1.1 Arms

**Treatment (Hypothesis Tree)**
- Agent generates a hypothesis (a prediction of what modification to the artifact will improve performance)
- Hypothesis explicitly states prior reasoning that supports it
- Agent executes the modification and observes outcome
- Outcome is scored against a rubric (pass/fail/partial)
- Passed hypothesis guides subsequent hypotheses (propagated insight)
- Failed hypothesis contributes a negative signal: subsequent hypotheses avoid similar modifications
- Agent organizes attempts as a tree where parent hypotheses seed the parameter space for children
- Search is depth-first with bounded width per node

**Control (Flat Queue)**
- Agent generates a modification proposal without explicit hypothesis structure
- Agent executes the modification and observes outcome
- Outcome is recorded in a flat log with no dependency structure
- Subsequent proposals are generated independently; past failures do not structure the parameter space
- Modifications are executed in queue order with no prioritization by prior signal

### 1.2 Shared Constraints

- **Compute budget**: Fixed at T attempts per arm (e.g., T=50, chosen from ResearchClawBench rubric-scoring precedent of 50-70 steps per task)
- **Backbone model**: Same model (e.g., Claude 3.5 Sonnet) serves both arms
- **Artifact type**: Fixed Python code module or configuration file (concrete example: optimizing hyperparameters of a PyTorch training loop for a classification task)
- **Task domain**: Held-out optimization problem with a measurable rubric (e.g., test-set accuracy, latency, memory footprint)

### 1.3 Held-Out Evaluation

- Final artifact from each arm is evaluated on a held-out test set
- Evaluation uses a pre-registered rubric (e.g., accuracy threshold, efficiency metric) decided before any arm runs
- No feedback from held-out set flows back to either arm during attempts

---

## 2. Ablation Studies

### Ablation 1: Hypothesis Structure Without Propagated Insight

**Condition**: "Explicit Hypothesis, No Propagation"
- Agent is required to generate explicit hypotheses (as in Treatment)
- Agent observes outcomes of attempts
- But failed hypotheses do NOT constrain subsequent proposals
- Proposals are still generated independently (like Control)

**Purpose**: Isolates whether requiring articulated hypotheses (forcing reasoning transparency) provides benefit independent of using failure information to prune the search space.

**Evidence basis**: 2607.09195 (Hypothesis Evolution Protocol) emphasizes both articulation and evolution; this ablation separates them.

### Ablation 2: Flat Queue With Outcome Logging But No Trajectory Analysis

**Condition**: "Control With Full History Access"
- Agent operates in flat queue mode
- Agent has full access to the complete history of all prior modifications and their outcomes
- Agent may review this history but is not required to; proposing the next attempt does not require referencing past attempts
- No explicit tree structure

**Purpose**: Tests whether the improvement from Treatment is due to the tree structure (forcing systematic exploration) versus just having outcome information available. If Control with history access performs similarly to Treatment, the tree structure itself is not driving the benefit.

**Evidence basis**: 2608.01913 (Search Agent Failure Modes) and 2609.00038 (Trajectory-Judge Blind Spots) both suggest that outcome visibility and trajectory access are insufficient without structural reasoning about how attempts relate to each other.

---

## 3. Analysis Plan

### 3.1 Primary Outcome

**Metric**: Held-out rubric score of the final artifact from each attempt budget

- **Definition**: A numeric or categorical score assigned by the pre-registered rubric
- **Collection**: After T attempts, the final artifact is frozen and evaluated on the held-out test set using only the rubric (no additional feedback to the agent)
- **Example rubrics** (chosen from ResearchClawBench / experimental design literature):
  - Classification accuracy on held-out test set
  - Multi-stage rubric (0=non-functional, 1=functional but poor performance, 2=meets baseline, 3=exceeds baseline) as in 2608.03501
  - Composite score combining multiple objectives (speed + accuracy) following 2606.07591 precedent

### 3.2 Secondary Outcomes (Process-Level)

To understand *why* one arm outperforms the other, we measure:

1. **Hypothesis reuse rate**: Proportion of agent proposals that explicitly reference or build on prior attempts (Treatment only). Evidence: 2607.09195 tracks hypothesis progression explicitly.

2. **Proposal diversity**: Entropy or Levenshtein distance of the set of all proposed modifications. If Treatment is more focused, diversity will be lower; if it explores more systematically, it may be higher. Evidence: 2608.01913 measures search breadth.

3. **First-attempt success rate**: Proportion of attempts that improve performance (within each arm). Evidence: 2605.30315 tracks resolution in early comparisons; 2608.01913 measures early-stage efficacy.

4. **Failure recovery time**: Number of attempts from a failed modification until the next improvement. Measures how quickly each arm escapes local minima. Evidence: 2608.01913 diagnoses failure modes.

5. **Judge consistency (meta-level)**: Inter-rater reliability of the rubric scorer if human judges rate a sample of artifacts. Evidence: 2608.29517 measures LLM judge severity and drift; if the scoring rubric uses an LLM judge, we apply pre-registered judge audit.

### 3.3 Uncertainty Quantification

#### Sample Size and Power

- **Inference target**: Does Treatment > Control on held-out rubric score?
- **Minimum detectable effect**: A 1-point improvement on a 5-point rubric (or equivalent) is the pre-registered threshold (aligned with 2605.30315 paired resolution norms)
- **Required sample size**: Using 2010.06595 power norms for LLM evaluations and 2605.30315 paired resolution guidance:
  - Expected variance in rubric scores: based on pilot data or prior benchmarks (e.g., OpenLLM Leaderboard shows ~8% variance in adjacent-rank pairs)
  - α = 0.05 (two-sided), 1 − β = 0.8
  - Estimated n = 30–40 held-out tasks per arm
  
  **Evidence basis**: 2605.30315 shows that 11/40 Open LLM Leaderboard comparisons are unresolved at (0.05, 0.8); this informs our sample-size defensibility.

#### Variance Decomposition

- **Within-task variance**: Repeated runs of the same arm on the same task; captures model sampling noise
- **Between-task variance**: Across different held-out tasks of similar difficulty; captures task heterogeneity
- **Approach**: Fit variance-components model following 2607.13304, estimating σ²(task) and σ²(model randomness)
- **Stratification**: Stratify tasks by difficulty (easy/medium/hard) based on baseline performance; ensure both arms receive equal task difficulty distribution

#### Outcome-Only vs Trajectory Judging

- **Primary judge**: The held-out rubric applied to final artifact (outcome-only)
- **Secondary judge**: A trajectory auditor (human or trained LLM) who reviews a sample (20%) of agent logs to verify that the outcome reflects genuine progress, not lucky parameter settings
- **Evidence basis**: 2609.00038 (trajectory-judge blind spots) shows outcome-only evaluation misses process quality; we include trajectory sampling to detect and quantify this blind spot

#### Judge Audit for LLM-Based Rubric

If the rubric uses an LLM to evaluate artifacts:
- **Severity audit**: Verify that the judge does not systematically rate one arm higher (following 2608.29517 pre-registered audit protocol)
- **Temporal drift**: Check if judge consistency degrades over time (common in long evaluation sequences per 2608.29517)
- **Mitigation**: Shuffle arm labels before judging; use a fixed-seed random permutation of rubric examples to anchor the judge's standard

---

## 4. Concrete Resources

### 4.1 Backbone Model

- **Model**: Claude 3.5 Sonnet (fixed across both arms)
- **Rationale**: Established in autonomous agent benchmarks (e.g., ResearchClawBench 2606.07591); stable inference API; sufficient reasoning for hypothesis articulation
- **Access**: Anthropic Claude API

### 4.2 Artifact Domain and Task Set

**Primary artifact type**: Hyperparameter configuration for a PyTorch image classification model or optimization algorithm

**Justification**: 
- Objective, measurable outcome (test accuracy)
- Bounded parameter space (prevents infinite action space)
- Precedent in automated machine learning and AutoML (e.g., Hyperband, BOHB frameworks)
- Task heterogeneity available: vary dataset (CIFAR-10, MNIST, custom), model architecture (ResNet, ViT variants), class imbalance

**Held-out test set**: 
- 30–40 distinct optimization tasks, stratified by difficulty
- Each task: train/validation set (70/15) held during agent attempts; test set (15%) withheld for final evaluation
- Baseline performance known for each task (e.g., default hyperparameters)

### 4.3 Rubric Definition (Pre-Registered)

Example rubric (stage-isolated scoring following 2608.03501):

| Score | Criterion |
|-------|-----------|
| 0 | Artifact does not run or produces errors |
| 1 | Artifact runs; test accuracy is worse than or equal to baseline (no improvement) |
| 2 | Test accuracy improves by 1–3% over baseline |
| 3 | Test accuracy improves by 3–6% over baseline |
| 4 | Test accuracy improves by >6% over baseline |
| 5 | Artifact also reduces inference latency by >10% with no accuracy drop |

**Redline (stage isolation)**: Artifacts scoring 0 are discarded from further analysis (non-functional); primary comparison uses scores 1–5.

### 4.4 Compute Budget

- **Per-arm attempts**: T = 50 (aligned with ResearchClawBench rubric-step guidance in 2606.07591)
- **Compute cost per attempt**: Model depends on task (code review + execution + output parsing); estimate ~2–3 tokens per proposal + feedback parsing
- **Total**: ~50 × 2.5K tokens per arm ≈ 125K tokens per arm, or ~5M tokens for 40 tasks × 2 arms

### 4.5 Evaluation Infrastructure

1. **Rubric scorer**: Pre-trained or LLM-based scorer (if LLM, audit per 2608.29517)
2. **Trajectory logger**: Capture all agent proposals, outcomes, and intermediate states
3. **Held-out test runner**: Isolated compute environment for final artifact evaluation (no data leakage)
4. **Judge blinding**: Randomized arm labels before rubric scorer sees artifacts

---

## 5. Outcome Metrics and Interpretation

### 5.1 Primary Statistical Test

**Test**: Welch's t-test (unequal variance) on mean held-out rubric scores, Treatment vs Control, one-sided (H1: Treatment > Control)

- **α = 0.05** (one-sided)
- **Effect size of interest**: d ≥ 0.5 (small-to-medium effect per Cohen)
- **Null hypothesis**: Mean rubric score (Treatment) ≤ Mean rubric score (Control)
- **Alternative**: Mean rubric score (Treatment) > Mean rubric score (Control)

**Interpretation**:
- **p < 0.05**: Reject null; Treatment significantly outperforms Control
- **p ≥ 0.05**: Fail to reject null; no significant difference detected (but CI will quantify the range of plausible effects)

### 5.2 Confidence Intervals and Effect Bounds

- **95% CI on difference**: [LB, UB]
  - If LB > 0: Treatment is clearly better (whole CI above zero)
  - If UB < 0: Control is clearly better (CI entirely below zero)
  - If CI straddles zero: difference is inconclusive at α=0.05

**Evidence basis**: 2605.30315 emphasizes that reported pairwise rankings should include resolution targets and CI; we adopt this reporting standard.

### 5.3 Heterogeneous Treatment Effects

**Sub-group analysis**:
- **By task difficulty**: Does Treatment benefit scale with task difficulty? (e.g., harder tasks may benefit more from structured search)
- **By attempt horizon**: Does the advantage of Treatment emerge early (first 10 attempts) or late?
- **By modification type**: Do certain types of modifications (e.g., learning rate vs batch size) show larger improvements under Treatment?

**Evidence basis**: 2403.14403 (Adaptive-RAG) shows that routing decisions depend on problem complexity; our heterogeneous effects analysis follows this principle.

### 5.4 Process-Level Metrics

| Metric | Interpretation |
|--------|---|
| Hypothesis reuse rate | High in Treatment: agent systematically builds on prior attempts; low in Control (not applicable) |
| Proposal diversity | Measures breadth of exploration; Treatment may be more focused (lower diversity) if it narrows on good regions |
| First-attempt success | High = efficient search; low = random exploration. Expected: Treatment > Control |
| Failure recovery time | Low = quick escape from local minima; high = stuck in poor regions. Expected: Treatment < Control |

**Evidence basis**: 2608.01913 defines these failure-mode metrics for search agents.

---

## 6. Uncertainty and Caveats

### 6.1 Known Threats to Validity

1. **Judge bias**: If the rubric scorer is an LLM, it may exhibit severity drift or halo effects (2608.29517). Mitigation: pre-registered judge audit with shuffled arm labels.

2. **Outcome-only blindness**: The held-out rubric only sees the final artifact, not the trajectory. An arm might reach the right answer "the wrong way" (2609.00038). Mitigation: trajectory audit on a sample.

3. **Variance in LLM generation**: Even with a fixed backbone model, LLM outputs are non-deterministic (2607.13304). Mitigation: multiple random seeds per task; fit variance-components model.

4. **Task selection**: Artifact optimization may not generalize to other domains (e.g., scientific discovery, code generation). Scope is limited to hyperparameter optimization by design.

5. **Compute budget coupling**: The T=50 attempt limit was chosen based on ResearchClawBench norms, but may not be optimal for this task domain. We will report power analysis sensitivity to this choice.

### 6.2 Assumptions

- **Assumption 1**: The backbone model is sufficiently capable of generating hypotheses and executing modifications. Validated by prior use in agent benchmarks.
- **Assumption 2**: The rubric is reliable and interpretable. Validated by pre-registration and judge audit.
- **Assumption 3**: Held-out tasks are representative of the broader optimization problem class. Addressed via stratification and task diversity.

### 6.3 Limitations of the Design

- **No within-task adaptation**: We do not use held-out feedback to adapt T per task; all tasks receive T=50 attempts regardless of convergence.
- **Single backbone model**: Results do not speak to whether the advantage of Treatment transfers to smaller or larger models.
- **Single artifact domain**: Hyperparameter optimization; does not cover code generation, algorithm design, or scientific hypothesis formation.

---

## 7. Implementation Checklist

### Pre-Experiment
- [ ] Pre-register rubric definition, task difficulty stratification, and primary statistical test (OSF or similar)
- [ ] Pilot n=2–3 tasks on both arms to validate rubric scorability and compute cost estimates
- [ ] Train or configure the LLM judge (if used); conduct severity audit on a hold-out rubric-example set
- [ ] Prepare 40 held-out tasks with train/val/test splits and baseline performance
- [ ] Set random seed for task ordering and initial proposal generation

### Experiment
- [ ] Run Treatment arm: n=40 tasks, T=50 attempts each, log all hypotheses and outcomes
- [ ] Run Control arm: n=40 tasks, T=50 attempts each, log all proposals and outcomes
- [ ] Freeze all artifacts after T attempts; no feedback from held-out set
- [ ] Evaluate final artifacts on held-out test set using pre-registered rubric
- [ ] Log artifact source, execution logs, and judge reasoning (for trajectory audit)

### Analysis
- [ ] Compute primary outcome (mean rubric score per arm, Welch's t-test, 95% CI)
- [ ] Fit variance-components model (task, model randomness)
- [ ] Conduct heterogeneous effects analysis (difficulty, attempt horizon, modification type)
- [ ] Audit judge consistency (severity, temporal drift) on a random sample (20%) of artifacts
- [ ] Perform trajectory audit on a random sample (20%) of agent logs
- [ ] Report secondary metrics (hypothesis reuse, diversity, recovery time)

### Post-Experiment
- [ ] Write pre-registered report (registered on OSF before running); deviations clearly marked
- [ ] Publish de-identified data and code (if artifact licenses permit)
- [ ] Discuss heterogeneous effects and generalizability limitations

---

## 8. Evidence Citations

This design draws on the following released evidence excerpts:

- **2010.06595**: Statistical power norms for LLM evaluation; informs minimum detectable effect and sample size.
- **2403.14403** (Adaptive-RAG): Complexity-conditioned routing; justifies heterogeneous effects analysis.
- **2605.30315**: Paired resolution targets and power analysis; establishes CI reporting standards and unresolved-pair prevalence.
- **2606.07591** (ResearchClawBench): Rubric-based scoring, stage isolation, and 50-step attempt budgets; provides precedent for artifact optimization benchmarking.
- **2607.09195**: Hypothesis Evolution Protocol; directly supports the Treatment condition design.
- **2607.13304**: Variance-components decomposition; informs uncertainty estimation with within-task and between-task variance.
- **2608.01913**: Search agent failure modes and process-level metrics (diversity, recovery time, first-attempt success); shapes secondary outcome definitions.
- **2608.03501**: Autonomous experimental design; informs rubric stage isolation and redline scoring.
- **2608.29517**: LLM judge audits for severity, halo, and drift; mandatory if rubric uses LLM scorer.
- **2609.00038** (Trajectory-Judge Blind Spots): Outcome-only evaluation blind spots; justifies trajectory audit in secondary evaluation.

---

## 9. Summary Table

| Component | Specification |
|-----------|---|
| **Research Question** | Does hypothesis tree + propagated insight outperform flat queue for agent artifact optimization? |
| **Design** | Two-arm randomized comparison with held-out evaluation |
| **Primary Arm** | Hypothesis-tree with propagated insight (Treatment) |
| **Control Arm** | Flat queue of independent attempts (Control) |
| **Ablation 1** | Explicit hypothesis, no propagation (confound isolation) |
| **Ablation 2** | Flat queue with full history access (structure vs information) |
| **Shared Constraints** | Fixed compute (T=50 attempts), same backbone model (Claude 3.5 Sonnet), held-out evaluation |
| **Primary Outcome** | Held-out rubric score (5-point scale: 0=non-functional to 5=high performance + efficiency) |
| **Sample Size** | n=40 held-out tasks per arm (stratified by difficulty) |
| **Statistical Test** | Welch's t-test, one-sided, α=0.05; 95% CI on difference |
| **Secondary Outcomes** | Hypothesis reuse, proposal diversity, first-attempt success, failure recovery time |
| **Uncertainty** | Variance-components model, judge audit, trajectory audit (20%), sensitivity to compute budget |
| **Evidence Basis** | 10 released excerpts from 2010–2609 (arXiv identifiers above) |

---

## 10. Next Steps (Not This Document)

Once this design is approved:
1. Pre-register on OSF (deviations allowed but flagged)
2. Pilot on n=2–3 tasks; refine rubric and compute estimates
3. Execute experiment (4–8 weeks depending on parallelization)
4. Analyze and report per pre-registered plan

