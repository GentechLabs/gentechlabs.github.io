---
name: defi-hybrid-strategy-engine
description: "Build DeFi multi-strategy portfolio allocation engines — regime detection, strategy return comparison (LP vs HODL vs staking vs lending), dynamic allocation matrices, and proactive rotation alerts. Uses DeFiLlama Yields API for rate feeds."
tags: [defi, allocation, regime, strategy, benqi, defillama, avax, portfolio]
version: 1.0.0
author: DMOB
---

# DeFi Hybrid Strategy Engine

Build multi-strategy portfolio allocation systems that compare returns across DeFi strategies and dynamically rotate based on market conditions.

## When to Use

- Building a system that compares LP vs HODL vs staking vs lending returns
- Need market regime detection (bull/bear/range/volatile) for strategy selection
- Designing allocation matrices that map regimes to portfolio splits
- Integrating DeFiLlama Yields API for staking/lending rate feeds on Avalanche
- Building proactive rotation alerts ("we're switching strategy")

## Architecture

```
Market Data → Regime Classification → Strategy Comparison → Allocation Recommendation
     │                │                       │                      │
 DexScreener    regime_classifier.py   strategy_returns.py   allocation_engine.py
 DeFiLlama                                (DeFiLlama rates)
 On-chain RPC
```

### Module Files

| Module | File | Purpose |
|--------|------|---------|
| Regime Classifier | `regime_classifier.py` | Classifies market into 6 regimes |
| Strategy Returns | `strategy_returns.py` | Fetches rates, compares returns across strategies |
| Allocation Engine | `allocation_engine.py` | Maps regime → allocation, detects rotation needs |
| Unified Pipeline | `aae-hybrid-signal.py` | Chains all three, outputs unified signal |

All files live in `03-Strategies/scripts/` (vault) and `~/.hermes/scripts/` (runtime).

## Data Sources

### DexScreener (Price/Volume)
```python
url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL_ADDRESS}"
# ⚠️ MUST include User-Agent header — returns 403 without it
headers = {"User-Agent": "Mozilla/5.0 (AAE-Hybrid/1.0)"}
```

### DeFiLlama Yields API (Staking/Lending Rates)
```python
url = "https://yields.llama.fi/pools"
# Filter for Benqi on Avalanche
```

**⚠️ Critical Gotcha — Benqi Project Names:**
DeFiLlama uses `project` field, not `name`. Benqi has MULTIPLE project names:
- `benqi-lending` (supply/borrow rates for USDC, AVAX, etc.)
- `benqi-staked-avax` (sAVAX staking APR)
- `benqi` (some pools)

Filter with: `project in ["benqi-lending", "benqi-staked-avax", "benqi"]`

**Pitfall:** If you filter for just `"benqi"`, you get 0 results. This was a 30-min debug session.

### On-Chain RPC (Wallet Balances)
```python
RPC_URL = "https://api.avax.network/ext/bc/C/rpc"
# Standard eth_call, eth_getBalance work fine
```

## Regime Classification

### The 6 Regimes

| Regime | Condition | Allocation Tilt |
|--------|-----------|-----------------|
| `BULL_TRENDING` | Momentum >10%, volume >1.3x, RSI >55 | HODL dominant (60%) |
| `BEAR_TRENDING` | Momentum <-10%, volume >1.3x, RSI <45 | Staking dominant (50%) |
| `RANGE_BOUND` | \|Momentum\| <5%, volume normal | LP dominant (40%) |
| `HIGH_VOLATILITY` | ATR/price >8% | Diversified (no tilt) |
| `ACCUMULATION` | Flat after dump, volume declining | HODL + staking (65%) |
| `PRICE_DISCOVERY` | New highs/lows, wide range | HODL dominant (70%) |

### Detection Logic
```python
def classify_regime(momentum, vol_ratio, rsi, atr_pct):
    if atr_pct > 0.08:          return "HIGH_VOLATILITY"
    if momentum > 0.10 and vol_ratio > 1.3 and rsi > 55:
                                return "BULL_TRENDING"
    if momentum < -0.10 and vol_ratio > 1.3 and rsi < 45:
                                return "BEAR_TRENDING"
    if abs(momentum) < 0.05:    return "RANGE_BOUND"
    # ... etc
```

### Indicators Needed
- **RSI (14-period):** Needs 15+ data points. Starts as `None`, populates over time.
- **ATR (14-period):** Same — needs history.
- **7-day momentum:** `(price_now - price_7d_ago) / price_7d_ago`
- **Volume ratio:** `volume_24h / volume_avg_7d`

**Pitfall:** First run will have `rsi=None, atr=None` because price history is empty. This is expected — the classifier defaults to RANGE_BOUND. Over time (15+ data points), indicators populate.

## Allocation Matrix

### Default Matrix (Balanced Risk)

```python
ALLOCATION_MATRIX = {
    "BULL_TRENDING":    {"lp": 15, "hodl": 60, "staking": 15, "lending": 10},
    "BEAR_TRENDING":    {"lp": 10, "hodl": 20, "staking": 50, "lending": 20},
    "RANGE_BOUND":      {"lp": 40, "hodl": 15, "staking": 30, "lending": 15},
    "HIGH_VOLATILITY":  {"lp": 25, "hodl": 30, "staking": 25, "lending": 20},
    "ACCUMULATION":     {"lp": 20, "hodl": 40, "staking": 25, "lending": 15},
    "PRICE_DISCOVERY":  {"lp": 10, "hodl": 70, "staking": 15, "lending": 5},
}
```

### Risk Profile Adjustments

| Profile | LP | HODL | Staking | Lending |
|---------|-----|------|---------|---------|
| Conservative | -10% | -5% | +10% | +5% |
| Balanced | 0 | 0 | 0 | 0 |
| Aggressive | +10% | +5% | -10% | -5% |

### Rotation Thresholds
- **Min delta to trigger rotation:** 20% (prevents overtrading)
- **Cooldown between rotations:** 4 hours
- **Max single allocation:** 70% (always diversify)
- **Min single allocation:** 5% (keep positions alive)

## Pitfalls

1. **DeFiLlama project names.** Benqi is `benqi-lending` + `benqi-staked-avax`, NOT `benqi`. Always check `yields.llama.fi/pools` for actual project names before filtering.

2. **DexScreener 403 errors.** Without `User-Agent` header, DexScreener returns 403 Forbidden. Always include a UA string.

3. **Price history cold start.** Regime classifier needs 15+ data points for RSI/ATR. First runs return `RANGE_BOUND` with null indicators. This is by design — don't hack around it.

4. **LP returns need real fees.** The strategy returns module uses `fees_24h` parameter. If passed 0, LP shows negative returns (just IL). Wire this to the existing AAE signal monitor's fee data.

5. **Allocation normalization.** After applying risk adjustments, allocations may not sum to 100%. Always normalize by adding the difference to the largest allocation.

6. **Module naming.** Python can't import files with hyphens. Use underscores: `regime_classifier.py` not `regime-classifier.py`.

## Integration with Existing AAE

The hybrid engine extends (not replaces) the existing AAE signal monitor:

```
Existing: lp-aae-signal-monitor.py → LP-only signal
New:      aae-hybrid-signal.py → Multi-strategy signal (includes LP data)
```

The hybrid signal can be added as an additional cron job or merged into the existing AAE cron prompt.

## Current Pool Info

- **Pool:** LFJ V2.2 AVAX/USDC, binStep 10, 5 bps
- **Pool Address:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Chain:** Avalanche
- **Current Range:** $9.00–$9.45 (Curve shape, as of Apr 29, 2026)
- **Wallet:** `[REDACTED_WALLET]`
