# YoYo — DeFi Milestone + LP Cron Optimization

**Date:** 2026-04-25
**Agent:** YoYo (Strategies)
**Status:** ✅ Complete

## What Changed

### 1. New AAE LP Monitor Script
- **File:** `~/.hermes/scripts/lp-aae-monitor.py`
- **Aligns with:** AAE signal spec (Scout/Raider/Warlord/Sovereign tiers)
- **Reads:** `.lfj-aae-config.json` (milestones, thresholds, DCA rules)
- **Reads:** `.lfj-position-tracker.json` (position, range, entry data)
- **Writes:** `.lfj-aae-state.json` (cumulative tracking, milestone progress)

**Features:**
- Range monitoring + fee efficiency
- AAE tiered milestone tracking ($5 → $20 → $55 → $200/day)
- Days-to-next-milestone estimation
- Compound readiness alerts ($50 threshold)
- DCA schedule (Sundays, $50)
- IL calculation + vs-HODL comparison
- Intelligent silent logic (only alerts on action needed)

### 2. Cron Job Restructure

| Job | ID | Schedule | Change |
|-----|-----|----------|--------|
| **AAE DeFi Milestone + LP Monitor** | `faed4f588aef` | Daily 10:00 AM ET | Was 4×/day. Now single daily run with full milestone analysis. |
| **Crypto Watchlist** | `bce87f59b79e` | 8:15, 12:15, 16:15, 20:15 ET | Was hourly. Reduced API load by ~80%. |

**Delivery:** Both to Strategies group (`telegram:-1002916759037`)

### 3. Milestone Alignment
- Old script used hardcoded `$3/$5/$8/$10/$15/$20` labels
- New script reads from AAE config: **Scout ($5) → Raider ($20) → Warlord ($55) → Sovereign ($200)**
- Current position (~$0.21/day) = pre-Scout (Tier 0)

### 4. State Files
- `.lfj-aae-state.json` — newly populated with tracking data
- `.lfj-unified-state.json` — deprecated (old format)
- `.lfj-position-tracker.json` — unchanged, still source of truth

## Alert Levels

| Level | Trigger | Action |
|-------|---------|--------|
| `CRITICAL` | Out of range | Immediate rebalance alert |
| `WARNING` | Efficiency < 50% | Range adjustment recommendation |
| `MILESTONE` | Tier promotion | Celebration + next tier preview |
| `COMPOUND` | Fees ≥ $50 accumulated | Claim + reinvest CTA |
| `DCA` | Sunday DCA day | Reminder to add capital |
| `PRICE_MOVE` | >5% from entry | IL impact check |
| `SILENT` | None of above | No message sent |

## Handoff

- DMOB has contract struct scaffolding task in Labs group
- Desmond has alert microcopy + tier UX task in Creative group
- Both have AAE-Signal-Spec-Structured.md as source
