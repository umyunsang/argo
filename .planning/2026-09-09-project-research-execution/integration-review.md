# Integration review of project research execution

Scope: independent static integration review requested by the root agent. This is not a blinded scientific supervisor, research AAA decision, domain-result review or PI judgment. Read the full `contracts.py`, `state.py`, `runner.py`, `container_task.py`, `dispatch.py`, `programme.py`, `dashboard.py`, review module, and the ORX adapter needed to trace dispatch continuity. No root implementation file was changed and no tests or scientific runs were executed by this review lane.

Initial-snapshot verdict: **0 Critical, 4 Major findings**. The response review below supersedes the original finding statuses. Current local development measurements may proceed under the explicit development-only scope. Completing the multiweek comparison programme is not required to close this bounded implementation turn.

## Response review after root repairs

Re-read root changes in full. Added only `experiments/project_research/test_dispatch.py` for the requested recovery cases; all ORX, git and launch operations are mocked and all file state is temporary. No root implementation file was changed by this lane. Ran `python3 -m unittest -v experiments.project_research.test_dispatch`: **4 passed**, 0.027 seconds. The ordinary retry fixture also preserves an existing UNKNOWN launch-intent file byte for byte while passing its original path to the adapter.

| Finding | Response status | Verified change and remaining scope |
|---|---|---|
| M1 | **Unsafe raw terminal outcomes blocked; full integration pending** | `Store.append` now rejects raw AAA, any non-PENDING PI outcome, and any non-NOT_ASSESSED superiority. This removes the unsupported terminal-outcome insertion path for new records. The validated review/freeze-to-Assessment import path and PI receipt import still do not exist, and the canonical review/schema mismatch remains; do not describe this as completed terminal assessment integration. |
| M2 | **Closed for the tested dispatch recovery boundary** | Request identity now depends on the spec and candidate-source digest, reuses the existing frozen experiment/commit/intent, and rejects an existing request without `frozen.json`. Four mocked regressions cover ordinary retry (including changed display title), a lost launch response after freezing, a timeout with ambiguous experiment creation, and an unparseable success response from creation. Only one create call is made and the prior request evidence is preserved. This is apparatus evidence; no real ORX job was launched by these tests. |
| M3 | **Requested admission checks repaired in source** | Charge and compute admissions now each reject unknown billing or compute; charge reservation starts/checks the project clock; continuation checks its existing project deadline; compute admission reads the immutable project contract and enforces the project's active CPU/memory limits as well as global limits. Static reinspection confirms these changes. Full actual session/model budget enforcement still depends on the campaign launcher using these entrypoints, including starting the clock at the first research session. That integration claim remains unverified rather than assumed. |
| M4 | **Partially addressed: envelope validation, candidate success withheld** | `valid_observation` now rejects a bare placeholder, wrong domain/status/scope/stage, missing resource values and nonfinite/negative resource use. Candidate mode explicitly reports `EXECUTED_UNVALIDATED`, with scientific validation NOT_ASSESSED. The check still accepts any nonempty inner `result` and any nonempty `code_sha256`; existing `test_runner.py` illustrates acceptance of `result={"observations": []}` and `code_sha256={"source.py": "sha"}`. Thus the original claim that process exit alone is sufficient is repaired, but source/input provenance, hash validity and actual domain-observation content are not fully validated by this function. Report it as a structural development-receipt check, not independent scientific admission or final evaluation. |

M1 and M4 therefore remain explicit integration/validation limitations. M2 is verified with the focused mocked tests; M3 is verified by source inspection here. The root owns tests for its state and runner edits. No new requirements beyond the original four findings were added.

Follow-up source identities observed during review: `state.py` SHA-256 `9f410cde413d6b9faf99e69abe0fc8f83343d31512ab898894d6e1c099885d3f`; `runner.py` `8ab28ed2a2245d333a9843af90cccc634a07af0adf19d9cb1edc2d033d248d9b`; `dispatch.py` `2431326bd71a391df75920005c26911eac069c8d77cd1c00bfe7c7beaf4a7adb`; new test `test_dispatch.py` `1cc2e3a8f2989603988699881915d5942673ff1751f495cbb153efc590c22611`. `runner.py` was changing concurrently; the response review is tied to the full read containing `valid_observation`, `EXECUTED_UNVALIDATED`, background-sample limits and the precondition-failure receipt path. Recheck any later runner semantic-validation repair separately.

## M1 — Authoritative Assessment records bypass the actual review and PI gates

- Evidence: `experiments/project_research/contracts.py:72-79` accepts `quality="AAA"` and `pi_acceptance="ACCEPTED"` after checking only enums and basic fields. `state.py:51-66` persists that record without invoking `review.assess` or validating a frozen assessment/candidate. `dashboard.py:25` then displays its outcomes. The real review output uses `supervisor_session_id`, `NOT_AAA`/`APPARATUS_PASS`, evidence scope and assessment hashes (`review.py:396-467`), while the four-record contract requires `session_id` and accepts only `AAA`/`REWORK`/`UNASSESSED`.
- Impact: a coordinator can insert a fully accepted result without six-dimension review, independent reproduction, immutable candidate linkage, final evaluation or a PI receipt. Conversely, an authentic apparatus-only review cannot be persisted directly. The strongest standalone review controls are bypassed at the programme's authoritative record boundary.
- Minimum fix: make raw Assessment insertion provisional only; add one controller conversion path that runs the review validator, binds packet/assessment/candidate hashes and preserves evidence scope. Persist AAA only from that result. Record PI acceptance solely from an explicit, immutable PI decision receipt. Keep superiority separate and unassessed without independent final evidence. It is sufficient to reject unsupported final outcomes until those integrations exist.
- Recheck: a minimal Assessment with `AAA` or `ACCEPTED` but no validated provenance must fail before persistence; an apparatus-only review must persist as apparatus-only without appearing as research AAA; modified review/freeze evidence must fail. No real AAA should be manufactured for this check.

## M2 — Public dispatch entrypoint discards idempotent submission identity on retry

- Evidence: `dispatch.py:39-48` allocates a fresh UUID and calls `create-experiment` on every invocation, even for the same project/spec/title. Its reusable launch intent is only created inside that new request directory (`dispatch.py:68-70`). `orx_adapter.py:177-231` correctly reattaches or blocks an ambiguous launch only when the same experiment and intent path are reused; it cannot reconcile a new dispatch request that creates another experiment.
- Impact: retrying the CLI after a lost response, crash or session/model change can launch a second ORX node for the same scientific decision. Exclusive compute admission may prevent overlap but does not prevent a duplicate sequential scientific run or unnecessary ORX submissions. A `SUBMITTING`/`UNKNOWN` intent from the first request is not inspected.
- Minimum fix: require a stable caller decision/request ID and persist the dispatch state under that identity before `create-experiment`. On repeated calls, recover the existing experiment/worktree/commit/intent and call `attach_or_run` with the original identity; block unknown create/launch outcomes for reconciliation. A deliberate rerun must have a new DecisionRecord and explicit lineage to the prior attempt.
- Recheck: simulate a response lost after experiment creation and after launch; replay the same public dispatch request and assert one experiment and at most one run. Verify a new explicit research decision can still create a new run and that all failed/unknown attempts remain recorded.

## M3 — Accounting admission is not global and project time is only enforced for compute

- Evidence: `state.py:82-94` checks unknown charges but not unknown compute, starts no project clock and checks no wall deadline. `state.py:106-124` checks unknown compute but not unknown charges. `state.py:138-150` resumes after a checkpoint without checking wall time. The project clock is initialized only by an explicit `start_project` call or first compute admission (`state.py:72-80,118-123`); no caller in the reviewed dispatch/container path marks earlier literature/reasoning work as project start. Project `cpus` and `memory_mib` are validated in `contracts.py:50-53` but are not stored or enforced by compute admission, which only uses the aggregate maxima.
- Impact: an unknown billed request does not stop new compute, unknown compute does not stop new charged work, and paid/model work can be reserved after the eight-hour project ceiling or before the recorded clock begins. The contract's lower per-project CPU/memory limits can also be exceeded through `admit_compute`. The current fixed local runner itself uses 1 CPU/2 GiB, so this finding concerns the exposed general admission API and the forthcoming campaign launcher.
- Minimum fix: use a shared transactional admission check for unresolved billing/compute/launch state and the project deadline; initialize the clock at the first actual project session/action, including literature/model work. Apply that check to charged work, compute and continuation. Read the immutable project resource limits when admitting compute. Until model/campaign dispatch is connected, explicitly keep it disabled rather than claiming its bounds are enforced.
- Recheck: unknown billing must block compute; unknown compute must block charged work; charged work and continuation after the project wall ceiling must fail; the clock must include precompute reasoning; requests exceeding the project's stated CPU/memory limits must fail despite fitting the aggregate cap.

## M4 — Development-result success depends only on nonempty JSON and process exit

- Evidence: `runner.py:119-122` loads `resource.json` and `result.json`, then sets `SUCCEEDED` for exit code 0, truthy objects and confirmed container removal. It does not validate their type/schema, domain, data/split/source provenance, receipt scope, resource exit code or domain acceptance fields. `runner.py:135-136` emits `development_research_result` with that status; `dashboard.py:23-24` counts such events as actual successful development experiments. `container_task.py:15-23` records a process receipt but does not validate the domain result.
- Impact: a malformed or wrong-domain result such as `{"placeholder": true}` produced by modified research tooling can be counted as a successful real development experiment. This does not currently grant AAA, but it can falsely satisfy the user's first-real-baseline/first-hypothesis evidence requirement.
- Minimum fix: distinguish process completion from admitted scientific evidence. Validate the selected domain's result contract, actual source/input identifiers, expected result mode/scope, and resource receipt consistency before emitting an admitted real-result event. Otherwise preserve the terminal process result as `FAILED_VALIDATION` or `UNCONFIRMED`, including the raw output. No performance superiority or final-validation claim should follow from process exit alone.
- Recheck: zero exit with missing, placeholder, wrong-domain, synthetic-only, nonfinite, or inconsistent result/resource JSON must remain unadmitted; a valid actual development receipt must still be recorded without being counted as an autonomous B/P campaign or final evaluation.

## Claims that remain unsupported by this integration snapshot

- The reviewed runner explicitly records `scope="DEVELOPMENT_RESEARCH"`, `autonomous_campaign=false`, `AAA="UNASSESSED"`, and `PI="PENDING"` (`runner.py:128-130`). `programme.py` also initializes every campaign as planned and completed count zero. These boundaries are correct and must remain visible in the result packet.
- The two-team blind loop, AAA freeze and single-use final reservation are implemented apparatus controls. There is no reviewed call path wiring actual independent worker/supervisor sessions, packet-only mounts, independent evaluator execution or a PI decision into programme state. Do not infer those outcomes from unit fixtures.
- `Store.resume` checks a caller-supplied allowed-model list, not the immutable model-pool digest, and merely returns the old model as unavailable. Actual session interruption, model unavailability, cross-model recovery, checkpoint evidence carryover and nonduplicated ORX execution have not been established by this static record. These remain explicit validation work before continuity campaigns.
- Hidden split custody and actual sample/group disjointness are evaluator obligations. The standalone reservation checks receipt declarations and identical hashes; it cannot establish OS isolation or sample disjointness by itself. Keeping one persistent evaluator-owned registry across campaigns is mandatory for its one-use guarantee.
- No comparative superiority, autonomous research completion, TPC benchmark result or SOTA claim follows from this review. Absence of such results is not a defect to hide or a reason to inflate scores.

## Reviewed source hashes

```json
{
  "contracts.py": "8bb641f444a89f0a81c6534099df49b87a4195160b8407d5715ea5c845e7bd55",
  "state.py": "0bab2e9716a4e7e7b1072e304eff67b023570a12da047989104c9363b7dff998",
  "runner.py": "24da3f8ab37fc789ac6ba7c4fa8089315c6c94109d7562e3ec03492b06186628",
  "container_task.py": "c39f4da7f6c53acc7e5f9bfb911fb8b1108af5cf737090c00579f25b90518836",
  "dispatch.py": "ef42762b60b26efb4a659d092d52c33cb2c92989a4edaecbba8c9fa91f285b2a",
  "programme.py": "1efd639c9743d69b7de7f69226af394151107ce1ba91c24398f723392f4c6eb0",
  "dashboard.py": "a7201e02c632fb1a98cbd1e7f1bd5c88d2c7f307c6d97f0ea9e93f780df0bf3d",
  "review.py": "dc5ec44c2e09d859a71e0f7ad869b755c016367bb6a5cf75e9cf8b61ec8ace54",
  "orx_adapter.py": "d40531cb7e6547212821fc7b1494c7c1d50f86ccc5290f4bc3abfd601d8e3e1d"
}
```

The code may be changing concurrently. These findings apply to the hashes above; root integration must recheck repaired paths against the final source and focused verification results.
