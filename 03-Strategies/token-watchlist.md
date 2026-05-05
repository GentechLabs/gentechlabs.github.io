# Jordan's Token Watchlist — "Bullish" (Standalone)
> Updated: 2026-04-28 — API key live, hourly cron active.

Long term holds for staking, yield farming, etc. Prices fetched from **CoinMarketCap API** with CoinGecko fallback. Alert threshold: **1.5% movement** to trigger report.

## Holdings
| # | Token | Ticker | Price (Apr 28) | 24h % | 7d % | Notes |
|---|-------|--------|----------------|-------|------|-------|
| 1 | Bitcoin | BTC | $75,935 | -1.10% | -0.06% | |
| 7 | Solana | SOL | $83.53 | -0.87% | -2.85% | |
| 15 | Chainlink | LINK | $9.22 | +0.22% | -1.99% | |
| 23 | Avalanche | AVAX | $9.17 | +0.15% | +2.33% | LP position tracked separately — see LP Monitor |
| 31 | Bittensor | TAO | $258.10 | +5.13% | +5.75% | |
| 32 | Tether Gold | XAUt | $4,581 | -1.80% | -2.84% | Gold-backed stable |
| 192 | Beam | BEAM | $0.001971 | -0.12% | ? | Gaming |
| ? | Coq Inu | COQ | ? | ? | ? | Meme |
| ? | The Arena | ARENA | ? | ? | ? | |
| 18 | Silver | XAG | $73.03 | ? | ? | Commodity |

## CMC Watchlist
- **Watchlist ID:** `67453707ad745f0bbd4ad54f`
- **URL:** https://coinmarketcap.com/watchlist/67453707ad745f0bbd4ad54f
- **API Key:** Stored in `~/.hermes/scripts/cmc_config.json` (chmod 600)

## Cron Schedule
- **Frequency:** Hourly, 7am–9pm (local)
- **Smart Skip:** If all tokens <1.5% move since last check, report is suppressed
- **Jobs:**
  - YoYo profile: `faed4f588aef`
  - Desmond profile: `862ae0c1f85d`
- **Script:** `~/.hermes/scripts/cmc-watchlist.py`

## What This Report Includes
1. **Prices** — Current + 1h/24h/7d change for all watchlist tokens
2. **Volume trends** — Unusual activity, breakout signals
3. **Token news** — Project updates, partnerships, governance votes
4. **Macro narrative** — 1-2 lines of "why" the market is moving

## Alerts to Watch For
- 🚨 **Rug signals:** Sudden liquidity removal, team wallet dumps, contract upgrades without notice
- 📢 **Major upgrades:** Protocol changes, mainnet launches, governance votes
- 💰 **Yield changes:** APY drops, staking reward reductions
- 📈 **Breakouts:** 20%+ moves in 24h, volume spikes
- 🏦 **Regulatory:** SEC actions, exchange delistings

## Sources to Monitor
- CoinMarketCap API (live prices)
- CoinMarketCap watchlist: https://coinmarketcap.com/watchlist/67453707ad745f0bbd4ad54f
- Twitter/X accounts for each project
- On-chain data (DeFiLlama for TVL changes)

## Related
- **LP + Milestone Tracker:** `03-Strategies/LP-Monitor-Rules.md` (separate, standalone report)

## Date Created
2026-04-17
