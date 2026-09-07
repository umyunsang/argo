# Option A2 root entry independent review

## Decision

**NEEDS FIX before root fan-in.**

Scope: the six hash-bound `run_entry` / staging / dev-receipt source and test files. This review used synthetic fixtures only. It did not use actual data, labels, OAuth, a provider, ORX, Docker, or native runtime changes.

Authority remained unchanged: A2 approval `fe261b55`; native construction paused; user-local OAuth pending.

## Hash-bound source

All six sources matched the review request before and after tests.

| File | SHA-256 |
|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/run_entry.py` | `facda04f10c180dc404cf34fd73de96fbfc03e0018d95c0cea1574433b17d3b0` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_run_entry.py` | `4f2faa7baebf497584122f0b143a10f42176b6073c2f92bc68754cf82c523afd` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/staging.py` | `0ad23908fcd5805b931658c10188a249b6e0c0026b1fd829c82597e3e112e469` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_staging.py` | `02ae810b40f02266a214ab76e4c3853cecb2fbb43c86b009dec79776835d6994` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/receipt_store.py` | `2c5a4b6978596b0f50a41543c909464f92d8a8376341f6bf0692ede5d79d4d4c` |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_receipt_store.py` | `ea487c560560f35dbf1b43d3ef561c457e6ae6052ead7d74eb4577c3c9de56f8` |

Contracts read in full:

| File | SHA-256 |
|---|---|
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-run-entry-contract-v1.json` | `6c992bc6b05f224f145f6fbb690ffa348549f78d1a478b80e0caa5c5d15f6933` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-selected-staging-contract-v1.json` | `a463bef32d0b269cbb2fe9bfa43a2469f252ba98a87ea897560ee5025ad1f02c` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-final-refit-lineage-v1.json` | `01e67319013506452d37ca0efdd8d15f970ac31dc369c5890ed8497521d9eef8` |
| `paper/research/public-ml-programme-qualification/house-price-p0/option-a-dev-receipt-contract-v1.json` | `55c7296d4686f77a2bb26db785877c44dfec86c0aeef86da4e27382af4b10c0e` |

## Findings

### F-01 — P1 — Invalid CSV and symlink-loop config escape the fixed protocol error boundary

Locations: `run_entry.py:69-78`, `run_entry.py:164-171`, `run_entry.py:260-275`.

`execute_entry` does not convert `csv.Error` or `RuntimeError` to `EntryError`. The fixed interface therefore does not always emit one safe `ARGO_HP_RESULT` record.

Negative evidence:

- NF-01: malformed quoted `features.csv` exited 1 with `_csv.Error: unexpected end of data`. It emitted zero `ARGO_HP_RESULT` records.
- NF-02: a controlled `local_runs_root` symlink loop exited 1 with `RuntimeError: Symlink loop`. The traceback exposed the temporary absolute path and emitted zero protocol records.

Required fix: map strict-CSV failures and the narrow `Path.resolve` loop failure to enum-only `EntryError` output.

### F-02 — P1 — A valid finite dev prediction can bypass terminal receipt publication

Locations: `run_entry.py:224-256`, `run_entry.py:260-266`; run-entry contract lines 48-54.

The frozen receipt schema admits `SCORER_ERROR`. The implementation can only copy a `RunStatus` from the runner. It converts every later `GradingError` to `ENTRY_INVALID` and writes no runner receipt.

NF-05 used exact IDs and finite `1e32` predictions. These pass `_validate_prediction_number`. The exact dev score exceeds `MAX_DEV_MAE`, so public metric formatting fails. Actual result:

```text
ARGO_HP_RESULT {{"schema_version": "argo-house-price-entry-error/v1", "status": "ENTRY_INVALID"}}
main_rc=1
runner_receipt_exists=False
```

Required fix: publish the frozen terminal `SCORER_ERROR` receipt for post-run grading/public-metric failure. Keep metric and other status-dependent fields consistent with the frozen schema.

### F-03 — P2 — Post-run log counters accept unbounded and inconsistent runner claims

Location: `run_entry.py:218-231`.

The adapter checks only exact-int and nonnegative shape. It does not enforce the fixed aggregate log bound or validate `logs_truncated` consistency.

NF-04 returned `TIMEOUT`, `stdout_bytes=10**100`, and `logs_truncated=False`. Actual result:

```text
accepted=True
stdout_digits=101
logs_truncated=False
runner_receipt_exists=True
```

Required fix: enforce the exact maximum aggregate count possible from the hash-bound `_PipeCounter`, including its bounded read-chunk overshoot. Check truncation and status consistency before receipt construction.

### F-04 — P2 — Selected-code staging leaks `RuntimeError`

Location: `staging.py:27-49`.

`Path.resolve(strict=True)` can raise `RuntimeError`, but the staging error mapping omits it. NF-03 on the exact source copy produced:

```text
exception_type=RuntimeError
safe_staging_error=False
```

Required fix: convert the narrow resolution failure to `StagingError`, or use the required nofollow directory traversal and identity check without `resolve`.

### F-05 — P2 — The local-runs/cwd relationship is not device/inode bound

Locations: `run_entry.py:69-78`, `run_entry.py:138-151`; run-entry contract line 27.

The contract explicitly rejects cwd matching without device/inode checks. `_canonical_dir` discards its `lstat` identity. `cwd.parent.parent != local_root` compares only canonical paths. File bindings are strong, but they do not prove this directory relationship.

Required fix: open `local_runs_root/<run_uuid>/repo` with `O_DIRECTORY | O_NOFOLLOW` and `dir_fd` traversal. Compare its `(st_dev, st_ino)` with the cwd identity before and after validation. This does not require an API change.

## Passing controls

- Strict config fields, duplicate-key rejection, fixed limits, and bounded config/input/solution reads are present.
- `final_refit` forbids `targets` and never grades. Only `train.csv` with its approved training target and `features.csv` are staged for the container.
- Successful predictions are reopened, bound by hash/size/mtime, checked for exact ordered IDs, and checked for finite bounded numeric lexemes.
- Candidate solution bytes are staged. This adapter never imports them on the host.
- Output collisions fail closed. Receipt publication uses `O_EXCL`. No duplicate-publication defect was found.
- `read_selected_code` uses fixed `final-solution.py`, checks supplied directory device/inode, and uses `read_bound` for exact regular-single-link bounded/hash reads.
- `verify_dev_receipt` matches every receipt field against `ExpectedDevExecution`, reopens predictions/IDs/targets, recomputes exact `Fraction` MAE, and constructs `DevResultReceipt` only after verification.
- No hidden target or metric reveal was found.

## Test commands

```text
{cmds[0]}
# exit 0; 8 tests; OK

{cmds[1]}
# exit 0; 4 tests; OK

{cmds[2]}
# exit 0; 4 tests; OK
```

All tests used `-B` and `PYTHONDONTWRITEBYTECODE=1`. `test_run_entry` read the root source only to make its controlled temporary copies.

## Negative-fixture record

All negative fixtures ran with `/usr/bin/python3 -B` in external temporary directories. They copied the exact reviewed source and its required runtime dependencies. No actual data, labels, provider, ORX, or Docker was used.

| Fixture | Controlled change | Actual result |
|---|---|---|
| NF-01 | Malformed quoted feature CSV with recomputed binding/config | RED: exit 1; `_csv.Error`; zero protocol records |
| NF-02 | `local_runs_root` symlink loop | RED: exit 1; `RuntimeError`; raw path traceback; zero protocol records |
| NF-03 | Staging `DirectoryIdentity.path` symlink loop | RED: `RuntimeError`, not `StagingError` |
| NF-04 | Runner returns 101-digit stdout count and false truncation | RED: accepted; receipt written |
| NF-05 | Runner success with exact-ID finite `1e32` predictions | RED: `ENTRY_INVALID`; no runner receipt |

## Boundary notes

`ExpectedDevExecution` independence is a bridge obligation. The current unit test builds receipt fields from the same `ExpectedDevExecution`. It proves comparison mechanics, not independent native derivation. This is the known bridge gate, not a new `receipt_store` defect.

`DirectoryIdentity` provenance is also supplied by the bridge. The helper checks the supplied identity but cannot prove how it was obtained.

Production command, real-data frozen config, immutable commit/source-digest fan-in, and OAuth remain external pending conditions. This review does not convert them into local defects or claim hostile whole-host isolation.
