import { AsyncLocalStorage } from "node:async_hooks";
import { createHash, randomUUID } from "node:crypto";
import { mkdirSync, readFileSync, renameSync, rmdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import type { StreamFn } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-agent-core/dist/types.js";
import type {
	Api,
	AssistantMessage,
	Context,
	Model,
	SimpleStreamOptions,
	Usage,
} from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/types.js";
import { streamOpenAICompletions } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/providers/openai-completions.js";
import { AssistantMessageEventStream } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/utils/event-stream.js";

const SCHEMA = "argo-study-model-meter/v1";
const MODEL_ID = "openai/gpt-5.6-sol";
const ENDPOINT = "https://openrouter.ai/api/v1/chat/completions";
const OUTPUT_LIMIT = 8000;
const INPUT_LIMIT = 64000;
const USD_PER_RESERVED_TOKEN = 30 / 1_000_000;
const MAX_RESPONSE_BYTES = 8 * 1024 * 1024;
const MAX_FRAME_BYTES = 1024 * 1024;

export interface SetupAllocation {
	knownTokens: number;
	unknownTokenReserve: number;
	roundingTokenReserve: number;
	knownUsd: number;
	unknownUsdReserve: number;
	note: string;
}

export interface ProviderUsage {
	input: number;
	output: number;
	cacheRead: number;
	cacheWrite: number;
	totalTokens: number;
	reasoningTokens: number | null;
	actualUsd: number;
	inputUsd: number | null;
	outputUsd: number | null;
}

interface RequestRecord {
	id: string;
	episodePath: string;
	state: "reserved" | "complete" | "unknown";
	startedAt: string;
	finishedAt?: string;
	requestSha256: string;
	inputUpperBound: number;
	reservedTokens: number;
	reservedUsd: number;
	responseId?: string;
	resolvedModel?: string;
	resolvedProvider?: string;
	httpStatus?: number;
	usage?: ProviderUsage;
	error?: string;
}

interface FamilyLedger {
	schema: typeof SCHEMA;
	familyLimit: number;
	usdCeiling: number;
	setup: SetupAllocation;
	requests: RequestRecord[];
	blockedReason?: string;
}

export interface MeterSnapshot {
	episodeLimit: number;
	episodeChargedTokens: number;
	familyLimit: number;
	familyChargedTokens: number;
	usdCeiling: number;
	familyChargedUsd: number;
	actualRequestUsd: number;
	setup: SetupAllocation;
	blockedReason: string | null;
	requests: RequestRecord[];
}

export interface MeterOptions {
	model: Model<Api>;
	ledgerPath: string;
	episodeLimit: number;
	familyLedgerPath: string;
	familyLimit: number;
	usdCeiling: number;
	timeoutMs: number;
	providerTag: "azure";
	/** A trusted host callback; no key is persisted. Default reads the existing OpenRouter key. */
	getApiKey?: () => string | Promise<string>;
	/** Fake HTTP transport for focused tests. Production omits this. */
	fetch?: typeof globalThis.fetch;
}

class MeterError extends Error {
	readonly code: string;

	constructor(code: string) {
		super(code);
		this.code = code;
	}
}

function object(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function amount(value: unknown, code: string): number {
	if (typeof value !== "number" || !Number.isFinite(value) || value < 0) throw new MeterError(code);
	return value;
}

function tokens(value: unknown): number {
	const result = amount(value, "INVALID_USAGE");
	if (!Number.isSafeInteger(result)) throw new MeterError("INVALID_USAGE");
	return result;
}

function optionalAmount(value: unknown): number | null {
	return value === undefined ? null : amount(value, "INVALID_USAGE");
}

export function normalizeProviderUsage(value: unknown): ProviderUsage {
	if (!object(value)) throw new MeterError("MISSING_PROVIDER_USAGE");
	const prompt = tokens(value.prompt_tokens);
	const output = tokens(value.completion_tokens);
	const total = tokens(value.total_tokens);
	const details = object(value.prompt_tokens_details) ? value.prompt_tokens_details : {};
	const completion = object(value.completion_tokens_details) ? value.completion_tokens_details : {};
	const costs = object(value.cost_details) ? value.cost_details : {};
	const cacheRead = tokens(details.cached_tokens ?? 0);
	const cacheWrite = tokens(details.cache_write_tokens ?? 0);
	const reasoning = completion.reasoning_tokens === undefined ? null : tokens(completion.reasoning_tokens);
	if (cacheRead + cacheWrite > prompt || total !== prompt + output || (reasoning !== null && reasoning > output)) {
		throw new MeterError("INCONSISTENT_PROVIDER_USAGE");
	}
	return {
		input: prompt - cacheRead - cacheWrite,
		output,
		cacheRead,
		cacheWrite,
		totalTokens: total,
		reasoningTokens: reasoning,
		actualUsd: amount(value.cost, "MISSING_ACTUAL_COST"),
		inputUsd: optionalAmount(costs.upstream_inference_prompt_cost),
		outputUsd: optionalAmount(costs.upstream_inference_completions_cost),
	};
}

/** Text-only byte-token bound, conditional on the documented framing allowance. */
export function inputUpperBound(payload: unknown): number {
	if (!object(payload) || !Array.isArray(payload.messages)) throw new MeterError("INVALID_REQUEST");
	for (const message of payload.messages) {
		if (!object(message)) throw new MeterError("INVALID_REQUEST");
		const content = message.content;
		if (Array.isArray(content) && content.some((part) => !object(part) || part.type !== "text" || typeof part.text !== "string")) {
			throw new MeterError("NON_TEXT_INPUT_UNSUPPORTED");
		}
		if (content !== undefined && content !== null && typeof content !== "string" && !Array.isArray(content)) {
			throw new MeterError("INVALID_REQUEST");
		}
	}
	const toolCount = Array.isArray(payload.tools) ? payload.tools.length : 0;
	return Buffer.byteLength(JSON.stringify(payload), "utf8") + 4096 + 256 * payload.messages.length + 1024 * toolCount;
}

function atomicWrite(path: string, value: unknown): void {
	mkdirSync(dirname(path), { recursive: true });
	const temporary = `${path}.${randomUUID()}.tmp`;
	writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600, flag: "wx" });
	renameSync(temporary, path);
}

function validateSetup(value: unknown): SetupAllocation {
	if (!object(value) || typeof value.note !== "string") throw new MeterError("INVALID_SETUP_SEED");
	const result: SetupAllocation = {
		knownTokens: amount(value.knownTokens, "INVALID_SETUP_SEED"),
		unknownTokenReserve: amount(value.unknownTokenReserve, "INVALID_SETUP_SEED"),
		roundingTokenReserve: amount(value.roundingTokenReserve, "INVALID_SETUP_SEED"),
		knownUsd: amount(value.knownUsd, "INVALID_SETUP_SEED"),
		unknownUsdReserve: amount(value.unknownUsdReserve, "INVALID_SETUP_SEED"),
		note: value.note,
	};
	if (!Number.isSafeInteger(result.knownTokens + result.unknownTokenReserve + result.roundingTokenReserve)) {
		throw new MeterError("NONINTEGER_SETUP_TOTAL");
	}
	return result;
}

export function initializeFamilyLedger(options: {
	familyLedgerPath: string;
	familyLimit: number;
	usdCeiling: number;
	setup: SetupAllocation;
}): void {
	const ledger: FamilyLedger = {
		schema: SCHEMA,
		familyLimit: tokens(options.familyLimit),
		usdCeiling: amount(options.usdCeiling, "INVALID_USD_CEILING"),
		setup: validateSetup(options.setup),
		requests: [],
	};
	if (setupTokens(ledger.setup) > ledger.familyLimit || setupUsd(ledger.setup) > ledger.usdCeiling) {
		throw new MeterError("SETUP_EXCEEDS_CAP");
	}
	const path = resolve(options.familyLedgerPath);
	mkdirSync(dirname(path), { recursive: true });
	writeFileSync(path, `${JSON.stringify(ledger, null, 2)}\n`, { mode: 0o600, flag: "wx" });
}

function setupTokens(setup: SetupAllocation): number {
	return setup.knownTokens + setup.unknownTokenReserve + setup.roundingTokenReserve;
}

function setupUsd(setup: SetupAllocation): number {
	return setup.knownUsd + setup.unknownUsdReserve;
}

function chargeTokens(request: RequestRecord): number {
	return request.state === "complete" && request.usage ? request.usage.totalTokens : request.reservedTokens;
}

function chargeUsd(request: RequestRecord): number {
	return request.state === "complete" && request.usage ? request.usage.actualUsd : request.reservedUsd;
}

function readLedger(path: string): FamilyLedger {
	const raw: unknown = JSON.parse(readFileSync(path, "utf8"));
	if (!object(raw) || raw.schema !== SCHEMA || !Array.isArray(raw.requests)) throw new MeterError("INVALID_FAMILY_LEDGER");
	tokens(raw.familyLimit);
	amount(raw.usdCeiling, "INVALID_FAMILY_LEDGER");
	validateSetup(raw.setup);
	for (const entry of raw.requests) {
		if (!object(entry) || typeof entry.id !== "string" || typeof entry.episodePath !== "string" || !["reserved", "complete", "unknown"].includes(String(entry.state))) {
			throw new MeterError("INVALID_FAMILY_LEDGER");
		}
		tokens(entry.reservedTokens);
		tokens(entry.inputUpperBound);
		amount(entry.reservedUsd, "INVALID_FAMILY_LEDGER");
		if (entry.state === "complete") {
			if (!object(entry.usage)) throw new MeterError("INVALID_FAMILY_LEDGER");
			const usage = entry.usage;
			const total = tokens(usage.input) + tokens(usage.output) + tokens(usage.cacheRead) + tokens(usage.cacheWrite);
			if (total !== tokens(usage.totalTokens)) throw new MeterError("INVALID_FAMILY_LEDGER");
			amount(usage.actualUsd, "INVALID_FAMILY_LEDGER");
		}
	}
	if (new Set(raw.requests.map((entry: Record<string, unknown>) => entry.id)).size !== raw.requests.length) throw new MeterError("DUPLICATE_REQUEST_ID");
	return raw as unknown as FamilyLedger;
}

interface Capture {
	id: string;
	fetchCount: number;
	sent: boolean;
	record?: RequestRecord;
	usage?: ProviderUsage;
	responseId?: string;
	resolvedModel?: string;
	resolvedProvider?: string;
	httpStatus?: number;
	preflightError?: string;
	fetchOverride?: typeof globalThis.fetch;
	reserve(payload: unknown): void;
}

const fetchContext = new AsyncLocalStorage<Capture>();
const liveRequests = new Set<string>();
let installedFetch: typeof globalThis.fetch | undefined;

function observeJson(capture: Capture, value: unknown): void {
	if (!object(value)) return;
	if (typeof value.id === "string") capture.responseId = value.id;
	if (typeof value.model === "string") capture.resolvedModel = value.model;
	if (typeof value.provider === "string") capture.resolvedProvider = value.provider;
	if (value.usage !== undefined && value.usage !== null) {
		const usage = normalizeProviderUsage(value.usage);
		if (capture.usage && JSON.stringify(capture.usage) !== JSON.stringify(usage)) throw new MeterError("CONFLICTING_USAGE_RECEIPTS");
		capture.usage = usage;
	}
}

function observeResponse(response: Response, capture: Capture): Response {
	capture.httpStatus = response.status;
	if (!response.body) return response;
	const decoder = new TextDecoder();
	const isSse = response.headers.get("content-type")?.includes("text/event-stream") === true;
	let buffered = "";
	let bytes = 0;
	const parse = (line: string): void => {
		const value = line.trim();
		if (value.startsWith("data:") && value.slice(5).trim() !== "[DONE]") {
			observeJson(capture, JSON.parse(value.slice(5).trim()));
		}
	};
	const body = response.body.pipeThrough(new TransformStream<Uint8Array, Uint8Array>({
		transform(chunk, controller) {
			bytes += chunk.byteLength;
			if (bytes > MAX_RESPONSE_BYTES) throw new MeterError("RESPONSE_BYTE_LIMIT");
			buffered += decoder.decode(chunk, { stream: true });
			if (isSse) {
				let newline = buffered.indexOf("\n");
				while (newline >= 0) {
					parse(buffered.slice(0, newline));
					buffered = buffered.slice(newline + 1);
					newline = buffered.indexOf("\n");
				}
			}
			if (Buffer.byteLength(buffered) > MAX_FRAME_BYTES) throw new MeterError("RESPONSE_FRAME_LIMIT");
			controller.enqueue(chunk);
		},
		flush() {
			buffered += decoder.decode();
			if (isSse) {
				if (buffered.trim()) parse(buffered);
			} else if (buffered.trim()) {
				observeJson(capture, JSON.parse(buffered));
			}
		},
	}));
	return new Response(body, { status: response.status, statusText: response.statusText, headers: response.headers });
}

function installFetchCapture(): void {
	if (installedFetch) {
		if (globalThis.fetch !== installedFetch) throw new MeterError("FETCH_INTERCEPTOR_REPLACED");
		return;
	}
	const originalFetch = globalThis.fetch;
	installedFetch = async (input, init) => {
		const capture = fetchContext.getStore();
		if (!capture) return originalFetch(input, init);
		if (++capture.fetchCount !== 1) throw new MeterError("RETRY_FORBIDDEN");
		const request = new Request(input, init);
		if (request.url !== ENDPOINT || request.method !== "POST") throw new MeterError("WRONG_ENDPOINT");
		const payload: unknown = JSON.parse(await request.clone().text());
		try { capture.reserve(payload); } catch (error) {
			capture.preflightError = error instanceof MeterError ? error.code : "RESERVATION_FAILED";
			throw error;
		}
		capture.sent = true;
		return observeResponse(await (capture.fetchOverride ?? originalFetch)(new Request(request, { redirect: "error" })), capture);
	};
	globalThis.fetch = installedFetch;
}

function defaultApiKey(): string {
	const auth: unknown = JSON.parse(readFileSync(join(homedir(), ".prime/agent/auth.json"), "utf8"));
	const credential = object(auth) ? auth.openrouter : undefined;
	if (!object(credential) || credential.type !== "api_key" || typeof credential.key !== "string" || !credential.key || /^[!$]/.test(credential.key)) {
		throw new MeterError("EXISTING_OPENROUTER_LITERAL_KEY_REQUIRED");
	}
	return credential.key;
}

function nativeUsage(usage: ProviderUsage): Usage {
	return {
		input: usage.input,
		output: usage.output,
		cacheRead: usage.cacheRead,
		cacheWrite: usage.cacheWrite,
		totalTokens: usage.totalTokens,
		cost: { input: usage.inputUsd ?? 0, output: usage.outputUsd ?? 0, cacheRead: 0, cacheWrite: 0, total: usage.actualUsd },
	};
}

function errorMessage(model: Model<Api>, code: string, usage?: ProviderUsage): AssistantMessage {
	return {
		role: "assistant", content: [], api: model.api, provider: model.provider, model: model.id,
		stopReason: "error", errorMessage: code, timestamp: Date.now(),
		usage: usage ? nativeUsage(usage) : { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } },
	};
}

export function createMeteredStream(options: MeterOptions): {
	streamFn: StreamFn;
	snapshot(): MeterSnapshot;
	reconcile(): MeterSnapshot;
} {
	if (options.model.id !== MODEL_ID || options.model.provider !== "openrouter" || options.model.api !== "openai-completions" || options.model.baseUrl.replace(/\/$/, "") !== "https://openrouter.ai/api/v1") {
		throw new MeterError("WRONG_MODEL_BINDING");
	}
	if (![80000, 120000].includes(options.episodeLimit) || options.timeoutMs !== 60000 || options.providerTag !== "azure") throw new MeterError("WRONG_FROZEN_LIMITS");
	const episodePath = resolve(options.ledgerPath);
	const familyPath = resolve(options.familyLedgerPath);
	if (episodePath === familyPath) throw new MeterError("LEDGER_PATH_COLLISION");
	installFetchCapture();

	function load(): FamilyLedger {
		const family = readLedger(familyPath);
		if (family.familyLimit !== options.familyLimit || family.usdCeiling !== options.usdCeiling) throw new MeterError("FAMILY_LIMIT_MISMATCH");
		return family;
	}
	function view(family: FamilyLedger): MeterSnapshot {
		const requests = family.requests.filter((request) => request.episodePath === episodePath);
		return {
			episodeLimit: options.episodeLimit,
			episodeChargedTokens: requests.reduce((sum, request) => sum + chargeTokens(request), 0),
			familyLimit: family.familyLimit,
			familyChargedTokens: setupTokens(family.setup) + family.requests.reduce((sum, request) => sum + chargeTokens(request), 0),
			usdCeiling: family.usdCeiling,
			familyChargedUsd: setupUsd(family.setup) + family.requests.reduce((sum, request) => sum + chargeUsd(request), 0),
			actualRequestUsd: family.requests.reduce((sum, request) => sum + (request.usage?.actualUsd ?? 0), 0),
			setup: family.setup,
			blockedReason: family.blockedReason ?? null,
			requests,
		};
	}
	function mutate(change: (family: FamilyLedger) => void): MeterSnapshot {
		const lock = `${familyPath}.lock`;
		try { mkdirSync(lock); } catch { throw new MeterError("FAMILY_LEDGER_LOCKED"); }
		try {
			const family = load();
			change(family);
			atomicWrite(familyPath, family);
			const snapshot = view(family);
			atomicWrite(episodePath, { schema: SCHEMA, familyLedgerPath: familyPath, ...snapshot });
			return snapshot;
		} finally { rmdirSync(lock); }
	}
	function reconcile(): MeterSnapshot {
		return mutate((family) => {
			for (const request of family.requests) {
				if (request.state === "reserved" && !liveRequests.has(request.id)) {
					request.state = "unknown";
					request.error = "UNRECONCILED_PRIOR_REQUEST";
					family.blockedReason = "UNKNOWN_REQUEST";
				}
			}
		});
	}
	load();

	const streamFn: StreamFn = (model, context, requestOptions) => {
		const output = new AssistantMessageEventStream();
		void execute(model, context, requestOptions, output);
		return output;
	};
	async function execute(model: Model<Api>, context: Context, requestOptions: SimpleStreamOptions | undefined, output: AssistantMessageEventStream): Promise<void> {
		const abort = new AbortController();
		const timeout = setTimeout(() => abort.abort(), options.timeoutMs);
		const signal = requestOptions?.signal ? AbortSignal.any([requestOptions.signal, abort.signal]) : abort.signal;
		const capture: Capture = {
			id: randomUUID(), fetchCount: 0, sent: false, fetchOverride: options.fetch,
			reserve(payload) {
				if (!object(payload) || payload.model !== MODEL_ID || payload.max_completion_tokens !== OUTPUT_LIMIT || payload.stream !== true || !object(payload.provider)) throw new MeterError("REQUEST_CONTRACT_MISMATCH");
				const bound = inputUpperBound(payload);
				if (bound > INPUT_LIMIT) throw new MeterError("ACTIVE_INPUT_CAP");
				const reservedTokens = bound + OUTPUT_LIMIT;
				const reservedUsd = reservedTokens * USD_PER_RESERVED_TOKEN;
				const record: RequestRecord = { id: capture.id, episodePath, state: "reserved", startedAt: new Date().toISOString(), requestSha256: createHash("sha256").update(JSON.stringify(payload)).digest("hex"), inputUpperBound: bound, reservedTokens, reservedUsd };
				liveRequests.add(capture.id);
				try {
					mutate((family) => {
						if (family.blockedReason) throw new MeterError("FAMILY_BLOCKED_UNKNOWN");
						if (family.requests.some((entry) => entry.state === "unknown" || (entry.state === "reserved" && !liveRequests.has(entry.id)))) throw new MeterError("UNRECONCILED_PRIOR_REQUEST");
						const before = view(family);
						if (before.episodeChargedTokens + reservedTokens > options.episodeLimit) throw new MeterError("EPISODE_TOKEN_CAP");
						if (before.familyChargedTokens + reservedTokens > family.familyLimit) throw new MeterError("FAMILY_TOKEN_CAP");
						if (before.familyChargedUsd + reservedUsd > family.usdCeiling) throw new MeterError("FAMILY_USD_CAP");
						family.requests.push(record);
					});
					capture.record = record;
				} catch (error) { liveRequests.delete(capture.id); throw error; }
			},
		};
		try {
			if (globalThis.fetch !== installedFetch) throw new MeterError("FETCH_INTERCEPTOR_REPLACED");
			if (model.id !== options.model.id || model.provider !== options.model.provider || model.api !== options.model.api || model.baseUrl !== options.model.baseUrl || requestOptions?.reasoning !== "high") throw new MeterError("MODEL_OR_REASONING_MISMATCH");
			const apiKey = requestOptions.apiKey ?? await (options.getApiKey ?? defaultApiKey)();
			if (!apiKey) throw new MeterError("MISSING_API_KEY");
			signal.throwIfAborted();
			const native = fetchContext.run(capture, () => streamOpenAICompletions(options.model as Model<"openai-completions">, context, {
				apiKey, signal, maxTokens: OUTPUT_LIMIT, maxRetries: 0, timeoutMs: options.timeoutMs, reasoningEffort: "high",
				sessionId: requestOptions.sessionId,
				onResponse: requestOptions.onResponse,
				onPayload: async (payload) => {
					const changed = requestOptions.onPayload ? await requestOptions.onPayload(payload, model) : payload;
					const body = changed === undefined ? payload : changed;
					if (!object(body) || body.plugins !== undefined || body.models !== undefined || body.route !== undefined || (body.n !== undefined && body.n !== 1) || (body.service_tier !== undefined && body.service_tier !== "default")) throw new MeterError("UNSUPPORTED_REQUEST_ROUTE");
					const fixedBody = { ...body };
					delete fixedBody.max_tokens;
					delete fixedBody.reasoning_effort;
					return { ...fixedBody, model: MODEL_ID, max_completion_tokens: OUTPUT_LIMIT, reasoning: { effort: "high" }, provider: { only: ["azure"], order: ["azure"], ignore: ["azure/us", "azure/eu"], allow_fallbacks: false, require_parameters: true, max_price: { prompt: 5, completion: 30 } } };
				},
			}));
			let final: AssistantMessage | undefined;
			for await (const event of native) {
				if (event.type === "done") final = event.message;
				else if (event.type === "error") final = event.error;
				else output.push(event);
			}
			if (!capture.record || !capture.sent) throw new MeterError(capture.preflightError ?? "NO_ADMITTED_REQUEST");
			if (!capture.usage) throw new MeterError("UNKNOWN_PROVIDER_USAGE_OR_COST");
			let violation: string | undefined;
			if (capture.resolvedModel !== MODEL_ID || capture.resolvedProvider?.toLowerCase() !== "azure") violation = "RESOLVED_ROUTE_MISMATCH";
			if (capture.usage.input + capture.usage.cacheRead + capture.usage.cacheWrite > capture.record.inputUpperBound) violation = "INPUT_BOUND_VIOLATION";
			if (capture.usage.output > OUTPUT_LIMIT || capture.usage.totalTokens > capture.record.reservedTokens || capture.usage.actualUsd > capture.record.reservedUsd + 1e-12) violation = "PROVIDER_CAP_VIOLATION";
			mutate((family) => {
				const record = family.requests.find((entry) => entry.id === capture.id);
				if (!record) throw new MeterError("LOST_RESERVATION");
				Object.assign(record, { state: "complete", finishedAt: new Date().toISOString(), usage: capture.usage, responseId: capture.responseId, resolvedModel: capture.resolvedModel, resolvedProvider: capture.resolvedProvider, httpStatus: capture.httpStatus, error: violation });
				if (violation) family.blockedReason = violation;
			});
			if (violation) throw new MeterError(violation);
			if (!final) throw new MeterError("MISSING_TERMINAL_MESSAGE");
			final.usage = nativeUsage(capture.usage);
			if (final.stopReason === "error" || final.stopReason === "aborted") output.push({ type: "error", reason: final.stopReason, error: final });
			else output.push({ type: "done", reason: final.stopReason, message: final });
		} catch (error) {
			const code = error instanceof MeterError ? error.code : "METER_REQUEST_FAILED";
			if (capture.sent || capture.record) {
				try {
					mutate((family) => {
						const record = family.requests.find((entry) => entry.id === capture.id);
						if (record?.state === "reserved") {
							Object.assign(record, { state: "unknown", finishedAt: new Date().toISOString(), error: code, httpStatus: capture.httpStatus });
							family.blockedReason = "UNKNOWN_REQUEST";
						}
					});
				} catch { /* The durable reservation still prevents fresh-process admission. */ }
			}
			output.push({ type: "error", reason: "error", error: errorMessage(model, code, capture.usage) });
		} finally {
			clearTimeout(timeout);
			liveRequests.delete(capture.id);
			output.end();
		}
	}
	return { streamFn, snapshot: () => view(load()), reconcile };
}
