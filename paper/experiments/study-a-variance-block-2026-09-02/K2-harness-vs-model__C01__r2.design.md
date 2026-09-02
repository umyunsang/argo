# Experimental Design: K2 Harness vs. Model — Measuring Self-Improvement

## 1. Research Question and Problem Statement

**Research Question:** How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

**Core Challenge:** A system that improves task execution could do so by:
1. Better structuring its internal workflow (harness improvement) — the object of measurement
2. Crafting a better prompt that the model responds to (model improvement or "prompt injection") — a confound
3. A combination of both

Distinguishing these requires a design that isolates the harness signal from the prompt signal.

---

## 2. Main Comparison: Three Conditions

### 2.1 Condition A: Candidate Harness (Test)
- **Harness version:** Improved harness (snapshotted candidate)
- **Model:** Same underlying model as baseline
- **Prompt:** Same prompt engineering as baseline (no manual enhancement)
- **Evaluation:** On held-out evaluation set

### 2.2 Condition B: Baseline Harness + Enhanced Prompt (Prompt Confound Control)
- **Harness version:** Same as baseline (status quo)
- **Model:** Same underlying model as baseline
- **Prompt:** Human-crafted or LLM-optimized prompt designed to match or exceed the quality that Condition A achieves
- **Evaluation:** On held-out evaluation set
- **Purpose:** Disentangle "better harness structure" from "better prompt to the same model"

### 2.3 Condition C: Baseline Harness (Control)
- **Harness version:** Status quo (original)
- **Model:** Same underlying model
- **Prompt:** Status quo
- **Evaluation:** On held-out evaluation set

**Key Constraint Compliance:** Scoring runs on the held-out evaluation set *outside* any candidate workspace. No scoring logic inside the harness.

---

## 3. Primary Analysis: Attribution and Power

### 3.1 Main Effect: Harness Improvement
**Estimand:** Paired mean difference in task-level evaluation score.
- Compute: `δ_harness = mean(Score_A − Score_C)` over all tasks in held-out set
- **Null hypothesis:** `H₀: δ_harness = 0`
- **Test:** Paired t-test (or paired bootstrap if normality violated)
- **Why paired:** Per 2605.30315, paired designs have ~2.15× better power than unpaired for within-subject LLM comparisons

### 3.2 Prompt Confound Verification
**Estimand:** Paired mean difference in prompt-only condition.
- Compute: `δ_prompt = mean(Score_B − Score_C)` over held-out set
- **Interpretation logic:**
  - If `|δ_harness| > |δ_prompt|` and both are in the same direction → harness is the dominant signal
  - If `|δ_prompt| ≥ |δ_harness|` → prompt engineering alone explains the improvement (harness improvement is spurious)
  - If `δ_harness` and `δ_prompt` have *opposite* signs → harness improvement exists but is masked by bad prompt wording in Condition A (design issue to fix)

### 3.3 Resolution Diagnostic
Apply the framework from 2605.30315 to report **resolution ratio** `q = N / N*` for each key comparison:
- Compute minimum detectable effect (MDE) at current N (held-out set size)
- Compute required N* at target effect size (e.g., δ = 1 point on rubric, if rubric is out of 5)
- Report q for both `δ_harness` and `δ_prompt`
- **Verdict:** Pair is "resolved" if `q ≥ 1`, meaning the observed gap is statistically distinguishable from noise at (α=0.05, 1−β=0.80)

**Justification (2605.30315):** Leaderboard evaluations of LLMs are frequently *unresolved* — the sample size does not support the claimed ranking. This diagnostic surfaces that risk.

---

## 4. Ablation 1: Model Generalization

**Question:** Is the harness improvement specific to this model, or does it generalize to other models?

### 4.1 Design
- Run Conditions A and C on a *different* model (a second model of comparable or different size)
- Compute `δ_harness_model2 = mean(Score_A_model2 − Score_C_model2)`
- Compare to `δ_harness` on the first model

### 4.2 Interpretation
- **Strong generalization:** δ values are similar magnitude and direction
  - *Inference:* Harness improvement is a property of the task structure, not model-specific coupling
  - *Citation:* Supports claim that improvement is truly a harness improvement
- **Weak generalization:** δ values diverge by model
  - *Inference:* Harness improvement may rely on model-specific quirks (e.g., sensitivity to a particular prompt pattern)
  - *Inference:* Limits applicability; harness may need re-tuning per model
- **Reversal:** δ_harness_model2 is negative or near-zero
  - *Inference:* Harness may degrade performance on this model; interaction effect present

### 4.3 Variance Components
Per 2607.13304 (variance decomposition in LLM measurement):
- Run both models on the same held-out prompts with ~5 resamples per task
- Fit a crossed random-effects model: `Score ~ (1|Task) + (1|Model) + (1|Harness) + (1|Resample)`
- Extract ICCs (intraclass correlations) for each component
- Compute decision-study projections: at what allocation of resamples, models, and harness conditions does reliability stabilize?

---

## 5. Ablation 2: Hidden vs. Visible Failure Modes

**Question:** Does the harness improve on aspects that matter (from the evaluator's perspective), or does it optimize for aspects the rubric can't see?

### 5.1 Design: Trajectory-Level and Outcome-Only Scoring

Per 2609.00038 (trajectory-judge study):
- Score each task submission using *two* evaluation lenses:
  - **Outcome-Only:** Judge sees only the final task output. Verdict: correct/incorrect or score rubric.
  - **Trajectory-Aware:** Judge sees the full process (prompts issued, intermediate states, reasoning steps) plus the final output. Verdict: same rubric.

- Compute:
  - `δ_outcome = mean(Score_A_outcome − Score_C_outcome)`
  - `δ_trajectory = mean(Score_A_trajectory − Score_C_trajectory)`
  - Compare: `δ_outcome` vs `δ_trajectory`

### 5.2 Interpretation
- **Agreement:** Both outcome and trajectory show the same improvement → harness improves the actual process and result
- **Outcome-only inflates signal:** `δ_outcome > δ_trajectory` → harness creates illusory improvement (reaches right answer via wrong path, or fools the judge)
  - *Concern level:* High; indicates harness gaming the evaluation
- **Trajectory catches failures:** `δ_trajectory > δ_outcome` → harness improves process but outcome still fails
  - *Concern level:* Medium; indicates harness takes better steps but can't quite land the plane
  - *Implication:* Further work needed on implementation, not just planning

### 5.3 Stage-Level Scoring
Per 2608.03501 (SCOPE benchmark):
- Decompose the task into stages:
  - High-level: planning, strategy selection, hypothesis formation
  - Low-level: dataset selection, parameter choice, metric choice
  - Execution: code/action runs without error
  - Analysis: results are correctly interpreted
- Score each stage independently (0–5 rubric per stage, not averaged)
- Report `δ_harness_per_stage` to identify which stages improve vs. regress

**Justification:** A rubric average can mask stage-level tradeoffs. Harness A might improve planning (high-level) but degrade analysis (low-level), and the two cancel out in the mean.

---

## 6. Scoring Reliability and Judge Calibration

Per 2608.29517 (LLM judge audit):

### 6.1 Judge Severity and Drift
- Select the evaluation judge (human or LLM; justify choice)
- **Anchor calibration:** Evaluate ~30–50 anchor tasks twice at different times, separated by ~1 week
  - Compute test–retest correlation
  - Compute severity shift (mean score difference at retest)
- **Version pinning:** If using an LLM judge, pin the model version and log the exact version ID
- **Multi-judge panel (optional, if budget allows):** Run 2–3 judges on the same 20% of tasks to measure inter-rater reliability and severity spread

### 6.2 Halo and Analytic Sub-Scores
- If the rubric has analytic sub-scores (e.g., "clarity," "correctness," "efficiency"), score each dimension in a *separate* call to the judge (per 2608.29517, separate calls reduce halo)
- Report correlation of sub-scores: high correlation → halo present, low correlation → dimensions independent

### 6.3 Stability Under Replications
- Rescore ~10% of tasks (randomly selected) twice
  - Compute pair-wise score correlation
  - If score variance > model variance, judge noise is the limiting factor (Zatuchin 2607.13304)

---

## 7. Outcome Metrics

### 7.1 Primary Outcome
**Harness Improvement Effect Size**
- Point estimate: `δ_harness` (paired mean difference)
- 95% CI: bootstrapped or parametric paired t-test CI
- Resolution ratio: `q = N / N*` at conventional target power (α=0.05, 1−β=0.80)
- **Decision rule:**
  - `q ≥ 1` and CI excludes zero → Improvement is real
  - `q < 1` or CI includes zero → Improvement is not statistically resolved; claim fails power check

### 7.2 Secondary Outcomes
1. **Prompt confound magnitude:** `δ_prompt` relative to `δ_harness` (attribution ratio)
2. **Model generalization:** correlation of `δ_harness` across models (r_pearson or rank correlation)
3. **Stage-level breakdown:** `δ_per_stage` vector (6 dimensions: planning, strategy, low-level, execution, analysis, synthesis)
4. **Trajectory vs. outcome discrepancy:** `δ_trajectory − δ_outcome` (bias indicator)
5. **Judge stability:** test–retest r and severity shift (σ)

### 7.3 Uncertainty Quantification
- Report not just point estimates but full posterior or bootstrap distributions
- Use the variance component model to estimate how much of remaining noise is from judge vs. resampling vs. genuine task variance
- Per 2605.30315: report resolution ratio q for every key claim (harness improvement, prompt effect, generalization to model 2)

---

## 8. Concrete Resources

### 8.1 Evaluation Set
- **Size:** Existing held-out evaluation set (assumed ~100–300 tasks, depending on domain)
- **Justification:** Power analysis (2010.06595): at 0.80 power, typical effect sizes in LLM tasks require n=80–150 paired observations to resolve differences at α=0.05
- **Pre-registration:** Lock in task set, rubric, and analysis plan before running

### 8.2 Models
- **Model 1:** The model embedded in the harness system (primary test bed)
- **Model 2:** A second model for ablation (justify the choice: similar scale? different vendor? different architecture?)
- **Justification:** Per ablation section; generalization is critical to claim the improvement is "harness" and not "model A quirk"

### 8.3 Rubric and Scoring Instructions
- **Source:** Inherit from existing evaluation protocol if one exists; otherwise, design a domain-specific rubric
- **Rubric format:** 0–5 Likert scale per dimension (stage-level scoring, per §6)
- **Anchor examples:** Provide 5–10 reference outputs (high, medium, low quality) with scores and justifications, to calibrate judges
- **Judge:** Human expert (preferred for reliability) or LLM if human not available
  - If LLM: use a stable, pinned version; implement calibration protocol per §6.1

### 8.4 Prompts
- **Status quo (C & B baseline):** Extract from the current harness system; document verbatim
- **Candidate harness (A):** Snapshot the candidate harness structure and extract its prompt; document verbatim
- **Enhanced prompt (B):** Create by:
  - Option 1 (preferred): Manual expert crafting, reflecting best practices in prompt engineering for this task domain
  - Option 2: Automated prompt optimization (e.g., using an LLM to improve the status-quo prompt iteratively)
  - **Pre-register:** Freeze the enhanced prompt before evaluation begins
- **Version control:** Store all three as diffs or snapshots in a version system; ensure reproducibility

### 8.5 Held-Out Evaluation Data
- **Ground truth:** Presumably exists (task solutions, reference implementations, or expert judgments)
- **Access restriction:** Evaluation set must be blind to the harness system (scoring runs outside the harness)
- **Replicability:** Release all scores, judge verdicts, and annotations as a public or archived dataset (per 2609.00038 transparency norm)

---

## 9. Analysis Workflow

### 9.1 Pre-Registration (Before Evaluation)
1. Freeze the three harness/prompt conditions (A, B, C)
2. Lock in: held-out task set, rubric, anchor examples, judge
3. Pre-specify:
   - Primary test: paired t-test on δ_harness; alternative: paired Wilcoxon if n-normality assumed
   - Secondary tests: paired t for δ_prompt; resolution diagnostics for both
   - Ablation 1 model: specify which model, justify choice
   - Ablation 2 protocol: trajectory vs. outcome scoring rules
   - Significance level: α = 0.05 (two-tailed)
   - Minimum N* required for power 0.80 at effect size δ (specify δ from pilot or prior literature)
4. Register the plan (OSF or Zenodo) with a timestamp

### 9.2 Evaluation Phase
1. Evaluate tasks in Conditions A, C under the judge (all tasks, ~5 resamples per task per 2607.13304)
2. Evaluate tasks in Condition B (all tasks, same resampling schedule)
3. Simultaneously:
   - Calibrate judge: evaluate ~30 anchor tasks at two time points, 1 week apart
   - Check stability: re-evaluate 10% of tasks at the end to detect drift

### 9.3 Analysis Phase
1. Compute primary estimands:
   - `δ_harness`, `δ_prompt`, their 95% CIs
   - Resolution ratios q_harness, q_prompt
   - Paired t-test p-values and effect sizes (Cohen's d)
2. Compute ablation estimates:
   - `δ_harness_model2`, generalization correlation
   - Variance components (crossed random-effects REML fit)
   - `δ_trajectory`, `δ_outcome`, per-stage breakdowns
3. Judge diagnostics:
   - Calibration: test–retest r and severity shift
   - Halo: analytic sub-score correlations
   - Report judge severity SD relative to true score SD (should be <<8× per 2608.29517 benchmark)
4. Sensitivity analyses:
   - Repeat all t-tests using Wilcoxon signed-rank test (non-parametric alternative)
   - Repeat all power diagnostics at 70% power and 90% power thresholds
   - Bootstrap CI resampling: use stratified resampling by task domain (if multi-domain)

### 9.4 Reporting
- **Main table:** δ_harness [95% CI], q-ratio, p-value, n, Cohen's d, along with δ_prompt for side-by-side comparison
- **Stage breakdown:** δ by stage (6 rows)
- **Generalization:** δ and q for Model 2; correlation of effects across models
- **Trajectory vs outcome:** δ_trajectory, δ_outcome, difference
- **Judge diagnostics:** test–retest r, severity shift, halo sub-score correlation
- **Open data:** Release scores, rubric verdicts, and full dataset under Creative Commons

---

## 10. Justification Summary and Evidence Citations

### 10.1 Why Paired Design?
- **2605.30315 (Kotawala):** Paired LLM evaluation is ~2.15× more efficient than unpaired. The resolution diagnostic framework (q = N/N*) ensures the sample size is adequate for the claimed effect.

### 10.2 Why Three Conditions (Not Two)?
- **2609.00038 (Mohammadi):** Outcome-only evaluation is blind to process. A third "prompt-only" condition (B) isolates whether the improvement comes from better orchestration (harness) or better prompting (model input).
- **Classic confound control:** Condition B is a positive control that should show *how much* a well-crafted prompt alone can improve, independent of harness structure.

### 10.3 Why Trajectory-Aware Scoring?
- **2609.00038 (Mohammadi):** "Outcome-only judge catches 84% of loud faults but 45% of silent ones." Systems that improve process but not final outcome are invisible to outcome-only judges.
- **2608.01913 (Liu, Diagnosing Search Behavior):** Decompose failures into retrieval gaps (did we find evidence?) vs. utilization gaps (did we use it?). Same principle applies to harness: plan vs. execute.

### 10.4 Why Stage-Level Scoring?
- **2608.03501 (SCOPE):** High-level planning and low-level configuration can have independent failure modes. Averaging across stages can hide important tradeoffs.
- **Practical:** Harness improvements often target specific stages. Granular scoring exposes which stages benefit.

### 10.5 Why Variance Decomposition?
- **2607.13304 (Zatuchin):** A single LLM answer carries almost no signal (ICC 0.0146). Reliability is achieved by spreading samples across prompts, models, and languages—not by resampling the same prompt repeatedly.
- **Implication:** In this design, one task evaluation should be treated as one cell in a crossed design (task × model × harness × resample). Allocation rule follows from REML components.

### 10.6 Why Judge Calibration?
- **2608.29517 (Sunkavalli):** Judge severity spans 219 points on a 1000-point scale (same corpus, 12 judges). Version upgrades shift scores by up to 13%. Pin versions and anchor against human-labeled samples.
- **2609.00038 (Mohammadi):** Invented false signals (e.g., a made-up promise appended to output) can evade step-level judges 82% of the time. Separate calls per dimension reduce halo.

### 10.7 Why No Network Search?
- **Constraint:** Only use ./evidence directory. All justifications, methods, and benchmarks cited from existing excerpts in the evidence pack.
- This design does not invent new methods; it integrates existing frameworks (paired hypothesis testing, resolution diagnostics, variance components, trajectory-aware scoring, judge audits) into one coherent protocol.

---

## 11. Key Assumptions and Limitations

### 11.1 Assumptions
1. **Exchangeability:** Tasks in the held-out set are representative of the target population; no time-dependent trends or drift.
2. **Carryover:** No carryover effects between conditions (e.g., Model 1's performance in A does not affect its performance in B). Conditions are evaluated independently.
3. **Rubric stability:** The rubric and judge anchor examples are stable across Conditions A, B, C; no interaction between rubric interpretation and condition.
4. **Prompt fidelity:** Condition B's "enhanced prompt" does not accidentally leak structure from Condition A's harness (orthogonality assumption).

### 11.2 Limitations
1. **Small effect regimes:** If true effect size is <0.5 points on a 5-point rubric, the design may remain underpowered (N* > N). Use resolution diagnostics to flag this.
2. **Multi-model generalization:** Ablation 1 tests only one alternative model. Stronger claim would require 3+ models, but budget may not allow.
3. **Judge subjectivity:** Human judges introduce noise. LLM judges (if used) are mutable. Mitigation: anchor calibration, version pinning, replication.
4. **External validity:** Held-out set is domain-specific. Generalization beyond this domain is not addressed.

---

## 12. Expected Outcomes (Not Results)

### 12.1 Success Scenario
- δ_harness is statistically resolved (q ≥ 1) with 95% CI excluding zero, in the improvement direction
- δ_prompt is smaller in magnitude than δ_harness (or opposite sign), supporting harness as the primary signal
- δ_harness_model2 has similar direction and magnitude on Model 2 (r > 0.60)
- Stage-level breakdown shows improvements concentrated in planning/strategy stages, not accidents in execution
- δ_trajectory ≈ δ_outcome (no divergence), suggesting the improvement is real and not outcome-only gaming

### 12.2 Failure Scenario
- δ_harness is unresolved (q < 1) or CI includes zero
  - *Conclusion:* Sample size insufficient or true effect is near zero
- δ_prompt ≥ δ_harness
  - *Conclusion:* Prompt engineering explains the improvement; harness is not the driver
- δ_harness reverses on Model 2
  - *Conclusion:* Improvement is model-specific coupling, not a general harness property
- δ_trajectory << δ_outcome
  - *Conclusion:* Improvement is an artifact of outcome-only judge; process is unchanged or worse

### 12.3 Ambiguous Scenario
- q ≈ 1 (barely resolved) and CI is wide
  - *Conclusion:* Improvement is real but modest; claim should be hedged
- δ_harness > δ_prompt but both are small
  - *Conclusion:* Harness is the driver, but effect is marginal; consider if practical significance justifies the harness change
- Stage breakdown shows mixed effects (improves planning, degrades execution)
  - *Conclusion:* Harness is not uniformly better; requires targeted fixes per stage

---

## 13. Timeline and Checkpoints

### 13.1 Pre-Evaluation (Week 1–2)
- [ ] Finalize three conditions (A, B, C) and freeze prompts
- [ ] Lock held-out task set
- [ ] Design rubric and anchor examples; train judge
- [ ] Pre-register plan on OSF

### 13.2 Evaluation (Week 3–5)
- [ ] Evaluate Conditions A, B, C on held-out set (~N tasks, ~5 resamples each)
- [ ] Calibrate judge: rescore anchor set at weeks 1 and 2 of evaluation
- [ ] Stability check: rescore 10% of tasks at end of week 5

### 13.3 Analysis (Week 6–7)
- [ ] Compute δ_harness, δ_prompt, resolution diagnostics
- [ ] Run variance component model on resampled data
- [ ] Ablation 1: evaluate Model 2 on A and C; compute generalization
- [ ] Ablation 2: rescore ~30 tasks with trajectory-aware protocol
- [ ] Judge diagnostics: calibration r, halo correlations

### 13.4 Reporting (Week 8)
- [ ] Write-up results, tables, and interpretive narrative
- [ ] Release scores and annotations as supplementary data
- [ ] Post pre-registered analysis report

---

## References and Evidence Justification

All citations are to files in ./evidence:

| Concept | Evidence File | Key Finding |
|---------|--------------|-------------|
| Statistical power for NLP | 2010.06595 | Underpowered experiments are common; power analysis is essential. Typical n=2000 for MT gives 75% power for 1 BLEU delta. |
| Paired evaluation resolution diagnostics | 2605.30315 | Paired McNemar required-N is 2.15× smaller than unpaired Gaussian formula. Resolution ratio q = N/N* flags unresolved claims. |
| Variance components in LLM measurement | 2607.13304 | Single answer ICC ≈ 0.015; reliability comes from spreading across models/languages, not repeats. Generalizability theory REML allocation. |
| Hidden-target task rubrics | 2606.07591 | Expert-curated multimodal rubrics enable open-ended evaluation. Target kept hidden during scoring. |
| Stage isolation in experimental design | 2608.03501 | High-level (planning) and low-level (config) can decouple. Redline scoring for fatal flaws. |
| Judge severity and drift | 2608.29517 | Judge severity SD is 8–15× that of trained raters. Version upgrades shift scores 13%; pin versions, anchor calibrate, monitor via 20-essay paired check. |
| Outcome-only judging blind spots | 2609.00038 | Outcome-only catches 84% loud faults, 45% silent; step-level rubric reaches 77% silent recall, 0% false alarms. Separate calls per dimension reduce halo. |
| Retrieval vs. utilization gaps | 2608.01913 | Decompose failures: retrieval gaps (evidence not found) vs utilization gaps (evidence found but misused). |
| Self-reflection and on-demand retrieval | 2310.11511 | Adaptive retrieval and self-critique enable selective knowledge augmentation; not all tasks need retrieval. |
| Complexity-conditioned routing | 2403.14403 | Queries of different complexity require different strategies (simple, iterative, grounded). Match strategy to complexity. |
| Efficient graph-indexed retrieval | 2405.14831 | Single-step retrieval with graph indexing achieves 10–20× speedup over iterative retrieval with comparable performance. |

---

## Conclusion

This design isolates harness improvement from model and prompt effects through three-condition comparison, paired statistical testing with resolution diagnostics, variance decomposition, and multi-level scoring (trajectory + stage-aware). It integrates evidence from prior work on statistical power, judge reliability, and evaluation methodology. The protocol is transparent, pre-registered, and produces publicly releasable data, enabling both internal verification and external reproduction.
