# Experiment and statistical audit: frozen C64

Date: 2026-09-05 KST. Root-authored bounded replacement after the delegated statistical reviewer disconnected without delivering its report. That branch was closed; this file is not presented as an independent second statistical approval.

Scope: full reads of the retained C design, approval, power scenarios/validation, and current `confirmation/run.py`, `analyze.py`, `score.py`, `pilot_v2/plan_confirmation.py`. Source hashes and independent closed-form arithmetic are in `evidence/statistical-arithmetic-check.json`; frozen authority snapshots are in `evidence/authority-hashes-at-synthesis.json`. The task generator, model tools and every raw attempt were not re-audited here. No experimental source was executed, no model call was made, and no running protocol was changed. Earlier status inspection exposed the first pair; this is not a blinded preregistration. Arithmetic below uses hypothetical assumptions only, not interim C effects.

## 1. What is actually being tested

`confirmation-design.json` defines a two-record allocation/decision microbenchmark over 16 synthetic structural graphs, eight affected and eight unaffected. C64 is 32 first-rollout episodes plus 32 order-reversed reliability episodes. The inference unit remains the structural task: **n=16, not n=32 or n=64**. Counts measure attempts, not independent scientific domains.

The current manifest's broader strong-result-tree versus typed-policy research question remains defensible, but this small task does not execute the integrated scientific workflow. A graph-policy superiority claim over an adaptive research tree is not established by winning against the frozen C allocation policy. A positive outcome is useful mechanism evidence at its declared scope; a negative result also cannot reject every possible graph system.

The separate user message approved C execution; the session owner selected C64 under the predeclared recommendation. Approval SHA: `997c2a3f21921aa6b07abf56633a22ec8bf7249ca227eebd605eeca90b5dbf63`. The old approval-null field inside the immutable design does not override this later receipt. Exactly 64 attempted episodes are authorized; no added sampling or post-hoc reruns are authorized by this audit.

## 2. Test direction: retain the frozen executable test

The design names a **two-sided exact sign test over discordant task pairs**, and `analyze.py:13` implements that test. Its `h0` wording is directional (`target win probability <= 0.5`), whereas the executable test uses the symmetric equality reference and additionally requires a positive paired difference for success. This is a wording/estimand clarification, not evidence of an implemented one-sided p-value or a reason to switch tests after seeing data.

- Five TARGET wins and zero BASE wins give two-sided p=0.0625, not significance at 0.05.
- Six TARGET wins and zero BASE wins give two-sided p=0.03125. Ties are excluded from the sign-test denominator, not from the reported task count or paired mean.
- Preserve primary and replication separately. Do not pool repeats, choose the better block, or change alpha/tail direction. A descriptive interval or sensitivity analysis added after the freeze must be labelled as such rather than retroactively preregistered.
- The probability model needs independent task-pair signs and an appropriate null symmetry/exchangeability interpretation. A deliberately assembled set of 16 structures is not a probability sample of scientific domains; its p-value does not create population representativeness.

## 3. Sample-size arithmetic is correct but highly assumption-sensitive

Independent arithmetic reproduces the selected n=16 scenario's rejection probability, 0.811842, under discordance=0.75 and conditional TARGET win probability=0.90. Thus the main issue is **not an arithmetic error**. It is treating an optimistic hypothetical alternative as established or conservative power for this task population.

| Hypothetical discordance | TARGET win given discordance | Two-sided rejection probability at n=16 |
|---|---|---|
| 0.75 | 0.90 | 0.811842 |
| 0.50 | 0.90 | 0.538526 |
| 0.50 | 0.75 | 0.174483 |
| 0.25 | 0.75 | 0.030737 |

These are assumed-alternative rejection probabilities, **not observed power**, not posterior probabilities, and not power of C's full conjunction of significance, positive effect, zero observed harm and token ratio <=1.20. That conjunction can succeed less often. The power source counts either significant direction; final success additionally requires the TARGET-favouring direction.

The design explains its preferred scenario using B3's 3/4 discordances and 3/3 wins while saying n=4 is not a point estimate. That statement does not justify calling 0.75/0.90 conservative for new structures. A sensitivity table is more defensible than a certainty claim.

The fixed 8/8 strata need separate reasoning. For illustration only, if all eight unaffected pairs tie and the eight affected pairs are always discordant with independent TARGET win probability 0.90, TARGET-favouring significance occurs only at 8-0, with probability 0.430467. This is **not asserted to be the actual C distribution**; unaffected tasks could also differ between conditions. It shows why the pooled homogeneous-discordance model is not automatically a stratum-aware justification.

Alternative: interpret C as a resource-bounded, large-effect mechanism probe and retain uncertainty for smaller effects. Falsifier: if meaningful smaller effects remain compatible with the result, a non-significant result cannot establish absence/equivalence. Unresolved gate: completed frozen outcomes and a separately justified future sample-size design; do not increase C's quota now.

## 4. Zero observed harm is a sample statement

The design separately requires no TARGET stale events among eight affected tasks and no TARGET overreaction among eight unaffected tasks. Preserve these observed-count requirements. Do not turn them into a general safety guarantee.

For scale, zero events in eight independent identically distributed Bernoulli observations gives a one-sided exact 95% risk upper bound of approximately 0.312344. The assumptions do not automatically hold across engineered structures; this calculation only illustrates how weak a universal safety claim would be. Report denominators, failure status and both strata, including independent surviving-support and unrelated-change cases in any separately approved extension.

## 5. Failure-completeness remains an acceptance condition

Static inspection, not a reproduced failure:

- `run.py:29` records missing decisions as inadmissible but parses present JSON and invokes the scorer before appending the attempt receipt. Malformed JSON or an uncaught scorer exception can interrupt receipt materialization. The reported completed count is therefore not by itself an exhaustive attempted-call ledger.
- `analyze.py:28` unconditionally opens `decision.json` and the access log. A missing artifact can abort terminal validation rather than yield a complete failure-inclusive summary. This is fail-closed for that analysis, but does not supply the missing reliability denominator.
- Exit code and timeout flags are stored by the runner, but `summarize` determines correctness from the saved score and does not use them. A decision artifact with a nonzero process exit is therefore not automatically a fatal-failure zero in this implementation. Reconcile this with the frozen failure contract before claiming contract-complete acceptance; do not silently relabel or delete the attempt.
- The count check compares scalar completed/planned/approved counts; schedule checks validate blocks that are present. Explicit matching of all assigned attempt identities/blocks and original failure records is still needed to establish that no attempts disappeared.

No such C failure or data loss is alleged from the counts-only progress read. Do not repair the running code, rerun attempts, or replace the original endpoint under this audit. At termination, disclose any contract gap and withhold the affected claim if completeness cannot be demonstrated. Keep any later analysis repair/version separate with explicit admission.

## 6. Fair comparison and practical interpretation

Equal two-record allowance is valuable, but the intervention also changes which evidence is initially allocated. This tests the total allocation policy; it does not isolate persistent graph maintenance from a better first record. A later preplanned equal-first-record diagnostic is appropriate only if that mechanistic distinction matters, not as post-hoc conditioning on a mediator.

For a subsequent integrated comparison, use one strong evidence-aware result tree with equal raw spans, versions, candidates, observations, critique opportunities and common model/tools. Match construction/update/retrieval/handoff allowances as well as failures, actual tokens, wall-clock and parallel compute. A simpler version-aware log is optional, not a mandatory new factorial grid. No gold affected closure may be given only to TARGET.

The terminal analysis currently reports a paired mean and exact p, but no effect interval, stratum-specific uncertainty interval or explicit practical-equivalence test. Report that limitation instead of interpreting a small p as practically large, or a large p as equivalence. Any additional descriptive interval must retain the frozen primary and its independent n.

**Verdict:** defensible, narrowly scoped mechanism confirmation; efficacy, integrated-workflow validity, general safety and SOTA remain unestablished by this audit. Preserve the current run. Propose at most one next-information experiment only after its completed interpretation and separate authorization.
