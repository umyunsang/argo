import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import {
	AuthStorage,
	createAgentSession,
	DefaultResourceLoader,
	ModelRegistry,
	SessionManager,
	SettingsManager,
} from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import type { AgentSession, ToolDefinition } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { unwrapSemanticEdgeStreamFn, wrapStreamFnWithSemanticEdges } from "/opt/homebrew/lib/node_modules/prime-agent/dist/core/semantic-edges.js";
import type { StreamFn } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-agent-core/dist/types.js";
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import type { AssistantMessage } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/types.js";
import { AssistantMessageEventStream } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/utils/event-stream.js";
import { Type } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/typebox/build/index.mjs";

const image = "sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c";
const model = getModel("openrouter", "openai/gpt-5.6-sol");
const here = dirname(fileURLToPath(import.meta.url));
const reportPath = resolve(here, "../../.planning/2026-09-09-autonomous-execution/native-episode-qualification.json");

function reply(content: AssistantMessage["content"]): AssistantMessageEventStream {
	const message: AssistantMessage = {
		role: "assistant", content, api: model.api, provider: model.provider, model: model.id,
		stopReason: content.some((part) => part.type === "toolCall") ? "toolUse" : "stop",
		usage: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } },
		timestamp: Date.now(),
	};
	const stream = new AssistantMessageEventStream();
	stream.push({ type: "start", partial: message });
	stream.push({ type: "done", reason: message.stopReason as "stop" | "toolUse", message });
	stream.end(message);
	return stream;
}

function tool(name: string, id: string, args: Record<string, unknown>): AssistantMessageEventStream {
	return reply([{ type: "toolCall", id, name, arguments: args }]);
}

function text(value: string): AssistantMessageEventStream {
	return reply([{ type: "text", text: value }]);
}

function readPool(control: string): { active: Record<string, { name: string; kind: string }>; conservative_cpu_seconds: number } {
	const path = join(control, "resource-pool.json");
	return existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : { active: {}, conservative_cpu_seconds: 0 };
}

async function waitFor(testCondition: () => boolean, timeoutMs = 15000): Promise<void> {
	const deadline = Date.now() + timeoutMs;
	while (!testCondition()) {
		assert.ok(Date.now() < deadline, "bounded condition timed out");
		await delay(50);
	}
}

test("installed native episode isolates Python, runs one inline child, and exposes phase/lifecycle evidence", { timeout: 120000 }, async () => {
	const parent = join(homedir(), ".local/share/argo-study-20260909/qualification");
	mkdirSync(parent, { recursive: true, mode: 0o700 });
	const episode = mkdtempSync(join(parent, "native-sdk-"));
	const workspace = join(episode, "workspace");
	const artifacts = join(episode, "artifacts");
	const control = join(episode, "control");
	const profile = join(control, "profile");
	const sessions = join(artifacts, "sessions");
	for (const path of [workspace, artifacts, control, profile, sessions]) mkdirSync(path, { recursive: true, mode: 0o700 });
	writeFileSync(join(workspace, "public.txt"), "synthetic-public", { mode: 0o600 });
	const privatePath = join(control, "private-labels.txt");
	writeFileSync(privatePath, "SYNTHETIC_PRIVATE_LABEL_MARKER", { mode: 0o600 });
	const configPath = join(control, "kernel.json");
	writeFileSync(configPath, JSON.stringify({ image, workspace, artifact_root: artifacts, control_dir: control,
		deadline_epoch: Date.now() / 1000 + 110, max_cpu_seconds: 180 }), { mode: 0o600 });
	const previous = { wrapper: process.env.PRIME_AGENT_KERNEL_PYTHON, config: process.env.ARGO_KERNEL_CONFIG, telemetry: process.env.PRIME_AGENT_TELEMETRY };
	process.env.PRIME_AGENT_KERNEL_PYTHON = join(here, "kernel_wrapper.py");
	process.env.ARGO_KERNEL_CONFIG = configPath;
	process.env.PRIME_AGENT_TELEMETRY = "0";
	const originalFetch = globalThis.fetch;
	let attemptedNetworkRequests = 0;
	globalThis.fetch = async () => { attemptedNetworkRequests++; throw new Error("QUALIFICATION_NETWORK_FORBIDDEN"); };
	let session: AgentSession | undefined;
	let childSession: AgentSession | undefined;
	let releaseChild: (() => void) | undefined;
	let childEntered: (() => void) | undefined;
	const childReady = new Promise<void>((done) => { childEntered = done; });
	const childGate = new Promise<void>((done) => { releaseChild = done; });
	const observation: Record<string, unknown> = { schema: "argo-native-episode-qualification/v1", image, fake_provider: true, actual_provider_requests: 0, scientific_runs: 0 };
	const calls: Array<{ sessionId: string | undefined; model: string; thinking: string | undefined; tools: string[] }> = [];
	const phaseCalls: Array<{ phase: string; admitted: boolean }> = [];
	let phase = "PLANNER";
	let parentCalls = 0;
	let childCalls = 0;
	let childSignal: AbortSignal | undefined;
	let parentSessionId = "";
	let disallowedToolCalls = 0;
	const customTools: ToolDefinition[] = [
		{ name: "phase_probe", label: "Synthetic phase", description: "Synthetic phase probe", parameters: Type.Object({}),
			async execute() {
				const admitted = phase === "INVESTIGATOR";
				phaseCalls.push({ phase, admitted });
				const status = admitted ? "ADMITTED" : "PHASE_REQUIRES_ASSESSMENT";
				return { content: [{ type: "text", text: status }], details: { phase, admitted } };
			} },
		{ name: "forbidden_probe", label: "Forbidden synthetic probe", description: "Must stay outside allowed tools", parameters: Type.Object({}),
			async execute() { disallowedToolCalls++; return { content: [{ type: "text", text: "forbidden" }], details: {} }; } },
	];
	const fakeStream: StreamFn = async (selected, context, options) => {
		calls.push({ sessionId: options?.sessionId, model: `${selected.provider}/${selected.id}`, thinking: options?.reasoning, tools: (context.tools ?? []).map((item) => item.name).sort() });
		assert.equal(selected.provider, model.provider);
		assert.equal(selected.id, model.id);
		assert.equal(options?.reasoning, "high");
		assert.ok(!(context.tools ?? []).some((item) => item.name === "forbidden_probe"));
		if (options?.sessionId === parentSessionId) {
			const n = parentCalls++;
			if (n === 0) return tool("ipython", "parent-boundary", { code: `from pathlib import Path\nassert not Path(${JSON.stringify(privatePath)}).exists()\nassert Path('public.txt').read_text() == 'synthetic-public'\nx = 40\nPath('parent-output.txt').write_text(str(x+2))\nprint('PARENT_BOUNDARY_OK')` });
			if (n === 1) return tool("ipython", "parent-persistence-spawn", { code: "assert x == 40\nx += 2\nchild = await rlm.run('SYNTHETIC_CHILD: verify public workspace and write child evidence.', name='synthetic-child')\nprint(child.rlm_child_id)" });
			return text("SYNTHETIC_PARENT_DONE");
		}
		const n = childCalls++;
		if (n === 0) {
			childSignal = options?.signal;
			childEntered?.();
			await childGate;
			return tool("ipython", "child-boundary", { code: `from pathlib import Path\nimport os,json\nassert 'x' not in globals()\nassert not Path(${JSON.stringify(privatePath)}).exists()\nassert Path('public.txt').read_text() == 'synthetic-public'\ny = 7\nPath('child-output.json').write_text(json.dumps({'depth': os.environ['RLM_DEPTH'], 'public': True, 'private_visible': False}))\nprint('CHILD_BOUNDARY_OK')` });
		}
		if (n === 1) return tool("ipython", "child-persistence", { code: "assert y == 7\ny += 1\nassert y == 8\nprint('CHILD_PERSISTENCE_OK')" });
		if (n === 2) return tool("phase_probe", "child-phase", {});
		return text("SYNTHETIC_CHILD_DONE");
	};
	try {
		const auth = AuthStorage.inMemory({ openrouter: { type: "api_key", key: "fake-native-qualification-never-sent" } }, { usePrimeCliConfig: false });
		const registry = ModelRegistry.inMemory(auth);
		const settings = SettingsManager.inMemory({ retry: { enabled: false, provider: { maxRetries: 0, timeoutMs: 10000 } }, autoRefine: { enabled: false }, compaction: { enabled: false }, idleEvictionMinutes: "off", packages: [], extensions: [], skills: [], prompts: [], mcpServers: {} });
		const loader = new DefaultResourceLoader({ cwd: workspace, agentDir: profile, settingsManager: settings, noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true, bundledSkillsDir: null, systemPrompt: "Synthetic native qualification only.", appendSystemPrompt: [] });
		await loader.reload();
		assert.equal(loader.getSkills().skills.length, 0);
		assert.equal(loader.getAgentsFiles().agentsFiles.length, 0);
		assert.equal(loader.getPrompts().prompts.length, 0);
		({ session } = await createAgentSession({ cwd: workspace, agentDir: profile, authStorage: auth, modelRegistry: registry, model, thinkingLevel: "high", resourceLoader: loader, settingsManager: settings, sessionManager: SessionManager.create(workspace, sessions), tools: ["ipython", "phase_probe"], allowedToolNames: ["ipython", "phase_probe"], customTools, includeGoals: false, includeCompactSkill: false, rlmMaxDepth: 2, prewarmIpythonKernel: false, telemetryDisabled: true }));
		parentSessionId = session.sessionId;
		session.agent.streamFn = fakeStream;
		session.agent.toolExecution = "sequential";
		session.setActiveToolsByName(["ipython"]);
		const nativeEvents: unknown[] = [];
		session.subscribe((event) => nativeEvents.push(event));
		const prompt = session.prompt("Run the synthetic persistent-kernel and inline-child fixture.", { expandPromptTemplates: false });
		await childReady;
		await prompt;
		observation.parent_prompt_returned_with_child_running = session.hasRunningRlmChildren();
		assert.equal(session.hasRunningRlmChildren(), true);
		const roster = await session.listRlmSubagents();
		assert.equal(roster.subagents.length, 1);
		childSession = session.getRlmChildSession(roster.subagents[0].rlm_child_id);
		assert.ok(childSession);
		assert.equal(unwrapSemanticEdgeStreamFn(childSession.agent.streamFn), fakeStream);
		assert.equal(childSession.model?.id, model.id);
		assert.equal(childSession.thinkingLevel, "high");
		assert.equal(childSession.settingsManager, settings);
		assert.equal(childSession.resourceLoader, loader);
		assert.equal(childSession.agent.toolExecution, "sequential");
		observation.child_shared_closure = true;
		observation.parent_active_at_spawn = session.getActiveToolNames();
		observation.child_active_at_spawn = childSession.getActiveToolNames();
		observation.child_model = childSession.model?.id;
		observation.child_thinking = childSession.thinkingLevel;
		observation.child_allowed_ceiling_excludes_forbidden = !childSession.getActiveToolNames().includes("forbidden_probe");
		phase = "ASSESSOR";
		session.setActiveToolsByName(["ipython"]);
		session.agent.abort();
		await delay(100);
		observation.parent_abort_did_not_abort_child = childSignal?.aborted === false;
		observation.child_active_after_parent_phase_switch = childSession.getActiveToolNames();
		releaseChild?.();
		await session.waitForRlmQuiescence(AbortSignal.timeout(30000));
		assert.equal(session.hasRunningRlmChildren(), false);
		const completedRoster = await session.listRlmSubagents();
		assert.equal(completedRoster.subagents[0].status, "completed");
		assert.equal(readFileSync(join(workspace, "parent-output.txt"), "utf8"), "42");
		assert.deepEqual(JSON.parse(readFileSync(join(workspace, "child-output.json"), "utf8")), { depth: "1", public: true, private_visible: false });
		assert.equal(disallowedToolCalls, 0);
		observation.phase_calls_from_delayed_child = phaseCalls;
		assert.deepEqual(phaseCalls, [{ phase: "ASSESSOR", admitted: false }]);
		observation.parent_semantic_request = session.semanticEdges.lastTurnRequestId ?? null;
		observation.child_semantic_request = childSession.semanticEdges.lastTurnRequestId ?? null;
		observation.native_child_status = completedRoster.subagents[0].status;
		const existingRecorder = session.semanticEdges;
		session.agent.streamFn = wrapStreamFnWithSemanticEdges(fakeStream, existingRecorder);
		await session.prompt("Confirm the synthetic shared stream through the existing native recorder.", { expandPromptTemplates: false });
		assert.equal(session.semanticEdges, existingRecorder);
		assert.equal(unwrapSemanticEdgeStreamFn(session.agent.streamFn), fakeStream);
		assert.ok(session.semanticEdges.lastTurnRequestId);
		observation.parent_semantic_request_after_public_wrapper = session.semanticEdges.lastTurnRequestId;
		observation.public_semantic_binding_preserves_recorder = true;
		observation.parent_and_child_kernel_leases = Object.values(readPool(control).active).filter((entry) => entry.kind === "kernel").length;
		const before = Date.now();
		session.dispose();
		observation.active_leases_immediately_after_sync_dispose = Object.keys(readPool(control).active).length;
		await waitFor(() => Object.keys(readPool(control).active).length === 0);
		observation.sync_dispose_cleanup_wait_ms = Date.now() - before;
		observation.active_leases_after_cleanup = 0;
		const containerNames = readdirSync(control).filter((name) => /^argo-kernel-.*\.json$/.test(name)).flatMap((name) => {
			const record: Record<string, unknown> = JSON.parse(readFileSync(join(control, name), "utf8"));
			return typeof record.container === "string" ? [record.container] : [];
		});
		for (const name of containerNames) {
			const result = spawnSync("/opt/homebrew/bin/docker", ["container", "ls", "--all", "--quiet", "--filter", `name=^/${name}$`], { encoding: "utf8", timeout: 10000 });
			assert.equal(result.status, 0);
			assert.equal(result.stdout.trim(), "");
		}
		assert.equal(attemptedNetworkRequests, 0);
		observation.calls = calls;
		observation.parent_calls = parentCalls;
		observation.child_calls = childCalls;
		observation.attempted_network_requests = attemptedNetworkRequests;
		observation.native_event_count = nativeEvents.length;
		observation.native_event_sha256 = createHash("sha256").update(JSON.stringify(nativeEvents)).digest("hex");
		observation.source_sha256 = createHash("sha256").update(readFileSync(join(here, "controller.ts"))).digest("hex");
		observation.status = "PASS_SYNTHETIC_NATIVE_SDK_WITH_CONTROLLER_DEFECTS";
		observation.fixture_passed = true;
		writeFileSync(reportPath, `${JSON.stringify(observation, null, 2)}\n`);
	} finally {
		releaseChild?.();
		if (childSession) await childSession.disposeAsync().catch(() => undefined);
		if (session) await session.disposeAsync().catch(() => undefined);
		await waitFor(() => Object.keys(readPool(control).active).length === 0).catch(() => undefined);
		globalThis.fetch = originalFetch;
		const restoreEnvironment: Array<[string, string | undefined]> = [["PRIME_AGENT_KERNEL_PYTHON", previous.wrapper], ["ARGO_KERNEL_CONFIG", previous.config], ["PRIME_AGENT_TELEMETRY", previous.telemetry]];
		for (const [key, value] of restoreEnvironment) {
			if (value === undefined) delete process.env[key]; else process.env[key] = value;
		}
		if (Object.keys(readPool(control).active).length === 0) rmSync(episode, { recursive: true, force: true });
	}
});
