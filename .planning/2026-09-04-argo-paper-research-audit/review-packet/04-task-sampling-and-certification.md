# 04 — Task Sampling, Split, and Evaluator-Certification Plan

Status: **DRAFT — no episode is authorized**  
Created: 2026-09-04T15:43:42+09:00

## Population and unit of inference

The target population is executable long-horizon scientific-computing tasks in a pinned benchmark release. The
**task** is the population inference unit. Seeds are repeated measurements nested within task; they are never counted
as independent tasks.

## Stage 0 certification

Pin the benchmark commit, environment image digest, Python/R/system dependency lock, scorer files, and dataset hashes.
For every candidate task, run deterministic positive and negative fixtures in both the scorer environment and the agent
workspace. The installed package/version sets must be byte-for-byte identical where task execution requires them.

A task is certified only if all checks pass:

1. unique task ID and task-content SHA-256;
2. declared output schema and scorer digest;
3. gold output passes and one deliberately corrupted output fails for the intended reason;
4. missing output, parse failure, evaluator crash, timeout, and nonzero exit all produce **score zero and
   `inadmissible_execution=true`**;
5. scorer output is deterministic across three clean reruns;
6. scorer executes outside the agent namespace with OS-level access logging and no oracle-readable path;
7. agent workspace and scorer environment expose the required package names and exact versions;
8. `environment_seed` reaches every controllable task/library RNG and each observed RNG seed equals it. If the model
   provider has no sampling-seed API, `model_sampling_seed=null` and every independent call uses a unique `rollout_id`;
   an unpropagated integer label is never called a seed;
9. hard token/tool/time/cost ceilings stop the task;
10. the condition-blind scorer receives no arm or factor identifiers;
11. the arm loader accepts exactly one registered cell config, recomputes its hash, and proves every non-target factor
    and accessible-content digest is equal; single-factor negative fixtures must fail for the named factor;
12. the receipt contains origin, model/provider revision, protocol fingerprint, harness commit, task hash, command,
    environment hash, transcript/artifact paths, actual timestamps, exit state, and measured usage;
13. stale-run detection compares registry state to worker PID/heartbeat/log progress and labels a dead worker with an
    unchanged registry entry `ORPHANED_NO_VERDICT`, never running or passed;
14. a known-valid reference output and deliberately degraded runnable baseline demonstrate scorer direction, nonzero
    progress, and headroom without exposing the hidden confirmation score;
15. technical issues are classified before condition outcomes as environment/infrastructure, agent-caused, or protocol
    defect, with exact retry and intention-to-run treatment.

The observed 2/38 record is located at
`paper/experiments/screening/t1prime/verifier-certification-receipt.json`, SHA-256 `54eed65e1f982a6faffb6bfe06d4bcd8698b652835379347f0cfd890e4706815`.
It reports two passes and 36 exclusions dominated by missing-package failures, but it lacks scorer/agent environment
parity. Therefore **2/38 is an observed file fact, not an admissible certification result or property of the tasks**.
It is superseded for admission purposes, not deleted.

## Sampling frame and split

1. Re-certify all deterministic tasks from the pinned release after using its documented environment setup.
2. Require at least **16 certified distinct tasks** across at least four scientific domains: four development/power
   tasks plus at least twelve confirmatory tasks. If fewer than 16 pass, block confirmation.
3. Select **exactly four domain strata** before any treatment outcome: rank domains by the number of certified tasks,
   descending, with normalized domain label as the deterministic tie-break. Freeze the selected four labels.
4. Within each selected domain, sort task IDs by
   `SHA256(release_commit || task_id || "ARGO-GCF-SPLIT-v1")`.
5. Assign exactly **one** first-ranked task from each of the four selected domains to development (four total). These
   tasks are permanently excluded from confirmation.
6. Assign the next 12–20 tasks from those same four domains to confirmation, cycling across domains to keep counts
   within one task when inventory permits. Freeze IDs and hashes before any confirmatory outcome is visible.
7. Keep the task packet hidden from treatment agents until its scheduled episode. The scorer and split steward remain
   condition blind.

## Seed and order schedule

Use at least three independent **rollout IDs** per task-cell. For controllable task/library randomness, generate sealed
`environment_seed` values and log every observed RNG seed. The current provider does not expose a sampling-seed option,
so `model_sampling_seed` remains null and model stochasticity is an unseeded nested repeat, not a seeded replicate.
Generate the counterbalanced eight-cell order from a separate sealed schedule seed.

## Rejection rules

- Fewer than 12 distinct confirmatory tasks: no population-level claim.
- Any environment mismatch, oracle access, missing provenance, or scorer nondeterminism: task blocked before spend.
- Any evaluator crash/timeout/nonzero exit during an episode: score zero in intention-to-run; run invalid for the
  protocol-complete sensitivity set.
- Repeated rollouts never replace missing tasks.
