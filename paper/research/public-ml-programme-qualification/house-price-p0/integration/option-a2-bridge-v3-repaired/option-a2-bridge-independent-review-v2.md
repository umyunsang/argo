# HousePrice P0 Option A2 bridge independent review v2

## Verdict

**SCOPED PASS for the A2BR-I1–I6 repair.** No remaining local defect was found in this narrow repair. This is not live P0 admission. `actual_P0` remains `false`.

Reviewed exact bytes:

- `bridge.py` — `979c84adc265541c816a01eca39ec775eaa6374a7bc4495a2366b6ca6eefdd03`
- `test_bridge.py` — `5a45ef18dd0486a5b5eb9dccfe1090c1258a3b42fbb2768a63b749bd0ef424c2`
- `a2-bridge-report.json` — `07d53096614f2fc123731ff738923c5004c2a3d55d0c192f2ac59a610ce90b9a`

The v1 review files were preserved unchanged.

## Closure review

### A2BR-I1 — closed

All exceptions after `Popen` now use `_terminate_and_reap`. The bounded overflow test proves the bridge polls the child, sends `SIGKILL` to its process group, and calls bounded `wait`. Output-cap failure no longer bypasses process ownership.

### A2BR-I2 — closed

`verified_dev` now opens and regrades without publishing. `read_dev_result` and the refused initial third-dev path preserve the full file-tree snapshot. Continuation and final publication occur only after `write_attempt`; the tests assert attempt mtime is no later than context/receipt publication. This closes read purity and fence ordering independently of whether inputs are trusted.

### A2BR-I3 — closed

The native getter now uses one monotonic deadline across connect, send, headers, and body reads. It remains literal-IPv4 loopback, proxy-free, redirect-free, header/body bounded, and strict about 200 framing. The five-byte 0.8-second slow-drip false control raises `ExecutorError` and completes below 3.5 seconds.

### A2BR-I4 — closed

Both `Bridge.handle` and `handle_bytes` map arbitrary `Exception` to the fixed `INTERNAL_ERROR` envelope without details. A request-local fenced marker keeps failures after an R1 attempt fence at `UNCERTAIN_NO_AUTOMATIC_RETRY`.

### A2BR-I5 — closed

Process/resource numbers now require finite, nonnegative, consistent values. Native timestamps are exact non-boolean integers in `0..2**53-1`. The suite rejects JSON `1e309`, infinite resource metadata, `2**100` timestamps, and boolean `sourceSize`.

### A2BR-I6 — closed as a root-bound dependency

`option-a2-native-empty-runs-capture-v1.json` binds actual ORX 0.1.120 stdout to `No runs found.
` (`cc7066c6b42115856f1d280d847826a9a34e35c766b72fdb47a6bb807ad19317`) and empty stderr. `orx_text.py` hash `c2d1802d38a2f49b233f9e497e7ce1706f02dbb84c88a131572e4919609936fa` accepts only that exact empty form. The bridge fake now emits the captured bytes instead of a fabricated header-only table. The exact eight parser tests passed.

## Failing-first and green evidence

The reviewed v3 report embeds a seven-test exit-1 run covering I1–I5 before final repair. I5 is falsified there by the oversized native timestamp case; the process-infinity test had already received a partial intermediate repair. That intermediate source is not separately archived by hash, so the transcript is not used alone. The exact-hash v1 independent report and probe already established all five negatives:

- v1 review JSON — `382630337829afb76ce5289dade295406bb04aae049376111691dc1eae12c785`
- v1 probe stdout — `23cd8db7ee498fdff5a3939b8ac6a3b00b9abb3f7b7d4438a0d4da03122c1a9b`

New exact-copy results:

- I1–I5 regressions: **7/7 pass**, 3.078 s.
- Full focused bridge suite: **21/21 pass**, 11.762 s. This was the single requested full suite; no extra end-to-end run was launched.
- Root parser suite: **8/8 pass**, 0.003 s.

## Held dependency and context checkpoint

The exact test copy used:

- `campaign_usage.py` — `d1e658d8402eee0e967ad05f35f4f5945d2025a6484ff658f8ea30efb76dc13a`
- `orx_text.py` — `c2d1802d38a2f49b233f9e497e7ce1706f02dbb84c88a131572e4919609936fa`
- `test_orx_text.py` — `e037f4c1f66d5b24d83b56d9ff19a5bd44036172c290de9fa964f86985192ac1`

The 21-test continuation checkpoint contains a nonempty `responseId` and passed the current complete four-category usage parser. No artificial missing-response-ID success was used. Child-usage attribution and the root reader repair remain outside this bridge repair review.

## Preserved exact outputs

External temporary root: `/tmp/argo-a2-bridge-independent-review-v2-20260907T222049`

- Source manifest: `79aa25855b59b9fd6a0a6ecdf3cf0152b905c783428162b41c3d631173fbf765`
- Bridge diff: `3b2c304ef1c0c7dbb867406ad18948feaca787364e9219325d38b820082f4f2f`
- Test diff: `dcc490ac5fe5813911f71f9717d33d60752193241a55184fc2472970948aa735`
- I1–I5 stderr: `b5cbc3b30000ad024de0d76c8fa477a67f846d135f46b76fbc5c969d5bc4ba09`; stdout empty: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Full-21 stderr: `6d66e2e450eb32cc7ec13b6b0e13f3f086247a378b14c178d43eb265a2c99346`; stdout empty: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Root-8 stderr: `17c32cd3ce433174bcaddb8de325bd52013e2b37aef58ab27ee9af0e81c568a3`; stdout empty: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Native empty capture receipt: `514a34e61fdf78a7c93809aee124fe0eab0374d9a746ce5cc503ba277ffcaf53`
- Native parser validation receipt: `6b9fc29bb085dc768e0871ab7681df3d5fccf3f7d5c830f514d874d00a837cb4`

`unittest -v` wrote its full output to the preserved stderr files.

## Boundary

No actual `orx` executable, provider, auth, raw HousePrice data, Docker, `run_controller`, controller test, model call, or P0 run was used in this review. Root deployment/source-closure materialization, OAuth/provider readiness, actual task/data/environment identity, live compatibility, and the root phase-gate/current-session usage reader remain external gates. They are not reopened as bridge findings.
