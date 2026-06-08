# Birdeye Data Services — x402 Pay-Per-Request API

**Saved:** April 21, 2026
**Source:** Birdeye announcement
**Category:** Crypto Data Infrastructure / x402 Ecosystem

## Pricing

| Detail | Spec |
|--------|------|
| **Price per request** | **$0.003** |
| **Access level** | Full REST API — all endpoints, no subscription needed |
| **Payment method** | USDC via x402 |
| **Settlement** | ~2s on-chain via **Coinbase CDP (Base)** or **PayAI (Solana)** |
| **Networks** | Base + Solana |
| **Limitation** | No WebSocket streaming (REST only) |

## x402 Flow
1. Client sends API request
2. 402 Payment Required response returned
3. Client sends USDC payment via x402 protocol
4. Settlement on Base (~2s via Coinbase CDP) or Solana (~2s via PayAI)
5. Request fulfilled

## Strategic Relevance for AAE
- **Data supply**: Pay-per-request removes subscription friction — AAE could integrate Birdeye for real-time token data without monthly commitments
- **x402 validation**: More infrastructure adopting x402 = stronger ecosystem pull for the payment model we're building around
- **Base + Solana dual settlement**: Aligns with AAE's multi-chain positioning
- **Cost efficiency at scale**: $0.003/request — need to model break-even vs subscription pricing at different query volumes

## Volume Cost Modeling
| Daily Requests | Daily Cost | Monthly Cost |
|---------------|------------|--------------|
| 100 | $0.30 | $9 |
| 1,000 | $3.00 | $90 |
| 10,000 | $30.00 | $900 |
| 100,000 | $300.00 | $9,000 |

**Note**: At ~3,333 requests/day, monthly cost = ~$300. Compare against Birdeye subscription tiers to find crossover point.

## Follow-ups
- [ ] Research Birdeye subscription pricing for comparison
- [ ] Evaluate which Birdeye endpoints AAE needs most
- [ ] Model token analytics feature cost for AAE platform
- [ ] Check if x402 MCP integration exists for Birdeye
