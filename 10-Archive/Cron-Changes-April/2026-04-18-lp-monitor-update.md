# LP Monitor — Cron Job Update
**Date:** April 18, 2026 (updated 5:47 PM EDT)
**Job ID:** `92df40e6e9bb`
**Changed by:** Jordan (voice request)
**Status:** ✅ Active

## What Changed
- **Range:** Updated to **$9.30–$9.50 curve** (was 9.66–9.95)
- **Script:** Updated `lpj-range-check.py` with new RANGE_LOW/RANGE_HIGH
- **State file:** Cleared (fresh start)
- **Memory:** Updated

## Alert Rules
| Condition | Action |
|-----------|--------|
| In range + fee efficiency 75-100% | 🔇 Silent |
| In range + fee efficiency <75% | ⚠️ Alert: "fee efficiency dropping" |
| Out of range <5 min | 🔇 Wait for confirmation |
| Out of range 5+ min | 🚨 Alert: consider rebalancing |

## Supporting Jobs
| Job | ID | Schedule | Purpose |
|-----|----|----------|---------|
| LP Range Monitor | `92df40e6e9bb` | `*/10 * * * *` | Main monitor |
| Pause (11 PM) | `2f58ab69f4d2` | `0 23 * * *` | Silence overnight |
| Resume (6:30 AM) | `ef9aa51eedbc` | `30 6 * * *` | Morning restart |

## Pool Details
- Pool: AVAX/USDC LFJ V2.2 (`0x864d4e5ee7318e97483db7eb0912e09f161516ea`)
- Bin Step: 10 (0.1%)
- Shape: Curve
- Range bins: 8363194–8363216 (22 bins)
- Current price: ~$9.41

## Notes
- CoinMC Watchlist (separate job) unchanged — every 2 hours
- Jordan wants cron changes always synced to Second Brain
