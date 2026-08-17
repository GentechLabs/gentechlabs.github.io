# From Gentech — Human Pricing for gentechlabs.net (Labs handoff)

**Date:** 2026-08-15
**Status:** ✅ GREENLIT by Jordan — part of the 90-day income plan, Priority #1.
**Why:** The gateway is currently x402-only (machine-payable). Humans can't buy our 13 working APIs. This converts them from "agents-only" to "anyone can buy" — the single highest-leverage change for near-term income.

## The problem
- Gateway (`api.gentechlabs.net`) serves all 13 APIs via x402 only — HTTP 402 challenge, pay in USDC via EIP-3009. No API-key auth, no Stripe, no subscription.
- Humans don't have agent wallets. They can't pay. So $0 human revenue despite 13 working APIs.

## The build
Add a **human-friendly API-key tier** alongside the existing x402 rail (keep x402 for agents — don't remove it):

1. **API-key auth on the gateway** — accept `Authorization: Bearer <api_key>` as an alternative to x402. When a valid key is present, skip the 402 challenge and serve the data.
2. **Key management** — issue/revoke keys, track usage per key.
3. **Pricing tiers** (recommended):
   - **Free:** 50 calls/mo (no key needed, or trial key)
   - **$19/mo:** 5,000 calls
   - **$99/mo:** unlimited
4. **Stripe checkout** — a `/subscribe` page on gentechlabs.net where a human pays with a card, gets an API key. (Stripe handles the card; we issue the key on webhook.)
5. **2 "done-for-you" bundles** at $99–$299 one-off:
   - **Token Security Report** — Rugcheck + wallet analysis + treasury defender → PDF-grade report
   - **DeFi LP Health Check** — defi_lp_analytics + wallet analysis → position health report

## Files
- Gateway: `/root/vaults/gentech/10-Labs/x402-gateway/server.py` (add API-key path alongside x402)
- Landing: `/var/www/gentechlabs/index.html` (add pricing section + subscribe page)
- New: `/var/www/gentechlabs/subscribe.html`

## Constraints
- **Keep x402 intact** — agents still pay per-call. Human API-key is additive.
- **Don't break the 402 flow** — the x402-list/AgentCash/OpenDexter listings depend on it.
- **Security:** API keys stored hashed; rate-limit per key; never log keys.

## Full context
- Positioning: `00-HQ/positioning-win-orchestrators.md` (convenience = the wedge)
- Income plan: 90-day plan (Strategy 1 — human API sales, $500–$3K/mo realistic)
- Service offers: `00-HQ/service-offers-consulting.md`
