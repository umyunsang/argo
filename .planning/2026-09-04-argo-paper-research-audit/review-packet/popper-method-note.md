# POPPER Full-Read Method Note — Boundary for Factor F

Source: Huang et al., *Automated Hypothesis Validation with Agentic Sequential Falsifications*, PMLR 267 / arXiv:2502.09858.  
Read receipt: `popper-full-read-receipt.json` SHA-256 `912c5d0c9937c6f5d37f1fc72a294cc88575fb435ae5f548daee5a52c168ae51`  
Locator set: `popper-locators.json` SHA-256 `e84dc1cd5394ce0922a5f18975c7e639e84b161baaa83caa00aea7186f6a49e7`

## What transfers

POPPER turns an abstract hypothesis into measurable null sub-hypotheses, separates experiment design from execution,
and accumulates evidence sequentially. Its formal Type-I guarantee requires all three conditions:

1. the main null implies every tested null sub-hypothesis (`popper_implication_assumption`);
2. each e-value is conditionally valid given all prior information, and unused data do not influence test selection
   (`popper_conditional_sequential_validity`);
3. termination is a stopping time over the observed filtration (`popper_optional_stopping`).

Under those assumptions, the terminal e-value controls Type-I error (`popper_type1_theorem`). Failed executions are
recorded as failures and do not become inferential observations (`popper_failed_attempt_not_evidence`).

## What does not transfer

ARGO factor F currently refines a method against deterministic **non-oracle protocol-validity checks**. Those checks are
not p-values or e-values. Therefore POPPER does **not** provide a Type-I guarantee for F, and its reported power does not
predict an ARGO effect. The paper also warns that per-hypothesis Type-I control does not make selected discoveries true
when many hypotheses are screened (`popper_type1_not_truth`).

## Design consequence

During confirmatory tasks F may not inspect the hidden scorer, gold output, or any trained proxy. It can refine only from
the sealed non-oracle `V[r]` checklist and execution diagnostics that reveal no outcome. Official task score is computed
once after the F path stops. If future work adaptively combines multiple statistical test outcomes, it needs a separate
POPPER-like preregistration proving implication, conditional validity, and optional-stopping assumptions; the current F
protocol cannot silently inherit that guarantee.

## Counterevidence and failure controls

POPPER reports errors from p-value misinterpretation, ineffective tests, broken implication, and incorrect
implementation (`popper_failure_modes`). Thus an LLM relevance checker or successful execution is not itself a validity
certificate. ARGO retains deterministic admission, explicit implication checks, and zero scoring for failed execution.
