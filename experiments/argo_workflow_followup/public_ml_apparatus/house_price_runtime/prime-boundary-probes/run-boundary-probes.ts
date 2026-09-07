import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import {
  closeSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  openSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI, ToolDefinition } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { validateToolArguments } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import {
  CONTROLLER_TOOL_NAMES,
  createControllerExtension,
  type ControllerExtensionBinding,
} from "../controller-extension.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const RUNTIME_ROOT = resolve(HERE, "..");
const REPO_ROOT = resolve(RUNTIME_ROOT, "../../../..");
const TEST_ROOT = join(HERE, ".tmp-prime-probes");
const RUNNER = join(HERE, "installed-prime-cli-probe.ts");
const TSX = join(REPO_ROOT, "node_modules", "tsx", "dist", "cli.mjs");
const CONTROLLER_SOURCE = join(RUNTIME_ROOT, "controller-extension.ts");
const FAKE_BRIDGE = join(HERE, "fake-bridge.mjs");
const FIXED_PROMPT = "You are the synthetic House Price controller boundary probe. Use only the supplied task tools.";
const TASK_PROMPT = "Inspect the current synthetic controller state, then stop without a real run.";
const SENTINELS = {
  agents: "SYNTHETIC_AGENTS_SENTINEL_5b8f",
  system: "SYNTHETIC_SYSTEM_SENTINEL_67c1",
  append: "SYNTHETIC_APPEND_SENTINEL_21d0",
  extension: "SYNTHETIC_EXTENSION_SENTINEL_049e",
  skill: "SYNTHETIC_SKILL_SENTINEL_9cc2",
  prompt: "SYNTHETIC_PROMPT_SENTINEL_32aa",
  harness: "SYNTHETIC_HARNESS_SENTINEL_884a",
  file: "SYNTHETIC_FILE_ARG_SENTINEL_4dd1",
  stdin: "SYNTHETIC_STDIN_SENTINEL_c8e2",
  prior: "SYNTHETIC_PRIOR_SESSION_SENTINEL_a77f",
} as const;

type Scenario = "stop" | "unknown-tool" | "schema-unknown" | "mutated-arguments" | "long-provider";
type CaseResult = {
  name: string;
  command: string[];
  stdin: string;
  exitCode: number | null;
  stdout: string;
  stderr: string;
  receipt: ProbeReceipt;
};
type ProbeReceipt = {
  installedPrimeVersion: string;
  processLocalExtensionFactoriesProvided: boolean;
  args: string[];
  elapsedMs: number;
  fauxCallCount: number;
  captures: Array<{
    systemPrompt?: string;
    messages: unknown[];
    tools?: Array<{ name: string; description: string; parameters: Record<string, unknown> }>;
  }>;
  audits: Array<{
    activeTools: string[];
    allTools: Array<{ name: string; sourcePath: string; source: string }>;
    commands: Array<{ name: string; source: string; path: string }>;
    systemPrompt: string;
  }>;
  mainError?: string;
};

type Test = { name: string; run: () => Promise<void> | void };
const tests: Test[] = [];
const caseResults: CaseResult[] = [];

function test(name: string, run: Test["run"]): void {
  tests.push({ name, run });
}

function sha256(bytes: Buffer | string): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function serializeUnknown(value: unknown): string {
  return JSON.stringify(value);
}

function prepareControllerMirror(): { extensionPath: string; extensionSha256: string; mtimeUpperBoundMs: number } {
  const extensionDir = join(TEST_ROOT, "loaded-extension");
  mkdirSync(extensionDir, { recursive: true });
  const extensionPath = join(extensionDir, "controller-extension.ts");
  copyFileSync(CONTROLLER_SOURCE, extensionPath);
  const extensionBytes = readFileSync(extensionPath);
  const extensionSha256 = sha256(extensionBytes);
  const bridgeRecord = join(TEST_ROOT, "cli-bridge-records.jsonl");
  writeFileSync(
    join(extensionDir, "controller-extension.binding.json"),
    JSON.stringify({
      schemaVersion: "argo-house-price-controller-extension-binding/v1",
      expectedExtensionSha256: extensionSha256,
      bridge: { command: process.execPath, argv: [FAKE_BRIDGE, bridgeRecord, "normal"] },
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
    }, null, 2),
  );
  return { extensionPath, extensionSha256, mtimeUpperBoundMs: statSync(extensionPath).mtimeMs };
}

function prepareDirtyResources(): { cwd: string; agentDir: string; resourcePromptPath: string } {
  const cwd = join(TEST_ROOT, "dirty-public-cwd");
  const agentDir = join(TEST_ROOT, "dirty-agent-dir");
  const projectAgent = join(cwd, ".prime", "agent");
  mkdirSync(join(projectAgent, "extensions"), { recursive: true });
  mkdirSync(join(agentDir, "skills", "synthetic-leak"), { recursive: true });
  mkdirSync(join(agentDir, "prompts"), { recursive: true });
  mkdirSync(join(agentDir, "harness"), { recursive: true });
  writeFileSync(join(cwd, "AGENTS.md"), SENTINELS.agents);
  writeFileSync(join(projectAgent, "SYSTEM.md"), SENTINELS.system);
  writeFileSync(join(projectAgent, "APPEND_SYSTEM.md"), SENTINELS.append);
  writeFileSync(
    join(projectAgent, "extensions", "leak.ts"),
    `export default function (pi) { pi.on("before_agent_start", (event) => ({ systemPrompt: event.systemPrompt + "\\n${SENTINELS.extension}" })); }\n`,
  );
  writeFileSync(
    join(agentDir, "skills", "synthetic-leak", "SKILL.md"),
    `---\nname: synthetic-leak\ndescription: ${SENTINELS.skill}\n---\n${SENTINELS.skill}\n`,
  );
  const resourcePromptPath = join(agentDir, "prompts", "leak.md");
  writeFileSync(resourcePromptPath, SENTINELS.prompt);
  writeFileSync(
    join(agentDir, "settings.json"),
    JSON.stringify({
      extensions: [join(projectAgent, "extensions", "leak.ts")],
      skills: [join(agentDir, "skills")],
      prompts: [join(agentDir, "prompts")],
      enableBuiltinSkills: false,
      retry: { enabled: false },
    }),
  );
  writeFileSync(
    join(agentDir, "harness", "harness_state.json"),
    JSON.stringify({
      schema: 1,
      entries: {
        prompt: {},
        memory: {
          synthetic: {
            id: "synthetic",
            kind: "memory",
            title: "Synthetic sentinel",
            content: SENTINELS.harness,
            path: "probe",
            reference: {},
            arguments: {},
            metadata: {},
            scope: "global",
          },
        },
        skill: {},
        subagent: {},
      },
      refinements: [],
    }),
  );
  return { cwd, agentDir, resourcePromptPath };
}

function strictArgs(extensionPath: string, cwd: string, sessionDir: string, taskPrompt = TASK_PROMPT): string[] {
  return [
    "--mode", "json",
    "--offline",
    "--cwd", cwd,
    "--session-dir", sessionDir,
    "--model", "<FAUX_MODEL>",
    "--thinking", "off",
    "--no-builtin-tools",
    "--tools", CONTROLLER_TOOL_NAMES.join(","),
    "--no-extensions",
    "--extension", extensionPath,
    "--no-skills",
    "--no-prompt-templates",
    "--no-themes",
    "--no-context-files",
    "--system-prompt", FIXED_PROMPT,
    "--append-system-prompt", "",
    "--",
    taskPrompt,
  ];
}

async function runCase(
  name: string,
  cliArgs: string[],
  scenario: Scenario,
  options: {
    agentDir: string;
    stdin?: string;
    resourcePromptPath?: string;
    lateToolCanaryPath?: string;
    allowMissingCapture?: boolean;
  },
): Promise<CaseResult> {
  const caseDir = join(TEST_ROOT, "cases", name);
  mkdirSync(caseDir, { recursive: true });
  const capturePath = join(caseDir, "capture.json");
  const auditPath = join(caseDir, "audit.json");
  const configPath = join(caseDir, "config.json");
  writeFileSync(configPath, JSON.stringify({
    scenario,
    capturePath,
    auditPath,
    agentDir: options.agentDir,
    cliArgs,
    resourcePromptPath: options.resourcePromptPath,
    lateToolCanaryPath: options.lateToolCanaryPath,
  }, null, 2));
  const childHome = join(caseDir, "home");
  mkdirSync(childHome, { recursive: true });
  const command = [process.execPath, TSX, RUNNER, configPath];
  const stdin = options.stdin ?? "";
  const result = await new Promise<{ exitCode: number | null; stdout: string; stderr: string }>((resolvePromise, rejectPromise) => {
    const stdoutPath = join(caseDir, "stdout.jsonl");
    const stderrPath = join(caseDir, "stderr.txt");
    const stdoutDescriptor = openSync(stdoutPath, "w");
    const stderrDescriptor = openSync(stderrPath, "w");
    let descriptorsClosed = false;
    const closeDescriptors = (): void => {
      if (descriptorsClosed) return;
      descriptorsClosed = true;
      closeSync(stdoutDescriptor);
      closeSync(stderrDescriptor);
    };
    const child = spawn(command[0], command.slice(1), {
      cwd: REPO_ROOT,
      shell: false,
      stdio: ["pipe", stdoutDescriptor, stderrDescriptor],
      env: {
        HOME: childHome,
        LANG: "C.UTF-8",
        LC_ALL: "C.UTF-8",
        PATH: "/opt/homebrew/bin:/usr/bin:/bin",
        PRIME_AGENT_CODING_AGENT_DIR: options.agentDir,
        PRIME_AGENT_TELEMETRY: "0",
        PI_OFFLINE: "1",
        PI_SKIP_VERSION_CHECK: "1",
        PRIME_AGENT_KERNEL_PYTHON: "/Users/um-yunsang/.prime/agent/kernel-venv/bin/python",
      },
    });
    child.on("error", (error) => {
      closeDescriptors();
      rejectPromise(error);
    });
    child.on("close", (exitCode) => {
      closeDescriptors();
      resolvePromise({
        exitCode,
        stdout: readFileSync(stdoutPath, "utf8"),
        stderr: readFileSync(stderrPath, "utf8"),
      });
    });
    child.stdin?.end(stdin, "utf8");
  });
  if (!existsSync(capturePath) && !options.allowMissingCapture) {
    assert.fail(`${name} capture missing: ${result.stderr}`);
  }
  const receipt: ProbeReceipt = existsSync(capturePath)
    ? JSON.parse(readFileSync(capturePath, "utf8")) as ProbeReceipt
    : {
        installedPrimeVersion: "0.9.2",
        processLocalExtensionFactoriesProvided: true,
        args: cliArgs,
        elapsedMs: 0,
        fauxCallCount: 0,
        captures: [],
        audits: [],
        mainError: result.stderr.trim() || "PROCESS_EXIT_BEFORE_CAPTURE",
      };
  const combined = { name, command, stdin, ...result, receipt };
  caseResults.push(combined);
  writeFileSync(join(caseDir, "case-result.json"), JSON.stringify(combined, null, 2));
  return combined;
}

function firstContext(result: CaseResult) {
  const context = result.receipt.captures[0];
  assert.ok(context, `${result.name} has no provider capture`);
  return context;
}

function firstAudit(result: CaseResult) {
  const audit = result.receipt.audits[0];
  assert.ok(audit, `${result.name} has no runtime audit`);
  return audit;
}

function contextText(result: CaseResult): string {
  return serializeUnknown(result.receipt.captures);
}

let mirror: ReturnType<typeof prepareControllerMirror>;
let dirty: ReturnType<typeof prepareDirtyResources>;
let sterileAgentDir: string;
let directValidationMeasurement: {
  input_content_bytes: number;
  diagnostic_bytes: number;
  diagnostic_sha256: string;
  full_content_echoed: boolean;
  bridge_invoked: boolean;
  evidence_path: string;
} | undefined;

test("T01 failing control exposes more than six tools", async () => {
  const sessionDir = join(TEST_ROOT, "sessions", "t01-control");
  const args = strictArgs(mirror.extensionPath, dirty.cwd, sessionDir);
  const filtered = args.filter((item, index) => item !== "--no-builtin-tools" && args[index - 1] !== "--tools" && item !== "--tools");
  const result = await runCase("t01-control", filtered, "stop", { agentDir: sterileAgentDir });
  const names = firstContext(result).tools?.map((tool) => tool.name) ?? [];
  assert.ok(names.includes("ipython"));
  assert.ok(names.length > CONTROLLER_TOOL_NAMES.length);
});

test("T01 pass provider payload and runtime census are exactly six strict tools", async () => {
  const result = await runCase(
    "t01-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t01-pass")),
    "stop",
    { agentDir: sterileAgentDir },
  );
  const tools = firstContext(result).tools ?? [];
  assert.deepEqual(tools.map((tool) => tool.name), [...CONTROLLER_TOOL_NAMES]);
  assert.deepEqual(firstAudit(result).activeTools, [...CONTROLLER_TOOL_NAMES]);
  for (const tool of tools) {
    assert.equal(tool.parameters.additionalProperties, false, tool.name);
  }
});

test("T02 existing system prompt path is opened while trusted content is also delivered", async () => {
  const systemFile = join(TEST_ROOT, "synthetic-system.md");
  writeFileSync(systemFile, SENTINELS.system);
  const literalArgs = strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t02-system-path"));
  literalArgs[literalArgs.indexOf(FIXED_PROMPT)] = systemFile;
  const literal = await runCase("t02-system-path-control", literalArgs, "stop", { agentDir: sterileAgentDir });
  assert.ok(firstContext(literal).systemPrompt?.startsWith(SENTINELS.system));
  assert.ok(contextText(literal).includes(SENTINELS.system));

  const openedContent = readFileSync(systemFile, "utf8");
  const contentArgs = strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t02-system-content"));
  contentArgs[contentArgs.indexOf(FIXED_PROMPT)] = openedContent;
  const content = await runCase("t02-system-content-pass", contentArgs, "stop", { agentDir: sterileAgentDir });
  assert.ok(firstContext(content).systemPrompt?.startsWith(openedContent));
  assert.ok(contextText(content).includes(SENTINELS.system));
  assert.equal(sha256(openedContent).length, 64);
});

test("T02 permissive resources leak synthetic context while sterile flags do not", async () => {
  const permissiveArgs = [
    "--mode", "json", "--offline", "--cwd", dirty.cwd,
    "--session-dir", join(TEST_ROOT, "sessions", "t02-control"),
    "--model", "<FAUX_MODEL>", "--thinking", "off",
    "--no-builtin-tools", "--extension", mirror.extensionPath,
    "--", TASK_PROMPT,
  ];
  const control = await runCase("t02-control", permissiveArgs, "stop", { agentDir: dirty.agentDir });
  const controlText = contextText(control);
  assert.ok(Object.values(SENTINELS).some((sentinel) => controlText.includes(sentinel)));

  const pass = await runCase(
    "t02-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t02-pass")),
    "stop",
    { agentDir: sterileAgentDir },
  );
  const passText = contextText(pass);
  for (const sentinel of [SENTINELS.agents, SENTINELS.system, SENTINELS.append, SENTINELS.extension, SENTINELS.skill, SENTINELS.harness]) {
    assert.equal(passText.includes(sentinel), false, sentinel);
  }
  assert.ok(firstContext(pass).systemPrompt?.startsWith(FIXED_PROMPT));
});

test("T03 explicit extension resource bypass control works and production closure has no resource ingress", async () => {
  const control = await runCase(
    "t03-control",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t03-control"), "/leak"),
    "stop",
    { agentDir: sterileAgentDir, resourcePromptPath: dirty.resourcePromptPath },
  );
  assert.ok(contextText(control).includes(SENTINELS.prompt));
  const pass = await runCase(
    "t03-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t03-pass")),
    "stop",
    { agentDir: sterileAgentDir },
  );
  assert.equal(contextText(pass).includes(SENTINELS.prompt), false);
  assert.equal(firstAudit(pass).commands.length, 0);
});

test("T04 @file and piped stdin controls ingress; final separator plus closed stdin do not", async () => {
  const filePath = join(TEST_ROOT, "synthetic-file-arg.txt");
  writeFileSync(filePath, SENTINELS.file);
  const fileArgs = strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t04-file"));
  fileArgs.splice(fileArgs.indexOf("--"), 0, `@${filePath}`);
  const fileControl = await runCase("t04-file-control", fileArgs, "stop", { agentDir: sterileAgentDir });
  assert.ok(contextText(fileControl).includes(SENTINELS.file));

  const stdinControl = await runCase(
    "t04-stdin-control",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t04-stdin")),
    "stop",
    { agentDir: sterileAgentDir, stdin: SENTINELS.stdin },
  );
  assert.ok(contextText(stdinControl).includes(SENTINELS.stdin));

  const pass = await runCase(
    "t04-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t04-pass")),
    "stop",
    { agentDir: sterileAgentDir },
  );
  assert.equal(contextText(pass).includes(SENTINELS.file), false);
  assert.equal(contextText(pass).includes(SENTINELS.stdin), false);
});

test("T04 persisted resume imports prior context while a fresh session dir does not", async () => {
  const sharedSessions = join(TEST_ROOT, "sessions", "t04-resume-control");
  await runCase(
    "t04-resume-seed",
    strictArgs(mirror.extensionPath, dirty.cwd, sharedSessions, SENTINELS.prior),
    "stop",
    { agentDir: sterileAgentDir },
  );
  const resumeArgs = strictArgs(mirror.extensionPath, dirty.cwd, sharedSessions, "second prompt");
  resumeArgs.splice(resumeArgs.indexOf("--"), 0, "--continue");
  const resumed = await runCase("t04-resume-control", resumeArgs, "stop", { agentDir: sterileAgentDir });
  assert.ok(contextText(resumed).includes(SENTINELS.prior));

  const fresh = await runCase(
    "t04-resume-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t04-fresh"), "second prompt"),
    "stop",
    { agentDir: sterileAgentDir },
  );
  assert.equal(contextText(fresh).includes(SENTINELS.prior), false);
});

test("T05/T06 permissive late tool executes canary; hard allowlist blocks active and provider ingress", async () => {
  const controlCanary = join(TEST_ROOT, "t05-control-canary");
  const permissiveArgs = [
    "--mode", "json", "--offline", "--cwd", dirty.cwd,
    "--session-dir", join(TEST_ROOT, "sessions", "t05-control"),
    "--model", "<FAUX_MODEL>", "--thinking", "off",
    "--no-builtin-tools", "--no-extensions", "--extension", mirror.extensionPath,
    "--no-skills", "--no-prompt-templates", "--no-themes", "--no-context-files",
    "--system-prompt", FIXED_PROMPT, "--append-system-prompt", "", "--", TASK_PROMPT,
  ];
  const control = await runCase("t05-control", permissiveArgs, "unknown-tool", {
    agentDir: sterileAgentDir,
    lateToolCanaryPath: controlCanary,
  });
  assert.equal(existsSync(controlCanary), true);
  assert.ok((firstContext(control).tools ?? []).some((tool) => tool.name === "escape_late"));

  const passCanary = join(TEST_ROOT, "t05-pass-canary");
  const pass = await runCase(
    "t05-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t05-pass")),
    "unknown-tool",
    { agentDir: sterileAgentDir, lateToolCanaryPath: passCanary },
  );
  assert.equal(existsSync(passCanary), false);
  assert.deepEqual(firstAudit(pass).activeTools, [...CONTROLLER_TOOL_NAMES]);
  for (const context of pass.receipt.captures) {
    assert.deepEqual(context.tools?.map((tool) => tool.name), [...CONTROLLER_TOOL_NAMES]);
  }
});

test("unknown schema properties are rejected before execute and never reach the bridge", async () => {
  const bridgeRecord = join(TEST_ROOT, "cli-bridge-records.jsonl");
  const before = existsSync(bridgeRecord) ? readFileSync(bridgeRecord, "utf8") : "";
  const result = await runCase(
    "schema-unknown-property",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "schema-unknown")),
    "schema-unknown",
    { agentDir: sterileAgentDir },
  );
  const after = existsSync(bridgeRecord) ? readFileSync(bridgeRecord, "utf8") : "";
  assert.equal(after, before);
  const finalContext = result.receipt.captures.at(-1);
  assert.ok(finalContext);
  const text = serializeUnknown(finalContext.messages);
  assert.ok(text.includes("Validation failed for tool"));
  assert.ok(text.includes("must not have additional properties"));
});

test("direct installed validator echoes the largest allowed source without truncation", () => {
  const recordPath = join(TEST_ROOT, "direct-validation-bridge-record.jsonl");
  const controllerBinding: ControllerExtensionBinding = {
    schemaVersion: "argo-house-price-controller-extension-binding/v1",
    expectedExtensionSha256: "0".repeat(64),
    bridge: { command: process.execPath, argv: [FAKE_BRIDGE, recordPath, "normal"] },
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
  const registered = new Map<string, ToolDefinition>();
  const api = {
    registerTool(tool: ToolDefinition) {
      registered.set(tool.name, tool);
    },
    getActiveTools() {
      return [...CONTROLLER_TOOL_NAMES];
    },
  } as unknown as ExtensionAPI;
  createControllerExtension(controllerBinding)(api);
  const tool = registered.get("write_solution");
  assert.ok(tool);
  const content = "x".repeat(131072);
  let diagnostic = "";
  try {
    validateToolArguments(tool as never, {
      id: "largest-direct-validation",
      type: "toolCall",
      name: "write_solution",
      arguments: { path: "solution.py", content, extra: true },
    } as never);
    assert.fail("validator accepted an unknown property");
  } catch (error) {
    diagnostic = error instanceof Error ? error.message : "";
  }
  assert.ok(diagnostic.includes("Validation failed for tool"));
  assert.ok(diagnostic.includes(content));
  assert.ok(Buffer.byteLength(diagnostic, "utf8") > 131072);
  assert.equal(existsSync(recordPath), false);
  const diagnosticPath = join(HERE, "evidence", "core-validation-largest-diagnostic-v1.txt");
  writeFileSync(diagnosticPath, diagnostic);
  directValidationMeasurement = {
    input_content_bytes: Buffer.byteLength(content, "utf8"),
    diagnostic_bytes: Buffer.byteLength(diagnostic, "utf8"),
    diagnostic_sha256: sha256(diagnostic),
    full_content_echoed: diagnostic.includes(content),
    bridge_invoked: existsSync(recordPath),
    evidence_path: diagnosticPath,
  };
});

test("T05 post-validation argument mutation reaches execute but is rejected before bridge", async () => {
  const bridgeRecord = join(TEST_ROOT, "cli-bridge-records.jsonl");
  const before = existsSync(bridgeRecord) ? readFileSync(bridgeRecord, "utf8") : "";
  const result = await runCase(
    "t05-mutated-arguments",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t05-mutation")),
    "mutated-arguments",
    { agentDir: sterileAgentDir },
  );
  const after = existsSync(bridgeRecord) ? readFileSync(bridgeRecord, "utf8") : "";
  assert.equal(after, before);
  assert.ok(contextText(result).includes("INVALID_ARGUMENT"));
});

test("T15 current provider call can exceed between-turn limit; tool cancellation is separately bounded", async () => {
  const args = strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t15"));
  args.splice(args.indexOf("--"), 0,
    "--autonomous",
    "--autonomous-max-continuations", "1",
    "--autonomous-max-turns", "1",
    "--autonomous-max-tokens", "1",
    "--autonomous-timeout-ms", "1",
  );
  const result = await runCase("t15-between-turn-control", args, "long-provider", { agentDir: sterileAgentDir });
  assert.ok(result.receipt.elapsedMs >= 100);
  assert.equal(result.receipt.fauxCallCount, 1);
});

test("T16 binding hash blocks pre-load mutation and active source path identifies loaded bytes", async () => {
  const sourceBytes = readFileSync(mirror.extensionPath);
  const preHash = sha256(sourceBytes);
  assert.equal(preHash, mirror.extensionSha256);
  const pass = await runCase(
    "t16-pass",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t16-pass")),
    "stop",
    { agentDir: sterileAgentDir },
  );
  const sourcePaths = firstAudit(pass).allTools
    .filter((tool) => CONTROLLER_TOOL_NAMES.includes(tool.name as (typeof CONTROLLER_TOOL_NAMES)[number]))
    .map((tool) => resolve(tool.sourcePath));
  assert.deepEqual([...new Set(sourcePaths)], [resolve(mirror.extensionPath)]);
  assert.equal(sha256(readFileSync(mirror.extensionPath)), preHash);
  assert.ok(statSync(mirror.extensionPath).mtimeMs <= Date.now());

  writeFileSync(mirror.extensionPath, `${sourceBytes.toString("utf8")}\n// post-prehash mutation control\n`);
  const mutated = await runCase(
    "t16-mutation-control",
    strictArgs(mirror.extensionPath, dirty.cwd, join(TEST_ROOT, "sessions", "t16-mutated")),
    "stop",
    { agentDir: sterileAgentDir, allowMissingCapture: true },
  );
  assert.notEqual(sha256(readFileSync(mirror.extensionPath)), preHash);
  assert.ok(mutated.receipt.mainError || (firstContext(mutated).tools?.length ?? 0) !== CONTROLLER_TOOL_NAMES.length);
  writeFileSync(mirror.extensionPath, sourceBytes);
});

async function main(): Promise<void> {
  rmSync(TEST_ROOT, { recursive: true, force: true });
  mkdirSync(TEST_ROOT, { recursive: true });
  sterileAgentDir = join(TEST_ROOT, "sterile-agent-dir");
  mkdirSync(sterileAgentDir, { recursive: true });
  writeFileSync(join(sterileAgentDir, "settings.json"), JSON.stringify({ retry: { enabled: false } }));
  mirror = prepareControllerMirror();
  dirty = prepareDirtyResources();

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
  const receipt = {
    schema_version: "argo-house-price-installed-prime-boundary-probes/v1",
    installed_prime_version: "0.9.2",
    installed_prime_root: "/opt/homebrew/lib/node_modules/prime-agent",
    process_shape: "in-process main() with process-local faux provider factories; no daemon client",
    controller_source: CONTROLLER_SOURCE,
    controller_source_sha256: sha256(readFileSync(CONTROLLER_SOURCE)),
    loaded_extension_path: mirror.extensionPath,
    loaded_extension_sha256: mirror.extensionSha256,
    loaded_extension_mtime_upper_bound_ms: mirror.mtimeUpperBoundMs,
    fixed_prompt_sha256: sha256(FIXED_PROMPT),
    exact_tool_names: CONTROLLER_TOOL_NAMES,
    tests: { total: tests.length, failures },
    direct_validation_measurement: directValidationMeasurement,
    cases: caseResults,
  };
  writeFileSync(join(TEST_ROOT, "boundary-probe-summary.json"), JSON.stringify(receipt, null, 2));
  writeFileSync(join(HERE, "evidence", "boundary-probe-summary-v1.json"), JSON.stringify(receipt, null, 2));
  if (failures.length > 0) process.exitCode = 1;
}

await main();
