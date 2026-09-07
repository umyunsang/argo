# HousePrice P0 runtime-boundary options

Status: **conditional go for the narrow P0 threat model; not yet certified or launch-admitted**  
Observed: `2026-09-07T07:06:44.135904+00:00`

## Answer

A concrete existing Prime configuration can remove direct host file, shell, REPL, MCP, and RLM actions from the **evaluated model** without changing Prime native code and without starting another daemon supervisor.

Use a fresh, headless, top-level Prime session. Load one hash-bound local extension. Combine `--no-builtin-tools` with an explicit six-name `--tools` allowlist. Disable ordinary resource discovery. Put generated code behind the fixed networkless Docker execution child. Keep hidden scoring outside the controller.

This is only a capability boundary for the evaluated model and an OS boundary for generated solution code. It is **not** a security sandbox for the Prime worker or the extension. Both remain trusted same-uid host code. If those components must also be unable to read host secrets, the current “no native edit/no new supervisor” scope is insufficient.

No raw dataset, labels, credential store, conversation, or private instance was inspected. No test, network call, model/train/eval run, ORX mutation, install, subagent, or commit was performed.

## Recommended shape

1. The trusted root keeps its existing REPL/RLM for orchestration only.
2. It launches the evaluated controller as a separate **top-level** `prime-agent --mode json` subprocess. It does not call `rlm()` for this controller.
3. Set `PRIME_AGENT_CODING_AGENT_DIR` to a new sterile task-local directory. The default daemon socket is under the OS temp directory, not the agent directory, so this still uses the existing supervisor.
4. Use a fresh session directory and a public-only cwd. Do not resume, continue, or fork.
5. Load one absolute local extension path after a trusted pre-launch byte/hash check.
6. Activate exactly:
   - `read_solution`
   - `write_solution`
   - `request_R1_run`
   - `read_public_result`
   - `read_dev_result`
   - `lock_final_artifact`
7. Execute generated solution code only through the fixed ORX R1 command and its fixed Docker child. ORX remains the only run-lifecycle authority.
8. Stop controller-visible writes at the protocol freeze/lock point. Run the trusted final scorer only after controller termination and final lock verification.

### Exact Prime argv surface

```text
/opt/homebrew/bin/prime-agent
--mode json
--offline
--cwd <public-controller-dir>
--session-dir <fresh-evidence-session-dir>
--model <exact-provider/model>
--thinking <frozen-level>
--no-builtin-tools
--tools read_solution,write_solution,request_R1_run,read_public_result,read_dev_result,lock_final_artifact
--no-extensions
--extension <absolute-hash-bound-task-extension.ts>
--no-skills
--no-prompt-templates
--no-themes
--no-context-files
--system-prompt <absolute-hash-bound-controller-system.md>
--append-system-prompt ""
--autonomous
--autonomous-gate <fixed-hash-bound-final-lock-verifier-command>
--autonomous-gate-retries <frozen-positive-integer>
--autonomous-gate-timeout-ms <frozen-positive-integer>
--autonomous-max-continuations <frozen-positive-integer>
--autonomous-max-turns <frozen-positive-integer>
--autonomous-max-tokens <frozen-positive-integer>
--autonomous-timeout-ms <frozen-positive-integer>
--
<fixed-task-prompt>
```

Trusted launch environment:

```text
PRIME_AGENT_CODING_AGENT_DIR=<sterile-task-agent-dir>
PRIME_AGENT_TELEMETRY=0
```

The numeric values are scientific protocol choices. They must be copied from the frozen protocol before launch. Prime’s defaults are not a preregistration.

Important details:

- `--tools` is the hard name allowlist. `--no-builtin-tools` alone is not enough.
- `--no-extensions -e <local-file>` means “no discovered extensions, but load this explicit extension.”
- `--no-context-files` suppresses `AGENTS.md`/`CLAUDE.md` only.
- The explicit `--system-prompt` prevents `SYSTEM.md` fallback.
- The explicit empty append argument prevents `APPEND_SYSTEM.md` fallback. The resource loader uses the explicit append array instead of discovery.
- A sterile `PRIME_AGENT_CODING_AGENT_DIR` prevents the operator’s settings, skills, prompt files, auth file, and global Continual Harness from becoming this session’s resource state. Use a scoped runtime provider credential. Do not copy the operator auth store.
- The extension should use `before_agent_start` only to replace the built prompt with the exact hash-bound controller prompt. Its safe fallback is the sterile base prompt. No other extension can run.
- Close stdin. Do not pipe a prompt. Put the fixed prompt after `--`; this prevents a leading `@` or `-` from being parsed as a file or option.
- Use JSON, not interactive or RPC mode. `!`, `!!`, editor `@file`, and slash commands are user/client input paths, not model tools, but headless closed-input operation removes them from the evaluated episode.
- Do not configure a model-authored autonomous gate. A gate is a host shell command outside the model tool allowlist. If autonomous continuation needs a completion gate, use one fixed hashed verifier over a lock path that `write_solution` cannot reach.

## What installed Prime actually supports

Installed `/opt/homebrew/lib/node_modules/prime-agent/package.json` declares `0.9.2`. The repo package declares `0.9.1`. The examined repo and installed `usage.md`, `extensions.md`, and `settings.md` files are byte-identical.

### Tools

The CLI parser accepts `--no-builtin-tools` and comma-separated `--tools`. The SDK maps explicit `tools` to both the initial active names and `allowedToolNames`. `AgentSession._refreshToolRegistry()` filters built-in, extension, and SDK tools against that set. Late ordinary tools cannot become active under another name. Do not use ACP mode; installed 0.9.2 has a separate ACP-MCP path.

Each custom tool uses a public `ToolDefinition` with a TypeBox schema and:

```text
execute(toolCallId, params, signal, onUpdate, ctx)
```

Core validates before execute, but it also performs conversion/coercion. `prepareArguments` runs before validation. An extension `tool_call` handler can mutate validated arguments with no revalidation. Therefore the task extension must:

- set `additionalProperties: false` explicitly;
- set string/array/byte/range bounds;
- revalidate inside every `execute`;
- register no generic argument-mutating `tool_call` handler;
- set `executionMode: "sequential"` on side-effecting run/lock tools; and
- atomically enforce run/lock state despite parallel model tool batches.

The extension API also exposes `pi.exec`, `modelRegistry`, dynamic tool/resource registration, session controls, and message injection. These are powers of trusted extension code. Tool descriptions do not constrain them.

### Resource leaks that the simple candidate misses

The naive flag set still has three gaps:

1. `--no-context-files` does not disable `SYSTEM.md` or `APPEND_SYSTEM.md` discovery.
2. Continual Harness state is appended even to a custom system prompt.
3. An explicit extension can return `skillPaths`, `promptPaths`, or `themePaths` from `resources_discover`; the later extension-resource path bypasses ordinary discovery suppression.

The recommended sterile agent directory, explicit system/append arguments, fixed prompt replacement, and audited extension closure close these paths for this P0 threat model. Prime does not hash-pin `-e`; the trusted root must record pre/post hash, size, mtime bound, and loaded absolute path.

### Budgets and cancellation

Prime exposes positive-integer limits for continuations, assistant turns, accumulated tokens, and elapsed autonomous time. Installed defaults are 3 continuations, 12 turns, 80,000 tokens, and 30 minutes. Gate defaults are 3 retries and 5 minutes.

These limits are checked between assistant responses. They stop another continuation. They do not interrupt the current provider call or tool. One response can overshoot a token/time threshold. The root therefore needs a separate hard wall-clock deadline, and every side-effecting tool needs its own timeout.

`pi.exec(command, args, ...)` uses `child_process.spawn(..., shell: false)`. This prevents shell interpolation when argv is fixed. Its abort/timeout path signals only the direct child, then sends `SIGKILL` after five seconds. It does not prove process-tree or Docker-container cleanup.

Headless JSON uses a client-owned daemon worker. Unexpected client loss starts a 30-second cleanup grace in installed source. A fixed runner must still own a deterministic container name/id, trap termination, remove the child, and leave an interruption receipt. Root cancellation must verify that no matching process/container survives.

## Task-local extension rules

The extension is part of the TCB. Keep it single-file or bind a closed import closure. It may import only the public Prime API, TypeBox, and reviewed Node built-ins. It must not use dynamic imports, `eval`, `shell:true`, npm/git sources, or model-controlled process fields.

- `read_solution`: regular bounded files under one source root only. Reject absolute paths, `..`, NUL, symlinks, hardlinks, devices/FIFOs, root escape after open, and oversize content.
- `write_solution`: atomic bounded regular-file writes under that root. No chmod/link/delete. Disable after freeze/lock.
- `request_R1_run`: empty strict schema, sequential execution, an atomic `O_EXCL` at-most-once admission fence, and exactly one fixed ORX argv. A crash between fence and observed ORX identity becomes `UNCERTAIN_NO_AUTOMATIC_RETRY`.
- `read_public_result`: fixed public metadata/result schema only.
- `read_dev_result`: the one permitted aggregate dev result/receipt only. Never return prediction vectors or arbitrary logs.
- `lock_final_artifact`: sequential and atomic. Recompute hashes from opened bytes. Bind solution closure, ORX run identity/receipt, environment/task digests, and prediction digest. Disable write/run after success.

The admission fence is not a run registry. It records only that the one side effect may have been attempted. ORX owns queued/running/completed/cancelled state. The task journal references the ORX run id and never mirrors that lifecycle.

## Docker/generated-code boundary

Required controls or equivalents:

```text
--network none
--read-only
--cap-drop ALL
--security-opt no-new-privileges
--user <non-root uid:gid>
--pids-limit <frozen>
--cpus <frozen>
--memory <frozen>
--memory-swap <same memory>
--ulimit <frozen>
--tmpfs /tmp:<bounded>
--rm
--name <deterministic-R1-name>
```

Bind exact prepared files. Never bind the protected cache directory or a parent directory. Mount solution source read-only. Mount dev/hidden features read-only. Never mount dev/hidden targets, Docker/daemon sockets, home, credentials, SSH/Git/cloud config, host `/tmp`, or a broad repo path. Put predictions in one dedicated output mount that controller read tools cannot browse.

The candidate’s literal “features only” mount set cannot fit a supervised model unless the fixed protocol separately provides the authorized training target. If needed, add only the training target as an explicit read-only mount. Never add dev or hidden targets.

Generated code can print any file it sees. Therefore networklessness alone is insufficient. Quarantine arbitrary stdout/stderr, exception strings, filenames, extra files, and predictions. Return only bounded schema-validated public diagnostics and the permitted aggregate dev metric. The final scorer separately receives the sealed target and hash-bound predictions after the controller is terminated. Do not return the hidden score to the controller.

Docker client/server `29.5.1/29.2.1` is inventory, not isolation certification.

## What is and is not bounded

Bounded, after the required tests:

- No model-callable host shell, REPL, edit, MCP, RLM, credential, or arbitrary filesystem/process API.
- Exactly six model-visible tool schemas.
- No ordinary extension/skill/prompt/context discovery.
- Generated code confined to the fixed container mounts, network, output, and resource channels.
- One ORX R1 admission and one final lock transition.

Not bounded by this design:

- The same-uid Prime worker or trusted extension can still read host environment/files.
- The existing supervisor merges its environment with the client launch environment. An absent client variable does not prove that every supervisor secret is absent from the worker.
- An unsafe implementation under an allowed tool name remains unsafe.
- Same-user concurrent mutation can defeat prehash/path assumptions outside the stated threat model.
- Prime autonomous counters are not hard compute, process, or spend enforcement.
- Docker version, tool descriptions, and JSON schemas are not OS proofs.

## Required failure-first synthetic gate

No safety claim is final until all tests pass with fake data and fake secrets:

1. **Tool census:** first show `ipython` or an injected tool under a weakened flag set; then capture exactly the six production schemas.
2. **Context sentinel:** seed synthetic sentinels in AGENTS, SYSTEM, APPEND_SYSTEM, settings, skill, prompt, harness, and an old session; first show a normal launch leaks one, then show the hardened provider payload leaks none.
3. **Extension resource bypass:** first show `resources_discover` defeats `--no-skills`; then prove the production extension has no such handler/resource content.
4. **Ingress:** first show `@file`, piped stdin, or resume imports a sentinel; then prove closed stdin, final `--`, and a fresh session do not.
5. **Escape prompts:** attempt `ipython`, `bash`, `edit`, MCP, RLM, `/reload`, `!`, `!!`, `@file`, unknown tools, and late tools. No canary may be read, executed, or changed.
6. **Late tool:** first show a late tool activates with only `--no-builtin-tools`; then show explicit `--tools` prevents activation in non-ACP JSON mode.
7. **Paths/schema:** first break naive prefix validation; then reject traversal, absolute/NUL/confusable paths, symlink swap, hardlink, FIFO/device, oversized inputs, and unknown fields.
8. **Command injection:** first break a shell-interpolated fake runner; then prove metacharacters/newlines remain data and fake ORX records one fixed argv.
9. **Exactly once:** race two same-batch calls, turns, restarts, and processes. Fake ORX must see one admission. Crash-window recovery must refuse automatic replay.
10. **Cancellation:** first show naive `pi.exec` leaves a descendant/container; then prove tool timeout, session abort, client loss, and outer deadline leave none.
11. **Container:** first expose a fake host secret/socket/network endpoint with a weak container; then prove all are absent/unreachable and all resource caps fire.
12. **Output exfiltration:** make generated code print/write synthetic feature/target sentinels. None may reach tool results, JSON transcript, or provider payload.
13. **Hidden seal:** first make a naive scorer accept a swapped target/prediction; then require hash/path/symlink/mtime checks and post-controller scoring only.
14. **Lock races:** race write/request/lock and duplicate lock. All post-lock mutation/admission must fail; the lock must bind opened bytes.
15. **Limits:** first show a current long tool survives an autonomous threshold; then prove tool timeout, Docker caps, outer deadline, and all four frozen Prime limits jointly stop it.
16. **Extension identity:** first mutate the extension between prehash and load; then require pre/post hashes, size, mtime bound, loaded absolute path, prompt hash, image digest, argv, and tool census to agree.

## Study interpretation

This boundary **does change the agent-visible action space**. HousePrice P0 must explicitly call it a bounded integration-feasibility test. It is not evidence about unmodified Prime/RLM performance and not a B/C/G causal comparison.

For later arms, keep the same installed Prime version, headless launch, sterile resources, six tools, Docker image/runner/mounts, scorer, budgets, final-lock rules, and all non-treatment prompt text. Vary only the preregistered treatment. Any boundary change creates a new protocol version.

Legacy RLM children cannot be the hidden-data boundary because they reuse the parent cwd, resource loader, tools, settings, and provider/session substrate. They remain valid for trusted root orchestration only.

## Minimal user decision if the stronger boundary is required

If the requirement is that the task extension and Prime worker themselves must be unable to read host secrets or hidden files, choose one:

1. accept the task-local extension and same-uid Prime worker as trusted P0 infrastructure; or
2. explicitly authorize a separately OS-sandboxed controller host/sterile supervisor with a scoped provider credential broker.

The current rights cannot provide option 2 through flags alone.

## Version and hash evidence

| Evidence | SHA-256 | Finding |
|---|---|---|
| `/opt/homebrew/lib/node_modules/prime-agent/package.json` | `46d8fba9e782d0a9fb3fb43ee35efacbebcfd5828544cbf3cad336be4c3b4841` | Installed version `0.9.2` |
| `/opt/homebrew/lib/node_modules/prime-agent/dist/bundle/cli.js` | `8e8786f67fa885c30715f563def89f4ee9a518d314cd26167bac1852b9a66507` | Resolved CLI entry bytes |
| `dist/cli/args.js.map` | `60c63a9301d7b3d92ec9162f0f00d59d0c0a466a02c19a159c87b873ba4f8aed` | Embedded `args.ts` SHA `906a66a4...94af18`; flags/parser |
| `dist/core/resource-loader.js.map` | `7dbeb808727314c01706ed6100b1333e218c12a223e283b031c81fa87dd12b51` | Embedded source SHA `b4ac632a...d8c852`; discovery gaps |
| `dist/core/sdk.js.map` | `5a33593647ff23bcee619a6801e4f4452e55bd473eaa284e25f531f40a3a256c` | Embedded source SHA `dba37d02...fc4d8`; tool allowlist mapping |
| `dist/core/agent-session.js.map` | `64e13f1ba0adf96c308d487da21769698e859d515d34074c65d6817dfc31cc90` | Embedded source SHA `d20e5b91...da219`; registry/harness/RLM behavior |
| `dist/core/system-prompt.js.map` | `fa55ea63ab908f9784be00440e4ba6a84ef6089909cb0601c55c8bb94185d9e2` | Embedded source SHA `35987b9e...7cfe`; prompt additions |
| `dist/core/extensions/types.d.ts` | `5a900c70c764a128620a329ca5e103a57a683f33a09b797736ea229ff8163ad9` | Public ExtensionAPI/tool/context schemas |
| `dist/core/exec.js.map` | `2923cb1d3da2b575d3e99a7036ee94ce3b5403ce8d89c9d9387ef9aefb9808f0` | Direct child spawn/cancel behavior |
| `dist/core/autonomous.js.map` | `ce9d3d5b7e1fa6e5860a7eaa4a91bc1384eb4a6a1393b117d903f6e1acf4199e` | Limits and gate order |
| Installed/repo `docs/usage.md` | `6d37373f25044ff8e0f8cc6e917832af95e9bf6e5f7401555929f4774bde5813` | Byte-identical examined docs |
| Installed/repo `docs/extensions.md` | `c11bbc8412ff151e3976a54bdea686804d85d6f8cf9b005efec96432a9b59508` | Byte-identical examined docs |
| Repo `packages/coding-agent/package.json` | `2e16750748f5122225811138592409ebff066f9e10bc29d8559bb9d2a6da72e2` | Repo package declares `0.9.1` |

Full machine-readable findings and the complete evidence list are in `runtime-boundary-options.json`.
