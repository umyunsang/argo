import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import type { Context } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/types.js";
import { createMeteredStream, initializeFamilyLedger, normalizeProviderUsage, type SetupAllocation } from "./model_meter.js";

const model = getModel("openrouter", "openai/gpt-5.6-sol");
const emptySetup: SetupAllocation = { knownTokens: 0, unknownTokenReserve: 0, roundingTokenReserve: 0, knownUsd: 0, unknownUsdReserve: 0, note: "synthetic only" };
const context: Context = { systemPrompt: "test", messages: [{ role: "user", content: "OK", timestamp: 1 }] };

function sse(options: { prompt?: number; output?: number; cached?: number; cacheWrite?: number; cost?: number; withUsage?: boolean; provider?: string; resolvedModel?: string } = {}): Response {
	const prompt = options.prompt ?? 100;
	const output = options.output ?? 5;
	const usage = { prompt_tokens: prompt, completion_tokens: output, total_tokens: prompt + output, prompt_tokens_details: { cached_tokens: options.cached ?? 0, cache_write_tokens: options.cacheWrite ?? 0 }, completion_tokens_details: { reasoning_tokens: 2 }, cost: options.cost ?? 0.00255, cost_details: { upstream_inference_prompt_cost: 0.000105, upstream_inference_completions_cost: 0.00015 } };
	const first = { id: "fake-request", model: options.resolvedModel ?? model.id, provider: options.provider ?? "Azure", choices: [{ index: 0, delta: { role: "assistant", content: "OK" }, finish_reason: null }] };
	const last = { id: "fake-request", model: options.resolvedModel ?? model.id, provider: options.provider ?? "Azure", choices: [{ index: 0, delta: {}, finish_reason: "stop" }], ...(options.withUsage === false ? {} : { usage }) };
	return new Response(`data: ${JSON.stringify(first)}\n\ndata: ${JSON.stringify(last)}\n\ndata: [DONE]\n\n`, { headers: { "content-type": "text/event-stream" } });
}

function fixture(fetch: typeof globalThis.fetch, seed = emptySetup, familyLimit = 1_500_000, episodeLimit = 120000) {
	const directory = mkdtempSync(join(tmpdir(), "argo-model-meter-"));
	const familyLedgerPath = join(directory, "family.json");
	initializeFamilyLedger({ familyLedgerPath, familyLimit, usdCeiling: 45, setup: seed });
	const meter = createMeteredStream({ model, ledgerPath: join(directory, "episode.json"), episodeLimit, familyLedgerPath, familyLimit, usdCeiling: 45, timeoutMs: 60000, providerTag: "azure", fetch, getApiKey: () => "fake-no-network-key" });
	return { meter, directory, familyLedgerPath, close: () => rmSync(directory, { recursive: true, force: true }) };
}

test("provider totals subtract cache reads and writes once; reasoning is already output", () => {
	const usage = normalizeProviderUsage({ prompt_tokens: 100, completion_tokens: 10, total_tokens: 110, prompt_tokens_details: { cached_tokens: 40, cache_write_tokens: 20 }, completion_tokens_details: { reasoning_tokens: 7 }, cost: 0.05 });
	assert.equal(usage.input, 40);
	assert.equal(usage.output, 10);
	assert.equal(usage.totalTokens, usage.input + usage.output + usage.cacheRead + usage.cacheWrite);
	assert.equal(usage.reasoningTokens, 7);
	assert.throws(() => normalizeProviderUsage({ prompt_tokens: 10, completion_tokens: 1, total_tokens: 11, prompt_tokens_details: { cached_tokens: 11 }, cost: 0.1 }), /INCONSISTENT/);
	assert.throws(() => normalizeProviderUsage({ prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 }), /MISSING_ACTUAL_COST/);
});

test("frozen route, high, output8000, actual billed cost replace SDK estimates", async () => {
	let sends = 0;
	const f = fixture(async (input, init) => {
		sends++;
		const request = new Request(input, init);
		const body = await request.json() as Record<string, unknown>;
		assert.equal(request.url, "https://openrouter.ai/api/v1/chat/completions");
		assert.equal(body.model, model.id);
		assert.equal(body.max_completion_tokens, 8000);
		assert.deepEqual(body.reasoning, { effort: "high" });
		assert.deepEqual(body.provider, { only: ["azure"], order: ["azure"], ignore: ["azure/us", "azure/eu"], allow_fallbacks: false, require_parameters: true, max_price: { prompt: 5, completion: 30 } });
		return sse({ prompt: 100, output: 5, cached: 40, cacheWrite: 20, cost: 0.00255 });
	});
	try {
		const result = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(result.stopReason, "stop");
		assert.equal(result.usage.totalTokens, 105);
		assert.equal(result.usage.input, 40);
		assert.equal(result.usage.cost.total, 0.00255);
		assert.equal(f.meter.snapshot().familyChargedTokens, 105);
		assert.equal(f.meter.snapshot().actualRequestUsd, 0.00255);
		assert.equal(sends, 1);
		assert.equal(f.meter.reconcile().blockedReason, null);
		assert.equal(readFileSync(f.familyLedgerPath, "utf8").includes("fake-no-network-key"), false);
	} finally { f.close(); }
});

test("wrong reasoning and input over64k cannot reach transport", async () => {
	let sends = 0;
	const f = fixture(async () => { sends++; return sse(); });
	try {
		const wrong = await (await f.meter.streamFn(model, context, { reasoning: "medium" })).result();
		assert.equal(wrong.errorMessage, "MODEL_OR_REASONING_MISMATCH");
		const tooLarge: Context = { messages: [{ role: "user", content: "x".repeat(65000), timestamp: 1 }] };
		const large = await (await f.meter.streamFn(model, tooLarge, { reasoning: "high" })).result();
		assert.equal(large.errorMessage, "ACTIVE_INPUT_CAP");
		assert.equal(sends, 0);
		assert.equal(f.meter.snapshot().requests.length, 0);
	} finally { f.close(); }
});

for (const episodeLimit of [80000, 120000]) {
test(`concurrent inline children reserve shared ${episodeLimit} episode budget before either completes`, async () => {
	let release: (() => void) | undefined;
	let entered: (() => void) | undefined;
	const inTransport = new Promise<void>((resolve) => { entered = resolve; });
	const gate = new Promise<void>((resolve) => { release = resolve; });
	let sends = 0;
	const f = fixture(async () => { sends++; entered?.(); await gate; return sse(); }, emptySetup, 1_500_000, episodeLimit);
	try {
		assert.equal(f.meter.snapshot().episodeLimit, episodeLimit);
		const large: Context = { messages: [{ role: "user", content: "x".repeat(55000), timestamp: 1 }] };
		const first = f.meter.streamFn(model, large, { reasoning: "high" });
		await inTransport;
		const second = await (await f.meter.streamFn(model, large, { reasoning: "high" })).result();
		assert.equal(second.errorMessage, "EPISODE_TOKEN_CAP");
		assert.equal(sends, 1);
		assert.ok(f.meter.snapshot().episodeChargedTokens > 60000);
		release?.();
		assert.equal((await (await first).result()).stopReason, "stop");
		assert.equal(f.meter.snapshot().episodeChargedTokens, 105);
	} finally { release?.(); f.close(); }
});
}

test("missing usage blocks new requests and retains conservative reservation", async () => {
	let sends = 0;
	const f = fixture(async () => { sends++; return sse({ withUsage: false }); });
	try {
		const first = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(first.errorMessage, "UNKNOWN_PROVIDER_USAGE_OR_COST");
		const before = f.meter.snapshot();
		assert.equal(before.blockedReason, "UNKNOWN_REQUEST");
		assert.ok(before.familyChargedTokens >= 8000);
		assert.equal(before.actualRequestUsd, 0);
		const second = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(second.stopReason, "error");
		assert.equal(sends, 1);
		assert.equal(f.meter.snapshot().familyChargedTokens, before.familyChargedTokens);
	} finally { f.close(); }
});

test("failed HTTP call is never retried and its absent usage is unknown", async () => {
	let sends = 0;
	const f = fixture(async () => { sends++; return new Response('{"error":{"message":"synthetic failure"}}', { status: 503, headers: { "content-type": "application/json" } }); });
	try {
		const result = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(result.stopReason, "error");
		assert.equal(sends, 1);
		assert.equal(f.meter.snapshot().blockedReason, "UNKNOWN_REQUEST");
	} finally { f.close(); }
});

test("actual output over cap is retained, blocks family, and suppresses tool execution", async () => {
	const f = fixture(async () => sse({ output: 8001, cost: 0.241 }));
	try {
		const result = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(result.errorMessage, "PROVIDER_CAP_VIOLATION");
		assert.deepEqual(result.content, []);
		assert.equal(f.meter.snapshot().requests[0].usage?.output, 8001);
		assert.equal(f.meter.snapshot().blockedReason, "PROVIDER_CAP_VIOLATION");
	} finally { f.close(); }
});

test("root setup seed preserves equal1130683 remaining and actual versus reserved USD", () => {
	const setup: SetupAllocation = { knownTokens: 273316.5, unknownTokenReserve: 96000, roundingTokenReserve: 0.5, knownUsd: 0.0001275, unknownUsdReserve: 11.0793825, note: "half shared setup; reserve is not invoiced cost" };
	const f = fixture(async () => sse(), setup);
	try {
		const snapshot = f.meter.snapshot();
		assert.equal(snapshot.familyLimit - snapshot.familyChargedTokens, 1130683);
		assert.ok(Math.abs(snapshot.familyChargedUsd - 11.07951) < 1e-10);
		assert.equal(snapshot.actualRequestUsd, 0);
		assert.equal(snapshot.setup.knownUsd, 0.0001275);
	} finally { f.close(); }
});

test("orphaned durable reservation reconciles to unknown, never refunded", async () => {
	const f = fixture(async () => sse());
	try {
		const raw = JSON.parse(readFileSync(f.familyLedgerPath, "utf8"));
		raw.requests.push({ id: "orphan", episodePath: join(f.directory, "episode.json"), state: "reserved", startedAt: "2026-09-09", requestSha256: "0".repeat(64), inputUpperBound: 5000, reservedTokens: 13000, reservedUsd: 0.39 });
		writeFileSync(f.familyLedgerPath, JSON.stringify(raw));
		const snapshot = f.meter.reconcile();
		assert.equal(snapshot.blockedReason, "UNKNOWN_REQUEST");
		assert.equal(snapshot.familyChargedTokens, 13000);
		assert.equal(snapshot.requests[0].state, "unknown");
	} finally { f.close(); }
});

test("two meter instances share family reservations across different episodes", async () => {
	let release: (() => void) | undefined;
	let entered: (() => void) | undefined;
	const inTransport = new Promise<void>((resolve) => { entered = resolve; });
	const gate = new Promise<void>((resolve) => { release = resolve; });
	let sends = 0;
	const fakeFetch: typeof globalThis.fetch = async () => { sends++; entered?.(); await gate; return sse(); };
	const f = fixture(fakeFetch, emptySetup, 20000);
	const secondMeter = createMeteredStream({ model, ledgerPath: join(f.directory, "episode-two.json"), episodeLimit: 120000, familyLedgerPath: f.familyLedgerPath, familyLimit: 20000, usdCeiling: 45, timeoutMs: 60000, providerTag: "azure", fetch: fakeFetch, getApiKey: () => "fake" });
	try {
		const first = f.meter.streamFn(model, context, { reasoning: "high" });
		await inTransport;
		const second = await (await secondMeter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(second.errorMessage, "FAMILY_TOKEN_CAP");
		assert.equal(sends, 1);
		assert.equal(secondMeter.snapshot().episodeChargedTokens, 0);
		assert.ok(secondMeter.snapshot().familyChargedTokens > 12000);
		release?.();
		await (await first).result();
		assert.equal(secondMeter.snapshot().familyChargedTokens, 105);
	} finally { release?.(); f.close(); }
});

test("USD reserve can reject before sending even with available tokens", async () => {
	let sends = 0;
	const f = fixture(async () => { sends++; return sse(); }, { ...emptySetup, knownUsd: 44.9 });
	try {
		const result = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(result.errorMessage, "FAMILY_USD_CAP");
		assert.equal(sends, 0);
		assert.equal(f.meter.snapshot().familyChargedUsd, 44.9);
	} finally { f.close(); }
});

test("provider prompt beyond explicit framing bound is recorded and stops family", async () => {
	const f = fixture(async () => sse({ prompt: 50000 }));
	try {
		const result = await (await f.meter.streamFn(model, context, { reasoning: "high" })).result();
		assert.equal(result.errorMessage, "PROVIDER_CAP_VIOLATION");
		assert.equal(f.meter.snapshot().blockedReason, "PROVIDER_CAP_VIOLATION");
		assert.equal(f.meter.snapshot().requests[0].usage?.input, 50000);
	} finally { f.close(); }
});

test("malformed completed accounting cannot turn family totals into NaN or negatives", () => {
	const f = fixture(async () => sse());
	try {
		const raw = JSON.parse(readFileSync(f.familyLedgerPath, "utf8"));
		raw.requests.push({ id: "invalid", episodePath: join(f.directory, "episode.json"), state: "complete", inputUpperBound: 1, reservedTokens: 8001, reservedUsd: 0.3, usage: { input: -1, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: -1, actualUsd: 0 } });
		writeFileSync(f.familyLedgerPath, JSON.stringify(raw));
		assert.throws(() => f.meter.snapshot(), /INVALID_USAGE/);
	} finally { f.close(); }
});
