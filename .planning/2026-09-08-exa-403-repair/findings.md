# Findings

- Prior unauthenticated public MCP initialize failed with HTTP403/Cloudflare1010 browser_signature_banned; no server tool invocation happened.
- Current Codex has no Exa server/plugin registration. ECC cached skill is not an active Exa connection.
- EXA_API_KEY exists in current process environment; value is not inspected or printed. Authenticated official API/local MCP is a separate supported path to verify.
- Memory says global MCP/plugins were deliberately disabled; current scoped Exa repair must preserve unrelated integration settings.

- User-supplied key via hidden stdin passed authenticated api.exa.ai/search HTTP200 with 3 real results. Search cost returned USD0.007. Key stored only in macOS Keychain service codex.exa.api-key/account exa; no key in repo or command argv.
- Official exa-mcp-server@3.4.1 is latest, published2026-08-18, Node>=20; local stdio with API key is officially supported.
