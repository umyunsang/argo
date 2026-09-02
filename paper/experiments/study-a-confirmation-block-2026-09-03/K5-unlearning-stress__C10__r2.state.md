# Research state (fill every field before writing the design)

decision_id: k5-unlearning-knowledge-removal-verification-via-adversarial-probing

question: Is knowledge truly removed from an unlearned model, or merely suppressed from standard queries? Can adversarial probing techniques surface supposedly-forgotten knowledge that would distinguish removal from hiding?

alternatives:
  - alt1_rejected: "Single-pass evaluation with only direct questions. Rejected because direct questions are precisely what unlearning is optimized against; failure to answer proves only suppression, not removal."
  - alt2_rejected: "Binary metrics (knows/doesn't know) without uncertainty quantification. Rejected because probing success has inherent variability; confidence intervals are needed to distinguish weak signal from noise."
  - alt3_rejected: "Test only one unlearning method. Rejected because procedure effects may be method-specific; multiple methods test whether removal is generalizable across techniques."

sampling_frame: The population is model states, the unit is (model_state, knowledge_domain, query_type) tuples. We sample across: (1) Model states: base model + K unlearned model variants from different procedures; (2) Knowledge domains: 2-3 specific bodies of knowledge targeted by unlearning (e.g., copyrighted works, sensitive personal information patterns); (3) Query types: direct factual questions, paraphrased queries, indirect multi-hop questions, jailbreak attempts, completion-based probes, few-shot adversarial examples.

evidence_used: 
  - We rely on publicly documented unlearning methods (e.g., SISA, gradient ascent, influence functions)
  - We rely on documented LLM probing techniques (adversarial suffixes, paraphrasing, indirect prompts from recent interpretability literature)
  - We cannot verify whether the "unlearning" actually occurred as claimed without independent model access or training logs
  - We cannot verify knowledge removal at the parameter level (only through behavioral tests)
  - We assume query APIs are honest (model served is what was claimed)

falsifier: If adversarial probes consistently retrieve target knowledge from supposedly-unlearned models at >80% the retrieval rate of the base model, the design's premise (that true removal can be distinguished from suppression) is refuted. The design assumes adversarial probing can distinguish; if it cannot, the research question becomes unsolvable via this approach.

stopping_rule: Collect until one of: (1) 95% CI on retrieval rate for each (model, domain, query_type) tuple does not overlap with baseline, indicating statistically clear removal; (2) 100 distinct adversarial queries per domain per model attempted without improvement in retrieval; (3) confidence intervals stabilize (new queries do not change credible intervals), indicating sample size is sufficient.
