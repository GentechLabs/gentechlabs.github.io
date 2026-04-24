# DMOB Audit: LP + Watchlist Cron Consolidation

**Date:** 2026-04-21 18:42 EDT
**Requested by:** Jordan (replying to YoYo's LP tracker analysis)

## Findings

### Active Cron Jobs (from my profile)
None of the following exist in the active cron list:
- `e030307a1a47` (consolidated watchlist) — **MISSING**
- `c2c2e40b440e` (LP Fee Efficiency Monitor) — **MISSING**
- `b2bb2bae4fc5` (old LP range monitor) — **MISSING**

### Scripts Found
| Script | Location | Status |
|--------|----------|--------|
| `lp-range-monitor.py` (v1) | `~/.hermes/scripts/` + vault `03-Strategies/scripts/` | ✅ Exists, DexScreener only |
| `lp-range-monitor-v2.py` | vault `03-Strategies/scripts/` | ✅ Exists, Birdeye + DexScreener |
| `crypto-watchlist.py` | NOT FOUND anywhere | ❌ Missing |

### Discrepancies
- `Cron-Jobs-Reference.md` references job `e030307a1a47` and script `crypto-watchlist.py` but neither exist
- `LP-Monitor-Rules.md` references range 9.30–9.50 but v2 script uses 9.10–9.65
- Green Room handoff says "no code changes needed" but the consolidated script doesn't exist

### Pool Address (from Jordan)
`0x864d4e5ee7318e97483db7eb0912e09f161516ea` — LFJ AVAX/USDC 5bps

## Action
Pinged YoYo in Strategies group to confirm his cron state and whether `crypto-watchlist.py` exists in his profile. Waiting for confirmation before building consolidated script.
