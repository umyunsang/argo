# Citation formatting slice

## Scope and active plan

Owned deliverables are `paper/manuscript/thesis-template.csl`, this review, and (explicitly authorized in the follow-up) `paper/manuscript/references-template.bib`, a display-only copy of the canonical bibliography. Only title values may differ in the display copy; every non-title byte and contributor remains unchanged. Root has reviewed the DISPLAY copy and retains manuscript, Typst, overall planning, integration, and delivery ownership. The latest follow-up removes automatic CSL title casing and reproduces the integrated English bibliography context in scratch; both bibliographies remain unchanged. Native ARGO construction remains paused. No canonical-bibliography/QMD/original-CSL changes, nested agents, research execution, npm commands, commits, or external writes are authorized.

| Slice phase | Status |
|---|---|
| Read template, guidance, and bibliography | complete |
| Implement isolated CSL | complete |
| Validate XML and disposable rendering | complete |
| Record limitations and hand off | complete |
| Audit 13 titles and display-copy map | complete |
| Probe harmless hyphen-initial formatting | complete |
| Validate display copy and native render | complete |
| Record follow-up verdict for root | complete |
| Correct approved Pineau title spacing | complete |
| Probe bibliography-only native name replacement | complete |
| Verify English-context exact-title rendering | complete |
| Record root's final integration confirmation | complete |

## Requirements and findings

- Template page 1 requires first-citation-order references, English entries for English-language sources, and bracketed reference numbers at the upper right of the cited statement.
- Rendered template page 3 shows initialized given names before surnames, comma-separated authors with final `and`, curly-quoted article titles, italic full venue titles, and ordinary baseline bibliography labels `[1]`, `[2]`.
- Journal example: authors, quoted title, italic journal, `Vol.19, No.6, pp.957-966, June 2014.` Conference example: authors, quoted title, italic proceedings, `Tokyo, Japan, pp. 2249-2252, 2008.` The space after conference `pp.` is visible in the rendered example.
- The explicit page-1 English sentence-case instruction takes precedence over page-3 title-case examples, as root reconfirmed. The reviewed DISPLAY bibliography now owns exact title capitalization; the CSL title node has no `text-case` attribute. Earlier Korean-context probes did not reproduce the manuscript's late `#set text(lang: "en")`: in that English context, native Typst applies `text-case="sentence"` by capitalizing five lowercase subtitle openings after colons. The paired English-context probe below reproduces and corrects this regression. Pandoc's separate BibLaTeX/citeproc path also normalizes unprotected titles and is not the native acceptance path. Proper names remain protected in the DISPLAY copy; canonical metadata and `citeproc: false` are preserved.
- Missing fields must disappear with their labels and separators; never infer venue, location, date precision, DOI, or publication status.
- Prior publication-identity memory is directly supported within this slice by the current bibliography: ResearchAgent is NAACL 2025 Long Papers with DOI `10.18653/v1/2025.naacl-long.342`; ScienceAgentBench is ICLR 2025 with no DOI supplied. This verifies preservation, not independent literature re-verification. Live `agent-brief.md` and migration construction fields confirm the paused boundary. `docs/CODEX-NAVIGATION-GUIDE.md` is absent.

## Implementation and expected output

- Authored a focused independent CSL after reading all 519 lines of `ieee.csl` and all 187 lines of the bibliography. Original IEEE formatting abbreviates venues, truncates long author lists, and prefers DOI over URL; the new style does none of these.
- In-text citation clusters render superscript `[1]`, `[2]` with superscript separators; repeated citations reuse their number. The entire citation layout, not just its digits, is superscript. Bibliography labels stay baseline and align continuation lines under entry text.
- Both bibliography and citation-cluster sorting use `citation-number`; no author/title sorting. The document controls first citation order and the position to the right of each statement. Root should use normal QMD citation clusters rather than adding a second manual superscript.
- Given names are initialized; all supplied authors and editors remain in the entry, with final `and`. English terms, curly quotation marks, full italic venue/series titles, literal `Vol.`/`No.`, expanded hyphenated page ranges, and full English month names are used. Titles preserve the exact reviewed DISPLAY spelling/case without an automatic casing transform; names and venues receive no case transformation. The one malformed native hyphen-initial output requires the narrowly scoped display rule documented below.
- Core order is authors, quoted title, italic venue, supplied event place, supplied editors/series/volume/number/publisher, pages, supplied date. Extra metadata is retained only when present. DOI and URL are both shown, even when the URL is the DOI resolver, to preserve every supplied identifier.
- Journal pages use `pp.957-966`; conference pages use `pp. 2249-2252`, matching the rendered sample's spacing. Sample metadata is used only in disposable formatting fixtures, never added to the thesis bibliography.
- Validation uses the installed Quarto, Pandoc, and Typst processors, not an assumed latest release or external literature. Two attempted documentation lookups returned no usable content; no outside claims or bibliography fields were imported.

## Source-data limitations

- Current bibliography contains 13 entries: 10 conference papers and 3 journal articles. Every entry has a title, authors, venue, year, and URL; 7 have DOI values. No entry supplies a conference or publisher location, so none may be inferred.
- `hu2025adas`, `chen2025scienceagentbench`, and `agarwal2021statistical` have no pages. Four entries lack volumes. The three journal entries supply volume/number/pages but no month/day. Conference dates have April for ResearchAgent and July for Hitchhiker's Guide; retain these supplied months rather than dropping precision to force year-only output.
- Pandoc's BibLaTeX reader maps Graph of Thoughts' `number = {16}` to `collection-number`, not `issue`. Both variables are rendered conditionally so `Vol.38, No.16` survives conversion. Series, publishers, and every supplied editor are retained too.
- Long complete author lists (up to 39 authors for AstaBench) and complete URLs may increase wrapping. Pagination, font size, line spacing, final citation placement, and the reference-heading layout remain root-owned.
- Native Typst renders the supplied hyphenated given name `Wen-tau Yih` as `W.-tau Yih`, whereas citeproc outputs `W. Yih`. Other demonstrated initials match the template. This is a processor-specific initialization limitation; no author spelling was rewritten to coerce it.

## Source preservation baseline

- `ieee.csl` SHA256: `b4c7619fc16c45a31e4cc3271eab94ffe83192d3b4c7fc729470a3b459448de3`.
- `references-current-evidence.bib` SHA256: `c3d605a73db6005d8b68abff44e742ca6e9e4af582b01c36aecb9edc3cc58cf4`.

## Progress and validation

- Read root instructions supplied with the task; no nested `AGENTS.md` appeared under the two owned directories. Read current agent brief and shared findings. Read full template text and visually inspected `template-page-03.png`.
- Initial shell discovery used zsh's special variable `path`, temporarily hiding `git` in that command only; corrected with a fresh shell and no configuration change.
- Combined guidance reads were truncated; subsequent reads were individually bounded and covered the full required inputs. Loaded `planning-with-files`; this delegate keeps its plan/findings/progress here rather than modifying root-owned shared files.
- Local tools: Quarto `1.10.18`, bundled Pandoc `3.10`, bundled Typst `0.15.1 (9dfd3a08)`, and system `xmllint`.
- XML well-formedness passed. A disposable three-page Quarto/Typst native rendering of all 13 entries passed compilation; deliberately non-bibliography-order citations retained numbers 1–13 and repeated/cluster citations retained their established numbers.
- The first Korean-document native render exposed that `default-locale="en-US"` alone does not prevent native Typst from rendering `and`, editor labels, and months in Korean. Fixed this in the CSL using language-independent English term overrides, including all 12 months and quote/page terms. A second native probe confirmed English output, punctuation inside quotes, preserved supplied months, and hyphenated page ranges.
- A sentence-case probe confirmed native Typst preserves supplied mixed-case titles and acronyms; it does not silently turn all bibliographic titles into sentence case. Pandoc citeproc HTML has reader-level normalization of unprotected title words, so this is a separate compatibility check, not evidence of native sentence-case compliance.
- Visually inspected all three disposable native PDF pages. Entire bracketed citation clusters are superscript at the statement's right; bibliography labels stay baseline; titles are quoted and full venues italic; English conjunctions/editor labels/months, supplied metadata, and complete author lists are present. No bibliography text or identifiers are visibly clipped. The default scratch font shows missing glyphs in its automatic Korean reference heading; root's font and custom centered bilingual heading remain outside this slice's visual verdict.
- The new CSL is ignored by the existing worktree-local `/paper/` exclusion in `.git/info/exclude`; it exists on disk for root integration. No ignore rule or Git staging was changed.
- Final assertions passed for all 13 references on native-PDF text and citeproc-HTML surfaces: 492 supplied-field/contributor checks, 16 superscript citeproc citation clusters, nonalphabetic first-citation order, repeated numbering, reordered clusters, page locators, full native source-title capitalization, italic HTML venues, and missing-field suppression. Case-insensitive metadata checks account for Pandoc's reader normalization; a separate case-sensitive check verifies every original title survives in native Typst output.
- Both original-file hashes still match the baseline. The final CSL is byte-identical to the scratch style used for rendering. This validates XML well-formedness and installed-processor acceptance, not an independently run CSL schema validator.

## Reproduction and evidence

Disposable scratch (outside the worktree): `/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-review.kLKkfv`.

- `smoke.qmd`, `smoke.pdf`, `smoke.typ`, `smoke.txt`, and `smoke-page-{1,2,3}.png`: all-source native Typst probe with Korean document language. Quarto used native bibliography processing (`citeproc: false`). All three PDF pages were visually inspected.
- `citeproc.html` and `references.json`: secondary Pandoc compatibility/field inspection, not the root's final rendering path.
- `template-samples.bib`, `template-samples.qmd`, `template-samples.pdf`, and `template-samples.html`: template-derived journal/conference samples plus a clearly synthetic title/year-only record. Both supplied examples reproduce author order, quoted title, italic venue, field order, date, and page-label spacing; the synthetic record creates no phantom venue, DOI, volume, number, pages, or URL. These records are never thesis bibliography additions.
- `validate-citations.py`: disposable standard-library assertions, not a new test framework or repo test suite.

Commands used, with `scratch` set to that directory and the workspace as the current directory:

```sh
xmllint --noout paper/manuscript/thesis-template.csl
quarto render "$scratch/smoke.qmd" --to typst --no-execute
quarto render "$scratch/template-samples.qmd" --to typst --no-execute
quarto pandoc "$scratch/smoke.qmd" --from=markdown --to=html --citeproc \
  --bibliography=paper/manuscript/references-current-evidence.bib \
  --csl=paper/manuscript/thesis-template.csl --output="$scratch/citeproc.html"
quarto pandoc "$scratch/references-current-evidence.bib" --from=biblatex \
  --to=csljson --output="$scratch/references.json"
pdftotext -layout "$scratch/smoke.pdf" "$scratch/smoke.txt"
python3 "$scratch/validate-citations.py"
shasum -a 256 paper/manuscript/ieee.csl paper/manuscript/references-current-evidence.bib
```

## Slice checklist

| Requirement | Status | Evidence or remaining owner |
|---|---|---|
| Numeric bibliography in first citation order | satisfied | Deliberately reordered 13-entry native and citeproc fixtures |
| Bracketed superscript in-text numbers | satisfied | Native visual inspection and 16 HTML superscript-cluster assertions |
| Citation immediately right of cited statement | satisfied in fixture | Final QMD placement remains root-owned |
| English entries for English sources | satisfied | Korean-document probe still prints English terms and supplied English metadata |
| Initials, final `and`, quoted titles, italic full venue | satisfied in scoped probe; root integration pending | Base native initialization is malformed for `Wen-tau Yih`; the tested bibliography-only rule below corrects its display without editing names |
| Journal Vol./No./pp./date and conference venue/place/pages/year | satisfied where supplied | Native sample fixtures plus actual-source assertions; absent location not applicable |
| Preserve available fields and publication identities | satisfied | All contributors, fields, identifiers, and supplied date precision retained; protected hashes unchanged |
| Explicit sentence-case titles without damaged proper names | satisfied in display-copy fixture; root reviewed | All 13 native-rendered titles match the exact display map below, including the approved Pineau spacing correction; canonical bibliography and QMD unchanged by delegate |
| Centered bilingual heading, reference font and final pagination | outside delegate scope | Root-owned Quarto/Typst layout and final-page visual check |

## Initial CSL-only verdict

PASS for the bounded CSL implementation and local rendering/field-preservation checks. CSL is ready for root integration using `csl: thesis-template.csl` from the manuscript directory, with normal QMD citations and no additional manual superscript. Sentence-case editorial normalization and the native hyphenated-name initialization limitation are explicitly unresolved; this is not an all-template or final-manuscript compliance claim. Only the two owned repository deliverables were created; no original bibliography/CSL, QMD, runtime, dependency, shared plan, or Git state was changed by this delegate. No research execution, npm commands, commits, or nested agents ran.

## Display-copy follow-up: findings

- User explicitly authorized a separate title-display bibliography after CSL integration. Re-read all 13 canonical entries; canonical bibliography and original CSL still match their protected baseline hashes. Current integrated CSL starts this follow-up at SHA256 `d73427fbd80a9dda1d637c64ca50ec1003dfa03a40927dc3a76488f9834f214c`.
- Local manuscript context confirms `Graph of Thoughts` as a named method; preserve it together with existing protected system/benchmark names. Normalize descriptive title wording, not venue names or author spellings. The initial copy retained the JMLR title's missing space; after reviewing the copy, root explicitly authorized adding that one space in the DISPLAY title only.
- Re-loaded `planning-with-files` and read root findings; keep follow-up plan/findings/progress in this owned review only. A combined review/findings read exceeded the tool output limit; individually bounded reads recovered the omitted section.
- Created the display copy through `apply_patch`: 13 titles audited, 10 title values changed and 3 unchanged. Only title values differ, including case-protection braces; a byte-exact masked comparison confirms all non-title content, field order, authors, and whitespace remain unchanged. Case-folded, brace-stripped title comparisons confirm no spelling, punctuation, wording, or spacing changes except the explicitly approved single space before the Pineau title's parenthesis.
- Applied the template's literal first-sentence-character instruction: descriptive text following colons and inside the JMLR parenthesis is lower-case, rather than importing title/subtitle capitalization from the example. Existing system/benchmark case protection remains; added protection for `Graph of Thoughts` and the named `NeurIPS 2019 Reproducibility Program`. `Automated design of agentic systems` is the descriptive paper title, not a renaming of its separately named Meta Agent Search algorithm.
- Both native display-copy renderings compiled successfully in disposable scratch `/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-display.nUcVTP`. The separate CSL-only `initialize-with-hyphen="false"` probe changes `W.-tau Yih` to `W. tau Yih`, not to correctly initialized components; it also changes `W.-L. Chiang` to `W. L. Chiang` and `N.-U. Nguyen` to `N. U. Nguyen`. This option changes punctuation but does not resolve the lowercase-component limitation. Rejected the candidate and left the integrated repository CSL unchanged. No given names, artificial initials, or processor packages were modified.
- The font-discovery wrapper printed to stderr, so its stdout-only filter returned status 1; no font installation or configuration change occurred. The scratch QMD attempts `reference-section-title: References`, but native Typst still generates its automatic Korean heading, with missing glyphs in the default scratch font. This setting did not resolve the heading. Root-owned Korean typography and the custom centered bilingual heading remain outside this title-display validation.
- Visually inspected all three native display-copy PDF pages. All 13 titles use the selected sentence case, retain protected names/acronyms, and remain quoted; full venues remain italic. Complete contributor lists, English terms, original identifiers and non-title metadata remain visible without clipping. Citation brackets remain superscript at the statement's right, with baseline bibliography labels. Entries may span pages; final manuscript pagination is not validated by this isolated smoke.

### Exact title map

These are the exact inner BibTeX `title` values; the field's outer braces are omitted. Additional braces only protect existing proper-name capitalization. The template text at lines 11–12 explicitly says to capitalize the first character of the English sentence and use lower case for the rest except proper names. Descriptive words after colons and inside the parenthesis are therefore lower case. No spelling, wording, punctuation, hyphenation, or apostrophe is changed after removing protection braces and ignoring letter case. The sole spacing change is the explicitly approved space in Pineau's `research (a report`.

| Citation key | Canonical title | DISPLAY title |
|---|---|---|
| `besta2024got` | `Graph of Thoughts: Solving Elaborate Problems with Large Language Models` | `{Graph of Thoughts}: solving elaborate problems with large language models` |
| `hu2025adas` | `Automated Design of Agentic Systems` | `Automated design of agentic systems` |
| `baek-etal-2025-researchagent` | `{ResearchAgent}: Iterative Research Idea Generation over Scientific Literature with Large Language Models` | `{ResearchAgent}: iterative research idea generation over scientific literature with large language models` |
| `chen2025scienceagentbench` | `{ScienceAgentBench}: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery` | `{ScienceAgentBench}: toward rigorous assessment of language agents for data-driven scientific discovery` |
| `pmlr-v267-huang25n` | `Automated Hypothesis Validation with Agentic Sequential Falsifications` | `Automated hypothesis validation with agentic sequential falsifications` |
| `Asai2026` | `Synthesizing scientific literature with retrieval-augmented language models` | `Synthesizing scientific literature with retrieval-augmented language models` |
| `agarwal2021statistical` | `Deep Reinforcement Learning at the Edge of the Statistical Precipice` | `Deep reinforcement learning at the edge of the statistical precipice` |
| `dror2018hitchhikers` | `The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing` | `The hitchhiker's guide to testing statistical significance in natural language processing` |
| `nosek2018preregistration` | `The preregistration revolution` | `The preregistration revolution` |
| `yang2024sweagent` | `{SWE-agent}: Agent-Computer Interfaces Enable Automated Software Engineering` | `{SWE-agent}: agent-computer interfaces enable automated software engineering` |
| `zheng2023judge` | `Judging {LLM-as-a-Judge} with {MT-Bench} and {Chatbot Arena}` | `Judging {LLM-as-a-Judge} with {MT-Bench} and {Chatbot Arena}` |
| `JMLR:v22:20-303` | `Improving Reproducibility in Machine Learning Research(A Report from the NeurIPS 2019 Reproducibility Program)` | `Improving reproducibility in machine learning research (a report from the {NeurIPS 2019 Reproducibility Program})` |
| `astabench2026` | `{AstaBench}: Rigorous Benchmarking of {AI} Agents with a Scientific Research Suite` | `{AstaBench}: rigorous benchmarking of {AI} agents with a scientific research suite` |

Ten title values changed; `Asai2026`, `nosek2018preregistration`, and `zheng2023judge` are unchanged. `Graph of Thoughts` is the named method, and `NeurIPS 2019 Reproducibility Program` is the named program already present in the canonical title. No acronym such as ADAS was inserted into a descriptive title. The JMLR source remains untouched; its DISPLAY title now includes the explicitly approved space before `(`. Venue capitalization is untouched because venue names are non-title source metadata.

### Prior DISPLAY-copy validation and protected hashes

These results and the CSL hash describe the earlier Korean-context DISPLAY/name probes, before root exposed the integrated English-context difference. They do not establish English-context compliance. The current correction, authoritative hashes, and reproduction commands are recorded in the English-context section below.

- PASS: exact title-masked byte comparison of both bibliography files, retaining field order, entry keys/types, author/editor strings, whitespace, and every non-title field. Masked non-title SHA256 is `896dda29d17eb8e1d58ef4de1b37096bac2efdfb70341d9525bdbdbc8893cb4c` for both files.
- PASS: Quarto Pandoc BibLaTeX-to-CSL-JSON comparison of all 13 entries confirms every parsed non-title field is identical; only `title` and its derived `title-short` are excluded from this semantic comparison. All 152 authors and 19 editors are preserved, in order.
- PASS: all 13 native-rendered titles match the exact display map case-sensitively after normalizing PDF line wrapping and removing BibTeX protection braces. All 13 complete native bibliography entries match the earlier canonical-bibliography smoke outside their quoted titles after normalizing PDF whitespace. No venue, DOI, URL, location, page range, contributor, or date is changed by the display copy.
- PASS: repeated citation returns `[1]`, a deliberately reversed cluster sorts to `[3], [5]`, and a supplied locator renders `[3, pp.857-858]`; visual inspection confirms whole-bracket superscripts. This is native Typst rendering with `citeproc: false`, not a citeproc-only approximation.
- PASS: both native Quarto/Typst smoke PDFs compile locally with execution disabled; the display fixture has three A4 pages, all visually inspected. Runtime: Quarto 1.10.18, Pandoc 3.10, Typst 0.15.1. No root manuscript or layout file was rendered or edited by this follow-up.
- BASE NATIVE LIMITATION: `Wen-tau Yih` renders as malformed `W.-tau Yih` without an override. The harmless CSL hyphen option probe does not resolve it and was rejected. The subsequently authorized bibliography-scoped Typst rule below successfully renders `W.-T. Yih` in scratch; root integration is still pending. The integrated CSL and every stored given-name spelling remain unchanged. This is not a claim of full native-initialization compliance.
- Source-data limitations recorded earlier remain unchanged. In particular, absent DOI, place, pages or volume are not inferred or fetched; canonical publication identities remain authoritative.

| Artifact | SHA256 | Follow-up result |
|---|---|---|
| `paper/manuscript/ieee.csl` | `b4c7619fc16c45a31e4cc3271eab94ffe83192d3b4c7fc729470a3b459448de3` | Protected original unchanged |
| `paper/manuscript/references-current-evidence.bib` | `c3d605a73db6005d8b68abff44e742ca6e9e4af582b01c36aecb9edc3cc58cf4` | Protected canonical source unchanged |
| `paper/manuscript/thesis-template.csl` | `d73427fbd80a9dda1d637c64ca50ec1003dfa03a40927dc3a76488f9834f214c` | Integrated CSL unchanged |
| `paper/manuscript/references-template.bib` | `e3bd421226b47de19df15e47142068f2683106155d1c9b7200e5dcd2ee9d567e` | DISPLAY copy after approved Pineau title space |

### Follow-up reproduction

Disposable evidence is under `/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-display.nUcVTP`: `native-display.qmd`, `native-display.typ`, `native-display.pdf`, `native-display.txt`, all three `native-page-*.png` renders, `canonical.json`, `display.json`, and `validate-display.py`. The rejected formatting probe is `without-hyphen.csl` with `hyphen-probe.qmd`/PDF/text. Scratch copies of both bibliographies and the integrated CSL are retained with the evidence; they do not replace repository authority.

```sh
scratch=/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-display.nUcVTP
quarto pandoc paper/manuscript/references-current-evidence.bib --from=biblatex --to=csljson --output="$scratch/canonical.json"
quarto pandoc paper/manuscript/references-template.bib --from=biblatex --to=csljson --output="$scratch/display.json"
quarto render "$scratch/native-display.qmd" --to typst --no-execute
quarto render "$scratch/hyphen-probe.qmd" --to typst --no-execute
pdftotext -layout "$scratch/native-display.pdf" "$scratch/native-display.txt"
pdftotext -layout "$scratch/hyphen-probe.pdf" "$scratch/hyphen-probe.txt"
python3 "$scratch/validate-display.py"
xmllint --noout paper/manuscript/thesis-template.csl
```

`validate-display.py` also compares native non-title output with the earlier canonical smoke in `/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-review.kLKkfv`. The then-current display bibliography and CSL were byte-identical to the copies used for that Korean-context render. This historical validator pins the prior CSL hash; use the new English-context validator for the current integrated CSL instead.

## Reviewed corrections and one bounded name probe

- Pineau DISPLAY title now reads `research (a report`. Exactly one ASCII space was added after the reviewed-copy baseline SHA256 `9cdeaffa6309d7035ebe2f437f3ce81633867c1de46cc71488cbe839bcdee0b5`. Reversing this one insertion reproduces that baseline hash exactly, proving all other display-copy bytes, including all proper-name protection, are unchanged. Canonical title remains `Research(A Report`.
- Re-rendered the native display fixture with execution disabled, extracted all 13 bibliography entries, and reran exact byte/parsed-field/title/proper-name/protected-hash checks. All pass. Visually inspected the corrected Pineau entry on `native-spacing-page-3.png`; the space is present and `NeurIPS 2019 Reproducibility Program` retains its spelling and case.
- One native Quarto/Typst probe compiled with the rule below in scratch-only `name-initials.typ`, included by `name-probe.qmd`. It changes the exact generated `W.-tau Yih` to `W.-T. Yih` only in bibliography entry `[3]` (`Asai2026`). The literal body-text control `Outside bibliography: W.-tau Yih.` remains unchanged. `W.-L. Chiang`, `N.-U. Nguyen`, all other contributor names, and all other text in all 13 bibliography entries remain unchanged after PDF whitespace normalization. Visually inspected entry `[3]` in `name-probe-page-2.png`.
- No bibliography, stored name or CSL was modified for the name probe. This is a narrow display override for one known malformed native output, not a general initialization algorithm. If root already has a `show bibliography` wrapper, place the inner regex rule inside that wrapper before returning/rendering the entry; do not make the regex rule global. Root-owned Typst has not been edited.

Tested minimal Typst rule:

```typst
#show bibliography: entry => {
  show regex("W\\.-tau Yih"): [W.-T. Yih]
  entry
}
```

The historical native name probe uses `citeproc: false`, the then-current integrated CSL, and the corrected display bibliography. Its reproduction commands below retain the earlier CSL hash expectation; the English-context probe later in this review revalidates the same name rule with the current CSL.

```sh
quarto render "$scratch/name-probe.qmd" --to typst --no-execute
pdftotext -layout "$scratch/name-probe.pdf" "$scratch/name-probe.txt"
python3 "$scratch/validate-name-probe.py"
```

`validate-name-probe.py` reruns the full display-preservation validator before checking the scoped replacement. The name probe was compiled once; only the verification script was corrected after its initial expectation wrongly targeted ResearchAgent `[4]` and missed a line-wrapped surname in Asai `[3]`. The corrected comparison normalizes PDF whitespace before applying the one allowed name replacement. A separate spacing assertion initially assumed `a report` stayed on one PDF line; it now permits the observed line break while still requiring whitespace before `(`. The first shell inspection used zsh's special `path` variable as a loop variable, temporarily hiding commands in that one process; reran read-only inspection with a normal loop variable in bash. No protected file changed in any failed check.

## Prior slice verdict (before English-context integration)

PASS for the reviewed 13-title DISPLAY copy including the approved Pineau title space, exact non-title/proper-name/protected-file preservation, and the one bibliography-scoped native display-name probe. The exact Typst rule is ready for root integration; without it, the native `W.-tau Yih` output remains malformed and is not compliant. Root still owns QMD bibliography switching, Typst rule integration, and final heading/font/page acceptance. Only `paper/manuscript/references-template.bib` and this review changed in the repository during these follow-ups; names, canonical bibliography, original/integrated CSL, root QMD/Typst, shared planning, runtime, dependencies, and Git staging/commits were not edited by this delegate. No external research, extra agents, publication, paid jobs, or npm commands ran. Stop condition reached: report these bounded results without another lane.

## English-context title correction

Root's integrated-PDF review exposed a missing context in the earlier smoke: the manuscript sets `#set text(lang: "en")` immediately before its native bibliography. The earlier PASS was limited to its Korean-context fixture and did not prove this English-context behavior.

- Removed only `text-case="sentence"` from the quoted title node in `thesis-template.csl`; updated the style's descriptive summary to state that the reviewed DISPLAY copy owns title case. XML comparison confirms no other formatting node or attribute changed. `xmllint --noout` passes.
- Compiled paired native Quarto/Typst fixtures with `citeproc: false`, execution disabled, the unchanged DISPLAY bibliography, and the same bibliography-scoped name rule. Both generated `.typ` files contain `#set text(lang: "en")` before the actual `#bibliography(...)` call; this is not a citeproc or static-text simulation.
- The pre-change CSL reproduces all five reported uppercase subtitle openings. The patched CSL preserves `AstaBench: rigorous`, `SWE-agent: agent-computer`, `ResearchAgent: iterative`, `Graph of Thoughts: solving`, and `ScienceAgentBench: toward` exactly. All 13 quoted native titles match the reviewed title map case-sensitively after normalizing PDF whitespace/soft hyphenation and removing BibTeX protection braces.
- All 13 complete native entries are identical between English-context before/after outputs outside their quoted titles after the same PDF normalization. First-citation numbering, repeated `[1]`, reordered `[3], [5]`, locator `[3, pp.857-858]`, venue/date/pages/identifier metadata, and italic venues are preserved.
- The same minimal bibliography-scoped rule renders `W.-T. Yih` exactly once, in `Asai2026`; malformed `W.-tau Yih` is absent from the bibliography and remains unchanged in the body-text control. `W.-L. Chiang` and `N.-U. Nguyen` are unchanged. Both stored bibliographies retain `Wen-tau Yih`; no author spelling is edited.
- Regenerated CSL-JSON from both live bibliographies and verified all parsed non-title fields, 152 authors and 19 editors in order. Exact title-masked byte equality and the 13-row canonical-to-DISPLAY map pass. Every DISPLAY byte, including all proper-name protection and the approved `research (a report` space, is unchanged from the reviewed corrected copy.
- Visually inspected all three patched scratch pages: superscript whole-bracket citations, lowercase subtitle openings, proper-name/acronym case, the scoped Yih correction, italic venues, and the Pineau space are present. This is citation-slice QA, not a new review of root's 17-page manuscript or its heading/layout compliance.

### Current protected hashes

| Artifact | SHA256 | English-context result |
|---|---|---|
| `paper/manuscript/ieee.csl` | `b4c7619fc16c45a31e4cc3271eab94ffe83192d3b4c7fc729470a3b459448de3` | Protected original unchanged |
| `paper/manuscript/references-current-evidence.bib` | `c3d605a73db6005d8b68abff44e742ca6e9e4af582b01c36aecb9edc3cc58cf4` | Protected canonical source unchanged |
| `paper/manuscript/references-template.bib` | `e3bd421226b47de19df15e47142068f2683106155d1c9b7200e5dcd2ee9d567e` | Reviewed corrected DISPLAY copy unchanged |
| `paper/manuscript/thesis-template.csl` | `31318b5528e82a9bdf4757adbb8ffd316df34fe807a03ed1609b63860bf679f2` | Automatic title casing removed; summary updated |

Both title-masked bibliography byte streams still hash to `896dda29d17eb8e1d58ef4de1b37096bac2efdfb70341d9525bdbdbc8893cb4c`. The pre-change style is retained as scratch `before.csl`, hash `d73427fbd80a9dda1d637c64ca50ec1003dfa03a40927dc3a76488f9834f214c`. Scratch `after.csl` and its bibliography are byte-identical to the current repository inputs.

### English-context reproduction

Evidence directory: `/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-display.nUcVTP/english-context`. It contains paired QMD/Typst/PDF/text outputs, `before.csl`, `after.csl`, unchanged `references-template.bib`, scratch-only `name-initials.typ`, regenerated `canonical.json`/`display.json`, `validate-english-context.py`, `validation.txt`, and three inspected `after-page-*.png` images. Each variant compiled successfully once.

```sh
scratch=/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/argo-citation-display.nUcVTP/english-context
xmllint --noout paper/manuscript/thesis-template.csl
quarto pandoc paper/manuscript/references-current-evidence.bib --from=biblatex --to=csljson --output="$scratch/canonical.json"
quarto pandoc paper/manuscript/references-template.bib --from=biblatex --to=csljson --output="$scratch/display.json"
quarto render "$scratch/before.qmd" --to typst --no-execute
quarto render "$scratch/after.qmd" --to typst --no-execute
pdftotext -layout "$scratch/before.pdf" "$scratch/before.txt"
pdftotext -layout "$scratch/after.pdf" "$scratch/after.txt"
python3 "$scratch/validate-english-context.py"
```

## Current slice verdict

PASS for the requested English-context title correction and bibliography-scoped name-rule combination in native Quarto/Typst. The quoted title node has no automatic `text-case` attribute; the reviewed DISPLAY bibliography owns exact sentence case and proper-name/acronym spelling. Current CSL SHA256 is `31318b5528e82a9bdf4757adbb8ffd316df34fe807a03ed1609b63860bf679f2`; unchanged corrected DISPLAY bibliography SHA256 is `e3bd421226b47de19df15e47142068f2683106155d1c9b7200e5dcd2ee9d567e`.

Root's final confirmation on September 5, 2026: the CSL and scoped name correction are integrated, the full 17-page Quarto render passes, all 13 actual PDF title letter cases match DISPLAY BibTeX, and `W.-T. Yih` is correct. Root directly inspected final reference pages 15–16; unchanged page 17 was already reviewed. These full-manuscript/render/visual results are explicitly root-reported, separate from this delegate's paired English-context smoke and exact preservation checks.

The English-context follow-up changes only `paper/manuscript/thesis-template.csl` and this review in the repository; canonical/DISPLAY bibliographies, original CSL, root QMD/Typst, shared planning, runtime, dependencies, and Git staging remain untouched by this delegate. After root's final confirmation, only this review was updated and the two current input hashes were read; no further experiments ran. No new research, agents, npm commands, commits, or additional lane. Citation slice complete; stop after this report.
