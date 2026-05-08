# Output Samples — Reference for Pattern Matching

This directory stores representative stdout from each LFJ monitoring script. Use these to:
- Recognize which script produced which output format
- Debug when output structure changes
- Validate new runs against known-good baselines

## Files

- `d5-milestone-summary-2026-05-02.md` — human-readable markdown report (executive summary)
- `lp-aae-signal-monitor-2026-05-02.json` — structured JSON signal with tier, efficiency, action
- `d5-master-cron-2026-05-02.md` — consolidated watchlist + LP + DCA zone
- `lfj_monitor-2026-05-02.json` — DexScreener price + wallet balances (JSON)
- `lp-position-reader-sample.json` — on-chain bin-level position decode (JSON)

---

## Format Quick Reference

### d5-milestone-summary.py
```
🏆 **D5 Milestone Report** — Saturday, May 02, 2026

**AVAX/USDC — AVALANCHE**
• Price: $9.1132 🟢 +0.10% (24h)
• Range: $9.0 — $9.45 | Status: 🟩 In Range
• Shape: CURVE | Efficiency: 50.3%
• Pool Vol (24h): $2,521,987 | TVL: $3,903,048

💰 **Revenue Summary**
• Est. Daily Fees: $0.03
• Implied APR: 13.0%
• Cumulative Fees: $0.00
• Days in Range: 0.0

📈 **D5 Milestone Ladder**
    **▶ Tier 1: Scout — $5.0/day ← CURRENT**
       ░░░░░░░░░░ 0.0% → Tier 2: Raider
    ⬜ Tier 2: Raider — $20.0/day
    ⬜ Tier 3: Warlord — $55.0/day
    ⬜ Tier 4: Sovereign — $200.0/day

🎯 **Action Items**
✅ **No Micro-DCA** — no bonus DCA, still earning
```
*(Note: Tier label shows $5 but AAE config says $3 — known inconsistency)*

---

### lp-aae-signal-monitor.py (JSON)
```json
{
  "status": "LOW",
  "signal": {
    "timestamp": "2026-05-02T06:23:20.886139-04:00",
    "signal_type": "POSITION",
    "severity": "LOW",
    "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    "chain": "avalanche",
    "price": 9.1132,
    "in_range": true,
    "fee_efficiency": 50.3,
    "current_tier": 0,
    "current_tier_label": "Unranked",
    "next_tier": 1,
    "next_tier_label": "Scout",
    "progress_to_next_pct": 1.5,
    "fees_24h": 0.04,
    "apr": 11.8,
    "suggested_action": "Consider rebalancing — efficiency at 50.3%."
  }
}
```

**Key field mapping**:
| JSON Path | Meaning | Threshold |
|-----------|---------|-----------|
| `signal.fee_efficiency` | Capital efficiency % | <50% = DCA boost |
| `signal.current_tier` | 0=Unranked, 1=Scout, … | Increases as fees grow |
| `signal.progress_to_next_pct` | % to next milestone | When ≥100%, tier increments |
| `signal.suggested_action` | Recommended next step | Human-readable |

---

### d5-master-cron.py
```
🏆 **D5 Master Report** — Saturday, May 02 @ 06:22 AM EDT

🚨 **Watchlist Alerts (|24h| ≥ 3%):**
• **TAO**: $272.85 🟢 +4.0%

📊 **Full Watchlist:**
• **BTC**: $78,277.92 🟢 +1.3% | MC: $1567.4B
...
💰 **LP Position: AVAX/USDC (AVALANCHE)**
• Price: $9.1132 🟢 +0.20% (24h)
• Range: $8.9500 — $9.3600 | Status: 🟩
• Shape: CURVE | Efficiency: **79.6%**
...
📈 **D5 Milestone Ladder:**
    **▶ Tier 1: Scout — $5.0/day ← CURRENT**
...
🎯 **Action Items:**
📉 **Shape-Aware DCA**: 🟢 Center zone — full $50 DCA
🏅 **Position Healthy** — Keep earning. Efficiency is strong.
...
💡 **Strategy**: Bear market accumulation — farm the bottom, compound rewards.
```
*(Note: Efficiency 79.6% vs 50.3% in AAE — known inconsistency)*

---

### lfj_monitor.py (JSON)
```json
{
  "time": "2026-05-02 10:22 UTC",
  "source": "DexScreener (LFJ pool)",
  "avax_usdc_price": 9.11,
  "in_range": true,
  "range": "8.95–9.36",
  "alert": "NONE",
  "lfj_metrics": {
    "fee_earnings_24h": 0.6528,
    "deposit_balance": {"avax": 6.719, "usdc": 73.58, "total_usd": 135.0}
  },
  "volume_24h": "$2,526,867",
  "liquidity": "$3,903,048",
  "wallet": {"avax_balance": 0.0969, "usdc_balance": 0.0}
}
```
**Note**: `fee_earnings_24h` here is hardcoded stub; `volume_24h` is real from DexScreener.

---

## Change Detection (What Constitutes "New")

When comparing today's output to yesterday's sample, flag if:
- `signal.fee_efficiency` changes by ≥5 percentage points
- `signal.current_tier` increments
- `signal.suggested_action` text changes (not just "No change")
- Price exits `[target_low, target_high]` band
- `lp_monitor.alert` changes from `NONE` to `YELLOW/RED`

Otherwise, mark as `[SILENT]`.

---

## Related Files

- `../state-file-schemas.md` — JSON schemas for position state, milestone tracker, efficiency trend
- `../milestone-ladder-current.md` — authoritative milestone definitions ( reconciled source)