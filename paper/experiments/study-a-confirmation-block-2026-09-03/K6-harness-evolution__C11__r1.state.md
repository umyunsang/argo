# Research state (fill every field before writing the design)

decision_id: k6-harness-generalization-design

question:
  Does a harness optimized on one task family generalize to a disjoint task family from the same domain, or does its improvement reflect overfitting to the optimization set's particular challenges?

alternatives:
  - Alt 1 (rejected): Measure only held-out test performance within the same benchmark family used for harness rewriting. This repeats prior RHO methodology (2606.05922) and does not address whether the harness truly generalizes beyond the coreset's statistical properties.
  - Alt 2 (rejected): Compare harness improvements across different random seeds without varying task families. This conflates within-domain variance (addressed in 2608.18066) with cross-domain generalization risk. High variance is necessary evidence of fragility, but not sufficient to establish generalization.

sampling_frame:
  Population: Task families in a single broad domain (e.g., code-generation, web-browsing, or QA).
  Sampling units: Disjoint task families such that (a) optimization family and held-out family have no overlapping instances, (b) both are representative of the domain, and (c) task distribution differs (e.g., optimization uses SWE-Bench Pro; held-out uses Terminal-Bench 2 or a held-out portion of GAIA-2). The model and baseline harness remain fixed; only the scaffold is rewritten.

evidence_used:
  - 2606.05922.txt (RHO): Demonstrates that self-supervised harness optimization via retrospective coreset selection improves held-out performance (SWE-Bench Pro 59→78%). However, RHO's evaluation is confined to held-out splits of the same benchmark; generalization to disjoint task families is not addressed.
  - 2608.18066.txt (Fragility): Demonstrates that agent improvement is brittle: variance increases in 71% of cases, and task order effects cause -4.5% performance swings. This motivates measuring robustness across independent task families as an antidote to hidden curriculum effects.
  - Could not verify: Whether prior work compares harness optimization on Task Family A against an unseen Task Family B from the same domain; most prior work only reports within-benchmark held-out gains.

falsifier:
  If the optimized harness achieves pass rate on Family B ≤ baseline harness on Family B (i.e., ∆_held-out_Family_B ≤ 0), the design's premise (that harness improvements generalize) is refuted. Additionally, if variance quantified across 10+ independent runs on Family B exceeds variance on Family A by >50%, this suggests overfitting.

stopping_rule:
  Stop collecting runs when: (1) at least 10 independent runs have been completed for both Family A (optimization) and Family B (held-out), AND (2) Family B pass rate and 95% CI have stabilized (coefficient of variation < 5%), OR (3) 10 runs are exhausted due to compute constraints. Do not continue optimization or re-tuning after Family B results are observed, to preserve train/test separation.
