---
name: crypto-lp-monitoring
description: Monitor and manage concentrated liquidity positions on AMM DEXs (LFJ/Trader Joe, etc.). Handles price fetching, range checking, efficiency metrics, and alert generation.
triggers:
  keywords: [lp monitor, liquidity position, concentrated liquidity, range check, avax lp, uniswap v3, lfj, trader joe]
  commands: [lp-status, check-range, lp-monitor, position-check]
  context: When monitoring DeFi LP positions or reporting portfolio health
platforms: [cli, telegram]
input_types:
  - Position tracker JSON
  - Pool address/chain
  - Range parameters (low, high)
output_types:
  - Status report (IN RANGE / EFFICIENCY LOW / OUT OF RANGE)
  - Position P&L breakdown
  - Rebalance recommendation
version: 1.0.0
last_updated: 2026-05-02
author: YoYo (Gentech Strategies)
---

# 🛡️ Crypto LP Position Monitoring — Gentech

**Class-level skill for monitoring concentrated liquidity positions across AMM DEXs.** Covers LFJ/Trader Joe AVAX/USDC primarily, with patterns applicable to Uniswap V3, Quickswap, etc.

## 📋 Quick Reference

### Core Position Files
```
Position tracker: ~/.hermes/scripts/.lfj-position-tracker.json
Range state:      ~/.hermes/scripts/.lfj-range-state.json
LP script:        /root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v2.py
Vault config:     /root/vaults/gentech/03-Strategies/cron-watchlist-config.md
```

### LFJ AVAX/USDC Pool Details
- **Pool address**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Chain**: Avalanche
- **Tokens**: WAVAX (`0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`), USDC (`0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`)
- **Target range** (per position tracker): `9.00 — 9.30` (Note: script default was `9.36-9.53` — tracker takes precedence)
- **Entry deposit** (per Jordan manual): `3.514 AVAX + $140.56 USDC = $173.04 total`

### Alert Conditions
- **🚨 OUT OF RANGE**: Price < low OR price > high → Immediate rebalance needed
- **⚠️ EFFICIENCY LOW**: Price within range but within 15% of either edge → Consider tightening/rebalancing before going out of range
- **✅ IN RANGE**: Price comfortably within range with >15% buffer to edges

## 🔄 Standard Workflow

### 1. Check Quiet Hours (Eastern Time)
The LP monitor script respects quiet hours:
- **Quiet start**: 23:00 (11 PM ET)
- **Quiet end**: 06:30 (6:30 AM ET)
- **Behavior during quiet hours**: Script returns `"QUIET_HOURS"` — no alerts sent, but still log locally
- **Override**: Use `--force` flag or call directly from analysis script outside cron schedule

### 2. Fetch Current Price (Priority Order)
1. **Birdeye x402 client** (if configured with API key) — enriched data with security scores
2. **DexScreener API** (free, no key) — `https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea`
3. **CoinGecko** — `https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd`
4. **Binance public API** — `https://api.binance.com/api/v3/ticker/24hr?symbol=AVAXUSDT` (fallback, no rate limits observed)

> **Fallback pattern**: If primary data source fails (HTTP 429, 403, timeout), immediately try next source. Log source used in position tracker `updated_by` field.

### 3. Read Position State
Position data lives in `~/.hermes/scripts/.lfj-position-tracker.json`:
```json
{
  "last_updated": "2026-04-28T17:46:24.063030+00:00",
  "updated_by": "jordan_manual",
  "actual_balance_usd": 135.09,
  "reported_by_cron_usd": 172.44,
  "discrepancy_usd": 37.35,
  "note": "Cron job computes position from initial deposit using CL math, not reading actual on-chain LP position. Real balance per Jordan: $135.09.",
  "position": {
    "range": { "low": 9.0, "high": 9.3 },
    "avax_price_at_update": 9.15
  },
  "entry": {
    "total_usd": 173.04,
    "avax": 3.514,
    "usdc": 140.56
  }
}
```

> **Critical**: The `actual_balance_usd` is the authoritative current value (from Jordan's manual entry). Cron's computed value often differs due to impermanent loss, fee accrual, and price movement. Report both but flag discrepancies > $20.

### 4. Calculate Position Metrics

#### Efficiency Calculation
```python
range_width = high - low
dist_to_edge = min(current_price - low, high - current_price)
efficiency_pct = (dist_to_edge / range_width) * 100
```
- **Efficiency ≥ 25%**: Healthy position
- **Efficiency 15–25%**: Caution zone (near edge)
- **Efficiency < 15%**: ⚠️ EFFICIENCY LOW — rebalance before going OOR

#### Impermanent Loss (IL) Forecast
Calculate IL at key price levels ($7, $8, $10, $12) using concentrated liquidity formula:
```python
# For constant product X * Y = K (simplified)
IL_pct = (2 * sqrt(P_current / P_entry) / (1 + P_current / P_entry) - 1) * 100
```

#### Rebalance Signal
Trigger when:
- Price within 5% of range edge (price < low×1.05 OR price > high×0.95)
- Efficiency < 50%
- Price moved >5% from entry since last update

### 5. Generate Report
Standard output format (cron delivery to Strategies group):
```
🛡️ LP STATUS (AVAX/USDC)
Range: 9.00–9.30 | Current: $9.08
Status: ✅ IN RANGE
Notes: $9.08 — comfortably positioned (efficiency 27%); entry value $173.04 → ~$135.09 current.

📊 Position Breakdown:
  Entry value: $173.04 (3.514 AVAX + $140.56 USDC)
  Current approx: $135.09 (actual balance)
  Discrepancy: $37.35 (IL + fees accrued)
  IL at $10: -3.2% | at $8: -1.8%
```

## 🚨 Alert Thresholds

| Condition | Alert Level | Action |
|-----------|------------|--------|
| Price < low OR > high | 🚨 OUT OF RANGE | Immediate rebalance required |
| Efficiency < 15% | ⚠️ EFFICIENCY LOW | Consider tightening range soon |
| Efficiency < 50% | ⚠️ REBALANCE SIGNAL | Plan DCA entry window |
| Value discrepancy > $50 | ⚠️ BALANCE MISMATCH | Verify on-chain position |
| AVAX moved >5% in 24h | 📊 PRICE SPIKE | Review IL exposure |

## 🔧 Data Source Priority & Fallback Chain

When fetching prices, use this exact order:

1. **Birdeye x402** (if `BIRDEYE_API_KEY` configured)
   - Endpoint: `overview` + `security` + `trade_data`
   - Pros: Enriched data (security scores, holder distribution)
   - Cons: Requires API key, occasional downtime

2. **DexScreener** (no key needed)
   - URL: `https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea`
   - Pros: Free, reliable, includes volume & liquidity
   - Cons: Slight delay (2-5 min), occasional Cloudflare blocks

3. **CoinGecko** (public)
   - URL: `https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd&include_24hr_change=true&include_7d_change=true`
   - Pros: No auth, full change history
   - Cons: Rate limited (10-30 req/min), HTTP 429 common

4. **Binance** (public spot API)
   - URL: `https://api.binance.com/api/v3/ticker/24hr?symbol=AVAXUSDT`
   - Pros: Extremely reliable, no rate limits, real-time
   - Cons: Only 24h change; need klines for 1h/7d

### Rate Limit Handling
- If HTTP 429 → exponential backoff: wait 2s → 4s → 8s → switch source
- If 403/404 → immediate source switch
- Log source fallback in `updated_by` field as `"binance_fallback"`, `"dexscreener_primary"`, etc.

## 📊 Calculating 1h and 7d Changes (Binance Method)

Binance ticker only gives 24h change. For 1h and 7d:

```python
# 1h change: get last 2 hourly klines
klines_1h = GET /api/v3/klines?symbol=AVAXUSDT&interval=1h&limit=2
prev_close = float(klines_1h[0][4])  # previous hour close
curr_close = float(klines_1h[1][4])  # most recent completed hour close
change_1h = ((curr_close - prev_close) / prev_close) * 100

# 7d change: get 8 daily klines (to cover full 7 days + current)
klines_7d = GET /api/v3/klines?symbol=AVAXUSDT&interval=1d&limit=8
week_ago_close = float(klines_7d[0][4])
today_close = float(klines_7d[-1][4])
change_7d = ((today_close - week_ago_close) / week_ago_close) * 100
```

## ⏰ Cron Schedule & Quiet Hours

The YoYo LP monitor cron (`faed4f588aef`) runs:
- **Schedule**: `15 8,12,16,20 * * *` → 8:15 AM, 12:15 PM, 4:15 PM, 8:15 PM ET
- **Quiet hours**: 11:00 PM – 6:30 AM ET (script outputs `"QUIET_HOURS"`, no Telegram delivery)
- **Silent run rule**: Only send report if LP is OUT OF RANGE, efficiency <50%, or AVAX moved >5% from entry

> **Note**: `lp-range-monitor-v2.py` checks `datetime.datetime.now(ET)` and returns early during quiet hours. The cron job still runs but suppresses delivery.

## 🧠 Integration with YoYo's Investment Reports

When building the combined Crypto Watchlist + LP Monitor report:

1. **Part 1**: Fetch all watchlist coin prices (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM)
   - Primary: Binance API (most reliable)
   - Compute 1h/7d from klines where not available
   - Format: `SYMBOL: $price (1h: X.X% | 24h: X.X% | 7d: X.X%) | Vol: N`

2. **Part 2**: Run LP monitor script
   ```bash
   cd /root/vaults/gentech/03-Strategies/scripts
   python3 lp-range-monitor-v2.py
   ```
   - If output = `"QUIET_HOURS"` → read position tracker manually, compute status inline
   - If output contains `"SILENT"` → still include 1-line LP status summary
   - If output contains `"ALERT"` or full report → include complete output

3. **Part 3** (triggered weekly or when AVAX >5% move):
   - IL forecast at $7, $8, $10, $12
   - Fee accumulation rate estimate (if APR known)
   - "Days to breakeven" calculation
   - Rebalance recommendation

## 📁 Vault File Conventions

All LP monitoring files live in `/root/vaults/gentech/03-Strategies/`:

| File | Purpose |
|------|---------|
| `cron-watchlist-config.md` | List of coins to monitor (editable by Jordan) |
| `token-watchlist.md` | Holdings table with target allocations |
| `LP-Monitor-Rules.md` | Alert thresholds, range rules, DCA windows |
| `scripts/lp-range-monitor-v2.py` | Main monitoring script (Birdeye + DexScreener) |
| `scripts/.lfj-position-tracker.json` | Current position state (auto-updated) |
| `scripts/.lfj-range-state.json` | Range boundaries and efficiency history |

> **Convention**: Files prefixed with `.` in scripts dir are runtime state, not versioned. Position tracker is manually updated by Jordan when on-chain balance changes.

## 🐛 Pitfalls & Troubleshooting

### Pitfall 1: Script Range vs Tracker Range Mismatch
- **Symptom**: LP monitor says "out of range" but manual check shows in range
- **Cause**: Script hardcoded `RANGE_LOW = 9.36, RANGE_HIGH = 9.53` but position tracker says `9.0-9.3`
- **Fix**: Always read range from `POSITION_FILE.position.range`, not script constants. Script needs patch to override its defaults with tracker values.
- **Workaround**: Manually compute status using tracker range and latest price.

### Pitfall 2: Birdeye x402 Client Import Failure
- **Symptom**: `ImportError: No module named 'birdeye_x402_client'`
- **Cause**: Birdeye client not installed or not in `sys.path`
- **Fix**: Script already has `try/except ImportError` — it falls back to DexScreener. Ensure fallback works by testing with `BIRDEYE_AVAILABLE = False`.
- **Verification**: Run `python3 lp-range-monitor-v2.py` — should output DexScreener data without errors.

### Pitfall 3: Quiet Hours Confusion
- **Symptom**: Cron job at 8:15 AM returns "QUIET_HOURS" unexpectedly
- **Cause**: System timezone vs ET mismatch. Script uses `datetime.datetime.now()` which is system local (likely UTC). QUIET_START=23, QUIET_END=6 are hardcoded as ET but compared to UTC → wrong window.
- **Fix**: Patch script to use `pytz` or `zoneinfo`:
  ```python
  from zoneinfo import ZoneInfo
  now_et = datetime.datetime.now(ZoneInfo("America/New_York"))
  hour_et = now_et.hour
  ```
- **Current state**: Script likely broken for ET quiet hours if system is UTC. Check with `date` command.

### Pitfall 4: Position Tracker Discrepancy Not Flagged
- **Symptom**: Cron reports computed value ($172.44) but actual balance is $135.09 — no alert sent
- **Cause**: Script compares computed value to entry, not to `actual_balance_usd` field. Discrepancy noted in file but ignored.
- **Fix**: When `discrepancy_usd > 20`, add warning to report: `"⚠️ BALANCE MISMATCH: Tracked $135.09 vs computed $172.44"`
- **Workaround**: Read `actual_balance_usd` directly from tracker and compare to `reported_by_cron_usd`.

### Pitfall 5: DexScreener Rate Limits
- **Symptom**: DexScreener occasionally returns 429 or empty data
- **Mitigation**: Already has try/except, but add retry with backoff. Consider caching pool address resolution.

## 📈 Extending to Other Pools/Chains

The script supports multiple chains via `CHAIN` and `POOL_ADDRESS` config. To add new pool:

1. Get pool address from LFG/Trader Joe UI or subgraph
2. Update constants:
   ```python
   POOL_ADDRESS = "0x..."  # new pool
   CHAIN = "avalanche" | "arbitrum" | "polygon" | ...
   RANGE_LOW = ...
   RANGE_HIGH = ...
   ```
3. Update position tracker file path convention: `~/.hermes/scripts/.{chain}-{token}-position.json`
4. Add watchlist entry in `cron-watchlist-config.md`

## 🧮 IL & Rebalance Math Reference

### Impermanent Loss Formula
For price ratio `r = P_current / P_entry`:
```
IL = (2 * sqrt(r) / (1 + r) - 1) * 100%
```
- r < 1 → loss (price went down)
- r > 1 → loss (price went up)
- r = 1 → 0% IL (best case for CL)

### Rebalance Timing
- **Full rebalance** when OOR: withdraw, reset range around current price, re-deposit
- **Tighten range** when efficiency < 15% but still in range: shift boundaries inward 10-20%
- **DCA entry** when efficiency < 50% and capital available: add funds to extend range or improve depth

## 🔄 Related Skills & Coordination

- **crypto-watchlist** — fetch watchlist prices; supply Part 1 of YoYo's report
- **defi-strategy** — LP position optimization, range adjustment strategies
- **hermes-cron** — cron job config, quiet hours, delivery routing
- **vault-navigation** — find/read vault files; locate position trackers

## 📝 Example: Full LP Monitor Call

```bash
# Full check with verbose output
python3 /root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v2.py --verbose

# Expected output during quiet hours (before 6:30 AM ET)
QUIET_HOURS

# Expected output during trading hours
{
  "source": "dexscreener",
  "price": 9.08,
  "range": {"low": 9.0, "high": 9.3},
  "status": "IN_RANGE",
  "efficiency_pct": 27.3,
  "position_value_usd": 135.09,
  "entry_value_usd": 173.04,
  "discrepancy_usd": 37.35,
  "il_at_10usd": -3.2,
  "il_at_8usd": -1.8,
  "recommendation": "HOLD — position healthy, no action needed"
}
```

## 🔄 Update History

- **2026-05-02** (v1.0.0): Initial skill capture based on YoYo LP monitoring session. Documented Birdeye x402 fallback, quiet hours bug (timezone), position tracker format, alert thresholds.