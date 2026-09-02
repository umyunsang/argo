# Study C RUNBOOK — execution-grounded closed-loop replication (not executed)

**Status:** design-only; blocked by resources, not by evidence.
**Decision:** `RD-2026-09-02-08A`. **Source:** `2602.15112` (`FULL_PAPER_READ`), locators `researchgym_execution_grading`, `researchgym_integrity_and_resources`.

## Why this study exists

Study A scores research designs without executing them. An execution-graded environment removes judge dependence by inheriting metrics from source papers, with provided baselines as lower bounds and author solutions as soft upper bounds. It therefore tests whether a design-quality advantage survives execution.

## Required resources

| Resource | Requirement | Current status |
|---|---|---|
| Accelerator | one GPU per task | absent locally |
| Wall clock | about 24 hours per task, per condition, per repeat | exceeds current ceiling |
| Isolation | one container per task with no network to grading state | not built |
| Task assets | source repositories, baselines, and grading scripts | not retrieved |
| Integrity | probes for grading-script edits, train/test leakage, hardcoded metrics | added to the evaluator gate this round |

## Execution steps once resources exist

1. Freeze the task list, conditions, budgets, and grading scripts, then hash them.
2. Build one container image per task; mount released assets read-only; keep grading state outside the agent workspace.
3. Run each condition with identical model, budget, and tool access; capture full trajectories.
4. Score with the inherited execution metrics only; record baseline and author-solution reference points.
5. Run integrity probes before accepting any score.
6. Report best-of-k and mean with dispersion across repeats; never report a single run as the effect.

## Stopping and falsification

Stop if integrity probes fire, if budgets diverge across conditions, or if the grading script is reachable from the agent workspace. A design-score advantage that does not appear here narrows Study A conclusions to planning artifacts.
