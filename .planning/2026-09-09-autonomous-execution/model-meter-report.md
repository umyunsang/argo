# Native stream meter handoff

Implemented research-local `experiments/argo_study_20260909/model_meter.ts` and `test_model_meter.ts`. Native source and installed packages are unchanged. There were no real model requests in this implementation task.

Validation: 14 focused tests using fake HTTP responses through the installed native OpenAI-completions stream parser passed. Independent strict TypeScript checking passed. Repository Biome excludes these experiment files and processed zero files; do not describe that as a style check. Root owns the required full `npm run check`.

## Exact integration

```ts
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import { createMeteredStream, initializeFamilyLedger } from "./model_meter.ts";

// Once per B/R family. flag=wx refuses to replace an existing family ledger.
initializeFamilyLedger({
  familyLedgerPath,
  familyLimit: 1_500_000,
  usdCeiling: 45,
  setup: {
    knownTokens: 273316.5,
    unknownTokenReserve: 96000,
    roundingTokenReserve: 0.5,
    knownUsd: 0.0001275,
    unknownUsdReserve: 11.0793825,
    note: "Half of shared setup; token/USD reserves are not actual invoiced spend.",
  },
});

const meter = createMeteredStream({
  model: getModel("openrouter", "openai/gpt-5.6-sol"),
  ledgerPath: episodeLedgerPath,
  episodeLimit: 80000, // development/selection; primary may use120000
  familyLedgerPath,
  familyLimit: 1_500_000,
  usdCeiling: 45,
  timeoutMs: 60000,
  providerTag: "azure",
});

meter.reconcile(); // Before prompting after a process restart.
session.agent.streamFn = meter.streamFn;
// session already has explicit model and thinkingLevel="high".
await session.prompt(taskPrompt);
const receipt = meter.reconcile();
```

`getApiKey` may optionally supply the trusted host's existing key callback. Otherwise the factory reads only the existing literal OpenRouter credential from `~/.prime/agent/auth.json`; it does not refresh or write credentials. No key value goes into either ledger. The optional `fetch` member is solely a fake transport seam for tests; production omits it.

The exact installed native provider import is `/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/providers/openai-completions.js`. The meter retains its parsing and native event stream. A single AsyncLocalStorage-aware fetch interceptor observes only calls started by a meter; unrelated calls pass through unchanged. Native inline RLM children inherit the same streamFn and therefore share reservations and accounting. A replaced global fetch is refused instead of silently losing measurement.

## Enforced request boundary

The M1 binding is exact `openrouter/openai/gpt-5.6-sol`, native API `openai-completions`, official HTTPS base URL, reasoning `high`, output `max_completion_tokens=8000`, SDK retries zero and timeout60000ms plus an independent AbortSignal. The request also carries:

```json
{
  "provider": {
    "only": ["azure"],
    "order": ["azure"],
    "ignore": ["azure/us", "azure/eu"],
    "allow_fallbacks": false,
    "require_parameters": true,
    "max_price": {"prompt": 5, "completion": 30}
  }
}
```

Azure's base slug matches its variants. The observed regional variants are excluded and max_price rejects higher prompt/output prices; freeze and recheck the endpoint metadata separately. Returned model and provider must still match M1/Azure. This factory intentionally does not admit M2 or a different endpoint without a prospective implementation/configuration change.

Payload hooks run before final route/cap/high enforcement. Alternate model lists, route fallback, plugins, multi-completion requests, and nondefault service tier are rejected. Conflicting legacy max_tokens/reasoning_effort fields are removed. HTTP redirects and second HTTP sends for the same request ID are refused. Successful `onResponse` observability is forwarded to the native caller.

## Reservation, settlement and failure

The shared family JSON is authority. A synchronous exclusive lock serializes reservations across all same-process inline root/child instances; each admitted request is written atomically before its fetch. Episode JSON is a derived view. The request reserves input upper bound plus8000 output tokens and $30 per million reserved tokens, which is a budget charge rather than invoiced cost. Admission checks the selected80000 or120000 episode token limit and the family token/USD ceilings including setup and concurrent reservations.

Provider `prompt_tokens` already includes cache reads/writes. Normalization is `input=prompt-cached-cache_write`, `output=completion`, `total=prompt+completion`; reasoning is a component of completion and is not added again. Inconsistent, negative or missing fields fail. SSE/JSON usage supplies actual billed `cost`; native SDK price estimates are not invoice authority. Final native AssistantMessage usage is replaced with this measured normalization and actual total, preserving native child attribution without charging it again in the family ledger.

Input/output cost components use provider details if present. If detail is absent, those component slots in the native interface are zero placeholders while its total is actual; the ledger retains nullable detail and actualUsd. Do not infer per-category invoiced cost from those placeholders. `actualRequestUsd` is the sum of observed request invoices only; blocked unknown requests retain reservations separately.

Known completion releases unused reservation. Missing usage/cost after a send leaves its reservation, records UNKNOWN, and blocks new calls. An explicit output/input/cost/route violation retains the actual report, blocks the family and returns an error without executable tool content. A restart's unfinished reservation is converted by `reconcile()` to UNKNOWN, never refunded. Missing/corrupt ledgers and stale lock directories require root reconciliation; the library does not clear other processes' locks or assume a request was free.

The family seed is exact: `546633 + 192000 = 738633`, rounded upward to the even allocation738634; each family consumes369317 tokens and retains1130683 from1.5M. Each seed's budget USD is11.07951, including its known invoice fraction0.0001275 and unknown reserve11.0793825. No cap increased. The audit's incident546607, successful setup26, and rejected Codex request remain visible in the separate setup receipts.

## Input-bound and execution limitations

The text-only active-input bound is UTF8 bytes of the complete serialized request plus4096 service-framing tokens,256 per message and1024 per tool. This is conservative for byte-fallback tokenization **conditional on hidden service framing fitting those explicit allowances**. No canonical server tokenizer/framing specification was available, so this is not claimed to be an exact or unconditional provider-token proof. Images and nontext message parts are rejected. Actual prompt tokens are checked against the reservation after every response; any violation stops the family.

This meter enforces model requests, not scientific CPU/wall/memory/tool limits or generation-specific60k sub-budgets. It does not install the native kernel/container launcher, scorer or ORX lifecycle. Cancellation and unknown settlement preserve limits but cannot establish actual billing for missing provider receipts. Response reads have8MiB total/1MiB-frame bounds. Network timeout relies on the installed SDK/native fetch honoring abort; root retains its process wall deadline.

Same-process inline children are the qualified sharing topology. Different OS processes can fail closed against each other's reservations; daemon propagation and multiprocess recovery are not claimed. Atomic ledger writes protect normal process interruption; this is not a power-loss durability or external exactly-once guarantee. Native transcript cost displays during streaming may contain temporary provider SDK estimates; final message and meter ledger are the measured authority.

## Verification commands

From `experiments/argo_study_20260909`:

```sh
../../node_modules/.bin/tsx --test test_model_meter.ts
```

From repository root:

```sh
node_modules/.bin/tsc --ignoreConfig --noEmit --target ES2022 --module NodeNext --moduleResolution NodeNext --strict --skipLibCheck --types node experiments/argo_study_20260909/model_meter.ts experiments/argo_study_20260909/test_model_meter.ts
```

Tests cover cache/reasoning normalization, actual cost, frozen provider payload, reasoning/input cap rejection, concurrent episode reservations, shared family reservations across distinct episodes, USD rejection, absent-usage and503 failure/no retry, reported output/input violations, setup arithmetic, orphan reconciliation, and invalid persisted accounting.

## Narrow compatibility amendment

Read prospective-runtime-amendment.json before changing the meter. The factory now admits exactly80000 and120000 episode limits:80000 for amended development/selection and120000 for primary evaluation. Both limits passed concurrent-reservation negative fixtures. The exact M1 binding is unchanged. MeterError now uses an explicit readonly field and constructor assignment, compatible with erasable TypeScript syntax. `/opt/homebrew/bin/node` v26.7.0 successfully imported model_meter.ts through a standard top-level import with native type stripping; no model request or factory invocation occurred. Independent strict TypeScript checking also passed after this change.
