# Research state (fill every field before writing the design)

decision_id: K4-benchmark-stopping-rule

question: Given that an optimizing agent can call a target evaluation function repeatedly, how should a benchmark distinguish genuine algorithmic improvement from score inflation via exhaustive search?

alternatives:
  - Naive cap: Impose a hard ceiling on evaluation calls per run (e.g., 100 calls max). REJECTED: This does not measure whether an agent is making real progress within its budget or just buying time-complexity. A weak agent at the cap and a strong agent at the cap are indistinguishable by this rule alone.
  - First-eval-only: Record only the target value from the agent's first evaluation call, discarding all subsequent ones. REJECTED: This throws away the agent's ability to learn and verify solutions. An agent that samples once blindly is rewarded equally with an agent that samples once after reasoning. The rule conflates call count with call necessity.
  - Post-hoc overfitting detection: After the agent finishes, use statistical tests (e.g., comparing in-distribution training accuracy to held-out test accuracy) to detect whether the agent exploited the evaluations. REJECTED: This requires a test set and assumes the agent was "trained" on the in-distribution samples. For a one-shot optimization agent (e.g., iterative solver for a single problem), there is no training set to compare against; the agent is simply exploring the same problem space repeatedly.

sampling_frame: A fixed benchmark of N evaluation problems, each with a known ground-truth optimal value (or a held-out test-set rank). The frame is the population of (problem, agent run) pairs where an agent is assigned a problem and given a resource budget B (measured in evaluation function calls). Each run produces a trajectory of evaluation calls and a final claimed solution. The unit of analysis is a single run on a single problem. The empirical claim we test is whether the agent's best solution found by call k plateaus (evidence saturation) before call B, or whether the agent continues to extract new solutions from the evaluation oracle up to the limit.

evidence_used: 
  - 2608.01913 (Liu et al., Diagnosing Search Behavior): Long-horizon agents show that search effort and answer quality are weakly aligned; what matters is cumulative evidence recall. Most evidence surfaces early in trajectories; later steps are a "wasted tail." Agents stop too late, not too early. This supports a stopping rule based on saturation detection.
  - 2605.30315 (Kotawala, Resolution Diagnostics): Paired-comparison tests have a minimum detectable effect (MDE) that depends on sample size and within-item correlation. A benchmark's ability to resolve whether two models are different requires adequate N. For a single agent on a single problem, this argues for measuring whether the agent's improvement rate drops below the MDE for the problem's noise level.
  - 2607.13304 (Zatuchin, Variance Components): Within-prompt resampling is one source of variance, but spreading queries across paraphrases and models reduces error more efficiently. This is relevant: if an agent makes 10 identical evaluation calls (resampling), the information gain per call decreases; if it makes 10 diverse solution attempts, information gain per call may be higher.
  - 2609.00038 (Mohammadi, trajectory-judge): Outcome-only evaluation misses process-level faults. Agents can reach correct answers by violating constraints. This argues that a benchmark must inspect the agent's trajectory (its sequence of calls and reasoning), not just its final score, to detect whether it is genuinely optimizing or gambling.
  - 2608.03501 (Liu et al., SCOPE): Experimental design benchmarks evaluate both high-level planning completeness (main/ablation/analysis) and low-level configuration accuracy. Our design must include not just a main comparison but ablations of the stopping rule itself.
  
  Cannot verify: We lack evidence on whether agents trained with RL to exploit benchmarks (against a fixed evaluator budget) do in fact reach a saturation point or continue to exploit until a hard cap. This is a prediction, not an observation.

falsifier: The design's core premise is that an optimizing agent exploring a fixed evaluation oracle will eventually saturate—that is, the marginal information gain per call will drop below a noise threshold or the best solution found will plateau for consecutive calls. A falsifier would be evidence that:
  (1) An agent systematically continues to improve beyond the observed plateau (i.e., the plateau is spurious), when scored on an independent held-out test set; or
  (2) The agent's best solution value drifts chaotically without any saturation-like behavior for call counts well below the resource budget (i.e., the agent is effectively gambling rather than optimizing), and this drift is indistinguishable from an underfitted model searching a genuine landscape.

stopping_rule: 
  - Data collection continues until all agents have completed their runs on all N benchmark problems, with each run metered up to a call budget B.
  - Analysis phase: For each (agent, problem) run, measure the marginal improvement over the last K consecutive calls. Set K = 5 (or to a value derived from the problem's noise level via a variance estimate). If max(improvement over last K calls) < noise_threshold (e.g., 0.01 * problem_range, or one standard error of estimate), mark the run as saturated and stop the trajectory at that point.
  - Reporting phase: Stop reporting when the main comparison (with stopping rule applied) is stable (i.e., the ranking of agents does not change under three independent noise samples of the problem set, via bootstrap). An ablation that removes the stopping rule (using full budget) is run in parallel and reported, with effect-size and resolution diagnostics from 2605.30315.
