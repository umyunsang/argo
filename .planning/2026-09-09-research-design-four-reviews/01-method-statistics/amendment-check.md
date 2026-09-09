# 통계 수정안의 좁은 추가 검토

판정: **6가지 배정과 Neyman 분산식은 맞다. 그러나 제안된 t CI는 확증 평균효과·MUE 판정용으로 아직 타당하지 않다.** 원검토와 v1을 수정하지 않았으며 다른 reviewer 결과를 읽지 않았다. 원문 추가 검색·모델 실행 없이 아래 6가지 수치 배정만 계산했다.

## 1. AM-01 · HIGH · Vhat=0일 때만 fallback하면 큰 undercoverage가 남는다

Neyman 추정량은 **기대값에서 보수적**이다. 각 관측 Vhat가 실제 분산보다 크다는 뜻은 아니다. 2개 관측으로 구한 arm 분산과 Satterthwaite df에 근사 t를 붙여도 유한표본 coverage가 확보되지 않는다.

정확한 반례: 19개 task에서는 네 slot 모두 양 arm의 잠재 결과가 0.5다. 마지막 task의 네 slot은 양 arm 모두 `[0, 0.001, 0.999, 1]`이다. 모든 개별 처치효과가 0이므로 평균효과뿐 아니라 Fisher sharp null도 참이다.

| R에 배정된 slot | 평균효과 추정량 | Vhat | t 구간이 0 포함 |
|---|---:|---:|---|
| 1, 2 | −0.04995 | 1.25e−9 | 아니오 |
| 1, 3 | −0.00005 | 0.00124750125 | 예 |
| 1, 4 | 0 | 0.0012475025 | 예 |
| 2, 3 | 0 | 0.0012475025 | 예 |
| 2, 4 | +0.00005 | 0.00124750125 | 예 |
| 3, 4 | +0.04995 | 1.25e−9 | 아니오 |

극단 두 배정의 df는 2, t 임계값은 4.3026527297, 구간 반폭은 0.0001521217461이다. Vhat는 양수여서 fallback이 전혀 작동하지 않는다. 따라서 이 예에서 95% 구간의 실제 coverage는 **4/6=66.7%**, CI만으로 +0.02 우위를 판정할 때 거짓 양성 지지는 **1/6=16.7%**다. 이 예의 Fisher 양측 p는 1/3이므로 Fisher 검정 자체의 실패를 보인 것은 아니다.

가장 단순한 수정은 t 구간을 명시적인 기술적 근사로 남기고, 확증 평균효과/MUE 판정은 아래 bounded interval을 **모든 complete 자료에** 적용하는 것이다. 또는 Fisher sharp-null만 확증하고 평균/MUE는 근사적·비확증 결과로 보고한다. 임의의 작은 Vhat threshold 추가는 해결 근거가 아니다.

## 2. 필요한 평균효과 명세와 간단한 타당 대안

네 slot의 identity와 자원·시간 상태를 배정 전에 고정한다. task별 6가지 배정은 독립이며, 한 slot의 결과가 다른 slot의 arm 배정에 따라 바뀌지 않아야 한다. fresh context만으로 이 no-interference 가정이 증명되지는 않는다. 모든 primary U가 관측되고 [0,1]에 있어야 하며 unknown에 대한 기존 규칙은 유지한다.

T=20, i=1,...,4에 대해

\[
\tau=\frac{1}{4T}\sum_{t,i}\{Y_{ti}(R)-Y_{ti}(B)\},\qquad
\widehat\Delta=\frac1T\sum_t D_t.
\]

S는 네 잠재 결과의 유한모집단 표본분산(분모 3), s는 배정된 두 결과의 표본분산(분모 1)으로 정의한다.

\[
\operatorname{Var}(\widehat\Delta)=\frac1{T^2}\sum_t
\left(\frac{S_{Rt}^2}{2}+\frac{S_{Bt}^2}{2}-\frac{S_{\tau,t}^2}{4}\right),\quad
E[\widehat V]-\operatorname{Var}(\widehat\Delta)
=\frac1{4T^2}\sum_tS_{\tau,t}^2\ge0.
\]

독립 task 배정과 D_t∈[−1,1]을 이용한 Hoeffding 구간은 다음과 같다. T=20, α=.05에서 h=0.60736146으로 매우 넓으며, lower>.02에는 관측 Δ>0.62736146이 필요하다. 이는 설계의 실제 정밀도 제한이며 근사 구간의 이름을 바꿔 숨길 수 없다.

\[
\Pr(|\widehat\Delta-\tau|\ge h)\le2\exp(-Th^2/2),\qquad
h=\sqrt{\frac2T\log\frac2\alpha},\qquad
C_H=[\max(-1,\widehat\Delta-h),\min(1,\widehat\Delta+h)].
\]

## 3. Fisher MC는 유지하고 statistic·동률·귀무가설을 고정하면 된다

99,999개 MC 반복마다 각 task의 6가지 배정을 독립 균등 추출하며 반복 간에는 복원 추출한다. seed뿐 아니라 PRNG 구현도 기록한다. observed U를 고정한 sharp-null 재배정을 사용한다. 평균 차이의 절댓값을 양측 statistic으로 쓰고 동률을 포함한다. 이는 6^20 exhaustive 계산이나 weak mean-null의 exact 검정이 아니다. 이 수정안의 Fisher 절차에서는 별도 수학적 오류를 찾지 못했다.

\[
H_{0,\mathrm{sharp}}:Y_{ti}(R)=Y_{ti}(B)\ \forall t,i,\qquad
S_b=|\widehat\Delta(Z_b)|,\qquad
p_{MC}=\frac{1+\sum_{b=1}^{99999}\mathbf1[S_b\ge |\widehat\Delta_{obs}|]}{100000}.
\]
