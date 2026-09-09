# 06 — Recovery and Fault-Injection Protocol

Status: **DRAFT — zero-cost specification only**  
Updated: 2026-09-04T19:36:57+09:00

## Objective and causal model

Stage 2 tests whether typed, separated research/engine lineage reduces recovery loss under deterministic interruption
without a final-quality drop. To avoid attributing a joint lineage+checkpoint+metadata removal to lineage alone, use a
separate **2×2 L×P factorial**:

- `L=1`: typed research-state and engine-version lineage with immutable edges and cross-lineage mutation guards.
- `L=0`: flat append-only recovery log containing the identical accessible content and timestamps, but no typed edges,
  lineage queries, or cross-lineage gates.
- `P=1`: checkpoint bytes plus recovery metadata/index are available after restart.
- `P=0`: no checkpoint or recovery index is available; only normal task artifacts allowed equally across L.

| cell | semantics |
|---|---|
| L0P0 | no typed lineage, no checkpoint package |
| L1P0 | typed lineage records exist, no checkpoint package |
| L0P1 | content-equivalent flat log plus checkpoint/metadata package |
| L1P1 | typed separated lineage plus checkpoint/metadata package |

**H7 primary contrast:** `L1P1 - L0P1`. This isolates typed lineage while holding checkpoint/metadata availability
constant. **Combined-package secondary:** `L1P1 - L0P0`. P main effect and L×P interaction are exploratory unless added
to the confirmatory family before sealing. No lineage claim may use the combined-package contrast.

## Capsules

Use 6–10 pinned, reproducible capsules from a certified CORE-Bench subset or an equivalently executable suite. Every
capsule has an environment digest, task hash, deterministic checkpoint trigger, scorer digest, and clean replay script.
This sample is disjoint from Stage 1.

## Required fields before execution — currently BLOCKED

| field | required sealed value | current status |
|---|---|---|
| capsule IDs | 6–10 exact IDs | PENDING certification |
| capsule hashes | task/input/scorer/environment hashes per ID | PENDING |
| injection trigger | exact event/tool index and pre/post semantics for each of 3 points | PENDING |
| outer seeds | at least 3 per capsule-cell, with inner-seed equality | PENDING power simulation |
| paired order | sealed counterbalanced four-cell order per capsule | PENDING schedule seed |
| content equivalence | L0/L1 accessible-content multiset hash at each P level | PENDING fixture |
| estimator | paired capsule-level L effect at P1; capsule is the cluster | FIXED |
| uncertainty | capsule-cluster bootstrap 95% interval preserving seeds and injection points | FIXED |
| success endpoint | resume success and lost-work ratio reported separately | FIXED |
| noninferiority | final normalized task score margin -0.05 | FIXED |
| cost envelope | four cells × three points × seeds plus 20% contingency | PENDING human approval |

No recovery episode is admissible while any PENDING field remains.

## Injection points

1. **after planning:** decision and protocol recorded, before first execution;
2. **during execution:** after a preregistered tool-call index and before its completion record;
3. **during review/refinement:** after result receipt creation, before the next decision is committed.

A controller sends the same deterministic termination signal at the sealed trigger. Recovery starts in a new process
and empty model context from only the surface permitted by L and P.

## Outcomes

- resume success;
- lost-work ratio (unrecovered valid actions / valid actions before interruption);
- repeated-action rate;
- time-to-resume;
- final-quality delta;
- exact protocol/run/artifact digest agreement;
- cross-lineage mutation violations;
- human interventions.

Estimate cell outcomes within capsule and injection point. The H7 estimator is the paired `L1P1 - L0P1` difference,
then aggregated at the **capsule cluster**. Primary uncertainty is a capsule-cluster bootstrap 95% interval preserving
nested seeds and injection points. H7 succeeds only if the adjusted lost-work upper bound is below -0.10 and the
final-quality lower bound exceeds -0.05. Report resume success and lost work separately.

## Failing-first certification

Before any model episode, fixtures must prove that the controller fires at each exact point; cannot see condition;
refuses an unsealed checkpoint; detects stale/orphaned registry state; detects research refinement that mutates engine
lineage; detects engine refinement that rewrites prior research evidence; fails on a digest mismatch; and verifies
L0/L1 content equality. A loader must prove only L or P changes in each paired contrast. Every fixture asserts the exact
reason string.

## Stop and retry rules

Stop on missed trigger, oracle leak, environment drift, unbounded replay, content inequality, or cross-lineage mutation.
No automatic retry of agent-caused recovery failure. Infrastructure retry follows the blinded one-retry rule and keeps
the original attempt in reliability.

## Claim boundary

Stage 2 can estimate the typed-lineage effect only through `L1P1 - L0P1`. It does not identify which individual edge,
checkpoint field, or metadata item caused the effect. The event demonstration is qualitative and is not Stage 2 data.
