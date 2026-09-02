# Research state (fill every field before writing the design)

decision_id: scaffold-vs-model-attribution-research

question: How much of a published agent capability score on scientific discovery tasks comes from the evaluation scaffold (task structure, evaluation rubric, harness design) versus the underlying model capability?

alternatives:
  - Rejected: Single-condition comparison (e.g., best agent vs best LLM). Confounds scaffold effects with model selection and cannot decompose the two contributions.
  - Rejected: Model ablations only (e.g., test one model in isolation). Cannot measure scaffold contributions across a representative model range without factorial design.
  - Retained: 3×5 factorial combining three scaffolds and five models on a shared benchmark with stratified task-level analysis.

sampling_frame: ResearchClawBench 40-task corpus (10 scientific domains: Astronomy, Chemistry, Earth Science, Energy Science, Information Science, Life Science, Material Science, Mathematics, Neuroscience, Physics). Each scaffold-model combination evaluated on all 40 tasks. Unit of analysis: (scaffold, model, task) triplet. Total: 3 scaffolds × 5 models × 40 tasks = 600 observations. Tasks are identical across cells; conditions (scaffold, model) are crossed independently.

evidence_used:
  - 2606.07591 (ResearchClawBench): Establishes the benchmark (40 real tasks, expert-curated rubrics, re-discovery anchor at 50 points), demonstrates gap between autonomous agents and native LLMs, provides concrete agent and model lists.
  - 2607.09195 (HEP protocol): Documents a structured agent scaffold (hypothesis-evolution harness) that externalizes hypothesis-test-evidence-belief state and improves generalization across tasks.
  - 2608.03501 (SCOPE and OptED): Describes stage isolation and rule-based constraint scaffolds for experimental design tasks, which overlap with ResearchClawBench domains.
  - 2609.00038 (trajectory-judge): Shows that outcome-only judgment blinds to trajectory details; motivates step-level rubric scoring rather than outcome-only measurement. Establishes need for fine-grained rubric design.
  - 2608.29517 (judge severity): Demonstrates judge severity drift of 8–15× trained-human SD and version instability; establishes need to pin evaluation models and versions, and to anchor scoring empirically.
  - 2607.13304 (variance components): Partitions variance into resampling, paraphrase, model identity, and language; informs repeat and model-sampling strategy to isolate scaffold-vs-model signal.
  
Could not verify:
  - Exact composition of the HEP protocol code/weights (paper describes it conceptually but does not provide open-source implementation).
  - Exact OptED rule-set and constraint definitions beyond high-level description (claimed to bridge high-level planning and low-level configuration bottleneck).
  - Whether all five proposed models have equal tool/knowledge coverage within ResearchClawBench tasks (literature does not detail per-model capability profiles).
  - Whether ResearchClawBench's rubrics account for domain-specific norms (rubrics described as expert-curated but inter-rater reliability or domain-expert validation not explicitly reported).

falsifier: A design is falsified if:
  - Scaffold effects account for <5% of total score variance after controlling for model and task; suggests scaffold contribution is negligible relative to measurement noise.
  - Model×Scaffold interaction variance exceeds main-effect variance for both factors; suggests factorial structure is invalid (effects are not additive and cannot be cleanly decomposed).
  - Score correlations between scaffold-model pairs on different task domains drop below ρ=0.40 (Spearman), violating generalizability assumption that scaffold-model effects transfer across domains.
  
stopping_rule: Collect complete 3×5×40 factorial (600 observations). Stop data collection once all observations are completed and rubric scoring passes consensus check: ≥2 independent human reviewers agree on ≥80% of high-stakes cases (tasks where scaffold-model pair score falls in the 40–60 re-discovery threshold window). No optional stopping; commitment is to the full design before observing results.
