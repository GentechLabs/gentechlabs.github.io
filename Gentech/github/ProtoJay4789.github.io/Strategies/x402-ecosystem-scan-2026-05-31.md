# x402 Ecosystem Scan — Weekly Report
**Date:** 2026-05-31
**Scan Period:** May 24 – May 31, 2026
**Previous Scan:** 2026-05-24

---

## 1. EXECUTIVE SUMMARY

The week of May 24–31 brought two significant developments: **x402 went live on Arbitrum** (expanding to the 5th major chain) and **Fiserv joined as a charter member** of the x402 Foundation, bringing traditional payment infrastructure credibility. The Foundation itself is now formally established under the Linux Foundation. On-chain, **t54.ai captured 25% of Solana x402 market share** with its x402-secure and x402monopoly protocols, while **x402station.io now tracks 86,599 active endpoints** (up from 26,302 in the May 24 scan — a 3.3x increase). However, Signal402's zero-transaction streak continues, and daily volume remains depressed. The infrastructure buildout is accelerating while commercial traction lags.

---

## 2. NEW IMPLEMENTATIONS, INTEGRATIONS & PARTNERSHIPS

### Major Integrations This Week

- **x402 on Arbitrum** — Late May 2026
  - x402 protocol now live on Arbitrum One (Ethereum L2)
  - 5th major chain (after Base, Solana, Polygon, BNB Chain)
  - Low gas costs + fast finality make it ideal for micropayments
  - Source: cryptowisser.com, GitHub vwakesahu/x402-arbitrum

- **Fiserv Charter Member** — May 1, 2026 (confirmed this week)
  - Fiserv (NASDAQ: FISV) — global payments and financial services technology provider
  - Joined x402 Foundation as charter member
  - Brings traditional payment rail credibility to the protocol
  - Source: investors.fiserv.com

- **x402 Foundation Formalized** — Under Linux Foundation
  - Neutral, industry-led home for x402 standard
  - Mission: foster development and adoption of M2M payment protocol
  - Charter members include: Coinbase, Cloudflare, Fiserv, and others
  - Source: linuxfoundation.org/x402foundation

### Ecosystem Growth

- **x402station.io endpoint count:** 86,599 active endpoints (as of May 13 snapshot)
  - Up from 26,302 in previous scan — **3.3x growth**
  - Probes endpoints on ~10-minute cadence
  - Independent risk signal layer for x402 commerce

- **t54.ai Solana Breakout**
  - x402-secure and x402monopoly protocols captured **25% of Solana x402 market share**
  - Rapid adoption after Solana support rollout
  - Source: meme-insider.com

- **Solana Foundation Vision**
  - Vibhu Norby (Solana Foundation product lead) predicted **99.99% of Solana onchain transactions** could be AI agent-driven within 2 years
  - x402 positioned as the payment primitive for this transition
  - Source: oracore.dev

### Existing Integrations (unchanged from May 24)

| Integration | Date | Details |
|------------|------|---------|
| AWS AgentCore Payments | May 7 | Coinbase x402 discovery + wallet infrastructure |
| Binance B402 | May 19 | HTTP-native payments on BNB Chain |
| Circle Agent Stack | May 12 | Agent Wallets, Marketplace, CLI, Nanopayments |
| The Graph x402 Gateway | May 12 | Per-query USDC payments on Base |
| Coinbase/Base Batch Settlement | May 11–13 | Microtransactions of $0.0001 or less |
| Cloudflare | Ongoing | 1 billion HTTP 402 responses/day |
| Berachain $HONEY | May 12 | x402 accepting HONEY stablecoin |
| BSV x402 Marketplace | May 13 | Permissionless on Cloudflare edge |

---

## 3. ON-CHAIN METRICS & ECOSYSTEM HEALTH

| Metric | Value | Change vs May 24 | Source |
|--------|-------|-------------------|--------|
| Signal402 weekly volume | $0.00 | Unchanged | Signal402 |
| Signal402 zero-txn streak | **11+ consecutive weeks** | +1 week | Signal402 |
| x402station.io endpoints | 86,599 | +3.3x (from 26,302) | x402station.io |
| Daily avg volume (2026 YTD) | ~$28K–$68K | Unchanged | Multiple |
| Q4 2025 daily avg | ~$448K | — | crypto.com |
| Volume decline from peak | ~92% | Unchanged | Multiple |
| Cumulative transactions | 165M+ | Unchanged | Presenc AI |
| Solana x402 market share (t54.ai) | 25% | New entrant | meme-insider.com |
| Active agents | ~69,000 | Unchanged | 0xProcessing |

**Assessment:** Endpoint count tripled (26K → 86K), suggesting rapid integration activity. But Signal402's zero-streak hit 11+ weeks, and daily volume remains flat. The gap between infrastructure buildout and commercial traffic is widening. The Solana market share capture by t54.ai is notable — it suggests real agent-to-agent payment activity may be happening on Solana but not tracked by Signal402's methodology.

---

## 4. COMPETITOR PROTOCOLS & PROGRESS

No new protocol launches this week. Landscape remains consolidated:

| Protocol | Backer(s) | Status | This Week |
|----------|-----------|--------|-----------|
| **x402** | Coinbase, Cloudflare, LF, Binance, Fiserv | Open standard | Arbitrum live, Foundation formalized |
| **MPP** | Stripe + Tempo | Production | No change |
| **AP2** | Google Cloud | Production | No change |
| **ACP** | Stripe + OpenAI | Production | No change |
| **TAP** | Visa | Pilot | No change |
| **L402** | Lightning Labs | Niche | No change |
| **Circle Nanopayments** | Circle | Mainnet | Settlement across 11 chains |

**Key dynamic:** The architecture continues consolidating into layers: TAP/AP2 for identity, ACP/UCP for orchestration, x402/MPP for settlement. x402's role as the settlement primitive is solidifying.

---

## 5. DEVELOPER TOOLING & SDKs

### New This Week
- **x402-arbitrum** (GitHub) — Easy-to-use Arbitrum integration library
- **@x402/hono** — Hono framework middleware (referenced in Stripe docs)

### Existing SDKs (unchanged)
- Coinbase CDP x402 SDK — TypeScript/Python
- Cloudflare Agents SDK — Native x402 support
- thirdweb SDK — x402 V2 support
- ampersend A2A x402 — Python package for Google A2A integration
- bonanza-x402 — Spending firewall (PyPI, May 18)
- bonanza-mcp — MCP server for x402 payment + spending controls
- @x402/fastify v2.13.0, @x402/express v2.5.0

### Repository Activity
- Canonical repo: **x402-foundation/x402**
- Foundation governance structure now formalized under Linux Foundation
- Community contributions increasing ( Arbitrum integration was community-built)

---

## 6. GRANT & FUNDING OPPORTUNITIES

### Active Programs
- Kite AI Global Hackathon (Coinbase Ventures)
- Cronos x402 PayTech ($42K prizes)
- CDP Builder Grants (~$30K)
- Base Grants
- Colosseum (Solana)
- Agentic.Market (Coinbase) — 480K+ agents registered

### New Developments
- **x402 Foundation** may announce grant programs post-formalization
- **Fiserv involvement** suggests potential enterprise integration grants
- No specific new grant programs announced this week

---

## 7. STRATEGIC TAKEAWAYS

1. **Arbitrum integration completes the L2 trifecta.** Base, Arbitrum, and Polygon now all support x402. Combined with Solana and BNB Chain, x402 covers 5 major chains. Multi-chain is no longer theoretical.

2. **Fiserv is the biggest signal this month.** A traditional payment processor joining the Foundation validates x402 beyond crypto-native use cases. This could unlock enterprise merchant adoption.

3. **86,599 endpoints is a 3.3x jump.** Either the ecosystem is growing rapidly, or the measurement methodology changed. Either way, more endpoints = more attack surface for commercial traffic.

4. **The Solana t54.ai capture is interesting.** 25% market share on Solana suggests real agent payment activity is happening. If this is genuine (not gamified), it's the first evidence of organic x402 transaction growth.

5. **Signal402's 11-week zero streak is now critical.** Either the metric is fundamentally misaligned with actual usage, or the tracked services are dead. This needs investigation — the endpoint count growth (86K) vs zero transactions is contradictory.

6. **Our positioning remains strong.** AgentCash (x402 payment discovery) + AdaptiveFolio (AI portfolio on Arc) at the intersection of agent payments + AI finance. As the ecosystem matures, early builders with working products get outsized attention.

---

## 8. RECOMMENDED ACTIONS

- **Investigate t54.ai Solana activity** — is the 25% market share genuine agent payments or gamified volume?
- **Monitor x402 Foundation grant announcements** — formalization under Linux Foundation suggests programs coming
- **Evaluate Arbitrum deployment** for AgentCash — 5th chain, low gas, fast finality
- **Track Fiserv integration** — enterprise payment rail could unlock merchant x402 adoption
- **Submit to Agentic.Market** — 480K+ agents, Coinbase-backed discovery layer
- **Watch Signal402 Week 22** — if the streak breaks with endpoint growth, it's a major recovery signal
- **Position AgentCash** for potential x402 Foundation grant programs (post-LF transition)

---

*Gentech x402 Ecosystem Scan — 2026-05-31*
