# Study B 사전등록 v4 (v2 본문 보존 + v3·v4 수정 부록)

- **선행 문서:** `paper/research/study-b-preregistration.md` (v1, sha256 `f8671c44f076039dbb7e9038f0f659cfd13d687ba0b7092c70328c18ad0cfa4d`, 2026-09-03T10:53:45)
- **개정 사유:** v1의 아암 조작이 프롬프트 수준에 그쳐 manipulation check에 실패(B0에서 ipython 328회 언급 및 호출 발생, B2 메커니즘 툴 부재)함에 따라, 도구 및 게이트 수준의 실제 하네스로 전면 재구현하고 봉인 범위를 모델 호출 경로 전체로 확장한다. 스크리닝 지출 $0.00, 확증 데이터 0건 상태에서 수행된 투명 pre-data amendment이다.
- **작성 일시:** 2026-09-03T15:52:57+09:00
- **§1.6 오염 점검 시각:** 2026-09-03T15:33:26+09:00
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

격리 환경에서 실행된 2차 드라이런(T3, seed 42, claude-haiku-4-5) 실측값:
- **B0:** $0.170364 (실행 시각 2026-09-03T15:42:12+09:00) (636,485 토큰, 0/5 통과, manipulation: PASS, ipython: 0)
- **B1:** $0.155862 (실행 시각 2026-09-03T15:43:33+09:00) (505,061 토큰, 0/5 통과, manipulation: PASS, ipython: 5)
- **B2:** $0.109955 (실행 시각 2026-09-03T15:46:00+09:00) (213,698 토큰, 1/5 통과, manipulation: PASS, gate_block: 1, decision: 3, thresh: 4)
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
| `experiments/study_b/episode_runner.py` | `ffedccc90712a67a62248c0b5b714cf0141d000a` |
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

### 3.1 실행 이후 변경된 파일과 그 증명

봉인 해시는 2차 드라이런 **뒤에** 계산되었다. 따라서 실행본과 봉인본이 다른 파일이 존재하며,
각각에 대해 기능 변경 여부를 검증 가능한 방식으로 판정했다.

| 파일 | 관찰 | 판정 | 증거 |
|---|---|---|---|
| `harness/extensions/b0_tools.js`<br>`harness/prompts/b0_system_prompt.txt` | mtime이 B0 실행(15:42:12) 이후(15:52:51, 15:53:03) | **내용 무변경** | 봉인 변조 탐침이 원본 바이트를 되썼다(되쓰기는 mtime만 갱신). 실행본 판별은 로그 형식으로 한다: 초판은 `execute()` 안에서 `{tool, path}`를, 채택판은 `tool_call` 인터셉터에서 `{tool, input}`을 기록한다. B0 로그 12건은 전부 `input` 형식이며, 이는 채택판=현재 커밋본이 실행되었음을 뜻한다. |
| `episode_runner.py` | 봉인 해시 계산(15:52:5x) 이후에 편집됨 | **비기능 변경 (docstring 전용)** | 커밋본과 작업본의 AST를 **docstring 제거 후 비교하여 동일**함을 확인(`ast.dump` 일치). 추가된 것은 모듈 docstring의 집계 기준 4줄뿐이며 실행 경로에 영향을 주지 않는다. |

**재실행하지 않는 사유:** 두 경우 모두 기능 변경이 아니므로 B0를 다시 돌리지 않는다. 다만 봉인 시점의
정직성을 위해, 봉인 해시가 실행 이후에 계산되었다는 사실과 위 판정 근거를 이 문서에 남긴다.
탐침으로 인한 mtime 오염을 피하려면 봉인 파일 변조 탐침은 사본에서 수행해야 하며, 그것은 다음
봉인부터 적용한다.

## 4. 조작 검사 집계 기준 (reproducible counting basis)

수신 receipt의 도구 호출 수는 `manipulation_log.json` 항목 수이며, 이 로그는 extension의
`tool_call` 인터셉터가 **호출 1회당 정확히 1건**을 기록한다. 원시 transcript는 같은 호출을
여러 번 센다: 각 도구 실행이 `tool_execution_start`와 다수의 `tool_execution_update` 이벤트를
내기 때문이다. 두 기준의 관계는 재현 가능하게 확정되어 있다.

| 아암 | 원시 이벤트 합계 | toolCallId 중복 제거 | manipulation_log | receipt |
|---|---:|---:|---:|---:|
| B0 | read 6 / bash 16 / write 2 | read 3 / bash 8 / write 1 | read 3 / bash 8 / write 1 | 동일 |
| B1 | ipython 76 / read 6 / bash 2 / write 2 | ipython 5 / read 3 / bash 1 / write 1 | ipython 5 / read 3 / bash 1 / write 1 | 동일 |
| B2 | ipython 166 / graph_add 12 / threshold 8 / loop 8 / decision 6 / bash 6 / read 4 / write 2 | ipython 7 / graph_add 6 / threshold_register 4 / loop_evaluate 4 / decision_record 3 / bash 3 / read 2 / write 1 | 동일 | 동일 |

**집계 기준 한 줄:** `transcript의 tool_execution_* 이벤트를 toolCallId로 중복 제거한 집합 = manipulation_log 항목 = receipt 수치`.

중요한 성질: **B0의 `ipython`은 어떤 집계 기준에서도 0이다.** 원시 이벤트에도, 중복 제거 후에도,
로그에도 `ipython` 키 자체가 존재하지 않는다. 즉 조작 검사 판정은 집계 기준에 의존하지 않는다.

## 5. 봉인 blob과 실행 blob의 관계 (instruction-0015a §2 대응)

`harness/extensions/b0_tools.js`와 `harness/prompts/b0_system_prompt.txt`의 mtime이
B0 실행(15:42:12)보다 나중(15:52:51, 15:53:03)인 것으로 관찰되었다. 원인은 내용 수정이 아니라
**본 세션의 봉인 변조 탐침 자체**다. 탐침은 파일을 읽어 원본 바이트를 보존하고, 변조 본을 쓴 뒤
원본 바이트를 그대로 되썼다. 되쓰기는 내용을 바꾸지 않지만 mtime은 갱신한다.

내용이 실행본과 동일하다는 증거는 파일 시스템이 아니라 **실행 잔존물**에서 나온다.
`b0_tools.js`에는 로깅 방식이 다른 두 판본이 있었다: 초판은 각 도구 `execute()` 안에서
`{tool, path}`/`{tool, command}`를 기록했고, 채택판은 `tool_call` 인터셉터에서
`{tool, input}`을 기록한다. B0 로그 12건은 **전부 `input` 필드 형식**이다. 따라서 B0는
채택판(현재 커밋본)으로 실행되었고, 커밋본과 작업본은 `git status`상 동일하다.

판정: **비기능 변경이 아니라 무변경(no change)**. 기능 변경이 아니므로 B0 재실행은 불필요하며,
재실행하지 않는다. 대신 교훈을 남긴다 — 봉인 대상 파일에 대한 변조 탐침은 mtime 증거를 오염시키므로,
사본에서 수행하거나 수행 직후 다이제스트 동일성을 함께 기록해야 한다.



---

## v3 amendment (2026-09-03, pre-data) — the sealed run command could not execute

**What v2 sealed was not runnable as an experiment.** The v2 `run_block.py` checked the approval record, the substrate id, the dry-run cap and the task adapter, printed `PRECONDITIONS_OK` and returned 0. It never imported the episode runner, never called a model, and never wrote the `--out` receipt. A screening block launched under v2 would have exited successfully having produced nothing. This was found on 2026-09-03 while preparing the first screening node, before any screening episode ran (screening spend $0.00).

**What changed (code only; hypotheses, endpoint, analysis, arms, prompts, tasks unchanged):**

| file | change |
|---|---|
| `run_block.py` | executes `seeds` episodes through the episode runner; writes the receipt after every episode so a crash or kill cannot lose a spent episode; the substrate id must resolve to a run directory the substrate created (a bare string was accepted before and a test fixture spent $0.085 outside any run); the executor is selected by name and a recorded executor is labelled `FIXTURE_NOT_A_MODEL_CALL`; code identity is derived from bytes because the substrate runs a snapshot without `.git` |
| `test_run_block.py` | 24 failing-first checks, 7/7 mutants caught; never calls a model |
| `fixture_executor.py` | new; the recorder the tests inject |

Arm files unchanged since v2 (byte-identical blob ids): harness/arms.py, harness/components.py, harness/test_harness.py, episode_runner.py, test_episode_runner.py, harness/test_extensions.py, harness/extensions/b0_tools.js, harness/extensions/b2_harness.js, harness/prompts/b0_system_prompt.txt, harness/prompts/b1_system_prompt.txt, harness/prompts/b2_system_prompt.txt, tasks/oracle_t3.py, tasks/run_t3.py.

Changed files: run_block.py.

**Proof the v3 command executes:** substrate run `2727d134` (snapshot `ce2bc723a`), B2/T3, 1 episode, 81 s, $0.178769, manipulation check PASS, receipt `paper/experiments/study-b-dryrun3-B2-T3-receipt.json` (`PIPELINE_DRY_RUN`, excluded from results).

**Budget after v3:** dry run $1.090033 / $2.00; screening $0.00 / $48.47. Unit cost observed for B2 alone: $0.130, $0.145, $0.179 across three dry runs. Screening size is re-derived from the first executed (task, seed) triple, not from the v2 estimate.

**Screening order (unchanged):** (task, seed) pair completion, B0 -> B1 -> B2 consecutive per seed, stop at cap, report only completed triples.

v2 digest: `9a39ef7519dfa8c45aa6e15a101e763f07a1d24f042c40ceaa02380dcae3a119`. v1 digest: `f8671c44f076039dbb7e9038f0f659cfd13d687ba0b7092c70328c18ad0cfa4d`.


---

## v4 amendment (2026-09-03, after a 3-episode pilot, before any block) — the T3 verifier scored unstated conventions

**Pilot (screening stage 1, T3 seed 0, one episode per arm, $0.300209 total, substrate runs `e23f60e8` / `10c8db47` / `40bcbfbf`):** all three arms passed 1 of 5 items. The failures were traced to the verifier, not the arms:

| item | what the oracle assumed and TASK.md did not say | consequence |
|---|---|---|
| `best_lambda`, `improvement_over_baseline` | 5 contiguous unshuffled folds; plain gradient descent, 200 steps, lr 0.1, unconverged | a converged solver picks a different best lambda on 2 of 5 seeds and reports 7x the improvement (probe over seeds 0-4) |
| `paired_t_stat`, `interaction_helps` | same unconverged fit at lambda 0.1 | t = 2.12 / 2.12 / 1.98 against 3.91 |
| `best_config` | exact string `sparsity20_bits4`; weights pruned by magnitude after one dense fit; uniform min-max weight quantisation; retention = dense / compressed in-sample Brier | all three arms failed on spelling alone; two quantised inputs instead of weights |

A block run in that state would have measured agreement with the verifier's private conventions, which is not the preregistered endpoint (item-level pass fraction on a stated task).

**What changed (task adapter only; hypotheses, endpoint, analysis, arms, prompts, runner unchanged):**

| file | change |
|---|---|
| `tasks/run_t3.py` | TASK.md now states the folds, the optimiser trajectory, the update rule, and the compression procedure; `best_config` is scored as the (sparsity percent, bits) pair via `parse_config`, spelling ignored; unparseable or different pairs still fail |
| `run_block.py` | `node_commit`/`harness_commit` fall back to the substrate run store's `commit_sha` for the run id when the snapshot has no `.git` (the pilot receipts recorded `snapshot:<digest>` and the provenance gate rejected them) |
| `tasks/test_t3.py` | 37 checks (was 26): six spellings of the true pair pass, five wrong or unparseable values fail, ten convention tokens must be present in TASK.md; 4/4 mutants caught |

Files unchanged since v3 (byte-identical): harness/arms.py, harness/components.py, harness/test_harness.py, episode_runner.py, test_episode_runner.py, harness/test_extensions.py, harness/extensions/b0_tools.js, harness/extensions/b2_harness.js, harness/prompts/b0_system_prompt.txt, harness/prompts/b1_system_prompt.txt, harness/prompts/b2_system_prompt.txt, tasks/oracle_t3.py, test_run_block.py, fixture_executor.py.

**Effect on the pilot:** the three pilot episodes ran under the v3 TASK.md and are **excluded from the block** (label `PRE_V4_PILOT`). Re-scored with the v4 scorer against the unchanged oracle, only B2's `best_config` moves (0 -> 1); the pilot is reported as a verifier defect finding, not as arm evidence. Stage 1 is repeated under v4 before block sizing.

**Not changed on purpose:** the oracle's conventions themselves (unshuffled folds, 200-step GD). Changing them to a converged solver would make the "correct" answer depend on solver tolerance; stating them makes the task answerable as posed.

**Budget:** screening $0.300209 / $48.47 spent on the pilot; dry run $1.090033 / $2.00.

v3 digest: `05d67c0d1b61f23ab4c17789291f495a7c8555d011b3615b9dc9a3293a2c8fca`.
