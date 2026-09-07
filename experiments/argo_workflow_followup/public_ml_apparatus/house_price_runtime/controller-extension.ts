import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import { closeSync, constants, fstatSync, openSync, readFileSync } from "node:fs";
import { dirname, isAbsolute, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI, ExtensionFactory } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { Type } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/typebox/build/index.mjs";

export const CONTROLLER_TOOL_NAMES = [
  "read_solution",
  "write_solution",
  "request_R1_run",
  "read_public_result",
  "read_dev_result",
  "lock_final_artifact",
] as const;

export type ControllerToolName = (typeof CONTROLLER_TOOL_NAMES)[number];
export type SolutionPath = "solution.py" | "research.md" | "intent.json";

export interface ControllerLimits {
  maxRequestBytes: 262144;
  maxResponseBytes: 262144;
  maxListItems: 5;
  maxSourceContentBytes: 131072;
  maxPathBytes: 32;
  maxMetricAbs: 1000000000000;
  maxMetricDecimalPlaces: 6;
  maxRows: 292;
  bridgeTimeoutMs: 30000;
}

export interface ControllerExtensionBinding {
  schemaVersion: "argo-house-price-controller-extension-binding/v1";
  expectedExtensionSha256: string;
  bridge: {
    command: string;
    argv: readonly string[];
  };
  limits: ControllerLimits;
}

type SafeError =
  | "INVALID_ARGUMENT"
  | "TOOL_SURFACE"
  | "PATH_DENIED"
  | "SOURCE_LIMIT"
  | "HASH_MISMATCH"
  | "SOURCE_LOCKED"
  | "CONFLICT"
  | "INTENT_INVALID"
  | "BUDGET_EXHAUSTED"
  | "UNCERTAIN_NO_AUTOMATIC_RETRY"
  | "RESULT_NOT_READY"
  | "RESULT_INVALID"
  | "FINAL_SELECTION_REQUIRED"
  | "FINAL_LOCKED"
  | "BRIDGE_TIMEOUT"
  | "BRIDGE_OUTPUT"
  | "INTERNAL_ERROR";

type BridgeRequest = {
  action: ControllerToolName;
  arguments: Record<string, unknown>;
};

type ReadSolutionResult = { path: SolutionPath; content: string; sha256: string };
type WriteSolutionResult = { path: SolutionPath; sha256: string; bytes: number };
type RunReference = {
  intent_sha256: string;
  run_id: string;
  experiment_id: string;
  solution_sha256: string;
  phase: "dev" | "final_refit";
};
type PublicRun = RunReference & {
  status: "QUEUED" | "RUNNING" | "DONE" | "FAILED" | "CANCELLED" | "UNKNOWN";
  artifact_sha256?: string;
};
type PublicResult = {
  phase: "development" | "final_selected" | "final_locked";
  dev_attempts: number;
  final_attempts: number;
  remaining_dev_opportunities: number;
  runs: PublicRun[];
};
type DevResult = {
  results: Array<{
    run_id: string;
    solution_sha256: string;
    valid: true;
    mae: number;
    rows: number;
  }>;
};
type LockResult = {
  run_id: string;
  artifact_sha256: string;
  lock_sha256: string;
  solution_sha256: string;
};
type ActionResult = ReadSolutionResult | WriteSolutionResult | RunReference | PublicResult | DevResult | LockResult;

const SAFE_ERRORS = new Set<SafeError>([
  "INVALID_ARGUMENT",
  "TOOL_SURFACE",
  "PATH_DENIED",
  "SOURCE_LIMIT",
  "HASH_MISMATCH",
  "SOURCE_LOCKED",
  "CONFLICT",
  "INTENT_INVALID",
  "BUDGET_EXHAUSTED",
  "UNCERTAIN_NO_AUTOMATIC_RETRY",
  "RESULT_NOT_READY",
  "RESULT_INVALID",
  "FINAL_SELECTION_REQUIRED",
  "FINAL_LOCKED",
  "BRIDGE_TIMEOUT",
  "BRIDGE_OUTPUT",
  "INTERNAL_ERROR",
]);
const PATHS = new Set<SolutionPath>(["solution.py", "research.md", "intent.json"]);
const TOOL_SET = new Set<string>(CONTROLLER_TOOL_NAMES);
const HEX64 = /^[0-9a-f]{64}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_BINDING_BYTES = 65536;
const MAX_COMMAND_BYTES = 4096;
const MAX_ARGV_ITEMS = 16;
const BRIDGE_CLOSE_GRACE_MS = 1000;

class BoundaryError extends Error {
  readonly safeError: SafeError;

  constructor(safeError: SafeError) {
    super(safeError);
    this.name = "BoundaryError";
    this.safeError = safeError;
  }
}

function fail(error: SafeError): never {
  throw new BoundaryError(error);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(record: Record<string, unknown>, required: readonly string[], optional: readonly string[] = []): boolean {
  const keys = Object.keys(record);
  if (!required.every((key) => Object.hasOwn(record, key))) return false;
  const allowed = new Set([...required, ...optional]);
  return keys.every((key) => allowed.has(key));
}

function isPositiveInteger(value: unknown, maximum: number): value is number {
  return Number.isSafeInteger(value) && typeof value === "number" && value > 0 && value <= maximum;
}

function isBoundedInteger(value: unknown, minimum: number, maximum: number): value is number {
  return Number.isSafeInteger(value) && typeof value === "number" && value >= minimum && value <= maximum;
}

function utf8Bytes(value: string): number {
  return Buffer.byteLength(value, "utf8");
}

function hasInvalidUnicode(value: string): boolean {
  if (value.includes("\0")) return true;
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) return true;
      index += 1;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      return true;
    }
  }
  return false;
}

function isSolutionPath(value: unknown, limits: ControllerLimits): value is SolutionPath {
  return (
    typeof value === "string" &&
    PATHS.has(value as SolutionPath) &&
    !hasInvalidUnicode(value) &&
    utf8Bytes(value) <= limits.maxPathBytes
  );
}

function assertHash(value: unknown): asserts value is string {
  if (typeof value !== "string" || !HEX64.test(value)) fail("RESULT_INVALID");
}

function assertUuid(value: unknown): asserts value is string {
  if (typeof value !== "string" || !UUID.test(value)) fail("RESULT_INVALID");
}

function assertSourceText(value: unknown, limits: ControllerLimits): asserts value is string {
  if (
    typeof value !== "string" ||
    hasInvalidUnicode(value) ||
    utf8Bytes(value) > limits.maxSourceContentBytes
  ) {
    fail("SOURCE_LIMIT");
  }
}

function assertToolSurface(pi: ExtensionAPI): void {
  const active = pi.getActiveTools();
  if (active.length !== CONTROLLER_TOOL_NAMES.length) fail("TOOL_SURFACE");
  const activeSet = new Set(active);
  if (activeSet.size !== CONTROLLER_TOOL_NAMES.length) fail("TOOL_SURFACE");
  if (!active.every((name) => TOOL_SET.has(name))) fail("TOOL_SURFACE");
}

function validateBinding(value: unknown): ControllerExtensionBinding {
  if (!isRecord(value) || !hasExactKeys(value, ["schemaVersion", "expectedExtensionSha256", "bridge", "limits"])) {
    fail("INTERNAL_ERROR");
  }
  if (value.schemaVersion !== "argo-house-price-controller-extension-binding/v1") fail("INTERNAL_ERROR");
  if (typeof value.expectedExtensionSha256 !== "string" || !HEX64.test(value.expectedExtensionSha256)) {
    fail("INTERNAL_ERROR");
  }
  if (!isRecord(value.bridge) || !hasExactKeys(value.bridge, ["command", "argv"])) fail("INTERNAL_ERROR");
  if (
    typeof value.bridge.command !== "string" ||
    !isAbsolute(value.bridge.command) ||
    hasInvalidUnicode(value.bridge.command) ||
    utf8Bytes(value.bridge.command) > MAX_COMMAND_BYTES
  ) {
    fail("INTERNAL_ERROR");
  }
  if (
    !Array.isArray(value.bridge.argv) ||
    value.bridge.argv.length > MAX_ARGV_ITEMS ||
    !value.bridge.argv.every(
      (item) => typeof item === "string" && !hasInvalidUnicode(item) && utf8Bytes(item) <= MAX_COMMAND_BYTES,
    )
  ) {
    fail("INTERNAL_ERROR");
  }
  if (
    !isRecord(value.limits) ||
    !hasExactKeys(value.limits, [
      "maxRequestBytes",
      "maxResponseBytes",
      "maxListItems",
      "maxSourceContentBytes",
      "maxPathBytes",
      "maxMetricAbs",
      "maxMetricDecimalPlaces",
      "maxRows",
      "bridgeTimeoutMs",
    ])
  ) {
    fail("INTERNAL_ERROR");
  }
  const limits = value.limits;
  if (
    limits.maxRequestBytes !== 262144 ||
    limits.maxResponseBytes !== 262144 ||
    limits.maxListItems !== 5 ||
    limits.maxSourceContentBytes !== 131072 ||
    limits.maxPathBytes !== 32 ||
    limits.maxMetricAbs !== 1000000000000 ||
    limits.maxMetricDecimalPlaces !== 6 ||
    limits.maxRows !== 292 ||
    limits.bridgeTimeoutMs !== 30000
  ) {
    fail("INTERNAL_ERROR");
  }
  return {
    schemaVersion: value.schemaVersion,
    expectedExtensionSha256: value.expectedExtensionSha256,
    bridge: { command: value.bridge.command, argv: [...value.bridge.argv] },
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

function validateReadArguments(value: unknown, limits: ControllerLimits): Record<string, unknown> {
  if (!isRecord(value) || !hasExactKeys(value, ["path"]) || !isSolutionPath(value.path, limits)) {
    fail("INVALID_ARGUMENT");
  }
  return { path: value.path };
}

function validateWriteArguments(value: unknown, limits: ControllerLimits): Record<string, unknown> {
  if (!isRecord(value) || !hasExactKeys(value, ["path", "content"], ["expected_sha256"])) {
    fail("INVALID_ARGUMENT");
  }
  if (!isSolutionPath(value.path, limits)) fail("PATH_DENIED");
  assertSourceText(value.content, limits);
  if (value.expected_sha256 !== undefined && (typeof value.expected_sha256 !== "string" || !HEX64.test(value.expected_sha256))) {
    fail("INVALID_ARGUMENT");
  }
  return {
    path: value.path,
    content: value.content,
    ...(value.expected_sha256 === undefined ? {} : { expected_sha256: value.expected_sha256 }),
  };
}

function validateEmptyArguments(value: unknown): Record<string, unknown> {
  if (!isRecord(value) || !hasExactKeys(value, [])) fail("INVALID_ARGUMENT");
  return {};
}

function validateLockArguments(value: unknown): Record<string, unknown> {
  if (!isRecord(value) || !hasExactKeys(value, ["run_id", "artifact_sha256"])) fail("INVALID_ARGUMENT");
  if (typeof value.run_id !== "string" || !UUID.test(value.run_id)) fail("INVALID_ARGUMENT");
  if (typeof value.artifact_sha256 !== "string" || !HEX64.test(value.artifact_sha256)) fail("INVALID_ARGUMENT");
  return { run_id: value.run_id, artifact_sha256: value.artifact_sha256 };
}

function validateArguments(action: ControllerToolName, value: unknown, limits: ControllerLimits): Record<string, unknown> {
  switch (action) {
    case "read_solution":
      return validateReadArguments(value, limits);
    case "write_solution":
      return validateWriteArguments(value, limits);
    case "request_R1_run":
    case "read_public_result":
    case "read_dev_result":
      return validateEmptyArguments(value);
    case "lock_final_artifact":
      return validateLockArguments(value);
  }
}

function validateRunReference(value: unknown): RunReference {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["intent_sha256", "run_id", "experiment_id", "solution_sha256", "phase"])
  ) {
    fail("RESULT_INVALID");
  }
  assertHash(value.intent_sha256);
  assertUuid(value.run_id);
  assertUuid(value.experiment_id);
  assertHash(value.solution_sha256);
  if (value.phase !== "dev" && value.phase !== "final_refit") fail("RESULT_INVALID");
  return {
    intent_sha256: value.intent_sha256,
    run_id: value.run_id,
    experiment_id: value.experiment_id,
    solution_sha256: value.solution_sha256,
    phase: value.phase,
  };
}

function validateResult(action: ControllerToolName, value: unknown, limits: ControllerLimits): ActionResult {
  if (!isRecord(value)) fail("RESULT_INVALID");
  switch (action) {
    case "read_solution": {
      if (!hasExactKeys(value, ["path", "content", "sha256"]) || !isSolutionPath(value.path, limits)) {
        fail("RESULT_INVALID");
      }
      assertSourceText(value.content, limits);
      assertHash(value.sha256);
      return { path: value.path, content: value.content, sha256: value.sha256 };
    }
    case "write_solution": {
      if (!hasExactKeys(value, ["path", "sha256", "bytes"]) || !isSolutionPath(value.path, limits)) {
        fail("RESULT_INVALID");
      }
      assertHash(value.sha256);
      if (!isBoundedInteger(value.bytes, 0, limits.maxSourceContentBytes)) fail("RESULT_INVALID");
      return { path: value.path, sha256: value.sha256, bytes: value.bytes };
    }
    case "request_R1_run":
      return validateRunReference(value);
    case "read_public_result": {
      if (
        !hasExactKeys(value, ["phase", "dev_attempts", "final_attempts", "remaining_dev_opportunities", "runs"]) ||
        (value.phase !== "development" && value.phase !== "final_selected" && value.phase !== "final_locked") ||
        !isBoundedInteger(value.dev_attempts, 0, 4) ||
        !isBoundedInteger(value.final_attempts, 0, 1) ||
        !isBoundedInteger(value.remaining_dev_opportunities, 0, 3) ||
        !Array.isArray(value.runs) ||
        value.runs.length > limits.maxListItems
      ) {
        fail("RESULT_INVALID");
      }
      const runs = value.runs.map((candidate): PublicRun => {
        if (!isRecord(candidate) || !hasExactKeys(candidate, ["intent_sha256", "run_id", "experiment_id", "solution_sha256", "phase", "status"], ["artifact_sha256"])) {
          fail("RESULT_INVALID");
        }
        const reference = validateRunReference({
          intent_sha256: candidate.intent_sha256,
          run_id: candidate.run_id,
          experiment_id: candidate.experiment_id,
          solution_sha256: candidate.solution_sha256,
          phase: candidate.phase,
        });
        if (
          candidate.status !== "QUEUED" &&
          candidate.status !== "RUNNING" &&
          candidate.status !== "DONE" &&
          candidate.status !== "FAILED" &&
          candidate.status !== "CANCELLED" &&
          candidate.status !== "UNKNOWN"
        ) {
          fail("RESULT_INVALID");
        }
        if (candidate.artifact_sha256 !== undefined) {
          assertHash(candidate.artifact_sha256);
          if (candidate.status !== "DONE") fail("RESULT_INVALID");
        }
        return {
          ...reference,
          status: candidate.status,
          ...(candidate.artifact_sha256 === undefined ? {} : { artifact_sha256: candidate.artifact_sha256 }),
        };
      });
      return {
        phase: value.phase,
        dev_attempts: value.dev_attempts,
        final_attempts: value.final_attempts,
        remaining_dev_opportunities: value.remaining_dev_opportunities,
        runs,
      };
    }
    case "read_dev_result": {
      if (!hasExactKeys(value, ["results"]) || !Array.isArray(value.results) || value.results.length > limits.maxListItems) {
        fail("RESULT_INVALID");
      }
      const results = value.results.map((candidate) => {
        if (!isRecord(candidate) || !hasExactKeys(candidate, ["run_id", "solution_sha256", "valid", "mae", "rows"])) {
          fail("RESULT_INVALID");
        }
        assertUuid(candidate.run_id);
        assertHash(candidate.solution_sha256);
        if (candidate.valid !== true) fail("RESULT_INVALID");
        if (
          typeof candidate.mae !== "number" ||
          !Number.isFinite(candidate.mae) ||
          candidate.mae < 0 ||
          candidate.mae > limits.maxMetricAbs ||
          !isPositiveInteger(candidate.rows, limits.maxRows)
        ) {
          fail("RESULT_INVALID");
        }
        return {
          run_id: candidate.run_id,
          solution_sha256: candidate.solution_sha256,
          valid: true as const,
          mae: candidate.mae,
          rows: candidate.rows,
        };
      });
      return { results };
    }
    case "lock_final_artifact": {
      if (!hasExactKeys(value, ["run_id", "artifact_sha256", "lock_sha256", "solution_sha256"])) {
        fail("RESULT_INVALID");
      }
      assertUuid(value.run_id);
      assertHash(value.artifact_sha256);
      assertHash(value.lock_sha256);
      assertHash(value.solution_sha256);
      return {
        run_id: value.run_id,
        artifact_sha256: value.artifact_sha256,
        lock_sha256: value.lock_sha256,
        solution_sha256: value.solution_sha256,
      };
    }
  }
}

function validateMetricLexemes(responseText: string, expectedCount: number, decimalPlaces: number): void {
  const matches = [...responseText.matchAll(/"mae"\s*:\s*(-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/g)];
  if (matches.length !== expectedCount) fail("RESULT_INVALID");
  const allowed = new RegExp(`^(?:0|[1-9][0-9]*)(?:\\.[0-9]{1,${decimalPlaces}})?$`);
  if (matches.some((match) => !allowed.test(match[1]))) fail("RESULT_INVALID");
}

function parseBridgeResponse(action: ControllerToolName, bytes: Buffer, limits: ControllerLimits): ActionResult {
  if (bytes.length === 0 || bytes.length > limits.maxResponseBytes) fail("BRIDGE_OUTPUT");
  const text = bytes.toString("utf8");
  if (!Buffer.from(text, "utf8").equals(bytes) || hasInvalidUnicode(text)) fail("BRIDGE_OUTPUT");
  let parsed: unknown;
  try {
    parsed = JSON.parse(text) as unknown;
  } catch {
    fail("BRIDGE_OUTPUT");
  }
  if (!isRecord(parsed)) fail("BRIDGE_OUTPUT");
  if (parsed.ok === false) {
    if (!hasExactKeys(parsed, ["ok", "error"]) || typeof parsed.error !== "string" || !SAFE_ERRORS.has(parsed.error as SafeError)) {
      fail("BRIDGE_OUTPUT");
    }
    fail(parsed.error as SafeError);
  }
  if (parsed.ok !== true || !hasExactKeys(parsed, ["ok", "result"])) fail("BRIDGE_OUTPUT");
  const result = validateResult(action, parsed.result, limits);
  if (action === "read_dev_result") {
    validateMetricLexemes(text, (result as DevResult).results.length, limits.maxMetricDecimalPlaces);
  }
  return result;
}


function assertResponseBinding(request: BridgeRequest, result: ActionResult): void {
  if (request.action === "read_solution") {
    const readResult = result as ReadSolutionResult;
    if (readResult.path !== request.arguments.path) fail("RESULT_INVALID");
    const contentSha256 = createHash("sha256").update(readResult.content, "utf8").digest("hex");
    if (contentSha256 !== readResult.sha256) fail("RESULT_INVALID");
    return;
  }
  if (request.action === "write_solution") {
    const writeResult = result as WriteSolutionResult;
    const content = request.arguments.content;
    if (writeResult.path !== request.arguments.path || typeof content !== "string") fail("RESULT_INVALID");
    const contentSha256 = createHash("sha256").update(content, "utf8").digest("hex");
    if (contentSha256 !== writeResult.sha256 || utf8Bytes(content) !== writeResult.bytes) fail("RESULT_INVALID");
    return;
  }
  if (request.action === "lock_final_artifact") {
    const lockResult = result as LockResult;
    if (
      lockResult.run_id !== request.arguments.run_id ||
      lockResult.artifact_sha256 !== request.arguments.artifact_sha256
    ) {
      fail("RESULT_INVALID");
    }
  }
}

function runBridge(binding: ControllerExtensionBinding, request: BridgeRequest, signal: AbortSignal | undefined): Promise<ActionResult> {
  const requestBytes = Buffer.from(JSON.stringify(request), "utf8");
  if (requestBytes.length > binding.limits.maxRequestBytes) fail("SOURCE_LIMIT");
  return new Promise<ActionResult>((resolve, reject) => {
    const child = spawn(binding.bridge.command, [...binding.bridge.argv], {
      shell: false,
      stdio: ["pipe", "pipe", "ignore"],
      env: { LANG: "C.UTF-8", LC_ALL: "C.UTF-8" },
    });
    const chunks: Buffer[] = [];
    let byteCount = 0;
    let forcedError: SafeError | undefined;
    let settled = false;
    let operationTimer: ReturnType<typeof setTimeout> | undefined;
    let closeGraceTimer: ReturnType<typeof setTimeout> | undefined;

    const cleanup = (): void => {
      if (operationTimer !== undefined) clearTimeout(operationTimer);
      if (closeGraceTimer !== undefined) clearTimeout(closeGraceTimer);
      signal?.removeEventListener("abort", abortHandler);
    };
    const finishReject = (error: SafeError): void => {
      if (settled) return;
      settled = true;
      cleanup();
      child.stdin.destroy();
      child.stdout.destroy();
      reject(new BoundaryError(error));
    };
    const finishResolve = (result: ActionResult): void => {
      if (settled) return;
      settled = true;
      cleanup();
      resolve(result);
    };
    const scheduleCloseGrace = (error: SafeError): void => {
      if (settled || closeGraceTimer !== undefined) return;
      closeGraceTimer = setTimeout(() => {
        child.kill("SIGKILL");
        finishReject(error);
      }, BRIDGE_CLOSE_GRACE_MS);
    };
    const terminate = (error: SafeError): void => {
      if (forcedError === undefined) forcedError = error;
      child.kill("SIGKILL");
      scheduleCloseGrace(forcedError);
    };
    const timeoutError: SafeError =
      request.action === "request_R1_run" ? "UNCERTAIN_NO_AUTOMATIC_RETRY" : "BRIDGE_TIMEOUT";
    const abortHandler = (): void => terminate(timeoutError);
    operationTimer = setTimeout(() => terminate(timeoutError), binding.limits.bridgeTimeoutMs);

    signal?.addEventListener("abort", abortHandler, { once: true });
    child.on("error", () => finishReject("INTERNAL_ERROR"));
    child.stdout.on("data", (chunk: Buffer) => {
      byteCount += chunk.length;
      if (byteCount > binding.limits.maxResponseBytes) {
        terminate("BRIDGE_OUTPUT");
        return;
      }
      chunks.push(Buffer.from(chunk));
    });
    child.on("exit", (code) => {
      if (forcedError !== undefined) {
        scheduleCloseGrace(forcedError);
      } else {
        scheduleCloseGrace(code === 0 ? "BRIDGE_OUTPUT" : "INTERNAL_ERROR");
      }
    });
    child.on("close", (code) => {
      if (settled) return;
      if (forcedError) {
        finishReject(forcedError);
        return;
      }
      if (code !== 0) {
        finishReject("INTERNAL_ERROR");
        return;
      }
      try {
        const result = parseBridgeResponse(request.action, Buffer.concat(chunks), binding.limits);
        assertResponseBinding(request, result);
        finishResolve(result);
      } catch (error) {
        finishReject(error instanceof BoundaryError ? error.safeError : "INTERNAL_ERROR");
      }
    });
    child.stdin.on("error", () => terminate("INTERNAL_ERROR"));
    if (signal?.aborted) {
      terminate(timeoutError);
      return;
    }
    child.stdin.end(requestBytes);
  });
}
function formatResult(action: ControllerToolName, result: ActionResult): string {
  if (action !== "read_dev_result") return JSON.stringify(result);
  const dev = result as DevResult;
  const rows = dev.results.map(
    (item) =>
      `{"run_id":${JSON.stringify(item.run_id)},"solution_sha256":${JSON.stringify(item.solution_sha256)},"valid":true,"mae":${item.mae.toFixed(6)},"rows":${item.rows}}`,
  );
  return `{"results":[${rows.join(",")}]}`;
}

async function executeAction(
  pi: ExtensionAPI,
  binding: ControllerExtensionBinding,
  action: ControllerToolName,
  rawArguments: unknown,
  signal: AbortSignal | undefined,
) {
  assertToolSurface(pi);
  const arguments_ = validateArguments(action, rawArguments, binding.limits);
  const result = await runBridge(binding, { action, arguments: arguments_ }, signal);
  return {
    content: [{ type: "text" as const, text: formatResult(action, result) }],
    details: { action },
  };
}

export function createControllerExtension(rawBinding: ControllerExtensionBinding): ExtensionFactory {
  const binding = validateBinding(rawBinding);
  return (pi: ExtensionAPI): void => {
    const pathSchema = Type.String({ pattern: "^(?:solution\\.py|research\\.md|intent\\.json)$", maxLength: 32 });
    const hashSchema = Type.String({ pattern: "^[0-9a-f]{64}$", minLength: 64, maxLength: 64 });
    const uuidSchema = Type.String({
      pattern: "^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$",
      minLength: 36,
      maxLength: 36,
    });

    pi.registerTool({
      name: "read_solution",
      label: "Read solution source",
      description: "Read one current allowlisted solution source file through the fixed trusted bridge.",
      parameters: Type.Object({ path: pathSchema }, { additionalProperties: false }),
      execute: (_id, params, signal) => executeAction(pi, binding, "read_solution", params, signal),
    });
    pi.registerTool({
      name: "write_solution",
      label: "Write solution source",
      description: "Atomically write one current allowlisted solution source file through the fixed trusted bridge.",
      parameters: Type.Object(
        {
          path: pathSchema,
          content: Type.String({ maxLength: binding.limits.maxSourceContentBytes }),
          expected_sha256: Type.Optional(hashSchema),
        },
        { additionalProperties: false },
      ),
      execute: (_id, params, signal) => executeAction(pi, binding, "write_solution", params, signal),
    });
    pi.registerTool({
      name: "request_R1_run",
      label: "Request R1 run",
      description: "Request the current immutable intent through the at-most-once trusted bridge fence.",
      parameters: Type.Object({}, { additionalProperties: false }),
      executionMode: "sequential",
      execute: (_id, params, signal) => executeAction(pi, binding, "request_R1_run", params, signal),
    });
    pi.registerTool({
      name: "read_public_result",
      label: "Read public run state",
      description: "Read bounded public run identities and status from the trusted bridge.",
      parameters: Type.Object({}, { additionalProperties: false }),
      execute: (_id, params, signal) => executeAction(pi, binding, "read_public_result", params, signal),
    });
    pi.registerTool({
      name: "read_dev_result",
      label: "Read development result",
      description: "Read only bounded aggregate development MAE receipts from the trusted bridge.",
      parameters: Type.Object({}, { additionalProperties: false }),
      execute: (_id, params, signal) => executeAction(pi, binding, "read_dev_result", params, signal),
    });
    pi.registerTool({
      name: "lock_final_artifact",
      label: "Lock final artifact",
      description: "Lock one eligible artifact identity after final-refit prediction through the trusted bridge.",
      parameters: Type.Object({ run_id: uuidSchema, artifact_sha256: hashSchema }, { additionalProperties: false }),
      executionMode: "sequential",
      execute: (_id, params, signal) => executeAction(pi, binding, "lock_final_artifact", params, signal),
    });
  };
}

function readRegularNoFollow(path: string, maximumBytes: number): Buffer {
  let descriptor: number | undefined;
  try {
    descriptor = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW);
    const stat = fstatSync(descriptor);
    if (!stat.isFile() || stat.nlink !== 1 || stat.size <= 0 || stat.size > maximumBytes) fail("INTERNAL_ERROR");
    const bytes = readFileSync(descriptor);
    if (bytes.length !== stat.size) fail("INTERNAL_ERROR");
    return bytes;
  } catch (error) {
    if (error instanceof BoundaryError) throw error;
    return fail("INTERNAL_ERROR");
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function loadDefaultBinding(): ControllerExtensionBinding {
  const extensionPath = fileURLToPath(import.meta.url);
  const bindingPath = join(dirname(extensionPath), "controller-extension.binding.json");
  const bindingBytes = readRegularNoFollow(bindingPath, MAX_BINDING_BYTES);
  let parsed: unknown;
  try {
    parsed = JSON.parse(bindingBytes.toString("utf8")) as unknown;
  } catch {
    fail("INTERNAL_ERROR");
  }
  const binding = validateBinding(parsed);
  const extensionBytes = readRegularNoFollow(extensionPath, 1048576);
  const actualSha256 = createHash("sha256").update(extensionBytes).digest("hex");
  if (actualSha256 !== binding.expectedExtensionSha256) fail("INTERNAL_ERROR");
  return binding;
}

export default function controllerExtension(pi: ExtensionAPI): void {
  createControllerExtension(loadDefaultBinding())(pi);
}
