# ARGO paper autonomous-research status

- **next_first_action:** rebuild sample-size planning as a generalizability design with the scoring method as a facet, and measure that facet properly before it carries a plan.

- **last_updated:** 2026-09-03T04:50:50+09:00
- **goal:** active — `abf5e851-82b2-49e6-9851-c869ae06a99b` (recreated 2026-09-02 after the previous goal entered error), no token budget — autonomously complete and improve the graduation paper with evidence-grounded claims and deterministic validation
- **model:** `openai-codex/gpt-5.6-sol`
- **current_phase:** cycle 57 closed — the paired detectable effect is void as a design target; the instrument facet varies more than the effect
- **last_checkpoint:** `f33f5993f` — round-9 sources, design comparison matrix, decisions 09A–09D, executed sandbox fixtures, GPU governance

## Completed in current phase

### Cycle 57 — the design target was sized on the smaller half of the problem

- **Gap picked:** if the scoring method moves the endpoint by 2.3x the detectable effect, whether that detectable effect still means anything had to be checked.
- **It does not.** Across the eight artifacts the method difference has **sd 0.301**, about **3.65x** the detectable effect of 0.0825, and the variance of that difference is **1.48x** the variance of the coverage being measured. The instrument varies more than the thing it measures.
- **It cannot be corrected away.** The difference changes sign, from **-0.167 to +0.667**, so no constant adjustment recovers the earlier number.
- **The paired detectable effect is void as a design target.** It was computed with the scoring method treated as fixed, so it omits a variance component larger than the one it used. `RD-2026-09-02-15B` and `RD-2026-09-02-33A` carry that status.
- **What replaces it is named, not hand-waved:** sample-size planning must treat the scoring method as a facet with its own variance, as generalizability designs do. That replacement is not built, and the facet estimated here rests on eight artifacts judged by one model, so it needs its own measurement before it can carry a plan.
- Claim checks now stand at 50.

### Cycle 56 — the instrument moves the endpoint more than the effect it was built to find

- **Executed:** all 48 element judgements over the eight confirmation artifacts re-scored on the full artifact, compared with the span-based verdict on the same items.
- **Mean coverage rises from 0.542 to 0.729**, a shift of **0.188**. Seventeen of forty-eight verdicts change — **13 negative to satisfied, 4 the other way** — so removing retrieval is not simply a looser rule.
- **The size is the finding.** The paired detectable effect on this endpoint is **0.0825**, so the scoring method moves the reading by about **2.3x** the smallest effect the design was sized to detect. An instrument choice of that magnitude does not modify the comparison; it dominates it.
- **Per-condition coverage is deliberately withheld.** Two artifacts per condition cannot separate a condition from a task, and the shift is a property of the instrument, not of any condition.
- **Admissibility unchanged:** these verdicts remain inadmissible for scoring, because no human-anchored calibration set exists. They describe what the instrument reads, not what an episode scored.
- Claim checks now stand at 47.

### Cycle 55 — remove rather than repair, decided on measured numbers

- **Gap picked:** the endpoint drops about two in five true positives at the retrieval stage. Repair or removal had to be chosen, and costed.
- **Measured the cost both ways**, three items judged span-based and whole-artifact by the same judge in a mode that reports usage: **$0.02682** against **$0.04320**, a ratio of **1.61**.
- **Repair rejected on the shape of the failure**, not on cost. Three of the four no-span misses were a single element stated in wording the cues do not match, and poor spans fail at a similar rate, so widening cues trades one silent miss for another with no recall measurement to bound it.
- **Decision:** whole-artifact judging becomes the primary path; the cheaper span verdict is retained on a **20% subsample** as a drift check, so disagreement between the two stays visible rather than assumed away.
- **The trade is stated as a trade.** Full-artifact judging has no accuracy measurement of its own, so a measured, directional failure mode is being exchanged for an unmeasured one. That is defensible only because the removed one is quantified.
- **Projected quality-arm judging cost** for a 116-episode block: $18.67 span-only, $30.07 full-only, $33.80 with the subsample. This does not change `Q-0007`, which covers the completion arm and needs no judging at all.

### Cycle 54 — the other half of the failure, and the size of the bias

- **Gap picked:** only items where retrieval returned *nothing* had been checked. The larger case — a span returned but poor — was untested.
- **Executed:** all nine items where a span was returned and the verdict on it was negative, re-judged by both models on the full artifact.
- **A returned span is not protection:** 3 of those 9 are called satisfied by both judges.
- **Complete picture: 7 of 18 pipeline negatives overturn** under the wider view, and the failure is not concentrated where retrieval found nothing — no-span 4/9, poor-span 3/9.
- **The endpoint understates coverage at roughly that rate, always in the same direction.** That is a measured bias in the endpoint of record, not a suspicion.
- **One caveat bounds the whole measurement**, and it is in the paper: the reference is two-judge agreement on the full artifact, which is not ground truth. It shows the pipeline verdict is unstable under a wider view, not that the wider view is right. The falsifier is written accordingly — if human labels later side with the pipeline, the overturn rate does not indicate bias.

### Cycle 53 — testing the recorded limit broke the endpoint assumption

- **Gap picked:** the previous cycle recorded that both judges saw the same retrieved spans, so a shared retrieval failure would look like agreement. That limit was tested rather than left standing.
- **Executed:** the nine items where cue retrieval returned **no span** — scored `not_satisfied` without any model call — were re-judged by both models on the **full artifact**.
- **Result:** both judges call **4 of 9** satisfied; at least one calls **5 of 9**. The agreement on those items was a shared retrieval failure, not a judgement.
- **This falsifies an assumption the endpoint rests on.** Cue matching was demoted to a *high-recall* candidate filter precisely so verification could do the deciding. A filter that misses at least four of nine makes the endpoint **understate coverage silently**, because no model is ever called on a miss.
- **Consequences applied:** a no-span result is now recorded as **unresolved**, not as a negative verdict; the retrieval step must have measured recall before the endpoint is used for scoring; and `RD-2026-09-02-14A` carries the falsified assumption.
- **Scope stated:** only items where retrieval returned *nothing* were checked. Items with a poor span could fail the same way and remain invisible.
- The earlier agreement figures are unaffected: the cross-judge replication had already excluded these nine from its denominator.

### Cycle 52 — the floor was tested on material it had never seen

- **Gap picked:** reliability was measured on the variance block. Reliability is a property of an instrument *on material*, so transfer had to be measured, not assumed.
- **Executed:** all 48 element judgements over the eight first-repeat confirmation artifacts, judged independently by two models from **different provider families**.
- **Raw agreement fell** to 0.667 from 0.703, because six items produced an unparsed verdict from one judge and are counted as **disagreements rather than dropped**. Excluding those: 0.788 with kappa 0.492, above the earlier figures.
- **The stratification replicated exactly** — and that is the result that matters:

| band | agreement |
|---|---|
| both above 0.9 | **12 / 12** |
| middle | 14 / 18 |
| below 0.7 | **0 / 9** |

- **The part of the instrument actually used held on unseen tasks.** Nothing here supports calling the judge reliable in general; below the floor the two judges disagree on roughly a third of items.
- **A limit is recorded that could inflate this:** both judges received the same prompt and the same retrieved spans, so a shared retrieval failure would look like agreement.

### Cycle 51 — auditing the paper against its own admission rule

- **Gap picked:** the admission rule made 48 episodes unscorable. Whether any manuscript claim still leaned on them, unmarked, had not been checked.
- **Executed:** every number in the body derived from those blocks was located and its surrounding paragraph checked for language marking the dependency. Eleven of thirteen numbers were already labelled.
- **Two were not:** the high-confidence reliability figures, 88.0% and 92.0%.
- **They do not need a downgrade, for a reason worth stating.** The admission rule refuses to **score an episode** whose usage was never measured. Reliability characterises the **judge** — how far a verdict reproduces on the same item — which the artifacts can support even when the episodes cannot enter a score.
- **The distinction is now in the paper**, not left to inference, so a reader can see why the variance components are provisional and these are not. Without it, both sets look equally supported.
- **A guard against stretching it** is recorded as the falsifier: if a reliability figure is ever used as an episode score or as evidence about a condition, the distinction is being abused and the figure must be downgraded.

### Cycle 50 — the executable arm is pre-registered and sealed

- **Gap picked:** the completion arm had a costed block size but no fixed analysis, so the analysis could still be chosen after seeing data.
- **Frozen before the data exists:** the document records that only 16 episodes existed at freeze, and names the confirmation receipt digest at that moment. Any block testing it must consist of episodes beyond those.
- **What it fixes:** the hypothesis and its null with **no direction taken from the pilot**; a two-sided Fisher exact test with alpha 0.05, chosen because counts are small and one arm sits near a boundary; the size and its source receipt; an exclusion rule that **explicitly forbids removing an episode for its outcome**; a stopping rule with **no interim looks**; the falsifier; and what the arm cannot show.
- **Only one arm was pre-registered.** Pre-registering the quality arm would fix an analysis that cannot be run, since it is blocked on human labels and an unbalanced design.
- **Sealed and gated:** the document carries its own digest, and once the block grows beyond 16 episodes any change fails the gate. Three failing-first mutations fire — removing the stopping rule, downgrading the status to draft, and adding an episode while the document is unsealed.
- **Honest limit recorded:** a preregistration written by the agent that will run and analyse the block constrains the analysis but does not make it independent. The seal proves the document did not change, not that it was wise.

### Cycle 49 — one half of the plan is executable, the other is blocked by one input

- **Gap picked:** completion had a costed block size; the quality endpoint had none.
- **It cannot be given one, and that is the finding.** A committed check walks each declared outcome and reports whether its block size is computable.
  - **Budget completion: planable.** 29 per condition, 116 episodes, about $18 — measured by the admission path with no judge in the loop.
  - **Design quality: not planable**, blocked twice. Judged scoring is inadmissible at **0 of 25** human-anchored labels, and the endpoint variance is **not estimable** from admissible episodes because the ceiling refusal left the design unbalanced.
- **The labels are the single binding constraint** on the entire quality arm, and nothing this loop can execute removes that dependency. Saying so is more useful than a block size resting on a variance the design cannot yield.
- **A receipt completeness defect was fixed:** the confirmation receipt listed only the first repeat, so the blocker was misreported as "one observation per cell" instead of "unbalanced". Both repeats are now listed with a per-episode admissible flag, and only admissible episodes may inform a plan.
- **11 fixtures, 5 of 5 mutations caught**, including "report planable despite blockers" and "let an inadmissible episode inform the plan".

### Cycle 48 — how much more measuring, computed rather than guessed

- **Gap picked:** the completion intervals are too wide to act on, and the choice was to extend the block or to state what extension is required.
- **Refused the cheap option.** A third repeat costs about a dollar and moves the half-width from **0.327** to roughly **0.29** — it would buy the appearance of progress and change nothing that can be concluded.
- **Computed the real requirement:** to reach a half-width of **0.15** at the lowest observed completion rate needs **29 episodes per condition, 116 in total**, at about **$18** using a cost per episode read from the executed receipt rather than assumed.
- **That is six times everything this project has spent on model calls.** Rather than drift toward it in small steps, `Q-0007` records the choice with a default of **not spending without approval**, and the loop proceeds on that default.
- **Committed as code, not a one-off:** 17 fixtures, 6 of 6 mutations caught — including "plan on a guessed cost when the receipt has none" and "use the highest rate instead of the lowest". One fixture was strengthened again after a removed guard still raised, from a square root of a negative number.
- Claim checks now stand at 40.

### Cycle 47 — the rate is reported, and the reading is refused

- **Computed** over the first admissible block, four episodes per condition: minimal, retrieval-only and scaffold-only all completed **4/4**; scaffold-plus-retrieval completed **3/4**.
- **Reported with denominators and Wilson intervals**, because the bare rates invite a conclusion the data cannot carry. Every interval spans more than half the range, the widest is **0.653** wide, and **all four overlap**.
- **Stated plainly in the manuscript:** four episodes per condition can show that a ceiling bound and where it bound; they cannot show that completion differs by condition. Small screening blocks read as settled questions can produce worse decisions than no block at all.
- **Kept separate from quality:** the quality endpoint is still not computed, because judged scoring remains inadmissible without a human-anchored calibration set.
- **Bound two-sidedly:** editing the rate in the prose alone and editing it in the receipt alone each fail the gate. Claim checks now stand at 37.

### Cycle 46 — budget failure became an outcome, and a stale name nearly corrupted the design

- **Gap picked:** refusals were being logged but not analysed, so a condition could look better simply by spending more and having its failures discarded.
- **Declared in the design document:** budget completion rate as a secondary outcome, computed by the same admission path that decides scoreability, reported **beside** the quality endpoint and never merged with it, with denominators stated. A refusal is a competing event for the quality endpoint.
- **The ceiling is explicitly not adjusted to remove refusals.** Moving a limit until it stops binding erases the asymmetry it revealed.
- **Timing recorded honestly:** this outcome was declared *after* the first refusal was observed. That is written into the design rather than concealed, and it is fixed now so later blocks cannot select it once the direction is known.
- **Near miss worth more than the cycle.** The insert used a variable name still bound from many cycles earlier, holding validator source code, because the assertion meant to stop the cell ran before the intended definition. About five thousand characters of Python went into the design document. It was caught when a membership check for the intended heading failed three times while writes were succeeding, repaired from the committed blob and verified against its committed digest.
- **Lesson recorded:** the working state of a long session is itself a hazard. No gate covers an uncommitted working file, so text blocks are now defined immediately before use and every insert is verified by reading the file back.

### Cycle 45 — the ceiling bound, and it bound on one side

- **Gap picked:** allocation could not be re-derived, because one repeat per cell leaves no residual term. The variance guard said so and refused, which is what it is for.
- **Executed:** a second repeat, 8 more episodes, completing a 2 tasks x 4 conditions x 2 repeats design. All 8 transcripts complete, zero canary leaks.
- **The declared ceiling bound for the first time.** One episode was refused at **18 calls against a limit of 16** — and it fell in the **full condition**, which uses the most calls in every single observation (C00 max 4, C01 max 10, C10 max 8, C11 max 18).
- **That is a selection hazard, not a nuisance.** A ceiling that binds asymmetrically removes episodes non-randomly, so dropping them would bias the comparison toward the cheaper condition.
- **Decision: treat violation as an outcome, not data loss.** If the full condition needs more calls, capping calls *is* the budget match, and the endpoint becomes completion within budget. The ceiling was **not** raised to make the refusal disappear, which would have hidden the asymmetry the measurement just revealed.
- **Consequence accepted:** the admissible set is now unbalanced at 7 against 8, so the variance guard again refuses to compute components. Both refusals are the guard working, not failing.
- Block cost $1.20; confirmation block total $2.46. GPU credit units remain 0.

### Cycle 44 — the first episodes that can actually be scored

- **Gap picked:** the confirmatory pipeline had never produced an episode admissible under its own rule.
- **Executed:** 8 episodes, 2 unburned tasks x 4 conditions, structured output mode so usage is measured. **8 of 8 admissible.** These are the first in the project.
- **Integrity:** transcripts complete 8/8, canary leaks **0**, fabrication redlines **0**, structural gaps in 5 of 8, anchors frozen before any artifact existed.
- **Cost:** $1.26 for the block; GPU credit units remain 0.
- **A visible pattern is recorded and deliberately not interpreted.** Structural gaps differ across conditions in this block, but two observations per condition cannot separate a condition from a task. A study that tested a mechanism where it ships found no detectable change despite earlier reports of large gains; that is the standard this block does not meet, and it has no preregistered hypothesis test.
- **No treatment effect is estimated.** Judged coverage is also not computed, because judged scoring stays inadmissible until a human-anchored calibration set exists.
- The evidence cycle was closed in the same turn: 803 files compared, all byte identical, anchor re-run and updated.

### Cycle 43 — back to the science: the confirmatory block had no tasks left

- **Gap picked:** four tasks are burned as development data and the other four were consumed by the variance block, so the confirmatory block had nothing disjoint to run on.
- **Executed:** two new tasks built from unseen recent studies whose experimental design is the withheld target — `K5-unlearning-stress` and `K6-harness-evolution`, six anchor elements each, two evidence files each.
- **Anchors frozen before any artifact exists**, and recorded as such with the instructions digest.
- **The cue check caught real leakage.** The first draft of the instructions pre-answered **five of twelve** scored elements, because the stated constraints named the design choices: a constraint mentioning a retain set gave away the retain-set control, one naming the fixed backbone gave away the frozen-backbone element, and the question itself named overfitting. Constraints were rewritten to define the setting without naming the choices; both tasks now leak **zero** cues.
- **Workspaces build and admit** in both the minimal and full conditions, with no canary in any released file.
- **Nothing has been run on them yet.** They exist so the confirmatory block has unburned tasks with anchors fixed in advance.

### Cycle 42 — closing the window without creating a rubber stamp

- **Gap picked:** staleness was detected but closed only in a later cycle.
- **The danger was the obvious fix.** A command that re-anchors after any run would silence the gate it exists to satisfy. So the anchor updates **only** when the claim level passed, every archive reached an acceptable status, and no file mismatched. A failed or partial run leaves it stale on purpose.
- **Four negative fixtures enforce that:** a failed claim level, a byte mismatch, a failed fetch, and a dry run must each leave the anchor untouched. 9 fixtures total; **5 of 5** mutations caught, including "re-anchor even when verification failed".
- **The run refused to pass, correctly.** One record — a versioned PDF — had no archive members and reported `INCOMPLETE_RECORD`. I completed the record by verifying its artifact digest and the derived text the quotations were cut from, rather than adding the incomplete status to the acceptable set. Widening the check would have been the easy fix and the wrong one.
- **Now closing in-cycle:** 132 archives, **787 files compared, 787 byte identical**, anchor re-run and updated after this round's own locators were added.
- **Honest limit:** the command and the gate share an author, so those negative tests are the only thing separating closure from silencing.

### Cycle 41 — the gate enforces the chain without needing a network

- **Gap picked:** byte-level verification was manual, so nothing forced it to be re-run.
- **The obvious move was wrong.** Running the network check inside the gate would make validation non-deterministic and fail for reasons unrelated to the work — which is how a gate becomes something people switch off.
- **Split by determinism.** The claim level is entirely local, so it runs on **every** validation: each locator's file digest and its excerpt hash at the recorded line range. The byte level records the **digest of the evidence base** it was run against, and the gate fails when that digest no longer matches.
- **Two staleness mutations fire:** corrupting one excerpt hash produced both a verification failure and a staleness failure; appending a locator produced staleness alone. Restoring returns to pass.
- **The contract bit immediately.** Adding this round's own locator made the byte-level receipt stale, and it had to be re-anchored before the gate would pass — the obligation is real, not notional.
- **Limit stated:** staleness is *detected*, not prevented, so a window exists between changing the evidence base and re-running the network check.

### Cycle 40 — the whole evidence base verified, not a sample

- **Gap picked:** byte-level verification covered 4 of 38 receipts, leaving the untested part exactly where a reader would look.
- **Executed across every receipt:** **130 archives** re-fetched and accepted only on a digest match, **782 files** compared byte for byte with their archive members. **782 identical, zero mismatches.**
- **One record is a versioned PDF with no members.** It was reporting `NOT_AN_ARCHIVE`, which reads like a failure although its digest had already been verified. It now reports `DIGEST_VERIFIED_NO_MEMBERS` — stating what was established and what was not, rather than sounding an alarm or hiding the gap.
- **Why not sample:** misalignment between a claim and its cited evidence is a common failure of model-generated reports, and this project generates its own citations, so a sample would leave the interesting part unchecked.
- **Limit unchanged and stated:** a re-fetch depends on the upstream service continuing to serve those exact versions.

### Cycle 39 — archive identity is not file identity

- **Gap picked:** the repair proved the *archive* was authentic; it did not prove the file in the repository came out of it.
- **Three levels, reported separately.** Claim: every locator's file digest and the excerpt hash at its recorded line range. Archive: accepted only on a digest match before anything is read. Byte: each committed file compared byte for byte with the same archive member.
- **Results:** **170 of 170** locators verify with zero file-digest and zero excerpt-hash failures. **27 archives** verified, **138 of 138** compared files byte identical, zero mismatches.
- **One record reported as incomplete, not verified:** a versioned PDF with no TeX members has no file list to compare, so it is excluded rather than counted as a pass.
- **7 fixtures, 6 of 6 mutations caught**, including two that would have reported success while checking nothing — treating an incomplete record as verified, and claiming verified while offline.
- **Coverage stated:** the byte level has been run over 4 of 36 receipt files. The rest are checkable by the same command and have not been run.

### Cycle 38 — the manifests asserted 190 files that were not there

- **Gap picked:** source receipts listed files whose existence had never been checked.
- **Measured:** 36 receipts, 127 records, **780 listed files**. **190 did not exist**, across 16 sources. No claim locator depended on any of them, but the manifests asserted their presence.
- **Repaired, not deleted:** every affected archive was re-fetched and accepted **only on a digest match**, then re-extracted. All 190 restored; zero missing afterwards. This also exercised the external-artifact policy on **16 sources** rather than the 4 spot checks recorded earlier.
- **Two conventions, both recorded.** Rewriting the lists to repository paths broke a receipt contract expecting archive member names; keeping member names left strings that look like repository paths. Both are now recorded, and the reference scan was made **structural** so it trusts the key rather than the shape of the string.
- **Failing-first check:** a placeholder value under a path-named key made the gate fire.
- **The clean clone caught the repair being incomplete.** Restoring the files locally left them uncommitted, because this worktree excludes the paper directory and only receipt-named files were being staged. The local run passed while the clean clone reported **298** dangling references. Tracked files under the source tree went from **484 to 782**, and the clean clone then reported zero. Restoring a file locally is not repairing the record.

### Cycle 37 — the rule was applied to the data that motivated it

- **Gap picked:** the new admission rule had never been applied to the blocks that produced the evidence for it. Exempting that data is how a rule becomes ceremonial.
- **Result:** of the **48** episodes in the pilot and variance blocks, **none is scorable**, for a single reason — their usage was never measured, so compliance cannot be shown. Only the **6** episodes run in structured output mode pass.
- **Nothing is retracted.** No score or effect was ever claimed from those blocks, and judged scoring was already inadmissible pending calibration, so the rule adds a second independent reason rather than overturning a claim.
- **What it does change:** the variance components and the allocation and minimum detectable effect derived from them are now labelled **provisional design inputs** taken from episodes that would not be admitted today. The confirmatory block must measure usage on every episode and re-derive its own allocation rather than inherit these numbers.
- **The reference gate caught a real ambiguity:** one upstream archive stores its sections under an internal directory named `paper`, so member names looked like repository paths and failed to resolve. Source receipts now record repository-relative paths, which removes the false reference *and* makes every listed file checkable.

### Cycle 36 — enforcement moved into the admission path

- **Gap picked:** ceiling violations were detected after the fact, which invites keeping a number that should not exist.
- **Executed:** the runner now records declared ceilings in the enforcer's vocabulary, and scoring is **refused** for five distinct cases: the episode did not execute, a pre-launch probe fired, its usage is unmeasured, it declares **no** ceiling at all, or it exceeds one. A non-integer ceiling is dropped at translation, which makes the episode inadmissible for lack of a limit rather than silently unlimited.
- **17 checks, 6 of 6 mutations caught** — after one fixture was rewritten. Its not-executed case was being blocked by a *different* guard, so deleting the execution-status check still passed. The receipt was made otherwise fully valid, and the mutation then fired.
- **All six measured episodes are scorable** under the retained ceilings.
- **Literature named the pattern:** production frameworks ship control primitives whose names imply barrier semantics but which do not stop anything — the failure this project has now met five times.
- **Retrieval note recorded:** the first candidate ranking returned mostly unrelated physics and mathematics records, so candidates were re-filtered on title relevance. The filtering step is recorded rather than hidden.

### Cycle 35 — the ceiling had no truth value until a quantity was named

- **Gap picked:** three declared ceilings enforced nothing. The choice was to implement or delete; I implemented.
- **Enforcement at admission,** since a provider call cannot be capped from outside. A committed module checks measured usage, **requires the quantity to be named**, and treats an unmeasured quantity as a violation rather than a pass. 16 fixtures, 5 of 5 mutations caught.
- **Applied to the six episodes with complete measured usage, the declared 32,000 gave opposite verdicts.** Read as **total tokens**: every episode inadmissible, exceeding by **4.7× to 20.3×**. Read as **marginal tokens**: every episode admissible, maximum **10,957**.
- **So the number had no truth value on its own.** The verdict is decided entirely by a quantity the protocol never named.
- **Total-token ceiling withdrawn**, not replaced with a guess, until it can be set from a measured distribution on the confirmatory task set. Marginal-token, call and wall-clock ceilings retained because measurement supports them.
- **Limit stated:** these maxima come from six episodes on one burned task and would not generalise.

### Cycle 34 — the declared ceilings enforced nothing

- **Gap picked:** the design constants were stated in prose and bound to nothing.
- **Derived, not restated.** Copying prose values into a receipt would have made the gate pass while proving nothing, so the constants were derived from the builder, the runner and the executed receipts.
- **The derivation contradicted the manuscript.** The paper described a *32,000-token ceiling, a 12 tool-call ceiling and a 45-minute wall time* as governing the work. All three governed nothing: the builder that produced every executed episode emits **no ceiling fields**, the runner only **type-checks** that a configuration declares them, and **no executed receipt records a token ceiling**.
- **What actually applied:** the pinned invocation at a fixed reasoning level with a **900-second** wall-clock limit and no token or call ceiling.
- **Corrected in the paper**, separating the specified confirmatory protocol from what the executed blocks applied, and the 900-second limit is now bound two-sidedly. 31 claim checks pass.
- **One source had no TeX**, so its text was extracted with the pinned `pdftotext` and the locator records that derivation rather than hiding it.

### Cycle 33 — coverage raised from 15 to 29 bindings, by refusing two

- **Gap picked:** only the headline numbers were bound; the reported figures in the results were not.
- **Executed:** 14 further two-sided bindings added, covering reliability, agreement, kappa, endpoint correlation, cost understatement, and the decision census. **29 checks now pass.**
- **Two candidate bindings were rejected, not forced.** One resolved to an episode *list* rather than a count and was rebound to a receipt that records the count. The other had no receipt field at all, and binding it would have required a wide tolerance around a different number — that is how a check stops checking.
- **Both directions still fire:** editing a reliability figure in the prose alone, and editing the same figure in the receipt alone, each fail the gate.
- **Coverage limit stated in the paper:** design constants and configuration ceilings stay unbound because no receipt records them. Partial and sound is preferred to complete and loose.

### Cycle 32 — the audit tool failed its own validity test

- **Gap picked:** only the abstract had numbers bound to receipts.
- **First attempt looked perfect and was worthless.** A matcher compared every body number against all 396 receipt values, allowing a factor of 100 either way, and reported **66 of 66 bound, zero unmatched**.
- **Then I tested the test.** Random numbers of the same shape were fed to the same matcher: it accepts **82.5%** of them. Expected matches under the null were 54.4 of 66, so the perfect score mostly measured how permissive the test was.
- **This is the same defect I falsified before**, in the same form: a high-recall filter presented as a decision procedure, exactly like the cue endpoint at a false-positive rate of 0.969. The matcher was rejected as a certificate.
- **Replaced by explicit two-sided binding:** a bound number names a receipt and a path, the rendered form must appear in the body, and the receipt must still hold the bound value. **Both directions fire** — changing the prose alone and changing the receipt alone each fail the gate.
- **Coverage is partial and said to be partial:** 15 checks bind the headline numbers; the rest of the body numbers are not individually bound.

### Cycle 31 — the abstract said the work had not been done

- **Gap picked:** the abstract was written before fifteen cycles of execution and never revisited.
- **It contradicted its own conclusions.** The abstract stated that "the pilot and confirmatory study have not been executed", while the conclusions of the same document reported three executed blocks. It also still named the endpoint that had been falsified.
- **Rewritten against the record:** the abstract now reports the three executed blocks, the falsified first endpoint at its measured false-positive rate of 0.969, the 14.4x cost-instrument understatement, the mutation audit that found four undetected fault classes, and the 28-decision census. It still states that no efficacy estimate exists and that judged scoring is inadmissible.
- **Gated, not just fixed.** Six checks now forbid non-execution phrasing while executed receipts exist and read headline counts from the receipts themselves. Three failing-first mutations all fired: reintroducing the non-execution claim, dropping the pilot episode count, and stating a wrong false-positive rate.
- **A duplicate source was caught by the commit guard.** This round re-ingested `arXiv:2608.25336`, which was already in the corpus under an existing bibliography key, producing a second locator, a second matrix row and a duplicate reference. The pre-commit validator refused on count mismatches; the duplicate was removed and the manuscript cites the existing entry.
- **Limit stated:** the gate checks only the numbers it is told about, so a new unbound claim in the abstract would still pass.

### Cycle 30 — a provenance hole, and a gate that verified nothing

- **Gap picked:** the path gate only covered experiment receipts. Extending it to the graph, protocol, locators and source receipts immediately found a dangling artifact.
- **Root cause is structural.** This checkout is a **linked worktree** whose shared exclude blocks the `paper/` directory, so files are tracked only when staged explicitly. Under that rule **911 paper files are tracked but zero source archives are** — every recorded archive path was absent from a clean checkout.
- **Resolution, not concealment:** upstream archives are external re-fetchable artifacts. The quoted evidence is committed as extracted text for **all 114** archives (419 tex files, 91 full-text and 114 report captures tracked). Every archive record must carry a fetch address and a digest.
- **Verified by re-fetch:** three archives and one PDF were re-fetched and reproduced their recorded digests **exactly**, including the originally missing PDF at 5,885,207 bytes.
- **My first gate verified nothing.** It scanned a character window around each reference, so a record could satisfy it by borrowing a neighbour's address and digest. The failing-first test stripped one record and **did not fire**. The check now walks the parsed structure so both must sit in the same record, and the same test then fired.
- **The clean clone caught two more gate defects.** The first version passed locally and failed in a clean checkout: the protocol's own prefix value matched as a reference, and an absent archive PDF was reported as both dangling and external. Both fixed, then re-tested by deleting the local PDF to reproduce the clean-checkout condition.
- **Limit stated:** a re-fetch depends on the upstream service still serving that version. The digest proves identity when a fetch succeeds; it cannot substitute for bytes if it does not.

### Cycle 29 — the analysis became code, and a dangling path surfaced

- **Gap picked:** the manuscript printed numbers produced by ad-hoc session work.
- **Executed:** the analysis is now a committed script with **22 fixtures** of three kinds — analytic cases whose components follow by construction, guard cases that must raise **with the correct cause**, and a regression case reproducing the earlier published receipt from the original record, an oracle that existed before the script.
- **Two implicit conventions are now explicit in the code:** coverage counts only an exactly satisfied verdict, and the effect uses the paired difference standard error.
- **Mutation audit: 5 of 5 caught**, but only after strengthening a guard fixture. One mutation removed the identifier guard and the code still raised, for a different reason, so the fixture passed. Guard fixtures now assert *why* an error was raised.
- **A dangling path reference was found.** A receipt named `paper/experiments/calibration/element-verdicts-corrected.json`, which does not exist; the real file is in the variance-block directory. A new gate scans **46 receipt files** for path strings that do not resolve, and was proven by reintroducing the bad path.
- **One source reviewed but not cited:** its TeX is a code-heavy conversion with no quotable prose, so no verifiable locator could be cut. Recorded rather than forced.

### Cycle 28 — the endpoint recomputed, and the check was wrong before the record was

- **Gap picked:** four verdicts changed, and the verified endpoint had been computed on the originals.
- **Validated the recomputation first.** A recomputation that has not reproduced the original is not a check. Running it on the original record reproduced the recorded variance shares and standard error exactly.
- **That step immediately paid.** The recomputed minimum detectable effect disagreed with the record, `0.0571` against `0.0808`. Deriving the quantity showed **the record was right and my check was wrong** by a factor of √2, because a paired difference of two condition means carries that factor. After the fix, every recorded value reproduced.
- **On the corrected record:** task share of variance rises **16.2% → 21.5%**, residual falls **83.8% → 78.5%**, condition and interaction remain **exactly zero**. Paired MDE moves `0.0808 → 0.0825`. Cue-versus-verified correlation falls `0.043 → 0.018`.
- **The structural conclusion is unchanged:** with zero interaction the standard error still does not depend on how a budget is split between tasks and repeats.
- **Limit stated:** four changed verdicts out of 192 is a small perturbation and says nothing about behaviour under a larger correction. The endpoint stays inadmissible for scoring until human labels exist.

### Cycle 27 — what confidence actually predicts, and a correction that carries its own counterevidence

- **Gap picked:** the modal rule was adopted for the low band, but the **mid band holds 112 of 192 judgements** and its treatment was undecided.
- **Measured, not assumed:** ten mid-band items over five repeats gave modal share **0.86**, close to the low band's **0.88**. Within-item stability does not separate the bands.
- **What separates them is representativeness of the recorded draw:** **9 of 10** in the mid band against **1 of 5** in the low band. So reported confidence predicts whether a single draw represents the item, not how concentrated the item's answer distribution is. The rule stays scoped below 0.7.
- **Applied:** five low-band records and five calibration key entries rewritten to modal verdicts; **four verdicts changed**. Every `unclear` verdict in the whole pool was a low-confidence single draw, and all three resolved to a definite verdict, so that category is now empty. Every original draw is retained beside its replacement.
- **Counterevidence recorded against my own new rule.** Majority vote has been shown to reduce per-problem accuracy on most hard problems for small models, and agreement can be high while the answer is wrong. The rule was applied to precisely the hardest items, so it could entrench a wrong answer.
- **The falsifier is written to revert it:** if the human labels agree more often with the original single draws than with the modal verdicts, the correction made the record worse.

### Cycle 26 — the items are labelable; the recorded draw was not representative

- **Hypothesis tested and refuted.** The previous cycle proposed that items below 0.7 confidence might be unlabelable. Repeating every low-confidence item five times, against five high-confidence controls, shows they are not.
- **Within-item stability:** low band mean modal share **0.88** (2 of 5 unanimous) versus **1.00** for the high-confidence controls (4 of 4). The items carry a stable answer.
- **What actually fails is the recorded draw.** It matches the item's own modal answer in only **1 of 5** low-band cases, and it returned `unclear` three times where repeats converge on a definite verdict.
- **The earlier claim was too strong and is corrected.** "Verdicts below 0.7 carry no reproducible content" is wrong as stated: the single verdict does not reproduce, the item's modal answer largely does. `RD-2026-09-02-30A` is now `REFINED_BY_MEASUREMENT`.
- **Consequences:** the three low-confidence items stay in the calibration set because a human can label them; and any recorded low-confidence verdict is replaced by a modal verdict over at least five repeats before comparison with a human label.
- **Limit kept in front:** agreement across repeats measures how concentrated an answer distribution is, not whether its mode is correct. A stable modal answer can still be wrong.

### Cycle 25 — the judged layer replays only where it is admitted

- **Gap picked:** the deterministic re-derivation could not reach judged verdicts, so their reproducibility was unmeasured.
- **Executed:** 24 recorded element judgements, sampled with a fixed seed and stratified across confidence bands, re-verified from the same artifacts with the same judge and the committed verifier.
- **Result by band, not in total.** Above 0.9 confidence: **10 of 10**. Between 0.7 and 0.9: **8 of 10**. Below 0.7: **0 of 4**. Overall 18 of 24; excluding two items that retrieved no span and so need no model call, 16 of 22.
- **The 0.9 admission floor is now measured, not just reasoned.** It was adopted in cycle 16 on reliability grounds; the band it admits replays perfectly here.
- **Verdicts below 0.7 carry no reproducible content** and must not be scored, rather than being treated as noisy but usable.
- **Three limits recorded:** replay is not correctness since no human label exists for these items; a disagreement cannot be attributed to judge stochasticity rather than item ambiguity from this design; and the low band held only 5 items in total.

### Cycle 24 — the recorded results were re-derived, not assumed

- **Gap picked:** every recorded score came from instrument code written before the mutation audit, so no recorded number had been checked against the audited instruments.
- **Executed:** the deterministic quantities of both blocks were re-derived from the retained artifacts. Re-running would have spent frozen tasks without testing the recorded numbers at all.
- **Both blocks matched exactly.** Variance block `32 / 0 / 0 / 26`, pilot block `16 / 0 / 0 / 13`, each equal to what was recorded.
- **Independent canary scan:** every retained design and state artifact was scanned against all eight per-task withheld canaries read from the **task bundles**, not from the receipts. No leak.
- **The new tool was defective on first use.** Its filename pattern required a repeat suffix, so it matched nothing in the pilot block and reported zero leaks and zero redlines — which reads as a pass. It now raises on an empty match, with a fixture for that case, and all five injected mutations are caught.
- **A fixture asserted my assumption again:** a sample artifact was declared clean when it did not satisfy all five structural checks. The sample was corrected, not the check weakened.
- **Boundary stated, not implied:** judged element verdicts depend on a model call and are outside this check.

### Cycle 23 — the last three instruments got suites, held to the same standard

- **Gap picked:** three instrument modules had no paired suite at all — the adversarial validity check, the pilot builder, and the element verifier.
- **Executed:** all three now have suites whose expected values come from each module's stated contract, not from its current output. Then **21 further mutations** were injected.
- **20 caught.** The 21st was shown by executing both variants side by side to be an **equivalent mutant**: the branch it changed cannot produce a different result once the evidence directory is absent. No fixture was invented to force a difference that does not exist.
- **A new fixture was wrong in the same old way.** It asserted the judge's model selector is shell quoted; a safe selector is correctly passed through unquoted. The assertion was my assumption again, and it was replaced by a check on an unsafe selector.
- **The judge has no reliable oracle**, so its suite asserts the deterministic shell around the model through an injected runner and never makes a live call.
- **No instrument module now lacks a suite.** The honest limit stands: a mutation set chosen by the author of the code can still miss a fault class that neither the code nor the mutations consider.

### Cycle 22 — the instruments were audited by mutation, not by reading

- **Gap picked:** one instrument had been wrong while its suite passed, so no other suite could be trusted on inspection alone.
- **Executed:** 17 semantic mutations, one at a time, across six instrument modules, each paired suite run, each module restored and digest-checked.
- **13 caught, 4 survived.** Three survivors were in scoring: an episode with a dimension scored zero could pass as fatal-error-free, a fabrication redline could stop blocking that endpoint, and the carry-through ratio could exceed one.
- **The fourth survivor was the worst.** The release sandbox could report a workspace **admissible while a probe had fired**, neutralising the entire fail-closed admission gate, and every test still passed.
- **Five fixtures added; all 17 mutations then caught.**
- **A defect in the test harness itself surfaced:** the scoring suite computed its pass tally *before* the newly added checks ran, reporting 14 of 18 while every check passed. The tally now runs last.
- **Literature named the defect class:** an oracle that takes its expected value from the system it judges cannot fail, because a fault moves measurement and expectation together. That is exactly how the cost fixture protected a wrong parser.
- **Two limits recorded:** catching 17 mutations does not show the instruments are correct, and three modules still have no paired suite at all.

### Cycle 21 — the instrument was wrong, and its own fixture protected the error

- **Gap picked:** whether retrieval context cost is chosen by the agent. Answering it required reading the transcripts, which exposed something worse.
- **The cost parser was wrong by 14.4x.** It summarised a run by its last usage record, assuming usage accumulated. Usage is reported **per completed API call**, and a multi-turn episode re-sends its context on every call, so the last record describes one call. Output tokens were understated 13.0x.
- **The fixture protected the defect.** It asserted that the last record was the run total, which is what I believed rather than what the transcript does. The suite passed while the instrument was wrong. A fixture that encodes the author's assumption tests the assumption, not the system.
- **How it surfaced:** the earlier run had already recorded `monotonic: false` on all six episodes. That signal was written down and not acted on. It was only chased when an unrelated question forced a look at the records.
- **Two further defects during repair.** Transcripts captured through standard output were truncated in **four of six** runs, losing middle records; transcripts are now written to files and checked for completeness. And the first repair swallowed every record after a truncation, caught by a failing-first fixture before use.
- **Every cost number from cycles 18, 19 and 20 is void**, including the fixed floor, both context figures, and both variability figures. The three affected decisions carry `VOIDED_BY_RD-2026-09-02-26A`; their structural content stands, their numbers do not.
- **Re-measured from complete transcripts:** minimal condition 167,251 total tokens over 3.3 calls; full condition 520,969 over 9.7 calls, a ratio of 3.1. Both vary widely, at 16.6% and 34.0%. No factor attribution: two factors move together, three repeats each.

### Cycle 20 — one episode is a draw, not a value

- **Gap picked:** cost was being reported per episode without ever testing whether a single episode is stable.
- **Executed:** six episodes on one burned task, three repeats per condition, with **identical workspace digests inside each condition**, so any spread is not workspace drift.
- **Result:** the minimal condition varied by **2.90%** around 51,138 context tokens; the retrieval condition varied by **11.34%** around 79,320. The retrieval within-condition range of 17,231 tokens covers **61.1% of the gap between conditions**.
- **The falsifier of `RD-2026-09-02-24A` fired for one condition.** That decision is now `REFINED_BY_MEASUREMENT` and `RD-2026-09-02-25A` replaces it: every cost quantity is a mean over repeats with its spread, never a single episode, and the retrieval condition needs more repeats than the minimal one.
- **A mechanism is offered as a hypothesis, not a result:** with retrieval available the agent chooses how much of the evidence pack to read, so context cost may be partly an outcome of its behaviour. Testing it needs per-episode read instrumentation this design does not yet have.
- **Consistency check passed:** the two single episodes from the previous cycle fall inside the ranges measured here, so the earlier numbers were not outliers.

### Cycle 19 — the previous cycle's cost decision was falsified by its own falsifier

- **Gap picked:** the cost instrument had only ever been validated on synthetic probes in an empty directory.
- **Executed:** one burned pilot task was run once in the minimal condition and once in the full condition, same pinned backend, structured output mode.
- **The falsifier of `RD-2026-09-02-23A` fired.** That decision claimed a fixed context floor of 46,763 tokens. Real episodes measured **51,596 and 76,496 context tokens**, a difference of 24,900, with totals differing by a factor of **1.487**.
- **Diagnosis:** the probes ran in an empty directory, so they measured harness context alone. A real episode also carries its mounted workspace, and the full condition mounts an evidence pack of 145,906 bytes. The floor was an artefact of how the instrument was probed.
- **Recorded as falsified, not amended.** `RD-2026-09-02-23A` now carries `FALSIFIED_BY_MEASUREMENT` and `RD-2026-09-02-24A` replaces it: context tokens and marginal tokens are reported separately, neither treated as constant, dollar cost still excluded.
- **Attribution limit stated, not implied:** the two episodes differ in both factors at once and each ran once, so nothing here attributes cost to retrieval or scaffold separately. One run scores one implementation, not an idea.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One discovery primitive returned nothing for the third objective; that is recorded rather than hidden by rewording the query.

### Second near miss — a receipt made stale by editing after validating

The clean-clone run failed while the working tree passed. Cause: the cost ledger was written **after** the validator had already run, so its committed receipt was stale by one edit. The working tree agreed with itself and proved nothing. The commit path now refreshes receipts, re-runs the validator, and refuses to commit on a failing gate, so "edit after validating" can no longer reach a commit.

### Cycle 18 — cost stopped being a proxy, and the measurement overturned the plan

- **Gap picked:** the pilot recorded token accounting as `UNMEASURED` and kept wall-clock duration as a proxy, which cannot support any budget-matched claim.
- **Executed:** the runner was switched to structured output mode and a committed parser with **11 fixtures** now reads the usage stream. One fixture exists because usage is reported repeatedly and grows, so summing records would overcount; the parser takes the final cumulative record and checks monotonicity rather than assuming it.
- **The measurement changed the plan.** Three probes on the pinned backend showed a **fixed context floor of 46,763 tokens, identical in every probe**, against work of 39 to 384 output tokens. Dollar cost for the *same* trivial task differed by **12.03x** between a cold and a warm cache.
- **Consequence:** cache state depends on execution order, not on the condition, so dollar cost is inadmissible for comparison; and a contrast measured on total tokens would be about one percent of the reported number. Cost is now reported as marginal input plus output, with the floor stated separately (`RD-2026-09-02-23A`).
- **A condition on any future effect claim was recorded, not deferred:** augmentation gains have been shown to vanish against a token-matched baseline, so a comparison here must be budget-matched rather than merely condition-matched.
- **First model cost entered the cost ledger** — three probes totalling $0.07. GPU credit units remain 0.

### Cycle 17 — the calibration set is complete and provably blinded

- **Gap picked:** the calibration set stood at 22 of 25 items, three short in the low-confidence stratum, and judged scoring stays inadmissible until it is complete.
- **Executed:** exactly three unused low-confidence judgements existed in the verdict pool, which is the number required. The set now stands at **25 items in the intended 10 / 10 / 5 stratification**.
- **Two defects found by checking rather than assuming.** The three added items lacked the `answer`, `labeller`, `labelled_at`, and `notes` fields the original items carry, and they were not joined to the blinded key. Both were fixed and every item now shares one field set and resolves to exactly one key entry.
- **Blinding verified mechanically:** no item carries a judge verdict, judge confidence, episode id, or element id. The word `confidence` does appear inside candidate passages, and was checked to be ordinary statistical wording rather than leakage.
- **Still inadmissible, and said so.** No labels have been collected. `Q-0006` is updated to 25 items and stays non-blocking; the loop continues on its default, and judged scoring remains barred until real labels certify the risk bound.

### Near miss recorded — a passing run that proved nothing

While closing cycle 16 the staging list named a manuscript path that does not exist. `git add` aborted, **nothing was staged**, the commit failed, and the validation run then passed against the *previous* commit. The pass was real and worthless: it validated work that was not in the repository. The tell was `submission_artifact_rebuild` coming back empty, because the old commit had no rebuild check. The loop now refuses to continue when the head does not move after a commit, and a run is only accepted as evidence for work that the head actually contains.

### Cycle 16 — the process claim is now a number, and reproducibility is enforced

- **Unit 1, reproducibility enforced.** The clean-clone comparison was folded into the validation gate: every run rebuilds the artifact from its committed builder into a temporary path and fails when the digest differs. Proven by tampering with one word in the committed artifact, which produced `reproducible: false` and a gate failure; restoring returned it to pass.
- **Unit 2, the self-correction claim measured.** The method claimed a loop that corrects itself but never quantified it. A committed script with eight fixtures now censuses the decision ledger: **28 records across 15 groups, all carrying falsifiers written before the result, 20 with executed evidence, and 3 revised**, a revision rate of `0.107`. All three revisions were triggered by the project's own executed measurements, not outside review.
- **Two limits recorded with the number.** The census counts the ledger that records the decision to run it, so it is reported against a stated ledger digest rather than as a constant. And a single project without a comparison group cannot show that writing falsifiers *caused* the revisions.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One names this project's ceiling directly: gates and receipts are operational rigor, which substitutes for understanding rather than supplying it. That sentence is now in the manuscript as the boundary of the contribution.
- **Two real defects fixed while integrating:** the new citations used the wrong macro so first-citation ordering silently passed on 3 of 60 entries, and adding a subsection before the Conclusions renumbered two later references. The bibliography was reordered programmatically to the true first-citation order.

### Cycle 15 — the artifact was not reproducible, and now is

- **Gap picked:** the artifact digest was pinned in the receipts but the artifact had never been rebuilt anywhere else, so the pin proved a machine rather than a build.
- **Measured first:** a clean clone at the same commit rebuilt the artifact to a **different digest**. The pinned receipt would have failed for any independent verifier.
- **Diagnosed from the bytes:** exactly one part differed in content, `docProps/core.xml`, carrying created and modified timestamps, and every zip entry carried the build time.
- **Fixed and re-measured:** every packed entry timestamp and both document-property timestamps are pinned to the epoch already used for the deterministic PDF, and parts are written in sorted order. A repeat build on this machine and a rebuild in the clean clone now produce the **same digest** `15a69f22`.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One sharpened the goal: reproducibility alone is not verifiability, because a verifier must also recover the source state and build instructions, which is why the builder is committed beside the artifact rather than only its digest (`RD-2026-09-02-21A`).
- **Honest ceiling recorded:** attested builds bind artifacts to their environment with hardware support this project does not use, so this is reproducibility without attestation.

### Cycle 14 — the artifact format is now guarded, not merely asserted

- **Gap picked:** the builder asserted numerals, spacing, page numbers, and citations, but nothing stopped a later rebuild from silently dropping them. A property asserted only by its producer is unguarded.
- **Executed:** the checks moved into the deterministic validator, which now re-derives title, front matter, chapter numerals, summary length, keyword count, double spacing, page numbering, citation numbering, and forbidden names from the artifact bytes on every run.
- **Proven by mutation, not by assertion.** Five deliberate corruptions each failed the gate: removing the footer, switching to single spacing, stripping the numerals, deleting the citations, and inflating the summary past its limit (`korean summary length 662`). Restoring the artifact returned the gate to pass with a matching digest.
- **One imprecise message recorded rather than hidden:** a crude sixth mutation that merged text into the keyword paragraph still failed closed but reported a less precise reason, so it is not counted as a clean length test.

### Cycle 13 — the inherited format properties were all missing

- **Gap picked:** Roman numerals, double spacing, and page numbers were inherited from a reference document and had never been checked. Assuming them would repeat the earlier mistake of trusting an unverified inheritance.
- **Measured from the artifact parts, all three were absent:** chapter headings carried no numerals, no line spacing was set anywhere, and the file had **no footer part at all**.
- **Implemented in the committed builder** so every rebuild reasserts them: chapters numbered I to V with the Korean front matter deliberately left unnumbered, double spacing written into document defaults, and a page-number footer wired through the footer part, relationship, content-type override, and section reference (`RD-2026-09-02-19A`).
- **Re-verified from bytes after the rebuild:** five Roman chapters, front matter unnumbered, `w:line=480` in defaults, footer with a PAGE field, 57 bracketed citations, zero forbidden names, and the artifact re-opens cleanly.
- **Honest limit:** the word processor PDF export still does not complete unattended on this machine, so what the parts declare has not been confirmed against a rendered page. The deterministic toolchain PDF remains the visual reference.

### Cycle 12 — the submission artifact is now complete and correct

- **Gap picked:** the Word artifact was missing the required Korean summary and keyword line.
- **Constraint discovered first:** the pinned LaTeX toolchain has no CJK font, so embedding Hangul in the source would break the deterministic PDF that every evidence claim rests on. The source stays ASCII and the build injects the front matter from its single side file, failing if the summary exceeds 500 characters or the keywords exceed five (`RD-2026-09-02-18A`).
- **First attempt was worse and was rejected.** A markdown round-trip carried the Korean text but dropped the title and citation markers, so it was discarded in favour of the direct conversion with an XML-level injection.
- **A real defect was found in the artifact:** the converter dropped every in-text citation, leaving dangling punctuation such as "correctness alone ;" where a reference belonged, in violation of the official bracketed-citation requirement. The build now materialises the same first-citation numbering the validator enforces; **57 citations render** and the reference list has 57 entries (`RD-2026-09-02-18B`).
- **Verified from the artifact's own bytes**, not from the converter: title present, `국문 요약` at 361 of 500 characters, 5 of 5 keywords, section order Introduction → Related Works → Proposed Method → Experimental Results → Conclusions, zero forbidden public names.
- **Open:** page numerals, spacing, and page numbers inherited from the reference document remain unverified, the application PDF export still times out, and display equations render as TeX text.

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
