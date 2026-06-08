# LFJ AVAX/USDC LP Monitor — 2026-04-27

## Executive Summary

- 🔴 **Position OUT OF RANGE** since 19:48 EDT — earning zero fees. AVAX at $9.25, range is $9.36–$9.53.
- **Pool is healthy**: $3.9M TVL, $11.4M 24h volume, 52.7% fee APR. Volume/TVL at 2.89x — strong trading activity.
- **Sell pressure HIGH**: 1,647 sells vs 1,258 buys (24h). B/S ratio 0.76 — downward momentum. Rebalancing recommended if AVAX breaks below $9.10.

---

## On-Chain Data

### Price & Market

| Metric | Value |
|--------|-------|
| AVAX Price | $9.25 |
| 24h Change | -2.39% |
| USDC Price | $0.9999 |

### Pool Metrics (LFJ AVAX/USDC — 5bps)

| Metric | Value |
|--------|-------|
| Pool TVL | $3,937,711 |
| 24h Volume | $11,367,417 |
| Volume/TVL | 2.89x |
| Est. Daily Fees | $5,684 |
| Pool Fee APR | 52.7% |
| 24h Buys | 1,258 |
| 24h Sells | 1,647 |
| Buy/Sell Ratio | 0.764 |

Source: DexScreener API (19:48 EDT snapshot)

---

## LP Fee Efficiency Analysis

### Position Status

| Metric | Value |
|--------|-------|
| Status | 🔴 **OUT OF RANGE** |
| Fee Efficiency | 0.0% |
| Range | $9.36 – $9.53 |
| Current Price | $9.25 |
| Distance from Lower Bound | -1.18% |
| Out of Range Since | 19:48 EDT |

### Position Value

| Metric | Value |
|--------|-------|
| Entry Date | Mar 31, 2026 |
| Entry AVAX | 1.39 @ $8.85 |
| Entry USDC | 18.85 |
| Entry Total | $31.16 |
| Current AVAX Value | $12.86 |
| Current USDC | $18.85 |
| **Current Total** | **$31.71** |
| **PnL** | **+$0.55 (+1.8%)** |
| Est. IL | -0.01% (minimal) |

### Rebalance Analysis (50/50 at $9.25)

For a balanced 50/50 position at current price:
- AVAX needed: 1.7139 (have 1.39)
- USDC needed: $15.85 (have $18.85)
- Net action: sell 0.32 AVAX → $3.00 USDC

---

## Risk Flags

1. 🔴 **Zero fee income** — Position out of range, earning nothing while pool APR is 52.7%
2. 🟡 **High sell pressure** — B/S ratio 0.76 suggests continued downside risk
3. 🟡 **1.18% gap** — Not huge, but if AVAX drops below $9.10, gap widens significantly
4. ℹ️ **Low IL** — Only -0.01% impermanent loss; position is well-managed

---

## Recommendations

### Option A: Rebalance Now (Recommended)
- **New range:** $9.00 – $9.50 (wider to capture volatility)
- **Action:** Sell 0.32 AVAX for USDC, re-deposit
- **Rationale:** Pool APR is 52.7% — every hour out of range costs ~$0.06 in missed fees
- **Risk:** If AVAX drops further, still out of range. Wider range mitigates.

### Option B: Wait for Recovery
- AVAX needs to recover 1.2% to re-enter range
- Keep earning zero fees while waiting
- **Rationale:** If you believe AVAX bounces from $9.25, no action needed
- **Risk:** Sell pressure suggests further downside; could be waiting days

### Option C: Tighten After Recovery
- Wait for AVAX to return to $9.36+
- Then rebalance to tighter range for higher efficiency
- **Rationale:** Avoid rebalancing at a local bottom
- **Risk:** If recovery doesn't come, zero fees indefinitely

**My recommendation:** Option A. The 52.7% pool APR means you're losing ~$0.06/hour in potential fees. A wider range ($9.00–$9.50) gives 5.4% buffer while still capturing concentrated fees.

---

## Data Sources

- CoinGecko API (token prices, 24h volume/change)
- DexScreener API (pool-specific data, liquidity, txns)
- LFJ LP Monitor Script v2 (position state, range data)
- Position tracker: `~/.hermes/scripts/.lfj-position-tracker.json`

Report generated: 2026-04-27 ~19:50 EDT
Next check: Run monitor again in 2-4 hours or on alert
