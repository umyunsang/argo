# Study B T1' 봉인 부록 v2 (T1' Addendum v2)

작성 시각: 2026-09-04T10:30:00+09:00
권한: supervisor instruction-0017 (T1' 과제군 확정 및 파일럿 결과 반영, v1 대체)
사전등록 참조: `paper/research/study-b-preregistration-v4.md` (sha256 `0325ce9fb92f9f98c339665e4cfccc401283c1fd89b64f090990df9f64ad8147`, seal_commit `5d9c0d088`)
분석 사양 참조: `paper/research/study-b-analysis-spec-v4a.md` (동점 처리 포함)

---

## 1. Q1 판정 결과 및 과제군 확정 (T1' ScienceAgentBench)

- **Q1 판정: (b) 기성 벤치마크 중 결정론적 채점 과제군으로 T1 재설계 (T1')**
  - 원 T1(ResearchClawBench)은 유일한 공식 채점기가 LLM 판정기(evaluation/score.py, sha256 `57320c35...`)임이 확인되어 즉시 배제되었다.
  - 대체 1순위인 **ScienceAgentBench (arXiv 2410.05080, OSU-NLP-Group/ScienceAgentBench, commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`, MIT 라이선스 sha256 `93b43d692b...`)**의 저장소 바이트 및 논문 원문을 전수 검증하였다.
  - 전체 102개 과제 중 GPT-4o visual judge(도표 평가) 및 LLM 기반 루브릭 채점을 제외한 **순수 프로그램 기반 결정론적 검증기(deterministic programmatic eval)를 보유한 과제 38건**을 식별하였다.
  - 이 중 공식 검증 아티팩트(`benchmark_verified.zip`) 내 gold results가 온전히 보존된 과제 36건을 후보 풀로 확정하였으며, 각 과제 데이터는 수십 KB ~ 수십 MB 수준으로 CPU 상에서 5분 이내 실행 가능하다.

## 2. 오라클 격리 및 워크스페이스 구축 설계

- **오라클 격리 (Oracle Isolation):**
  - ScienceAgentBench 원문 설계(arXiv 2410.05080, 라인 683)에 따라, 모델 개발 과제의 테스트셋 라벨은 평가용으로만 보관되며 에이전트에게 제공되는 데이터셋 내에서는 더미 값(`-1`, `-999`, 더미 클래스 등)으로 치환되어 있다.
  - `experiments/study_b/tasks/run_t1.py`의 `setup_workspace()` 함수는 오라클 격리를 물리적으로 강제한다:
    - 에이전트 워크스페이스(`/tmp/study_b_workdir/...`)에는 오직 원시 데이터셋 폴더(`benchmark/datasets/<folder>/`)와 과제 지시문(`TASK.md`)만 배치된다.
    - 정답 프로그램(`gold_programs/`), 채점 스크립트(`eval_programs/`), 정답 데이터(`gold_results/`)는 에이전트 실행 환경에 전혀 주입되지 않으며, 실행 완료 후 별도 격리 환경에서 `verify_output()`을 통해 실행된다.

## 3. B0 Headroom 파일럿 측정 결과 및 분석

- **파일럿 실행 개요:**
  - 실행 일시: 2026-09-04T09:59 ~ 01:07 KST
  - 대상: B0 아암, Task 1 (Clintox 다중작업 분자독성/FDA 승인 예측, Computational Chemistry)
  - 지출 한도: 드라이런 한도 line(상한 $2.00, 기지출 $1.09, 잔여 $0.91) 중 ≤$0.90 예산 배정.
  - 측정 비용: **$0.282667 (291,404 토큰, 소요시간 386.6초)**. 드라이런 누적 잔여 $0.627333 유지.
  - 조작 검사(Manipulation Check): **통과** (bash 10회, write 3회, ipython 호출 0회).
- **성공률 및 Headroom 관측:**
  - 에이전트 응답: 22개 테스트 화합물에 대해 다중작업 신경망(DNN)을 직접 설계·학습하고 `pred_results/clintox_test_pred.csv`를 성공적으로 생성(answered=True).
  - 검증기 판정: **0점 (Fail)**. 에이전트가 출력 컬럼명을 `['smiles', 'tox21_prob', 'FDA_APPROVED_prob']`로 저장하여 검증기가 요구하는 `['FDA_APPROVED', 'CT_TOX']`와 불일치함(KeyError).
  - 이는 ScienceAgentBench 논문(arXiv 2410.05080, 라인 752·872)에서 보고된 "LLM 에이전트는 고수준 구조는 파악하나 구체적 API·출력 규격에서 미세 실패를 겪음"과 완전히 부합하며, T3 과제군에서 나타난 만점 천장 효과(Ceiling Effect)와 대조적으로 **충분한 난이도와 헤드룸(headroom)이 존재함**을 실증한다.
- **파일럿 중단 및 인증 만료 사실 공시:**
  - Task 2~5 시도 과정에서 OAuth 인증 토큰 만료(`No API key for provider: anthropic`, timestamp 1788483953554, expires 1788452843333)가 발생하여 즉각 실행을 중단하였다. Task 2~5의 지출은 각 $0.0000이며, 실측 데이터가 확보된 Task 1(1개 완결 에피소드)을 파일럿 영수증으로 보존한다.
  - 파일럿 영수증: `paper/experiments/screening/block/pilot_receipts/pilot_b0_t1_task1_receipt.json` (`evidence_level: PIPELINE_DRY_RUN`).

## 4. 표본 크기(n) 및 예산 수식 재산정

- **단위 비용 및 잔여 예산:**
  - 실측 단위 비용: $0.282667 / episode
  - 스크리닝+블록 확정 잔여 예산: **$29.910686** (상한 $48.47 - 기지출 $18.559314)
- **n=40 (기본 설계) 검토:**
  - 필요 에피소드: 40 pairs × 3 arms = 120 episodes
  - 예상 비용: 120 × $0.282667 = **$33.920040**
  - 판정: 잔여 $29.91을 $4.01 초과하여 버퍼 ≥$5 조건을 충족할 수 없음.
- **예산 제약 하 권고 표본 크기: n = 29 pairs (triples)**
  - 산정 수식: `floor((29.910686 - 5.00) / (3 * 0.282667)) = 29 pairs`
  - 총 에피소드: 29 × 3 = 87 episodes
  - 확정 소요 예산: 87 × $0.282667 = **$24.592029**
  - **보존되는 안전 버퍼: $29.910686 - $24.592029 = $5.318657 (≥$5 조건 완벽 충족)**
- **재계산된 MDE (Minimum Detectable Effect):**
  - Wilcoxon signed-rank test (Pratt tie-rule, 양측 α = 0.05, 80% 검정력, discordant pair 비율 $p_d = 0.30$):
    - n = 40: MDE = 0.243
    - **n = 29: MDE ≈ 0.285**
    - n = 24: MDE = 0.313
    - n = 20: MDE = 0.343
  - n=29 설정은 충분한 검정력(MDE < 0.30)을 유지하면서 규정된 안전 버퍼를 온전히 확보한다.

## 5. 부록 v1 대비 정정 사항 (Errata & Corrections)

1. **조작 검사 규칙 표기 오기 정정 (instruction-0017 §9 반영):**
   - 부록 v1의 "B0: ipython/bash 호출 0" 표기는 명백한 오기이다.
   - 올바른 사전등록 v4 규약: **B0는 ipython 호출만 0이어야 하며, 기본 도구인 bash는 완전 허용된다.**
   - 파일럿 Task 1에서도 에이전트가 bash를 10회 정상 호출하여 코드를 실행하였으며, manipulation check를 성공적으로 통과하였다.
2. **용어 교정:**
   - 부록 v1의 "ceiling effect(바닥효과)" 표기를 올바른 통계·심리측정학적 한국어 용어인 **"천장 효과 (Ceiling Effect)"**로 전면 정정한다.
