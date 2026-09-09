# Graduation thesis — editable source

This package contains the Quarto source of the one-column thesis edition dated 2026-09-05. It is a working manuscript, not a submitted or institution-approved final thesis.

## Render

Run from this directory:

```sh
quarto render thesis-ko.qmd --to typst --no-execute
```

The output is `thesis-boundary-20260905.pdf`. The verified local environment uses Quarto 1.10.18 and macOS fonts AppleMyungjo, Times New Roman, Arial and New Computer Modern Math. Fonts are embedded in the PDF but are not redistributed in this source package. Substituting fonts may change line breaks and pagination.

## Contents

- `thesis-ko.qmd`: manuscript and figure/table references.
- `thesis-template.typ`: one-column A4 layout, typography and caption rules.
- `thesis-publication.csl` and `references-template.bib`: citation formatting and scholarly bibliography.
- `figures/thesis-boundary-20260905/`: three editable monochrome vector diagrams.

The manuscript distinguishes literature-grounded proposals from completed measurement checks. Its evidence cutoff remains 2026-09-05 05:13:55 KST. Rendering does not run research experiments or create additional results.

## Submission caveats

The supplied writing guide specifies one column; this edition follows that layout. Its ambiguous length clause and HWP/Word submission requirement still need institutional confirmation. A rendered Quarto PDF and editable source package do not independently establish compliance with those submission requirements.
