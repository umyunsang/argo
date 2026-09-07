# HousePrice P0 A2 synthetic-combination contract review v1

## Verdict

**BLOCKED before root combination-driver implementation.** The contracts are directionally consistent, but five exact integration gaps remain. They concern construction and evidence semantics, not general P0 readiness. No unfinished fixture or acceptance source was treated as final.

## CBR-01 — BLOCKER — the frozen namespace materializer cannot build the contracted synthetic namespace

`option-a2-combination-driver-source-v1.json` requires `namespace_tree` to contain the runtime plus the combination driver, fixture, acceptance module, and the test-only NativeHarness dependency. `option-a2-combination-source-contract-v2.json` also names `test_bridge.py` as synthetic-only namespace material.

The frozen `deployment_assets.py` contradicts that requirement:

- `RUNTIME_NAMES`/`MEMBER_PATHS` do not include `combination_driver.py`, `combination_fixture.py`, `combination_acceptance.py`, or `test_bridge.py`.
- `materialize_namespace` rejects every member outside `MEMBER_PATHS`.
- This production namespace allowlist should not be silently broadened with test-only code.

**Correction:** freeze a separate synthetic-only namespace materializer and exact allowlist for A2-Faux-C1. It must include only the reviewed runtime dependencies plus the exact driver/fixture/acceptance/NativeHarness files, emit a SourceTree, and remain impossible to call from production materialization. Do not add test modules to production `RUNTIME_NAMES`.

## CBR-02 — BLOCKER — the required pre-import seal has no executable entry contract

The combination driver API is only `run_case(config)`. Importing it will execute its static imports, including the fixture/acceptance chain, before `run_case` can verify `namespace_tree`. The contracts correctly say the external caller must verify the namespace before import, but no fixed caller/bootstrap/config encoding is defined. The existing `write_module_bootstrap` supports only Bridge and phase-gate modules; the driver contract explicitly has no CLI.

**Correction:** freeze a root-only one-shot pre-import entry. It must use only already sealed deployment/source-closure code, open a bounded case-config file, rederive the synthetic namespace and installed Prime trees, then `execve` a fixed installed module/entry with no user argv. Alternatively define an equally concrete pre-import root caller. Do not solve this with `sys.path` mutation or a dynamic import inside the unverified namespace.

## CBR-03 — BLOCKER — fixture cleanup confirmation has no typed producer interface

The output contract requires `cleanup_confirmed`, maps failure to `CLEANUP_UNCONFIRMED`, and says the driver closes exactly its owned fixture once. The fixture contracts only say `close()` is idempotent and tracks ownership; they do not define a return type, terminal fields, or what constitutes confirmed server shutdown. The future driver cannot derive the required boolean without inventing semantics or trusting absence of an exception.

**Correction:** freeze `CombinationFixture.close() -> FixtureCloseResult` (or an exact boolean contract) with fields sufficient to prove the one owned server was shut down and its serve thread/socket closed. Define first-call and repeated-call behavior, bounded deadline, and how an exception/unknown maps to false. The final receipt must bind that result; no cleanup inference from process success.

## CBR-04 — HIGH — native public tool-result bytes and gate public-view hash are different shapes

`controller-extension.ts:639-660` writes `formatResult(read_public_result, result)` into the native tool-result text. That is JSON for `PublicResult` alone. `phase_gate.py:473-475` hashes the full Bridge envelope `{"ok":true,"result":PublicResult}`.

The acceptance I/O addendum says to compare a “canonical envelope hash” only if wire equivalence is confirmed, but does not freeze the reconstruction. Directly hashing parsed tool-result text cannot equal `latest_gate.view_sha256.public`.

**Correction:** freeze the exact conversion: parse the first tool-result text as strict `PublicResult`, revalidate the tool name/call ID/error flag, construct exactly `{"ok":true,"result":parsed_public_result}`, serialize with the phase-gate canonical ASCII sorted compact encoder, and compare that hash. Any extra wrapper/details/native format drift must return `TOOL_TRANSCRIPT_INVALID`; no fallback.

## CBR-05 — HIGH — case evidence publication limits are not frozen

The contracts bound provider metadata to 4096 bytes, native/artifact output to 1 MiB, and timing to 20/180 seconds. They do not set exact caps for `case-admission.json`, the copied process receipt, `case-receipt.json`, evidence-directory file count, or aggregate evidence bytes. “Typed output” is not a bounded write contract.

**Correction:** freeze per-file and aggregate case-evidence caps before implementation, including modes and maximum file count. A compatible narrow choice is admission/gate/config/final receipt <=65,536 bytes, process receipt <=1,048,576 bytes, and an explicit small aggregate/count ceiling. Require descriptor-relative O_EXCL full-write/fsync/reopen. On cap or partial publication, retain evidence and return the existing safe failure stage with no fabricated FileBinding.

## Confirmed contract alignments

- Normal and synthetic process configs differ only in frontend path/identity; the normal config is never executed.
- The copied Faux entry imports the copied `controller-main.ts` through its fixed relative path. Its direct-entry guard uses `import.meta.url`, while `prepareControllerMain` verifies the normal controller-main asset path.
- Bridge and gate bootstraps use fixed `-B -m` entries, empty external argv, and fixed config hashes.
- The gate/current-session equality rule is deliberately strict: post-gate append or prefix-only evidence must fail, not be weakened silently.
- Faux supplies exactly two fixed response IDs, one public-read tool call, no third response/fallback, and native session usage remains authority. Installed Faux estimates usage at stream time rather than trusting metadata cost zeros.
- Acceptance remains pure and does not manufacture a gate outcome or hidden score.

## Fixed source evidence read

- `controller_deployment.py` — `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`
- `deployment_assets.py` — `2087db073f9c10f3cb7264fc1dda1df2e31a7cdfb6671af0fce537720b3faccc`
- `phase_driver.py` — `dc2bf22e7d1a33c52660200b8e25ab90c98cabce91f271befa781e0280cbec77`
- `phase_completion.py` — `4153bb2d4b92d8602211220913309fd73a995de3b0f83cd28107128896c73f98`
- `bridge.py` — `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558`
- `controller-main.ts` — `dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21`
- `controller-extension.ts` — `8e2ca3351e601b5d4733000dc9c704f0327fdc941851fadbc0d3f59357d2d3fe`
- `a2-frontend-probes/a2-combination-frontend.ts` — `cc03a228690ca176a9ee8970c203ac610b487f79a6a81e077f68c5aba0e73da4`

## Scope

Source/contract read only. No tests, unfinished-file acceptance, actual NativeHarness/Git/socket/Faux/Prime, `run_controller`, ORX, Docker, provider, auth, data, scoring, P0, nested worker, npm, or commit.
