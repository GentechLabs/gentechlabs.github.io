# x402 Ecosystem Scan — Weekly Report
**Date:** 2026-06-14
**Scan Period:** May 24 – June 14, 2026
**Previous Scan:** May 24, 2026

---

## 1. EXECUTIVE SUMMARY

Three weeks since the last scan, the x402 ecosystem has delivered two notable chain integrations (Injective, confirmed Cardano) and a major platform play (Coinbase MCP agent for autonomous trading). The x402 Foundation (Linux Foundation) is now operational with 22+ founding members including AWS, Google, Visa, Mastercard, and AmEx. However, the volume paradox deepens: institutional adoption accelerates while Signal402 reports **14 consecutive weeks of zero transactions** (up from 10 weeks at last scan). Independent forensic analysis reveals that 89% of dollar volume comes from OTC-sized settlements that don't need x402, while actual sub-dollar micropayments total only ~$4,000/day. The protocol's long-term viability depends on enterprise integrations translating into real micropayment adoption.

---

## 2. NEW IMPLEMENTATIONS & INTEGRATIONS

### Chain Integrations (New Since May 24)

| Chain | Date | Details |
|-------|------|---------|
| **Injective** | Jun 8-9 | x402 for real-time AI agent payments. No account creation needed. |
| **Cardano** | Apr 23 (confirmed) | x402 Foundation merged Cardano Specification PR. Masumi Smart Contract accepted. |

**Updated chain count:** ~16+ chains (Base, Solana, Polygon, BNB Chain, Arbitrum, World, Ethereum, Cardano, Etherlink, Injective, Algorand, and others).

### Major Platform Integrations

- **Coinbase MCP Agent** (Jun 11) — Autonomous trading + premium research access via x402. Integrates with ChatGPT/Claude via MCP server. [TechCrunch]
- **AWS Bedrock AgentCore Payments** (May 7) — Coinbase + Stripe built. Agents autonomously discover, authorize, execute micropayments. Managed wallet with spending limits. ~200ms settlement on Base.
- **Travala** — USDC hotel reservations via x402 on Base. ~$0.01/booking, gasless.
- **CoinGecko API** — x402 support for crypto price/market data.
- **Google Cloud** — Pay.sh on Solana. x402 is default stablecoin rail in AP2.

---

## 3. ON-CHAIN METRICS & ECOSYSTEM HEALTH

### Signal402 Status
- **14 consecutive weeks of $0 volume** (W10–W23, Mar 8 – Jun 7)
- Last active week: W09 (Mar 1) — $400.3K volume / 110,287 transactions
- Signal402 monitoring may have stopped tracking, or ecosystem flatlined

### Alternative Volume Estimates

| Metric | Value | Source |
|--------|-------|--------|
| Peak monthly volume | $5.15M → $1.19M | Binance News |
| Volume decline | 77% | Binance Square (May 27) |
| Transaction count rebound | 2.89M in 30-day window | NS3.AI |
| Avg transaction size | $0.52 | NS3.AI |
| "Real" daily volume | ~$50,000/day | Artemis (May 19) |
| Base dominance | 93% of real volume | Artemis |
| Cumulative settled | $36.9M verified | Signal402 homepage |
| Cumulative transactions | 120.9M | Signal402 homepage |

### KuCoin Forensic Analysis (Apr 15 – May 15, EIP-3009 on Base)
- **2,996,656 transactions, $64.78M total**
- **89% of dollar volume** from $1,000+ OTC settlements between unlabeled wallets
- **Sub-$1 micropayments: $125,000 over 31 days = $4,032/day**
- 59% of transactions at exactly $0.001, combined daily value under $50
- Only 0.96% of micropayments pass authenticity test
- **Conclusion:** "x402's volume comes from transactions that do not need it. The transactions that need x402 have almost no volume."

### Assessment
The gap between institutional signaling and organic usage continues to widen. The 77% volume decline from peak, combined with 14 weeks of Signal402 zeros, suggests the ecosystem is in a "build now, use later" phase. The 2.89M transaction count rebound is encouraging but may reflect testing/gaming rather than commercial activity.

---

## 4. COMPETITOR PROTOCOLS

| Protocol | Creator | Status | This Period |
|----------|---------|--------|-------------|
| **x402** | Coinbase (LF) | Live, 16+ chains | Injective, Coinbase MCP agent |
| **MPP** | Stripe + Tempo | Production | No major change |
| **AP2** | Google Cloud | Production | Pay.sh launched on Solana |
| **ACP** | Stripe + OpenAI | Production | No change |
| **TAP** | Visa | Pilot | Visa on x402 Foundation board |
| **L402** | Lightning Labs | Niche | No change |

**Key dynamic:** Stripe explicitly supports both MPP and x402. Cloudflare co-founded x402 Foundation AND ships MPP proxy (protocol-agnostic). The architecture is consolidating into layers: TAP/AP2 for identity, ACP/UCP for orchestration, x402/MPP for settlement.

---

## 5. DEVELOPER TOOLING

### New SDKs & Tools

| Tool | Details |
|------|---------|
| **Python SDK** | Published on PyPI (x402 package). Updated Apr 12. |
| **FastAPI SDK** | PayRelayer's `x402-fastapi` — one decorator turns any endpoint pay-per-call |
| **Algorand SDK** | `@algo-wallet/x402-client` — full x402 handshake in ms on Algorand |
| **g402 (Managed Gateway)** | Niceberg's managed gateway with Buyer/Seller SDKs, JWT proofs |
| **Signal402 MCP** | Agent discovers x402 services via `npx signal402-mcp` |
| **Cloudflare MPP Proxy** | Open-source MPP proxy for Workers (protocol-agnostic) |
| **AWS Sample** | Full reference: Bedrock AgentCore + CloudFront + Lambda@Edge |

### Facilitator Model
- Hosted CDP facilitator supports Base, Polygon, Arbitrum, World, Solana
- Free tier: 1,000 txns/month, then ~$0.001/txn

---

## 6. FOUNDATION GOVERNANCE

### x402 Foundation (Linux Foundation, April 2, 2026)
- **22+ founding members** spanning payments, cloud, e-commerce, Web3, AI
- **Governing board:** Cloudflare and Stripe
- **Founding contributor:** Coinbase (transferred protocol IP)
- **Members:** AWS, Google, Microsoft, Visa, Mastercard, AmEx, Shopify, Circle, Polygon, Solana, Ampersend, Sierra, and more
- **No grant program announced** as of Jun 14

---

## 7. STRATEGIC TAKEAWAYS

1. **Coinbase MCP agent is the biggest signal this period.** Direct integration with ChatGPT/Claude means x402 payments can happen inside LLM conversations. This is the "agent pays per API call" use case finally shipping from the protocol creator.

2. **Signal402 zero-streak at 14 weeks is now critical.** Either the monitoring service is broken, or the ecosystem it tracks is dead. We need to verify which. If monitoring is broken, alternative metrics (NS3.AI's 2.89M transactions) suggest some activity exists.

3. **The OTC volume problem is real.** KuCoin's forensic analysis showing 89% OTC volume means x402's reported metrics are misleading. Actual micropayment activity (~$4K/day) is orders of magnitude smaller than headline numbers suggest.

4. **16+ chains is ecosystem breadth, not depth.** More chains doesn't equal more usage. The question is whether any chain achieves meaningful transaction density.

5. **Our positioning is strong but timing matters.** AgentCash (x402 discovery layer) + AAE financial stack puts us at the intersection. But if real micropayment adoption takes 2-3 more years, we need sustainable revenue in the interim.

6. **Watch Injective integration.** Injective's focus on DeFi + AI agents could drive organic micropayment volume if their agent ecosystem takes off.

---

## 8. RECOMMENDED ACTIONS

- **Verify Signal402 monitoring status** — Is the $0 streak real or a monitoring artifact?
- **Monitor Coinbase MCP agent adoption** — First real-world test of x402 in LLM conversations
- **Track Injective integration** for organic micropayment signals
- **Evaluate bonanza-x402** for spending controls in our agent payment stack
- **Submit to Agentic.Market** — Coinbase's agent marketplace could drive discovery
- **Watch Google Pay.sh** on Solana — AP2 + x402 convergence could be significant
- **Position AgentCash** for potential x402 Foundation grant programs (post-LF transition)

---

*Gentech x402 Ecosystem Scan — 2026-06-14*
