# Laso Finance — Integration Candidate (x402 Spend Rail)

**Status:** 🔵 CANDIDATE — documented + MCP wired. Not funded / not building yet.
**Date logged:** 2026-08-11
**Source:** Laso Finance article (X, Jun 22 2026) + agents.laso.finance + laso.finance/SKILL.md

## What it is
Crypto prepaid card platform (Solana-native, also Base). Privacy at the point of spend.
Backed by Colosseum, Theia Research, DBA, Anagram, MetaDAO. FinCEN-registered MSB.
Live business: $720K payments / $34.5K revenue / 3,155 MAS in 30 days (Jun 2026).

## Why it matters to GenTech
- **x402-native spend layer** — same protocol stack we build on. No API keys, no subs;
  agents pay per call in USDC on **Base or Solana**.
- **Agentic commerce is live** — 2-4% of volume already AI agents (cards, purchases,
  bank transfers, no human in loop). Default card provider for PayWithLocus + Ampersend,
  default prepaid for PaySponge.
- **Complement, not competitor** — Laso = spend layer (cards/gift/bank). We = payment
  rail (per-tx x402 fees). Agent earns via our rail → spends via Laso cards.
- **Agent bank accounts** — US bank account that converts dollars↔USDC, agent reads its
  own routing/account numbers, sends bank payments over x402. Only human step = KYC.

## Open integration surface (all pluggable)
- `laso.finance/SKILL.md` — agent self-onboarding instructions
- `laso.finance/openapi.json` — OpenAPI 3.1 spec
- `laso.finance/.well-known/ai-plugin.json` — AI plugin manifest
- `laso.finance/llms.txt` — LLM-optimized context
- `laso.finance/.well-known/mcp/server-card.json` — MCP server card
- **MCP server:** `https://agents.laso.finance/mcp` (streamable-http) — docs search only
- **x402 HTTP API** (the actual spend surface): `/get-card`, `/order-intl-card`,
  `/order-gift-card`, `/get-push-to-card`, bank accounts

## Key endpoints (x402, pay-per-call)
- `GET /get-card?amount=N` — USA prepaid card (instant, ~7-10s, poll `/get-card-data`)
- `GET /order-intl-card` — international card (24h admin fulfillment, 3.8% fee)
- `GET /order-gift-card?amount=N&laso_server_id=...` — gift cards
- `GET /get-push-to-card?amount=N&currency=USD|EUR|GBP` — debit card transfer (4.8% fee)
- Networks: Base (eip155:8453) + Solana. Currency: USDC.
- Base recipient: `0x3291e96b3bff7ed56e3ca8364273c5b4654b2b37`
- Solana recipient: `3MZVk97x9SeRxbYpc3jhzRfU2fyA3emYutnqfn9kNfYX`

## Wallet options
- Laso-managed (`lasoak_` key, via agent/dashboard) — simplest
- Bring-your-own: Locus (`claw_`), Sponge, Ampersend (all x402) — our lane

## MCP wiring (done 2026-08-11)
- Added `laso` server to gentech-treasury config.yaml:
  `url: https://agents.laso.finance/mcp`, enabled, sampling off.
- `hermes mcp test laso` → ✓ Connected, 3 tools:
  `search_laso_finance_api`, `query_docs_filesystem_laso_finance_api`, `submit_feedback`
- NOTE: MCP = docs search only. Real spend = x402 HTTP API (call endpoints directly).

## Next steps (when dry powder available)
1. Fund a Laso-managed wallet (or Ampersend wallet) with USDC on Base/Solana.
2. Test live `/get-card` (small amount) to prove the spend rail end-to-end.
3. Wire into Agentic Treasury demo: agent earns via x402 rail → spends via Laso card.

## Watch items
- Agent bank accounts + reloadable credit cards (roadmap Q3-Q4 2026) — agent-native
  financial tooling we want our agents to plug into.
- LASO token on MetaDAO (futarchy raise, closed Jun 30-Jul 3) — governance model to study
  (blind cap, $50k/mo team allowance, performance-gated team unlocks).
