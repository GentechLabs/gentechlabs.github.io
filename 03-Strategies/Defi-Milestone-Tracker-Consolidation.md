# DeFi Milestone Tracker — Consolidation Complete
**Owner:** Desmond (Creative) · DMOB (Code Review) · YoYo (Cron Ops)
**Status:** Draft — Awaiting Jordan Approval (see `00-HQ/Approvals/2026-05-02-defi-milestone-tracker-consolidation.md`)
**Date:** 2026-05-02
**Canonical Script:** `03-Strategies/scripts/defi-milestone-tracker.py`

---

## 🎯 What This Is

The **DeFi Milestone Tracker** is the single source of truth for Jordan's LFJ AVAX/USDC LP position + CMC portfolio watchlist. It replaces four overlapping cron jobs with one unified, smarter monitor.

**Runs:** 4× daily at 08:15, 12:15, 16:15, 20:15 ET
**Delivers to:** Strategies group (-1002916759037)
**Quiet hours:** 23:00–6:30 ET (silent)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Live Config** | Reads `.lfj-aae-config.json` (no more hardcoded $83.92 bugs) |
| **CMC Watchlist** | 7-coin portfolio (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM) |
| **LP Position** | Range, fee efficiency, P&L, impermanent loss |
| **Milestone Ladder** | Scout → Raider → Warlord → Sovereign → Freedom tiers |
| **5-min Escalation** | Breakout warning → red alert if still out after 5 min |
| **Edge Detection** | ≤30% efficiency = urgent rebalance recommendation |
| **Smart DCA** | 4 zones: Center (≥70% → $50) / Mid (50–70% → $30) / Low (30–50% → $20) / Edge (<30% → $10) |
| **Compound Alerts** | Notifies when cumulative fees hit thresholds |
| **Monday DCA** | Auto-reminder with efficiency-based amount |

---

## 📁 Files Changed

| Action | File | Note |
|--------|------|------|
| **NEW** | `03-Strategies/scripts/defi-milestone-tracker.py` | Canonical unified script |
| **ARCHIVE** | `lp-range-monitor-v2.py` → `lp-range-monitor-v2.py.archive-2026-05-02` | Old Birdeye-only version |
| **ARCHIVE** | `lp-range-monitor-v3.py` → `lp-range-monitor-v3.py.archive-2026-05-02` | Previous milestone tracker |
| **RETIRE** | Hermes job `1f10f10b2a07` | "CMC Crypto Watchlist" (errored) |
| **RETIRE** | Hermes job `915b1df66348` | "Crypto Watchlist" (redundant) |
| **RETIRE** | Hermes job `862ae0c1f85d` | "CMC Watchlist + Market News" (redundant) |
| **KEEP?** | Hermes job `8ae8a04f3b71` | 10-min LP Position Monitor — Jordan to decide |

---

## 🔧 How It Works

### Alert Logic

```
SILENT if:
  - Within range AND efficiency > 50% AND
  - No CMC moves ≥3% AND
  - Not Monday AND
  - No compound ready

ALERT if ANY:
  - CMC move ≥3%
  - Out of range
  - Efficiency ≤ 50%
  - Compound ready (> $50 cumulative)
  - Monday (DCA day)
  - Efficiency ≤ 30% (edge rebalance zone)
```

### Breakout Escalation

```
t+0 min  → Price crosses range bound → LIGHT WARNING ⚠️
t+5 min  → Still out of range? → RED ALERT 🔴
t+∞      → Back in range → RESET (all clear ✅)
```

### DCA by Zone (Curve shape)

```
Efficiency ≥70%  → Center zone  → $50 (full steam)
Efficiency 50–70% → Mid zone    → $30 (steady)
Efficiency 30–50% → Low zone    → $20 (edge watch)
Efficiency <30%   → Edge/crash  → $10 + URGENT rebalance
```

---

## 📊 Sample Output

```
🏆 DeFi Milestone Report — Monday, May 02 @ 08:15 AM EDT

📊 Full Watchlist:
• BTC:  $94,231.50 🟢 +2.4% | MC: 1.8T
• SOL:  $145.20    🔴 -1.2% | MC: 65.2B
...

💰 LP Position: AVAX/USDC (AVALANCHE)
• Price: $9.2740 🟢 +0.45% (24h)
• Range: $9.00 — $9.30 | Status: 🟩 IN RANGE
• Shape: CURVE | Efficiency: 82.3%
• Pool Vol (24h): $1,243,500 | TVL: $2.1M

💰 Revenue:
• Est. Daily Fees: $0.87
• Implied APR: 12.4%
• Cumulative: $42.50

📈 DeFi Milestone Ladder:
    ▶ Tier 3: Raider — $20.0/day ← CURRENT
       ▓▓▓▓▓▓░░░░░ 60% → Tier 4: Warlord
    ✅ Tier 2: Scout+ — $10.0/day (ACHIEVED)

🎯 Action Items:
📉 Shape-Aware DCA: 🟢 Center zone — full $50 DCA → $50 today
🏅 Position Healthy — Fee efficiency strong. Keep earning.

📊 Data: CMC + DexScreener | DeFi Milestone Tracker v1.0
```

---

## 🔄 State Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/.defi-milestone-state.json` | Primary state (last check, price, efficiency, alerts) |
| `~/.hermes/scripts/.lfj-milestone-tracker.json` | Read-only: legacy milestone history |
| `~/.hermes/scripts/.lfj-range-state.json` | Read-only: legacy range state (for migration) |

---

## ✅ Transition Checklist (post-approval)

**Performed by Desmond (Creative):**
- [ ] Document script feature set in vault (this doc)
- [ ] Update `03-Strategies/cron-jobs.md` manifest with new job details
- [ ] Archive old scripts with clear deprecation notices
- [ ] Announce in Strategies group (new DeFi Tracker live)

**Performed by YoYo (Ops):**
- [ ] Create Hermes cron job: `DeFi Milestone Tracker` → 08:15, 12:15, 16:15, 20:15 ET
- [ ] Remove jobs: `1f10f10b2a07`, `915b1df66348`, `862ae0c1f85d`
- [ ] Confirm: is `8ae8a04f3b71` (LP Position Monitor) kept or retired?
- [ ] Verify first run produces output, no errors

**Performed by DMOB (Code):**
- [ ] Review script logic (optional if code is straightforward)
- [ ] Confirm config loading from `.lfj-aae-config.json`
- [ ] Validate 30% edge threshold + DCA zones match Jordan spec
- [ ] Sign off on exit codes/ALERT prefixes

---

## 📋 Open Questions

1. **Should we keep the 10-min LP Position Monitor (`8ae8a04f3b71`) as fallback?** If DeFi tracker runs 4×/day, 10-min may be overkill. Jordan's rule: no duplication.
2. **Bid-ask spread integration:** Not yet implemented (would require order book API). If needed, add to "TODO" section.
3. **State migration:** Old state files (`.lfj-range-state.json`) remain for backward compatibility; new state is `.defi-milestone-state.json`. Can we clean up old state after 30 days?

---

*This document marks the Creative handoff. Script implementation ready for DMOB review, YoYo ops coordination, Jordan final approval.*
