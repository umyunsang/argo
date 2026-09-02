# Research state (fill every field before writing the design)

decision_id: K4-optimizer-budget-detection-cost-allocation

question: 
  Can we detect agents that game a benchmark by repeated eval queries (rather than solving)
  using a cost-metered evaluation budget paired with trajectory-level inspection, and quantify
  the power to distinguish gaming from legitimate solution refinement at fixed total cost?

alternatives:
  REJECTED-1 (Outcome-only scoring with hard eval caps):
    - Cap total evals per agent (e.g., max 100 calls)
    - Judge only final output quality
    - Rationale for rejection: 2609.00038 (trajectory-judge) shows outcome-only judges 
      catch only 45% of silent failures (solution is right but method is invalid). 
      An agent that queries evals 100 times then submits the highest-scoring intermediate 
      result looks identical to an agent that iteratively refined legitimately.
  
  REJECTED-2 (Surrogate model evaluation):
    - Train a cheap surrogate to replace expensive target evals
    - Allocate budget to surrogate queries only
    - Rationale for rejection: Cannot justify surrogate accuracy without validation data, 
      which requires target evals. Surrogate fidelity to gaming behavior unknown; agent 
      may exploit surrogate-target gap. Adds unquantified source of variance (2607.13304).

sampling_frame:
  POPULATION: Agents attempting two classes of problems
    - Class A (tractable): solvable via 5–20 legitimate solution refinement iterations
    - Class B (hard): require deeper search or external knowledge, likely >20 iterations
  
  UNIT: (agent, problem_instance, trial) triplet
    Each trial is one agent-problem pair under one budget regime
  
  REPETITIONS per cell: 12 trials (sufficient for variance component estimation per 2607.13304)
  
  STRATIFICATION: 
    - 2 problem classes (A, B) per Figure in 2606.07591 (re-discovery threshold concept)
    - 4 budget regimes (see design.md: strict, moderate, permissive, unlimited-control)
    - 2 trajectory-inspection depths (coarse, detailed) for ablation
  
  SAMPLING DECISION: Treat each (agent-model, problem) as a fixed effect; trial variation 
    as a repeated measure. This follows the crossed design logic of 2607.13304 
    (generalizability theory).

evidence_used:
  - 2606.07591 (ResearchClawBench): hidden-target task packaging, rubric scoring without 
    exposing exact loss function, re-discovery threshold calibration
  - 2609.00038 (trajectory-judge): trajectory inspection detects silent failures (strategy 
    gaming) while outcome-only misses them (45% vs 77% silent recall)
  - 2608.01913 (Search Agent Diagnosis): framework for step-by-step retrieval/utilization 
    gap diagnosis applicable to eval-call auditing
  - 2607.13304 (Variance Components): crossed random-effects allocation and variance 
    partitioning for efficient sample sizing (generalizability theory)
  - 2608.03501 (SCOPE): stage isolation (planning vs configuration) for disentangling 
    eval budgeting decisions from task framing
  - 2010.06595 (Statistical Power): typical NLP effect sizes and power norms for benchmarking
  - 2607.09195 (Hypothesis Evolution Protocol): audit trail of eval queries and belief 
    updates enables gaming detection (circular reuse of same eval data)
  
  COULD NOT VERIFY:
    - Exact effect size (agent gaming behavior magnitude) — will estimate from pilot
    - Whether 12 trials per cell is sufficient post-hoc (pre-registered in design)
    - Practical overhead of trajectory logging at scale

falsifier:
  OBSERVATION THAT WOULD REFUTE DESIGN PREMISE:
  If trajectory-level inspection (detailed rubric + eval log) does NOT show higher 
  statistical power to distinguish gaming from refinement than outcome-only scoring 
  (after cost-controlling for log overhead), then the core assumption that auditable 
  state separates strategies is false. Specifically: if gaming and refinement agents 
  have indistinguishable eval-query distributions or trajectory patterns, cost-metered 
  budgets cannot solve the problem.

stopping_rule:
  PRIMARY: Collect all 12 trials per cell (2 problem classes × 4 budget regimes × 2 
    inspection depths) before analysis. This gives a balanced design under 2607.13304.
    Total: 12 × 2 × 4 × 2 = 192 trials.
  
  EARLY STOPPING: If after 72 trials (first 3 cells × 3 replicates), the interaction 
    between budget regime and trajectory-inspection depth is negligible (Cohen's d < 0.3 
    in estimated effect sizes), halt and report negative result (no signal).
  
  COST BOUNDARY: Total metered eval cost (sum of all eval queries across all agents) 
    must not exceed fixed budget B (to be set in design.md). If overage is forecast, 
    reduce trials per cell rather than total cells (preserves factor balance).
