# 기제–native 계약표 — active successor

상태: **ACTIVE DESIGN MAP · EFFICACY NOT EVALUATED**
갱신: 2026-09-05T06:52:41+09:00
상위 설계: `paper/research/integrated-research-design-active.md`

이 문서는 2026-09-04 판의 T3/B0/B1/B2 기반 `Adopted/Conditional` 결론을 삭제하지 않고 git 이력에 보존하면서
active 판정에서 대체한다. T3는 한 task dry run, T1′은 48회 중 evaluator crash 42회, B2는 persistent typed ARGO의
단독 조작이 아니므로 효능 채택 근거가 아니다. `pivots=0`도 과제 난이도나 구현 정상의 증거가 아니다.

## 판정 어휘

- `FIXED_SUBSTRATE`: 기존 native 실행 소유권으로 고정하되 이 연구의 효능 기여로 세지 않음
- `CANDIDATE`: 논문 실험으로 비교할 설계안
- `INSTRUMENT_VALIDATED`: 계측·무결성 위험을 실제로 잡았으나 시스템 효능은 미평가
- `DEFERRED`: 첫 contrast가 필요성을 만들 때만 후속 평가
- `OUT_OF_MVP`: 연구 계보에는 있으나 NAIS 현장 최소 구현 밖

## 일곱 재료의 근거·대안·owner/interface·측정 계약

| 재료 | 원문 기제와 적용 범위 | 대안·반례 | native owner와 입출력 계약 | 측정 signature / 비교 | 현재 판정 | NAIS MVP |
|---|---|---|---|---|---|---|
| **1. Pi/Prime 실행 기질** | Prime Agent·RLM·Continual Harness의 worker, AgentSession, persistent REPL, recovery 기제를 계승한다. 문헌은 prior mechanism이며 ARGO 효능이 아니다. locators: `primeagent_harness_architecture`, `primeagent_runtime_repl`, RLM/Continual Harness 보존 receipt. | 별도 orchestrator가 session/worker lifecycle을 다시 소유하면 복구·상태 authority가 분열된다. 단순 shell baseline은 해석용일 수 있으나 native owner 대체가 아니다. | owner: 기존 daemon/AgentSession/worker/REPL/RLM. 입력: goal, messages, tool calls. 출력: transcript, tool result, worker state. Research plane은 이 lifecycle을 호출할 뿐 재구현하지 않는다. | 고정 substrate hash·capability·receipt; 조건 간 동일성. substrate 자체를 주 treatment로 부르지 않음. | `FIXED_SUBSTRATE` | 공개 기반 사용 가능성은 규칙 확인 전 미정. 현장 custom 구현과 구분. |
| **2. Discovery adapter** | Exa 등 검색은 URL·후보 source를 찾는 discovery 역할이다. snippet은 claim evidence가 아니다. PaperQA2/OpenScholar는 retrieval stage별 오류와 precision/recall 분리를 동기화한다. | keyword/OpenAlex/직접 URL, 또는 retrieval 없음. OpenScholar 전체 시스템 효과를 semantic retrieval 단독 효과로 전이할 수 없다. | owner: PaperService의 discovery port. 입력: query, corpus/provider/budget. 출력: URL, metadata, discovery timestamp. claim 승인 출력은 금지. | query/provider/corpus/budget hash, candidate recall·unsupported source; retrieval이 병목일 때만 별도 screen. | `DEFERRED` | 최소 source discovery는 필요할 수 있으나 provider 선택은 고정되지 않음. |
| **3. 원문·evidence plane** | 발견 URL을 저장 bytes/hash와 실제 읽은 span으로 승격하고 적용 범위·반례를 기록한다. PROV/RO-Crate는 교환·패키징 기제이지 과학적 타당성 보장이 아니다. | snippet 승인, 경로만 기록, self-attested digest는 기각. 출처 하나 철회가 독립 출처까지 자동 무효화하지 않는다. | owner: PaperService/source store + append-only evidence journal. 입력: source bytes, version, locator. 출력: immutable source ID, hash, span, scope, review status. | byte/hash/span 재도출, source→claim reachability, unsupported claim 수. | `INSTRUMENT_VALIDATED`; scientific benefit는 미평가 | **필수 후보**. 출처와 적용 범위를 시연해야 함. |
| **4. Versioned research/context graph** | source→claim→alternative→decision→action→run/result→successor와 revision/retraction dependency를 표현한다. A-MEM은 기억 QA 근거일 뿐 과학 graph 필수성 증명이 아니다. | flat ledger, result-driven tree, proximity graph. graph node 수나 query 도구 존재만으로 control 효과를 주장할 수 없다. | candidate owner: native ResearchState projection. AgentSession 소유 금지. 입력: evidence/decision/run events. 출력: revisioned snapshot, dependency query, affected-set/reopen action. APP의 LangGraph StateGraph/SqliteSaver는 구현 후보 중 하나이며 native append-only event+projection 또는 SQLite event store와 비교한다. | 주 contrast `TYPED_POLICY − RESULT_TREE_POLICY`; relevant invalidation과 unrelated perturbation, fresh-context handoff. | `CANDIDATE`; efficacy 0 | 첫 contrast가 채택하면 MVP research-state plane. 아니면 audit/export로 축소. |
| **5. OpenResearch scientific-run authority** | 고정 protocol/code/environment에서 scientific run과 stdout evidence를 식별한다. repository의 별도 ad-hoc process 또는 두 번째 run registry를 만들지 않는다. | 직접 subprocess, 중복 run DB, 요약문만 남기는 실행은 provenance와 lifecycle authority를 분열한다. | owner: 지정 ORX CLI/project. 입력: protocol hash, experiment commit, command/env. 출력: run ID, immutable receipt, artifacts. ARGO는 receipt importer/link만 소유한다. | command/cwd/input/env/output hash와 terminal state; result→decision edge. | `FIXED_SUBSTRATE` for authorized scientific runs; 현재 primary runner는 `NOT_IMPLEMENTED` | 공개 도구 재사용 범위 확인 전 미정. 시연에는 한 scientific run receipt 연결 필요. |
| **6. Research refine** | 관측에 따라 가설·조건·방법·다음 실험을 successor로 갱신한다. POPPER의 순차 Type-I 보장은 conditional e-value와 stopping 조건에 한하며 “세 번 critique”에 전이되지 않는다. | one-shot, generic iteration, result-tree repair. 무조건 pivot을 보상하면 유효 설계 유지도 실패로 오판한다. | owner: ResearchState/decision lineage. 입력: non-oracle validity signal과 공개 관측. 출력: 유지·보류·수정·기각 successor 및 이유. 과거 결과를 덮어쓰지 않는다. | bounded opportunity-matched revise, invalid reuse, unnecessary pivot, next-decision contract. | `CANDIDATE`; bounded critique의 효능 미평가 | 관측 기반 next decision 1회는 MVP 후보. 통계적 순차 반증 구현 주장은 금지. |
| **7. Engine refine** | harness 자체 변경은 research refine과 다른 계보다. held-out promotion 전에는 기존 scientific result의 의미를 바꾸지 않는다. | scientific result와 engine patch를 같은 lineage에 쓰면 원인 귀속과 재현이 깨진다. | owner: 기존 Continual Harness/engine promotion path. 입력: engine failure evidence, held-out eval. 출력: versioned engine change와 promotion/rollback. scientific decision graph에는 link만 남긴다. | old/new engine hash, held-out regression, source result immutability. | `OUT_OF_MVP`; native construction pause | 현장 MVP 밖. self-modification을 시연 범위로 주장하지 않음. |

## 기존 2026-09-04 판정의 active 재분류

| 구 판정 | active 재분류 | 이유 |
|---|---|---|
| 최소 shell `Adopted` | `FIXED_SUBSTRATE` | T3/T1′ 비용·점수는 효능 근거가 아니며 실행 기질 선택과 causal treatment를 분리한다. |
| persistent REPL `Conditional` | `FIXED_SUBSTRATE` | B1-B0 한 task 반복을 통계적 채택 근거로 쓰지 않는다. |
| typed graph·graph engineering `Conditional` | `CANDIDATE` | B2 graph count는 persistent relationship-aware control의 manipulation evidence가 아니다. |
| fail-closed lifecycle `Adopted` | `INSTRUMENT_VALIDATED` | 실제 계측 결함 탐지는 보존하되 task/system efficacy로 승격하지 않는다. |
| loop engineering `Deferred: 구현 정상` | `CANDIDATE, IMPLEMENTATION UNVERIFIED` | pivots=0은 미발화이며 난이도나 구현 정상의 원인을 식별하지 못한다. |
| semantic search `Unjustified Default` | `DEFERRED` | retrieval 병목과 fixed corpus/provider/query budget이 생긴 뒤에만 비교한다. |

## 설계 선택이 구현으로 이동하는 조건

1. 논문 experiment의 source/task/protocol/run/result/decision이 같은 active graph revision에 연결된다.
2. 선택된 기제의 native owner가 기존 AgentSession/worker/ORX authority를 중복 소유하지 않는다.
3. implementation evidence는 code hash, 실행 receipt, verifier result로 확인된다. 문서 제안은 `NOT_IMPLEMENTED`다.
4. NAIS 시연 claim은 실제 둘 이상의 실행 후보, 같은 기준 경쟁, 이유 있는 접기, 관측 기반 successor, fresh-context 인계를 요구한다.
5. NOTICE p.3의 적합성 10·활용성 20·혁신성 25·실현가능성 25·확장성 20을 각각 구현 증거에 연결하되 논문 primary outcome으로 사용하지 않는다.
6. NOTICE p.5의 현장 개발 전 과정 조건과 APP p.7의 AI·OSS·외부 데이터 공개 의무를 보존한다. 재사용 허용 범위는 확인 전 `UNKNOWN`이다.

## 근거 상태

- THESIS p.1 SHA-256 `d2ab302410321cb43c499a681d289df72d86f889eaf4ca0b58b8e8ad804ea8f5`
- APP pp.2–4,7 SHA-256 `a829572375ddca11ec94cbbd48827419564f655fa36aab25e3a9d3fdca8a47e6`
- NOTICE pp.3,5 SHA-256 `b46c64b79eec2c317017977c6821115f49d02cd16bf481949e91bcd38c92610a`
- `paper/research/integrated-research-design-active.md`
- `.planning/2026-09-05-argo-direction-review/literature-challenge.md`
- `.planning/2026-09-04-argo-paper-research-audit/review-packet/oracle-isolation-v4/stage0-observer-closure.json`

현재 인정된 효능 결과는 0이며 native implementation은 재개되지 않았다.
