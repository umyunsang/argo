# Native paper-pipeline contract

The paper service is a deterministic downstream view of validated research. It does not search literature, choose methods after seeing outcomes, invent rationale, or treat session prose as evidence.

## Pipeline

```text
append-only ResearchEvent store
  -> deterministic ContextGraphSnapshot
  -> closed-world PaperEvidenceSnapshot
  -> typed PaperIR
  -> grounding / decision / attribution / numeric / staleness audits
  -> deterministic TeX and bibliography renderer
  -> isolated compiler adapter
  -> immutable PaperBuildRecord and artifact manifest
```

## Canonical source evidence levels

`DISCOVERY_ONLY < ABSTRACT_VERIFIED < FULL_PAPER_READ < PRIMARY_SPEC_OR_CODE < REPRODUCED_EXPERIMENT`

Unknown levels fail closed. A Boolean `verified`, a citation ID, model-generated summary, compaction summary, branch summary, transcript message, or Continual Harness memory never establishes paper evidence.

- `DISCOVERY_ONLY` can open a search but cannot enter a release bibliography as claim support.
- `ABSTRACT_VERIFIED` supports only abstract-scoped claims.
- Detailed method or result claims require `FULL_PAPER_READ` plus retained source/report bytes, hashes, and a locator.
- Software/protocol facts require a pinned `PRIMARY_SPEC_OR_CODE` record.
- Local efficacy claims require `REPRODUCED_EXPERIMENT` under an exact protocol fingerprint.

## `PaperEvidenceSnapshot`

A closed-world snapshot binds:

- instance ID, graph revision/digest, event-root digest, and projection version;
- reviewed claim text/revision/hash, scope, counterevidence, and evidence edges;
- citation metadata, canonical source ID/version, retrieved bytes hash, locator/excerpt hash, reading receipt, license, and attribution;
- result fields extracted by JSON path from immutable run artifacts with units and rounding policy;
- preregistered DecisionRecords and proof they preceded outcome visibility;
- contribution identity derived from lineage: `INHERITED`, `RE_DERIVED`, `MODIFIED`, `ORIGINAL_ARGO`, or `EXTERNAL_ORACLE`.

A free-form node status never attests itself.

## `PaperIR`

PaperIR contains typed sections, paragraphs, claims, equations, tables, figures, and author interpretations. Factual units reference reviewed manuscript claim IDs. Empirical values are references to result fields, not copied numbers. Citation keys, TeX escaping, labels, bibliography, and rounding belong to the renderer.

Raw body TeX, raw `\cite`, arbitrary bibliography entries, and unanchored empirical numbers are rejected. Draft mode may expose unresolved claims clearly. Release mode requires reviewed text hashes and all gates.

## Immutable build record

Each build records paper/build IDs, mode, instance/session IDs, graph/event digests, all claim/decision/component/citation/result/figure/template hashes, upstream Prime SHA, ARGO commit, dirty-input digest, model/session trace references, compiler binary/version/arguments or container digest, `SOURCE_DATE_EPOCH`, build-log hash, audits, human release authority, and hashes of `.tex`, `.bib`, figures, and `.pdf`.

The user remains the thesis author. Model/session traces document the research instrument and do not replace authorship.

## Storage and runtime boundary

Canonical bundles live in the instance artifact store, not only in session artifacts. Session deletion, branch/fork operations, compaction, or Continual Harness refinement must not delete or rewrite a paper build.

The eventual native owner is a domain-neutral research package. The coding-agent adapter injects a small `PaperService`; thin Python skills call typed host requests. The TypeScript host performs evidence and release gates. TUI Markdown/Mermaid are preview surfaces only and never become TeX or figure authority.

A compiler is an explicit capability. Missing LaTeX/PDF tooling yields an unavailable/failed build, never silent success.

## Required test families

1. source/read-level and bytes/hash/locator negative fixtures;
2. cross-instance, stale-claim, post-outcome DecisionRecord, and protocol mismatch rejection;
3. contribution-tag wording and inherited-as-original rejection;
4. PaperIR raw-TeX/citation/number injection rejection;
5. deterministic TeX/Bib and safe isolated compiler fixtures;
6. compaction/resume/session-delete persistence;
7. engine-refine noninterference;
8. end-to-end claim/citation/result/attribution audit before human release.
