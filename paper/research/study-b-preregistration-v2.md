# Study B 사전등록 v2 (Pre-Data Amendment)

- **선행 문서:** `paper/research/study-b-preregistration.md` (v1, sha256 `f8671c44f076039dbb7e9038f0f659cfd13d687ba0b7092c70328c18ad0cfa4d`, 2026-09-03T10:53:45)
- **개정 사유:** v1의 아암 조작이 프롬프트 수준에 그쳐 manipulation check에 실패(B0에서 ipython 328회 언급 및 호출 발생, B2 메커니즘 툴 부재)함에 따라, 도구 및 게이트 수준의 실제 하네스로 전면 재구현하고 봉인 범위를 모델 호출 경로 전체로 확장한다. 스크리닝 지출 $0.00, 확증 데이터 0건 상태에서 수행된 투명 pre-data amendment이다.
- **작성 일시:** 2026-09-03T15:33:26+09:00
- **승인 근거:** 사용자 지시 2026-09-03 10:47 KST (Q-0009 시나리오 a, 지출 상한 $48.47) 및 instruction-0015 §2.

---

## 1. v1 대비 주요 변경점 (Diff Summary)

1. **하네스 구현 방식의 전환 (프롬프트 → 툴·게이트 인터셉트):**
   - 시스템 프롬프트 분리: 각 아암별 시스템 프롬프트는 파일(`prompts/b{0,1,2}_system_prompt.txt`)에서 `--system-prompt`로 분리 주입. 과제 텍스트(`TASK.md`)는 사용자 턴으로만 전달되며 아암 간 바이트 동일(sha256: `d2e232f8ae2892092f246bc1b3544e0087fa485f44f813553e36f6d629f22904`).
   - **B0 (최소 도구):** `--no-builtin-tools`로 `ipython`을 원천 박탈하고, 최소 파일/쉘 도구(`read`, `write`, `edit`, `bash`) extension(`b0_tools.js`)만 탑재.
   - **B1 (표현력 REPL):** B0 도구에 더해 내장 `ipython` 활성화.
   - **B2 (책임 복합):** B1 도구에 더해 타입드 컨텍스트 그래프(`graph_add`, `graph_query`), 결정 프로토콜(`decision_record`, `threshold_register`), 반증 루프(`loop_evaluate`) extension(`b2_harness.js`) 탑재.
   - **B2 fail-closed 인터셉트 게이트:** 6필드 결정 레코드 및 사전 임계값 등록 없이 `ipython`/`bash` 실행을 시도할 경우 도구 호출 단계에서 즉시 차단(fail-closed).
2. **오염 격리 환경 확정:**
   - 실행 워크디렉토리를 레포 외부 임시 경로(`/tmp/study_b_workdir/...`)로 격리.
   - `PRIME_AGENT_CODING_AGENT_DIR=/tmp/clean_agent_dir`로 설정하여 글로벌 Continual Harness(메모리 41건, 프롬프트 노트 2건) 주입 원천 차단.
   - `-nc -ne -ns -np --no-session` 플래그 강제.
3. **사전 명시 배제 규칙 (Manipulation Check Failure):**
   - B0에서 `ipython` 호출이 1회라도 발생하거나, B2에서 사전 결정/임계 등록 없는 실행이 발생한 에피소드는 하네스 결함으로 무효 처리하며 확증 데이터에서 배제한다.
4. **바닥효과 해소 (1차 지표 개정):**
   - 1차 지표: 검증기 항목 단위 통과 비율 (`score.n_pass / score.n_total`, 0.0 ~ 1.0 연속형).
   - 1차 가설 검정: 동일 (task, seed) 쌍에 대한 **쌍대 Wilcoxon 부호순위 검정 (paired Wilcoxon signed-rank test)**, 양측 α = 0.05.
   - 2차 지표: 검증기 전부 통과 여부 (`score.pass` 이진형, 5/5 통과 시 1)에 대한 풀링 McNemar 검정.
5. **쌍 완결 실행 순서:**
   - 각 (task, seed) 쌍에 대해 B0, B1, B2를 연속 실행하여 예산 상한($48.47) 도달 시 미완결 쌍 없이 완결 쌍만 남도록 강제.
6. **봉인 범위의 확장:**
   - 러너, 아암 프롬프트, TypeScript extension, 오라클 검증기를 모두 포함하여 14개 파일 블롭 해시를 봉인.

---

## 2. 2차 드라이런 실측 기반 비용 및 표본 크기 재산정

2026-09-03 2026-09-03T15:33:26+09:00 격리 환경에서 실행된 2차 드라이런(T3, seed 42, claude-haiku-4-5) 실측값:
- **B0:** $0.170364 (636,485 토큰, 0/5 통과, manipulation: PASS, ipython: 0)
- **B1:** $0.155862 (505,061 토큰, 0/5 통과, manipulation: PASS, ipython: 5)
- **B2:** $0.109955 (213,698 토큰, 1/5 통과, manipulation: PASS, gate_block: 1, decision: 3, thresh: 4)
- **에피소드당 평균 실측 비용:** **$0.14539**

사용자 승인 지출 상한은 **$48.47**이다.
- $48.47 / $0.14539 = 최대 333 에피소드.
- 3개 아암(B0, B1, B2)을 3개 과제에 동수 배분할 경우:
  - 3개 과제 × 3개 아암 = 9셀. 333 / 9 = 과제당 **n = 37쌍** (총 333 에피소드, 예상 지출 $48.42).
  - 만약 자율 연구 완전 자기완결 과제 T3에 집중할 경우: T3에 n=40쌍 (120 에피소드, 예상 지출 $17.45) 실행 후 잔여 예산 내에서 확장.
- 누적 지출이 $48.47에 도달하면 즉시 중단하고 완결된 쌍만 분석에 포함한다.

---

## 3. v2 봉인 대상 아암 및 인프라 블롭 해시 (git blob sha1)

| 파일 | git blob sha1 |
|---|---|
| `experiments/study_b/harness/arms.py` | `d2f52da4bbd3130e428caecd03446850ff2a2868` |
| `experiments/study_b/harness/components.py` | `301fc1e7418764a08db770f323296671c84672b0` |
| `experiments/study_b/harness/test_harness.py` | `68d6bc4a1a2c4b7e78294c60f368defcf511b70e` |
| `experiments/study_b/run_block.py` | `01aa0a3601fc470e1d999ec495d4eb2cd16be6df` |
| `experiments/study_b/episode_runner.py` | `63dbf02f3be339320a91f64b6561b8d7e94e4249` |
| `experiments/study_b/test_episode_runner.py` | `5d07a82dc28e7c44886bba95413c5390baef443c` |
| `experiments/study_b/harness/test_extensions.py` | `97028838eac786c3d2cd58eb12763aef8e0469fc` |
| `experiments/study_b/harness/extensions/b0_tools.js` | `1085847e30d0bc99e307d59fbc1c670419601f66` |
| `experiments/study_b/harness/extensions/b2_harness.js` | `e30b9fc06c3e2aa67ddb7afc6434fdb8ecb2d706` |
| `experiments/study_b/harness/prompts/b0_system_prompt.txt` | `3f662865279e6e19b9486e8221ff7d4db0a66ad9` |
| `experiments/study_b/harness/prompts/b1_system_prompt.txt` | `50d229862511a1d7ff271588cd2b9b5cd3bdd39a` |
| `experiments/study_b/harness/prompts/b2_system_prompt.txt` | `009b8d3d98d59665910e7cdefc25d960abe05314` |
| `experiments/study_b/tasks/oracle_t3.py` | `f042b1de71388a59bd46bdd858c5e94fe6167804` |
| `experiments/study_b/tasks/run_t3.py` | `a595992323a61190fc8911beb6a6d285f13cd94b` |

- 고정 run command:
  `/usr/bin/python3 experiments/study_b/run_block.py --arm <ARM> --task <TASK> --seeds <N> --out <RECEIPT>`
