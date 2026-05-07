---
title: Solana Yield Farming Platforms Reference
date: 2026-05-03
updated: 2026-05-03
session: PROPS-LAND-real-estate-analysis
tags: [solana, defi, yield, platforms]
---

# Solana Yield Farming Platforms — Quick Reference

**Use case:** Generate stablecoin or SOL yield to compound while holding RWA tokens on Avalanche. Target: 8-20% APR with lowimpermanent loss risk.

## Platform Matrix

| Platform | Primary Pools | Typical APR (SOL) | Typical APR (USDC) | Fees | Status |
|----------|--------------|------------------|-------------------|------|--------|
| **Marinade** | mSOL/SOL, mSOL/USDC | 3-5% | 8-12% | 0.04% | ✅ Liquid staking, low IL |
| **MarginFi** | SOL borrow/lend, USDC lending | 4-7% (supply) | 10-15% (supply) | 0.07% | ✅ Lending, no IL |
| **Raydium** | SOL/USDC, stablecoin farms | 5-10% (LP) | 12-20% (LP) | 0.25% | ⚠️ Watch for token rewards expiration |
| **Orca** | Whirlpools (concentrated) | 8-15% (targeted) | 15-25% (narrow) | 0.30% | 🔶 Higher fee, active rebalancing needed |
| **Jupiter** | Aggregated routes + farm | Varies | Varies | Varies | 🔶 Auto-routing, less control |
| **Drift** | Perps funding rate arbitrage | funding-based | funding-based | 0.05% | ⚠️ Leverage risk |

## Recommended Allocation (Conservative)

**Strategy:** Marinade + MarginFi split (70/30)

```
Marinade Finance:
  - mSOL/SOL LP → 4-6% APR, minimal IL (mSOL tracks SOL)
  - mSOL/USDC LP → 8-12% APR, stablecoin exposure
  - Auto-compound daily

MarginFi:
  - USDC lending → 10-15% supply APY, zero IL
  - SOL borrow to multiply (optional, risky)
```

**Rationale:**
- Low IL risk (stablecoin or correlated-asset LPs)
- Daily/weekly compounding
- No active rebalancing required

## Platform Comparison Criteria

| Factor | Weight | Notes |
|--------|--------|-------|
| **IL risk** | 30% | Stablecoin pairs = minimal; correlated assets = low |
| **APY sustainability** | 25% | Pure fee-based > token rewards; check emission schedule |
| **TVL depth** | 20% | >$100M pool depth reduces slippage, improves stability |
| **Protocol risk** | 15% | Audit history, age of protocol, TVL locked |
| **Ease of use** | 10% | Auto-compound feature, gas efficiency |

## Current Protocol State (May 2026)

- **Marinade** — matured, mSOL main liquid staking derivative; APYs compressed but stable
- **MarginFi** — lending dominant; USDC pool depth >$500M → reliable rates
- **Raydium** — AMM still active but volume shifted to Orca for LPs; watch token reward programs
- **Orca** — concentrated liquidity dominates; requires range management (150-200 bps optimal)
- **Jupiter** — aggregator, not a farm platform per se; use for best route, not yield

## Integration with AAE Hybrid Strategy

**Regime mapping:**
- `BULL_TRENDING` → 40% LP (Raydium/Orca narrow ranges), 60% staking (Marinade)
- `RANGE_BOUND` → 70% LP (wider ranges on Raydium), 30% lending (MarginFi)
- `BEAR_TRENDING` → 30% LP, 70% USDC lending (protective)
- `HIGH_VOLATILITY` → 20% LP (very wide), 80% staking/lending (defensive)

**Position sizing w/ RWA layer:**
- Base: 70% of DeFi capital in Solana yield (DMOB allocation)
- Trim: Reduce to 50% if adding new LP positions on Avalanche for RWA
- Allocate freed capital to PROPS/LAND direct holds

## Monitoring Hooks

Add to `allocation_engine.py` regime check:

```python
if regime == "RANGE_BOUND":
    solana_yield_allocation = 70  # up from 60 base
    avalanche_rwa_allocation = 10  # DCA during consolidation as Jordan suggested
elif regime == "BEAR_TRENDING":
    solana_yield_allocation = 50  # defensive
    avalanche_rwa_allocation = 20  # buy the dip
```

## Pitfalls
1. **Token rewards decay** — Raydium farm APYs often include token emissions that halve quarterly. Check emission schedule.
2. **Smart contract risk** — Newer platforms may have unaudited contracts. Prefer Marinade/MarginFi (established, audited).
3. **Impermanent loss on correlated assets** — mSOL/SOL minimal IL; SOL/USDC moderate IL in volatile conditions.
4. **APR manipulation** — Some pools show inflated APR from temporary incentives; look for 30-day average not peak.
5. **Gas costs on rebalancing** — Orca narrow ranges require frequent adjustments; factor in Solana transaction fees (~$0.00025 each).

## Verification
- [ ] Pool TVL > $50M for stablecoin pairs, >$20M for SOL pairs
- [ ] APY track record >90 days (avoid brand-new farms)
- [ ] Protocol audits: at least 1 public audit by reputable firm (OtterSec, Neodyme, Trail of Bits)
- [ ] No recent major exploits (check Immunefi, Cantina)
- [ ] Clear tokenomics: emissions schedule, fee distribution, buyback mechanisms

## Sample Entry Workflow
```
1. Determine weekly DCA amount ($100)
2. 70% → Solana yield layer:
   - $35 Marinade mSOL/USDC LP (auto-compound)
   - $35 MarginFi USDC supply (earn interest)
   - $30 Raydium SOL/USDC LP (manual rebalance monthly)
3. 30% → RWA layer (reserved for Avalanche buys when PROPS/LAND dip 10%+)
```

## References
- [Marinade Finance docs](https://docs.marinade.finance/)
- [MarginFi docs](https://docs.marginfi.com/)
- [Raydium liquidity mining](https://raydium.io/liquidity-mining/)
- [Orca whirlpools](https://orca.so/whirlpools)
- [Solana DeFi Llama yields](https://defillama.com/chain/Solana)
