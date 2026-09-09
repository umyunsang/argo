# Independent two-column layout review

## Scope and status

- Reviewer owns only this file. No manuscript, scientific content, experiment, runtime, configuration, or Git writes; no nested agents or paid calls.
- Source and exact-PDF inspection complete. **Scoped layout QA PASS** for the identified 12-page candidate; final findings and limitations follow below.
- The root-owned task plan, findings, and progress were read. Reviewer-specific progress is kept here to preserve write ownership.
- Read the complete 32-line `paper/manuscript/thesis-current.typ` and all 289 lines of `paper/manuscript/thesis-ko.qmd` in bounded sections. Read project instructions, `docs/argo/agent-brief.md`, and `docs/argo/migration-state.json`; native construction remains paused. `docs/CODEX-NAVIGATION-GUIDE.md` is absent.
- Prior memory was used only as a navigation hint, not claim or layout authority. No historical scientific claims were reused.

## Baseline fingerprint

- Current QMD SHA-256 at inspection: `9fc5189ceaf2924a140219d040f0deb71683953a912fcc58d56807da617bc907`.
- Frozen single-column source at `paper/manuscript/versions/2026-09-05-current-evidence/source/thesis-ko.qmd` has the same SHA-256.
- Current Typst layout SHA-256 at inspection: `1d3d9a784a8637375485958ec94dec690f610a54bb750a2b5a02516e29aae92a`.
- Baseline inventory: Korean abstract, chapters I–V, 3 SVG figures, 7 tables, 1 numbered display equation, and bibliography. Figure document order is architecture, graph, measurement; SVG filename numbers are not the document numbering authority.

## Immediate constraints for root

1. **Keep all three figures full-width.** QMD lines 116, 126, 174 explicitly request 160 mm. Their natural sizes are 160 × 136 mm, 160 × 139.2 mm, and 160 × 132.8 mm. All use a 1000-unit viewBox and 20-unit base labels: about 9.07 pt at 160 mm. A hypothetical 76.5 mm column would reduce them to 4.34 pt. Shrinking these figures into a column is not acceptable; retain vector diagrams and distinctions among solid, dotted, dashed, and directional connections.
2. **Span prose-heavy tables rather than shrink text.** All seven tables contain interpretive text; six have three columns, and `tbl-domains` has four. Prioritize full-width `tbl-literature`, `tbl-hypotheses`, `tbl-analysis-status`, `tbl-measurement-results`, and `tbl-legacy-limits`. `tbl-scope` and `tbl-domains` still need a rendered check because their Korean headings and qualification text are long. Existing table text is 9 pt with 5 pt horizontal and 4 pt vertical cell insets; narrow equal-width columns would cause excessive wrapping.
3. **Do not mistake `width: 100%` for page-spanning behavior.** The existing figure and table show rules use `block(width: 100%, breakable: false)`; their width depends on the containing layout. Verify that the selected two-column placement actually spans the page, not merely one column. Keep each complete diagram/table attached to its complete caption. Large unbreakable objects can create vacant columns or near-empty pages.
4. **Keep the estimand legible and mathematically identical.** QMD lines 186–189 contain nested expectations, conditional bars, braces, and an equation number. It is a likely narrow-column overflow point. Use full-width placement or a mathematically neutral line break; do not shrink away legibility, drop delimiters, or alter the expression, label, or explanatory paragraph.
5. **Preserve body and reference column flow.** The current A4 page has 25 mm horizontal margins, hence 160 mm usable width before adding a gutter. Body is 10.5 pt, with 0.85 em leading and 1 em paragraph indent. Check Korean/English mixed strings, numeric citations, heading orphans, and column order at real page scale. The raw Typst `#pagebreak()` before references must not reset bibliography to one column or produce an unintended blank page. Keep English bibliography language and 1.5 em hanging indent readable within the column.
6. **Preserve the scientific boundary text verbatim.** Long captions explicitly deny completed implementation/efficacy and distinguish the 96 scoring checks from integrated runs. Keep every caption sentence, the intermediate-manuscript subtitle, the stated measurement cutoff, hypotheses/alternative explanations, table qualifiers, and conclusion limitations. Layout changes must not imply additional experiments or results.
7. **Validate preservation separately from appearance.** Compare manuscript body, table cells, figure paths/captions, equation, citation keys and bibliography against the frozen source. Then independently inspect the exact rendered PDF for missing/duplicate text, wrong float numbering, broken cross-references, clipped content, font fallback, margin/gutter intrusion, and caption detachment. `ieee.csl` is citation styling, not evidence of IEEE submission compliance.

## Follow-up PDF QA plan

- Receive the exact candidate PDF path; record its hash, page count, and relevant source hashes before inspection.
- Extract text and positions locally; compare against the preserved single-column PDF/source without treating whitespace/reflow differences as scientific edits.
- Render every page locally and inspect all floats, the equation, abstract/title, section transitions, and reference pages; use higher-resolution views for dense diagrams/tables.
- Record page-specific findings and a scoped verdict here. PDF visual QA does not establish scientific validity, runtime acceptance, or publisher submission compliance.
- After the requested PDF QA and final report, stop. Until then, remain available for that exact-path follow-up; do not infer a candidate from files changing concurrently.

## Progress and limitations

- Source inspection and float inventory complete; source baseline matches the frozen single-column QMD.
- Some combined reads exceeded the tool response limit. Missing content was recovered using smaller bounded reads; no truncated excerpt was treated as a complete source read.
- Local `pdfinfo`, `pdftotext`, `pdftoppm`, and Quarto are available. A command-availability probe returned nonzero because standalone `typst`/`mutool` were not found; Poppler is sufficient for the planned PDF inspection.
- No PDF render or PDF acceptance claim has been made in this first-stage review.

## Exact final candidate review

- Candidate: `/Users/um-yunsang/argo-paper-orx/paper/manuscript/thesis-two-column-20260905.pdf`.
- SHA-256 before inspection: `ca4b43582463d3bdef5e6bd2b549d8a8ad5d14513c86dad1629064378602c125`.
- PDF metadata: 12 A4 pages, 595.276 × 841.89 pt, Typst 0.15.1, PDF 1.7, created 2026-09-05 08:30:29 KST. This is the final 12-page candidate, not the earlier 13-page render mentioned in progress notes.
- Current QMD hash: `d77305e8560499743cbd3b620f2129ac6c5a27368e760132a8ed4526e63b5475`.
- Requested backup: `paper/manuscript/versions/2026-09-05-two-column/before/thesis-ko.qmd`, hash `9fc5189ceaf2924a140219d040f0deb71683953a912fcc58d56807da617bc907`.
- Complete source diff has only three hunks: two-column metadata/stylesheet selection; aligned two-line equation with Big delimiters; removal of the old bibliography page break. No prose, table, figure/caption, or citation edits occur in that diff. Expected `diff` exit code 1 denotes these differences, not command failure.
- Independently rendered all pages with Poppler at 130 dpi to `/tmp/argo-layout-review.qcfoqj/`; text/position extraction reports zero words outside physical page bounds on all 12 pages. All four used fonts are embedded with Unicode mappings: AppleMyungjo, Arial Bold, Arial, NewCMMath. These automated checks supplement, not replace, visual inspection.

### Page-specific visual findings

| Page | Independently inspected finding |
|---|---|
| 1 | Full-width Korean/English title, author and intermediate-manuscript scope line are intact. Abstract and body use two columns with a clear gutter; introduction flows left-bottom to right-top without clipping. |
| 2 | Table 1 spans the text area, has its full caption above, and keeps all four body rows readable. Two-column text resumes underneath; the measurement cutoff and claim-boundary prose remain visible. |
| 3 | Table 2 spans the text area; all five named studies and the multi-line limitation caption fit without clipped cells. Body continues in left-to-right columns beneath the table; the lower-left subsection heading has following text rather than being stranded. |
| 4 | Figure 1 (architecture) remains full-width with readable English labels, distinct connection styles, complete bottom legend, and its complete Korean caption directly below. The paused/unevaluated qualifications remain visible. Two-column chapter III text continues below the float. |
| 5 | Figure 2 (typed dependency graph) spans the page text area. Both panels, directional edge labels, recheck/handoff legend, and the full caption are legible; the caption retains the distinction between recheck requests and falsity judgments. Two-column prose resumes beneath it. |
| 6 | Table 3 is full-width with its caption attached above; H1, H2, H3 and all alternative explanations are present and readable. Continued text and subsequent subsections follow two-column order without an empty column. |
| 7 | Figure 3 (measurement and isolation) is full-width. Both evidence paths, 16-task/96-check/48+48 labels, the integrated-tasks-zero qualification, and the entire four-line Korean caption remain readable and attached. Body columns resume below without overlap. |
| 8 | Table 4 spans the full text area; all four status rows and its two-line caption are intact. The estimand is visibly split across two aligned lines near the left-column bottom, with number (1) beside it; no visual overlap with the adjacent right column. Detailed bounds check follows below. |
| 9 | Tables 5 and 6 are intact with attached captions. Table 5 uses a compact four-column numeric grid centered in a spanning float (not stretched to the entire text width); its four domain rows and total preserve 16 tasks and 48/48 checks. Table 6 spans the text area with all six rows, including 15/15, Python 91, Debian 95, 96 checks, six checks, and integrated tasks zero. Two-column text resumes below without collision. |
| 10 | Table 7 spans the text area; its caption, header, and all four comparison rows are legible. Discussion, validity limitations, and Chapter V flow in two columns below. The conclusion heading has following paragraphs, and the final paragraph continues onto page 11 without visible clipping. |
| 11 | The conclusion continues at the left-column top, then the bibliography begins immediately below it, without an intervening forced page break. References [1]–[4] occupy the left column and [5]–[10] the right. Hanging indents, wrapped URLs/DOIs, and the gutter remain legible; [10] continues onto page 12. |
| 12 | Reference [10] continues at the left-column top, followed by [11]–[13]. All text remains within the same narrow column geometry; the unused right column is an unbalanced final bibliography tail, not a switch to full-width references or an inserted blank page. This is a non-blocking space-efficiency limitation, not missing content. |

### Equation and bibliography detail checks

- **Page 8, equation (1): PASS.** Independently inspected a 216-dpi PDF detail render. The two lines retain the outer expectation, the conditional A/C expectations, subtraction, delimiters, and final period; no terms disappear at the line break. The equation content spans x=108.862–251.138 pt and y=679.095–712.595 pt. Number (1) occupies x=276.354–289.134 pt, inside the left column; the right column begins at approximately 306.142 pt, leaving approximately 17 pt of gutter clearance after the number. No equation/number/body collision is visible.
- **Pages 11–12, bibliography: PASS.** The conclusion flows directly into the bibliography on page 11. Entry starts [1]–[10] occur once on page 11 and [11]–[13] once on page 12; [10] continues across the page boundary with its publisher/year/pages/DOI visible at page 12 top. References retain column-width geometry, hanging indents, and readable URL/DOI wrapping. No obsolete forced-break blank page remains.
- **Requested QMD comparison: PASS within the inspected scope.** The full three-hunk diff contains only format metadata, display-math alignment/delimiter sizing, and removal of the old bibliography pagebreak. After normalizing precisely those differences, the before/current QMD strings match. A preliminary normalization probe assumed two-space YAML indentation; correcting that checker to the observed four spaces resolves its false mismatch, without changing either source.
- **Candidate stability: PASS.** Final recheck retains PDF SHA-256 `ca4b43582463d3bdef5e6bd2b549d8a8ad5d14513c86dad1629064378602c125`, 12 pages, and QMD SHA-256 `d77305e8560499743cbd3b620f2129ac6c5a27368e760132a8ed4526e63b5475`.

### Final verdict and limits

- **PASS — independent visual/layout QA, all 12 pages.** No blocking clipping, overlap, detached caption, or missing diagram/table content was found. Figures 1–3 are on pages 4/5/7; tables 1–7 are on pages 2/3/6/8/9/9/10. Body and bibliography follow two-column geometry; all three diagrams and seven table floats span the columns, with Table 5's compact numeric grid centered rather than stretched.
- Non-blocking limitations: reference [10] crosses pages 11–12; page 12's bibliography tail uses only its left column. These do not imply missing text. No balancing change is requested or performed.
- This verdict is layout inspection plus the specified QMD comparison, not scientific revalidation, new research, IEEE submission compliance, or independent archive/rebuild certification. Root reports packaging/rebuild identity and archive CRC success separately; those checks are not represented as reviewer-executed evidence.
- Only this report was modified in the repository; rendering/extraction outputs are temporary files under `/tmp/argo-layout-review.qcfoqj/`. No manuscript edits, Git writes, paid calls, runtime changes, or nested agents were used. Review is complete; no further wait or work is queued.
