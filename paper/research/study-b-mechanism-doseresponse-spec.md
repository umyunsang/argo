# Study B 기제별 용량-반응 2차 분석 사양 (Dose-Response Specification)

- **작성 시각:** 2026-09-04T12:00:00+09:00
- **권한:** supervisor instruction-0020 §3 (T1′ 확증 데이터 관측 전 사전등록 봉인)
- **분석 유형:** 관찰적 2차 분석 (Observational Secondary Analysis, 비인과적 상관/용량-반응 모형)
- **사전등록 참조:** `paper/research/study-b-preregistration-v4.md`, `paper/research/study-b-t1t2-addendum.md` (v3)

---

## 1. 분석 목적 및 성격 규정

- **목적:** B2 복합 하네스 내부의 5대 기제(context graph, decision protocol, threshold/falsification loop, result-driven search, fail-closed lifecycle)가 단일 아암으로 일괄 투입되어 개별 기제의 효과 귀속이 불가능한 한계를 극복하기 위해, 에피소드 내부에서 실측된 각 기제의 작동 강도(intensity / dosage) 변수를 활용하여 종점과의 용량-반응 관계를 2차 분석한다.
- **인과적 한계 명시:** 본 분석은 기제가 무작위 배정된 실험(experimental arm)이 아니며, 에이전트의 자율적 도구 호출 빈도에 의존하는 **관찰적 분석(observational analysis)**이다. 따라서 도출되는 통계량은 기제 사용 강도와 성과 간의 연관성(association)만을 나타내며, 엄밀한 인과적 효과(causal attribution)로 해석될 수 없음을 사전에 확정한다.

## 2. 변수 정의

### 2.1 결과 변수 (Dependent Variable)
- **T1′ 종점:** 3수준 순서형 점수 $Y \in \{0, 1, 2\}$
  - 0 = 미생성 또는 실행 충돌
  - 1 = 유효 실행·결과 오답 (도메인 기준 미달)
  - 2 = 도메인 기준 충족 (과제 성공)
- **T3 종점 (탐색적 전용):** 검증기 통과 항목 비율 $Y_{T3} \in [0.0, 1.0]$ (5개 항목 통과 수 / 5). 단, B2 평균 0.96의 만점 천장 효과로 인해 본 사양의 주 검정 대상이 아니며 탐색적(exploratory)으로만 보고한다.

### 2.2 설명 변수 (Independent Variables / Mechanism Dosages)
에피소드 종료 후 `manipulation_log.json`에서 추출되는 기제별 강도 계측치 5종:
1. $X_{\text{graph}}$: `graph_nodes_added` (타입드 컨텍스트 노드 추가 수, 정수형 $\ge 0$)
2. $X_{\text{decision}}$: `decisions_recorded` (사전 등록된 6필드 결정 레코드 수, 정수형 $\ge 0$)
3. $X_{\text{threshold}}$: `thresholds_registered` (사전 등록된 가설/성능 임계값 수, 정수형 $\ge 0$)
4. $X_{\text{gate}}$: `gate_blocks` (게이트 미충족으로 차단된 도구 호출 시도 수, 정수형 $\ge 0$)
5. $X_{\text{pivot}}$: `pivots` (가설 반증 판정 후 발생한 방향 전환 수, 정수형 $\ge 0$)

## 3. 통계 모형 및 검정 절차

### 3.1 1차 모형 (Primary Model for T1′)
- **모형:** 시드(seed)를 층화 블록으로 고려한 **순서형 로지스틱 회귀 (Ordinal Logistic Regression / Proportional Odds Model)** 및 설명변수별 **순위 상관 분석 (Spearman rank correlation)**.
- **순열 검정 (Permutation Test):** 표본 크기가 작거나 비정규성이 강한 경우, 시드 블록 내에서 기제 강도 $X$를 무작위 치환(10,000회 순열)하여 경험적 p-값을 도출한다.
- **방향 가설 (One-tailed Directional Hypotheses):**
  - $H_{1\text{a}}$ (Graph): $X_{\text{graph}}$ 증가는 순서형 점수 $Y$와 양의 상관을 가질 것이다 ($ho > 0$).
  - $H_{1\text{b}}$ (Decision): $X_{\text{decision}}$ 증가는 $Y$와 양의 상관을 가질 것이다 ($ho > 0$).
  - $H_{1\text{c}}$ (Threshold): $X_{\text{threshold}}$ 증가는 $Y$와 양의 상관을 가질 것이다 ($ho > 0$).
  - $H_{1\text{d}}$ (Gate): $X_{\text{gate}}$ 증가는 게이트 위반 시도로서 $Y$와 음의 상관을 가질 것이다 ($ho < 0$).
  - $H_{1\text{e}}$ (Pivot): $X_{\text{pivot}}$ 증가는 오류 수정 노력을 반영하여 $Y$와 양의 상관을 가질 것이다 ($ho > 0$).

### 3.2 다중 비교 보정 (Multiple Comparison Correction)
- 5개 기제 설명변수에 대한 유의성 검정에 대해 **Holm-Bonferroni 보정**을 적용하여 패밀리 단위 오류율(FWER)을 양측 $lpha = 0.05$ 수준에서 통제한다.

### 3.3 결측 및 영분산(Zero-Variance) 처리 규칙
- 만약 특정 기제(예: $X_{\text{pivot}}$)의 관측값이 전체 에피소드에서 동일(분산 0, 예: 전부 0)하여 변동이 없을 경우:
  - 해당 기제에 대한 회귀 계수 및 상관계수 산출을 시도하지 않고 검정 대상에서 즉시 제외한다.
  - 이를 "기제 미발화(Unfired Mechanism / Invariant Zero)"로 분류하고, 해당 기제가 해당 과제군 난이도 또는 하네스 조건에서 실질적으로 작동하지 않았음을 수치(variance = 0.0, rate = 0/N)와 함께 가감 없이 보고한다.
