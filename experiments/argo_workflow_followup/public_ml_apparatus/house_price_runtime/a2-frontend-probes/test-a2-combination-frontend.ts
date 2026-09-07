import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type {
  ExtensionAPI,
  ExtensionFactory,
  MainOptions,
} from "/opt/homebrew/lib/node_modules/prime-agent/dist/index.js";
import type {
  Context,
  FauxProviderRegistration,
  FauxResponseStep,
  Model,
} from "/opt/homebrew/lib/node_modules/prime-agent/node_modules/@earendil-works/pi-ai/dist/index.js";
import type { PreparedControllerMain } from "../controller-main.ts";
import {
  runSyntheticCombination,
  type SyntheticCombinationMetadata,
} from "./a2-combination-frontend.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const SCHEMA_AUTHORITY_PATH = join(HERE, "controller-tool-schema-authority-v1.json");
const EXPECTED_SCHEMA_SHA256 = "553e00b05207cc51eaf80d3d58ff480279319990ce620409ea52a1e4d281ad61";

const TOOL_NAMES = [
  "read_solution",
  "write_solution",
  "request_R1_run",
  "read_public_result",
  "read_dev_result",
  "lock_final_artifact",
] as const;

type Test = { name: string; run: () => Promise<void> | void };
const tests: Test[] = [];

function test(name: string, run: Test["run"]): void {
  tests.push({ name, run });
}

function parameters(properties: Record<string, object>) {
  return { type: "object", properties, additionalProperties: false };
}

function validContext(): Context {
  const bytes = readFileSync(SCHEMA_AUTHORITY_PATH);
  assert.equal(createHash("sha256").update(bytes).digest("hex"), EXPECTED_SCHEMA_SHA256);
  const tools = JSON.parse(bytes.toString("utf8")) as Context["tools"];
  return { systemPrompt: "synthetic", messages: [], tools };
}

function contextWithMutation(mutate: (tools: NonNullable<Context["tools"]>) => void): Context {
  const context = validContext();
  assert.ok(context.tools);
  mutate(context.tools);
  return context;
}

function prepared(overrides: { mainArgs?: string[]; verify?: () => void } = {}): PreparedControllerMain {
  const args = overrides.mainArgs ?? [
    "--print", "--mode", "text", "--model", "openai-codex/gpt-5.6-sol",
    "--tools", TOOL_NAMES.join(","), "--", "synthetic task",
  ];
  return {
    deployment: { directories: { artifact_root: { path: "/synthetic/artifacts" } } },
    mainArgs: args,
    fixedFactories: [(() => undefined) as ExtensionFactory],
    verifyPostflight: overrides.verify ?? (() => undefined),
  } as unknown as PreparedControllerMain;
}

interface FakeRegistration extends FauxProviderRegistration {
  pending: FauxResponseStep[];
  unregistered: boolean;
}

function fakeRegistration(): FakeRegistration {
  const model: Model<string> = {
    id: "gpt-5.6-sol",
    name: "A2 Synthetic Combination Faux",
    api: "a2-faux-api",
    provider: "openai-codex",
    baseUrl: "http://localhost:0",
    reasoning: true,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 4096,
  };
  const registration = {
    api: "a2-faux-api",
    models: [model],
    state: { callCount: 0 },
    pending: [] as FauxResponseStep[],
    unregistered: false,
    getModel: (id?: string) => (id === undefined || id === model.id ? model : undefined),
    setResponses(responses: FauxResponseStep[]) {
      registration.pending = [...responses];
    },
    appendResponses(responses: FauxResponseStep[]) {
      registration.pending.push(...responses);
    },
    getPendingResponseCount: () => registration.pending.length,
    unregister() {
      registration.unregistered = true;
    },
  };
  return registration as FakeRegistration;
}

function mockPi(onBeforeAgentStart: (handler: (event: unknown, context: unknown) => unknown) => void): ExtensionAPI {
  return {
    registerProvider(name: string, config: Parameters<ExtensionAPI["registerProvider"]>[1]) {
      assert.equal(name, "openai-codex");
      assert.equal(config.apiKey, "faux-test-only");
      assert.equal(config.models?.length, 1);
      assert.equal(config.models?.[0]?.id, "gpt-5.6-sol");
    },
    on(event: string, handler: unknown) {
      if (event === "before_agent_start" && typeof handler === "function") {
        onBeforeAgentStart(handler as (event: unknown, context: unknown) => unknown);
      }
    },
    getActiveTools: () => [...TOOL_NAMES],
  } as unknown as ExtensionAPI;
}

async function consume(
  registration: FakeRegistration,
  context: Context,
): Promise<Array<{ responseId?: string; content: unknown[] }>> {
  const messages: Array<{ responseId?: string; content: unknown[] }> = [];
  while (registration.pending.length > 0) {
    const step = registration.pending.shift();
    if (typeof step !== "function") throw new Error("expected response factory");
    registration.state.callCount += 1;
    const message = await step(context, undefined, registration.state, registration.models[0]);
    assert.ok(message);
    messages.push({ responseId: message.responseId, content: message.content });
  }
  return messages;
}

async function expectFullSchemaRejection(context: Context): Promise<void> {
  const fixture = fakeRegistration();
  await assert.rejects(
    runSyntheticCombination(
      prepared(),
      async (_args, options) => {
        const handlers: Array<(event: unknown, context: unknown) => unknown> = [];
        const pi = mockPi((handler) => handlers.push(handler));
        for (const factory of options?.extensionFactories ?? []) await factory(pi);
        await handlers[0]({}, {});
        await consume(fixture, context);
        return undefined;
      },
      () => fixture,
      () => undefined,
    ),
    /A2_SYNTHETIC_FRONTEND_FAILED/,
  );
  assert.equal(fixture.unregistered, true);
}

test("identical wrong property type is rejected against root authority", async () => {
  await expectFullSchemaRejection(contextWithMutation((tools) => {
    const path = (tools[0].parameters as { properties: { path: { type: string } } }).properties.path;
    path.type = "number";
  }));
});

test("identical wrong required array is rejected against root authority", async () => {
  await expectFullSchemaRejection(contextWithMutation((tools) => {
    (tools[1].parameters as { required: string[] }).required = ["content", "path"];
  }));
});

test("identical wrong description is rejected against root authority", async () => {
  await expectFullSchemaRejection(contextWithMutation((tools) => {
    tools[2].description = "Synthetic wrong description";
  }));
});

test("identical extra JSON schema keyword is rejected against root authority", async () => {
  await expectFullSchemaRejection(contextWithMutation((tools) => {
    (tools[3].parameters as unknown as Record<string, unknown>).unevaluatedProperties = false;
  }));
});

test("mocked main receives unchanged args and exactly one additional test-only factory", async () => {
  const fixture = fakeRegistration();
  const original = prepared();
  const originalArgs = [...original.mainArgs];
  let verified = 0;
  original.verifyPostflight = () => {
    verified += 1;
  };
  let metadata: SyntheticCombinationMetadata | undefined;
  const callMain = async (args: string[], options?: MainOptions): Promise<undefined> => {
    assert.deepEqual(args, originalArgs);
    assert.equal(options?.extensionFactories?.length, 2);
    const handlers: Array<(event: unknown, context: unknown) => unknown> = [];
    const pi = mockPi((handler) => handlers.push(handler));
    for (const factory of options?.extensionFactories ?? []) {
      await factory(pi);
    }
    assert.equal(handlers.length, 1);
    await handlers[0]({}, {});
    const messages = await consume(fixture, validContext());
    assert.deepEqual(messages.map((message) => message.responseId), [
      "a2-combination-response-0001",
      "a2-combination-response-0002",
    ]);
    const first = messages[0].content[0] as { type?: string; name?: string; arguments?: object };
    assert.equal(first.type, "toolCall");
    assert.equal(first.name, "read_public_result");
    assert.deepEqual(first.arguments, {});
    return undefined;
  };
  const result = await runSyntheticCombination(
    original,
    callMain,
    () => fixture,
    (value, artifactRoot) => {
      assert.equal(artifactRoot, "/synthetic/artifacts");
      metadata = value;
    },
  );
  assert.deepEqual(original.mainArgs, originalArgs);
  assert.equal(verified, 1);
  assert.equal(fixture.unregistered, true);
  assert.equal(result, metadata);
  assert.equal(result.test_only, true);
  assert.equal(result.provider_call_count, 2);
  assert.match(result.tool_schema_sha256, /^[0-9a-f]{64}$/);
  assert.equal(Buffer.byteLength(`${JSON.stringify(result)}\n`, "utf8") <= 4096, true);
});

test("schema drift fails before metadata and always unregisters", async () => {
  const fixture = fakeRegistration();
  const context = validContext();
  context.tools?.push({ name: "escape_late", description: "escape", parameters: parameters({}) });
  let sinkCalls = 0;
  await assert.rejects(
    runSyntheticCombination(
      prepared(),
      async (_args, options) => {
        const pi = mockPi(() => undefined);
        for (const factory of options?.extensionFactories ?? []) await factory(pi);
        await consume(fixture, context);
        return undefined;
      },
      () => fixture,
      () => {
        sinkCalls += 1;
      },
    ),
    /A2_SYNTHETIC_FRONTEND_FAILED/,
  );
  assert.equal(sinkCalls, 0);
  assert.equal(fixture.unregistered, true);
});

test("fewer than two provider calls fails without fallback", async () => {
  const fixture = fakeRegistration();
  await assert.rejects(
    runSyntheticCombination(
      prepared(),
      async (_args, options) => {
        const handlers: Array<(event: unknown, context: unknown) => unknown> = [];
        const pi = mockPi((handler) => handlers.push(handler));
        for (const factory of options?.extensionFactories ?? []) await factory(pi);
        await handlers[0]({}, {});
        const first = fixture.pending.shift();
        if (typeof first !== "function") throw new Error("expected response factory");
        fixture.state.callCount = 1;
        await first(validContext(), undefined, fixture.state, fixture.models[0]);
        return undefined;
      },
      () => fixture,
      () => undefined,
    ),
    /A2_SYNTHETIC_FRONTEND_FAILED/,
  );
  assert.equal(fixture.getPendingResponseCount(), 1);
  assert.equal(fixture.unregistered, true);
});

test("more than two provider calls fails without another response or fallback", async () => {
  const fixture = fakeRegistration();
  await assert.rejects(
    runSyntheticCombination(
      prepared(),
      async (_args, options) => {
        const handlers: Array<(event: unknown, context: unknown) => unknown> = [];
        const pi = mockPi((handler) => handlers.push(handler));
        for (const factory of options?.extensionFactories ?? []) await factory(pi);
        await handlers[0]({}, {});
        await consume(fixture, validContext());
        fixture.state.callCount = 3;
        return undefined;
      },
      () => fixture,
      () => undefined,
    ),
    /A2_SYNTHETIC_FRONTEND_FAILED/,
  );
  assert.equal(fixture.getPendingResponseCount(), 0);
  assert.equal(fixture.unregistered, true);
});

test("prepared binding rejects provider or tool changes before Faux registration", async () => {
  let factoryCalls = 0;
  for (const args of [
    ["--model", "other/model", "--tools", TOOL_NAMES.join(",")],
    ["--model", "openai-codex/gpt-5.6-sol", "--tools", `${TOOL_NAMES.join(",")},escape_late`],
    ["--model", "openai-codex/gpt-5.6-sol", "--tools", TOOL_NAMES.join(","), "--api-key", "forbidden"],
  ]) {
    await assert.rejects(
      runSyntheticCombination(prepared({ mainArgs: args }), async () => undefined, () => {
        factoryCalls += 1;
        return fakeRegistration();
      }),
      /A2_SYNTHETIC_FRONTEND_FAILED/,
    );
  }
  assert.equal(factoryCalls, 0);
});

async function main(): Promise<void> {
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
  process.stdout.write(`${JSON.stringify({ total: tests.length, failures: failures.length })}\n`);
  if (failures.length > 0) process.exitCode = 1;
}

await main();
