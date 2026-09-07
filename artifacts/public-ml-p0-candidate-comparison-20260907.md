# 첫 P0 자율연구 과제 비교

**추천: MLAgentBench House Price(`home-data-for-ml-course`)를 첫 통합 실행 가능성 검증 과제로 선택. 아직 선택·실행 승인된 상태는 아니다.**

기존 Prime Agent/RLM에서 원문·코드·인터페이스 감사와 공통 static 장치를 병렬 처리했다. Kaggle 계정 접근은 다시 검사하지 않고 기존 읽기 전용 receipt를 사용했다. 계정 요구로 과제를 제외하지 않았다.

| 후보 | 연구 기회 | 첫 P0의 주요 부담 | 제안 |
|---|---|---|---|
| **House Price** | 혼합형 특성 처리, RF·선형·트리 계열 비교, residual 기반 후속 수정 | 빈 baseline 학습 부분, 공개 suffix split/hidden custody, ID/finite scorer, 약관·실제 비용 | **추천** |
| **Spaceship Titanic** | Cabin·여행 그룹·지출·결측 처리, logistic·tree 비교 | group/entity 분할 판단, 누락 행·dummy alignment, scorer row 검증 | **차선** |
| CIFAR-10 | augmentation·architecture·optimizer 경쟁, 완성된 starter | test label/epoch score 노출 제거, torch 환경·하드웨어·비용 미측정 | 대안 유지 |
| California Housing/TabM | tabular method 경쟁 가능, seeded source split | finite HPO/test feedback를 open research로 분리, pre-staged asset·외부 코드, 결과 JSON 대신 prediction artifact | 대안 유지 |

House Price는 `house-prices-advanced-regression-techniques` 대회가 아니다. pinned preparation은 `home-data-for-ml-course/train.csv`를 읽어 자기80/20 prefix/suffix task를 만든다. 공식 Kaggle leaderboard test를 그대로 쓰지 않으며 source metric은 SalePrice **MAE**다. split의 타당성·변경 여부는 과제 프로토콜에서 별도로 정한다.

## 확인한 것

- MLAgentBench v2 원문 추출 텍스트 전체 LF1–2374 완독. published/illustrative 수치는 local 효과나 비용 추정으로 쓰지 않았다.
- 후보24개 source 파일과43개 비교 quote를 root가 해시/정확한LF 범위로 재도출했다.
- Kaggle 두 후보의 파일목록 HTTP200 receipt가 있다. dataset download·약관 수락·제출은0이다.
- 공통 artifact-lock static fixture commit `ccdbf3df0a23169637711ea363262ced89aaf2df`: clean clone7 tests PASS, `npm run check` PASS. process-local per-lock-ID 사양이며 trusted/durable/campaign-wide lock은 아니다.

## 아직 모르는 것

실제 data bytes·분포·license/terms, baseline 성과·분산, CPU/GPU 실행 시간·메모리·비용, independent scorer custody는 미확정이다. House Price의 낮은 환경 부담은 source를 보고 내린 판단이지 실측 성능 비교가 아니다. 공개 Kaggle rules/data 페이지는 HTML 제목·메타만 확인됐고 전체 규칙은 아직 읽지 못했다.

## 다음 결정

**첫 P0 과제로 House Price(`home-data-for-ml-course`)를 선택할까요?** 그룹·개체 연구의 풍부함을 더 중시하면 Spaceship Titanic이 대안이다. 선택 후 task-bound baseline·split/scorer·MUE·정확한 budget/command를 고정하며 실제 P0는 별도 실행 계약을 따른다. 다른 후보를 최종 제외한 것은 아니다.

## 근거

- [원문·코드 통합](../paper/research/public-ml-programme-qualification/integration/qualification-summary-ko.md)
- [상세 네 후보 비교](../paper/research/public-ml-programme-qualification/integration/restored-candidate-comparison.md)
- [root 검증·조건](../paper/research/public-ml-programme-qualification/integration/restored-comparison-intake-v1.json)
- [과제 선택 제안](../paper/research/public-ml-programme-qualification/p0-task-selection-proposal-v1.json)
- [static 장치 검증](../paper/research/public-ml-programme-qualification/integration/artifact-lock-immutable-validation-v1.json)
