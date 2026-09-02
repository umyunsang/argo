# Research state (fill every field before writing the design)

decision_id: K3-rubric-shift__adopt-variant

question: 
  Does the new rubric variant produce a measurably different (not merely noisier) 
  human-automatic rater agreement compared to the baseline rubric, holding the 
  items and raters constant?

alternatives:
  - Alternative 1 (rejected): Compare rubric variants using raw score differences 
    without variance decomposition. This conflates rubric effect with rater severity 
    drift and model noise (2608.29517 shows judge severity can vary by 15-33% of 
    scale range; uncontrolled changes masquerade as rubric effects).
  
  - Alternative 2 (rejected): Use a single pass of ratings per item per rubric. 
    This provides no signal about noise structure and cannot distinguish whether 
    agreement shifts are real or within resampling variance (2010.06595 documents 
    that underpowered designs conflate noise and effect; 2607.13304 shows 
    crossed random-effects decomposition is required to separate variance sources).

sampling_frame:
  Population: Items scored by at least one human rater and one automatic rater 
  under both the baseline rubric and the new variant (same item, cross-over design).
  Unit: (item, rubric_variant) with replicate ratings from the human pool.
  Cardinality: All items for which paired baseline and variant scores exist from 
  both automatic and at least one human rater. The design requires balanced replication 
  structure to estimate variance components.

evidence_used:
  - 2010.06595: Statistical power norms show that agreement-detection experiments 
    are commonly underpowered in NLP, and underpowered studies cannot discern 
    noise from true effect. Justifies pre-registered power calculation.
  
  - 2608.29517: LLM Judges as Raters documents rater-effects battery (severity, 
    halo, generalizability/decision studies, version shifts). Shows that judge 
    severity spans 15-33% of score range even on matched dispersion; demonstrates 
    how rater-effects confound rubric evaluation. Justifies crossed-random-effects 
    variance decomposition.
  
  - 2607.13304: Variance-components decomposition shows how to partition non-determinism 
    into separable sources (within-prompt, paraphrase, model identity, language) 
    and embed components in allocation decision. Justifies generalizability-theory 
    framing for this rubric-shift study (sources: rubric variant, rater, item, 
    within-rater noise).
  
  - 2605.30315: Resolution diagnostics for paired LLM evaluation shows how to 
    invert level-α, power-(1−β) tests and report resolution ratio q=N/N⋆. Shows 
    small-effect paired test power deviates from unpaired Cohen-h by factor of 
    two in close-comparison regime. Justifies paired-test power calculation with 
    inter-rater correlation adjustment.
  
  - 2608.03501: SCOPE benchmark for experiment design shows that high-quality 
    designs include main, ablation, and analysis experiments with explicit stage 
    isolation. Justifies ablation (measurement model variant) separate from main 
    (rubric variant effect).
  
  Could not verify: (a) The specific items and their score distributions under 
  both rubrics (not in ./evidence). (b) The pool size and composition of available 
  human raters. (c) The automatic rater model and its replicability/stability 
  across rubric variants. (d) Whether items have been pre-stratified by difficulty 
  or domain. These are required to finalize sample-size and blocking decisions.

falsifier:
  The null hypothesis is: H₀: correlation(agreement_baseline, agreement_variant) ≥ ρ₀ 
  (agreement rank is preserved under rubric change, after removing noise).
  
  Falsifier: If the variance-component estimate of rubric-variant effect on 
  human-automatic agreement is zero or within its confidence interval, or if 
  the effect direction reverses across random halves of the item pool, the design 
  fails to support adoption of the new variant.

stopping_rule:
  Stop data collection when:
  (1) The paired-test resolution ratio q = N_actual / N_target reaches q ≥ 1.0 
      at α = 0.05, power = 0.80 for the main comparison (variance-component estimate 
      of rubric effect on agreement correlation).
  (2) AND ablation (measurement model variant) shows that the rubric effect remains 
      significant after controlling for rating scales and functional form.
  (3) AND replication-consistency check: the effect does not reverse sign in 50% or 
      more bootstrap samples of item subsets (at least two disjoint halves).
  
  Pre-stop in favor of null: If after N_max items (half of available pool), 
  q < 0.50 and the confidence interval includes zero.
