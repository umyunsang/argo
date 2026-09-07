import type { ExtensionAPI } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { createControllerExtension } from "../controller-extension.ts";

const captured: Array<{ name: string; description: string; parameters: unknown }> = [];
const extension = createControllerExtension({
  schemaVersion: "argo-house-price-controller-extension-binding/v1",
  expectedExtensionSha256: "8e2ca3351e601b5d4733000dc9c704f0327fdc941851fadbc0d3f59357d2d3fe",
  bridge: { command: "/usr/bin/false", argv: [] },
  limits: {
    maxRequestBytes: 262144, maxResponseBytes: 262144, maxListItems: 5,
    maxSourceContentBytes: 131072, maxPathBytes: 32, maxMetricAbs: 1000000000000,
    maxMetricDecimalPlaces: 6, maxRows: 292, bridgeTimeoutMs: 30000,
  },
});
const mock = {
  registerTool(tool: Parameters<ExtensionAPI["registerTool"]>[0]) {
    captured.push({ name: tool.name, description: tool.description, parameters: tool.parameters });
  },
} as unknown as ExtensionAPI;
await extension(mock);
if (captured.length !== 6) throw new Error("SCHEMA_CAPTURE_INVALID");
process.stdout.write(`${JSON.stringify(captured)}\n`);
