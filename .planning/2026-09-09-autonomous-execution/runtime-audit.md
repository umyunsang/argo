# Runtime audit for the 2026-09-09 study

Status: native persistent REPL/RLM can be retained with a research-local container launcher and public SDK. The original `openai-codex/gpt-5.6-sol` binding does not support the specified per-call output cap. A direct OpenRouter binding is present and one explicitly authorized M1/high request succeeded with an accepted output cap. Cap exhaustion and M2 access remain untested. No scientific experiment was launched in this lane. One unintended model session, one authorized rejected Codex request, and one authorized successful OpenRouter request are recorded below.

## Authority and scope

Read current `AGENTS.md`, `docs/argo/agent-brief.md`, `docs/argo/migration-state.json`, study `README.md`, `design-v2.md`, and `protocol-v2.json`. Root's current user authorization permits actual study experiments and adaptive development. Native construction remains paused. Historical House Price source was inspected only as reference; its approvals, data, runner, and experiments were not reused. `docs/CODEX-NAVIGATION-GUIDE.md` is absent at the requested path. Repository HEAD observed: `ea45dacde9b151c023ea8d65189e4dc1871d79c0`; the existing dirty worktree was preserved.

`planning-with-files` was read and the root-owned active plan was read; this lane writes only these two runtime-audit files. Native large-file inspection was limited to the relevant SDK, kernel, RLM, provider, and autonomous-accounting sections; this is not a full native-runtime correctness audit.

## Installed execution surfaces

| Surface | Observed state |
|---|---|
| Prime executable | `/opt/homebrew/bin/prime-agent` -> `/opt/homebrew/lib/node_modules/prime-agent/dist/bundle/cli.js`; version 0.9.2 |
| Public installed SDK | `/opt/homebrew/lib/node_modules/prime-agent/dist/index.js` |
| Installed AI SDK | `/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js` |
| ORX | `/Users/um-yunsang/.local/bin/orx`; version 0.1.120 |
| Node / npm | 26.7.0 / 12.0.2 |
| Host Python | 3.14.5; no project `.venv` |
| Existing Prime kernel | `~/.prime/agent/kernel-venv/bin/python`; Python 3.11.15, prime-agent-runtime 0.1.0, dill 0.4.1, numpy 2.4.6, pandas 3.0.5, scikit-learn 1.9.0; openml absent in this environment |
| Docker | client 29.5.1, server 29.2.1; active context `colima-argo-sab-arm`; Linux arm64 daemon responded |
| Images | python:3.11-slim and old House Price/SAB images exist. Their suitability for this study or native REPL was not tested. |
| Provider credentials | Prime auth store contains openai-codex OAuth/access and openrouter api_key/nonempty literal. Values were never printed or saved by this audit. M1 OpenRouter access was subsequently confirmed by one scoped probe; remaining quota is not inferred from credential presence. |

The default Python runtime is named an IPython tool but does not require an `ipython` distribution: the native module is `rlm.repl`. Importlib metadata reported `ipython` absent; this alone is not a runtime blocker.

## Model and cap findings

| Binding | Catalog context / output | Client and actual evidence |
|---|---:|---|
| openai-codex/gpt-5.6-sol | 272000 / 128000 | high supported; native provider omits max_output_tokens, ignores timeoutMs/maxRetries in its SSE loop; live max_output_tokens=64 request returned HTTP400 unsupported parameter |
| openai-codex/gpt-5.5 | 272000 / 128000 | high supported; same client implementation; no request sent |
| opencodex/gpt-5.6-sol | 922000 / 32000 | configured local OpenAI-completions frontend; its ChatGPT forward route removes output-cap fields; not a qualified cap workaround |
| opencodex/gpt-5.5 | 272000 / 32000 | configured local frontend; no request sent |
| openrouter/openai/gpt-5.6-sol | 1050000 / 128000 | high supported; direct openai-completions provider accepts cap64; one HTTP200 OK response with 26 tokens via Azure; cap exhaustion not stress-tested |
| openrouter/openai/gpt-5.5 | 1050000 / 128000 | same client capability; no request sent |

Catalog maxima are not imposed host caps. Native `--autonomous-max-tokens` is checked after assistant responses and counts `input + output + cacheWrite`, explicitly excluding cacheRead. The study counts cacheRead. It is therefore unsuitable as the sole normalized-token enforcement mechanism. Native Codex SSE retries are hard-coded to 3 regardless of requested maxRetries=0. A signal supplied by the caller can abort the request, but a settings timeout alone is not enforced in that provider.

One exactly bounded capability probe used the installed Codex provider, existing access credential in memory, high reasoning, `Reply only OK.`, SSE, a 60-second abort, and onPayload adding max_output_tokens=64. A process-local fetch gate allowed exactly one HTTP request and blocked the provider's three attempted retries before sending. Result after 7.388 seconds: HTTP400, unsupported max_output_tokens. Returned SDK usage zeros are defaults from an error object, not provider-confirmed zero consumption. No successful OK or resolved model revision was observed. Do not retry this rejected route as though a cap now exists.

The direct OpenRouter route is the narrow candidate for a prospective provider-binding amendment. Exact API shape for a root-authorized probe is:

```ts
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import { streamOpenAICompletions } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/providers/openai-completions.js";

const model = getModel("openrouter", "openai/gpt-5.6-sol");
const result = await streamOpenAICompletions(model, context, {
  apiKey: existingCredentialInMemory,
  reasoningEffort: "high",
  maxTokens: 8000,
  maxRetries: 0,
  timeoutMs: 60000,
  signal: episodeAbortSignal,
  onPayload: body => ({
    ...body,
    provider: {
      only: ["azure"],
      order: ["azure"],
      ignore: ["azure/us", "azure/eu"],
      allow_fallbacks: false,
      require_parameters: true,
    },
  }),
}).result();
```

This is the qualified client interface. The executed minimal probe used maxTokens64 and added provider={allow_fallbacks:false,require_parameters:true} through onPayload, with one actual HTTP request. It returned OK from exact model openai/gpt-5.6-sol, provider Azure, input21/output5/total26, reasoning0, billed cost0.000255 USD credits, in 2.934 seconds. The 64-token parameter was accepted; this short response did not exercise exhaustion. M2, exact underlying backend revision and remaining balance were not tested. Freeze the endpoint before scientific execution. Reasoning is included in completion_tokens by the installed provider's usage normalization; do not add it again.

## Preserve native REPL and RLM

`PRIME_AGENT_KERNEL_PYTHON` is resolved as an executable path and invoked first with `-c` runtime/import checks, then with `-m rlm.repl`. It may therefore point to an executable launcher that starts the same native Python runtime inside Docker. The override path need not be a literal Python binary. No source modification is needed for this mechanism.

The launcher must preserve stdin/stdout byte streams and emit no stdout banners. A research-local launcher may use Docker `run -i --rm`, an image ID/digest, `--network none`, a read-only root, no added capabilities, no-new-privileges, explicit CPU/memory/PID limits, a bounded writable tmpfs, and selected bind mounts. Bake the current prime-agent-runtime and required packages into the image. Override readiness checks require protocol 3 plus native harness CRUD, rlm.run/host_request, and imports requests, httpx, yaml, tomli, dotenv, pandas, numpy, scipy, bs4, lxml, pydantic and tyro; snapshots need dill.

Required path handling:

- Mount the episode's public worker workspace and session-artifact tree at the same absolute paths used by the host; set container workdir to the episode cwd. Kernel snapshots and local harness files use host-provided absolute paths.
- Forward only required `RLM_DEPTH`, `RLM_MAX_DEPTH`, `RLM_SESSION_DIR`, and `RLM_HARNESS_STATE_DIR`; define any global harness path inside this episode's state. Do not mount the auth/profile root, scorer custody, test data, unrelated session artifacts, or Docker socket. Do not forward the whole host environment.
- The native stdio host_request bridge remains available with network none, so native RLM delegation and explicitly registered host tools work without a second REPL or agent loop.
- The wrapper must work for bootstrap `-c` probes as well as the persistent `-m rlm.repl` process. A new container per bootstrap check is expected; one persistent container owns each actual session kernel.
- Qualify interrupt, cancellation, shutdown, killed-parent, and restore paths. Prime sees the Docker CLI process while the Linux container processes reside in the VM; `--rm` alone does not prove container cancellation. A wrapper must forward termination and ensure its own identified container is closed. Never kill unrelated containers or native ORX supervisors.

Native inline RLM children copy parent `streamFn`, `onPayload`, `onResponse`, context transformation, settings, resource loader, active/allowed tool names and custom tools. They get their own SessionManager and kernel; depth increments. A shared, public `session.agent.streamFn` guard can reject the wrong provider/model/reasoning and account/reserve requests across root and children before sending, while retaining native execution. The child registry and child_usage_attributed transcript records remain native authority. Do not add child aggregate tokens to own child records a second time.

`rlm.run` admits only name/model/thinking options and returns a handle, not the child answer. Child results arrive through native agent messages or files. Native `rlmMaxDepth` is a depth gate, not the study's global concurrency gate. Model selection must be enforced at the request boundary; a prompt asking children to keep M1/high is insufficient. Root has not qualified daemon-backed propagation of research-local closures; the inheritance above is directly inspected for the inline SDK path. An SDK execution does not claim the full daemon recovery path was exercised.

The minimal SDK setup should use `createAgentSession`, a sterile explicit ResourceLoader, SettingsManager.inMemory, SessionManager.create in an episode-only directory, tools including `ipython` and bounded scientific/custom tools, no ambient context/skills/prompts, and an explicit model. Do not reuse the House Price six-tool frontend: it intentionally omitted REPL/RLM. Keep all B/R access and common starting records symmetric. The scorer remains outside all model-accessible mounts.

## ORX ownership and scientific receipts

Observed ORX projects are old thesis/House Price/private-instance projects; no project for this new study was present in the inspected list. Do not attach these experiments to an old run approval. Native CLI project creation is through `orx up` import/create dashboard; `orx create-experiment` requires an existing project ID. Loopback API project-import details were not inspected in this lane.

After root creates an isolated study runner repository/project and freezes the common command, the supported lifecycle is:

```sh
orx --no-telemetry project edit STUDY_PROJECT_ID --run-command 'python runner.py'
orx --no-telemetry create-experiment STUDY_PROJECT_ID --title 'Episode baseline'
# Commit the exact node code/config on the printed branch before launch.
orx --no-telemetry exp run EXPERIMENT_ID --backend local
orx --no-telemetry exp status EXPERIMENT_ID
orx --no-telemetry runs STUDY_PROJECT_ID --experiment EXPERIMENT_ID
orx --no-telemetry logs RUN_ID --head --bytes 200000
orx --no-telemetry exp wait EXPERIMENT_ID --interval 5 --timeout 50
orx --no-telemetry exp cancel EXPERIMENT_ID
```

Commands above are interface recipes and were not launched. The fixed command must be identical across nodes, with differences in committed code/config. Use child nodes for answered hypotheses; preserve answered node history. ORX local extracts an immutable committed snapshot under its local-runs/runID directory and owns the detached supervisor. Its local backend has no timeout/image/flavor resource flags. The fixed research runner must enforce scientific container limits and cumulative reservations, while ORX remains the lifecycle authority. Docker --cpus limits simultaneous capacity, not cumulative CPU-core-minutes. Aggregate kernel/fit concurrency and memory must honor the episode cap; per-container caps alone can exceed it.

Every accepted scientific result needs the original ORX project/experiment/run IDs, branch commit, fixed-command and image hashes, candidate/config/data/split/scorer identities, start/end and terminal status, dev feedback slot, lock/refit identity, CPU/wall/resource receipt, and a final compact result printed to stdout then read back via `orx logs`. A successful run status alone is not metric evidence. A trusted custody failure or missing receipt stays UNKNOWN; no blind re-launch. The current study scorer/feedback/refit enforcement was outside this lane and is not certified here.

## Audit incident and costs

An intended catalog command was wrongly formed as `prime-agent --offline model list gpt-5.6-sol`. Leading run options prevented command dispatch and the words became three prompts, `model`, `list`, `gpt-5.6-sol`, in a new native default-model session. The command unexpectedly invoked opencodex/gpt-6-astra. The second M2 shell command never ran.

Root was told immediately after detection. Only the audit-owned command shell, client PID 23454, new worker 23496 and its kernel 23678 were terminated; subsequent process inspection found all absent. Native `prime-agent stop` could not resolve the transient worker by its transcript session ID, so termination used the positively identified new process PIDs. The pre-existing daemon and other sessions were preserved.

Final transcript: `/Users/um-yunsang/.prime/agent/sessions/01a08360-5ec6-7179-9fe6-c1b95574091e.jsonl`, SHA256 `33353a6807fab931a843e0fd1e10918e05b8c5a78ce34e302fef3aa957ab5096`. It contains 13 assistant messages including aborted endings. Recorded input 233522, output 2685, cacheRead 310400, cacheWrite 0: **546607 normalized tokens**. Catalog cost zero does not establish zero real monetary cost. Inspected tool calls were native harness, model-catalog, and documentation reads; no ML fit, ORX run, repository edit, or credential mutation was shown. Kernel/session artifacts are an unintended side effect. This is a setup-protocol incident, not a scientific assignment or approved M1 episode. Root explicitly directed this consumption into the shared development/setup ledger without expanding caps.

## Concrete remaining work

1. Root: prospectively bind the verified direct OpenRouter M1 path, pin endpoint and request/price semantics, and qualify remaining cap behavior. Native Codex cap is contradicted by the actual probe; M2 access remains untested.
2. Materialize and qualify the research-local native-kernel container launcher, including path mapping, snapshot continuity, host-request controls, child request inheritance and process cleanup.
3. Implement shared pre-request normalized-token reservation (including cached input), exact active-input accounting, and complete-call reconciliation. Failed/aborted requests with missing usage remain unknown; never treat SDK default zeros as free work.
4. Pin independent scientific container/scorer custody, cumulative CPU/wall limits, feedback12 and one final refit; register the new study with ORX and use native run receipts.

No broad native rewrite, further generic review, House Price rerun, new credential, or extra scientific trial is needed to resolve the identified interface questions.

## Successful direct OpenRouter probe and endpoint prices

Before sending, the [official model metadata](https://openrouter.ai/api/v1/models) returned exact ID openai/gpt-5.6-sol and canonical slug openai/gpt-5.6-sol-20260709 with max_completion_tokens, max_tokens and reasoning support. The [official endpoint metadata](https://openrouter.ai/api/v1/models/openai/gpt-5.6-sol/endpoints) subsequently identifies Azure tag azure at $5 input / $30 output / $0.50 cached-input per million tokens below the long-context threshold, matching the actual billed receipt. Azure regional tags azure/us and azure/eu have different prices. The aggregate catalog cheapest price ($2/$10) and SDK estimate ($0.000092) did not describe this request; use provider-reported cost $0.000255. OpenRouter documents explicit max_tokens and detailed response usage in its [API reference](https://openrouter.ai/docs/api_reference/overview).

Response ID gen-1788911029-e1V6abCmhNxNyM2RknyJ; safe request SHA256 487a43eed1cee575707b0325858230be929dff00bb4b3bfde80e62ee08855dd9. No model fallback or provider fallback was allowed. No credential or response header values were logged. The successful setup probe adds 26 known normalized tokens: known setup total is **546633**, plus the rejected Codex request with unconfirmed usage. This does not increase any scientific or development cap. Full safe metadata and receipts are in runtime-audit.json.

Root accepted the prospective direct OpenRouter/Azure binding after the probe. The SDK recipe now includes the exact onPayload provider object. OpenRouter [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) treats a base slug such as azure as matching all its regional endpoints; the recipe excludes the two regional endpoints in the retrieved metadata. Freeze that endpoint roster and stop on unexpected routing or price drift; only=[azure] alone does not promise one specific regional endpoint. The live probe used allow_fallbacks=false and require_parameters=true but did not yet apply only/order/ignore. No later live probe was performed. ORX loopback project-registration API shape remains NOT_INSPECTED; the known supported import surface is orx up dashboard.
