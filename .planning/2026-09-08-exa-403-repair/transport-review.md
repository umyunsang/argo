# Exa stdio transport review — 2026-09-08

Scope: read-only package/source review. No credentials or MCP configuration payloads read; no package installation, configuration changes, or Exa search API calls performed. This is an independent lane under the root repair plan. `planning-with-files` was read; this file contains the lane findings and completion record.

## Verified facts

- npm registry `latest` is `exa-mcp-server@3.4.1`, published `2026-08-18T19:39:05.639Z` (20 full days before 2026-09-08 UTC). It satisfies the repository's 7-day minimum release age. Node requirement is `>=20.0.0`.
- npm bin is `dist/stdio.cjs`; the package is a bundled executable. Registry gitHead is `66bacbe4afd35a7e1671be9ab55c2b6bf60aff34`. Registry metadata and the actual 3.4.1 tarball were read in memory without installation or extraction to disk.
- `src/stdio-cli.ts` calls `main()` without parsing user CLI arguments. `src/stdio.ts` uses `StdioServerTransport` and reads `EXA_API_KEY`, `ENABLED_TOOLS` (fallback `TOOLS`), `DEBUG`, and `DEFAULT_SEARCH_TYPE` from the environment.
- Pinned invocation: `npx -y exa-mcp-server@3.4.1`, or `node <verified-install>/dist/stdio.cjs`. Do not depend on `--tools` for this version. Set `ENABLED_TOOLS=web_search_exa,web_fetch_exa,web_search_advanced_exa` if those three tools are wanted; selection replaces defaults. Empty selection means server defaults.
- `web_search_exa` accepts `query` and optional `numResults` (default 10). The 3.4.1 simple tool has no `type`, `livecrawl`, or `contextMaxCharacters` parameter. Set `DEFAULT_SEARCH_TYPE=fast` if needed, or use advanced search after inspecting its schema.
- Search follows `createExaClient(config)` → `new Exa(key)` → `exa.request('/search', 'POST', ...)`. The actual bundled Exa SDK constructor defaults to `https://api.exa.ai` and creates `x-api-key`, `Content-Type: application/json`, and SDK User-Agent headers. The simple tool requests highlights and uses a 60-second tool timeout.

## Interpretation of existing 403 evidence

Root reports anonymous urllib `initialize` against `https://mcp.exa.ai/mcp` returned HTTP 403 with Cloudflare 1010 / `browser_signature_banned`. That identifies a hosted HTTP gateway rejection for that request; it does not establish an invalid API key, and no new-key authentication was tested in this lane. The officially supported local stdio server uses the separate authenticated Exa API endpoint; it is an appropriate supported transport to validate with the user's key. It is not evidence that the hosted endpoint itself has recovered.

## Node MCP SDK call contract

Locally inspected SDK files:

- `/opt/homebrew/lib/node_modules/@bitkyc08/opencodex/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.d.ts`
- `/opt/homebrew/lib/node_modules/@bitkyc08/opencodex/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js`

`StdioClientTransport` accepts `command`, `args`, `env`, `cwd`, and `stderr`. `Client.connect(transport)` starts transport and performs MCP initialization; do not separately start transport first. `listTools()` performs `tools/list`; `callTool({name, arguments}, undefined, {timeout})` performs `tools/call`. Tool-level errors can be returned with `isError: true`, so transport success alone is insufficient.

Illustrative code only; not executed by this lane. `loadedKey` is supplied privately by the root repair process, and `serverBundlePath` is a verified installed bundle path:

```js
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport, getDefaultEnvironment } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [serverBundlePath],
  env: {
    ...getDefaultEnvironment(),
    EXA_API_KEY: loadedKey,
    ENABLED_TOOLS: 'web_search_exa',
    DEBUG: 'false',
  },
  stderr: 'pipe',
});
const client = new Client({ name: 'exa-repair-validation', version: '1.0.0' });
try {
  await client.connect(transport, { timeout: 30000 });
  const tools = await client.listTools();
  const result = await client.callTool({
    name: 'web_search_exa',
    arguments: { query: 'Exa official search API documentation', numResults: 1 },
  }, undefined, { timeout: 70000 });
  // Validate tool name/schema and result.isError/content without logging credentials.
} finally {
  await client.close();
}
```

## Sources

- [npm registry metadata](https://registry.npmjs.org/exa-mcp-server)
- [Pinned package metadata](https://github.com/exa-labs/exa-mcp-server/blob/66bacbe4afd35a7e1671be9ab55c2b6bf60aff34/package.json)
- [Pinned stdio configuration](https://github.com/exa-labs/exa-mcp-server/blob/66bacbe4afd35a7e1671be9ab55c2b6bf60aff34/src/stdio.ts)
- [Pinned CLI bootstrap](https://github.com/exa-labs/exa-mcp-server/blob/66bacbe4afd35a7e1671be9ab55c2b6bf60aff34/src/stdio-cli.ts)
- [Pinned Exa client creation](https://github.com/exa-labs/exa-mcp-server/blob/66bacbe4afd35a7e1671be9ab55c2b6bf60aff34/src/tools/config.ts)
- [Pinned simple search implementation](https://github.com/exa-labs/exa-mcp-server/blob/66bacbe4afd35a7e1671be9ab55c2b6bf60aff34/src/tools/webSearch.ts)
- [Exa official API reference](https://exa.ai/docs/reference/search)
- [Official npm installation instructions](https://github.com/exa-labs/exa-mcp-server/blob/main/npm.readme.md)

Status: source and package contract review complete. Authentication, actual search, Codex discovery, and Desktop session reload remain root-owned validation surfaces. No relevant memory evidence was found or reused. Optional Codex configuration review was not undertaken; only local `codex --help` was read.
