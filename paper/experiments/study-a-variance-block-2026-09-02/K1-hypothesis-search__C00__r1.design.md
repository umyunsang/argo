# Experimental Design: Hypothesis Tree vs. Flat Queue for Autonomous Agent Artifact Optimization

## Research Question

Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

## Primary Comparison

### Treatment: Hypothesis Tree (HT)
Agents construct and traverse a tree structure where:
- Each node represents a distinct hypothesis about how to solve a task
- Child nodes inherit insights from parent nodes (e.g., failed constraint classes, successful heuristics, feature interactions)
- Edges encode the reasoning that led to branching
- Agents prioritize branches by estimated information gain and prior success patterns
- Backpropagated results update parent-node priors to inform sibling exploration

### Control: Flat Queue (FQ)
Agents maintain an ordered queue of unrelated attempts where:
- Each attempt is independent with no shared state or learned relationships
- Queue ordering follows a simple heuristic (e.g., random, recency, size-based priority)
- No insight propagation between attempts
- Agents restart context and reasoning for each task

### Budget Constraint
- Both arms receive identical compute allocations: T total wall-clock time per task
- Both arms receive identical workspace allocations: M maximum intermediate artifacts, N maximum search depth per artifact
- Both arms use the same backbone model and tokenization

### Held-Out Evaluation Protocol
- Training tasks: drawn from a public benchmark (e.g., DACON LG Aimers competition submission history or similar public archive)
- Held-out test tasks: 10–15 never-before-seen tasks from the same domain, locked until final evaluation
- Promotion rule: only artifacts that clear held-out performance thresholds are considered successful
- No information about held-out task structure leaks into training

---

## Experimental Conditions

### Condition 1: HT with Full Propagation
- Hypothesis tree with complete insight propagation
- Child-to-parent backpropagation of success metrics and constraint violations
- Pruning rule: abandon branches where leaf success rate < baseline + 2σ for 3 consecutive iterations

### Condition 2: HT with Lossy Propagation (Ablation)
- Hypothesis tree structure preserved
- Insight propagation limited to: (a) final outcome only, (b) no intermediate heuristics
- Pruning rule identical to Condition 1
- **Purpose**: isolate the value of rich insight propagation vs. tree structure alone

### Condition 3: FQ Baseline
- Flat queue with random ordering reset each run
- No inter-attempt communication
- Queue size: M attempts, selected uniformly at random
- **Purpose**: establish baseline for unstructured search

### Condition 4: FQ + Heuristic Ordering (Ablation)
- Flat queue with learned ordering heuristic
- Heuristic trained on training-task success patterns (artifact type, size, depth) via lightweight logistic regression
- Queue reordered every 10% of time budget
- **Purpose**: test whether flat-queue benefits are achievable through simple reordering without tree structure

---

## Analysis Plan

### Primary Outcome: Held-Out Success Rate
- **Definition**: fraction of held-out test tasks where final artifact meets performance threshold (e.g., ≥80% on validation metric)
- **Comparison**: HT (Condition 1) vs. FQ (Condition 3)
- **Metric**: binomial proportion with Wilson score 95% CI, reported per task and aggregated
- **Threshold for evidence**: HT success rate > FQ success rate, CI does not include equality, posterior probability P(HT > FQ | data) > 0.95 under Beta-Binomial model

### Secondary Outcomes
1. **Insight Reuse Rate** (HT only): fraction of final solutions that contain heuristics or constraints inherited from prior branches
2. **Tree Depth Distribution** (HT only): mean, median, and 90th percentile branch depth
3. **Compute Efficiency**: successful solutions per unit wall-clock time, by condition
4. **Artifact Size**: median bytes of final artifact, comparing HT vs. FQ
5. **Early Termination**: fraction of tasks stopped before T expires (may indicate confidence or failure)

### Ablation Analysis
- **HT vs. HT-Lossy**: quantify loss from removing intermediate propagation (success rate delta)
- **FQ vs. FQ-Heuristic**: quantify gain from learned reordering without tree structure (success rate delta)
- **Interpretation**: 
  - If HT >> HT-Lossy and FQ ≈ FQ-Heuristic, then tree structure matters more than ordering
  - If HT ≈ HT-Lossy and FQ-Heuristic >> FQ, then ordering matters more than tree structure
  - If HT >> both FQ-Heuristic and HT-Lossy, then combination of tree + propagation is synergistic

### Uncertainty Quantification
- **Binomial model**: Model success counts as Binomial(n_tasks, p_arm)
  - Priors: Beta(1, 1) for each arm (weakly informative)
  - Posterior: Beta(successes + 1, failures + 1) for each arm
  - Report: posterior mean, 95% credible interval, P(HT > FQ | data)
  
- **Effect size**: Cohen's h (difference in proportions), computed as 2 × (arcsin(√p_HT) − arcsin(√p_FQ))
  - Small effect: h ≈ 0.2; Medium: h ≈ 0.5; Large: h ≈ 0.8

- **Sensitivity to task selection**: 
  - Repeat analysis leaving out one test task at a time (leave-one-out jackknife)
  - Report min/max posterior P(HT > FQ | data) across jackknife folds
  - If range > 0.3, note high sensitivity and request additional test tasks

- **Power analysis**:
  - Retrospectively compute power for observed difference using sequential Fisher exact test
  - Report: given observed counts, what is power to detect this effect with n_tasks additional test tasks?

---

## Concrete Resources

### Artifacts

**Training Data**: 
- Source: DACON LG Aimers public archive (https://dacon.io/competitions/)
- Tasks: select 50–100 historical submission instances with ground-truth labels (public leaderboard rank, final score)
- Format: one JSON file per task, containing problem statement, constraints, evaluation metric, and golden reference solution (if public)
- Storage: local `/workspace/training_tasks/` directory, versioned by commit hash

**Test Data** (held-out, locked):
- 10–15 new competition tasks, never released publicly or used in training
- Locked: withheld in a separate directory with read-protected artifact outputs only
- Revealed: only after all models finish training and queue/tree construction
- Format: identical JSON schema to training tasks
- Storage: `/workspace/test_tasks_locked/` on isolated machine with access logs

### Compute

- **Backbone model**: Claude 3.5 Sonnet (text-only, fixed weights)
- **Per-task budget**: T = 300 seconds wall-clock time per condition per task
- **Parallel execution**: up to 4 tasks in parallel per condition to bound total experiment time
- **Hardware**: local GPU-enabled machine or modal.com serverless GPU (if local unavailable)
  - Justification: experiments must be reproducible and auditable; cloud provider neutral

### Workspace

- **Maximum intermediate artifacts**: M = 50 per task (disk quota: 500 MB per task)
- **Maximum search depth**: N = 7 levels for tree-structured search, or 7 queue entries for flat queue
- **State storage**: SQLite database logging all attempts, branches, and outcomes to `/workspace/experiment_log.db`

### Monitoring & Reproducibility

- **Seed management**: 
  - Model temperature fixed to 0.2 (low variability for reproducible reasoning)
  - RNG seed for queue ordering: fixed per task, different seed per condition
  - Git commit hash recorded for backbone model prompt and condition code
  
- **Experiment tracking**: 
  - MLflow or local file logging to record start/end time, model tokens used, intermediate artifact hashes (SHA-256)
  - All runs tagged with experiment_id, condition, task_id, run_number
  - Logs stored in `/workspace/runs/` with one JSONL file per condition

---

## Outcome Metrics (No Results Reported Here)

### Primary
- Held-out success rate (HT, FQ, conditions 1–4)
- 95% Bayesian credible interval and posterior probability P(HT > FQ)

### Secondary  
- Insight reuse rate (HT only)
- Tree depth and breadth distributions (HT only)
- Compute cost per success (wall-clock seconds)
- Artifact size distributions (median, IQR)
- Early termination rate by condition

### Inference
- Posterior predictive distribution for success rate on 10 additional held-out tasks
- Bayes factor B₁₀ (HT > FQ vs. HT ≤ FQ) computed via Savage–Dickey density ratio
- Jackknife sensitivity bounds on posterior probability

---

## Success Criteria

- **Primary success**: P(HT > FQ | data) > 0.95 with non-trivial effect size (h > 0.3)
- **Secondary success**: ablations reveal which component (tree structure vs. propagation) drives the effect
- **Robustness**: jackknife sensitivity analysis shows stable ranking across task subsets
- **Reproducibility**: all artifacts, logs, and code versioned; re-run from stored seeds produces ≤ 1% variation in token count

---

## Notes & Limitations

1. **Justification for backbone & budget**: Claude 3.5 Sonnet is chosen because it is widely available, deterministic enough for reproducible reasoning at low temperature, and represents a reasonable proxy for production autonomous-agent scenarios. T = 300 seconds is a practical bound for competitive programming and artifact design tasks, reflecting real user expectations.

2. **Held-out locking**: Test tasks are locked to prevent data leakage. No peek at structure, evaluation metric, or ground truth until final evaluation begins. This is essential because agents could memorize or overfit to test patterns.

3. **Ablation justification**: The two ablations (lossy propagation and heuristic reordering) are chosen to decompose whether tree structure, insight propagation, or learned reordering matters most. This informs whether to invest in tree maintenance overhead.

4. **Uncertainty quantification**: Bayesian binomial model is chosen over frequentist because (a) it naturally incorporates prior knowledge, (b) allows direct statements like "P(HT > FQ) = 0.97", and (c) is more interpretable for small sample sizes (10–15 test tasks).

5. **Power sensitivity**: If jackknife analysis reveals high sensitivity (range > 0.3), the experiment result is considered inconclusive, and additional test tasks are required before deployment.

6. **Resource realism**: All named resources (model, compute platform, benchmark data) are concrete and verifiable. No hypothetical or unavailable services are assumed.

