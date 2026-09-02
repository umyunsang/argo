# GPU cost ledger

**Rule:** one row per GPU unit, appended before the unit starts and completed after it ends. No row, no run.
**Gates:** single unit above 10 CU or cumulative above 25 CU needs user approval. First run needs Q-0005 answered.

| date | unit | pre-registered | VM time | rate | est_CU | actual_CU | cumulative_CU | session closed |
|---|---|---|---|---|---|---|---|---|
| 2026-09-02 | Study A instrument pilot, 16 episodes | fixed command and pinned backend committed before launch | 1942.9 s agent wall time, no VM | no GPU | 0 CU | 0 CU | 0 CU | no session opened |

**Backend probe, 2026-09-02:** session provider `HTTP 429 usage limit reached` (resets in about 4.8 days); one hosted provider timed out at 240 s; one router `HTTP 402 insufficient credits`; two selectors answered correctly. Treatment pinned to `anthropic/claude-haiku-4-5`; rubric judging reserved for a different provider family.

**Pilot resource record:** 16 episodes, total wall time 1942.9 s, artifacts 287,707 bytes. Per-episode token usage is `UNMEASURED` because the headless text mode emits no usage record; the confirmatory run must use the json output mode. The 2,000,000-token gate could therefore not be evaluated from measurement and no GPU or compute unit was consumed.

**Cumulative to date: 0 CU.** Verified at 2026-09-02T21:52: `sessions` reported no active sessions.
