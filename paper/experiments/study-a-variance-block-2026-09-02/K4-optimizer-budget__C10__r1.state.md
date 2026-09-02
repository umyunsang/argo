# Research state (fill every field before writing the design)

decision_id: k4-eval-budget-stopping-rule

question: |
  How should a benchmark bound an optimizing agent's evaluation budget for the target to prevent overfitting while still allowing meaningful optimization work?

alternatives: |
  1. REJECTED: Unlimited evaluations with post-hoc test-set gap analysis
     - Rationale: Does not prevent the overfitting; only measures it after the fact.
  
  2. REJECTED: Fixed evaluation count (e.g., 1000 calls) with no adaptation
     - Rationale: May waste budget on already-converged solutions or starve legitimate optimization.
  
  3. CANDIDATE (A): Static evaluation budget with early stopping via confidence bounds
     - One-time allocation (e.g., 500 evaluations) with stopping when the agent's improvement margin falls below a threshold over a window (e.g., no >1% improvement in last 50 evals).
  
  4. CANDIDATE (B): Tiered evaluation budget with held-out checkpoint validation
     - Dynamic budget: grant base allocation (e.g., 300 evals); after each milestone, validate agent's test-set score against a held-out checkpoint; if generalization gap exceeds threshold (e.g., >0.15 in normalized space), deny further allocation.

sampling_frame: |
  Population: Optimization benchmark tasks and optimizing agent architectures
  Unit of analysis: (agent_type, target_function, budget_rule) triples
  
  - Agent types: gradient-free optimizer (e.g., Nevergrad), model-based Bayesian optimizer (e.g., BoTorch), 
    greedy policy gradient agent (simple convergent baseline)
  - Target functions: 3–5 synthetic test functions (Rosenbrock, Sphere, Rastrigin, one real ML hyperparameter landscape if available)
  - Budget rules: Static (A), Tiered (B), and Unrestricted control
  
  We compare each (agent, function) pair under each budget rule, sampling 10 random seeds per condition.

evidence_used: |
  - Existing literature: AutoML evaluation budgets (Hyperband, successive halving) constrain evaluations to prevent overfitting
  - Benchmark design: ImageNet validation splits, held-out test sets in competition benchmarks
  - Agent over-fitting: Documented behavior in hyperparameter optimization where more evals → test-set gap widens
  
  Could not verify: Exact generalization-gap trajectory under budget pressure for modern LLM-based optimizers; 
  evidence is mostly from classical AutoML. Assumed synthetic functions behave analogously.

falsifier: |
  The design fails if:
  - Static budget (A) causes >15% performance drop vs. Tiered (B) on average across all functions
    (suggesting the static rule is wastefully conservative)
  - Tiered budget (B) exhibits >10% mean test-set gap relative to training loss
    (suggesting the held-out checkpoint validation does not catch overfitting)
  - Both A and B show no improvement over Unrestricted control on the test set
    (suggesting neither stopping rule actually prevents overfitting at all)

stopping_rule: |
  Collect data until:
  1. All 10 seeds complete for every (agent_type, function, budget_rule) combination (60 runs minimum)
  2. Test-set performance is sampled for each run (final agent checkpoint against held-out test)
  3. Confidence intervals on mean test gap (95% CI via t-bootstrap) do not overlap between A and B
     OR 50 runs total, whichever is reached first
  4. Stop if the design is invalidated (falsifier holds)
