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

