# Research state (fill every field before writing the design)

decision_id: K6-harness-evolution-design-001

question:
  Given the ability to rewrite the agent's scaffold between iterations while keeping the model fixed, 
  can we demonstrate that measured performance gains are real improvements to the harness rather than 
  overfitting to the specific family of tasks used during scaffold development?

alternatives:
  1. Single Test Set Approach (REJECTED): Re-evaluate improved harness on the same task family 
     used for development. Reason: Cannot distinguish genuine improvements from task-specific 
     overfitting. One scaffold rewrite could simply fit the idiosyncratic characteristics of a 
     particular task distribution.
  
  2. Cross-Domain Transfer Only (REJECTED): Test improved harness on completely different domains 
     (e.g., if developed on code tasks, test on summarization). Reason: Scaffold improvements are 
     often domain-sensitive and require domain-relevant tools/skills. Complete transfer may be 
     infeasible and would penalize domain-appropriate optimizations. Fails to test real generalization 
     within related task families.
  
  3. Multiple Held-Out Task Families Within Domain (SELECTED): Divide the family of related tasks 
     into separate development and evaluation cohorts, with multiple evaluation sets drawn from 
     independent distributions within the same domain. This allows detection of overfitting to 
     particular task characteristics while maintaining ecological validity.

sampling_frame:
  Population: A family of related multi-step agent tasks within a single domain (e.g., software 
  engineering, knowledge work, or technical operations). Units of analysis: Individual task instances 
  within that family.
  
  Sampling design: Stratified random partition of the task family into three cohorts:
  - Development cohort (40% of tasks): Used to generate trajectories and diagnose scaffold weaknesses
  - Evaluation cohort A (30% of tasks): Held-out evaluation set, never seen during development
  - Evaluation cohort B (30% of tasks): Held-out evaluation set from independent sub-distribution, 
    never seen during development
  
  The two evaluation cohorts are drawn to differ in dimensions likely to stress-test robustness 
  (e.g., task difficulty, interaction patterns, error types) to avoid the development cohort's 
  implicit curriculum.

evidence_used:
  - 2606.05922.txt (Pan et al., RHO - Retrospective Harness Optimization): Demonstrated that 
    harness improvements can be validated on held-out test sets without external grading. Showed 
    improvements on SWE-Bench Pro, Terminal-Bench, and GAIA-2 by splitting benchmarks into 
    trajectory and test sets. This establishes the feasibility of the development/test separation.
  
  - 2608.18066.txt (Ye et al., Fragility of Self-Improving Agents): Demonstrated critical finding 
    that agent performance is sensitive to task order, with improvements of +1.5% reverting to -4.5% 
    degradation under random shuffling. Also showed variance in baseline performance itself (4.4% 
    best-worst gaps) and that self-improvement methods amplify variance in 71% of cases. Established 
    need for multiple runs and randomized task orderings.
  
  Could not verify: The specific task families available in this study, their inherent variance 
  distributions, or the magnitude of improvements expected from scaffold rewriting for these 
  particular tasks.

falsifier:
  If the improved harness shows large gains on Evaluation cohort A but significantly lower gains 
  (or degradation) on Evaluation cohort B, this would falsify the claim that improvements are real 
  generalizable harness gains. It would indicate the scaffold was optimized for the particular 
  failure modes or task characteristics in the development cohort rather than for fundamental 
  capability improvements.
  
  Specifically, falsification threshold: If the 95% CI for cohort A improvement and cohort B 
  improvement do not substantially overlap, and cohort B shows <50% of cohort A's gain magnitude, 
  the hypothesis of real improvement is refuted in favor of task-specific overfitting.

stopping_rule:
  Collect data until both conditions hold:
  1. Minimum sample size: At least N=30 task instances per evaluation cohort (N=60 total eval tasks)
  2. Minimum runs: At least 3 independent runs of the improved harness on each evaluation cohort, 
     with different random seeds
  3. Convergence in uncertainty: Standard error of the mean pass-rate difference falls below 2% 
     for both cohorts
  
  Stop additional data collection after this point; proceed to analysis even if running longer 
  would provide additional precision, to bound total compute cost.
