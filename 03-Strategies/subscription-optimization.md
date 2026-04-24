# 💰 Subscription Optimization Analysis

## Current Subscriptions
| Service | Est. Cost | Purpose |
|---------|-----------|---------|
| Nous (Hermes) | $50-100/mo | Agent platform, model access, Telegram integration |
| OpenCode | ~$20/mo | Coding workspace with any model |
| Ollama | ~$20/mo (if active) | Cloud + local models |

## Recommended Setup
| Service | Cost | Purpose |
|---------|------|---------|
| **Ollama** | ~$20-30/mo | Primary model provider (cloud + local) |
| **OpenCode** | ~$20/mo | Coding workspace |
| **Total** | ~$40-50/mo | **Saves $30-70/mo vs current** |

## Why Ollama Wins
- Cloud models for complex work
- Local models for 24/7 agent uptime
- No rate limits on local
- One subscription, dual capability
- Hermes install script is free (open-source)

## What Nous Subscription Actually Provides
- Model access (MiMo, Qwen via API)
- Managed web tools (Firecrawl)
- Image generation (FAL)
- OpenAI TTS
- Browser automation

## If Dropping Nous
- Firecrawl → use Hyperbrowser (backup) or direct web scraping
- Image generation → FAL direct or alternatives
- TTS → ElevenLabs (already using)
- Browser → Browser Use (could run locally via Ollama)

## Decision Framework
- **Keep Nous if:** Heavily using managed tools (Firecrawl, FAL) that aren't easily replaceable
- **Drop Nous if:** Ollama models match quality and you can self-host alternatives
- **Test first:** Run Ollama for 1 week, compare quality to current models

## Timeline
1. Check Ollama subscription status
2. If active → start routing tasks immediately
3. If inactive → reactivate, test for 1 week
4. After test → make keep/drop decision on Nous

## Date
2026-04-17
