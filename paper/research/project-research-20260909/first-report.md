# 첫 실행 보고

실제 공개 자료·수치 문제에서 세 분야 기준선과 첫 가설 시험을 시작했다. 이는 **개발 연구 측정**이다. 자율 B/P 캠페인12개, AAA, 독립 최종 평가와 PI 완료 판정은 별도이며 아직 완료되지 않았다. Native ARGO 건설 중지는 유지한다.

| 분야 | 관측 | 현재 해석 |
|---|---|---|
| Wine | pooled ExtraTrees 0.520788, 색상별 ExtraTrees 0.520226 동일가중 MAE | 차이가 작음. 한 개발 분할의 우위·일반화는 미확정 |
| DuckDB | 준비 비용 포함 74.15% 감소, 대응 bootstrap95%구간 68.71–77.34%, 20쌍 | 질의 답 동등. 개발 Q1 재구성 범위; 최종 목표 달성은 미확정 |
| 이방성 확산 | 8개 개발 설정, 세 해법 정확성 통과. AMG 총비용은 가장 빠른 기준선의 1.99–5.47배 | 이번 크기·우변 수에서 AMG 이점 없음. 더 넓은 범위 일반화는 하지 않음 |

Wine은 새 ORX 프로세스에서 같은 데이터·seed로 재학습했고 세 방법의 예측 파일 해시가 일치했다. 이 재현은 새 독립 데이터 표본이 아니다. 모든 자료의 중복 입력 그룹을 분할 간 격리했고, 최종·후속 자료는 작업 컨테이너에 마운트하지 않았다.

## 자율 캠페인 세션

아래는 에이전트가 스스로 질문·방법·실험을 정해 제출한 후보다. **품질(AAA)·우위·PI 판정은 모두 미정**이며, 제출 자체는 완료 판정이 아니다. 모델 요청은 기존 구독의 포함 사용량 전후 관측으로 추가 과금0원을 확인했다.

| 캠페인 | 팀/모델 | 모델 요청 | 토큰 | 추가 과금 | ORX 실행 | 상태 |
|---|---|---|---|---|---|---|
| first_week-wine-B-normal | free / anthropic/claude-sonnet-4-6 | 15 | 462,755 | 0원 | ac1771a8 FAILED, 550773ff EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | supervisor / anthropic/claude-sonnet-4-6 | 31 | 2,159,815 | 0원 | 없음 | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-1 / anthropic/claude-sonnet-4-6 | 17 | 847,846 | 0원 | 0c317c9e EXECUTED_UNVALIDATED, dc13a80d FAILED, 4dcef095 EXECUTED_UNVALIDATED, 79af4add EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-1 / anthropic/claude-sonnet-4-6 | 14 | 1,016,421 | 0원 | 0c317c9e EXECUTED_UNVALIDATED, dc13a80d FAILED, 4dcef095 EXECUTED_UNVALIDATED, 79af4add EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-1 / anthropic/claude-sonnet-4-6 | 13 | 345,277 | 0원 | 0c317c9e EXECUTED_UNVALIDATED, dc13a80d FAILED, 4dcef095 EXECUTED_UNVALIDATED, 79af4add EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-2 / anthropic/claude-sonnet-4-6 | 15 | 753,797 | 0원 | 7020511e EXECUTED_UNVALIDATED, 16a6157e EXECUTED_UNVALIDATED, 89d7b721 EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-2 / anthropic/claude-sonnet-4-6 | 18 | 1,343,944 | 0원 | 7020511e EXECUTED_UNVALIDATED, 16a6157e EXECUTED_UNVALIDATED, 89d7b721 EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |
| first_week-wine-P-normal | team-2 / anthropic/claude-sonnet-4-6 | 16 | 445,615 | 0원 | 7020511e EXECUTED_UNVALIDATED, 16a6157e EXECUTED_UNVALIDATED, 89d7b721 EXECUTED_UNVALIDATED | CANDIDATE_SUBMITTED / AAA UNASSESSED / PI PENDING |

**first_week-wine-B-normal 후보 주장** (에이전트 작성, 미검증):

- Color-specific GBM achieves equal-weight dev MAE=0.5183 vs. unified GBM MAE=0.5245, delta=+0.0063 (1.2% relative improvement), confirming that color-stratified modeling outperforms a unified model on this wine quality dataset under group-isolated evaluation [ORX run_id=550773ff, receipt_sha256=f7007055e1e26131321fb2b26d434493abfa7811cbe35b93b28c93b21b32615d]
- The wine dataset group_id structure encodes unique (feature_vector, quality) pairs: 100% feature consistency within groups, zero quality variance within groups, 682 duplicate rows in 3,872 train samples, and zero train-dev group overlap — requiring GroupKFold by group_id to prevent CV contamination [same ORX receipt]
- Feature importance differs meaningfully by wine color: sulphates are rank-2 for red wine (importance=0.138) but rank-11 for white (0.043); free SO2 is rank-3 for white wine (0.125) but rank-11 for red (0.035); alcohol is the top predictor for both colors [same ORX receipt]
- A unified GBM model assigns color indicator importance of only 0.00251 (lowest of 12 features), indicating it fails to adequately capture color-conditional feature relationships, explaining why separate color-specific models yield better predictions [same ORX receipt]

에이전트가 스스로 밝힌 한계:

- Only one model class (GBM with fixed hyperparameters) was tested; other model classes (Random Forest, ridge regression, neural networks) were not compared and may show different relative performance
- The performance delta (0.0063 EW-MAE) is modest; bootstrapped confidence intervals were not computed, so statistical significance of the advantage is not established
- GBM hyperparameters were not tuned separately for red vs. white models; tuning could change the relative gap between approaches
- The EXECUTED_UNVALIDATED status means the ORX run completed in isolation; this is development-scope evidence, not final evaluation
- The 3:1 white-to-red imbalance in both train and dev means red wine predictions are based on smaller training sets; the red-wine benefit may partially reflect reduced training interference rather than pure color-specific signal
- Dev set is fixed (not held-out test); final evaluation uses independent scoring criteria and hidden data

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- Candidate-f4bade713c3fef5821e03fbc is selected as the branch to continue. All 6 dimensions PASS with cited artifact evidence. No Critical or Major findings. Independent reproduction receipt artifact-4ec5fddc2d4d2959fe4f715a (status: PASS) confirms 8/8 checks at 4-decimal-place precision.
- Candidate-9ad042eee483f9e98d7b6c5f is not selected due to one unresolved Major finding (F-A1): the H2 leakage magnitude claim '16–17% bias' cannot be reproduced with available code (experiment.py SHA256=e3b0c44 empty); the reproduction using KFold(shuffle=True) finds only 5.0% bias; the specific protocol is unknown.
- Both candidates find the same direction: unified GBM matches or outperforms color-stratified models on equal-weight MAE (GroupKFold-isolated); color as a feature contributes negligibly to individual predictions but joint training benefits from larger effective training data.
- Candidate-f4bade713c3fef5821e03fbc uniquely confirms an applicable prediction range: quality scores 5–7 yield MAE 0.37–0.69 for both colors (covering 93.9% red and 90.9% white dev), while extreme scores (3–4 or 8–9) yield MAE>1.0 due to training data sparsity.
- Spearman rho=0.236 between red/white wine feature importance rankings is independently verified from artifact-6abbad080c9f542dec3e73d8.json feature data (computed rho=0.236 exactly), confirming substantial divergence in physicochemical quality determinants.
- EW-MAE correctness verified for all reported model comparisons in both candidates: all match 0.5*(MAE_red + MAE_white) to floating-point precision (<1e-9 error).

에이전트가 스스로 밝힌 한계:

- This review is same-team blinded only (scope field in both reproduction receipts confirms 'Same-team fresh-session rerun'). Cross-team or external replication was not performed.
- The supervisor has no experiment tool; all numerical checks are performed analytically from artifact data. Code review is not possible — only outputs are inspectable.
- Feature importances in both candidates are sklearn split-count-based (not SHAP or permutation importance); relative magnitudes are indicative orderings, not precise effect sizes.
- The H4 INCONCLUSIVE result in candidate-f4bade713c3fef5821e03fbc means the effect of explicit color-by-physicochemical interaction features remains unresolved; a larger dev set (or multiple splits) would be needed to resolve the CV/dev directional conflict.
- LightGBM was unavailable in the ORX science container for all three runs in candidate-f4bade713c3fef5821e03fbc; absolute MAE values and the magnitude of the unified vs stratified gap may differ under LightGBM, though qualitative conclusions are expected to generalize within the GBM model family.
- All results use a single train/dev split and single or no explicit random seed variation; ranking differences of 0.001–0.005 EW-MAE across models should be treated as exploratory pending bootstrap or multi-seed validation.

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- REPRODUCED: Research baseline verified — GBT-default with binary color feature achieves dev EW-MAE=0.5217 (receipts: research sha256=ed15f69d0acbd23f316250d61f2b9bafaf0fc0c8fc1854c6c68fb3b87ea5f6d1, experiment sha256=c22a0a45ddd70574ba2c2c48dca6118f371662d7ad1203c4d1e1a69da3d9e287)
- FALSIFIED H3: Tuned GBT (n=500, lr=0.03, d=5, sub=0.8, min_leaf=5) achieves dev EW-MAE=0.5191, improvement=0.0026 over research best — below 0.005 threshold; source: result.json hypothesis_verdicts.H3_gbt_tuned_vs_research_best
- BORDERLINE FALSIFIED H4: 3-model ensemble (GBT-default + GBT-tuned + RF) achieves dev EW-MAE=0.5167, improvement=0.004965, group-CV=0.5206; improvement is 0.000035 below the 0.005 threshold and within sampling variability on n=1300; source: result.json hypothesis_verdicts.H4_ensemble_vs_research_best
- FALSIFIED H5: Color×physicochemical interaction features (color×sulphates, color×free_SO2, color×alcohol, color×volatile_acidity) worsen white wine dev MAE by 0.0012 (0.5651→0.5663) vs tuned GBT without interactions; source: result.json hypothesis_verdicts.H5_interactions_reduce_white_mae
- CONFIRMED from research (reproduced): naive 5-fold KFold EW-MAE 0.437-0.440 vs group-isolated GroupKFold EW-MAE 0.524-0.527 — 16-17% optimistic bias attributable to group_id leakage; source: checkpoint-f97d9e67b5674f5dac9c03ca124f0dfb confirmed_decisions
- CONFIRMED from research (reproduced): white wine consistently harder to predict than red — experiment best model white=0.566, red=0.468, gap=0.098; consistent with research finding 0.080-0.107 across all models; source: result.json color_difficulty_analysis
- CONFIRMED from research (reproduced): binary color feature contributes only 0.0014 (0.14%) importance in unified GBT; physicochemical features implicitly encode wine color with sufficient predictive fidelity; source: result.json feature_importances_gbt_tuned_with_color.color_enc=0.0014
- PRESERVED FAILURE: Experiment v1 run_id=dc13a80d receipt_sha256=f3f3ce985edcc84a88326e2c27efea357cea4be36e6d57642a0aae943ec20cba failed (exit_code=1) due to hardcoded underscore column names; actual dataset uses space-delimited multi-word feature names ('fixed acidity', 'volatile acidity', etc.)

에이전트가 스스로 밝힌 한계:

- H4 ensemble improvement (0.004965) is 0.000035 below the 0.005 threshold — given n=1300 dev samples, this is within sampling variability; a single different split could flip the verdict; statistical significance of the 0.005 improvement is not established
- All experiments use a single fixed random seed (42) and a single train/dev split; variance across seeds or bootstrap dev splits was not assessed; model ranking at differences of 0.001-0.005 EW-MAE should be treated as exploratory
- Dev/train group overlap was not verified; if any group_ids appear in both train and dev, the dev evaluation may be slightly optimistic, particularly for GBT whose group-CV (0.5293) is notably worse than dev (0.5217) while RF group-CV closely tracks dev
- No hyperparameter search beyond two GBT configurations was tested; deeper tuning or other learner classes (XGBoost, LightGBM, neural networks) were not tested due to resource constraints and library availability in the ORX environment
- The H5 null result on interaction features may be specific to GBT learners which can discover interactions internally; RF-based or linear models may benefit differently from explicit interaction terms
- White wine difficulty gap (0.09) persists across all model types and strategies tested; the cause (distributional characteristics, label noise, feature informativeness) was not investigated
- Research session experiment.py was not preserved in the handoff (inbox experiment.py is empty, SHA256=e3b0c44); reproduction relies on matching research session result.json outputs, not on inspecting the original code

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- REPRODUCED: GBT baseline dev EW-MAE=0.52168 matches experiment session to 5 decimal places (reproduction run_id=79af4add, receipt=a0a771eedc023edce734c200e891860a115ecebbb7f3221e77a7e555ede537e2)
- REPRODUCED: All 5 key metrics within ±0.0005 tolerance — GBT 0.52168, RF 0.52308, H3 0.51913, H4 0.51673, H5 white MAE change −0.00121
- CONFIRMED H1 FALSIFIED: GBT-with-color (0.52168) < RF-no-color (0.52308) reproduced — color-specific modeling is counterproductive
- CONFIRMED H3 FALSIFIED: tuned GBT improvement = 0.00257 < 0.005 threshold, reproduced from experiment
- CONFIRMED H4 BORDERLINE FALSIFIED: ensemble improvement = 0.004965 < 0.005, 0.000035 below threshold, reproduced from experiment
- CONFIRMED H5 FALSIFIED: interaction features worsen white wine MAE by 0.00121, reproduced from experiment
- RESOLVED R3: Dev/train group overlap = 0 — 3190 train groups and 1064 dev groups are completely disjoint; dev score is fully isolated
- CONFIRMED R2: Ensemble best (0.5167) outperforms mean predictor (0.6928) by 34.1% relative — results substantially non-trivial
- DISCREPANCY H2: Reproduction finds 5.0% leakage (shuffled KFold) vs research's 16–17%; direction confirmed, magnitude cannot be reproduced without original experiment.py (SHA256=e3b0c44, empty in handoff)
- ESTABLISHED DATA PROVENANCE: train SHA256=ceb6a556..., dev SHA256=06df0fb7..., ORX image SHA256=3333b0fb...
- CONFIRMED WHITE HARDER THAN RED: ensemble white MAE=0.566, red MAE=0.468, gap=0.098 across all reproduced models and splits
- CONFIRMED FEATURE IMPORTANCE: alcohol=0.288, volatile_acidity=0.137, color_enc=0.0014 — physicochemical features dominate; color is near-irrelevant (0.14%)

에이전트가 스스로 밝힌 한계:

- H2 leakage magnitude (5.0% in reproduction vs 16–17% in research) cannot be reconciled without the original experiment.py — empty in handoff (SHA256=e3b0c44); the 16–17% figure is unverified and may depend on KFold shuffle=False with specific row ordering
- H4 ensemble improvement of 0.004965 is 0.000035 below the 0.005 material threshold; at n=1300 dev samples this margin is within sampling variability and the verdict (BORDERLINE FALSIFIED) could flip with a different dev split
- All experiments use a single random seed (42) and a single train/dev split; no bootstrap variance estimate was produced; differences of 0.001–0.003 EW-MAE should be treated as exploratory
- The reproduction CV measure of 5% leakage uses KFold(shuffle=True) while research used an unknown protocol; the true leakage magnitude may be larger under specific data orderings
- No hyperparameter search beyond two GBT configurations was tested; XGBoost, LightGBM, and neural networks were not assessed due to library availability constraints in the ORX environment
- White wine difficulty gap (0.095–0.107) is confirmed but unexplained — distributional characteristics, label noise, or feature informativeness differences were not investigated
- The 'EXECUTED_UNVALIDATED' status indicates code completed in isolation but scientific claims remain subject to independent scientific review; no PI acceptance has been granted

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- FALSIFIED: Color-specific Random Forest models do not achieve lower equal-weight MAE than unified models; color-specific RF dev EW-MAE=0.5255 vs unified RF=0.5231 (source: ORX receipt sha256=ed15f69d0acbd23f316250d61f2b9bafaf0fc0c8fc1854c6c68fb3b87ea5f6d1, result.json dev_ew_mae_ranking)
- CONFIRMED: Naive 5-fold CV without group isolation overestimates performance by 0.084-0.089 MAE units (16-17% bias) for all tested models; naive CV EW-MAE 0.437-0.440 vs group-isolated CV 0.524-0.527 (source: same receipt, result.json model_results.*.leakage_delta)
- Color as a binary feature in a unified RF contributes 0.13% feature importance; physicochemical features implicitly encode wine color with sufficient fidelity for prediction purposes (source: receipt result.json feature_importances.unified_with_color.color_enc=0.0013)
- Feature importance differs between wine colors: sulphates importance for red=0.135 vs white=0.062 (2.2x); free sulfur dioxide for white=0.117 vs red=0.046 (2.5x); alcohol is the dominant predictor for both colors at 0.28 and 0.25 respectively (source: receipt result.json feature_importances)
- White wine quality is consistently harder to predict than red wine across all models and evaluation protocols: dev MAE white-red gap ranges from +0.080 (color-specific RF) to +0.107 (GBT with color); this gap is meaningful under the equal-weight evaluation criterion (source: receipt result.json model_results.*.dev_mae_by_color)
- Best observed dev EW-MAE is 0.5217 from GBT with color feature (unified, default hyperparameters), but the margin over the next best (unified RF, 0.5231) is 0.0014, within sampling variability on n=1300 dev samples

에이전트가 스스로 밝힌 한계:

- Model ranking margins between unified models are small (<0.004 MAE on n=1300 dev samples) and within expected sampling variability; statistical significance of pairwise model differences is not established
- Whether dev.csv group_ids overlap with train group_ids was not verified; if overlap exists, dev evaluation may also be mildly optimistic, particularly for the GBT model whose dev score (0.5217) is better than its group-CV score (0.5293) while RF group-CV closely tracks dev
- No hyperparameter tuning was performed; off-the-shelf RF(n=200) and GBT(n=200, lr=0.05, depth=4) defaults used; tuned color-specific models might narrow the gap
- Feature importances are RF-specific (MDI/mean decrease impurity); SHAP values or permutation importance on GBT may show different relative rankings
- Negative result on H1 (color-specific vs unified) is established for the Random Forest learner class; it does not rule out benefits for other architectures (gradient boosting, neural networks, or heavily feature-engineered models) that exploit color-conditional statistics differently
- Only one ORX experiment was run (single seed, single train/dev split); variance across seeds or alternative data splits was not assessed

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- H1 NEGATIVE (ORX 16a6157e + 7020511e): 색별 분리 GBM이 통합 GBM을 이기지 못한다. 통합 CV EW-MAE=0.5305 vs 분리 CV=0.5436(−2.5%); Dev 동점(0.5261 vs 0.5267). 근거: run_id=7020511e receipt_sha256=8cf6c56f4cb7efdef9cec4a7aad534068ca6af6b8fe65e6e0533666be440ad6d(research phase) + 실험 단계 재현 run_id=16a6157e receipt_sha256=31453ca90cb87aa33e057c77065053423b1174e8cee895b5179f40e3e776e336(실험 단계 기준선 CV=0.5305, Dev=0.5261 정확 재현).
- H2 POSITIVE: 색별 이화학적 품질 결정인자가 실질적으로 다르다(Spearman ρ=0.236 on 11-feature rankings). 황산염: 적 #2(13.2%) vs 백 #9(5.5%); 자유 SO₂: 백 #3(12.3%) vs 적 #11(4.7%); 알코올: 양색 공통 #1(~27-28%). 근거: run_id=7020511e 색별 분리 모델 특성 중요도 필드.
- H3 POSITIVE (독립 재확인): 신뢰 예측 범위=품질 5–7 (MAE 0.37–0.69 양색); 극값(3–4 또는 8–9)은 MAE>1.0으로 비신뢰. 근거: run_id=16a6157e quality_score_error 필드 — 적 q=5 MAE=0.371, q=6 MAE=0.449, q=7 MAE=0.610; 백 q=5 MAE=0.541, q=6 MAE=0.380, q=7 MAE=0.688.
- H4 INCONCLUSIVE: 색×이화학 명시적 상호작용 항(11개)의 효과는 CV와 Dev 간 불일치(CV: +0.0005 기준선 우세; Dev: −0.0037 상호작용 우세). 상호작용 항 합산 중요도 7.8%로 GBM 묵시적 처리 가능 해석. 확정적 결론 불가. 근거: run_id=16a6157e h4_result 필드.
- BACKEND CONSTRAINT: 양 ORX 실행 모두 LightGBM 미탑재로 sklearn GBM 폴백. 절대 MAE값은 백엔드 의존; 질적 결론(통합≈분리, 색별 특성 다양, 품질 5–7 신뢰) 강건 예상.

에이전트가 스스로 밝힌 한계:

- LightGBM 미탑재(양 ORX 실행): sklearn GBM(n_estimators=300) 폴백 사용. LightGBM 시 절대 MAE 이동 가능; 통합 vs 분리 격차 크기 변동 가능 (방향 변화는 미예상).
- H4 불확실: CV(5-fold GroupKFold, 더 신뢰)와 Dev(n=1,300, 소규모) 결과 불일치. Dev의 −0.0037 이득은 노이즈 범위. 더 큰 데이터셋에서의 재검증 필요.
- 극값 품질 분석 고분산: Dev q=3(n=7 합계), q=9(n=1) — 극값 경계 MAE 추정치 신뢰구간 넓음.
- 특성 중요도 한계: sklearn GBM split-count 기반(gain/SHAP 아님). 상대적 크기 비교는 순위 수준 신뢰에 한정.
- 하이퍼파라미터 탐색 없음: 단일 기본값 조합. 조정 시 통합/분리 격차 또는 상호작용 효과 변동 가능.
- Dev 세트 크기 불균형: 적 n=294, 백 n=1,006 — 적 MAE 추정치의 표준오차가 백보다 ~1.8배 크다.

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- REPRODUCTION CONFIRMED (run_id=89d7b721, receipt_sha256=4deae6ac...): 8/8 재현 검사 통과. 기준선 CV EW-MAE=0.5305 (실험 단계 일치), Dev=0.5261 (일치); 상호작용 CV=0.5310, Dev=0.5224. 4자리 소수점 정확도로 재현. 불일치 없음.
- H1 NEGATIVE (3개 ORX 실행 공통): 색별 분리 GBM이 통합 GBM을 이기지 못한다. 통합 CV EW-MAE=0.5305 vs 분리 CV=0.5436 (2.5% 차이); Dev는 동점(0.5261 vs 0.5267, 차이=0.0006). 통합 훈련 데이터 효과(3×)가 색별 분리의 이점을 압도함.
- H2 POSITIVE: 색별 이화학적 품질 결정인자가 실질적으로 다르다(Spearman ρ=0.236). 황산염: 적 #2(13.2%) vs 백 #9(5.5%); 자유 SO₂: 백 #3(12.3%) vs 적 #11(4.7%); 알코올: 양색 공통 #1(~27-28%). 근거: run_id=7020511e 색별 분리 모델 특성 중요도 + run_id=89d7b721 통합 모델 특성 중요도.
- H3 POSITIVE (독립 재확인 3회): 신뢰 예측 범위=품질 5-7 (MAE 0.37-0.69 양색); 극값(3-4: MAE>1.0; 8-9: MAE>1.3) 비신뢰. 재현 run_id=89d7b721에서: 적 q=5 MAE=0.371, q=6=0.449, q=7=0.610; 백 q=5=0.541, q=6=0.380, q=7=0.688.
- H4 INCONCLUSIVE: 색×이화학 명시적 상호작용 항(11개) 효과가 CV(+0.0005 기준선 우세)와 Dev(-0.0037 상호작용 우세) 간 불일치. 상호작용 항 합산 중요도 7.8%로 GBM 묵시적 처리 가능 해석. 확정적 결론 불가. 재현에서도 동일 패턴 확인.
- STRONG BASELINE CHECK PASS: 색별 평균 예측기 Dev EW-MAE=0.6881 >> GBM EW-MAE=0.5261. GBM이 자명하지 않은 예측기임을 확인(23.5% 개선).
- LEAKAGE CHECK PASS: GroupKFold(5) on group_id에서 5개 fold 모두 train/val 간 group_id 중복 없음. Feature-duplicate 누출 방지 확인(재현 run_id=89d7b721 독립 검증)
- BACKEND CONSTRAINT: 모든 3개 ORX 실행에서 LightGBM 미탑재, sklearn GBM 폴백. 절대 MAE값은 백엔드 의존; 질적 결론(통합≈분리, 색별 특성 다양, 품질 5-7 신뢰)의 강건성은 sklearn GBM이 GBM 계열의 대표적 구현임에 근거하여 예상됨.

에이전트가 스스로 밝힌 한계:

- LightGBM 미탑재(3개 ORX 실행 모두): sklearn GBM 폴백. 절대 MAE값과 통합/분리 격차 크기는 백엔드 의존; 방향 변화는 예상하지 않으나 확인 불가.
- H4 불확실: CV(5-fold GroupKFold, 더 신뢰)와 Dev(n=1,300, 소규모) 결과 불일치. Dev의 -0.0037 이득은 노이즈 범위. 더 큰 검증 데이터셋에서의 재검증 필요.
- 극값 품질 분석 고분산: 재현 시 Dev q=3(n=7 합계), q=9(n=1) — 극값 MAE 추정치 신뢰구간 넓음. 통계적 유의성 불확실.
- 특성 중요도 한계: sklearn GBM split-count 기반(gain/SHAP 아님). 상대적 크기 비교는 순위 수준만 신뢰.
- 하이퍼파라미터 탐색 없음: n_estimators=300, lr=0.05, max_depth=5 단일 조합. 조정 시 통합/분리 격차 또는 H4 결론 변동 가능.
- Dev 색상 불균형: 적 n=294, 백 n=1,006 — 적 MAE 추정치 표준오차가 백보다 ~1.8배 크다. EW-MAE의 적 성분은 더 큰 불확실성을 갖는다.

**first_week-wine-P-normal 후보 주장** (에이전트 작성, 미검증):

- NEGATIVE RESULT (dev): Color-stratified models do not outperform unified model in equal-weight MAE on dev set (0.5267 vs 0.5261, delta=-0.0006). CAUTION: small absolute delta; meaningful CV evidence: unified CV EW-MAE=0.5305 vs stratified CV=0.5436 (-2.5%), 5-fold GroupKFold on group_id. Source: ORX run_id=7020511e, receipt_sha256=8cf6c56f4cb7efdef9cec4a7aad534068ca6af6b8fe65e6e0533666be440ad6d.
- FEATURE DIVERGENCE (confirmed): Physicochemical importance rankings differ substantially between red and white wine (Spearman rho=0.236 on n=11 features). Sulphates #2 red (13.2%) vs #9 white (5.5%); free SO2 #11 red (4.7%) vs #3 white (12.3%); alcohol #1 for both (~25-28%); volatile acidity top-3 for both. Source: same ORX run, stratified_model.feature_importance_by_color field.
- APPLICABLE RANGE (confirmed): Reliable predictions (MAE 0.37-0.69) confined to quality scores 5-7 for both colors, covering 93.9% of red and 90.9% of white dev samples. Extreme scores (3-4 or 8-9) yield MAE >1.0, driven by training data sparsity. Source: same ORX run, quality_score_error field.
- BACKEND CONSTRAINT (recorded): sklearn GradientBoostingRegressor used (lightgbm absent in ORX science container); conclusions about relative model ordering are expected qualitatively robust to backend but absolute MAE values are backend-dependent.

에이전트가 스스로 밝힌 한계:

- LightGBM was unavailable in the ORX science container; sklearn GBM (n_estimators=300) was used. LightGBM may change absolute MAE values and potentially the magnitude of the unified vs. stratified delta, though the qualitative finding (parity) is consistent with both CV and dev evidence.
- Dev set is small (n=1300: 294 red, 1006 white) and the dev delta of -0.0006 is within noise; the stronger CV evidence (unified wins by 2.5%) is more reliable for the H1 conclusion.
- Extreme quality score analysis (quality 3: n=2 red dev, n=5 white dev; quality 9: n=1) is based on very small samples; applicable range boundary estimates at those scores carry high variance.
- Feature importances are sklearn split-count-based (not gain or SHAP); relative magnitudes should be treated as indicative ordering, not precise quantitative effect sizes.
- No hyperparameter search was performed; results represent a single set of reasonable defaults. A tuned model may show different relative behavior between unified and stratified architectures.
- Only two model architectures compared; other approaches (e.g., stacking, meta-learning with color) were not tested within this study.

첫 Wine 노드는 다른 프로젝트의 LiveKit 컨테이너 존재를 감지해 학습 전에 중단됐다. 실패를 보존하고 별도 수정 노드로 실행했다. 기존 서비스는 건드리지 않았다. 개발 성능 측정에는 기존 저활동 서비스의 전후 CPU 표본만 있으며 연속적인 무경쟁 환경 증명은 없다. 따라서 개발 timing만으로 최종 최소10% 개선을 확정하지 않는다. ORX 대시보드 연결 중단 후에도 기존 실행 ID로 종료 결과를 회수했고 재실행으로 바꾸지 않았다.

ORX 프로젝트는 `4d54d8cb-64b6-4091-a739-85cf18a15d94`, 고정 명령은 `/opt/homebrew/bin/python3 runner.py`다. 각 노드의 커밋·실행 ID·결과 해시·자원 기록은 [수치와 실행 목록](first-results.json)에 있다. 첫 준비와 초기 노드 이후 소스 수정은 새 커밋에만 적용했다. 원본·실패·이전 설계는 보존했다.

다음은 모델 경로·과금의 실제 인증, 독립 역할 전달과 새 감독 세션, B/P 정상 캠페인, 중단·모델 교체, 최종 평가의 비노출을 연결하는 일이다. 모델 카탈로그·로그인·프롬프트·모의 검사만으로 이 연결을 완료 처리하지 않는다. 추가 과금300000원·프로젝트8시간/8 CPU-core-hours·합계4 CPU/4.5GiB 상한은 유지한다. 미확인 사용량은0으로 처리하지 않는다.

[현재 실행 규약](README.md) · [대시보드](../../../.planning/2026-09-09-project-research-execution/dashboard.html) · [통합 검토](../../../.planning/2026-09-09-project-research-execution/integration-review.md)
