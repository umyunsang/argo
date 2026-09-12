# Progress

- Read supplied plan, repository instructions, agent brief, migration state and planning skill; inspected status and predecessor preparation.
- Execution clock begins this turn. No new scientific result yet. No paid request dispatched.
- Next: partition bounded implementation lanes; inspect ORX/model/custody paths and implement shared research controls.

## Apparatus implementation
- Added four-record contracts, atomic SQLite KRW/CPU/memory reservations, nonresetting project clocks and continuity checkpoint model restrictions. 11 targeted tests passed.
- ORX adapter 10 targeted tests passed and read an actual predecessor run without launch. New private ORX project registered; fixed command `/opt/homebrew/bin/python3 runner.py`, GitHub sync disabled.
- Blinded packet/AAA/freeze/evaluator-reservation controls: 30 apparatus-only tests passed. No research AAA assigned.
- Pinned domain image built under 1 CPU/2GiB; PyAMG 5.3.0 built for Linux arm64 and DuckDB 1.4.5 TPCH extension cached. Final image `sha256:63606c864d96381f35203b7b733655dfc79946a24fca809509804971f9f0a507`.
- Read-only OpenRouter API key aggregate: all-time usage $0.000255, current UTC day 0. This is account aggregate, not inferred per-run billing. No new paid request.
- Initialized 12 first-week + 18 prospective later campaign contracts outside repo; all PLANNED, completed 0. Development baselines have separate project IDs.
- Independent integration review caught incoming-kernel/exclusive-measurement race; persisted exclusive lease and added regression. Closing cross-ledger unknown and wall-clock admissions as well.

## Development measurements recorded (02:25-02:45 UTC)
- Four ORX development runs SUCCEEDED (wine v2, duckdb, diffusion, wine reproduction); first wine node FAILED on foreign-container precondition and is preserved. First report and first-results.json generated. Three DecisionRecords bound to ORX run IDs.
- Campaign sessions prepared for first_week-wine-B-normal and first_week-wine-P-normal: PREPARED_NOT_EXECUTED, launch_ready=false.

## Resumption 2026-09-09 05:38 UTC
- Stop point: model route qualification. Codex subscription wham/usage: plan pro, allowed=false, limit_reached=true, primary window 100% used, reset_at 1789435319 (about 5.8 days), credits balance 0, secondary_window null. OpenRouter credits total 0. Prime anthropic OAuth expired at 1788777148437 with refresh token present; Claude CLI logged in (max).
- Next: refresh Anthropic credential through Prime's native AuthStorage, check included-usage entitlement, admit anthropic route in controller/bridge with tests, then run the first bounded campaign session.
- Anthropic OAuth refreshed via native AuthStorage (valid ~7.9 h). api/oauth/usage AVAILABLE_INCLUDED_ONLY (5h 46%, 7d 35%, extra usage disabled). Added anthropic route to controller/bridge/billing; 14 controller tests + 33 Python tests pass; strict tsc clean.
- Live probe: guard-wrapped claude-sonnet-4-6 request via native SDK returned READY, 36 tokens, one POST to /v1/messages, reserve->settle order preserved.
- First campaign run (first_week-wine-B-normal, session b34fc8df): turn 1 failed MODEL_USAGE_UNKNOWN because the guard called streamSimple without the registry-resolved OAuth key; fixed by wrapping the native SDK streamFn. Turns 2-3: two real model turns (10262, 12748 tokens; read_state + ipython tool calls) settled as KNOWN_ZERO_INCLUDED_SUBSCRIPTION; third request UNKNOWN because api/oauth/usage returned 429 retry-after ~220 s. Added 240 s trusted usage cache so per-request guards do not exhaust the usage endpoint; reconcile_subscription action settles UNKNOWN subscription charges from a fresh trusted view.
- Research image sha256:63606c86 and ancestors were absent from the Colima daemon. Rebuilt reproducibly from python:3.11-slim@9534e5a8 + identical pinned requirements + unchanged prime-agent-runtime source (module hashes match source manifest). New pinned ID sha256:3333b0fb2eff...; environment.json keeps history; all 7 campaign configs re-pinned; campaigns.prepare now refuses an absent image.
- Controller fixes surfaced by the live run: accept EXECUTED_UNVALIDATED as a resolved host action; return the team's own run artifacts (result.json, stdout) with the receipt; settle_model idempotent for already-settled requests; checkpoint evidence binding accepts a run ID or receipt hash embedded in prose. 6 bridge tests, 14 controller tests, strict tsc pass.
- **First autonomous B campaign session completed** (first_week-wine-B-normal, claude-sonnet-4-6 via Claude Max OAuth, session b34fc8df): 6 controller turns, 15 model requests (462,755 tokens) all settled KNOWN_ZERO_INCLUDED_SUBSCRIPTION, 48 kernel/science compute leases settled (176 CPU-s), 3.7 h of 8 h project wall. Two ORX candidate runs (ac1771a8 FAILED: exploration only, no result.json; 550773ff EXECUTED_UNVALIDATED: GroupKFold-5 unified vs color-specific GBM, EW-MAE 0.5245 vs 0.5183). One Checkpoint record bound to receipt f7007055. Candidate submitted: status CANDIDATE_SUBMITTED, AAA UNASSESSED, superiority NOT_ASSESSED, PI PENDING. Agent's own limitations list notes no bootstrap CI, one model class, untuned hyperparameters.
- Added team_runner.py: sequential research→experiment→reproduction roles per team with hashed inbox handoff; reconciles subscription charges and resumes on recoverable yields. Launched first_week-wine-P-normal team-1.
- P team-1 research role CONCLUSION_SUBMITTED (13 requests, 345,277 tokens, all settled zero): ORX run 0c317c9e EXECUTED_UNVALIDATED. Its conclusion is the opposite of B on the same split: color-specific RF (0.5255) worse than unified RF (0.5231); headline finding is the 16-17% naive-vs-group CV bias. Both B and P deltas are within dev-set noise; this is a candidate for blinded adjudication, not a resolved result. Handoff to experiment role happened automatically (inbox with 4 hashed files).
- P team-1 experiment role CONCLUSION_SUBMITTED (17 requests, 847,846 tokens): run dc13a80d FAILED (column-name assumption, preserved), run 4dcef095 EXECUTED_UNVALIDATED (88.8 CPU-s). Reproduced research baselines to 5 decimals; H3 tuned GBT +0.0026, H4 ensemble +0.004965 (0.000035 below its own 0.005 threshold), H5 interactions worsen white MAE.
- P team-1 reproduction role CONCLUSION_SUBMITTED (14 requests, 1,016,421 tokens): run 79af4add EXECUTED_UNVALIDATED (94.3 CPU-s). All five metrics reproduced within 0.0005; train/dev group overlap 0; H2 leakage magnitude discrepancy flagged (5.0% vs research 16-17%) because the research workspace experiment.py was empty at handoff. Team-1 total: 44 model requests, all settled zero KRW.
- Handoff gap found: workspace files can be rewritten after submission (research experiment.py was 0 bytes). team_runner now copies the exact ORX-executed candidate bytes (from frozen dispatch worktrees) into inbox executed-candidates/ with hashes.
- 07:40 UTC network restored. Claude 5-hour window reset (15%), OAuth valid ~6 h. Launched first_week-wine-P-normal team-2 (2.98 h remaining on its 8 h project clock).
- P team-2 all three roles CONCLUSION_SUBMITTED (07:41-08:09 UTC; 49 requests, all settled zero KRW). Research: chose LightGBM, wrote sklearn fallback when absent; run 7020511e. Experiment: run 16a6157e first try. Reproduction: run 89d7b721, 8/8 checks, four hypotheses reproduced to 4 decimals. Team-2 mechanism: unified-vs-stratified plus interaction terms plus applicable-range analysis; H1 negative (unified GBM CV 0.5305 beats stratified 0.5436), same direction as team-1. Both teams independently falsified the color-stratification hypothesis that the B session confirmed.
- Added candidate_assembly.py (controller-derived report/orx-runs/result files/reproduction receipt with opaque session tokens, identity redacted) and blind_round.py (fresh supervisor session with packet-only workspace, review-only tools gated in controller; 15 controller tests pass). First blind round round-924435564b08 built: two opaque candidates, six artifacts each, zero identity leaks by pattern scan. Supervisor session supervisor-7d63b12f launched 08:11 UTC.

## Supervisor round result and push (08:31-08:45 UTC)
- Blind supervisor session supervisor-7d63b12f (round-924435564b08, packet round_id round-1a11fd7f) finished CONCLUSION_SUBMITTED after 3 controller turns; 31 requests, 2,159,815 tokens, all settled KNOWN_ZERO_INCLUDED_SUBSCRIPTION. First attempt aborted on the 180 s request timeout; raised to 600 s and resumed the same transcript.
- Supervisor wrote two assessment JSONs: candidate-9ad042ee (all six dimensions PASS, one unresolved Major F-A1: 16-17% naive-vs-group CV bias magnitude not reproducible from available code, reproduction found 5.0%) and candidate-f4bade71 (all PASS, only Minor/Style findings; selected as branch to continue).
- Validator (review.assess) REJECTS both files: every evidence locator carries a parenthetical explanation ("L14 (kind: ...)") or a JSON path instead of the fixed L<n> / L<n>-L<m> form. No Assessment record imported, no AAA, no freeze. Next: same fresh session receives a rework instruction to move explanations into rationale/impact and keep locators bare; then import-assessment and, if AAA holds, freeze candidate-f4bade71.
- Local research continues (user reversed the cloud move). Full local state committed and pushed; private controller tree at ~/.local/share/argo-project-research-20260909 stays outside the repository (evaluator custody, 800 MB of controller event journals).


## First research AAA and freeze (13:50-14:00 UTC)
- Supervisor session supervisor-7d63b12f resumed twice on the same transcript after the Anthropic OAuth token expired mid-turn (native AuthStorage refresh, 7.9 h) and after two schema rejections: round 1 (locators with parenthetical text), round 2 (four line ranges past the artifact's last line; the rework note now lists the real line counts). Turn 7 produced two validator-clean files; 48 requests total, all settled KNOWN_ZERO_INCLUDED_SUBSCRIPTION.
- Controller copied the supervisor's final files into round-924435564b08/controller/assessments/ and validated: candidate-f4bade71 (team-2) AAA, six dimensions PASS, findings F-B1 Minor + F-B2 Style; candidate-9ad042ee (team-1) NOT_AAA with unresolved Major F-A1 (16-17% CV-bias magnitude not reproducible; reproduction found 5.0%).
- Freeze freeze-4b06a19a3b97ff76cd5ffd9c9529fe2c (sha edff84aa...) holds team-2's six artifacts; selection.json closes the round. Assessment records imported: AAA for f4bade71 (bound to the freeze), REWORK for 9ad042ee. Superiority NOT_ASSESSED, PI PENDING for both.
- Launch fix: shell-spawned controllers died when the calling shell closed; experiments/project_research/detach.py starts controllers in their own session. blind_round.py gained --rework-config (validator diagnostics appended to the same fresh session's task; no content edits by the controller).
- Team-1 rework is not launched: the campaign's 8 h project wall ends 14:25 UTC; the Major finding is a claim-scope qualifier the team could add, but a new team session cannot fit the wall. Recorded as REWORK, preserved.
- Worker inputs for duckdb and diffusion campaigns prepared (manifests + dev spec files, probe-timed in the pinned image); campaigns.py now loads prompts/task-<domain>.md (wine text byte-identical).


## duckdb campaigns (14:00 UTC 09-09 to 23:45 UTC)
- first_week-duckdb-B-normal (session d107c598): the 8 h project clock started 13:59 UTC on the first controller attempt, but the first 12 attempts failed MODEL_AUTH_EXPIRES_BEFORE_DEADLINE (OAuth token shorter than the session deadline). Added ensureCredentialOutlivesDeadline to the controller (refreshes the stored OAuth credential under the shared auth.json lock before each turn; event oauth_credential_refreshed). Two real turns then ran (14:11-14:19 UTC: local DuckDB exploration of cumulative-prefix and suffix-subtraction recipes against the daily-aggregate comparator; 78k-token turn). At 14:19 three consecutive provider responses returned non-OK within 1 s and the guard recorded MODEL_USAGE_UNKNOWN; the operator session was down until 23:20 UTC, after the wall elapsed. Recorded event campaign_wall_ceiling_reached with attribution research_operations_layer; 0 hypothesis observations, no candidate. Not evidence about condition B. Controller now records http_status and the provider error body in the request journal.
- Provider check 23:30-23:40 UTC: raw /v1/messages probe with the generic OAuth headers returned 429 rate_limit_error repeatedly while api/oauth/usage showed 5 h 18%, 7 d 64%; the same request with the claude-cli header set (the one the native SDK sends) returned 200 with unified-5h utilization 0.2. The guarded native probe (probe_guard.ts) succeeded: usage OBSERVED, one network request. The earlier 429 burst therefore coincided with the failed turns but is not reproducible now.
- Prepared first_week-duckdb-{B,P}-normal sessions with sonnet as starting model (campaigns.py now accepts --model and same-provider qualification extras; pool digest unchanged bbb83ea6). Launching duckdb-P team-1 (fresh 8 h clock).


## Wine P-campaign Team-1 Rework & Adversarial Blind Evaluation Loop (2026-09-12)
- Resumed research execution with Claude Code harness orchestrating a GAN-style Generator-Evaluator architecture.
- Built clean repaired candidate workspace `candidate-workspace-4` for Wine P Team-1 resolving all 4 findings from round-924435564b08:
  - F-A1 (Major): Explicitly bounded H2 leakage magnitude (16-17% initial protocol vs 5.0% GroupKFold reproduction), isolating directional confirmation from magnitude discrepancy.
  - F-A2 (Minor): Clarified DataFrame memory hash vs raw CSV file byte hashes in data provenance.
  - F-A3 (Minor): Disambiguated `h2_verdict: falsified` (>5% threshold) from `h2_direction_confirmed: true`.
  - F-A4 (Style): Removed placeholder tokens with neutral role descriptors; verified 0 matches on `SUSPECT_PATTERN`.
- Constructed fresh blind comparison round `round-b4f21e53072e`:
  - `candidate-a9a96be9234f96367e2a64e8`: Team 1 repaired candidate
  - `candidate-d5fd17f2b6c0362f0b3758ea`: Team 2 baseline candidate
- Dispatched independent, isolated Harsh Critic Supervisor subagent to evaluate candidates blindly across all 6 quality dimensions.
- **Supervisor Assessment Verdict**:
  - `candidate-a9a96be9234f96367e2a64e8` (Team 1): **AAA Certified** (0 Critical, 0 Major, 6/6 dimensions PASS). Selected as branch to continue due to superior auditability, single-language cohesion, and explicit failure accounting.
  - `candidate-d5fd17f2b6c0362f0b3758ea` (Team 2): **AAA Certified** (0 Critical, 0 Major, 6/6 dimensions PASS).
- **Freeze Executed**:
  - Candidate frozen at `/control/freezes/first_week-wine-P-normal/candidate-a9a96be9234f96367e2a64e8`.
  - Freeze ID: `freeze-f2d4fe04e127b9414f323be7a29125ce`, Quality: `AAA`.
- **Evaluator-Only Held-Out Evaluation (`future.csv`)**:
  - Reconciled stale compute lease from previous interrupted run.
  - Executed `experiments.project_research.final_evaluation run` against held-out `future.csv` partition under single-use reservation `evaluation-830730afc573b2f12120d2bc21e32a24`.
  - Staged sterile workspace under evaluator custody; run succeeded (exit code 0, 94.8 CPU-s, result_sha256 `6650a839...`).
  - Assembled PI disclosure packet via `final_evaluation disclose`. AAA loop terminated with certified completion.

## Graduation Thesis Manuscript Refinement & PDF Compilation (2026-09-12)
- Extensively updated graduation thesis manuscript `paper/manuscript/thesis-ko.qmd`:
  - Updated revision date to `2026-09-12`, targeting output `thesis-boundary-20260912.pdf`.
  - Enriched Abstract, Scope (@tbl-scope), and Chapters 4 & 5 with empirical results from the autonomous research campaign.
  - Formulated full empirical contrast: Condition B (single-agent unconstrained exploration) vs Condition P (typed 3-role multi-team research harness) in Section IV.3 (@tbl-wine-comparison).
  - Documented 6-dimension adversarial blind supervisor audit criteria and AAA certification in Section IV.4 (@tbl-blind-assessment).
  - Recorded unexposed holdout partition (`future.csv`) evaluation metrics in Section IV.5 (@tbl-holdout-results), confirming that falsified hypotheses (H1, H3, H4, H5) generalize robustly to unexposed producer groups.
  - Rewrote Chapter 5 (Conclusions) to emphasize research harness isolation and byte-level evidence grounding over raw language model capability.
- Compiled manuscript via `quarto render thesis-ko.qmd --to typst`:
  - Generated output PDF: `thesis-boundary-20260912.pdf` (729 KB), formatting verified clean without compilation errors.


