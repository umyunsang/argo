# Research state (fill every field before writing the design)

decision_id: K2-harness-vs-model

question: How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

alternatives:
  - Single comparison with fixed prompt: measure task performance before/after harness change. REJECTED: confounds harness improvement with model drift. Cannot isolate which improvements come from better tool use and workflow structure vs. better prompting of the same base model.
  - Two-arm with prompt re-tuning per harness: optimize prompt in each harness version separately. REJECTED: makes the "better prompt" factor an independent variable rather than a control, and increases measurement burden. Doesn't measure harness effect holding prompting constant.
  - Outcome-only scoring with single judge: record task success/failure only. REJECTED: based on 2609.00038 (trajectory-judge), outcome-only judging is blind to silent failures where the correct outcome is reached through wrong steps or skipped checks—exactly the kind of harness-level discipline that harness improvements target.

sampling_frame: 
  population: Task instances from the held-out evaluation set (finite, known set provided to the study).
  unit: (task, harness-version, base-model) triplet. A single task run once with a candidate harness version and a fixed frozen base model.
  comparison strata: Two harness versions × one base model, held constant. Multiple tasks sampled from the evaluation set without replacement. Repeat allocation follows 2607.13304 generalizability-theory plan: repeats per task × task sample size, to understand both within-task noise and between-task variance.

evidence_used:
  - 2010.06595 (Card et al.): statistical power norms. NLP experiments commonly underpowered; typical test sets for small effect differences fall short of 80% power. Informs minimum sample size targets.
  - 2605.30315 (Kotawala): paired resolution targets. Paired hypothesis tests require explicit N* calculation accounting for correlation structure; naive Cohen-h shortcuts underestimate N* by factor of ~2 in close-comparison regime. Design must pre-compute minimum detectable effect and sample size for the paired harness comparison.
  - 2607.13304 (Zatuchin): variance components. LLM response variance splits across multiple separable facets (within-prompt resampling, paraphrase, model, language). Crossed random-effects allocation optimizes repeat strategy. Informs where to buy repeats: within same task, or across task paraphrase/formulation.
  - 2608.03501 (Liu et al., OptED): stage isolation. Separating high-level planning (main, ablation) from low-level configuration (datasets, baselines, metrics) reduces configuration bottleneck. Design stage must isolate comparison structure separately from metric selection.
  - 2608.29517 (Sunkavalli): LLM judge severity, halo, drift. Essay graders differ enormously in severity (219-point spread on 1000-point scale); versions shift scores beyond permutation null; average repeats stabilize but don't improve accuracy. Scoring must use rubric-based step-level judges (not outcome-only), pre-calibrate severity against anchor set, pin judge versions, and monitor drift on a fixed monitor set scheduled across runs.
  - 2609.00038 (Mohammadi): trajectory-judge/outcome-only blind spot. Outcome-only judges miss 55% of silent faults (failures where final answer is correct but process violated checks). Step-level rubric judges reach 77% recall on silent faults with zero false alarms at 3× cost. Design must score trajectory structure, not just outcome.
  - Could not verify: Ground truth on what constitutes "good" harness design principles (e.g., which architectural features of a harness are known to improve task success in isolation). Treating this as a measurement problem, not a causal identification problem, so relying on trajectory-level evidence rather than attributive claims.

falsifier: 
  - If harness A and harness B produce indistinguishable trajectory-level rubric scores despite different structure, the premise that the chosen rubric measures harness quality is false.
  - If severity-adjusted scores reverse rank ordering of harness versions from unadjusted scores (as per 2608.29517 permutation null), the measurement is driven by judge calibration rather than harness effect.
  - If repeated measurements on the same task + harness + model show variance (σ_within-task) that dominates the variance between harnesses, the design is underpowered and cannot detect harness effects.

stopping_rule: 
  Stop collecting when:
  1. Paired rubric-score comparison has crossed the minimum detectable effect threshold (per 2605.30315, inverse of paired test at α=0.05, 1−β=0.80 power).
  2. Judge severity anchor set (n≈30–50 essays per rubric; per 2608.29517 recovery guidance) stabilizes, and drift monitor set (n≈20 essays) shows no significant shifts in judge calibration across the run.
  3. Within-task variance component (generalizability theory, per 2607.13304) is estimated to adequate precision (e.g., relative standard error <0.15) to inform whether more within-task repeats would yield further power gain.
  If harness versions are indistinguishable at the rubric-level (falsifier 1), halt and report null finding.
  If judge drift or severity shifts threaten validity (falsifier 2), re-calibrate or halt.
