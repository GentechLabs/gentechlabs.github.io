# Model Routing Configuration
**Last updated:** 2026-07-21

## Stack
| Tier | Provider | Cost | Role |
|------|----------|------|------|
| 🥇 **Primary** | OpenCode Go → V4 Flash | $10/mo | Prototyping, content, daily ops |
| 🥇 **Complex** | OpenCode Go → K3/K2.7 | Included | Heavy reasoning, game design, audits |
| 🥇 **Fallback** | Nous Research (Hermes agent) | $20/mo | Emergency backup + agent platform |
| ⏸️ **Expiring** | GLM 5.2 sub | Runs out Jul 28 | Not renewing. GLM still available via OpenCode Go. |

**Total: ~$92/mo** ($10 OpenCode Go + $20 Nous Research + $20 Ollama Cloud Pro + $42 VPS)

*The Nous Research sub enables Hermes Cloud for Forge — 24/7 agent uptime. The VPS is our infrastructure backbone. Worth every penny.*

## Tiered Routing

| Layer | Model | When |
|-------|-------|------|
| **Base** | DeepSeek V4 Flash via OpenCode Go | Default for everything. Day-to-day work, quick responses, simple reasoning. |
| **Audit** | Kimi K2.7 via OpenCode Go | Code review, debugging, refactoring, QA. Default audit model. |
| **Complex** | Kimi K3 via OpenCode Go | Heavy reasoning, architecture, game design, strategic planning. |
| **Fallback** | GLM 5.2 via OpenCode Go | Only if K3 is unavailable (capacity crunch). GLM-5.2 direct sub expires Jul 28. |
| **Emergency** | Nous Research (Hermes default) | Free fallback if OpenCode Go is down. |

## Decision Logic (Develop & Verify)
1. **Develop:** DeepSeek V4 Flash (fast, cheap, unlimited quota)
2. **Verify/Audit:** Kimi K2.7 (review the work)
3. **Reason:** Kimi K3 (heavy thinking, design decisions, game logic)
4. **Polish:** Kimi K3 (front-end, UX, final pass)
5. **Fallback:** If K3 quota hit → GLM 5.2 via OpenCode Go
6. **Emergency:** If both down → Nous Research

## Resilience Strategy — "Big Brother Audits" (2026-07-21)

**Core insight:** We don't need every model to be the best. We need a cheap/fast coder + a powerful auditor. The auditor doesn't run every call — it spot-checks the important ones.

| Pattern | Coder | Auditor | Cost vs using auditor for everything |
|---------|-------|---------|--------------------------------------|
| **Current** | V4 Flash ($0) | K2.7 ($0) | Already free — both on OpenCode Go |
| **Local fallback** | Nemo Tron 12B (free) | K3 (OpenCode Go) | ~90% cheaper than K3 for everything |
| **Emergency** | Mistral 7B (free) | Claude Opus (pay-per-call) | ~95% cheaper than Opus for everything |

**The math:** If Claude Opus costs $15/hr of coding and Haiku costs $1/hr, using Haiku for 90% of the work + Opus to audit the final output = ~$2.50/hr. Same quality, 6x cheaper.

## Local Model Backup Plan

**What we can actually run on our VPS (CPU-only, 16-32GB RAM):**

| Model | Size | RAM | Quality | Role |
|-------|------|-----|---------|------|
| Llama 3.2 3B | 2GB | 4GB | Basic | Last-resort fallback |
| Nemo Tron 12B | 7GB | 12GB | Decent | Primary local coder |
| Mistral 7B | 4GB | 8GB | Good | Primary local coder |
| Qwen 2.5 7B | 4GB | 8GB | Good | Primary local coder |
| DeepSeek Coder 6.7B | 4GB | 8GB | Good | Code-specific fallback |

**What we CANNOT run on VPS (need GPU):**
- DeepSeek V4 Flash (671B) — needs 400GB+ VRAM
- Kimi K3 (2.8T) — needs 1.5TB+ VRAM
- Qwen 3.8 (2.4T) — needs 1.2TB+ VRAM

**Cold storage plan:** Download K3 weights Jul 27. Store on $50 external drive. Rent GPU ($0.50-2/hr) if needed.

## Notes
- "Same-provider rule" = V4 Flash + GLM fallback go through OpenCode Go. K3 (direct sub) goes through Kimi's API. This breaks the old "same provider" rule in favor of reliability — the priority is having a working model, not enforcing provider purity.
- Kimi K3 open source weights expected ~Jul 27, 2026. Once community quants land, we may self-host a distilled version.
- K3 new subscriptions are paused as of Jul 19 — we're on the waiting list for Code Membership.
- **Resilience principle:** A weak model + strong auditor > a single strong model. The auditor doesn't need to run every call — just the critical ones.
