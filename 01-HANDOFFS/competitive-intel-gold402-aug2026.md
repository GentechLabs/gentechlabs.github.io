# Competitive Intel — gold-402 New Arrivals (Aug 20, 2026)

## Source
gold-402 discussion #42 (Haustorium12/gold-402) — "New arrivals: five x402 services joined the directory this week"

## Our status
- **We ARE listed** in gold-402 `directory/apis.md` via PR #39 (merged Jul 19).
- Entry: "GenTech x402 Gateway — 15 pay-per-call endpoints for crypto intelligence, wallet analysis, token risk scoring, NFT search, game/movie deals, agent scanning. $0.001-$0.10 USDC/call across 5 chains (Base, Solana, Avalanche, BNB, OKX)." with OpenAPI + Discovery links.
- Announcement in discussion #42 confirms we're recognized as a multi-chain (5-chain) integration.

## The 5 new arrivals (peer / potential competitors)

| Service | Stack | Notes |
|---|---|---|
| **fry.farm** | Algorand, non-custodial | DeFi/DePIN data + unsigned atomic tx builders. MCP server alongside. |
| **Grey Ridge Signals** | Base, **Cloudflare Worker** | 17 endpoints, blockchain + security checks. Ships llms.txt, NO skill.md. |
| **GenTech x402 Gateway** (us) | Multi-chain | Base, Solana, Avalanche, BNB, OKX. USDC settlement. |
| **Bincrease** | Base (no-spend) | USDC work shortlisting w/ risk + payout-evidence filters. |
| **Venture NL Open-Data** | Base | Dutch gov open-data (vehicle registry, addresses, geocoding, transit). Ships openapi.json, NO skill.md/llms.txt. |

## KEY LEARNING — Grey Ridge's free-preview pattern (worth adopting)
Grey Ridge ships a **free `/preview` endpoint on nearly every paid route** so agents can verify data quality BEFORE paying. e.g.:
- `/chain/gas-price/preview` — free, identical to paid
- `/crypto/prices/preview` — free 1-token sample
- `/scan/mcp/preview` — free counts+risk score (withholds detail)
- `/chain/token-security/preview` — free full analysis of a fixed well-known token

This is a **demand-generation lever**: lets agents "taste the data" → confidence → pay for the full result. We DON'T have free previews for our paid services.

**Recommendation:** consider adding `/preview` endpoints for our top services (e.g. `market_intelligence`, `token_security`, `wallet_analysis`). Low effort, high conversion. This is the natural next step after we've confirmed real buyer interest.

## Other observation
- Grey Ridge ships **llms.txt with full per-endpoint pricing + previews** — matches the docs-first discoverable pattern we already adopted (we have llms.txt + llms-full.txt + skill.md).
- Venture NL ships openapi.json only — no skill.md/llms.txt. We're AHEAD on discovery surface vs some peers.

## File
Logged to vault: `01-HANDOFFS/competitive-intel-gold402-aug2026.md`
