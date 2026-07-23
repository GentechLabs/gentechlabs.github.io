# Dynamic $TECH Token Payment Mechanisms — Research

**Author**: DMOB (Labs)
**Date**: 2026-04-20
**Status**: Research Phase

---

## The Problem

Fixed discount ($7-8 equivalent in $TECH) breaks when token price moves:
- $TECH moons → users pay fewer tokens → burn rate drops
- $TECH dumps → users pay tons of tokens → looks expensive

Need a **dynamic discount** that adapts to market conditions while keeping the flywheel spinning.

---

## Mechanism Options

### 1. Oracle-Based Dynamic Pricing (Recommended)

**How it works**: Chainlink (or Pyth) price feed determines $TECH/USD rate. Discount percentage adjusts based on price relative to a moving average.

```solidity
// Conceptual — not production ready
function calculateTechPayment(uint256 usdPrice) external view returns (uint256) {
    uint256 techPrice = oracle.getLatestPrice(TECH_USD_FEED);
    uint256 sma50 = movingAverage.get(TECH_USD_FEED, 50 days);

    // Discount scales with price vs 50-day SMA
    uint256 discountBps;
    if (techPrice > sma50 * 120 / 100) {
        discountBps = 1000; // Price 20%+ above SMA → only 10% discount
    } else if (techPrice > sma50) {
        discountBps = 2000; // Price above SMA → 20% discount
    } else {
        discountBps = 3000; // Price below SMA → 30% discount (encourage buying)
    }

    return usdPrice * (10000 - discountBps) / techPrice;
}
```

**Pros**: Market-responsive, creates counter-cyclical incentive
**Cons**: Oracle dependency, gas cost for on-chain SMA (or compute off-chain)

**SDKs/Tools**:
- **Chainlink Data Feeds** — battle-tested, ~$0.01 per read on L2s
- **Pyth Network** — lower latency, pull-based model (cheaper on Base)
- **Uniswap V3 TWAP** — no oracle dependency, compute on-chain via `TickMath`

---

### 2. Bonding Curve Discount

**How it works**: Discount is a function of how much $TECH is in the payment contract's buffer. More $TECH collected recently = higher discount (encourage more payments).

```solidity
// Discount based on recent payment volume
function dynamicDiscount(uint256 totalTechLast30Days) public pure returns (uint256) {
    // Sigmoid curve: 10% min, 30% max
    uint256 midpoint = 1_000_000e18; // 1M $TECH target volume
    uint256 k = 1e18; // steepness

    // Returns bps between 1000-3000
    return 1000 + 2000 * totalTechLast30Days / (totalTechLast30Days + midpoint);
}
```

**Pros**: No oracle needed, self-referencing system
**Cons**: Can be gamed, harder to explain to users

---

### 3. Tiered Discount (Simplest)

**How it works**: Fixed tiers based on how much $TECH user holds or has spent.

| Tier | $TECH Held | Discount |
|------|-----------|----------|
| Bronze | 0 - 10K | 10% |
| Silver | 10K - 100K | 20% |
| Gold | 100K - 1M | 25% |
| Diamond | 1M+ | 30% |

**Pros**: Dead simple, no oracle, good for whales
**Cons**: Static, doesn't respond to price action

---

### 4. Hybrid: Oracle + Tier (My Recommendation)

Combine oracle-based pricing with loyalty tiers:

```
Base discount: oracle-driven (10-30% based on price vs SMA)
Loyalty boost: +1-5% based on cumulative $TECH spent
Maximum total: 35% cap
```

This gives you:
- Market-responsive base rate (oracle)
- Loyalty rewards for repeat customers (on-chain tracking)
- Hard cap prevents abuse

---

## SDK & Tooling Landscape

### For Price Oracles
| Tool | Chain | Latency | Cost | Notes |
|------|-------|---------|------|-------|
| **Chainlink Data Feeds** | ETH, Base, most EVMs | ~1hr (heartbeat) | ~$0.01 on L2 | Most battle-tested |
| **Pyth Network** | 50+ chains | ~400ms (pull) | Cheap on Base | Better for frequent updates |
| **Uniswap V3 TWAP** | Any with Uni V3 | Configurable | Gas only | No external dependency |

### For Payment Routing
| Tool | Purpose | Notes |
|------|---------|-------|
| **OpenZeppelin SafeERC20** | Safe token transfers | Always use this |
| **OpenZeppelin AccessControl** | Role-based admin | Treasury ops, param changes |
| **Sablier V2** | Streaming payments | If you want recurring subscriptions |
| **0x Protocol** | Swap routing | If users want to pay with *any* token |

### For Token Burns
| Pattern | Gas | Verifiability | Reversibility |
|---------|-----|---------------|---------------|
| `transfer(dead)` | Low | Medium | No (but tokens exist) |
| Custom burn (reduce totalSupply) | Low | High | No |
| Buyback + burn | High | High | No |

### For Moving Averages (on-chain)
| Approach | Description |
|----------|-------------|
| **Off-chain + signature** | Compute SMA off-chain, verify signature on-chain (cheapest) |
| **Cumulative price** | Uniswap V3 style `observation` array |
| **Chainlink Automation** | Keeper updates SMA periodically |

---

## Architecture Recommendation

```
┌─────────────────────────────────────────────┐
│              TechPaymentRouter               │
│                                             │
│  ┌───────────┐   ┌──────────────────────┐   │
│  │ Chainlink │──▶│  DiscountCalculator  │   │
│  │ Price Feed│   │  (oracle + tiers)    │   │
│  └───────────┘   └──────────┬───────────┘   │
│                             │               │
│                    ┌────────▼────────┐      │
│                    │ Payment Splitter│      │
│                    │                 │      │
│                    │  70% → burn     │      │
│                    │  30% → treasury │      │
│                    └────────┬────────┘      │
│                             │               │
│              ┌──────────────┼──────────┐    │
│              ▼              ▼          ▼    │
│         0xdead...     Treasury    Events    │
│         (burn)        (multisig)  (index)   │
└─────────────────────────────────────────────┘
```

### Key Contracts
1. **TechPaymentRouter** — Entry point, accepts $TECH, calculates price, routes split
2. **DiscountCalculator** — Pure math contract, takes oracle price + user tier → returns discount
3. **BurnSplitter** — Handles the 70/30 split, emits burn events

### Key Events
```solidity
event PaymentProcessed(
    address indexed user,
    uint256 techAmount,
    uint256 usdValue,
    uint256 discountBps,
    uint256 burned,
    uint256 toTreasury
);
```

---

## Security Considerations

1. **Oracle manipulation** — Use TWAP + circuit breaker if price moves >20% in 1 block
2. **Reentrancy** — checks-effects-interactions on all external calls
3. **Rounding** — burn amount rounds down, treasury gets remainder (no dust loss)
4. **Admin keys** — Discount params changeable by multisig only, timelock on critical changes
5. **Flash loan protection** — No discount-tier logic based on same-block balance

---

## Next Steps

- [ ] Decide: Chainlink vs Pyth vs TWAP for Base deployment
- [ ] Choose burn ratio (70/30 is a starting point, not final)
- [ ] Define discount curve parameters
- [ ] Build Foundry test suite
- [ ] Internal audit before any testnet deploy
