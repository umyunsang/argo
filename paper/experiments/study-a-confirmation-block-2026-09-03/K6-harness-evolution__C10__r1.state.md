# Research state (fill every field before writing the design)

decision_id: whether_scaffold_rewriting_generalizes_beyond_training_tasks

question: Do improvements in task performance from iterative scaffold rewriting generalize to held-out tasks from the same family, or are they artifacts of fitting to the particular task distribution used during rewriting?

alternatives:
  - rejected: "Compare final vs baseline on the same training tasks only" — this cannot detect overfitting; improvement could be pure task-distribution fitting with no real capability gain
  - rejected: "Use multiple diverse tasks but evaluate all of them during rewriting" — no held-out set, so cannot separate task-distribution fit from genuine improvement; task diversity without independence is insufficient
  - rejected: "Compare against a fixed scaffold baseline on only one held-out task" — a single task is too noisy to detect real improvements; need multiple independent held-out samples to estimate generalization error with confidence

sampling_frame: independent task instances sampled from a documented family of related agent tasks (e.g., coding, planning, or retrieval tasks with varying complexity, context size, and goal structure). The unit is a single task instance. Partition the task family into two sets: (1) training/rewriting set (used during scaffold iteration), (2) held-out evaluation set (never seen during rewriting). Both sets must be representative of the family and drawn via a pre-committed sampling strategy.

evidence_used: 
  - prior work on generalization in hyperparameter optimization (Bengio et al., Bergstra & Bengio) showing that optimization on a limited distribution can overfit
  - established methodology in ML: train/test splits and cross-validation to detect distribution-specific improvements
  - agent research: scaffold design affects performance (Anthropic, Redwood Research prompt engineering work)
  - confirmed prior knowledge: the model and inference settings are fixed; only the scaffold (prompts, tools, action space structure) can change
  - cannot verify: whether the task family is truly representative of all real-world agent tasks; assumed to be sufficient for this study

falsifier: If improvements on held-out tasks equal or exceed improvements on training tasks (no generalization gap), then the design's premise—that overfitting risk exists—would be refuted; improvements would be genuine capability gains rather than task-distribution artifacts. Operationally, this would require held-out task performance improvement ≥ 95% of training-task improvement with confidence interval not excluding parity.

stopping_rule: Collect results until either (1) held-out evaluation sample size reaches n=30 task instances, OR (2) the generalization gap (training – held-out improvement) is detected with 95% CI not crossing zero, whichever comes first. Stop rewriting after ≤5 iterations of scaffold changes or when improvement plateaus on training set for 2 consecutive iterations.
