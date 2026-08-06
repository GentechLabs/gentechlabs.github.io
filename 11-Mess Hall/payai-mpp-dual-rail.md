# PayAI — Dual-Protocol (x402 + MPP) Integration Research

**Date:** 2026-08-06
**Source:** github.com/PayAINetwork (31 repos, all TypeScript)
**Lens:** Borrow / Spit-Out

---

## What PayAI Is
- **#2 x402 facilitator by volume**, native Solana settlement, no API key needed.
- We already integrate: `payai_facilitator.py` (June 25) is our Solana leg; PayAI is the facilitator behind our WURK flow.
- Open-source arm on GitHub: 31 repos, all TypeScript.

## The New Signal — `agentic-payments` (dual-protocol SDK)
`@payai/agentic-payments` v0.1.6 accepts **both x402 AND MPP** through one Express middleware:
- Unauthenticated → `402` with **both** challenge headers:
  - `PAYMENT-REQUIRED` (x402 clients)
  - `WWW-Authenticate: Payment ...` (MPP clients)
- Either one settles the same endpoint.
- Dependencies: `@x402/core ^2.7.0` + `mppx ^0.4.0`.
- **Settle-on-success buffering:** response is buffered; on status < 400 the payment settles + receipt headers attach; on failure no settlement. (Same pattern as @x402/core Express middleware.)

## MPP — Machine Payments Protocol (paymentauth.org)
- **IETF draft** `draft-httpauth-payment-00` (Jul 29, 2026, expires Jan 30, 2027). Authors: Tempo Labs (B. Ryan, J. Moxey, T. Meagher) + **Stripe** (J. Weinstein, S. Kaliski).
- Gives HTTP 402 its semantics via a `Payment` HTTP auth scheme.
- **Payment-method agnostic** — registered method IDs: EVM, Solana, Lightning, Stripe, USDC, Stellar, Hedera, Tempo, Near Intents, Card.
- Flow: 402 with `WWW-Authenticate: Payment id=.., method=.., intent=.., request=..` → client fulfills → `Authorization: Payment <credential>` → server verifies + settles → 200 + `Payment-Receipt`.
- Supports multiple payment options in one 402 (client picks one).
- Intents: charge, session, subscription. Discovery + JSON-RPC/MCP transport drafts exist.

## PayAI Facilitator Pricing
- **Free tier:** $0/mo, up to 10,000 settlements/mo, no API key.
- **Beyond:** $0.001/tx (min tx $0.001).
- **16 networks:** Solana, Base, X Layer, Avalanche, Arbitrum, Polygon, Sei, SKALE (+ testnets).

## Borrow / Spit-Out

### BORROW (the meat)
1. **Dual-challenge 402 pattern** — serve x402 AND MPP on the same endpoint. Our gateway is x402-only today. This is a genuine capability gap.
2. **Settle-on-success buffering** — settle only when the downstream handler returns < 400. Clean, correct.
3. **MPP method-agnostic model** — one challenge surface, many payment methods (EVM/Solana/Lightning/Stripe). Future-proof.

### SPIT OUT (the bones)
- **No license on any PayAI repo** — cannot fork/build on the code. Borrow the mechanism, not the code.
- **TypeScript-only SDK** — we're Python-first; their SDK doesn't drop in.
- **Eliza-centric marketplace** (`plugin-payai`) — we run Hermes, not Eliza.

## Verdict: 🔧 Watch + borrow
Worth building the **dual-rail (x402 + MPP)** capability into our gateway. MPP is early (IETF draft, expires Jan 2027) but Stripe-backed — a strong signal it becomes standard. Adding MPP support lets us serve both payment rails and positions us ahead of x402-only competitors.

## Build Queue
→ **#47** Dual-Protocol Payments — add MPP rail alongside x402 (medium, labs).

## Open Questions
- Does MPP have a facilitator model like x402, or is it self-verified on-chain? (Check `draft-evm-charge-00` / `draft-solana-charge-00`.)
- Is `mppx` (the MPP client lib) usable from Python, or do we hand-roll the `WWW-Authenticate: Payment` challenge?
- Should we add MPP now (early, Stripe-backed) or wait for the draft to stabilize?

## Sources
- github.com/PayAINetwork (org) · github.com/PayAINetwork/agentic-payments
- paymentauth.org (MPP specs) · draft-httpauth-payment-00
- docs.payai.network (facilitator intro, pricing, supported networks)
