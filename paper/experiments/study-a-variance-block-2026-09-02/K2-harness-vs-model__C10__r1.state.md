# Research state (fill every field before writing the design)

decision_id: K2-harness-evaluation-protocol

question: How do you measure whether a system improves its own harness, without the measurement being explained by the underlying model getting a better prompt?

alternatives:
  - REJECTED: End-to-end scoring within candidate workspace. Allows the harness to optimize for the scoring process itself; violates the constraint that scoring must not run inside candidate workspace.
  - REJECTED: Qualitative inspection of harness changes. Lacks quantification; cannot support claims about improvement magnitude or statistical significance relative to natural variation.
  - ADOPTED: Fixed-model, fixed-prompt cross-harness comparison on held-out evaluation set, with prompt instrumentation to detect prompt-level changes.

sampling_frame: 
  population: "All tasks in the held-out evaluation set (a pre-existing benchmark of decision/reasoning tasks where harness tools and composition matter)"
  unit_of_analysis: "Single (harness_version, task) evaluation pair"
  frame_size: "Sample size determined by power calculation on primary metric; described in design"
  independence: "Tasks are independent; harness versions are independent snapshots"

evidence_used:
  - Held-out evaluation set exists and is task-complete (confirmed: referenced in constraints)
  - Harness versions can be snapshot and instantiated (confirmed: stated in constraints)
  - Model behavior is reproducible across identical prompts and conditions (assumption: standard practice, but repeatability checked via control runs)
  - What could NOT be verified: That harness changes are isolated from model prompt changes without explicit instrumentation (thus prompted in design)

falsifier: |
  Refutation scenarios:
  1. If harness A outperforms harness B on evaluation set, but bytewise inspection shows the harnesses are functionally identical in tool choice, tool parameter binding, and control flow, the measured difference is noise, not harness improvement.
  2. If performance differences correlate with model release dates or prompt version tags rather than harness structural changes, the improvement is attributable to model, not harness.
  3. If a harness change is introduced (e.g., new tool added) but model system prompt is also changed in the same commit, we cannot attribute improvement to the harness change alone.

stopping_rule: |
  - Primary criterion: Collect results for all predefined harness versions and the held-out set (fixed N).
  - Secondary criterion: Stop early if 95% confidence interval for the difference between any pair of harness versions excludes zero and the interval width is <5 percentage points (for binary/accuracy metrics).
  - Tertiary criterion: If results show no systematic trend after first half of evaluation set, document and report; do not expand sample size.
