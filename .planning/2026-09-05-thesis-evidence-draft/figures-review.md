# Figure worker review — 2026-09-05 KST

## Ownership and bounded plan

- Own only this file and `paper/manuscript/figures/current-evidence-20260905/`.
- Manuscript, shared plan files, runtime, experiments, and other workers' files remain untouched.
- Plan: verify primary IEEE guidance and current evidence; draw three editable monochrome schematics; render PDF/600 dpi PNG; inspect visual and font bounds; deliver captions and evidence limits.
- Status: completed — primary guidance and current evidence checked; all three SVG/PDF/600 dpi PNG sets rendered and visually reviewed; captions and handoff ready.
- Planning-with-files guidance loaded. This worker keeps its plan/findings/progress here rather than modifying root-owned planning files.

## Initial findings

- Read root `AGENTS.md`, `docs/argo/agent-brief.md`, and migration state. Native ARGO construction remains paused; diagrams are research proposals, not an implementation claim.
- No nested AGENTS.md found under the owned figure tree or planning tree. `docs/CODEX-NAVIGATION-GUIDE.md` is absent.
- Local clock confirms 2026-09-05 KST. Relevant memory was navigation only; current authority files and receipts determine figure claims.
- Existing tools: librsvg (`rsvg-convert`), Poppler (`pdfinfo`, `pdffonts`, `pdftoppm`), Pillow and PyMuPDF. No installation needed.
- Root clarified typography: at 160 mm final width, all ordinary labels must be approximately 9–10 pt, not 6 pt. Use 20–22 SVG units with a 1000-unit-wide viewBox.
- Mandatory `web.run` searches and direct official-page opens returned empty payloads. Independently fetch the official page text through available HTTP tooling; do not claim search-result verification.

## Primary guidance

Official IEEE Author Center file-formatting, resolution/size, accessibility guidance, and the editorial style manual were retrieved directly. Exact URLs, applicability limits, and Korean captions are recorded in `paper/manuscript/figures/current-evidence-20260905/README.md`. The source manual and extracted text are archived under its `guidance/` folder. This is a thesis adaptation, not formal IEEE certification. PNG is 600 dpi grayscale; prefer vector PDF rather than claiming to exceed IEEE's strict >600 dpi black-and-white raster threshold.

## Progress

- Reserved ownership; inspected instructions, live authority, and toolchain. No nested delegation or model runs.
- Rendered and visually inspected all three PDF previews. Fixed an overlong line, a dotted-link/header collision, missing arrowheads caused by multi-subpath markers, and ambiguous support/handoff notation.
- All typography tightened to 9.071–9.978 pt at 160 mm, including headings. Native SVG text remains editable; PDF fonts are embedded.
- Fixture receipt confirms three repeated normal and three repeated corrupt checks per task. Changed “variants” to “checks”; 96 checks are not 96 distinct tasks, integrated-agent runs, or model calls.

## Final validation and handoff

- Validation timestamp: 2026-09-05 05:57 KST. All three PDF-derived previews were visually inspected after the final edits. No clipped labels, missing arrowheads, or ambiguous proposed-versus-completed status remained in this standalone review.
- Figure 1: `fig1-research-agent-architecture.pdf`, 160 × 136 mm; PNG 3780 × 3213 px.
- Figure 2: `fig2-stage0-measurement-isolation.pdf`, 160 × 132.8 mm; PNG 3780 × 3138 px.
- Figure 3: `fig3-evidence-dependency-contract.pdf`, 160 × 139.2 mm; PNG 3780 × 3289 px.
- Each basename also has an editable `.svg` (`width="160mm"`), a 600 dpi `.png`, and a 1000 px PDF-derived `-preview.png` in `paper/manuscript/figures/current-evidence-20260905/`.
- PDF fonts are embedded; measured sizes are 9.071 and 9.978 pt. Automated page/node text-bound checks report no violations, and PDFs contain no raster-image objects. Some Cairo glyph subsets use embedded Type 3 fonts; source text remains editable in SVG.
- Exact byte sizes, SHA-256 hashes, font inventories, pixel dimensions, and current receipt provenance are in `asset-validation.json`. Full Korean captions and four official guidance URLs are in `README.md`.
- Scope of PASS: standalone figure rendering, typography, geometry, and evidence-boundary review only. Root manuscript placement/page breaks, journal-specific acceptance, and formal IEEE certification are not covered. No manuscript or native runtime files were modified; no model experiments, dependency installs, external writes, or delegation occurred.

## Root integration correction

- Request: remove benchmarking vendor names from public figure text/captions and distinguish artifact rechecks from independent statistical evaluation.
- Status: completed at 2026-09-05 06:15 KST — all three SVG/PDF/600 dpi PNG/preview sets regenerated; final previews visually inspected and hashes refreshed.
- Figure 1 uses “Persistent execution substrate” / “지속 실행 기반 구조”; SVG accessibility text also uses generic terminology. Proposed/untested and no-current-runtime qualifications remain.
- Figure 2 uses “Separately rechecked” / “별도 재점검”; its caption explicitly excludes independent statistical evaluation. Scorer checks and the runtime probe remain separate, with no integrated efficacy claim.
- Figure 1 uses “Alternative candidates”, removes the unexplained substrate acronym, and states “Conceptual design; integrated efficacy not yet evaluated” under a PROPOSED heading.
- Figure 3 uses `requires_recheck` throughout the diagram, accessibility description, legend and README. Its subtitle is “PROPOSED CONTRACT — dependency tracking and re-evaluation”; source retraction prompts review rather than automatic truth falsification.
- Root integrates the 160 mm SVGs through Typst. Standalone embedded-font PDFs remain available. Captions, dimensions and asset filenames are unchanged except for the requested wording corrections.
- Final checks: all public SVG/PDF/README text is free of the excluded benchmarking names and unexplained acronym; 9.071–9.978 pt fonts remain embedded; no page/node text-bound violations. Duplicate graph labels are matched by text plus nearest baseline in the bounds check. All 12 asset hashes and the README hash were updated in `asset-validation.json`.
