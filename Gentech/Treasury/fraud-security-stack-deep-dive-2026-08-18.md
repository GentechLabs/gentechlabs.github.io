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

## The honest gap — CORRECTED (2026-08-18 audit)
**My earlier "source ahead of deploy" read was WRONG.** The deployed rugcheck at `/root/rugcheck/` (v2.1.0, git repo, clean) is actually **AHEAD** of the vault source — it already has:
- OWASP Agentic Top 10 full scan (55 checks) — `full_scan.py`
- ERC-8004 identity verification — `agent_identity.py`
- MCP server trust scoring — `mcp_trust.py`
- x402 endpoint audit — `x402_audit.py`
- Token risk scoring (bags_scanner) — the live `/v1/score/{mint}`

**Verified live:** all 8 endpoints respond; 178/178 tests pass (after installing pytest-asyncio — the 26 "failures" were a missing plugin, not a code bug).

**The real gap found:** our **x402-compliance-scanner** was stale (v1 spec) — it flagged the live gateway as non-compliant (25/39) because it wrongly required a `type` field in `accepts[]` and v1 top-level fields. The gateway is actually **fully x402 v2 compliant** (16/16 after fixing the scanner). Fixed the scanner to the verified v2 spec (Coinbase CDP, PayAI, x402.org).

## Recommendation
1. ✅ **x402-compliance-scanner fixed to v2 spec** — gateway verified 16/16 compliant.
2. ✅ **All components verified** — rugcheck 178/178, token-security 2/2, mastercard demo 10/10, treasury-defender live.
3. **Position the Mastercard demo as the "agentic fraud" showcase** — it's the pre-execution governance answer to APA's question.
4. **Treasury Defender is our proof point** — 3 real homoglyph scams caught. Lead with that.

## Next actions
- [x] Fix x402-compliance-scanner to v2 spec
- [x] Verify all components (rugcheck 178/178, token-security 2/2, mastercard 10/10)
- [ ] Wire Treasury Defender + Rugcheck into the Mastercard demo as the "real data" layer
- [ ] Track APA standards vs ERC-8004 direction
