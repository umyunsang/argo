import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import {
  chmodSync,
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  realpathSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const RUNTIME_ROOT = resolve(HERE, "..");
const REPO_ROOT = resolve(RUNTIME_ROOT, "../../../..");
const TEST_ROOT = join(realpathSync.native(tmpdir()), "argo-house-price-a2-installed-main-probe");
const PROBE = join(HERE, "installed-main-faux-probe.ts");
const FAKE_BRIDGE = join(HERE, "fake-bridge.mjs");
const SOURCE_EXTENSION = join(RUNTIME_ROOT, "controller-extension.ts");
const KERNEL_INVOCATION = "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python";
const TOOLS = [
  "read_solution",
  "write_solution",
  "request_R1_run",
  "read_public_result",
  "read_dev_result",
  "lock_final_artifact",
];

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function allFiles(path: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(path, { withFileTypes: true })) {
    const child = join(path, entry.name);
    if (entry.isDirectory()) files.push(...allFiles(child));
    else if (entry.isFile()) files.push(child);
  }
  return files;
}

async function main(): Promise<void> {
  rmSync(TEST_ROOT, { recursive: true, force: true });
  const artifactRoot = join(TEST_ROOT, "artifacts");
  const temporaryDir = join(artifactRoot, "tmp");
  const cwd = join(TEST_ROOT, "public-cwd");
  const profile = join(TEST_ROOT, "profile");
  const sessionDir = join(artifactRoot, "session");
  const extensionDir = join(TEST_ROOT, "extension");
  for (const path of [TEST_ROOT, artifactRoot, temporaryDir, cwd, profile, sessionDir, extensionDir]) {
    mkdirSync(path, { recursive: true, mode: 0o700 });
    chmodSync(path, 0o700);
  }
  writeFileSync(join(profile, "settings.json"), JSON.stringify({
    retry: { enabled: false, provider: { timeoutMs: 120000, maxRetries: 0 } },
  }));
  const extensionPath = join(extensionDir, "controller-extension.ts");
  copyFileSync(SOURCE_EXTENSION, extensionPath);
  const bridgeRecordPath = join(artifactRoot, "bridge-record.jsonl");
  writeFileSync(join(extensionDir, "controller-extension.binding.json"), JSON.stringify({
    schemaVersion: "argo-house-price-controller-extension-binding/v1",
    expectedExtensionSha256: sha256(extensionPath),
    bridge: { command: process.execPath, argv: [FAKE_BRIDGE, bridgeRecordPath] },
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
  }));
  const capturePath = join(artifactRoot, "provider-capture.json");
  const daemonSocketPath = join(artifactRoot, "daemon-canary.sock");
  const configPath = join(artifactRoot, "probe-config.json");
  writeFileSync(configPath, JSON.stringify({ cwd, sessionDir, extensionPath, daemonSocketPath, capturePath }));
  const stdoutPath = join(artifactRoot, "stdout.txt");
  const stderrPath = join(artifactRoot, "stderr.txt");
  const startedAt = Date.now();
  const child = spawn(process.execPath, ["--max-old-space-size=1024", PROBE, configPath], {
    cwd: REPO_ROOT,
    shell: false,
    stdio: ["ignore", "pipe", "pipe"],
    env: {
      PRIME_AGENT_CODING_AGENT_DIR: profile,
      PRIME_AGENT_KERNEL_PYTHON: KERNEL_INVOCATION,
      PRIME_AGENT_TELEMETRY: "0",
      PATH: "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
      TMPDIR: `${temporaryDir}/`,
      LANG: "C.UTF-8",
      LC_ALL: "C.UTF-8",
      TZ: "UTC",
    },
  });
  const stdout: Buffer[] = [];
  const stderr: Buffer[] = [];
  child.stdout.on("data", (chunk: Buffer) => stdout.push(Buffer.from(chunk)));
  child.stderr.on("data", (chunk: Buffer) => stderr.push(Buffer.from(chunk)));
  let timedOut = false;
  const deadline = setTimeout(() => {
    timedOut = true;
    child.kill("SIGKILL");
  }, 20000);
  const exitCode = await new Promise<number | null>((resolvePromise, rejectPromise) => {
    child.on("error", rejectPromise);
    child.on("close", resolvePromise);
  });
  clearTimeout(deadline);
  const elapsedMs = Date.now() - startedAt;
  const stdoutText = Buffer.concat(stdout).toString("utf8");
  const stderrText = Buffer.concat(stderr).toString("utf8");
  writeFileSync(stdoutPath, stdoutText);
  writeFileSync(stderrPath, stderrText);

  assert.equal(timedOut, false);
  assert.equal(exitCode, 0, stderrText);
  assert.ok(elapsedMs < 20000);
  assert.ok(Buffer.byteLength(stdoutText) <= 1048576);
  assert.ok(Buffer.byteLength(stderrText) <= 1048576);
  assert.equal(stdoutText, "A2 synthetic probe complete\n");
  assert.equal(stderrText, "");
  assert.equal(existsSync(daemonSocketPath), false);
  const syntheticAuthPath = join(profile, "auth.json");
  assert.equal(existsSync(syntheticAuthPath), true);
  const syntheticAuthStat = lstatSync(syntheticAuthPath);
  assert.ok(syntheticAuthStat.isFile());
  assert.equal(syntheticAuthStat.mode & 0o777, 0o600);
  assert.equal(existsSync(join(profile, "kernel-venv")), false);

  const capture = JSON.parse(readFileSync(capturePath, "utf8")) as {
    fauxCalls: number;
    captures: Array<{ tools?: Array<{ name: string; parameters: { additionalProperties?: unknown } }> }>;
    audits: Array<{ activeTools: string[]; tools: Array<{ name: string; sourcePath: string }> }>;
    initialEnvironmentKeys: string[];
    finalEnvironmentKeys: string[];
    error?: string;
  };
  assert.equal(capture.error, undefined);
  assert.equal(capture.fauxCalls, 2);
  assert.deepEqual(capture.initialEnvironmentKeys, [
    "LANG", "LC_ALL", "PATH", "PRIME_AGENT_CODING_AGENT_DIR", "PRIME_AGENT_KERNEL_PYTHON",
    "PRIME_AGENT_TELEMETRY", "TMPDIR", "TZ", "__CF_USER_TEXT_ENCODING",
  ]);
  assert.deepEqual(capture.finalEnvironmentKeys, [
    "LANG", "LC_ALL", "PATH", "PI_OFFLINE", "PI_SKIP_VERSION_CHECK", "PRIME_AGENT_CODING_AGENT_DIR",
    "PRIME_AGENT_KERNEL_PYTHON", "PRIME_AGENT_TELEMETRY", "TMPDIR", "TZ", "__CF_USER_TEXT_ENCODING",
  ]);
  for (const context of capture.captures) {
    assert.deepEqual(context.tools?.map((tool) => tool.name), TOOLS);
    assert.ok(context.tools?.every((tool) => tool.parameters.additionalProperties === false));
  }
  assert.deepEqual(capture.audits[0]?.activeTools, TOOLS);
  assert.deepEqual(
    [...new Set(capture.audits[0]?.tools.filter((tool) => TOOLS.includes(tool.name)).map((tool) => resolve(tool.sourcePath)))],
    [resolve(extensionPath)],
  );
  const bridgeRequests = readFileSync(bridgeRecordPath, "utf8").trim().split("\n").map((line) => JSON.parse(line) as { action: string });
  assert.deepEqual(bridgeRequests.map((request) => request.action), ["read_public_result"]);

  const sessionFiles = allFiles(sessionDir).filter((path) => path.endsWith(".jsonl"));
  assert.equal(sessionFiles.length, 1);
  const sessionBytes = statSync(sessionFiles[0]).size;
  assert.ok(sessionBytes > 0 && sessionBytes <= 1048576);
  const entries = readFileSync(sessionFiles[0], "utf8").trim().split("\n").map((line) => JSON.parse(line) as Record<string, unknown>);
  const messages = entries
    .filter((entry) => entry.type === "message")
    .map((entry) => entry.message as { role?: string; toolName?: string; usage?: Record<string, unknown>; content?: unknown[] });
  assert.ok(messages.some((message) => message.role === "toolResult" && message.toolName === "read_public_result"));
  const assistants = messages.filter((message) => message.role === "assistant");
  assert.equal(assistants.length, 2);
  assert.ok(assistants.every((message) => message.usage && Number.isFinite(message.usage.totalTokens)));
  assert.ok(assistants.some((message) =>
    message.content?.some((part) => typeof part === "object" && part !== null && (part as { type?: string }).type === "toolCall"),
  ));

  const archivedSessionPath = join(HERE, "evidence", "installed-main-native-session-v1.jsonl");
  const archivedCapturePath = join(HERE, "evidence", "installed-main-provider-capture-v1.json");
  const archivedBridgePath = join(HERE, "evidence", "installed-main-bridge-record-v1.jsonl");
  copyFileSync(sessionFiles[0], archivedSessionPath);
  copyFileSync(capturePath, archivedCapturePath);
  copyFileSync(bridgeRecordPath, archivedBridgePath);
  const evidence = {
    schema_version: "argo-house-price-a2-installed-main-probe/v1",
    installed_prime_version: "0.9.2",
    process_shape: "public main() in-process forced by fixed no-op plus synthetic-only provider factory",
    production_provider_factory: false,
    command: [process.execPath, "--max-old-space-size=1024", PROBE, configPath],
    environment_keys_before_import: [
      "PRIME_AGENT_CODING_AGENT_DIR", "PRIME_AGENT_KERNEL_PYTHON", "PRIME_AGENT_TELEMETRY", "PATH",
      "TMPDIR", "LANG", "LC_ALL", "TZ",
    ],
    stdin: "DEVNULL",
    exit_code: exitCode,
    elapsed_ms: elapsedMs,
    stdout: stdoutText,
    stderr: stderrText,
    stdout_bytes: Buffer.byteLength(stdoutText),
    stderr_bytes: Buffer.byteLength(stderrText),
    daemon_socket_created: false,
    provider_tool_names: capture.captures[0]?.tools?.map((tool) => tool.name),
    active_tool_names: capture.audits[0]?.activeTools,
    extension_source_path: resolve(extensionPath),
    extension_sha256: sha256(extensionPath),
    session_jsonl: { path: archivedSessionPath, bytes: sessionBytes, sha256: sha256(archivedSessionPath) },
    provider_capture: { path: archivedCapturePath, bytes: statSync(archivedCapturePath).size, sha256: sha256(archivedCapturePath) },
    bridge_record: { path: archivedBridgePath, bytes: statSync(archivedBridgePath).size, sha256: sha256(archivedBridgePath) },
    assistant_message_count: assistants.length,
    tool_result_names: messages.filter((message) => message.role === "toolResult").map((message) => message.toolName),
    faux_calls: capture.fauxCalls,
    total_case_regular_file_bytes: allFiles(TEST_ROOT).reduce((total, path) => total + statSync(path).size, 0),
    synthetic_empty_auth_file_created_by_native_storage: true,
    synthetic_auth_contents_read_by_probe: false,
    actual_provider_or_credentials_used: false,
  };
  writeFileSync(join(HERE, "evidence", "installed-main-faux-pass-v1.json"), JSON.stringify(evidence, null, 2));
  rmSync(TEST_ROOT, { recursive: true, force: true });
  process.stdout.write("PASS installed public main text-mode faux boundary\n");
}

await main();
