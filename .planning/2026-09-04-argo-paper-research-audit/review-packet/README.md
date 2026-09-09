# ARGO Thesis Causal Realignment — Independent Review Packet

Created: 2026-09-04T15:43:42+09:00  
Status: **DRAFT FOR HUMAN REVIEW — NO EXPERIMENT OR SPEND AUTHORIZED**

## Binding research position

Under a fixed model, tool surface, corpus snapshot, and resource budget, test whether typed evidence-and-experiment
lineage (`G`), design competition with deterministic admission (`C`), and a bounded falsification/refinement loop (`F`)
improve validity, held-out scientific task outcome, reproducibility, and recovery in long-horizon autonomous R&D.

ARGO is a lineage-aware, evidence-grounded, recovery-capable closed-loop R&D harness. Persistent REPL, recursive agents,
semantic search, evidence graphs, and multi-agent review are prior substrate or prior art, not claimed inventions.

## Audit verdict

No current efficacy claim is admissible. Study A is an instrument study. T3 is one-task descriptive evidence. The full
T1-prime pilot/block is quarantined because evaluator crashes were scored one rather than zero; 42 of 48 current block
receipts are crashes. The synthetic fixture result remains retracted and its stale `supports` edge is disabled only in
the proposed overlay. The canonical graph and source receipts are unchanged.

## Deliverables

| # | path | purpose |
|---|---|---|
| 1 | `01-causal-design-decision-record.json` | six-field decision superseding S×R and B0/B1/B2 efficacy models |
| 2 | `02-treatment-manifest.json` | all eight G×C×F cells, fixed surfaces, and manipulation checks |
| 3 | `03-admissibility-corrections.json` | Study A, T3, T1-prime, and synthetic-fixture status overlay |
| 4 | `04-task-sampling-and-certification.md` | distinct-task sampling and Stage 0 evaluator plan |
| 4b | `04-task-sampling-manifest.json` | machine-readable four-domain split state; task IDs deliberately unfilled pending certification |
| 0 | `stage0-certification-spec.json` / `validate_stage0_spec.py` / `stage0-spec-validation-receipt.json` | 13-category, 45-fixture acceptance contract; spec PASS, runner NOT certified |
| 0a | `stage0-evaluator-semantics-receipt.json` / `validation/evaluator-semantics/` | evaluator failure rules: meaningful red 13, green 22+17+9; clean clone at `fbd20a779`, not full clean-environment |
| 0b | `stage0-identity-validator-receipt.json` / `stage0-legacy-identity-audit-receipt.json` | environment-seed/rollout/task identity; T3 117 outer/inner mismatches, T1 no seed/task proof; clean clone at `d89c93aee`, runner integration absent |
| 0c | `stage0-treatment-loader-receipt.json` / `validation/treatment-loader/` | 8 configs, fixed surface, -G/-C/-F, G-content and C-independence validators; clean clone at `3e1daf3e4`, actual runner not connected |
| 0d | `stage0-orphan-run-audit-receipt.json` / `validation/run-state/` | live/stalled/orphan/terminal classifier; current stale run remains `ORPHANED_NO_VERDICT`; clean clone at `d2d6b8f44` |
| 0e | `stage0-provenance-validator-receipt.json` / `stage0-legacy-provenance-audit-receipt.json` | full path/hash provenance validator; 0/120 T3 and 0/48 T1′ legacy receipts conform; clean clone at `7f8f1dd42` |
| 0f | `stage0-sab-dependency-inventory.json` / `validation/environment/` | exact environment parity validator + 38-task/26-package AST inventory; clean clone at `2031cb2b4`, lock/install/parity still false |
| 0g | `stage0-resource-ceiling-receipt.json` / `validation/resource-ceiling/` | pre-action token/tool/time/cost reservation; clean clone at `f8141d865`, actual runner integration and cap values pending |
| 0h | `stage0-scorer-boundary-receipt.json` / `stage0-isolation-capability-receipt.json` | blind payload + namespace/access-log policy; clean clone at `aae695d28`; current host has no usable Linux isolation runtime |
| 0i | `stage0-scorer-certification-receipt.json` / `stage0-synthetic-scorer-anchor-receipt.json` | 3-state anchors + floor/ceiling + blinded issue classifier; clean clone at `aa5f35ce5`, real four-task distribution pending |
| 10 | `10-protocol-fingerprint-schema.json` / `10-protocol-fingerprint-template.json` / `validate_protocol_fingerprint.py` | fail-closed canonical identity template; binding-valid but sealable=false |
| 11 | `11-design-choice-matrix.json` / `11-integrated-experiment-design.md` / `validate_design_synthesis.py` | 15 evidence-bound choices forming one complete G×C×F/L×P design; validator 6/6 mutations |
| R | `stage-r-retrieval-screening.md` | development-only retrieval-policy selection: none vs semantic-vector vs citation/entity graph |
| 5 | `05-preregistration-draft.md` | hypotheses, outcomes, estimands, analysis, retries, stopping, power, fingerprint fields |
| 6 | `06-recovery-fault-injection.md` | planning/execution/review interruption protocol |
| 7 | `07-context-graph-repair-overlay.json` | non-destructive causal authority overlay |
| 7b | `validate_context_overlay.py` | deterministic combined-view validator and eleven failing-first mutations |
| 7c | `context-graph-validation-receipt.json` | overlay validation receipt |
| 8 | `08-cost-projection.md` / `.json` | Stage 0/R/1/2 and contingency envelope; measured gaps remain TBD |
| 8b | `resource-anchor-manifest.json` | 53 resource-only receipts with path and byte hash |
| 9 | `09-nais-clean-room-lineage.md` | event-window build separation and provenance plan |
| L | `literature-anchor-map.md` | full-read locators, non-novelty boundaries, and missing-source blockers |
| P | `popper-full-read-receipt.json` / `popper-locators.json` / `popper-method-note.md` | POPPER primary-source archive, 9 verified spans, and F validity boundary |
| Ps | `sources/popper-2502.09858/` | arXiv source archive and extracted TeX bound by the recursive packet manifest |
| RA | `researchagent-full-read-receipt.json` / `researchagent-locators.json` / `researchagent-method-note.md` | ResearchAgent primary source, 10 spans, and C non-transfer boundary |
| RAs | `sources/researchagent-2404.07738/` | arXiv source archive and extracted TeX bound recursively |
| PQ | `paperqa2-full-read-receipt.json` / `paperqa2-locators.json` / `paperqa2-method-note.md` | PaperQA2 primary source, 12 spans, and Stage R metric/reproducibility boundary |
| PQs | `sources/paperqa2-2409.13740/` | arXiv source archive and extracted main/SI TeX bound recursively |
| OS | `openscholar-full-read-receipt.json` / `openscholar-locators.json` / `openscholar-method-note.md` | OpenScholar primary source, 11 spans, and Stage R corpus/factor/evaluator boundary |
| OSs | `sources/openscholar-2411.14199/` | arXiv source archive and extracted main/appendix TeX bound recursively |
| PR | `provenance-standards-read-receipt.json` / `provenance-standards-locators.json` / `provenance-standards-method-note.md` | W3C PROV official specs + RO-Crate paper, 13 spans, and G interoperability/non-efficacy boundary |
| PRs | `sources/provenance-standards/` | archived W3C HTML/text and RO-Crate PDF/text bound recursively |
| RE | `rebench-full-read-receipt.json` / `rebench-locators.json` / `rebench-method-note.md` | RE-Bench canonical report, 14 spans, and Stage 1 task/budget/transfer boundary |
| REs | `sources/rebench-2411.15114/` | arXiv source archive; locators bind current `report.tex`, not older `converted.tex` |

## Validator output

- combined base+overlay active view: **PASS**;
- active root reachability: **104/104**;
- exact authority chain `research_question -> hypothesis -> protocol -> run -> artifact -> result -> claim -> decision`: PASS;
- active scientific efficacy results: **0**; current result is explicitly `AUDIT_FINDING`;
- node kinds: **25**; used active relations: **17**, all declared;
- combined endpoint integrity, retraction propagation, source and H6/H7 authority path/hash/span binding,
  decision admission rule, ablation direction, lineage closure, vocabulary closure, stale-action checks: PASS;
- failing-first mutations caught with named reasons: **13/13**;
- validator sha256 `d61b6b88ce3c6af7b39117b0427e713330a04682f18cc4a94fa82273ad67890c`, command `/Library/Developer/CommandLineTools/usr/bin/python3 validate_context_overlay.py`, runtime 0.359027s, exit 0;
- canonical graph modified: **false**; clean-clone claim: **none**.

## Unresolved blockers

1. Stage 0 acceptance is specified as 13 categories and 49 fixtures. Evaluator-state passes from committed bytes at
   `fbd20a779`; the identity component passes from committed bytes at `d89c93aee` and exposes legacy pseudo-replication.
   Neither is integrated into a certified G×C×F runner/environment, and the remaining categories are unexecuted. **The full runner/scorer is not certified.**
2. Synthetic fatal/wrong/correct scorer anchors and the blinded issue classifier pass committed-byte tests, but no
   four-task development distribution or real task scorer has been certified.
3. Current task certification is inadmissible. The 38 candidate tasks span exactly four domains and their 26 external
   distribution candidates are inventoried, but exact Linux lock, installation, agent/scorer parity, and recertification
   remain false. At least 16 distinct certified tasks are still required.
4. Scorer payload and oracle-boundary validators pass committed-byte tests, but current Darwin host has no bwrap/strace
   and Docker server is unavailable. No Linux namespace or OS access log has executed, so condition blindness and oracle
   isolation remain uncertified.
5. Current B2 is a forced-recording stub, not a persistent graph/retrieval/recovery prototype. B2-G/B2-P/B2-R remain
   invalid and MUST_NOT_EXECUTE. The generic 8-cell config loader passes from committed bytes at `3e1daf3e4`, but no
   actual G×C×F runner is connected to it.
6. C1 independence and G0/G1 content-equivalence validators pass synthetic fixtures, but no real candidate/content
   receipt exists. They remain manipulation blockers.
7. No disjoint development-task power simulation exists for the 0.10 minimum practical effect.
8. Stage R task count, corpus/index/provider/query budget, and power/cost are not frozen.
9. Stage 0/R/1/2 costs and the 20% contingency cannot yet form a numeric human envelope. The historical $48.47 cap is
   not silently reused.
10. The minimum literature-anchor list is now primary-source read and locator-bound. This closes a sourcing gap only;
   it does not remove Stage 0, sampling, power, cost, treatment-loader, canonical-graph, or clean-environment blockers,
   and none of the sources proves local efficacy.
11. The latest experiment-run attempt is deterministically classified `ORPHANED_NO_VERDICT` from dead PID and empty log.
   The classifier passes committed-byte tests at `d2d6b8f44`, but registry/heartbeat integration is not yet wired; the
   orphan still supplies no experiment verdict.
12. Canonical graph still contains legacy incompatible statuses and `edge:744`; only this uncommitted overlay proposes
   correction.
13. Stage 2 is now separately factorized as L×P and H7 uses L1P1-L0P1, but capsule IDs/hashes,
    content-equivalence fixtures, schedule, power and cost remain PENDING; no recovery episode is authorized.
14. The event artifact does not exist and must be created during the official window under the clean-room plan.

## Proposed human approval gate

Request paid-experiment approval only when one review bundle proves all items below:

1. Stage 0 positive/negative fixtures pass in a clean environment, including outer/inner seed identity, zero scoring for
   evaluator and agent failures, OS-level oracle isolation, ceilings, condition blinding, provenance, and stale-run
   detection.
2. At least 16 distinct tasks across four domains are certified with scorer/agent dependency parity; four are sealed as
   development-only and 12–20 as hidden confirmation.
3. Every G×C×F cell has a treatment-loader receipt and exact manipulation checks with no undeclared surface difference;
   C1 candidate independence and G0/G1 accessible-content multiset equality are both proven.
4. Stage R freezes the development-only task set, corpus/index/query/provider/budget identities, runs the three policies,
   and selects one without confirmatory outcome visibility.
5. A disjoint-pilot clustered power simulation shows ≥80% power at +0.10 and outputs the selected task count.
6. A complete budget envelope covers Stage 0, Stage R, development, confirmation, recovery, and ≥20% contingency.
7. The preregistration, task split, environment, scorer, treatment manifest, schedule, analysis code, and stopping/retry
   authority have one canonical protocol fingerprint.
8. A clean-environment packet validator passes from committed bytes.

Human choice after those proofs:

- **A — FULL:** approve the eight-cell factorial and its exact total envelope.
- **B — FALLBACK:** approve FULL, -G, -C, -F, G0C0F0 only; claims are limited to removal impacts.
- **C — HOLD:** no paid confirmation.

Until then the automatic decision is **C — HOLD**.

## Packet identity

`packet-manifest.json` binds every packet source except its own validation receipt. Hash dependencies are acyclic:
protocol template binds the graph overlay, while the overlay references the template path/status without hashing it; a
mutual hash cycle is forbidden. The 53-receipt resource manifest is
`resource-anchor-manifest.json`, SHA-256 `df749a08c67deea582399be79023ef35b392167b70968fbaf6394b2519502e13`. `review-packet-validation-receipt.json` binds the packet manifest
and must be regenerated after every change.

## Preservation statement

This packet was added without modifying source receipts, existing experiment outputs, the canonical context graph, or
native runtime code. No model episode, OpenResearch run, benchmark block, publication, commit, push, or spend occurred.
