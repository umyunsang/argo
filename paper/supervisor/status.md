# ARGO paper autonomous-research status

- **next_first_action:** embed the Korean summary and keyword line into the manuscript body so the Word artifact carries them, then verify Roman chapter numerals, double spacing, and page numbers against the official form.

- **last_updated:** 2026-09-03T00:21:27+09:00
- **goal:** active — `abf5e851-82b2-49e6-9851-c869ae06a99b` (recreated 2026-09-02 after the previous goal entered error), no token budget — autonomously complete and improve the graduation paper with evidence-grounded claims and deterministic validation
- **model:** `openai-codex/gpt-5.6-sol`
- **current_phase:** cycle 11 closed — conclusions rewritten to the instrument boundary and the Word submission artifact built and structurally verified
- **last_checkpoint:** `f33f5993f` — round-9 sources, design comparison matrix, decisions 09A–09D, executed sandbox fixtures, GPU governance

## Completed in current phase

### Cycle 11 — conclusions rewritten and the submission artifact built

- **Counterevidence sweep first:** three discovery primitives searched specifically for evidence that cue-based checklist scoring is adequate, which would have reversed the endpoint replacement. Nothing supporting it was found, so the replacement stands.
- **Conclusions rewritten:** the thesis now states that it set out to test an effect, reached the prior question of whether the instrument could be trusted, and stopped there. The contribution is named as methodological, and bounded by three limits including the calibration set the system cannot produce for itself.
- **Word submission artifact built** from the validated manuscript and verified by parsing its own document XML rather than trusting the converter: correct top-level section order, 232 paragraphs, 50 headings, zero forbidden public names.
- **A gate fired on ordinary language and was narrowed deliberately.** The inherited pattern blocked the word used for handing in a thesis. Rather than renaming artifacts or disabling the check, the pattern was narrowed to competition-specific forms and proved by fixture to still fire on every competition term (`RD-2026-09-02-17A`). Describing the gate then tripped it, so exact patterns now live in the hashed ledger and the graph points to them.
- **Known gaps recorded, not hidden:** the Korean summary and keywords are not yet embedded in the manuscript body, the application-rendered PDF export timed out, and the page-format properties inherited from the reference document are unverified against the official form.

### Cycle 10 — front matter aligned, and the self-verification hazard named

- **Gap picked:** the Introduction and Proposed Method still described the round-7 design, and the thesis had not stated what a system that studies itself is entitled to claim.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators. One is directly adversarial to this project: when an agent controls both the optimized object and its verifier, self-assigned scores can stay high while real performance does not.
- **Executed:** the scope subsection now states that the work reached the instrument-admissibility boundary and stopped there, and a new method subsection makes the three instruments first-class design objects, each with its own falsifier. Five references added, bibliography reordered.
- **Named hazards rather than assumed immunity:** self-authored verification, harness tampering by a self-improving agent, and self-evolving loops that presuppose a metric which does not exist. The mitigations already implemented are stated against each.
- Manuscript is now 7,781 words with 121 reviewed locators behind it.

### Cycle 9 — the manuscript now reports what was executed

- **Gap picked:** five cycles of executed instrument evidence existed and the manuscript reported none of it, which is the gap that matters most against the thesis objective.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators on construct-validity reporting, validity degradation across evaluation pipelines, audit failure modes, preregistration deviation, and negative-result publication.
- **Executed:** the results section was rewritten to report the three executed blocks, the falsification of the first primary endpoint, the measured reliability of its replacement, and the two design parameters fixed by measurement. Ten new references were added and the bibliography was reordered to first-citation order.
- **The section leads with the falsification rather than hiding it**, because publishing filters out negative results and models trained on that literature inherit the bias.
- **Still no efficacy claim.** The section states explicitly that no treatment effect is estimated, that four preregistered decisions were superseded or falsified, that pilot tasks are development data, and that all element verdicts remain inadmissible as scores.

### Cycle 8 — is the verifier even stable?

- **Gap picked:** labels are expensive and require a human, so before requesting any, test whether the verifier is stable enough to be worth calibrating.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators, including one that directly challenges the plan: agreement is not accuracy, and high self-consistency frequently co-occurs with wrong answers.
- **Executed:** reliability audit on 64 stratified pairs, each re-judged by the same judge with the same prompt and independently judged by a second model.
- **Measured:** test-retest agreement **0.844**, cross-model agreement **0.703**, chance-corrected kappa **0.411**. Above 0.9 confidence retest agreement is **0.880**, cross-model **0.920**, and **0 of 20** high-confidence pairs disagreed across models. Between 0.7 and 0.9 cross-model agreement falls to **0.568**, near chance.
- **Decision:** a reliability floor at 0.9 confidence abstains before calibration, and calibration may only tighten it (`RD-2026-09-02-16A`). This is reliability, not validity, and is reported as such.
- **Calibration form emitted:** 22 blinded items sampled stratified across confidence bands with a recorded seed, plus a separate evaluator-owned key. Stratification rather than uncertainty sampling was chosen because uncertainty sampling concentrates the items where annotation error also concentrates (`RD-2026-09-02-16B`). Q-0006 requests the labels; the default is to continue without them.

### Cycle 7 — replacement endpoint implemented and measured

- **Executed:** filter-plus-verification over all 32 retained episodes, 192 element judgements, judge drawn from a different provider family than the treatment backend. Receipt `paper/experiments/verified-endpoint-receipt.json`.
- **The falsification held outside the probe set.** On real artifacts the falsified cue endpoint and the verified endpoint correlate at **0.043** with a mean absolute difference of **0.484**. They were not measuring the same thing.
- **Variance recomputed on the verified endpoint:** residual **83.8 percent**, task **16.2 percent**, condition and interaction both estimated at **zero**.
- **Consequence for allocation:** with a zero interaction component the standard error of a condition mean does not depend on the task-versus-repeat split, so resolution cannot be bought by reallocating. The split is now chosen for task breadth, and the projected paired minimum detectable effect is about **0.081**, roughly double what the falsified endpoint implied (`RD-2026-09-02-15B`).
- **Nothing is scored.** All 192 verdicts come from an uncalibrated judge and are inadmissible; 2 unparsed and 3 unclear replies are counted rather than dropped. The verdicts are now the labelling material for the 25-label calibration set.

### Cycle 6 — my primary endpoint failed its own falsifier

- **Gap picked:** `RD-2026-09-02-11A` carried the falsifier "if coverage does not separate artifacts a reader would rank differently, it measures vocabulary". That was untested.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 6 locators. Planted-shortcut evaluation, solution hacking, and grounded checklist partial credit supplied the audit method.
- **Executed:** an adversarial probe suite over all eight anchor checklists. Cue matching counted negated sentences containing the cue as satisfied at **0.969**, and missed genuine paraphrases at **0.909**.
- **Ablation:** a negation guard drove false positives to **0.000** but raised misses to **1.000**. The failure is structural: matching cannot decide satisfaction.
- **Verdict: falsifier fired.** Cue matching is rejected as the primary endpoint and demoted to a high-recall candidate filter; element satisfaction becomes a verified judgement admitted through the selective evaluator (`RD-2026-09-02-14A`).
- **Two consequences recorded rather than hidden.** The 25-label calibration set moves from optional to load-bearing for the primary endpoint. The variance components from cycle 5 were computed on the falsified endpoint, so the numeric allocation is void while the algebra stands; the 32 episodes are retained and rescorable, so no episode is wasted (`RD-2026-09-02-14B`).

### Cycle 5 — variance block EXECUTED, allocation reversed by measurement

- **Executed:** 32 episodes on the four frozen confirmation tasks, 4 conditions x 2 repeats, all exit zero, zero canary leaks. Receipt `paper/experiments/variance-block-receipt.json`.
- **Measured variance components of the coverage endpoint:** repeat residual **64.3 percent**, condition **22.6 percent**, task-by-condition **13.1 percent**, task **0.0 percent** (boundary estimate).
- **This refuted my own pre-registered assumption.** `RD-2026-09-02-09D` had kept two repeats and stated the falsifier "if task variance dominates residual, add tasks instead". The measurement came out the other way, so the decision is superseded rather than defended.
- **Allocation derived, not chosen:** at a fixed episode budget the standard error of a condition mean is `(repeats x interaction variance + residual) / (budget / conditions)`, which increases monotonically with repeats. The block therefore moves to the maximum number of tasks at one repeat, with a small repeated subset kept to re-estimate residual variance (`RD-2026-09-02-13A`). Projected paired MDE improves from about 0.049 to about 0.045 while quadrupling task coverage.
- **Honest limits recorded:** 32 episodes give 3, 3, 9 and 16 degrees of freedom, the task component is a boundary estimate at zero, and coverage is per-task normalised, which suppresses between-task variance by construction.
- **Label protocol frozen:** `paper/research/human-label-protocol.md` fixes element-level blinded labelling, stratified sampling, an overlap-agreement gate, and append-only records.

### Cycle 5 (earlier) — confirmation set frozen

- Four confirmation tasks frozen on sources disjoint from the pilot and excluded from their own released evidence packs: structure-versus-insight ablation, attribution of improvement to harness rather than model, instrument-change measurement under scarce labels, and budget and access control in optimization benchmarks.
- Element checklists were written and frozen **before any artifact exists**, which is the property the pilot anchors could not have (`RD-2026-09-02-12A`).
- Judged scoring remains blocked on the 25-label calibration set; unscored artifact generation is not.

### Cycle 4 — the scoring anchor gap is closed by construction

- **Gap picked:** rubric scores were inadmissible without a human anchor, and the deterministic layer alone could not carry the validity endpoint.
- **Literature loop:** 9 discovery calls across 3 objectives, 6 new `FULL_PAPER_READ` records, 8 line-anchored locators. Record: `paper/research/literature-round10-retrieval-record.json`.
- **Anchor found in prior work:** criteria can be derived from an expert reference rather than authored freely, analytic per-criterion scoring avoids holistic halo, and selective evaluation bounds judge error through calibrated abstention.
- **Executed:** reference-anchored analytic coverage over evaluator-owned element checklists, measured on all 16 retained pilot artifacts. Coverage ranges 0.667 to 1.000 and names the missed elements, where fabrication redlines had produced no signal at all.
- **Defect found by fixture:** the first selective-evaluation implementation chose its threshold from the empirical error rate, which overfits a finite calibration set. Replaced with a one-sided binomial upper bound, so an undersized set is now refused and the required size is reported.
- **The blocker became a number:** at 95 percent confidence a flawless calibration set of **25** labels certifies a 10 percent risk level, **11** certifies 20 percent, and **52** certifies 5 percent. The adopted target is at least 25 labels on tasks disjoint from the burned pilot set (`RD-2026-09-02-11C`).
- **Suites:** reference-anchor 13/13, scoring 14/14, sandbox 10/10, runner 7/7.
- **exa MCP usage this cycle: not used.**
### Cycle 3 — instrument pilot EXECUTED

- **Backend probe (live):** session provider `HTTP 429 usage limit reached`, reset in about 4.8 days; one hosted provider timed out at 240 s; one router `HTTP 402 insufficient credits`; two selectors answered. Treatment pinned to one selector, judging reserved for a different family (`RD-2026-09-02-10C`).
- **Tasks frozen:** four design tasks built from retained sources with withheld targets isolated by the release sandbox, each with a released evidence pack of 12 excerpts for the retrieval conditions.
- **Pilot executed:** 16 episodes, 4 tasks x 4 conditions, all exit zero, 1942.9 s total, 287,707 bytes of artifacts. Receipt `paper/experiments/study-a-pilot-receipt.json`.
- **PF-1 hidden-task boundary held:** zero withheld canaries in all 16 artifacts.
- **PF-2 the deterministic layer had no discrimination:** fabrication redlines fired on 0 of 16 real artifacts while firing on every corrupted fixture. Five structural-completeness checks were added and flag 13 of 16 (`RD-2026-09-02-10B`).
- **PF-3 the manipulation probe was mis-specified:** all 8 structured episodes filled the scaffold, yet 7 of 8 never echoed the field name, so the probe fired on episodes whose state was consumed. Respecified to filled-field consumption plus carry-through (`RD-2026-09-02-10A`); consumption is now 5 of 8.
- **Cost:** no GPU, no compute unit, 0 CU cumulative. Token usage is `UNMEASURED` because headless text mode emits no usage record; the confirmatory run must use json mode.
- **Burned:** all four pilot tasks are permanently excluded from confirmation, two of them as the Q-0004 disclosure tasks.
- **No effect is claimed.** Four cells with one run each cannot resolve any contrast, and the structural checks were specified after seeing these artifacts.
### Cycle 1 under the standing loop (instruction #0005)

- **Gap picked:** the round-8 retrieval record had zero discovery loops, no design comparison existed, and no pilot prerequisite had been built.
- **Literature loop:** 3 objectives x 3 primitives = 9 discovery calls, 135 candidates, 7 new `FULL_PAPER_READ` records with exact versions and 10 line-anchored locators. Record: `paper/research/literature-round9-retrieval-record.json`.
- **Design comparison:** `paper/research/design-comparison-round8.md` compares 16 prior experiments across 10 design columns and states where Study A is stronger, weaker, and what changed.
- **Counterevidence found:** a controlled two-agent, 288-run ablation of persistent external context reports no reliable gain and attributes failures to implementation skill. This is direct counterevidence to H-A and forced two design changes.
- **Decisions 09A-09D:** manipulation probe for state use; pre-registered equivalence margin with TOST plus a resolution target; judge admission on severity, halo, and step-level review; no change to repeats with a pre-registered variance decomposition.
- **Execution unit: `EXECUTED`.** `experiments/study_a/release_sandbox.py` with six fail-closed probes, verified by `experiments/study_a/test_release_sandbox.py`: 10/10 checks, every probe demonstrated firing on a corrupted fixture. Receipt `paper/sources/study-a-sandbox-fixture-receipt.json`.
- **Verification:** validator PASS; clean-clone run `d98a34a2-bfd6-43e6-be18-cc57605e1a44` PASS at `f33f5993f`, 92/92 locators re-derived.
- **Instruction #0006 applied:** Study C moved to `EXECUTION_PATH_SECURED_PREREGISTRATION_REQUIRED`; `paper/research/colab-usage.md`, `paper/supervisor/cost-ledger.md` (cumulative 0 CU, no active sessions), `paper/research/burned-task-ledger.json` created; Q-0005 opened as blocking.
- **exa MCP usage this cycle: not used.** All candidates were reachable through the research CLI primitives; recorded in the retrieval record `web_queries` field.

### Remaining pilot prerequisites

| Prerequisite | State |
|---|---|
| hidden-task release sandbox and integrity probes | **PASS**, 10/10 checks, six probes demonstrated firing |
| independent scoring calibration and judge agreement fixture | **PASS**, 9/9 checks, identical across three runs |
| fixed Study A runner as one command | **PASS**, 7/7 checks |
| 16-episode pilot | blocked only on task freeze, backend pin, and burned-task entries |

### Cycle 2 under the standing loop

- **Gap picked:** the two remaining pilot prerequisites, both GPU-free, per instruction #0006.
- **Built and executed:** `experiments/study_a/scoring.py` (deterministic redlines, one judge call per dimension, calibration on agreement, severity, halo) and `experiments/study_a/run_episode.py` (fixed one-command runner refusing incomplete configuration, condition/factor mismatch, or a fired pre-launch probe).
- **Three defects were found by the fixtures, not by reading:** the manipulation probe ran pre-launch where no artifact exists and blocked every structured-state episode; the calibration fixture seeded randomness with the salted builtin hash and was therefore non-reproducible; judge severity was computed on the 30-point total but tolerated at half a point. All three are fixed and recorded in `paper/sources/study-a-prerequisite-receipt.json`.
- **Local reproduction of a reviewed finding:** a judge with agreement `0.9653` against the human anchor was still inadmissible at severity `-1.78`, which is why agreement alone is not the admission test.
- **Remaining before the pilot:** freeze four tasks with withheld targets, pin the model backend, and open the two burned-task entries approved in Q-0004.

### Resume procedure (instruction #0004 §2)

- HEAD confirmed and continued on the canonical branch; no ancestor node edited.
- `paper/evidence-matrix.csv` was 0 bytes in the working tree and was restored from HEAD. Cause: the receipt had recorded CRLF working-tree bytes while git stores the LF-normalized blob, so the recorded digest could never be reproduced from the repository. The writer now emits LF, `.gitattributes` pins `eol=lf`, and the digest matches the committed blob.
- Validation run `3fe2958b-44b6-4760-89fb-f711440c2ae0` is **failed** (exit 1) at commit `b2070ed09`. Root cause was not the manuscript: the local pass depended on working-tree bytes absent from the repository — five round-4 reports were never committed and 25 of 74 claim locators pointed at source slices missing from both repo and worktree.
- Repair: 16 exact-version archives re-fetched, all **byte-identical** to recorded digests; 20 TeX slices re-extracted and one PDF-derived text reproduced (recipe recovered as `pdftotext -layout`); all locators verified by file digest, line slice, and excerpt digest; a global fail-closed locator gate was added and shown to fire on a deleted slice. Receipts: `paper/sources/legacy-source-restoration-receipt.json`, `paper/sources/global-locator-gate-failing-first.json`. Commit `c677aeb6e`, clean-clone run `67bec1bc-b8da-47a6-8f49-6a486799f844` **PASS**.

### Round 8 — design competition (instruction #0003 §3-3~§3-5)

- Four full reads with exact versions: `2403.14403v2`, `2310.11511v1`, `2405.14831v3`, `2602.15112v2`; 8 line-anchored locators; 8 evidence rows; graph now 170 nodes / 397 edges.
- Three six-field decision records (`RD-2026-09-02-08A/B/C`) recorded in the ledger and linked into the context graph as `decision:*` nodes with `informs_decision` edges from their reviewed sources.
- Study A inherits its 2x2 structure; changed elements: retrieval-decision quality added as a secondary endpoint, integrity probes added to the evaluator gate, and an ideation-versus-configuration attribution arm added to the pilot.
- Execution-graded replication deferred as Study C with resources and steps in `paper/research/study-c-runbook.md`.
- Engine usage verified and written to `paper/research/orx-usage.md`.
- Commit `5527c7926`; clean-clone run `7184ad85-57e3-4fa4-a12c-21a5b80513db` **PASS** with 82/82 locators re-derived.

- Root-agent adaptive round 5: five `FULL_PAPER_READ` design/evaluation records. Architecture round 6 adds six `FULL_PAPER_READ` harness/context anchors, including programmatic context management. Corpus: 43 full reads and 74 reviewed locators; round 7 adds routing, protocol, RAG, and agentic-stack evidence with 22 exact locators.
- Prospective experiment revised to provisional 2×2 structured-state × dynamic-retrieval Study A.
- Minimum executable unit proposed: 16-episode instrument pilot; no result claim.
- ResearchClawBench runner pinned at `5bc7963f82b8cc4f13ea27e7524709e0d6a12a96`; workspace projection and missing sandbox guarantee recorded as separate code locators.
- Public-paper hard exclusions applied; `paper.tex` hard-exclusion scan is zero.
- 30-minute heartbeat active: `c024a580-775d-4253-9249-e62de07a047a` (cron `*/30 * * * *`). The previous id `28b18ed8` was paused and is retired.

## Literature-map progress (preliminary anchor count / target ≥3 FULL reads)

| Area | Preliminary FULL reads | Status / named gap |
|---|---:|---|
| 1. Harness functions | 12+ | anchor count passes; necessity/design split mapped, remaining approval and sandbox experiments open |
| 2. Memory functions | 6+ | anchor count passes; personalized memory remains thin |
| 3. Protocols | 5+ | academic anchor threshold passes; official MCP/A2A versions and human-factor evaluation remain |
| 4. Skills | 4+ | anchor count passes; normative constraints need focused support |
| 5. RAG engine | 4+ | academic anchor threshold passes; product backends and local corpus evaluation remain |
| 6. Agentic AI development stack | 5+ | method threshold passes; exact framework/product primary behavior remains follow-up |
| 7. Coding-agent harness architecture | 9+ | routing mechanism axis anchored; pi standalone source and two direct primary contrasts remain open |
| 8. Autonomous research engine functions | 8+ | anchor count passes; seven functional subtopics mapped, public-engine naming forbidden |
| 9. Provider and dynamic model routing | 5+ | academic threshold passes; H-E remains unexecuted and fixed model retained for Study A |

## Capability map and public-name gate

- capability map: `46/46` sub-capability rows drafted; current-cycle validation set selected, literature gaps remain.
- public-name source gate: added and passing with `0` current hits; synthetic sample detected all 7 forbidden classes.
- public-name PDF gate: implemented with pinned `pdftotext`; full 43-source deterministic two-build validation PASS, source/PDF token hits `0`.
- current-cycle targets: hidden-task sandbox, independent evaluator, observability, context graph, research procedures/norms/decision records, retrieval pipeline, source verification, claim–evidence ledger, preregistration/deterministic validation, iterative stopping.
- model routing: target capability, design-only in Study A (`R-ROUTING-DEFER`) to avoid a treatment confound.

## Next concrete actions

1. Freeze four unseen confirmation tasks disjoint from the burned pilot set, and re-validate the frozen structural checks on them before any scoring.
2. Build the human-anchored calibration subset so rubric scores become admissible; deterministic checks alone cannot carry the validity endpoint.
3. Switch episode execution to the json output mode so per-episode token usage is measured rather than proxied.
4. Estimate the confirmatory block cost from measured pilot durations and token usage, then open the GPU question again only if Study C is scheduled.
5. Keep every claim scoped: the pilot validated instruments and estimated no effect.

## Blockers and questions

- **E5 launch:** blocking — hidden-task sandbox, independent scoring, and fixed Study A runner are not implemented.
- **research design:** preregistration-ready at `paper/research/research-design.md`; H-B direct comparator and H-E rationale are closed, while launch remains blocked by hidden-task isolation, independent scoring, and fixed runner.
- **plan deadline:** answered `2026-10-31`; schedule updated in research design.
- **Q-0001:** answered — department plan deadline `2026-10-31`; current semester assumption retained.
- **Q-0002:** answered — six non-executable capability groups remain design-only/follow-up; no new native runtime.
- **DeepVoice evidence:** forbidden by existing user instruction; no access or edit planned.
- No efficacy experiment is running; `Experimental Results` remains explicitly unexecuted.
