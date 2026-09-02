# Research state (fill every field before writing the design)

decision_id: K5-unlearning-stress-primary-comparison-design

question: Does an unlearning procedure produce genuine knowledge removal (unrecoverable via adversarial queries) versus suppression-at-inference (recoverable by bypassing safety layers or using indirect prompts)?

alternatives:
  - Alternative 1 (rejected): Direct behavioral comparison only. Rejected because suppressed knowledge can still be retrieved via jailbreaks, indirect questions, or multi-turn adversarial prompts. This would conflate removal with mere response filtering.
  - Alternative 2 (rejected): Mechanistic circuit analysis without behavioral testing. Rejected because circuit-level changes do not guarantee functional knowledge removal; models may route around removed circuits or recover information through redundant pathways. Behavioral tests are necessary to confirm external unavailability.

sampling_frame:
  population: Knowledge domain(s) claimed to be unlearned (specific knowledge assertions, facts, procedures, or reasoning patterns documented in the unlearning procedure's paper or disclosure)
  unit: Individual knowledge-retrieval task (each task attempts to elicit a single fact, reasoning step, or behavioral capability from the population via a distinct query method)
  sample_design: Stratified by query method (direct factual recall, indirect reasoning, adversarial/jailbreak, multi-turn context-building, code generation with incidental recall) to ensure broad coverage of retrieval pathways

evidence_used:
  - Public unlearning procedure papers or model cards claiming knowledge removal (e.g., model weights, training procedure descriptions)
  - Published adversarial attack patterns for language models (jailbreaking, prompt injection, indirect elicitation)
  - Query interfaces to the purportedly unlearned model and control models (non-unlearned, partially unlearned variants if available)
  - Manual annotation of knowledge difficulty and retrieval surface (is this knowledge commonly referenced in web data? Is it highly specific or widely known?)
  - Could NOT verify: Actual training procedure implementation details; ground truth about pre-unlearning model knowledge; internal representations of the model

falsifier: If every retrieval method (direct factual, adversarial, indirect, multi-turn) consistently fails to retrieve the knowledge from the unlearned model across multiple independent trials, and retrieval succeeds at similar rates for a control non-unlearned model, then the design's premise (that removal can be distinguished from suppression) is falsified. We would be unable to reliably detect the distinction experimentally.

stopping_rule:
  primary: Once at least N=30 distinct knowledge units have been tested across ≥3 retrieval methods each, producing ≥90 independent retrieval attempts with documented success/failure.
  early stopping: If the retrieval success rate in the unlearned model reaches zero across all methods for the first 10 units, terminate early (evidence is already conclusive). If retrieval rates match the control model within 5 percentage points for 15 consecutive units, halt (no evidence of unlearning detected).
  confidence: Continue until 95% Bayesian credible interval width (posterior probability that unlearned ≠ control) is ≤0.10.
