# Thesis contribution and attribution ledger

## Non-negotiable boundary

This ledger is an internal repository accounting artifact and is not a manuscript source. The public thesis presents a generic harnessed LLM-agent system grounded in published literature and executed experiments; it excludes product lineage, migration, internal oracle, branch, commit, and operational-control details.

Internal architecture work may carry one contribution tag for repository review:

| Tag | Meaning | Internal accounting rule |
|---|---|---|
| `INHERITED` | Present in the Prime Agent base before the ARGO branch. | Track the inherited base internally; the manuscript cites only public foundations needed for the generic method. |
| `RE_DERIVED` | Independently motivated from literature and revalidated under an ARGO protocol. | A public method claim requires prior work plus an executed, scoped experiment; internal derivation history is omitted. |
| `MODIFIED` | An inherited component whose contract or behavior ARGO changed. | Track the implementation delta internally; only the generic intervention and matched result may enter the manuscript. |
| `ORIGINAL_ARGO` | A new ARGO mechanism with no equivalent in the base. | Do not use this tag as manuscript authority; originality requires public prior-art review and executed ablations. |
| `EXTERNAL_ORACLE` | OpenResearch, DACON, or another external system supplies lifecycle or evaluation facts. | Keep external authority and scope explicit; internal lifecycle details remain outside the manuscript. |

## Initial component ledger

| Component | Initial tag | Required evidence before final wording |
|---|---|---|
| Persistent IPython REPL and programmatic context | `INHERITED` | Prime Agent paper, base source paths, frozen base SHA |
| Daemon, worker, detach/reattach, recovery | `INHERITED` | Base architecture and lifecycle tests |
| Recursive RLM subagents and agent messaging | `INHERITED` | RLM paper, Prime Agent paper, base tests |
| Continual Harness prompts/memories/skills/subagent specs | `INHERITED` | Continual Harness and Prime Agent papers, base source |
| ARGO research-object taxonomy and evidence graph | `RE_DERIVED` / `MODIFIED` candidate | Compare EviGraph, claim-aware observability, XScientist, and ScientistOne; isolate immutable answered-run, exact-contrast, and authority semantics; implement and test |
| Exact protocol fingerprint and comparability gate | `UNCLASSIFIED` candidate | Compare matched-budget and inaccessible-held-out protocols from Rethinking Harness Evaluation and HarnessOpt-Bench; formalize the residual; add cross-language and unmatched-comparison tests |
| OpenResearch receipt boundary | `MODIFIED` / integration | OpenResearch contract, capability boundary, identity tests |
| Research-refine versus engine-refine separation | `RE_DERIVED` / `MODIFIED` candidate | Compare RSEA, Evo-Bench, Regimes, and Autogenesis; implement disjoint scientific/engine state, matched-budget noninterference, rollback, and inaccessible held-out evaluation |
| Paper claim/citation/run lineage | `RE_DERIVED` / `MODIFIED` candidate | Compare EviGraph, claim locking/observability, XScientist, and ScientistOne; isolate retained-byte, exact-contrast, authority, and immutable-build semantics |
| ARGO TUI and CLI | `MODIFIED` | Native product diff and usability/recovery evaluation |

Tags are provisional until source archaeology and experiments confirm them. A new name or rewrite does not turn inherited work into an original contribution. Full-read prior work already makes aggregate typed-graph, portable research-artifact, claim-aware lineage, claim-typed writing/verification, evidence-before-prose, and versioned harness-promotion originality claims unavailable. Matched-budget counterevidence and inaccessible-held-out protocols make important evaluation constituents prior art and force the exact comparability gate to remain `UNCLASSIFIED`; they do not establish an equivalent invariant-key/per-arm-receipt/planned-contrast triple. In the dual-refinement row, the prior constituents justify only a `RE_DERIVED` / `MODIFIED` candidate classification; the exact cross-lineage noninterference residual remains `UNCLASSIFIED` until separately compared, implemented, and evaluated.

## Public-paper exclusion boundary

The public paper centers the necessity, literature-derived architecture, falsifiers, and executed evaluation of a generic harnessed LLM-agent system. It has no implementation/provenance section for product migration. Prime-to-ARGO lineage, repository archaeology, internal contracts, code commits, oracle records, OpenResearch internals, supervisor artifacts, and instance operations are excluded. Reproducibility may name only public foundations, public research engines, and the minimum condition settings needed to rerun an experiment.

## Claim record

Each manuscript claim must resolve to:

```text
claim_id
contribution_tag
claim_text
source_or_run_ids
source_read_level
code_commit
protocol_fingerprint
scope
counterevidence
review_status
```

A claim with `source_read_level=discovery_only` or `abstract_only` may motivate a question but cannot support detailed method or result wording.
