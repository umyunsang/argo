# Research state (fill every field before writing the design)

decision_id: K1-hypothesis-search-tree-vs-flat-queue

question: Does organizing an autonomous agent's attempts as a hypothesis tree with propagated insight beat a flat queue of attempts on held-out artifact optimization?

alternatives:
  - Alternative 1 (rejected): Random allocation of compute budget across agent attempts without any organization structure. Rejected: lacks principled comparison baseline and ignores evidence (2607.09195) that hypothesis evolution requires explicit, auditable structure to yield gains.
  - Alternative 2 (rejected): Purely learning-based routing (e.g., bandit-style or reinforcement-learned allocation) without explicit hypothesis generation and tracking. Rejected: 2607.09195 demonstrates that when agents do not externalize hypothesis-evidence-belief state, they cannot propagate insight across attempts. Unstructured learning-based allocation would confound the signal.
  - Alternative 3 (rejected): Independent parallel searches (one per task, no cross-task learning). Rejected: leaves held-out generalization untested; cannot measure whether insight propagates across task instances.

sampling_frame: 
  Population: Artifact optimization problems requiring iterative refinement (code tuning, hyperparameter search, prompt engineering) that have ground-truth success metrics and admit multiple solution paths.
  Unit of analysis: A single held-out optimization task.
  Sampling design: Stratified random split of tasks into held-out evaluation set (30% of tasks, used to decide promotion between arms) and exploration budget split between hypothesis-tree arm and flat-queue arm (70% of tasks, used to train and consume compute budget).

evidence_used:
  - 2607.09195 (Hypothesis Evolution Protocol): Demonstrates that explicit hypothesis-test-evidence-belief cycles in agent harnesses enable auditable scientific reasoning. Found that HEP-equipped agents generalize across research questions and exploit the protocol more fully. Directly supports tree-based organization with propagated insight.
  - 2608.03501 (SCOPE benchmark): Establishes evaluation framework for autonomous experimental design quality, distinguishing main experiments, ablations, and analysis. Informs our experiment structure.
  - 2608.01913 (Diagnosing Search Behavior): Introduces the retrieval/utilization gap decomposition and trajectory-level diagnosis. Relevant for decomposing where hypothesis-tree arm succeeds or fails.
  - 2609.00038 (trajectory-judge): Outcome-only evaluation is structurally blind to silent failures. Step-level trajectory rubrics catch 77% of silent failures vs 45% for outcome-only. Informs our evaluation protocol.
  - 2605.30315 (Paired LLM Evaluation): Specifies paired-test resolution targets and minimum detectable effect (MDE). Off-the-shelf sample-size calculators using unpaired Cohen-h can underestimate N* by ~2× in close-comparison regime. Informs statistical power calculation.
  - 2010.06595 (Statistical Power Norms): Meta-analysis of NLP papers finds most experiments underpowered. Small test sets mean most comparisons to SOTA are not adequately powered. Justifies pre-registration of MDE and power target.
  - Couldn't verify: (1) Whether propagated insight actually reduces redundant exploration under realistic compute budgets; (2) Whether hypothesis tree structure imposes overhead (e.g., time to articulate hypotheses) that negates gains on short-horizon tasks; (3) Whether the same backbone architecture scales equally to both arms.

falsifier:
  The hypothesis-tree arm fails to outperform the flat-queue arm on held-out tasks at the pre-registered minimum detectable effect (MDE) under equivalent compute budgets. Specifically: if the observed effect size on held-out tasks is ≤ MDE, or if confidence interval includes zero, the premise that explicit hypothesis organization provides optimization advantage is refuted.

stopping_rule:
  Primary: Stop when all held-out task batches have been evaluated and we have collected sufficient paired measurements to detect MDE at α=0.05, power=0.80 under the true paired-test design (accounting for within-task correlation per 2605.30315).
  Secondary (override): Stop if either arm exhausts its compute budget (fixed tokens, inference calls, or wall-clock time as specified in resource allocation) before reaching the power threshold. Report as underpowered and flag for larger followup.
