# LFJ Position Tracker Format — Reference

## File Location
```
~/.hermes/scripts/.lfj-position-tracker.json
```

## JSON Schema

```json
{
  "last_updated": "ISO 8601 timestamp (UTC)",
  "updated_by": "who_last_modified (jordan_manual | cron | auto)",
  "actual_balance_usd": float,       // Authoritative value from on-chain / manual entry
  "reported_by_cron_usd": float,     // Computed value from CL math
  "discrepancy_usd": float,          // actual_balance_usd - reported_by_cron_usd (can be negative)
  "note": "free-text explanation of discrepancy or special conditions",
  "position": {
    "range": {
      "low": float,                   // Lower bound of concentrated liquidity range
      "high": float                  // Upper bound
    },
    "avax_price_at_update": float    // Price when position state was last calculated
  },
  "entry": {
    "total_usd": float,              // Initial USD value deposited
    "avax": float,                   // AVAX quantity deposited
    "usdc": float                    // USDC quantity deposited
  }
}
```

## Example (Current as of 2026-04-28)

```json
{
  "last_updated": "2026-04-28T17:46:24.063030+00:00",
  "updated_by": "jordan_manual",
  "actual_balance_usd": 135.09,
  "reported_by_cron_usd": 172.44,
  "discrepancy_usd": 37.35,
  "note": "Cron job computes position from initial deposit (3.514 AVAX + $140.56 USDC) using CL math, not reading actual on-chain LP position. Real balance per Jordan: $135.09.",
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

## Field Semantics

- `actual_balance_usd`: **Trust this.** Manually updated by Jordan based on on-chain portfolio tracker (Zapper, DeBank, or direct contract read). Reflects real-time LP value including IL and accrued fees.
- `reported_by_cron_usd`: Computed by the LP monitor script using concentrated liquidity formulas assuming no IL or fees. Useful for theoretical comparison.
- `discrepancy_usd`: Positive → actual < computed (loss, likely IL). Negative → actual > computed (gain, likely fee accumulation).
- `updated_by`: Tracks source of position state update. Values:
  - `jordan_manual`: Jordan manually updated based on on-chain check
  - `cron`: Automatic update from LP monitor script
  - `auto`: Automated via bot/script
- `position.range`: **This is the canonical range**. Overrides any hardcoded ranges in the LP monitor script.
- `avax_price_at_update`: Price of AVAX at the moment position was recorded. Useful for IL calculation at that snapshot.

## Update Protocol

### When to Update
- **Daily** during market hours if LP is active
- **Immediately** after any manual rebalance (withdraw + redeposit)
- **Weekly** during quiet periods

### How to Update (Manual)
```bash
# Edit the tracker file
nano ~/.hermes/scripts/.lfj-position-tracker.json

# Update these fields:
1. last_updated = current ISO timestamp (use: date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
2. updated_by = "jordan_manual"
3. actual_balance_usd = [read from on-chain portfolio aggregator, e.g., $135.09]
4. discrepancy_usd = actual_balance_usd - reported_by_cron_usd (recompute)
5. position.avax_price_at_update = [current AVAX price from Binance/CG]

# Leave entry fields unchanged (historical record)
```

### How to Update (Cron-Automated)

The LP monitor script (`lp-range-monitor-v2.py`) can auto-update if configured:

```python
# Inside script, after fetching current price and computing position:
new_state = {
    "last_updated": datetime.utcnow().isoformat() + "Z",
    "updated_by": "cron",
    "actual_balance_usd": current_onchain_value,    # ← Requires on-chain read (hard)
    "reported_by_cron_usd": computed_theoretical_value,
    "discrepancy_usd": discrepancy,
    "position": {
        "range": {"low": RANGE_LOW, "high": RANGE_HIGH},
        "avax_price_at_update": current_price
    },
    "entry": TRACKED_ENTRY  # Preserve from previous
}
with open(POSITION_FILE, 'w') as f:
    json.dump(new_state, f, indent=2)
```

> **Current limitation**: Script cannot read on-chain balance directly. `actual_balance_usd` must be manually entered or fetched from external portfolio API (not implemented). Current workflow: Jordan manually updates every few days.

## Interpretation Guide

### Healthy Position
- `discrepancy_usd` between -$20 and +$20 (close to theoretical)
- `actual_balance_usd` ≈ `reported_by_cron_usd` → IL minimal, fees roughly offset
- `efficiency_pct` (computed separately) > 25%

### IL Accumulation
- `discrepancy_usd` large negative (e.g., -$37.35) → actual value below theoretical
- Likely cause: price moved away from entry, causing impermanent loss
- Check IL at current price using formula in crypto-lp-monitoring skill

### Fee Accumulation
- `discrepancy_usd` large positive → actual value above theoretical
- Indicates fees earned > IL loss. Good sign.
- Verify by checking pool's fee accumulation history on LFJ explorer.

### Out-of-Range Detection
- Compare `position.avax_price_at_update` vs current price from API:
  - If current price < `position.range.low` → OOR low
  - If current price > `position.range.high` → OOR high
  - If within → in range but check efficiency

### Range Drift
- If `position.range` hasn't been updated in >7 days while price moved >10%, consider recentering range around current price.
- Update `range.low` and `range.high` to new symmetric or asymmetric bounds based on conviction.

## Cross-Check With Other Sources

1. **LFJ Explorer**: Verify on-chain position directly
   - URL: `https://traderjoexyz.com/avalanche/pool/0x864d4e5ee7318e97483db7eb0912e09f161516ea`
   - Connect wallet, check your liquidity position

2. **Birdeye Position Tracker** (if API key):
   - `GET /v1/wallet/{wallet_address}/positions?chain=avalanche`
   - Confirms token balances and LP value

3. **DeBank / Zapper**: Aggregate portfolio view across chains
   - Quick USD valuation of all positions

## File Format Evolution

- **v1** (2026-04-20): Initial format — entry, position, computed values
- **v1.1** (2026-04-28): Added `actual_balance_usd` field (Jordan manual entry), `discrepancy_usd`, `updated_by`
- **Future**: May add `fee_accrued_usd`, `il_usd`, `last_rebalance_timestamp`

## Related Files
- `~/.hermes/scripts/.lfj-range-state.json` — historical efficiency tracking (if implemented)
- `/root/vaults/gentech/03-Strategies/LP-Monitor-Rules.md` — threshold definitions
