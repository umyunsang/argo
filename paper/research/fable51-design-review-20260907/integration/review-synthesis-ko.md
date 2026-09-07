# Fable 5.1 연구설계 검토 — 수신·대조·반영

## 결론

- 검토 모델: `anthropic/claude-fable-5-1`, `xhigh`.
- 검토 대상: `f2e203058eedd4bbf5af2674fcc77d6013d5437b`.
- Fable 판정: **REVISE_BEFORE_EXPERIMENT**. 설계 방향은 **ADEQUATE_WITH_REVISIONS**, 실행은 **NOT_READY**.
- root 판정도 실험 전 수정 필요다. 이 문서는 검토를 처리한 기록이지, 수정본에 대한 Fable 재검토 PASS가 아니다.
- 보고서 두 파일의 SHA와 요청의 13개 입력을 committed blob에서 재도출했다. primary 6개·resource 10개·analysis 5개, 총 21개 미정 필드도 확인했다. 인증 task와 실행 가능한 B/C/G arm, 통합 효능 근거는 아직 없다.

## 1. Sol 검토 뒤에도 남은 중요한 공백

1. **실험용 apparatus 계층.** native 구축이 중단된 상태에서 무엇을 사용해 실제 연구 비교를 수행할지 불명확했다. 기존 Prime 세션/REPL/RLM 위의 project-local 연구 prompt/모듈/journal/ORX adapter/scorer 계층을 개념상 분리했다. Python fixture를 제품 runtime으로 승격하거나 별도 supervisor를 만드는 것은 아니다. 구현 파일·권한·protocol hash는 아직 미정이다.
2. **기제 발화와 주 outcome.** graph의 revision/revalidation/continuation 기능을 관측할 과제 조건이 필요하다. 자연 과제와 정당한 event-inclusive 과제를 후보로 남겼다. 모든 arm에 공통인 event bytes·시점·미도달 처리를 사전 정의해야 한다. G의 효과가 잘 나오는 event를 보고 고르는 방식은 허용하지 않는다.
3. **R1 scientific execution / R2 local analysis.** 학습·후보 생성·선택용 평가·hidden scoring은 task-bound scientific-run 권위에 둔다. 기존 공개 input/output의 bounded 분석·재계산은 별도 분석 receipt로 기록한다. small/sanity라는 이름으로 새 학습이나 채점을 우회하지 않는다.
4. **통합 loop 자체의 feasibility.** 하나의 공개 ML programme에서 실제 근거→실행→평가→successor→복구가 성립하는지와 실패·전체 비용을 보고할 별도 단계 P0를 둔다. 한 programme의 완주는 일반 신뢰성이나 비교 효능이 아니다. 기존 SAB Stage 0와 구별한다.

## 2. 그대로 채택하지 않은 처방

| Fable 제안 | root 판단 |
|---|---|
| UNKNOWN이면 모든 arm의 programme block을 primary에서 제외 | 기본 규칙으로 기각. launch 횟수가 treatment에 달리면 whole-block complete-case 제외도 선택 편향이다. 배정 분모·UNKNOWN·비용을 보존하고 outcome 정의에 맞는 결측/범위/감도분석을 사전 고정한다. |
| event가 없으면 G−C 기대효과 0, event-inclusive primary를 기본값으로 | 근거 부족. Prime 논문의 nanoGPT 잡음 관측은 이 가설의 증명이 아니다. 과제 관련성과 관측 가능성을 먼저 판단한다. |
| hash로 hidden split/family를 봉인 | 변경 탐지로 수용하되 기밀성·blindness로 부르지 않는다. 독립 custody/접근 제어와 사람·모델의 사전 노출은 별도다. 공통 오염도 policy와 상호작용할 수 있다. |
| graph 기능 호출 로그가 추가 ablation을 대체 | 로그는 발화를 보여 줄 뿐 표현·결정적 계산·context의 인과 효과를 분리하지 못한다. 기본 주장은 package 수준에 둔다. |
| 단일 programme 두 시작으로 후속 power 계획 | 초기 within-cell 변동의 탐색 자료일 뿐이다. between-programme 분산이나 안정된 표본 계획을 보장하지 않는다. MUE도 잡음에 맞춰 낮추지 않는다. |
| C feasibility → C/G confirmation, 가장 저렴한 arm을 prototype 기본값으로 | 작업용 권고로 보존한다. 최강의 단순 비교군은 개발 뒤 고정하며, 실제 측정한 feasible/safe 후보 밖의 비용 우위를 추정하지 않는다. fallback은 공학적 선택이지 효능 승자가 아니다. |
| 한 번의 repair 또는 총 예산 소진으로 연구 완료 | 유한 중단 원칙은 수용한다. 횟수/예산은 아직 고정하지 않는다. 중단은 실행 종료이며, 분석·범위 결정 없이 ResearchDone/원고 권한이 열리지 않는다. |

## 3. 설계에 반영한 규칙

- B/C는 같은 비graph 도구·원문·계산 권리를 가진다. C는 실제 controller/tool guard를 사용해 의무를 집행한다. C/G의 집행 강도는 같게 맞춘다. 아직 prompt/code/capsule/context 한도 해시는 미정이다.
- programme을 block으로 paired 배치하고 순서/resource slot을 무작위화한다. source ancestry·반복 시작·between/within 변동을 구별한다.
- final scorer는 treatment-labelled 연구 trace를 받지 않는다. P0/P1 평가 자료와 P2 confirmation 자료를 분리한다. final artifact 선택 전 hidden score 공개는 금지한다.
- continuation·근거 승계·행동 지표는 secondary다. terminal primary가 null이면 승격하지 않는다.
- 단계별 권한을 분리한다: **RD4a-pre(P0), RD4a-dev(P1), RD4b(P2)**. 첫 승인은 후속 단계를 허용하지 않는다. 현재 모두 미승인이다.
- native 재개에는 기존 test-instance 성과·안정성·병목 검증과 사용자의 명시적 재개가 필요하다. 이 공개 연구나 Fable 리뷰가 DeepVoice 관련 조건을 해제하지 않는다.
- 외부 Arbor anchor는 선택이다. 현재 설계에서는 서술적 비교로 한정한다. 다른 substrate라고 모든 whole-system causal 연구가 불가능한 것은 아니지만 graph-control 단독 귀속은 불가능하다.

## 4. 보존·다음 작업

전체 F1–F14의 수용/조건/반박과 종결 근거는 `finding-response-matrix.json`에 있다. `integrated-study-design.json`은 apparatus·run class·결측·봉인·블록·차이표·단계의 현행 successor다. `research-completion-contract.json`은 단계별 승인과 bounded closure를 규정한다. 이전 다섯 Sol 문서와 Fable 원검토는 변경하지 않았다.

다음은 **하나의 실제 공개 small-compute ML programme, 독립 scorer와 source ancestry의 구체화**다. 그 과제에 맞춰 apparatus와 B/C/G 실행 명세, event 여부, 결측 규칙, MUE·비용·표본을 정한다. 이후에만 immutable method/runtime review와 정확한 새 실행 승인을 요청한다.

C64 causal invalid, v12 INVALID/NOT_ADMITTED, font의 다섯 호출 한정 호환성, World-init static-only는 그대로다. 새 실험·설치·원고·native 구현·push는 없었다. 다른 모델의 독립 검토는 실제로 추가됐지만 과학 실험이나 효능 증거가 추가된 것은 아니다.
