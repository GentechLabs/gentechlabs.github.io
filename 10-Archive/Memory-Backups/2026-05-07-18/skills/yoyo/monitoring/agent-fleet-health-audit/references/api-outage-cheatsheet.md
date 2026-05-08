# API Outage Cheatsheet — Hermes Agent Providers

Quick identification guide for third-party service failures observed in gateway error logs.

## ElevenLabs TTS

**Error signature:**
```
elevenlabs.core.api_error.ApiError: status_code: 401, body:
{'detail': {'status': 'quota_exceeded',
            'message': 'This request exceeds your quota of 121002.
You have 0 credits remaining, while X credits are required.'}}
```

**Severity:** Critical — TTS functions fully broken
**Affected:** All agents ( fleet-wide, 2026-05-04 )
**Check:** https://elevenlabs.io/app/usage
**Fix:** Top up billing OR switch fallback TTS provider in config

---

## OpenAI Vision / Chat

**Error signature (Vision 404):**
```
tools.vision_tools: Error analyzing image: Error code: 404 -
{'status': 404, 'message': "Couldn't find that, sorry."}
openai.NotFoundError: Error code: 404 - {'status': 404, 'message': "Couldn't find that, sorry."}
```

**Error signature (Provider unknown):**
```
agent.auxiliary_client: resolve_provider_client: unknown provider 'openai'
```

**Severity:** High — vision analysis + GPT models broken
**Root causes:**
- `404` — Model name deprecated/changed; check `OPENAI_MODEL` env var
- `unknown provider` — Auth header missing/invalid; check `OPENAI_API_KEY`
**Check:** https://status.openai.com

---

## Anthropic

**Error signature:**
```
agent.auxiliary_client: resolve_provider_client: anthropic requested but no Anthropic credentials found
```

**Severity:** Medium — fallback LLM path broken
**Fix:** Set `ANTHROPIC_API_KEY` in agent `.env` or keychain

---

## Telegram

**Error signature (Flood control):**
```
gateway.platforms.telegram: [Telegram] Telegram flood control on send (attempt 1/3), retrying in 10.0s: Flood control exceeded
```

**Severity:** Low — backpressure working; will auto-retry
**Action:** Wait; if persistent, reduce send burst size

**Error signature (Chat not found):**
```
gateway.platforms.telegram: [Telegram] Failed to send Telegram message: Chat not found
```

**Severity:** High — agent cannot deliver messages
**Root causes:**
- Chat ID changed (group recreated, bot removed)
- Bot not added to target chat
- Using user ID instead of group ID
**Fix:** Verify `TELEGRAM_CHAT_ID` in agent config matches active chat

---

## Provider Health Matrix

| Provider | Agent Impact | Status (2026-05-04) | Monitor Link |
|----------|--------------|---------------------|--------------|
| ElevenLabs | All (TTS) | 🟥 Out — quota 0 | elevenlabs.io/app/usage |
| OpenAI | All (Vision/Chat) | 🟥 Degraded — 404 model errors | status.openai.com |
| Anthropic | All (fallback) | 🟨 Unconfigured — missing key | docs.anthropic.com |
| Telegram | Gentech only | 🟥 Broken — Chat not found | @BotFather → /status |

---

*Source: 2026-05-04 agent error.log sweep; patterns used in agent-fleet-health-audit skill.*