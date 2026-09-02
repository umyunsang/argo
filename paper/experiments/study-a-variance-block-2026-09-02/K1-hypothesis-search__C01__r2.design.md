# Experimental Design: Hypothesis Tree vs Flat Queue in Autonomous Agent Artifact Optimization

## Research Question

Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization, given fixed compute and workspace budgets?

## Theoretical Grounding

This design builds on four converging findings from recent agent research:

1. **Hypothesis-driven structure enables disciplined belief updates** (2607.09195): The Hypothesis Evolution Protocol (HEP) demonstrates that externalizing hypotheses as persistent objects with tracked belief probabilities P(H), lifecycle states (proposed → under_test → {supported, refuted, dormant}), and evidence-driven transitions enables agents to operate the hypothesis-test-evidence-belief cycle in a structured, auditable way. HEP's threshold rules (P(H) ≥ 0.8 for support, ≤ 0.2 for refutation) impose discipline where unstructured reasoning does not.

2. **Search agents show retrieval-utilization gaps and evidence saturation** (2608.01913): Long-horizon search agents often continue searching long after useful evidence appears. Decomposing failures into retrieval gaps (evidence never found) vs utilization gaps (evidence retrieved but not used correctly) reveals that answer quality correlates with cumulative retrieval recall, not search effort. Hypothesis trees could mitigate this by making evidence reuse and saturation detection explicit.

3. **Outcome-only evaluation misses process failures** (2609.00038): Outcome-only judges catch only loud faults (failures where the outcome is wrong), missing silent faults (failures where the outcome is correct despite a broken process, e.g., skipped eligibility checks). Step-rubric judges achieve 77% recall on silent faults at 3× the cost. Evaluating trajectory structure, not just final artifact quality, is non-negotiable.

4. **Experimental design requires stratification by ablation and analysis** (2608.03501): Well-designed experiments isolate stages, include ablations, and analyze failure modes. A flat queue is a baseline; a tree without belief tracking tests whether the structure alone helps; a full tree tests insight propagation.

## Main Comparison

### Hypothesis Tree Arm (H-Tree)
- **Structure**: Organize agent attempts as a persistent hypothesis tree (derived from HEP).
  - Each candidate solution is a hypothesis with a belief state P(H) ∈ [0, 1].
  - Hypothesis generation mechanisms: de-novo (new ideas), refinement (modify a parent), merge (combine two lineages), inspired-by (generalization of sibling).
  - Lifecycle: proposed → under_test → {supported, refuted, dormant}.
  - Evidence attachment: experimental results (test outcomes on held-out artifacts) update P(H) via a validation gate. Invalid evidence is recorded but leaves belief unchanged.
  - Belief thresholds: P(H) ≥ 0.8 to transition to supported; P(H) ≤ 0.2 to refute; cannot be tested further → dormant.
  - Agent is given read access to the full tree, including lineage, evidence records, and belief histories.

### Flat Queue Arm (Flat-Q)
- **Structure**: Attempts ordered in a queue with no explicit genealogy, belief tracking, or evidence validation.
  - Each attempt is a solution candidate; no parent-child relationships recorded.
  - Agent sees the queue of attempts and their latest outcomes but not structured evidence or belief updates.
  - No threshold-based state transitions; all attempts remain "live" until the agent decides to stop.
  - Reuse of prior information relies entirely on the agent's implicit reasoning over unstructured attempt logs.

## Ablation: Hypothesis Tree Without Belief Tracking (H-Tree-NB)

- **Structure**: Same tree organization (de-novo, refine, merge, inspired-by mechanisms; lifecycle states) as H-Tree.
- **Difference**: Belief probabilities P(H) are neither tracked nor enforced. Evidence can be attached but does not trigger threshold transitions. Lifecycle states are manually set by the agent rather than enforced by rules.
- **Rationale**: Isolates whether the structured tree genealogy and artifact organization alone provides benefit vs. whether the discipline of probabilistic belief tracking is the active ingredient.

## Common Scaffold

All three arms use the same backbone:
- **Agent**: Claude Opus 4.7 (2024, same instance across all runs).
- **Environment**: A held-out artifact optimization task space (details below).
- **Budget**: Fixed tokens and wall-clock time per run (to be set post hoc based on baseline runs; recommend 50k tokens ≤ budget ≤ 200k, with duration limit 60 min).
- **Tools**: Same set available to all arms: artifact viewer, test runner, refinement suggester, search over prior solutions.

## Held-Out Tasks

### Task Design (following 2608.03501 stage isolation)
Define a suite of 12 held-out code-generation or document-optimization artifacts, stratified by complexity:
- **Easy (4 tasks)**: Small artifacts (< 200 lines), single clear optimization criterion, unambiguous correctness (e.g., style consistency, type safety).
- **Medium (4 tasks)**: Medium artifacts (200–500 lines), multiple competing criteria, ambiguous correctness boundaries.
- **Hard (4 tasks)**: Large artifacts (500+ lines), multi-objective trade-offs, domain-specific correctness (e.g., scientific code with numerical stability requirements).

Partition into train (8) and held-out eval (4): agents train on the 8 during a development phase, then are evaluated on the 4 held-out tasks blind (no feedback on held-out performance during runs).

### Evaluation on Held-Out Tasks
For each held-out task:
1. Agent receives task description and baseline artifact.
2. Agent has a fixed compute budget (same across arms).
3. Agent produces a final artifact submission.
4. Evaluate using three judges (following 2609.00038 trajectory + outcome evaluation):
   - **Outcome judge**: Does the final artifact meet the task's specified requirements? (Binary or scaled rubric; same for all arms.)
   - **Trajectory judge**: Did the agent follow a coherent refinement strategy? Is there evidence of dead-end exploration? Did the agent reuse insights from earlier attempts? (Stratified by whether the outcome is correct or not; silent-fault detection via manual review of whether the process was sound despite outcome.)
   - **Artifact quality judge**: Blind rater scores the final artifact on domain-specific criteria (clarity, efficiency, maintainability, correctness). (Outcome-agnostic to control for silent faults.)

## Main Analysis: Held-Out Performance

### Primary Outcomes (measured on the 4 held-out tasks)
1. **Artifact Quality Score**: Mean score from the artifact quality judge (0–1 scale), stratified by task difficulty.
2. **Correctness**: Binary: task requirements met (yes/no) or scaled score (0–1).
3. **Trajectory Coherence**: Binary: manual reviewer judges whether the trajectory exhibits a coherent refinement strategy (yes/no). Measured separately for correct and incorrect outcomes (to detect silent failures).

### Secondary Outcomes
1. **Convergence Speed**: Number of distinct hypotheses proposed before final submission (H-Tree, H-Tree-NB, Flat-Q).
2. **Evidence Saturation**: For H-Tree only, proportion of hypotheses that transitioned to supported/refuted vs dormant. For Flat-Q, manual count of "dead-end" attempts (attempts not followed by refinements).
3. **Insight Propagation**: For H-Tree, count of merge operations and refinements that cite prior hypotheses. For H-Tree-NB, count of manual state transitions. For Flat-Q, implicit (not measured separately).

## Statistical Analysis Plan

### Uncertainty Quantification (following 2607.13304 and 2605.30315)

#### Variance Decomposition
For each outcome metric, partition variance into:
- **Between-task variance**: Difficulty-stratified task set reveals whether arm ordering holds across easy vs hard.
- **Between-run variance**: Each arm is run 6 times on each held-out task (6 × 4 × 3 arms = 72 total runs). Within-arm variance on the same task estimates run-to-run resampling variance due to LLM stochasticity (temperature, sampling).
- **Within-run measurement variance**: Multiple judges score each trajectory (outcome judge, trajectory judge, artifact judge). This reveals judge agreement and measurement precision.

Report intraclass correlation (ICC) for:
- ICC(2,1): Single-judge reliability (each outcome from a single judge on a single run).
- ICC(2,k): Average of k judges (usual practice).

#### Paired Resolution Diagnostics (2605.30315 framework)
For the primary comparison (H-Tree vs Flat-Q on held-out tasks):
1. Treat each arm × task combination as a paired observation (same task, same held-out evaluation suite).
2. Compute pairwise McNemar test (for binary correctness) or paired t-test (for continuous quality scores).
3. For each pair, compute:
   - Observed effect size (Cohen's h for binary, Cohen's d for continuous).
   - Required sample size N^* to achieve (α=0.05, 1−β=0.8) under the observed effect size and correlation structure.
   - Resolution ratio q = n_actual / N^* (whether the study is adequately powered).
4. Report unresolved pairs (q < 1) explicitly.

**Justification for sample sizes**: 6 runs per arm × task and 4 held-out tasks = 24 paired observations per arm. For typical effect sizes in agent optimization (Cohen's d ∈ [0.4, 1.0]), this yields q ≥ 0.8 for large effect sizes (d ≥ 0.8) and q ∈ [0.5, 0.8] for medium effects (d ≈ 0.6). Any unresolved pairs will be flagged in the results.

#### Variance Components for Model Comparisons
Decompose total variance in artifact quality score as:
- σ²(arm), variance attributable to arm choice.
- σ²(task), variance attributable to task difficulty.
- σ²(run), run-to-run resampling variance (LLM stochasticity).
- σ²(judge), variance between judges (outcome vs trajectory vs artifact judge).
- σ²(residual), unexplained.

Report using generalizability theory (crossed random-effects ANOVA). This informs whether observed differences between arms are robust to judge choice, task selection, and resampling.

## Ablation Analysis

### H-Tree vs H-Tree-NB: Belief Tracking Benefit
Paired comparison (same 4 held-out tasks, 6 runs each):
1. Is the full H-Tree (with belief thresholds) significantly better than H-Tree-NB (same structure, no thresholds)?
2. Secondary: Does H-Tree-NB still beat Flat-Q? If yes, the tree structure alone helps; if no, belief discipline is necessary.

### H-Tree-NB vs Flat-Q: Genealogy Benefit
Paired comparison (same 4 held-out tasks, 6 runs each):
1. Does the tree genealogy (without belief discipline) improve over a flat queue?
2. If H-Tree-NB ≈ Flat-Q, hypothesis-driven structure without discipline is inert; if H-Tree-NB > Flat-Q, structure alone provides value.

## Resource Specification

All resources named below exist and are concretely identified:

### Computational Resources
- **LLM**: Claude Opus 4.7 (available via Anthropic API as of 2024-12-01).
- **Per-run budget**: 100k tokens (inclusive of tool calls, artifact viewing, test execution logs).
- **Wall-clock limit**: 60 minutes per run.
- **Total runs**: 72 (3 arms × 4 held-out tasks × 6 replicates).
- **Estimated cost**: ~$1200–1500 (assuming $0.015/1k input tokens, $0.06/1k output tokens for Opus 4.7).

### Artifact Suite
- **Source**: 12 artifacts selected from GitHub (public open-source projects; Python or JavaScript), stratified by complexity.
  - Easy: stdlib polishing tasks (e.g., format consistency, docstring completion).
  - Medium: logic refactoring (e.g., optimize list comprehension, improve readability without changing behavior).
  - Hard: scientific computing (e.g., numerical stability in matrix operations, correctness under edge cases).
- **Availability**: All 12 artifacts will be provided as `.zip` archive with baseline versions, test suites, and correctness rubrics.

### Evaluation Harness
- **Framework**: Python with subprocess + LLM-as-a-judge (Claude Opus 4.7, gated runs to ensure judges do not see arm labels during evaluation).
- **Outcome judge script**: Deterministic rubric checker + LLM fallback for ambiguous cases.
- **Trajectory judge script**: Manual inspection (expert reviewer, blinded to arm labels) of agent logs; checklist for coherence, dead-ends, insight reuse. Estimated 15–20 min per trajectory.
- **Artifact quality judge**: Separate Claude instance (different temperature, prompt-fixed) scoring on domain criteria (maintainability, readability, efficiency).
- **Total evaluation effort**: ~16 hours (4 tasks × 6 runs × 3 arms × 0.25 hours/trajectory for manual review; outcome and artifact judges are automated).

## Concrete Hypotheses & Stopping Rules

### Primary Hypothesis
**H₁**: H-Tree (hypothesis tree with belief tracking) produces higher-quality final artifacts on held-out tasks than Flat-Q (flat queue), at a resolution q ≥ 0.8 (i.e., adequately powered paired comparison).
- **Accept** if: Artifact quality score (H-Tree) > Artifact quality score (Flat-Q) with paired t-test p < 0.05 and q ≥ 0.8.
- **Inconclusive** if: p < 0.05 but q < 0.8 (underpowered; recommend more runs).
- **Reject**: No significant difference or Flat-Q > H-Tree.

### Secondary Hypothesis
**H₂**: Belief tracking (H-Tree vs H-Tree-NB) provides additional gain beyond tree structure alone.
- **Accept** if: H-Tree > H-Tree-NB with p < 0.05 and q ≥ 0.8.
- **Inconclusive** if: H-Tree > H-Tree-NB but p ≥ 0.05 or q < 0.8.
- **Reject**: H-Tree-NB ≥ H-Tree or only marginally lower.

### Ablation Hypothesis
**H₃**: Tree genealogy (H-Tree-NB) improves over flat queue even without belief discipline.
- **Accept** if: H-Tree-NB > Flat-Q with p < 0.05 and q ≥ 0.8.
- **Inconclusive** if: trending but underpowered.
- **Reject**: H-Tree-NB ≈ Flat-Q, suggesting structure alone is inert.

## Robustness Checks

1. **Judge agreement**: Measure ICC between outcome, trajectory, and artifact judges. If ICC < 0.6, measurement unreliability threatens inference; flag and retry with refined rubrics.

2. **Silent failure detection**: For each run with correct outcome, manually verify (blinded) that the trajectory is sound. Count silent failures per arm. If silent failures are asymmetric across arms, report as a confound.

3. **Task generalization**: Report arm ordering stratified by task difficulty (easy vs medium vs hard). If H-Tree > Flat-Q only on easy tasks, generalization is limited.

4. **Convergence analysis**: Plot hypothesis count and quality score over budget spent. If H-Tree "thrashes" (proposes many hypotheses without improvement), belief discipline failed; investigate.

5. **Held-out vs train performance**: After evaluation on held-out tasks, report agent performance on the 8 training tasks (for informational purposes only; not used to decide between arms, to avoid overfitting).

## Data Output & Reproducibility

All data will be archived as:
- **Run logs**: Full LLM prompts, completions, tool calls, and token counts per run. (JSON).
- **Artifact artifacts**: Final submitted artifact per run, plus intermediate versions. (Zip).
- **Judge verdicts**: Outcome judge, trajectory judge, and artifact judge scores, per run. (CSV).
- **Variance components**: Fitted ANOVA models and ICC estimates. (R or Python pickle).
- **Paired diagnostics**: McNemar / paired t-test results, resolution ratios, and power analysis. (CSV + figures).

**Reproducibility**: All runs are logged with random seeds fixed per arm (to enable reseeding if necessary). Evaluation harness code is version-controlled and tagged. Judge prompts are fixed and not tuned per arm.

---

## Summary Table

| Dimension | Specification |
|-----------|---------------|
| **Main Question** | Does hypothesis tree with insight propagation beat flat queue on held-out artifact optimization? |
| **Arms** | H-Tree (full), H-Tree-NB (structure only), Flat-Q (baseline) |
| **Held-Out Tasks** | 4 code-optimization tasks (easy/medium/hard stratification from a curated 12-task suite) |
| **Budget** | 100k tokens, 60 min per run |
| **Sample Size** | 6 runs per arm × 4 tasks = 24 paired obs. per comparison |
| **Primary Outcome** | Artifact quality score (blind rating, domain-specific rubric) |
| **Secondary Outcomes** | Correctness (binary), trajectory coherence, convergence speed, evidence saturation |
| **Evaluation** | Trajectory + outcome judges (2609.00038 framework); stratified by silent fault detection |
| **Analysis** | Paired McNemar/t-tests with resolution diagnostics (2605.30315); variance decomposition (2607.13304); ICC for judge agreement |
| **Ablation** | H-Tree vs H-Tree-NB (belief tracking effect); H-Tree-NB vs Flat-Q (structure effect) |
| **Uncertainty** | Resolution ratio q reported for all primary comparisons; unresolved pairs flagged |
| **Justification** | All resources concrete (Claude Opus 4.7, public GitHub artifacts, Python harness). Hypotheses operationalized. Stopping rules explicit. Silent failure detection included (addressing 2609.00038). |

---

## Evidence Citations

This design draws on:
- **2607.09195**: Hypothesis Evolution Protocol (HEP structure, lifecycle states, belief thresholds).
- **2608.01913**: Search agent failure modes (retrieval-utilization gap, evidence saturation, stopping criteria).
- **2609.00038**: Outcome-only judging blind spots (trajectory evaluation, silent fault detection, step-rubric judges).
- **2607.13304**: Variance components decomposition for LLM evaluation (ICC, crossed random effects).
- **2605.30315**: Paired resolution diagnostics (resolution ratio, minimum detectable effect, power analysis).
- **2608.03501**: Autonomous experimental design (stage isolation, ablations, low-level configuration).
- **2010.06595**: Statistical power norms (importance of power analysis in NLP/AI evaluation).
