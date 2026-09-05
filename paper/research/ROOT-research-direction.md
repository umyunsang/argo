# 연구 방향과 목적 — ROOT active entrypoint

상태: **AUTHORITATIVE RESEARCH ENTRYPOINT · NATIVE CONSTRUCTION PAUSED**
갱신: 2026-09-05T06:52:41+09:00

이 문서가 현재 연구의 루트다. 하위 가설·방법·지표·판정은 이 문서와 active revision을 따라야 한다.
원본 PDF는 수정하지 않으며 개인 식별값을 graph나 공개 산출물에 복사하지 않는다.

## 1. 단일 연구 연쇄

> **졸업논문 연구 → 문헌·실험으로 검증한 ARGO 통합 설계 → 허용된 native 구현 → NAIS 프로토타입·시연 → 구현 관측의 연구 계보 환류**

논문과 NAIS를 독립 트랙으로 나누지 않는다. 졸업논문은 ARGO의 구성·연결·제어 정책을 선택하는 선행 연구다.
NAIS 프로토타입은 그 선택을 계승해야 한다. 연구 지표, 구현 acceptance, 현장 규칙은 같은 연쇄의 서로 다른 증거층이다.

## 2. 권위 원본

| ID | 역할 | 경로/범위 | SHA-256 |
|---|---|---|---|
| THESIS | 연구 목적·scientific choice | Desktop 졸업논문계획서 p.1 | `d2ab302410321cb43c499a681d289df72d86f889eaf4ca0b58b8e8ad804ea8f5` |
| APP | 목표 제품 동작·구현 제안·공개 의무 | 현재 사용자 제공 NAIS 신청서 pp.2–4,7 | `a829572375ddca11ec94cbbd48827419564f655fa36aab25e3a9d3fdca8a47e6` |
| NOTICE | 대회 일정·배점·현장 개발·제출 | 현재 사용자 제공 모집 공고 pp.2,3,5 | `b46c64b79eec2c317017977c6821115f49d02cd16bf481949e91bcd38c92610a` |

현재 APP는 이전 Downloads 사본 및 구 `ca35…` 참조와 다른 파일이다. 현재 APP에는 36시간 계획이 없다.
실제 제출 성공 여부는 이 경로만으로 추정하지 않는다.

## 3. 연구 목적

1. agent가 연구 문제·가설·대안·구분 예측·조건·방법·지표·중단 규칙을 직접 선택한다.
2. 모든 선택은 실제 읽은 source bytes/span, 반례, 적용 범위와 연결된다.
3. 둘 이상의 설계/실험 후보를 같은 비교 조건에서 경쟁시키고 이유 있게 유지·보류·수정·기각한다.
4. 실행은 사전 고정 protocol/code/environment와 receipt로 재현 가능해야 한다.
5. 결과가 다음 연구 결정을 바꾸며 실패·무효·기각 방향도 재개 조건과 함께 보존된다.
6. 다른 agent가 사적 대화 없이 active graph와 receipt로 허용 next action과 금지 이유를 복구한다.
7. 검증된 최소 구성이 후행 ARGO 계약과 NAIS prototype acceptance를 실제로 바꾼다.

## 4. 현재 연구 질문과 active 설계

전체 질문은 다음과 같다.

> 장기 자율 R&D에서 근거 기반 scientific choice, 경쟁 실행, 결과 기반 successor, 재현·인계를 제공하는 유용한 최소 ARGO 구성과 native ownership 경계는 무엇인가?

가장 먼저 검사할 불확실성은 typed evidence dependency/version 정책이 동일 기회의 강한 result-driven experiment-tree
comparator보다 다음 실험 선택·선택적 재개방·fresh-context 인계를 개선하는지다.

Active 설계: `paper/research/integrated-research-design-active.md`
기제–native 계약: `paper/research/material-mechanism-evidence-map.md`
Active graph 인계: `paper/research/active-graph-handoff-manifest.json`
다음 실험 명세: `paper/research/next-experiment-manifest.json`

기존 `.planning/.../11-integrated-experiment-design.md`의 G×C×F/L×P/Stage R 설계는 보존된 대안이다. 8-cell factorial,
16과제, 13개 검정은 더 이상 루트의 불변 조건이 아니다. 첫 주 contrast가 설명을 구분하지 못할 때만 후속으로 연다.

## 5. 비교·채점·분석 규율

- 고정 비처리 조건: task/data/split/source/scorer/opportunity/model/tool/budget.
- 사전 등록된 treatment policy와 condition별 code hash 차이는 허용한다. 미등록 차이만 비교 불가다.
- primary는 condition-blind rule verifier의 independently checkable decision-contract success다.
- 규칙 점수는 과학적 진실·보편적 참신성·SOTA를 자동 인증하지 않는다.
- task/episode가 추론 단위이며 rollout/seed는 nested다.
- confirmatory 주 가설은 `H0: Δ≤0`; `Δ=+0.10`은 power 설계 시나리오다. CI lower `>+0.10` 구 성공 조건은 폐기한다.
- best-of-k/seed/checkpoint 선택은 confirmatory estimand가 아니다.
- fatal protocol/evaluator/agent failure는 intention-to-run 0점이다. infrastructure failure만 blinded 1회 retry한다.
- hidden scorer/gold 접근은 run 무효다.

## 6. 재료와 ownership

- Pi/Prime: daemon, AgentSession, worker, persistent REPL/RLM과 복구의 고정 실행 기질
- Exa 등: discovery adapter; snippet은 증거가 아님
- 원문/evidence plane: bytes/hash/span/scope의 append-only 근거
- research/context graph: versioned dependency projection과 selective recheck 후보
- ORX: 지정 scientific run authority; ARGO는 receipt link/import만 소유
- research refine: 가설·방법·다음 결정 successor
- engine refine: 별도 held-out promotion/rollback 계보

APP의 LangGraph StateGraph/SqliteSaver는 구체적인 graph-plane 구현 **후보**다. native ownership 중복, 정합성·복구 비용과
대안을 비교하기 전 최선으로 고정하지 않는다. Python validator/fixture는 제품 runtime이 아니다.

## 7. 현재 증거 상태

- Stage 0 scorer: 16개 task, valid/corrupt 각 3회, 총 96 evaluator 실행, 16/16 deterministic PASS
- 공통 image: Linux arm64 `sha256:026ce848fa7de5d15510192aaeaadfe05cc252364df51ddc292d3655f0cc2060`
- environment parity: Python distribution 91개, Debian package 95개, PASS
- actual syscall isolation: runtime policy PASS
- Opus 4.6 OAuth 개발 파일럿: primary non-stale delta 0; secondary full-resolution BASE 0/6, TARGET 6/6
- 한계: 여섯 주제는 한 인과 template의 표면 변형, 최종 순서 6/6 TARGET→BASE, TARGET token 1.1007×
- Confirmatory efficacy result 0; C confirmation은 HOLD

Stage 0은 계측기·runtime boundary 결과다. Stage B는 한 template-family의 탐색 행동 결과이며 모집단 효능이 아니다. Study A, T3, T1′, B2와 구 synthetic 결과는 active efficacy
근거에서 격리·철회한다.

## 8. Graph authority와 revision

`paper/context-graph.json`은 현재 구 root/status와 역사 edge를 포함하므로 active projection으로 그대로 사용하지 않는다.
`07-context-graph-repair-overlay.json`은 `DRAFT_NOT_APPLIED`이며 canonical 수리로 보고하지 않는다. 원고의
`current-evidence-20260905/context-graph.json`은 46-node local editing map이며 제품/canonical graph가 아니다.

모든 새 agent는 `active-graph-handoff-manifest.json`을 통해 실제 consumer, precedence, 미적용 상태를 먼저 확인한다.
RETRACTED result의 역사 `supports` edge는 보존할 수 있으나 active support로 소비하지 않는다. source 무효화는 영향받는
결정만 `requires_recheck`로 열고 독립 근거와 무관한 결과를 보존한다.

## 9. NAIS 조건과 clean-room

NOTICE p.3 본선 배점: 적합성 10, 활용성 20, 혁신성 25, 실현가능성 25, 확장성 20. 논문 primary metric과 다르다.
NOTICE p.5는 실제 개발 전 과정이 본선 기간에 수행되어야 함을 명시한다. 사전 세로 JPG/PNG 포스터와 현장 개발을 구분하고,
본선 결과물은 prototype, PPT/PDF, GitHub source이며 발표 약 5분·질의응답 약 3분이다.

웹페이지의 17:00–다음 날 12:00은 전체 행사 관측치이며 순수 개발시간으로 확정하지 않는다. 공개 OSS/API, 사전 설계자료,
custom 코드의 정확한 재사용 범위는 `UNKNOWN`이다. 현재 연구 worktree 반입을 허용 또는 금지로 가정하지 않는다.
Push·공개·제출 권한도 없다.

NAIS 최소 동작 후보는 source→둘 이상의 실제 실행 설계→동일 기준 비교→이유 있는 접기→관측 기반 successor 1회→graph와
fresh-context 인계다. 한 번의 실행만으로 병렬 경쟁을 구현했다고 주장하지 않는다. engine self-modification은 MVP 밖이다.

## 10. 현재 중단선과 다음 행동

Native construction은 계속 중단한다. paid episode는 Stage별 exact upper cost와 20% contingency를 숫자로 계산하고 사용자가
그 금액을 승인하기 전 실행하지 않는다. LG Aimers와 private instance는 접근하지 않는다.

Stage A와 Opus 4.6 개발 파일럿은 완료됐다. 네 비동형 causal family와 fail-closed runner도 무과금으로 검증됐다.
교정 B2 8개는 실행됐으나 scorer의 stale 정의, action 의미, record 접근 enum 결함 때문에 인과 판정에 사용할 수 없다.
원 결과는 보존하고 status-only 감도분석만 보고한다. 현재 다음 행동은 outcome contract만 교정한 B3 8개를 사용자에게
별도 승인 요청하는 것이다. C confirmation은 계속 승인되지 않았다.
