# GenTech Fraud / Security Stack — Deep Dive (APA mapping)

**Date:** 2026-08-18
**Trigger:** Jordan — "we already have something for fraud (rug check + other agentic things). Let's deep dive."
**Context:** Agentic Payments Alliance (APA) just formed (Visa/Mastercard/Circle/Solana/Avalanche) with "how fraud gets caught" as a core question. We already have a fraud/security stack — this maps it.

## What we ACTUALLY have (verified live)

### 1. Rugcheck v2 API — rugcheck.gentechlabs.net (port 8088) 🟢 LIVE
- **Live version 2.1.0**, mode=simulation, uptime 835k sec (~9.6 days).
- Solana token risk scoring via x402 micropayments ($0.01 USDC, X-Payment-Proof header).
- Source (`main.py`) has a NEWER v2.0.0 agent-scan/credit-score engine (5 security domains, ERC-8004 identity, 0-850 credit score) — **but the live deploy is the older token-scoring version.** The agent-scan endpoints (`/api/v1/agent/scan`, `/api/v1/agent/credit-score`) 404 on the live box. **Gap: source ahead of deploy.**

### 2. Token Security API — security.gentechlabs.net (port 8086) 🟢 LIVE
- Proxies to Rugcheck engine (port 8088). `/v1/score/{mint}` returns real Solana token risk scores, preserves x402 402 challenges.

### 3. Treasury Defender — port 8096 🟢 LIVE (x402 service #7)
- Classifies any token **KNOWN / SUSPICIOUS** (homoglyph detection + liquidity check).
- Quarantines flagged tokens, returns **safe burn calldata**.
- **Already quarantined 3 scam tokens** from Jordan's Avalanche wallet (ÚSDС, USḌC, UЅDС — homoglyph USDC fakes).

### 4. x402 Compliance Scanner — contrib/x402-compliance-scanner/scanner.py
- Validates x402 endpoint responses against the protocol spec (402 shape, accepts[], CORS, settlement flow, schema drift).

### 5. Mastercard red/blue-team demo — 10-Labs/mastercard-challenge/ (built today)
- Pre-execution governance guard: BLOCK/FLAG/ALLOW on payment intents (identity, beneficiary, chain, injection, velocity, amount). 10/10 tests.

### 6. Agent Credit Score — agent-credit-score/ (thumbnail only)
- **Not built** — just a thumbnail.html. The engine exists in rugcheck source but isn't deployed.

### Empty / not built:
- `code-audit-api/` — only pytest cache (no code)
- `rugcheck-payment-classifier/` — only pytest cache (no code)
- `Security-Analysis/intelligent-oracle/` — only a genlayer init script
- `Audits/` — kite-ai C4 audit contracts (reference material, not a service)

## Mapping to APA's "how fraud gets caught"

| APA question | Our layer | Status |
|---|---|---|
| Token-level fraud (rugs, homoglyphs) | Rugcheck v2 + Treasury Defender | 🟢 LIVE, proven (3 quarantined) |
| Agent identity / authorization | ERC-8004 identity (rugcheck source) | ⚠️ in source, not deployed |
| Payment-flow integrity | x402 Compliance Scanner | 🟢 built |
| Pre-execution governance (stop at boundary) | Mastercard red/blue demo | 🟢 built today |
| Agent credit scoring | Agent Credit Score engine | ⚠️ in source, not deployed |

## The honest gap
Our **strongest, proven** fraud layer is **token-level** (rugs, homoglyphs, quarantine, burn). That's real and it's live. But the APA's question is broader — **agentic** fraud: how an *agent* gets authorized and how *agent-driven* fraud gets caught. That's where the Mastercard demo (pre-execution governance) and the ERC-8004 identity + credit-score engine (in rugcheck source, not deployed) are the forward-looking pieces.

## Recommendation
1. **Deploy the newer rugcheck agent-scan/credit-score engine** (source is ahead of live) — closes the identity + credit-score gap with work we already have.
2. **Position the Mastercard demo as the "agentic fraud" showcase** — it's the pre-execution governance answer to APA's question, and it's our doorway into that conversation.
3. **Treasury Defender is our proof point** — 3 real homoglyph scams caught. Lead with that.

## Next actions
- [ ] Deploy rugcheck v2.0.0 agent-scan engine (source → live)
- [ ] Wire Treasury Defender + Rugcheck into the Mastercard demo as the "real data" layer
- [ ] Track APA standards vs ERC-8004 direction
