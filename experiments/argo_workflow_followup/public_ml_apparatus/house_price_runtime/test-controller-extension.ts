import assert from "node:assert/strict";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type {
  ExtensionAPI,
  ExtensionContext,
  ToolDefinition,
} from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import {
  CONTROLLER_TOOL_NAMES,
  createControllerExtension,
  type ControllerExtensionBinding,
  type ControllerToolName,
} from "./controller-extension.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const TEST_ROOT = join(HERE, "prime-boundary-probes", ".tmp-controller-tests");
const FIXTURE_BRIDGE = resolve(HERE, "prime-boundary-probes", "fake-bridge.mjs");
const LINGERING_STDOUT_BRIDGE = resolve(HERE, "a2-frontend-probes", "lingering-stdout-bridge.mjs");
const ZERO_HASH = "0".repeat(64);
const RUN_ID = "11111111-1111-4111-8111-111111111111";
const ARTIFACT_HASH = "a".repeat(64);

type Test = { name: string; run: () => Promise<void> | void };
const tests: Test[] = [];

function test(name: string, run: Test["run"]): void {
  tests.push({ name, run });
}

function binding(recordPath: string, mode = "normal"): ControllerExtensionBinding {
  return {
    schemaVersion: "argo-house-price-controller-extension-binding/v1",
    expectedExtensionSha256: ZERO_HASH,
    bridge: { command: process.execPath, argv: [FIXTURE_BRIDGE, recordPath, mode] },
    limits: {
      maxRequestBytes: 262144,
      maxResponseBytes: 262144,
      maxListItems: 5,
      maxSourceContentBytes: 131072,
      maxPathBytes: 32,
      maxMetricAbs: 1000000000000,
      maxMetricDecimalPlaces: 6,
      maxRows: 292,
      bridgeTimeoutMs: 30000,
    },
  };
}

function registerTools(
  controllerBinding: ControllerExtensionBinding,
  activeNames: string[] = [...CONTROLLER_TOOL_NAMES],
): Map<string, ToolDefinition> {
  const registered = new Map<string, ToolDefinition>();
  const pi = {
    registerTool(tool: ToolDefinition) {
      registered.set(tool.name, tool);
    },
    getActiveTools() {
      return [...activeNames];
    },
    on() {
      return undefined;
    },
  } as unknown as ExtensionAPI;
  createControllerExtension(controllerBinding)(pi);
  return registered;
}

async function invoke(
  tools: Map<string, ToolDefinition>,
  name: ControllerToolName,
  arguments_: unknown,
  signal?: AbortSignal,
): Promise<string> {
  const tool = tools.get(name);
  assert.ok(tool, `missing tool ${name}`);
  const result = await tool.execute(
    `call-${name}`,
    arguments_ as never,
    signal,
    undefined,
    {} as ExtensionContext,
  );
  const content = result.content[0];
  assert.equal(content?.type, "text");
  return content && content.type === "text" ? content.text : "";
}

async function expectSafeError(operation: Promise<unknown>, expected: string): Promise<void> {
  await assert.rejects(operation, (error: unknown) => error instanceof Error && error.message === expected);
}

test("lock description places final artifact lock after final-refit prediction", () => {
  const tools = registerTools(binding(join(TEST_ROOT, "description.jsonl")));
  assert.match(tools.get("lock_final_artifact")?.description ?? "", /after final-refit prediction/i);
});

test("bridge promise settles safely when a descendant retains stdout", async () => {
  const recordPath = join(TEST_ROOT, "lingering-stdout.jsonl");
  const configured = binding(recordPath);
  configured.bridge = { command: process.execPath, argv: [LINGERING_STDOUT_BRIDGE] };
  const tools = registerTools(configured);
  const startedAt = Date.now();
  await expectSafeError(invoke(tools, "read_public_result", {}), "BRIDGE_OUTPUT");
  const elapsedMs = Date.now() - startedAt;
  assert.ok(elapsedMs >= 900 && elapsedMs < 1400, `unexpected close-grace settlement: ${elapsedMs}ms`);
});

test("registers only the six exact strict schemas", () => {
  const tools = registerTools(binding(join(TEST_ROOT, "registration.jsonl")));
  assert.deepEqual([...tools.keys()], [...CONTROLLER_TOOL_NAMES]);
  for (const [name, definition] of tools) {
    assert.equal((definition.parameters as { additionalProperties?: unknown }).additionalProperties, false, name);
  }
  assert.equal(tools.get("request_R1_run")?.executionMode, "sequential");
  assert.equal(tools.get("lock_final_artifact")?.executionMode, "sequential");
});

test("delegates all actions to one fixed shell-false bridge and validates results", async () => {
  const recordPath = join(TEST_ROOT, "all-actions.jsonl");
  const tools = registerTools(binding(recordPath));
  const readText = await invoke(tools, "read_solution", { path: "solution.py" });
  assert.match(readText, /fit_predict/);
  await invoke(tools, "write_solution", { path: "research.md", content: "# bounded\n", expected_sha256: ZERO_HASH });
  await invoke(tools, "request_R1_run", {});
  await invoke(tools, "read_public_result", {});
  const devText = await invoke(tools, "read_dev_result", {});
  assert.match(devText, /"mae":12345\.125000/);
  await invoke(tools, "lock_final_artifact", { run_id: RUN_ID, artifact_sha256: ARTIFACT_HASH });
  const requests = readFileSync(recordPath, "utf8").trim().split("\n").map((line) => JSON.parse(line) as unknown);
  assert.deepEqual(
    requests.map((request) => (request as { action: string }).action),
    [...CONTROLLER_TOOL_NAMES],
  );
  for (const request of requests) {
    assert.deepEqual(Object.keys(request as object).sort(), ["action", "arguments"]);
  }
});

test("execute revalidation rejects unknown properties and exact-surface drift", async () => {
  const recordPath = join(TEST_ROOT, "revalidation.jsonl");
  const tools = registerTools(binding(recordPath));
  await expectSafeError(invoke(tools, "read_solution", { path: "solution.py", extra: true }), "INVALID_ARGUMENT");
  await expectSafeError(invoke(tools, "write_solution", { path: "../escape", content: "x" }), "PATH_DENIED");
  const contaminated = registerTools(binding(recordPath), [...CONTROLLER_TOOL_NAMES, "escape_late"]);
  await expectSafeError(invoke(contaminated, "read_public_result", {}), "TOOL_SURFACE");
});

test("metacharacters remain bounded JSON data and cannot create a canary", async () => {
  const recordPath = join(TEST_ROOT, "command-injection.jsonl");
  const canaryPath = join(TEST_ROOT, "command-injection-canary");
  const payload = `\"; touch ${canaryPath}; printf pwned; #\n$(${canaryPath})`;
  const tools = registerTools(binding(recordPath));
  await invoke(tools, "write_solution", { path: "solution.py", content: payload });
  const recorded = JSON.parse(readFileSync(recordPath, "utf8").trim()) as {
    action: string;
    arguments: { content: string };
  };
  assert.equal(recorded.action, "write_solution");
  assert.equal(recorded.arguments.content, payload);
  assert.equal(requireCanary(canaryPath), false);
});

function requireCanary(path: string): boolean {
  try {
    readFileSync(path);
    return true;
  } catch {
    return false;
  }
}

test("unknown bridge errors and unknown response properties do not pass through", async () => {
  const unknownErrorTools = registerTools(binding(join(TEST_ROOT, "unknown-error.jsonl"), "unknown-error"));
  await expectSafeError(invoke(unknownErrorTools, "read_public_result", {}), "BRIDGE_OUTPUT");
  const unknownPropertyTools = registerTools(binding(join(TEST_ROOT, "unknown-property.jsonl"), "unknown-property"));
  await expectSafeError(invoke(unknownPropertyTools, "read_public_result", {}), "BRIDGE_OUTPUT");
});

test("bridge output limits, metric lexical form, and cancellation fail closed", async () => {
  const oversize = registerTools(binding(join(TEST_ROOT, "oversize.jsonl"), "oversize"));
  await expectSafeError(invoke(oversize, "read_public_result", {}), "BRIDGE_OUTPUT");
  const scientific = registerTools(binding(join(TEST_ROOT, "scientific.jsonl"), "metric-scientific"));
  await expectSafeError(invoke(scientific, "read_dev_result", {}), "RESULT_INVALID");

  const abortRead = new AbortController();
  const timeoutRead = registerTools(binding(join(TEST_ROOT, "timeout-read.jsonl"), "timeout"));
  const readPromise = invoke(timeoutRead, "read_public_result", {}, abortRead.signal);
  abortRead.abort();
  await expectSafeError(readPromise, "BRIDGE_TIMEOUT");

  const abortAdmission = new AbortController();
  const timeoutAdmission = registerTools(binding(join(TEST_ROOT, "timeout-admission.jsonl"), "timeout"));
  const admissionPromise = invoke(timeoutAdmission, "request_R1_run", {}, abortAdmission.signal);
  abortAdmission.abort();
  await expectSafeError(admissionPromise, "UNCERTAIN_NO_AUTOMATIC_RETRY");
});

test("trusted binding rejects unfrozen numeric limits and model-shaped bridge overrides", () => {
  const valid = binding(join(TEST_ROOT, "binding.jsonl"));
  const changedTimeout = structuredClone(valid) as unknown as Record<string, unknown>;
  (changedTimeout.limits as Record<string, unknown>).bridgeTimeoutMs = 1;
  assert.throws(
    () => createControllerExtension(changedTimeout as unknown as ControllerExtensionBinding),
    (error: unknown) => error instanceof Error && error.message === "INTERNAL_ERROR",
  );
  const extra = structuredClone(valid) as unknown as Record<string, unknown>;
  extra.cwd = TEST_ROOT;
  assert.throws(
    () => createControllerExtension(extra as unknown as ControllerExtensionBinding),
    (error: unknown) => error instanceof Error && error.message === "INTERNAL_ERROR",
  );
});

async function main(): Promise<void> {
  rmSync(TEST_ROOT, { recursive: true, force: true });
  mkdirSync(TEST_ROOT, { recursive: true });
  const failures: Array<{ name: string; error: string }> = [];
  for (const item of tests) {
    try {
      await item.run();
      process.stdout.write(`PASS ${item.name}\n`);
    } catch (error) {
      const message = error instanceof Error ? `${error.name}: ${error.message}\n${error.stack ?? ""}` : String(error);
      failures.push({ name: item.name, error: message });
      process.stdout.write(`FAIL ${item.name}\n${message}\n`);
    }
  }
  writeFileSync(join(TEST_ROOT, "unit-summary.json"), JSON.stringify({ total: tests.length, failures }, null, 2));
  if (failures.length > 0) process.exitCode = 1;
}

await main();
