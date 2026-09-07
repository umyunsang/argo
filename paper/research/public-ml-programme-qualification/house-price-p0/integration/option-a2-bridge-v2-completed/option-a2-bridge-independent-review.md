# HousePrice P0 Option A2 bridge independent review

## Verdict

**NOT ADMITTED for live P0.** The exact requested slice has two blocker defects and four further substantive findings. `actual_P0` remains `false`. The 17 focused tests pass, but they do not establish live ORX or source provenance.

Reviewed exact bytes:

- `bridge.py` — `2ec0f2791274d4c83994c2172b69f9655ec90e2c27d7d9e76288ed20f3a9d5c2`
- `test_bridge.py` — `c5d68741c2d4e8e8fa41f62736913b3017f71ba5d19fcde828cac981e0b9dc38`
- `a2-bridge-report.json` — `894764ba930968056e3ab45c13ef304cba47d614d32c47caa71fc5e20820ff59`

## Findings

### A2BR-I1 — BLOCKER — output overflow skips child termination and reap

`bridge.py:350-359` raises `ExecutorError` on aggregate stdout/stderr overflow. The cleanup handler at `bridge.py:367-376` does not catch `ExecutorError`. A bounded mocked probe reproduced `poll_calls=0`, `wait_calls=0`, and `kill_calls=0` after overflow. A still-running ORX/Git child can continue effects after the bridge returns uncertainty.

Required: route every post-spawn failure, including `ExecutorError`, through one kill-process-group and wait/reap path. Add an alive-child overflow regression.

### A2BR-I2 — BLOCKER — read-only gates and pre-fence checks persist state

`FixedNativePort.verified_dev` publishes a receipt at `bridge.py:698-731`. `Bridge._dev_result` calls it at `1243-1245`, although the phase-gate contract labels `read_dev_result` read-only. The exact-copy synthetic production path added `receipts/<run_id>.json` during that read.

The same writer is called during context checks (`1343-1364`) and final validation (`1150-1153`) before the attempt fences at `1123`/`1155`. Continuation admission is also written at `1375` before the fence. Thus a gate read or a later-denied request can change durable state without an attempt record.

Required: split pure verification/regrading from publication. Keep all phase-gate reads pure. Compute admission/eligibility without writes, persist the attempt fence, and only then publish context/receipt/admission facts for that attempt.

### A2BR-I3 — HIGH — HTTP timeout is not a total three-second deadline

`StrictNativeGetter` sets a three-second socket timeout at `bridge.py:393`, then makes several blocking operations at `395-405` without a monotonic total deadline. A loopback response of four bytes spaced 1.1 seconds apart succeeded after **3.309 seconds**.

Required: enforce one three-second deadline over connect, headers, and every body read. Keep direct `127.0.0.1`, no proxy, no redirect, status 200, and the 128 KiB cap.

### A2BR-I4 — HIGH — arbitrary dependency exceptions escape both handler APIs

The fixed exception tuples in `Bridge.handle` (`1052-1055`) and `handle_bytes` (`1025`) omit `RuntimeError`/`ExecutorError`. An injected `RuntimeError` from `TrustedIo.read_solution` escaped both claimed APIs. The phase gate uses `Bridge.handle` directly, so `main()`'s broad catch is not sufficient.

Required: add an outer `Exception`-to-`INTERNAL_ERROR` boundary without catching `BaseException`. Preserve `UNCERTAIN_NO_AUTOMATIC_RETRY` after an R1 fence and never return exception text.

### A2BR-I5 — MEDIUM — strict metadata accepts non-finite and unsafe integers

`_valid_prior_process_receipt` (`1741`) accepts any numeric `elapsed_seconds`. Valid JSON `1e309` became positive infinity and passed. `parse_native_run_json` (`1505-1516`) accepted `createdAt=updatedAt=endedAt=2**100`, despite the frozen schema's `safeinteger` requirement. The unexpected-field false control was rejected.

Required: require finite, nonnegative, internally consistent receipt metadata. Bound native timestamps to the selected JSON safe-integer range.

### A2BR-I6 — HIGH — first-root preflight depends on uncaptured empty `orx runs` bytes

`FixedNativePort.prepare` calls `_cli_state` before launch (`637`), and `_cli_state` always calls `orx runs` (`840-843`). The parser requires a table header. Existing inert receipts capture `exp status` with `last run: — (never run)`, but not exact empty `orx runs` output. `test_bridge.py:662-666` fabricates a header-only table.

Required: in root setup, capture and hash actual ORX 0.1.120 empty-list stdout/stderr/exit code, then bind the parser fixture or revise preflight. Do not infer it from fake ORX.

## Verified controls

- Exact temporary source copy passed all 17 focused tests: 17/17, 8.672 s.
- Invalid typed arguments returned `INVALID_ARGUMENT`.
- Extra deployment/native fields were rejected.
- Canonical directory checks rejected symlink and explicit-`..` forms.
- The synthetic normal path exercised Git blob/config binding, native tar binding, run-to-experiment parent mapping, selected historical final bytes, dev regrade, prediction IDs, and O_EXCL final-lock publication.
- The portable `-m` entry has top-level imports and no `sys.path` mutation. Its outside-CWD fake test passed.
- Once an attempt fence exists, unbound attempts and nonterminal/UNKNOWN observations block later R1 admission. Attempt counts do not rely only on bindings.

## Validation evidence

External temporary root: `/tmp/argo-a2-bridge-independent-review-20260907T213954`

- Full-17 command: `full17-command.txt` SHA-256 `26729d597d0cda26997fb551e4f93fe2e6b34480fb27d0d835f80f8408230335`
- Full-17 stdout: `full17-stdout.txt` SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty; `unittest -v` wrote to stderr)
- Full-17 stderr: `full17-stderr.txt` SHA-256 `8148a3bd01c4743b5317d58c0b4670867448ae5939861482bb83c5ab9337c5c7`
- Probe command: `probe-command.txt` SHA-256 `458e1ea700a88a0df0de735fb60f8abbc8cea93f087ea1c6a999c1f815a91cb4`
- Probe stdout: `probe-stdout.txt` SHA-256 `23cd8db7ee498fdff5a3939b8ac6a3b00b9abb3f7b7d4438a0d4da03122c1a9b`
- Probe stderr: `probe-stderr.txt` SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty)
- Probe source: `independent-probes.py` SHA-256 `e63e694df7c5f35a64d840777935b224faa36b17ed4958ce5a683c69df346f02`

No actual `orx` executable, service, provider, auth, raw HousePrice data, Docker, `run_controller`, controller test, model call, or P0 run was used.

## External open conditions, not new local findings

Root deployment/module sealing, root source-closure audit, ORX/OAuth/local-login readiness, actual task/data/environment identity, and actual ORX/provider/Docker compatibility remain external gates. This review does not relabel them as bridge defects.
