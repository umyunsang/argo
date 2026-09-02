# Research state (fill every field before writing the design)

decision_id: K6-HE-001: Does agent-driven scaffold rewriting produce generalizable improvements or task-specific overfitting?

question: When an agent iteratively rewrites its executable scaffold while performing tasks from a fixed family, do the measured performance gains transfer to held-out tasks from the same family, and to structurally similar tasks from adjacent families?

alternatives:
  - REJECTED: Run all tasks repeatedly from a fixed task family, measure improvement, claim success. (Risk: improvements fit the narrow task distribution, not the scaffold logic itself.)
  - REJECTED: Use cross-validation over task families. (Risk: does not distinguish between task-specific tuning of task-selection logic vs. genuine scaffold improvements; overfitting can move to the meta-level.)

sampling_frame: The population is the space of tasks that the agent model + scaffold can meaningfully attempt. The unit is a single (task, scaffold_variant) pair. We sample tasks stratified by source family (primary family used during scaffold rewriting, held-out variant family with same structure, adjacent-domain family to test transfer). Each sampled task is evaluated once per scaffold variant under fixed random seed and model temperature.

evidence_used:
  - Assumption: The model's reasoning quality is identical across scaffold variants (no model weight changes, same inference settings).
  - Assumption: Scaffold changes produce measurable differences in the model's output structure and reasoning steps (can be logged and inspected).
  - Assumption: A family of related tasks is available (per problem statement) with documented structure and difficulty.
  - Cannot verify: Whether the model's internal representations truly remain constant (only weights and settings are held fixed).
  - Cannot verify: Whether the scaffolding changes influence model reasoning in ways that are purely task-specific vs. generalizable (only empirical comparison can assess this).

falsifier: The improvement measured on held-out tasks from the primary family is not statistically significant (p > 0.05, or 95% confidence interval includes zero), OR the improvement on the adjacent-domain family is less than 50% of the improvement on the primary family. Either observation would indicate that gains are primarily task-specific rather than robust scaffold improvements.

stopping_rule: Stop after evaluating ≥ 30 unique held-out primary-family tasks per scaffold variant AND ≥ 15 unique adjacent-domain tasks per variant. If improvement magnitude is clearly trending zero or null after 30 primary tasks, stop early. If improvement is ≥ 10 percentage points on held-out primary tasks with p < 0.01, continue to adjacent-domain evaluation to test transfer; otherwise stop after primary-family evaluation.
