---
name: crypto-lp-monitoring
description: Production-ready crypto watchlist + LP position tracking workflow. Fetches live prices from CoinGecko, runs LP monitor, computes IL projections and fee efficiency analysis.
triggers:
  - scheduled_cron_job
  - weekly_position_review
  - price_threshold_breach
---
# Crypto LP Monitoring

Numbers-first, risk-aware analysis with automatic fallback handling.

## Process

### 1. Fetch watchlist prices

**Issue:** CoinGecko simple price endpoint returns empty without a `User-Agent` header. Use `urllib.request` with headers `{'User-Agent': 'Mozilla/5.0'}`.

**Endpoint selection:**
- `/api/v3/simple/price` — gives `current_price` and `usd_24h_change`. **Does NOT include 7d change.**
- `/api/v3/coins/markets?price_change_percentage=7d` — gives full data including 7d % change. Use this as primary.

**BEAM token disambiguation:** `search?query=beam` returns multiple tokens. Use `beam-2` (market cap rank ~274) over `moonbeam` (GLMR) or legacy `beam` (rank ~1800). Include `beam-2` in the coins/markets IDs list.

### 2. Execute LP monitor

Run `lp-range-monitor-v2.py` from `/root/vaults/gentech/03-Strategies/scripts/`.

**Input files:**
- Position: `~/.hermes/scripts/.lfj-position-tracker.json`
- State: `~/.hermes/scripts/.lfj-range-state.json`
- Observation cache: `~/.hermes/shared/MARKET_OBSERVATION_avax_lp.json`

**Data sources:** Birdeye x402 (primary) → DexScreener (fallback). Script auto-falls back.

**Output behavior:**
- `SILENT` — in_range AND efficiency ≥ 75%
- `ALERT:low_efficiency` — in_range but efficiency < 75%
- `ALERT:out_of_range_confirmed` — confirmed out-of-range
- `OK` — in_range but not silent (non-alert status)

Regardless of exit code, always include a 1-line LP status summary in reports.

### 3. Compute IL projections

**IL formula:**
```
price_ratio = current_price / entry_price
il_pct = (2 * sqrt(price_ratio) / (1 + price_ratio) - 1) * 100
il_usd = hold_value * (il_pct / 100)
```

Where `hold_value = entry_avax * current_price + entry_usdc`.

Entry data read from position tracker (`entry_avax_price`, `entry_avax`, `entry_usdc`).

**Key levels:** $7, $8, $10, $12 for AVAX to show IL progression.

### 4. Fee efficiency analysis

```
effective_daily_yield = pool_apr / 365 * (efficiency_pct / 100)
days_to_breakeven = abs(vs_hodl) / (position_value * effective_daily_yield)  # when vs_hodl < 0
```

Pool APR taken from `MARKET_OBSERVATION_avax_lp.json` (`apr_7d` field).

**Thresholds:**
- ≥75% — optimal
- <75% — efficiency low, warning triggered

### 5. Trigger conditions

Part 3 (IL forecast + breakeven + rebalance recommendation) runs when:
- **Price breach**: AVAX moves >5% from `entry_avax_price`
- **Weekly**: Every Sunday (full projections regardless of move)

**Rebalance signal:** When current price within 5% of `RANGE_LOW` or `RANGE_HIGH`.

## Output Format

```
📊 CRYPTO WATCHLIST + LP REPORT
🗓️ <timestamp> | Gentech Investment Analyst (YoYo)

━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PART 1 — MARKET PRICES
━━━━━━━━━━━━━━━━━━━━━━━━━━

| Asset | Price | 24h % | 7d % |
| BTC   | $XX,XXX | 🔴 +X.XX% | 🟢 +X.XX% |

[Macro context: 1–2 lines on ETF flows / macro drivers]

━━━━━━━━━━━━━━━━━━━━━━━━━━
💧 PART 2 — LP POSITION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━

[LP status: efficiency, price vs range, P&L breakdown]
- Entry: $X.XX (Mon DD) | X.XX AVAX + X.XX USDC
- LP Value: $X.XX | IL: ±X.XX% | Fees: $X.XX
- Net: $±X.XX (±X.X%) | vs HODL: $±X.XX

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 PART 3 — POSITION ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━

[Only if triggered:] IL forecast table, fee accumulation, days to breakeven, rebalance recommendation.
```

## Error Handling & Pitfalls

| Error | Fix |
|---|---|
| CoinGecko returns empty/404 | Add User-Agent header; switch to coins/markets endpoint |
| Missing 7d change | Use `/coins/markets` not `/simple/price` |
| LP script `SILENT` | Still report 1-line LP status: "✅ LP in range, efficiency X%, net $Y" |
| Position file missing | LP script auto-creates default (Mar 31, 1.39 AVAX, 18.85 USDC, $31.16) |
| Price near range edge (<5%) | Flag rebalance warning; consider widening range |

## Current Notes (26-04-22)

- **AVAX/USDC LFJ pool:** Range $9.10–$9.65 (JUMP 5bps), concentrated. Price $9.55 → 35.8% efficiency (LOW), near upper edge (-0.9%).
- **Position:** +3.0% vs entry but trailing HODL by $0.02. Fees effectively $0 due to low efficiency.
- **Trigger threshold hit:** AVAX +8.0% from $8.85 entry → Part 3 analysis generated.
- **BEAM token ID:** `beam-2` on CoinGecko (not GLMR or legacy BEAM).
