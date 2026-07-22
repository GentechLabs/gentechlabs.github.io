# DeFi Milestone Tracker — Architecture Diagram

## Before Consolidation (Duplication)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BEFORE — Cron Duplication Mess                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Job A: CMC Watchlist           Job B: LP + Milestone             │
│  ┌──────────────┐              ┌──────────────┐                  │
│  │ lp-range-    │              │ lp-range-    │                  │
│  │ monitor-     │              │ monitor-     │                  │
│  │ v2.py        │              │ v3.py        │                  │
│  └──────┬───────┘              └──────┬───────┘                  │
│         │                             │                           │
│         ▼                             ▼                           │
│  ⏰ Every 2h                        ⏰ Hourly                     │
│  📢 CMC-only alerts                📢 LP alerts                  │
│                                                                     │
│  Problems: Separate config, duplicated state, no CMC+LP unified  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## After Consolidation (Single Source of Truth)

```
                              ↓↓ CONSOLIDATION ↓↓

┌─────────────────────────────────────────────────────────────────────┐
│              AFTER — DeFi Milestone Tracker (Canonical)              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                  ┌─────────────────────────────┐                  │
│                  │ defi-milestone-tracker.py     │                  │
│                  │ (Single source of truth)    │                  │
│                  └─────────────┬───────────────┘                  │
│                                │                                  │
│               ┌────────────────┼────────────────┐                 │
│               ▼                ▼                ▼                 │
│         ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│         │ CMC      │    │ LP       │    │ Milestone│             │
│         │ Watchlist│   │ Position │    │ Tracker  │             │
│         └──────────┘    └──────────┘    └──────────┘             │
│               │                │                │                 │
│         Coins: BTC         Range: $9.00–     Tiers:              │
│                SOL             $9.30      Scout → Raider        │
│                LINK           Efficiency   Warlord → Freedom    │
│                AVAX           0–100%      Thresholds:          │
│                TAO                         $0.50 → $200/day    │
│                XAUt                                                   │
│                BEAM                                                   │
│                                                                     │
│  ⏰ Schedule: 08:15, 12:15, 16:15, 20:15 ET (4×/day)               │
│  📢 ALERT prefixes: ALERT: / MILESTONE:$ / STATUS:OK               │
│  🔄 Loads config from .lfj-aae-config.json (live)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────┐
│ .lfj-aae-   │ ← Live pool config (range, position, milestones)
│ config.json │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐     ┌──────────────┐
│ defi-milestone-       │────▶│ CMC Watchlist│ (fetches CMC API, checks ≥3% moves)
│ tracker.py          │     └──────┬───────┘
│                     │            │
│ 1. Loads config    │            ▼
│ 2. Fetches CMC     │     ┌──────────────┐
│ 3. Fetches DexScreener◀────│ LP Position  │ (price, range, fees, efficiency)
│ 4. Calculates      │     └──────┬───────┘
│ 5. Alerts if needed│            │
│ 6. Prints report   │            ▼
│                    │     ┌──────────────┐
└────────────────────┘     │ Milestone    │ (tier tracking, DCA zones)
       │                   │ Tracker      │
       │                   └──────┬───────┘
       ▼                          │
┌──────────────┐                 ▼
│ Exit code 0  │           ┌──────────────┐
│ (silent)     │           │ Alert Logic  │
│ Exit code 1  │           │ - Out of     │
│ (error)      │           │   range? →   │
│ ALERT prefix │           │ - Eff ≤30%?  │
│ MILESTONE    │           │ - CMC move?  │
│ STATUS:OK    │           └──────┬───────┘
└──────────────┘                  │
       │                          ▼
       │                ┌─────────────────────┐
       └────────────────▶│ Formatted Report    │
                         │ → Telegram/Slack    │
                         └─────────────────────┘
```

## State Persistence

```
~/.hermes/scripts/
├── .defi-milestone-state.json         ← Primary state (new)
│   {
│     "last_price": 9.274,
│     "last_efficiency": 82.3,
│     "alert_level": null,
│     "alert_direction": null,
│     "milestones_acknowledged": [5.0, 10.0],
│     "last_check": "08:15 EDT"
│   }
│
├── .lfj-milestone-tracker.json       ← Read-only (legacy, for migration)
├── .lfj-range-state.json             ← Read-only (legacy)
└── .lfj-aae-config.json              ← Read-only (live config)
```

## Cron Schedule Matrix

| Job Name | Old Schedule | New Schedule | Status |
|----------|-------------|--------------|--------|
| CMC Watchlist | Every 2h | — | 🗑️ Retiring |
| Crypto Watchlist | Every 2h | — | 🗑️ Retiring |
| CMC + Market News | Every 2h | — | 🗑️ Retiring |
| LP Position Monitor | Every 10 min | — | 🤔 Keep as fallback? |
| **DeFi Milestone Tracker** | — | **4×/day** | 🆕 New canonical |

## Alert Flowchart

```
                    ┌──────────────────┐
                    │  Fetch Data       │
                    │  (CMC + DexScr)   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Calc Efficiency │
                    │  Range Check      │
                    │  Tier Check       │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐           ┌──────▼──────┐
         │ Any CMC ≥3%?│           │ Out of      │
         │             │           │ Range?      │
         └──────┬──────┘           └──────┬──────┘
                │                         │
           (YES)│                         │(YES)
                │                         │
                ▼                         ▼
         ┌─────────────────────────────────────┐
         │         🚨 SEND ALERT               │
         │   (ALERT prefix + full report)      │
         └─────────────────────────────────────┘
                │
                ▼
         ┌──────────────────┐
         │  Check Efficiency│
         │  ≤ 30%?          │
         └────────┬─────────┘
                  │
              (YES)│
                  │
                  ▼
         ┌─────────────────────────────┐
         │ 🔴 REBALANCE URGENT         │
         │ Efficiency ≤ 30% (edge zone)│
         └─────────────────────────────┘

─────────────────────────────────────────────────────

Silent Path:
  In range AND eff > 50% AND no CMC moves → STATUS:OK → Exit 0
```

---

*Creative deliverable — Desmond, 2026-05-02*
