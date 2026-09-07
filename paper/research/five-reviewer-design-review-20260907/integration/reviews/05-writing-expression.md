# 05 — 글쓰기·표현 독립 검토 (Sol/xhigh)

- **판정:** `REVISE_BEFORE_EXPERIMENT`
- **검토 범위:** 동결 packet과 저장된 문헌 bundle만 사용했다. 새 검색·실험·원고 작성·타 reviewer 열람은 없었다.
- **판정의 뜻:** 실행·출판·프로토타입 승인이나 효능 판정이 아니다.
- **packet SHA-256:** `a89c23c4c5e5fda79fc3efd2301a3c33eb3b13f1bdc8fd6a597a85bdd59e2fe9`

## 1. 핵심 판단

기존 원고는 제안/관측 경계를 정직하게 표시한다. 계측 96회를 독립 과제나 agent 성공률로 바꾸지 않고(`packet/existing-thesis-ko.qmd.txt` §Ⅲ.6, lines 176–188; §Ⅳ.1, lines 224–240), graph 연결과 과학적 타당성을 구분하며(lines 128–140), 같은 model의 역할 분리를 독립 평가로 부르지 않는다(lines 142–146, 170–174).

그러나 현재 원고는 2026-09-05의 **유형화된 문맥 그래프 + 이중 수정 + Stage-0 계측** 논문이다. 최신 목적은 현재 AI/ML 문헌 아래 통합 구조를 경쟁시키고 실제 ML 캠페인으로 선택한 설계를 후행 프로토타입에 넘기는 것이다(`packet/review-brief.md` §Governing user direction, lines 5–9; §What is under review, lines 13–15). 반면 pivot은 이미 “증거 기반 연구 연속성 하네스”를 선택했다고 쓴다(`packet/integrated-research-design-active.md` §3, lines 21–28). 이는 유력안이지 최적안이 아니다. 기존 QMD는 source shelf로 동결하고 연구 완료 뒤 새 evidence snapshot에서 다시 조립해야 한다.

## 2. 차단 이슈와 수정 조건

| ID | 등급 | 근거 | 문제와 영향 | 필요한 수정 | 닫는 증거 |
|---|---|---|---|---|---|
| WR-01 | **BLOCKER** | `packet/review-brief.md` lines 5, 13, 30–34; `packet/existing-thesis-ko.qmd.txt` lines 37, 59, 118–146, 296–300; `packet/study-contract.json` lines 47–56 | 원고는 typed context graph를 중심 구조처럼 제안하지만 현재 계약은 `typed_graph_required:false`이고 broad architecture 선택도 끝나지 않았다. 선택 전 원고화는 제품 로드맵을 학술 방법으로 고정하거나 후보 기제를 기여로 오인하게 한다. | A–D 후보를 mechanism-distinct design으로 비교하고, graph **representation**과 compulsory **control**을 구분한다. 논문에는 실험으로 선택된 generic design과 탈락 이유만 남긴다. | outcome 열람 전 동결된 DecisionRecord, 후보별 owner/interface/falsifier, 선택·기각 근거, graph-vs-tree 및 필요시 representation/control ablation receipt. |
| WR-02 | **BLOCKER** | `packet/existing-thesis-ko.qmd.txt` §Ⅰ.2 lines 51–55, §Ⅲ.4 lines 148–162; `packet/study-contract.json` lines 12–17, 88–100; `packet/integrated-research-design-active.md` lines 78–84, 123 | 기존 RQ/H1–H3는 선택·인계·철회 진단이고, 최신 primary endpoint인 숨은 평가의 단일 최종 산출물 성과가 전면에 없다. task suite, metric, selection rule, N, power, 최소효과도 `null`이다. 결과 장과 표의 단위가 아직 결정될 수 없다. | P0를 “동일 hard ceiling에서 사전 선택한 단일 artifact의 independent held-out task performance”로 고정한다. 선택·부정결과 재사용·회복은 별도 진단으로 둔다. programme/task family를 추론 단위, seed/round/candidate를 nested로 표기한다. | 채워진 사전등록 contract, task/source lineage, metric·unit·aggregation·invalid 처리·selection rule, N/power/minimum useful effect, 전체 비용 단위와 hidden scorer 봉인 증거. |
| WR-03 | **BLOCKER (writing gate)** | `packet/review-brief.md` line 9; `packet/existing-thesis-ko.qmd.txt` lines 118, 176–188, 222–282, 294–300; `packet/manuscript-boundary.md` lines 13–20 | 제안 loop 안에 “원고 갱신”이 들어 있고 Stage-0 계측이 주 `Experimental results` 장을 차지한다. 최신 지시는 bounded research 완료 전 새 manuscript body를 쓰지 말라는 것이다. 계측 적합성이 본 연구 결과처럼 시각적으로 과대 대표될 위험이 있다. | 연구 loop에서 paper 생성을 제거하고 bounded stop 뒤의 downstream rendering으로 이동한다. 96회·환경 점검은 보존하되 최종 논문의 “계측/프로토콜 자격 확인” 또는 부록으로 내린다. 주 결과 장은 실제 ML 캠페인만 받는다. | 모든 예정 launch의 terminal receipt, 독립 평가, 분석·실패 회계, 완료된 claim ledger와 research-completion sign-off. 그 전에는 outline만 유지. |
| WR-04 | **MAJOR** | `packet/existing-thesis-ko.qmd.txt` §Ⅱ lines 72–112; `packet/integrated-research-design-active.md` lines 110–121; `packet/review-brief.md` line 15; `long-horizon-harness-benchmark-20260907/benchmark-synthesis-ko.md` lines 7–24, 26–54 | 관련 연구가 이전 ResearchAgent/OpenScholar/ScienceAgentBench/POPPER/GoT/ADAS 중심이라 최신 8편이 보여 주는 persistence, artifact/evidence separation, reversible context contracts, feedback-held-out gap, conditional negative reuse, higher-order refinement, environment provenance가 구조적으로 빠져 있다. 반대로 8개 framework를 기능 목록으로 모두 결합하면 attribution이 사라진다. | 관련 연구를 제품명이 아니라 “발전 대상 / 보장 / 비보장 / 본 연구의 testable implication”으로 재편한다. 기존 full-read 근거는 유지한다. 신규 8편 성능은 항상 **author-reported, locally unreproduced**로 표시하고 SOTA 문구를 금지한다. | 문장별 retained bytes/hash/locator, read level, scope/counterevidence를 가진 claim table; 정확한 verified title/metadata; code availability는 stored snapshot 상태로 한정. |
| WR-05 | **MAJOR (release blocker)** | `packet/existing-thesis-ko.qmd.txt` lines 120–138, 182–188; `packet/manuscript-boundary.md` lines 16, 18, 24–30, 43–46 | 캡션은 “제안 구조/계측 점검”만 말하고 구현·제안·결과 상태를 그림 자체에서 즉시 구분하지 못한다. packet에는 참조 SVG bytes가 없어 내부 명칭, 화살표 의미, 접근성 metadata를 독립 확인할 수 없다. | 모든 그림에 `PROPOSED`, `MEASUREMENT-ONLY`, `OBSERVED RESULT` 중 하나의 상태와 데이터/claim ID를 둔다. 내부 ARGO/NAIS/Prime/OpenResearch CLI/Exa, 경로, roadmap은 그림·alt·SVG title/desc·PDF metadata에서 제외한다. 정확한 학술 논문 제목은 서지정보에서만 보존한다. | 최종 SVG/PNG/PDF hash manifest, caption-to-claim/run binding, 추출 텍스트·alt/title/desc·metadata 검사, 전 페이지 육안 확인. |
| WR-06 | **MAJOR** | `packet/existing-thesis-ko.qmd.txt` lines 2–3, 37–39, 53, 70, 178, 226, 244–255; `packet/integrated-research-design-active.md` lines 15–19 | `자율 연구개발/autonomous R&D`, `자율연구/autonomous research`, context graph, research state, harness가 시기별로 흔들린다. 2026-09-05 한 cutoff는 09-07 문헌/설계와 섞인다. count도 task, scorer invocation, package count, run을 함께 보여 독자가 독립 표본으로 오독할 수 있다. | 용어집과 claim-state vocabulary를 먼저 고정한다. literature/design/measurement/run cutoff를 분리한다. 모든 수치 열에 단위와 분모를 쓰고 `16 tasks`, `96 deterministic scorer invocations`, `0 admitted integrated campaigns`처럼 표기한다. | terminology lint, 단위·분모 audit, 표/본문 숫자 재도출, cutoff별 snapshot hash, 교차참조 검사. |

WR-01·02는 실험 전 차단, WR-03은 writing gate, WR-05는 release 차단이다. WR-04·06은 protocol 확정 전 반영 권고다.

## 3. 연구 완료 뒤 사용할 publication-safe outline

1. **초록:** 문제, 사전등록 contrast, programme 수, primary outcome, 비용, 한계만 쓴다.
2. **서론:** 장기 자율연구의 누적 결정 문제, 왜 output 품질만으로 부족한지, P0와 진단 RQ, 검증된 기여 범위를 제시한다.
3. **관련 연구:** persistent execution/context, evidence·artifact contracts, iterative refinement, held-out evaluation/provenance를 보장과 전이 한계로 묶는다.
4. **후보 구조와 선택 원리:** generic research loop, authority boundary, competing designs, graph representation/control 구분, falsifier. 내부 제품 owner나 후행 hackathon 계획은 넣지 않는다.
5. **사전등록 방법:** public ML task families, lineage split, baseline/treatment, equal rights/opportunities/hard ceilings, single-artifact selection, hidden assessment, interruption stress, failure·cost accounting.
6. **결과:** paired primary outcome, 모든 launch/invalid/failure와 cost, diagnostics/ablation 순이다. Stage-0은 부록이다.
7. **논의·한계:** 대안 설명, null/negative 결과, author-reported와 local reproduction의 차이, 외적 타당도.
8. **결론:** 관측된 범위만 요약한다. 후행 프로토타입명·로드맵·구축 약속은 없다.

## 4. 그림·표 계획

| 우선 | 산출물 | 주장 상태와 안전 규칙 |
|---|---|---|
| Fig. 1 | objective → full source → evidence/state → competing design → frozen run → independent assessment → update/stop의 generic loop | **설계/방법**. process owner 중복 금지와 paper-after-stop을 표시. 제품·도구명 금지. |
| Fig. 2 | treatment와 strong iterative tree/notebook baseline의 동등권·차이 도식 | **사전등록 조작**. 같은 source/context/opportunity/budget, graph representation과 compulsory control을 별도 색상. |
| Fig. 3 | task-family별 paired primary effect와 full-cost curve | **관측 결과만**. CI/분모/invalid 포함. 데이터 hash 없으면 생성 금지. |
| Fig. 4 | interruption·negative-result reuse의 오류 유형 | **진단 결과**. false suppression과 redundant retry를 둘 다 표시. |
| Table 1 | prior work: object improved / guarantee / non-guarantee / evidence status | 성능 수치는 `author-reported`; locally reproduced로 승격 금지. |
| Table 2 | frozen study contract | estimand, unit, split, metric, selection, budget, stop/retry, hidden assessor. |
| Table 3 | task-family·license·ancestry·split | seed/round를 N으로 세지 않음. |
| Table 4 | 모든 campaign terminal status와 비용 | 성공만 남기지 않음. |
| Table 5 | primary + diagnostic + ablation result | primary와 schema conformity 분리. |
| Appendix | 기존 16과제/96회 scorer 및 환경 점검 | `INSTRUMENT_ONLY`; 기존 표의 제한 문구를 보존. |

## 5. 용어·claim-state 표

| 항목 | 고정 표현/상태 | 금지되는 혼용 |
|---|---|---|
| 연구 대상 | `장기 자율연구를 위한 하네스 기반 LLM 에이전트 시스템` | `autonomous R&D`와 교차 사용 |
| 전체 시스템 | `research harness` | `context graph`를 전체 하네스와 동의어로 사용 |
| graph | `evidence/context graph`의 표현 기능과 `graph-mediated control`의 행동 기능을 분리 | node/edge 존재를 효능으로 표현 |
| 대조군 | `strong source-backed iterative research tree/notebook baseline` | stateless/single-shot baseline |
| 독립 평가 | treatment-blind hidden scorer/전문가 및 고정 protocol | 같은 모델의 역할명 분리를 독립성으로 표현 |
| 선행 성능 | `AUTHOR_REPORTED / LOCALLY_UNREPRODUCED` | SOTA 또는 로컬 기대효과 |
| 로컬 96회 | `INSTRUMENT_ONLY`; 16 tasks × 6 scorer invocations | 96 samples, agent success rate |
| 통합 효능 | `NOT_ESTABLISHED` | PASS, improvement, causal effect |
| C64/UI/font/World | 각각 `INVALID_CAUSAL`, `INVALID_NOT_ADMITTED`, exact five-call compatibility, static initialization only | 새 방향의 양성 결과로 합산 |
| 제품 연결 | 내부 crosswalk에서만 ARGO/NAIS/도구 owner 사용 | 이름 삭제 후 같은 roadmap을 논문 방법으로 게재 |

## 6. 우선순위가 있는 exact-line 편집 큐 (연구 완료 뒤에만)

- **P0:** lines 2–3의 `연구개발/R&D`를 `장기 자율연구` 계열로 통일한다. 성능·자기진화 표현은 금지.
- **P0:** lines 37–39 초록과 lines 294–300 결론은 patch하지 말고 완료된 claim ledger에서 재생성한다.
- **P0:** lines 51–55와 148–162를 primary terminal outcome → diagnostics 순으로 재정렬한다. H1–H3는 primary hypothesis가 아니라 mechanism diagnostics로 내린다.
- **P0:** line 118의 `원고 및 인계 자료 갱신`에서 원고를 연구 loop 밖으로 이동한다. lines 120–146은 “후보 설계/미구현” 상태를 유지하고, graph가 실험으로 선택된 경우에만 최종 method로 승격한다.
- **P0:** lines 176–188 및 222–282의 Stage-0 material을 본 결과에서 분리한다. lines 224–255의 숫자와 한계 문구는 삭제하지 않고 Appendix instrument qualification로 이동한다.
- **P1:** lines 72–112의 관련 연구를 최신 8편을 포함한 보장-경계 matrix로 재편한다. 기존 full-read 논문은 범위가 맞으면 유지한다.
- **P1:** line 70의 단일 cutoff를 literature/design/measurement/confirmatory-run 네 cutoff로 바꾼다.
- **P1:** lines 122, 134, 184의 그림은 source bytes를 packet에 동결한 뒤 상태, claim/run ID, alt/title/desc를 검토한다.

## 7. 재사용·격리와 결정적 실험

**재사용:** 제안/결과 분리, 96회 계측의 분모, failure-admission table, estimand, graph≠truth·hash≠validity 경계, reviewer 비독립성, source receipts/locators, 모든 실패를 보존한다.

**격리:** 96회 계측·정적 graph/replay를 agent efficacy로 사용하지 않는다. C64의 nominal `p=.03125`는 인과 주장에 쓰지 않는다. UI-parity v12, font five-call, World-init는 각 좁은 상태에서만 둔다. 여덟 선행연구의 성능과 unavailable/unverified code를 로컬 재현으로 쓰지 않는다.

**가장 강한 대안 설명:** treatment가 이겨도 graph/control 때문이 아니라 더 많은 노출 문맥, 강제 체크리스트, 평가 기회, critic 호출 또는 추가 비용 때문일 수 있다. 반대로 strong baseline이 같은 체크를 자발적으로 구현하면 별도 graph control의 필요성이 사라질 수 있다.

**결정적 실험:** 여러 독립 public small-compute ML task/source families에서 `graph/evidence-mediated continuity package`와 strong source-backed iterative tree/notebook를 paired 비교한다. model/version, source rights, candidate pool, dev feedback, hidden assessor, opportunities와 root+descendant token/tool/compute/wall/cost ceiling을 맞춘다. 종료 전에 단일 artifact를 선택한다. primary는 hidden task performance, 보조는 full cost, useful decisions, false suppression/redundant retry, regression, interruption recovery다. representation-only와 compulsory-control ablation은 package 차이가 관측될 때만 한다.

**원고 작성 시작의 최소 조건:** (1) architecture DecisionRecord와 primary contract 동결, (2) task/license/ancestry/gold/scorer 인증, (3) N·power·효과 기준·invalid/retry/stop 규칙 확정, (4) 모든 campaign terminal receipt와 비용 보존, (5) treatment-blind 평가 및 lineage-aware 분석 완료, (6) null/negative/failed 결과 포함, (7) 문장별 claim/citation/run ledger와 numeric re-derivation, (8) figure bytes·metadata·브랜딩 audit 완료. 하나라도 없으면 새 원고 본문을 쓰지 않는다.

## 8. 내부 prototype mapping — 발행물에 넣지 않음

- persistent execution → Prime/Pi daemon·AgentSession·REPL/RLM의 고정 기질
- discovery candidates → Exa 등 adapter; verified claim 권한 없음
- evidence/context graph → versioned ResearchState projection; process supervisor 아님
- scientific runs → ORX/OpenResearch authority와 immutable receipt import
- assessment → scorer/budget/hidden test를 treatment가 수정할 수 없는 독립 경계
- update → research-refine lineage; engine-refine은 별도 promotion/rollback lineage
- paper → bounded stop 뒤 claim/run identity에서 생성되는 downstream view
- 선택된 generic design만 후행 ARGO/NAIS prototype requirement로 변환하며, 이 crosswalk 자체는 논문 내용이 아니다.

## 9. 서술 점수 (1–5, 과학적 투표 아님)

- 목적 정합성 **2/5**
- 제안/결과 분리 **4/5**
- 구조와 독자 흐름 **2/5**
- 용어·단위 일관성 **3/5**
- 그림·표 claim 안전성 **2/5**
- 출판 경계 준수 가능성 **4/5** (본문 브랜드는 보이지 않으나 figure bytes 미검토)
