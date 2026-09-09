# Graph · memory · research-loop 독립 검토

**판정: 연구 종합은 타당하며, 향후 task-bound 비교 명세에 세 가지 보완이 필요하다.** 현행 P0는 C0 feasibility다. 아래 공백은 P0 무효나 native 구현 결함이 아니며 새 구현·실행 승인을 요구하지 않는다.

검토 독립성은 fresh model context와 `graph/` 출력 소유권 분리다. 다른 reviewer의 보고서·대화를 읽거나 연락하지 않았다. 오류 독립성, 독립 ground truth 또는 OS sandbox를 뜻하지 않는다.

## 근거가 타당한 부분

- Local context-graph.json explicitly identifies itself as a research map; Source→DesignInterpretation→P1→thesis/prototype edges describe future evidence flow, not an implemented native controller. It is sufficient as a navigation/audit map for this scope.
- C/G match compulsory obligations and preserve a strong B/C evidence-capable control; G−C is correctly a graph-control package, not pure topology. Graph extraction cost/errors count and simpler designs may win.
- Scientific run authority, process/session ownership, audit history, research decisions and engine refinement are explicitly separated. UNKNOWN does not authorize blind retry.
- Frozen current P0 is C0 feasibility only, with one fresh context and preserved opportunities; current operational disposition records zero programmes/runs/fits/hidden scores. Prospective specification gaps do not reverse preparation or add P0 requirements.

## 세 가지 명세 공백

### GRAPH-01 · medium · Claim 수정·범위 축소 후 근거와 의존성을 판정할 task-bound 의미 계약이 없다.

**분류:** `directly_supported` / `prospective_specification_gap`

동일 C/G 의무를 집행하고 invalid carryover·false suppression·preservation을 비교하려면 두 조건이 같은 답을 적용해야 한다. 현재 자료만으로는 문장/범위가 바뀐 claim에 옛 support를 붙일 수 있는 조건, 내용 의존 edge와 문맥 edge의 차이, 독립 support가 남은 claim의 상태가 결정되지 않는다. 한 task의 negative result로 전체 family를 막거나, 수정 claim이 검증 없이 옛 positive evidence를 받는 상반된 구현 모두 현행 상위 문구에 맞는다고 주장할 여지가 있다.

**최소 수정:** 다음 P1 task-bound 명세에 작은 claim-transition/판정 표를 넣는다. claim text/revision/hash와 task에 필요한 scope 및 source/protocol identity를 묶고, support 승계는 해당 revision·scope에 대한 재판정 결과로 기록한다. contextual/content dependency, 공동필수/대체 support가 해당 task에 존재하면 구별하고, scoped negative·execution failure/UNKNOWN·source correction 각각의 active/qualified/recheck/retracted 결과와 무관 evidence 보존을 예시로 고정한다. 새 graph backend 구현은 필요 없다.

**저비용 반증 확인:** 문서만으로 네 사례의 기대 상태를 C/G 공통으로 표시한다: 한정 실패와 무관 task, narrowed claim과 옛 support, 두 독립 support 중 하나 철회, contextual edge만 연결된 노드. 두 독립 적용자가 같은 활성 claim/재검증 집합을 도출할 수 있는 기존 계약이 제시되면 이 공백은 해소된다. 이 검사는 제안이며 실행하지 않았다.

**불확실성:** Frozen packet 내 후보 명세에 한정한 부재 판단이다. packet 밖의 task-bound 규격 존재는 확인하지 않았다. 현재 P0는 C0 feasibility이므로 이 공백을 P0 무효나 native 구현 결함으로 판정하지 않는다.

**근거:**

- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` L30–35 · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` — Latest synthesis requires revised evidence applicability but explicitly defers specification.
- `packet/paper/research/exa-prior-art-expansion-20260908/decision-update.json` L30–36 · SHA-256 `95c3346a61715e9ad18619339d535e79cbf9a6cfd62902f0f44c1f4607aeda30` — UPD-3 asks for revised evidence applicability; no selected transition rule.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L131–149 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — Typed/versioned dependencies, active revision and affected set are named without an operational applicability predicate.
- `packet/docs/argo/research-decision-contract.md` L43–50 · SHA-256 `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de` — Scoped assimilation and prohibition on globally closing a family are already mandatory.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L685–728 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0` — Equation 15 copies old positive queries to edited content and resets its negative set; useful concrete prior-art boundary.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L2035–2050 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff` — EviGraph distinguishes content dependency from contextual reachability.

### GRAPH-02 · medium · Fresh-context 성공이 복구된 결정의 보존인지 새 행동의 일치인지 정해지지 않았다.

**분류:** `directly_supported` / `prospective_specification_gap`

동일 event에서 deterministic active view를 만드는 일과 LLM이 새 next-action proposal을 생성하는 일은 다른 검증 대상이다. 같은 다음 행동을 문자 그대로 요구하면 합법적인 다른 선택을 복구 실패로 오인할 수 있고, 반대로 선택한 행동만 일치하면 최신 retraction·남은 budget·UNKNOWN run이 빠진 capsule도 성공으로 보일 수 있다. 공통 audit graph가 생성한 관계/요약을 어느 조건에 얼마나 공급하는지도 정하지 않으면 G−C의 정보 차이가 정의되지 않는다.

**최소 수정:** P1 capsule/복구 항목에서 이미 commit된 선택·pending intent의 재현과 재개 후 새 proposal 생성을 구분한다. capsule의 revision/event watermark, 필수 retained/invalidated evidence pointer, pending run identity/UNKNOWN, 남은 기회·비용 상태, generator/prompt version과 context ceiling을 선언하고 B/C/G의 동일 원자료 접근과 audit projection 비노출 경계를 명시한다. 복구 secondary는 상태·근거 보존 및 허용 행동 집합으로 채점하고, exact next action은 이미 commit된 경우에만 요구한다.

**저비용 반증 확인:** 한 번의 중단 전 기록을 사용해 latest retraction과 미해결 run이 있는 handoff를 손으로 점검한다. 두 합법적 후속 행동이 다르더라도 필수 상태가 보존되면 둘 다 통과하도록 rubric을 적용하고, 최신 무효화가 빠졌는데 행동만 같은 capsule은 실패시키는지 확인한다. 새로운 model run이나 P0 변경 없이 정의를 판별할 수 있다. 미실행 제안이다.

**불확실성:** Next action이 이미 기록된 결정을 뜻한다면 실제 충돌은 없다. 현재 문구가 그 의미를 명시하지 않아 발생하는 해석 공백이다. P0에는 별도 exact handoff/기회 보존 계약이 있으며 이를 미정이라고 취급하지 않았다.

**근거:**

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L73–81 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — Fresh session should reconstruct candidate/evidence/run identity and next action.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L186–194 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — Fresh replay is expected to reconstruct the same active revision and next action.
- `packet/paper/research/fable51-design-review-20260907/integration/integrated-study-design.json` L239–287 · SHA-256 `f73eef99ba186f5882fc79a07e72c911d0d54ce8f85a4a7c08560e551940c72e` — Arm table leaves capsule generator/context ceilings and activation receipt details null; states logging cannot establish semantic sufficiency.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json` L62–98 · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — Neutral audit graph is hidden from treatment decisions while candidate policy emits the capsule.

### GRAPH-03 · medium · 연구 graph rollback과 되돌릴 수 없는 event/receipt의 경계가 명세되지 않았다.

**분류:** `directly_supported` / `prospective_specification_gap`

현재 owner 분리는 타당하지만 conflict 탐지 이후 어느 revision을 채택할지, source 철회 뒤의 graph 복원에서 과거 active 상태를 다시 살릴 수 있는지, 중간 결과·비용·이미 잠근 artifact를 되돌리는지는 결정되지 않는다. 하나의 동일 event열에서 합법적으로 다른 active 상태가 만들어지면 preservation/replay 비교가 의미를 잃는다. 이는 dual-owner 구현이 발견됐다는 주장이 아니다.

**최소 수정:** 다음 task-bound event/transition 표에 event ID와 parent revision, projector version, policy proposal과 accepted commit의 구분, 중복·순서 역전·동시 수정의 처리 원칙을 지정한다. rollback은 연구 해석/projection의 새 descendant로 표현하고 source retraction, external receipt, 이미 쓴 예산, artifact lock과 원본 근거를 지우거나 외부 실행을 취소한 것으로 만들지 않는다고 명시한다. 충돌·부분 repair는 적용 상태를 보존한 채 명시적 unresolved/recheck로 남길 수 있다. 새로운 process/run authority나 별도 backend는 필요 없다.

**저비용 반증 확인:** 문서상 사건열 source-v2 철회 → 연구 수정 제안 → external terminal receipt 수신 → 수정 중단 → 이전 projection 복원을 추적한다. receipt·사용 비용·철회 사실은 유지되고 stale support가 재활성화되지 않으며 중복 receipt가 새 run으로 바뀌지 않는 하나의 결과가 도출되는지 확인한다. 제안만 했으며 실행하지 않았다.

**불확실성:** Append-only history와 과거 outcome 보존 원칙은 이미 있다. 발견한 것은 그 원칙을 동시에 만족시키는 commit/rollback 절차가 이 candidate packet에 없다는 점이다. 실제 runtime 동작이나 ORX 버그는 검사하지 않았다.

**근거:**

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L141–143 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — ResearchEventStore feeds active ResearchState projection.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L164–168 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — Research loop is separate from engine-refine; negative and execution-failure boundaries are retained.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` L186–194 · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc` — A single event history, deterministic replay and conflict detection are proposed without accepted revision/rollback transaction semantics.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json` L62–98 · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — Store and candidate-policy ownership are named, but accepted-mutation/commit boundary is not specified.
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json` L229–261 · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b` — External reconciliation and at-most-once local receipt binding are already constrained.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L2060–2111 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff` — EviGraph explicitly stages repair groups while retaining debited budget and immutable execution records.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L2143–2176 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff` — Prior art gives checkpoint selection and append-only history; historical graph material is not current-run result evidence.

## 원문 대조 결론

- **EvoGraph-Mem active-negative-set concern** (`directly_supported`): Valid conditional invariant, not an observed implementation bug. Starting empty and restricting edits to retrieved active nodes, ADD/REVISE create active nodes with empty negative sets, KEEP preserves that set, and ARCHIVE/old REVISE deactivate the only nodes receiving negative evidence. Edge updates do not change this. Therefore the negative penalty is zero for reachable active candidates under those assumptions. Nonempty initialization or an additional reactivation/update path can invalidate the invariant. The latest README states these assumptions and preserves this uncertainty correctly.
  - `packet/paper/research/exa-prior-art-expansion-20260908/README.md` L41–41 · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L478–608 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L609–792 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L1162–1198 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
- **EvoGraph-Mem evidence inheritance and reported ablation** (`directly_supported`): Equation 15 explicitly transfers old positive query support to the new text; the controller labels usefulness from task feedback. Checking applicability after editing is justified. The 34% archive-enabled versus 31% full-controller GPT-4o-mini PDDL counterexample is accurately scoped to a reported setting, not a universal winner or local result.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L609–728 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L956–988 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` L1035–1052 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
- **EviGraph mechanisms** (`directly_supported`): Typed operational graph, content-dependent repair, scoped negative-result retention and transactional checkpoint/rollback are specified in retained text. This supports narrowing novelty. Source text specifies masked normalized evaluation and common accounting; it does not certify the published implementation or our matched C/G effect.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L211–340 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L1749–1764 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L2035–2176 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`.
  - `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` L2570–2594 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`.
- **Iris mechanisms** (`directly_supported`): Iris explicitly defines claim scope, supporting/refuting pointers, active/qualified/invalidated status, revision and multi-granularity evidence access. The latest synthesis correctly treats these as prior art and preserves evidence rights in controls. The information-management ablation removes persistent knowledge, revision and access jointly, so it cannot identify graph topology alone.
  - `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.02143v1.txt` L727–890 · SHA-256 `120c15dda4a5da8e58f7c549bd185a7d73930c281efb0a7a369bb25e6c165eb6`.
  - `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.02143v1.txt` L1041–1064 · SHA-256 `120c15dda4a5da8e58f7c549bd185a7d73930c281efb0a7a369bb25e6c165eb6`.

원문 대조는 위 method/appendix/해당 결과 구간의 **selected-section reading**이다. 과거 source receipt의 FULL_READ 표기를 이번 fresh full-paper read로 승계하지 않았다. 특히 active-negative-set 불변식은 빈 초기 상태·명시 연산·retrieved active node만 수정한다는 가정 아래의 수식 추론이며, 구현 버그나 재현 실패 판정이 아니다.

## 읽기·검증 manifest

모든 primary target README/decision/context-map/crosswalk는 전체를 읽었다. 아래 해시는 frozen packet bytes에 대해 확인했다. source paper는 표시한 구간만 읽었다. 상세 근거 구조는 동명 JSON에 있다.

- `packet-manifest.json` · full document · SHA-256 `7c687b6014dbf61584a807edfaf0224646feda837861593c84caa63fd68fcae5`
- `review-contract.md` · full document · SHA-256 `90b793608af9b13778df92d5fb6ba823b396105176adaa1017ff976742d73b6c`
- `packet/AGENTS.md` · full document · SHA-256 `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455`
- `packet/docs/argo/agent-brief.md` · full document · SHA-256 `a76a9cfd7b1c0e877930c144dba446035c4c121b11324bb4bb759592c09fd14d`
- `packet/docs/argo/migration-state.json` · full document · SHA-256 `bb7105c7ce57e6f29d67b0f1e811b3128828f0fd3f0dfee2954d43d52f8e103e`
- `packet/docs/argo/research-to-prototype-objective.md` · full document · SHA-256 `f7c8b1d578f3f5ac4f1a85b7422d74a6e8def96bcbd80aad88578b3e019ddcd4`
- `packet/docs/argo/research-decision-contract.md` · full document · SHA-256 `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de`
- `packet/docs/argo/paper-pipeline-contract.md` · full document · SHA-256 `f23a67c1432df8a79cc0946fd817aff55127dc6bb4db6b7a828ccbe965f3978c`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/README.md` · full document · SHA-256 `68e281b339772ab44add809b2b0bdd78ea54200f222088d094f1a6869f5262a1`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/decision-record.json` · full document · SHA-256 `96ee5c2311156ece38123f577ea70aaa2d053dea6e23d538f87aa961c97b68a1`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.md` · full document · SHA-256 `f25a0cbddbf2ac24f7e93101cfe7f9544f3020e976739e51d8d73f1a3439aacc`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/prototype-crosswalk.json` · full document · SHA-256 `e6df58ef7b959ad807fdc64ab02f2c979502005f2d3e7892566f33d1f9103164`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/source-evidence.json` · full document · SHA-256 `31f8e87e0b3270e62f9b1a140fd4d7f10de69f7982dd80d664699316661e31fa`
- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · full document · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0`
- `packet/paper/research/exa-prior-art-expansion-20260908/decision-update.json` · full document · SHA-256 `95c3346a61715e9ad18619339d535e79cbf9a6cfd62902f0f44c1f4607aeda30`
- `packet/paper/research/exa-prior-art-expansion-20260908/context-graph.json` · full document · SHA-256 `2ab50828e97b40355bfb6a5b46f832a948f3cbd43a3b15c23afe84387813a943`
- `packet/paper/research/exa-prior-art-expansion-20260908/source-evidence.json` · full document · SHA-256 `3ff020aae62e692b0b3a5957a729fe374cedbde01bbafc098bb5b4a97120f56c`
- `packet/paper/research/fable51-design-review-20260907/integration/integrated-study-design.json` · full document · SHA-256 `f73eef99ba186f5882fc79a07e72c911d0d54ce8f85a4a7c08560e551940c72e`
- `packet/paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json` · full document · SHA-256 `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60`
- `packet/paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json` · full document · SHA-256 `75782903e0db49a49f777dac7ebacb3d1e501f806fc8042a31b8f94da6202a5b`
- `packet/paper/research/integrated-research-design-active.md` · full document · SHA-256 `63f0a873bcf04540d8a3143dbca31446790dc101ba1c436476dd5143f8c9889a`
- `packet/metadata/current-p0-protocol.json` · full document · SHA-256 `2e4ce502ae98280f8d43839cc11e43b26d66a149a89614a788165b5a0c0704bf`
- `packet/metadata/current-operational-disposition.json` · full document · SHA-256 `eed99338c83b70d6e149c7c1755b577233de32e9b38b05680e045195f1abb3a1`
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` · selected sections 280–792, 956–988, 1035–1058, 1161–1231 · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` · selected sections 170–436, 1648–1765, 2035–2181, 2568–2594 · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.02143v1.txt` · selected sections 727–898, 1037–1088, 1141–1165 · SHA-256 `120c15dda4a5da8e58f7c549bd185a7d73930c281efb0a7a369bb25e6c165eb6`

## 확인하지 않은 것

- Other reviewers or previous review verdict reports; referenced past PASS markers were not inherited.
- Native TypeScript code, Python apparatus implementation and deployed graph/control behavior.
- Source-paper implementations, external repositories, visual PDFs/figures, full fresh paper reads, experiment reproduction or reported effect precision.
- ScienceFlow, Efficiency Matters, Arbor and Life After Benchmark Saturation method/result claims beyond summaries supplied as review targets.
- Credentials, datasets, payloads, accounts, tools installation, external posting and model/test/scientific execution.
- Artifacts outside the frozen packet; no claim that a missing packet detail is absent from every historical file.

모델·학습·실험·source test·설치·외부 posting을 수행하지 않았다. 수정 파일은 `graph/review.md`, `graph/review.json`뿐이다. cheap falsification checks는 후속 문서 검증안이며 이번에 실행한 검사가 아니다.
