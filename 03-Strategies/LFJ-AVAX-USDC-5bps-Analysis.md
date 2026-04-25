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

## Jordan's Active Position (Apr 24, 2026)

- **Entry:** $83.92 (Mar 31, 2026)
- **Deposit Balance:** $83.37 (Apr 24)
- **AVAX:** 3.88 (~$36.56)
- **USDC:** 46.82 (~$46.81)
- **AVAX Price:** ~$9.418
- **Range:** $9.33 – $9.52 (Curve Shape) — *rebalanced Apr 24 (2nd time)*
- **Status:** In range, earning fees
- **Fees 24H:** $0.58 (~0.7% daily → ~255% APR implied)
- **Claimable Rewards:** $0.0075
- **Pool APR (7D):** 88.77%
- **Platform:** LFJ mobile app
- **Risk Note:** Moderate-tight range — rebalance if AVAX moves >3% either direction
- **Tracker Script:** `03-Strategies/scripts/lp-unified-monitor.py` (consolidated watchlist + P&L)
- **Position File:** `~/.hermes/scripts/.lfj-position-tracker.json`

## Pool Health (Apr 24, 2026)

| Metric | Value | Change |
|--------|-------|--------|
| TVL | $3.98M | +11.8% since Apr 14 |
| Volume (24h) | $21.5M | -28.4% since Apr 14 spike |
| Fees (24h) | $10,967 | -32.7% since Apr 14 spike |
| APR (7d) | 88.77% | -4.72pp since Apr 14 |
| AVAX Price | $9.418 | — |

## Snapshot Log

| Date | Deposit | AVAX | USDC | AVAX Price | Fees 24H | Source |
|------|---------|------|------|------------|----------|--------|
| Mar 31 | $83.92 | 3.762 | 48.37 | $9.45 | — | Entry |
| Apr 24 | $83.37 | 3.88 | 46.82 | $9.418 | $0.58 | Screenshot |
| Apr 24 | $83.37 | 3.88 | 46.82 | $9.418 | — | Rebalance: range 9.10-9.65 → 9.26-9.46 |
| Apr 24 | $83.14 | 3.311 | 52.08 | $9.381 | — | Rebalance: range 9.26-9.46 → 9.33-9.52 |

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
