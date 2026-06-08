# LP Monitoring — Unified Cron Architecture (Apr 26, 2026)

## Single Source of Truth

**Script:** `~/.hermes/scripts/lp-aae-signal-monitor.py`
**Cron:** `faed4f588aef` (runs hourly, 7AM–9PM EDT)
**Deliver:** Strategies Group

---

## Why This Script Wins

Jordan confirmed it's the cleanest format:
- **Position block**: Value, splits, price, range, efficiency, APR
- **Revenue block**: 24H fees, cumulative, claimable, days in range
- **Progression block**: Rank (Scout→Raider→Warlord→Sovereign), next tier, progress %
- **Action**: HOLD / WATCH / COMPOUND / DCA / REBALANCE (one-line, decisive)
- **Silence logic**: Only speaks when status ≠ SILENT (in-range, healthy, no action needed → quiet)

---

## What Got Consolidated

| Old | Status |
|-----|--------|
| `daily-lp-summary.py` | Retained but not scheduled (can be run manually if needed) |
| `lp-unified-monitor.py` | Retained (has multi-pool + compound logic if we expand) |
| `lp-aae-monitor.py` | Retained (legacy, can be archived later) |
| Cron `76d0ee972be9` (D5 daily) | **Removed** — redundant, absorbed into hourly script |
| Cron `faed4f588aef` (Unified hourly) | **Updated** — now runs `lp-aae-signal-monitor.py` directly |

---

## Jordan's Latest Request: Bid-Ask-Aware Micro-DCA

When the AAE signal monitor fires (efficiency < 50%), add bid-ask-aware DCA sizing:

| Fee Efficiency | Shape Position | Micro-DCA | Rationale |
|--------------|----------------|-----------|-----------|
| <30% | Near edge / below range | $20 | Urgency — position needs repositioning |
| 30–50% | Mid-range drift | $10 | Monitor — slight edge positioning helps |
| 50–70% | Center-ish | $0 | No bonus DCA needed |
| >70% | Center (Curve peak) | $0 | Optimal earning, just hold |
| If below range | Out of range | REBALANCE | No DCA without rebalancing first |

**Implementation:** In `lp-aae-signal-monitor.py` — update `get_suggested_action()` to include micro-DCA sizing based on `fee_efficiency` + `shape` position within range.

**Routed to:** DMOB (Labs) for script update — this is a Python logic change, not a cron change.
