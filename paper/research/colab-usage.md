# GPU execution path — hosted notebook CLI usage (verified 2026-09-02)

**Scope:** operating notes for units that need a GPU. Nothing in the public manuscript names this tool.
**Rule of record:** no GPU run without pre-registration. See `paper/supervisor/cost-ledger.md` and Q-0005.

## Verified surface

`--help` and `sessions` were run locally. Commands present: `new`, `run`, `exec`, `upload`, `download`, `ls`, `rm`, `install`, `status`, `sessions`, `stop`, `log`, `repl`, `console`, `drivemount`, `restart-kernel`, `url`, `pay`, `skill`, `readme`, `version`, `update`.
Observed state at write time: `No active sessions found on server.`

`run` is the preferred entry point: it runs one script on a fresh VM and releases the VM afterwards, which matches the checkpoint-sized unit rule better than a long-lived `new` session.

## Mandatory pre-registration fields

A GPU unit may start only after these are committed:

| Field | Meaning |
|---|---|
| objective | the single question the run answers |
| fixed command | exact script path and arguments, unchanged during the run |
| input digests | sha256 of every uploaded input |
| est_CU | estimated compute units before launch |
| stop rule | wall-clock and CU ceiling that ends the run |
| checkpoint plan | what is written back, and how often, so a time limit cannot destroy the unit |

## Budget gates

- First GPU run requires an answered Q-0005.
- Approval required before any single unit exceeds 10 CU or the cumulative total exceeds 25 CU.
- Every run appends VM time, rate, est_CU, actual, and running total to `paper/supervisor/cost-ledger.md`.
- After each run: stop the session and confirm `sessions` reports none active.

## Checkpoint discipline

Hosted sessions have a wall-clock limit, so a unit is designed as a sequence of resumable checkpoints that each write results back before the limit, never as one long job whose failure loses everything.

## Current status

No GPU unit has been executed. Study A and its prerequisites do not need a GPU. Study C is the first candidate GPU unit and stays pre-registration-blocked.
