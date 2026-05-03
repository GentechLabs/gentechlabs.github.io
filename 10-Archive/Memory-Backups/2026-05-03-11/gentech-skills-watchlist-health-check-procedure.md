# Watchlist Health Check Procedure

## Quick Health Check (run manually)

### 1. Verify Recent Cron Output
```bash
# Check last 3 runs of YoYo's Crypto Watchlist + LP Monitor
ls -lt /root/.hermes/profiles/gentech/cron/output/*/2026-*/ | head -5
```

Look for:
- ✅ Files present with size > 1KB
- ✅ No "ERROR" or "Traceback" in filenames or content
- ✅ Recent timestamps (within last 4 hours for 4× daily schedule)

### 2. Test Script Execution Directly
```bash
cd /root/vaults/gentech/03-Strategies/scripts
python3 lp-aae-signal-monitor.py 2>&1 | head -50
```

Expected:
- JSON output or human-readable report
- Exit code 0
- No `NameError` or `ImportError`

### 3. Verify Data Source Connectivity
```bash
# Test DexScreener
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" | jq '.pairs[0].priceUsd'

# Test CoinGecko
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd" | jq
```

Both should return valid JSON with price data.

### 4. Check State File Freshness
```bash
ls -la ~/.hermes/scripts/.lfj-aae-state.json
ls -la ~/.hermes/scripts/.lfj-position-tracker.json
```

Last modified should be within last 4 hours for active monitoring.

---

## Common Failure modes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `NameError: EFFICIENCY_RED_THRESHOLD` | Constants crammed on one line with `\n` literals | Patch to separate lines |
| Empty output / SILENT | All conditions false (price in range, efficiency OK) | Expected when position healthy |
| "API rate limit" errors | CMC/DexScreener throttling | Add exponential backoff, switch to fallback source |
| No recent files in cron/output | Cron daemon stopped or job misconfigured | Check `hermes cron status`, restart agent |
| Telegram delivery failure | Chat ID changed or bot token revoked | Verify origin config, re-auth if needed |

---

## Recovery Checklist

- [ ] Restart Hermes agent if cron output stopped: `hermes restart`
- [ ] Patch broken constants in `lp-aae-signal-monitor.py`
- [ ] Verify `~/.hermes/scripts/.lfj-aae-config.json` exists and is valid JSON
- [ ] Test script manually → fix import errors (e.g., `birdeye_x402_client` missing)
- [ ] Check disk space on root partition (full disk kills cron writes)
- [ ] Review last 3 Telegram messages from bot — was there a delivery error?

---

## Monitoring Schedule Alignment

| Cron Job | Schedule ET | Expected Output |
|----------|-------------|-----------------|
| YoYo — Crypto Watchlist + LP Monitor | 08:15, 12:15, 16:15, 20:15 | 4× daily reports (unless silent) |
| YoYo — DeFi Milestone + LP Monitor | 14:10 daily | Milestone progress report |
| Gentech Watchdog | Every 5 minutes | Agent health ping (no LP data) |

Note: After 23:00 ET, quiet hours apply — scripts may return `"QUIET_HOURS"` intentionally.
