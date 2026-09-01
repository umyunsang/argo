# Systematic literature-review protocol for ARGO

## Objective

Build an auditable research corpus for every major harness design choice, then compare methods and experiments before selecting an ARGO contract. The review supports both implementation and the graduation thesis.

## Sources

1. alphaXiv full-text/semantic discovery through `orx discover`;
2. OpenAlex for cross-disciplinary scholarly coverage and citation context;
3. selected paper reads through `orx paper`;
4. official protocol/software specifications such as OpenResearch, MCP, ACP, OpenTelemetry, W3C PROV, and RO-Crate;
5. primary code repositories at pinned commits;
6. scoped MIT/Stanford course or lab materials as explanatory references, never as proof of ARGO performance.

## Evidence levels

`discovery_only < abstract_verified < full_paper_read < primary_spec_or_code < reproduced_experiment`

The corpus records source ID, title, authors, date, URL, retrieved artifact hash, claim excerpts, method, assumptions, evaluation, limitations, license, code, reading level, and ARGO design links.

## Search streams

| Stream | Questions | Required comparison output |
|---|---|---|
| Agent tools | How are tools described, selected, called, permissioned, and verified? | Typed function calling vs code/ReAct vs protocol-hosted tools; failure and injection model |
| Protocols | What should cross the model/runtime, client/daemon, tool, and lifecycle boundaries? | MCP, ACP, A2A, JSON-RPC, event protocols, capability negotiation |
| Agent–user | How are intent, uncertainty, progress, steering, abstention, and release authority represented? | Mixed initiative, calibrated trust, interaction cost, interruption and resume |
| Approval loops | Which actions require preview, confirmation, independent evidence, or human release? | Risk-tiered approval designs and authority non-bypass tests |
| Agent–agent | How do agents delegate, communicate, discover capabilities, share state, and resolve conflict? | Supervisor, peer, blackboard, market, debate, and recursive-session designs |
| Subagent orchestration | When should work fan out, fan in, persist, stop, or be deleted? | Topology, model routing, budget attribution, result identity, failure recovery |
| Evaluators/verifiers | How are open-ended outputs judged without self-grading or reward hacking? | Deterministic, process, model, human, and environment graders; independence and calibration |
| Compression/context | What is kept in active context, variables, summaries, retrieval, or external state? | Lossy compression, programmatic context, explicit state, retrieval, and resume fidelity |
| Observability/provenance | Which events, artifacts, causal links, costs, and decisions must be inspectable? | OpenTelemetry/W3C PROV/RO-Crate/event sourcing and claim-aware traces |
| Normative constraints | How are permissions, policies, constitutional rules, safety limits, and escalation enforced? | Prompt rules vs typed policy vs sandbox vs independent monitor |
| Decision heuristics | How do agents plan, search, reflect, backtrack, stop, and allocate information-gathering budget? | ReAct, ToT/GoT, Reflexion, LATS, Bayesian/value-of-information variants |
| Operational procedure skills | How are successful procedures extracted, parameterized, tested, versioned, and retired? | Code skills, natural-language procedures, workflows, and skill graphs |
| Episodic experience | How are trajectory successes/failures retained with provenance and scope? | Raw trajectories, reflections, case memory, experience banks |
| Personalized memory | What user-specific state is useful, consented, isolated, correctable, and forgettable? | Profile, preference, relationship, privacy, expiration, user control |
| Semantic knowledge | How are stable facts, ontologies, citations, and conflicts represented? | RAG/vector stores, knowledge graphs, provenance, temporal validity |
| Working-context memory | What state must remain immediately addressable during one task? | Token context, scratchpad, REPL variables, task state, artifact handles |
| Continual adaptation | When should memory, prompts, skills, roles, or tools change? | Trigger, candidate edit, held-out validation, promotion, rollback, contamination |
| Autonomous research | How are questions, hypotheses, protocols, experiments, evidence, and papers linked? | AI Scientist, Co-Scientist, SciAgents, EviGraph, EurekAgent, OpenResearch |

## Inclusion criteria

- primary or high-quality survey/specification;
- method is inspectable enough to derive a contract or experiment;
- evaluation reports task, baseline, metric, and limitations;
- relation to at least one ARGO design decision is explicit.

## Exclusion or downgrade

- uncited product marketing;
- discovery snippet used as detailed evidence;
- benchmark result without a comparable protocol;
- inaccessible method or unverifiable source;
- source whose license prevents required inspection or use;
- duplicate paper unless it adds a distinct method, evaluation, or negative result.

## Per-stream synthesis

Each stream produces:

1. problem and terminology;
2. ranked prior work;
3. method comparison matrix;
4. failure modes and counterevidence;
5. candidate ARGO contracts;
6. one or more falsifiable experiments;
7. implementation targets in the fork;
8. claim records for the paper.

The review is iterative. A stream is never marked complete because a search returned no results; it closes only with documented coverage and remaining uncertainty.
