# D5 Consolidation Case Study (2026-05-02)

## Problem

Two separate cron jobs were running overlapping LP monitoring logic:

1. **Crypto Watchlist + LP Monitor** — `lp-range-monitor-v2.py`, 4× daily
2. **DeFi Milestone + LP Monitor** — `lp-range-monitor-v2.py`, daily at 14:10

Both hit the same pool data, triggered similar alerts, and created redundant Telegram messages. No single source of truth for state.

## Solution Architecture

Adopted a **config-driven, stateful, unified tracker** built on `d5-lp-consolidated.py` with three integrated modules:

```
d5-milestone-tracker.py
├── CMC Watchlist       (7 assets, daily reset state)
├── LP Position Monitor (DexScreener, 5min debounce)
├── Milestone Ladder    (tier estimation from daily fees)
└── DCA Strategy Engine (zone-based sizing)
```

All state lives in `$HERMES_HOME/home/.hermes/scripts/` via `hermes_path()`.

## Key Files

| File | Purpose |
|------|---------|
| `.lfj-aae-config.json` | Position range, milestones (tiers 1–4, $5→$100), DCA params, quiet hours (23–6 ET), alert rules |
| `.d5-lp-state.json` | `out_of_range_start`, `efficiency_low_start`, `last_alert_times`, `last_price`, `last_check`, `current_milestone_idx` |
| `.cmc-watchlist-state.json` | `date`, `last_prices` (per-coin) — reset daily |
| `.lfj-position-tracker.json` | `entry_avax_price`, `entry_timestamp` — for IL calculation |

## Behavior

### Price Efficiency Zones (Shape-Aware)

| Fee Efficiency | Status | DCA Action |
|----------------|--------|------------|
| ≥50% | 🟢 OK | Base amount ($50) |
| 30–50% | 🟡 WARN | Boost amount (+$15) |
| <30% | 🔴 CRITICAL | Rebalance suggestion + optional DCA |

**Shape adjustments** (`cfg["position"]["shape"]`):
- `curve` → range suggestion: `f"${new_low:.2f} – ${new_high:.2f} (shift up; price above range)"`
- `spot` / `bidirectional` → range suggestion: `f"${range_low:.2f} – ${range_high:.2f} (current is fine; check shape balance)"`

### Breakout Confirmation (5-minute Debounce)

When price leaves `[range_low, range_high]`:
1. Record `out_of_range_start = now_ts()` if not set
2. On subsequent runs: if `now - out_of_range_start ≥ 300s`, trigger HIGH alert
3. If price returns to range before debounce elapses, clear `out_of_range_start` (silent recovery)

Same logic for `efficiency_low_start` when efficiency < 30%.

### Milestone Ladder

Milestones pulled from config `cfg["milestones"]`. Current tier computed from estimated daily fees:

```python
def get_current_tier(est_fees, milestones):
    if est_fees < milestones[0]["daily_fees"]: return -1  # Unranked
    for i, ms in enumerate(milestones):
        if est_fees < ms["daily_fees"]: return i - 1
    return len(milestones) - 1  # Max tier
```

`milestone_changed = current_idx > previous_idx` → triggers milestone promotion alert.

### CMC Watchlist

Assets: `BTC`, `SOL`, `LINK`, `AVAX`, `TAO`, `XAUt`, `BEAM` (CoinMarketCap IDs hardcoded).

Daily reset logic: if `state["date"] != today`, clear `last_prices`. On each run:
- Fetch current price
- If previous price exists and `abs(pct_change) ≥ 5%`, trigger MEDIUM alert (overrides quiet hours)
- Store current price as new `last_price`

## Exit Codes

| Code | Meaning | Trigger |
|------|---------|---------|
| 0 | OK | In range, efficiency OK, no CMC moves |
| 1 | MEDIUM | CMC asset moved ≥5%, or LP alert LOW/MEDIUM |
| 2 | HIGH | Breakout confirmed OR efficiency <30% confirmed |

Cron should capture stderr/stdout to log file. Telegram message always sent regardless of exit code (report is stdout).

## Cron Consolidation Steps (Reference)

1. **Audit**: `grep -r "lp-range-monitor" 00-System/agent-profiles/yoyo/cron/` — found 2 jobs
2. **Choose base**: `d5-lp-consolidated.py` (already config-driven, debounce, quiet hours)
3. **Merge features**:
   - Copied `COINS`, `fetch_cmc()`, `build_watchlist()` from `cmc-watchlist.py`
   - Added `milestones = cfg.get("milestones", [])` and tier logic from `lp-aae-signal-monitor.py`
   - Extended `format_report()` to include CMC and Milestone sections
   - Modified `main()` to call CMC first, merge alerts, compute `daily_fees_est`
4. **Path fix**: Replaced `os.path.expanduser("~")` with `hermes_path()`; state stored in `/root/.hermes/profiles/yoyo/home/.hermes/scripts/`
5. **Archive**: Backed up original jobs + scripts to `10-Archive/cron-consolidation-2026-05-02/`
6. **Update `jobs.json`**: (pending final rename)
   - Remove IDs: `faed4f588aef`, `cfa8d1c19357`
   - Keep single job pointing to `d5-milestone-tracker.py`
7. **Test**: (pending live run with real API data)

## Open Questions

- **Script location**: Should final script live in vault (`03-Strategies/scripts/`) or Hermes profile (`~/.hermes/scripts/`)? Current design: vault (version-controlled), cron executes from vault path (verify).
- **Fee estimation**: `est_daily_fees` placeholder — actual calculation requires 24h volume and pool fee tier. Implement with: `(volume_24h * fee_tier_bps / 1e6) * (our_liquidity / pool_tvl)`.
- **Bid-ask detection**: Not yet implemented in `check_alerts()` — requires order book data (Birdeye?). Defer to v2.

## Validation Checklist

Before declaring victory:
- [ ] Rename `d5-milestone-tracker.py.tmp` → `d5-milestone-tracker.py`
- [ ] Run manually: `python3 d5-milestone-tracker.py` → no exceptions, Telegram message posts
- [ ] Verify CMC prices fetch for all 7 coins
- [ ] Trigger a breakout (move price outside range) and confirm alert after 5 minutes
- [ ] Check state file updates (timestamps increment)
- [ ] Update `jobs.json` to remove duplicates and point to new script
- [ ] Restart Hermes gateway: `hermes gateway restart`
- [ ] Wait for next scheduled run, verify single Telegram report
- [ ] Monitor for 24h to confirm no duplicate alerts

## Related Documentation

- `strategies` skill (core patterns): debounce, config-driven architecture, milestone ladder, CMC integration
- `hermes-agent` skill (path resolution, cron management)
- `D5-Milestone-Tracker-Consolidation.md` — detailed changelog (vault)
