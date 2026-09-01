# Prime Agent → ARGO migration plan

## Construction invariant

`Prime Agent base + validated migration slices = ARGO`

A big-bang rename would destroy the ability to attribute behavior and merge upstream fixes. Product naming follows behavior, not the other way around.

## Construction pause and resume gate

M1–M8 are design plans, not active implementation. Current authorized work is thesis research and test-instance validation only. Native construction resumes when all of the following are evidenced and the user explicitly approves:

1. a prospective test instance demonstrates material performance and credible high-score potential;
2. autonomous question/hypothesis/protocol/design/evidence/decision flow is stable under repeated runs;
3. context resume, duplicate avoidance, protocol comparability, scoped closure, and dual-refine boundaries pass their validation suite;
4. the main harness bottlenecks and proposed native fixes have immutable evidence;
5. the user issues a new construction-start instruction.

## M0 — lineage and evidence foundation (current)

- Preserve GitHub fork ancestry and sync the base to upstream v0.9.1.
- Isolate local test-instance data from the public engine repository.
- Preserve Python contract oracles in a private validation repository.
- Add ARGO agent context, migration state, literature map, and acceptance plan.

**Exit:** fork parent, upstream SHA, local root, and oracle SHA are independently verifiable; engine working tree is clean before the first native slice.

## M1 — native research event and identity contracts

- Add a domain-neutral TypeScript package for canonical JSON, content IDs, instance IDs, protocol fingerprints, and normalized research events.
- Add mutation/deletion/reorder negative fixtures and cross-instance isolation tests.
- Do not modify daemon protocol yet.

**Exit:** TypeScript output is byte-equivalent to approved language-neutral fixtures and introduces no Prime runtime behavior change.

## M2 — instance-scoped research state

- Bind one research instance to one session/artifact namespace.
- Add append-only event storage and deterministic graph projection under the existing session persistence owner.
- Keep raw prompts/tool payloads in native transcripts; tracked research events contain approved fields and hashes only.

**Exit:** fresh-process replay yields the same graph digest; stopped/frozen instances cannot launch work.

## M3 — context graph and design admission

- Add typed Objective→Gap→PriorWork→Mechanism→Hypothesis→Design→Experiment→Evidence→Result→Decision→Closure validation.
- Require a null, falsifier, alternatives, rationale, protocol identity, control, intervention, metrics, stop rule, resources, risks, and source evidence.
- Scope closures exactly and distinguish execution failure from scientific falsification.

**Exit:** adversarial fixtures fail closed and a fresh agent reconstructs the same active state.

## M4 — OpenResearch lifecycle boundary

- Start with a read-only receipt importer for run ID, immutable commit, fixed command/environment, stdout/artifact hashes, and status.
- Only after parity, add a capability-gated internal lifecycle module. Never create a second run registry.

**Exit:** unrelated, mutable, or incomparable run evidence cannot enter Result/Decision/Closure.

## M5 — design competition and research loop

- Add mechanism-distinct proposal, independent critique, selection, execution, evidence assimilation, and scoped next-design routing.
- Optimize expected information and validity, not just the task metric.

**Exit:** matched stock-versus-ARGO agent evals reduce correction latency, duplicate proposals, over-broad closures, and incomparable mixing without unacceptable completion/time/cost regressions.

## M6 — dual refine

- Research refine may change only the instance graph.
- Engine refine may propose prompts, memories, skills, roles, routing, or tools, but may not create scientific results or closures.
- Use different episodes for trigger and validation. Cross-instance/global promotion requires held-out evidence and human approval.

**Exit:** rollback works and held-out probes improve without instance contamination.

## M7 — evidence-grounded paper pipeline

- Maintain a paper corpus with source identifiers, retrieved bytes/report hashes, claim excerpts, license/attribution, and reading status.
- Generate manuscripts only from validated claim-evidence paths and immutable experiment receipts.
- Produce LaTeX/PDF plus a claim-citation and claim-result audit.

**Exit:** unsupported claims, discovery-only citations, mismatched numbers, and stale downstream sections fail the paper gate.

## M8 — ARGO product surface

- Rename CLI/package/TUI surfaces only after native research paths pass migration and compatibility tests.
- Keep explicit upstream attribution and MIT license.

**Exit:** installer, daemon attach/recovery, REPL, RLM, refine, research loop, and paper workflow work under ARGO names with migration documentation.

## M9 — thesis evaluation

Use LG Aimers as frozen historical evidence and DeepVoice as the prospective second instance. Compare stock Prime and ARGO on matched tasks. Report reliability, scientific validity, context resume consistency, duplicate avoidance, human interventions, latency, tokens, cost, and failures, not only final competition score.
