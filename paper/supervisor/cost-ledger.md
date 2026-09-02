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

