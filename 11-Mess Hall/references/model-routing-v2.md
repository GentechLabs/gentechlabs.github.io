# Model Routing V2 — Unified Logic (Chat + Cron)
**Last updated:** 2026-07-23
**Status:** ✅ Active

## Principle
One routing logic applies to **every** LLM call — whether it's a chat session, a cron job, or a background agent. No manual per-job provider pinning. The router picks the best available model based on **task type + quota availability + cost**.

---

## Tier Definitions

| Tier | Default Model | Provider | Quota | Cost | Used For |
|------|--------------|----------|-------|------|----------|
| **T1 — Free** | DeepSeek V4 Flash | OpenCode Go | Unlimited | $0 | Daily ops, quick responses, simple reasoning |
| **T2 — Audit** | Kimi K2.7 | OpenCode Go | Unlimited | $0 | Code review, debugging, refactoring, QA |
| **T3 — Complex** | Kimi K3 | OpenCode Go | Included | $0 | Heavy reasoning, architecture, game design, audits |
| **T4 — Weekly** | DeepSeek V4 Flash | Ollama Cloud Pro | Weekly cap | $20/mo | Scheduled cron jobs, batch processing |
| **T5 — Emergency** | DeepSeek V4 Flash | Nous Research | Fallback | $20/mo | If OpenCode Go and Ollama Cloud are both down |
| **T6 — Cold** | Local models | VPS (CPU) | Unlimited | $0 | Last resort — Llama 3.2, Nemo Tron, Mistral 7B |

---

## Routing Logic (Applied In Order)

```
1. Is OpenCode Go available?
   → YES → Route to T1 (Free). Use V4 Flash for everything.
              If task needs audit → T2 (K2.7, same provider)
              If task needs complex reasoning → T3 (K3, same provider)
   → NO → Go to step 2

2. Is Ollama Cloud under weekly limit?
   → YES → Route to T4 (Weekly). Use V4 Flash.
   → NO (HTTP 429) → Go to step 3

3. Is Nous Research available?
   → YES → Route to T5 (Emergency). Use V4 Flash via Hermes.
   → NO → Go to step 4

4. Are local models available on VPS?
   → YES → Route to T6 (Cold). Use Mistral 7B or Nemo Tron 12B.
   → NO → Report outage. Cannot serve request.
```

---

## Cron Job Assignment

Cron jobs are no longer pinned to a specific provider. Instead, they specify a **tier**, and the router picks the best available provider at runtime.

### Cron Tiers

| Tier | Run Frequency | Routing | Examples |
|------|--------------|---------|---------|
| **Critical** | Multiple daily | OpenCode Go (T1) preferred | Morning Digest, PR Maintainer, Revenue Monitor |
| **Standard** | Daily | OpenCode Go (T1) preferred | Nightly Build, Build Queue, Hub Sync |
| **Weekly** | Weekly or less | Ollama Cloud (T4) acceptable | Sunday Review, API Marketplace Scout, Hive Monitor |
| **Background** | No LLM needed | No_agent scripts | API Safety Suite, Vault Watcher, CMC Watchlist |

### Cron Provider Fallback
If a cron job's assigned tier provider is unavailable:
- **Critical/Standard** → Fall back T4 (Ollama Cloud) → T5 (Nous) → T6 (Local)
- **Weekly** → Fall back T5 (Nous) → Skip if unavailable (non-critical)
- **Background** → Always runs (no LLM needed)

---

## Quota Budget Tracking

| Provider | Monthly Cost | Quota Type | Notes |
|----------|-------------|------------|-------|
| OpenCode Go | $10/mo | Unlimited* | *Fair use. No hard cap observed. Primary provider. |
| Ollama Cloud Pro | $20/mo | Weekly cap | Hit weekly limit Jul 23 (HTTP 429). Use for batch/weekly only. |
| Nous Research | $20/mo | Quota-based | Hermes Cloud for Forge. Emergency backup only. |
| **Total** | **$50/mo** | | *VPS ($42/mo) excluded — infrastructure cost, not model cost.* |

---

## Migration Status

| What | Status | Date |
|------|--------|------|
| Chat sessions | ✅ Follows T1→T6 routing automatically | Always |
| Cron jobs | ✅ All crons unpinned from specific providers | Jul 23 |
| Errored crons (Ollama 429) | ✅ Re-routed to OpenCode Go (T1) | Jul 23 |
| V2 doc written | ✅ Saved to model-routing.md | Jul 23 |
