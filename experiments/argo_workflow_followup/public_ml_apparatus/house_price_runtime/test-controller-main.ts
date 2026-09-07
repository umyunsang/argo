import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  chmodSync,
  closeSync,
  copyFileSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  readlinkSync,
  readSync,
  realpathSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { prepareControllerMain } from "./controller-main.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const TEST_ROOT = join(realpathSync.native(tmpdir()), "argo-house-price-a2-controller-main-tests");
const PRIME_ENTRY = "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
const KERNEL_INVOCATION = "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python";
const CONTROLLER_MAIN = join(HERE, "controller-main.ts");
const EMPTY_NOAUTH_SAMPLE = join(HERE, "a2-frontend-probes", "deployment.sample.noauth.json");
const TOOLS = [
  "read_solution",
  "write_solution",
  "request_R1_run",
  "read_public_result",
  "read_dev_result",
  "lock_final_artifact",
];

type Test = { name: string; run: () => Promise<void> | void };
const tests: Test[] = [];
const hashCache = new Map<string, string>();

function test(name: string, run: Test["run"]): void {
  tests.push({ name, run });
}

function hashFile(path: string): string {
  const cached = hashCache.get(path);
  if (cached) return cached;
  const hash = createHash("sha256");
  const descriptor = openSync(path, "r");
  const buffer = Buffer.allocUnsafe(65536);
  try {
    while (true) {
      const count = readSync(descriptor, buffer, 0, buffer.length, null);
      if (count === 0) break;
      hash.update(buffer.subarray(0, count));
    }
  } finally {
    closeSync(descriptor);
  }
  const digest = hash.digest("hex");
  hashCache.set(path, digest);
  return digest;
}

function fileSeal(path: string) {
  const stat = statSync(path, { bigint: true });
  return { path, sha256: hashFile(path), bytes: Number(stat.size), mtime_ns_max: stat.mtimeNs.toString() };
}

function directorySeal(path: string, mustBeEmpty: boolean) {
  const stat = lstatSync(path, { bigint: true });
  return {
    path,
    realpath: realpathSync.native(path),
    device: stat.dev.toString(),
    inode: stat.ino.toString(),
    mtime_ns_max: stat.mtimeNs.toString(),
    mode_octal: `0${(Number(stat.mode) & 0o777).toString(8).padStart(3, "0")}`,
    must_be_empty: mustBeEmpty,
  };
}

function exactEnvironment(profile: string, temporary: string) {
  return {
    PRIME_AGENT_CODING_AGENT_DIR: profile,
    PRIME_AGENT_KERNEL_PYTHON: KERNEL_INVOCATION,
    PRIME_AGENT_TELEMETRY: "0",
    PATH: "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
    TMPDIR: `${temporary}/`,
    LANG: "C.UTF-8",
    LC_ALL: "C.UTF-8",
    TZ: "UTC",
  };
}

function fixture(name: string) {
  const root = join(TEST_ROOT, name);
  const artifactRoot = join(root, "artifacts");
  const cwd = join(root, "public-cwd");
  const profile = join(root, "profile");
  const sessionDir = join(artifactRoot, "session");
  const temporaryDir = join(artifactRoot, "tmp");
  const assetsDir = join(root, "assets");
  for (const path of [root, artifactRoot, cwd, profile, sessionDir, temporaryDir, assetsDir]) {
    mkdirSync(path, { recursive: true, mode: 0o700 });
    chmodSync(path, 0o700);
  }
  const deploymentPath = join(artifactRoot, "deployment.json");
  writeFileSync(deploymentPath, "placeholder");
  const extensionPath = join(assetsDir, "controller-extension.ts");
  writeFileSync(extensionPath, "export default function controller() {}\n");
  const extensionHash = hashFile(extensionPath);
  const bindingPath = join(assetsDir, "controller-extension.binding.json");
  writeFileSync(bindingPath, JSON.stringify({
    schemaVersion: "argo-house-price-controller-extension-binding/v1",
    expectedExtensionSha256: extensionHash,
    bridge: { command: process.execPath, argv: [] },
    limits: { bridgeTimeoutMs: 30000, maxRows: 292 },
  }));
  const settingsPath = join(profile, "settings.json");
  writeFileSync(settingsPath, JSON.stringify({ retry: { enabled: false, provider: { timeoutMs: 120000, maxRetries: 0 } } }));
  const systemPromptPath = join(assetsDir, "system.md");
  const taskPromptPath = join(assetsDir, "task.md");
  writeFileSync(systemPromptPath, "Synthetic fixed system prompt.");
  writeFileSync(taskPromptPath, "Synthetic fixed task prompt.");
  const gatePath = join(assetsDir, "gate.sh");
  writeFileSync(gatePath, "#!/bin/sh\nexit 0\n");
  chmodSync(gatePath, 0o700);
  const primeManifest = join(assetsDir, "prime-closure.json");
  const frontendManifest = join(assetsDir, "frontend-closure.json");
  writeFileSync(primeManifest, "{}\n");
  writeFileSync(frontendManifest, "{}\n");
  const kernelResolved = realpathSync.native(KERNEL_INVOCATION);
  const kernelLink = lstatSync(KERNEL_INVOCATION, { bigint: true });
  const pyvenv = join(dirname(dirname(KERNEL_INVOCATION)), "pyvenv.cfg");

  const deployment = {
    schema_version: "argo-house-price-a2-controller-main-deployment/v1",
    status: "TRUSTED_FIXED_DEPLOYMENT",
    assets: {
      prime_entry: fileSeal(PRIME_ENTRY),
      prime_closure_manifest: fileSeal(primeManifest),
      controller_main: fileSeal(CONTROLLER_MAIN),
      frontend_closure_manifest: fileSeal(frontendManifest),
      extension: fileSeal(extensionPath),
      binding: fileSeal(bindingPath),
      settings: fileSeal(settingsPath),
      system_prompt: fileSeal(systemPromptPath),
      task_prompt: fileSeal(taskPromptPath),
      autonomous_gate: fileSeal(gatePath),
      node_executable: fileSeal(process.execPath),
      kernel_interpreter: {
        invocation_path: KERNEL_INVOCATION,
        invocation_link: {
          device: kernelLink.dev.toString(),
          inode: kernelLink.ino.toString(),
          mtime_ns_max: kernelLink.mtimeNs.toString(),
          link_target: readlinkSync(KERNEL_INVOCATION),
        },
        resolved_target: fileSeal(kernelResolved),
        pyvenv_cfg: fileSeal(pyvenv),
      },
    },
    directories: {
      artifact_root: directorySeal(artifactRoot, false),
      cwd: directorySeal(cwd, false),
      profile: directorySeal(profile, false),
      session_dir: directorySeal(sessionDir, true),
      temporary_dir: directorySeal(temporaryDir, true),
    },
    runtime: {
      phase: "dev",
      model: "openai-codex/synthetic-model-id",
      thinking: "off",
      mode: "text",
      print: true,
      offline: true,
      fresh_session: true,
      tools: TOOLS,
    },
    environment: {
      exact: exactEnvironment(profile, temporaryDir),
      home_must_be_unset: true,
      forbidden_prefixes: ["PRIME_AGENT_INTERNAL_"],
    },
    limits: {
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
    },
  };
  writeFileSync(deploymentPath, JSON.stringify(deployment, null, 2));
  return {
    root,
    artifactRoot,
    cwd,
    profile,
    sessionDir,
    temporaryDir,
    deploymentPath,
    deployment,
    environment: exactEnvironment(profile, temporaryDir),
    extensionPath,
    systemPromptPath,
  };
}

function expectSafe(operation: () => unknown, code: string): void {
  assert.throws(operation, (error: unknown) => error instanceof Error && error.message === code);
}

test("empty sample contains no auth material and is not executable", () => {
  const sampleText = readFileSync(EMPTY_NOAUTH_SAMPLE, "utf8");
  const sample = JSON.parse(sampleText) as Record<string, unknown>;
  assert.equal(Object.hasOwn(sample, "auth"), false);
  assert.equal(sampleText.includes("access_token"), false);
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", EMPTY_NOAUTH_SAMPLE, "--artifact-root", realpathSync.native(tmpdir())],
      {},
      ["--max-old-space-size=1024"],
    ),
    "A2_DEPLOYMENT",
  );
});

test("builds the exact public main text-mode six-tool argv from sealed assets", () => {
  const item = fixture("valid");
  const prepared = prepareControllerMain(
    ["--deployment", item.deploymentPath, "--artifact-root", item.artifactRoot],
    item.environment,
    ["--max-old-space-size=1024"],
  );
  assert.deepEqual(prepared.fixedFactories.length, 1);
  assert.deepEqual(prepared.mainArgs.slice(0, 4), ["--print", "--mode", "text", "--offline"]);
  assert.ok(prepared.mainArgs.includes("--no-builtin-tools"));
  assert.equal(prepared.mainArgs[prepared.mainArgs.indexOf("--tools") + 1], TOOLS.join(","));
  assert.equal(prepared.mainArgs[prepared.mainArgs.indexOf("--extension") + 1], item.extensionPath);
  assert.equal(prepared.mainArgs[prepared.mainArgs.indexOf("--system-prompt") + 1], "Synthetic fixed system prompt.");
  assert.deepEqual(prepared.mainArgs.slice(-2), ["--", "Synthetic fixed task prompt."]);
  for (const forbidden of ["--api-key", "--continue", "--resume", "--fork"]) {
    assert.equal(prepared.mainArgs.includes(forbidden), false);
  }
});

test("rejects unknown deployment fields and extra or inherited environment", () => {
  const unknown = fixture("unknown");
  (unknown.deployment as Record<string, unknown>).extra = true;
  writeFileSync(unknown.deploymentPath, JSON.stringify(unknown.deployment));
  expectSafe(
    () => prepareControllerMain(["--deployment", unknown.deploymentPath, "--artifact-root", unknown.artifactRoot], unknown.environment, ["--max-old-space-size=1024"]),
    "A2_DEPLOYMENT",
  );

  const env = fixture("environment");
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", env.deploymentPath, "--artifact-root", env.artifactRoot],
      { ...env.environment, HOME: "/synthetic-home" },
      ["--max-old-space-size=1024"],
    ),
    "A2_ENVIRONMENT",
  );
});

test("allows only artifact-root mtime change from parent log creation", () => {
  const item = fixture("parent-log-order");
  writeFileSync(join(item.artifactRoot, "stdout.txt"), "");
  writeFileSync(join(item.artifactRoot, "stderr.txt"), "");
  prepareControllerMain(
    ["--deployment", item.deploymentPath, "--artifact-root", item.artifactRoot],
    item.environment,
    ["--max-old-space-size=1024"],
  );

  const wrongMode = fixture("artifact-mode");
  chmodSync(wrongMode.artifactRoot, 0o755);
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", wrongMode.deploymentPath, "--artifact-root", wrongMode.artifactRoot],
      wrongMode.environment,
      ["--max-old-space-size=1024"],
    ),
    "A2_DIRECTORY",
  );

  const wrongIdentity = fixture("artifact-identity");
  wrongIdentity.deployment.directories.artifact_root.inode = "1";
  writeFileSync(wrongIdentity.deploymentPath, JSON.stringify(wrongIdentity.deployment));
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", wrongIdentity.deploymentPath, "--artifact-root", wrongIdentity.artifactRoot],
      wrongIdentity.environment,
      ["--max-old-space-size=1024"],
    ),
    "A2_DIRECTORY",
  );

  const staleTemporary = fixture("stale-temporary");
  writeFileSync(join(staleTemporary.temporaryDir, "stale"), "x");
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", staleTemporary.deploymentPath, "--artifact-root", staleTemporary.artifactRoot],
      staleTemporary.environment,
      ["--max-old-space-size=1024"],
    ),
    "A2_DIRECTORY",
  );
});

test("keeps deployment exact-eight while allowing only bounded Darwin post-import metadata", () => {
  const configured = fixture("configured-extra");
  (configured.deployment.environment.exact as Record<string, string>).__CF_USER_TEXT_ENCODING = "0x1:0:0";
  writeFileSync(configured.deploymentPath, JSON.stringify(configured.deployment));
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", configured.deploymentPath, "--artifact-root", configured.artifactRoot],
      configured.environment,
      ["--max-old-space-size=1024"],
      "darwin",
    ),
    "A2_ENVIRONMENT",
  );

  const observed = fixture("darwin-observed");
  prepareControllerMain(
    ["--deployment", observed.deploymentPath, "--artifact-root", observed.artifactRoot],
    { ...observed.environment, __CF_USER_TEXT_ENCODING: "0x1:0:0" },
    ["--max-old-space-size=1024"],
    "darwin",
  );
  for (const value of ["bad\nvalue", "x".repeat(129)]) {
    expectSafe(
      () => prepareControllerMain(
        ["--deployment", observed.deploymentPath, "--artifact-root", observed.artifactRoot],
        { ...observed.environment, __CF_USER_TEXT_ENCODING: value },
        ["--max-old-space-size=1024"],
        "darwin",
      ),
      "A2_ENVIRONMENT",
    );
  }
  expectSafe(
    () => prepareControllerMain(
      ["--deployment", observed.deploymentPath, "--artifact-root", observed.artifactRoot],
      { ...observed.environment, __CF_USER_TEXT_ENCODING: "0x1:0:0" },
      ["--max-old-space-size=1024"],
      "linux",
    ),
    "A2_ENVIRONMENT",
  );
});

test("rejects stale session/temp state and artifact-root mismatch", () => {
  const stale = fixture("stale");
  writeFileSync(join(stale.sessionDir, "prior.jsonl"), "synthetic prior session");
  expectSafe(
    () => prepareControllerMain(["--deployment", stale.deploymentPath, "--artifact-root", stale.artifactRoot], stale.environment, ["--max-old-space-size=1024"]),
    "A2_DIRECTORY",
  );
  const mismatch = fixture("artifact-mismatch");
  expectSafe(
    () => prepareControllerMain(["--deployment", mismatch.deploymentPath, "--artifact-root", mismatch.cwd], mismatch.environment, ["--max-old-space-size=1024"]),
    "A2_ARGUMENT",
  );
});

test("binds the venv invocation symlink, resolved binary, and pyvenv.cfg without auth", () => {
  const item = fixture("kernel");
  rmSync(join(item.profile, "auth.json"), { force: true });
  const prepared = prepareControllerMain(
    ["--deployment", item.deploymentPath, "--artifact-root", item.artifactRoot],
    item.environment,
    ["--max-old-space-size=1024"],
  );
  assert.equal(prepared.deployment.assets.kernel_interpreter.invocation_path, KERNEL_INVOCATION);
  assert.equal(prepared.deployment.assets.kernel_interpreter.resolved_target.path, realpathSync.native(KERNEL_INVOCATION));
});

test("requires the exact trusted retry settings and detects postflight mutation", () => {
  const settings = fixture("settings");
  const settingsPath = join(settings.profile, "settings.json");
  writeFileSync(settingsPath, JSON.stringify({ retry: { provider: { timeoutMs: 120000, maxRetries: 0 } } }));
  hashCache.delete(settingsPath);
  settings.deployment.assets.settings = fileSeal(settingsPath);
  writeFileSync(settings.deploymentPath, JSON.stringify(settings.deployment));
  expectSafe(
    () => prepareControllerMain(["--deployment", settings.deploymentPath, "--artifact-root", settings.artifactRoot], settings.environment, ["--max-old-space-size=1024"]),
    "A2_SETTINGS",
  );

  const postflight = fixture("postflight");
  const prepared = prepareControllerMain(
    ["--deployment", postflight.deploymentPath, "--artifact-root", postflight.artifactRoot],
    postflight.environment,
    ["--max-old-space-size=1024"],
  );
  writeFileSync(postflight.systemPromptPath, "mutated after preflight");
  expectSafe(() => prepared.verifyPostflight(), "A2_ASSET");
});

async function main(): Promise<void> {
  rmSync(TEST_ROOT, { recursive: true, force: true });
  mkdirSync(TEST_ROOT, { recursive: true, mode: 0o700 });
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
  writeFileSync(join(TEST_ROOT, "summary.json"), JSON.stringify({ total: tests.length, failures }, null, 2));
  if (failures.length > 0) process.exitCode = 1;
}

await main();
