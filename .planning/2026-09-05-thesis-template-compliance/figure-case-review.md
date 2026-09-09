# Figure sentence-case review

## Scope and ownership

- Date: 2026-09-05. Completed bounded display-only SVG typography lane under the active parent thesis-template plan.
- Write ownership: only three new SVG copies in `paper/figures/template-20260905/`, this review, and sibling `figure-case-checks.json`.
- All three original SVGs were read in full before creation. Originals, QMD, Typst, manifests, runtime, research data and parent planning files are not edited by this lane.
- `planning-with-files` guidance is applied through the existing parent plan and this lane-local progress record; no replacement plan or extra planning files are created.
- Prior memory is `near_match_only` for typography and supplies no casing authority. The live user brief and current SVG text define the exact substitutions.

## Lane plan and progress

| Step | Status |
|---|---|
| Read originals and inspect uppercase text | completed |
| Create byte-preserving display copies | completed |
| Apply two additional root-approved prose edits | completed |
| Verify XML, text, geometry and hashes | completed |
| Return source-only QA and parent handoff | completed |

## Declared substitutions

Exactly six case-only substitutions, one occurrence each: the four original heading/subtitle changes plus two explicitly approved figure 2 prose changes. No wording is added or removed.

| Figure | Source/display line | Original display text | Replacement display text |
|---|---|---|---|
| `fig1-research-agent-architecture.svg` | 18 | `PROPOSED RESEARCH-AGENT ARCHITECTURE` | `Proposed research-agent architecture` |
| `fig2-stage0-measurement-isolation.svg` | 17 | `STAGE 0: TWO DISTINCT EVIDENCE PATHS` | `Stage 0: two distinct evidence paths` |
| `fig2-stage0-measurement-isolation.svg` | 42 | `Untrusted; NO gold / oracle` | `Untrusted; no gold / oracle` |
| `fig2-stage0-measurement-isolation.svg` | 43 | `NO network access` | `No network access` |
| `fig3-evidence-dependency-contract.svg` | 24 | `TYPED EVIDENCE DEPENDENCY GRAPH` | `Typed evidence dependency graph` |
| `fig3-evidence-dependency-contract.svg` | 25 | `PROPOSED CONTRACT` | `Proposed contract` |

The em dash and following subtitle text in figure 3 are preserved. Headings/subtitle emphasis and both `NO` tokens are prose, not status identifiers. The additional root approval supersedes the provisional decision to retain `NO`.

## QA result

**PASS: source-only SVG typography.**

- Three originals and three display copies pass Python XML parsing and independent `xmllint --nonet --noout` validation.
- Every display file exactly equals its original with only its declared substitutions; reversing the six substitutions restores the original bytes exactly.
- All three original SHA-256 hashes remain identical to the initial full-read baselines, including the final post-validation recheck.
- All 199 elements retain their order, topology and attributes: coordinates, sizes, IDs, paths, relations, markers and inline styles are identical. Embedded CSS, accessible title/description text and whitespace are identical.
- Full lowercased XML text, every lowercased display text node, all numbers and protected technical identifiers are identical. `PASS`, `STALE`, `IDs`, `REPL`, `TUI`, `JSON` and `KST` remain unchanged wherever present; absent codes are not introduced.
- Exactly six lines/text nodes differ across the copies, comprising 105 ASCII uppercase-to-lowercase byte changes. File sizes are unchanged: 5,251 / 4,067 / 5,800 bytes.
- No visual or full-thesis compliance claim: changed letter case can change glyph extents despite unchanged authored geometry. The parent owns rendered-page inspection.

## Artifact hashes

Originals: `paper/figures/current-evidence-20260905/`. Display copies: `paper/figures/template-20260905/`. Each row uses the same basename in both directories.

| Figure | Original SHA-256, before = after | Display SHA-256 |
|---|---|---|
| `fig1-research-agent-architecture.svg` | `11509f8d309c4cbb3b8409f7ad7c7fac1d93727bb75ec3fb1aec49dc39593cff` | `a5b6490ff6a156bf85da915896b97ce202824f6d518a5e9c9358ca90e67d6f2d` |
| `fig2-stage0-measurement-isolation.svg` | `7c30090936f91165ff5d0716249f9bbe6900a8389979f84b56b8dff0bea01bcc` | `56709ba4633669c8c239fc8761ffa5a7b22cce535686385e28489744698182fd` |
| `fig3-evidence-dependency-contract.svg` | `7b25d44c59499abd981c129beb710e3c43ae00270ecd979196adb6a87dbf99d8` | `4cdda40253c9e5b46baf96cab26da7205f8f34cb4f815622ffbc1f5c8d97047d` |

Machine-readable checks and exact unified diffs: `figure-case-checks.json`.
Receipt SHA-256: `aaee72a7fdacf33c4bd5d34eef4f4b46de7c2fcbf3818011c472da9556038771`.

## Inspection notes

- `docs/CODEX-NAVIGATION-GUIDE.md`, named in inherited instructions, is absent; no replacement file is created.
- Initial combined context reads were truncated. The three SVG reads were individually complete; missing instruction context was recovered with bounded reads.
- The initial four-substitution receipt was provisional. This six-substitution receipt supersedes it following explicit root approval of the two `NO` prose edits.

## Parent handoff

The source-typography lane is complete. The parent redirects the three QMD image references to the matching SVG basenames under `paper/figures/template-20260905/`, renders Quarto, and visually rechecks the three affected pages. This lane does not change QMD, render, generate raster images, run research/runtime, delegate, commit or perform external writes.
