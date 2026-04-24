# LP + Milestone Tracker Rules — AVAX/USDC

> Established: 2026-04-18
> Updated: 2026-04-24 — Split from Crypto Watchlist. LP + Milestone now consolidated standalone.
> Status: Active
> Pool: LFJ V2.2 AVAX/USDC (binStep 10, pool 0x864d4e5ee7318e97483db7eb0912e09f161516ea)

## Current Position

- **Range:** $9.31 — $9.53 (rebalanced Apr 24)
- **Position:** ~$83.37 (3.88 AVAX + $46.82 USDC)
- **Shape:** Curve
- **Strategy:** Bear market accumulation — farm the bottom, compound rewards

---

## Monitoring Rules (Jordan's Exact Spec)

### Rule 1 — Check Frequency
⏱️ Check every **10 minutes** (cron runs 4x/day: 8:15, 12:15, 16:15, 20:15 UTC)

### Rule 2 — In Range + High Efficiency → SILENT
🤫 Price in range AND fee efficiency **75–100%** → **no alert, stay silent** (compact log only)

### Rule 3 — In Range + Low Efficiency → ALERT
⚠️ Price in range BUT fee efficiency **< 75%** → alert: *"fee efficiency dropping — consider rebalancing"*

### Rule 4 — Out of Range → Confirm Then ALERT
⚠️ Price out of range → **wait 5 minutes** for confirmation, then alert if still out

### Rule 5 — Overnight Pause
🌙 **Pause at 11 PM**, resume at **6:30 AM** (EDT/EST)

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

## Fee Estimation Formula

```
daily_fees = pool_volume_24h × 0.0005 × (position_usd / pool_liquidity)
```

---

## Cron Jobs

| Job | ID | Schedule |
|-----|----|----------|
| LP + Milestone Tracker | `0c8debb70799` | `15 8,12,16,20 * * *` |
| LP Monitor — Pause (11 PM) | `a5a8aa5c64db` | `0 23 * * *` |
| LP Monitor — Resume (6:30 AM) | `390536c113fb` | `30 6 * * *` |

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

- LP generates fees in the $9.31-$9.53 range
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

- Script: `/root/vaults/gentech/03-Strategies/scripts/lp-milestone-monitor.py`
- Synced to: `~/.hermes/scripts/lp-milestone-monitor.py`
- State: `~/.hermes/scripts/.lfj-lp-milestone-state.json`
- Analysis: `/root/vaults/gentech/03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md`
- Crypto Watchlist (standalone): `/root/vaults/gentech/03-Strategies/token-watchlist.md`
