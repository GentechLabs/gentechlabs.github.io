# Change-Based Alert Suppression (Quiet-on-No-Change)

**Pattern**: Suppress periodic monitoring reports when metrics are stable.

**When to use**: Any cron job running every 5–60 minutes where the user only wants actionable updates, not routine "everything is fine" pings.

## User Preference

*"if nothing has changed to much, keep silent"* — Jordan, May 3, 2026

**Interpretation**: Do not send a report unless at least one material change occurred since the last report. This applies to all frequent monitoring jobs (D5 LP, watchlist scanners, price alerts).

## Change Types That Trigger a Report

| Change Type | Threshold | Notes |
|-------------|-----------|-------|
| Price move | ≥1% **or** ≥$0.20 absolute (whichever comes first) | For stable pairs, tighten to 0.5% / $0.10; for high-vol assets, loosen to 1.5% / $0.30 |
| Efficiency zone shift | Transition between buckets | `≥70% → 50–70% → 30–50% → <30%` |
| Range status flip | in-range ↔ out-of-range | Binary change |
| New alerts | Any debounced alert that just fired | Out-of-range confirmed, low-efficiency rebalance, milestone hit |
| Manual override | `force_send` flag set in state file | Emergency broadcast |

**First run**: Always sends (baseline establishment).

**Quiet hours**: Still respected — no reports during 23:00–06:00 ET regardless of changes.

## State Schema

Persisted between runs in `.lfj-d5-state.json` (or equivalent):

```json
{
  "last_price": 9.1223,
  "last_efficiency": 81.5,
  "last_in_range": true,
  "last_zone": "zone_70_plus",
  "last_check": "2026-05-03T16:50:34.738416-04:00",
  "force_send": false,
  "out_of_range_start": null,
  "efficiency_low_start": null,
  "last_alert_times": {}
}
```

**Critical**: `last_price`, `last_efficiency`, `last_in_range`, `last_zone` must be updated *only after* a report is sent (or silently skipped, to keep baseline current).

## Implementation Flow

```python
def main():
    if is_quiet_hours():
        sys.exit(0)

    # Fetch data, compute price, efficiency, in_range, alerts...

    state = load_state()

    # First run → always send
    if state.get("last_price") is None:
        should_send = True
        reason = "first run — establishing baseline"
    else:
        should_send, reason = significant_change_detected(
            state, price, efficiency, in_range, alerts
        )

    if not should_send and not alerts:
        # Silent path — update baseline and exit
        update_state_after_report(state, price, efficiency, in_range)
        sys.exit(0)

    # Generate and emit report
    report = format_report(...)
    print(report)
    update_state_after_report(state, price, efficiency, in_range)

    # Exit code semantics (unchanged)
    sys.exit(2 if alert_level == "HIGH" else 1 if alert_level == "MEDIUM" else 0)
```

**Key functions**:
- `within_zone(eff)` — returns bucket key string
- `significant_change_detected()` — evaluates all change thresholds, returns `(bool, reason_string)`
- `update_state_after_report()` — persists last_* fields and clears `force_send`

## Threshold Tuning Guide

| Pair Type | Suggested Price Threshold | Rationale |
|-----------|--------------------------|-----------|
| Stablecoin pair (USDC/DAI) | 0.5% / $0.10 | Low volatility; tighter catches meaningful depegs |
| Correlated assets (AVAX/USDC) | 1.0% / $0.20 | Mid-vol; balances sensitivity vs. chatter |
| High-vol altcoin | 1.5% / $0.30 | Prevents noise from daily swings |

**Store in config** if monitoring multiple pairs:
```json
{
  "monitoring": {
    "d5_lp": {
      "price_change_pct_min": 1.0,
      "price_change_abs_min": 0.20
    }
  }
}
```

## Emergency Override

**Purpose**: Send a report even if no thresholds triggered (e.g., user requests "send latest status now").

**Mechanism**: Set `state["force_send"] = True` from an external trigger (manual Telegram command, another cron job, handoff instruction).

**Auto-clear**: `force_send` resets to `False` after the next report (sent or silent-update).

## Date

2026-05-03 — Introduced with D5 Milestone script update (commit: quiet-on-no-change gate added).

## Related

- Main pattern in `strategies` SKILL: Section 6 "Change-Based Alert Suppression"
- Implementation: `/root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py`
- Ground truth protocol: `references/ground-truth-protocol.md` (state file consistency)
