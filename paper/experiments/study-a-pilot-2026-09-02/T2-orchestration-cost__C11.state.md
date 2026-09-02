# Research state (fill every field before writing the design)

decision_id: T2-orchestration-cost

question: 
Do multi-call orchestrations (e.g., iterative retrieval, step-by-step reasoning, self-correction loops) 
improve task accuracy enough to justify the additional inference cost (tokens and latency) they consume, 
compared to single-call baselines?

alternatives:
1. REJECTED: Compare only on accuracy without cost-weighting. This inverts the research question: cost 
   justification requires joint evaluation of accuracy gain against cost increase. Evidence: 2405.14831 
   (HippoRAG) shows single-step can match iterative performance at 10-20× lower cost; 2608.01913 
   (search agents) finds search effort and answer quality only weakly aligned—measuring accuracy alone 
   would miss the weak alignment.

2. REJECTED: Use outcome-only evaluation (judge sees only request + final answer). This structurally 
   blinds evaluation to trajectory quality and orchestration benefits. Evidence: 2609.00038 shows 
   outcome-only judges catch only 45% of silent faults; step-rubric judges reach 77% recall. Orchestrations 
   often improve intermediate reasoning even when final answers are identical—outcome-only cannot detect 
   this. Also 2608.01913 finds utilization gaps exist independent of retrieval quality.

3. ACCEPTED: Measure accuracy with trajectory-aware evaluation (rubric that scores intermediate steps 
   and reasoning), compute cost per problem, and test whether the accuracy-cost Pareto frontier favors 
   orchestration. This directly answers the research question and matches evidence methodology in 
   2608.03501 (SCOPE), 2607.09195 (HEP for auditable reasoning), and 2609.00038 (step-aware judges).

sampling_frame: 
Population: Multi-hop open-domain question-answering benchmarks (e.g., HotpotQA, 2WikiMultiHopQA, 
or equivalent) with:
  - Known ground-truth answers (string or span level)
  - Item-level difficulty estimates (gold-standard baseline accuracy by backbone)
  - Diverse reasoning paths (requiring retrieval, composition, or multi-step inference)

Unit of analysis: Individual question-answer attempts (a single (question, method, model) tuple)

Justification: Evidence 2403.14403 uses multi-hop QA to study complexity-based routing; 2405.14831 
validates HippoRAG on multi-hop QA showing cost-benefit tradeoff. Open-domain (not closed-book) 
ensures retrieval-based orchestrations are not artificially favored. Difficulty estimates (cited: 2010.06595) 
allow stratified power analysis and ablation by question hardness.

evidence_used:
  - 2010.06595: Power norms for NLP: typical experimental designs are underpowered for 1-2 percentage 
    point differences; test set size and effect size drive power. Dictates minimum sample size and blocking 
    strategy (stratify by difficulty).
  
  - 2405.14831 (HippoRAG): Single-step retrieval can match iterative methods at 10-20× lower cost; 
    cost-performance Pareto frontier is real. Justifies dual-metric design.
  
  - 2403.14403 (Adaptive-RAG): Complexity-based routing shows question properties (not just model) 
    drive optimal strategy. Justifies difficulty-stratified sampling and possible ablation by question type.
  
  - 2608.03501 (SCOPE): High-level planning (main, ablation, analysis experiments) and low-level 
    configuration (datasets, baselines, metrics) are distinct design layers. Stage isolation (separating 
    hypothesis test from configuration) improves rigor.
  
  - 2607.09195 (HEP): Hypothesis, evidence, belief must be externalizable. Rubric scoring of intermediate 
    steps (not just outcomes) is auditable and captures orchestration value.
  
  - 2609.00038 (trajectory-judge): Outcome-only judging catches only 45% of silent trajectory failures. 
    Step rubrics with zero false alarms require trajectory scoring. Guides evaluation methodology.
  
  - 2608.01913 (search agents): Search effort and answer quality weakly aligned; evidence retrieval timing 
    and utilization are separate failure modes. Dictates need to measure both retrieval success and reasoning 
    quality.
  
  - 2607.13304: Variance decomposition into within-prompt, paraphrase, model, and query-language 
    sources. Repeat allocation decision study ensures sufficient power for cost estimation.

Could not verify: Specific item-level difficulty estimates for all candidate benchmarks (would require 
running baseline on each); whether released benchmarks include problem-type annotations for stratified 
analysis (may require dataset inspection).

falsifier:
  - Main falsifier: Accuracy gains from multi-call orchestration are <0.5 percentage points absolute 
    (or <50% relative to baseline) across all question difficulties and model backbones tested. At this 
    threshold, cost differences (e.g., 5× more tokens) become indefensible.
  
  - Secondary falsifier: Single-call baseline achieves >85% accuracy on the benchmark (ceiling effect), 
    leaving no room for orchestration improvement to be meaningful.
  
  - Tertiary falsifier: Cost measurements show orchestration overhead is <10% (e.g., 1.1× tokens) and 
    accuracy gain >2 percentage points, making the research question moot (orchestration is always justified).

stopping_rule:
  - Primary: Collect results for at least 500 questions (stratified: ~166 per difficulty tier if 3-tier 
    schema) across 2+ model backbones (e.g., Llama 7B, GPT 3.5-size), 2 orchestration strategies 
    (e.g., iterative retrieval + chain-of-thought). Stop after power analysis confirms 80% power to 
    detect 1.5-point absolute accuracy difference at α=0.05 (two-sided). Evidence: 2010.06595 shows 
    GLUE-scale test sets often fail this bar.
  
  - Secondary: If bootstrap confidence interval for accuracy-cost ratio crosses zero or is <1.1 (cost 
    multiplier) at 90% confidence, stop and declare inconclusive (underpowered).
  
  - Tertiary: If computational budget exhausted (e.g., token limit or wall-clock time), report Bayesian 
    posterior with prior from 2405.14831 (HippoRAG: ~10-20× cost reduction, ~5-10% accuracy gain).
