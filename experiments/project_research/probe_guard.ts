import { AuthStorage } from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import { getModel } from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import { createRequestGuard } from "./campaign_controller.ts";
import type { HostBridge, ModelChoice } from "./campaign_controller.ts";

// Bounded live probe of the subscription request guard; one tiny request, no scientific content.
const storage = AuthStorage.create();
const { apiKey } = await storage.getApiKeyWithSourceToken("anthropic", {});
const model = getModel("anthropic", "claude-sonnet-4-6");
const choice: ModelChoice = { id: "anthropic/claude-sonnet-4-6", provider: "anthropic", model_id: "claude-sonnet-4-6", status: "QUALIFIED", billing_upper_krw: 0, billing_basis: "probe", billing_mode: "subscription", billing_authorized: true };
const calls: unknown[] = [];
const bridge: HostBridge = async (action, args) => { calls.push({ action, usage: args.usage }); return { status: action === "reserve_model" ? "RESERVED" : "SETTLED" }; };
const guard = createRequestGuard(choice, bridge, { deadline: Date.now() / 1000 + 120, ownerSessionId: "probe" });
const stream = guard.streamFn(model, { messages: [{ role: "user", content: "Reply with exactly the word READY.", timestamp: Date.now() }] }, { apiKey, reasoning: "high", sessionId: "probe" });
let final: { stopReason?: string; errorMessage?: string; usage?: unknown } | undefined;
for await (const event of stream) { if (event.type === "done") final = event.message; else if (event.type === "error") final = event.error; }
console.log(JSON.stringify({ stopReason: final?.stopReason, errorMessage: final?.errorMessage?.slice(0, 300), usage: final?.usage, blocked: guard.blockedReason(), calls }, null, 1));

