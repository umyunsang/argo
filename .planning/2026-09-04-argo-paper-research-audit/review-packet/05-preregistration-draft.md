# 05 — G × C × F Confirmatory Preregistration Draft

Status: **DRAFT, NOT SEALED, NOT APPROVED, NOT EXECUTABLE**  
Created: 2026-09-04T15:43:42+09:00

## Research question

Under a fixed model, tool surface, corpus snapshot, and resource budget, do typed evidence-and-experiment lineage,
design competition with rule-based admission, and a bounded falsification/refinement loop improve validity, scientific
task outcome, reproducibility, and recovery in long-horizon autonomous R&D?

## Hypotheses

- **H1-G:** G improves rule-verified evidence/experiment lineage completeness and reduces unsupported retained claims.
- **H2-C:** C improves held-out scientific task score under the same maximum resource budget.
- **H3-F:** F improves method validity and held-out task score without exceeding the resource cap.
- **H4-GC:** C benefits are larger with typed lineage than with flat state.
- **H5-GF:** F is less likely to introduce unsupported or stale conclusions with typed lineage.
- **H6-FULL:** G1C1F1 has the best observed reliability-adjusted task score among the eight cells. This fails unless
  Holm-adjusted paired task-cluster intervals exceed the H6 practical-effect threshold against every comparator.
- **H7-RECOVERY:** separated graph-backed research/engine lineage reduces recovery loss under injected interruption
  without a final-quality drop beyond the noninferiority margin. Stage 2 isolates this through `L1P1 - L0P1`, holding
  checkpoint/recovery metadata constant.

## Treatment and baseline

The binding manifest is `02-treatment-manifest.json`. `G0C0F0` is the same-backbone causal reference. A model-only
anchor is development-only and cannot replace it.

## Outcomes

**Primary:** condition-blind, rule-based, held-out official task score, normalized to [0,1]. Fatal protocol violation,
oracle access, invalid provenance, agent-caused failure, missing output, parse failure, evaluator crash, timeout, or
nonzero exit receives zero in intention-to-run.

Report separately: official score/pass@1/median/reliability `pass^3`; protocol-valid completion; independent clean
rerun; evidence-link completeness; citation precision/recall/coverage; unsupported-claim and justified-abstention
rates; duplicate proposal/action rate; resume fidelity; human interventions; invalid/crash/timeout/provider incidents;
wall time, tokens, cost, tool calls, and experiment count. No opaque composite replaces these outcomes.

For H6 only, define the preregistered **reliability-adjusted task statistic** for task `t`, cell `c` as
`RA[t,c] = S[t,c] * P[t,c]^3`, where `S[t,c]` is the intention-to-run mean normalized official score across scheduled
seeds and `P[t,c]` is the fraction of those seeds that achieve the official task pass criterion. Failures stay zero in
both terms. This nonlinear H6 statistic is reported in addition to, never instead of, `S` and `P`.

## Estimands

- marginal within-task average treatment effects for G, C, and F;
- within-task GC and GF interactions;
- FULL-minus-each-comparator contrasts for H6;
- recovery treatment effect and final-quality noninferiority contrast for H7.

The confirmatory cell statistic averages all scheduled intention-to-run seeds within task. **Best-of-k, best-seed,
and best-checkpoint selection are forbidden confirmatory estimands** because time allocation across independent attempts
changes the estimand (`rebench_best_of_k_allocation`). The official held-out score is hidden until each F path stops;
within-loop score visibility is limited to the non-oracle validity signal.

The minimum practically important effect for normalized task score is **0.10 absolute**. This equals one additional
success per ten tasks **only when the endpoint is binary and tasks are equally weighted**; for graded scores it means a
0.10 increase in the mean normalized scorer output and has no one-in-ten interpretation. H6 uses +0.10 absolute on the
separately defined `RA` statistic. H7's final-quality noninferiority margin is **-0.05 absolute**.

## Sampling, randomization, and blinding

Use `04-task-sampling-and-certification.md`: 4 distinct development tasks excluded permanently; 12–20 distinct hidden
confirmatory tasks across at least four domains; at least three unique rollout IDs per task-cell. Propagate and verify
`environment_seed` for controllable task/library RNGs. Because the provider has no sampling-seed interface,
`model_sampling_seed=null`; model calls are unseeded nested repeats. Randomize and counterbalance cell order within task.
Scorer and infrastructure-failure classifier are blind to condition.

## Exclusions and retries

No attempted run is deleted. Manipulation failure, invalid provenance, or oracle access stays zero in intention-to-run
and is excluded only from the protocol-complete sensitivity set. Only a preregistered infrastructure incident may be
retried once, after a blinded classifier labels it without seeing condition outcomes. The original remains in the
reliability denominator. Agent-caused failure is not retried.

## Hypothesis-to-test mapping

| hypothesis | task-level statistic and contrast | success rule |
|---|---|---|
| H1-G | marginal G contrast in evidence-link completeness | Holm-adjusted two-sided 95% interval lower bound > +0.10; unsupported-claim rate reported separately |
| H2-C | marginal C contrast in normalized official task score `S` | adjusted lower bound > +0.10 |
| H3-F | marginal F contrast in `S` | adjusted lower bound > +0.10 |
| H4-GC | difference-in-differences of C across G in `S` | adjusted lower bound > +0.10 |
| H5-GF | difference-in-differences of F across G in unsupported retained-claim rate | adjusted upper bound < -0.05 |
| H6-FULL | seven paired `RA[G1C1F1] - RA[comparator]` task contrasts | all seven adjusted lower bounds > +0.10; otherwise H6 fails |
| H7-RECOVERY | paired Stage 2 `L1P1 - L0P1` contrast in lost-work ratio plus final-quality contrast | adjusted lost-work upper bound < -0.10 and final-quality lower bound > -0.05 |

## Analysis

Primary uncertainty: task-cluster bootstrap 95% intervals, resampling tasks and retaining nested rollout IDs/cells. Secondary:
mixed-effects model with condition fixed and task/reviewer random effects. The global confirmatory family contains the
five H1–H5 contrasts, seven H6 pairwise contrasts, and the H7 recovery-superiority contrast; apply Holm correction over
those 13 superiority tests. H7 final-quality noninferiority is an intersection requirement with its fixed -0.05 margin,
not a substitute superiority claim. Report intention-to-run and protocol-complete sensitivity analyses. Never treat
seeds or rollouts as independent n.

## Power and cost simulation

Before confirmation, use only the four development tasks to estimate task-level contrast variance and empirical cost.
Run Monte Carlo power simulation preserving task clusters, nested rollout variability, eight-cell counterbalancing, zero/failure mass,
and Holm multiplicity. Choose 12–20 tasks for at least 80% power at the 0.10 practical effect. If 20 tasks cannot reach
that target inside the human-approved cost envelope, confirmation is blocked or the five-arm removal fallback is
submitted for a new approval with downgraded claims.

## Stopping and reopening

Hard-stop on budget, wall-time, token, tool-call, provenance, oracle-isolation, or environment-seal violation. F=1 has
at most three rounds. Its within-episode improvement signal is **non-oracle**:
`V[r] = passed preregistered protocol-validity checks / K`, where the fixed K checks cover method validity, provenance,
source support, and executable preconditions but exclude the hidden scorer, gold output, official score, and any proxy
trained on them. Stop early after two consecutive `V` improvements smaller than `1/K`, when `V=1`, or at budget
exhaustion. Do not inspect confirmatory scorer outcomes or contrasts midstream. Reopen only for a documented protocol defect found without condition outcomes;
archive the old protocol and assign a new fingerprint and disjoint confirmation set.


## Sequential-falsification boundary

POPPER (`2502.09858`, full-read receipt `popper-full-read-receipt.json`) motivates the need to bind adaptive stopping to
valid information. Its theorem requires implication, conditional sequential validity, and optional-stopping
measurability (`popper_implication_assumption`, `popper_conditional_sequential_validity`,
`popper_optional_stopping`). Factor F does not produce p/e-values, so it inherits **no Type-I guarantee** from POPPER.
F uses only the non-oracle `V[r]` signal; the condition-blind official scorer runs once after F terminates. Failed
execution remains zero/inadmissible and never becomes positive evidence (`popper_failed_attempt_not_evidence`). The
unrefined candidate is retained because OpenScholar reports that an initial output was preferred over its refined
output around 20% of the time (`openscholar_overediting`); improvement is not assumed monotone.

## Protocol fingerprint fields

Canonical JSON must include: research-question version; treatment-manifest hash; hypotheses/outcomes/estimands;
benchmark release and task hashes; split/schedule seed; environment seeds; rollout IDs; provider seed-support flag and nullable model sampling seed; scorer and environment digests; model checkpoint/API revision;
system-task interface; tool/retrieval/corpus hashes; retry/stopping authority; token/tool/time/cost caps; analysis-code
hash; actor and timestamp. Fingerprint is SHA-256 over UTF-8 canonical JSON (`sort_keys=true`, compact separators).
