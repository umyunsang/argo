# Research state (fill every field before writing the design)

decision_id: K3-rubric-shift-agreement-signal-v1

question: |
  Does the revised rubric variant produce a statistically meaningful increase in 
  human-automatic rater agreement compared to the baseline rubric, or is observed 
  agreement change attributable to random noise in a small sample?

alternatives:
  - Alternative 1 (rejected): Simple paired agreement statistics (McNemar, Cohen's kappa change).
    Rejection: Cannot distinguish systematic improvement from noise fluctuation without 
    a null distribution or repeated-sampling design.
  
  - Alternative 2 (rejected): Single agreement measure pre/post without ablation.
    Rejection: Cannot isolate which rubric dimension(s) drive agreement change; 
    confounds wording clarity with scoring logic changes.

sampling_frame: |
  Population: Scoreable items (documents, essays, or media segments) that can be 
  independently rated by both human raters and an automatic scoring system.
  
  Unit of sampling: (item, human_rater_1, human_rater_2, automatic_rater) tuples 
  across both rubric variants (baseline and revised).
  
  Concrete frame: A set of items scored in prior work under the baseline rubric 
  by two independent human raters and one automatic system. The *same items* 
  are re-scored by the same automatic system under the revised rubric. 
  Human raters re-score under the revised rubric only (to avoid practice effects).
  
  Assumption: At least 20–30 items with complete baseline triples 
  (human_1, human_2, automatic) are available for re-scoring under revised rubric.

evidence_used:
  - The research premise: that rubric clarity and structure affect human-automatic 
    agreement independent of rater noise.
  - Justification: Prior rubric-design literature (Arter & McTighe; Moskal & Leydens) 
    shows rubric wording affects rater consistency.
  - Constraint evidence: The problem statement confirms limited human ratings and 
    same-items comparison are required; this bounds design choices.
  - Limitation: No access to historical data on agreement variance across rubric 
    edits in this specific domain; design choices rely on general statistical principles 
    (e.g., paired designs reduce variance, ablation isolates mechanisms).

falsifier: |
  The design premise (that systematic rubric change can be distinguished from noise) 
  is refuted if:
  
  - The observed agreement change (e.g., kappa or overlap rate) falls within the 
    95% confidence interval of the null distribution (bootstrapped from baseline 
    human-human agreement), OR
  
  - The ablation (revised rubric, baseline human training) shows no meaningful 
    difference from the full revision, suggesting agreement change is driven by 
    human adaptation, not rubric clarity, OR
  
  - Repeated items show inconsistent agreement shifts (high variance), indicating 
    noise dominates over systematic rubric effect.

stopping_rule: |
  Stop data collection when:
  
  1. All available items (n ≥ 20) have been re-scored under the revised rubric 
     by the automatic system, AND
  
  2. A random sample of n_h human raters (budget-limited, likely n_h = 2–4) 
     have re-scored all items under the revised rubric, AND
  
  3. 95% confidence interval for agreement change (via bootstrap) excludes zero 
     OR includes zero (either outcome provides sufficient evidence to decide).
  
  Hard stop: If agreement variance is >2× the baseline, consider design failure 
  and recommend expert review of automatic system behavior under revised rubric 
  before collecting more data.
