# Exa capability receipt

- Checked at 2026-09-08 UTC.
- User Codex config has no Exa MCP entry; project `.codex/config.toml` is absent.
- ECC 2.2.1 contains the Exa skill but the ECC plugin is disabled. No standalone Exa plugin was located under the installed plugin cache.
- The official Exa document (<https://exa.ai/docs/reference/exa-mcp>) documents the public endpoint `https://mcp.exa.ai/mcp` and a free plan. This supported one configuration-free, credential-free MCP initialization attempt.
- Initialization failed with HTTP 403, Cloudflare 1010 `browser_signature_banned`; the response says `retryable: false`, `owner_action_required: true`, and “Do not retry.” No retry or browser-signature workaround was performed.
- `tools/list` and `tools/call` were not attempted because initialization failed. No Exa scholarly search succeeded, and no paper claims can be attributed to this attempted search.

## Safe reuse after the external block is resolved

Use the same endpoint with `Content-Type: application/json`, `Accept: application/json, text/event-stream` and the `initialize` JSON request retained in `receipt.json`. Read the negotiated protocol version and session header in process, send `notifications/initialized`, then `tools/list`, and only then call the actually exposed search tool. Never serialize authentication headers or session identifiers into artifacts. No installation, user configuration change, or credential copying is needed for the documented public free endpoint. Do not repeat this call until the service-side block is resolved.

The intended public query is retained in `receipt.json`. `initialize.raw.txt` is the verbatim response body; `initialize.json` is its decoded JSON representation. No keys or credentials were used.
