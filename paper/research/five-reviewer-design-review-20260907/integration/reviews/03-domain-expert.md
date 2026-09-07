# 역할 3 도메인 전문가 설계 검토 — Sol/xhigh

- **판정:** `REVISE_BEFORE_EXPERIMENT`
- **검토 범위:** 기술 정확성, native ownership/interface, 관련 연구, 복구·권한, paper-to-prototype lineage
- **packet SHA-256:** `a89c23c4c5e5fda79fc3efd2301a3c33eb3b13f1bdc8fd6a597a85bdd59e2fe9`
- 이 판정은 **연구설계 수정 요구**이며 출판, 실험 실행, 설치 또는 native construction 승인으로 해석하면 안 된다.

## 총평

패킷은 중요한 기반을 이미 갖췄다. Pi/Prime의 실행 기질과 과학적 상태를 구분하고, Exa discovery를 근거 승인과 분리하며, ORX/OpenResearch를 향후 scientific-run authority로 두고, 연구 수정과 엔진 수정을 분리하려는 방향은 타당하다. 특히 세션/하네스 상태를 과학적 권위로 쓰지 말라는 제한은 정확하다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` §Candidate native ownership, lines 30–34; `paper/research/five-reviewer-design-review-20260907/packet/paper__research__active-graph-handoff-manifest.json` lines 1373–1378).

그러나 현재 pivot은 통합 아키텍처 선택 전에 `research-continuity`와 negative-result reuse를 사실상 선택했다. `study-contract.json`은 primary contrast를 이미 하나로 고정하면서 graph를 선택 사항으로 내리고, 첫 진단을 negative-result reuse로 정한다 (`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json` lines 8–10, 47–68). 최신 지시는 이를 승인된 결론이 아닌 도전할 초안으로 명시한다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` lines 13–15, 34–43). 따라서 자료는 충분하지만 실행 설계는 아직 준비되지 않았다.

## 차단 이슈

### D3-B1 — lifecycle owner와 port 계약이 서로 충돌한다 (`BLOCKER`)

`paper/research/five-reviewer-design-review-20260907/packet/paper__research__material-mechanism-evidence-map.md`는 discovery adapter의 owner를 `PaperService`로 둔다 (lines 23–25). 반면 `paper/research/five-reviewer-design-review-20260907/packet/docs__argo__paper-pipeline-contract.md`는 `PaperService`가 문헌을 검색하지 않는 deterministic downstream view라고 규정한다 (lines 1–4, 55–61). 이는 단순 명칭 문제가 아니다. 검색이 release view 안으로 들어가면 discovery 후보가 claim evidence로 승격되거나, paper build가 네트워크·모델 결과에 따라 달라질 수 있다.

**수정:** `DiscoveryPort`는 research plane의 별도 owner로 둔다. 출력은 `DiscoveredSourceCandidate{query, provider, timestamp, url, metadata}`뿐이어야 한다. 별도 `SourceEvidenceService`가 retained bytes, version, hash, locator, read level을 검증하여 `ReviewedSource`를 만든다. `PaperService`는 closed `PaperEvidenceSnapshot`만 읽는다. ORX adapter도 `run/status/cancel/logs` lifecycle을 소유하지 말고 identity-bound request/receipt translation만 담당해야 한다.

**종결 증거:** owner×command/event matrix, 각 port의 typed input/output/error/idempotency 계약, `discovery_only`의 paper 진입 거부 fixture, ORX 외부 run ID 중복 등록 거부 fixture, owner 없는 상태와 두 owner 상태를 모두 실패시키는 contract test.

### D3-B2 — Prime 복구는 과학적 replay가 아니며, 불확실 run 조정 상태가 없다 (`BLOCKER`)

REPL snapshot은 top-level variable별 best-effort `dill` 저장이다. open file, socket, GPU tensor 같은 객체는 건너뛰고, 변수당 16 MiB·전체 256 MiB 상한이 있다 (`packages/coding-agent/src/core/kernel/state-snapshot.ts` lines 1–14, 19–37). restore와 snapshot은 실패해도 `null`로 돌아가는 best-effort 경로다 (`packages/coding-agent/src/core/kernel/repl-manager.ts` lines 1328–1415). daemon은 crash 전에 받은 mutating command의 결과가 없으면 이를 **재실행하지 않고 uncertain**으로 둔다 (`packages/coding-agent/src/modes/daemon/command-recovery-journal.ts` lines 48–52; `packages/coding-agent/src/modes/daemon/daemon-supervisor.ts` lines 3731–3813). 이 동작은 안전하지만, 외부 ORX run이 실제 시작됐는지 판별하지 못한 채 새 run을 만들면 중복 실행과 budget 위반이 발생한다.

**수정:** scientific event store에 `RUN_INTENT_FROZEN → LAUNCH_REQUESTED → RECONCILING → RUN_ID_BOUND → TERMINAL_RECEIPT_IMPORTED` 상태를 둔다. `external_request_id`와 `protocol_fingerprint`를 먼저 영속화하고, crash 후에는 ORX 조회로 기존 run을 bind하거나 `NOT_FOUND` 증거 뒤에만 새 실행 승인을 요청한다. REPL 변수·compaction summary·RLM registry는 cache/view로만 취급한다. Session JSONL도 malformed line을 건너뛴다 (`packages/coding-agent/src/core/session-manager.ts` lines 375–390, 540–559). 그러므로 scientific events에는 sequence, previous digest, event digest, schema version, fsync/transaction 경계가 필요하다.

**종결 증거:** launch 전/중/후 강제중단 fixture, 같은 `external_request_id`의 at-most-once bind, ORX lookup timeout/ambiguous/not-found 분기, snapshot에서 빠진 변수 뒤 fresh-process graph digest 동일성, 손상된 중간 event의 fail-closed replay.

### D3-B3 — graph representation과 loop control을 분리하지 않아 선택 근거가 없다 (`BLOCKER`)

현재 draft는 package 효과만 재고 개별 graph·memory·refine 효과를 주장하지 않는다고 한다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` lines 30–38, 104–108). 이는 과장 방지에는 좋지만, 어느 통합 설계를 prototype으로 선택할지는 답하지 못한다. graph가 이겨도 원인은 typed representation, compulsory checklist, 추가 노출 token, critique 호출, 자동 invalidation 중 무엇인지 알 수 없다. 반대로 null이면 graph를 전부 버려야 하는지도 알 수 없다.

**수정:** 개발용 architecture-selection 단계에서 2×2를 사용한다. 축 R은 `versioned graph projection` 대 `structured source-backed notebook/tree`, 축 C는 `enforced dependency/applicability traversal` 대 `동일 정보를 가진 advisory/free iteration`이다. 모든 조건에 같은 source bytes, result history, model/version/thinking, tools, candidate/evaluation opportunities, root+descendant budget을 준다. 이 단계는 treatment 선택용이며 확증 결과가 아니다. 별도 task/source families에서 선택한 단일 통합 설계를 가장 강한 경쟁 설계와 다시 고정해 확증한다. negative-result reuse와 interruption은 진단/스트레스이지 primary thesis 자체가 아니다.

**종결 증거:** 사전 고정된 네 arm의 유일 차이 diff, delivered/used evidence와 token/tool/compute accounting, task/source-family split, pilot과 confirmatory family 분리, MDE/power/invalid handling/selection rule, 결과를 보기 전 서명된 최종 두-arm protocol.

### D3-B4 — independent assessment의 권한·맹검·정보 흐름이 명세되지 않았다 (`BLOCKER`)

초안은 independent assessor를 요구하지만 “역할 분리만으로 의미적 독립성이 생기지 않는다”고만 한다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` lines 44–51, 67–80). 실제 RLM child contract는 parent session, model, active/allowed tools를 전달할 수 있으며 별도의 `assessor` 보안 역할을 정의하지 않는다 (`packages/coding-agent/src/core/rlm-runtime.ts` lines 214–253). 기존 capability map도 independent Study A scorer가 없다고 기록한다 (`paper/research/capability-map.md` lines 33–40).

**수정:** 개발 평가와 final hidden assessment를 분리한다. final assessor는 `artifact_id + frozen_evaluation_manifest`만 받고 treatment label, research trace, graph state, hidden test bytes, candidate selection 권한, launch 권한을 받지 않는다. 결과는 모든 final selection이 잠긴 뒤 공개한다. deterministic scorer, blinded rubric judge, human calibration의 역할과 disagreement rule을 미리 정한다. 같은 모델 family의 critic은 독립 측정자가 아니라 보조 비평으로만 표기한다.

**종결 증거:** capability allowlist/denylist, assessor가 hidden bytes·treatment label·scorer code를 읽지 못하는 negative probes, selection timestamp가 score visibility보다 앞선 receipt, calibration set agreement와 adjudication 기록, score가 graph/result를 자기 승인하지 못하는 one-way import test.

## 주요 수정과 관련 연구

### D3-M1 — 새 8편 bundle만으로 graph-based autonomous research의 prior-art 경계가 닫히지 않는다 (`MAJOR`)

8편의 source/locator와 한계 분석은 재사용 가능하며 모든 성능은 author-reported다 (`paper/research/long-horizon-harness-benchmark-20260907/source-receipts.json` lines 33, 87, 139, 203, 251, 294, 340, 383, 436, 470). 다만 저장된 더 넓은 corpus에는 AI Scientist, Co-Scientist, SciAgents, EviGraph, SCOPE, ResearchClawBench, Arbor, RSEA, Evo-Bench, Regimes, HarnessOpt-Bench, claim-aware lineage 연구가 이미 정리돼 있다 (`docs/argo/research-foundations.md` lines 44–73). contribution ledger도 graph, protocol comparability, dual refine, paper lineage에 이 비교를 요구한다 (`paper/research/five-reviewer-design-review-20260907/packet/docs__argo__thesis-contribution-ledger.md` lines 17–32). 이를 새 DecisionRecord와 study arms에 실제로 bind해야 한다.

**종결 증거:** 각 architecture choice에 mechanism-distinct prior, counterevidence, exact locator, 구현/평가 차이를 연결한 matrix와 “기존 기제/재유도/수정/미분류 residual” 판정. 저장 source의 hash/read receipt가 부족할 때만 root가 재조회한다.

**미독 후보(검증 주장 아님, root retrieval 후보):** `MLAgentBench`, `MLE-bench`, `PaperBench`, 최신 `AI Scientist` 후속 연구. 목적은 실제 ML experimentation, research reproduction, hidden evaluation의 task 적합성과 실패 정의를 확인하는 것이다. 제목·판본·주장·코드는 아직 이 검토가 검증하지 않았다.

### D3-M2 — paper completion과 prototype promotion 사이에 선택 record가 빠져 있다 (`MAJOR`)

`PaperEvidenceSnapshot`과 immutable build 계약은 강하다 (`paper/research/five-reviewer-design-review-20260907/packet/docs__argo__paper-pipeline-contract.md` lines 30–52). 그러나 현 study contract에는 task, metric, invalid handling, selection rule, n, power, exact budget/command가 모두 비어 있다 (`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json` lines 12–22, 88–100, 118–132). 기존 원고는 graph 설계와 계측 점검을 중심으로 이미 abstract/RQ를 좁힌 상태다 (`paper/research/five-reviewer-design-review-20260907/packet/existing-thesis-ko.qmd.txt` lines 35–53, 114–150). 지금 본문을 발전시키면 design selection 결과를 사후 합리화할 위험이 있다.

**수정:** `ArchitectureSelectionRecord`가 chosen design, rejected alternatives, null-result fallback, exact evidence cutoff, prototype mapping을 잠근 뒤 manuscript research-complete gate를 연다. 기존 16-task/96-check material은 instrument validation으로만 보존한다. 최종 원고 계획은 ① 문제/관련 연구 ② owner-neutral interface ③ architecture selection ④ frozen confirmatory method ⑤ 모든 launch·failure 포함 결과 ⑥ 한계로 한다. ARGO/NAIS/Prime/ORX/Exa 운영명과 내부 경로는 출판 본문에서 제외하되 정확한 학술 논문 제목은 유지한다 (`paper/research/five-reviewer-design-review-20260907/packet/manuscript-boundary.md` lines 22–39).

**종결 증거:** 아래 완료 기준 전부와 signed selection record, closed evidence snapshot, claim-to-source/run audit, 내부 prototype mapping과 공개 generic method의 분리 검사.

## 결정적 실험

1. **Preflight(효능 아님):** owner/permission, source 승격, event replay, ORX reconcile, assessor isolation을 failing-first fixture로 검증한다.
2. **Architecture selection:** 서로 독립인 개발 task/source families에서 위 2×2 R×C를 동일 hard ceiling으로 비교한다. primary가 아니라 설계 선택 단계다.
3. **Confirmatory study:** 선택된 통합 설계와 개발 단계의 최강 competitor를 새로운 공개 small-compute ML campaign families에 paired 배치한다. 각 campaign은 baseline, 둘 이상의 mechanism-distinct 후보, 실제 training/analysis, 관측 기반 다음 결정, 고정 stop을 가진다. final artifact는 hidden scoring 전에 하나만 선택한다.
4. **Primary endpoint:** preselected final artifact의 task-specific held-out performance. 별도로 full cost, valid/useful scientific decisions, repeated failure/false suppression, preservation regression, interruption recovery를 보고한다. retrospective replay와 schema pass는 조작·진단만 담당한다.
5. **가장 강한 대안 설명:** graph 우위가 관계 구조 때문이 아니라 compulsory checklist, 더 많은 visible tokens, 추가 critic/evaluation opportunity 또는 evaluator leakage 때문에 생긴다. R×C와 delivered/used-context 계측이 이를 직접 겨냥해야 한다.

## native prototype mapping

| 단계 | 유일 owner | prototype port / 금지 경계 |
|---|---|---|
| process/session/tool loop | Pi/Prime daemon + `AgentSession` | 세션, REPL, RLM, TUI, recovery 소유; scientific truth 금지 |
| discovery | research-plane `DiscoveryPort` | Exa 등은 candidate metadata만 반환; claim 승인 금지 |
| source/evidence | `SourceEvidenceService` | bytes/hash/version/locator/read-level 승격 |
| research state | append-only `ResearchEventStore` + deterministic graph projection | process supervisor/run registry 금지 |
| planning | bounded loop policy | `DecisionRecord` 제안; scorer·budget·authority 수정 금지 |
| scientific execution | ORX/OpenResearch | run lifecycle와 immutable artifact ID 소유; Prime은 adapter 호출/대기만 |
| final evaluation | evaluator-owned isolated assessor | hidden state와 score 소유; selection/graph mutation 금지 |
| research-refine | research lineage | successor hypothesis/design/decision만 append |
| engine-refine | Continual Harness promotion lineage | prompt/memory/skill 변경; held-out+human promotion 전 scientific state 불변 |
| paper | read-only `PaperService` | closed snapshot에서만 render; prototype roadmap 비공개 |

## 설치 기준

초기에는 graph DB나 새 orchestrator를 설치하지 않는다. canonical JSONL/SQLite event store와 deterministic projection으로 기준선을 만든다. 새 dependency는 (a) 사전 지정한 correctness 또는 p95/recovery 한계를 실제로 넘고, (b) owner 중복 없이 그 병목을 해결하며, (c) project-local pin, 7-day release-age, license/NOTICE, security/SBOM, offline export, deterministic replay, rollback 검사를 통과할 때만 후보가 된다. 설치 허용은 외부 계정, paid compute, run 권한이 아니다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` lines 5–9).

## 재사용과 격리

**재사용:** exact-version source/locator/audit, byte/hash/protocol 도구, owner를 확인한 Pi/Prime source, B3의 작은 allocation 개발 관측은 각각의 원래 범위에서 유지한다. 더 넓은 기존 corpus도 새 설계에 다시 연결한다.

**격리:** C64는 causal claim `INVALID`이고 nominal p값으로 구제하지 않는다. T3는 one-task dry run, T1′은 48회 중 evaluator crash 42회, B2는 persistent typed graph 단독 조작이 아니므로 efficacy가 아니다 (`paper/research/five-reviewer-design-review-20260907/packet/paper__research__material-mechanism-evidence-map.md` lines 7–9, 31–40). graph/retrospective replay는 구조·복원 진단뿐이다. UI-parity v12는 30/30 pre-observation crash로 영구 `INVALID/NOT_ADMITTED`, font는 exact five-call compatibility만, World-init는 static-only다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` lines 17–26). 모든 author-reported performance와 unverified code는 local efficacy 밖에 둔다. 실패 artifact는 삭제·덮어쓰기·분모 제외하지 않는다.

## 작성 전 최소 완료 기준

- 2×2 선택 기록과 별도 confirmatory protocol이 immutable하게 고정됨.
- 독립 task/source families, split, metric, invalid score, final selection, MDE/power, total budget/command가 확정됨.
- owner/port/permission/reconcile contract와 recovery·tamper negative fixtures가 통과함.
- 모든 launch, failure, critique, recovery, descendant cost가 보존됨.
- 최소 둘 이상의 독립 campaign family에서 최종 artifact hidden score와 full-cost 결과가 확보됨. 정밀 null도 유효 결론으로 허용함.
- literature matrix가 기존 broad corpus와 새 8편을 exact locators로 연결하고 미검증 코드를 분리함.
- chosen design과 rejected alternatives가 `ArchitectureSelectionRecord`에 남고 prototype mapping이 고정됨.
- closed `PaperEvidenceSnapshot`, claim/run/citation/number audit, 내부 브랜드·경로·roadmap 누출 검사가 완료됨.

## 기술 점수(설명용, 1–5)

- native ownership 명료성: **2/5** — 방향은 맞지만 `PaperService` 충돌과 ORX port 상태기가 비어 있다.
- recovery/replay 안전성: **2/5** — Prime 복구는 강하지만 scientific side-effect reconciliation이 없다.
- architecture identifiability: **2/5** — 현재 package contrast로 representation/control을 분리할 수 없다.
- evidence provenance 재사용성: **4/5** — bytes/hash/locator와 실패 보존은 강하다.
- related-work binding: **3/5** — 넓은 corpus는 있으나 새 선택 계약에 연결되지 않았다.
- independent assessment: **2/5** — 원칙은 있으나 capability와 맹검 계약이 없다.
- paper-to-prototype lineage: **3/5** — downstream 구조는 있으나 selection/promotion gate가 없다.
