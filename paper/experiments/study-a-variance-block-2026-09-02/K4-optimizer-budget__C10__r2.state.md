# Research state (fill every field before writing the design)

decision_id: K4-budget-stopping-mechanism

question: 
  Should a benchmark enforce an explicit evaluation budget cap per agent run, 
  or should it allow adaptive stopping rules that vary by observed convergence behavior?

alternatives:
  - "Hard budget cap (rejected): Treats all agents identically regardless of their search 
    efficiency. Agents that discover good solutions quickly are not rewarded for efficiency, 
    and the comparison becomes a race against arbitrary limits rather than a test of 
    optimization quality. Evidence: budget-based competition rules often incentivize 
    gaming behavior (agents probing near boundaries) rather than principled search."
  
  - "No stopping rule (rejected): Allows unlimited evaluations until some external halt 
    (wall-clock, human stop). Creates open-ended optimization pressure that makes scores 
    non-comparable across runs and time. The held-out test becomes a noisy downstream 
    check rather than the controlled anchor for the design. Agent learning curves become 
    dependent on implementation details (how aggressive is the eval queue?)."

sampling_frame:
  Population: Hyperparameter optimization runs on a fixed target function (e.g., a 
  machine-learning training pipeline's validation score as a function of hyperparameters).
  Unit: A single agent-guided search trajectory, measured from initialization to stopping. 
  Each unit records (a) sequence of evaluation queries, (b) their evaluation cost, 
  (c) best score found at each step, (d) held-out test score at stopping point.
  Replicates: Multiple independent runs per condition, seeded differently.

evidence_used:
  - Prior work: Leite et al. (2012) show that stopping rules based on improvement plateau 
    reduce overfitting in nested CV; applied here to agent evaluation budgets. Evidence 
    supports the idea that convergence signals matter for generalization.
  - Feasibility: Target function (validation score) and held-out test are concrete and 
    queryable in the benchmark framework; evaluation cost is metered.
  - Could NOT verify: Whether agent behavior (greedy vs exploratory) shifts under 
    evaluation-budget pressure in ways that invalidate downstream test performance 
    correlations. This becomes a design assumption, tested via ablation.

falsifier:
  If the held-out test score shows NO correlation with the number of evaluations used 
  (Pearson r < 0.2, p > 0.1 across replicates), then stopping rules tied to eval count 
  are not measuring real optimization progress and the entire design premise fails. 
  The benchmark would be measuring agent wall-clock efficiency or implementation speed 
  rather than solution quality.

stopping_rule:
  - For adaptive stopping: Monitor improvement magnitude over a rolling window 
    (e.g., last 10 evaluations). Stop when improvement < threshold AND held-out 
    test has not improved in 5 consecutive eval rounds.
  - For hard budget: Stop at a fixed count (e.g., 1000 evals) regardless of convergence.
  - In both cases, record the trial number, eval count, best train score, and test score.
