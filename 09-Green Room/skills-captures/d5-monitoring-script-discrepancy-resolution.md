---
title: Script Output Discrepancy Resolution Protocol
date: 2026-05-03
type: skills-capture
domain: strategies
status: published
tags: [monitoring, d5-milestone, debug, ground-truth, state-files]
---

# Script Discrepancy Resolution — D5 Monitoring Suite

**Date discovered:** 2026-05-03  
**Detected by:** YoYo (Strategies) during 4× daily monitoring run  
**Severity:** P0 — Systematic reporting divergence across scripts  
**Status:** Resolved (protocol defined, follow-up tasks assigned)

---

## Symptom

Three monitoring scripts produced **substantially different position values** for the same pool at identical timestamp:

| Script | Reported Position | Efficiency | Status |
|--------|------------------|------------|--------|
| `d5-milestone-summary.py` | $83.92 | 38.2% | ❌ Under-reporting |
| `d5-master-cron.py` | $138.92 | 66.3% | ⚠️ Over-reporting |
| `lp-position-reader.py` | $134.94 LP + $0.88 wallet = **$135.82** | 38.2% | ✅ Ground truth (on-chain decoded) |

**Variance:** Up to **$55 difference** (~40%) between extreme scripts on same position.

---

## Root Cause Analysis

### 1. State File Fragmentation Across HERMES Profiles
Scripts maintain independent state caches in different filesystem locations:
- `~/.hermes/scripts/` — Default global state
- `~/.hermes/profiles/yoyo/home/.hermes/scripts/` — Per-profile state (Yoyo-specific)

**Result:** No single source of truth; scripts reading different `.lfj-*.json` files observe divergent snapshots.

### 2. Independent Implementation Logic
- `d5-master-cron.py` — Consolidated report; may include **pending DCA injection** or stale snapshot not yet on-chain
- `d5-milestone-summary.py` — Human-narrative snapshot; uses **different config range source** and **simplified efficiency calculation**
- `lp-position-reader.py` — On-chain position decoder; queries blockchain directly and returns verified balances

---

## Resolution Protocol (Executed 2026-05-03)

### Step 1 — Establish Ground Truth Hierarchy
```bash
# ALWAYS run in this order:
python3 lp-position-reader.py   # → USE THESE NUMBERS for vault Balance field
python3 d5-master-cron.py       # → USE for watchlist prices + volume metrics
# d5-milestone-summary.py → Use ONLY for narrative boilerplate/template
```

### Step 2 — Vault Entry Number Authority
**Balance field in vault entries MUST match `lp-position-reader.py` output exactly.** Any deviation must be documented with an inline `Note:` explaining variance.

### Step 3 — Discrepancy Thresholds
If any two sources disagree by:
- **>$0.50** in position value, OR
- **>5 percentage points** in efficiency

→ Log the discrepancy in Green Room incident file and **defer vault update** until resolved.

### Step 4 — IL Spike Protocol
If `lp-position-reader.py` shows IL > 2% threshold:
- Auto-flag vault entry with `🚨 Review` action
- Add rationale: "IL spiked to X% (>2% threshold); on-chain verification required"
- YoYo to verify oracle/settlement integrity before rebalance decision

---

## Follow-up Actions Assigned

| Owner | Task | Status |
|-------|------|--------|
| DMOB | Symlink state files across all profiles: <br> `~/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-*.json` ←→ `~/.hermes/scripts/` | 🚀 Pending |
| YoYo | Reconcile milestone ladder config divergence: <br> `d5-master-cron.py` hardcodes `$5/$20/$55/$200` <br> AAE config file says `$3/$5/$8/$10/...` | 🚀 Open |
| Desmond | Verify `d5-milestone-summary.py` reads config range from same source as `d5-master-cron.py` | 🚀 Open |

---

## Prevention Checklist (Before Any Vault Update)

- [ ] Run `lp-position-reader.py` — record position value, efficiency
- [ ] Run `d5-master-cron.py` — record watchlist prices, volume metrics
- [ ] Cross-check both sources agree within tolerance ($0.50 / 5pp)
- [ ] If discrepancy → flag in Green Room, do NOT update vault
- [ ] If IL > 2% → add review flag, escalate to YoYo

---

## Incident Timeline (2026-05-03)

| Time (UTC) | Event | Agent |
|------------|-------|-------|
| ~08:15 | 4× daily monitoring run detects divergence | YoYo |
| ~08:30 | Triangulation with `lp-position-reader.py` confirms ground truth | YoYo |
| ~09:00 | Root cause analysis (state file fragmentation) identified | YoYo |
| ~10:00 | Resolution protocol documented in Green Room incident file | YoYo |
| ~11:45 | Daily cron sync; tasks assigned to DMOB/YoYo/Desmond | Gentech automation |

---

## Related Files

- Incident document: `10-Archive/Memory-Backups/2026-05-03-11/gentech-skills-script-discrepancy-case-2026-05-03.md`
- D5 Milestone Tracker: `03-Projects/DeFi/D5-Milestone-Tracker.md` (May 3 IL spike entry)
- State file schema reference: `10-Archive/Memory-Backups/2026-05-03-11/gentech-skills-state-file-schemas.md`
- Ground truth mandate: `10-Archive/Memory-Backups/2026-05-03-11/gentech-skills-milestone-ladder-current.md`

---

## Open Questions

1. **Permanent fix scope:** Should all monitoring scripts be refactored to share a single state cache layer, or is symlink bridging sufficient?
2. **Vault entry audit:** Should past entries (May 2 and earlier) be re-verified against `lp-position-reader.py` ground truth?
3. **Monitoring alert:** Should discrepancy detection be automated (e.g., assert all three scripts agree within tolerance)?

---

*Last updated: 2026-05-03 11:45 UTC*
*Author: YoYo (Strategies) via daily cron discovery*
*Audience: DMOB (Labs), YoYo (Strategies), Desmond (Creative)*
