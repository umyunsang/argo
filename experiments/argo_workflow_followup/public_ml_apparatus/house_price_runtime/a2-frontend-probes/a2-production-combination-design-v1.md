# A2 frontend/process/usage/gate/Bridge synthetic combination design v1

Status: **source-only design; no run and no production admission**.

## Purpose

Run one bounded synthetic composition check across:

1. the production `controller_process.run_controller` resource path;
2. a clearly test-only frontend that calls the held `prepareControllerMain` and installed public Prime `main`;
3. the unchanged six-tool controller extension;
4. a real `bridge.load_bridge_from_config` using the independently reviewed `test_bridge.NativeHarness` / `FixedNativePort`, local fake ORX executable, local Git repository, and loopback status server;
5. `UsageObserver` as the process campaign callback; and
6. the real `phase_gate` module through a fixed bootstrap.

The check must finish in less than 15 minutes of operator time. The controller process gets a separate `abort_event` at 20 seconds. It uses the full production environment and cap values; the 20-second abort and a 1 MiB observed-output assertion are supplemental test bounds, not replacements for production caps.

## What public Prime can and cannot test

`controller-main.ts` statically imports public `main` at line 18. It exports `prepareControllerMain`, but its `executeControllerMain` is private and always calls:

```ts
primeMain(prepared.mainArgs, { extensionFactories: prepared.fixedFactories })
```

The fixed list contains only the no-op factory used to force in-process execution. There is no production injection seam for a Faux provider. Therefore a no-auth synthetic test cannot honestly execute the exact production entry and exact one-factory list.

The smallest honest alternative is a separate test-only frontend. It statically imports `prepareControllerMain` and the installed public `main`. It calls the real preparation and postflight functions, but adds one test-only provider factory. That factory registers the public Faux API under the exact identity `openai-codex/gpt-5.6-sol`. It is not shipped or referenced by production deployment.

This proves the composed process, argument, tool, session, gate, and Bridge behavior described below. It does **not** prove builtin Codex OAuth, headers, refresh, paid network transport, latency, genuine response IDs, the private production error wrapper, or the production one-factory list.

### Deployment-producer constraint

The new `controller_deployment.py` producer is a useful real dependency (`c57a7685...71b044`, six synthetic tests green but not independently reviewed). Use `write_extension_binding` and `write_frontend_deployment` directly. Its `write_process_config` always derives `frontend_path` from deployment `assets.controller_main`; `prepareControllerMain` requires that asset to be the actual `controller-main.ts`. It therefore cannot produce the separate Faux frontend process.

The driver must create two process configs:

1. a normal producer output from `write_process_config`, bound to actual `controller-main.ts`, validated but **not executed**; and
2. a separately constructed test-only `RunControllerConfig`, bound to `a2_combination_frontend.ts`, with `synthetic_test_context=false`, exact production eight-key environment, and full production caps.

The second choice exercises the production validation branch without lowering caps. However, `ControllerRunReceipt` has no synthetic marker. The root's external combination receipt must bind the different frontend identity and label the run synthetic. It must never be presented as the normal producer/production frontend combination.

## Proposed future files

These files are future test inputs. This design does not create them.

| File | Owner | Exact role |
|---|---|---|
| `a2_combination_frontend.ts` | frontend validation | Static-import `prepareControllerMain` and public `main`; install the test-only Faux provider; emit two unique nonempty synthetic response IDs; call `read_public_result` once; run postflight and exit. |
| `combination_driver.py` | root | Build/seal all inputs, seed two dev results, construct observer/process config, run once, validate and archive allowlisted evidence. |
| `bridge_bootstrap.py` | root generated | No-argument 0700 bootstrap into the sealed namespace; `execve` the real Bridge module with one fixed config/hash. |
| `phase_gate_bootstrap.py` | root generated | No-argument 0700 bootstrap into the sealed namespace; `execve` the real phase-gate module with one fixed config/hash. |

The root input is one strict `argo-house-price-a2-combination-input/v1` record. It binds the namespace tree, both bootstraps/configs, test frontend, controller/extension/binding, frontend deployment, process config, and all directory identities. Fixed expectations are: initial context, 292 rows, `read_public_result`, response IDs `a2-combination-response-0001` and `a2-combination-response-0002`, final outcome `READY_INITIAL_CHECKPOINT`, campaign budget 120000, and abort at 20 seconds.

## Regular-file namespace

Follow `option-a2-regular-namespace-deployment-v1.json` (`b4c62f...73feed`). Create a canonical 0700 namespace outside the repository, controller cwd, profile, session, and artifact tree. It contains:

- empty regular `__init__.py` files for `experiments`, `argo_workflow_followup`, `public_ml_apparatus`, and `house_price_runtime`;
- reviewed copies of `bridge.py`, `phase_gate.py`, `usage_observer.py`, `campaign_usage.py`, `grading.py`, `intent.py`, `orx_text.py`, `receipt_store.py`, `run_entry.py`, `staging.py`, `trusted_io.py`, `container_runner.py`, `container_entry.py`, `source_closure.py`, `controller_process.py`, `process_exec.py`, `controller_deployment.py`, `deployment_assets.py`, `test_bridge.py`, and `house_price_scorer.py`; and
- the root-owned combination driver.

After every destination file closes, independently compare its opened bytes to the source binding. Then call `capture_tree` with at most 128 members, 1 MiB per member, 8 MiB aggregate, and relative paths at most 4096 bytes. Store the SourceTree outside the namespace. Call `verify_tree` before any native module import and after the run.

Do not place auth, native session logs, raw data, predictions, or controller output in this namespace.

## Bridge fixture and two dev results

The driver imports `NativeHarness` from the copied, reviewed `test_bridge.py` and constructs it with `rows=292`. It writes `NativeHarness.deployment()` as canonical bytes, hashes it, and calls the real `load_bridge_from_config`. This selects `FixedNativePort`; no fake `Bridge` class is substituted.

Seed exactly two development results before the controller starts:

1. Call `Bridge.handle(request_R1_run)` using the fixture's initial solution and intent.
2. Read the new binding, observe `RUNNING` through the real port/loopback reader, call `NativeHarness.mark_done`, and read the dev result.
3. Write a second synthetic `solution.py` and matching dev `intent.json` through `Bridge.handle`. The intent names the first run as `parent_run_id`.
4. Request the second run, observe it, mark it done, and read the dev results again.
5. Require two distinct valid results with 292 rows and the expected receipt/source identities. Require nonempty `research.md`. Do not request a third dev run or final refit.

This executes the reviewed local fake ORX executable, local Git staging, source archive checks, loopback getter, runner-receipt verification, and dev regrade. It does not execute the real `orx`, Docker, training, protected data, or hidden scoring.

During the controller run, the model makes one read-only `read_public_result` call through the extension and fixed Bridge bootstrap. Compare the Bridge state namespace before and after that call: no attempt, binding, receipt, context, or final-lock file may appear.

## Test-only frontend

The test frontend is hash-bound by `RunControllerConfig.frontend_identity`. The normal frontend deployment still binds the held `controller-main.ts`, extension, binding, settings, prompts, gate bootstrap, interpreter, and manifests.

The test provider uses the public Faux implementation. It registers the exact provider/model name but no authored stream implementation. Queue only:

1. an assistant `read_public_result({})` tool call with response ID `a2-combination-response-0001`; and
2. bounded terminal text with response ID `a2-combination-response-0002`.

Capture the provider context in the Faux response factories. It must show exactly the six unchanged schemas. Run public `main` with `prepared.mainArgs` and `[...prepared.fixedFactories, testFauxFactory]`. Call `prepared.verifyPostflight()` and exit only after `main` returns.

The profile contains sealed settings and no real auth. Native creation of an empty test-profile `auth.json` is metadata-only evidence. Never open, copy, hash, or archive it.

## UsageObserver and process boundary

Build `UsageObserverConfig` with the fresh session directory identity, controller cwd, `openai-codex`, `gpt-5.6-sol`, budget 120000, and no prior session. Reuse one observer instance for the whole process call.

The `campaign_guard` callback returns:

- `None` for `WAITING_FIRST_USAGE` and `WITHIN_BUDGET`;
- `CAMPAIGN_TOKEN_TRIGGER` or `CAMPAIGN_USAGE_UNKNOWN` only when reported by the observer.

Any exception or other return becomes `CAMPAIGN_USAGE_UNKNOWN` through `run_controller`. An empty directory or a header without completed assistant usage is waiting, not zero usage and not a failure.

Create `RunControllerConfig` with `synthetic_test_context=false`, the root v2 exact eight-key environment, `DEVNULL` stdin, and the full `FROZEN_PRODUCTION_CAPS`. Non-frozen cleanup and observer fields must come from the reviewed deployment producer; do not invent smaller values. Arm a separate `threading.Event` for 20 seconds and pass both `abort_event` and `campaign_guard` to `run_controller`. Cancel the timer when the call returns. Never retry an uncertain or non-success result.

The 20-second timer is supplemental. It does not rewrite `phase_wall_seconds=3600`, `campaign_wall_seconds=10800`, `file_size_bytes=8388608`, RSS trigger, or other production caps.

## Real phase gate

Write an initial-context `argo-house-price-a2-phase-gate-deployment/v1` with:

- the exact Bridge config FileBinding;
- the fresh session directory identity and private non-Git controller cwd;
- provider/model `openai-codex/gpt-5.6-sol`;
- budget 120000;
- `prior_session`, `prior_session_id`, and `prior_cwd` all null;
- the canonical Bridge final-lock path;
- an empty root-private 0700 gate-outcome directory; and
- `expected_rows=292`.

The fixed gate bootstrap invokes `phase_gate` with that config and hash. `NOT_READY` returns 1 and allows another native continuation. READY and STOP return 0. Process exit 0 or gate stdout is never enough: the driver must independently open the latest contiguous outcome and require `READY_INITIAL_CHECKPOINT`.

The phase gate owns a separate `UsageObserver` restored from its outcome checkpoint chain. At final validation, its category counts, session ID, file identity, prefix hash, and total must agree with the process callback's observation.

## Bootstrap cwd and environment assessment

Each bootstrap imports only `os` and `sys`, rejects any argument, and uses fixed literals only. Prefer:

1. `os.open(namespace, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)`;
2. `fstat` against embedded canonical path/device/inode/mode0700;
3. `os.fchdir` on that held descriptor; and
4. `os.execve` of the approved interpreter invocation path with `-B -m`, the fixed module, and fixed config/hash.

A plain `chdir(path)` adds a second pathname resolution window. `fchdir` narrows it, though it is not fexecve/pidfd or hostile-host proof.

The exec environment is exactly `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, `PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin`, and `TZ=UTC`. It has no HOME, profile, provider, credential, TMPDIR, PI, or internal variables. PATH is not execution authority; executable and config paths are bound and absolute.

The module cwd is the source namespace, not the controller cwd. Current `phase_gate`, `bridge`, `usage_observer`, and `campaign_usage` contain no `Path.cwd` or `os.getcwd` dependency. The controller cwd remains a separate absolute config identity and must be outside Git, preventing Prime's unchanged-Git gate skip.

On bootstrap failure, emit only a fixed safe payload. Bridge failure uses `{"error":"INTERNAL_ERROR","ok":false}`. Gate failure uses `STOP_PROTOCOL_INVALID` and exit 0 so Prime stops. The parent still requires a durable typed gate outcome, so this fail-safe exit cannot become readiness.

Residual risks:

- Python site initialization occurs before bootstrap top-level and again on `-B -m`. `-B` is not isolated mode. The existing interpreter, venv, site packages, stdlib, shared libraries, and OS remain external TCB.
- The root seal is checked under the accepted no-concurrent-same-UID-mutator assumption. It is not hostile-host proof.
- FixedNativePort's separately sealed synthetic environment may contain fixture HOME for fake ORX subprocesses. It is not the bootstrap/controller environment and carries no real credential.

## Order and 15-minute budget

1. **0-3 min:** copy and seal namespace; write and seal bootstraps.
2. **3-6 min:** instantiate `NativeHarness(rows=292)`, load the real Bridge, and seed two verified dev results.
3. **6-8 min:** write/hash gate config and gate bootstrap.
4. **6-9 min:** use the real producers for extension binding and frontend deployment. Generate/revalidate the normal actual-controller process config without executing it. Separately bind the test frontend in a synthetic-labeled full-cap process config.
5. **9-11 min:** store both process configs outside artifact root; construct observer and 20-second abort; execute only the test-frontend config once.
6. **11-14 min:** reopen process receipt, session, gate outcomes, Bridge views, and all closure records.
7. **14-15 min:** archive only allowlisted synthetic evidence and write one immutable receipt. Stop.

## Pass predicates

All must hold:

- the test-only process config takes the production validation branch with exact v2 environment/full production caps and the external receipt labels its different frontend identity synthetic; the normal producer config binds actual controller-main and remains unexecuted;
- supplemental abort did not fire and elapsed time is below 20 seconds;
- receipt is `status=succeeded`, `terminal_reason=completed`, `returncode=0`, with cleanup confirmed for every tracked process and no resource/campaign trigger;
- observed stdout, stderr, and total controller artifacts are each/collectively below 1 MiB for this fixture, without changing process caps;
- no daemon socket/service appears;
- provider and active tool lists are exactly the six schemas;
- the one native session has exact ID/cwd/provider/model and the two unique nonempty response IDs with all four usage categories;
- process `UsageObserver` is complete, within budget, and below 120000;
- the latest contiguous durable gate outcome is `READY_INITIAL_CHECKPOINT`, names exactly the two seeded dev run IDs, carries the same complete usage, and hashes the saved research;
- Bridge reports two valid rows292 dev results and one remaining opportunity; the model's read caused no state mutation or run;
- namespace, bootstraps, configs, frontend assets, process identities, and every declared member byte reverify unchanged; and
- no auth content, raw data, predictions, arbitrary logs, fake-ORX internals, or target values reach model context, stdout, session, or the evidence archive.

Any abort, non-success receipt, cleanup uncertainty, usage unknown/exhausted, missing response ID, non-ready/missing gate outcome, source drift, new Bridge launch/state mutation, or size/time trigger ends the check without retry.

## Confounds and nonclaims

- The test-only Faux override is not builtin Codex auth/transport evidence.
- The process executes the test frontend, not the exact private production entry wrapper. The real producer cannot create that process config; the driver constructs it directly, and the native receipt itself has no synthetic marker.
- `NativeHarness.mark_done` synthesizes local predictions/receipts; no real ORX, Docker, training, or hidden score is tested.
- Usage remains completed-response accounting. There is no hard current-call token cap or backpressure.
- Full production cap validation does not make RSS a kernel-hard limit. The 20-second/1 MiB fixture assertions are supplemental only.
- SourceTree covers copied source, not the external interpreter/site/shared-library/OS TCB.
- A passing combination is integration feasibility evidence only. It does not admit P0 or prove unchanged Prime/RLM or research efficacy.
