import { createHash } from "node:crypto";
import {
  closeSync,
  constants,
  existsSync,
  fstatSync,
  lstatSync,
  openSync,
  readFileSync,
  readlinkSync,
  readdirSync,
  readSync,
  realpathSync,
} from "node:fs";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionFactory } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { main as primeMain } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";

const DEPLOYMENT_SCHEMA = "argo-house-price-a2-controller-main-deployment/v1";
const DEPLOYMENT_STATUS = "TRUSTED_FIXED_DEPLOYMENT";
const PRIME_ENTRY_PATH = "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
const MAX_DEPLOYMENT_BYTES = 65536;
const MAX_SMALL_ASSET_BYTES = 1048576;
const MAX_EXECUTABLE_BYTES = 268435456;
const MAX_SOURCE_BYTES = 131072;
const EXPECTED_ENVIRONMENT_KEYS = [
  "LANG",
  "LC_ALL",
  "PATH",
  "PRIME_AGENT_CODING_AGENT_DIR",
  "PRIME_AGENT_KERNEL_PYTHON",
  "PRIME_AGENT_TELEMETRY",
  "TMPDIR",
  "TZ",
] as const;
const TOOL_NAMES = [
  "read_solution",
  "write_solution",
  "request_R1_run",
  "read_public_result",
  "read_dev_result",
  "lock_final_artifact",
] as const;
const HEX64 = /^[0-9a-f]{64}$/;
const DECIMAL_INTEGER = /^(?:0|[1-9][0-9]*)$/;
const MODEL_SELECTOR = /^openai-codex\/[A-Za-z0-9._:-]+$/;
const SAFE_GATE_PATH = /^[A-Za-z0-9_./-]+$/;
const BRIDGE_BINDING_SCHEMA = "argo-house-price-controller-extension-binding/v1";
const ENV_PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin";

type ControllerToolName = (typeof TOOL_NAMES)[number];
type ThinkingLevel = "off" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max";
type Phase = "dev" | "final_refit";
type SafeFrontendError =
  | "A2_ARGUMENT"
  | "A2_DEPLOYMENT"
  | "A2_ENVIRONMENT"
  | "A2_ASSET"
  | "A2_DIRECTORY"
  | "A2_SETTINGS"
  | "A2_RUNTIME"
  | "A2_MAIN_FAILED"
  | "A2_SESSION_EVIDENCE"
  | "A2_POSTFLIGHT";

interface FileSeal {
  path: string;
  sha256: string;
  bytes: number;
  mtime_ns_max: string;
}

interface LinkIdentity {
  device: string;
  inode: string;
  mtime_ns_max: string;
  link_target: string;
}

interface KernelInterpreterSeal {
  invocation_path: string;
  invocation_link: LinkIdentity;
  resolved_target: FileSeal;
  pyvenv_cfg: FileSeal;
}

interface DirectorySeal {
  path: string;
  realpath: string;
  device: string;
  inode: string;
  mtime_ns_max: string;
  mode_octal: string;
  must_be_empty: boolean;
}

interface ControllerDeployment {
  schema_version: typeof DEPLOYMENT_SCHEMA;
  status: typeof DEPLOYMENT_STATUS;
  assets: {
    prime_entry: FileSeal;
    prime_closure_manifest: FileSeal;
    controller_main: FileSeal;
    frontend_closure_manifest: FileSeal;
    extension: FileSeal;
    binding: FileSeal;
    settings: FileSeal;
    system_prompt: FileSeal;
    task_prompt: FileSeal;
    autonomous_gate: FileSeal;
    node_executable: FileSeal;
    kernel_interpreter: KernelInterpreterSeal;
  };
  directories: {
    artifact_root: DirectorySeal;
    cwd: DirectorySeal;
    profile: DirectorySeal;
    session_dir: DirectorySeal;
    temporary_dir: DirectorySeal;
  };
  runtime: {
    phase: Phase;
    model: string;
    thinking: ThinkingLevel;
    mode: "text";
    print: true;
    offline: true;
    fresh_session: true;
    tools: ControllerToolName[];
  };
  environment: {
    exact: Record<(typeof EXPECTED_ENVIRONMENT_KEYS)[number], string>;
    home_must_be_unset: true;
    forbidden_prefixes: ["PRIME_AGENT_INTERNAL_"];
  };
  limits: {
    provider_timeout_ms: 120000;
    provider_retries: 0;
    phase_wall_seconds: 3600;
    campaign_wall_seconds: 10800;
    cpu_seconds_per_process: 600;
    file_size_bytes: 8388608;
    rss_trigger_bytes: 2147483648;
    rss_sample_ms: 250;
    v8_old_space_mib: 1024;
    model_tokens_between_turns: 120000;
    controller_turn_limit_per_phase: 20;
    source_text_max_bytes: 131072;
    bridge_close_grace_ms: 1000;
    autonomous_max_continuations: 20;
    autonomous_gate_retries: 20;
    autonomous_gate_timeout_ms: 30000;
  };
}

export interface PreparedControllerMain {
  deployment: ControllerDeployment;
  mainArgs: string[];
  fixedFactories: [ExtensionFactory];
  verifyPostflight(): void;
}

class FrontendError extends Error {
  readonly safeCode: SafeFrontendError;

  constructor(safeCode: SafeFrontendError) {
    super(safeCode);
    this.name = "FrontendError";
    this.safeCode = safeCode;
  }
}

function fail(code: SafeFrontendError): never {
  throw new FrontendError(code);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(record: Record<string, unknown>, keys: readonly string[]): boolean {
  const actual = Object.keys(record);
  return actual.length === keys.length && keys.every((key) => Object.hasOwn(record, key));
}

function hasValidUnicode(value: string): boolean {
  if (value.includes("\0")) return false;
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) return false;
      index += 1;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      return false;
    }
  }
  return true;
}

function assertCanonicalAbsolutePath(path: unknown, code: SafeFrontendError): asserts path is string {
  if (
    typeof path !== "string" ||
    !hasValidUnicode(path) ||
    !isAbsolute(path) ||
    resolve(path) !== path ||
    Buffer.byteLength(path, "utf8") > 4096
  ) {
    fail(code);
  }
}

function parseDecimalBigInt(value: unknown, code: SafeFrontendError): bigint {
  if (typeof value !== "string" || value.length > 30 || !DECIMAL_INTEGER.test(value)) fail(code);
  return BigInt(value);
}

function assertCanonicalParent(path: string): void {
  const parent = dirname(path);
  try {
    if (realpathSync.native(parent) !== parent) fail("A2_ASSET");
    const stat = lstatSync(parent, { bigint: true });
    if (!stat.isDirectory() || stat.isSymbolicLink()) fail("A2_ASSET");
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    fail("A2_ASSET");
  }
}

function validateFileSeal(value: unknown): FileSeal {
  if (!isRecord(value) || !hasExactKeys(value, ["path", "sha256", "bytes", "mtime_ns_max"])) fail("A2_DEPLOYMENT");
  assertCanonicalAbsolutePath(value.path, "A2_DEPLOYMENT");
  if (typeof value.sha256 !== "string" || !HEX64.test(value.sha256)) fail("A2_DEPLOYMENT");
  if (typeof value.bytes !== "number" || !Number.isSafeInteger(value.bytes) || value.bytes < 0) fail("A2_DEPLOYMENT");
  if (typeof value.mtime_ns_max !== "string") fail("A2_DEPLOYMENT");
  parseDecimalBigInt(value.mtime_ns_max, "A2_DEPLOYMENT");
  return { path: value.path, sha256: value.sha256, bytes: value.bytes, mtime_ns_max: value.mtime_ns_max };
}

function validateLinkIdentity(value: unknown): LinkIdentity {
  if (!isRecord(value) || !hasExactKeys(value, ["device", "inode", "mtime_ns_max", "link_target"])) fail("A2_DEPLOYMENT");
  if (typeof value.device !== "string" || typeof value.inode !== "string" || typeof value.mtime_ns_max !== "string") {
    fail("A2_DEPLOYMENT");
  }
  parseDecimalBigInt(value.device, "A2_DEPLOYMENT");
  parseDecimalBigInt(value.inode, "A2_DEPLOYMENT");
  parseDecimalBigInt(value.mtime_ns_max, "A2_DEPLOYMENT");
  if (typeof value.link_target !== "string" || !hasValidUnicode(value.link_target) || Buffer.byteLength(value.link_target) > 4096) {
    fail("A2_DEPLOYMENT");
  }
  return {
    device: value.device,
    inode: value.inode,
    mtime_ns_max: value.mtime_ns_max,
    link_target: value.link_target,
  };
}

function validateKernelSeal(value: unknown): KernelInterpreterSeal {
  if (!isRecord(value) || !hasExactKeys(value, ["invocation_path", "invocation_link", "resolved_target", "pyvenv_cfg"])) {
    fail("A2_DEPLOYMENT");
  }
  assertCanonicalAbsolutePath(value.invocation_path, "A2_DEPLOYMENT");
  return {
    invocation_path: value.invocation_path,
    invocation_link: validateLinkIdentity(value.invocation_link),
    resolved_target: validateFileSeal(value.resolved_target),
    pyvenv_cfg: validateFileSeal(value.pyvenv_cfg),
  };
}

function validateDirectorySeal(value: unknown): DirectorySeal {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["path", "realpath", "device", "inode", "mtime_ns_max", "mode_octal", "must_be_empty"])
  ) {
    fail("A2_DEPLOYMENT");
  }
  assertCanonicalAbsolutePath(value.path, "A2_DEPLOYMENT");
  assertCanonicalAbsolutePath(value.realpath, "A2_DEPLOYMENT");
  if (typeof value.device !== "string" || typeof value.inode !== "string" || typeof value.mtime_ns_max !== "string") {
    fail("A2_DEPLOYMENT");
  }
  parseDecimalBigInt(value.device, "A2_DEPLOYMENT");
  parseDecimalBigInt(value.inode, "A2_DEPLOYMENT");
  parseDecimalBigInt(value.mtime_ns_max, "A2_DEPLOYMENT");
  if (typeof value.mode_octal !== "string" || !/^0[0-7]{3}$/.test(value.mode_octal)) fail("A2_DEPLOYMENT");
  if (typeof value.must_be_empty !== "boolean") fail("A2_DEPLOYMENT");
  return {
    path: value.path,
    realpath: value.realpath,
    device: value.device,
    inode: value.inode,
    mtime_ns_max: value.mtime_ns_max,
    mode_octal: value.mode_octal,
    must_be_empty: value.must_be_empty,
  };
}

function readAndHashFile(seal: FileSeal, maximumBytes: number, returnBytes = false): Buffer | undefined {
  assertCanonicalParent(seal.path);
  if (seal.bytes > maximumBytes) fail("A2_ASSET");
  let descriptor: number | undefined;
  try {
    descriptor = openSync(seal.path, constants.O_RDONLY | constants.O_NOFOLLOW);
    const before = fstatSync(descriptor, { bigint: true });
    if (!before.isFile() || before.nlink !== 1n || before.size !== BigInt(seal.bytes)) fail("A2_ASSET");
    if (before.mtimeNs > parseDecimalBigInt(seal.mtime_ns_max, "A2_ASSET")) fail("A2_ASSET");
    const hash = createHash("sha256");
    const chunks: Buffer[] = [];
    const buffer = Buffer.allocUnsafe(65536);
    let total = 0;
    while (total < seal.bytes) {
      const count = readSync(descriptor, buffer, 0, Math.min(buffer.length, seal.bytes - total), null);
      if (count <= 0) fail("A2_ASSET");
      const chunk = buffer.subarray(0, count);
      hash.update(chunk);
      if (returnBytes) chunks.push(Buffer.from(chunk));
      total += count;
    }
    if (readSync(descriptor, buffer, 0, 1, null) !== 0) fail("A2_ASSET");
    const after = fstatSync(descriptor, { bigint: true });
    if (
      after.dev !== before.dev ||
      after.ino !== before.ino ||
      after.size !== before.size ||
      after.mtimeNs !== before.mtimeNs ||
      hash.digest("hex") !== seal.sha256
    ) {
      fail("A2_ASSET");
    }
    return returnBytes ? Buffer.concat(chunks, seal.bytes) : undefined;
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    fail("A2_ASSET");
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function readUtf8Asset(seal: FileSeal, maximumBytes: number): string {
  const bytes = readAndHashFile(seal, maximumBytes, true);
  if (!bytes) fail("A2_ASSET");
  const text = bytes.toString("utf8");
  if (!Buffer.from(text, "utf8").equals(bytes) || !hasValidUnicode(text)) fail("A2_ASSET");
  return text;
}

function readDeploymentFile(path: string): string {
  assertCanonicalAbsolutePath(path, "A2_ARGUMENT");
  assertCanonicalParent(path);
  let descriptor: number | undefined;
  try {
    descriptor = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW);
    const stat = fstatSync(descriptor, { bigint: true });
    if (!stat.isFile() || stat.nlink !== 1n || stat.size <= 0n || stat.size > BigInt(MAX_DEPLOYMENT_BYTES)) {
      fail("A2_DEPLOYMENT");
    }
    const bytes = readFileSync(descriptor);
    if (BigInt(bytes.length) !== stat.size) fail("A2_DEPLOYMENT");
    const text = bytes.toString("utf8");
    if (!Buffer.from(text, "utf8").equals(bytes) || !hasValidUnicode(text)) fail("A2_DEPLOYMENT");
    return text;
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    return fail("A2_DEPLOYMENT");
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function assertDirectory(seal: DirectorySeal, checkMtime = true): void {
  try {
    const stat = lstatSync(seal.path, { bigint: true });
    if (!stat.isDirectory() || stat.isSymbolicLink() || realpathSync.native(seal.path) !== seal.realpath || seal.path !== seal.realpath) {
      fail("A2_DIRECTORY");
    }
    if (stat.dev !== parseDecimalBigInt(seal.device, "A2_DIRECTORY") || stat.ino !== parseDecimalBigInt(seal.inode, "A2_DIRECTORY")) {
      fail("A2_DIRECTORY");
    }
    if (checkMtime && stat.mtimeNs > parseDecimalBigInt(seal.mtime_ns_max, "A2_DIRECTORY")) fail("A2_DIRECTORY");
    const actualMode = `0${(Number(stat.mode) & 0o777).toString(8).padStart(3, "0")}`;
    if (actualMode !== seal.mode_octal) fail("A2_DIRECTORY");
    if (seal.must_be_empty && readdirSync(seal.path).length !== 0) fail("A2_DIRECTORY");
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    fail("A2_DIRECTORY");
  }
}

function isStrictDescendant(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path.length > 0 && !path.startsWith("..") && !isAbsolute(path);
}

function validateRuntime(value: unknown): ControllerDeployment["runtime"] {
  if (!isRecord(value) || !hasExactKeys(value, ["phase", "model", "thinking", "mode", "print", "offline", "fresh_session", "tools"])) {
    fail("A2_DEPLOYMENT");
  }
  if (value.phase !== "dev" && value.phase !== "final_refit") fail("A2_RUNTIME");
  if (typeof value.model !== "string" || !MODEL_SELECTOR.test(value.model)) fail("A2_RUNTIME");
  if (
    value.thinking !== "off" &&
    value.thinking !== "minimal" &&
    value.thinking !== "low" &&
    value.thinking !== "medium" &&
    value.thinking !== "high" &&
    value.thinking !== "xhigh" &&
    value.thinking !== "max"
  ) {
    fail("A2_RUNTIME");
  }
  if (value.mode !== "text" || value.print !== true || value.offline !== true || value.fresh_session !== true) fail("A2_RUNTIME");
  if (!Array.isArray(value.tools) || value.tools.length !== TOOL_NAMES.length || !value.tools.every((name, index) => name === TOOL_NAMES[index])) {
    fail("A2_RUNTIME");
  }
  return {
    phase: value.phase,
    model: value.model,
    thinking: value.thinking,
    mode: "text",
    print: true,
    offline: true,
    fresh_session: true,
    tools: [...TOOL_NAMES],
  };
}

function validateEnvironment(value: unknown): ControllerDeployment["environment"] {
  if (!isRecord(value) || !hasExactKeys(value, ["exact", "home_must_be_unset", "forbidden_prefixes"])) fail("A2_DEPLOYMENT");
  if (!isRecord(value.exact) || !hasExactKeys(value.exact, EXPECTED_ENVIRONMENT_KEYS)) fail("A2_ENVIRONMENT");
  for (const key of EXPECTED_ENVIRONMENT_KEYS) {
    if (typeof value.exact[key] !== "string" || !hasValidUnicode(value.exact[key] as string)) fail("A2_ENVIRONMENT");
  }
  if (value.home_must_be_unset !== true || !Array.isArray(value.forbidden_prefixes) || value.forbidden_prefixes.length !== 1 || value.forbidden_prefixes[0] !== "PRIME_AGENT_INTERNAL_") {
    fail("A2_ENVIRONMENT");
  }
  return {
    exact: value.exact as ControllerDeployment["environment"]["exact"],
    home_must_be_unset: true,
    forbidden_prefixes: ["PRIME_AGENT_INTERNAL_"],
  };
}

function validateLimits(value: unknown): ControllerDeployment["limits"] {
  const expected = {
    provider_timeout_ms: 120000,
    provider_retries: 0,
    phase_wall_seconds: 3600,
    campaign_wall_seconds: 10800,
    cpu_seconds_per_process: 600,
    file_size_bytes: 8388608,
    rss_trigger_bytes: 2147483648,
    rss_sample_ms: 250,
    v8_old_space_mib: 1024,
    model_tokens_between_turns: 120000,
    controller_turn_limit_per_phase: 20,
    source_text_max_bytes: 131072,
    bridge_close_grace_ms: 1000,
    autonomous_max_continuations: 20,
    autonomous_gate_retries: 20,
    autonomous_gate_timeout_ms: 30000,
  } as const;
  if (!isRecord(value) || !hasExactKeys(value, Object.keys(expected))) fail("A2_DEPLOYMENT");
  for (const [key, expectedValue] of Object.entries(expected)) {
    if (value[key] !== expectedValue) fail("A2_RUNTIME");
  }
  return expected;
}

function validateDeployment(value: unknown): ControllerDeployment {
  if (!isRecord(value) || !hasExactKeys(value, ["schema_version", "status", "assets", "directories", "runtime", "environment", "limits"])) {
    fail("A2_DEPLOYMENT");
  }
  if (value.schema_version !== DEPLOYMENT_SCHEMA || value.status !== DEPLOYMENT_STATUS) fail("A2_DEPLOYMENT");
  if (!isRecord(value.assets) || !hasExactKeys(value.assets, [
    "prime_entry",
    "prime_closure_manifest",
    "controller_main",
    "frontend_closure_manifest",
    "extension",
    "binding",
    "settings",
    "system_prompt",
    "task_prompt",
    "autonomous_gate",
    "node_executable",
    "kernel_interpreter",
  ])) {
    fail("A2_DEPLOYMENT");
  }
  if (!isRecord(value.directories) || !hasExactKeys(value.directories, ["artifact_root", "cwd", "profile", "session_dir", "temporary_dir"])) {
    fail("A2_DEPLOYMENT");
  }
  return {
    schema_version: DEPLOYMENT_SCHEMA,
    status: DEPLOYMENT_STATUS,
    assets: {
      prime_entry: validateFileSeal(value.assets.prime_entry),
      prime_closure_manifest: validateFileSeal(value.assets.prime_closure_manifest),
      controller_main: validateFileSeal(value.assets.controller_main),
      frontend_closure_manifest: validateFileSeal(value.assets.frontend_closure_manifest),
      extension: validateFileSeal(value.assets.extension),
      binding: validateFileSeal(value.assets.binding),
      settings: validateFileSeal(value.assets.settings),
      system_prompt: validateFileSeal(value.assets.system_prompt),
      task_prompt: validateFileSeal(value.assets.task_prompt),
      autonomous_gate: validateFileSeal(value.assets.autonomous_gate),
      node_executable: validateFileSeal(value.assets.node_executable),
      kernel_interpreter: validateKernelSeal(value.assets.kernel_interpreter),
    },
    directories: {
      artifact_root: validateDirectorySeal(value.directories.artifact_root),
      cwd: validateDirectorySeal(value.directories.cwd),
      profile: validateDirectorySeal(value.directories.profile),
      session_dir: validateDirectorySeal(value.directories.session_dir),
      temporary_dir: validateDirectorySeal(value.directories.temporary_dir),
    },
    runtime: validateRuntime(value.runtime),
    environment: validateEnvironment(value.environment),
    limits: validateLimits(value.limits),
  };
}

function assertKernelInterpreter(seal: KernelInterpreterSeal): void {
  assertCanonicalAbsolutePath(seal.invocation_path, "A2_ASSET");
  assertCanonicalParent(seal.invocation_path);
  try {
    const link = lstatSync(seal.invocation_path, { bigint: true });
    if (!link.isSymbolicLink()) fail("A2_ASSET");
    if (
      link.dev !== parseDecimalBigInt(seal.invocation_link.device, "A2_ASSET") ||
      link.ino !== parseDecimalBigInt(seal.invocation_link.inode, "A2_ASSET") ||
      link.mtimeNs > parseDecimalBigInt(seal.invocation_link.mtime_ns_max, "A2_ASSET") ||
      readlinkSync(seal.invocation_path) !== seal.invocation_link.link_target ||
      realpathSync.native(seal.invocation_path) !== seal.resolved_target.path
    ) {
      fail("A2_ASSET");
    }
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    fail("A2_ASSET");
  }
  const venvRoot = dirname(dirname(seal.invocation_path));
  if (seal.pyvenv_cfg.path !== join(venvRoot, "pyvenv.cfg")) fail("A2_ASSET");
  readAndHashFile(seal.resolved_target, MAX_EXECUTABLE_BYTES);
  readAndHashFile(seal.pyvenv_cfg, MAX_DEPLOYMENT_BYTES);
}

function parseJsonObject(text: string, code: SafeFrontendError): Record<string, unknown> {
  let value: unknown;
  try {
    value = JSON.parse(text) as unknown;
  } catch {
    fail(code);
  }
  if (!isRecord(value)) fail(code);
  return value;
}

function assertSettings(text: string): void {
  const settings = parseJsonObject(text, "A2_SETTINGS");
  if (!hasExactKeys(settings, ["retry"]) || !isRecord(settings.retry) || !hasExactKeys(settings.retry, ["enabled", "provider"])) {
    fail("A2_SETTINGS");
  }
  if (settings.retry.enabled !== false || !isRecord(settings.retry.provider) || !hasExactKeys(settings.retry.provider, ["timeoutMs", "maxRetries"])) {
    fail("A2_SETTINGS");
  }
  if (settings.retry.provider.timeoutMs !== 120000 || settings.retry.provider.maxRetries !== 0) fail("A2_SETTINGS");
}

function assertBinding(text: string, extensionSha256: string): void {
  const binding = parseJsonObject(text, "A2_ASSET");
  if (
    binding.schemaVersion !== BRIDGE_BINDING_SCHEMA ||
    binding.expectedExtensionSha256 !== extensionSha256 ||
    !isRecord(binding.limits) ||
    binding.limits.bridgeTimeoutMs !== 30000 ||
    binding.limits.maxRows !== 292
  ) {
    fail("A2_ASSET");
  }
}

function assertEnvironment(
  deployment: ControllerDeployment,
  environment: NodeJS.ProcessEnv,
  execArgv: readonly string[],
  platform: NodeJS.Platform,
): void {
  const expected = {
    PRIME_AGENT_CODING_AGENT_DIR: deployment.directories.profile.path,
    PRIME_AGENT_KERNEL_PYTHON: deployment.assets.kernel_interpreter.invocation_path,
    PRIME_AGENT_TELEMETRY: "0",
    PATH: ENV_PATH,
    TMPDIR: `${deployment.directories.temporary_dir.path}/`,
    LANG: "C.UTF-8",
    LC_ALL: "C.UTF-8",
    TZ: "UTC",
  };
  if (!hasExactKeys(deployment.environment.exact, EXPECTED_ENVIRONMENT_KEYS)) fail("A2_ENVIRONMENT");
  for (const key of EXPECTED_ENVIRONMENT_KEYS) {
    if (deployment.environment.exact[key] !== expected[key]) fail("A2_ENVIRONMENT");
  }
  const actualKeys = Object.keys(environment).sort();
  const extraKeys = actualKeys.filter((key) => !EXPECTED_ENVIRONMENT_KEYS.includes(key as (typeof EXPECTED_ENVIRONMENT_KEYS)[number]));
  if (!EXPECTED_ENVIRONMENT_KEYS.every((key) => actualKeys.includes(key))) fail("A2_ENVIRONMENT");
  if (extraKeys.length > 1 || (extraKeys.length === 1 && extraKeys[0] !== "__CF_USER_TEXT_ENCODING")) {
    fail("A2_ENVIRONMENT");
  }
  if (extraKeys.length === 1) {
    const cfValue = environment.__CF_USER_TEXT_ENCODING;
    if (
      platform !== "darwin" ||
      typeof cfValue !== "string" ||
      Buffer.byteLength(cfValue, "ascii") > 128 ||
      !/^[\x20-\x7e]*$/.test(cfValue)
    ) {
      fail("A2_ENVIRONMENT");
    }
  }
  for (const key of EXPECTED_ENVIRONMENT_KEYS) {
    if (environment[key] !== expected[key]) fail("A2_ENVIRONMENT");
  }
  if (Object.hasOwn(environment, "HOME") || actualKeys.some((key) => key.startsWith("PRIME_AGENT_INTERNAL_") || key.startsWith("PI_"))) {
    fail("A2_ENVIRONMENT");
  }
  if (execArgv.length !== 1 || execArgv[0] !== "--max-old-space-size=1024") fail("A2_ENVIRONMENT");
}

function assertProfileHasNoStaleResources(profilePath: string, cwd: string): void {
  const allowed = new Set(["auth.json", "settings.json"]);
  const entries = readdirSync(profilePath);
  if (entries.some((entry) => !allowed.has(entry))) fail("A2_DIRECTORY");
  if (existsSync(join(cwd, ".prime"))) fail("A2_DIRECTORY");
}

function verifyFixedAssets(deployment: ControllerDeployment): { systemPrompt: string; taskPrompt: string } {
  const assets = deployment.assets;
  if (assets.prime_entry.path !== PRIME_ENTRY_PATH) fail("A2_ASSET");
  if (assets.controller_main.path !== fileURLToPath(import.meta.url)) fail("A2_ASSET");
  if (assets.node_executable.path !== process.execPath) fail("A2_ASSET");
  if (assets.binding.path !== join(dirname(assets.extension.path), "controller-extension.binding.json")) fail("A2_ASSET");
  if (assets.settings.path !== join(deployment.directories.profile.path, "settings.json")) fail("A2_SETTINGS");
  readAndHashFile(assets.prime_entry, MAX_SMALL_ASSET_BYTES);
  readAndHashFile(assets.prime_closure_manifest, MAX_SMALL_ASSET_BYTES);
  readAndHashFile(assets.controller_main, MAX_SMALL_ASSET_BYTES);
  readAndHashFile(assets.frontend_closure_manifest, MAX_SMALL_ASSET_BYTES);
  readAndHashFile(assets.extension, MAX_SMALL_ASSET_BYTES);
  const binding = readUtf8Asset(assets.binding, MAX_DEPLOYMENT_BYTES);
  const settings = readUtf8Asset(assets.settings, MAX_DEPLOYMENT_BYTES);
  const systemPrompt = readUtf8Asset(assets.system_prompt, MAX_SOURCE_BYTES);
  const taskPrompt = readUtf8Asset(assets.task_prompt, MAX_SOURCE_BYTES);
  readAndHashFile(assets.autonomous_gate, MAX_SMALL_ASSET_BYTES);
  readAndHashFile(assets.node_executable, MAX_EXECUTABLE_BYTES);
  assertKernelInterpreter(assets.kernel_interpreter);
  assertBinding(binding, assets.extension.sha256);
  assertSettings(settings);
  if (!systemPrompt.trim() || !taskPrompt.trim() || existsSync(systemPrompt)) fail("A2_ASSET");
  try {
    const gate = lstatSync(assets.autonomous_gate.path, { bigint: true });
    if ((Number(gate.mode) & 0o111) === 0 || !SAFE_GATE_PATH.test(assets.autonomous_gate.path)) fail("A2_ASSET");
  } catch (error) {
    if (error instanceof FrontendError) throw error;
    fail("A2_ASSET");
  }
  return { systemPrompt, taskPrompt };
}


function assertOutsideGitRepository(cwd: string): void {
  let current = cwd;
  while (true) {
    if (existsSync(join(current, ".git"))) fail("A2_DIRECTORY");
    const parent = dirname(current);
    if (parent === current) return;
    current = parent;
  }
}

function verifyDirectories(deployment: ControllerDeployment, artifactRootArgument: string, deploymentPath: string): void {
  const directories = deployment.directories;
  assertDirectory(directories.artifact_root, false);
  assertDirectory(directories.cwd);
  assertDirectory(directories.profile);
  assertDirectory(directories.session_dir);
  assertDirectory(directories.temporary_dir);
  if (directories.artifact_root.path !== artifactRootArgument) fail("A2_ARGUMENT");
  if (directories.artifact_root.mode_octal !== "0700" || directories.profile.mode_octal !== "0700") fail("A2_DIRECTORY");
  if (
    directories.session_dir.mode_octal !== "0700" ||
    directories.temporary_dir.mode_octal !== "0700" ||
    directories.session_dir.must_be_empty !== true ||
    directories.temporary_dir.must_be_empty !== true ||
    directories.artifact_root.must_be_empty !== false ||
    directories.profile.must_be_empty !== false ||
    directories.cwd.must_be_empty !== false
  ) {
    fail("A2_DIRECTORY");
  }
  if (directories.temporary_dir.path !== join(directories.artifact_root.path, "tmp")) fail("A2_DIRECTORY");
  if (!isStrictDescendant(directories.artifact_root.path, directories.session_dir.path)) fail("A2_DIRECTORY");
  if (!isStrictDescendant(directories.artifact_root.path, deploymentPath)) fail("A2_DIRECTORY");
  if (isStrictDescendant(directories.artifact_root.path, directories.profile.path)) fail("A2_DIRECTORY");
  assertProfileHasNoStaleResources(directories.profile.path, directories.cwd.path);
  assertOutsideGitRepository(directories.cwd.path);
}

function parseFrontendArguments(argv: readonly string[]): { deploymentPath: string; artifactRoot: string } {
  if (argv.length !== 4 || argv[0] !== "--deployment" || argv[2] !== "--artifact-root") fail("A2_ARGUMENT");
  assertCanonicalAbsolutePath(argv[1], "A2_ARGUMENT");
  assertCanonicalAbsolutePath(argv[3], "A2_ARGUMENT");
  return { deploymentPath: argv[1], artifactRoot: argv[3] };
}

function fixedNoOpFactory(): void {}

export function prepareControllerMain(
  argv: readonly string[],
  environment: NodeJS.ProcessEnv,
  execArgv: readonly string[],
  platform: NodeJS.Platform = process.platform,
): PreparedControllerMain {
  const { deploymentPath, artifactRoot } = parseFrontendArguments(argv);
  const deployment = validateDeployment(parseJsonObject(readDeploymentFile(deploymentPath), "A2_DEPLOYMENT"));
  verifyDirectories(deployment, artifactRoot, deploymentPath);
  assertEnvironment(deployment, environment, execArgv, platform);
  const { systemPrompt, taskPrompt } = verifyFixedAssets(deployment);
  const mainArgs = [
    "--print",
    "--mode",
    "text",
    "--offline",
    "--cwd",
    deployment.directories.cwd.path,
    "--session-dir",
    deployment.directories.session_dir.path,
    "--model",
    deployment.runtime.model,
    "--thinking",
    deployment.runtime.thinking,
    "--no-builtin-tools",
    "--tools",
    TOOL_NAMES.join(","),
    "--no-extensions",
    "--extension",
    deployment.assets.extension.path,
    "--no-skills",
    "--no-prompt-templates",
    "--no-themes",
    "--no-context-files",
    "--system-prompt",
    systemPrompt,
    "--append-system-prompt",
    "",
    "--autonomous",
    "--autonomous-gate",
    deployment.assets.autonomous_gate.path,
    "--autonomous-gate-retries",
    "20",
    "--autonomous-gate-timeout-ms",
    "30000",
    "--autonomous-max-continuations",
    "20",
    "--autonomous-max-turns",
    "20",
    "--autonomous-max-tokens",
    "120000",
    "--autonomous-timeout-ms",
    "3600000",
    "--",
    taskPrompt,
  ];
  return {
    deployment,
    mainArgs,
    fixedFactories: [fixedNoOpFactory],
    verifyPostflight: () => {
      verifyFixedAssets(deployment);
    },
  };
}

async function executeControllerMain(): Promise<void> {
  let prepared: PreparedControllerMain;
  try {
    prepared = prepareControllerMain(process.argv.slice(2), process.env, process.execArgv);
  } catch (error) {
    const code = error instanceof FrontendError ? error.safeCode : "A2_DEPLOYMENT";
    process.stderr.write(`${code}
`);
    process.exitCode = 1;
    return;
  }
  try {
    await primeMain(prepared.mainArgs, { extensionFactories: prepared.fixedFactories });
    if (process.exitCode !== undefined && process.exitCode !== 0) fail("A2_MAIN_FAILED");
    prepared.verifyPostflight();
  } catch (error) {
    const code = error instanceof FrontendError ? error.safeCode : "A2_MAIN_FAILED";
    process.stderr.write(`${code}
`);
    process.exitCode = 1;
  }
}

const directPath = process.argv[1] ? resolve(process.argv[1]) : "";
if (directPath === fileURLToPath(import.meta.url)) {
  await executeControllerMain();
  process.exit(process.exitCode ?? 0);
}
