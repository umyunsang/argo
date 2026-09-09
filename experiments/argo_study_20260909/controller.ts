import { spawn } from "node:child_process";
import { appendFileSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  AuthStorage,
  createAgentSession,
  DefaultResourceLoader,
  ModelRegistry,
  SessionManager,
  SettingsManager,
} from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import { wrapStreamFnWithSemanticEdges } from "/opt/homebrew/lib/node_modules/prime-agent/dist/core/semantic-edges.js";
import { Type } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/typebox/build/index.mjs";
import { createMeteredStream } from "./model_meter.ts";

type RecordValue = Record<string, unknown>;
type Phase = "FREE" | "PLANNER" | "INVESTIGATOR" | "ASSESSOR";

interface EpisodeConfig {
  episode_id: string;
  arm: "B" | "R";
  candidate_id: string;
  workspace: string;
  private_artifact_dir: string;
  kernel_config: string;
  family_ledger: string;
  auth_path: string;
  common_prompt: string;
  policy_prompt: string;
  task_prompt: string;
  corpus: Record<string, string>;
  model_id: "openai/gpt-5.6-sol" | "openai/gpt-5.5";
  token_limit: number;
  family_limit: number;
  family_usd_limit: number;
  deadline_epoch: number;
}

function record(value: unknown): value is RecordValue {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function loadJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8"));
}

function inside(parent: string, child: string): boolean {
  const rel = relative(parent, child);
  return rel === "" || (!rel.startsWith("..") && !isAbsolute(rel));
}

function configuration(path: string): EpisodeConfig {
  const value = loadJson(path);
  if (!record(value)) throw new Error("EPISODE_CONFIG");
  for (const key of ["episode_id", "candidate_id", "workspace", "private_artifact_dir", "kernel_config", "family_ledger", "auth_path", "common_prompt", "policy_prompt", "task_prompt", "model_id"]) {
    if (typeof value[key] !== "string" || String(value[key]).includes("\0")) throw new Error("EPISODE_CONFIG");
  }
  if (value.arm !== "B" && value.arm !== "R") throw new Error("EPISODE_ARM");
  if (value.model_id !== "openai/gpt-5.6-sol" && value.model_id !== "openai/gpt-5.5") throw new Error("EPISODE_MODEL");
  for (const key of ["token_limit", "family_limit", "family_usd_limit", "deadline_epoch"]) {
    if (typeof value[key] !== "number" || !Number.isFinite(value[key]) || value[key] <= 0) throw new Error("EPISODE_LIMIT");
  }
  if (Number(value.token_limit) > 120000 || Number(value.family_limit) > 1500000) throw new Error("EPISODE_LIMIT");
  const cfg = value as unknown as EpisodeConfig;
  if (!record(value.corpus) || !Object.values(value.corpus).every((entry) => typeof entry === "string")) throw new Error("EPISODE_CORPUS");
  const episodeRoot = dirname(realpathSync(cfg.workspace));
  if (!inside(episodeRoot, realpathSync(cfg.private_artifact_dir)) || inside(realpathSync(cfg.workspace), realpathSync(cfg.private_artifact_dir))) throw new Error("EPISODE_PATH");
  return cfg;
}

function readOpenRouterKey(path: string): string {
  const auth = loadJson(path);
  if (!record(auth) || !record(auth.openrouter) || auth.openrouter.type !== "api_key" || typeof auth.openrouter.key !== "string" || auth.openrouter.key.length === 0) throw new Error("MODEL_ACCESS");
  return auth.openrouter.key;
}

async function bridge(configPath: string, action: string, args: RecordValue, deadline: number): Promise<RecordValue> {
  const script = join(dirname(fileURLToPath(import.meta.url)), "scientific_bridge.py");
  const remainingMs = Math.max(1, Math.floor((deadline - Date.now() / 1000) * 1000));
  return new Promise((resolveResult, reject) => {
    const child = spawn("/opt/homebrew/bin/python3", [script, "--episode-config", configPath, action], { stdio: ["pipe", "pipe", "pipe"] });
    let output = "";
    let bytes = 0;
    let done = false;
    const timer = setTimeout(() => child.kill("SIGTERM"), remainingMs);
    child.stdout.on("data", (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > 262144) child.kill("SIGTERM");
      else output += chunk.toString("utf8");
    });
    // Bridge stderr is operational diagnostics and is never returned to the model.
    child.stderr.on("data", () => {});
    child.once("error", () => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      reject(new Error("BRIDGE_START_FAILED"));
    });
    child.once("close", (code) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      if (code !== 0 || bytes > 262144) return reject(new Error("BRIDGE_UNKNOWN"));
      try {
        const parsed: unknown = JSON.parse(output.trim());
        if (!record(parsed)) throw new Error("BRIDGE_RESPONSE");
        resolveResult(parsed);
      } catch {
        reject(new Error("BRIDGE_RESPONSE"));
      }
    });
    child.stdin.end(JSON.stringify(args));
  });
}

function toolResult(result: RecordValue) {
  return { content: [{ type: "text" as const, text: JSON.stringify(result) }], details: result };
}

export async function runEpisode(configPath: string): Promise<RecordValue> {
  const cfg = configuration(configPath);
  const kernelConfig = loadJson(cfg.kernel_config);
  if (!record(kernelConfig) || typeof kernelConfig.artifact_root !== "string") throw new Error("KERNEL_CONFIG");
  const artifactRoot = kernelConfig.artifact_root;
  const sessionDir = join(artifactRoot, "sessions");
  const profile = join(cfg.private_artifact_dir, "profile");
  mkdirSync(sessionDir, { recursive: true, mode: 0o700 });
  mkdirSync(profile, { recursive: true, mode: 0o700 });
  process.env.PRIME_AGENT_KERNEL_PYTHON = join(dirname(fileURLToPath(import.meta.url)), "kernel_wrapper.py");
  process.env.ARGO_KERNEL_CONFIG = cfg.kernel_config;
  process.env.PRIME_AGENT_TELEMETRY = "0";
  const eventPath = join(cfg.private_artifact_dir, "controller-events.jsonl");
  let phase: Phase = cfg.arm === "B" ? "FREE" : "PLANNER";
  let usedInvestigationSlot = false;
  let finalLocked = false;
  let stopReason = "FINISHED";
  let haltNative = () => {};
  let turns = 0;
  const log = (value: RecordValue) => appendFileSync(eventPath, `${JSON.stringify({ at: new Date().toISOString(), ...value })}\n`, { mode: 0o600 });

  const customTools = [
    {
      name: "read_candidate", label: "Read observed candidate", description: "Read a bounded source or JSON-config excerpt from one previously observed candidate, including the initial RF baseline. Offset and length count characters; this does not consume development feedback.",
      parameters: Type.Object({ candidate_id: Type.String(), kind: Type.Optional(Type.Union([Type.Literal("source"), Type.Literal("config")])), offset: Type.Optional(Type.Integer({ minimum: 0 })), length: Type.Optional(Type.Integer({ minimum: 1, maximum: 4000 })) }, { additionalProperties: false }), executionMode: "sequential" as const,
      async execute(_id: string, args: { candidate_id: string; kind?: "source" | "config"; offset?: number; length?: number }) {
        return toolResult(await bridge(configPath, "read_candidate", args, cfg.deadline_epoch));
      },
    {
      name: "read_corpus", label: "Read fixed source", description: "Read one immutable method excerpt from the fixed corpus. Supply an empty name to list source names. Both conditions have the same source access.",
      parameters: Type.Object({ name: Type.String() }, { additionalProperties: false }), executionMode: "sequential" as const,
      async execute(_id: string, args: { name: string }) {
        if (args.name === "") return toolResult({ sources: Object.keys(cfg.corpus) });
        if (!Object.hasOwn(cfg.corpus, args.name)) return toolResult({ error: "SOURCE_NOT_IN_CORPUS" });
        const text = readFileSync(cfg.corpus[args.name], "utf8");
        if (Buffer.byteLength(text) > 24000) throw new Error("SOURCE_LIMIT");
        return toolResult({ source: args.name, text });
      },
    },
    {
      name: "run_candidate", label: "Run candidate", description: "Freeze solution.py and config, launch one ORX scientific candidate, and return the permitted development feedback. The candidate must define fit(train_X, train_y, frozen_config), returning an object with predict(X).",
      parameters: Type.Object({ relative_source: Type.Optional(Type.String()), config: Type.Optional(Type.Record(Type.String(), Type.Unknown())), hypothesis: Type.String(), parent_experiment_id: Type.Optional(Type.String()) }, { additionalProperties: false }),
      executionMode: "sequential" as const,
      async execute(_id: string, args: { relative_source?: string; config?: RecordValue; hypothesis: string; parent_experiment_id?: string }) {
        if (cfg.arm === "R" && (phase !== "INVESTIGATOR" || usedInvestigationSlot)) return toolResult({ status: "PHASE_REQUIRES_ASSESSMENT" });
        usedInvestigationSlot = true;
        const result = await bridge(configPath, "run_candidate", args, cfg.deadline_epoch);
        log({ event: "candidate_tool", phase, result });
        if (result.status === "UNKNOWN") { stopReason = "RESEARCH_UNKNOWN"; haltNative(); }
        return toolResult(result);
      },
    },
    {
      name: "list_results", label: "Research results", description: "Read all permitted development receipts and remaining feedback opportunities. No outer-test outcome is returned.",
      parameters: Type.Object({}, { additionalProperties: false }), executionMode: "sequential" as const,
      async execute() {
        const result = await bridge(configPath, "list_results", {}, cfg.deadline_epoch);
        if (result.halted === true) { stopReason = "RESEARCH_UNKNOWN"; haltNative(); }
        return toolResult(result);
      },
    },
    {
      name: "lock_candidate", label: "Lock final candidate", description: "Select one previously observed valid candidate for the final frozen outer-training refit. This ends further candidate experimentation.",
      parameters: Type.Object({ candidate_id: Type.String() }, { additionalProperties: false }), executionMode: "sequential" as const,
      async execute(_id: string, args: { candidate_id: string }) {
        if (cfg.arm === "R" && phase !== "ASSESSOR") return toolResult({ status: "PHASE_REQUIRES_ASSESSMENT" });
        const result = await bridge(configPath, "lock_candidate", args, cfg.deadline_epoch);
        if (result.status === "FINAL_LOCKED") finalLocked = true;
        log({ event: "selection_tool", phase, result });
        return toolResult(result);
      },
    },
  ];

  const model = getModel("openrouter", cfg.model_id);
  const authStorage = AuthStorage.inMemory({ openrouter: { type: "api_key", key: readOpenRouterKey(cfg.auth_path) } }, { usePrimeCliConfig: false });
  const modelRegistry = ModelRegistry.inMemory(authStorage);
  const settingsManager = SettingsManager.inMemory({ retry: { enabled: false, provider: { maxRetries: 0, timeoutMs: 60000 } }, autoRefine: { enabled: false }, compaction: { enabled: false }, idleEvictionMinutes: "off", packages: [], extensions: [], skills: [], prompts: [], mcpServers: {} });
  const systemPrompt = `${readFileSync(cfg.common_prompt, "utf8")}\n${readFileSync(cfg.policy_prompt, "utf8")}\n\nUse the native ipython tool for persistent Python and rlm delegation. Only the episode workspace and native session artifacts are mounted. Scientific candidate feedback comes through the named host tools. Read TASK.md in the workspace and use read_corpus for immutable method excerpts as useful. Never infer a score without its receipt.`;
  const resourceLoader = new DefaultResourceLoader({ cwd: cfg.workspace, agentDir: profile, settingsManager, noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true, bundledSkillsDir: null, systemPrompt, appendSystemPrompt: [] });
  await resourceLoader.reload();
  const meter = createMeteredStream({ model, ledgerPath: join(cfg.private_artifact_dir, "model-usage.json"), episodeLimit: cfg.token_limit, familyLedgerPath: cfg.family_ledger, familyLimit: cfg.family_limit, usdCeiling: cfg.family_usd_limit, timeoutMs: 60000, providerTag: "azure" });
  const commonTools = ["ipython", "read_corpus", "read_candidate", "list_results"];
  const allTools = [...commonTools, "run_candidate", "lock_candidate"];
  const { session } = await createAgentSession({ cwd: cfg.workspace, agentDir: profile, authStorage, modelRegistry, model, thinkingLevel: "high", resourceLoader, settingsManager, sessionManager: SessionManager.create(cfg.workspace, sessionDir), tools: allTools, allowedToolNames: allTools, customTools, includeGoals: false, includeCompactSkill: false, rlmMaxDepth: 2, prewarmIpythonKernel: false, telemetryDisabled: true });
  session.agent.streamFn = wrapStreamFnWithSemanticEdges(meter.streamFn, session.semanticEdges);
  haltNative = () => { void session.abort().catch(() => {}); };
  session.agent.toolExecution = "sequential";
  session.subscribe((event) => { log({ event: "native_event", value: event }); });
  const deadlineAbort = new AbortController();
  const stop = () => {
    stopReason = "WALL_BUDGET";
    deadlineAbort.abort();
    void session.abort().catch(() => {});
  };
  const deadlineTimer = setTimeout(stop, Math.max(1, (cfg.deadline_epoch - Date.now() / 1000 - 600) * 1000));
  process.once("SIGTERM", stop);
  process.once("SIGINT", stop);
  try {
    const initial = await bridge(configPath, "initialize", {}, cfg.deadline_epoch);
    log({ event: "initial_artifact", result: initial });
    for (let round = 0; round < 24 && !finalLocked && stopReason === "FINISHED"; round++) {
      if (Date.now() / 1000 >= cfg.deadline_epoch - 600) { stopReason = "FINAL_TIME_RESERVE"; break; }
      const publicState = await bridge(configPath, "list_results", {}, cfg.deadline_epoch);
      if (publicState.error || publicState.status === "UNKNOWN" || publicState.halted === true) { stopReason = "RESEARCH_UNKNOWN"; break; }
      if (cfg.arm === "B") {
        phase = "FREE";
        session.setActiveToolsByName(allTools);
        await session.prompt(`${round === 0 ? readFileSync(cfg.task_prompt, "utf8") : "Continue your research if another investigation is worthwhile and admitted; otherwise lock your chosen candidate. Do not claim a final score."}\nCurrent permitted state: ${JSON.stringify(publicState)}`, { expandPromptTemplates: false });
        await session.waitForRlmQuiescence(deadlineAbort.signal);
        if (session.agent.state.errorMessage || meter.snapshot().blockedReason) throw new Error("MODEL_STOPPED");
        turns++;
      } else {
        for (const next of ["PLANNER", "INVESTIGATOR", "ASSESSOR"] as const) {
          if (finalLocked || stopReason !== "FINISHED" || Date.now() / 1000 >= cfg.deadline_epoch - 600) break;
          phase = next;
          usedInvestigationSlot = false;
          session.setActiveToolsByName(next === "PLANNER" ? commonTools : next === "INVESTIGATOR" ? [...commonTools, "run_candidate"] : [...commonTools, "lock_candidate"]);
          const current = await bridge(configPath, "list_results", {}, cfg.deadline_epoch);
          await session.prompt(`${round === 0 && next === "PLANNER" ? readFileSync(cfg.task_prompt, "utf8") : ""}\nResearch phase: ${next}. Follow your fixed phase policy. ${next === "INVESTIGATOR" ? "At most one new development candidate may be admitted in this phase." : ""}\nAddressable permitted evidence: ${JSON.stringify(current)}`, { expandPromptTemplates: false });
          await session.waitForRlmQuiescence(deadlineAbort.signal);
          if (session.agent.state.errorMessage || meter.snapshot().blockedReason) throw new Error("MODEL_STOPPED");
          turns++;
        }
      }
    }
  } catch (error) {
    if (stopReason === "FINISHED") stopReason = error instanceof Error && /^[A-Z_]+$/.test(error.message) ? error.message : "CONTROLLER_STOPPED";
    log({ event: "controller_stop", safe_reason: stopReason });
  } finally {
    clearTimeout(deadlineTimer);
    process.removeListener("SIGTERM", stop);
    process.removeListener("SIGINT", stop);
    await session.abort();
    await session.disposeAsync();
    await meter.reconcile();
  }
  let final: RecordValue;
  let finalStatus = "UNKNOWN";
  try {
    final = await bridge(configPath, "finalize", {}, cfg.deadline_epoch);
    const privateReceipt = loadJson(join(cfg.private_artifact_dir, "final-private-receipt.json"));
    if (record(privateReceipt) && (privateReceipt.status === "VALID" || privateReceipt.status === "AGENT_INVALID")) finalStatus = privateReceipt.status;
  } catch {
    final = { status: "UNKNOWN", reason: "FINALIZATION_REQUIRES_RECONCILIATION" };
  }
  const summary = { schema: "study-episode-summary/v1", episode_id: cfg.episode_id, arm: cfg.arm, candidate_id: cfg.candidate_id, status: finalStatus, stop_reason: stopReason, controller_prompts: turns, finalization: final, model_usage: await meter.snapshot(), scientific_result_scope: "See independent ORX final receipt; this summary does not expose held-out accuracy" };
  writeFileSync(join(cfg.private_artifact_dir, "episode-summary.json"), `${JSON.stringify(summary, null, 2)}\n`, { mode: 0o600 });
  return summary;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) throw new Error("EPISODE_ARGUMENT");
    const result = await runEpisode(resolve(process.argv[2]));
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    process.stdout.write(`${JSON.stringify({ schema: "study-episode-summary/v1", status: "CONTROLLER_FAILED", error: error instanceof Error && /^[A-Z_]+$/.test(error.message) ? error.message : "CONTROLLER_FAILURE" })}\n`);
    process.exitCode = 1;
  }
}
