---
title: Ground Truth Protocol for Multi-Script Monitoring
used_in: [monitoring-data-consistency, D5-Milestone-Tracker]
date: 2026-05-03
author: YoYo (Strategies)
type: reference
---

# Ground Truth Protocol — Cross-Script Monitoring Consistency

## TL;DR

When multiple monitoring scripts track the same on-chain entity, **define a single source of truth hierarchy** before any vault entry is published. Use this protocol to diagnose divergence, establish which script owns which data domain, and prevent stale/inconsistent numbers from entering the vault.

---

## Problem Statement

Three scripts → three different position values for the same LFJ AVAX/USDC LP position:

| Script | Position Value | Efficiency | Root Cause |
|--------|----------------|------------|------------|
| `d5-milestone-summary.py` | $83.92 | 38.2% | Different config range + simplified efficiency calc |
| `d5-master-cron.py` | $138.92 | 66.3% | Includes pending DCA injection not yet on-chain |
| `lp-position-reader.py` | $135.82 | 38.2% | On-chain decoded balances (ground truth) |

**Variance:** Up to $55 (~40%) between extremes.

---

## Hierarchy Template

Adapt this template for your monitoring domain:

| Data Type | Tier 1 (Ground Truth) | Tier 2 (Secondary) | Tier 3 (Narrative) | Notes |
|-----------|----------------------|--------------------|--------------------|-------|
| On-chain balances | `lp-position-reader.py` | — | — | Direct blockchain decode |
| Active bin / efficiency | `lp-position-reader.py` | `d5-master-cron.py` | — | Ground truth authoritative |
| Watchlist prices | — | `d5-master-cron.py` | — | CMC + DexScreener aggregated |
| Pool volume / fees | — | `d5-master-cron.py` | — | Volume-based estimates |
| Milestone tier label | — | `lp-aae-signal-monitor.py` | `d5-milestone-summary.py` | Config-driven |
| Narrative boilerplate | — | — | `d5-milestone-summary.py` | Template only |
| Pending capital (DCA) | — | `d5-master-cron.py` | — | **EXCLUDE from vault Balance** |

**Golden rule:** Vault Balance field **MUST** match Tier 1. All other fields cite source explicitly in vault entry.

---

## Diagnostics Command Bundle

```bash
# 1. Identify all scripts in the monitoring suite
find 03-Strategies/scripts/ -name '*d5*.py' -o -name '*lp-*monitor*.py'

# 2. Run all scripts, capture outputs to temp files
python3 lp-position-reader.py > /tmp/t1.json 2>&1
python3 d5-master-cron.py > /tmp/t2.json 2>&1
python3 d5-milestone-summary.py > /tmp/t3.json 2>&1

# 3. Extract key metrics for comparison
for f in /tmp/t*.json; do
  echo "=== $f ==="
  grep -E 'Position|Efficiency|IL|Tier' "$f" || echo "(no matches)"
done

# 4. Check state file locations (look for duplicates across profiles)
echo "=== Global state ==="
find ~/.hermes/scripts/ -name '.lfj-*.json' 2>/dev/null
echo "=== Profile state ==="
find ~/.hermes/profiles/ -name '.lfj-*.json' 2>/dev/null

# 5. Compare modification times (stale caches)
stat ~/.hermes/scripts/.lfj-* 2>/dev/null
stat ~/.hermes/profiles/*/home/.hermes/scripts/.lfj-* 2>/dev/null
```

---

## Discrepancy Thresholds (ABORT VAULT UPDATE IF EXCEEDED)

| Metric | Tolerance | Action |
|--------|-----------|--------|
| Position value delta | > $0.50 | ❌ Do NOT update vault — resolve first |
| Efficiency delta | > 5 percentage points | ❌ Log incident, halt vault writes |
| IL variance (any) | N/A (requires on-chain ground truth) | Use `lp-position-reader.py` only |
| Tier label mismatch | Any | Reconcile config source prior to publishing |

**Vault entry field source rules:**

| Vault Field | Allowed Source | Must Match |
|-------------|---------------|------------|
| `Balance:` | Tier 1 only (`lp-position-reader.py`) | Ground truth exact |
| `Efficiency:` | Tier 1 only | Ground truth exact |
| `Action:` | Tier 2 acceptable | Cite source if not Tier 1 |
| `Milestone:` | Tier 2 (`lp-aae-signal-monitor.py`) | Cite which script used |

**If sourcing from narrative script (`d5-milestone-summary.py`):**
```markdown
**Milestone:** Tier 2 (Raider) — $20/day target
Note: Narrative tier label from d5-milestone-summary.py; ground truth tier = 1 (lp-aae-signal-monitor.py)
```

---

## State File Symlink Procedure

If state files exist in both global and profile locations:

```bash
# For each .lfj-*.json file, ensure profile points to global via symlink
GLOBAL_DIR="$HOME/.hermes/scripts"
PROFILE_DIR="$HOME/.hermes/profiles/yoyo/home/.hermes/scripts"

cd "$PROFILE_DIR"
for statefile in .lfj-position-state .lfj-efficiency-trend .lfj-aae-state; do
  if [ -f "$GLOBAL_DIR/$statefile" ] && [ ! -L "$statefile" ]; then
    # Existing file—backup then symlink
    mv "$statefile" "${statefile}.bak-$(date +%s)"
  fi
  if [ -f "$GLOBAL_DIR/$statefile" ] && [ ! -e "$statefile" ]; then
    ln -s "$GLOBAL_DIR/$statefile" "$statefile"
  fi
done

# Verification
find "$PROFILE_DIR" -type l -name '.lfj-*.json' -exec readlink {} \;
echo "Symlink verification complete"
```

**Post-symlink:** Delete stale backup copies 24h after confirming no errors.

---

## Config-Code Drift Detection

When scripts hardcode thresholds that should be config-driven:

```bash
# Find hardcoded values
grep -rn '\$[0-9]\+\.\?[0-9]*' 03-Strategies/scripts/ | grep -E 'milestone|tier|threshold'

# Compare against config
cat 00-HQ/config/defi-lp-config.env | grep -E 'MILESTONE|TIER|TARGET'
```

If mismatch found, assign reconciliation:
- **DMOB:** Update code to read from config (preferred)
- **YoYo:** Update config to match approved thresholds (if config was stale)

**Validation script** (add to scripts/):

```python
#!/usr/bin/env python3
"""Verify milestone ladder consistency between code and config."""
import json, sys
with open('00-HQ/config/defi-lp-config.env') as f:
    cfg = json.load(f)
config_vals = [m['daily_fees'] for m in cfg.get('milestones', [])]
code_vals  = [5.0, 20.0, 55.0, 200.0]   # ← update from actual constant

if config_vals != code_vals:
    print(f"MISMATCH: config={config_vals} code={code_vals}")
    sys.exit(1)
print("✓ Milestone ladder aligned")
```

---

## Incident Documentation Template

Create in `10-Archive/Memory-Backups/YYYY-MM-DD-HH/` or `09-Green Room/skills-captures/`:

```markdown
# Script Discrepancy — <Brief Description>

**Date:** YYYY-MM-DD  
**Detected by:** <Agent> during <monitoring run/context>  
**Severity:** P0 / P1 / P2  
**Scripts involved:** <comma-separated list>

---
## Symptom

| Script | Reported Value | Efficiency | Status |
|--------|----------------|------------|--------|
| `script-a.py` | $X | Y% | ❌ Under-reporting |
| `script-b.py` | $Z | W% | ⚠️ Over-reporting |
| `ground-truth.py` | $G | V% | ✅ Canonical |

## Root Cause

<Classify: state file fragmentation / pending DCA / config divergence / calculation logic>

## Resolution Protocol

1. <Step-by-step actions taken>
2. <Ground truth established>
3. <Follow-ups assigned>

## Follow-up Actions

| Owner | Task | Deadline | Status |
|-------|------|----------|--------|

---
*Documented in: skills-captures/<filename>.md*
```

---

## Related Skills

- `strategies/monitoring-data-consistency` — **parent skill** for this reference
- `gentech/hermes-agent-health` — rule out agent auth/cron issues first
- `strategies/cron-consolidation` — consolidation often triggers state fragmentation

---

*Maintained by:* YoYo (Strategies)  
*Last updated:* 2026-05-03 (IL spike incident)  
*Next review:* Before Kite AI monitoring addition (May 17)
