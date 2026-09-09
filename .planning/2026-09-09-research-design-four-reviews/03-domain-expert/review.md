# Reviewer 3 — domain expert

Verdict: **REVISE_BEFORE_LAUNCH**. The two-loop interpretation is technically sound. Five fixable proposal gaps remain. These are prospective design findings, not observed runtime defects or experimental failures.

Scope: frozen packet v1; technical accuracy, ML task validity and directly related methods. All 19 manifest hashes matched. No experiments or source edits were performed.

## D1 — HIGH: The retained roster does not consistently apply the stated IID source criterion

UCI describes pendigits as repeated samples from 44 writers, with an original 30-writer/14-writer distinction. Satimage consists of 3×3 neighborhoods from one small image area. One-per-dataset family grouping does not resolve dependence between rows within a task. A random fold can test interpolation among familiar writers or neighboring image patches; it does not establish unseen-writer or unseen-scene generalization.

This is a concrete unresolved inclusion decision under the proposal's own IID frame. A harness that exploits local source regularities can gain score without improving the intended independent-sample task. It does not by itself invalidate a deliberately conditional comparison on fixed rows.

**Minimum correction.** Before outcomes, explicitly adjudicate these two datasets. The simplest consistent option is exclusion and deterministic roster refreezing. Alternatively retain them as named within-source prediction tasks, retract the IID eligibility description, and avoid claims of new-subject/source generalization. Do not infer grouping from data_id alone.

**Cheap falsifier.** Metadata-only source/split check: identify whether OpenML task 32 preserves writer separation and whether task 2074 has recoverable spatial grouping. An overlapping writer/source assignment, or absent group identity under a claimed grouped split, falsifies the proposed eligibility claim without training a model.

**Uncertainty.** Exact OpenML row-to-source mapping and fold indices were not accessed. UCI satimage reports 6,435 instances while this roster reports 6,430, so exact version ancestry remains unresolved. No observed leakage rate or performance inflation is claimed.

Evidence:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 25–31: Excludes repeated-subject/sequential data; fixes row-based outer/inner splits.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/task-roster.json`, SHA-256 `e952968e594b2bd32ed10e6b8f9c3c0863f8e856490e41932fd333e3d388c691`, lines 339–381, 965–968: Retains pendigits and satimage; excludes MiceProtein for grouped provenance.
- [Primary source](https://archive.ics.uci.edu/dataset/81/pen+based+recognition+of+handwritten+digits): Dataset Information and file list; rendered lines 42–51 and 79–87. Primary collection description, no data/labels downloaded.
- [Primary source](https://archive.ics.uci.edu/dataset/146/statlog+landsat+satellite): Dataset Information; rendered lines 43–51. Primary collection description, no data/labels downloaded.

## D2 — HIGH: The 12-call development budget lacks a defined feedback unit and label-custody contract

The worker is given train/dev material and arbitrary Python, but the contract never says whether y_dev remains outside its environment. If y_dev is mounted, it can compute unlimited development scores without invoking the named scorer. Even with hidden labels, one script could submit a sweep or multiple prediction vectors unless one feedback event is defined.

The claimed equality of development opportunities can then measure invocation packaging rather than information used for model selection. The outer test may remain untouched, but the intended budgeted treatment comparison is no longer specified.

**Minimum correction.** Define one charged development event as feedback about one locked candidate prediction vector on the fixed dev set. Keep y_dev with the trusted evaluator until the final refit, or explicitly abandon the hard 12-feedback interpretation. State that train-only internal search remains allowed within CPU limits; member-level dev selection in an ensemble consumes feedback when exposed.

**Cheap falsifier.** In an apparatus-only synthetic fixture, request 13 distinct development prediction vectors through one tool invocation and through worker-local scoring. A purported 12-feedback hard cap fails if a thirteenth score becomes observable. No scientific model run is needed.

**Uncertainty.** This is an incomplete proposal, not a demonstrated implementation bypass. If the future runner already keeps y_dev private and meters prediction-level feedback, documenting that resolves the finding.

Evidence:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 35, 63, 73–75, 85: Common train/dev access, arbitrary code tools, 12 score calls, only outer test labels explicitly withheld.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json`, SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`, lines 18–28: dev_calls=12 without definition of candidate or label custody.

## D3 — MEDIUM: The baseline and final-refit definition leaves consequential ML behavior unspecified

Imputation plus unknown-safe encoding and seeded RF100 is not yet a reproducible pipeline. The text does not fix imputation/encoding choices, categorical schema, seed values and estimator settings, or require every learned transform to fit only on the current training partition. The final code hash also does not specify how an early-stopped model, threshold, feature selector or ensemble chosen on dev becomes a single frozen outer-train refit.

Differences can arise from preprocessing or refit semantics rather than the selected research policy. Re-running code that performs model selection during final refit changes the submitted candidate; a mutable config outside the code hash has the same problem. Balanced accuracy is a reasonable objective, but its class mapping and prediction contract must be bound to the artifact.

**Minimum correction.** Add a small executable ML interface: fit(train_X, train_y, frozen_config), predict(test_X), and a canonical baseline configuration. Freeze transform fit scope, class labels, seeds, configuration/artifact hashes, and how dev-selected stopping counts or thresholds are reused. Define whether final fitting of an ensemble counts as one pipeline refit and meter its total compute.

**Cheap falsifier.** Use a tiny synthetic table with an all-missing training column, a dev-only category and a rare class. Confirm that changing dev rows cannot alter fitted preprocessing, prediction class order is stable, and final refit makes no new selection or test access. Inspect the recorded configuration to see whether code-hash identity alone would miss a change.

**Uncertainty.** The draft explicitly lists frozen executable artifacts as pending. This finding supplies the ML-specific content required in that artifact, not evidence that a real run used incorrect preprocessing.

Evidence:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 31, 63, 79, 85–89: Outer-train refit, one final refit, fallback RF100, artifact code hash, balanced accuracy.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/task-roster.json`, SHA-256 `e952968e594b2bd32ed10e6b8f9c3c0863f8e856490e41932fd333e3d388c691`, lines 229–249, 581–601: Missing-heavy dresses-sales and sick tasks make preprocessing choices consequential.

## D4 — MEDIUM: The design rationale omits the closest optimization-specific ML-agent and AutoML comparisons

AIDE directly specifies code-solution search with draft/debug/improve operations, evaluated nodes and concise historical summaries; it also evaluates CPU tabular tasks. Auto-sklearn 2.0 explicitly formulates time-bounded pipeline search and generalization across development/evaluation datasets. These are close methodological alternatives to the proposed work, beyond generic coding-harness comparisons.

A single RF starting artifact calibrates validity, not the value of research orchestration over ordinary automated pipeline search. R−B remains a valid narrow package contrast after other fixes, but neither novelty nor usefulness over established ML optimization follows from that contrast alone.

**Minimum correction.** Add an explicit comparison of R with AIDE's search/state policy and with a bounded non-LLM pipeline optimizer. Preserve R−B as the primary question. Either include one optimization-specific reference during development or state clearly why it is out of scope and limit 'strong existing method' to the actual frozen B. A whole extra confirmatory factorial study is unnecessary.

**Cheap falsifier.** On development tasks only, compare the expected search-space coverage and, when authorized, run a fixed 12-feedback pipeline portfolio under the same compute/refit contract. If it matches gains at much lower total cost, a claim of research-specific practical value needs narrowing; this does not falsify the R−B causal contrast.

**Uncertainty.** Selected primary methods were read, not full papers or implementations. Published headline scores were not treated as comparable, and no local result or SOTA ranking was inferred.

Evidence:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 13–23, 35–57, 85, 109: Five-anchor rationale, expressive B candidate family, pipeline-search task and fallback estimator.
- [Primary source](https://arxiv.org/html/2502.13138v1): Sections 2–3.2, and 4.1 protocol/baselines; rendered lines 75–211, with line 173–196 display gap not used. Selected sections, not full-paper read.
- [Primary source](https://jmlr.org/papers/volume23/21-0992/21-0992.pdf): Sections 2–2.2 and opening 3.1, printed pp. 3–6; selected text on OpenML ancestry in 3.4.1, printed p. 13. Selected sections, not full-paper read; no visual PDF review.

## D5 — MEDIUM: The long-horizon proxy criterion is too weak to distinguish sustained research from ordinary adaptive search

Any basic adaptive optimizer changes later trials in response to earlier scores. Merely observing that behavior or a source pointer does not show that persistent context, recovery or extended evidence dependencies were needed. RE-Bench's methods and limitations explicitly separate task duration, engineering complexity and feedback structure; even its broader research-engineering tasks do not establish full R&D automation.

The selected tasks are suitable for bounded ML pipeline engineering, including real implementation and model selection. They may never exercise the sustained-research mechanisms that motivate the title. A positive score result would then support orchestration within short adaptive searches; a null would not meaningfully test long-horizon context value.

**Minimum correction.** Name the primary result bounded iterative ML pipeline optimization from the outset. For a sustained-research interpretation, predefine a small trace criterion identifying a later decision that needs earlier non-current evidence after a genuine context or recovery boundary, and verify the source-to-decision link. Keep this a scope criterion; do not select primary tasks after observing treatment gains.

**Cheap falsifier.** Inspect development traces for the purported dependency: if current code plus latest score suffices, or no actual context/recovery boundary occurs, the sustained-research interpretation fails and the narrower primary result remains reportable.

**Uncertainty.** The draft already acknowledges this limitation and permits narrowing, which is sound. This finding concerns making that criterion operational, not requiring multi-day runs or asserting that small tasks cannot involve research.

Evidence:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 7–9, 23, 63, 103–109: Sustained research framing; 90-minute, 12-feedback task; pilot criterion based on prior observations influencing later choices.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt`, SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`, lines 72–103, 408–429: Exact history retrieval after working-view eviction.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt`, SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`, lines 325–403: Cross-loop artifact and evidence continuity.
- [Primary source](https://arxiv.org/html/2411.15114v2): Sections 3.1–3.2 (rendered lines 201–262), 5.1–5.3 and 6.1 (382–438). Selected sections, not full-paper read.

## Sound points

- Fixed frontier weights and separation of research-artifact updates from pre-evaluation harness development correctly preserve the main mechanism distinction.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 15–19, 49–57.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt`, SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`, lines 285–289.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt`, SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`, lines 198–227.
- B retains persistent execution, code, record access and delegation; same-model R roles are not described as statistically independent. R−B is explicitly a package contrast.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 35–47.
- One underlying session/REPL owner and external run receipt ownership are preserved. The source-inspired context policy is an adaptation; no full Scroll reproduction or merged-system efficacy is claimed.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 41–44, 113.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.23552v1.txt`, SHA-256 `bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3`, lines 194–210.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01622v1.txt`, SHA-256 `4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985`, lines 237–269, 315–343.
- Single locked final artifact, independent outer scoring, finite-suite scope and explicit refusal to compare to the OpenML 10-fold leaderboard are defensible. U includes deliverability rather than pretending every failure is a model accuracy.
  Evidence: `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md`, SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`, lines 29–31, 79–99.

## Read scope and limits

The design, protocol and entire 1,042-line roster were read, together with the packet instructions, brief, objective, decision contract, five-anchor README, decision record and evidence manifest. This reviewer does not inherit earlier full-read receipts.

Retained primary-text selections:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.23552v1.txt`, lines 131–294; SHA-256 `bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3`. Architecture §§2.1–2.6.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt`, lines 80–432; SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`. Introduction/related work and methods through §3.4.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt`, lines 40–442; SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`. Introduction and §2 context mechanism, start of §3.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt`, lines 60–300; SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`. Creation/evolution distinction and benchmark §3.1–3.2.
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01622v1.txt`, lines 1–400; SHA-256 `4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985`. Intro/related work, architecture §§3.1–3.4, experimental setup and start of results.

The five external primary sources and exact read scopes are attached to findings D1, D4 and D5 and recorded in review.json. Four targeted search queries were used; no broad discovery loop. Search snippets were navigation only. No source headline performance was used as a comparable result.

Unreviewed: full papers/visual PDF layouts, dataset rows and split files, actual B/R code and environment, model access, runtime isolation, scoring/budget enforcement, statistical calibration and broad literature completeness. Power/model/OpenML metadata attachments were hash-checked only. No peer outputs, prior verdicts or peer contact. `docs/CODEX-NAVIGATION-GUIDE.md` was absent.

Retrieval exposure: generic memory guidance and MEMORY.md lines 30–118 were visible; historical design conclusions were not used as authority. The current packet controls scope. Initial unconfirmed thyroid-family lead was discarded after reading the whole roster.

Planning/progress: frozen packet inspection complete; selected methods and four-query targeted lookup complete; five findings and JSON consistency review complete. Only the assigned review.md and review.json were written. No native code, manuscript, source protocol, data, installation, model call, scientific run or external posting.
