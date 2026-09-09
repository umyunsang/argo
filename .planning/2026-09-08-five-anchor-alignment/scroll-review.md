# Scroll fresh primary-source review

Status: complete primary-text reading; design synthesis only; no experiments or implementation.

## Source and read receipt

- Paper: Yin Lin, Elaine Ang, Erkang Zhu, Bolin Ding, Jingren Zhou. *Context as an Environment: Programmatic Context Management for Long-Horizon Agents*. Technical report, arXiv:2608.21690v1, 21 August 2026. Official identity: https://arxiv.org/abs/2608.21690v1.
- Local source: `sources/2608.21690v1.txt`.
- SHA-256: `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`.
- Extent: 98,884 bytes; 2,070 LF lines; 37 printed pages.
- Reading: every LF line, 1–400, 401–850, 851–1250, 1251–1660 and 1661–2070; main text, references, benchmark rubrics and all four example trajectories/code listings. Targeted locator checks followed the full read.
- Scope limitation: text extraction read in full; PDF layout and source-code repository were not audited; no reported result was reproduced. Prior review verdicts were not read or inherited. Historical-memory search returned no Scroll-specific evidence and supplied no paper claims.
- Current project authority checked: `AGENTS.md`, `docs/argo/agent-brief.md`, `docs/argo/migration-state.json`, and this plan's `task_plan.md`. The agent brief verifies inherited persistent REPL/RLM/session recovery and the construction pause. It does not constitute an independent Prime implementation audit.

All LF locators below refer to the frozen local source above. “Direct” means the source says it; “inference” means a design consequence or an evidentiary limit, not an experimentally verified result.

## Mechanisms and agent agency

| Mechanism | What the paper actually provides | Locator |
|---|---|---|
| Executable session state | State is an event log, payload storage and derived resident state. A model-written program selects the next bounded working view at query time. | §2.1, LF 229–288 |
| Exact historical addresses | One append-only SQLite log spans sessions; events have role, session/agent identifiers, timestamps and tool-state metadata plus immutable monotone `seq` addresses. BM25 search is the default and needs no index-time model calls. | §2.2, LF 325–331 |
| Payload indirection | Small payloads stay inline; large ones move to JSON/artifact storage with previews and lazy recovery handles. A log record and a full payload are distinct objects. | §2.2, LF 332–338 |
| Persistent executable state | A sandboxed Python kernel retains typed variables and lazy handles across model calls within a session. A namespace digest gives names/types/shapes and small scalars. The kernel sees a read-only Event Log and only declared capabilities. | §2.2, LF 339–348 |
| Model-controlled observation | `ms.search` locates, `ms.expand` materializes exact records/payloads, Python computes, and explicit `print` chooses the substantive observation. The model also receives fixed prompts, active turns, namespace digest and eviction index; “print-only” describes the tool-result observation boundary, not literally every possible state channel. | Table 1, LF 295–307; §2.2–2.3, LF 339–406 |
| Recoverable eviction | Above `rho*C`, persist live turns; protect active turn/recent tail/newest tool results; fold completed payloads to pointers; remove old complete spans only if needed. Removed records remain addressable. | Algorithm 1 and §2.4, LF 387–429 |
| Navigation over evicted history | Model-generated response headlines capture task, verified state, next action and status. They bind to exact `seq` addresses and form a tiered index: recent detail, older coarse ranges, asymptotic `O(k log_k n)` blocks. | §2.4, LF 419–429 |

The acting model decides what to retrieve, compute, retain in variables and expose; the harness manages execution/storage boundaries. The same agent retrieves and answers, with no separate reader. Scroll does not prescribe research objectives, research-plan revision, independent scientific judgment, task decomposition or a hierarchy of root/subagents (§4.1–4.2, LF 512–513 and 559–563). Calling that acting model the “root” is an architectural mapping for this project, not a term or new hierarchy established by Scroll.

## What lossless does and does not establish

Directly supported: eviction does not destroy the original events/payloads; summaries and indexes remain navigation views instead of the sole evidence representation (§2.4, LF 409–429; §5, LF 700–728).

The log is historical ground truth about recorded interactions. It does not make a recorded assistant statement, experiment interpretation or user assertion true about the world. Provenance and ordering support checking these distinctions; they do not replace checking them. Appendix C explicitly distinguishes user facts from assistant suggestions, and Appendix D.2 checks this distinction (LF 968–979, 1017–1028, 1303–1328).

The source's own failures separate storage from successful use:

- Wrong question decomposition: fourteen searches pursue mapping tools without querying the toll-avoidance constraint, even after a toll-related hit appears. The records exist and the code works, yet preference-following scores 0.0 (D.3, LF 1476–1609).
- Incomplete projection after complete retrieval: all 4,448 events in the requested range are paged/merged, but head/tail sampling omits middle-of-session driving, sleep and hydration evidence. Summarization scores 0.42 (D.4, LF 1686–1695, 1775–1838, 1878–1899).
- LongMemEval degrades from 94.8 on S to 89.6 on M, with missed multi-session evidence; BEAM multi-session reasoning remains 21.9 (A.1–A.2, LF 852–924). These are source-reported results, not this review's reproduction.

Therefore lossless retention does not guarantee finding all relevant records, selecting the correct semantic axis, printing sufficient evidence, terminating at the right point or making a valid scientific decision. The paper also does not establish crash-consistent namespace restoration, storage-corruption recovery, cross-worker execution semantics or months-long autonomous project continuity. The memory protocol carries the Event Log and eviction index across session boundaries; it does not claim that the same Python variables survive those boundaries (§3.3, LF 480–484). These are unmeasured limits, not observed implementation failures.

## Evidence strength and fair comparisons

| Result | Supported reading | Main constraint |
|---|---|---|
| LongMemEval S 94.8; BEAM 10M 73.1 | Reported Scroll scores. The BEAM lead over published Exabase M-1 is 5.1 points. | Table 2 is explicitly uncontrolled: different reader models, retrieval budgets and judges; baseline runs were not reproduced. Scroll is below the best listed LongMemEval score, 96.4. LF 493–540. |
| LOCA 128K/256K: Scroll 89.3/86.7; CodeAct 89.3/85.3 | Same Qwen3.8-Max and toolset; the closest comparator already uses programmatic tool calling. Scroll's incremental accuracy difference is 0 and 1.4 points, respectively. | No confidence intervals or quantified repeat variance accompany Table 3. Exact resource parity cannot be reconstructed from the paper alone. LF 541–558. |
| LOCA 256K 86.7 vs published 49.3 | A system-level 37.4-point gap is reported. | Different models; it does not isolate the effect of Scroll. Appendix B, LF 926–939. |
| BEAM ablations | Discarding originals: 19.9 overall. Removing REPL: minus 7.3 points. Removing eviction index: minus 1.8 points. | Summary-only deletion is a strong information-loss intervention; it does not establish superiority over every raw-log-preserving summary/retrieval alternative. Ablations concern BEAM, not research projects. LF 605–637. |
| Six fixed-harness backbones | LOCA 256K ranges 22.7–86.7; weaker models have more execution errors or early termination. | Shows backbone sensitivity under the supplied harness, not universal benefit from any future model upgrade or scientific validity. LF 559–619. |

Evaluation and budget details that must travel with any reused claim:

- One shared system prompt/rule set, no few-shot demonstrations, but benchmark-specific memory rubrics include data layout, search guidance, temporal/provenance conventions, abstention and final-answer instructions (§3.2 and Appendix C). “No few-shot” is not “no benchmark-specific guidance” (LF 471–478, 941–1049).
- LongMemEval/BEAM use benchmark judge prompts with Qwen3.6-flash at temperature 0; LOCA uses its native rule-based final-state verifier. Each task is evaluated once with a random seed unless otherwise noted (§3.3, LF 485–490). Appendix A mentions consistent profiles across repeated runs without a quantitative repeat protocol or uncertainty estimate (LF 923–924).
- Cost figures cover memory retrieval alone for LongMemEval/BEAM and full task completion for LOCA. They are not interchangeable end-to-end research costs. BEAM median model-facing input is 105K, about 1% of its 10M history. The report gives tokens/turns, not comparative latency or monetary cost (§4.4, LF 686–698).
- Example traces expose a 32,000-character observation limit and a 1,000-row SQL result cap. Paging and re-filtering resident variables can recover from these limits, but the caps can affect coverage (D.1, LF 1123–1145; D.4, LF 1700–1732). These are example implementation limits, not complete reported evaluation budgets.
- The paper specifies `rho*C` and tier width `k` symbolically; it does not numerically disclose all live-view, roll-up, total-token, turn, compute, storage and timeout budgets needed for an equal-budget reproduction. Do not infer that LOCA's 256K environment-description size is the actual prompt limit.

A fair follow-up needs the same base model/reasoning setting, tools, data access, task/evaluation cut, context/observation caps, total model and tool-compute budget, termination policy and independent evaluation across compared configurations. Charge ingestion/index maintenance and retrieval where applicable. Separate best-quality comparisons from equal-budget comparisons. Record repeated outcomes and confidence intervals where claiming small differences. This is a proposed measurement design, not a statement that the paper implemented it.

## Role among the five anchors

This source supports Scroll as the **within-project evidence-continuity and executable working-state layer** of sustained autonomous research. The root research agent can revisit exact tool results, failed approaches, revisions and evidence after context eviction, choose the next research action and compose an auditable view. An outer project/research loop can use those records for review and revision. The research question remains how an externally supplied frontier model sustains valid autonomous research; context storage is one mechanism within that question.

| Adjacent role | Complementary contribution | Redundancy or unresolved interaction |
|---|---|---|
| Prime persistent REPL and programmatic context | Stable historical addressing, lazy exact payload recall, tiered navigation and provenance-aware context construction can specify stronger history access around the inherited execution substrate. | A second persistent Python kernel would duplicate an inherited function. Existing transcript/payload/recovery owners should be mapped before any implementation; no migration is authorized now. Prime-side fact is from current agent brief LF 11–18, not a code audit. |
| Prime RLM/subagents | Root/subagent decisions could point to recoverable shared or scoped events while delegated programs process large evidence. | Scroll does not test recursive delegation, cross-agent consistency, ownership of derived state or long-term subagent lifecycle. A log plus RLM is not an empirically established combination in this source. |
| Harness-of-Harness outer project/research loop | Recall the exact trajectory and artifacts that a project-level reviewer or steering loop needs before setting the next objective or revision. | Scroll supplies neither that controller nor its evaluation policy. HoH-side role comes from the assigned five-anchor framing; this lane did not reread HoH. |
| RecEvolve/HarnessDev harness revision | Preserve concrete failure and success records so an outer improvement process can inspect the experience behind candidate harness changes. | Addressable records are not an evaluator, a candidate-selection procedure or evidence of generalizing improvement. Those papers require their own primary reviews; no claimed compatibility effect here. |

The useful integration principle is one native execution/lifecycle authority with explicit historical access, plus root-directed scientific choices and separately evaluated outer revision. This is an architectural inference awaiting measurement, not a prescription to wrap or replace Prime.

## Research questions worth measuring

These are subordinate mechanisms of long-horizon autonomous-research methodology, not a decision to make memory storage the thesis topic.

1. **Preservation to scientific progress:** At fixed model and total research budget, does addressable history with navigation improve correct continuation after revisions/interruptions and independently validated research progress over the already-programmatic Prime/CodeAct baseline? Measure evidence recovery, erroneous repetition, useful completed research decisions and end-artifact validity; byte retention alone is insufficient.
2. **Coverage and stopping:** When evidence is available, which root-agent policy detects an omitted question dimension or an incomplete projection before a research decision? Measure coverage of independently defined decision-relevant evidence, justified abstention, missing counterevidence and marginal cost of additional retrieval. Avoid scoring only the agent's self-reported confidence.
3. **Context policy with outer revision:** Does targeted review of exact failed decision traces cause better research-plan correction than more retrieval or a longer summary alone? Evaluate the resulting hypothesis/design/experiment choices, preserve failure provenance, and include unsuccessful revisions in cost. This tests the connection to outer loops rather than assuming the connection is beneficial.
4. **Frontier-model substitution:** With weights fixed within each run and the harness held constant, which context/programming/termination failures improve with a stronger external model, and which persist? Evaluate at least one different backbone when authorized; the source motivates interaction measurement, not an assumption that every model benefits equally.

The paper ends with proposed supervised fine-tuning/policy distillation of context retrieval/injection from frontier traces (§6, LF 730–737). That is future work in the source and outside this project's fixed-frontier-weight scope. The current harness mechanisms and research questions can be studied without weight training.

## Handoff

Directly supported: executable session state, exact event/payload recovery, model-owned context policy, indexed eviction, controlled CodeAct proximity, benchmark/evaluator limits and retrieval/projection failure modes.

Inference only: the proposed placement within a native autonomous-research architecture and possible cross-anchor interactions. Insufficient evidence: any claim of end-to-end scientific research superiority, lossless scientific understanding, uninterrupted project autonomy, causal five-component synergy or implementation-ready integration.

No native/runtime files, credentials, experiments or external resources were modified. Deliverables are only this review and `scroll-review.json`; root owns overall plan/progress synthesis.
