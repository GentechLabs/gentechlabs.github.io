---
type: config
title: "Jordan's Coin Watchlist"
created: 2026-04-20
updated: 2026-05-05
tags: [strategies, crypto, watchlist, cmc]
---

# 💰 Jordan's Coin Watchlist

**Edit this file to add/remove coins.** The Strategies cron job reads from here.

## Format
One coin per line: `SYMBOL — optional notes`
The cron pulls price data for any symbol listed below.

## Active Coins

- BTC — Bitcoin, market leader
- SOL — Solana, high-speed L1
- LINK — Chainlink, oracle network
- AVAX — Avalanche, AAE home chain (LP position tracked separately)
- TAO — Bittensor, AI/ML network
- XAUt — Tether Gold, gold-backed stable
- BEAM — Beam, gaming

## Removed

- ~~LAND~~ — Landshare, dApp shutting down May 2026. Removed from active watchlist.
- ~~PROPS~~ — Propbase, Southeast Asia real estate RWA. Removed May 2026 — micro cap ($2.5M), 98% off ATH, on Aptos not AVAX. Revisit if bullish market returns.
<!-- Coins you've dropped — keep for reference -->

---

## CMC API Configuration

**API Key Location:** `/root/.hermes/profiles/yoyo/secrets/cmc_api_key.txt`
**Config File:** `/root/.hermes/scripts/cmc_config.json`

**Watchlist ID:** `67453707ad745f0bbd4ad54f`
**Watchlist Name:** Bullish
**URL:** https://coinmarketcap.com/watchlist/67453707ad745f0bbd4ad54f

## Cron Job Schedule

**Job:** YoYo — Crypto Watchlist (`faed4f588aef`)
**Schedule:** Every hour from 7 AM to 9 PM (`0 7-21 * * *`)
**Smart Skip:** Skips if all tokens moved < 0.5% since last check
**Alert Threshold:** 3%+ move triggers alert

## Smart Skip Logic

1. Load last prices from `~/.hermes/scripts/.cmc-watchlist-state.json`
2. Fetch current prices from CMC API
3. Calculate max price change across all tokens
4. **Skip** if max change < 0.5% (silent)
5. **Report** if max change ≥ 0.5% (show watchlist)
6. **Alert** if any token moved ≥ 3% (highlight movers)

---

*Last updated: May 5, 2026*
