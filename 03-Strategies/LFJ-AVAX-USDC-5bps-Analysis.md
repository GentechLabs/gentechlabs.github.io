# LFJ AVAX/USDC 5bps Pool — Analysis

**Date Queued:** April 14, 2026
**Status:** 🟢 Active — monitored by LP Watchlist cron (every 2 hrs, 6:30 AM–11 PM Eastern)
**Priority:** Active Position
**Agent:** YoYo (Strategies)

## Pool Details

- **Pool Address:** 0x864d4e5ee7318e97483db7eb0912e09f161516ea
- **Chain:** Avalanche
- **Platform:** LFJ (formerly Trader Joe)
- **Pair:** AVAX / USDC
- **Fee Tier:** 5 bps (0.05% base fee)
- **Bin Steps:** 10bps

## Current Metrics (Apr 14, 2026)

| Metric | Value | Change |
|--------|-------|--------|
| Liquidity | $3,565,755 | +0.43% |
| Volume (24h) | $30,013,981 | +288.56% |
| Fees (24h) | $16,292 | +288.57% |
| APR (7d) | 93.49% | — |
| AVAX Reserves | 273,723 AVAX | — |
| USDC Reserves | 994,281 USDC | — |
| AVAX Price | ~$9.41 | — |

## Token Addresses

- **AVAX:** 0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7
- **USDC:** 0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e

## Jordan's Active Position (Apr 23, 2026)

- **Entry:** $31.16 (Mar 31, 2026)
- **Deposit Balance:** $82.80 (Apr 23)
- **AVAX:** 0.383
- **USDC:** 79.23
- **AVAX Price:** ~$9.37
- **Range:** 9.18 – 9.40 (Curve Shape, tightened for reward bin capture)
- **Status:** In range, earning fees
- **Pool APR:** ~122% (7D)
- **Platform:** LFJ mobile app
- **Risk Note:** Tight range — needs rebalance if AVAX moves >3.5% either direction
- **Tracker Script:** `03-Strategies/scripts/lp-unified-monitor.py` (consolidated watchlist + P&L)
- **Position File:** `~/.hermes/scripts/.lfj-position-tracker.json`

## Analysis Requested

1. **APR Stability** — Is the 93% sustainable or driven by today's 288% volume spike?
2. **IL Risk** — Impermanent loss exposure at current AVAX volatility
3. **Historical Volume Patterns** — Normal daily volume vs spike days
4. **TVL Trend** — Steady growth to $3.5M — is this organic?
5. **Position Sizing** — If Jordan wanted to LP here, what size makes sense?
6. **Comparison** — How does this compare to other AVAX/USDC pools on LFJ?

## Jordan's DeFi Context
- Ex-DeFi strategist and market maker
- Previous AVAX-USDC & MON-USDC LP positions on LFJ
- Uses concentrated vs. curve distributions based on market conditions
- Tracks BTC 200-week and 50-week moving averages
- Currently building skills, not trading actively

## Source
Screenshot from LFJ analytics dashboard. Jordan bookmarked this pool for potential LP position.

## Tags
#strategy:lp #chain:avalanche #platform:lfj #pair:avax-usdc #status:pending #agent:yoyo
