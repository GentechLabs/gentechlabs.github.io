# Vault Data Sources for LP Position Tracking

## Primary Data Files

### Daily Vault Entries (`08-Daily/*.md`)
- Contains narrative summaries with position values extracted from `lp-position-reader.py`
- Look for patterns:
  - `Position value (on-chain)` → `$XXX.XX`
  - `Balance:` with dollar amount
  - `Efficiency:` percentage
  - `IL:` impermanent loss

### Strategy Documents (`03-Strategies/*.md`)
- `hybrid-lp-spot-strategy.md`: Baseline position composition
- `D5-Milestone-Tracker-Consolidation.md`: Milestone definitions and cron behavior
- HTML trackers are **templates**, not live data sources

## Ground Truth Sources (in priority order)

1. **`lp-position-reader.py`** output (on-chain decoded)
   - Provides: position value, token balances, active bin, efficiency
   - This is the authoritative source for vault Balance field

2. **`d5-master-cron.py`** (for watchlist prices, pool volume only)
   - Does **not** include pending DCA injections
   - Use only for market context, not position valuation

3. **`d5-milestone-summary.py`** (narrative only)
   - Do not trust numeric values from this script

## JSON State Files
- `~/.hermes/scripts/.lfj-position-tracker.json` — entry price, IL tracking
- `~/.hermes/scripts/.d5-milestone-state.json` — last check, price, efficiency, alerts
- **Warning**: State files may be duplicated across profiles; ensure all scripts read same location or use symlinks.

## Extraction Patterns (Python regex)
```python
pos_value = re.search(r'position value.*?\$(\d+\.\d+)', content, re.IGNORECASE)
balance = re.search(r'Balance:.*?\$(\d+\.\d+)', content, re.IGNORECASE)
efficiency = re.search(r'Efficiency.*?(\d+\.\d+)%?', content, re.IGNORECASE)
apr = re.search(r'APR.*?(\d+\.?\d*)%?', content, re.IGNORECASE)
fees = re.search(r'Fees.*?\$(\d+\.\d+)', content, re.IGNORECASE)
```

## Last Verified Values (May 3, 2026)
- Position: $135.82 (6.169 AVAX + 78.22 USDC)
- Efficiency: 38.2%
- IL: -17.65%
- APR: ~79% (inferred from 3-day growth)
- Daily fees: ~$0.11

*These values are superseded by live `lp-position-reader.py` output.*