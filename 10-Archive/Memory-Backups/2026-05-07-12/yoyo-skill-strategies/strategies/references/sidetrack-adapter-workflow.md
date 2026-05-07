# Sidetrack Adapter Workflow — Reference

## API Research Template

For each sidetrack sponsor, fill out:

| Field | Value |
|-------|-------|
| **Sponsor** | Name |
| **Bounty** | $ amount |
| **Deliverable** | What they want |
| **API Auth** | API key / OAuth / x402 / MCP |
| **SDK** | `@package/name` or REST-only |
| **Key Endpoints** | List top 3-5 endpoints we'd use |
| **Solana Support** | ✅ / ❌ / Partial |
| **Rate Limits** | Free tier limits, pay-per-request option |
| **Dashboard** | Where to register for API key |

## Example: Zerion API Research (May 2026)

| Field | Value |
|-------|-------|
| **Sponsor** | Zerion |
| **Bounty** | $5,000 |
| **Deliverable** | Agent that auto-discovers and delegates tasks via CLI |
| **API Auth** | HTTP Basic Auth (API key as username, empty password) |
| **SDK** | `@zerion/api` (TypeScript) |
| **Key Endpoints** | `/wallets/{address}/portfolio`, `/wallets/{address}/defi-positions`, `/wallets/{address}/transactions`, `/wallets/{address}/pnl` |
| **Solana Support** | ✅ Native |
| **Rate Limits** | Plan-dependent; x402/MPP for no-rate-limit per-request |
| **Dashboard** | dashboard.zerion.io |

## Example: GoldRush API Research (May 2026)

| Field | Value |
|-------|-------|
| **Sponsor** | Covalent/GoldRush |
| **Bounty** | $3,000 |
| **Deliverable** | Agent risk dashboard with on-chain data feed |
| **API Auth** | API key |
| **SDK** | `@covalenthq/client-sdk` (TypeScript) |
| **Key Endpoints** | `/v2/{chain}/address/{addr}/balances_v2/`, `/v2/{chain}/address/{addr}/transactions_v2/`, `/v2/{chain}/address/{addr}/token-transfers/` |
| **Solana Support** | ✅ 200+ chains |
| **Rate Limits** | $10/mo starter; free tier available |
| **Dashboard** | goldrush.covalenthq.com |

## Adapter Spec Template

Each adapter spec should include:

1. **What We're Building** — 1-2 sentence description
2. **API Surface** — Auth method, key endpoints, SDK, rate limits
3. **Adapter Architecture** — File structure (index.ts, feature files, config, README)
4. **CLI Commands** — Example commands the agent would expose
5. **Integration with Main Project** — How it feeds into existing Solana programs
6. **Submission Narrative** — 2-3 sentence pitch for judges

## Sprint Integration Pattern

When adding sidetracks to an existing sprint:

- **Days 1-3**: Focus on main submission only
- **Day 2**: Register for sidetrack API keys (parallel with main build)
- **Days 4-5**: Build adapters (thin wrappers, 2-3hr each)
- **Day 6**: Polish + submit all

**Key rule**: Main submission is ALWAYS priority. Adapters are bonus, not replacement.

## Common Pitfalls

1. **Don't research forever** — 30 min max per API, then start building
2. **Don't build new programs** — adapters wrap existing code, not new Solana programs
3. **Don't skip the spec** — writing the spec forces you to think through integration points
4. **Don't forget Solana** — verify Solana support before committing to a sidetrack
5. **Don't conflate tracks** — main submission and sidetracks are separate submissions with separate READMEs

---

*Last updated: 2026-05-05 by YoYo*
