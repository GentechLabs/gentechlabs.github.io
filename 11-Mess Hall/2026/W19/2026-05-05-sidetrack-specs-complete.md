# Sidetrack Adapter Specs Complete
**Date:** 2026-05-05 17:30 UTC
**From:** YoYo (Strategies)

---

## Status
✅ Jordan confirmed **Option B** — Zerion ($5K) + GoldRush ($3K) = $8K total

## What I Did
1. **Researched both APIs** — Zerion (developers.zerion.io) and GoldRush (goldrush.mintlify.app)
2. **Created detailed adapter specs** — `09-Green Room/active-handoffs/sidetrack-adapter-specs.md`
   - Zerion: HTTP Basic Auth, portfolio/DeFi/PnL endpoints, TypeScript SDK
   - GoldRush: API key, balances/transactions/risk scoring, TypeScript SDK (`@covalenthq/client-sdk`)
3. **Updated sprint plan** — Both adapters now in `02-Labs/Hackathons/Active/sidetrack-sprint.md`
4. **Updated DMOB handoff** — `09-Green Room/active-handoffs/zerion-cli-sidetrack-handoff.md` now covers both sidetracks

## Key API Details
| API | Auth | SDK | Solana | Cost |
|-----|------|-----|--------|------|
| Zerion | HTTP Basic Auth (API key) | `@zerion/api` | ✅ | Free tier or x402 |
| GoldRush | API key | `@covalenthq/client-sdk` | ✅ | $10/mo or free tier |

## What DMOB Needs Tomorrow (May 6)
1. Register for Zerion API key (dashboard.zerion.io)
2. Register for GoldRush API key (goldrush.covalenthq.com)
3. Scaffold both adapter projects
4. Start building — main submission first, adapters last 2 days

## Workflow Directive
Jordan confirmed: **Don't idle.** When hitting a stopping point, queue up next project and start working.

---

*Vault synced. Ready for DMOB to pick up tomorrow.*
