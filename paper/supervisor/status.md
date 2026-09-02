# ARGO paper autonomous-research status

- **last_updated:** 2026-09-02T21:41:37+09:00
- **goal:** active — autonomously complete and improve the graduation paper with evidence-grounded claims and deterministic validation
- **model:** `openai-codex/gpt-5.6-sol`
- **current_phase:** round 8 design-competition integrated; claim locators now re-derivable from the repository; clean-clone validation node PASS; Study A still prelaunch-blocked
- **last_checkpoint:** `5527c7926` — round-8 sources, six-field decision records, Study C RUNBOOK, engine usage notes

## Completed in current phase

### Resume procedure (instruction #0004 §2)

- HEAD confirmed and continued on the canonical branch; no ancestor node edited.
- `paper/evidence-matrix.csv` was 0 bytes in the working tree and was restored from HEAD. Cause: the receipt had recorded CRLF working-tree bytes while git stores the LF-normalized blob, so the recorded digest could never be reproduced from the repository. The writer now emits LF, `.gitattributes` pins `eol=lf`, and the digest matches the committed blob.
- Validation run `3fe2958b-44b6-4760-89fb-f711440c2ae0` is **failed** (exit 1) at commit `b2070ed09`. Root cause was not the manuscript: the local pass depended on working-tree bytes absent from the repository — five round-4 reports were never committed and 25 of 74 claim locators pointed at source slices missing from both repo and worktree.
- Repair: 16 exact-version archives re-fetched, all **byte-identical** to recorded digests; 20 TeX slices re-extracted and one PDF-derived text reproduced (recipe recovered as `pdftotext -layout`); all locators verified by file digest, line slice, and excerpt digest; a global fail-closed locator gate was added and shown to fire on a deleted slice. Receipts: `paper/sources/legacy-source-restoration-receipt.json`, `paper/sources/global-locator-gate-failing-first.json`. Commit `c677aeb6e`, clean-clone run `67bec1bc-b8da-47a6-8f49-6a486799f844` **PASS**.

### Round 8 — design competition (instruction #0003 §3-3~§3-5)

- Four full reads with exact versions: `2403.14403v2`, `2310.11511v1`, `2405.14831v3`, `2602.15112v2`; 8 line-anchored locators; 8 evidence rows; graph now 170 nodes / 397 edges.
- Three six-field decision records (`RD-2026-09-02-08A/B/C`) recorded in the ledger and linked into the context graph as `decision:*` nodes with `informs_decision` edges from their reviewed sources.
- Study A inherits its 2x2 structure; changed elements: retrieval-decision quality added as a secondary endpoint, integrity probes added to the evaluator gate, and an ideation-versus-configuration attribution arm added to the pilot.
- Execution-graded replication deferred as Study C with resources and steps in `paper/research/study-c-runbook.md`.
- Engine usage verified and written to `paper/research/orx-usage.md`.
- Commit `5527c7926`; clean-clone run `7184ad85-57e3-4fa4-a12c-21a5b80513db` **PASS** with 82/82 locators re-derived.

- Root-agent adaptive round 5: five `FULL_PAPER_READ` design/evaluation records. Architecture round 6 adds six `FULL_PAPER_READ` harness/context anchors, including programmatic context management. Corpus: 43 full reads and 74 reviewed locators; round 7 adds routing, protocol, RAG, and agentic-stack evidence with 22 exact locators.
- Prospective experiment revised to provisional 2×2 structured-state × dynamic-retrieval Study A.
- Minimum executable unit proposed: 16-episode instrument pilot; no result claim.
- ResearchClawBench runner pinned at `5bc7963f82b8cc4f13ea27e7524709e0d6a12a96`; workspace projection and missing sandbox guarantee recorded as separate code locators.
- Public-paper hard exclusions applied; `paper.tex` hard-exclusion scan is zero.
- 30-minute heartbeat active: `28b18ed8-647f-4144-a92d-f6e39e3b9c85`.

## Literature-map progress (preliminary anchor count / target ≥3 FULL reads)

| Area | Preliminary FULL reads | Status / named gap |
|---|---:|---|
| 1. Harness functions | 12+ | anchor count passes; necessity/design split mapped, remaining approval and sandbox experiments open |
| 2. Memory functions | 6+ | anchor count passes; personalized memory remains thin |
| 3. Protocols | 5+ | academic anchor threshold passes; official MCP/A2A versions and human-factor evaluation remain |
| 4. Skills | 4+ | anchor count passes; normative constraints need focused support |
| 5. RAG engine | 4+ | academic anchor threshold passes; product backends and local corpus evaluation remain |
| 6. Agentic AI development stack | 5+ | method threshold passes; exact framework/product primary behavior remains follow-up |
| 7. Coding-agent harness architecture | 9+ | routing mechanism axis anchored; pi standalone source and two direct primary contrasts remain open |
| 8. Autonomous research engine functions | 8+ | anchor count passes; seven functional subtopics mapped, public-engine naming forbidden |
| 9. Provider and dynamic model routing | 5+ | academic threshold passes; H-E remains unexecuted and fixed model retained for Study A |

## Capability map and public-name gate

- capability map: `46/46` sub-capability rows drafted; current-cycle validation set selected, literature gaps remain.
- public-name source gate: added and passing with `0` current hits; synthetic sample detected all 7 forbidden classes.
- public-name PDF gate: implemented with pinned `pdftotext`; full 43-source deterministic two-build validation PASS, source/PDF token hits `0`.
- current-cycle targets: hidden-task sandbox, independent evaluator, observability, context graph, research procedures/norms/decision records, retrieval pipeline, source verification, claim–evidence ledger, preregistration/deterministic validation, iterative stopping.
- model routing: target capability, design-only in Study A (`R-ROUTING-DEFER`) to avoid a treatment confound.

## Next concrete actions

1. Build the hidden-task release sandbox and the integrity probes as failing-first fixtures, since both are now specified by `RD-2026-09-02-08C`.
2. Build the final Word thesis pipeline from the validated manuscript and visually inspect DOCX/PDF pagination, equations, references, and headings.
3. Run one residual literature cycle for personalized-memory/privacy and official product/provenance specifications; do not reopen closed routing/protocol/RAG academic streams without a named gap.
4. Design evaluator-owned hidden-task isolation, independent scoring calibration, and the separate fixed Study A runner without native runtime changes.
5. Execute only the 16-episode instrument pilot after all three prelaunch gates pass; report no effect before immutable run evidence exists.

## Blockers and questions

- **E5 launch:** blocking — hidden-task sandbox, independent scoring, and fixed Study A runner are not implemented.
- **research design:** preregistration-ready at `paper/research/research-design.md`; H-B direct comparator and H-E rationale are closed, while launch remains blocked by hidden-task isolation, independent scoring, and fixed runner.
- **plan deadline:** answered `2026-10-31`; schedule updated in research design.
- **Q-0001:** answered — department plan deadline `2026-10-31`; current semester assumption retained.
- **Q-0002:** answered — six non-executable capability groups remain design-only/follow-up; no new native runtime.
- **DeepVoice evidence:** forbidden by existing user instruction; no access or edit planned.
- No efficacy experiment is running; `Experimental Results` remains explicitly unexecuted.
