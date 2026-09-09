# Rendered manuscript inspection

## Scope

Inspect the final rendered pages, not just source or extracted text. Typography, line wrapping, figure/table placement, caption position, formula layout and footer are the acceptance surfaces. This review does not certify the research findings or resolve the template's contradictory length wording.

## Inspected pages

- Pages 1, 3 and 4 of the current `qa-final` render: centered bilingual title and Korean abstract, five-keyword line, Roman chapter labels, Arabic section labels, 21 pt body rhythm, readable superscript references and thin full-grid table 2. No clipping or overlap seen.
- Page 2 and page 7 were inspected after native in-flow placement was adopted. Table 1, dependency diagram, left-aligned captions and centered hyphenated footers are readable. Recheck their final raster equality before counting that earlier inspection toward final acceptance.
- Pages 5, 6, 8 and 9: no body clipping or overlaps; chapter III remains attached to its first section and paragraph. Architecture diagram is intact with legible paths, labels and legend, caption below, and actual body reference on page 6. Table 3 is intact with caption above. Page 5's lower whitespace is deliberate: the nonbreaking architecture moves to page 6's top.
- Pages 10–13: the measurement-isolation diagram is intact with readable labels and its caption below; the two-line estimand and right-side equation number are clear. Chapter IV and tables 4–7 remain within the page, with complete thin grids and captions above. Table 5 uses its natural centered width. No clipping, overlap or missing labels were observed; first-mention placement is independently checked from PDF coordinates.
- Pages 2 and 7 have now been directly re-inspected in `qa-final`, replacing the earlier provisional review. Page 14's limitations and validity-threat sections are also legible, with normal paragraph continuation and no overlap with the footer. All pre-bibliography pages 1–14 are now visually reviewed.
- Pages 15–17 after display-bibliography integration: conclusions, bilingual reference heading, all 13 entries, long contributor lists, italic venues and wrapped URLs are readable without clipping. Rendering is still provisional: the native engine re-capitalizes words after colons despite the display-copy casing, and the known hyphenated-initial defect remains visible. These typography issues are returned to the citation owner for a bounded correction before final acceptance.

## Final correction review

- Directly re-inspected final pages 15 and 16 after the last full Quarto render. The bibliography now preserves lowercase words after colons, proper names and acronyms, and the corrected `W.-T. Yih` initials. All entries on these pages remain readable without clipping, overlap or missing content.
- Final page rasters 1–14 and 17 are unchanged from their directly inspected predecessors. Only pages 15–16 changed and both were re-inspected. This completes visual inspection of all 17 final pages; page and PDF hashes are bound in `qa-final/visual-review-receipt.json`.
- Page 5's lower whitespace and page 17's short ending are intentional pagination, not lost text. The approximate characters-per-page rule and contradictory length limit remain unresolved institutional requirements.

## Paragraph-spacing correction, superseding the provisional 17-page edition

- Changed paragraph spacing from 0.5em to 1em after coordinate inspection found 15.75 pt body paragraph boundaries. This corrects the earlier incomplete within-paragraph-only check. The newly rendered PDF has 18 pages and SHA-256 `3bb74949f924423b26e5eba36cc66c4d1a431d48f035db5d6c4b118c39019397`.
- Directly inspected every new page 1–18. No text clipping, caption overlap, missing table cells, unreadable paths or footer collision was observed. Tables retain complete thin grids; superscripts, formula and reference URLs remain readable.
- Figure 3 now follows its first mention on page 10 and occupies the top of page 11. Table 4 follows its first mention on page 12 and starts at the top of page 13. These two next-page cases satisfy the template's explicit fallback placement rule; the other eight objects remain on their first-mention page. Page 10's lower blank area is the result of keeping the diagram and caption intact, not omitted content.
- Identified a final display-case refinement: the three uppercase diagram headings and one uppercase subtitle are headings, not status codes. Separate display-only SVG copies will use sentence case while preserving the originals, geometry and semantic wording. Recheck only the three changed page rasters and bind unchanged pages by hash afterward.

## Final 18-page edition

- Integrated exactly six case-only SVG substitutions: four headings and two emphatic NO prose tokens. Original SVGs, diagram geometry, technical identifiers, numbers and semantic wording are unchanged. Final PDF SHA-256 is `bf5389834b5b4c2f9e2036761b3c40da4396996b377881c99246de4107ee65f9`.
- Only page rasters 6, 7 and 11 changed relative to the directly inspected 18-page spacing-corrected PDF. All other 15 page rasters are byte-identical. Directly re-inspected these three final pages: headings fit, labels and paths remain legible, figure captions sit below the figures, and no overlap, clipping or footer collision appears.
- Figure 3 remains at the top of page 11; table 4's already inspected page 13 raster is unchanged. The two next-page placement cases remain valid. All 18 final pages are covered by direct inspection or exact raster identity to that inspection.
- The provisional 17-page review and package are historical only. Final delivery receipts must bind to this 18-page PDF and its current page images.
