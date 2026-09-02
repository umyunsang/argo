# Research state (fill every field before writing the design)

decision_id: T3-scaffold-elicitation-v1

question: How much variance in published agent capability scores is attributable to scaffold choice versus model choice? Specifically, what is the main effect of scaffold (fixed model) versus main effect of model (fixed scaffold)?

alternatives:
  - Alternative 1 (rejected): Run only the benchmark on one fixed scaffold with all five models. Rationale for rejection: Cannot isolate scaffold variance—any cross-model differences confound model and scaffold effects. Does not satisfy the research question.
  - Alternative 2 (rejected): Conduct human raters evaluating qualitative agent traces instead of running a quantitative benchmark. Rationale for rejection: Introduces subjective assessment variance; introduces new confounds (rater training, calibration) not present in automated benchmark; cannot isolate scaffold effects cleanly from model effects.

sampling_frame: The population is all (scaffold, model) pairings from the Cartesian product of {3 scaffolds} × {5 models}. The sampling unit is a single (scaffold, model, task) trial where a task is one problem instance from the public multi-step task benchmark. Each task instance produces one performance score. The frame covers all 15 scaffold-model combinations, all available task instances from the benchmark (treating all instances as the replication unit), with all conditions held constant (identical task text, identical evaluation metrics, identical time budgets).

evidence_used:
  - Assumption: A public multi-step task benchmark exists with at least 10 task instances of sufficient complexity to reveal model-scaffold interactions.
  - Assumption: The three scaffolds and five models can be instantiated in a common harness without modification to their core logic.
  - Assumption: Scaffold differences are implementable as isolated changes (e.g., prompt engineering, planning, reasoning depth) that do not require retraining.
  - Could not verify: Which specific benchmark is "public multi-step task"—assumed to exist, e.g., ARC-Challenge, GPQA, or similar; specific identities of the 3 scaffolds (e.g., chain-of-thought, tree-of-thought, direct) and 5 models (e.g., GPT-4, Claude 3 Opus, Llama 70B, Gemini 2.0, Grok 3) are assumed but not verified here.

falsifier: If analysis shows no significant main effect of scaffold (two-way ANOVA, p ≥ 0.05) and no interaction between scaffold and model (p ≥ 0.05), the design premise fails: scaffold choice would be shown to have negligible impact on published scores. This would suggest capability scores are driven almost entirely by model, not scaffold.

stopping_rule: Collect complete results for all 15 (scaffold, model) cells across all task instances in the benchmark. Stop after all tasks have been run to completion and analyzed. If a single cell fails or times out (≥10% of task instances in that cell fail), document the failure mode and continue; do not exclude the cell. Confidence intervals and effect sizes will be computed after all data are collected; no sequential testing or adaptive stopping occurs.
