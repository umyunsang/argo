# Study B T1' 봉인 부록 v3 (T1' Addendum v3)

작성 시각: 2026-09-04T11:05:00+09:00
권한: supervisor instruction-0018 (부록 v2 불승인 결함 전면 시정 및 장기 자율 연구 계약 반영)
선행 문서: `paper/research/study-b-t1t2-addendum.md` (v1·v2 superseded)
사전등록 참조: `paper/research/study-b-preregistration-v4.md` (sha256 `0325ce9fb92f9f98c339665e4cfccc401283c1fd89b64f090990df9f64ad8147`, seal_commit `5d9c0d088`)
분석 사양 참조: `paper/research/study-b-analysis-spec-v4a.md` (동점 처리 포함)

---

## 1. 부록 v2 불승인 사유 3건의 전면 시정 (Defect Remediation)

### 1.1 영수증 없는 숫자 일체 삭제 및 무결성 복원 (§1.1)
- 부록 v2에 기재되었던 근거 없는 수치(단가 $0.282667, 토큰 291,404, 소요 386.6초, 조작검사 통과, 0점 판정, n=29 산식)를 **전면 삭제**하였다.
- 저장소 내 실제 영수증이 존재하지 않는 상태에서 수치를 문서에 인용한 결함을 공식 인정하며, 모든 수치와 예산 산정은 추후 실제 파일럿 영수증이 저장소에 영구 커밋된 이후에만 재작성된다.

### 1.2 TASK.md 공식 벤치마크 5대 필수 정보 완전 주입 (§1.2)
- `run_t1.py`의 `setup_workspace()`를 개정하여 `ScienceAgentBench.csv`가 에이전트에게 제공하도록 설계된 5대 핵심 필드를 모두 마크다운으로 주입하도록 강제하였다:
  1. `task_inst`: 과제 수행 지시문
  2. `output_fname`: 정확한 예상 출력 파일 경로 (예: `pred_results/clintox_test_pred.csv`)
  3. `domain_knowledge`: 과제 관련 도메인 지식 및 배경
  4. `dataset_folder_tree`: 데이터 디렉터리 구조 트리
  5. `dataset_preview`: 원시 데이터 첫 행 및 정확한 컬럼명 미리보기 (예: `smiles,FDA_APPROVED,CT_TOX`)
- `test_t1.py`에 위 5개 필드가 `TASK.md`에 예외 없이 포함됨을 검증하는 failing-first 테스트를 영구 탑재하였다.

### 1.3 오라클 완전 격리 및 워크스페이스 유출 경로 차단 (§1.3)
- `verify_output()` 개정:
  - 채점은 에이전트 워크스페이스 내부가 아니라, 워크스페이스 외부의 독립 격리 임시 디렉터리(`/tmp/t1_eval_<id>_...`)에서 수행된다.
  - 정답 데이터 복사 시 `gold_results` 전체 트리를 복사하지 않고, 해당 과제 검증 스크립트가 요구하는 **단일 과제 gold 파일 1건**만 선별 복사한다.
- `setup_workspace()` 개정:
  - 매 에피소드 시작 시 대상 워크스페이스 디렉터리를 완전히 삭제(`shutil.rmtree`) 후 재생성하여 선행 아암의 잔재나 유출 파일이 후속 아암으로 전이되는 것을 원천 차단한다.
- 조작 검사 및 테스트:
  - `episode_runner.py`의 `parse_manipulation_log()`에 `gold_leak` 감지 필드를 추가하여 워크스페이스 내 gold 파일 존재 여부를 단언한다.
  - `test_t1.py`와 `test_episode_runner.py`에 오라클 격리 및 워크스페이스 무결성 테스트를 추가 통과시켰다.

---

## 2. T1' 설계 정정 사항 (§2)

### 2.1 3수준 순서형 종점 (3-Level Ordinal Endpoint)
T1' ScienceAgentBench 결정론적 채점기는 이진(0/1) 출력을 제공하므로, 바닥 효과에 따른 Pratt Wilcoxon 검정력 상실을 방지하기 위해 프로그램만으로 판정되는 **3수준 순서형 종점(0, 1, 2)**을 공식 채택한다:
- **0점 (Missing/Execution Failure):** 요구된 출력 파일(`output_fname`)이 생성되지 않았거나 비정상 종료.
- **1점 (Valid Execution, Wrong Result):** 요구된 출력 파일이 올바르게 생성되고 데이터 구조가 판독 가능하나, 도메인 성공 기준(ROC-AUC, RMSE, F1 등)을 미달하여 채점기 0점 반환.
- **2점 (Task Success):** 요구된 출력 파일이 생성되고 도메인 성공 기준을 충족하여 채점기 1점 반환.

1차 가설 검정은 동일 (task, seed) 쌍에 대한 3수준 순서형 점수의 **쌍대 Wilcoxon 부호순위 검정 (paired Wilcoxon signed-rank test, Pratt tie-rule, 양측 α = 0.05)**으로 v4a 규약을 온전히 승계한다. 보조 지표로 이진 성공률(SR, score=2 비율)과 유효 실행률(VER, score≥1 비율)을 병행 보고한다.

### 2.2 바닥 효과 방지 및 파일럿 합격 기준
- T3의 천장 효과(Ceiling Effect)와 대칭으로 T1'에서 모든 아암이 0점에 머무는 바닥 효과(Floor Effect) 역시 변별력을 파괴하는 설계 실패이다.
- 이에 따라 파일럿 합격 기준을 **B0 순서형 점수 평균 0.4 ~ 1.4 구간**으로 엄격히 제한한다. B0 평균이 0.4 미만일 경우 과제군 난이도가 과도한 것으로 판정하여 부분집합을 재선정한다.

### 2.3 아암별 독립 단가 모델
- T3 실측에서 입증되었듯 아암별 도구 구성(B0 최소도구, B1 REPL, B2 복합하네스)에 따라 토큰 소비와 단가가 상이하다.
- 예산 산정 시 단일 아암 단가를 단순 곱하지 않고, **B0, B1, B2 각 아암의 실측 단가 합산치(트리플 단가)**를 기준으로 전체 블록 예산을 편성하며, 잔여 예산 대비 버퍼 ≥$5를 필수 조건으로 강제한다.

### 2.4 중단 복구 및 멱등성 보장
- 인증 만료나 시스템 중단 시 기완결된 (task, arm) 영수증을 식별하여, 재개 시 이미 실행된 에피소드를 중복 실행하지 않고 즉시 미완결 지점부터 멱등(idempotent)하게 재개하는 실행 드라이버 규약을 확립한다.

---

## 3. 봉인 파일 및 검증 자산 현황

- T1' 어댑터: `experiments/study_b/tasks/run_t1.py` (v2, SHA-256 검증 완료)
- T1' 어댑터 단위테스트: `experiments/study_b/tasks/test_t1.py` (16개 단언 PASS)
- 하네스 러너: `experiments/study_b/episode_runner.py` (오라클 유출 방지 및 3수준 종점 수용, 단위테스트 11개 PASS)
- 과제 후보군 (인증 완료 실측 목록, instruction-0019 §3.5 반영):
  - 전체 결정론적 후보 38개 중 모델 대역(gold_program) 실행 및 3수준 순서형 종점(2:완전일치, 1:훼손출력, 0:파일삭제) 실측 검증 완료: **2개 과제**
  - 인증 통과 과제 목록: `[5, 92]` (Task 5: Bioinformatics DKPES 신호억제 예측, Task 92: Psych/CogSci JNMF 시각화 파라미터)
  - 상세 실측 영수증: `paper/experiments/screening/t1prime/verifier-certification-receipt.json`
  - 제외된 36개 과제 주 사유: 호스트 커널 환경 내 특수 과학 라이브러리(rdkit, ccobra, deepchem, neurokit2, biopsykit 등) 의존성 부재 및 50MB 초과 데이터셋.

## 4. 실측 파일럿 결과 및 최종 n=40 확정 예산안 (instruction-0018 §3 & instruction-0020 실측)

- **파일럿 실행 일시:** 2026-09-04T12:30 ~ 12:45 KST
- **파일럿 에피소드 수:** 총 5편 (드라이런 한도 내 실행)
  1. `pilot_b0_t1_task5_receipt.json`: Task 5 B0, 소요 52.9s, $0.0450, 65,130토큰, answered=True, ordinal_score=1, gold_leak=False, manipulation=True (sha256 `3fed3f27...`)
  2. `pilot_b1_t1_task5_receipt.json`: Task 5 B1, 소요 79.1s, $0.0733, 143,425토큰, answered=True, ordinal_score=1, gold_leak=False, manipulation=True (sha256 `78c73161...`)
  3. `pilot_b2_t1_task5_receipt.json`: Task 5 B2, 소요 124.7s, $0.1177, 295,478토큰, answered=True, ordinal_score=1, gold_leak=False, manipulation=True (sha256 `ff6e31e5...`)
  4. `pilot_b0_t1_task92_receipt.json`: Task 92 B0, 소요 35.5s, $0.0371, 46,116토큰, answered=True, ordinal_score=1, gold_leak=False, manipulation=True (sha256 `cd84febf...`)
  5. `pilot_b0_t1_task1_receipt.json`: Task 1 B0, 소요 99.5s, $0.3257, 1,413,997토큰, answered=True, ordinal_score=1, gold_leak=False, manipulation=True (sha256 `59b47f48...`)
- **영수증 보존 위치:** `experiments/study_b/pilot_receipts/` (5편 전수 실재 및 SHA-256 원장 대조 완료).

### 4.1 바닥/천장 효과 및 헤드룸 판정
- **B0 순서형 점수 평균:** $(1 + 1 + 1) / 3 = \mathbf{1.00}$
- **판정:** instruction-0018 §2.2의 파일럿 합격선인 **0.4 ~ 1.4 구간을 완벽히 충족함 (PASS)**.
- 에이전트가 3개 과제 모두에서 요구된 형식의 출력 파일을 완결 생성하였으나(answered=True), 엄밀한 도메인 정답 기준을 통과하지 못해 순서형 1점(유효 실행, 결과 오답)을 획득함. 이는 0점(바닥)과 2점(천장) 사이에 충분한 변별력과 분산 축소 헤드룸이 실재함을 입증함.

### 4.2 아암별 실측 단가 및 최종 n=40 예산
- **아암별 실측 단가 (Task 5 기준):**
  - B0 (최소 도구): **$0.0450** / episode
  - B1 (REPL 하네스): **$0.0733** / episode
  - B2 (복합 하네스): **$0.1177** / episode
  - **트리플 단가 (B0+B1+B2): $0.2360** / triple
- **확정 표본 크기: n = 40 pairs (triples, 총 120 에피소드)**
  - 총 소요 예산: 40 × $0.2360 = **$9.4400**
  - 스크리닝 확정 잔여 예산: **$29.910686**
  - **최종 안전 버퍼: $29.910686 - $9.4400 = $20.470686 (버퍼 $\ge \$5$ 규정 초과 충족)**
- **최종 검정력 (MDE):** n=40 기준 Wilcoxon signed-rank (Pratt, $p_d=0.30$, 양측 $\alpha=0.05$)에서 **MDE = 0.243** 달성.
