# Research state (fill every field before writing the design)

decision_id: harness-self-improvement-vs-prompt-quality
question: Can we measure harness improvement independently of underlying-model prompt-following quality improvements?
alternatives:
  - "Alternative 1 (rejected): Evaluate before/after harness versions on the held-out set and attribute any gain to harness quality. Rejected: Does not control for the confound that the model itself may generate better prompts over time, independent of harness structure."
  - "Alternative 2 (rejected): Examine syntactic or semantic diff of harness artifacts (tools, rules, skills) before and after. Rejected: Heuristic comparison of harness structure does not measure causal impact on task performance; changes may be noise or merely cosmetic."
  - "Alternative 3 (rejected): Use within-workspace evaluation (scoring harness performance inside the same environment where the harness improved). Rejected: Violates stated constraint that scoring must not run inside the candidate workspace; introduces uncontrolled bias."

sampling_frame: Population = individual task instances in the held-out evaluation set; Unit = single (task, harness_version, model_version) triplet performance observation. We sample across task diversity and hold harness constant while varying model prompt-adaptation separately.

evidence_used:
  - "Held-out evaluation set (confirmed to exist per constraints)"
  - "Ability to snapshot harness versions (confirmed per constraints)"
  - "External scoring mechanism outside candidate workspace (confirmed per constraints)"
  - "Access to a fixed reference model version to isolate model-improvement confound"
  - "Assumption: harness artifacts (CLAUDE.md, skills, rules, prompts) are version-controllable and inspectable"
  - "Could not verify: whether prompt changes within the model's context window are tracked separately from harness changes; whether the model can be held constant while harness varies in a realistic workflow"

falsifier:
  - "If improvement in average task performance persists when we compare (old_harness, fixed_model) vs (new_harness, fixed_model), but disappears when we compare (old_harness, model_v2) vs (new_harness, model_v2), this suggests the improvement is model-driven, not harness-driven, falsifying the design premise."
  - "If we cannot construct a counterfactual (fixed model with new harness) because the model version is locked to a harness snapshot, the design becomes unexecutable."

stopping_rule: Collect results until (a) both harness condition and ablation reach n≥30 task samples with settled confidence intervals on the performance delta, OR (b) after 2 sequential harness snapshots have been evaluated (to provide one before/after comparison), whichever comes first.
