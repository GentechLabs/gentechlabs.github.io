# AAE Tooling Reference

> All platform configs, endpoints, credentials, and operational details.

## Paperclip Dashboard

- **Dashboard URL**: [REDACTED — see secure vault]
- **Login**: [REDACTED — see secure vault]
- **API**: http://127.0.0.1:3102/api
- **Auth**: Cookie + Origin header for mutations
- **Skills path**: auto-discovers ~/.hermes/skills/
- **Stuck fix**: kill `hermes chat` + `npm run start`, restart gateway
- **Philosophy**: "I don't marry technology" — use what works

## PentAGI Admin Panel

- **URL**: [REDACTED — see secure vault]
- **Login**: [REDACTED — see secure vault]

## VPS Specs

- **RAM**: 16GB
- **Storage**: 193GB total (~160GB free)
- **CPU**: 4 vCPU AMD
- **OS**: Linux

## Cron Jobs

| Job ID | Purpose | Schedule | Status |
|--------|---------|----------|--------|
| c4f8e875e50c | Merged DeFi dashboard (watchlist + LP) | 9a/3p/9p UTC | Active |
| 78e6b3eb210c | Old LP-only job | — | Paused |
| f8cccea870be | Agent Watchdog (3h stale check) | Continuous | Active |

## Voice/TTS Engine

### ElevenLabs (Primary)
- **Plan**: Starter $5/mo, 30K chars/month
- **Voices**: Gentech-Iroh, YoYo, D-Mob, Desmond-SH
- **Audio chain**: highpass=80, lowpass=8000, 96k opus

### Kokoro (Local Backup)
- **Voices**: am_adam, bm_george, am_onyx, am_michael
- **Model**: Kokoro-82M, Apache 2.0 license

### Fallback Stack
- Voicebox + Kokoro

## Watchdog Details

- **Job ID**: f8cccea870be
- **What it checks**: vault/08-Daily/agent-states/ files (updated every session)
- **NOT checking**: AGENTS.md (rarely changes — was the old bug)
- **Alert threshold**: stale agent >3h
- **Fixed**: Apr 18 — prompt rewritten to check agent-state files + Mess Hall chat
- **Recovery**: stale recovery flags cleaned up after fix

## Nous Subscription
- **Included**: Firecrawl (web tools), FAL (image gen), OpenAI TTS, Browser Use
- **Not using**: Firecrawl web tools (not selected), Modal (using local)
- **Active**: Image gen via FAL, ElevenLabs for TTS (not OpenAI TTS)
