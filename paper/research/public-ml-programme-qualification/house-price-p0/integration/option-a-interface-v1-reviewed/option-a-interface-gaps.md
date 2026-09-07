# HousePrice Option A existing-interface audit

Status: **source audit complete; root bridge and real launch remain blocked**.

This audit did not read HousePrice payloads, credential files, or an ORX project store. It did not start an ORX server/project/run or call a provider. It made no native or apparatus-code change.

## Result

The minimal adapter protocol is **`HP_ORX_LOCAL_RECEIPT_BRIDGE_V1`**. It uses existing ORX 0.1.120 and Git interfaces. It is not a supervisor or a second run registry.

The six existing model tools are sufficient. `request_R1_run {}` must read the current `intent.json` and source closure, derive the immutable intent digest from opened bytes, and acquire a durable fence **per immutable intent**. Campaign budgets remain a separate trusted check. ORX alone owns lifecycle status.

Final refit has a separate pre-fit transition. It must resolve the controller-selected eligible development run/code receipt, restore the exact trusted archived `solution.py` bytes, and freeze that source before the ORX final-refit launch. The later `lock_final_artifact(run_id, artifact_sha256)` only attests the produced prediction artifact. Atomic restore/select remains an open root integration gap; it is not satisfied by prose or the trusted-I/O unit report.

The historical B0/L1/G2 menu in `integration/protocol-options.json` is not the current method contract. The controller can choose preprocessing, estimator, features, and hyperparameters through `solution.py`. The source baseline remains available. Aggregate dev MAE is an intentional bounded information channel, not proof of zero leakage.

## Exact ORX surfaces

Installed binary: `/Users/um-yunsang/.local/bin/orx`, version `0.1.120`, SHA-256 `03097743c44a2562e14d2d22dab783b9a57005d24b5f4b637acc426c92ee6756`.

### Fresh project setup

There is no `orx project create` command. The documented route is:

```text
orx up --port <frozen-port> --no-browser --no-agent --no-telemetry
```

Then the operator imports or creates a fresh project in the dashboard. The pinned UI client uses `POST /api/projects` with:

```text
{name,path,createFolder,requireNewFolder,initializeGit,githubSyncEnabled,locale,
 optional paperId, optional cloneUrl}
```

That REST route is UI-internal. Its server schema and response were not exercised. Do not put project creation inside a model tool call. Pre-create the project during trusted preflight. If root automates the REST route, bind the UI bundle hash and exact request and add a native fixture.

`orx projects --json --no-telemetry` is the only documented JSON surface relevant here. This audit did not run it because it reads the local ORX store.

### Fixed command, experiment, and immutable commit

```text
orx project edit <projectId> --run-command <fixed-repository-root-relative-command> --no-telemetry
orx create-experiment <projectId> --title <trusted-title> --description <trusted-description> --parent <parentExpId> --no-telemetry
orx exp status <expId> --no-telemetry
```

For the first empty-project baseline only, omit `--parent`. Omit `--run-command` on `create-experiment`; the node inherits the fixed project command.

The trusted adapter must create one committed closure per immutable intent on the assigned unfrozen experiment branch. It must compare the branch, command, and recorded commit from `exp status` before launch. The command must address the committed apparatus below `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime` from the extracted snapshot root. It must not execute a live-worktree source path.

ORX snapshots include committed Git bytes only. Ignored/private prepared CSVs are not in the archive. The snapshot-local entry must call the trusted runner, which opens only exact separately staged inputs from trusted deployment configuration and rechecks manifest hashes. A model intent cannot select host paths.

### Launch and reconciliation

```text
orx exp run <expId> --backend local --no-telemetry
orx runs <projectId> --experiment <expId> --no-telemetry
orx exp status <expId> --no-telemetry
```

Never pass `--force`. Local exposes no ORX timeout flag.

The bundled guide says launch queues a detached run and returns immediately. The task/root contract says a successful reply carries the queued run UUID, but the help/manual does not specify stable output grammar or JSON. Bind a UUID only after an exact parser succeeds, then cross-check `runs` and `status`. Missing or ambiguous launch output is `UNKNOWN/BLOCKED`; never infer acceptance from the subprocess or admission fence and never retry automatically.

`exp status` and `runs` are human text. They have no `--json`. A pinned, failure-closed parser and actual native faux-ORX fixtures are required.

### Raw status mapping

The pinned UI bundle uses raw `starting`, `running`, `done`, `failed`, and `cancelled`, plus `cancelRequested`. It computes `cancelling` only for display.

| Native raw | Bridge |
|---|---|
| `starting` | `QUEUED` |
| `running` | `RUNNING` |
| `done` | `DONE` |
| `failed` | `FAILED` |
| `cancelled` | `CANCELLED` |
| missing/unknown | `UNKNOWN` |

Preserve `cancelRequested` in the trusted raw receipt. It does not make cancellation terminal. The word “queues” in the launch guide is not proof of a native raw status string `queued`.

### Logs

```text
orx logs <runId> --head --bytes 1000000 --no-telemetry
orx logs <runId> --range <start>:<end> --no-telemetry
```

Log content is stdout. Byte-window and truncation metadata are stderr. Default content cap is 64 KiB; documented maximum is 1 MiB. Preserve bounded raw byte hashes in trusted evidence. Return only the strict runner summary to the controller. Arbitrary stdout, stderr, exception text, predictions, and rows remain quarantined. No general artifact enumeration CLI was observed.

### Cancel

```text
orx exp cancel <expId> --no-telemetry
```

Cancellation is experiment-scoped. There is no cancel-by-run-ID flag. Before cancel, `runs`/`status` must show exactly one in-flight run and its ID must equal the bound intent run. A missing, multiple, newer, or mismatched run blocks cancellation. A cancel request is not terminal evidence; re-read ORX state. Do not relaunch automatically.

## Exact supported OpenAI Codex provisioning route

A supported route exists without copying or reading the operator profile. The user must provision OAuth locally into:

```text
/Users/um-yunsang/.cache/argo-research/house-price-p0/prime-agent-profile-v1
```

Use a separate empty login working directory. Environment:

```text
PRIME_AGENT_CODING_AGENT_DIR=/Users/um-yunsang/.cache/argo-research/house-price-p0/prime-agent-profile-v1
PRIME_AGENT_TELEMETRY=0
```

Exact login argv:

```json
["/opt/homebrew/bin/prime-agent",
 "--cwd", "<SEPARATE_EMPTY_LOGIN_CWD>",
 "--no-session", "--no-tools", "--no-extensions", "--no-skills",
 "--no-prompt-templates", "--no-themes", "--no-context-files",
 "--append-system-prompt", ""]
```

The user enters `/login`, selects `ChatGPT Plus/Pro (Codex)`, completes browser OAuth, then enters `/quit`. Do not use `--offline` during OAuth. Do not pass a task prompt or run a test model call.

Installed source verifies that daemon runtime creation uses the client command's `agentDir`, then opens `<effectiveAgentDir>/auth.json`. An existing supervisor profile does not replace this task path. Source shows creation with mode `0600`; this audit did not create, stat, hash, or read any credential file.

The later headless controller freezes:

```text
--model openai-codex/gpt-5.6-sol --thinking xhigh
```

It uses the same task agent directory, a different evaluated cwd/session, the complete six-tool sterile flags, and no `--api-key`. The installed catalog contains that model. Account entitlement and real provider success remain untested.

There is no `openai-codex` environment-variable mapping. `--api-key` is a raw string runtime override with no OAuth refresh record and would expose the value in argv. It is not the secure subscription route. No provider shim is needed or authorized.

Prime's built-in Codex OAuth scope is `openid profile email offline_access`. This gives task-directory and tool-surface scoping, not provider-side per-task or spend scoping. If provider-side task/spend scope is required, no documented route exists.

## Blocking gaps

1. Fresh ORX project, IDs, and setup receipt do not exist.
2. No actual native 0.1.120 faux local fixture has captured launch run-ID grammar, status rows/transitions, log range metadata, or cancel behavior.
3. Root bridge fixed argv, parser, per-intent staging/commit, reconciliation, and cancel checks are not implemented.
4. Atomic restore/select of an earlier eligible dev source for final refit is still open.
5. Private input staging and manifest revalidation outside the Git snapshot are not frozen.
6. Exact repository-root run command, task self-time/resource enforcement, and environment digest are not frozen.
7. User-local Codex OAuth provisioning is pending.
8. Current-call/tool/OS/currency caps and immutable task-bound review remain pending.

## Validation and evidence limits

No tests were created or run in this audit-only lane. Five expected-failure CLI controls were run:

- `orx project create --help` → exit 2, no create subcommand.
- `orx exp status --json --help` → exit 2, no JSON flag.
- `orx runs --json --help` → exit 2, no JSON flag.
- `orx create-experiment --json --help` → exit 2, no JSON flag.
- `orx exp cancel --run <uuid> --help` → exit 2, no run-ID target.

`option-a-interface-gaps.json` records the exact full output and SHA-256 for every help/manual/control command. It also records source hashes and exact line or byte locators. These probes establish the interface surface only. They do not establish project creation, launch acceptance, lifecycle transitions, cancellation completion, credential validity, isolation, or scientific performance.
