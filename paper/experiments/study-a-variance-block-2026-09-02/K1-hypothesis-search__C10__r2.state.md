# Research state (fill every field before writing the design)

decision_id: K1-hypothesis-tree-vs-flat-queue

question: Does organizing autonomous agent attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization tasks?

alternatives:
  - Rejected: Random restart strategy (no structure at all). Rationale: Provides no learning signal between attempts; baseline is too weak to learn anything meaningful.
  - Rejected: Linear priority queue ordered by heuristic scoring. Rationale: Ignores multi-branch exploration; cannot compare tree structure's benefit when priority heuristic dominates outcome differences.

sampling_frame: 
  population: Held-out artifact optimization tasks from Claude Code projects
  unit_of_analysis: (task, backbone_configuration, arm_assignment) — a single task solved by one backbone under one experimental condition
  sampling_method: Stratified random assignment by task difficulty (inferred from prior artifact size and constraint complexity); fixed equal budget per arm per task
  N_per_arm: Determined by compute budget and per-task timeout allocation (concrete N set during resource specification phase)

evidence_used:
  - Reliance: Claude Code artifact optimization is an established problem class (used in continuous agent-loop skill documentation)
  - Reliance: Hypothesis trees with insight propagation are established patterns in LLM reasoning (loop-design-check, recursive-decision-ledger skills provide precedent)
  - Cannot verify: Whether held-out test tasks are truly disjoint from backbone training; mitigation via task provenance audit before assignment
  - Cannot verify: Whether all tasks benefit equally from tree structure; mitigation via per-task heterogeneity analysis post-hoc

falsifier:
  - If flat queue achieves ≥95% of tree arm success rate OR if tree arm achieves <60% on >50% of tasks despite propagated insight, the hypothesis is refuted (suggesting structure does not confer advantage at this scale or backbone capacity)

stopping_rule:
  - Primary: Complete all assigned (task, arm) pairs within compute budget; no early stopping for statistical significance
  - Secondary: If a single arm fails to improve on >75% of first 5 tasks, log concern but continue (possible task difficulty mismatch rather than arm failure)
  - Tertiary: No adaptive reallocation between arms during the experiment

