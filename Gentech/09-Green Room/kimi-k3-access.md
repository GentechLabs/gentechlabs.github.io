# Kimi K3 — Access via Existing Setups (verified Aug 15, 2026)

## Result: Kimi K3 is AVAILABLE through our existing OpenCode Go provider — and it's FREE (cost: 0)

Verified live: direct call to `https://opencode.ai/zen/go/v1/chat/completions` with model `kimi-k3`
- Response: `KIMI_K3_OK` ✅
- API reported `cost: "0"` — no extra usage charged
- Uses the existing `OPENCODE_GO_API_KEY` already in `~/.hermes/profiles/gentech/.env`

## Why this matters
Boss flagged the Kimi K3 viral tweet (premium website in 13 min). We don't need a new key or signup — Kimi K3 is **already in our OpenCode Go provider config** (line 16 of config.yaml):
```
models: ["deepseek-v4-flash","deepseek-v4-pro","kimi-k2.7-code","kimi-k3","glm-5.2","glm-5","qwen3.7-plus"]
```

## Provider status summary (all three setups checked)
| Setup | Kimi K3 status |
|-------|---------------|
| **OpenCode Go** | ✅ **AVAILABLE + FREE (cost 0)** — direct API works. Best route. |
| **Ollama Cloud** | ⚠️ Has kimi-k3:cloud but **NOT in any sub tier (even Max)** — PAYG only, extra usage credits. Avoid while conserving reset. |
| **Nous Portal** | ✅ Listed in Hermes model catalog (`moonshotai/kimi-k3`). Native subscription path. |

## How to use for coding work (free route)
Direct API (works now):
```
curl -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -d '{"model":"kimi-k3","messages":[...]}'
```
Note: OpenCode CLI (`opencode run --model opencode-go/kimi-k3`) returned a server error on first attempt — direct API call is the reliable path. CLI model reference may need a different naming format.

## Two birds, one stone
This setup: (1) gives us Kimi K3's premium web-design capability via existing infra, AND (2) routes our coding work through a FREE provider (cost 0) instead of burning the Ollama Cloud weekly reset. Aligned with conserving usage until tomorrow's reset.

## Still to verify (next)
- Whether Kimi K3 via OpenCode Go counts against a monthly quota or is truly unlimited-free
- OpenCode CLI model-name format for `kimi-k3`
- Nous Portal direct route (native sub)

*Source: live API test Aug 15, 2026. Recorded in 09-Green Room.*
