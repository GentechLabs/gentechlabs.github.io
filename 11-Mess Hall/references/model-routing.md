# Model Routing Configuration
**Last updated:** 2026-07-19

## Stack
| Tier | Provider | Cost | Role |
|------|----------|------|------|
| 🥇 **Primary** | OpenCode Go → V4 Flash | $10/mo | Prototyping, content, daily ops |
| 🥇 **Complex** | OpenCode Go → K3/K2.7 | Included | Heavy reasoning, game design, audits |
| 🥇 **Fallback** | Nous Research (Hermes agent) | $20/mo | Emergency backup + agent platform |
| ⏸️ **Expiring** | GLM 5.2 sub | Runs out Jul 28 | Not renewing. GLM still available via OpenCode Go. |

**Total: ~$30/mo**

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

## Who This Applies To
- **Gentech** (Hermes Agent) — configured via provider/model settings
- **Forge** (Olima Cloud) — same models, same routing logic

## Notes
- "Same-provider rule" = V4 Flash + GLM fallback go through OpenCode Go. K3 (direct sub) goes through Kimi's API. This breaks the old "same provider" rule in favor of reliability — the priority is having a working model, not enforcing provider purity.
- Kimi K3 open source weights expected ~Jul 27, 2026. Once community quants land, we may self-host a distilled version.
- K3 new subscriptions are paused as of Jul 19 — we're on the waiting list for Code Membership.
