# ARGO Thesis and NAIS Research Audit Plan

## Goal

Audit the live `argo-paper-root` autonomous-research session against the two supplied PDFs, the current NAIS hackathon requirements, the repository's ARGO authority boundary, and primary research literature; then issue a bounded, evidence-backed next instruction that yields a coherent research design and context graph without starting native ARGO construction.

## Scope and constraints

- Read current authority from `AGENTS.md`, `docs/argo/agent-brief.md`, and `docs/argo/migration-state.json`.
- Treat the graduation-plan and signed-application PDFs as user-source authority.
- Inspect live Prime Agent/session artifacts before trusting summaries.
- Verify SOTA/comparator claims from full papers or official primary sources, not search snippets.
- Keep LG Aimers read-only and do not start native ARGO implementation.
- Preserve all pre-existing untracked experiment artifacts.
- Any instruction sent to Prime Agent must require explicit evidence, falsifiable hypotheses, baselines, ablations, budgets, stopping rules, and context-graph lineage.

## Research questions

1. What thesis and competition commitments are fixed by the supplied PDFs and official NAIS page?
2. What has `argo-paper-root` actually completed, and what remains only planned or asserted?
3. Is the proposed synthesis of Pi/Prime Agent/OpenResearch/Exa/context graphs/loop and graph engineering a research contribution rather than a product feature list?
4. Which measurable hypotheses, tasks, baselines, ablations, and statistical analyses can isolate the contribution of each mechanism?
5. What is the smallest defensible prototype and experiment sequence permitted by the current migration gates?

## Phases

| Phase | Work | Status |
|---|---|---|
| 1 | Establish authority: repo rules, migration state, PDFs, competition page, live session inventory | complete |
| 2 | Audit current research artifacts and context graph for claims, gaps, and testability | complete |
| 3 | Deep-read primary literature and comparable agent/research-system evaluations | complete |
| 4 | Synthesize contribution model, hypotheses, experimental matrix, metrics, and gates | complete |
| 5 | Send bounded next instruction to `argo-paper-root` and verify receipt/progress | complete |
| 6 | Record verdict, evidence limits, and handoff | complete |

## Decision gates

- G1: User-source commitments and current session identity are confirmed.
- G2: Every central mechanism has a causal role, comparator, observable, and ablation.
- G3: Paper claims are supported by read primary sources; product inspirations remain uncited unless they have suitable published sources.
- G4: Prototype scope fits competition deliverable and repository authorization.
- G5: Prime Agent records the revised design and context-graph update with receipts.

## Errors encountered

| Error | Attempt | Resolution |
|---|---:|---|
| `prime-agent send --steer --json <agent> ...` rejected `--steer` despite help text | 1 | Treat as CLI option-order/parser issue; retry with target before option after recording the failure. |
| `prime-agent send <agent> --steer ...` also rejected `--steer`; installed parser does not implement the advertised flag | 2 | Inspected installed 0.9.1 parser; used `send <agent> --message ...`, which returned `Queued for argo-paper-root`. |
| Browser `open` and search calls returned empty output for the official competition page | 1 | Switch to direct official-page retrieval and/or visible browser inspection; record no claim from the empty responses. |
