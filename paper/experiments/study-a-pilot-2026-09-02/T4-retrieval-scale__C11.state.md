# Research state (fill every field before writing the design)

decision_id: T4-retrieval-scale-eval-design

question: At what corpus sizes do retrieval and reranking pipelines start to degrade in scientific question answering, and what is the minimum corpus size at which observed quality plateaus?

alternatives:
  - Alt 1 (rejected): Evaluate all corpus sizes identically with uniform label budget
    Rationale: Variance components differ across corpus size and retrieval scenario (2607.13304); uniform allocation ignores the fact that relevance variance scales with corpus size. Stratification by retrieval difficulty is more efficient.
  - Alt 2 (rejected): Use outcome-only judgment on answer correctness
    Rationale: Outcome-only judges miss silent failures and cannot distinguish retrieval gaps from utilization gaps (2609.00038, 2608.01913). Document-level relevance judgments are necessary to separate retrieval quality from answer reasoning.

sampling_frame: |
  Population: Scientific questions from benchmark QA datasets (e.g., Natural Questions, sciq, or papers-with-code retrieval benchmarks)
  Unit of sampling: (question, corpus_size) pairs where corpus_size ∈ {10k, 50k, 100k, 500k, 1M documents}
  Stratification: By question difficulty (as measured by retrieval recall on full corpus) into three tiers (hard, medium, easy)
  Document pool: Subset of arXiv + Wikipedia + open scientific corpora; corpus subsets created by random sampling without replacement
  Relevance judgments: Document-level binary or graded (0-3) relevance to question, labeled by domain experts or trained crowdworkers

evidence_used:
  - 2010.06595 (power norms): Statistical power is critical; underpowered experiments miss real effects and exaggerate findings. Power analysis required before settling sample size.
  - 2605.30315 (paired resolution targets): Minimum detectable effect (MDE) framework; resolution ratio q=N/N* tells whether design can distinguish observed gaps from noise at target power (α=0.05, 1-β=0.8).
  - 2607.13304 (variance components): Variance partitions into sources with different costs; allocation to repeats, paraphrases, models, languages differs. Here, allocation is to corpus-size conditions, question tiers, and replicates.
  - 2608.01913 (retrieval vs utilization gaps): Separates retrieval recall (what the pipeline finds) from answer utility (whether the LLM uses it); independent failure modes require different interventions. Design must measure both.
  - 2608.03501 (stage isolation): High-level design (main + ablations + analysis) separate from low-level configuration (datasets, baselines, metrics). Redline mechanism catches fatal flaws (source hallucination, metric incompatibility).
  - 2609.00038 (outcome-only blind spots): Outcome-only judges catch 84% of loud (answer-breaking) faults but only 45% of silent ones. Step-level (trajectory) evaluation needed; here, document-level relevance grounding required.
  - 2608.29517 (judge severity): LLM judges vary in severity by 8-15× rater SD; version shifts exist. Mitigation: train crowdworkers or use multi-judge consensus; if LLM judges, calibrate and report severity.
  
  Could not verify from evidence:
  - Exact cost per relevance label (depends on crowdsourcing platform and annotator expertise)
  - Whether arXiv subset has distribution shifts across time periods (relevant if corpus represents different eras)
  - Specific thresholds for "plateau" (domain-dependent; needs stakeholder input)

falsifier: |
  If retrieval quality (nDCG@10, MRR, recall@k) shows no significant difference across corpus sizes 10k to 1M documents at conventional power (1-β ≥ 0.8), the premise that corpus growth affects retrieval quality is false. 
  Specifically: if the 95% confidence interval on the difference in nDCG between 1M and 10k documents includes zero after accounting for multiplicity across corpus-size pairs, the effect is not resolvable at the planned sample size.

stopping_rule: |
  Stop data collection for a corpus-size condition when:
  1. Minimum detectable effect (MDE) at current label count N falls below a practically meaningful threshold (e.g., ≥ 0.02 nDCG points) at α=0.05, 1-β=0.8 (following 2605.30315), OR
  2. Bootstrap confidence intervals on nDCG@10 for that condition stop overlapping with the next-smaller corpus-size condition at 95% level, OR
  3. Variance estimate stabilizes (Gelman et al. shrinkage diagnostic ≤ 1.05), indicating additional labels do not reduce uncertainty.
  
  Stop the overall study when all five corpus sizes have met stopping criterion for the primary metric (nDCG@10), or label budget is exhausted (whichever first).
