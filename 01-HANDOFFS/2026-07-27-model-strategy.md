# Forge — Model Strategy Update

**Date:** Jul 27, 2026

**Kimi K3 is now available on Ollama Cloud.** This changes our model strategy.

## New Model Strategy

| Role | Model | When |
|------|-------|------|
| **Primary** | deepseek-v4-flash | All standard work, builds, cron jobs |
| **Audit/Reasoning** | kimi-k3:cloud | Code reviews, audits, complex reasoning tasks |

## What This Means for You

1. **Your default model stays deepseek-v4-flash** — it's fast, cheap, and handles 95% of work
2. **Use Kimi K3 for:** code audits, security reviews, complex debugging, architecture decisions
3. **Harness Critic** has been switched to Kimi K3 — anti-collusion with Evolution (deepseek-v4-flash)

## How to Use Kimi K3

```bash
# In your prompts, specify when you need it
# For audits/reviews, use kimi-k3:cloud
# For standard work, stick with deepseek-v4-flash
```

## Context

- All 29 cron jobs are on ollama-cloud
- Kimi K3 requires Pro/Max subscription + extra credits
- Use it sparingly — reserve for when reasoning depth matters

## Build Queue

- v32 — Model strategy documented
- OKX #72 cancelled (deadline missed)
- Algorand #82 is top priority
- SPC Founder Fellowship application due Aug 2
