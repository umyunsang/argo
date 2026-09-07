import { readFileSync, writeFileSync } from "node:fs";
import type { ExtensionFactory } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { main } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import {
  fauxAssistantMessage,
  fauxToolCall,
  registerFauxProvider,
  type Context,
} from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";

interface ProbeConfig {
  cwd: string;
  sessionDir: string;
  extensionPath: string;
  daemonSocketPath: string;
  capturePath: string;
}

const configPath = process.argv[2];
if (!configPath) throw new Error("synthetic probe config required");
const config = JSON.parse(readFileSync(configPath, "utf8")) as ProbeConfig;
const initialEnvironmentKeys = Object.keys(process.env).sort();
const provider = `a2-faux-${process.pid}`;
const faux = registerFauxProvider({
  provider,
  models: [{
    id: "a2-probe",
    name: "A2 Probe",
    reasoning: false,
    input: ["text"],
    contextWindow: 128000,
    maxTokens: 4096,
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
  }],
});
const captures: Array<{
  systemPrompt?: string;
  messages: unknown[];
  tools?: Array<{ name: string; description: string; parameters: Record<string, unknown> }>;
}> = [];
const snapshot = (context: Context): void => {
  captures.push({
    systemPrompt: context.systemPrompt,
    messages: JSON.parse(JSON.stringify(context.messages)) as unknown[],
    tools: context.tools?.map((tool) => ({
      name: tool.name,
      description: tool.description,
      parameters: JSON.parse(JSON.stringify(tool.parameters)) as Record<string, unknown>,
    })),
  });
};
faux.setResponses([
  (context) => {
    snapshot(context);
    return fauxAssistantMessage(fauxToolCall("read_public_result", {}));
  },
  (context) => {
    snapshot(context);
    return fauxAssistantMessage("A2 synthetic probe complete");
  },
]);

const audits: Array<{
  activeTools: string[];
  tools: Array<{ name: string; sourcePath: string; source: string }>;
  commands: string[];
}> = [];
const noOpFactory: ExtensionFactory = () => undefined;
const fixtureFactory: ExtensionFactory = (pi) => {
  pi.registerProvider(provider, {
    name: "A2 Faux Probe",
    baseUrl: "http://localhost:0",
    apiKey: "faux-test-only",
    api: faux.api,
    models: faux.models.map((model) => ({
      id: model.id,
      name: model.name,
      api: model.api,
      baseUrl: model.baseUrl,
      reasoning: model.reasoning,
      input: model.input,
      cost: model.cost,
      contextWindow: model.contextWindow,
      maxTokens: model.maxTokens,
    })),
  });
  pi.on("before_agent_start", () => {
    audits.push({
      activeTools: pi.getActiveTools(),
      tools: pi.getAllTools().map((tool) => ({
        name: tool.name,
        sourcePath: tool.sourceInfo.path,
        source: tool.sourceInfo.source,
      })),
      commands: pi.getCommands().map((command) => command.name),
    });
  });
};

let error: string | undefined;
try {
  await main([
    "--print",
    "--mode", "text",
    "--offline",
    "--daemon-socket", config.daemonSocketPath,
    "--cwd", config.cwd,
    "--session-dir", config.sessionDir,
    "--model", `${provider}/a2-probe`,
    "--thinking", "off",
    "--no-builtin-tools",
    "--tools", "read_solution,write_solution,request_R1_run,read_public_result,read_dev_result,lock_final_artifact",
    "--no-extensions",
    "--extension", config.extensionPath,
    "--no-skills",
    "--no-prompt-templates",
    "--no-themes",
    "--no-context-files",
    "--system-prompt", "A2 synthetic fixed system prompt.",
    "--append-system-prompt", "",
    "--",
    "Use read_public_result once, then stop.",
  ], { extensionFactories: [noOpFactory, fixtureFactory] });
} catch (caught) {
  error = caught instanceof Error ? `${caught.name}:${caught.message}` : "UNKNOWN";
  process.exitCode = 1;
} finally {
  writeFileSync(config.capturePath, JSON.stringify({ provider, fauxCalls: faux.state.callCount, captures, audits, initialEnvironmentKeys, finalEnvironmentKeys: Object.keys(process.env).sort(), error }, null, 2));
  faux.unregister();
}

process.exit(process.exitCode ?? 0);
