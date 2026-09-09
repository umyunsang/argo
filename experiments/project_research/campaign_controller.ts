import { AsyncLocalStorage } from "node:async_hooks";
import { spawn } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import { appendFileSync, existsSync, mkdirSync, readFileSync, realpathSync, renameSync, rmdirSync, unlinkSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { AuthStorage, createAgentSession, DefaultResourceLoader, ModelRegistry, SessionManager, SettingsManager } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import type { AgentSession, ToolDefinition } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import type { AuthCredential } from "/opt/homebrew/lib/node_modules/prime-agent/dist/core/auth-storage.js";
import { getModels, streamSimple } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import type { Api, AssistantMessage, Model } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/types.js";
import type { StreamFn } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-agent-core/dist/types.js";
import { AssistantMessageEventStream } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/utils/event-stream.js";
import { Type } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/typebox/build/index.mjs";

type Json = Record<string, unknown>;
export type HostBridge = (action: string, arguments_: Json) => Promise<Json>;
const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, "../..");
const privateRoot = join(homedir(), ".local/share/argo-project-research-20260909");

export interface ModelChoice {
  id: string;
  provider: string;
  model_id: string;
  status: string;
  billing_upper_krw?: number;
  billing_basis?: string;
  billing_mode?: "subscription" | "paid";
  billing_authorized?: boolean;
  openrouter_provider?: "openai" | "anthropic";
  expected_returned_model?: string;
  max_prompt_usd_per_million?: number;
  max_completion_usd_per_million?: number;
  accounting_rate_krw_per_usd?: number;
  max_output_tokens?: number;
}

export interface CampaignConfig {
  campaign_id: string;
  team_id: string;
  workspace: string;
  artifact_root: string;
  control_dir: string;
  project_id: string;
  image: string;
  model_pool: ModelChoice[];
  model_id: string;
  session_id: string;
  deadline_epoch: number;
  condition: "B" | "H" | "P";
  common_prompt: string;
  policy_prompt: string;
  task_prompt: string;
  auth_path: string;
  bridge_python: string;
  max_controller_turns?: number;
  role?: string;
}

function object(value: unknown): value is Json {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function inside(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path === "" || (!path.startsWith("..") && !isAbsolute(path));
}

function atomic(path: string, value: unknown): void {
  const temporary = `${path}.${randomUUID()}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600, flag: "wx", flush: true });
  renameSync(temporary, path);
}

function acquireControllerOwner(control: string, sessionId: string): () => void {
  const lock = join(control, "controller-owner.lock");
  const ownerPath = join(lock, "owner.json");
  const token = randomUUID();
  const claim = { pid: process.pid, session_id: sessionId, token };
  try { mkdirSync(lock, { mode: 0o700 }); atomic(ownerPath, claim); }
  catch (error) {
    if (!object(error) || error.code !== "EEXIST" || realpathSync(lock) !== lock) throw error;
    const recoveryLock = join(lock, "recovery.lock");
    try { mkdirSync(recoveryLock, { mode: 0o700 }); } catch { throw new Error("CONTROLLER_OWNER_RECOVERY_BUSY"); }
    try {
      const previous: unknown = JSON.parse(readFileSync(ownerPath, "utf8"));
      if (!object(previous) || typeof previous.pid !== "number" || !Number.isSafeInteger(previous.pid) || previous.pid <= 0) throw new Error("CONTROLLER_OWNER_UNKNOWN");
      try { process.kill(previous.pid, 0); throw new Error("CONTROLLER_SESSION_ALREADY_OWNED"); }
      catch (error) { if (!object(error) || error.code !== "ESRCH") throw error; }
      atomic(ownerPath, claim);
    } finally { rmdirSync(recoveryLock); }
  }
  return () => {
    const owner: unknown = JSON.parse(readFileSync(ownerPath, "utf8"));
    if (!object(owner) || owner.token !== token || owner.pid !== process.pid) throw new Error("CONTROLLER_OWNER_CHANGED");
    unlinkSync(ownerPath);
    rmdirSync(lock);
  };
}

export function loadCampaignConfig(path: string): CampaignConfig {
  const value: unknown = JSON.parse(readFileSync(path, "utf8"));
  if (!object(value)) throw new Error("CAMPAIGN_CONFIG_INVALID");
  for (const field of ["campaign_id", "team_id", "workspace", "artifact_root", "control_dir", "project_id", "image", "model_id", "session_id", "common_prompt", "policy_prompt", "task_prompt", "auth_path", "bridge_python"]) {
    if (typeof value[field] !== "string" || value[field] === "" || String(value[field]).includes("\0")) throw new Error("CAMPAIGN_CONFIG_INVALID");
  }
  if (!Array.isArray(value.model_pool) || !value.model_pool.every(object) || !["B", "H", "P"].includes(String(value.condition))) throw new Error("CAMPAIGN_POOL_INVALID");
  if (typeof value.deadline_epoch !== "number" || !Number.isFinite(value.deadline_epoch) || value.deadline_epoch <= Date.now() / 1000) throw new Error("CAMPAIGN_DEADLINE_EXHAUSTED");
  const config = value as unknown as CampaignConfig;
  for (const root of [config.workspace, config.artifact_root, config.control_dir]) {
    if (!isAbsolute(root) || realpathSync(root) !== root || !inside(privateRoot, root)) throw new Error("CAMPAIGN_PATH_INVALID");
  }
  if (new Set([config.workspace, config.artifact_root, config.control_dir]).size !== 3 || dirname(config.workspace) !== dirname(config.artifact_root) || !inside(join(privateRoot, "control"), config.control_dir) || !inside(config.control_dir, realpathSync(path)) || inside(config.workspace, config.control_dir) || inside(config.artifact_root, config.control_dir)) throw new Error("CAMPAIGN_PATH_INVALID");
  if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/.test(config.session_id) || !/^sha256:[a-f0-9]{64}$/.test(config.image) || !isAbsolute(config.bridge_python)) throw new Error("CAMPAIGN_IDENTITY_INVALID");
  if (config.max_controller_turns !== undefined && (!Number.isInteger(config.max_controller_turns) || config.max_controller_turns < 1 || config.max_controller_turns > 256)) throw new Error("CAMPAIGN_TURN_BOUND_INVALID");
  if (new Set(config.model_pool.map((choice) => choice.id)).size !== config.model_pool.length) throw new Error("DUPLICATE_MODEL_POOL_ID");
  return config;
}

export function selectedModel(config: CampaignConfig): { choice: ModelChoice; model: Model<Api> } {
  const choice = config.model_pool.find((entry) => entry.id === config.model_id);
  if (!choice || choice.status !== "QUALIFIED" || !["openai-codex", "anthropic", "openrouter"].includes(choice.provider)) throw new Error("MODEL_ROUTE_UNQUALIFIED");
  if (choice.billing_authorized !== true || !choice.billing_basis || !["subscription", "paid"].includes(String(choice.billing_mode))) throw new Error("MODEL_BILLING_UNQUALIFIED");
  const model = getModels(choice.provider as "openai-codex" | "anthropic" | "openrouter").find((entry) => entry.id === choice.model_id);
  const routeValid = model && (choice.provider === "openai-codex" ? model.api === "openai-codex-responses" && model.baseUrl === "https://chatgpt.com/backend-api"
    : choice.provider === "anthropic" ? model.api === "anthropic-messages" && model.baseUrl === "https://api.anthropic.com"
    : model.api === "openai-completions" && model.baseUrl === "https://openrouter.ai/api/v1");
  if (!routeValid) throw new Error("MODEL_ROUTE_MISMATCH");
  if (choice.provider === "openrouter") routerLimits(choice, model);
  else if (choice.billing_mode !== "subscription" || choice.billing_upper_krw !== 0) throw new Error("MODEL_BILLING_UNQUALIFIED");
  return { choice, model };
}

function executeJson(python: string, args: string[], input: Json, timeout: number): Promise<Json> {
  return new Promise((success, failure) => {
    const child = spawn(python, args, { cwd: repository, stdio: ["pipe", "pipe", "pipe"] });
    let output = "";
    let bytes = 0;
    const timer = setTimeout(() => child.kill("SIGTERM"), Math.max(1, timeout));
    child.stdout.on("data", (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > 1048576) child.kill("SIGTERM");
      else output += chunk.toString("utf8");
    });
    child.stderr.on("data", () => {});
    child.once("error", () => { clearTimeout(timer); failure(new Error("HOST_PROCESS_START_FAILED")); });
    child.once("close", (code) => {
      clearTimeout(timer);
      if (code !== 0 || bytes > 1048576) return failure(new Error("HOST_RESULT_UNKNOWN"));
      try {
        const value: unknown = JSON.parse(output.trim());
        if (!object(value)) throw new Error("HOST_RESULT_INVALID");
        success(value);
      } catch { failure(new Error("HOST_RESULT_INVALID")); }
    });
    child.stdin.on("error", () => {});
    child.stdin.end(JSON.stringify(input));
  });
}

export function hostBridge(configPath: string, config: CampaignConfig): HostBridge {
  return (action, args) => executeJson(config.bridge_python, ["-m", "experiments.project_research.campaign_bridge", "--config", configPath, action], args,
    Math.min(action === "run_experiment" ? 28800000 : 30000, (config.deadline_epoch - Date.now() / 1000) * 1000));
}

function routerLimits(choice: ModelChoice, model: Model<Api>) {
  if (choice.billing_mode !== "paid" || !["openai", "anthropic"].includes(String(choice.openrouter_provider))
      || choice.max_prompt_usd_per_million !== 2 || choice.max_completion_usd_per_million !== 10
      || choice.accounting_rate_krw_per_usd !== 2000 || (choice.max_output_tokens ?? 8192) !== 8192
      || !choice.expected_returned_model || !Number.isSafeInteger(model.contextWindow) || model.contextWindow <= 8192) throw new Error("OPENROUTER_BOUNDS_UNQUALIFIED");
  return { provider: choice.openrouter_provider as "openai" | "anthropic", prompt: 2, completion: 10, rate: 2000, output: 8192, input: model.contextWindow };
}

function rejectsCacheControl(value: unknown): boolean {
  if (Array.isArray(value)) return value.some(rejectsCacheControl);
  return object(value) && (Object.hasOwn(value, "cache_control") || Object.values(value).some(rejectsCacheControl));
}

export function fixedRouterPayload(choice: ModelChoice, model: Model<Api>, input: unknown): Json {
  const bounds = routerLimits(choice, model);
  if (!object(input) || input.model !== model.id || !Array.isArray(input.messages) || rejectsCacheControl(input)
      || input.plugins !== undefined || input.models !== undefined || input.route !== undefined || (input.n !== undefined && input.n !== 1)) throw new Error("OPENROUTER_PAYLOAD_UNSUPPORTED");
  for (const message of input.messages) {
    if (!object(message) || (Array.isArray(message.content) && message.content.some((part) => !object(part) || part.type !== "text" || typeof part.text !== "string"))
        || (message.content !== undefined && message.content !== null && typeof message.content !== "string" && !Array.isArray(message.content))) throw new Error("OPENROUTER_NON_TEXT_REQUEST");
  }
  const output = { ...input };
  delete output.max_completion_tokens;
  return { ...output, model: model.id, max_tokens: bounds.output, stream: true, stream_options: { include_usage: true },
    provider: { only: [bounds.provider], order: [bounds.provider], allow_fallbacks: false, require_parameters: true,
      max_price: { prompt: bounds.prompt, completion: bounds.completion, request: 0 } } };
}

export function routerReservation(choice: ModelChoice, model: Model<Api>, payload: Json): Json {
  const bounds = routerLimits(choice, model);
  if (JSON.stringify(fixedRouterPayload(choice, model, payload)) !== JSON.stringify(payload)) throw new Error("OPENROUTER_PAYLOAD_MUTATED");
  const bytes = Buffer.byteLength(JSON.stringify(payload), "utf8");
  const messages = Array.isArray(payload.messages) ? payload.messages.length : 0;
  const tools = Array.isArray(payload.tools) ? payload.tools.length : 0;
  const byteEstimate = bytes + 4096 + 256 * messages + 1024 * tools;
  if (byteEstimate > bounds.input || bytes > 4 * 1024 * 1024) throw new Error("OPENROUTER_INPUT_BOUND_EXCEEDED");
  // Reserve the registered full context: framing estimates do not prove tokenizer bounds.
  const usd = (bounds.input * bounds.prompt + bounds.output * bounds.completion) / 1_000_000;
  return { upper_krw: Math.ceil(usd * bounds.rate), input_upper_tokens: bounds.input, serialized_payload_bytes: bytes,
    byte_framing_estimate: byteEstimate, input_bound_basis: "registered_model_context_window", output_limit: bounds.output,
    max_price_usd_per_million: { prompt: bounds.prompt, completion: bounds.completion },
    usd_to_krw_upper: bounds.rate, reserved_usd: usd,
    request_sha256: createHash("sha256").update(JSON.stringify(payload)).digest("hex") };
}

interface NetworkCapture {
  requests: number; abort: AbortController; endpoint: string; sent: boolean;
  beforeSend?: (body: unknown) => Promise<void>;
  fetchOverride?: typeof globalThis.fetch;
  raw?: Json; rawUsageFrame?: string; responseId?: string; returnedModel?: string; resolvedProvider?: string;
  responseSha256?: string; complete?: boolean;
}

export function observeRouterResponse(response: Response, capture: NetworkCapture): Response {
  if (!response.body) return response;
  const hash = createHash("sha256");
  const decoder = new TextDecoder();
  const sse = response.headers.get("content-type")?.includes("text/event-stream") === true;
  let buffer = "";
  let bytes = 0;
  const observe = (value: unknown, frame: string) => {
    if (!object(value)) throw new Error("OPENROUTER_RESPONSE_INVALID");
    for (const [field, current] of [["id", capture.responseId], ["model", capture.returnedModel], ["provider", capture.resolvedProvider]] as const) {
      if (value[field] !== undefined && (typeof value[field] !== "string" || (current && value[field] !== current))) throw new Error("OPENROUTER_RESPONSE_IDENTITY_CHANGED");
    }
    if (typeof value.id === "string") capture.responseId = value.id;
    if (typeof value.model === "string") capture.returnedModel = value.model;
    if (typeof value.provider === "string") capture.resolvedProvider = value.provider;
    if (value.usage !== undefined && value.usage !== null) {
      if (!object(value.usage) || (capture.raw && JSON.stringify(capture.raw) !== JSON.stringify(value.usage))) throw new Error("OPENROUTER_USAGE_CHANGED");
      capture.raw = value.usage;
      capture.rawUsageFrame = frame;
    }
  };
  const line = (value: string) => {
    const trimmed = value.trim();
    if (trimmed.startsWith("data:") && trimmed.slice(5).trim() !== "[DONE]") observe(JSON.parse(trimmed.slice(5).trim()), trimmed.slice(5).trim());
  };
  const body = response.body.pipeThrough(new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      bytes += chunk.byteLength;
      if (bytes > 8 * 1024 * 1024) throw new Error("OPENROUTER_RESPONSE_TOO_LARGE");
      hash.update(chunk);
      buffer += decoder.decode(chunk, { stream: true });
      if (sse) {
        for (let index = buffer.indexOf("\n"); index >= 0; index = buffer.indexOf("\n")) { line(buffer.slice(0, index)); buffer = buffer.slice(index + 1); }
      }
      if (Buffer.byteLength(buffer) > 1024 * 1024) throw new Error("OPENROUTER_FRAME_TOO_LARGE");
      controller.enqueue(chunk);
    },
    flush() {
      buffer += decoder.decode();
      if (buffer.trim()) { if (sse) line(buffer); else observe(JSON.parse(buffer), buffer); }
      capture.complete = true;
      capture.responseSha256 = hash.digest("hex");
    },
  }));
  return new Response(body, { status: response.status, statusText: response.statusText, headers: response.headers });
}

export function routerInvoice(choice: ModelChoice, model: Model<Api>, capture: NetworkCapture, reservation: Json): Json {
  const bounds = routerLimits(choice, model);
  const usage = capture.raw;
  if (!capture.complete || !capture.responseSha256 || !capture.responseId || !usage || capture.returnedModel !== choice.expected_returned_model
      || capture.resolvedProvider?.toLowerCase() !== bounds.provider || capture.requests !== 1) throw new Error("OPENROUTER_INVOICE_IDENTITY_UNKNOWN");
  const prompt = usage.prompt_tokens;
  const completion = usage.completion_tokens;
  const total = usage.total_tokens;
  const cost = usage.cost;
  if (![prompt, completion, total].every((value) => typeof value === "number" && Number.isSafeInteger(value) && value >= 0)
      || Number(prompt) + Number(completion) !== total || Number(prompt) > bounds.input || Number(completion) > bounds.output
      || typeof cost !== "number" || !Number.isFinite(cost) || cost < 0 || cost > Number(reservation.reserved_usd)) throw new Error("OPENROUTER_RAW_CHARGE_UNKNOWN");
  const details = object(usage.prompt_tokens_details) ? usage.prompt_tokens_details : {};
  if (![details.cached_tokens ?? 0, details.cache_write_tokens ?? 0].every((value) => typeof value === "number" && Number.isSafeInteger(value) && value >= 0)
      || Number(details.cached_tokens ?? 0) > Number(prompt) || Number(details.cache_write_tokens ?? 0) > 0) throw new Error("OPENROUTER_UNRESERVED_CACHE_WRITE");
  const costText = String(cost);
  const [coefficient, exponent = "0"] = costText.toLowerCase().split("e");
  const [integer, fraction = ""] = coefficient.split(".");
  const scale = fraction.length - Number(exponent);
  const numerator = BigInt(integer + fraction) * BigInt(bounds.rate) * 10n ** BigInt(Math.max(0, -scale));
  const denominator = 10n ** BigInt(Math.max(0, scale));
  const allocated = Number((numerator + denominator - 1n) / denominator);
  return { source: "openrouter.raw_usage.cost", generation_id: capture.responseId, requested_model: model.id,
    returned_model: capture.returnedModel, provider: capture.resolvedProvider, usage,
    cost_usd: costText, accounting_rate_krw_per_usd: bounds.rate,
    allocation_krw: allocated, response_sha256: capture.responseSha256 };
}
const networkScope = new AsyncLocalStorage<NetworkCapture>();
let capturedFetch: typeof globalThis.fetch | undefined;

function installNetworkGuard(): void {
  if (capturedFetch) {
    if (globalThis.fetch !== capturedFetch) throw new Error("NETWORK_GUARD_REPLACED");
    return;
  }
  const nativeFetch = globalThis.fetch;
  capturedFetch = async (input, options) => {
    const scope = networkScope.getStore();
    if (!scope) return nativeFetch(input, options);
    const request = new Request(input, options);
    if (++scope.requests !== 1 || request.method !== "POST" || request.url !== scope.endpoint) {
      scope.abort.abort();
      throw new Error("UNRESERVED_PROVIDER_REQUEST_BLOCKED");
    }
    if (scope.beforeSend) await scope.beforeSend(JSON.parse(await request.clone().text()));
    scope.sent = true;
    const response = await (scope.fetchOverride ?? nativeFetch)(new Request(request, { redirect: "error" }));
    if (!response.ok) scope.abort.abort();
    return scope.endpoint.startsWith("https://openrouter.ai/") ? observeRouterResponse(response, scope) : response;
  };
  globalThis.fetch = capturedFetch;
}

function errorStreamMessage(model: Model<Api>, code: string): AssistantMessage {
  return { role: "assistant", content: [], api: model.api, provider: model.provider, model: model.id,
    stopReason: "error", errorMessage: code, timestamp: Date.now(),
    usage: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } } };
}

export function createRequestGuard(choice: ModelChoice, bridge: HostBridge, options: {
  stream?: StreamFn; shouldStop?: () => boolean; enforceNetwork?: boolean; deadline: number; journalPath?: string;
  fetch?: typeof globalThis.fetch; ownerSessionId?: string;
}) {
  const provider = options.stream ?? streamSimple;
  let blocked: string | null = null;
  let queue = Promise.resolve();
  const abort = new AbortController();
  const journal: Json[] = options.journalPath && existsSync(options.journalPath) ? JSON.parse(readFileSync(options.journalPath, "utf8")) : [];
  if (!Array.isArray(journal) || !journal.every((entry) => object(entry) && typeof entry.request_id === "string" && typeof entry.state === "string")) throw new Error("MODEL_REQUEST_JOURNAL_INVALID");
  const persistJournal = () => { if (options.journalPath) atomic(options.journalPath, journal); };
  const prior = journal.filter((entry) => entry.state !== "SETTLED" && entry.state !== "REFUSED");
  let reconciledPrior = false;
  if (options.enforceNetwork !== false) installNetworkGuard();
  const streamFn: StreamFn = (model, context, streamOptions) => {
    const output = new AssistantMessageEventStream();
    queue = queue.then(async () => {
      let reserved = false;
      let settled = false;
      let final: AssistantMessage | undefined;
      const requestId = randomUUID();
      const requestAbort = new AbortController();
      // Long review/analysis turns with a large context can exceed three minutes; the deadline still bounds each request.
      const timer = setTimeout(() => requestAbort.abort(), Math.max(1, Math.min(600000, (options.deadline - Date.now() / 1000) * 1000)));
      const ownerSession = streamOptions?.sessionId ?? options.ownerSessionId ?? (options.enforceNetwork === false ? "synthetic-fixture" : "");
      const paid = choice.provider === "openrouter";
      const endpoint = paid ? "https://openrouter.ai/api/v1/chat/completions" : choice.provider === "anthropic" ? "https://api.anthropic.com/v1/messages" : "https://chatgpt.com/backend-api/codex/responses";
      const capture: NetworkCapture = { requests: 0, abort: requestAbort, endpoint, sent: false, fetchOverride: options.fetch };
      let journalEntry: Json | undefined;
      let requestReservation: Json = { upper_krw: choice.billing_upper_krw };
      const reserve = async (bounds: Json) => {
        journalEntry = { request_id: requestId, owner_session_id: ownerSession, owner_pid: process.pid,
          state: "RESERVING", model_id: choice.id, ...bounds, at: new Date().toISOString() };
        journal.push(journalEntry);
        persistJournal();
        const admission = await bridge("reserve_model", { model_id: choice.id, owner_session_id: ownerSession, owner_pid: process.pid,
          reason: "Selected frozen-pool model for the current research session", request_id: requestId, ...bounds, billing_basis: choice.billing_basis });
        if (admission.status !== "RESERVED") { journalEntry.state = "REFUSED"; persistJournal(); throw new Error("MODEL_RESERVATION_REFUSED"); }
        reserved = true;
        journalEntry.state = "RESERVED";
        persistJournal();
      };
      try {
        if (prior.length && !reconciledPrior) {
          reconciledPrior = true;
          for (const entry of prior) {
            const receipt = object(entry.provider_invoice) ? { provider_invoice: entry.provider_invoice, actual_krw: entry.provider_invoice.allocation_krw } : {};
            const reconciled: Json = await bridge("settle_model", { request_id: entry.request_id, owner_session_id: entry.owner_session_id,
              ...receipt, usage: { native: entry.usage ?? null, usage_status: "UNKNOWN", reason: "UNFINISHED_REQUEST_FROM_PREVIOUS_CONTROLLER", cost_basis: "SDK_ESTIMATE_NOT_INVOICE" } }).catch(() => ({ status: "UNKNOWN" }));
            entry.state = reconciled.status === "SETTLED" && (object(entry.provider_invoice) || reconciled.already_settled === true) ? "SETTLED" : "UNKNOWN";
          }
          persistJournal();
          if (prior.some((entry) => entry.state !== "SETTLED")) blocked = "PRIOR_MODEL_REQUEST_REQUIRES_RECONCILIATION";
        }
        if (blocked || abort.signal.aborted || options.shouldStop?.()) throw new Error(blocked ?? "CONTROLLER_YIELD");
        if (!ownerSession || model.provider !== choice.provider || model.id !== choice.model_id) throw new Error("UNSELECTED_MODEL_OR_OWNER_BLOCKED");
        if (choice.status !== "QUALIFIED" || choice.billing_authorized !== true || !choice.billing_basis) throw new Error("MODEL_BILLING_UNQUALIFIED");
        if (paid) {
          if (model.api !== "openai-completions" || model.baseUrl !== "https://openrouter.ai/api/v1") throw new Error("MODEL_ROUTE_MISMATCH");
          routerLimits(choice, model);
          capture.beforeSend = async (body) => {
            if (!object(body)) throw new Error("OPENROUTER_PAYLOAD_UNSUPPORTED");
            requestReservation = routerReservation(choice, model, body);
            await reserve(requestReservation);
          };
        } else {
          if (!Number.isInteger(choice.billing_upper_krw) || Number(choice.billing_upper_krw) < 0) throw new Error("MODEL_BILLING_UNQUALIFIED");
          await reserve(requestReservation);
        }
        const signal = AbortSignal.any([abort.signal, requestAbort.signal, ...(streamOptions?.signal ? [streamOptions.signal] : [])]);
        const native = await networkScope.run(capture, () => provider(model, context, { ...streamOptions, signal, transport: "sse", serviceTier: "default", maxRetries: 0, timeoutMs: 600000,
          ...(paid ? { cacheRetention: "none" as const, maxTokens: 8192, onPayload: async (payload: unknown, selected: Model<Api>) => {
            const changed = streamOptions?.onPayload ? await streamOptions.onPayload(payload, selected) : payload;
            return fixedRouterPayload(choice, model, changed ?? payload);
          } } : {}) }));
        for await (const event of native) {
          if (event.type === "done") final = event.message;
          else if (event.type === "error") final = event.error;
          else output.push(event);
        }
        if (final && final.stopReason === "error" && journalEntry) journalEntry.provider_error = String(final.errorMessage ?? "").slice(0, 600);
        const usage = final?.usage;
        const observed = Boolean(usage && Number.isSafeInteger(usage.totalTokens) && usage.totalTokens > 0 && [usage.input, usage.output, usage.cacheRead, usage.cacheWrite].every((value) => Number.isSafeInteger(value) && value >= 0) && usage.input + usage.output + usage.cacheRead + usage.cacheWrite === usage.totalTokens);
        if (!journalEntry || !reserved) throw new Error("NO_ADMITTED_PROVIDER_REQUEST");
        if (paid) { journalEntry.raw_response = { generation_id: capture.responseId, returned_model: capture.returnedModel, provider: capture.resolvedProvider, response_sha256: capture.responseSha256, complete: capture.complete ?? false, usage: capture.raw, raw_usage_frame: capture.rawUsageFrame }; persistJournal(); }
        const invoice = paid ? routerInvoice(choice, model, capture, requestReservation) : undefined;
        if (invoice && (!usage || usage.input + usage.cacheRead + usage.cacheWrite !== capture.raw?.prompt_tokens || usage.output !== capture.raw?.completion_tokens)) throw new Error("OPENROUTER_NATIVE_USAGE_MISMATCH");
        if (invoice) { journalEntry.provider_invoice = invoice; journalEntry.raw_usage_frame = capture.rawUsageFrame; journalEntry.usage = usage ?? null; persistJournal(); }
        const settlement = await bridge("settle_model", { request_id: requestId, owner_session_id: ownerSession,
          ...(invoice ? { provider_invoice: invoice, actual_krw: invoice.allocation_krw } : {}),
          usage: { native: usage ?? null, usage_status: observed ? "OBSERVED" : "UNKNOWN", stop_reason: final?.stopReason ?? "missing_terminal", network_requests: capture.requests, cost_basis: "SDK_ESTIMATE_NOT_INVOICE" } });
        settled = true;
        journalEntry.state = settlement.status === "SETTLED" && observed ? "SETTLED" : "UNKNOWN";
        journalEntry.usage = usage ?? null;
        persistJournal();
        if (settlement.status !== "SETTLED") { blocked = "MODEL_CHARGE_UNKNOWN"; throw new Error(blocked); }
        if (!observed || !final || (options.enforceNetwork !== false && capture.requests !== 1)) { blocked = "MODEL_USAGE_UNKNOWN"; throw new Error(blocked); }
        if (final.stopReason === "error" || final.stopReason === "aborted") {
          blocked = "MODEL_REQUEST_FAILED";
          output.push({ type: "error", reason: final.stopReason, error: final });
        } else output.push({ type: "done", reason: final.stopReason, message: final });
      } catch (error) {
        if (journalEntry && paid) journalEntry.raw_response = { generation_id: capture.responseId, returned_model: capture.returnedModel, provider: capture.resolvedProvider, response_sha256: capture.responseSha256, complete: capture.complete ?? false, usage: capture.raw, raw_usage_frame: capture.rawUsageFrame };
        if (journalEntry && journalEntry.state !== "SETTLED" && journalEntry.state !== "REFUSED") { journalEntry.state = "UNKNOWN"; persistJournal(); }
        if (reserved && !settled) {
          blocked = "MODEL_SETTLEMENT_UNKNOWN";
          await bridge("settle_model", { request_id: requestId, owner_session_id: ownerSession, usage: { native: final?.usage ?? null, raw_openrouter_usage: capture.raw ?? null, usage_status: "UNKNOWN", network_requests: capture.requests, cost_basis: "SDK_ESTIMATE_NOT_INVOICE" } }).catch(() => {});
        }
        const code = error instanceof Error && /^[A-Z_]+$/.test(error.message) ? error.message : "MODEL_REQUEST_UNKNOWN";
        if (code !== "CONTROLLER_YIELD") blocked ??= code;
        output.push({ type: "error", reason: "error", error: errorStreamMessage(model, code) });
      } finally {
        clearTimeout(timer);
        output.end();
      }
    });
    return output;
  };
  return { streamFn, blockedReason: () => blocked, halt: () => abort.abort() };
}

interface PendingAction { request_id: string; action: "run_experiment" | "choose_model" | "finish"; arguments: Json; }
interface ControllerState { schema: string; campaign_id: string; team_id: string; session_id: string; model_id: string; session_file?: string; pending?: PendingAction; last_host_result?: Json; status: string; turns: number; }
export interface ControllerFixtures { bridge?: HostBridge; stream?: StreamFn; auth?: AuthStorage; kernelBarrier?: () => Promise<Json>; }

function result(value: Json) {
  return { content: [{ type: "text" as const, text: JSON.stringify(value) }], details: value };
}

export async function runCampaign(configPath: string, fixtures: ControllerFixtures = {}): Promise<Json> {
  const config = loadCampaignConfig(configPath);
  const { choice, model } = selectedModel(config);
  const bridge = fixtures.bridge ?? hostBridge(configPath, config);
  const statePath = join(config.control_dir, "controller-state.json");
  const eventsPath = join(config.control_dir, "controller-events.jsonl");
  const profile = join(config.control_dir, "native-profile");
  const sessions = join(config.artifact_root, "sessions");
  for (const directory of [profile, sessions]) mkdirSync(directory, { recursive: true, mode: 0o700 });
  const previous: unknown = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : undefined;
  if (previous !== undefined && (!object(previous) || previous.campaign_id !== config.campaign_id || previous.team_id !== config.team_id)) throw new Error("CONTROLLER_STATE_IDENTITY_CHANGED");
  let state: ControllerState = object(previous) && previous.session_id === config.session_id ? previous as unknown as ControllerState : { schema: "project-research-controller/v1", campaign_id: config.campaign_id, team_id: config.team_id, session_id: config.session_id, model_id: config.model_id, status: "STARTING", turns: 0 };
  if (state.model_id !== config.model_id) throw new Error("MODEL_CHANGE_REQUIRES_NEW_SESSION");
  if (state.schema !== "project-research-controller/v1" || !Number.isInteger(state.turns) || state.turns < 0 || (state.session_file && !inside(sessions, realpathSync(state.session_file)))) throw new Error("CONTROLLER_STATE_INVALID");
  if (!state.pending && ["MODEL_CHANGE_REQUESTED", "CONCLUSION_SUBMITTED"].includes(state.status)) return { ...state, scope: "RESEARCH_APPARATUS", AAA: "UNASSESSED", PI: "PENDING" };
  const releaseOwner = acquireControllerOwner(config.control_dir, config.session_id);
  const log = (value: Json) => appendFileSync(eventsPath, `${JSON.stringify({ at: new Date().toISOString(), ...value })}\n`, { mode: 0o600 });
  const save = () => atomic(statePath, state);
  const barrier = fixtures.kernelBarrier ?? (() => executeJson(config.bridge_python, ["-m", "experiments.project_research.kernel_launcher", "--config", configPath, "--status"], {}, 15000));
  let session: AgentSession | undefined;
  let activeGuard: ReturnType<typeof createRequestGuard> | undefined;
  let stopping = false;
  const stop = () => { stopping = true; activeGuard?.halt(); void session?.abort().catch(() => {}); };
  process.once("SIGTERM", stop);
  process.once("SIGINT", stop);
  const deadlineTimer = setTimeout(stop, Math.max(1, (config.deadline_epoch - Date.now() / 1000 - 15) * 1000));
  const previousEnvironment = { wrapper: process.env.PRIME_AGENT_KERNEL_PYTHON, config: process.env.ARGO_KERNEL_CONFIG, telemetry: process.env.PRIME_AGENT_TELEMETRY };
  process.env.PRIME_AGENT_KERNEL_PYTHON = join(here, "kernel_launcher.py");
  process.env.ARGO_KERNEL_CONFIG = configPath;
  process.env.PRIME_AGENT_TELEMETRY = "0";
  try {
    for (; state.turns < (config.max_controller_turns ?? 64) && !stopping; ) {
      if (state.pending) {
        const pending = state.pending;
        const clear = await barrier();
        if (clear.status !== "CLEAR") { state.status = "KERNEL_RECONCILIATION_REQUIRED"; save(); break; }
        const answer = await bridge(pending.action, { ...pending.arguments, request_id: pending.request_id });
        state.last_host_result = answer;
        const accepted = !answer.error && (pending.action === "run_experiment" ? ["OBSERVED", "SUCCEEDED", "EXECUTED_UNVALIDATED", "FAILED", "CANCELLED"].includes(String(answer.status)) : pending.action === "choose_model" ? answer.status === "MODEL_CHANGE_REQUESTED" : answer.status === "CANDIDATE_SUBMITTED");
        if (accepted) state.pending = undefined;
        state.status = !accepted ? "HOST_ACTION_REQUIRES_RECONCILIATION" : pending.action === "run_experiment" ? "RESEARCH_OBSERVED" : pending.action === "choose_model" ? "MODEL_CHANGE_REQUESTED" : "CONCLUSION_SUBMITTED";
        log({ event: "host_action_result", action: pending.action, request_id: pending.request_id, result: answer });
        save();
        if (!accepted || pending.action !== "run_experiment") break;
      }
      const publicState = await bridge("read_state", {});
      if (publicState.halted === true || publicState.status === "UNKNOWN" || publicState.error) { state.status = "HOST_RECONCILIATION_REQUIRED"; save(); break; }
      const auth = fixtures.auth ?? (() => {
        const value: unknown = JSON.parse(readFileSync(config.auth_path, "utf8"));
        const credential = object(value) ? value[choice.provider] : undefined;
        if (!object(credential) || !["oauth", "api_key"].includes(String(credential.type))) throw new Error("MODEL_AUTH_MISSING");
        if (credential.type === "oauth" && (typeof credential.expires !== "number" || credential.expires <= config.deadline_epoch * 1000)) throw new Error("MODEL_AUTH_EXPIRES_BEFORE_DEADLINE");
        return AuthStorage.inMemory({ [choice.provider]: credential as unknown as AuthCredential }, { usePrimeCliConfig: false });
      })();
      const settings = SettingsManager.inMemory({ retry: { enabled: false, provider: { maxRetries: 0, timeoutMs: 600000 } }, autoRefine: { enabled: false }, compaction: { enabled: false }, idleEvictionMinutes: "off", packages: [], extensions: [], skills: [], prompts: [], mcpServers: {} });
      const systemPrompt = `${readFileSync(config.common_prompt, "utf8")}\n${readFileSync(config.policy_prompt, "utf8")}\nUse the native ipython tool for persistent research code and RLM delegation. Only this team's workspace and artifacts are visible. run_experiment yields execution to the trusted host after kernels are snapshotted and closed; its result arrives on continuation. Model selection yields to a new host-started session. Record a checkpoint before changing model or submitting your conclusion. Final evaluation is unavailable here.`;
      const loader = new DefaultResourceLoader({ cwd: config.workspace, agentDir: profile, settingsManager: settings, noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true, bundledSkillsDir: null, systemPrompt, appendSystemPrompt: [] });
      await loader.reload();
      if (loader.getSkills().skills.length || loader.getAgentsFiles().agentsFiles.length || loader.getPrompts().prompts.length) throw new Error("AMBIENT_RESOURCES_LOADED");
      const defer = (action: PendingAction["action"], args: Json) => {
        if (state.pending) return result({ status: "ACTION_ALREADY_PENDING" });
        state.pending = { request_id: randomUUID(), action, arguments: args };
        state.status = "YIELDED";
        save();
        return result({ status: "YIELDED_TO_HOST", action, request_id: state.pending.request_id });
      };
      const customTools: ToolDefinition[] = [
        { name: "read_state", label: "Research state", description: "Read this team's permitted research state, evidence gaps, results and budget.", parameters: Type.Object({}, { additionalProperties: false }), async execute() { return result(await bridge("read_state", {})); } },
        { name: "run_experiment", label: "Run research experiment", description: "Freeze a workspace source and test a stated hypothesis using authoritative ORX. The controller yields, closes kernels, then returns its real development receipt on continuation.", parameters: Type.Object({ relative_source: Type.String(), hypothesis: Type.String() }, { additionalProperties: false }), async execute(_id, args: { relative_source: string; hypothesis: string }) {
          const source = resolve(config.workspace, args.relative_source);
          if (!inside(config.workspace, source) || realpathSync(source) !== source || isAbsolute(args.relative_source)) return result({ error: "SOURCE_PATH_INVALID" });
          const sha = createHash("sha256").update(readFileSync(source)).digest("hex");
          return defer("run_experiment", { ...args, source_sha256: sha });
        } },
        { name: "checkpoint", label: "Persist research checkpoint", description: "Record question, confirmed decisions, artifacts, uncertainties and actual first-hypothesis evidence for recovery.", parameters: Type.Object({ question: Type.String(), artifacts: Type.Array(Type.String()), uncertainties: Type.Array(Type.String()), confirmed_decisions: Type.Array(Type.String()), first_hypothesis_observed: Type.Boolean(), observation_evidence: Type.Array(Type.String()) }, { additionalProperties: false }), async execute(_id, args: Json) { if (state.pending) return result({ status: "ACTION_ALREADY_PENDING" }); return result(await bridge("checkpoint", args)); } },
        { name: "choose_model", label: "Choose another model", description: "Request another qualified frozen-pool model with a research reason. This ends this native session and requires a host-started new session.", parameters: Type.Object({ model_id: Type.String(), reason: Type.String() }, { additionalProperties: false }), async execute(_id, args: { model_id: string; reason: string }) { if (!config.model_pool.some((entry) => entry.id === args.model_id && entry.status === "QUALIFIED") || args.model_id === choice.id) return result({ error: "MODEL_CHOICE_INVALID" }); return defer("choose_model", args); } },
        { name: "finish", label: "Submit bounded conclusion", description: "Submit conclusion, evidence-linked claims and limitations for separate quality and PI review.", parameters: Type.Object({ conclusion: Type.String(), claims: Type.Array(Type.String()), limitations: Type.Array(Type.String()) }, { additionalProperties: false }), async execute(_id, args: Json) { return defer("finish", args); } },
      ];
      const manager = state.session_file ? SessionManager.open(state.session_file, sessions, config.workspace) : SessionManager.create(config.workspace, sessions);
      if (!state.session_file) manager.newSession({ id: config.session_id });
      // A blinded supervisor reviews only: no experiment launch, no model change.
      const reviewOnly = config.role === "supervisor";
      const activeCustomTools = reviewOnly ? customTools.filter((tool) => ["read_state", "finish"].includes(tool.name)) : customTools;
      const toolNames = ["ipython", ...activeCustomTools.map((tool) => tool.name)];
      ({ session } = await createAgentSession({ cwd: config.workspace, agentDir: profile, authStorage: auth, modelRegistry: ModelRegistry.inMemory(auth), model, thinkingLevel: "high", settingsManager: settings, resourceLoader: loader, sessionManager: manager, tools: toolNames, allowedToolNames: toolNames, customTools: activeCustomTools, includeGoals: false, includeCompactSkill: false, rlmMaxDepth: reviewOnly ? 0 : 2, prewarmIpythonKernel: false, telemetryDisabled: true }));
      manager.flushNow();
      state.session_file = session.sessionFile;
      state.status = "RUNNING";
      save();
      // The native SDK streamFn resolves provider auth from the in-memory registry; the guard wraps it.
      const nativeStream = session.agent.streamFn;
      activeGuard = createRequestGuard(choice, bridge, { stream: fixtures.stream ?? nativeStream, enforceNetwork: fixtures.stream ? false : true, deadline: config.deadline_epoch, ownerSessionId: config.session_id, journalPath: join(config.control_dir, "model-requests.json"), shouldStop: () => stopping || Boolean(state.pending) });
      session.agent.streamFn = activeGuard.streamFn;
      session.agent.toolExecution = "sequential";
      session.agent.transport = "sse";
      session.agent.shouldStopBeforeTurn = () => stopping || Boolean(state.pending);
      const nativeBeforeTool = session.agent.beforeToolCall;
      session.agent.beforeToolCall = async (context, signal) => state.pending ? { block: true, reason: "Pending host action must be resolved before additional tool calls" } : nativeBeforeTool?.(context, signal);
      session.subscribe((event) => log({ event: "native_event", value: event }));
      try {
        await session.prompt(`${readFileSync(config.task_prompt, "utf8")}\nCurrent permitted state: ${JSON.stringify(publicState)}\nLast host result: ${JSON.stringify(state.last_host_result ?? null)}`, { expandPromptTemplates: false });
        if (!state.pending && !stopping) await session.waitForRlmQuiescence(AbortSignal.timeout(Math.max(1, Math.min(60000, (config.deadline_epoch - Date.now() / 1000) * 1000))));
      } finally {
        if (state.pending || stopping) activeGuard.halt();
        await session.abort();
        await session.disposeAsync({ kernelSnapshot: true });
        session = undefined;
        state.turns++;
        save();
      }
      if (activeGuard.blockedReason()) { state.status = activeGuard.blockedReason() ?? "MODEL_UNKNOWN"; save(); break; }
      if (!state.pending) { state.status = "AWAITING_RESEARCH_DECISION"; save(); break; }
    }
    if (stopping) { state.status = "INTERRUPTED_CHECKPOINT_RETAINED"; save(); }
    else if (state.turns >= (config.max_controller_turns ?? 64) && state.pending) { state.status = "CONTROLLER_TURN_LIMIT"; save(); }
  } catch (error) {
    state.status = error instanceof Error && /^[A-Z_]+$/.test(error.message) ? error.message : "CONTROLLER_FAILURE_REQUIRES_RECONCILIATION";
    save();
  } finally {
    activeGuard?.halt();
    if (session) { await session.abort().catch(() => {}); await session.disposeAsync({ kernelSnapshot: true }).catch(() => {}); }
    clearTimeout(deadlineTimer);
    process.removeListener("SIGTERM", stop);
    process.removeListener("SIGINT", stop);
    for (const [key, value] of [["PRIME_AGENT_KERNEL_PYTHON", previousEnvironment.wrapper], ["ARGO_KERNEL_CONFIG", previousEnvironment.config], ["PRIME_AGENT_TELEMETRY", previousEnvironment.telemetry]] as const) {
      if (value === undefined) delete process.env[key]; else process.env[key] = value;
    }
    releaseOwner();
  }
  const summary = { ...state, model_provider: choice.provider, concrete_model_id: choice.model_id, scope: "RESEARCH_APPARATUS", AAA: "UNASSESSED", PI: "PENDING" };
  atomic(join(config.control_dir, "controller-summary.json"), summary);
  atomic(join(config.control_dir, `controller-summary-${config.session_id}.json`), summary);
  return summary;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) throw new Error("CONFIG_PATH_REQUIRED");
    const summary = await runCampaign(resolve(process.argv[2]));
    process.stdout.write(`${JSON.stringify(summary)}\n`);
  } catch (error) {
    process.stdout.write(`${JSON.stringify({ status: error instanceof Error && /^[A-Z_]+$/.test(error.message) ? error.message : "CONTROLLER_INITIALIZATION_FAILED" })}\n`);
    process.exitCode = 1;
  }
}
