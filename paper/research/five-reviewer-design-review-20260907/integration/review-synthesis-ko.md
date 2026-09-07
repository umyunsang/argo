# 5인 Sol/xhigh 검토 통합 — 연구에서 프로토타입까지

상태: **설계 수정 완료, 실험 전 필수 증거는 미완료**. 2026-09-07.

## 1. 검토 결과와 의미

동일 동결 packet을 서로 다른 Sol/xhigh 세션이 독립 검토했다. 방법론·통계, 비교 공정성, 도메인, 회의적 독자, 글쓰기·표현 모두 `REVISE_BEFORE_EXPERIMENT`다. 총 29개 finding을 `finding-response-matrix.json`에 연결했다. 이는 다섯 표로 과학적 진실을 결정했다는 뜻이 아니다. 자료·주장·설계의 결함을 발견한 전문가형 검토다. 이전 취소된 Astra 작업은 결과로 소비하지 않았다.

## 2. 유지하는 연구 목적

**장기 자율연구 하네스 기반 LLM 시스템 + 최신 AI/ML 연구·실험 흐름**을 유지한다. 문헌과 공정한 실험으로 요소들의 연결·제어 방식을 선택하고, 그 선택이 후행 ARGO 프로토타입 요구사항으로 이어진다. 논문은 도구 목록이나 해커톤 계획 소개가 아니다. 검증한 일반적 방법과 완료된 결과·한계만 담는다.

직전 연구 연속성/negative-memory pivot은 승인된 최적안이 아니라 대안으로 보존한다. graph/evidence-mediated 통합 연구 제어를 **우선 검토할 연구 프로그램**으로 선택했지만, graph를 실험의 승자로 선택하지 않았다. 기록용 graph, 실험의 agent-visible graph treatment, 미래 native graph 구현을 구분한다.

## 3. 공통 차단과 수정

| 문제 | 통합 조치 | 아직 필요한 증거 |
|---|---|---|
| 주 contrast가 기능 목록 수준 | 공통 기질과 B/C/G 정책 차이를 분리 | runnable code/config/prompt/action manifest, activation과 조작 확인 |
| 실제 ML research task/metric 없음 | coherent 공개 과제군에서 실제 경쟁 실험·후속 결정·최종 artifact를 요구 | license/ancestry/split, independent gold/scorer, metric/failure 계약 |
| 추가 숙고·정보·사람 정리 confound | C를 schema-neutral compulsory control로 두고 G-C를 비교 가능하게 설계 | 동일 정보권/기회, delivered/used evidence와 전체 비용 ledger |
| 표본·power·MUE·예산 미정 | 사전 개발 자료로 power 또는 precision/비용 계획 산출 | 근거 없는 고정 표본 하한이나 author-reported 효과 prior 사용 금지 |
| PaperService 검색 owner 충돌 | DiscoveryPort / SourceEvidenceService / downstream PaperService로 역할 정정 | no-owner/dual-owner, source promotion, one-way import 검증 |
| 중단 뒤 외부 run 재실행 위험 | durable intent와 RECONCILING/UNKNOWN을 둔 adapter 계약 | ORX 실제 capability 확인; request-ID lookup/exactly-once 실행은 주장하지 않음 |
| critic와 scorer 혼동 | trusted hidden-data scorer와 untrusted LLM critic 분리 | actual access isolation, selection-before-score, blind assessment |
| 기존 결과 범위 확대 위험 | 재사용과 효능 승격을 분리 | 새 campaign의 독립 outcome; 이전 실패를 성공으로 바꾸지 않음 |

## 4. 실험안 이견의 조정

방법론·도메인 리뷰는 개발용 2×2 representation×control, 공정성 리뷰는 우선 두-arm 후 순차 ablation, 회의적 리뷰는 B/C/G를 제안했다. root는 **B/C/G 개발 screen**을 현재 작업안으로 둔다.

- **B:** 강한 원문 기반 hypothesis/result tree 또는 notebook과 explicit advisory validity/preservation 지침.
- **C:** 같은 사실·기회에 compulsory applicability/revalidation/preservation/capsule 절차를 추가.
- **G:** C와 같은 의무를 versioned evidence graph traversal/scoped invalidation으로 연결.

C-B는 compulsory-process package, G-C는 graph-control package의 증분이다. 이는 순수 topology 효과를 모두 분리하지는 못한다. 해당 구분이 prototype 선택에 중요하고 비용이 정당화될 때만 passive-graph 네 번째 arm을 추가한다. 개발 후 후보와 최강의 신뢰 가능한 simpler competitor, 하나의 primary contrast를 봉인하고 별도 과제 계보에서 확인한다. 개발에서 고른 후보가 graph라는 보장은 없다.

**리뷰 숫자는 자동 채택하지 않는다.** 개발 6/확증24 families, 또는 두 family 완료 기준은 계산된 power 근거가 아니다. 두 family는 feasibility 범위로만 해석한다. 표본은 최소 유용효과·family/within-family variance·실패율·정밀도·자원에 따라 정한다. 네 결정/두 의존/한 restart 등의 지평 숫자도 개발용 후보 template이며 보편적 정의가 아니다.

## 5. 출처와 기술 범위의 재확인

새 여덟 논문 이외에 EviGraph, SCOPE, ResearchClawBench, Arbor, RSEA, Evo-Bench, Regimes, Harness Evaluation/Opt와 claim-lineage 계열의 기존 **21개 exact locator**를 원문 bytes/인용 span과 다시 대조했다. 전부 hash/quote가 맞았다. 이것은 저장 원문의 scoped 재결합이지 전체 prior-art 신규 완독이나 신규성 인증이 아니다. EviGraph의 operational graph와 downstream repair가 이미 알려져 있으므로 broad-first graph 주장은 불가하다.

Prime snapshot 코드에는 best-effort 변수별 복구와 용량 제한이 명시돼 있다. daemon journal은 결과 없는 mutation을 uncertain으로 두고 자동 replay하지 않는다. 이는 강점이지만 scientific run의 exactly-once나 완전 환경 복구가 아니다. ORX help에서 확인한 status/list 인터페이스만으로 external_request_id lookup을 가정할 수 없다. RECONCILING 실패 시 UNKNOWN/BLOCKED로 남긴다.

trusted scorer는 자신의 경계 안에서 hidden test를 읽어야 한다. 금지 대상은 planner/developer/critic의 hidden 접근과 final selection 전 score 공개다. 리뷰의 “assessor도 hidden bytes 금지”는 이 구분으로 수정했다.

## 6. 기존 작업의 유지·격리

**유지:** original source/locator, 원문 보존, protocol fingerprint, exact byte/lineage 검사, 실패 원장, graph/replay fixtures, B3의 제한된 개발 관측, C64 semantic conflict를 잡는 반례, font/runtime 호환성 자료. 중단된 World-init static 자료는 보존하되 새 주 연구의 의무 선행 단계로 두지 않는다.

**효능에서 격리:** C64 인과 주장, 96 scorer 검사를 96 agent sample로 해석, retrospective/schema PASS, v12의 30/30 pre-observation crash, 다섯 font 호출 밖 일반화, static World-init의 실행 성공 주장, 선행논문 수치의 local reproduction/SOTA 승격. 소모된 font/v12 권한은 재사용하지 않는다.

## 7. 연구 완료와 글쓰기·출판을 분리

`ResearchDone`은 고정된 task/protocol, 끝난 개발·평가 campaign, 모든 실패/비용, 단일 preselected artifact의 hidden 분석, 불확실성, 선택/기각 record, closed claim evidence를 요구한다. valid null/negative도 완료일 수 있다. 유의하지 않다는 사실만으로 동등성이나 비열등성을 주장하지 않는다. invalid-only 종료는 efficacy 완료가 아니다.

그 뒤 원고를 작성한다. **완성 그림/최종 PDF metadata는 원고 작성 전에 존재할 수 없으므로 PublicationReady 단계에서 검사**한다. 이는 연구 완료 전 본문을 쓰라는 예외가 아니다. 현재는 원고를 수정하지 않고 향후 outline/figure plan만 보존한다.

prototype는 선택 결과를 내부 owner/port로 옮기며 native 재개 승인·현장 재사용 규칙·실제 구현/시연 검증이 별도로 필요하다. 필요한 설치는 기존 capability와 병목/재현성 요구를 확인한 뒤 선택한다. 설치 수는 SOTA의 근거가 아니다.

## 8. 다음 자율 연구 우선순위

1. 한 coherent 공개 ML research task programme의 원문·데이터·license·baseline·scorer 적합성을 조사한다.
2. B/C/G의 유일 차이와 공통 정보/권한/예산을 실행 가능한 contract로 정의한다.
3. Independent neutral task/gold와 실제 hidden isolation, ORX adapter capability를 확인한다.
4. 개발 비용·분산·조작 가능성으로 합리적인 표본/예산을 계산하고, 별도 실행 승인을 요청한다.
5. 고정한 캠페인 결과로 설계를 선택한다. 결과가 어떤 방향이든 기록과 한계를 보존하고 research-completion을 판단한다.

새 학술 결과·SOTA·실험 실행·native 구축·출판 권한은 이번 통합으로 생기지 않는다.
