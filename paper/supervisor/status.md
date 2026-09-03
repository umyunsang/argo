# status (argo-paper-root)

goal: `661de7ea-39d8-4d81-8284-d41edff45288` status=**active** budget=none
orx_node: `c11c76ef-640e-4de7-8046-0507b163fa71` — 클린 클론 done (`c0777239` @ `930f0db06`)
orx_runs_this_cycle: 3
exa_calls_this_cycle: 2 — **exa 복구됨**(401 해소, web_search_exa 2회 성공). 결과 가치는 낮아 인용하지 않음.
study_b_spend_to_date: **$14.42** (드라이런 1~3차 $1.09 / 상한 $2.00, 스크리닝 $5.02 / 상한 $48.47; 파일럿 $0.30 + T3 v4 seed 0..10)
block_progress: T3 seeds 31/40 완결 (77.5%), 현재 seed 31 진행 중, 예상 완료 시각: 오늘 21:50 KST (seed당 평균 약 3.8분)
prereg_sealed: **yes** — v4 `0325ce9fb92f` (seal_commit `5d9c0d088`, 16개 파일; v1·v2·v3 superseded, instruction-0015b 반영)
hackathon_materials: v4 하네스(b0_tools.js / b2_harness.js, manipulation-check receipt) 기준 갱신 완료 상태. 접수(09-07)는 사용자 행위 권한.
results_origin_list: **없음.** N=40 완결 전 중간 분석 금지(동결 규칙); 원고 표 `tbl-studyb-status`의 결과 열은 블록 완결 후 분석 receipt에서만 생성.
## Completed in current phase

- **instruction-0015c 이행 완료:** §1 세션 모델 표기 일체 삭제(헤더 및 Q-0010 철회 반영). §2 블록 범위 부록 검정 방향을 v4 봉인 사양대로 '양측'으로 정정. §3 동점(쌍 차이 0) 처리 사양 v4a(pratt 채택, scipy 1.17.1) 및 analyze_block.py 스크립트·단위테스트 작성 및 protocol 봉인 sha 추가. §4 block_driver.py(래퍼) 커밋 반영.











### 사이클 (RD-96A) — 스크리닝 1단계 v4 재실행 완결 및 T3 블록 규모 확정 (N=40)

- **v4 재실행 결과 (T3 seed 0):**
  - B0 (`8e815dee`): **5/5 만점**, $0.129302, 54 s, 314k tok, bash 2·read 2.
  - B1 (`fb9f9569`): **5/5 만점**, $0.199258, 82 s, 724k tok, ipython 9·read 3.
  - B2 (`d7695483`): **5/5 만점**, $0.211856, 93 s, 863k tok, graph 6·decisions 1·thresholds 4·loop 4·ipython 7.
  - 조작 검사 3/3 PASS, 봉인 코드 동일성 3/3 검증 완료.
- **RD-95A falsifier 검증 판정:** **미발화 (정상 통과)**. 오라클 규약이 과제문에 명시되고 의미 채점이 적용되자 세 아암 모두 만점을 획득함. 오라클 결함 가설 기각, T3 과제 유지.
- **실측 단가 및 예산 현황:**
  - v4 triple 실측 단가: **$0.540416** (B0 $0.129, B1 $0.199, B2 $0.212).
  - 누적 스크리닝 지출: **$0.840625 / $48.47** (잔여 $47.629375).
- **블록 규모 결정 (`RD-96A`):**
  - T3 단일 과제에 전체 잔여 예산(88 triples)을 소진하지 않고, **N=40 triples (seeds 0..39, 총 120 에피소드, 예상 ~$21.62)**로 확정.
  - 잔여 예산(>$25)은 T1/T2 또는 강건성 검정용으로 보존.
  - 실행 순서: 엄격한 seed 순차 (seed k: B0 -> B1 -> B2).

### 사이클 (RD-95A) — 스크리닝 1단계 파일럿: 세 아암 1/5, 원인은 T3 검증기의 미명시 규약

- **파일럿 실행(기판 내, 실제 지출):** T3 seed 0, B0 `e23f60e8` $0.183918 (656k tok, 88 s, bash 7·ipython 0) → B1 `10c8db47` $0.040690 (36k tok, 52 s, ipython 5) → B2 `40bcbfbf` $0.075601 (122k tok, 95 s, decisions 3·thresholds 3·graph 8·pivot 1). Triple **$0.300209**; 조작검사 3/3 PASS; code identity 3/3 = v3 봉인.
- **결과:** 세 아암 모두 5항목 중 **1개** 통과. B0·B1은 `best_lambda=10.0`, `t=2.1167`로 소수점까지 같은 오답 — 아암 차이가 아니라 검증기 신호.
- **원인 추적(재현 프로브, seeds 0–4):** 오라클은 비셔플 연속 폴드 + **200스텝 미수렴 GD**로 적합하는데 TASK.md는 어느 것도 말하지 않았다. 수렴 솔버(lbfgs)는 best_lambda를 2/5 시드에서 다르게 고르고 improvement를 7배로 낸다(0.062 vs 0.007). `best_config`는 정확 문자열 `sparsity20_bits4` 요구라 세 아암 전부 **철자만으로** 탈락(`sparsity_20_bits_8`, dict, `sparsity=20%_bits=4`).
- **판단:** 이 상태의 블록은 "검증기의 사적 규약을 맞혔는가"를 재므로 사전등록 엔드포인트가 아니다. **블록 지출 보류.**
- **수정(과제 어댑터만, failing-first 37/37, 변이 4/4 적발):** TASK.md에 폴드·최적화 궤적·갱신식·압축 절차 명시; `best_config`는 (sparsity%, bits) 쌍으로 의미 채점(`parse_config`), 다른 쌍·파싱 불가는 여전히 실패. 오라클 규약 자체는 바꾸지 않음(수렴 솔버로 바꾸면 정답이 tolerance에 의존).
- **v4 재봉인** digest `0325ce9fb92f` (초기 중간 다이제스트 `c9b69d25463e`에서 run store commit 조회 로직 반영 후 최종 봉인): 변경 파일 `tasks/run_t3.py` 하나, 15개 바이트 동일. 파일럿 3건은 `PRE_V4_PILOT`으로 블록 제외(v4 채점기로 재채점 시 B2 best_config만 0→1; 아암 증거로 쓰지 않음).
- **예산:** 스크리닝 **$0.300209 / $48.47**, dry run $1.090033 / $2.00. 실측 triple 단가 $0.30 → 잔여로 산술상 160 triple이나, 규모는 v4 재실행 단가로 확정.

### 사이클 (RD-93A·94A) — 봉인된 run command가 실행 불가였다; v3 재봉인, 첫 기판 내 실행 dry run

- **결함:** v2가 봉인한 `run_block.py`는 전제조건만 검사하고 `PRECONDITIONS_OK`·exit 0으로 끝났다. 실행기를 import하지도, 모델을 호출하지도, `--out` 영수증을 쓰지도 않았다. **v2 아래서 스크리닝을 띄웠다면 333개 노드가 전부 "성공"하고 아무것도 남기지 않았을 것이다.** 스크리닝 지출 전에 발견(스크리닝 $0.00).
- **계획 밖 지출 $0.085264:** 실행 경로를 붙인 직후 기존 테스트의 긍정 검사가 `ORX_RUN_ID=probe`(위조 문자열)로 실제 B2/T3 에피소드를 실행했고, `/tmp` 경로의 `relative_to` 크래시로 영수증이 사라졌다. 사용량 파일에서 복원해 원장에 **불인정 지출**로 계상, 전사본 보존.
- **수정 3건(전부 failing-first, 24/24, 변이 7/7 적발):** ① 기판 id는 실제 run 디렉터리로 해석돼야 한다(문자열만으로 통과 불가). ② 실행기는 이름으로 주입; 기록기로 만든 영수증은 `FIXTURE_NOT_A_MODEL_CALL`로 라벨돼 모델 호출로 통과 불가. ③ 에피소드마다 영수증을 쓰고 예외·hard kill(os._exit)에서도 지출 에피소드가 디스크에 남는다.
- **3차 dry run(기판 내, 실제 모델):** run `2727d134`, 스냅샷 `ce2bc723a`, B2/T3 1 에피소드, 81 s, **$0.178769**, 조작 검사 PASS, `BLOCK_COMPLETE`. 발견된 2차 결함: 기판이 `.git` 없는 스냅샷을 돌려 `harness_commit=""` → 바이트 유도 blob id `code_identity`로 대체(tree blob과 일치하는 테스트 포함). 전사본의 기판 경로 접두어는 엔진명을 담아 `<RUNS_ROOT>`로 치환(REDACTION.json에 개수 기록).
- **v3 재봉인:** 변경 파일은 `run_block.py` 하나, 나머지 13개 봉인 파일은 v2와 바이트 동일. 가설·엔드포인트·분석·아암·프롬프트·과제 불변. digest `05d67c0d1b61`. 변조 프로브 2종 발화, 복원 PASS.
- **예산:** dry run **$1.090033 / $2.00**, 스크리닝 **$0.00 / $48.47**. B2 단독 단가 $0.130→$0.145→$0.179로 v2 추정($0.1454)보다 높을 수 있어 스크리닝 규모는 첫 실행 triple 단가로 재산정한다.

### 사이클 (instruction-0015 §3·§4) — 설계공간 문헌 검증과 그래프 확장, 그리고 스키마 게이트 신설

- **§3 문헌 검증 (16종):** `orx discover openalex/keyword`로 위치. **처음엔 16/16 "검증"으로 나왔지만 그건 내 오류였다.**
  - 부분 문자열 충돌 2건: `CodeAct`가 무관한 "Code Adaptive Compute-efficient Tuning"과, `GraphOfThoughts`/`GraphRAG`가 원 논문이 아닌 별개 연구와 매칭됐다. 재검색으로 CodeAct는 정정(`arxiv.2402.01030`), GraphRAG·GoT는 **별개 연구로 분류**하고 계열 존재 근거로만 쓰도록 제한했다.
  - `CORE-Bench`는 두 원시 검색에서 **위치하지 못했다** → 인용하지 않고 `source_id='NOT_LOCATED'` 노드로 검색 시도 사실만 기록.
  - 최종: **VERIFIED 13 / VERIFIED_DIFFERENT_WORK 2 / UNVERIFIED 1**.
- **§3.6 결정 (`RD-90A`):** 왜 자동 설계 탐색(ADAS·AFlow·AgentSquare·DSPy)이 아니라 고정·사전등록인가 — 탐색을 함께 열면 최적화 책임과 하네스 책임이 분리되지 않고, 결과를 본 뒤 설계가 바뀌어 사전등록이 무너지며, 시드마다 구성이 달라져 귀속·회계·재현이 붕괴한다. 절제 아암이 탐색 대신 귀속을 제공한다.
- **§4 그래프 확장:** `material:*` 7개(각각 메커니즘·아암·근거 결속), `prototype:argo`, `event:prototype_competition`, 검증 문헌 16개 소스 노드, 결정 사슬. 노드 473·엣지 850.
- **§4 필드 보장:** component 5종에 `description/implementation_path/tested_by/usage_metric` 채움. 7개 재료 메커니즘은 definition·falsifier·implemented_in_arm·removed_in_arm·**sources 3~8편(요건 ≥2)** 모두 충족 확인.
- **§4 스키마 게이트 신설:** `experiments/study_a/graph_schema.py` + 테스트 11건, **변이 7건 중 7건 적발**( dangling edge·중복 id·요구 필드 누락·고아 허용·stale 허용·tier 승격·tier 개명). 검증기 `paper_validate.py`가 이 모듈을 호출해 **하나의 정의**만 쓰도록 했다.
- **강제와 측정의 분리:** 중복 id·끊긴 엣지·`summary/status/next_action` 누락·정당화되지 않은 고아는 **차단**. `evidence` 누락 112건은 **측정 보고**만 한다 — 빈 증거 자리에 값을 넣는 것은 발명이며, 이 논문이 제거 대상으로 지목한 결함 그 자체이기 때문이다.
- **지시 충돌 2건을 발견해 기록했다:**
  1. `RD-91A`: §4가 요구한 노드 id `hackathon:nais_2026`은 공개 게이트가 금지한 어휘를 담고 있다(경로 안의 `hackathon`까지 검출). 게이트를 완화하는 대신 노드를 일반 정체성으로 바꿨다.
  2. §4의 요구 필드 보장을 위해 소스 노드를 추가하자 `source_metadata` 검증이 `None` 키(JSON 라운드트립 실패)로 깨졌다. 미위치 노드에 `NOT_LOCATED` 센티넬을 부여해 해결했다.
- **인용 수준 정직성 (`RD-92A`):** 신규 문헌은 전부 `METADATA_LOCATED_NOT_READ`. 제목·식별자만 확인했고 전문을 읽지 않았으므로 **본문 주장의 근거로 쓸 수 없다**는 제약을 노드와 표 헤더에 명시했다.

### 사이클 (instruction-0015a 검수 보정) — 봉인 정합성 1–5 닫음

- **§1 시각 오기 (실제 결함, 수정):** `sealed_at`·v2 작성 일시·cost-ledger 2차 드라이런 3행이 전부 `15:33:26`이었다. 원인은 **하나의 `nowr` 변수를 사이클 초반에 계산해 20분 뒤 사건들에 재사용**한 것. 각 항목을 실측 mtime으로 교체했다 — B0 15:42:12, B1 15:43:33, B2 15:46:00, v2 문서 15:52:57, 프로토콜 등록 15:54:17. `15:33:26`은 §1.6 점검 시각으로만 남겼다.
- **§2 B0 봉인 blob ≠ 실행 blob (판정: 무변경):** mtime이 실행보다 나중인 이유는 내용 수정이 아니라 **내 봉인 변조 탐침이 원본 바이트를 되썼기** 때문(되쓰기는 내용을 안 바꾸나 mtime은 바꾼다). 증거는 파일시스템이 아니라 실행 잔존물에 있다: `b0_tools.js`의 초판은 `execute()` 안에서 `{tool, path}`를, 채택판은 `tool_call` 인터셉터에서 `{tool, input}`을 기록한다. **B0 로그 12건이 전부 `input` 형식** → B0는 채택판(=현재 커밋본)으로 실행됨. 기능 변경이 아니므로 재실행하지 않는다. 교훈을 v2에 남겼다: 봉인 파일 탐침은 사본에서 하거나 다이제스트 동일성을 함께 기록해야 한다.
- **§3 seal_commit:** v1의 `9eeabc9e2`에서 봉인 커밋으로 갱신(아래 커밋 후 기록).
- **§4 집계 기준 (재현 가능하게 확정):** receipt 수치는 `tool_call` 인터셉터가 호출당 1건 기록. 원시 transcript는 `tool_execution_update` 스트림 때문에 과다 계상된다. **toolCallId 중복 제거 = manipulation_log = receipt**가 세 아암에서 정확히 일치했다(B0 read3/bash8/write1, B1 ipython5/read3/bash1/write1, B2 ipython7/graph_add6/threshold4/loop4/decision3/bash3/read2/write1). 결정적 성질: **B0의 ipython은 어떤 기준에도 키 자체가 없다** → 판정은 집계 기준에 의존하지 않는다.
- **§5 status 꼬리:** stale한 `next_first_action`(0014a 대기)을 현재 단계로 교체. (세션 모델 기재 요구는 instruction-0015c에 따라 철회됨).

### 사이클 (Study B 하네스 구현·2차 드라이런·v2 재봉인) — manipulation-check 3/3 PASS 및 투명 재봉인

- **배경:** instruction-0015 지적에 따라, 1차 드라이런에서 B0에 ipython이 누출(328회 언급)되고 B2 메커니즘이 프롬프트 텍스트로만 존재했던 manipulation check 실패를 인정하고 전면 재구현.
- **§1 실제 하네스 구현:**
  - **프롬프트 분리:** `--system-prompt`를 파일(`prompts/b{0,1,2}_system_prompt.txt`)에서 분리 주입. 과제 텍스트(`TASK.md`)는 사용자 턴 메시지로 전달(sha256 `d2e232f8...` 세 아암 간 100% 바이트 동일).
  - **B0 (최소 도구):** `--no-builtin-tools`로 `ipython` 원천 박탈. `b0_tools.js` extension으로 최소 도구(`read`, `write`, `edit`, `bash`)만 제공.
  - **B1 (표현력 REPL):** B0 도구 + `ipython` 활성화.
  - **B2 (책임 복합):** B1 도구 + `b2_harness.js` extension 탑재. `graph_add`/`graph_query` 도구, `decision_record`/`threshold_register` 도구, `loop_evaluate` 도구. 6필드 결정과 임계 등록 전 `bash`/`ipython` 실행 시 tool_call 인터셉트하여 즉시 차단(fail-closed).
  - **오염 격리:** 워크디렉토리를 `/tmp/study_b_dryrun2/...`로 격리, `PRIME_AGENT_CODING_AGENT_DIR=/tmp/clean_agent_dir`로 글로벌 continual harness 주입 100% 차단.
  - **테스트:** `test_extensions.py` 17/17 PASS, `test_episode_runner.py` 9/9 PASS.
- **§1.5 manipulation-check 3/3 통과 실측 (2차 드라이런):**
  - **B0:** ipython 호출 **0회**, 원시 도구 12회(`read` 3, `bash` 8, `write` 1) -> **PASS**. 비용 $0.170 (636,485 토큰).
  - **B1:** ipython 호출 **5회**, 파일/쉘 5회 -> **PASS**. 비용 $0.156 (505,061 토큰).
  - **B2:** 게이트 차단 **1회** (사전 등록 전 실행 시도 차단 실증), 이후 결정 3건(`decision_record`)·임계 4건(`threshold_register`) 등록, 그래프 노드 6건 추가(`graph_add`), 평가 4회(`loop_evaluate`), ipython 7회 정상 허용 -> **PASS**. 비용 $0.110 (213,698 토큰).
  - **2차 드라이런 지출:** $0.436. 누적 드라이런 지출 **$0.826** (드라이런 상한 $2.00 이내, $1.174 잔여). 스크리닝 지출 $0.00.
- **§2 사전등록 v2 투명 재봉인 (`study-b-preregistration-v2.md`):**
  - 스크리닝 지출 $0.00 상태의 투명 pre-data amendment. v1(f8671c44f076) 보존 및 대체 사유 명시.
  - 바닥효과 해소: 1차 지표를 검증기 항목 단위 통과 비율(`score.n_pass / score.n_total`)로 개정, 동일 (task, seed) 쌍대 Wilcoxon 부호순위 검정 채택.
  - 재산정 단가($0.1454/ep) 반영: $48.47 상한 내 과제당 n=37쌍 확정.
  - 14개 인프라 및 아암 파일 git blob sha1 봉인 완료 (다이제스트: `52939b05b166`).
  - 봉인 게이트 훼손 탐침 3건(b0_tools 변조, v2 문서 변조, 프롬프트 파일 삭제) 전부 즉시 발화 확인.
- **결정 기록:** `RD-2026-09-03-89A`.

### §1.6 하네스 오염 점검 보고 (instruction-0015 §1.6 이행)

- **점검 시각:** 2026-09-03T15:33:26+09:00
- **점검 대상:** 1차 드라이런 전사 3종(`B0_T3`, `B1_T3`, `B2_T3`), `prime-agent` 기본 런타임 환경, 격리 차단 플래그.

#### 1. 발견된 오염 실태 (실측 증거)
1. **글로벌 Continual Harness 및 프롬프트 주입 확인 (심각):**
   - 워크디렉토리가 레포 내부(`paper/experiments/...`)이고 별도 격리 플래그가 없을 때, `prime-agent`가 `~/.prime/agent/harness/harness_state.json`을 기본 로드하여 **프롬프트 노트 2건(ARGO pause 규칙 등), 글로벌 메모리 41건(ARGO 마이그레이션 정체성 등), 서브에이전트 1건, MCP 서버 2개(exa, parallel)**를 에이전트 시스템 프롬프트에 자동 주입함.
   - 격리 프로브 에이전트 질의 결과: 에이전트가 "AGENTS.md 위치, ARGO가 Prime Agent 포크 마이그레이션이라는 점, pause 상태"를 그대로 인지하고 답변함.
2. **B0 아암의 ipython 누출 및 조작 실패 확인 (심각):**
   - B0 전사에서 `ipython`이 328회 언급되었으며, Line 29에서 모델이 실제로 `ipython` 툴콜을 실행함.
   - 원인: `prime-agent`의 유일한 내장 툴이 `ipython`(`BUILTIN_TOOL_NAMES = ["ipython"]`)이며, 프롬프트로만 "네 가지 원시 도구만 쓰라"고 지시했으나 API 레벨에서 `ipython` 툴 정의가 전달되어 모델이 이를 호출함. 즉 조작이 프롬프트 수준에 그쳤고 툴 수준에서 분리되지 않음.
3. **B2 메커니즘 부재:**
   - B2 전사에서 `graph_add`/`graph_query` 툴콜 0회, 6필드 결정 게이트 인터셉트 0회. 텍스트로만 존재함.

#### 2. 격리 차단 검증 완료 (해결책 실측)
1. **컨텍스트 파일 및 레포 격리:**
   - `--cwd /tmp/study_b_workdir/...` (레포 외부 임시 경로로 완전 격리)
   - `-nc` (`--no-context-files`): 레포 상위 `AGENTS.md`, `CLAUDE.md` 탐색 원천 차단.
   - `-ne -ns -np`: 확장, 스킬, 프롬프트 템플릿 탐색 차단.
2. **글로벌 Continual Harness 차단:**
   - `PRIME_AGENT_CODING_AGENT_DIR=/tmp/clean_agent_dir` (auth.json만 존재) 설정 시 실측:
     `prompt: 0, memory: 0, skill: 0, subagent: 0, recent refinements: 0`으로 글로벌 주입 100% 차단 확인.
3. **아암별 툴/게이트 실측 분리 설계 확정:**
   - **B0:** `--no-builtin-tools` (`ipython` 원천 제거) + 최소 원시 도구(`read`, `write`, `edit`, `bash`) extension 탑재.
   - **B1:** B0 + `ipython` 활성화.
   - **B2:** B1 + TypeScript extension으로 도구 수준 `graph_add`/`graph_query` + 6필드 decision 미등록 시 실행 차단 fail-closed 게이트 인터셉트.

### 사이클 (Study B 파이프라인 드라이런) — B0·B1·B2 3아암 모델 엔드투엔드 실행 및 검증 완료

- **실행 목표:** instruction-0014a 승인 시나리오 (a)($48.47 상한)에 들어가기 전, $2.00 드라이런 상한 안에서 세 아암(B0, B1, B2)의 모델 호출·도구 실행·답안 작성·검증기 채점·비용 파싱이 엔드투엔드로 작동하는지 실측 검증.
- **실행 기판 결속:** orx 실험 노드 `2440f1b7-01bc-4b2c-9d16-f86da6c42168`(`study-b/B2/T3`)에서 run `0626325a-bd4f-480b-a366-336b420fc869`로 기판 안에서 실행되었으며 `orx.db` 영수증 검증 통과.
- **아암별 실측 결과 (과제 T3, 시드 42, 모델 claude-haiku-4-5):**
  - **B0 (최소 도구):** 55.7초, 405,799 토큰, **$0.133588**, answers.json 제출, 검증기 1/5 통과
  - **B1 (표현력 REPL):** 67.1초, 391,973 토큰, **$0.137553**, answers.json 제출, 검증기 2/5 통과 (best_lambda, interaction_helps)
  - **B2 (책임 복합):** 99.9초, 547,290 토큰, **$0.118492**, answers.json 제출, 검증기 1/5 통과
  - **드라이런 총 지출:** **$0.390** (드라이런 상한 $2.00 대비 $1.610 잔여)
- **비용 계측 결함 발견 및 수정:** `prime-agent` 기본 텍스트 모드에서는 토큰/비용이 출력되지 않아 0으로 파싱되던 결함을 발견하고, `--mode json` 이벤트 스트림의 `message_end` 어시스턴트 사용량 레코드를 파싱하도록 `episode_runner.py`를 정밀화하여 정확한 토큰수와 달러 비용을 실측 파싱함.
- **결과 격리:** 0013 §4.4 규칙에 따라 이 드라이런 결과는 `evidence_level: PIPELINE_DRY_RUN`으로 라벨하고 논문 결과표에 산입하지 않음(`tbl-studyb-status` 결과열 미실행 유지).
- **결정 기록:** `RD-2026-09-03-88A` (Study B 파이프라인 드라이런 실측 검증 및 격리).

### 사이클 (감독자 재기동 후) — 봉인이 실제로는 검사하고 있지 않았다

- **클린 클론이 처음으로 봉인에서 실패했다.** 로컬은 arm 4개 전부 일치, 클린 클론은 **4개 전부 불일치**. 같은 파일인데 결과가 정반대였다.
- **원인:** 봉인 검사가 blob id를 버전관리 도구에 물어봤다. 검증 사본에는 `.git`이 없어 명령이 실패하고 id 표가 비었으며, 그 결과 **모든 arm이 변조된 것처럼** 보고됐다.
- **더 나쁜 점:** 진짜 변조와 도구 부재가 **같은 메시지**를 낸다. 즉 이 검사로는 둘을 구분할 수 없었고, 봉인이 도입된 이후 모든 검증 실행을 막고 있었다. 봉인은 통과한 적이 **한 번도 없다**.
- **고친 방식:** blob id를 파일 바이트에서 도구와 같은 구성으로 직접 계산한다. 저장소 메타데이터에 의존하지 않는다. arm 파일 부재는 내용 불일치와 **다른 메시지**로 보고한다.
- **변조 탐침 3건 모두 발화 확인:** arm 파일에 한 줄 추가, 봉인된 사전등록 편집, arm 파일 삭제.
- `RD-2026-09-03-87A`.

### 사이클 (감독자 재기동 후) — 세션 상태 오염을 되돌리고 게이트 공백을 닫았다

- **먼저 저장소 상태를 확인했다.** 세션 문맥이 압축된 뒤 내 작업 변수가 오래된 상태를 가리키고 있었고, 그 상태로 쓴 편집이 `context-graph.json`과 결정 원장의 **round77 레코드를 덮어썼다**. `git diff`로 확인한 뒤 두 파일만 `git checkout`으로 되돌렸다. 실제 RD-77A(정본 전환·인용 95건 달성)는 그대로 보존됐다.
- **교훈:** 재기동 뒤에는 기억이 아니라 `git log`·`git status`·`status.md`를 먼저 읽어야 한다. 나는 이미 끝난 작업(인용 이관)을 다시 하려 했다.
- **exa 복구:** `web_search_exa` 2회 성공. 401이 해소됐다. 다만 결과가 일반 블로그 수준이라 인용하지 않았다.
- **실제로 닫은 공백:** `public_output_gate`의 `instance_identity` 패턴이 **이전 인스턴스 이름만** 담고 있었다. Study B는 호스팅 런타임을 쓰고 환경 프로브가 그 호스트명과 계정명을 출력한다. 이 식별자를 막는 패턴이 **하나도 없었다**.
- **현재 유출은 0건**이다(원고·산출물 0, supervisor 전용 노트 2건뿐). 즉 결함은 출력이 아니라 **가드**에 있었다.
- `runtime_host_identity` 패턴을 추가하고, 원고에 호스트명을 넣어 **게이트가 실제로 실패하는지 확인한 뒤 되돌렸다**.

### Cycle 59 — the manipulation is not inert; the endpoint is blind

- **Gap picked:** a near-zero condition component has two very different explanations. Cycle 58 could not tell them apart.
- **Executed:** for every per-episode quantity on the 15 admissible episodes, the share of variance lying between condition means within a task.
- **Process quantities separate the conditions sharply** — interface calls **0.899 / 0.951**, context tokens **0.915 / 0.925**, marginal tokens 0.845 / 0.896, cost 0.771 / 0.936.
- **Artifact quantities separate weakly** — artifact size **0.367 / 0.702**, structural gap count 0.443 / 0.657.
- **Judged coverage separates them not at all** — 0.009 and a clamped zero.
- **The process figures are read as a manipulation check, not a result.** A condition supplying more context and access makes more calls by construction. Promoting one to primary endpoint was explicitly rejected: it would report the manipulation back as if it were a finding.
- **Two readings remain alive and the design cannot separate them:** the conditions do not change artifact quality, or the endpoint cannot see the change. The falsified retrieval filter and the near-zero condition component both sit on the second branch, which is reason to suspect the instrument before concluding anything about the conditions.
- Claim checks 58.

### Cycle 58 — sizing rebuilt with the instrument as a facet, and the arm abandoned

- **Built the replacement:** `experiments/study_a/gstudy.py` with `test_gstudy.py` — a crossed condition x method x element variance decomposition and decision study. **32 checks; 11 of 11 mutations caught** after 5 survivors forced exact-arithmetic fixtures (the analytic value of the condition component, divisor-by-divisor error variances, explicit degrees of freedom, and a residual pinned against an independently computed sum of squares).
- **Applied per task**, because anchor elements are task specific and pooling would manufacture degrees of freedom.
- **The condition carries almost none of the endpoint variance:** **0.9%** of the clamped total in K5, and a **negative estimate clamping to zero** in K6. Element difficulty is **47.9%** and residual **37.1%** in K5; residual is **50.5%** in K6.
- **Dependability as run is 0.040 and 0.000**, and no element count within a cap of 400 reaches 0.8 — more measurement cannot enlarge a signal estimated at zero.
- **A block size was the wrong question.** The quality arm cannot be repaired by adding episodes. Either the endpoint changes or no condition claim is available from it. `RD-2026-09-03-53A/54A` now carry `SIZING_ABANDONED`.
- **Precision caveat stated, and it does not rescue the arm:** four conditions leave the condition component three degrees of freedom, and negative components mean quantities small relative to sampling error, not quantities known to be zero.
- **Gate caught me mid-cycle:** two shares were bound as percentages against fractions in the receipt. Rather than add a scale transform that would loosen every binding, the percentages are now stored explicitly. Claim checks 55.

### Cycle 57 — the design target was sized on the smaller half of the problem

- **Gap picked:** if the scoring method moves the endpoint by 2.3x the detectable effect, whether that detectable effect still means anything had to be checked.
- **It does not.** Across the eight artifacts the method difference has **sd 0.301**, about **3.65x** the detectable effect of 0.0825, and the variance of that difference is **1.48x** the variance of the coverage being measured. The instrument varies more than the thing it measures.
- **It cannot be corrected away.** The difference changes sign, from **-0.167 to +0.667**, so no constant adjustment recovers the earlier number.
- **The paired detectable effect is void as a design target.** It was computed with the scoring method treated as fixed, so it omits a variance component larger than the one it used. `RD-2026-09-02-15B` and `RD-2026-09-02-33A` carry that status.
- **What replaces it is named, not hand-waved:** sample-size planning must treat the scoring method as a facet with its own variance, as generalizability designs do. That replacement is not built, and the facet estimated here rests on eight artifacts judged by one model, so it needs its own measurement before it can carry a plan.
- Claim checks now stand at 50.

### Cycle 56 — the instrument moves the endpoint more than the effect it was built to find

- **Executed:** all 48 element judgements over the eight confirmation artifacts re-scored on the full artifact, compared with the span-based verdict on the same items.
- **Mean coverage rises from 0.542 to 0.729**, a shift of **0.188**. Seventeen of forty-eight verdicts change — **13 negative to satisfied, 4 the other way** — so removing retrieval is not simply a looser rule.
- **The size is the finding.** The paired detectable effect on this endpoint is **0.0825**, so the scoring method moves the reading by about **2.3x** the smallest effect the design was sized to detect. An instrument choice of that magnitude does not modify the comparison; it dominates it.
- **Per-condition coverage is deliberately withheld.** Two artifacts per condition cannot separate a condition from a task, and the shift is a property of the instrument, not of any condition.
- **Admissibility unchanged:** these verdicts remain inadmissible for scoring, because no human-anchored calibration set exists. They describe what the instrument reads, not what an episode scored.
- Claim checks now stand at 47.

### Cycle 55 — remove rather than repair, decided on measured numbers

- **Gap picked:** the endpoint drops about two in five true positives at the retrieval stage. Repair or removal had to be chosen, and costed.
- **Measured the cost both ways**, three items judged span-based and whole-artifact by the same judge in a mode that reports usage: **$0.02682** against **$0.04320**, a ratio of **1.61**.
- **Repair rejected on the shape of the failure**, not on cost. Three of the four no-span misses were a single element stated in wording the cues do not match, and poor spans fail at a similar rate, so widening cues trades one silent miss for another with no recall measurement to bound it.
- **Decision:** whole-artifact judging becomes the primary path; the cheaper span verdict is retained on a **20% subsample** as a drift check, so disagreement between the two stays visible rather than assumed away.
- **The trade is stated as a trade.** Full-artifact judging has no accuracy measurement of its own, so a measured, directional failure mode is being exchanged for an unmeasured one. That is defensible only because the removed one is quantified.
- **Projected quality-arm judging cost** for a 116-episode block: $18.67 span-only, $30.07 full-only, $33.80 with the subsample. This does not change `Q-0007`, which covers the completion arm and needs no judging at all.

### Cycle 54 — the other half of the failure, and the size of the bias

- **Gap picked:** only items where retrieval returned *nothing* had been checked. The larger case — a span returned but poor — was untested.
- **Executed:** all nine items where a span was returned and the verdict on it was negative, re-judged by both models on the full artifact.
- **A returned span is not protection:** 3 of those 9 are called satisfied by both judges.
- **Complete picture: 7 of 18 pipeline negatives overturn** under the wider view, and the failure is not concentrated where retrieval found nothing — no-span 4/9, poor-span 3/9.
- **The endpoint understates coverage at roughly that rate, always in the same direction.** That is a measured bias in the endpoint of record, not a suspicion.
- **One caveat bounds the whole measurement**, and it is in the paper: the reference is two-judge agreement on the full artifact, which is not ground truth. It shows the pipeline verdict is unstable under a wider view, not that the wider view is right. The falsifier is written accordingly — if human labels later side with the pipeline, the overturn rate does not indicate bias.

### Cycle 53 — testing the recorded limit broke the endpoint assumption

- **Gap picked:** the previous cycle recorded that both judges saw the same retrieved spans, so a shared retrieval failure would look like agreement. That limit was tested rather than left standing.
- **Executed:** the nine items where cue retrieval returned **no span** — scored `not_satisfied` without any model call — were re-judged by both models on the **full artifact**.
- **Result:** both judges call **4 of 9** satisfied; at least one calls **5 of 9**. The agreement on those items was a shared retrieval failure, not a judgement.
- **This falsifies an assumption the endpoint rests on.** Cue matching was demoted to a *high-recall* candidate filter precisely so verification could do the deciding. A filter that misses at least four of nine makes the endpoint **understate coverage silently**, because no model is ever called on a miss.
- **Consequences applied:** a no-span result is now recorded as **unresolved**, not as a negative verdict; the retrieval step must have measured recall before the endpoint is used for scoring; and `RD-2026-09-02-14A` carries the falsified assumption.
- **Scope stated:** only items where retrieval returned *nothing* were checked. Items with a poor span could fail the same way and remain invisible.
- The earlier agreement figures are unaffected: the cross-judge replication had already excluded these nine from its denominator.

### Cycle 52 — the floor was tested on material it had never seen

- **Gap picked:** reliability was measured on the variance block. Reliability is a property of an instrument *on material*, so transfer had to be measured, not assumed.
- **Executed:** all 48 element judgements over the eight first-repeat confirmation artifacts, judged independently by two models from **different provider families**.
- **Raw agreement fell** to 0.667 from 0.703, because six items produced an unparsed verdict from one judge and are counted as **disagreements rather than dropped**. Excluding those: 0.788 with kappa 0.492, above the earlier figures.
- **The stratification replicated exactly** — and that is the result that matters:

| band | agreement |
|---|---|
| both above 0.9 | **12 / 12** |
| middle | 14 / 18 |
| below 0.7 | **0 / 9** |

- **The part of the instrument actually used held on unseen tasks.** Nothing here supports calling the judge reliable in general; below the floor the two judges disagree on roughly a third of items.
- **A limit is recorded that could inflate this:** both judges received the same prompt and the same retrieved spans, so a shared retrieval failure would look like agreement.

### Cycle 51 — auditing the paper against its own admission rule

- **Gap picked:** the admission rule made 48 episodes unscorable. Whether any manuscript claim still leaned on them, unmarked, had not been checked.
- **Executed:** every number in the body derived from those blocks was located and its surrounding paragraph checked for language marking the dependency. Eleven of thirteen numbers were already labelled.
- **Two were not:** the high-confidence reliability figures, 88.0% and 92.0%.
- **They do not need a downgrade, for a reason worth stating.** The admission rule refuses to **score an episode** whose usage was never measured. Reliability characterises the **judge** — how far a verdict reproduces on the same item — which the artifacts can support even when the episodes cannot enter a score.
- **The distinction is now in the paper**, not left to inference, so a reader can see why the variance components are provisional and these are not. Without it, both sets look equally supported.
- **A guard against stretching it** is recorded as the falsifier: if a reliability figure is ever used as an episode score or as evidence about a condition, the distinction is being abused and the figure must be downgraded.

### Cycle 50 — the executable arm is pre-registered and sealed

- **Gap picked:** the completion arm had a costed block size but no fixed analysis, so the analysis could still be chosen after seeing data.
- **Frozen before the data exists:** the document records that only 16 episodes existed at freeze, and names the confirmation receipt digest at that moment. Any block testing it must consist of episodes beyond those.
- **What it fixes:** the hypothesis and its null with **no direction taken from the pilot**; a two-sided Fisher exact test with alpha 0.05, chosen because counts are small and one arm sits near a boundary; the size and its source receipt; an exclusion rule that **explicitly forbids removing an episode for its outcome**; a stopping rule with **no interim looks**; the falsifier; and what the arm cannot show.
- **Only one arm was pre-registered.** Pre-registering the quality arm would fix an analysis that cannot be run, since it is blocked on human labels and an unbalanced design.
- **Sealed and gated:** the document carries its own digest, and once the block grows beyond 16 episodes any change fails the gate. Three failing-first mutations fire — removing the stopping rule, downgrading the status to draft, and adding an episode while the document is unsealed.
- **Honest limit recorded:** a preregistration written by the agent that will run and analyse the block constrains the analysis but does not make it independent. The seal proves the document did not change, not that it was wise.

### Cycle 49 — one half of the plan is executable, the other is blocked by one input

- **Gap picked:** completion had a costed block size; the quality endpoint had none.
- **It cannot be given one, and that is the finding.** A committed check walks each declared outcome and reports whether its block size is computable.
  - **Budget completion: planable.** 29 per condition, 116 episodes, about $18 — measured by the admission path with no judge in the loop.
  - **Design quality: not planable**, blocked twice. Judged scoring is inadmissible at **0 of 25** human-anchored labels, and the endpoint variance is **not estimable** from admissible episodes because the ceiling refusal left the design unbalanced.
- **The labels are the single binding constraint** on the entire quality arm, and nothing this loop can execute removes that dependency. Saying so is more useful than a block size resting on a variance the design cannot yield.
- **A receipt completeness defect was fixed:** the confirmation receipt listed only the first repeat, so the blocker was misreported as "one observation per cell" instead of "unbalanced". Both repeats are now listed with a per-episode admissible flag, and only admissible episodes may inform a plan.
- **11 fixtures, 5 of 5 mutations caught**, including "report planable despite blockers" and "let an inadmissible episode inform the plan".

### Cycle 48 — how much more measuring, computed rather than guessed

- **Gap picked:** the completion intervals are too wide to act on, and the choice was to extend the block or to state what extension is required.
- **Refused the cheap option.** A third repeat costs about a dollar and moves the half-width from **0.327** to roughly **0.29** — it would buy the appearance of progress and change nothing that can be concluded.
- **Computed the real requirement:** to reach a half-width of **0.15** at the lowest observed completion rate needs **29 episodes per condition, 116 in total**, at about **$18** using a cost per episode read from the executed receipt rather than assumed.
- **That is six times everything this project has spent on model calls.** Rather than drift toward it in small steps, `Q-0007` records the choice with a default of **not spending without approval**, and the loop proceeds on that default.
- **Committed as code, not a one-off:** 17 fixtures, 6 of 6 mutations caught — including "plan on a guessed cost when the receipt has none" and "use the highest rate instead of the lowest". One fixture was strengthened again after a removed guard still raised, from a square root of a negative number.
- Claim checks now stand at 40.

### Cycle 47 — the rate is reported, and the reading is refused

- **Computed** over the first admissible block, four episodes per condition: minimal, retrieval-only and scaffold-only all completed **4/4**; scaffold-plus-retrieval completed **3/4**.
- **Reported with denominators and Wilson intervals**, because the bare rates invite a conclusion the data cannot carry. Every interval spans more than half the range, the widest is **0.653** wide, and **all four overlap**.
- **Stated plainly in the manuscript:** four episodes per condition can show that a ceiling bound and where it bound; they cannot show that completion differs by condition. Small screening blocks read as settled questions can produce worse decisions than no block at all.
- **Kept separate from quality:** the quality endpoint is still not computed, because judged scoring remains inadmissible without a human-anchored calibration set.
- **Bound two-sidedly:** editing the rate in the prose alone and editing it in the receipt alone each fail the gate. Claim checks now stand at 37.

### Cycle 46 — budget failure became an outcome, and a stale name nearly corrupted the design

- **Gap picked:** refusals were being logged but not analysed, so a condition could look better simply by spending more and having its failures discarded.
- **Declared in the design document:** budget completion rate as a secondary outcome, computed by the same admission path that decides scoreability, reported **beside** the quality endpoint and never merged with it, with denominators stated. A refusal is a competing event for the quality endpoint.
- **The ceiling is explicitly not adjusted to remove refusals.** Moving a limit until it stops binding erases the asymmetry it revealed.
- **Timing recorded honestly:** this outcome was declared *after* the first refusal was observed. That is written into the design rather than concealed, and it is fixed now so later blocks cannot select it once the direction is known.
- **Near miss worth more than the cycle.** The insert used a variable name still bound from many cycles earlier, holding validator source code, because the assertion meant to stop the cell ran before the intended definition. About five thousand characters of Python went into the design document. It was caught when a membership check for the intended heading failed three times while writes were succeeding, repaired from the committed blob and verified against its committed digest.
- **Lesson recorded:** the working state of a long session is itself a hazard. No gate covers an uncommitted working file, so text blocks are now defined immediately before use and every insert is verified by reading the file back.

### Cycle 45 — the ceiling bound, and it bound on one side

- **Gap picked:** allocation could not be re-derived, because one repeat per cell leaves no residual term. The variance guard said so and refused, which is what it is for.
- **Executed:** a second repeat, 8 more episodes, completing a 2 tasks x 4 conditions x 2 repeats design. All 8 transcripts complete, zero canary leaks.
- **The declared ceiling bound for the first time.** One episode was refused at **18 calls against a limit of 16** — and it fell in the **full condition**, which uses the most calls in every single observation (C00 max 4, C01 max 10, C10 max 8, C11 max 18).
- **That is a selection hazard, not a nuisance.** A ceiling that binds asymmetrically removes episodes non-randomly, so dropping them would bias the comparison toward the cheaper condition.
- **Decision: treat violation as an outcome, not data loss.** If the full condition needs more calls, capping calls *is* the budget match, and the endpoint becomes completion within budget. The ceiling was **not** raised to make the refusal disappear, which would have hidden the asymmetry the measurement just revealed.
- **Consequence accepted:** the admissible set is now unbalanced at 7 against 8, so the variance guard again refuses to compute components. Both refusals are the guard working, not failing.
- Block cost $1.20; confirmation block total $2.46. GPU credit units remain 0.

### Cycle 44 — the first episodes that can actually be scored

- **Gap picked:** the confirmatory pipeline had never produced an episode admissible under its own rule.
- **Executed:** 8 episodes, 2 unburned tasks x 4 conditions, structured output mode so usage is measured. **8 of 8 admissible.** These are the first in the project.
- **Integrity:** transcripts complete 8/8, canary leaks **0**, fabrication redlines **0**, structural gaps in 5 of 8, anchors frozen before any artifact existed.
- **Cost:** $1.26 for the block; GPU credit units remain 0.
- **A visible pattern is recorded and deliberately not interpreted.** Structural gaps differ across conditions in this block, but two observations per condition cannot separate a condition from a task. A study that tested a mechanism where it ships found no detectable change despite earlier reports of large gains; that is the standard this block does not meet, and it has no preregistered hypothesis test.
- **No treatment effect is estimated.** Judged coverage is also not computed, because judged scoring stays inadmissible until a human-anchored calibration set exists.
- The evidence cycle was closed in the same turn: 803 files compared, all byte identical, anchor re-run and updated.

### Cycle 43 — back to the science: the confirmatory block had no tasks left

- **Gap picked:** four tasks are burned as development data and the other four were consumed by the variance block, so the confirmatory block had nothing disjoint to run on.
- **Executed:** two new tasks built from unseen recent studies whose experimental design is the withheld target — `K5-unlearning-stress` and `K6-harness-evolution`, six anchor elements each, two evidence files each.
- **Anchors frozen before any artifact exists**, and recorded as such with the instructions digest.
- **The cue check caught real leakage.** The first draft of the instructions pre-answered **five of twelve** scored elements, because the stated constraints named the design choices: a constraint mentioning a retain set gave away the retain-set control, one naming the fixed backbone gave away the frozen-backbone element, and the question itself named overfitting. Constraints were rewritten to define the setting without naming the choices; both tasks now leak **zero** cues.
- **Workspaces build and admit** in both the minimal and full conditions, with no canary in any released file.
- **Nothing has been run on them yet.** They exist so the confirmatory block has unburned tasks with anchors fixed in advance.

### Cycle 42 — closing the window without creating a rubber stamp

- **Gap picked:** staleness was detected but closed only in a later cycle.
- **The danger was the obvious fix.** A command that re-anchors after any run would silence the gate it exists to satisfy. So the anchor updates **only** when the claim level passed, every archive reached an acceptable status, and no file mismatched. A failed or partial run leaves it stale on purpose.
- **Four negative fixtures enforce that:** a failed claim level, a byte mismatch, a failed fetch, and a dry run must each leave the anchor untouched. 9 fixtures total; **5 of 5** mutations caught, including "re-anchor even when verification failed".
- **The run refused to pass, correctly.** One record — a versioned PDF — had no archive members and reported `INCOMPLETE_RECORD`. I completed the record by verifying its artifact digest and the derived text the quotations were cut from, rather than adding the incomplete status to the acceptable set. Widening the check would have been the easy fix and the wrong one.
- **Now closing in-cycle:** 132 archives, **787 files compared, 787 byte identical**, anchor re-run and updated after this round's own locators were added.
- **Honest limit:** the command and the gate share an author, so those negative tests are the only thing separating closure from silencing.

### Cycle 41 — the gate enforces the chain without needing a network

- **Gap picked:** byte-level verification was manual, so nothing forced it to be re-run.
- **The obvious move was wrong.** Running the network check inside the gate would make validation non-deterministic and fail for reasons unrelated to the work — which is how a gate becomes something people switch off.
- **Split by determinism.** The claim level is entirely local, so it runs on **every** validation: each locator's file digest and its excerpt hash at the recorded line range. The byte level records the **digest of the evidence base** it was run against, and the gate fails when that digest no longer matches.
- **Two staleness mutations fire:** corrupting one excerpt hash produced both a verification failure and a staleness failure; appending a locator produced staleness alone. Restoring returns to pass.
- **The contract bit immediately.** Adding this round's own locator made the byte-level receipt stale, and it had to be re-anchored before the gate would pass — the obligation is real, not notional.
- **Limit stated:** staleness is *detected*, not prevented, so a window exists between changing the evidence base and re-running the network check.

### Cycle 40 — the whole evidence base verified, not a sample

- **Gap picked:** byte-level verification covered 4 of 38 receipts, leaving the untested part exactly where a reader would look.
- **Executed across every receipt:** **130 archives** re-fetched and accepted only on a digest match, **782 files** compared byte for byte with their archive members. **782 identical, zero mismatches.**
- **One record is a versioned PDF with no members.** It was reporting `NOT_AN_ARCHIVE`, which reads like a failure although its digest had already been verified. It now reports `DIGEST_VERIFIED_NO_MEMBERS` — stating what was established and what was not, rather than sounding an alarm or hiding the gap.
- **Why not sample:** misalignment between a claim and its cited evidence is a common failure of model-generated reports, and this project generates its own citations, so a sample would leave the interesting part unchecked.
- **Limit unchanged and stated:** a re-fetch depends on the upstream service continuing to serve those exact versions.

### Cycle 39 — archive identity is not file identity

- **Gap picked:** the repair proved the *archive* was authentic; it did not prove the file in the repository came out of it.
- **Three levels, reported separately.** Claim: every locator's file digest and the excerpt hash at its recorded line range. Archive: accepted only on a digest match before anything is read. Byte: each committed file compared byte for byte with the same archive member.
- **Results:** **170 of 170** locators verify with zero file-digest and zero excerpt-hash failures. **27 archives** verified, **138 of 138** compared files byte identical, zero mismatches.
- **One record reported as incomplete, not verified:** a versioned PDF with no TeX members has no file list to compare, so it is excluded rather than counted as a pass.
- **7 fixtures, 6 of 6 mutations caught**, including two that would have reported success while checking nothing — treating an incomplete record as verified, and claiming verified while offline.
- **Coverage stated:** the byte level has been run over 4 of 36 receipt files. The rest are checkable by the same command and have not been run.

### Cycle 38 — the manifests asserted 190 files that were not there

- **Gap picked:** source receipts listed files whose existence had never been checked.
- **Measured:** 36 receipts, 127 records, **780 listed files**. **190 did not exist**, across 16 sources. No claim locator depended on any of them, but the manifests asserted their presence.
- **Repaired, not deleted:** every affected archive was re-fetched and accepted **only on a digest match**, then re-extracted. All 190 restored; zero missing afterwards. This also exercised the external-artifact policy on **16 sources** rather than the 4 spot checks recorded earlier.
- **Two conventions, both recorded.** Rewriting the lists to repository paths broke a receipt contract expecting archive member names; keeping member names left strings that look like repository paths. Both are now recorded, and the reference scan was made **structural** so it trusts the key rather than the shape of the string.
- **Failing-first check:** a placeholder value under a path-named key made the gate fire.
- **The clean clone caught the repair being incomplete.** Restoring the files locally left them uncommitted, because this worktree excludes the paper directory and only receipt-named files were being staged. The local run passed while the clean clone reported **298** dangling references. Tracked files under the source tree went from **484 to 782**, and the clean clone then reported zero. Restoring a file locally is not repairing the record.

### Cycle 37 — the rule was applied to the data that motivated it

- **Gap picked:** the new admission rule had never been applied to the blocks that produced the evidence for it. Exempting that data is how a rule becomes ceremonial.
- **Result:** of the **48** episodes in the pilot and variance blocks, **none is scorable**, for a single reason — their usage was never measured, so compliance cannot be shown. Only the **6** episodes run in structured output mode pass.
- **Nothing is retracted.** No score or effect was ever claimed from those blocks, and judged scoring was already inadmissible pending calibration, so the rule adds a second independent reason rather than overturning a claim.
- **What it does change:** the variance components and the allocation and minimum detectable effect derived from them are now labelled **provisional design inputs** taken from episodes that would not be admitted today. The confirmatory block must measure usage on every episode and re-derive its own allocation rather than inherit these numbers.
- **The reference gate caught a real ambiguity:** one upstream archive stores its sections under an internal directory named `paper`, so member names looked like repository paths and failed to resolve. Source receipts now record repository-relative paths, which removes the false reference *and* makes every listed file checkable.

### Cycle 36 — enforcement moved into the admission path

- **Gap picked:** ceiling violations were detected after the fact, which invites keeping a number that should not exist.
- **Executed:** the runner now records declared ceilings in the enforcer's vocabulary, and scoring is **refused** for five distinct cases: the episode did not execute, a pre-launch probe fired, its usage is unmeasured, it declares **no** ceiling at all, or it exceeds one. A non-integer ceiling is dropped at translation, which makes the episode inadmissible for lack of a limit rather than silently unlimited.
- **17 checks, 6 of 6 mutations caught** — after one fixture was rewritten. Its not-executed case was being blocked by a *different* guard, so deleting the execution-status check still passed. The receipt was made otherwise fully valid, and the mutation then fired.
- **All six measured episodes are scorable** under the retained ceilings.
- **Literature named the pattern:** production frameworks ship control primitives whose names imply barrier semantics but which do not stop anything — the failure this project has now met five times.
- **Retrieval note recorded:** the first candidate ranking returned mostly unrelated physics and mathematics records, so candidates were re-filtered on title relevance. The filtering step is recorded rather than hidden.

### Cycle 35 — the ceiling had no truth value until a quantity was named

- **Gap picked:** three declared ceilings enforced nothing. The choice was to implement or delete; I implemented.
- **Enforcement at admission,** since a provider call cannot be capped from outside. A committed module checks measured usage, **requires the quantity to be named**, and treats an unmeasured quantity as a violation rather than a pass. 16 fixtures, 5 of 5 mutations caught.
- **Applied to the six episodes with complete measured usage, the declared 32,000 gave opposite verdicts.** Read as **total tokens**: every episode inadmissible, exceeding by **4.7× to 20.3×**. Read as **marginal tokens**: every episode admissible, maximum **10,957**.
- **So the number had no truth value on its own.** The verdict is decided entirely by a quantity the protocol never named.
- **Total-token ceiling withdrawn**, not replaced with a guess, until it can be set from a measured distribution on the confirmatory task set. Marginal-token, call and wall-clock ceilings retained because measurement supports them.
- **Limit stated:** these maxima come from six episodes on one burned task and would not generalise.

### Cycle 34 — the declared ceilings enforced nothing

- **Gap picked:** the design constants were stated in prose and bound to nothing.
- **Derived, not restated.** Copying prose values into a receipt would have made the gate pass while proving nothing, so the constants were derived from the builder, the runner and the executed receipts.
- **The derivation contradicted the manuscript.** The paper described a *32,000-token ceiling, a 12 tool-call ceiling and a 45-minute wall time* as governing the work. All three governed nothing: the builder that produced every executed episode emits **no ceiling fields**, the runner only **type-checks** that a configuration declares them, and **no executed receipt records a token ceiling**.
- **What actually applied:** the pinned invocation at a fixed reasoning level with a **900-second** wall-clock limit and no token or call ceiling.
- **Corrected in the paper**, separating the specified confirmatory protocol from what the executed blocks applied, and the 900-second limit is now bound two-sidedly. 31 claim checks pass.
- **One source had no TeX**, so its text was extracted with the pinned `pdftotext` and the locator records that derivation rather than hiding it.

### Cycle 33 — coverage raised from 15 to 29 bindings, by refusing two

- **Gap picked:** only the headline numbers were bound; the reported figures in the results were not.
- **Executed:** 14 further two-sided bindings added, covering reliability, agreement, kappa, endpoint correlation, cost understatement, and the decision census. **29 checks now pass.**
- **Two candidate bindings were rejected, not forced.** One resolved to an episode *list* rather than a count and was rebound to a receipt that records the count. The other had no receipt field at all, and binding it would have required a wide tolerance around a different number — that is how a check stops checking.
- **Both directions still fire:** editing a reliability figure in the prose alone, and editing the same figure in the receipt alone, each fail the gate.
- **Coverage limit stated in the paper:** design constants and configuration ceilings stay unbound because no receipt records them. Partial and sound is preferred to complete and loose.

### Cycle 32 — the audit tool failed its own validity test

- **Gap picked:** only the abstract had numbers bound to receipts.
- **First attempt looked perfect and was worthless.** A matcher compared every body number against all 396 receipt values, allowing a factor of 100 either way, and reported **66 of 66 bound, zero unmatched**.
- **Then I tested the test.** Random numbers of the same shape were fed to the same matcher: it accepts **82.5%** of them. Expected matches under the null were 54.4 of 66, so the perfect score mostly measured how permissive the test was.
- **This is the same defect I falsified before**, in the same form: a high-recall filter presented as a decision procedure, exactly like the cue endpoint at a false-positive rate of 0.969. The matcher was rejected as a certificate.
- **Replaced by explicit two-sided binding:** a bound number names a receipt and a path, the rendered form must appear in the body, and the receipt must still hold the bound value. **Both directions fire** — changing the prose alone and changing the receipt alone each fail the gate.
- **Coverage is partial and said to be partial:** 15 checks bind the headline numbers; the rest of the body numbers are not individually bound.

### Cycle 31 — the abstract said the work had not been done

- **Gap picked:** the abstract was written before fifteen cycles of execution and never revisited.
- **It contradicted its own conclusions.** The abstract stated that "the pilot and confirmatory study have not been executed", while the conclusions of the same document reported three executed blocks. It also still named the endpoint that had been falsified.
- **Rewritten against the record:** the abstract now reports the three executed blocks, the falsified first endpoint at its measured false-positive rate of 0.969, the 14.4x cost-instrument understatement, the mutation audit that found four undetected fault classes, and the 28-decision census. It still states that no efficacy estimate exists and that judged scoring is inadmissible.
- **Gated, not just fixed.** Six checks now forbid non-execution phrasing while executed receipts exist and read headline counts from the receipts themselves. Three failing-first mutations all fired: reintroducing the non-execution claim, dropping the pilot episode count, and stating a wrong false-positive rate.
- **A duplicate source was caught by the commit guard.** This round re-ingested `arXiv:2608.25336`, which was already in the corpus under an existing bibliography key, producing a second locator, a second matrix row and a duplicate reference. The pre-commit validator refused on count mismatches; the duplicate was removed and the manuscript cites the existing entry.
- **Limit stated:** the gate checks only the numbers it is told about, so a new unbound claim in the abstract would still pass.

### Cycle 30 — a provenance hole, and a gate that verified nothing

- **Gap picked:** the path gate only covered experiment receipts. Extending it to the graph, protocol, locators and source receipts immediately found a dangling artifact.
- **Root cause is structural.** This checkout is a **linked worktree** whose shared exclude blocks the `paper/` directory, so files are tracked only when staged explicitly. Under that rule **911 paper files are tracked but zero source archives are** — every recorded archive path was absent from a clean checkout.
- **Resolution, not concealment:** upstream archives are external re-fetchable artifacts. The quoted evidence is committed as extracted text for **all 114** archives (419 tex files, 91 full-text and 114 report captures tracked). Every archive record must carry a fetch address and a digest.
- **Verified by re-fetch:** three archives and one PDF were re-fetched and reproduced their recorded digests **exactly**, including the originally missing PDF at 5,885,207 bytes.
- **My first gate verified nothing.** It scanned a character window around each reference, so a record could satisfy it by borrowing a neighbour's address and digest. The failing-first test stripped one record and **did not fire**. The check now walks the parsed structure so both must sit in the same record, and the same test then fired.
- **The clean clone caught two more gate defects.** The first version passed locally and failed in a clean checkout: the protocol's own prefix value matched as a reference, and an absent archive PDF was reported as both dangling and external. Both fixed, then re-tested by deleting the local PDF to reproduce the clean-checkout condition.
- **Limit stated:** a re-fetch depends on the upstream service still serving that version. The digest proves identity when a fetch succeeds; it cannot substitute for bytes if it does not.

### Cycle 29 — the analysis became code, and a dangling path surfaced

- **Gap picked:** the manuscript printed numbers produced by ad-hoc session work.
- **Executed:** the analysis is now a committed script with **22 fixtures** of three kinds — analytic cases whose components follow by construction, guard cases that must raise **with the correct cause**, and a regression case reproducing the earlier published receipt from the original record, an oracle that existed before the script.
- **Two implicit conventions are now explicit in the code:** coverage counts only an exactly satisfied verdict, and the effect uses the paired difference standard error.
- **Mutation audit: 5 of 5 caught**, but only after strengthening a guard fixture. One mutation removed the identifier guard and the code still raised, for a different reason, so the fixture passed. Guard fixtures now assert *why* an error was raised.
- **A dangling path reference was found.** A receipt named `paper/experiments/calibration/element-verdicts-corrected.json`, which does not exist; the real file is in the variance-block directory. A new gate scans **46 receipt files** for path strings that do not resolve, and was proven by reintroducing the bad path.
- **One source reviewed but not cited:** its TeX is a code-heavy conversion with no quotable prose, so no verifiable locator could be cut. Recorded rather than forced.

### Cycle 28 — the endpoint recomputed, and the check was wrong before the record was

- **Gap picked:** four verdicts changed, and the verified endpoint had been computed on the originals.
- **Validated the recomputation first.** A recomputation that has not reproduced the original is not a check. Running it on the original record reproduced the recorded variance shares and standard error exactly.
- **That step immediately paid.** The recomputed minimum detectable effect disagreed with the record, `0.0571` against `0.0808`. Deriving the quantity showed **the record was right and my check was wrong** by a factor of √2, because a paired difference of two condition means carries that factor. After the fix, every recorded value reproduced.
- **On the corrected record:** task share of variance rises **16.2% → 21.5%**, residual falls **83.8% → 78.5%**, condition and interaction remain **exactly zero**. Paired MDE moves `0.0808 → 0.0825`. Cue-versus-verified correlation falls `0.043 → 0.018`.
- **The structural conclusion is unchanged:** with zero interaction the standard error still does not depend on how a budget is split between tasks and repeats.
- **Limit stated:** four changed verdicts out of 192 is a small perturbation and says nothing about behaviour under a larger correction. The endpoint stays inadmissible for scoring until human labels exist.

### Cycle 27 — what confidence actually predicts, and a correction that carries its own counterevidence

- **Gap picked:** the modal rule was adopted for the low band, but the **mid band holds 112 of 192 judgements** and its treatment was undecided.
- **Measured, not assumed:** ten mid-band items over five repeats gave modal share **0.86**, close to the low band's **0.88**. Within-item stability does not separate the bands.
- **What separates them is representativeness of the recorded draw:** **9 of 10** in the mid band against **1 of 5** in the low band. So reported confidence predicts whether a single draw represents the item, not how concentrated the item's answer distribution is. The rule stays scoped below 0.7.
- **Applied:** five low-band records and five calibration key entries rewritten to modal verdicts; **four verdicts changed**. Every `unclear` verdict in the whole pool was a low-confidence single draw, and all three resolved to a definite verdict, so that category is now empty. Every original draw is retained beside its replacement.
- **Counterevidence recorded against my own new rule.** Majority vote has been shown to reduce per-problem accuracy on most hard problems for small models, and agreement can be high while the answer is wrong. The rule was applied to precisely the hardest items, so it could entrench a wrong answer.
- **The falsifier is written to revert it:** if the human labels agree more often with the original single draws than with the modal verdicts, the correction made the record worse.

### Cycle 26 — the items are labelable; the recorded draw was not representative

- **Hypothesis tested and refuted.** The previous cycle proposed that items below 0.7 confidence might be unlabelable. Repeating every low-confidence item five times, against five high-confidence controls, shows they are not.
- **Within-item stability:** low band mean modal share **0.88** (2 of 5 unanimous) versus **1.00** for the high-confidence controls (4 of 4). The items carry a stable answer.
- **What actually fails is the recorded draw.** It matches the item's own modal answer in only **1 of 5** low-band cases, and it returned `unclear` three times where repeats converge on a definite verdict.
- **The earlier claim was too strong and is corrected.** "Verdicts below 0.7 carry no reproducible content" is wrong as stated: the single verdict does not reproduce, the item's modal answer largely does. `RD-2026-09-02-30A` is now `REFINED_BY_MEASUREMENT`.
- **Consequences:** the three low-confidence items stay in the calibration set because a human can label them; and any recorded low-confidence verdict is replaced by a modal verdict over at least five repeats before comparison with a human label.
- **Limit kept in front:** agreement across repeats measures how concentrated an answer distribution is, not whether its mode is correct. A stable modal answer can still be wrong.

### Cycle 25 — the judged layer replays only where it is admitted

- **Gap picked:** the deterministic re-derivation could not reach judged verdicts, so their reproducibility was unmeasured.
- **Executed:** 24 recorded element judgements, sampled with a fixed seed and stratified across confidence bands, re-verified from the same artifacts with the same judge and the committed verifier.
- **Result by band, not in total.** Above 0.9 confidence: **10 of 10**. Between 0.7 and 0.9: **8 of 10**. Below 0.7: **0 of 4**. Overall 18 of 24; excluding two items that retrieved no span and so need no model call, 16 of 22.
- **The 0.9 admission floor is now measured, not just reasoned.** It was adopted in cycle 16 on reliability grounds; the band it admits replays perfectly here.
- **Verdicts below 0.7 carry no reproducible content** and must not be scored, rather than being treated as noisy but usable.
- **Three limits recorded:** replay is not correctness since no human label exists for these items; a disagreement cannot be attributed to judge stochasticity rather than item ambiguity from this design; and the low band held only 5 items in total.

### Cycle 24 — the recorded results were re-derived, not assumed

- **Gap picked:** every recorded score came from instrument code written before the mutation audit, so no recorded number had been checked against the audited instruments.
- **Executed:** the deterministic quantities of both blocks were re-derived from the retained artifacts. Re-running would have spent frozen tasks without testing the recorded numbers at all.
- **Both blocks matched exactly.** Variance block `32 / 0 / 0 / 26`, pilot block `16 / 0 / 0 / 13`, each equal to what was recorded.
- **Independent canary scan:** every retained design and state artifact was scanned against all eight per-task withheld canaries read from the **task bundles**, not from the receipts. No leak.
- **The new tool was defective on first use.** Its filename pattern required a repeat suffix, so it matched nothing in the pilot block and reported zero leaks and zero redlines — which reads as a pass. It now raises on an empty match, with a fixture for that case, and all five injected mutations are caught.
- **A fixture asserted my assumption again:** a sample artifact was declared clean when it did not satisfy all five structural checks. The sample was corrected, not the check weakened.
- **Boundary stated, not implied:** judged element verdicts depend on a model call and are outside this check.

### Cycle 23 — the last three instruments got suites, held to the same standard

- **Gap picked:** three instrument modules had no paired suite at all — the adversarial validity check, the pilot builder, and the element verifier.
- **Executed:** all three now have suites whose expected values come from each module's stated contract, not from its current output. Then **21 further mutations** were injected.
- **20 caught.** The 21st was shown by executing both variants side by side to be an **equivalent mutant**: the branch it changed cannot produce a different result once the evidence directory is absent. No fixture was invented to force a difference that does not exist.
- **A new fixture was wrong in the same old way.** It asserted the judge's model selector is shell quoted; a safe selector is correctly passed through unquoted. The assertion was my assumption again, and it was replaced by a check on an unsafe selector.
- **The judge has no reliable oracle**, so its suite asserts the deterministic shell around the model through an injected runner and never makes a live call.
- **No instrument module now lacks a suite.** The honest limit stands: a mutation set chosen by the author of the code can still miss a fault class that neither the code nor the mutations consider.

### Cycle 22 — the instruments were audited by mutation, not by reading

- **Gap picked:** one instrument had been wrong while its suite passed, so no other suite could be trusted on inspection alone.
- **Executed:** 17 semantic mutations, one at a time, across six instrument modules, each paired suite run, each module restored and digest-checked.
- **13 caught, 4 survived.** Three survivors were in scoring: an episode with a dimension scored zero could pass as fatal-error-free, a fabrication redline could stop blocking that endpoint, and the carry-through ratio could exceed one.
- **The fourth survivor was the worst.** The release sandbox could report a workspace **admissible while a probe had fired**, neutralising the entire fail-closed admission gate, and every test still passed.
- **Five fixtures added; all 17 mutations then caught.**
- **A defect in the test harness itself surfaced:** the scoring suite computed its pass tally *before* the newly added checks ran, reporting 14 of 18 while every check passed. The tally now runs last.
- **Literature named the defect class:** an oracle that takes its expected value from the system it judges cannot fail, because a fault moves measurement and expectation together. That is exactly how the cost fixture protected a wrong parser.
- **Two limits recorded:** catching 17 mutations does not show the instruments are correct, and three modules still have no paired suite at all.

### Cycle 21 — the instrument was wrong, and its own fixture protected the error

- **Gap picked:** whether retrieval context cost is chosen by the agent. Answering it required reading the transcripts, which exposed something worse.
- **The cost parser was wrong by 14.4x.** It summarised a run by its last usage record, assuming usage accumulated. Usage is reported **per completed API call**, and a multi-turn episode re-sends its context on every call, so the last record describes one call. Output tokens were understated 13.0x.
- **The fixture protected the defect.** It asserted that the last record was the run total, which is what I believed rather than what the transcript does. The suite passed while the instrument was wrong. A fixture that encodes the author's assumption tests the assumption, not the system.
- **How it surfaced:** the earlier run had already recorded `monotonic: false` on all six episodes. That signal was written down and not acted on. It was only chased when an unrelated question forced a look at the records.
- **Two further defects during repair.** Transcripts captured through standard output were truncated in **four of six** runs, losing middle records; transcripts are now written to files and checked for completeness. And the first repair swallowed every record after a truncation, caught by a failing-first fixture before use.
- **Every cost number from cycles 18, 19 and 20 is void**, including the fixed floor, both context figures, and both variability figures. The three affected decisions carry `VOIDED_BY_RD-2026-09-02-26A`; their structural content stands, their numbers do not.
- **Re-measured from complete transcripts:** minimal condition 167,251 total tokens over 3.3 calls; full condition 520,969 over 9.7 calls, a ratio of 3.1. Both vary widely, at 16.6% and 34.0%. No factor attribution: two factors move together, three repeats each.

### Cycle 20 — one episode is a draw, not a value

- **Gap picked:** cost was being reported per episode without ever testing whether a single episode is stable.
- **Executed:** six episodes on one burned task, three repeats per condition, with **identical workspace digests inside each condition**, so any spread is not workspace drift.
- **Result:** the minimal condition varied by **2.90%** around 51,138 context tokens; the retrieval condition varied by **11.34%** around 79,320. The retrieval within-condition range of 17,231 tokens covers **61.1% of the gap between conditions**.
- **The falsifier of `RD-2026-09-02-24A` fired for one condition.** That decision is now `REFINED_BY_MEASUREMENT` and `RD-2026-09-02-25A` replaces it: every cost quantity is a mean over repeats with its spread, never a single episode, and the retrieval condition needs more repeats than the minimal one.
- **A mechanism is offered as a hypothesis, not a result:** with retrieval available the agent chooses how much of the evidence pack to read, so context cost may be partly an outcome of its behaviour. Testing it needs per-episode read instrumentation this design does not yet have.
- **Consistency check passed:** the two single episodes from the previous cycle fall inside the ranges measured here, so the earlier numbers were not outliers.

### Cycle 19 — the previous cycle's cost decision was falsified by its own falsifier

- **Gap picked:** the cost instrument had only ever been validated on synthetic probes in an empty directory.
- **Executed:** one burned pilot task was run once in the minimal condition and once in the full condition, same pinned backend, structured output mode.
- **The falsifier of `RD-2026-09-02-23A` fired.** That decision claimed a fixed context floor of 46,763 tokens. Real episodes measured **51,596 and 76,496 context tokens**, a difference of 24,900, with totals differing by a factor of **1.487**.
- **Diagnosis:** the probes ran in an empty directory, so they measured harness context alone. A real episode also carries its mounted workspace, and the full condition mounts an evidence pack of 145,906 bytes. The floor was an artefact of how the instrument was probed.
- **Recorded as falsified, not amended.** `RD-2026-09-02-23A` now carries `FALSIFIED_BY_MEASUREMENT` and `RD-2026-09-02-24A` replaces it: context tokens and marginal tokens are reported separately, neither treated as constant, dollar cost still excluded.
- **Attribution limit stated, not implied:** the two episodes differ in both factors at once and each ran once, so nothing here attributes cost to retrieval or scaffold separately. One run scores one implementation, not an idea.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One discovery primitive returned nothing for the third objective; that is recorded rather than hidden by rewording the query.

### Second near miss — a receipt made stale by editing after validating

The clean-clone run failed while the working tree passed. Cause: the cost ledger was written **after** the validator had already run, so its committed receipt was stale by one edit. The working tree agreed with itself and proved nothing. The commit path now refreshes receipts, re-runs the validator, and refuses to commit on a failing gate, so "edit after validating" can no longer reach a commit.

### Cycle 18 — cost stopped being a proxy, and the measurement overturned the plan

- **Gap picked:** the pilot recorded token accounting as `UNMEASURED` and kept wall-clock duration as a proxy, which cannot support any budget-matched claim.
- **Executed:** the runner was switched to structured output mode and a committed parser with **11 fixtures** now reads the usage stream. One fixture exists because usage is reported repeatedly and grows, so summing records would overcount; the parser takes the final cumulative record and checks monotonicity rather than assuming it.
- **The measurement changed the plan.** Three probes on the pinned backend showed a **fixed context floor of 46,763 tokens, identical in every probe**, against work of 39 to 384 output tokens. Dollar cost for the *same* trivial task differed by **12.03x** between a cold and a warm cache.
- **Consequence:** cache state depends on execution order, not on the condition, so dollar cost is inadmissible for comparison; and a contrast measured on total tokens would be about one percent of the reported number. Cost is now reported as marginal input plus output, with the floor stated separately (`RD-2026-09-02-23A`).
- **A condition on any future effect claim was recorded, not deferred:** augmentation gains have been shown to vanish against a token-matched baseline, so a comparison here must be budget-matched rather than merely condition-matched.
- **First model cost entered the cost ledger** — three probes totalling $0.07. GPU credit units remain 0.

### Cycle 17 — the calibration set is complete and provably blinded

- **Gap picked:** the calibration set stood at 22 of 25 items, three short in the low-confidence stratum, and judged scoring stays inadmissible until it is complete.
- **Executed:** exactly three unused low-confidence judgements existed in the verdict pool, which is the number required. The set now stands at **25 items in the intended 10 / 10 / 5 stratification**.
- **Two defects found by checking rather than assuming.** The three added items lacked the `answer`, `labeller`, `labelled_at`, and `notes` fields the original items carry, and they were not joined to the blinded key. Both were fixed and every item now shares one field set and resolves to exactly one key entry.
- **Blinding verified mechanically:** no item carries a judge verdict, judge confidence, episode id, or element id. The word `confidence` does appear inside candidate passages, and was checked to be ordinary statistical wording rather than leakage.
- **Still inadmissible, and said so.** No labels have been collected. `Q-0006` is updated to 25 items and stays non-blocking; the loop continues on its default, and judged scoring remains barred until real labels certify the risk bound.

### Near miss recorded — a passing run that proved nothing

While closing cycle 16 the staging list named a manuscript path that does not exist. `git add` aborted, **nothing was staged**, the commit failed, and the validation run then passed against the *previous* commit. The pass was real and worthless: it validated work that was not in the repository. The tell was `submission_artifact_rebuild` coming back empty, because the old commit had no rebuild check. The loop now refuses to continue when the head does not move after a commit, and a run is only accepted as evidence for work that the head actually contains.

### Cycle 16 — the process claim is now a number, and reproducibility is enforced

- **Unit 1, reproducibility enforced.** The clean-clone comparison was folded into the validation gate: every run rebuilds the artifact from its committed builder into a temporary path and fails when the digest differs. Proven by tampering with one word in the committed artifact, which produced `reproducible: false` and a gate failure; restoring returned it to pass.
- **Unit 2, the self-correction claim measured.** The method claimed a loop that corrects itself but never quantified it. A committed script with eight fixtures now censuses the decision ledger: **28 records across 15 groups, all carrying falsifiers written before the result, 20 with executed evidence, and 3 revised**, a revision rate of `0.107`. All three revisions were triggered by the project's own executed measurements, not outside review.
- **Two limits recorded with the number.** The census counts the ledger that records the decision to run it, so it is reported against a stated ledger digest rather than as a constant. And a single project without a comparison group cannot show that writing falsifiers *caused* the revisions.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One names this project's ceiling directly: gates and receipts are operational rigor, which substitutes for understanding rather than supplying it. That sentence is now in the manuscript as the boundary of the contribution.
- **Two real defects fixed while integrating:** the new citations used the wrong macro so first-citation ordering silently passed on 3 of 60 entries, and adding a subsection before the Conclusions renumbered two later references. The bibliography was reordered programmatically to the true first-citation order.

### Cycle 15 — the artifact was not reproducible, and now is

- **Gap picked:** the artifact digest was pinned in the receipts but the artifact had never been rebuilt anywhere else, so the pin proved a machine rather than a build.
- **Measured first:** a clean clone at the same commit rebuilt the artifact to a **different digest**. The pinned receipt would have failed for any independent verifier.
- **Diagnosed from the bytes:** exactly one part differed in content, `docProps/core.xml`, carrying created and modified timestamps, and every zip entry carried the build time.
- **Fixed and re-measured:** every packed entry timestamp and both document-property timestamps are pinned to the epoch already used for the deterministic PDF, and parts are written in sorted order. A repeat build on this machine and a rebuild in the clean clone now produce the **same digest** `15a69f22`.
- **Literature loop:** 9 discovery calls, 3 new `FULL_PAPER_READ` records. One sharpened the goal: reproducibility alone is not verifiability, because a verifier must also recover the source state and build instructions, which is why the builder is committed beside the artifact rather than only its digest (`RD-2026-09-02-21A`).
- **Honest ceiling recorded:** attested builds bind artifacts to their environment with hardware support this project does not use, so this is reproducibility without attestation.

### Cycle 14 — the artifact format is now guarded, not merely asserted

- **Gap picked:** the builder asserted numerals, spacing, page numbers, and citations, but nothing stopped a later rebuild from silently dropping them. A property asserted only by its producer is unguarded.
- **Executed:** the checks moved into the deterministic validator, which now re-derives title, front matter, chapter numerals, summary length, keyword count, double spacing, page numbering, citation numbering, and forbidden names from the artifact bytes on every run.
- **Proven by mutation, not by assertion.** Five deliberate corruptions each failed the gate: removing the footer, switching to single spacing, stripping the numerals, deleting the citations, and inflating the summary past its limit (`korean summary length 662`). Restoring the artifact returned the gate to pass with a matching digest.
- **One imprecise message recorded rather than hidden:** a crude sixth mutation that merged text into the keyword paragraph still failed closed but reported a less precise reason, so it is not counted as a clean length test.

### Cycle 13 — the inherited format properties were all missing

- **Gap picked:** Roman numerals, double spacing, and page numbers were inherited from a reference document and had never been checked. Assuming them would repeat the earlier mistake of trusting an unverified inheritance.
- **Measured from the artifact parts, all three were absent:** chapter headings carried no numerals, no line spacing was set anywhere, and the file had **no footer part at all**.
- **Implemented in the committed builder** so every rebuild reasserts them: chapters numbered I to V with the Korean front matter deliberately left unnumbered, double spacing written into document defaults, and a page-number footer wired through the footer part, relationship, content-type override, and section reference (`RD-2026-09-02-19A`).
- **Re-verified from bytes after the rebuild:** five Roman chapters, front matter unnumbered, `w:line=480` in defaults, footer with a PAGE field, 57 bracketed citations, zero forbidden names, and the artifact re-opens cleanly.
- **Honest limit:** the word processor PDF export still does not complete unattended on this machine, so what the parts declare has not been confirmed against a rendered page. The deterministic toolchain PDF remains the visual reference.

### Cycle 12 — the submission artifact is now complete and correct

- **Gap picked:** the Word artifact was missing the required Korean summary and keyword line.
- **Constraint discovered first:** the pinned LaTeX toolchain has no CJK font, so embedding Hangul in the source would break the deterministic PDF that every evidence claim rests on. The source stays ASCII and the build injects the front matter from its single side file, failing if the summary exceeds 500 characters or the keywords exceed five (`RD-2026-09-02-18A`).
- **First attempt was worse and was rejected.** A markdown round-trip carried the Korean text but dropped the title and citation markers, so it was discarded in favour of the direct conversion with an XML-level injection.
- **A real defect was found in the artifact:** the converter dropped every in-text citation, leaving dangling punctuation such as "correctness alone ;" where a reference belonged, in violation of the official bracketed-citation requirement. The build now materialises the same first-citation numbering the validator enforces; **57 citations render** and the reference list has 57 entries (`RD-2026-09-02-18B`).
- **Verified from the artifact's own bytes**, not from the converter: title present, `국문 요약` at 361 of 500 characters, 5 of 5 keywords, section order Introduction → Related Works → Proposed Method → Experimental Results → Conclusions, zero forbidden public names.
- **Open:** page numerals, spacing, and page numbers inherited from the reference document remain unverified, the application PDF export still times out, and display equations render as TeX text.

### Cycle 11 — conclusions rewritten and the submission artifact built

- **Counterevidence sweep first:** three discovery primitives searched specifically for evidence that cue-based checklist scoring is adequate, which would have reversed the endpoint replacement. Nothing supporting it was found, so the replacement stands.
- **Conclusions rewritten:** the thesis now states that it set out to test an effect, reached the prior question of whether the instrument could be trusted, and stopped there. The contribution is named as methodological, and bounded by three limits including the calibration set the system cannot produce for itself.
- **Word submission artifact built** from the validated manuscript and verified by parsing its own document XML rather than trusting the converter: correct top-level section order, 232 paragraphs, 50 headings, zero forbidden public names.
- **A gate fired on ordinary language and was narrowed deliberately.** The inherited pattern blocked the word used for handing in a thesis. Rather than renaming artifacts or disabling the check, the pattern was narrowed to competition-specific forms and proved by fixture to still fire on every competition term (`RD-2026-09-02-17A`). Describing the gate then tripped it, so exact patterns now live in the hashed ledger and the graph points to them.
- **Known gaps recorded, not hidden:** the Korean summary and keywords are not yet embedded in the manuscript body, the application-rendered PDF export timed out, and the page-format properties inherited from the reference document are unverified against the official form.

### Cycle 10 — front matter aligned, and the self-verification hazard named

- **Gap picked:** the Introduction and Proposed Method still described the round-7 design, and the thesis had not stated what a system that studies itself is entitled to claim.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators. One is directly adversarial to this project: when an agent controls both the optimized object and its verifier, self-assigned scores can stay high while real performance does not.
- **Executed:** the scope subsection now states that the work reached the instrument-admissibility boundary and stopped there, and a new method subsection makes the three instruments first-class design objects, each with its own falsifier. Five references added, bibliography reordered.
- **Named hazards rather than assumed immunity:** self-authored verification, harness tampering by a self-improving agent, and self-evolving loops that presuppose a metric which does not exist. The mitigations already implemented are stated against each.
- Manuscript is now 7,781 words with 121 reviewed locators behind it.

### Cycle 9 — the manuscript now reports what was executed

- **Gap picked:** five cycles of executed instrument evidence existed and the manuscript reported none of it, which is the gap that matters most against the thesis objective.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators on construct-validity reporting, validity degradation across evaluation pipelines, audit failure modes, preregistration deviation, and negative-result publication.
- **Executed:** the results section was rewritten to report the three executed blocks, the falsification of the first primary endpoint, the measured reliability of its replacement, and the two design parameters fixed by measurement. Ten new references were added and the bibliography was reordered to first-citation order.
- **The section leads with the falsification rather than hiding it**, because publishing filters out negative results and models trained on that literature inherit the bias.
- **Still no efficacy claim.** The section states explicitly that no treatment effect is estimated, that four preregistered decisions were superseded or falsified, that pilot tasks are development data, and that all element verdicts remain inadmissible as scores.

### Cycle 8 — is the verifier even stable?

- **Gap picked:** labels are expensive and require a human, so before requesting any, test whether the verifier is stable enough to be worth calibrating.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 5 locators, including one that directly challenges the plan: agreement is not accuracy, and high self-consistency frequently co-occurs with wrong answers.
- **Executed:** reliability audit on 64 stratified pairs, each re-judged by the same judge with the same prompt and independently judged by a second model.
- **Measured:** test-retest agreement **0.844**, cross-model agreement **0.703**, chance-corrected kappa **0.411**. Above 0.9 confidence retest agreement is **0.880**, cross-model **0.920**, and **0 of 20** high-confidence pairs disagreed across models. Between 0.7 and 0.9 cross-model agreement falls to **0.568**, near chance.
- **Decision:** a reliability floor at 0.9 confidence abstains before calibration, and calibration may only tighten it (`RD-2026-09-02-16A`). This is reliability, not validity, and is reported as such.
- **Calibration form emitted:** 22 blinded items sampled stratified across confidence bands with a recorded seed, plus a separate evaluator-owned key. Stratification rather than uncertainty sampling was chosen because uncertainty sampling concentrates the items where annotation error also concentrates (`RD-2026-09-02-16B`). Q-0006 requests the labels; the default is to continue without them.

### Cycle 7 — replacement endpoint implemented and measured

- **Executed:** filter-plus-verification over all 32 retained episodes, 192 element judgements, judge drawn from a different provider family than the treatment backend. Receipt `paper/experiments/verified-endpoint-receipt.json`.
- **The falsification held outside the probe set.** On real artifacts the falsified cue endpoint and the verified endpoint correlate at **0.043** with a mean absolute difference of **0.484**. They were not measuring the same thing.
- **Variance recomputed on the verified endpoint:** residual **83.8 percent**, task **16.2 percent**, condition and interaction both estimated at **zero**.
- **Consequence for allocation:** with a zero interaction component the standard error of a condition mean does not depend on the task-versus-repeat split, so resolution cannot be bought by reallocating. The split is now chosen for task breadth, and the projected paired minimum detectable effect is about **0.081**, roughly double what the falsified endpoint implied (`RD-2026-09-02-15B`).
- **Nothing is scored.** All 192 verdicts come from an uncalibrated judge and are inadmissible; 2 unparsed and 3 unclear replies are counted rather than dropped. The verdicts are now the labelling material for the 25-label calibration set.

### Cycle 6 — my primary endpoint failed its own falsifier

- **Gap picked:** `RD-2026-09-02-11A` carried the falsifier "if coverage does not separate artifacts a reader would rank differently, it measures vocabulary". That was untested.
- **Literature loop:** 9 discovery calls, 5 new `FULL_PAPER_READ` records, 6 locators. Planted-shortcut evaluation, solution hacking, and grounded checklist partial credit supplied the audit method.
- **Executed:** an adversarial probe suite over all eight anchor checklists. Cue matching counted negated sentences containing the cue as satisfied at **0.969**, and missed genuine paraphrases at **0.909**.
- **Ablation:** a negation guard drove false positives to **0.000** but raised misses to **1.000**. The failure is structural: matching cannot decide satisfaction.
- **Verdict: falsifier fired.** Cue matching is rejected as the primary endpoint and demoted to a high-recall candidate filter; element satisfaction becomes a verified judgement admitted through the selective evaluator (`RD-2026-09-02-14A`).
- **Two consequences recorded rather than hidden.** The 25-label calibration set moves from optional to load-bearing for the primary endpoint. The variance components from cycle 5 were computed on the falsified endpoint, so the numeric allocation is void while the algebra stands; the 32 episodes are retained and rescorable, so no episode is wasted (`RD-2026-09-02-14B`).

### Cycle 5 — variance block EXECUTED, allocation reversed by measurement

- **Executed:** 32 episodes on the four frozen confirmation tasks, 4 conditions x 2 repeats, all exit zero, zero canary leaks. Receipt `paper/experiments/variance-block-receipt.json`.
- **Measured variance components of the coverage endpoint:** repeat residual **64.3 percent**, condition **22.6 percent**, task-by-condition **13.1 percent**, task **0.0 percent** (boundary estimate).
- **This refuted my own pre-registered assumption.** `RD-2026-09-02-09D` had kept two repeats and stated the falsifier "if task variance dominates residual, add tasks instead". The measurement came out the other way, so the decision is superseded rather than defended.
- **Allocation derived, not chosen:** at a fixed episode budget the standard error of a condition mean is `(repeats x interaction variance + residual) / (budget / conditions)`, which increases monotonically with repeats. The block therefore moves to the maximum number of tasks at one repeat, with a small repeated subset kept to re-estimate residual variance (`RD-2026-09-02-13A`). Projected paired MDE improves from about 0.049 to about 0.045 while quadrupling task coverage.
- **Honest limits recorded:** 32 episodes give 3, 3, 9 and 16 degrees of freedom, the task component is a boundary estimate at zero, and coverage is per-task normalised, which suppresses between-task variance by construction.
- **Label protocol frozen:** `paper/research/human-label-protocol.md` fixes element-level blinded labelling, stratified sampling, an overlap-agreement gate, and append-only records.

### Cycle 5 (earlier) — confirmation set frozen

- Four confirmation tasks frozen on sources disjoint from the pilot and excluded from their own released evidence packs: structure-versus-insight ablation, attribution of improvement to harness rather than model, instrument-change measurement under scarce labels, and budget and access control in optimization benchmarks.
- Element checklists were written and frozen **before any artifact exists**, which is the property the pilot anchors could not have (`RD-2026-09-02-12A`).
- Judged scoring remains blocked on the 25-label calibration set; unscored artifact generation is not.

### Cycle 4 — the scoring anchor gap is closed by construction

- **Gap picked:** rubric scores were inadmissible without a human anchor, and the deterministic layer alone could not carry the validity endpoint.
- **Literature loop:** 9 discovery calls across 3 objectives, 6 new `FULL_PAPER_READ` records, 8 line-anchored locators. Record: `paper/research/literature-round10-retrieval-record.json`.
- **Anchor found in prior work:** criteria can be derived from an expert reference rather than authored freely, analytic per-criterion scoring avoids holistic halo, and selective evaluation bounds judge error through calibrated abstention.
- **Executed:** reference-anchored analytic coverage over evaluator-owned element checklists, measured on all 16 retained pilot artifacts. Coverage ranges 0.667 to 1.000 and names the missed elements, where fabrication redlines had produced no signal at all.
- **Defect found by fixture:** the first selective-evaluation implementation chose its threshold from the empirical error rate, which overfits a finite calibration set. Replaced with a one-sided binomial upper bound, so an undersized set is now refused and the required size is reported.
- **The blocker became a number:** at 95 percent confidence a flawless calibration set of **25** labels certifies a 10 percent risk level, **11** certifies 20 percent, and **52** certifies 5 percent. The adopted target is at least 25 labels on tasks disjoint from the burned pilot set (`RD-2026-09-02-11C`).
- **Suites:** reference-anchor 13/13, scoring 14/14, sandbox 10/10, runner 7/7.
- **exa MCP usage this cycle: not used.**
### Cycle 3 — instrument pilot EXECUTED

- **Backend probe (live):** session provider `HTTP 429 usage limit reached`, reset in about 4.8 days; one hosted provider timed out at 240 s; one router `HTTP 402 insufficient credits`; two selectors answered. Treatment pinned to one selector, judging reserved for a different family (`RD-2026-09-02-10C`).
- **Tasks frozen:** four design tasks built from retained sources with withheld targets isolated by the release sandbox, each with a released evidence pack of 12 excerpts for the retrieval conditions.
- **Pilot executed:** 16 episodes, 4 tasks x 4 conditions, all exit zero, 1942.9 s total, 287,707 bytes of artifacts. Receipt `paper/experiments/study-a-pilot-receipt.json`.
- **PF-1 hidden-task boundary held:** zero withheld canaries in all 16 artifacts.
- **PF-2 the deterministic layer had no discrimination:** fabrication redlines fired on 0 of 16 real artifacts while firing on every corrupted fixture. Five structural-completeness checks were added and flag 13 of 16 (`RD-2026-09-02-10B`).
- **PF-3 the manipulation probe was mis-specified:** all 8 structured episodes filled the scaffold, yet 7 of 8 never echoed the field name, so the probe fired on episodes whose state was consumed. Respecified to filled-field consumption plus carry-through (`RD-2026-09-02-10A`); consumption is now 5 of 8.
- **Cost:** no GPU, no compute unit, 0 CU cumulative. Token usage is `UNMEASURED` because headless text mode emits no usage record; the confirmatory run must use json mode.
- **Burned:** all four pilot tasks are permanently excluded from confirmation, two of them as the Q-0004 disclosure tasks.
- **No effect is claimed.** Four cells with one run each cannot resolve any contrast, and the structural checks were specified after seeing these artifacts.
### Cycle 1 under the standing loop (instruction #0005)

- **Gap picked:** the round-8 retrieval record had zero discovery loops, no design comparison existed, and no pilot prerequisite had been built.
- **Literature loop:** 3 objectives x 3 primitives = 9 discovery calls, 135 candidates, 7 new `FULL_PAPER_READ` records with exact versions and 10 line-anchored locators. Record: `paper/research/literature-round9-retrieval-record.json`.
- **Design comparison:** `paper/research/design-comparison-round8.md` compares 16 prior experiments across 10 design columns and states where Study A is stronger, weaker, and what changed.
- **Counterevidence found:** a controlled two-agent, 288-run ablation of persistent external context reports no reliable gain and attributes failures to implementation skill. This is direct counterevidence to H-A and forced two design changes.
- **Decisions 09A-09D:** manipulation probe for state use; pre-registered equivalence margin with TOST plus a resolution target; judge admission on severity, halo, and step-level review; no change to repeats with a pre-registered variance decomposition.
- **Execution unit: `EXECUTED`.** `experiments/study_a/release_sandbox.py` with six fail-closed probes, verified by `experiments/study_a/test_release_sandbox.py`: 10/10 checks, every probe demonstrated firing on a corrupted fixture. Receipt `paper/sources/study-a-sandbox-fixture-receipt.json`.
- **Verification:** validator PASS; clean-clone run `d98a34a2-bfd6-43e6-be18-cc57605e1a44` PASS at `f33f5993f`, 92/92 locators re-derived.
- **Instruction #0006 applied:** Study C moved to `EXECUTION_PATH_SECURED_PREREGISTRATION_REQUIRED`; `paper/research/colab-usage.md`, `paper/supervisor/cost-ledger.md` (cumulative 0 CU, no active sessions), `paper/research/burned-task-ledger.json` created; Q-0005 opened as blocking.
- **exa MCP usage this cycle: not used.** All candidates were reachable through the research CLI primitives; recorded in the retrieval record `web_queries` field.

### Remaining pilot prerequisites

| Prerequisite | State |
|---|---|
| hidden-task release sandbox and integrity probes | **PASS**, 10/10 checks, six probes demonstrated firing |
| independent scoring calibration and judge agreement fixture | **PASS**, 9/9 checks, identical across three runs |
| fixed Study A runner as one command | **PASS**, 7/7 checks |
| 16-episode pilot | blocked only on task freeze, backend pin, and burned-task entries |

### Cycle 2 under the standing loop

- **Gap picked:** the two remaining pilot prerequisites, both GPU-free, per instruction #0006.
- **Built and executed:** `experiments/study_a/scoring.py` (deterministic redlines, one judge call per dimension, calibration on agreement, severity, halo) and `experiments/study_a/run_episode.py` (fixed one-command runner refusing incomplete configuration, condition/factor mismatch, or a fired pre-launch probe).
- **Three defects were found by the fixtures, not by reading:** the manipulation probe ran pre-launch where no artifact exists and blocked every structured-state episode; the calibration fixture seeded randomness with the salted builtin hash and was therefore non-reproducible; judge severity was computed on the 30-point total but tolerated at half a point. All three are fixed and recorded in `paper/sources/study-a-prerequisite-receipt.json`.
- **Local reproduction of a reviewed finding:** a judge with agreement `0.9653` against the human anchor was still inadmissible at severity `-1.78`, which is why agreement alone is not the admission test.
- **Remaining before the pilot:** freeze four tasks with withheld targets, pin the model backend, and open the two burned-task entries approved in Q-0004.

### Resume procedure (instruction #0004 §2)

- HEAD confirmed and continued on the canonical branch; no ancestor node edited.
- `paper/evidence-matrix.csv` was 0 bytes in the working tree and was restored from HEAD. Cause: the receipt had recorded CRLF working-tree bytes while git stores the LF-normalized blob, so the recorded digest could never be reproduced from the repository. The writer now emits LF, `.gitattributes` pins `eol=lf`, and the digest matches the committed blob.
- Validation run `3fe2958b-44b6-4760-89fb-f711440c2ae0` is **failed** (exit 1) at commit `b2070ed09`. Root cause was not the manuscript: the local pass depended on working-tree bytes absent from the repository — five round-4 reports were never committed and 25 of 74 claim locators pointed at source slices missing from both repo and worktree.
- Repair: 16 exact-version archives re-fetched, all **byte-identical** to recorded digests; 20 TeX slices re-extracted and one PDF-derived text reproduced (recipe recovered as `pdftotext -layout`); all locators verified by file digest, line slice, and excerpt digest; a global fail-closed locator gate was added and shown to fire on a deleted slice. Receipts: `paper/sources/legacy-source-restoration-receipt.json`, `paper/sources/global-locator-gate-failing-first.json`. Commit `c677aeb6e`, clean-clone run `67bec1bc-b8da-47a6-8f49-6a486799f844` **PASS**.

### Round 8 — design competition (instruction #0003 §3-3~§3-5)

- Four full reads with exact versions: `2403.14403v2`, `2310.11511v1`, `2405.14831v3`, `2602.15112v2`; 8 line-anchored locators; 8 evidence rows; graph now 170 nodes / 397 edges.
- Three six-field decision records (`RD-2026-09-02-08A/B/C`) recorded in the ledger and linked into the context graph as `decision:*` nodes with `informs_decision` edges from their reviewed sources.
- Study A inherits its 2x2 structure; changed elements: retrieval-decision quality added as a secondary endpoint, integrity probes added to the evaluator gate, and an ideation-versus-configuration attribution arm added to the pilot.
- Execution-graded replication deferred as Study C with resources and steps in `paper/research/study-c-runbook.md`.
- Engine usage verified and written to `paper/research/orx-usage.md`.
- Commit `5527c7926`; clean-clone run `7184ad85-57e3-4fa4-a12c-21a5b80513db` **PASS** with 82/82 locators re-derived.

- Root-agent adaptive round 5: five `FULL_PAPER_READ` design/evaluation records. Architecture round 6 adds six `FULL_PAPER_READ` harness/context anchors, including programmatic context management. Corpus: 43 full reads and 74 reviewed locators; round 7 adds routing, protocol, RAG, and agentic-stack evidence with 22 exact locators.
- Prospective experiment revised to provisional 2×2 structured-state × dynamic-retrieval Study A.
- Minimum executable unit proposed: 16-episode instrument pilot; no result claim.
- ResearchClawBench runner pinned at `5bc7963f82b8cc4f13ea27e7524709e0d6a12a96`; workspace projection and missing sandbox guarantee recorded as separate code locators.
- Public-paper hard exclusions applied; `paper.tex` hard-exclusion scan is zero.
- 30-minute heartbeat active: `c024a580-775d-4253-9249-e62de07a047a` (cron `*/30 * * * *`). The previous id `28b18ed8` was paused and is retired.

## Literature-map progress (preliminary anchor count / target ≥3 FULL reads)

| Area | Preliminary FULL reads | Status / named gap |
|---|---:|---|
| 1. Harness functions | 12+ | anchor count passes; necessity/design split mapped, remaining approval and sandbox experiments open |
| 2. Memory functions | 6+ | anchor count passes; personalized memory remains thin |
| 3. Protocols | 5+ | academic anchor threshold passes; official MCP/A2A versions and human-factor evaluation remain |
| 4. Skills | 4+ | anchor count passes; normative constraints need focused support |
| 5. RAG engine | 4+ | academic anchor threshold passes; product backends and local corpus evaluation remain |
| 6. Agentic AI development stack | 5+ | method threshold passes; exact framework/product primary behavior remains follow-up |
| 7. Coding-agent harness architecture | 9+ | routing mechanism axis anchored; pi standalone source and two direct primary contrasts remain open |
| 8. Autonomous research engine functions | 8+ | anchor count passes; seven functional subtopics mapped, public-engine naming forbidden |
| 9. Provider and dynamic model routing | 5+ | academic threshold passes; H-E remains unexecuted and fixed model retained for Study A |

## Capability map and public-name gate

- capability map: `46/46` sub-capability rows drafted; current-cycle validation set selected, literature gaps remain.
- public-name source gate: added and passing with `0` current hits; synthetic sample detected all 7 forbidden classes.
- public-name PDF gate: implemented with pinned `pdftotext`; full 43-source deterministic two-build validation PASS, source/PDF token hits `0`.
- current-cycle targets: hidden-task sandbox, independent evaluator, observability, context graph, research procedures/norms/decision records, retrieval pipeline, source verification, claim–evidence ledger, preregistration/deterministic validation, iterative stopping.
- model routing: target capability, design-only in Study A (`R-ROUTING-DEFER`) to avoid a treatment confound.

## Next concrete actions

1. Freeze four unseen confirmation tasks disjoint from the burned pilot set, and re-validate the frozen structural checks on them before any scoring.
2. Build the human-anchored calibration subset so rubric scores become admissible; deterministic checks alone cannot carry the validity endpoint.
3. Switch episode execution to the json output mode so per-episode token usage is measured rather than proxied.
4. Estimate the confirmatory block cost from measured pilot durations and token usage, then open the GPU question again only if Study C is scheduled.
5. Keep every claim scoped: the pilot validated instruments and estimated no effect.

## Blockers and questions

- **E5 launch:** blocking — hidden-task sandbox, independent scoring, and fixed Study A runner are not implemented.
- **research design:** preregistration-ready at `paper/research/research-design.md`; H-B direct comparator and H-E rationale are closed, while launch remains blocked by hidden-task isolation, independent scoring, and fixed runner.
- **plan deadline:** answered `2026-10-31`; schedule updated in research design.
- **Q-0001:** answered — department plan deadline `2026-10-31`; current semester assumption retained.
- **Q-0002:** answered — six non-executable capability groups remain design-only/follow-up; no new native runtime.
- **DeepVoice evidence:** forbidden by existing user instruction; no access or edit planned.
- No efficacy experiment is running; `Experimental Results` remains explicitly unexecuted.

## instruction-0013 보고 (§9 형식) — 2026-09-03T09:28:45+09:00

### 1. §1 격리 (retraction) — 완료
- **1.1 원고 토큰 카운트 (지정 토큰집합, 6/6 파일 0건):**
  `thesis-ko.qmd` 0 · `word/graduation-thesis.docx`(본문 XML) 0 · `graduation-thesis.pdf`(pdftotext) 0 ·
  `korean-summary.txt` 0 · `evidence-matrix.csv` 0 · `context-graph.md` 0.
  제거 대상: Ⅳ장 §12 "3대 자율 연구 하네스 아키텍처 실증 비교" 34행 2,193자(`tbl-bench-comparison` 코드셀 포함),
  경진대회 명칭 문장 2건 포함 전부. docx/pdf 재빌드 완료.
- **1.2 이동 경로 (삭제 아님, 재라벨링):**
  - `experiments/argo_benchmark/run_benchmark_experiments.py` → `experiments/argo_benchmark/fixtures/simulated_oracles.py`
    (docstring 첫 줄 `SYNTHETIC FIXTURE. No model call. Must never be cited as evidence.`, `execute_*` → `fixture_*`)
  - `paper/experiments/rd_benchmark_2026/comparative_benchmark_receipt.json`
    → `paper/experiments/fixtures/rd_benchmark_2026_SIMULATED/comparative_benchmark_fixture.json`
    (`evidence_level: SYNTHETIC_FIXTURE`, `executed: false`, `model_calls: 0`, `origin: simulation`,
     `retracted_by: RD-2026-09-03-80A`, `benchmark_date` → `fixture_generated_at`)
  - `paper/research/sota-benchmark-design.md` → `paper/research/retracted/sota-benchmark-design.md`
    (§3-4 삭제 후 RETRACTED 블록 1개만 잔존; §1-2·§5는 Study B 사전등록 문서로 흡수 예정)
  - `comparative_eval.py`(계측기)는 유지, 테스트는 fixture만 참조. 11/11 통과.
- **1.3 그래프 변경:** `result:r_rd_bench_bench_outcomes` → `status: RETRACTED` + `SYNTHETIC_FIXTURE`(삭제 안 함) ·
  `experiment:rd_bench_comparative_benchmark` → `executed: false, origin: simulation` ·
  `artifact:comparative_benchmark_receipt` → fixtures 경로 + `SYNTHETIC_FIXTURE` ·
  `hypothesis:h_rd_bench_comparative_sota` → `status: UNTESTED`(Study B 출발점) ·
  신설 `decision:rd_2026_09_03_80a` + 엣지 2개(`retracts` → result, `supersedes` → 기존 decision).
  엣지 어휘에 `retracts` 추가. 노드 425 / 엣지 746.
- **1.4 결정 원장:** `RD-2026-09-03-79A`에 `status: RETRACTED_FABRICATED_EVIDENCE` + `retraction_note`(원문 무수정,
  79A의 순환 논리를 명시 기록) · `RD-2026-09-03-80A` 6필드 신설.
- **1.5 failing-first 3/3 (확인 후 원복):**
  (i) fixture receipt를 비-fixtures 경로에 두면 → `simulation receipt must live under a /fixtures/ path` FAIL
  (ii) 원고가 fixture receipt를 참조하면 → `manuscript references a synthetic fixture receipt` FAIL
  (iii) `total_tokens 999` vs usage 합 `300` → `declared total_tokens 999 != usage log sum 300` FAIL
  원복 후 receipt 6건 스캔 0 실패. 검증 전체 **PASS**.
- **1.6 retraction 커밋:** `aa4315e148573d3b2e45bd65ff4692518b68f8dd`

### 2. 메커니즘 노드 7/7
미착수 (§8-3 다음 사이클). 현재 루프 엔지니어링·그래프 엔지니어링은 원장·그래프에 정의 0건.

### 3. 사전등록 문서 / 아암 커밋 해시 / 검증기
미착수 (§8-4).

### 4. 드라이런 비용
없음. 이번 사이클 모델 호출 0건, 지출 $0.00.

### 5. Q-0009 개정 3 시나리오 비용
미등록 (§8-5 예정). 기본값은 계속 "승인 전 미실행".

### 6. 해커톤 산출물 3건
미착수 (§6). `paper/hackathon/` 미생성.

### 7. 이번 사이클 결과표에 들어간 숫자의 origin 목록
**없음.** 이번 사이클은 결과표에 어떤 숫자도 추가하지 않았고, 기존 §12 결과표를 제거했다.

### 부수 조치 — 기존 receipt 5건의 출처 소급 기입
`receipt_provenance` 게이트 신설로 Study A의 실제 실행 receipt 5건이 출처 필드 부재로 함께 걸렸다.
필드를 위조하지 않고 게이트도 낮추지 않기 위해, 각 receipt에 실측 가능한 값만 기입했다:
`origin: model_call`, `model_id: anthropic/claude-haiku-4-5`, `protocol_fingerprint`(기존 runner/parser sha256;
`variance-block`은 저장된 runner digest가 없어 design 블록 + 정렬된 episode_id 목록의 sha256으로 명시 정의),
`provider_usage_log: null`, `episode_transcripts_dir: null`, `provenance_gap` 문자열,
`evidence_level: EXECUTED_LEGACY_UNINSTRUMENTED`. 이 5건은 `.orx/paper_protocol.json`의
**동결된 `legacy_uninstrumented` 목록**에만 허용되며 신규 receipt는 전 필드가 필수다.
**잔존 위험(정직하게 기록):** 이 allowlist는 목록에 항목을 추가하면 우회가 가능하다. 게이트는 목록 자체의
증가를 막지 못하며, 추가 시 신규 결정 기록을 요구하는 것은 현재 정책이지 기계적 강제가 아니다.

next_first_action: instruction-0013 §8-3 — 7개 재료의 mechanism 노드 생성 착수. 루프 엔지니어링·그래프 엔지니어링은 정의·출처 0건이므로 `orx discover` 신규 검색 → FULL_PAPER_READ ≥ 2편 확보 후 정의한다.

## instruction-0013a 보고 — 2026-09-03T10:13:05

### A. goal
`goal.get()` 실측 결과 이전 goal `abf5e851…`이 `status: error`(tokens_used 1,602,465)였다. 0013a §A.2대로
지정 문안으로 재생성 → 신규 id `b2f7431e-942d-4fc5-b68d-cf0c316e5ffc`, status active, 토큰 예산 없음.
사유: active가 아니었음(세션 기억이 아니라 호출 결과).

### B. orx 실행 기판
- 클린 클론 run `583923a1-8680-4b7e-b729-de22b8c6f626` = **done** @ `aa4315e14`(retraction 커밋) — 게이트 통과 확인.
- `orx runs <project>`는 "Project 0dd58a66… is not registered locally. Run `orx up` first" 를 반환한다.
  현재 노드 조회는 로컬 `orx.db`로 수행했다. run 통계: done 137 · failed 18 · cancelled 5.
- **최근 실패 run 9건 원인(각 1줄):**
  1. `6fa0faee` @`ed2199922` exit1 — submission artifact is not reproducible from its committed builder
  2. `ffe9499d` @`d6a8c3679` exit1 — receipt references a path that does not exist
  3. `301aee55` @`aa7c807b2` exit1 — external source artifact recorded without a fetch url and digest (+ 경로 부재)
  4. `22a3c1e3` @`29db7d3fe` exit1 — evidence receipt or locator identity mismatch
  5. `3fe2958b` @`b2070ed09` exit1 — receipt/locator mismatch + round-4 full-read receipt·URL 불일치
  6. `531eed22` @`34bb4910f` exit1 — FileNotFoundError: 클린 클론 작업 디렉터리 경로 부재
  7. `d9d1045f` @`c2c7edbd5` exit1 — ModuleNotFoundError: No module named 'numpy'(격리 환경에 미설치)
  8. `83699d34` @`77897e238` exit1 — colab 업로드 400 Bad Request(외부 백엔드 오류)
  9. `24abc3b6` @`e14bb9570` exit1 — compiled document has overfull boxes(조판 게이트)
- receipt 필수 필드에 `orx_project_id`/`orx_experiment_id`/`orx_run_id`/`node_commit` 추가 및 run 존재·done·커밋 일치 검사와
  failing-first 1건은 **다음 사이클**에서 Study B 하네스 구축과 함께 구현한다(현재 게이트는 origin/usage/transcript 축까지 완료).

### C. exa MCP 의무 사용
- **exa 사용 불가:** `web_search_exa` → `401 Invalid API key`. 건너뛴 것이 아니라 도구가 인증 실패했다.
- 0013a §C가 허용한 **parallel MCP로 5개 항목 전부 검색**(호출 5건), 기록은 `paper/research/retrieval-record-0013.json`의 `web_queries`.
  1. 루프 엔지니어링 → `2607.01641`(When Agents Do Not Stop), `2606.27009`(Semantic Early-Stopping)
  2. 그래프 엔지니어링 → `2602.05665`(Graph-based Agent Memory taxonomy)
  3. ResearchClawBench 저장소 → `github.com/InternScience/ResearchClawBench`(라이선스·다운로드 경로는 사용 전 확인 예정)
  4. 비교 연구 공개 코드 → `2608.07545`(DarwinX, 4개 벤치마크 + ablation) 등 후보 확보
  5. 해커톤 페이지 → 본선 09-30~10-01, 총상금 1,000만원, 4개 팀 시상. **공개 심사 기준 변화 없음.**
- 채택 논문은 0006 §3대로 `orx paper`로 재획득해 provenance 확보(6편 FULL_PAPER_READ).

### §8-3. 메커니즘 노드 7/7 완료
| 재료 | 노드 | 출처 수 | 구현 아암 | 절제 아암 |
|---|---|---:|---|---|
| 최소 도구 하네스 | `mechanism:minimal_tool_coding_harness` | 3 | B0 | — |
| 영속 REPL·재귀 하네스 | `mechanism:persistent_repl_recursive_harness` | 3 | B1 | — |
| 페일클로즈드 수명주기 | `mechanism:failclosed_research_lifecycle` | 3 | B2 | B2-P |
| 결과 주도 검색 | `mechanism:result_driven_semantic_search` | 4 | B2 | B2-R |
| 타입 컨텍스트 그래프 | `mechanism:typed_research_context_graph` | 3 | B2 | B2-G |
| 루프 엔지니어링 | `mechanism:loop_engineering` | 8 | B2 | B2-L |
| 그래프 엔지니어링 | `mechanism:graph_engineering` | 4 | B2 | B2-G |

각 노드는 `definition`·`sources`·`implemented_in_arm`·`removed_in_arm`·`falsifier`를 갖는다. 전부 출처 ≥ 2편.
**키스톤 출처:** `2608.21156`이 Harness Engineering·**Loop Engineering**·**Graph Engineering**을 명시 정의하고
개별 에이전트를 `Loop(LLM + Harness)`로 형식화한다 — 사용자가 지목한 두 재료의 학술 정의가 확보됐다.
그래프 정리: 중복 스킴(`source:NNNN`) 25건 제거 후 정규 `source:arxiv:NNNN`으로 재연결, 신규 출처는 정확히 6편,
dangling 엣지 0. 노드 438 / 엣지 774. 검증 PASS. 커밋 `816559320`.

next_first_action: instruction-0013 §8-4 — `paper/research/study-b-preregistration.md` 작성 착수. 7아암(B0/B1/B2/B2-G/B2-P/B2-R/B2-L) 정의, 결정론적 검증기 과제, McNemar 1차 endpoint, Cycle 48 계산기로 과제당 40·60 에피소드 MDE를 계산해 문서에 기입하고 봉인 다이제스트를 만든다. 실행은 Q-0009 개정 승인 전까지 하지 않는다.

## instruction-0014 보고 (§6 형식) — 2026-09-03T10:30:34

### Q-0009 상태
`questions.md` 갱신 완료: **APPROVED (a) 1차 스크리닝 — 사용자, 2026-09-03 — 지출 상한은 0014a 대기**.
승인 범위 B0/B1/B2 3아암. 미승인 유지: 절제 4아암, 시나리오 (b)(c), Q-0007 별도 지출, MLE-bench Lite.
원장 **RD-2026-09-03-81A** 기록. **스크리닝 에피소드 미실행, 지출 $0.00.**

### 사전등록 §9 미완 5항목 — 개별 진행
| # | 항목 | 상태 | 증거 |
|---|---|---|---|
| 1 | ResearchClawBench 라이선스·다운로드 | **완료** | MIT 확인, HF `InternScience/ResearchClawBench`, 40개 과제, clone 경로 — `retrieval-record-0013.json` |
| 2 | 아암 7개 구현 | **완료** | `experiments/study_b/harness/`; 절제 4개가 B2와 **정확히 한 성분**만 다름을 테스트가 강제 (19/19) |
| 3 | T3 검증기·oracle 격리 | **완료** | `tasks/oracle_t3.py` 실제 계산·결정론적, `run_t3.py` 격리 강제(중첩·심볼릭 링크 거부), 테스트 15/15 |
| 4 | 고정 run command | **완료** | `run_block.py`; 미승인 지출·기판 밖 실행·드라이런 상한 초과를 **스스로 거부** |
| 5 | 비교 실험 표 | **완료** | `comparable-experiments-study-b.md` 8편 |
| 6 | 아암별 커밋 해시 봉인 | 미완 | 봉인 시점(0014a 이후) 기입 |
| 7 | 원논문 부록에서 n·검정·비용 재확인 | 미완 | 정독 보고서 범위 한정 명시함 |

### §3 항목 1~4 확정 여부 — 4/4 확정
1. **주 대비:** **B2 vs B0** 1개를 1차로 선언. B0–B1, B1–B2는 2차 **Holm 보정**(3대비, α=0.05). supervisor 권고 채택.
2. **풀링:** **1차는 과제 3종 풀링**(짝 단위 = 과제×시드), 과제별 검정과 이질성은 2차. 두 MDE를 §6에 모두 기재:
   **풀링 120쌍 0.140 / 과제별 40쌍 0.243**(불일치율 0.30). 스크립트 재계산으로 문서 수치 일치 확인.
   n 축소 시 재계산치도 확보: n=20×3 → 0.198, n=30×3 → 0.162.
3. **모델 고정:** `anthropic/claude-haiku-4-5`. 단가 $0.13463/에피소드는 이 모델의 실측값이므로 재산정·재승인 없이 변경 금지.
4. **중단 규칙:** 누적 지출이 상한 도달 시 즉시 중단, 완료분만 보고, 예산 완주율에 경쟁 사건으로 반영.
   결과에 따른 에피소드 제외 금지 유지.

### 드라이런 지출
**$0.00.** 드라이런은 아직 실행하지 않았다. `run_block.py`가 `ORX_RUN_ID` 없는 환경을 거부하므로
드라이런도 실험 노드 경로로만 수행하며, 노드 생성은 봉인 직전에 한다.

### 해커톤 산출물 3건 (0013 §6)
`paper/hackathon/` 신설: `idea-sheet-ko.md`(1쪽, 근거 상태를 "사전등록 완료·미실행"으로 명시),
`demo-scenario.md`(5분, 4:30에 B2−P 대비 시연이 핵심), `prototype-kernel.md`(B2 구현이 곧 커널, 진입점 고정).

### 이번 사이클 결과표 숫자의 origin
**없음.** MDE·단가는 각각 `power_mcnemar.py`(라벨된 검정력 계산)와 실측 receipt(`origin: model_call`)에서 왔고,
어느 것도 효능 결과표에 들어가지 않았다.

### 특기 사항 — 설계 결함 2건을 지출 전에 잡음
1. **T3 정답이 시드 간 거의 불변**이라 추측만으로 맞출 수 있었다(n=1200 ≫ d=10이라 과적합 없음).
   생성 규칙을 바꿔(n=140, d=40, 시드 의존 상호작용) 정답이 변하도록 고쳤고, 테스트가 "정답이 상수가 아님"을 강제한다.
2. **청구 잠금이 짧은 지표명을 통째로 건너뛰었다**(`f1 = 0.95`가 검사에서 누락). fail-open 결함이라 정규식을 고쳤다.
   두 결함 모두 실패 우선 테스트가 잡았다.

next_first_action: 0014a(지출 상한·과제당 n·과제 수) 수신 대기. 대기 중에는 봉인하지 않고 (a) `comparable-experiments-study-b.md` 항목 7(원논문 부록에서 n·검정·비용 재확인)을 닫고, (b) T1(ResearchClawBench 서브셋)·T2 어댑터를 구축하며, (c) `study_b.demo` 진입점을 실제로 만들어 해커톤 데모를 실행 가능하게 한다. 0014a 도착 즉시 §6 표를 승인된 n으로 재계산 → 봉인 → 아암 커밋 해시 확정 → 드라이런.

## 대기 사이클 보고 — 2026-09-03T10:36:04

0014a 미도착. 봉인하지 않고 next_first_action의 (a)(b)(c)를 진행했다.

### (c) `study_b.demo` 실행 가능화 — 완료
`/usr/bin/python3 -m study_b.demo T3 --seed 42 --arm B2`가 9단계를 실제로 수행한다.
모델 호출 0건이며, 출력되는 모든 수치는 결정론적 검증기에서 나온다(데모 스스로 그 사실을 밝힌다).
오라클을 한 번도 보지 않은 채 5/5 채점 통과. **핵심 대비 실증:**
`--arm B2` → 부풀린 초안에서 미근거 주장 2건 지목 / `--arm B2-P` → 같은 초안이 "검사 안 함"으로 **그대로 통과**.

### 지출 전에 잡은 계측기 결함 — RD-2026-09-03-82A
청구 잠금의 **절대 허용오차가 fail-open**이었다. 참값 `improvement_over_baseline = 0.02183`인데
`0.02650`(21.4% 오차)을 주장해도 통과했다 — 절대 오차 0.00467이 허용오차 0.02보다 작기 때문이다.
측정량 자체가 허용오차 크기와 비슷하면 절대 기준은 무의미하다. `max(1e-6, 0.05×|참값|)`의 상대 방식으로 바꾸고
T3 채점기에도 같은 규칙을 적용했다. 재발 방지 테스트 3건 추가(하네스 22/22, T3 15/15 통과).

### (a) 비교 실험 표 항목 7 — 완료, 그리고 **초판 진술 정정** RD-2026-09-03-83A
초판은 8편 전부 "짝지은 검정 미기재"로 적었다. **그 진술은 틀렸다.** arXiv 전문 HTML을 직접 받아 확인한 결과:
- **DarwinX [2608.07545]: paired exact McNemar 실제 사용** — TerminalWorld 41개 held-out 과제에서
  25/41 대 28/41, **p=0.45**, 저자 스스로 "decisive가 아니라 suggestive"라고 적는다.
- **HarnessOpt-Bench [2608.06301]: K=3 라운드 평균의 표준오차** 보고, "두 라운드는 산포를 추정하지 못한다"고 명시.
- 나머지 6편은 전문에서도 짝지은 추론 미확인.

정독 요약본은 방법 세부를 누락하므로 **방법 주장의 근거로 쓸 수 없다.** 표와 §3을 정정했고 초판 오류는 문서에 남겼다.
이 정정은 Study B를 약화시키지 않는다. 이탈점을 "검정의 존재"가 아니라 **"검정의 위치(사전등록 대 사후 보고)"**로
좁혔고, DarwinX의 p=0.45는 **검출력 부족의 직접 선례**가 되어 §6의 MDE 사전 공개를 뒷받침한다.

### (b) T1/T2 어댑터 — 미착수
0014a에서 과제 수(2 또는 3)가 정해지면 T1 채택 여부가 갈리므로 상한 확정 후 구축한다.

### 이번 사이클 결과표 숫자의 origin
**없음.** 데모 출력은 `origin: verifier`이며 결과표에 넣지 않았다.

next_first_action: 0014a 수신 시 즉시 (1) 승인된 과제당 n으로 §6 MDE 표 재계산 → (2) 사전등록 봉인·다이제스트를 `.orx/paper_protocol.json`에 등록 → (3) 아암 커밋 해시 확정 → (4) orx 실험 노드 생성 후 드라이런(아암당 n=1, 총 $2 상한, `PIPELINE_DRY_RUN`). 0014a 이전에는 T1/T2 어댑터와 receipt의 `orx_run_id` 검사(0013a §B-3 failing-first 1건)를 구축한다.

## 대기 사이클 보고 — 2026-09-03T10:39:05

0014a 미도착(확인함). 봉인하지 않고 0013a §B-3을 구현했다.

### 실행 기판 바인딩 게이트 — RD-2026-09-03-84A
RD-80A의 출처 게이트는 `origin`·usage·transcript 축을 검사했지만 **"그 실행이 실제로 불변 노드 안에서
일어났는가"는 묻지 못했다.** run id를 필드로 요구만 하고 조회하지 않으면 아무 문자열이나 통과한다 —
자기 신고 필드를 검사하는 게이트는 검사가 아니라 주석이다.

이제 게이트가 로컬 run 저장소에서 run을 **직접 조회**해 존재·`status = done`·`node_commit` 일치를 재도출한다.
저장소를 읽을 수 없으면 검증 불가로 **실패**시킨다(통과로 바꾸지 않는다).

**실패 우선 4건 + 정상 1건 실증:**
| 사례 | 결과 | 게이트 사유 |
|---|---|---|
| 없는 run id | FAIL | `does not exist in the run store` |
| done 아닌 run | FAIL | `has status 'failed', not 'done'` |
| 커밋 불일치 | FAIL | `node_commit ... does not match the run commit` |
| orx 필드 누락 | FAIL | `missing experiment-substrate field: orx_project_id` |
| 실제 run(`22a61c87`) 바인딩 | PASS | 통과 |

사전등록 §3에 이 계약을 반영했다.

### 이번 사이클 결과표 숫자의 origin
**없음.**

next_first_action: 0014a 수신 시 즉시 (1) 승인된 과제당 n으로 §6 MDE 표 재계산 → (2) 봉인·다이제스트 등록 → (3) 아암 커밋 해시 확정 → (4) orx 실험 노드 생성 후 드라이런(아암당 n=1, $2 상한, `PIPELINE_DRY_RUN`). 0014a 이전에는 T2(Q-0007 완주 과제) 어댑터를 구축한다 — T2는 과제 수 결정과 무관하게 승인 범위에 포함돼 있다.

## 대기 사이클 보고 (T2 어댑터) — 2026-09-03T10:41:24

### T2 예산 완주 어댑터 — 구축 완료, 실행 전제 미충족
`tasks/run_t2.py` + 테스트 9/9. 예산 소진을 **경쟁 사건**으로 다뤄 에피소드를 버리지 않는다:
`completed` / `budget_exhausted` / `failed_within_budget`를 구분하며, 상한을 넘겨도 답을 냈으면 완주로 센다.

**정직한 차단:** released/withheld 과제 번들 바이트가 이 저장소에 없다(receipt에는 digest만 있다).
어댑터는 번들을 **지어내지 않고** 전제 미충족을 보고하며 호출자를 멈춘다. 실측 출력:
`bundle directory absent: paper/experiments/task-bundles`, 필요한 4개 과제명을 함께 반환한다.
T2 실행 전에 평가자 소유 번들 확보가 필요하며 사전등록 §4에 기록했다.

### 이번 사이클 결과표 숫자의 origin
**없음.**

next_first_action: 0014a 수신 시 (1) 승인 n으로 §6 MDE 재계산 → (2) 봉인 → (3) 아암 커밋 해시 확정 → (4) orx 노드 생성·드라이런($2 상한). 0014a 이전에는 T1(ResearchClawBench) 어댑터를 구축하되 데이터는 내려받지 않고 전제 검사까지만 만든다.

## 대기 사이클 보고 (T1 어댑터 + 러너 연결) — 2026-09-03T10:44:47

### T1 ResearchClawBench 어댑터 — 구축 완료 (테스트 15/15)
- 라이선스 **MIT** 기록·검증. **비허용 라이선스면 체크아웃이 완전해도 차단**한다(테스트로 실증).
- **스스로 데이터를 내려받지 않는다.** 획득은 의도적이고 기록되는 행위이지 전제 검사의 부작용이 아니다.
  전제 미충족 시 `git clone` 명령을 호출자에게 알려줄 뿐이다.
- 서브셋 선택은 `sha256(seed:task)` 정렬이라 **디렉터리 순서에 의존하지 않고** 사전등록 보유자가 재도출할 수 있다.
  요청 수가 가용 수를 넘으면 두 수를 명시하며 거부한다.

### 러너가 어댑터에 직접 묻는다 — 네 번째 거부 경로 (테스트 10/10)
`run_block.py`는 이제 어느 어댑터도 준비됐다고 **가정하지 않는다**. 실측:
T3 `ready`(자기완결 검증기) · T1 `TASK_NOT_READY` · T2 `TASK_NOT_READY`.
연결 중 출력 dict의 `task` 키 중복으로 아암/과제 표시가 덮어써지는 버그를 발견해 고쳤고,
"덮어쓰이지 않는다"를 테스트로 고정했다.

### 전체 회귀
| 스위트 | 통과 |
|---|---:|
| 하네스 | 22 |
| T1 | 15 |
| T2 | 9 |
| T3 | 15 |
| run_block | 10 |
| 계측기 | 14 |
| **합계** | **85** |
데모 `--arm B2 --seed 42`는 여전히 오라클 대비 5/5.

### 이번 사이클 결과표 숫자의 origin
**없음.**

next_first_action: 0014a 수신 시 (1) 승인 n으로 §6 MDE 재계산 → (2) 봉인·다이제스트 등록 → (3) 아암 커밋 해시 확정 → (4) orx 노드 생성·드라이런($2 상한). 0014a 이전에는 원고 Ⅲ·Ⅳ장에 Study A를 '측정 장', Study B를 '주 장(사전등록 완료·미실행)'으로 재배치하는 작업을 시작한다 — 0013 §3이 지시한 원고 재구성이며 실행 승인과 무관하다.

## 대기 사이클 보고 (원고 재구성) — 2026-09-03T10:49:07

0013 §3의 원고 재배치를 수행했다. 실행 승인과 무관한 작업이다.

### Ⅳ장을 측정 장으로 선언
Ⅳ장 첫머리에 이 장이 **측정 장(measurement chapter)**임을 명시했다. 보고 대상은 하네스 간 우열이 아니라
**우열을 재려고 만든 계측 도구 자체의 성질**이며, Study A의 음성 결과는 실패가 아니라 Study B 설계의 입력이다.

### Ⅲ장 8절 신설 — 하네스 구성 벤치마크 설계
일곱 메커니즘과 절제 아암을 표로 넣었다(`tbl-mechanisms`). 표는 컨텍스트 그래프의 mechanism 노드를 읽어
**정독 출처가 2편 미만이면 assert로 실패**한다. 조사 문헌의 `Loop(LLM + Harness)` 형식화를 인용해
하네스 설계와 루프 설계의 구분을 실험 축으로 삼는 근거를 밝혔다. 주 대비(B2 대 B0)·Holm 보정·풀링도 본문에 고정했다.

### Ⅳ장 12절 신설 — 사전등록 완료, 미실행
아암 7개의 상태표(`tbl-studyb-status`)를 넣되 **검증기 통과율 열을 전부 "미실행"으로 채웠다.**
표는 사전등록 문서를 읽어 비실행 선언이 남아 있는지 assert한다. 미실행은 누락이 아니라 기록이다.
설계 값(MDE 0.140/0.243)은 "설계 파라미터이지 관측이 아니다"라고 본문에 명시했다.
선행 하네스 진화 연구가 41개 과제에서 짝지은 정확 McNemar로 **p = 0.45**를 얻고 스스로 결정적이지 않다고 적은
사례를 인용해, 검출 한계를 결과 이전에 공개하는 이유를 밝혔다. RD-2026-09-03-85A.

### 인용 8편 추가 — 저자를 조작하지 않음
신규 bib 항목을 만들 때 임시로 `author = {arXiv}`를 넣었는데, 이는 조작이므로 arXiv 초록 페이지에서
**실제 저자를 전부 확인해 교체**했다(8편, 최대 8인). 자리표시자 저자 0건, 짧은 저자 0건.
게이트가 인용 상한 95 → 98 증가를 잡아냈고 실제 증가이므로 기대값을 갱신했다.

### 산출물
PDF 26쪽, 형식 규칙 13/13 ENFORCED PASS, 금지어 0건, 철회 토큰 0건.

### 이번 사이클 결과표 숫자의 origin
**없음.** `tbl-studyb-status`의 결과 열은 전부 "미실행"이며, MDE·단가는 설계 값으로 분리 표기했다.

next_first_action: v4 1단계 완결 상태를 커밋/푸시하고, 스크리닝 본 블록(T3 seeds 1..39)을 (seed, arm) 순차 완결 루프로 구동한다.
