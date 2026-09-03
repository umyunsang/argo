# Study B Analysis Specification v4a (T3 N=40)

작성 시각: 2026-09-03T20:11:30+09:00
사전등록 참조: `paper/research/study-b-preregistration-v4.md` (sha256 `0325ce9fb92f9f98c339665e4cfccc401283c1fd89b64f090990df9f64ad8147`, seal_commit `5d9c0d088`)

**공개 고지:**
본 분석 사양은 T3 seed 0..11의 실행 완료 및 각 트리플별 단순 통과 수(cost-ledger 기록)가 가시화된 이후에 작성되었다.
사전등록 v4는 쌍대 Wilcoxon 검정을 주 분석으로 명시하였으나, 동점(쌍 차이 0) 처리 방식을 구체화하지 않았다.
본 사양을 확정하는 과정에서 특정 처리 방식(pratt vs wilcox 등)이 가시화된 데이터에 유리한지 여부는 사전에 **계산하지 않았고 계산하지 않는다**. 사양은 통계학적 보수성과 선행 합의에 근거하여 사전에 동결된다.

---

## 1. 1차 가설 검정 (Primary Hypothesis Test)
- **비교 대상:** B2 vs B0 (항목 수준 통과 비율 `item_pass_fraction`, 0.0 ~ 1.0)
- **검정 방법:** 대응표본 Wilcoxon 부호순위 검정 (Paired Wilcoxon Signed-Rank Test)
- **동점(쌍 차이 0) 처리:** `zero_method='pratt'`
  - 사유: Pratt(1959) 방식은 차이가 0인 쌍을 전체 순위 산정에 포함한 뒤 0인 순위를 검정 통계량에서 제외하는 방식으로, 0 차이를 표본에서 완전히 배제하여 표본 크기를 인위적으로 줄이는 Wilcoxon(1945) 방식 대비 보수적 검정을 제공함.
- **방향:** 양측 검정 (`alternative='two-sided'`), 유의수준 alpha = 0.05
- **구현 환경:** Python `scipy.stats.wilcoxon` (scipy version 1.17.1, numpy version 2.4.6 고정)

## 2. 2차 가설 검정 (Secondary Hypothesis Tests)
- **비교 대상:** B2 vs B1, B1 vs B0
- **동일 사양 적용:** `scipy.stats.wilcoxon(..., zero_method='pratt', alternative='two-sided')`
- **다중비교 보정:** Holm-Bonferroni 단계적 보정 (가족 유의수준 alpha = 0.05)

## 3. 민감도 검정 (Sensitivity Analyses)
1차 및 2차 검정 결과의 강건성을 검증하기 위해 다음 세 가지 대안 검정을 함께 실행하고 보고한다:
1. `zero_method='wilcox'`: 0 차이 쌍을 순위화 전 표본에서 완전히 배제하는 표준 방식.
2. **정확 부호검정 (Exact Sign Test):** 순위 크기를 배제하고 양수/음수 차이 부호 빈도만을 이항분포(p=0.5)로 검정.
3. **쌍대 순열검정 (Paired Permutation Test):** 
   - 10,000회 무작위 부호 반전 순열.
   - 재현성 보장 시드: `random_state = 20260903` 고정.

## 4. 효과크기 및 기술통계 (Effect Sizes & Descriptive Statistics)
- **평균 쌍 차이:** mean_d = sum(score_B2 - score_B0) / N (통과 비율 단위, -1.0 ~ +1.0)
- **부트스트랩 95% 신뢰구간:**
  - 10,000회 백분위수 부트스트랩 (대응표본 단위 리샘플링).
  - 난수 시드: `random_state = 20260903` 고정.
- **보고 필수 요약 통계:**
  - 각 아암별 평균 통과율 및 표준편차.
  - 동점 쌍 수 (차이 0인 시드 수).
  - 천장 효과(Ceiling Effect) 지표: 세 아암이 모두 5/5(1.0)를 기록한 시드 수.

## 5. 분석 실행 및 결과물
- 실행 스크립트: `experiments/study_b/analyze_block.py`
- 산출물: `paper/experiments/study-b-analysis-receipt.json` (receipt schema, origin='verifier')
- 원고 및 status.md의 결과 보고는 반드시 위 단일 분석 receipt로부터만 전사된다.
