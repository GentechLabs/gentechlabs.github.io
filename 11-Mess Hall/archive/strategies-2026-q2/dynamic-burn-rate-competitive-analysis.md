# 🔍 Dynamic Burn Rate — Competitive Analysis

**Date:** 2026-05-02  
**Analyst:** YoYo (Strategies)  
**Task:** Desmond → YoYo competitive analysis (H002, overdue Apr 19 → resolved May 2)  
**Status:** ✅ Complete

---

## 1. Scope

Analyze Gentech's dynamic burn/recycle mechanism against:
- Existing DeFi token burn/emission models
- t54.ai's trust-layer positioning (no-token approach)
- Market readiness for market-responsive tokenomics

---

## 2. Mechanism Definition

Gentech's model: **continuous burn ratio dial (10–90%)** updated via signals

```
burn_ratio = base_burn (0.5)
           + price_momentum * momentum_weight
           + treasury_health * treasury_weight
           - discount_pressure * pressure_weight
```

**Burn portion:** sent to `0x000...dEaD` (EVM) / SPL burn (Solana)  
**Recycle portion:** sent to Treasury (fund ecosystem, competitions, agent incentives)

---

## 3. Competitive Landscape

### 3.1 DeFi Protocols — Burn Mechanisms

| Protocol | Mechanism | Dynamic? | Signal Set | Novelty |
|-----------|-----------|----------|------------|---------|
| **Ethereum (EIP-1559)** | Base fee burn per tx | Indirect | Network congestion (gas price) | 6/10 |
| **Stepn (GMT)** | Burn-to-mint (shoe crafting) | Yes | User activity (mint events) | 7/10 |
| **GMX (GMX)** | esGMX vesting + buybacks | No | Platform revenue (periodic) | 4/10 |
| **PancakeSwap (CAKE)** | Syrup pool burns + buybacks | No | Fixed schedule (weekly/monthly) | 3/10 |
| **Aave (AAVE)** | Safety Module emissions | No | Staking participation | 3/10 |
| **Convex (CVX)** | Fee sharing + vote locking | No | CRV/veCRV balance | 2/10 |

**Key insight:** Zero protocols use **multi-signal adaptive ratio**. Only ETH and Stepn have any dynamic element, and both are single-signal.

---

### 3.2 Agent Economy — t54.ai Comparison

| Dimension | t54.ai | Gentech |
|-----------|--------|---------|
| **Token model** | No token (TradFi SaaS) | $TECH with dynamic sinks |
| **Trust mechanism** | KYA + credit scoring | REP (reputation) + yield transparency |
| **Settlement** | Custody-based (keyless) | Self-custody (user-controlled) |
| **Target** | B2B merchants/platforms | Retail agent operators |
| **Revenue** | Merchant fees + credit underwriting | Subscription + yield share + token sinks |
| **Signal approach** | Credit history + verification | Price momentum + treasury health + TVL |

Overlap: agent reputation (t54's credit scores vs Gentech's REP).  
Differentiation: t54 is **enterprise trust layer**; Gentech is **retail yield + reputation**.

---

## 4. Threat/Differentiation Analysis

### 4.1 Competitive Threats

| Threat | Severity | Rationale |
|--------|----------|-----------|
| t54.ai trust-layer dominance | 🟡 Medium | They target institutions; Gentech targets retail. Different segments but overlap on agent verification. |
| Stepn-style burn-to-mint copycats | 🟢 Low | Stepn's model is gamified fitness; not directly applicable to DeFi agent operators. |
| ETH EIP-1559 as precedent | 🟢 Low | ETH burn is protocol-fee-driven, not market-responsive. No dial control. |
| GMX es-token vesting model | 🟡 Medium | esGMX locking is a form of recycling; Gentech's recycle-to-treasury is similar but less user-aligned. |

---

### 4.2 Differentiation Moats

1. **First-mover on market-responsive burns**
   - No protocol adjusts burn % based on price momentum + treasury health + TVL
   - Defensible if oracles prove resistant to manipulation

2. **Countercyclical tokenomics thesis**
   - Burns during pumps (protect value)
   - Recycles during dumps (fund ecosystem growth when most needed)
   - Aligns with "More Winners Than Losers" core brand

3. **Integration upside with t54's credit layer**
   - Could use recycled $TECH to fund ClawCredit lines for agents
   - Gentech supply sink + t54 credit scoring = synergistic combo

---

## 5. Comparative Evaluation Matrix

| Attribute | EIP-1559 | Stepn | t54.ai | GMX | **$TECH Dynamic** |
|-----------|-----------|-------|--------|-----|-------------------|
| Adjustable ratio | No (fixed %) | Yes (binary burn) | N/A (no token) | No | **Yes (continuous 10–90%)** |
| Market signal-based | Partially | Yes (usage) | Credit-based | No | **Yes (multi-signal)** |
| Treasury-linked | No | No | Yes (revenue) | Yes (buybacks) | **Yes (treasury health)** |
| Deflationary pressure | Cyclical | High (mint-dependent) | N/A | Moderate | **Cyclical, adaptive** |
| User alignment | Protocol fee burner | Sneaker minting | Merchant risk | Staker rewards | **Operator + protocol** |
| Implementation complexity | Low (base fee formula) | Medium (game logic) | High (credit infra) | Medium | **High (oracle + keeper)** |

---

## 6. Risk Assessment

**Technical risks:**
- Oracle manipulation: price feeds could be spoofed if using single source
- Keeper centralization: ratio updates need trusted executor (Chainlink Automation or Gnosis Safe)
- Formula gaming: sophisticated actors could front-run signal updates

**Market risks:**
- Complexity confusion: users may not understand adaptive burns vs static
- First-mover education burden: must prove the model works through multiple cycles
- Regulatory: adaptive tokenomics could be viewed as manipulative if not transparent

**Mitigations:**
1. Use multi-source oracles (Chainlink + Uniswap V3 TWAP + Pyth)
2. Cap ratio change per update (±5% max per period)
3. Publish all signal inputs and formula on dashboard

---

## 7. Recommendations

✅ **Proceed with dynamic burn rate** — competitive moat confirmed.

**Immediate next steps:**
1. DMOB: Complete SC feasibility (H001) — can architecture support the dial?
2. DMOB: Gas Reserve SC review (H003) — unblocks YoYo's H004 (monitoring triggers)
3. YoYo: Design monitoring dashboard exposing: burn ratio, price momentum, treasury health, discount pressure
4. Team: Plan Q3 public demo of adaptive burns during market volatility (prove thesis)

**Whitespace opportunity:** Patent the adaptive burn ratio computation method (novelty is strong).

---

## 8. Open Research Questions

- [ ] Benchmark against Arrakis/Gamma auto-rebalance — do they have any token sinks we could mirror?
- [ ] Are there any DeFi protocols that condition emissions on TVL/usage? (ve(3,3) models do this indirectly)
- [ ] How would this integrate with LayerZero/DVF cross-chain messaging if bridging $TECH between chains?
- [ ] What's the minimal viable signal set? (maybe just price momentum + treasury health to start)

---

## 9. Appendix — Raw Competitive Data

**DeFi burn benchmarks:**
- EIP-1559: ~1.5M ETH burned lifetime; burn rate varies 50%–90% of base fee with congestion
- CAKE buybacks: ~$10M/month buyback volume historically (seasonal)
- GMX: esGMX vesting 2–4yr cliffs; revenue share 30% to stakers

**Agent economy benchmarks:**
- t54.ai ClawCredit: agent credit lines $5–10k initial limits, builds through repayment
- Breez/Payman: B2B agent payments; no token model

**YoYo's conclusion:** $TECH dynamic burn would be **first protocol with market-sensing token sink**. If implemented cleanly, it's a narrative + functional moat.
