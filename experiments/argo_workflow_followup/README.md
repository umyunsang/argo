# ARGO workflow follow-up instrumentation

Status: scorer and one historical multi-hop replay semantics are validated at zero model cost. OS-level runner isolation is not validated. No task pack, model episode, or OpenResearch project is admitted.

`decision_sufficiency.py` keeps four objects separate:

1. exact routing of affected decisions;
2. claim-relative evidence sufficiency;
3. decision correctness when a hidden choice oracle exists;
4. the external end-to-end task outcome.

A correct route alone cannot pass. Missing or conflicting evidence returns `INCONCLUSIVE`. A stale version, over-broad route, wrong choice, malformed packet, or hidden-oracle access returns `INVALID`. Confirmatory success additionally requires the independently supplied task outcome.

`probe_discoveryworld.py` is a zero-cost source probe. It tests only a pinned local DiscoveryWorld install. It does not run an LLM. The proposed comparison remains blocked until a text-only, separately sandboxed runner, correction/handoff event pack, deterministic gold, immutable environment, exact resource envelope, and explicit approval exist.

Run the scorer tests:

```bash
python3 experiments/argo_workflow_followup/test_decision_sufficiency.py
```

Run one DiscoveryWorld probe with the external repository's isolated interpreter:

```bash
~/.cache/argo-research/DiscoveryWorld/.venv/bin/python   experiments/argo_workflow_followup/probe_discoveryworld.py   --scenario Proteomics --difficulty Easy --seed 0 --thread-id 918280
```

## Historical multi-hop pipeline falsifier

`historical_multihop/` replays the actual corrected-B2 protocol repair. Its gold choice predates this instrument in the byte-pinned audit and B3 closure. The typed conjunctive rule changes five nodes across a four-edge `claim → decision → action → result` path and preserves two descriptive nodes. A deliberately coarse ANY-support comparator incorrectly promotes the invalid endpoint. This is one pipeline falsifier, not a policy-efficacy result or an independent population.

```bash
python3 experiments/argo_workflow_followup/historical_multihop/test_historical_multihop.py
python3 experiments/argo_workflow_followup/historical_multihop/test_isolation_command.py
```

Do not run `historical_multihop/run_isolated.py` again under the current authority. Both Docker attempts failed before launch because a macOS logical temporary path was not daemon-visible. The one allowed infrastructure retry is consumed. The path is prospectively resolved and passes pure command tests, but end-to-end isolation remains `FIXED_UNVALIDATED`.

## DiscoveryWorld-derived pack design

`discoveryworld_pack/pack-design.json` defines ten paired rows from two source-audited families: Combinatorial Chemistry Normal and Archaeology Dating Normal, each at literal API seeds `0..4`. The inference unit is the task family, so this is `n=2`, never `n=10`. The design uses text only, excludes the LLM knowledge judge, keeps `completedSuccessfully` as primary, retains old record versions, and requires a fresh-context handoff plus unaffected-decision preservation.

```bash
python3 experiments/argo_workflow_followup/discoveryworld_pack/test_validate_pack.py
```

The 12/12 tests validate schema and mutation sensitivity only. No seed-specific task gold was generated. Long-horizon RNG, procedural action-success semantics, OS isolation, runner identity, cost, and approval remain open. Do not execute or call this an official DiscoveryWorld benchmark result.

## Arbor comparator source audit

The strong TREE comparator is pinned to official Arbor commit `2f4e65410a5c21c9e55835a9a0d77ead21a64ffa`. Its `Node` schema supplies hierarchy, hypothesis, insight, result, dev/test scores, code reference, grounding, outcome status, and attempts. It does not supply typed evidence identity, version, validity, applicability, or dependency edges, so both future arms must receive the same external raw evidence log.

The repository is not an independent real-graph task source. Its bundled 7-node/117-event recording is explicitly illustrative and hand-authored. The separate BrowseComp HTML embeds ten nodes, but the referenced raw run directory is absent, and embedded non-root status counts (`4 done / 1 merged / 4 pruned`) disagree with its narrative (`5 / 1 / 3`). Use the code/schema as a comparator prior. Do not claim run reproduction or dependency-targeting evidence from these demo bytes.

## External architecture research trace

The supplementary repository for `2608.01995v1` contributes an external real research trace: 111 hypotheses plus three baselines in one programme. The authors' parser reproduces the committed 114-row CSV byte-for-byte from the 211-KB Markdown log. Three Phase-1→Phase-2 decisions reverse under a combined regime change: stochastic-depth removal (`+0.46` to `-0.60`), label smoothing off→on (`+0.13` / `+0.30`), and Mixup off→mild (`+0.68` / `+0.77`).

A retrospective replay gives scoped revalidation `3/3` exact while preserving all original-scope results. Unscoped reuse selects the wrong Phase-2 setting `3/3`; global invalidation destroys all three still-valid original-scope records. These three pairs are nested observations in one programme, not `n=3`. Dataset, parameter scale, augmentation, and evaluation protocol changed together, so this is a regime-applicability result, not a scale-only effect or prospective predictor.

The snapshot omits training code, tracking-service exports, failed-run configurations, and per-hypothesis Git commits. It supports trace semantics, not score/code reproduction or ARGO efficacy.

## Grounded-physics archive: aggregate versus decision evidence

The official Zenodo record `10.5281/zenodo.21126996` is checksum-complete and aggregate-replayable. Its 1.33-MB CC-BY-4.0 ZIP passes CRC and 125/125 internal SHA-256 records. The supplied in-package script reproduces seven anchors (`4 PASS / 3 caveat`), 15 catch episodes, 14 literature channels, 2,162 consultation events, and 47 sessions byte-for-byte.

This does not make the archive a raw decision graph. The README explicitly withholds raw session transcripts, and none of the 15 episode-ledger rows has its named direct `pilot/...` source path in the public ZIP. The strict result is `0/15` direct source-path closure, not a claim that the curated summaries are false. It shows that aggregate integrity and correct event routing do not alone make a decision basis independently reconstructable.

## Isolation canary v2 approval gate

A new runner prepares exactly one zero-model isolation canary. It resolves macOS bind paths before Docker, pins the local Python 3.11 image digest, disables image pulls and networking, uses a read-only root with all capabilities dropped, limits the container to 1 CPU / 256 MB / 64 PIDs, and enforces a 30-second run timeout. The approval template is intentionally `AWAITING_USER_APPROVAL`; invoking the runner with that file exits before Docker with `docker_calls=0`.

This is not approval. Do not run it until the user explicitly authorizes the exact envelope in `paper/research/isolation-canary-v2-proposal.json`. If approved, exactly one container attempt is permitted and there is no retry.

## Canonical real decision packets

`real_decision_packets/` rederives facts from four existing canonical receipt families: the external architecture trace, the grounded-physics public archive, the DiscoveryWorld pack design, and isolation-canary v2 readiness. The evaluator keeps route fidelity, claim-relative sufficiency, narrow policy-decision correctness, and external task outcome separate.

Measured descriptive replay: route fidelity 4/4, sufficient evidence for the stated narrow claim 2/4, correct narrow hold/admit-with-limit decisions 4/4, and external task outcomes 0/4. Four one-artifact withdrawal trials were selectively exact 4/4; a global-reset comparator over-revoked 12 unaffected packets. These are four curated real research-state packets, not four efficacy trials or a population estimate.

## Third external programme: Graphectory

The pinned Graphectory repository (`052079f7`) contains 3,972 precomputed graph paths and exactly matching metric rows across eight agent/model collections. The paper reports 3,973 non-empty trajectories; the one-row difference is localized to SWE-agent/DeepSeek-V3 (`498` repository rows versus `499` in the paper). Twenty-two selected graph files match their metric status.

The graph builder reads terminal resolution from a separate evaluator report. In six bundled raw samples, report-backed graph status matches 6/6. The three OpenHands records' embedded `resolved` fields match only 1/3. Thus a correctly routed trajectory does not itself establish the terminal outcome. Static selected graph JSON files contain no complete raw `thought`, `observation`, or `response` fields.

Pinned-builder replay initially failed because the capsule omitted three parser YAML files (SWE full-graph exactness 0/3). After adding those recipe dependencies, SWE raw-to-full graphs reproduced byte-exactly 3/3. Across six current-versus-bundled graph comparisons, 26 of 382 metadata/node/edge units changed and 356 were stable; global invalidation would over-revoke those 356 units. This is a retrospective version-diff locality oracle within one external programme, not six independent trials or policy efficacy.

## Isolation canary v2 closure and v3 proposal

The explicitly approved v2 launch consumed its only attempt and exited 125 before container creation because Docker Desktop could not see the writable output bind under `/private/var/folders/...`. Image identity passed, but the policy did not execute. All canary fields other than image identity are therefore `NOT_OBSERVED`, not isolation failures. There is no v2 retry.

V3 removes the failed dependency. It has no writable host bind: the policy writes only to container `/tmp` and emits its JSON on stdout; the host runner writes the receipt after exit. Two read-only repository mounts remain. V3 tests pass 8/8 and its unapproved probe exits before Docker with zero calls. V3 remains unapproved and unexecuted.

V3 immutable readiness attempt at commit `5f82fdf28` exposed one test-only path assumption: the clean clone lived under `/private/var/folders`, which the test incorrectly banned even for read-only source mounts. The corrected test enforces the real invariant—exactly two read-only mounts and no `/output` bind. Runner, policy, command, resources, and execution scope are unchanged. V3 remains unapproved and unexecuted.

## Isolation canary v3 result

The separately approved v3 attempt passed all nine exact canary checks in 0.311928 seconds. The pinned image started with two read-only repository mounts and no writable host bind; released input was readable, four forbidden/oracle paths were unreadable, external networking and the tested loopback service were unreachable, no named secret environment keys were present, and no withheld mount was visible. The one-attempt authority is consumed. This validates only the exact generic canary boundary, not a DiscoveryWorld runner, 1,000-step replay, score semantics, correction gold, integrated tasks, or model efficacy.

## DiscoveryWorld long-horizon determinism proposal

A separate design freezes 20 zero-model host-subprocess episodes: two task families, literal API seeds 0–4, two fresh-process repeats, and 1,000 fixed rotation/action-tick steps per episode. It hashes text/UI state and action/tick results at fixed checkpoints. It excludes vision, task scorecards, hidden gold, correction generation, task completion, and models. The environment is sanitized and Python socket calls are denied, but this is not OS-container isolation. Seeds and repeats are nested; the inference unit remains two task families. Tests pass 9/9 and the unapproved runner exits before episodes with zero steps. Execution requires separate explicit approval.

## DiscoveryWorld long-horizon result

The separately approved frozen run exhausted all 20 one-attempt subprocesses. Every 1,000-step episode hit its 120-second timeout; no episode emitted a terminal receipt. The controller stopped after 2,400.32 seconds with no retries, exclusions, or endpoint shortening. Therefore the zero values in its raw summary are aggregation over missing episode receipts, not observations that zero steps/actions occurred. The result rejects the exact runtime envelope as infeasible and yields no determinism, task-success, hidden-key, or model conclusion.

## DiscoveryWorld exploratory latency calibration proposal

A new, explicitly exploratory protocol does not retry or replace the closed long-horizon endpoint. It fixes two task families at seed 0, horizons 10/50/100, two fresh-process repeats, 12 cells and 640 planned steps. Each cell has a 60-second timeout and flushes NDJSON after load and at fixed progress checkpoints so timeouts preserve partial evidence. It excludes vision, scorecard, gold, task completion, behavioral conditions, models and confirmatory inference. Tests pass 10/10; the unapproved branch starts zero episodes. Separate approval is required.

## DiscoveryWorld exploratory latency result

All 12 fixed cells completed 640/640 actions and ticks in 85.16 seconds with no timeouts. Same-cell final chains were exact 6/6, and 14/14 cross-horizon prefix groups were exact through the maximum observed horizon of 100 steps at seed 0. Median per-step latency was about 0.121 seconds in both families; median-based 1,000-step projections were 121.58–121.61 seconds, slightly above the failed 120-second cap. These are exploratory planning measurements, not observed 1,000-step or all-seed determinism. The calibration authority is consumed and cannot be reused.
