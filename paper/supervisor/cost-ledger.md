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
