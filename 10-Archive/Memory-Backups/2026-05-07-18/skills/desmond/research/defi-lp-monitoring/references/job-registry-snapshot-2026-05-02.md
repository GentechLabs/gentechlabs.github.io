# DeFi Monitoring Job Registry — Snapshot
**Date:** 2026-05-02  
**Agents:** DMOB, Desmond, YoYo  
**Pool:** LFJ AVAX/USDC (0x864d4e5ee7318e97483db7eb0912e09f161516ea)

## Active Jobs Monitoring This Pool

### DMOB Profile

| Job Name | Job ID | Schedule | Script | Last Run | Status |
|----------|--------|----------|--------|----------|--------|
| Defi Milestone | `3fc1a11a88d7` | Daily (1440m) | d5-master-cron.py | May 1 | ✅ ok |
| LP Range Monitor | `b2bb2bae4fc5` | Every 10 min | lp-range-monitor-v3.py | Apr 27 | ⚠️ Stale |
| Consolidated Crypto Watchlist | `3044d70c58bc` | Every 2h (6-18) | Prompt-based | May 2 | ✅ ok |

**Note:** Job `3fc1a11a88d7` is the authoritative source (uses `d5-master-cron.py` + `lp-aae-signal-monitor.py`).

---

### Desmond Profile

| Job Name | Job ID | Schedule | Script | Last Run | Status |
|----------|--------|----------|--------|----------|--------|
| YoYo — Crypto Watchlist + LP Monitor (Hardened) | `e00b46103b08` | 4× daily (8,12,16,20) | Prompt-based | May 2 | ✅ ok |
| YoYo — LP Position Monitor | `0b2beec3f702` | Every 10 min (6-23) | Manual scrape | May 2 | ✅ ok |
| CMC Watchlist + Market News | `862ae0c1f85d` | Every 2h | CMC + news | Apr 28 | ⚠️ Stale |
| YoYo — DeFi Dashboard | `66e224d2a6bd` | 3× daily (9,15,21) | Prompt-based | Apr 28 | ⚠️ Stale |

**Note:** These are **duplicates** of DMOB's functionality, running different prompts/scripts. Should be disabled after consolidation.

---

### YoYo Profile

| Job Name | Job ID | Schedule | Script | Last Run | Status |
|----------|--------|----------|--------|----------|--------|
| YoYo — Crypto Watchlist + LP Monitor | `faed4f588aef` | 4× daily (8,12,16,20) | Prompt-based | May 2 | ✅ ok |
| YoYo — DeFi Milestone + LP Monitor | `cfa8d1c19357` | Daily 14:10 | lp-range-monitor-v2.py | Apr 30 | ❌ error |

**Note:** Both jobs duplicate DMOB's `Defi Milestone` but with older scripts (`v2`, `v3`). Should consolidate to DMOB's version.

---

## Consolidation Target (Post-Cleanup)

After cleanup, ONLY these jobs should remain:

| Job Name | Owner | Job ID | Schedule | Reason |
|----------|-------|--------|----------|--------|
| Defi Milestone | DMOB | `3fc1a11a88d7` | Daily | Single source of truth for LP data |
| YoYo — Crypto Watchlist | YoYo | `faed4f588aef` | 4× daily | Price-only watchlist (no LP re-scrape) |
| Consolidated Crypto Watchlist | DMOB | `3044d70c58bc` | Every 2h | Alternative watchlist source |

All other LP-specific jobs should be **paused** or **removed**.

## How to Verify Consolidation

1. **Check active jobs:** `hermes cron list`
2. **Inspect outputs:** `ls ~/.hermes/profiles/*/cron/output/`
3. **Search for duplicate scripts:** `grep -r "lp-range-monitor\|d5-master" ~/.hermes/profiles/*/cron/`
4. **Confirm single state file writer:** `lsof ~/.hermes/scripts/.lfj-aae-state.json 2>/dev/null`

## Commands

```bash
# Pause a duplicate job (safe — preserves history)
hermes cron pause <job-id>

# Remove a job completely
hermes cron remove <job-id>

# Find all config file copies (after rebalance)
find /root/.hermes -name ".lfj-aae-config.json" 2>/dev/null

# Run the authoritative D5 cron manually
HOME=/root python3 /root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py

# Run the AAE signal monitor manually
HOME=/root python3 /root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py
```

## See Also

- `defi-lp-monitoring` skill — main monitoring patterns and pitfalls
- `/root/vaults/gentech/03-Strategies/LP-Monitor-Rules.md` — consolidated rules doc