# 연구 방향과 목적 — ROOT active entrypoint

상태: **PUBLIC_ML_TASK_COMPARISON_ACTIVE · SCOPED_APPARATUS_VERIFIED · EXPERIMENT_AND_WRITING_NOT_READY**
갱신: 2026-09-07

## 1. 두 핵심과 하나의 연구 연쇄

1. 장기 자율연구를 수행하는 하네스 기반 LLM 에이전트 시스템.
2. 최근 AI/ML 원문과 공정한 실험으로 근거를 만든 연구 방향과 설계.

연쇄는 **문헌·대안 → graph-based 자율연구 → 고정 실험·독립 평가 → 설계 선택 → 연구 완료 → 논문 → 선택 근거를 계승한 ARGO 프로토타입**이다. 이는 내부 연구/제품 계보다. 논문은 검증된 일반적 설계·방법·결과·한계를 다루고 제품명·해커톤 계획·운영 경로를 싣지 않는다. 정확한 학술 논문 제목과 서지는 보존한다.

최근 사용자는 유효한 기존 작업의 보존, 통합 연결 설계의 실험 비교, 연구 완료 뒤 원고 작성, 필요 도구 설치의 재량을 명시했다. 직전 continuity/negative-memory pivot은 비교할 후보이지 최적 설계가 아니다. 초기 설치 허용만으로 새 유료 실행·계정·native 재개 권한이 생기지 않으며, 후속 명시적 범주 승인과 제한은 §6/§10에 별도로 기록한다.

## 2. 권위와 보존

- 현재 사용자 방향/공통 검토 자료: `paper/research/five-reviewer-design-review-20260907/packet/review-brief.md`
- 다섯 Sol/xhigh 원검토와 수신 기록: `paper/research/five-reviewer-design-review-20260907/integration/five-reviews.json`, `intake.json`
- 이견 조정: `paper/research/five-reviewer-design-review-20260907/integration/disagreement-resolution.json`
- Active 설계: `paper/research/integrated-research-design-active.md`
- 현행 Fable-reviewed study/완료 계약: `paper/research/fable51-design-review-20260907/integration/integrated-study-design.json`, `research-completion-contract.json` (검토 commit `ee7e0fdaf`). 위 5인 문서는 보존된 predecessor다.
- 재검토 결론/과제별 필수 후속 조건: `paper/research/fable51-design-review-20260907/re-review-01/integration/review-synthesis-ko.md`, `task-qualification-requirements.json`.
- 기제–owner/port: `paper/research/material-mechanism-evidence-map.md`
- 인계와 다음 행동: `paper/research/active-graph-handoff-manifest.json`, `paper/research/next-experiment-manifest.json`

서명된 계획서/신청서/공고 원본은 변조하지 않는다. 기존 source SHA는 THESIS `d2ab302410321cb43c499a681d289df72d86f889eaf4ca0b58b8e8ad804ea8f5`, APP `a829572375ddca11ec94cbbd48827419564f655fa36aab25e3a9d3fdca8a47e6`, NOTICE `b46c64b79eec2c317017977c6821115f49d02cd16bf481949e91bcd38c92610a`다. 학과의 제목 변경 승인, 해커톤에서 사전 custom 코드 재사용 허용 여부, 실제 제출 상태는 미확인이다. 웹 행사 소개는 상세 규칙을 대체하지 않는다.

## 3. 선택한 연구 프로그램, 아직 선택하지 않은 승자

우선 연구 프로그램은 **graph/evidence-mediated 장기 ML 연구 제어를 강한 원문 기반 반복 연구와 비교하여 최소 유용 설계를 선택하는 것**이다. graph가 우수하다는 결론은 없다. Pi/Prime, 검색, ORX는 서로 다른 계층이므로 하나의 framework 성능순위로 묶지 않는다.

작업용 개발 screen은 B/C/G다. B는 강한 persistent hypothesis/result tree·원문 복구·명시적 advisory 점검을 가진다. C는 같은 사실·기회에 schema-neutral compulsory applicability/revalidation/preservation/capsule 절차를 더한다. G는 C와 같은 의무를 versioned evidence graph 제어에 연결한다. C-B와 G-C를 구분하되, G-C도 순수 topology 효과가 아닌 graph-control package 효과다. 필요성과 비용을 먼저 입증할 때만 passive-graph fourth arm을 추가한다.

개발 결과로 후보와 최강의 신뢰 가능한 대조군을 선택한 후, 별도 task/source families에서 단일 primary contrast를 동결한다. 아직 task, metric, 표본, power/precision, MUE, budget, command, 승인은 없다. 6/24 family나 고정 지평 숫자는 reviewer 제안이지 검증된 하한이 아니다.

## 4. 주 outcome과 graph의 세 역할

주 outcome은 고정 전체 예산에서 **hidden scoring 전에 선택한 하나의 최종 artifact의 독립 과제 성과**다. 무효·실패 floor, 선택 규칙, 추정량은 실행 전에 정한다. 모든 launch/실패/사람 개입과 root+descendant 비용을 센다. 유의하지 않음은 동등성/비열등성의 증거가 아니다.

- 연구 관리용 graph: source/hypothesis/experiment/result/decision을 연결해 지금의 연구를 진행한다.
- 중립 audit graph: 두 조건의 기록을 동일하게 수집하며 실험용 gold를 treatment에 노출하지 않는다.
- agent-visible active graph: G 조건에서 평가할 후보 제어 기제다. 원문 노출·계약 추출 오류와 비용도 포함한다.

schema/edge/hash, raw record 복구, 의미 충분성, 현재 조건의 유효성, 실제 task 성공은 별도다. 장기는 시간만이 아니라 앞 관측이 뒤의 과학적 결정을 바꾸는 의존 지평이다.

## 5. 유지할 기존 근거

원문/locator/protocol/byte 검사, 실패 회계, B3의 제한된 개발 관측, C64의 semantic conflict 반례, graph/replay fixture, font 호환성 자료를 원래 범위에서 유지한다. C64는 causal invalid다. UI-parity v12는 30/30 pre-observation crash로 INVALID/NOT_ADMITTED이며 영구 재실행 불가다. font qualification은 한 host/runtime의 정확한 다섯 호출만 ADMITTED다. World-init은 static-only이고 integrated efficacy는 0이다.

DiscoveryWorld를 버리지는 않지만 주 논문의 필수 벤치마크나 무기한 환경수리 경로로 두지 않는다. 새 여덟 문헌과 더 넓은 기존 corpus를 연결하되 author-reported 수치를 local efficacy나 power prior로 바꾸지 않는다. exact novelty residual과 SOTA는 아직 미확립이다.

## 6. 실행·설치·출판

현재 허용: 원문/공개 과제 연구, 기존 Prime RLM 병렬 감사, 지정 경로의 연구용 apparatus 코드와 로컬 정적/모의 검증(사용자 `c40c59a9`). 실제 모델·학습·평가, 설치·공개는 범주 수준 승인(`dbbd432b`)을 받았지만 구체 task/scorer/environment/command/자원·비용 상한/대상과 검토·승인은 별도로 고정한다. 네이티브 변경은 검증 조건 충족 전 금지(`b33563e4`)이며 예외 해제 질문은 끝났다. Kaggle 토큰은 사용자 제공 뒤 일회성 유효성/파일목록 확인만 완료했다. 이를 credential 저장·약관 동의·다운로드·제출·계정 변경 권한으로 확대하지 않는다. DeepVoice/LG Aimers 비공개 자료는 접근하지 않는다.

필요한 설치는 기존 capability, 측정 병목 또는 재현성 요구, 유일 owner, version/license/security와 rollback을 확인한 후 project-local로 판단한다. 신규 설치를 최신성이나 성과의 대리 지표로 쓰지 않는다. RLM 위임은 등록 provider 모델을 확인하고 model/thinking을 명시한다. 현재 깊은 연구 검토는 `openai-codex/gpt-5.6-sol` / `xhigh`를 사용하며 Astra/max를 자동 상속하지 않는다.

`ResearchDone` 이후에만 새 원고를 작성한다. 그 후 `PublicationReady`에서 실제 문장·최종 그림·PDF metadata·모든 페이지를 검증한다. 지금 정본 QMD·protected evidence·기존 dated exports는 수정하지 않는다. prototype 구현/시연/재사용 규칙은 별도 gate다. 유효한 null/negative도 연구 완료가 될 수 있지만 invalid-only를 efficacy 완료로 바꾸지 않는다.

## 7. Graph 재개 규칙

현재 canonical JSON은 연구 projection이지 native event store가 아니다. 비순환 `next → handoff → graph`를 유지한다. UI-parity 전용 과거 navigation validator는 해당 frozen predecessor에 남기고, 새 연구 navigation은 별도 contract로 검사한다. 전체 graph byte/integrity와 출판 gate는 면제하지 않는다. 과거 experimental cutoff와 현재 literature/design revision date는 분리한다.

**다음 우선순위:** 공개 ML task programme/neutral scorer 적합성 → B/C/G 차이 명세 → owner/port/uncertain-run capability 확인 → 예산·분산·표본 계획 → 별도 실행 승인. 원고나 native 기능 확장이 다음 단계가 아니다.

## 8. Fable 5.1 독립 검토 반영

검토 commit `f2e203058`의 Fable 판정은 `REVISE_BEFORE_EXPERIMENT`다. 보고서와 13개 입력 해시를 검증했고 F1–F14를 수용/조건/반박으로 조정했다. 이전 5인 문서와 원검토는 보존한다. 최신 qualifier는 `paper/research/fable51-design-review-20260907/integration/review-synthesis-ko.md`, 현행 study와 phase-completion 계약은 같은 디렉터리의 `integrated-study-design.json`, `research-completion-contract.json`이다. 이 첫 검토 기록은 당시 수정본의 재검토가 아니었다. 후속 `ee7e0fdaf` 재검토는 아래 §9에 별도로 기록한다.

기존 Prime native 기질 위의 project-local 연구 apparatus를 제품 구현과 구별한다. R1 scientific run과 bounded R2 분석에 각각 receipt를 요구한다. P0 통합 feasibility → P1 B/C/G 개발 → P2 별도 봉인 확증을 작업용 경로로 둔다. 각 단계는 독립 계약·수치 예산·승인이 필요하며 아직 모두 미승인이다. UNKNOWN 블록 자동 제외, event 없는 G 효과 0, hash만으로 blindness, 기능 로그만으로 인과 분리, C/G primary 자동 고정은 채택하지 않는다.

다음은 실제 공개 ML programme/scorer/ancestry에 이 정의를 맞추는 것이다. feasibility 실패나 예산 소진은 실행 중단이며 분석·명시적 범위 결정 없이 ResearchDone나 writing gate를 열지 않는다. native 재개는 기존 test-instance 조건과 사용자 승인에 계속 종속된다.

## 9. 수정본 재검토 — 과제 구체화로 진행

Fable 5.1 재검토 판정은 **READY_FOR_TASK_QUALIFICATION**(조건부)이다. F1–F14 중 12개는 설계 해결, F3/R1–R2 집행과 F7/강제 gate는 부분 해결이다. 실증 종결은 없고 task/arm/efficacy는 0이다. 전체 보고서와 22개 입력을 검토 commit `ee7e0fdaf`에서 확인했다. 다음은 추가 일반 검토가 아니라 실제 공개 ML programme/scorer/license/ancestry의 문서 수준 적합성 연구다.

과제별 P0 명세에는 `re-review-01/integration/task-qualification-requirements.json`의 N1–N10 조건을 반영한다. 모든 단계에서 invalid/missingness/retry/repair 규칙을 고정하고, MUE는 P1 대비를 보기 전에 commit한다. 실행·최종 lock의 신뢰 경계와 자동 R1/R2 분류/lineage는 실제 capability로 검증한다. adapter 밖 우회 탐지나 비차등 scorer 결측을 가정하지 않는다.

이 재검토 당시 `apparatus-scope-decision.json`은 보류였지만, 후속 `c40c59a9`가 지정 경로의 apparatus 코드·로컬 모의 검증을 승인했다. 원 proposal의 pending 값은 과거 상태로 보존한다. 현행 권위는 `paper/research/public-ml-programme-qualification/effective-authority-v2.json`이다. 구현 승인은 특정 P0 실행, native 재개 또는 원고 권한을 포함하지 않는다. 설치·공개 범주 승인은 별도 실제 대상/조건을 충족해야 한다.

## 10. 현재 작업 — 과제 비교·정적 장치와 결정 권한

현행 자료는 `paper/research/public-ml-programme-qualification/`에 있다. `effective-authority-v2.json`, `account-and-important-decision-policy-v1.json`, `candidate-disposition-correction-v1.json`과 비밀 없는 `kaggle-readonly-access-receipt-v1.json`을 먼저 읽는다. 계정은 ACCESS_DEPENDENCY이지 자동 제외 조건이 아니다. House Price(`home-data-for-ml-course`)와 Spaceship Titanic을 복원했고, CIFAR-10 및 California Housing과 비교한다. 최종 과제·중요 제외·연구 범위/지표/비교군 변경은 제안 후 사용자 확인을 받는다. 아직 과제를 확정하지 않았다.

기존 Prime daemon/AgentSession/REPL/RLM으로 파일 소유권이 다른 문헌·코드·인터페이스·정적 구현을 병렬 처리했다. 소규모 byte-binding fixture는 로컬 commit `ccdbf3df0a23169637711ea363262ced89aaf2df`이며, clean clone에서 7 tests와 `npm run check`가 통과했다. 이는 process-local lock-ID 및 실제 byte 비교 사양일 뿐 durable/campaign-level lock이나 hidden scorer 격리가 아니다.

원문/코드/인터페이스 fan-in은 `integration/parallel-audit-intake-v1.json`, MLAgentBench 완독은 `mlagentbench-primary-read-v1.json`, 원문 LF 보정은 `recent-source-lf-locator-correction-v1.json`에 있다. 원보고서의 account-free 제외와 LF 표기는 그대로 보존하되 현행 결론으로 채택하지 않는다. 실제 학습·평가·World 실행은 0이고 기존 invalid/소모 run은 재사용하지 않는다. 다음은 네 과제의 과학적 적합성·채점/누설 위험·비용 비교안과 선택 확인이다.
