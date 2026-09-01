# Thesis contribution and attribution ledger

## Non-negotiable boundary

The thesis may present ARGO as one coherent harness design and explain every architectural choice from first principles. It may not present an inherited Prime Agent component as an original ARGO invention.

Every architecture, method, experiment, and result claim carries one contribution tag:

| Tag | Meaning | Permitted thesis wording |
|---|---|---|
| `INHERITED` | Present in the Prime Agent base before the ARGO branch. | “ARGO inherits/adopts … from Prime Agent.” Cite the Prime Agent paper and source revision. |
| `RE_DERIVED` | Independently motivated from literature and revalidated under an ARGO protocol. | “We re-derived and evaluated … for ARGO.” Cite both prior work and the ARGO experiment. |
| `MODIFIED` | An inherited component whose contract or behavior ARGO changed. | “We modify … by …” State the base behavior, diff, and matched evaluation. |
| `ORIGINAL_ARGO` | A new ARGO mechanism with no equivalent in the base. | “We introduce …” Bind the claim to design records, code commits, ablations, and evidence. |
| `EXTERNAL_ORACLE` | OpenResearch, DACON, or another external system supplies lifecycle or evaluation facts. | “The external system reports …” Never imply ARGO generated the fact. |

## Initial component ledger

| Component | Initial tag | Required evidence before final wording |
|---|---|---|
| Persistent IPython REPL and programmatic context | `INHERITED` | Prime Agent paper, base source paths, frozen base SHA |
| Daemon, worker, detach/reattach, recovery | `INHERITED` | Base architecture and lifecycle tests |
| Recursive RLM subagents and agent messaging | `INHERITED` | RLM paper, Prime Agent paper, base tests |
| Continual Harness prompts/memories/skills/subagent specs | `INHERITED` | Continual Harness and Prime Agent papers, base source |
| ARGO research-object taxonomy and evidence graph | `ORIGINAL_ARGO` candidate | Literature comparison, native implementation, adversarial graph tests |
| Exact protocol fingerprint and comparability gate | `ORIGINAL_ARGO` candidate | Formal contract, cross-language fixtures, unmatched-comparison tests |
| OpenResearch receipt boundary | `MODIFIED` / integration | OpenResearch contract, capability boundary, identity tests |
| Research-refine versus engine-refine separation | `ORIGINAL_ARGO` candidate | Held-out dual-refine protocol, noninterference tests, rollback evidence |
| Paper claim/citation/run lineage | `ORIGINAL_ARGO` candidate | Corpus contract, claim audit, generated manuscript parity |
| ARGO TUI and CLI | `MODIFIED` | Native product diff and usability/recovery evaluation |

Tags are provisional until source archaeology and experiments confirm them. A new name or rewrite does not turn inherited work into an original contribution.

## Design-paper narrative

The final paper should center the research problem, competing architectures, selected contracts, falsifiers, implementation, and evaluation. Migration details belong in the implementation/provenance section. The narrative can therefore read as a complete ARGO harness design paper without becoming a misleading clean-room origin story.

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
