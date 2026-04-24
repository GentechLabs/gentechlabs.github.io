# LP Monitor Rules — AVAX/USDC (Unified)

> Established: 2026-04-18
> Updated: 2026-04-21 — Unified with compound tracker
> Status: Active
> Pool: LFJ V2.2 AVAX/USDC (binStep 10, pool 0x864d4e5ee7318e97483db7eb0912e09f161516ea)

## Current Position

- **Range:** $9.10 — $9.65
- **Position:** ~$83.37 (3.88 AVAX + 46.82 USDC) — *last updated from screenshot 2026-04-24*
- **Shape:** Curve
- **Strategy:** Bear market accumulation — farm the bottom, compound rewards
- **Entry:** $83.92 (Mar 31, 3.762 AVAX + 48.37 USDC @ $9.4498/AVAX)

---

## Monitoring Rules (Jordan's Exact Spec)

### Rule 1 — Check Frequency
⏱️ Check **4× daily** via unified cron (`faed4f588aef` at 8:15, 12:15, 16:15, 20:15 UTC). Manual screenshot updates → immediate position file refresh.

### Rule 2 — In Range + High Efficiency → SILENT
🤫 Price in range AND fee efficiency **75–100%** → **no alert, stay silent** (compact log only)

### Rule 3 — In Range + Low Efficiency → ALERT
⚠️ Price in range BUT fee efficiency **< 75%** → alert: *"fee efficiency dropping"*

### Rule 4 — Out of Range → Confirm Then ALERT
⚠️ Price out of range → **wait 5 minutes** for confirmation, then alert if still out

### Rule 5 — Overnight Pause
🌙 **Pause at 11 PM**, resume at **6:30 AM** (EDT/EST). Handled by unified job quiet-hours logic.

### Rule 6 — Recovery Alert
🔔 When price returns to range after being out → alert with "recovered"

---

## Compound Tracker Rules

### Milestone Schedule
| # | Daily Fee Target | Status |
|---|-----------------|--------|
| 1 | $3/day | ✅ Current |
| 2 | $5/day | Next target |
| 3 | $8/day | |
| 4 | $10/day | |
| 5 | $15/day | |
| 6 | $20/day | |

### Rule C1 — Milestone Reached
🏆 When estimated daily fees cross a milestone → ALERT with new milestone

### Rule C2 — DCA Day Reminder
💰 **Monday** → Alert: "$50 DCA ready to deploy"

### Rule C3 — Compound Ready
🔄 When cumulative fees hit **$50 threshold** → ALERT: "Compound ready — reinvest + DCA"

### Rule C4 — Compound Report
📊 Every alert includes:
- Est. daily fees (from pool volume × position share)
- Cumulative fees earned
- Days in range
- Current milestone
- Days to next milestone
- DCA countdown
- Compound threshold progress

---

## Data Sources

- **Primary:** Birdeye x402 (if API key configured)
- **Fallback:** DexScreener (free, no key)
- **Position Data:** `~/.hermes/scripts/.lfj-position-tracker.json` (updated from Jordan screenshots)

## Fee Estimation Formula

```
daily_fees = pool_volume_24h × 0.0005 × (position_usd / pool_liquidity)
```

---

## Cron Jobs

| Job | ID | Schedule | Status |
|-----|----|----------|--------|
| **Crypto Watchlist + LP Monitor** (unified) | `faed4f588aef` | `15 8,12,16,20 * * *` | ✅ Active |
| ~~LP Unified Monitor (10min)~~ | ~~`00ef264dbdab`~~ | ~~`*/10 * * * *`~~ | ❌ Removed (unified into `faed4f588aef`) |
| ~~LP Monitor — Pause~~ | ~~`2f58ab69f4d2`~~ | ~~`0 23 * * *`~~ | ❌ Removed (quiet-hours logic in unified job) |
| ~~LP Monitor — Resume~~ | ~~`ef9aa51eedbc`~~ | ~~`30 6 * * *`~~ | ❌ Removed (quiet-hours logic in unified job) |

---

## Fee Efficiency Formula (Curve Shape)

```
position = (price - RANGE_LOW) / (RANGE_HIGH - RANGE_LOW)
fee_efficiency = (1 - abs(position - 0.5) * 2) * 100
```

- **Center (50%)** → 100% efficiency → SILENT
- **Edge (0% or 100%)** → 0% efficiency → ALERT

---

## Compound Strategy (Jordan's Vision)

**"Bear market accumulation play — farm the bottom, compound rewards"**

- LP generates fees in the $9.10-$9.65 range
- Compound weekly: reinvest accumulated fees + $50-100 DCA
- Target: $5/day → $20/day by July
- Each compound increases position → more fees → faster milestone progression

### Compound Checklist
1. ✅ LP in range, earning fees
2. ⬜ Accumulate $50+ in fees
3. ⬜ It's Monday (DCA day)
4. ⬜ Withdraw fees → swap to AVAX+USDC → re-deposit to LP
5. ⬜ Add $50-100 fresh capital (DCA)
6. ⬜ Log compound event in state file

---

## Related Files

- Script: `/root/vaults/gentech/03-Strategies/scripts/lp-unified-monitor.py`
- Synced to: `~/.hermes/scripts/lp-unified-monitor.py`
- State: `~/.hermes/scripts/.lfj-unified-state.json`
- Analysis: `/root/vaults/gentech/03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md`
- Watchlist: `/root/vaults/gentech/03-Strategies/token-watchlist.md`
