# Handoff: Ollama Cloud Integration
- **From:** YoYo (Strategies group)
- **To:** Dmob
- **Requested by:** Jordan
- **Date:** 2026-04-17
- **Priority:** 🟡 MEDIUM — enables 24/7 uptime

## Jordan's Decision
- **KEEP Nous** ($20/mo) — complex work + managed tools
- **ADD Ollama Cloud** ($20/mo) — cheap 24/7 routine tasks
- **NO local Ollama** — save VPS resources

## Ollama Credentials
- **API Key:** `5003d76ec5254a9eb94f4fa473f28bee.MmeUWVTZIWgfPtD2lywYRn78`
- **API Base URL:** `https://api.ollama.com/v1`
- **Plan:** Pro ($20/mo, active until May 9, 2026)

## Setup Steps
1. Add Ollama as a provider in Hermes config
2. Set API base URL: `https://api.ollama.com/v1`
3. Add the API key
4. Choose cloud models (watch this video for model recommendations: https://youtu.be/Af7Fg1m7hRw — "Top AI Models for Hermes Agent (Tier List)")
5. Configure routing:
   - Complex work → Nous (MiMo, Qwen)
   - Routine tasks → Ollama Cloud (cheaper model)
   - Cron jobs → Ollama Cloud
6. Test with a simple task

## What NOT to Do
- Do NOT install Ollama locally on VPS
- Do NOT change Nous config
- Do NOT replace managed tools

## Video Reference
"Top AI Models for Hermes Agent (Tier List)" by BoxminingAI
- Tested every major AI model with Hermes for a month
- Ranked: orchestrators, executors, auxiliary support
- Watch to pick the best Ollama cloud models

## Deliverable
- Ollama cloud configured as secondary provider
- Cheapest/best model selected for routine tasks
- Cron jobs routed to Ollama
- Report back with model choice + test results

## Docs
- Migration plan: `03-Strategies/nous-to-ollama-migration.md`
- Subscription analysis: `03-Strategies/subscription-optimization.md`
