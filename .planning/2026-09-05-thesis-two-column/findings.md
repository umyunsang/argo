# Findings

- Current source is the prior 15-page single-column edition. Memory serves only as navigation; current agent brief confirms native construction remains paused.
- Scope is layout-only. Existing unrelated research/experiment changes must remain untouched.
- Large monochrome figures were designed at 160 mm and cannot be shrunk into a narrow column without harming typography.
- Current QMD SHA256 matches the previously fully inspected source exactly (9fc5189ceaf2924a140219d040f0deb71683953a912fcc58d56807da617bc907). No intervening body edits.
- Official Typst columns/place documentation was fetched directly after web.run returned no body. Page-level columns plus parent-scoped floats supports full-width title/figures/tables. Docs retained locally.
- Chosen body: 10 pt, 0.55 em leading, 6 mm gutter; 160 mm text area preserves diagram design scale. Single-column dated files and old stylesheet are preserved.
- First rendered 13-page candidate shows the old mandatory bibliography page break leaving an almost empty conclusion page. Remove that layout-only break. Split the long estimand across two aligned math lines, without changing symbols or algebra, to avoid a gutter intrusion.
- Final 12-page edition has identical normalized scientific source and citation keys. Its extracted alphanumeric inventory matches the prior frozen PDF exactly after excluding page numbers; page bounds and embedded fonts pass. Root inspected every final page, including the two-line estimand.
- Portable editable ZIP contains exactly the guide plus seven source/assets files. CRC passes. A no-execute Quarto render from the extracted archive reproduces all 12 page sizes, word text/positions and 72-dpi raster digests exactly in the current toolchain. PDF byte hashes may differ due to creation timestamps.
- Before-layout QMD and style match the previous frozen edition byte-for-byte. The previous PDF remains in `versions/2026-09-05-current-evidence/`, not the manuscript root. Native ARGO runtime and research records are untouched.
- Independent exact-PDF review passes all 12 pages, the two-line equation, three diagrams, seven tables and references [1]–[13]. Non-blocking layout notes: reference [10] crosses the last page boundary and the final bibliography page uses the left column only. This review does not certify IEEE/university submission compliance.
