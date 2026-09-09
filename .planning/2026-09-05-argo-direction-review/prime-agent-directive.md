# ARGO-PAPER-ROOT 방향 교정 — 2026-09-05

## 사용자 목적과 범위

사용자는 현재 자율 연구가 졸업논문 및 NAIS용 ARGO prototype으로 이어지는지 실제 검토하고 지시하도록 요청했다. 목표는 재료를 나열하는 시스템이 아니라, 선행연구로 정당화된 과학적 선택을 실험으로 경쟁시켜 유용한 최소 구성을 찾는 것이다. scientific choices는 스스로 비교·결정하되 근거·반례·기각 이유를 남겨라.

이 지시는 **연구 설계/문헌/graph authority 정리와 기존 허용된 검증 범위**다. 새 유료 episode, native runtime/daemon/RLM/CLI/TUI 구현, ORX 내부화, credential 변경, push·게시·제출은 승인하지 않는다. 기존 native construction pause, LG Aimers 정지/읽기 전용, private instance 분리를 유지한다. 추가 중단 게이트를 무조건 늘리라는 뜻이 아니다.

먼저 아래 두 문서를 전체 읽고 현재 연구 state에 이 검토를 연결하라.

- `/Users/um-yunsang/argo-paper-orx/.planning/2026-09-05-argo-direction-review/review.md`
- `/Users/um-yunsang/argo-paper-orx/.planning/2026-09-05-argo-direction-review/literature-challenge.md`

## 우선순위 교정

1. **과제 실행과 과학적 설계 선택을 분리하라.** 현재 ScienceAgentBench 중심 primary는 주어진 일을 실행하는 능력이지 문제/가설/변별 실험 선택 능력의 직접 측정이 아니다. 이 차이는 원 논문 한계와도 일치한다. 기존 execution benchmark는 보조 평가로 유지하되 `경쟁 가설 → 구분 예측 → 실험 선택 → 관측 → 다음 결정/인계`의 핵심 episode를 주 연구로 설계하라.
2. **기존 GCF 전체와 작은 핵심 설계를 실제 비교하라.** 최신 15개 선택표를 무시하지 말되, 기존 supervisor 제안이라는 이유로 GCF·16과제·13검정·Stage R/복구를 불변 조건으로 만들지 마라. 사용자 목적에 대한 식별력·비용·prototype 경로를 기준으로 선택/기각하라. 한 주 contrast와 다음 정보성 실험부터 정하고 factorial/검색/복구는 필요한 설명을 가르는 후속으로 분리하라.
3. **강한 comparator를 쓰라.** Co-Scientist(Nature 2026-05-19)의 proximity graph/tournament/evolution과 The AI Scientist(Nature 2026-03-25)의 result-driven experiment tree가 이미 존재한다. 넓은 graph+competition+refine을 신규성으로 팔지 마라. 같은 정보·후보 기회·review/refine 기회·모델·예산의 proximity/tree 정책과 typed evidence dependency/무효화/재계획 정책을 비교하라. flat+generic iteration은 해석용 baseline이다. 원 시스템 전체를 재현하지 않으면 mechanism-matched comparator라고 정확히 쓰고 재현 실적을 꾸미지 마라.
4. **검정력 모순을 먼저 수정하라.** `05-preregistration-draft.md:80`의 lower CI >+0.10과 `:101`의 true effect +0.10에서 80% power는 동시에 성립하지 않는다. H0 delta<=0 / alternative +0.10과 최소유용효과 검정 H0 delta<=delta0 / alternative delta1>delta0 중 연구 질문에 맞게 선택하라. 네 개발 과제로 이질성이 확정됐다고 취급하지 말고 분산 시나리오와 비용 민감도를 명세하라. 탐색적이면 탐색적이라고 밝혀라.
5. **S와 P 및 비용을 분리하라.** RA=S*P^3는 binary task에서 P^4다. 이 임의 효용과 FULL이 일곱 대안을 모두 이겨야 한다는 조건을 주 기여의 필수 조건으로 유지할 과학적 근거가 없다면 제거/보조화하라. 더 단순한 구성이 이기면 그것을 채택하라. paper상 제거는 revision/이유를 남기며 과거 protocol을 소급 변경하지 않는다.
6. **active authority를 하나로 정리하라.** material-mechanism-evidence-map의 quarantined T3/B012 기반 Adopted/Conditional, pivots=0의 난이도 단정, 오래된 active research-design을 새 결정으로 supersede하라. immutable receipt와 원본 PDF는 보존하라. canonical RETRACTED 노드의 supports edge는 역사일 뿐 활성 지지가 아니어야 한다. DRAFT_NOT_APPLIED overlay가 paper validator에 적용된 것처럼 보고하지 마라. 소비자별 실제 read path와 단일 active projection을 명시하고 미적용은 미적용으로 써라. native 변경 없이 가능한 연구 문서·projection 계약 정리를 우선하라.
7. **graph를 실제 선택/인계에 연결하라.** 현재 b2_harness에는 graph_query가 있지만 이것만으로 persistent relationship-aware control이 증명되지 않는다. snapshot/query→evidence spans→alternatives→decision→action→run/result→successor 경로를 설계하고 선택별 근거/반례 edge를 명시하라. 새-context agent가 대화 이력 없이 허용 next action과 금지 이유를 재구성하는 시험을 넣어라. source support 무효화 시 관련 결정만 재개방하고 유효 결과는 보존해야 한다. 관련 dependency와 무관한 edge perturbation을 구분하되 manipulation/비중복성 확인 없는 null을 “효과 없음”으로 해석하지 마라.
8. **재료별 native 연결 계약을 작성하라.** Pi/Prime은 고정 실행 기질, Exa는 discovery adapter, 원문은 review 후 evidence, graph는 versioned research state, ORX는 지정 scientific run authority와 receipt 연결, research refine와 engine refine는 다른 lineage다. 기존 AgentSession/worker lifecycle을 중복 소유하지 마라. 각 재료에 원문 기제·대안·반례·native owner·입출력·측정 signature·ablation·MVP 여부를 연결하라. Python oracle을 제품으로 보고하지 마라.
9. **문헌의 지위와 적용 범위를 교정하라.** A-MEM은 NeurIPS 2025 기억 QA 근거이지 과학 graph 필수성 증명이 아니다. POPPER는 ICML 2025의 조건부 순차 검정이며 “세 번 critique”가 그 보장을 얻지는 않는다. Nature 정식판이 있는 항목은 실제 정식판을 검토하고, preprint는 preprint로 분리하라. section-read와 full-paper-read를 구분하고 본문 claim은 실제 읽은 원문에만 결합하라. 제품명을 기여로 전면화하지 않는 것과 OSS/구현 attribution을 숨기는 것을 혼동하지 마라.
10. **19시간 event MVP로 정리하라.** 공식 본선은 2026-09-30 17:00–10-01 12:00 KST다. 원 신청서의 36시간 계획과 “19시간이므로 사전 prototype이 완성돼야 함” 추론은 현재 계획 addendum에서 교정하라. 현재 연구/코드/graph가 본선 반입 허용이라고 가정하지 마라. 정확한 재사용 허용범위는 주최 측 규칙 미확인으로 남기고 clean-room 경계를 유지하라. source→두 설계→결정→한 실행→한 refine→graph/인계 시연에 한정하고 engine self-modification은 현장 MVP 밖으로 둬라.

## 바로 이어서 할 일 — 문서량보다 완료된 결정

진행 중인 무과금 agent/scorer observer probe는 결과를 수집해 해당 범위의 PASS/FAIL과 남은 blocker를 닫아라. 기존 작업을 중복 실행하거나 새 paid run을 시작하지 마라. 구체적인 새 측정 위험이 없으면 fixture/gate 목록을 더 늘리지 말고 위 설계 작업을 병행/진행하라.

다음 연구 산출물은 기존 canonical entrypoint에서 연결되는 아래 네 개로 제한한다. 같은 내용을 여러 새 framework에 반복하지 마라.

1. 통합 연구설계: 목적, 핵심 가설, 선택/기각 설계, 강한 comparator, 독립 outcome, population/split/unit, analysis/power-or-precision, budget/stopping 및 결과별 다음 결정.
2. 기제–native 계약표: 일곱 재료를 원문 근거·반례·owner/interface·측정·MVP로 연결.
3. active graph 인계 manifest: 실제 소비 경로, revision/retraction 규칙, decision-to-source edges, fresh-context next-action 복구의 명세 및 실행 여부.
4. next experiment manifest: 가장 작은 정보성 실험 하나의 absolute cwd/command/input hashes/기대 판별 결과/비용/필요 승인. 실재 command가 없으면 NOT_IMPLEMENTED로 써라. 모르는 값을 만들지 말고 launch하지 마라.

정확한 repository cwd는 `/Users/um-yunsang/argo-paper-orx`다. roster의 `/Users/um-yunsang/argo/lgaimer`로 실행하지 마라. 기존 다른 작업자의 변경을 보존하고 파일 write ownership을 분리하라.

첫 응답은 (a) 두 review 문서 읽기 완료 여부, (b) 수용/반박하는 핵심 finding과 근거, (c) 실제 다음 변경 대상·산출물 경로, (d) 기존 pause/비용 경계 유지 여부를 짧게 알려라. 전달 수신이나 plan 작성만을 개선 완료라고 하지 마라. 이후 heartbeat는 새 증거·수정한 결정·파일 diff 또는 정확한 blocker를 보고하라.
