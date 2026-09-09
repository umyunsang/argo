# Efficiency Matters 원문 검토

**설계 판단:** 검색 예산 배분과 evidence graph 제어를 서로 다른 설계 축으로 분리할 근거다. graph의 우월성이나 현 House Price에서의 fluid 선택을 뒷받침하지 않는다. 현재 단일 locked artifact의 hidden MAE를 유지하며, dev 단계의 anytime 곡선과 실제 총비용을 보완 관측으로 설계하는 데 유용하다.

[Efficiency Matters in Autonomous Research](https://arxiv.org/abs/2607.24647v1), Haiqian Yang·Yuan Cao, arXiv v1. **Preprint**이며 supplied full text에서 peer-reviewed venue는 확인되지 않았다. 제목면은 2026-07-28, arXiv stamp는 2026-07-27이다. 원문은 LF 1–1061 전체를 읽었다. PDF figure pixels와 코드/원자료는 별도 검증하지 않았다.

## 원문이 실제로 비교한 것

12개 AutoLab 시스템 최적화 과제에서 Qwen3-Coder-480B FP8가 이전 평가 이력을 바탕으로 한 번의 completion으로 코드 수정을 제안한다. multi-turn agent loop는 없다. 고정 정책은 width 64, 평가 500회, 과제별 seed 3개다(LF 487–501). 이것은 현재 P0의 dev 3회·final refit 1회와 다른 프로토콜이다.

| 설계 | 고유 기제 | 현 연구에 주는 역할 |
|---|---|---|
| Greedy chains | 독립 incumbent chain에 예산 배분 | 단순 반복 개선 대안 |
| Beam | 좋은 frontier를 유지하며 초기에 빠르게 깊이 확장 | breadth/depth 스케줄 대안 |
| Tree | 하나의 후보 tree에서 유망 branch에 평가 배분 | candidate search 구조 |
| Evolutionary | population과 tournament parent 선택 | 실패에 견디는 다양성 유지 대안 |
| Fluid | hill-climbing chain forest에서 다음 평가를 bandit 배분 | 적응형 예산 스케줄 대안 |

근거 LF 535–552, 629–730. Fluid는 서로 다른 검색 알고리즘을 혼합한 heterogeneous portfolio가 아니다. 이질적 검색 구조 portfolio는 Discussion의 미래 확장이다(LF 762–765). Fluid의 우선순위는 최근 개선율·incumbent 품질·탐색 보너스로 결정되고, archive/reseed·crashed-parent repair·중복 완화·16→64 warm start가 함께 포함된다. 전체 gain을 bandit 한 요소나 graph topology로 귀속할 개별 ablation 결과는 이 원문에서 제시되지 않는다.

## 비용과 endpoint의 차이

논문은 각 평가까지의 최고 verifier reward를 `R(n) = max(r_1, ..., r_n)`로 두고 평균 높이 AUC로 효율을 측정한다(LF 303–432). 관측된 과제 최고 reward를 정규화 ceiling으로 사용한다. **저자 보고치**는 normalized AUC fluid 0.780, beam 0.718, 같은 run들에서 최선 고정 정책을 사후 고르는 oracle 0.784다(LF 733–742). 로컬 재현값·독립 hidden 성과·graph 효과·power prior가 아니다.

- 평가 횟수는 총 token·금액·CPU/GPU·wall time을 대체하지 않는다. 초기는 8개/16 chains, 이후 최대 32개/64 chains가 비동기로 실행된다(LF 719–723).
- Archive-best verifier reward는 dev evidence로 단일 artifact를 먼저 고정한 후 얻는 hidden MAE와 다른 endpoint다. 현행 primary를 이 AUC로 교체하거나 hidden score를 반복 조회해서 곡선을 만들면 안 된다.
- 같은 run에서 얻은 empirical ceiling과 oracle은 서술적 비교 장치다. 이를 사전 MUE·유효 표본수 또는 확증 분석의 독립 기준으로 재사용하지 않는다.
- 본문은 비싼 과학 실험을 동기로 삼지만 실제 verifier는 고정·저비용·형식적·즉시 평가다. 후속 재사용을 통해 가치가 드러나는 연구나 평가 기준의 발전은 실험 범위 밖임을 직접 인정한다(LF 766–804).

## 논문과 후행 prototype 연결

다음은 원문에서 도출한 **제안**이며 승인된 protocol 변경이나 구현 완료가 아니다.

1. B/C/G에서 evidence representation 효과를 보려면 검색 scheduler와 trial 권리를 공통으로 두거나, 바꾸는 경우 전체 package 효과라고 명시한다. 이 paper의 search tree는 scholarly evidence/dependency graph와 동일하지 않다.
2. 단일 locked artifact의 hidden MAE를 주 outcome으로 유지한다. Dev 단계 anytime 곡선과 비용·무산출물/UNKNOWN을 보조 관측으로 미리 정의한다. Reward 변환과 정규화가 필요하면 outcome을 보고 정하지 않는다.
3. Prototype 설계에서 실행 완료 record를 scheduler 관측으로 제공하고, graph는 근거·적용성·버전 관계를 별도로 보존하는 연결을 후보로 둔다. 그래프 크기나 생성 문서 수는 진척 reward가 아니다.
4. Greedy·beam·tree·population·adaptive allocation은 비교 가능한 대안 목록이다. 모든 대안을 필수 arm으로 추가하거나 현재 P0를 교체할 근거는 없다.

**재사용 금지:** 이 논문의 crash repair는 UNKNOWN 외부 run 재시작을 정당화하지 않는다. Seed·chain·context를 독립 과제로 늘려 세지 않는다. Preprint 수치나 단일 completion 연구를 장기 연구·hidden custody·source recovery의 실증으로 승격하지 않는다.

## Provenance

- Text SHA-256: `c5d3f2f9ce91d5c76b7eda74e133a56860fdcb2edcaf97dea5f1a20bfcc59020`; 53326 bytes; LF 1061.
- Read ranges: 1–230, 231–460, 461–730, 731–940, 941–1061.
- ORX receipt exit 0, bytes/hash 일치. Receipt SHA-256: `3ae981b366e9c203a1c12e64204135b716d4ca97784dad35b743e2535213f1b8`.
- 기계 판독 claim/locator와 비교 불가 범위: `efficiency-review.json`.
