# Bounded model and billing qualification

Scope: preparation-only qualification, not an autonomous research campaign. Parent's latest direction allocates common preparation costs to existing development-wine (first_week), preserving the first campaign's wall clock.

## Plan

1. Read shared Store/bridge/controller and official model/billing/routing interfaces — complete.
2. Implement raw invoice parsing, conservative KRW allocation, reserved/no-retry bounded probes and focused negative tests — pending.
3. Make at most two tiny paid requests, one openai/gpt-5.6-sol and one registered Claude, each after shared reservation <=100 KRW; stop next call on missing invoice or credit failure — BLOCKED_INSUFFICIENT_CREDITS before any generation request.
4. Hand exact IDs, raw billing fields, bounds and native stream integration scheme to root/runtime lane — pending.

## Authority and limits

- Existing credential is loaded only in memory from ~/.prime/agent/auth.json openrouter.key. Do not print or persist credentials, change credentials/accounts, top up credits or retry a generation.
- Shared Store: ~/.local/share/argo-project-research-20260909/control/state.sqlite; project development-wine, phase first_week.
- Probe total additional authorization <=200 KRW, still inside the nonresetting 300000 KRW cap.
- Dollar conversion uses ceil(actual invoice USD * 2000) for conservative KRW budget allocation. This is an allocation rate, not a quoted FX rate.
- Unknown invoices remain UNKNOWN and block additional paid dispatch. No default zero usage/cost.

## Findings

- Read state.py and campaign_bridge.py in full; Store atomically reserves before request, blocks UNKNOWN across charge/compute ledgers, and sets over-reservation invoices UNKNOWN.
- Current campaign controller only admits openai-codex subscription route; runtime integration lane is adding OpenRouter using native SDK streams. This qualification lane does not edit controller/native code.
- Official /models currently lists openai/gpt-5.6-sol at prompt $0.000002/token, completion $0.00001/token. Registered Claude options include claude-sonnet-5 at the same text prices and claude-opus-5 at $0.000005/$0.000025. Concrete Claude choice pending endpoint/SDK registration check.
- Official usage-accounting and routing documents opened; raw usage.cost and provider-routing restrictions are being checked before paid requests.
- Official usage-accounting states usage.cost is the amount charged to the account, included in complete JSON or final SSE frame; upstream_inference_cost and SDK estimates are not substitutes. Deprecated usage.include/stream_options.include_usage need not be sent.
- Selected common actual catalog/native-SDK IDs are openai/gpt-5.6-sol and anthropic/claude-sonnet-5. Both use openai-completions and https://openrouter.ai/api/v1 in the installed native registry. Provider endpoint tags openai and anthropic, display names OpenAI and Anthropic; dated catalog aliases openai/gpt-5.6-sol-20260709 and anthropic/claude-sonnet-5-20260630. Returned identities remain unverified without successful generation.
- Live authenticated GET /api/v1/credits returned HTTP 200, total_credits=0, total_usage=0.000255. Remaining purchased credits are -0.000255 USD. No generation request or reservation was made; parent/runtime lane were notified immediately. No topup or account change.
- Shared Store snapshot before qualification had no charge entries and no UNKNOWN compute leases. Existing development-wine contract confirmed.
- Native SDK defaults cacheRetention=short and may inject Anthropic cache_control. Runtime lane was told to disable requested cache writes or reserve their higher known prices; prompt price alone is not a safe cache-write bound.

## Progress

No paid request made. No reservation made. Source/API lookups are read-only. Implementing bounded future probes plus invoice-validation tests without dispatching generations under the known credit blocker.
