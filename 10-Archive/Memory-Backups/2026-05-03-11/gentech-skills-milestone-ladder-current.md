# Milestone Ladder Definitions — As of 2026-05-02

**⚠️ WARNING**: Three different ladders exist across the codebase. This file documents the divergence. YoYo must reconcile.

---

## Ladder A: AAE Signal Monitor (Primary — from `.lfj-aae-config.json`)

Source: `/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json` → `milestones[]`

| Tier | Label | Daily Fees Target | Description |
|------|-------|-------------------|-------------|
| 1 | Scout | $3.00 | Entry rank — basic strategies unlocked |
| 2 | Scout+ | $5.00 | Consistent earner — tighter ranges unlocked |
| 3 | Raider | $8.00 | Intermediate — SPOT shape unlocked |
| 4 | Raider+ | $10.00 | Advanced single-pool — bidirectional unlocked |
| 5 | Warlord | $15.00 | Multi-pool ready — portfolio strategies |
| 6 | Warlord+ | $20.00 | High capital efficiency — custom ranges |
| 7 | Sovereign | $55.00 | Squad-level coordination — treasury mgmt |
| 8 | Freedom | $200.00 | Freedom milestone — custom strategy creation |

**Used by**: `lp-aae-signal-monitor.py`, `d5-milestone-summary.py`

---

## Ladder B: D5 Master Cron (Secondary — hardcoded in `d5-master-cron.py`)

Source: `/root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py` (lines ~40–60)

| Tier | Label | Daily Fees Target | Notes |
|------|-------|-------------------|-------|
| 1 | Scout | $5.00 | Only 4 tiers defined |
| 2 | Raider | $20.00 | |
| 3 | Warlord | $55.00 | |
| 4 | Sovereign | $200.00 | |

**Inconsistency**: Missing Scout+/Raider+/Warlord+ intermediate tiers. Scout target is $5 vs $3 in Ladder A.

---

## Ladder C: Crown Milestones (Fee Accumulation — hardcoded in `lp-range-monitor-v3.py`)

Source: `/root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v3.py` line 30:
```python
FEE_MILESTONES = [0.50, 1.00, 2.00, 5.00, 10.00, 25.00, 50.00, 100.00]
```

| Crown # | Threshold | Meaning |
|---------|-----------|---------|
| 1 | $0.50 | First earnings milestone |
| 2 | $1.00 | |
| 3 | $2.00 | |
| 4 | $5.00 | |
| 5 | $10.00 | |
| 6 | $25.00 | |
| 7 | $50.00 | Compound threshold also marks this |
| 8 | $100.00 | |

**Note**: These are **cumulative fees earned**, not daily rate. Used for crown tracking and celebration triggers.

---

## Reconciliation Decision Log

**2026-05-02** (Gentech): Created this reference. Current system reports:
- AAE: "Unranked" (Tier 0) — earning ~$0.04/day vs $3 target
- D5 Master: "Scout" — earning $0.04/day vs $5 target (different target!)

**YoYo to decide**:
1. Should D5 milestones match AAE (8 tiers) or simplify (4 tiers)?
2. Should crown milestones align with DCA compound threshold ($50) — they already do at milestone 7.
3. Update all three sources to single canonical configuration file.

**Canonical location candidate**: `~/.hermes/scripts/.lfj-aae-config.json` (already holds milestones array). If selected, patch:
- `d5-master-cron.py` to read from config instead of hardcoding
- `lp-range-monitor-v3.py` to derive crowns from cumulative fee tracker (not hardcode)

---

## Quick Diff Summary

| Tier | AAE (config) | D5-Master | Crown (cumulative) |
|------|--------------|-----------|-------------------|
| Entry | Unranked (<$3) | Scout (<$5) | $0.00 |
| 1 | Scout $3 | Scout $5 | $0.50 |
| 2 | Scout+ $5 | — | $1.00 |
| 3 | Raider $8 | Raider $20 | $2.00 |
| 4 | Raider+ $10 | — | $5.00 |
| 5 | Warlord $15 | Warlord $55 | $10.00 |
| 6 | Warlord+ $20 | — | $25.00 |
| 7 | Sovereign $55 | Sovereign $200 | $50.00 (compound) |
| 8 | Freedom $200 | — | $100.00 |

**Bottom line**: Until reconciled, **trust `lp-aae-signal-monitor.py` output** — it reads from the config file and is the most systematically maintained.