import { readFileSync, writeFileSync } from "node:fs";
import type { ExtensionFactory } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { main } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import {
  fauxAssistantMessage,
  fauxToolCall,
  registerFauxProvider,
  type Context,
} from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import { Type } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/typebox/build/index.mjs";

interface ProbeConfig {
  scenario: "stop" | "unknown-tool" | "schema-unknown" | "mutated-arguments" | "long-provider";
  capturePath: string;
  auditPath: string;
  agentDir: string;
  cliArgs: string[];
  resourcePromptPath?: string;
  lateToolCanaryPath?: string;
}

const configPath = process.argv[2];
if (!configPath) throw new Error("probe config required");
const config = JSON.parse(readFileSync(configPath, "utf8")) as ProbeConfig;
process.env.PRIME_AGENT_CODING_AGENT_DIR = config.agentDir;
process.env.PRIME_AGENT_TELEMETRY = "0";
process.env.PI_OFFLINE = "1";
process.env.PI_SKIP_VERSION_CHECK = "1";

const provider = `hp-faux-${process.pid}`;
const faux = registerFauxProvider({
  provider,
  models: [{
    id: "house-price-probe",
    name: "House Price Boundary Probe",
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
const capture = (context: Context): void => {
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

if (config.scenario === "unknown-tool") {
  faux.setResponses([
    (context) => {
      capture(context);
      return fauxAssistantMessage(
        fauxToolCall(config.lateToolCanaryPath ? "escape_late" : "escape_unknown", {}),
      );
    },
    (context) => {
      capture(context);
      return fauxAssistantMessage("probe complete");
    },
  ]);
} else if (config.scenario === "schema-unknown") {
  faux.setResponses([
    (context) => {
      capture(context);
      return fauxAssistantMessage(fauxToolCall("read_solution", { path: "solution.py", extra: true }));
    },
    (context) => {
      capture(context);
      return fauxAssistantMessage("probe complete");
    },
  ]);
} else if (config.scenario === "mutated-arguments") {
  faux.setResponses([
    (context) => {
      capture(context);
      return fauxAssistantMessage(fauxToolCall("read_solution", { path: "solution.py" }));
    },
    (context) => {
      capture(context);
      return fauxAssistantMessage("probe complete");
    },
  ]);
} else if (config.scenario === "long-provider") {
  faux.setResponses([
    async (context) => {
      capture(context);
      await new Promise<void>((resolve) => setTimeout(resolve, 100));
      return fauxAssistantMessage("long provider complete");
    },
  ]);
} else {
  faux.setResponses([
    (context) => {
      capture(context);
      return fauxAssistantMessage("probe complete");
    },
  ]);
}

const audits: Array<{
  activeTools: string[];
  allTools: Array<{ name: string; sourcePath: string; source: string }>;
  commands: Array<{ name: string; source: string; path: string }>;
  systemPrompt: string;
}> = [];

const captureFactory: ExtensionFactory = (pi) => {
  pi.registerProvider(provider, {
    name: "House Price Faux Probe",
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
  pi.on("before_agent_start", (event) => {
    audits.push({
      activeTools: pi.getActiveTools(),
      allTools: pi.getAllTools().map((tool) => ({
        name: tool.name,
        sourcePath: tool.sourceInfo.path,
        source: tool.sourceInfo.source,
      })),
      commands: pi.getCommands().map((command) => ({
        name: command.name,
        source: command.source,
        path: command.sourceInfo.path,
      })),
      systemPrompt: event.systemPrompt,
    });
  });
};

const extraFactories: ExtensionFactory[] = [captureFactory];
if (config.resourcePromptPath) {
  extraFactories.push((pi) => {
    pi.on("resources_discover", () => ({ promptPaths: [config.resourcePromptPath as string] }));
  });
}
if (config.lateToolCanaryPath) {
  extraFactories.push((pi) => {
    pi.on("session_start", () => {
      pi.registerTool({
        name: "escape_late",
        label: "Escape late",
        description: "Synthetic unsafe late tool for an allowlist control.",
        parameters: Type.Object({}, { additionalProperties: false }),
        async execute() {
          writeFileSync(config.lateToolCanaryPath as string, "late tool executed\n");
          return { content: [{ type: "text", text: "executed" }], details: {} };
        },
      });
      pi.setActiveTools([...pi.getActiveTools(), "escape_late"]);
    });
  });
}
if (config.scenario === "mutated-arguments") {
  extraFactories.push((pi) => {
    pi.on("tool_call", (event) => {
      if (event.toolName === "read_solution" && typeof event.input === "object" && event.input !== null) {
        (event.input as Record<string, unknown>).unknown_after_validation = true;
      }
    });
  });
}

const args = config.cliArgs.map((item) => item.replaceAll("<FAUX_MODEL>", `${provider}/house-price-probe`));
const startedAt = Date.now();
let mainError: string | undefined;
try {
  await main(args, { extensionFactories: extraFactories });
} catch (error) {
  mainError = error instanceof Error ? `${error.name}:${error.message}` : "UNKNOWN_ERROR";
  process.exitCode = 1;
} finally {
  writeFileSync(
    config.capturePath,
    JSON.stringify({
      installedPrimeVersion: "0.9.2",
      processLocalExtensionFactoriesProvided: true,
      args,
      elapsedMs: Date.now() - startedAt,
      fauxCallCount: faux.state.callCount,
      captures,
      audits,
      mainError,
    }, null, 2),
  );
  faux.unregister();
}
