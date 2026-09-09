# Findings

## Initial authority observations

- The project rules state that ARGO construction is paused; thesis research and test-instance validation are authorized, while native runtime changes require passed validation/resume gates and an explicit user restart.
- DeepVoice is the active second test instance. LG Aimers must remain stopped and read-only.
- Search snippets are not sufficient evidence for paper claims; selected papers must be read before claims are bound.
- The working tree already contains numerous untracked `experiments/study_b/` block outputs, harness extensions, prompts, and a test file. They predate this audit and must not be modified or staged.

## Live Prime Agent evidence

- Prime Agent version is 0.9.1. The active top-level `argo-paper-root` is session `01a05f13-5001-77c8-8530-d92634405424` / active id `d522d196a0c1`, model `claude-opus-5`, thinking `high`.
- The listing reports cwd `/Users/um-yunsang/argo/lgaimer`, while its session header records `/Users/um-yunsang/argo-paper-orx`; this identity drift must be explained before treating cwd-bound receipts as clean.
- The current branch is `orx/integrate-harness-evaluation-counterevidence-and`, head `2d166c113`. The session committed and reported push success before launching a clean-clone OpenResearch validation run.
- The newest local validation run produced an empty log; the session's JSON extraction failed and it began diagnosing/relaunching. This is an execution-state failure, not paper-validation PASS.
- The UI's long `Waiting` state was a false-working condition: run `53cba191-407c-47d5-8277-1839c7e5c2e4` had a dead recorded PID (`79434`) and a zero-byte log, while a surviving `orx exp wait` process waited indefinitely on its stale `running` state. No actual run/validator worker remained.
- Only the exact orphaned `orx exp wait` process was terminated. Prime Agent, daemon, session transcript, IPython kernel, files, and prior results were preserved. The tool call then returned and the queued hold instruction was delivered at 2026-09-04 15:17 KST.
- Current status claims signed-document realignment and a four-branch combined design, but also shows T1-prime block execution at 19/120 episodes and an approved spend envelope. Further paid execution should be held until the new root design and existing protocol are reconciled.
- A hold instruction was queued successfully through Prime Agent's generic `send_message` path. The installed 0.9.1 CLI advertises `--steer`/`--follow-up` for `send`, but the installed parser rejects both flags; this is a CLI contract defect, not evidence that the user declined the intervention.
- After the hold was received, the session entered `orx exp wait` once more on the same stale run. The run still reported `running` after about 53 minutes, but its recorded PID `79434` was absent and its log remained zero bytes. The exact new wait process was terminated; Prime Agent then performed its own liveness check, confirmed `pid_alive: false`, and moved to the requested read-only inventory without relaunching work.
- At the latest check the top-level session remained live and streaming, with no Bash command and no tool process running. This is active reasoning/inventory work, not another blocked wait. Additional paid episodes, ablations, T1-prime, protocol mutation, commits, and pushes remain held.
- Prime Agent twice more used blocking `orx exp wait` while attempting a final status check, even after its own liveness check showed the worker PID absent. Each exact wait process was terminated without touching the daemon, session, run directory, or artifacts. A follow-up explicitly forbids further waits on this orphaned run and requires non-blocking `orx exp status` only.
- Its read-only inventory found 48 on-disk T1 receipts for one task (`t1/task5`), three arms, and 16 seeds per arm; 25 are untracked and 23 committed. The receipt set contains no `origin`, `model_id`, or protocol fingerprint and reports zero model-call records, so the labels `CONFIRMATION_EPISODE` and apparent costs/tokens do not establish admissible executed evidence.
- The T1 endpoint is at floor: B0 0/16, B1 1/16, B2 0/16; B2-vs-B0 has zero discordant pairs. Even if execution provenance were repaired, one task repeated over seeds cannot support task-population generalization, and the endpoint cannot distinguish the arms.
- The implemented T1 block maps only the single-agent baseline to B0. It does not execute the declared design-competition or refine removals, and none of the signed application metrics (evidence-link completeness, duplicate proposal rate, resume consistency, human interventions) has a directly valid receipt field.
- After returning the inventory, the persistent goal automatically started further continuations despite the explicit HOLD. The saved top-level session was therefore stopped with `prime-agent stop`; current live flags are `isSessionActive=false`, `isStreaming=false`, `isRunningTools=false`, and `unfinishedActionCount=0`. The session JSONL, daemon, working tree, untracked receipts, and prior results remain preserved for resumption after the revised directive is ready.

## PDF lane preliminary result

- Both PDFs were fully text-extracted and visually inspected by the dedicated lane: the graduation plan is 1 page; the signed NAIS application is 7 pages.
- The documents are thematically aligned, but the current design is not causally closed: four implementation strands do not map one-to-one to promised ablations; current metrics emphasize process/provenance over scientific-output quality; and a single hackathon execution cannot support repeated-trial or variance claims.
- Any claim that preliminary experiments are complete must be separated from the signed pledge that no pre-developed competition artifact will be imported.

## Official competition page retrieval

- Direct retrieval of `https://ai4scikorea.org/` succeeded with HTTP 200 on 2026-09-04. The static metadata identifies AI for Science Conference 2026, Seoul Dragon City, 2026-09-27 through 2026-10-01, and frames the conference around AI agents for research and ML for domain science.
- Competition-specific content is bundled in `/assets/index-CBWg0NOf.js`; it was not present in the base HTML. The prior browser tool's empty output is therefore not evidence of absence.
- The official competition section describes an idea-and-prototype competition for R&D-specialized AI agents, not a completed-system benchmark. The main event is 2026-09-30 17:00 through 2026-10-01 12:00 at Seoul Dragon City; the currently published page still says application details are TBD and links the application form.
- The official page provides no technical judging rubric or claim that a single event run demonstrates SOTA. Therefore the NAIS deliverable should be treated as an MVP/functionality demonstration, with thesis efficacy claims reserved for the preregistered repeated experiment.

## Canonical boundary findings

- `migration-state.json` is stale relative to the live worktree: it records branch `argo/migration-foundation` and update time 2026-09-02, while the live branch/head have advanced substantially. Its construction prohibition remains explicit, but its dynamic research status cannot be treated as current.
- The public thesis must exclude internal product lineage/control-plane details. Product inspirations can guide design internally; public claims require published primary sources and executed scoped evidence.
- A component name, aggregate graph, or integrated feature list cannot establish originality. The contribution must be an isolated residual mechanism with prior-art comparison and executed ablation.

## Current design contradictions

- `ROOT-research-direction.md` defines the target as an optimum combination of four strands: persistent REPL recursion, trajectory-based harness updates, isolated immutable execution, and semantic literature search. Its declared removals instead target graph, design competition, refine, and a single-agent baseline. These are not one-to-one factors.
- `research-design.md` still defines a different 2x2 causal model: structured protocol/state (`S`) by dynamic retrieval (`R`), with C00/C01/C10/C11. It does not test the four root strands or dual-refine separation.
- Study B's B0/B1/B2 comparison and planned B2-G/B2-P/B2-R removals form a third treatment model. Combining results from these three incompatible designs cannot support a single optimum-configuration claim.
- `proposal-alignment-map.md` marks design documents, graph counts, and prototype specifications as `satisfied` evidence for development and autonomous efficacy. This confuses artifact existence with implementation, mechanism activation, causal effect, or acceptance; the `10/11 satisfied` summary is not defensible.
- `research-design.md` still treats a calibrated model judge as load-bearing for the co-primary endpoint, while the signed thesis plan fixes a rule-based verifier as primary. A model critic can remain a candidate generator or secondary diagnostic, but not the primary admission/effect oracle.
- `research-design.md` labels a 25-item set `human-anchored`, while `questions.md` records that the labels came from a supervisor model and only 19 were non-unclear. This wording is stale and scientifically material.
- The current `T1-prime` block was correctly halted by instruction 0025 because a seal gate cited a stored hash instead of recomputing it, task dependencies were not provisioned, only 2 of 38 tasks certified, repeated seeds over two tasks created pseudoreplication, and spend ledger totals diverged.
- The proposed ablation budget's MDE values do not repair task-level pseudoreplication or factor mismatch; affordability is not identifiability.

## Experiment implementation audit

- The T3 `40 seeds` claim is not true task or inner-seed replication. `block_driver.py` changes only the filename/title outer index and calls `run_block.py --seeds 1`; the latter executes `range(1)`, so all 120 arm receipts use inner seed 0 and the same task SHA. The analysis script mistakes the outer filename index for a seed. The only defensible description is 40 stochastic rollouts per arm on one T3 instance; task-level generalization, 40-seed confirmation, SOTA, and component causality are inadmissible. Fixed B0→B1→B2 execution order also permits time/order confounding.
- T1′ scoring is directionally wrong for failures. The protocol says crash/nonzero exit must score zero, but the implementation assigns evaluator nonzero/timeout a score of one. Forty-two of the current 48 task5 receipts are evaluator crashes; 47 report score 1 and one reports score 2. The complete T1′ pilot/current block must be quarantined from confirmation, including the six non-crash cases until an independent rerun under a repaired, pinned evaluator.
- The untracked B2-G/B2-P/B2-R arms do not satisfy single-component removal: B2-G and B2-R are operationally equivalent to B2, B2-P removes multiple mechanisms, and the episode runner does not map the new arms. No v5 ablation may run in this state.
- The implemented B2 is only a forced-recording prompt/tool stub: it has an in-process node map without typed edges or persistence, no Exa/search capability, the lexical retrieval component is not connected to the runner, and `--no-session` resets every episode. It cannot yet be called the paper's persistent context-graph/retrieval/refinement prototype.
- Oracle isolation is not established. The current checks inspect paths/names but allow unrestricted shell and parent/absolute-path access without OS sandboxing or access logs. Absence of observed leakage is not proof of isolation.
- T3 preregistration is partly retrospective, dependency versions drift, budgets are not hard-enforced, and the primary inferential unit is one task. The existing p-value is therefore descriptive for one task only, not population-level evidence.

## Evidence admissibility

- Study A pilot/variance results: instrumentation or provisional variance evidence only; not efficacy evidence.
- Study A confirmation: budget-completion/usage evidence only; episode-count identity is inconsistent and no treatment effect is established.
- Study B T3: executed provenance for one task is present, but only one-task repeated-rollout descriptives are admissible.
- Study B T1′: quarantine; evaluator failures corrupt the endpoint and receipts lack required provenance/fingerprint fields.
- The prior 33.2% token and 100/83.3/66.7% claim-support figures are explicitly retracted fabricated fixtures with zero model calls. They are not active scientific evidence, but a stale `supports` edge remains a graph reactivation hazard.
- Root-aligned removals, root metrics, held-out confirmation, recovery tests, and native ARGO efficacy: not executed.

## Context graph audit

- The graph parses and has no duplicate node IDs or dangling endpoints: 487 nodes and 879 edges. This is structural integrity only.
- The new authoritative root reaches only three direct children and four nodes total; 483 of 487 nodes are not downstream-reachable from it. Existing hypotheses, protocols, experiments, results, sources, and decisions therefore do not inherit the new root in an agent-traversable way.
- Actual edge relations include `governs` and `cites`, but neither is declared in the 24-item edge vocabulary. The schema admits semantics it does not enumerate.
- The graph contains only one typed experiment-to-result chain. That experiment is `NOT_EXECUTED`, its synthetic result is `RETRACTED`, and current Study A/B executions are represented mainly as artifact/decision prose rather than protocol-run-result nodes. It is not yet an executable research-state graph.
- The graph's event constraint says a working skeleton must exist before the event and the prototype node marks the existing Study B harness `ACTIVE`. Both conflict with the signed no-pre-developed-artifact pledge. Thesis test artifacts may remain, but the event build must have a separate clean-room lineage beginning inside the event window.
- The root's four strands, its three mechanism-removal arms plus baseline, and the old S-by-R hypotheses are not connected by a common factor/estimand model in the graph.
- A `projection_inputs` key comparison against node IDs was explored but rejected as an invalid diagnostic because that object is an artifact input registry, not a node projection map.

## Evidence classification

- Current repository/runtime/PDF/official-page evidence: pending collection.
- Memory-derived navigation hints: Prime Agent session state is time-sensitive and must be verified with live CLI/session files before reuse.

## Open questions

- The session accepted the hold instruction and started the read-only inventory; its completed inventory response and stable HOLD/awaiting-input state remain pending.
- Exact thesis/application commitments and any divergence between them.
- Existing context-graph schema and whether claims have source/experiment lineage.
- Which experiment outputs are complete, reproducible, and accepted versus merely generated.
