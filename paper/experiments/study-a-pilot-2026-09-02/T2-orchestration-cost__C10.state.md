# Research state (fill every field before writing the design)

decision_id: T2-orch-cost-accuracy-tradeoff

question: At what accuracy improvement threshold does multi-call orchestration (e.g., planning + refinement loops) become cost-justified compared to single-pass inference, across open-weight and closed-source model backbones?

alternatives:
  1. Fixed orchestration depth: Rejected because accuracy may vary by task complexity; adaptive orchestration can be evaluated first to establish thresholds.
  2. Prompt optimization as the primary lever: Rejected because it applies equally to both conditions by constraint; orchestration is the true differing variable.
  3. Only closed-source models (e.g., GPT-4): Rejected because the question must inform decisions for both API-dependent and self-hosted deployments; multi-backbone testing is essential.

sampling_frame:
  population: Reasoning tasks from two benchmark families—general multi-step reasoning (MMLU-Pro) and code synthesis (HumanEval)—each with item-level difficulty annotations or pass-rate baselines.
  unit: Single task instance (MMLU-Pro question or HumanEval problem).
  coverage: Sample 40 items per benchmark, stratified by difficulty quartile (10 per quartile), ensuring representation across the difficulty range on which accuracy vs. cost trade-offs may differ.

evidence_used:
  - MMLU-Pro difficulty tags (published with the benchmark; fully verifiable).
  - HumanEval baseline pass rates from Hugging Face transformers library (public, reproducible).
  - Model inference cost from official API pricing (OpenAI, Anthropic) and measured token consumption on open-weight models.
  - Could not verify: exact breakdown of training compute vs. inference cost for Llama models (proprietary training details); actual latency under production load (design uses published rates, not production runtime).

falsifier:
  If single-pass inference achieves >98% of orchestrated accuracy at <1.5× the token cost across both benchmarks and all tested model backbones, the premise of the research question (that orchestration is cost-justified) would be refuted.

stopping_rule:
  Collect results from all 80 sampled items (40 per benchmark) across all condition–backbone combinations. Stop if any backbone shows unambiguous preference (Δ accuracy >5 percentage points, token cost difference >3×) after 30 items; report confidence intervals and continue to 40 for final comparison.
