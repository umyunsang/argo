# ARGO 통합 연구설계 — active revision

상태: **ACTIVE DESIGN · NOT PREREGISTERED · NOT AUTHORIZED FOR PAID EXECUTION**
갱신: 2026-09-05T06:52:41+09:00
상위 권위: `paper/research/ROOT-research-direction.md`

이 문서는 `.planning/2026-09-04-argo-paper-research-audit/review-packet/11-integrated-experiment-design.md`의
G×C×F 전체요인 설계를 삭제하지 않고 **active 연구 선택에서 대체**한다. 기존 문서는 설계 이력이며 실행 권한이 아니다.

## 1. 하나의 연구 프로그램

본 연구는 서로 독립인 논문 benchmark와 해커톤 demo를 만들지 않는다.

> 문헌·유사 실험 → 설계 대안 → 구분 가설과 실험 → 관측 → 채택·기각한 ARGO 계약 → 허용된 구현 → NAIS 프로토타입·시연 → 연구 계보 환류

졸업논문은 ARGO의 구성과 연결 방식을 선택하는 선행 연구다. NAIS 프로토타입은 그 결과를 계승해야 한다.
연구 지표, 구현 acceptance, 현장 개발 규칙은 같은 연쇄의 서로 다른 증거층이다.

## 2. 연구 질문

### 전체 질문

근거를 읽고 문제·가설·조건·방법·지표·중단 규칙을 선택하며, 경쟁 설계를 실제 결과로 비교하고,
유효한 연구 상태를 다른 agent에게 넘길 수 있는 **유용한 최소 ARGO 구성과 native ownership 경계**는 무엇인가?

### 첫 인과 질문

동일한 source spans, 후보, 구분 예측, 실행 결과, 검토·수정 기회, 모델 및 예산에서,
**버전·반증·evidence dependency를 사용해 무효화와 재계획을 제어하는 정책**은 가장 가까운 강한
result-driven experiment-tree 정책보다 증거에 맞는 다음 실험 선택과 fresh-context 인계를 개선하는가?

이 첫 실험은 전체 통합 목적을 graph 실험 하나로 축소하지 않는다. 가장 불확실하고 prototype 구조를 실제로 바꿀
정책 선택을 먼저 검사한다.

## 3. 경쟁 대안과 선택

| 대안 | 지위 | 선택/기각 이유 |
|---|---|---|
| flat ledger + generic iteration | 해석용 baseline | 저비용 기준선이나 강한 선행 comparator가 아니다. |
| proximity graph + tournament/evolution | 후속 또는 후보 생성 정책 | Co-Scientist의 가까운 기제다. graph+competition+refine 자체의 신규성 주장을 차단한다. |
| result-driven experiment tree | **주 comparator** | The AI Scientist의 결과 기반 branch/repair/improve 기제와 가장 가까워 ARGO의 다음 실험 선택을 강하게 비교한다. 전체 시스템 재현이 아니라 mechanism-matched comparator다. |
| typed evidence-dependency/version policy | **주 treatment** | source→claim→decision→action 의존성과 선택적 무효화·재개방·인계를 시험한다. 아직 효능은 미평가다. |
| 기존 G×C×F 8-cell factorial | 조건부 후속 | graph, 후보 경쟁, refine 중 어떤 요소가 설명하는지 첫 결과가 구분하지 못할 때만 실행한다. |

주 contrast는 `TYPED_POLICY − RESULT_TREE_POLICY` 하나다. proximity/tournament를 후보 생성에 사용한다면 두 조건에
같게 고정한다. flat baseline은 개발단계 floor/해석에만 사용하며 강한 comparator를 대체하지 않는다.

## 4. 처리 조건과 비교 가능성

두 조건에서 다음을 고정한다.

- 같은 task/episode, source bytes와 spans, 후보 pool, 구분 예측, 관측 결과
- 같은 최대 후보 수, review/critique/refine 횟수와 순서
- 같은 모델/provider revision, tool surface, token·tool·시간·비용 ceiling
- 같은 condition-blind rule scorer와 실패 처리
- 같은 실행 substrate와 scientific-run authority

허용되는 유일한 차이는 사전 등록된 **research-state control policy와 그 구현 hash**다. 총 코드 hash가 다르다는 이유로
처리군 비교를 금지하지 않는다. 미등록된 data/scorer/opportunity/budget 차이는 비교 불가로 처리한다.

## 5. episode와 독립 평가

한 episode는 다음 연쇄를 완결한다.

1. 경쟁 가설 또는 설명 두 개 이상
2. 서로를 구분하는 관측 가능 예측
3. 고정 자원 안에서 선택한 다음 실험
4. held-out 관측 또는 재현 가능한 공개 관측
5. 유지·보류·수정·기각 중 다음 결정
6. 새 context agent가 복구할 handoff

독립 **task/episode**가 추론 단위다. rollout/API 호출은 task 안 반복이며 독립 표본으로 세지 않는다. 동일 문제의 seed만
바꾸어 population 크기를 늘리지 않는다. task family별 development/evaluation 분리를 고정한다.

ScienceAgentBench는 주어진 scientific-computing 실행 능력의 보조 endpoint로만 유지한다. 원 논문이 범위 밖으로 둔
ideation/experimental design을 대신 측정한다고 주장하지 않는다.

## 6. outcome

### Primary: independently checkable decision-contract success

규칙 기반 verifier가 다음을 모두 확인할 때 episode 성공이다.

- 선택이 제공된 source span·제약·관측과 모순되지 않는다.
- 관련 source 무효화 시 그 source에 의존한 결정만 `requires_recheck` 또는 재개방된다.
- 무관한 edge perturbation은 유효한 결정·실행 결과를 보존한다.
- 다음 실험은 두 가설을 실제로 구분하며 중복 완료/기각 방향을 이유 없이 반복하지 않는다.
- handoff가 허용 next action과 금지 이유를 원 대화 없이 복구한다.

이 점수는 과학적 진실이나 보편적 참신성을 자동 인증하지 않는다.

### 별도 secondary

- official task execution score
- invalid/retracted claim reuse 수
- 불필요한 반복 실행 수
- handoff contract 충족률
- token/tool/time/cost 및 fatal reliability
- evidence-to-decision trace completeness

임의 곱 `S×P³`와 ALL-ON이 일곱 대안을 모두 이겨야 한다는 조건은 primary에서 제거한다.

## 7. 표본·분석·검정력

현재 task pack과 실제 variance가 없으므로 confirmatory 표본 수는 **미정**이다. 네 개발 과제로 이질성을 확정하지 않는다.

- development에서 manipulation, floor/ceiling, task-family 분리, discordant-pair/분산 시나리오와 episode 비용을 측정한다.
- confirmatory 주 검정은 하나의 paired task-level contrast에 대해 `H0: Δ ≤ 0`, 설계 대립효과 `Δ = +0.10`으로 둔다.
- `+0.10`은 power 설계값이며, 유용성은 점추정·구간·비용과 별도로 해석한다.
- CI lower bound가 `+0.10`을 넘어야 한다는 구 조건은 폐기한다. 최소유용효과 검정을 택하려면 별도 `Δ1>0.10` 근거가 필요하다.
- binary endpoint면 task-level discordance를 사용하는 paired exact/사전 고정 permutation 계열을 검토하고, graded endpoint면
  bounded paired mean의 task-cluster randomization/bootstrap을 사전 고정한다.
- best-of-k, best-seed, best-checkpoint는 confirmatory estimand가 아니다.

Power는 development 결과를 본 뒤 outcome-blind simulation으로 계산한다. 최대 task 수, 중단 기준, exact budget이 없으면
protocol fingerprint를 만들지 않는다.

## 8. 실패·비용·중단

- fatal protocol/evaluator/agent failure는 intention-to-run에서 0점이다.
- infrastructure failure만 blinded 1회 retry가 가능하며 원 실행은 reliability 분모에 남긴다.
- hidden scorer/gold 접근은 run 무효다.
- 비용·token·tool·시간은 action 전 예약하며 ceiling 초과 action을 시작하지 않는다.
- paid episode는 Stage 0/R/primary/follow-up의 exact upper envelope와 20% contingency를 숫자로 계산하고 사용자가 그 금액을
  승인한 뒤에만 시작한다.
- 현재 exact paid budget과 승인은 `null`이다.

## 9. 결과가 실제 ARGO 선택을 바꾸는 규칙

| 결과 | 다음 설계 결정 |
|---|---|
| typed 정책이 주 contrast에서 양수이고 구간·비용이 채택 기준을 충족 | typed dependency/version control을 ARGO research-state plane의 MVP 계약으로 승격 |
| 유용한 차이를 배제할 만큼 정밀한 null | 더 단순한 result-tree 정책을 채택하고 graph는 audit/export 용도로 축소 |
| typed 정책이 음수 | control policy를 기각하고 원인 분석 전 구현하지 않음 |
| manipulation 미발화·ceiling·중복 정보 | 효능 null로 해석하지 않고 task/instrument를 수정, 결과는 효능 분모에서 격리 |
| 불충분한 precision 또는 비용 초과 | 선택 보류; 기능을 더 쌓지 않고 표본·비용 대안을 다시 비교 |

첫 결과가 graph 표현, candidate competition, bounded refine, retrieval, recovery 중 원인을 구분하지 못할 때만 해당 ablation을
후속으로 연다. 더 단순한 구성이 이기면 그 구성을 ARGO 후보로 남긴다.

## 10. 논문→native 계약→NAIS

논문에서 채택된 선택은 `material-mechanism-evidence-map.md`의 owner/interface 계약으로 이동한다. 구현 증거가 없으면
`NOT_IMPLEMENTED`다. Python oracle과 Stage 0 fixture는 제품 runtime이 아니다.

NOTICE p.3의 본선 기준은 적합성 10, 활용성 20, 혁신성 25, 실현가능성 25, 확장성 20이다. 이는 논문의 primary metric이
아니다. prototype acceptance에서는 최소한 둘 이상의 **실제 실행 후보**, 같은 기준의 비교, 이유 있는 접기, 관측 기반 다음
결정 1회, fresh-context 인계를 보여야 한다. 한 설계만 실행해 병렬 경쟁을 구현했다고 말하지 않는다.

NOTICE p.5에 따라 실제 개발 전 과정은 본선 기간 안에서 수행되어야 한다. 사전 포스터/기획과 현장 개발을 구분한다.
현재 연구 코드·graph·custom 구현의 반입 가능성을 가정하지 않는다. 공개 도구/OSS/API/설계자료의 정확한 재사용 범위와 순수
개발시간은 본선 지침 전까지 미확정이다.

## 11. 근거와 현재 상태

- THESIS p.1, SHA-256 `d2ab302410321cb43c499a681d289df72d86f889eaf4ca0b58b8e8ad804ea8f5`
- APP pp.2–4,7, SHA-256 `a829572375ddca11ec94cbbd48827419564f655fa36aab25e3a9d3fdca8a47e6`
- NOTICE pp.2,3,5, SHA-256 `b46c64b79eec2c317017977c6821115f49d02cd16bf481949e91bcd38c92610a`
- 방향 검토 `review.md`, SHA-256 `b5c39b936cda41164ab4f385c1d31b2bfb2a6a0f239795c368338bec904bc0b8`
- 직접 문헌 비교 `literature-challenge.md`, SHA-256 `856c7808aff64671a3641efb29b2fa7e5c640aa48d77511b7fd31eccfa95395c`
- 원본 조정 `source-addendum.md`, SHA-256 `0609708c351bf3fa5b8619400561f8a32cc701817431396df0cb83e045b3e403`

Stage 0에서 scorer 16/16, evaluator 96회, environment parity, 실제 OS runtime policy는 검증됐다. 이는 계측기 결과다.
`integrated_task_runner_certified=false`, 인정된 효능 결과 0, paid model call 0이다.

## 12. Frontier-model development pilot outcome (2026-09-05)

`anthropic/claude-opus-4-6` under OAuth was tested in a same-two-record verification-budget task. The computed dependency target allocated one slot to the sole support and left one model-selected slot. A thin four-tool mechanism enforced actual reads.

- preregistered primary non-stale decision: BASE 6/6, TARGET 6/6, paired delta 0
- secondary fully resolved withdrawal: BASE 0/6, TARGET 6/6
- critical record inspection: BASE 0/6, TARGET 6/6
- TARGET/BASE tokens: 59,214/53,796 = 1.1007×

The primary null is compatible with a frontier ceiling: the base model already avoided stale action by abstaining. The secondary suggests targeting can convert conservative abstention into a resolved decision, but it is not a causal efficacy result because the six topics share one causal template, realized order was TARGET→BASE in every pair, and treatment content increased tokens. Therefore confirmation C is **HOLD**, not promoted.
