# Runtime / prototype 독립 검토

판정: **책임 배치는 일관되지만, 향후 handoff 명세 두 곳을 보완해야 한다.** 현재 설계의 정적 검토이며 runtime 인수·P0 admission·B/C/G 효능·native 구현 재개를 인증하지 않는다. 두 지적은 미구현 설계의 명세 공백이며 현재 P0 결함이나 관측된 누출로 판정하지 않았다.

동결 묶음: `2026-09-08T22:29:57.231730+09:00` · HEAD `ea45dacde9b151c023ea8d65189e4dc1871d79c0`. 41개 파일의 크기와 SHA-256이 manifest와 일치했다. hash 검사는 전체 의미 읽기를 뜻하지 않는다.

검토 독립성은 fresh model context와 별도 출력 소유권이다. OS 격리, 모델 오류의 독립성, 독립 ground truth를 뜻하지 않는다. 일반 memory summary는 지침으로 주입돼 노출됐으나 memory 파일·과거 세션·다른 검토자 결과를 열거나 근거로 쓰지 않았다. 필수 설계 문서 안의 과거 PASS 표시는 내 판정으로 계승하지 않았다.

## RUNTIME-01 · medium · runtime/prototype assessment visibility

**Assessment-to-successor handoff needs an explicit development/final release discriminator**

분류: `directly_supported` · `PROSPECTIVE_PORT_SPECIFICATION_GAP_NOT_OBSERVED_LEAKAGE`

The detailed study and P0 contracts prohibit hidden-score feedback, while the prototype connection and owner outputs use one generic Result/assessment route. No final-score visibility/release field or consumer rule is specified in that route.

A future importer could satisfy the drawn assessment-to-successor path while exposing terminal hidden assessment to the still-active research policy. This would change the scientific information set, and accidental differences between C/G would invalidate the intended comparison. Correct prose elsewhere does not define the port message semantics.

근거:

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.json:284-291` · SHA-256 `e6df58ef7b959ad807fdc64ab02f2c979502005f2d3e7892566f33d1f9103164` — The shared path connects authoritative terminal receipt plus independent task assessment directly to result and successor decision.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json:81-98` · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — Active policy accepts permitted public observations and must not use hidden scores.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json:141-158` · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — The final scorer has a distinct hidden-data boundary and returns a score/validity receipt.
- `packet/paper/research/integrated-research-design-active.md:50-52` · SHA-256 `63f0a873bcf04540d8a3143dbca31446790dc101ba1c436476dd5143f8c9889a` — The detailed scientific contract requires a preselected single artifact and release only after all final locks.
- `packet/metadata/current-p0-protocol.json:1-1` · SHA-256 `2e4ce502ae98280f8d43839cc11e43b26d66a149a89614a788165b5a0c0704bf` — Current P0 requires final assessment after final prediction lock and controller termination, with no score returned for reselection.

최소 수정: In the existing handoff row, distinguish DevelopmentObservation from FinalAssessment with programme/phase, assessment kind, artifact lock identity, release condition and allowed consumer. Keep development observations on the online loop; expose hidden final assessment only at the declared post-lock/termination boundary and to a closed-study analysis or an explicitly new programme. Point the row to the existing selection/sealing rules; do not amend frozen P0.

저비용 반증 확인: Later, before adopting the port, walk a small fixture containing a dev score and a hidden-final receipt in the same programme. Before the required locks/termination, only the dev receipt may reach policy input; after closure, final assessment may reach the designated analysis view, with no new same-programme selection. This review did not execute the check.

불확실성: This is a handoff ambiguity, not evidence of a current leak. The current task-specific bridge does not return a hidden final score in its inspected public/dev result paths. A more specific future typed adapter contract could close the gap.

## RUNTIME-02 · medium · runtime/prototype recovery and decision lineage

**Replay acceptance does not identify the committed decision frontier or distinguish replay from a new model decision**

분류: `directly_supported` · `PROSPECTIVE_REPLAY_ACCEPTANCE_SPECIFICATION_GAP_NOT_NATIVE_RUNTIME_BUG`

The handoff promises deterministic active-state/next-action replay but leaves the durable programme decision frontier, its link to native session/fork IDs, and the distinction between an already committed action and a new LLM choice unspecified.

Namespace recovery can lag an external action. Re-running a policy is not necessarily deterministic, and a forked session identity must not imply fresh scientific execution authority. Without a shared committed-action record, a future implementation can either change the next action or restore stale pending state while appearing to satisfy normal session recovery. The same ambiguity must not become a G-only recovery capability.

근거:

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.json:92-97` · SHA-256 `e6df58ef7b959ad807fdc64ab02f2c979502005f2d3e7892566f33d1f9103164` — Research state is connected to the session artifact namespace and fresh-session recovery must reconstruct candidate/evidence/latest run/next action.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.json:275-280` · SHA-256 `e6df58ef7b959ad807fdc64ab02f2c979502005f2d3e7892566f33d1f9103164` — ResearchEventStore is the single event history and fresh replay is expected to produce the same active revision and next action.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json:62-98` · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — The event-store input/output and active-policy output lists omit a defined committed-decision/frontier record.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json:229-251` · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — Reconciliation lists states and run identity fields but no event commit boundary tied to native recovery/fork.
- `packet/packages/coding-agent/src/core/kernel/repl-manager.ts:1328-1376` · SHA-256 `7625fc7f99cbaa59bac3620560ad2c2ac04e8c9245c8565ec87e2c5178dd8278` — Snapshotting is best-effort per variable and can return null or skipped values.
- `packet/packages/coding-agent/src/core/kernel/repl-manager.ts:1434-1444` · SHA-256 `7625fc7f99cbaa59bac3620560ad2c2ac04e8c9245c8565ec87e2c5178dd8278` — Automatic snapshots are debounced, so a completed action can precede its namespace snapshot.
- `packet/packages/coding-agent/src/core/agent-session-runtime.ts:567-574` · SHA-256 `9a4b34a2219637d8e5750efbc37b279fe72367d097414875835510981b3ab5c4` — Native fork constructs a new session path and acquires its session lease.
- `packet/experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py:1283-1303` · SHA-256 `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` — The task bridge writes a durable attempt before prepare/start and later binds identity; this is task apparatus evidence, not a native graph checkpoint contract.

최소 수정: Add one concrete checkpoint/decision record to the existing ResearchEventStore contract: programme/arm authority identity, event sequence or parent digest, committed decision and RunIntent identity, policy/projector revision and pending reconciliation frontier. State that replay restores committed decisions; a fresh model proposal is a new event. Declare how resumed/forked sessions reference that same scientific frontier, and which durable artifact survives session lifecycle operations. This is a future task-bound/native handoff requirement, not a request to resume construction.

저비용 반증 확인: Later use a paper or static fixture walkthrough at three cuts: before decision commit, after commit but before launch reply, and after run binding but before kernel snapshot. Resume from a stale snapshot and fork a second session; each must find the same committed decision/frontier, keep ambiguous launch UNKNOWN, and never infer unused budget or permission from the new session ID. No model or live ORX call is needed for the initial check; none was run here.

불확실성: The packet already specifies conservative UNKNOWN handling and the task bridge implements write-ahead fencing. The gap is their explicit mapping into the proposed native event/replay contract. No claim is made that the inherited session/REPL implementation is defective or that arbitrary fresh LLM choices should be identical.

## 타당한 부분

- All seven materials have distinct roles rather than being an installation checklist: inherited pi hooks; native Prime process/session/REPL/RLM; ORX run identity; Exa discovery; research graph; research loop; graph-maintenance policy. Runtime existence is consistently separated from efficacy.
- Process/session authority, research event projection and external scientific-run authority are separated. The bridge queries ORX identities and stops on uncertainty; a local journal is not asserted to prove exactly-once execution.
- Task apparatus, Python fixtures and native ARGO modules are explicitly different. No completed migration slices or empirical architecture winner is asserted.
- B/C/G retain common information, computation, recovery and resource rights; C/G match obligation strength. Graph extraction/update cost belongs to G and the G-C claim is a package increment, not pure topology.
- The current P0 is C0 feasibility only, and all real scientific-run/score counts remain zero. Previous host execution restrictions are recorded without being generalized into scientific impossibility.
- The inspected bridge selects a verified historical method before final refit and then locks the final prediction artifact; native run/commit/source/config and task/protocol identities remain attached. Hidden final performance is not an online selection value.
- Prototype evidence must show real candidate comparison, a successor decision and native code/run receipts; a simpler B/C outcome is allowed. Research-refine and engine-refine are separate, and inherited implementation is not thesis novelty.

## 일곱 재료와 수용 근거

| 재료 | 검토한 범위와 한계 |
|---|---|
| pi | Hook interface verified in full agent.ts; loop implementation and actual cancellation/resource enforcement not executed. |
| Prime Agent | Session runtime/services/RLM files fully read. REPL snapshot and refinement sections inspected; daemon supervisor, TUI and complete process lifecycle not audited. |
| OpenResearch CLI | Task FixedNativePort/Bridge interfaces inspected for launch/status/source/final-lock lineage. Live CLI/server/API capability and successful scientific execution not verified. |
| Exa | Role as candidate discovery is coherent. Crosswalk retains an earlier session-blocked label; later packet source-evidence reports four successful searches. Treat this as time-scoped history, not current native integration certification. Raw query receipts were not in the packet and were not fetched. |
| context graph | Prospective research representation and local research map are identified separately from native control. No native graph implementation or useful graph efficacy established. |
| loop engineering | Generic loop hooks and refinement apply/rollback sections exist. Scientific control is prospective, engine mutation is deferred. |
| graph engineering | Single research event owner and conditional backend selection are coherent. Committed replay/frontier semantics remain RUNTIME-02. |

native owner의 hook/session/RLM과 task bridge 경로는 소스에 있다. 실제 prototype에는 선택된 정책의 native code/run receipt, 두 후보의 유지·기각 이유, 원문과 run/artifact 계보, 허용된 observation으로 바뀐 다음 행동, 중단·재개 및 UNKNOWN 처리 증거가 필요하다. 현재 그 완료 증거는 없다. 기존 test-instance 검증과 명시적 restart 조건은 유지된다.

P0는 C0 feasibility이고 실제 programme/run/hidden score/B/C/G 배정이 모두 0이다. 준비와 합성 검증은 과학 실행 성공률이 아니다. 응답 불명 처리와 method→final-refit→artifact-lock의 정적 경로는 확인했으며, 이것을 native ARGO importer 또는 OS-origin/scorer custody의 검증으로 확대하지 않았다.

## Read manifest

아래 경로는 동결 묶음 기준이다. SHA-256과 각 finding/sound point의 정확한 evidence 범위는 `review.json`에도 보존했다. 원문 논문 7편은 이 runtime lane에서 새로 읽지 않았으며 문헌 효능/신규성 재판정에 사용하지 않았다.

| 경로 | 읽기 범위 | SHA-256 |
|---|---|---|
| `packet/AGENTS.md` | FULL_FILE_READ · 1-269 | `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455` |
| `packet/docs/argo/agent-brief.md` | FULL_FILE_READ · 1-49 | `a76a9cfd7b1c0e877930c144dba446035c4c121b11324bb4bb759592c09fd14d` |
| `packet/docs/argo/migration-state.json` | FULL_FILE_READ · 1-299 | `bb7105c7ce57e6f29d67b0f1e811b3128828f0fd3f0dfee2954d43d52f8e103e` |
| `packet/docs/argo/research-to-prototype-objective.md` | FULL_FILE_READ · 1-17 | `f7c8b1d578f3f5ac4f1a85b7422d74a6e8def96bcbd80aad88578b3e019ddcd4` |
| `packet/docs/argo/research-decision-contract.md` | FULL_FILE_READ · 1-56 | `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de` |
| `packet/docs/argo/paper-pipeline-contract.md` | FULL_FILE_READ · 1-72 | `f23a67c1432df8a79cc0946fd817aff55127dc6bb4db6b7a828ccbe965f3978c` |
| `packet/paper/research/integrated-research-design-active.md` | FULL_FILE_READ · 1-137 | `63f0a873bcf04540d8a3143dbca31446790dc101ba1c436476dd5143f8c9889a` |
| `packet/paper/research/autonomous-thesis-to-prototype-20260908/README.md` | FULL_FILE_READ · 1-91 | `68e281b339772ab44add809b2b0bdd78ea54200f222088d094f1a6869f5262a1` |
| `packet/paper/research/autonomous-thesis-to-prototype-20260908/decision-record.json` | FULL_FILE_READ · 1-103 | `96ee5c2311156ece38123f577ea70aaa2d053dea6e23d538f87aa961c97b68a1` |
| `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` | FULL_FILE_READ · 1-224 | `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` |
| `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.json` | FULL_FILE_READ · 1-585 | `e6df58ef7b959ad807fdc64ab02f2c979502005f2d3e7892566f33d1f9103164` |
| `packet/paper/research/exa-prior-art-expansion-20260908/README.md` | FULL_FILE_READ · 1-62 | `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` |
| `packet/paper/research/exa-prior-art-expansion-20260908/decision-update.json` | FULL_FILE_READ · 1-85 | `95c3346a61715e9ad18619339d535e79cbf9a6cfd62902f0f44c1f4607aeda30` |
| `packet/paper/research/exa-prior-art-expansion-20260908/source-evidence.json` | FULL_FILE_READ · 1-85 | `3ff020aae62e692b0b3a5957a729fe374cedbde01bbafc098bb5b4a97120f56c` |
| `packet/paper/research/exa-prior-art-expansion-20260908/context-graph.json` | FULL_FILE_READ · 1-126 | `2ab50828e97b40355bfb6a5b46f832a948f3cbd43a3b15c23afe84387813a943` |
| `packet/paper/research/fable51-design-review-20260907/integration/integrated-study-design.json` | FULL_FILE_READ · 1-326 | `f73eef99ba186f5882fc79a07e72c911d0d54ce8f85a4a7c08560e551940c72e` |
| `packet/paper/research/fable51-design-review-20260907/integration/research-completion-contract.json` | FULL_FILE_READ · 1-114 | `4a25e882cad5e031f2802415d833d51bd8bb4add404e51221777262d9dc951a6` |
| `packet/paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` | FULL_FILE_READ · 1-172 | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` |
| `packet/paper/research/public-ml-programme-qualification/house-price-p0/effective-authority-v4.json` | FULL_FILE_READ · 1-34 | `d724ae5c6fdac744dfe6fd1a9e0e1b1bae6ee8292cf7c78472aa30a3a90bb2d1` |
| `packet/paper/research/public-ml-programme-qualification/house-price-p0/p0-observability-disposition-v1.json` | FULL_FILE_READ · 1-129 | `0c0f8f50dc2439638e32e8f08a9bef9efe24a3c4e4d64a85cbaef9398e5b29ae` |
| `packet/paper/research/public-ml-programme-qualification/house-price-p0/final-assessment-source-qualification-v1.json` | FULL_FILE_READ · 1-37 | `b207859d9c372e3b024349f725e836c9ac0accc06c053cc72523cd864acd4da6` |
| `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json` | FULL_FILE_READ · 1-266 | `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` |
| `packet/packages/agent/src/agent.ts` | FULL_FILE_READ · 1-604 | `f7e2b0b720bace0a791d5e5f8dc052b8f42f9388fe25a812361d062723a94934` |
| `packet/packages/coding-agent/src/core/agent-session-runtime.ts` | FULL_FILE_READ · 1-782 | `9a4b34a2219637d8e5750efbc37b279fe72367d097414875835510981b3ab5c4` |
| `packet/packages/coding-agent/src/core/agent-session-services.ts` | FULL_FILE_READ · 1-270 | `0e76f2f664238c830cee5a1626fd769f237e9a0810320b5ba92da70eb32af249` |
| `packet/packages/coding-agent/src/core/rlm-runtime.ts` | FULL_FILE_READ · 1-255 | `3efe402235d0a7652b09688fd4ac8dd188f62bdeafa932e4b250dfab4ca11cc7` |
| `packet/metadata/current-p0-protocol.json` | FULL_FILE_READ · 1-1 | `2e4ce502ae98280f8d43839cc11e43b26d66a149a89614a788165b5a0c0704bf` |
| `packet/metadata/current-operational-disposition.json` | FULL_FILE_READ · 1-31 | `eed99338c83b70d6e149c7c1755b577233de32e9b38b05680e045195f1abb3a1` |
| `packet/packages/coding-agent/src/core/kernel/repl-manager.ts` | SELECTED_INTERFACE_SECTIONS_ONLY · 719-790, 1323-1502 | `7625fc7f99cbaa59bac3620560ad2c2ac04e8c9245c8565ec87e2c5178dd8278` |
| `packet/packages/coding-agent/src/core/refinement/refinement.ts` | SELECTED_INTERFACE_SECTIONS_ONLY · 660-900 | `b8dfffe650a66e89672869b3d66f4625ff91e35f962a73cbd4a3671ab0cab897` |
| `packet/experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py` | SELECTED_INTERFACE_SECTIONS_ONLY · 704-1675 | `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` |

## 확인하지 않은 것

- No retained research-paper text was freshly read in this runtime lane; author-reported scholarly mechanisms/results are not independently re-adjudicated here.
- No other reviewer or historical review reports, raw datasets/labels, credentials, private instance files, live ORX server, account state or external resources were accessed.
- No tests, model calls, training, scientific runs, installs, configuration/source/manuscript changes, commits or external writes.
- No full REPL-manager, refinement module or bridge-wide audit; only the manifest line ranges support source judgments. Underlying trusted I/O, process capture, scorer implementations and raw receipts outside the packet were not opened.
- Crosswalk citations to files absent from the frozen packet were not followed.
- The prior host nonblocking/background restriction was not re-enacted; no universal impossibility inferred.

공통 review contract, runtime assignment, packet manifest와 `planning-with-files/SKILL.md`를 읽었다. 지정 출력만 쓰는 조건에 따라 계획·진행·완료 상태를 `review.json`에 함께 기록했다. `docs/CODEX-NAVIGATION-GUIDE.md`는 지정 workspace 경로에 없었다. 다른 입력/source/config는 수정하지 않았다.
