# Agentic Treasury — V2 Revenue Model

**Date:** 2026-07-18  
**Author:** GenTech Labs  
**Status:** Strategic white paper

---

## The Thesis

We shift from selling API access to managing capital.

**V1 (shipping now):** x402 pay-per-call + API subscriptions.
**V2 (this doc):** Performance fees on routed capital + platform take rate on P2P funding + token economics.

---

## Why This Matters

Current SaaS models for AI agents cap out at user count. Capital management scales with *AUM*, not with users. A single agent routing $100k through the Treasury generates more revenue than 1,000 users paying $3/mo each.

Arc changes the math because:
- USDC as native gas means capital can move without friction
- $0.001/tx means microtransactions are actually profitable
- CCTP means cheap cross-chain settlement
- Lens AI already pays builders in USDC — revenue on day one

---

## Revenue Stack (V2)

| Layer | Model | Est. Margin | Scales With |
|-------|-------|-------------|-------------|
| **🧠 Agentic Treasury** | 10% of yield above baseline | 100% (software) | AUM |
| **🤝 P2P Causes** | 2% platform fee | 100% | Transaction volume |
| **x402 Gateway** | $0.01/call | 90% | Call volume |
| **🪙 $GENTECH token** | 95% of 0.7% swap fee | On-chain | Trading volume |
| **API subscriptions** | $3/$10/$25/mo | 90% | Active users |

**The 80/20:** Agentic Treasury (yield share) + $GENTECH (trading fees) will out-earn everything else within 6 months of launch.

---

## Agentic Treasury — Fee Structure

The Treasury routes capital across chains and strategies. We take a percentage of the *profit above a baseline* — not the principal, not the total. This aligns incentives.

**Tiers:**

| Tier | AUM | Fee | Baseline Return |
|------|-----|-----|-----------------|
| Scout | <$10k | Free | — |
| Agent | $10k–$100k | 10% of excess over 4% APY | 4% |
| Institution | $100k+ | 7% of excess over 5% APY | 5% |

**Example:** Institution tier routes $500k. Yearly return is 12% ($60k). Baseline is 5% ($25k). Fee is 7% of ($60k - $25k) = **$2,450**. User keeps $57,550.

Compare to typical 2&20 hedge fund ($10k + $7k on same returns). We're cheaper at scale.

---

## $GENTECH Token Economics

Launch on Bankr (Base). 100B supply.

| Allocation | Share | Vesting | Purpose |
|------------|-------|---------|---------|
| Liquidity pool | 85% | Immediate | Trading on Uniswap V4 |
| Creator vesting | 15% | 2 yrs (30d cliff) | GenTech Labs treasury |

**Fee flow:**
- 0.7% swap fee on every trade
- 95% of fees → GenTech Labs
- 5% → Bankr protocol

**Token utility (planned):**
- Discount on Agentic Treasury fees (hold $GENTECH → lower take rate)
- Governance on P2P cause curation
- Staking for yield boost on routed capital

---

## Projected Revenue (Conservative)

| Stream | Month 1 | Month 6 | Month 12 |
|--------|---------|---------|----------|
| x402 calls | $200 | $1,500 | $5,000 |
| API subs | $150 | $800 | $2,500 |
| Agentic Treasury | $0 | $3,000 | $25,000 |
| P2P Causes | $0 | $500 | $4,000 |
| $GENTECH fees | $0 | $2,000 | $15,000 |
| **Total** | **$350** | **$7,800** | **$51,500** |

Month 12 target: **$50k+/mo** primarily from Treasury yield share + token fees.

---

## Path Forward

1. **Immediate:** x402 gateway on Arc (first mover)
2. **This week:** $GENTECH token launch on Bankr
3. **Hackathon:** Agentic Treasury MVP for Arc Programmable Money Hackathon
4. **Circle Grant:** Apply for tiered USDC funding
5. **V2:** Launch yield share model + P2P Causes

---

*The shift: from selling tools to managing capital. Arc makes it possible. We make it profitable.*
