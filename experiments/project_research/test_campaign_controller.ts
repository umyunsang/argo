import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { AuthStorage } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { getModels } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import type { AssistantMessage } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/types.js";
import type { StreamFn } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-agent-core/dist/types.js";
import { AssistantMessageEventStream } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/utils/event-stream.js";
import { createRequestGuard, fixedRouterPayload, routerReservation, runCampaign, selectedModel } from "./campaign_controller.ts";
import type { CampaignConfig, HostBridge, ModelChoice } from "./campaign_controller.ts";

const model = getModels("openai-codex").find((entry) => entry.id === "gpt-5.6-sol");
assert.ok(model);
const choice: ModelChoice = { id: "codex-sol", provider: "openai-codex", model_id: "gpt-5.6-sol", status: "QUALIFIED", billing_upper_krw: 0, billing_basis: "Synthetic fixture; provider replaced", billing_mode: "subscription", billing_authorized: true };
const routerModel = getModels("openrouter").find((entry) => entry.id === "openai/gpt-5.6-sol");
assert.ok(routerModel);
const routerChoice: ModelChoice = { id: "router-sol", provider: "openrouter", model_id: "openai/gpt-5.6-sol", status: "QUALIFIED",
  billing_basis: "Synthetic raw-provider fixture; no network", billing_mode: "paid", billing_authorized: true,
  openrouter_provider: "openai", expected_returned_model: "openai/gpt-5.6-sol-20260709",
  max_prompt_usd_per_million: 2, max_completion_usd_per_million: 10, accounting_rate_krw_per_usd: 2000, max_output_tokens: 8192 };

function routerSse(options: { omitCost?: boolean; provider?: string; cost?: number } = {}) {
  const identity = { id: "gen-synthetic-only", object: "chat.completion.chunk", created: 1,
    model: routerChoice.expected_returned_model, provider: options.provider ?? "OpenAI" };
  const usage = { prompt_tokens: 10, completion_tokens: 3, total_tokens: 13,
    prompt_tokens_details: { cached_tokens: 0, cache_write_tokens: 0 },
    ...(options.omitCost ? {} : { cost: options.cost ?? 0.00005 }), cost_details: { upstream_inference_cost: 123 } };
  const frames = [{ ...identity, choices: [{ index: 0, delta: { role: "assistant", content: "검사" }, finish_reason: null }] },
    { ...identity, choices: [{ index: 0, delta: {}, finish_reason: "stop" }], usage }];
  const bytes = new TextEncoder().encode(frames.map((frame) => `data: ${JSON.stringify(frame)}\n\n`).join("") + "data: [DONE]\n\n");
  return new Response(new ReadableStream<Uint8Array>({ start(controller) { for (let i = 0; i < bytes.length; i += 17) controller.enqueue(bytes.slice(i, i + 17)); controller.close(); } }), { headers: { "content-type": "text/event-stream" } });
}

test("OpenRouter bound comes from registered context and output cap; cache writes and multimodal payloads are rejected", () => {
  const payload = fixedRouterPayload(routerChoice, routerModel, { model: routerModel.id, messages: [{ role: "user", content: "fixture" }] });
  const reservation = routerReservation(routerChoice, routerModel, payload);
  assert.equal(payload.max_tokens, 8192);
  assert.equal(reservation.input_upper_tokens, routerModel.contextWindow);
  assert.equal(reservation.upper_krw, Math.ceil((routerModel.contextWindow * 2 + 8192 * 10) / 1_000_000 * 2000));
  assert.throws(() => fixedRouterPayload(routerChoice, routerModel, { model: routerModel.id, messages: [{ role: "user", content: [{ type: "text", text: "fixture", cache_control: { type: "ephemeral" } }] }] }), /UNSUPPORTED/);
  assert.throws(() => fixedRouterPayload(routerChoice, routerModel, { model: routerModel.id, messages: [{ role: "user", content: [{ type: "image_url", image_url: { url: "data:fixture" } }] }] }), /NON_TEXT/);
});

test("native OpenRouter SDK stream settles captured raw usage.cost after complete SSE consumption", async () => {
  const order: string[] = [];
  const calls: Array<{ action: string; args: Record<string, unknown> }> = [];
  const bridge: HostBridge = async (action, args) => { order.push(action); calls.push({ action, args }); return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" }; };
  const fakeFetch: typeof fetch = async (input) => {
    order.push("http");
    const request = new Request(input);
    assert.equal(request.url, "https://openrouter.ai/api/v1/chat/completions");
    const payload = await request.json() as Record<string, unknown>;
    assert.equal(payload.max_tokens, 8192);
    assert.equal(JSON.stringify(payload).includes("cache_control"), false);
    assert.deepEqual(payload.provider, { only: ["openai"], order: ["openai"], allow_fallbacks: false, require_parameters: true, max_price: { prompt: 2, completion: 10, request: 0 } });
    return routerSse();
  };
  const guard = createRequestGuard(routerChoice, bridge, { fetch: fakeFetch, deadline: Date.now() / 1000 + 60 });
  const message = await consume(guard.streamFn(routerModel, { messages: [{ role: "user", content: "synthetic", timestamp: 1 }] }, { apiKey: "fake-unsent", sessionId: "native-owner-fixture", reasoning: "high" }));
  assert.equal(message?.stopReason, "stop");
  assert.deepEqual(order, ["reserve_model", "http", "settle_model"]);
  assert.equal(calls[0].args.owner_session_id, "native-owner-fixture");
  const invoice = calls[1].args.provider_invoice as Record<string, unknown>;
  assert.equal(invoice.source, "openrouter.raw_usage.cost");
  assert.equal(invoice.cost_usd, "0.00005");
  assert.equal(invoice.allocation_krw, 1);
  assert.equal(calls[1].args.actual_krw, 1);
  assert.equal(String(invoice.response_sha256).length, 64);
  assert.equal((invoice.usage as Record<string, unknown>).cost, 0.00005);
  assert.equal(guard.blockedReason(), null);
});

test("missing raw charge or wrong returned provider remains UNKNOWN and prevents another send", async () => {
  for (const fixture of [{ omitCost: true }, { provider: "UnqualifiedProvider" }]) {
    let http = 0;
    const calls: Array<{ action: string; args: Record<string, unknown> }> = [];
    const bridge: HostBridge = async (action, args) => { calls.push({ action, args }); return { status: action === "reserve_model" ? "RESERVED" : "UNKNOWN" }; };
    const guard = createRequestGuard(routerChoice, bridge, { fetch: async () => { http++; return routerSse(fixture); }, deadline: Date.now() / 1000 + 60 });
    const request = (): Promise<AssistantMessage | undefined> => consume(guard.streamFn(routerModel, { messages: [{ role: "user", content: "fixture", timestamp: 1 }] }, { apiKey: "fake-unsent", sessionId: "native-owner-fixture" }));
    assert.equal((await request())?.stopReason, "error");
    assert.equal((await request())?.stopReason, "error");
    assert.equal(http, 1);
    assert.equal(Object.hasOwn(calls.at(-1)?.args ?? {}, "provider_invoice"), false);
    assert.equal((calls.at(-1)?.args.usage as Record<string, unknown>).usage_status, "UNKNOWN");
  }
});

test("explicit raw zero cost is accepted only with complete positive-usage response", async () => {
  let allocated: unknown;
  const guard = createRequestGuard(routerChoice, async (action, args) => { if (action === "settle_model") allocated = args.actual_krw; return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" }; }, { fetch: async () => routerSse({ cost: 0 }), deadline: Date.now() / 1000 + 60 });
  assert.equal((await consume(guard.streamFn(routerModel, { messages: [] }, { apiKey: "fake-unsent", sessionId: "native-owner-fixture" })))?.stopReason, "stop");
  assert.equal(allocated, 0);
});

function response(content: AssistantMessage["content"] = [{ type: "text", text: "fixture" }], tokens = 5) {
  assert.ok(model);
  const message: AssistantMessage = { role: "assistant", content, provider: model.provider, model: model.id, api: model.api, timestamp: Date.now(), stopReason: content.some((item) => item.type === "toolCall") ? "toolUse" : "stop", usage: { input: tokens, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: tokens, cost: { input: 99, output: 0, cacheRead: 0, cacheWrite: 0, total: 99 } } };
  const stream = new AssistantMessageEventStream();
  stream.push({ type: "start", partial: message });
  stream.push({ type: "done", reason: message.stopReason as "stop" | "toolUse", message });
  stream.end();
  return stream;
}

async function consume(stream: ReturnType<StreamFn>) {
  let message: AssistantMessage | undefined;
  for await (const event of await stream) {
    if (event.type === "done") message = event.message;
    else if (event.type === "error") message = event.error;
  }
  return message;
}

test("request guard reserves first and never treats SDK estimated cost as invoice", async () => {
  const order: string[] = [];
  const payloads: Record<string, unknown>[] = [];
  const bridge: HostBridge = async (action, args) => { order.push(action); payloads.push(args); return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" }; };
  const guard = createRequestGuard(choice, bridge, { stream: () => { order.push("provider"); return response(); }, enforceNetwork: false, deadline: Date.now() / 1000 + 60 });
  const message = await consume(guard.streamFn(model, { messages: [] }, {}));
  assert.deepEqual(order, ["reserve_model", "provider", "settle_model"]);
  assert.equal(message?.usage.cost.total, 99);
  assert.equal(Object.hasOwn(payloads[1], "cost"), false);
  assert.equal((payloads[1].usage as Record<string, unknown>).cost_basis, "SDK_ESTIMATE_NOT_INVOICE");
});

test("unknown settlement serializes and blocks a queued model call", async () => {
  let providerCalls = 0;
  const bridge: HostBridge = async (action) => ({ status: action === "reserve_model" ? "RESERVED" : "UNKNOWN" });
  const guard = createRequestGuard(choice, bridge, { stream: () => { providerCalls++; return response(); }, enforceNetwork: false, deadline: Date.now() / 1000 + 60 });
  const replies = await Promise.all([consume(guard.streamFn(model, { messages: [] }, {})), consume(guard.streamFn(model, { messages: [] }, {}))]);
  assert.equal(providerCalls, 1);
  assert.ok(replies.every((reply) => reply?.stopReason === "error"));
  assert.equal(guard.blockedReason(), "MODEL_CHARGE_UNKNOWN");
});

test("missing usage is UNKNOWN even when native SDK emits zero placeholders", async () => {
  const bridge: HostBridge = async (action, args) => {
    if (action === "settle_model") assert.equal((args.usage as Record<string, unknown>).usage_status, "UNKNOWN");
    return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" };
  };
  const guard = createRequestGuard(choice, bridge, { stream: () => response(undefined, 0), enforceNetwork: false, deadline: Date.now() / 1000 + 60 });
  assert.equal((await consume(guard.streamFn(model, { messages: [] }, {})))?.stopReason, "error");
  assert.equal(guard.blockedReason(), "MODEL_USAGE_UNKNOWN");
});

test("refused reserve never invokes a model", async () => {
  let calls = 0;
  const guard = createRequestGuard(choice, async () => ({ status: "REFUSED" }), { stream: () => { calls++; return response(); }, enforceNetwork: false, deadline: Date.now() / 1000 + 60 });
  assert.equal((await consume(guard.streamFn(model, { messages: [] }, {})))?.errorMessage, "MODEL_RESERVATION_REFUSED");
  assert.equal(calls, 0);
});

test("UNQUALIFIED Claude or missing billability never selects a provider", () => {
  assert.throws(() => selectedModel({ model_id: "claude", model_pool: [{ id: "claude", provider: "claude-cli", model_id: "claude-opus-4-7", status: "UNQUALIFIED" }] } as CampaignConfig), /UNQUALIFIED/);
  assert.throws(() => selectedModel({ model_id: choice.id, model_pool: [{ ...choice, billing_authorized: false }] } as CampaignConfig), /BILLING/);
  const claude: ModelChoice = { id: "claude-sonnet", provider: "anthropic", model_id: "claude-sonnet-4-6", status: "QUALIFIED", billing_upper_krw: 0, billing_basis: "included allowance snapshot", billing_mode: "subscription", billing_authorized: true };
  const selected = selectedModel({ model_id: claude.id, model_pool: [claude] } as CampaignConfig);
  assert.equal(selected.model.api, "anthropic-messages");
  assert.equal(selected.model.baseUrl, "https://api.anthropic.com");
  assert.throws(() => selectedModel({ model_id: claude.id, model_pool: [{ ...claude, billing_upper_krw: 5 }] } as CampaignConfig), /BILLING/);
  assert.throws(() => selectedModel({ model_id: claude.id, model_pool: [{ ...claude, billing_mode: "paid" }] } as CampaignConfig), /BILLING/);
});

test("anthropic subscription guard admits only the messages endpoint once per reserved request", async () => {
  const claudeModel = getModels("anthropic").find((entry) => entry.id === "claude-sonnet-4-6");
  assert.ok(claudeModel);
  const claude: ModelChoice = { id: "claude-sonnet", provider: "anthropic", model_id: "claude-sonnet-4-6", status: "QUALIFIED", billing_upper_krw: 0, billing_basis: "included allowance snapshot", billing_mode: "subscription", billing_authorized: true };
  const order: string[] = [];
  const bridge: HostBridge = async (action) => { order.push(action); return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" }; };
  const seen: string[] = [];
  const guard = createRequestGuard(claude, bridge, { deadline: Date.now() / 1000 + 60, fetch: async (input) => { seen.push(new Request(input).url); throw new Error("fixture-no-network"); } });
  const message = await consume(guard.streamFn(claudeModel, { messages: [{ role: "user", content: "synthetic", timestamp: 1 }] }, { apiKey: "sk-ant-oat01-fixture-unsent", sessionId: "native-owner-fixture", reasoning: "high" }));
  assert.equal(message?.stopReason, "error");
  assert.deepEqual(seen, ["https://api.anthropic.com/v1/messages"]);
  assert.deepEqual(order, ["reserve_model", "settle_model"]);
  assert.notEqual(guard.blockedReason(), null);
});

test("unfinished request journal blocks dispatch across a new controller guard", async () => {
  const f = fixture("B");
  const path = join(f.config.control_dir, "request-journal.json");
  writeFileSync(path, JSON.stringify([{ request_id: "reserved-before-process-crash", state: "RESERVED" }]));
  let providerCalls = 0;
  const actions: string[] = [];
  try {
    const guard = createRequestGuard(choice, async (action) => { actions.push(action); return { status: "UNKNOWN" }; }, { journalPath: path, stream: () => { providerCalls++; return response(); }, enforceNetwork: false, deadline: Date.now() / 1000 + 60 });
    assert.equal((await consume(guard.streamFn(model, { messages: [] }, {})))?.stopReason, "error");
    assert.deepEqual(actions, ["settle_model"]);
    assert.equal(providerCalls, 0);
    assert.equal(guard.blockedReason(), "PRIOR_MODEL_REQUEST_REQUIRES_RECONCILIATION");
  } finally { rmSync(f.directory, { recursive: true, force: true }); rmSync(f.config.control_dir, { recursive: true, force: true }); }
});

function fixture(condition: "B" | "P") {
  const root = join(homedir(), ".local/share/argo-project-research-20260909/qualification");
  mkdirSync(root, { recursive: true, mode: 0o700 });
  const directory = mkdtempSync(join(root, "controller-"));
  const workspace = join(directory, "workspace");
  const artifact_root = join(directory, "artifacts");
  const control_dir = join(homedir(), ".local/share/argo-project-research-20260909/control/qualification", directory.split("/").at(-1) ?? "missing");
  for (const path of [workspace, artifact_root, control_dir]) mkdirSync(path, { recursive: true, mode: 0o700 });
  const common_prompt = join(control_dir, "common.md");
  const policy_prompt = join(control_dir, "policy.md");
  const task_prompt = join(control_dir, "task.md");
  for (const path of [common_prompt, policy_prompt, task_prompt]) writeFileSync(path, "Synthetic native controller fixture. No actual scientific claims.");
  writeFileSync(join(workspace, "solution.py"), "print('synthetic candidate')\n");
  const config: CampaignConfig = { campaign_id: "fixture", team_id: condition, workspace, artifact_root, control_dir, project_id: "11111111-1111-4111-8111-111111111111", image: "sha256:" + "a".repeat(64), model_pool: [choice, { ...choice, id: "codex-terra", model_id: "gpt-5.6-terra" }], model_id: choice.id, session_id: `fixture-${condition}-${Date.now()}`, deadline_epoch: Date.now() / 1000 + 60, condition, common_prompt, policy_prompt, task_prompt, auth_path: join(control_dir, "fake-auth.json"), bridge_python: "/opt/homebrew/bin/python3", max_controller_turns: 5 };
  const path = join(control_dir, "config.json");
  writeFileSync(path, JSON.stringify(config));
  const auth = AuthStorage.inMemory({ "openai-codex": { type: "api_key", key: "fake-no-provider-call" } }, { usePrimeCliConfig: false });
  return { directory, config, path, auth };
}

test("native controller exposes symmetric tools, yields through kernel barrier and resumes same transcript", { timeout: 60000 }, async () => {
  await runSymmetricToolsFixture();
});

test("blinded supervisor role sees only review tools", { timeout: 60000 }, async () => {
  const f = fixture("P");
  const supervisorConfig = { ...f.config, role: "supervisor", team_id: "supervisor", session_id: `fixture-supervisor-${Date.now()}` };
  writeFileSync(f.path, JSON.stringify(supervisorConfig));
  const seenTools: string[][] = [];
  try {
    const bridge: HostBridge = async (action) => ({ status: action === "reserve_model" ? "RESERVED" : action === "finish" ? "CANDIDATE_SUBMITTED" : "SETTLED", records: [], events: [] });
    const stream: StreamFn = (_model, context) => { seenTools.push((context.tools ?? []).map((tool) => tool.name).sort()); return response([{ type: "text", text: "review complete" }]); };
    await runCampaign(f.path, { bridge, stream, auth: f.auth, kernelBarrier: async () => ({ status: "CLEAR" }) });
    assert.ok(seenTools.length > 0);
    for (const tools of seenTools) {
      assert.deepEqual(tools, ["finish", "ipython", "read_state"]);
    }
  } finally { rmSync(f.directory, { recursive: true, force: true }); rmSync(f.config.control_dir, { recursive: true, force: true }); }
});

async function runSymmetricToolsFixture() {
  const toolsPerCondition: string[][] = [];
  for (const condition of ["B", "P"] as const) {
    const f = fixture(condition);
    const actions: string[] = [];
    const requestIds: string[] = [];
    let calls = 0;
    let barrierCalls = 0;
    const bridge: HostBridge = async (action, args) => {
      actions.push(action);
      if (action === "reserve_model") return { status: "RESERVED" };
      if (action === "settle_model") return { status: "SETTLED" };
      if (action === "run_experiment") { assert.ok(barrierCalls > 0); requestIds.push(String(args.request_id)); return { status: "OBSERVED", evidence: "synthetic-observation-only" }; }
      return { status: action === "finish" ? "CANDIDATE_SUBMITTED" : "READY" };
    };
    const fake: StreamFn = (_model, context, options) => {
      assert.equal(options?.transport, "sse");
      if (calls++ === 0) {
        toolsPerCondition.push((context.tools ?? []).map((tool) => tool.name).sort());
        return response([{ type: "toolCall", id: "run-test", name: "run_experiment", arguments: { relative_source: "solution.py", hypothesis: "Synthetic mechanism" } }]);
      }
      return response([{ type: "toolCall", id: "finish-test", name: "finish", arguments: { conclusion: "Synthetic controller qualification only", claims: ["No scientific result"], limitations: ["No actual kernel was launched in this test"] } }]);
    };
    try {
      const summary = await runCampaign(f.path, { bridge, stream: fake, auth: f.auth, kernelBarrier: async () => { barrierCalls++; return { status: "CLEAR" }; } });
      assert.equal(summary.status, "CONCLUSION_SUBMITTED");
      assert.equal(summary.session_id, f.config.session_id);
      assert.equal(summary.turns, 2);
      assert.equal(requestIds.length, 1);
      assert.equal(actions.filter((action) => action === "reserve_model").length, 2);
      const transcript = readFileSync(String(summary.session_file), "utf8");
      assert.match(transcript, /synthetic-observation-only/);
      assert.match(transcript, /run_experiment/);
      const repeated = await runCampaign(f.path, { bridge, stream: fake, auth: f.auth, kernelBarrier: async () => ({ status: "CLEAR" }) });
      assert.equal(repeated.status, "CONCLUSION_SUBMITTED");
      assert.equal(calls, 2);
    } finally { rmSync(f.directory, { recursive: true, force: true }); rmSync(f.config.control_dir, { recursive: true, force: true }); }
  }
  assert.deepEqual(toolsPerCondition[0], toolsPerCondition[1]);
  assert.ok(toolsPerCondition[0].includes("ipython"));
}

test("model choice records handoff after kernel barrier and ends the session", { timeout: 30000 }, async () => {
  const f = fixture("B");
  const actions: string[] = [];
  try {
    const bridge: HostBridge = async (action) => { actions.push(action); return { status: action === "reserve_model" ? "RESERVED" : action === "settle_model" ? "SETTLED" : action === "choose_model" ? "MODEL_CHANGE_REQUESTED" : "READY" }; };
    const summary = await runCampaign(f.path, { bridge, auth: f.auth, kernelBarrier: async () => ({ status: "CLEAR" }), stream: () => response([{ type: "toolCall", id: "change", name: "choose_model", arguments: { model_id: "codex-terra", reason: "Synthetic alternative model" } }]) });
    assert.equal(summary.status, "MODEL_CHANGE_REQUESTED");
    assert.equal(actions.filter((action) => action === "choose_model").length, 1);
    assert.equal(actions.filter((action) => action === "reserve_model").length, 1);
  } finally { rmSync(f.directory, { recursive: true, force: true }); rmSync(f.config.control_dir, { recursive: true, force: true }); }
});

test("a second controller cannot own the same native session concurrently", { timeout: 30000 }, async () => {
  const f = fixture("B");
  let entered: (() => void) | undefined;
  let release: (() => void) | undefined;
  const ready = new Promise<void>((resolve) => { entered = resolve; });
  const gate = new Promise<void>((resolve) => { release = resolve; });
  const bridge: HostBridge = async (action) => ({ status: action === "reserve_model" ? "RESERVED" : action === "settle_model" ? "SETTLED" : action === "finish" ? "CANDIDATE_SUBMITTED" : "READY" });
  const fixtures = { bridge, auth: f.auth, kernelBarrier: async () => ({ status: "CLEAR" }), stream: async () => { entered?.(); await gate; return response([{ type: "toolCall", id: "finish-owner-test", name: "finish", arguments: { conclusion: "Synthetic ownership test", claims: [], limitations: [] } }]); } };
  const first = runCampaign(f.path, fixtures);
  try {
    await ready;
    await assert.rejects(runCampaign(f.path, fixtures), /CONTROLLER_SESSION_ALREADY_OWNED/);
    release?.();
    assert.equal((await first).status, "CONCLUSION_SUBMITTED");
  } finally { release?.(); await first; rmSync(f.directory, { recursive: true, force: true }); rmSync(f.config.control_dir, { recursive: true, force: true }); }
});
