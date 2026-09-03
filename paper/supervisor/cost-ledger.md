# GPU cost ledger

**Rule:** one row per GPU unit, appended before the unit starts and completed after it ends. No row, no run.
**Gates:** single unit above 10 CU or cumulative above 25 CU needs user approval. First run needs Q-0005 answered.

| date | unit | pre-registered | VM time | rate | est_CU | actual_CU | cumulative_CU | session closed |
|---|---|---|---|---|---|---|---|---|
| 2026-09-02 | Study A instrument pilot, 16 episodes | fixed command and pinned backend committed before launch | 1942.9 s agent wall time, no VM | no GPU | 0 CU | 0 CU | 0 CU | no session opened |

**Backend probe, 2026-09-02:** session provider `HTTP 429 usage limit reached` (resets in about 4.8 days); one hosted provider timed out at 240 s; one router `HTTP 402 insufficient credits`; two selectors answered correctly. Treatment pinned to `anthropic/claude-haiku-4-5`; rubric judging reserved for a different provider family.

**Pilot resource record:** 16 episodes, total wall time 1942.9 s, artifacts 287,707 bytes. Per-episode token usage is `UNMEASURED` because the headless text mode emits no usage record; the confirmatory run must use the json output mode. The 2,000,000-token gate could therefore not be evaluated from measurement and no GPU or compute unit was consumed.

**Cumulative to date: 0 CU.** Verified at 2026-09-02T21:52: `sessions` reported no active sessions.

## 2026-09-02 — measured model cost enters the ledger

Until this entry the ledger tracked GPU credit units only, and model cost was
unmeasured. Three probes on the pinned treatment backend, run in structured output
mode and parsed by committed code, produced the first measured figures.

| probe | marginal in+out tokens | total tokens | cost (USD) |
|---|---:|---:|---:|
| trivial reply, cold cache | 60 | 46823 | 0.05871 |
| trivial reply, warm cache | 49 | 46812 | 0.00488 |
| four-sentence reply, warm cache | 394 | 47170 | 0.00719 |

Probe total: $0.07079. GPU credit units remain 0 and `colab sessions` remains empty.

The fixed context floor is 46,763 tokens in all three probes, so total tokens are
not a usable comparison quantity. Dollar cost for identical work differed 12.03x
with cache state alone. Per RD-2026-09-02-23A the block reports marginal tokens and
states the floor separately.

## 2026-09-02 — first measured episode cost, and a falsified assumption

Two real episodes of a burned pilot task, same pinned backend, structured output mode.

| condition | context tokens | marginal in+out | total | cost (USD) |
|---|---:|---:|---:|---:|
| C00 minimal | 51,596 | 385 | 51,981 | 0.01208 |
| C11 scaffold + retrieval | 76,496 | 789 | 77,285 | 0.01287 |

Episode total: $0.02495. Cumulative measured model cost: $0.09574. GPU credit units remain 0.

The probe-derived fixed floor of 46,763 tokens did not hold. Context differs by 24,900
tokens between conditions because the full condition mounts an evidence pack. RD-2026-09-02-23A
is falsified and replaced by RD-2026-09-02-24A: context and marginal tokens are reported
separately and neither is treated as a constant.

## 2026-09-02 — repeat variance, and why one episode is not a value

Six episodes, one burned task, three repeats per condition, identical workspace digest
within each condition.

| condition | context mean | context sd | CV | within range |
|---|---:|---:|---:|---:|
| C00 minimal | 51,138 | 1,484 | 2.9% | 2,746 |
| C11 scaffold + retrieval | 79,320 | 8,997 | 11.34% | 17,231 |

Six-episode cost: $0.07032. Cumulative measured model cost: $0.16606. GPU credit units remain 0.

The retrieval condition varies about four times more than the minimal one, and its
within-condition range covers 61.1% of the between-condition gap. RD-2026-09-02-24A is
refined by RD-2026-09-02-25A: cost is reported as a mean over repeats with its spread.

## 2026-09-02 — every earlier cost figure in this ledger is void

The token accounting parser read the last usage record as the run total. Usage is per
completed API call and context is re-sent on every call, so the parser understated one
episode by **14.4x**. Its fixture asserted the same wrong assumption, so the suite passed
while the instrument was wrong. Transcripts captured through standard output were also
truncated in four of six runs. Both are fixed; transcripts are now written to files and
checked for completeness.

**All dollar and token figures in the entries above are void.** Corrected measurement over
six episodes from complete transcripts:

| condition | API calls | context tokens | marginal | total | cost (USD) |
|---|---:|---:|---:|---:|---:|
| C00 minimal | 3.3 | 161,835 | 5,416 | 167,251 | 0.10280 |
| C11 scaffold + retrieval | 9.7 | 511,551 | 9,418 | 520,969 | 0.16642 |

Six-episode measured cost: $0.80776. Corrected cumulative measured model cost is
not recoverable for the earlier runs, whose transcripts were truncated; only this block is
reported as measured. GPU credit units remain 0 and `colab sessions` remains empty.

## 2026-09-03 — first admissible confirmation episodes

Eight episodes on two unburned tasks, structured output mode, all admissible under the
declared ceilings.

| condition | context tokens (mean) | marginal (mean) | calls (mean) |
|---|---:|---:|---:|
| C00 | 145,035 | 4,458 | 3.0 |
| C11 | 734,579 | 11,604 | 13.5 |

Block cost: $1.26082. GPU credit units remain 0.
No treatment effect is estimated from one repeat per cell.

## 2026-09-03 — second repeat, and the first binding ceiling

Eight further episodes completed the two-repeat design. Block cost $1.20026;
cumulative for the confirmation block $2.46108. GPU credit units remain 0.

One episode was refused for exceeding the declared call ceiling, 18 against 16. It fell in
the full condition, which uses the most calls in every observation. The ceiling was left
where measurement placed it and the violation is treated as an outcome.

## 2026-09-03 — judging cost measured both ways

Three items judged both ways by the same judge in structured output mode.

| path | mean total tokens | mean cost |
|---|---:|---:|
| span-based | 56,676 | $0.02682 |
| full artifact | 90,309 | $0.04320 |

Ratio 1.61. Projected judging cost for a 116-episode block at six elements each:
span only $18.67, full only $30.07, full plus a twenty percent
span subsample $33.8. This belongs to the quality arm and does not
change the pending completion-arm question. GPU credit units remain 0.

## Hugging Face 판정기 (Hugging Face judge calls)

판정기 호출(`huggingface/Qwen3.6-27B`, `huggingface/GLM-5.3`)은 Hugging Face Inference Providers를
경유하며 크레딧을 소비한다. 이 절은 **소급 추정**이다: 해당 호출들은 텍스트 모드로 실행되어 usage가
기록되지 않았으므로 토큰 수를 프롬프트 크기에서 추정했고, 단가는 **보수적 상한**(입력 $2.00/1M,
출력 $4.00/1M, 출력 200토큰 가정)을 적용했다. 실제 비용은 이보다 낮을 가능성이 높다.
가정임을 명시하며, 이 수치를 실측값으로 인용하지 않는다.

| 시각 | 호출 묶음 | 호출 수 | 입력토큰/호출(추정) | USD(상한 추정) |
|---|---|---:|---:|---:|
| 2026-09-02 13:12 | backend probes | 3 | 600 | 0.006 |
| 2026-09-02 15:39 | verified endpoint element judgements | 174 | 900 | 0.452 |
| 2026-09-02 17:17 | judge reliability set | 78 | 900 | 0.203 |
| 2026-09-03 cycle 52 | cross-judge replication | 78 | 1,200 | 0.250 |
| 2026-09-03 cycle 53 | no-span full-artifact re-judgement | 18 | 3,500 | 0.140 |
| 2026-09-03 cycle 54 | span-negative full-artifact re-judgement | 18 | 3,500 | 0.140 |
| 2026-09-03 cycle 55 | span versus full cost comparison | 6 | 2,000 | 0.029 |
| 2026-09-03 cycle 56 | whole-artifact rescore | 30 | 3,500 | 0.234 |
| 2026-09-03 01:34 | judged verdict replay | 24 | 900 | 0.062 |
| 2026-09-03 01:46 | mid-band stability | 50 | 900 | 0.130 |
| 2026-09-03 cycle 60 | second-repeat whole-artifact judgement | 42 | 3,500 | 0.328 |
| **누적** | 2026-09-02 13:12 이후 | **521** | — | **1.97** |

- 상한 규칙: 누적 추정 USD가 10을 넘으면 새 HF 호출을 멈추고 Q를 올린다. 현재 **1.97 < 10**이므로 계속한다.
- 앞으로의 HF 호출은 receipt에 `provider: huggingface`, 호출 수, USD를 남긴다.
- 판정기 유지 근거: 처치 모델(anthropic 계열)과 제공자 계열이 달라 독립성이 유지된다. anthropic 계열로
  바꾸면 처치와 제공자가 겹친다.

## 이미지 생성 (image generation)

| 시각 | 모델 | 호출 | 결과 | USD |
|---|---|---:|---|---:|
| 2026-09-03T05:26:37+09:00 | gpt-image-2 | 1 | HTTP 429 `credit_balance_exhausted`, 이미지 미반환 | 0.00 |

누적 이미지 USD **0.00**. 자격 증명은 유효하나 계정 크레딧이 없어 벡터 폴백을 유지한다.
## Study B 하네스 비교 지출 (Study B harness comparison spend)

| 시각 | 단계 | 아암 | 과제 | 시드 | 모델 | 토큰 | USD | 비고 |
|---|---|---|---|---|---|---:|---:|---|
| 2026-09-03T15:08:45+09:00 | 드라이런 | B0 | T3 | 42 | anthropic/claude-haiku-4-5 | 405,799 | 0.134 | PIPELINE_DRY_RUN (answers.json 제출 완료, 검증기 1/5) |
| 2026-09-03T15:08:45+09:00 | 드라이런 | B1 | T3 | 42 | anthropic/claude-haiku-4-5 | 391,973 | 0.138 | PIPELINE_DRY_RUN (answers.json 제출 완료, 검증기 2/5) |
| 2026-09-03T15:08:45+09:00 | 드라이런 | B2 | T3 | 42 | anthropic/claude-haiku-4-5 | 547,290 | 0.118 | PIPELINE_DRY_RUN (answers.json 제출 완료, 검증기 1/5) |
| 2026-09-03T15:42:12+09:00 | 2차 드라이런 | B0 | T3 | 42 | anthropic/claude-haiku-4-5 | 636,485 | 0.170 | PIPELINE_DRY_RUN (b0_tools.js, ipython 0회, 조작 PASS) |
| 2026-09-03T15:43:33+09:00 | 2차 드라이런 | B1 | T3 | 42 | anthropic/claude-haiku-4-5 | 505,061 | 0.156 | PIPELINE_DRY_RUN (b0_tools.js + ipython 5회, 조작 PASS) |
| 2026-09-03T15:46:00+09:00 | 2차 드라이런 | B2 | T3 | 42 | anthropic/claude-haiku-4-5 | 213,698 | 0.110 | PIPELINE_DRY_RUN (b2_harness.js, 게이트차단 1회 후 결정 3/임계 4, 조작 PASS) |
| **드라이런 합계** | — | **3개 (2회)** | **T3** | — | — | **2,700,306** | **0.826** | **드라이런 상한 $2.00 이내 (잔여 $1.174)** |
| **스크리닝 누적** | — | — | — | — | — | **0** | **0.000** | **스크리닝 상한 $48.47 미사용 (0014a)** |

### 2026-09-03 17:34 — 계획되지 않은 지출 (테스트 픽스처가 실제 에피소드를 실행)

| 항목 | 값 |
|---|---|
| 원인 | `run_block.py`에 실행 경로를 추가한 직후 `test_run_block.py`의 긍정 검사가 `ORX_RUN_ID=probe`(위조 기판 id)로 실제 B2/T3 dry-run 에피소드를 실행 |
| 지출 | **$0.085264**, 163,293 tokens, 1 에피소드 (B2/T3 seed 0) |
| 결과 | 지출 후 `relative_to(ROOT)`(경로가 `/tmp`)에서 크래시 → **영수증 미작성**. 사용량은 `/tmp/usage_B2_T3.json`에만 남음 |
| 인정 여부 | **불인정** (기판 밖, 위조 run id). 결과 표에 들어가지 않음. 예산에는 계상 |
| dry-run 누적 | $0.826 + $0.085264 = **$0.911264** / $2.00 (잔여 $1.088736) |
| 스크리닝 누적 | $0.00 / $48.47 (변동 없음) |

교훈: (1) 기판 검사가 문자열 존재만 봐서 위조 가능했다 → run id가 실제 run 디렉터리로 해석되는지 검사하도록 강화. (2) 실행기는 테스트에서 주입 가능해야 하며, 서브프로세스 긍정 검사는 실행기 주입 없이 돌리면 안 된다. (3) 지출 뒤 크래시가 영수증을 삼켰다 → 완료된 에피소드는 항상 영수증에 남기고 중단 상태를 기록하도록 수정.

### 2026-09-03 18:0x — 3차 dry run (실행 가능한 run command의 첫 기판 내 실행)

| 항목 | 값 |
|---|---|
| run | `2727d134-8d32-47b3-8cb3-576aa3cb4f00`, 스냅샷 커밋 `ce2bc723a`, B2/T3 seed 0, 1 에피소드, 81 s |
| 지출 | **$0.178769**, 591,695 tokens |
| 조작 검사 | PASS (decisions 1, thresholds 3, graph_add 1, loop_evaluate 3, gate_blocks 0) |
| 영수증 | `paper/experiments/study-b-dryrun3-B2-T3-receipt.json` (`evidence_level=PIPELINE_DRY_RUN`, `executor=study_b.episode_runner:run_episode`, `orx_run_id` 실제 run 디렉터리) |
| 결함 | `harness_commit=""` — 기판은 `.git` 없는 스냅샷을 실행하므로 git 기반 식별이 비었다. 다음 리비전부터 바이트 유도 blob id(`code_identity`)로 대체 |
| dry-run 누적 | $0.911264 + $0.178769 = **$1.090033** / $2.00 (잔여 $0.909967) |
| 스크리닝 누적 | $0.00 / $48.47 |

단가 관찰: 1차 $0.130, 2차 $0.145, 3차 $0.179 (B2 단독). B2는 도구 사용이 많아 아암 중 가장 비싸다. 스크리닝 예산은 실측 triple 단가로 다시 산정한다.

### 2026-09-03 — 스크리닝 1단계 (실측 단가 triple, T3 seed 0) — 진행 중

| 아암 | run | 스냅샷 | 에피소드 | 시간 | 토큰 | 지출 | 조작검사 | 스크리닝 누적 / $48.47 |
|---|---|---|---|---:|---:|---:|---|---:|
| B0 | `e23f60e8-3f36-4776-826b-2df51fb38bcb` | code digest `05ca89bd1c432bc0` | 1 | 88 s | 656,018 | **$0.183918** | PASS (bash 7, read 2, write 1, ipython 0) | **$0.183918** |
| B1 | `10c8db47-dddd-452c-be18-9dda9032003a` | same | 1 | 52 s | 36,463 | **$0.040690** | PASS (ipython 5) | $0.224608 |
| B2 | `40bcbfbf-079a-4b9f-8cbc-a30807fdfc56` | same | 1 | 94.7 s | 122,067 | **$0.075601** | PASS (decisions 3, thresholds 3, graph 8, pivots 1, gate_blocks 0) | **$0.300209** |

**Triple 실측 단가 $0.300209** (v2 추정 3×$0.1454=$0.436보다 낮음). 잔여 $48.169791 → 산술상 160 triple.
**블록 착수 보류 (RD-95A):** 세 아암 모두 5항목 중 1개만 통과했고, 실패 원인이 아암이 아니라 T3 검증기의 **미명시 규약**(비셔플 폴드, 200회 GD 미수렴 해, λ↔C 스케일, `sparsity20_bits4` 정확 문자열)에 있음이 확인됐다. 이 상태의 블록은 "검증기의 사적 규약을 맞혔는가"를 재므로 사전등록 엔드포인트가 아니다. 검증기 수정·v4 봉인 전까지 스크리닝 지출 없음.

### 2026-09-03 — 스크리닝 1단계 v4 재실행 (T3 seed 0) — 진행 중

| 아암 | run | 스냅샷 | 시간 | 토큰 | 지출 | n_pass (파일럿→v4) | 스크리닝 누적 / $48.47 |
|---|---|---|---:|---:|---:|---|---:|
| B0 | `8e815dee-05ab-490f-8583-e4cf3563c22c` | `33bba4e36` | 54 s | 314,086 | **$0.129302** | 1/5 → **5/5** | $0.429511 |
| B1 | `fb9f9569-9abe-4c46-8159-4185a6d80855` | `33bba4e36` | 82 s | 724,419 | **$0.199258** | 1/5 → **5/5** | $0.628769 |
| B2 | `d7695483-80af-4f7d-a22d-26b5f0cc29e5` | `33bba4e36` | 93 s | 862,891 | **$0.211856** | 1/5 → **5/5** | **$0.840625** |

**v4 1단계 완결 요약:**
- 3개 아암 모두 **5/5 만점** 달성 (pilot 1/5 → v4 5/5).
- RD-95A falsifier 미발화: 오라클 규약 명시 및 의미 채점 도입으로 세 아암이 모두 정답에 도달함. 과제 유효성 검증 완료.
- v4 triple 실측 단가: **$0.540416** (B0 $0.129302, B1 $0.199258, B2 $0.211856).
- 누적 스크리닝 지출: **$0.840625 / $48.47** (잔여 $47.629375).
- 잔여 예산으로 가능한 추가 triple: **88 triples** (seed 1..88).
| Block | T3 | s1 | B0/B1/B2 | 3 | $0.1486/$0.1916/$0.2026 | **$0.542766** | 3/3/5 | **$1.083182** |
| Block | T3 | s2 | B0/B1/B2 | 3 | $0.1424/$0.1933/$0.0896 | **$0.425312** | 1/5/5 | **$1.508494** |
| Block | T3 | s3 | B0/B1/B2 | 3 | $0.1285/$0.1618/$0.0718 | **$0.362041** | 5/3/5 | **$1.870535** |
| Block | T3 | s4 | B0/B1/B2 | 3 | $0.1419/$0.1756/$0.0804 | **$0.397911** | 3/5/5 | **$2.268446** |
| Block | T3 | s5 | B0/B1/B2 | 3 | $0.1394/$0.1717/$0.0857 | **$0.396784** | 5/5/4 | **$2.665230** |
| Block | T3 | s6 | B0/B1/B2 | 3 | $0.1580/$0.1687/$0.2725 | **$0.599197** | 5/3/5 | **$3.264427** |
| Block | T3 | s7 | B0/B1/B2 | 3 | $0.1367/$0.1754/$0.0729 | **$0.384969** | 3/3/5 | **$3.649396** |
| Block | T3 | s8 | B0/B1/B2 | 3 | $0.1369/$0.2016/$0.0767 | **$0.415170** | 5/5/5 | **$4.064566** |
| Block | T3 | s9 | B0/B1/B2 | 3 | $0.1389/$0.1816/$0.0683 | **$0.388731** | 2/3/5 | **$4.453297** |
| Block | T3 | s10 | B0/B1/B2 | 3 | $0.1367/$0.1894/$0.2414 | **$0.567510** | 3/5/5 | **$5.020807** |
| Block | T3 | s11 | B0/B1/B2 | 3 | $0.1399/$0.1974/$0.2289 | **$0.566160** | 5/5/5 | **$5.586967** |
| Block | T3 | s12 | B0/B1/B2 | 3 | $0.1391/$0.1724/$0.2189 | **$0.530403** | 4/5/5 | **$6.117370** |
| Block | T3 | s13 | B0/B1/B2 | 3 | $0.1394/$0.2078/$0.1963 | **$0.543399** | 5/5/5 | **$6.660769** |
| Block | T3 | s14 | B0/B1/B2 | 3 | $0.1723/$0.1552/$0.2105 | **$0.537973** | 4/5/3 | **$7.198742** |
| Block | T3 | s15 | B0/B1/B2 | 3 | $0.1712/$0.1829/$0.0687 | **$0.422817** | 3/5/5 | **$7.621559** |
| Block | T3 | s16 | B0/B1/B2 | 3 | $0.1471/$0.1945/$0.0749 | **$0.416504** | 2/3/5 | **$8.038063** |
| Block | T3 | s17 | B0/B1/B2 | 3 | $0.1683/$0.2044/$0.0880 | **$0.460681** | 3/5/3 | **$8.498744** |
| Block | T3 | s18 | B0/B1/B2 | 3 | $0.1288/$0.1932/$0.0774 | **$0.399479** | 5/5/5 | **$8.898223** |
| Block | T3 | s19 | B0/B1/B2 | 3 | $0.1372/$0.2086/$0.0837 | **$0.429524** | 5/5/5 | **$9.327747** |
| Block | T3 | s20 | B0/B1/B2 | 3 | $0.1434/$0.2194/$0.0906 | **$0.453373** | 3/5/5 | **$9.781120** |
| Block | T3 | s21 | B0/B1/B2 | 3 | $0.2193/$0.1840/$0.2158 | **$0.619112** | 5/5/5 | **$10.400232** |
| Block | T3 | s22 | B0/B1/B2 | 3 | $0.1501/$0.1832/$0.2245 | **$0.557821** | 5/5/5 | **$10.958053** |
| Block | T3 | s23 | B0/B1/B2 | 3 | $0.1412/$0.0541/$0.2123 | **$0.407640** | 5/5/5 | **$11.365693** |
| Block | T3 | s24 | B0/B1/B2 | 3 | $0.1795/$0.1732/$0.0887 | **$0.441465** | 5/3/5 | **$11.807158** |
| Block | T3 | s25 | B0/B1/B2 | 3 | $0.1281/$0.1685/$0.0951 | **$0.391811** | 5/5/5 | **$12.198969** |
| Block | T3 | s26 | B0/B1/B2 | 3 | $0.1271/$0.1902/$0.2037 | **$0.520985** | 3/5/4 | **$12.719954** |
| Block | T3 | s27 | B0/B1/B2 | 3 | $0.1416/$0.1615/$0.0710 | **$0.373993** | 5/3/5 | **$13.093947** |
| Block | T3 | s28 | B0/B1/B2 | 3 | $0.1514/$0.1718/$0.2247 | **$0.547935** | 1/5/3 | **$13.641882** |
| Block | T3 | s29 | B0/B1/B2 | 3 | $0.1431/$0.1897/$0.0800 | **$0.412798** | 3/5/5 | **$14.054680** |
| Block | T3 | s30 | B0/B1/B2 | 3 | $0.1410/$0.1580/$0.0681 | **$0.367103** | 5/3/5 | **$14.421783** |
| Block | T3 | s31 | B0/B1/B2 | 3 | $0.1466/$0.1854/$0.0814 | **$0.413287** | 5/3/5 | **$14.835070** |
| Block | T3 | s32 | B0/B1/B2 | 3 | $0.1872/$0.0710/$0.0698 | **$0.327947** | 5/5/5 | **$15.163017** |
| Block | T3 | s33 | B0/B1/B2 | 3 | $0.1403/$0.1817/$0.0855 | **$0.407468** | 3/3/5 | **$15.570485** |
| Block | T3 | s34 | B0/B1/B2 | 3 | $0.1623/$0.1771/$0.0822 | **$0.421590** | 5/3/5 | **$15.992075** |
| Block | T3 | s35 | B0/B1/B2 | 3 | $0.1600/$0.1846/$0.2137 | **$0.558305** | 5/5/5 | **$16.550380** |
| Block | T3 | s36 | B0/B1/B2 | 3 | $0.1471/$0.1868/$0.2043 | **$0.538238** | 3/5/5 | **$17.088618** |
| Block | T3 | s37 | B0/B1/B2 | 3 | $0.1342/$0.2584/$0.1228 | **$0.515436** | 5/5/5 | **$17.604054** |
| Block | T3 | s38 | B0/B1/B2 | 3 | $0.1408/$0.1647/$0.0813 | **$0.386742** | 3/5/5 | **$17.990796** |
