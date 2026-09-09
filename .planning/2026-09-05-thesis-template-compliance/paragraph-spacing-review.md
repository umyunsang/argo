# Ordinary body paragraph baseline review

## Verdict and artifact binding

**PASS — ordinary body paragraph baselines only.** All 65 QMD body paragraphs uniquely match the final PDF. All 231 same-page within-paragraph differences and all 30 eligible same-page paragraph boundaries meet 21 pt within a 0.05 pt tolerance. No remaining ordinary-body paragraph-spacing defect was detected. This does not certify scientific content, object placement, or full thesis formatting.

- Review date: 2026-09-05. Local dependency: PyMuPDF 1.28.2.
- Final PDF: `paper/manuscript/thesis-template-20260905.pdf`, 18 pages.
- Final PDF SHA-256: `bf5389834b5b4c2f9e2036761b3c40da4396996b377881c99246de4107ee65f9`.
- QMD: `paper/manuscript/thesis-ko.qmd`; SHA-256: `00e9a699b15331e2e27fa22bab4977f7f81e827490d53c65c1adc8a35acf1005`.
- Checker SHA-256: `38c917833d21e5c781064a0e195be7b15a53845436e8b5f5c3a6395e90727aef`.
- Negative fixture: `before-paragraph-spacing/thesis-template-20260905.pdf` in this task folder, 17 pages; SHA-256: `ab143982c3e215902b8d0bafc9bc53f37d186878a12f659d8520007490485f12`.
- `paragraph-spacing-checks.json` is rebound to the root-confirmed final hash, not the earlier 18-page `3bb74949...` render. The current QMD contains the root's final image-target paths. Both fixtures match the same 65 ordinary paragraphs.

## Measurements

| PDF / interval | Measured | Passing | Failing | Minimum–maximum (pt) | Median (pt) |
|---|---:|---:|---:|---|---:|
| Final / within a paragraph | 231 | 231 | 0 | 20.999969–21.000061 | 21.00 |
| Final / ordinary paragraph boundary | 30 | 30 | 0 | 21.000000–21.000031 | 21.00 |
| Old / within a paragraph | 231 | 231 | 0 | 20.999969–21.000061 | 21.00 |
| Old / ordinary paragraph boundary | 32 | 0 | 32 | 15.750000–15.750031 | 15.75 |

The negative fixture fails on paragraph boundaries, not on within-paragraph spacing. For example, paragraph P002 ends on physical PDF page 2 at baseline 204.108642578125 pt. P003 begins at 219.858642578125 pt in the old PDF: **15.75 pt**. In the final PDF it begins at 225.108642578125 pt: **21 pt**. These are glyph-origin baseline differences, not bounding-box whitespace measurements. The JSON preserves unrounded coordinates, paragraph IDs, and their source line ranges.

## Independent method

1. Parse blank-separated ordinary QMD paragraphs beneath numbered chapter headings. Source structure, rather than PDF font size alone, distinguishes section headings and non-prose blocks.
2. Normalize each complete paragraph's Korean prose with NFKC and expand figure/table/equation cross-reference tokens to their rendered Korean labels. Ignore inline mathematics and citation markup for identity matching.
3. Extract PDF character origins with PyMuPDF `rawdict`. Select 10.5 pt prose glyphs, with a 0.05 pt size tolerance, from `AppleMyungjo` and `TimesNewRoman` font prefixes. Math-font and superscript glyphs are not baseline anchors; surrounding prose remains included.
4. Group co-baseline glyphs to 0.01 pt, then retain the median of their original, unrounded baseline origins. Match each entire normalized Korean paragraph uniquely in page/baseline/x reading order. Reject absent, ambiguous, overlapping, out-of-order, or partial-edge matches.
5. Measure every same-page baseline pair within each matched paragraph. Measure between paragraphs only when they are consecutive ordinary source blocks and consecutive PDF prose rows on the same page. There is **no gap-size prefilter** that could discard the old 15.75 pt defect.
6. Require complete source-paragraph coverage and nonempty within/between samples. Assert the requested PDF hashes and reject inputs that change during inspection. The combined control passes only when the positive PDF passes and the separate old fixture demonstrably fails at 15.75 pt.

This is a Korean-prose layout-identity checker, not a general Markdown parser or a text-content equality audit. It does not verify English/numeric content, inline-math placement, or rendered image contents. Unsupported block constructs and missing/ambiguous paragraph matches fail closed rather than silently reduce coverage.

## Exclusions and coverage

- Both PDFs cover **65/65 source paragraphs and 301 distinct ordinary-body baselines**. Final body coverage spans physical pages 1–16; old body coverage spans pages 1–15. Other pages contain no matched ordinary-body baselines and contribute no measurements.
- **47 non-body QMD blocks are explicitly excluded:** one YAML/front-matter block, one abstract heading, one abstract paragraph, one keyword block, five chapter headings, 19 section headings, one display equation, three figures with captions, seven tables, seven table captions, and one bibliography setup block. Generated bibliography is outside ordinary-body matching. Exclusion records include source line ranges in the JSON.
- There are **64 transitions between the 65 source paragraphs**. **30** transitions contain intervening headings, display mathematics, figures/captions or tables/captions and are excluded regardless of page position. This leaves **34 structurally adjacent ordinary paragraph boundaries**.
- Final PDF: **30 measured boundaries + 4 excluded paragraph-boundary page breaks = 34**. Old PDF: **32 measured boundaries + 2 excluded paragraph-boundary page breaks = 34**. Reflow moves two boundaries across pages; no eligible same-page boundary is lost from matching.
- Each PDF additionally has **5 page breaks inside paragraphs**, excluded explicitly. Accounting is `301 baselines - 65 paragraphs = 231 measured within-paragraph differences + 5 page breaks`.
- Thus the final PDF has **261 measured differences** and **9 explicit page-break exclusions** after structural exclusions. Headings and abstract are not blended into this body-only count or into the root's separate aggregate check.

## Reusable CLI and validation

Run from the repository root with the existing Python/PyMuPDF environment; no render or application runtime is started:

```bash
python3 .planning/2026-09-05-thesis-template-compliance/inspect_paragraph_spacing.py \
  --pdf paper/manuscript/thesis-template-20260905.pdf \
  --qmd paper/manuscript/thesis-ko.qmd \
  --output .planning/2026-09-05-thesis-template-compliance/paragraph-spacing-checks.json \
  --expect-pdf-sha256 bf5389834b5b4c2f9e2036761b3c40da4396996b377881c99246de4107ee65f9 \
  --negative-pdf .planning/2026-09-05-thesis-template-compliance/before-paragraph-spacing/thesis-template-20260905.pdf \
  --expect-negative-sha256 ab143982c3e215902b8d0bafc9bc53f37d186878a12f659d8520007490485f12
```

`--output -` (the default) emits JSON to stdout without creating a report file. PDF/QMD paths are required; hash guards and the negative fixture are optional for reuse but supplied for this acceptance run. Default expected spacing is twice the 10.5 pt body font, with configurable spacing/font/tolerance flags. Exit codes: **0** passes all requested checks, **1** indicates spacing/coverage/control failure, **2** indicates an input or hash error.

| Validation executed | Result |
|---|---|
| Python AST syntax parse | PASS |
| Final PDF plus preserved negative fixture, exact hashes supplied | Exit 0; final PASS, old FAIL, negative-control detection PASS |
| Preserved old PDF as the primary input | Exit 1; all 32 short paragraph boundaries detected; all 231 within-paragraph differences pass |
| Final PDF with the stale `3bb74949...` expected hash | Exit 2; hash mismatch; no JSON success report emitted |
| Final PDF with nonexistent body-font prefix | Exit 1; zero matched paragraphs and no samples; coverage fails rather than vacuously passing |
| Receipt hashes rechecked against current PDF, QMD and checker; coverage equations reconciled | PASS |

The JSON records every measurement and exclusion for both fixtures, the parsed source-block counts, the actual PDF/QMD/checker hashes and dependency version. Overall JSON PASS includes successful detection of the old PDF's expected failure; it does not mean the old PDF is compliant.

## Scope and completion

- Parent plan remains authoritative for task progress. This reviewer owns only the new checker, this review and `paragraph-spacing-checks.json`; existing files are not edited.
- Scope is ordinary body paragraph identity and baseline spacing only. No scientific review, runtime changes, source/style edits, rendering, object-placement review, publication or commits.
- Current QMD, live ARGO brief and migration-state were inspected. Earlier ARGO research memory is `near_match_only`, not evidence of spacing. The referenced `docs/CODEX-NAVIGATION-GUIDE.md` is absent; no substitute repository exploration was undertaken.

- Paragraph-baseline lane is complete. Root retains all-page visual review, SVG typography, object placement, source/style/render and delivery ownership. No additional investigation is needed for this lane.

## Inspection incident

- An initial shell loop used zsh's reserved `path` variable and shadowed `PATH` only within that command. Reissued read-only inspection in a fresh shell with no persistent environment changes. Large combined reads were then split into smaller ranges after tool truncation.
