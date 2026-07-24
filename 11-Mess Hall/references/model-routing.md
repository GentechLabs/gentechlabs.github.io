# Model Routing Configuration
**Last updated:** 2026-07-23

**⏩ V2 is now active. See `model-routing-v2.md` for the full routing logic.**

## Quick Reference

| Tier | Default | Provider | Cost |
|------|---------|----------|------|
| **T1 — Free** | V4 Flash | OpenCode Go | $0 |
| **T2 — Audit** | K2.7 | OpenCode Go | $0 |
| **T3 — Complex** | K3 | OpenCode Go | $0 |
| **T4 — Weekly** | V4 Flash | Ollama Cloud Pro | $20/mo |
| **T5 — Emergency** | V4 Flash | Nous Research | $20/mo |
| **T6 — Cold** | Mistral 7B | VPS (local) | $0 |

**Total model cost: $50/mo** (OpenCode $10 + Ollama $20 + Nous $20)
**Infrastructure: $42/mo** (VPS)
**Grand total: $92/mo**

## Key Change in V2
- **Cron jobs are no longer pinned to specific providers.** They specify a tier, and the router picks the best available provider at runtime.
- **Ollama Cloud reserved for batch/weekly work** — hit weekly cap Jul 23. High-frequency crons moved to OpenCode Go.
- **Fallback chain:** T1 → T4 → T5 → T6. Never a single point of failure.