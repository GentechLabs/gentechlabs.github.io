---
name: lp-position-tracker
description: Combine LP pool monitoring with position P&L tracking for concentrated liquidity positions
---

# LP Position Tracker

Combine pool health monitoring (volume, liquidity, APR, range status) with position-level P&L tracking (entry value, impermanent loss, fees earned, net returns vs HODL).

## When to Use
When monitoring a DeFi LP position and need combined pool + position reports via cron.

## Context
Pattern built for Jordan's LFJ AVAX/USDC 5bps concentrated LP on Avalanche. Works for any concentrated liquidity position on any DEX.

## Position Data File (JSON)
Store entry data in a persistent JSON file:
```json
{
  "entry_date": "2026-03-31",
  "entry_avax": 1.39,
  "entry_usdc": 18.85,
  "entry_avax_price": 8.85,
  "entry_total_usd": 31.16,
  "snapshots": [
    {"date": "2026-04-21", "avax": 1.538, "usdc": 14.2, "total_usd": 28.66, "avax_price": 8.94}
  ]
}
```
Path: `~/.hermes/scripts/.lfj-position-tracker.json`

## Impermanent Loss Formula (50/50 LP)
```python
def calc_impermanent_loss(entry_price: float, current_price: float) -> dict:
    price_ratio = current_price / entry_price
    il_pct = (2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1) * 100
    return {"il_pct": round(il_pct, 2), "price_ratio": round(price_ratio, 4)}
```

## Full P&L Calculation
```python
def calc_position_pnl(price: float, position: dict, fees_earned: float = 0) -> dict:
    entry = position["entry_total_usd"]
    entry_avax = position["entry_avax"]
    entry_usdc = position["entry_usdc"]
    entry_price = position["entry_avax_price"]

    # Value if just held (no LP)
    hold_value = (entry_avax * price) + entry_usdc

    # IL applied to hold value
    il = calc_impermanent_loss(entry_price, price)
    il_usd = hold_value * (il["il_pct"] / 100)

    # LP value = hold value - IL + fees
    lp_value = hold_value - abs(il_usd) + fees_earned

    net_pnl = lp_value - entry
    net_pnl_pct = (net_pnl / entry) * 100
    vs_hodl = lp_value - hold_value

    return {
        "entry_usd": round(entry, 2),
        "current_lp_value": round(lp_value, 2),
        "hold_value": round(hold_value, 2),
        "il_pct": il["il_pct"],
        "il_usd": round(il_usd, 2),
        "fees_earned": round(fees_earned, 2),
        "net_pnl": round(net_pnl, 2),
        "net_pnl_pct": round(net_pnl_pct, 2),
        "vs_hodl": round(vs_hodl, 2),
    }
```

## Data Sources
1. **DexScreener** (free, no key): `https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}`
2. **Birdeye x402** ($0.003/req): token overview, security, trade data — primary source
3. **CMC API** (key: [CMC-API-KEY-REDACTED]): watchlist token prices

## Pool Details (LFJ AVAX/USDC)
- Pool: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- Chain: Avalanche
- AVAX: `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`
- USDC: `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`

## Cron Integration
Combine LP monitoring with crypto watchlist in one cron job:
- Schedule: hourly (7 AM – 9 PM ET)
- Report 3 sections: crypto prices → pool health → position P&L
- Alert: Silent if in range + efficiency >75%, alert if out of range
- Deep-dive triggers: AVAX moves >5% or Sundays → IL forecasts, rebalancing rec

## Pitfalls
- APR is misleading at low TVL — track 7D APR not instant
- Tight ranges (<5%) can exit in hours — confirm out-of-range on 2nd check
- IL compounds: 2x price = ~5.7% IL, 3x = ~13.4%
- Fees vary with volume — use 7D rolling average
- Position file needs manual update when adding/withdrawing liquidity

## Files
- Script: `03-Strategies/scripts/lp-range-monitor-v2.py`
- Position data: `~/.hermes/scripts/.lfj-position-tracker.json`
- Analysis: `03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md`
- Cron manifest: `03-Strategies/cron-jobs.md`
