# Research state (filled)

decision_id:
T1-context-artifact__decision-on-context-provision-strategy

question:
Among coding tasks drawn from merged pull requests, do agents that receive
a human-written persistent project context artifact (CLAUDE.md style) 
achieve higher task success rates compared to agents that receive no
context artifact, within a three-attempt budget per strategy?

alternatives:
[REJECTED] Comparison: Context artifact vs. no context vs. in-prompt context injection
  Reason: Three-way comparison exceeds power constraints on hidden test sets;
  binary comparison (with vs. without) is the minimum viable design.
  Evidence: 2010.06595 (power norms), 2605.30315 (paired test resolution).

[REJECTED] Design: Agent-only evaluation without stratification by task difficulty
  Reason: Silent failures (2609.00038) and utilization vs. retrieval gaps (2608.01913)
  require trajectory-level diagnosis, not outcome-only judgment. Stratification 
  exposes whether artifact helps equally on simple vs. complex tasks.
  Evidence: 2609.00038 (silent fault detection), 2608.01913 (two-stage decomposition).

sampling_frame:
Population: Pull requests merged into public GitHub repositories (any language).
            Drawn from the hidden test set accompanying the two agent products.
            Unit: (repository_id, task_id, strategy) triplets.
            Sampling: All tasks in the hidden test set (no random sampling within; 
            stratify by task complexity/type if the test set metadata supports it).
            
Agents: Two coding agents from different vendors (e.g., Claude Code, Codex).
        Each agent attempts the same task set under two conditions
        (with artifact, without artifact), with up to 3 attempts per condition per task.

strategies:
  - WITH: Agent provided a human-written project context artifact (CLAUDE.md) at task start.
  - WITHOUT: Agent provided only the task description, no artifact.

evidence_used:
  • 2010.06595 ("With Little Power Comes Great Responsibility"): 
    Established power-analysis norm for NLP experiments; underpowered experiments 
    are common. Justifies sample-size and replication planning.
  
  • 2605.30315 ("Resolution Diagnostics for Paired LLM Evaluation"): 
    Paired LLM comparisons often unresolved at (α, 1−β)=(0.05, 0.8) due to 
    small test sets. Minimum detectable effect and resolution ratio q=N/N* critical.
  
  • 2606.07591 ("ResearchClawBench"): 
    Demonstrates hidden-target task packaging and rubric scoring (50-point 
    threshold = rediscovery). Establishes precedent for gold-test evaluation.
  
  • 2608.03501 ("SCOPE"): 
    High-level planning completeness requires main experiment, ablations, and 
    analysis stages. Stage isolation improves LLM experimental design.
  
  • 2608.01913 ("Diagnosing Search Behavior"): 
    Retrieval vs. utilization gap decomposition. Suggests artifact efficacy 
    may differ by task complexity (needs ablation).
  
  • 2608.29517 ("LLM Judges as Raters"): 
    Judge severity, halo, and drift are large. Justifies pre-registration and 
    multiple raters (judges) or rule-based scoring over LLM judgement alone.
  
  • 2609.00038 ("trajectory-judge"): 
    Outcome-only judges miss 55% of silent faults. Step-rubric evaluation or 
    trajectory inspection required; cannot rely on final outcome alone.

Could not verify:
  - Whether the specific hidden test set is balanced across languages/domains
    (drives stratification strategy).
  - Typical effect size of context provision on agent success; no prior work 
    on CLAUDE.md-style artifacts for coding agents exists.

falsifier:
[Falsifies the design premise] The artifact provides no detectable improvement 
over the "no artifact" baseline, even when stratified by task complexity, and 
95% confidence intervals for the difference in success rates overlap zero or 
favor the no-artifact condition.

[Reduces confidence] Success improvement from artifact is 2% or less in 
absolute terms (below minimum detectable effect given power constraints).

[Structural failure] Judge or rubric agreement (inter-rater or test-retest on 
replicated attempts) falls below 0.60 (Cronbach's α), invalidating the metric.

stopping_rule:
Stop when:
  1. All tasks in the hidden test set have been attempted with all strategies 
     (both agents × both conditions × 3 attempts each = saturated design).
  2. Confidence intervals for the main effect (artifact vs. no artifact) 
     achieve 95% coverage and minimum detectable effect ≥ 2% absolute 
     success-rate difference, OR minimum detectable effect < 2% and 
     sample size is exhausted (test set size is fixed, not power-designed).
  3. Stratified analysis by task complexity/type reveals consistent direction 
     of effect across strata (no Simpson's paradox reversal).
