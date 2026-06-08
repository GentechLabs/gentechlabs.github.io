---
type: strategy
title: "Tradesta Leverage Trading Setup"
created: 2026-06-01
tags: [strategies, trading, perps, tradesta]
---

# 📈 Tradesta — DEX Perpetual Exchange

**Platform:** [app.tradesta.io](https://app.tradesta.io)
**Type:** Decentralized perpetual exchange (long/short with leverage)

## Jordan's Favorites (Long/Short Watchlist)

| Asset | Type | Notes |
|-------|------|-------|
| AVAX/USD | Crypto | AAE home chain. 90-day floor $8.59. Sub-$8 = rare. |
| LINK/USD | Crypto | Oracle play. Tracks BTC correlation. |
| PENGU/USD | Meme | Low cap, high volatility. Max 2x leverage. |
| SOL/USD | Crypto | High beta. Good for momentum trades. |
| XAG/USD | Commodity | Silver spot. Safe haven / inflation hedge. |
| XAU/USD | Commodity | Gold spot. Risk-off asset. |
| USOILSPOT/USD | Commodity | WTI crude. Geopolitical sensitivity. |

## Signal Cron Job
- **Job ID:** dd6455d35760
- **Schedule:** Daily at 3:00 PM UTC (11 AM ET)
- **Delivers to:** Strategies group
- **Output:** Daily leverage signal with LONG/SHORT/NO TRADE per asset

## Trading Rules
- Max leverage: 5x (2x for PENGU)
- Always use stop losses
- Bear market = bias SHORT on relief rallies
- Don't force trades — "NO TRADE" is a valid signal
- Key levels flagged when price within 2% of support/resistance

---
*Setup: 2026-06-01*
