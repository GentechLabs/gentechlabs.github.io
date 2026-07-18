# x402 Ecosystem Scan — Biweekly Report
**Date:** 2026-05-24
**Scan Period:** May 17 – May 24, 2026

---

## 1. EXECUTIVE SUMMARY

The week of May 17–24 delivered the two biggest x402 integrations since AWS AgentCore: **Binance launched B402 on BNB Chain** (May 19) and **The Graph went live with production x402 payments** (May 12, confirmed this week). Coinbase/Base also shipped **batch settlement** enabling microtransactions of $0.0001 or less — solving the critical "too small to pay gas" problem. However, on-chain metrics tell a different story: **Signal402 recorded 10 consecutive weeks of zero transactions**, and daily volume remains stuck at ~$28K–$68K (down 92% from Q4 2025). The gap between institutional infrastructure buildout and actual commercial traffic continues to widen.

---

## 2. NEW IMPLEMENTATIONS, INTEGRATIONS & PARTNERSHIPS

### Major Integrations This Week

- **Binance x402 (B402)** — May 19, 2026
  - HTTP-native programmable payment service on BNB Smart Chain
  - Off-chain authorization with on-chain settlement
  - Trust Wallet AgentKit supports x402 natively
  - **4th major chain** adding x402 (after Base, Solana, Polygon)
  - Source: binance.com/blog, blockonomi.com

- **The Graph x402 Gateway** — May 12, 2026 (confirmed this week)
  - Per-query USDC payments on Base — no API key required
  - HTTP 402 → payment → authentication → data returned
  - First major Web3 data provider accepting x402 in production
  - The Graph serves billions of queries monthly
  - Source: tomcn.uk analysis

- **Coinbase/Base Batch Settlement** — May 11–13, 2026
  - Enables microtransactions of $0.0001 or less
  - Cryptographic vouchers with bulk on-chain redemption
  - Critical for economic viability of high-frequency AI agent interactions
  - Source: Jesse Pollak announcement

- **Cloudflare** — 1 billion HTTP 402 responses per day across their network
  - x402 positioned as solution for AI agent web economics
  - Source: CoinDesk May 5, 2026

### Recent Integrations (May 2026)

| Integration | Date | Details |
|------------|------|---------|
| AWS AgentCore Payments | May 7 | Coinbase x402 discovery + wallet infrastructure |
| Circle Agent Stack | May 12 | Agent Wallets, Marketplace, CLI, Nanopayments |
| Berachain $HONEY | May 12 | x402 accepting HONEY stablecoin |
| BSV x402 Marketplace | May 13 | Permissionless on Cloudflare edge |
| AllUnity (SEKAU) | Recent | Swedish krona stablecoin + x402 settlement |
| Fireblocks | Recent | Joined Foundation, launched Agentic Payments Suite |

---

## 3. ON-CHAIN METRICS & ECOSYSTEM HEALTH

| Metric | Value | Source |
|--------|-------|--------|
| Signal402 weekly volume | $0.00 | Signal402 Week 20 |
| Signal402 zero-txn streak | **10 consecutive weeks** | Signal402 |
| Daily avg volume (2026 YTD) | ~$28K–$68K | Artemis, crypto.com |
| Q4 2025 daily avg | ~$448K | crypto.com |
| Volume decline from peak | ~92% | Multiple sources |
| Cumulative transactions | 165M+ | Presenc AI |
| Cumulative volume | $50M+ | 0xProcessing |
| Active agents | ~69,000 | 0xProcessing |
| Correct endpoint implementation | 0.41% (107 of 26,302) | Ecosystem scan |
| Solana share of agentic payments | ~65% | Solana Foundation |
| Base settlement share | ~85% | Multiple sources |
| "Gamified" volume | ~50% | Presenc AI |

**Assessment:** The infrastructure gap is now extreme. Major enterprises (AWS, Binance, Cloudflare, Stripe, Google) all support x402, but on-chain tracked services show zero activity for 10 weeks. Only 0.41% of advertised endpoints correctly implement the protocol. The market is either waiting for a catalyst, or activity has migrated to untracked facilitators.

---

## 4. COMPETITOR PROTOCOLS & PROGRESS

No new protocol launches this week. The landscape remains fragmented:

| Protocol | Backer(s) | Status | This Week |
|----------|-----------|--------|-----------|
| **x402** | Coinbase, Cloudflare, LF, Binance | Open standard | B402 launch, batch settlement |
| **MPP** | Stripe + Tempo | Production | No change |
| **AP2** | Google Cloud | Production | No change |
| **ACP** | Stripe + OpenAI | Production | No change |
| **TAP** | Visa | Pilot | No change |
| **L402** | Lightning Labs | Niche | No change |
| **Circle Nanopayments** | Circle | Mainnet (May 3) | Settlement across 11 chains |

**Key dynamic:** The architecture is consolidating into layers: TAP/AP2 for identity, ACP/UCP for orchestration, x402/MPP for settlement. This suggests x402's role is as the settlement primitive, not the full stack.

---

## 5. DEVELOPER TOOLING & SDKs

### New This Week

- **bonanza-x402** (PyPI, May 18) — Spending firewall for x402: policy-based controls, budget checks, risk scoring, vendor allowlists, approval queues
- **@x402/fastify** v2.13.0 — Updated Fastify middleware
- **@x402/express** v2.5.0 — Updated Express middleware

### Existing SDKs

- **Coinbase CDP x402 SDK** — TypeScript/Python
- **Cloudflare Agents SDK** — Native x402 support
- **thirdweb SDK** — x402 V2 support
- **ampersend A2A x402** — Python package for Google A2A integration
- **bonanza-mcp** — MCP server for x402 payment + spending controls

### Repository Activity

- Canonical repo migrated to **x402-foundation/x402** (from coinbase/x402)
- PR #2279: ADI Chain (chain ID 36900) support — new chain integration
- PR #2357: FeedOracle hybrid-PQC receipt interop fixture
- OpenGradient and Altude Platform both forked x402 SDKs (May 12–14)

---

## 6. GRANT & FUNDING OPPORTUNITIES

**No new x402 Foundation grant program announced.** Foundation still in early governance phase.

### Active Programs (unchanged from May 17)

- Kite AI Global Hackathon (Coinbase Ventures)
- Cronos x402 PayTech ($42K prizes)
- CDP Builder Grants (~$30K)
- Base Grants
- Colosseum (Solana)

### New Ecosystem Opportunities

- **Agentic.Market** (Coinbase) — Public marketplace for x402 services (launched Apr 19). 480K agents registered.
- **Sports Prediction Oracle** — x402.org/ecosystem submission (PR #2303, review window expired May 22)

---

## 7. STRATEGIC TAKEAWAYS

1. **Binance entry is the biggest signal this month.** x402 is no longer a Coinbase/US ecosystem play — it's genuinely cross-chain and cross-exchange. BNB Chain + Binance Pay gives it reach into the Asian market.

2. **Batch settlement changes the economics.** $0.0001 microtransactions make high-frequency AI agent interactions viable. This was the missing piece for "agents paying per API call" at scale.

3. **The Graph is a bellwether.** If billions of queries shift to x402 payment, transaction volume could recover dramatically. Watch this space.

4. **The 10-week zero streak is alarming.** Signal402 tracks specific services, not the whole ecosystem. But 10 weeks of zero is hard to explain away. Either tracked services are dead, or the metric is misaligned with actual usage.

5. **0.41% correct implementation is a quality problem.** Most x402 "endpoints" aren't actually working correctly. This suggests hasty integrations or misconfiguration — a support/education opportunity.

6. **Our positioning is strong.** AgentCash (x402 payment discovery layer) + AdaptiveFolio (AI-driven portfolio on Arc) puts us at the intersection of agent payments + AI finance. As the ecosystem matures, early builders with working products get outsized attention.

---

## 8. RECOMMENDED ACTIONS

- **Monitor The Graph x402 gateway** for transaction volume recovery signals
- **Track Binance B402** for ecosystem growth on BNB Chain
- **Evaluate bonanza-x402** for spending controls in our agent payment stack
- **Watch Signal402 Week 21** — if the streak breaks, it's a major signal
- **Position AgentCash** for potential x402 Foundation grant programs (post-LF transition)
- **Submit to Agentic.Market** — Coinbase's agent marketplace could drive discovery

---

*Gentech x402 Ecosystem Scan — 2026-05-24*
