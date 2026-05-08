---
name: monitoring-data-consistency
description: Ensure integrity across multiple monitoring scripts reporting on same on-chain state. Diagnose and resolve divergence when independent scripts produce conflicting values, establish ground truth hierarchy, and implement state synchronization across HERMES profiles.
triggers: [monitoring-discrepancy, multi-script-divergence, vault-data-validation, state-file-fragmentation]
杏 category: strategies
杏 mentor: YoYo
---

# Monitoring Data Consistency — Class-Level Skill

**Domain:** Strategies (DeFi LP Monitoring, Milestone Tracking)  
**Author:** YoYo (2026-05-03 incident-driven)  
**Status:** Active — Used in D5 Milestone Tracker consolidation phase  
**Tags:** monitoring, data-integrity, state-sync, ground-truth, herm profiles, vault-validation

---

## 🎯 When To Use

**Trigger conditions (any one):**
- Multiple monitoring scripts report **different position values** for same on-chain entity (pool, wallet, position)
- Vault entry audit reveals numeric discrepancies between sources
- State files exist in both `~/.hermes/scripts/` and `~/.hermes/profiles/*/home/.hermes/scripts/`
- Cron job consolidation merges previously independent monitors
- New script added to existing monitoring ecosystem

**Do NOT use for:**
- Single-script bugs (use debugging skills instead)
- On-chain RPC errors (use blockchain-query-troubleshooting)
- Strategy disagreements (use strategy-review)
- Pure performance tuning (use performance-optimization)

---

## 📋 Pattern Overview

### The Multi-Script Divergence Problem

As Gentech's monitoring suite matures, multiple scripts observe the **same on-chain reality** but maintain **independent state caches** in different filesystem locations. Over time, they drift apart due to:

1. **State file fragmentation** — Profile-specific state (`~/.hermes/profiles/<agent>/home/.hermes/scripts/`) vs global state (`~/.hermes/scripts/`)
2. **Different calculation logic** — Simplified efficiency vs precise on-chain decoding
3. **Timing skew** — Pending DCA injection, stale snapshots, race conditions
4. **Config source divergence** — Hardcoded values vs env config vs API-derived thresholds

### Resolution Philosophy

**Establish a single source of truth hierarchy** and document which script owns which data domain. Never rely on a single script for all metrics.

---

## 🔄 Ground Truth Hierarchy Protocol

Define the **authoritative chain** for every data point type:

| Data Type | Tier 1 (Ground Truth) | Tier 2 (Secondary) | Tier 3 (Narrative Only) | Decision Authority |
|-----------|----------------------|--------------------|------------------------|-------------------|
| On-chain balances | `lp-position-reader.py` (direct decode) | — | — | **Absolute** |
| Active bin / efficiency | `lp-position-reader.py` | `d5-master-cron.py` (derived) | — | Tier 1 |
| Watchlist prices | — | `d5-master-cron.py` (CMC + DexScreener) | — | Tier 2 |
| Pool volume / fees | — | `d5-master-cron.py` | — | Tier 2 |
| Milestone tier label | — | `lp-aae-signal-monitor.py` (reads config) | `d5-milestone-summary.py` | Tier 2 |
| Narrative boilerplate | — | — | `d5-milestone-summary.py` | Tier 3 only |
| Pending capital injection | — | `d5-master-cron.py` (if tracking) | — | **Exclude from vault** |

**Golden rule:** Vault Balance fields **MUST** match Tier 1 ground truth exactly. All other fields cite source explicitly.

---

## 🔍 Diagnostics Checklist

Run this sequence when divergence detected:

```bash
# Step 1: Identify which scripts disagree
# (enumerate all monitoring scripts in 03-Strategies/scripts/ for the domain)
find 03-Strategies/scripts/ -name '*d5*.py' -o -name '*lp-*monitor*.py'

# Step 2: Run all scripts, capture outputs
python3 lp-position-reader.py > /tmp/t1.json 2>&1
python3 d5-master-cron.py > /tmp/t2.json 2>&1
python3 d5-milestone-summary.py > /tmp/t3.json 2>&1

# Step 3: Extract key metrics (position value, efficiency, IL)
grep -E 'Position|Efficiency|IL' /tmp/t*.json

# Step 4: Check state file locations
find ~/.hermes -name '.lfj-*.json' 2>/dev/null
find ~/.hermes/profiles -name '.lfj-*.json' 2>/dev/null

# Step 5: Compare last modified times
stat ~/.hermes/scripts/.lfj-* 2>/dev/null
stat ~/.hermes/profiles/*/home/.hermes/scripts/.lfj-* 2>/dev/null
```

---

## ⚙️ Resolution Steps

### Phase 1 — Immediate Triage
1. **Freeze vault updates** until ground truth is established
2. **Run `lp-position-reader.py` first** — treat its decoded output as canonical for Balance field
3. **Document divergence** in Green Room incident file (`10-Archive/Memory-Backups/YYYY-MM-DD-HH/`)
4. **Alert YoYo** (or domain owner) for confirmation

### Phase 2 — Root Cause Classification
Match observed pattern to known causes:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Script A ~10–20% higher than ground truth | Includes pending DCA injection | Exclude pending capital from vault Balance field |
| Script B ~40–50% lower than ground truth | Simplified efficiency calc / different bin range | Use only for narrative; cite ground truth |
| All scripts differ from on-chain | State file corruption or stale RPC | Rebuild state: delete `.lfj-*.json`, rerun ground truth |
| Scripts disagree only on milestone tier | Config source mismatch | Unify config read path to single env file |
| Divergence appears post-cron-consolidation | State files not symlinked across profiles | Create profile→global symlinks |

### Phase 3 — State File Synchronization
If fragmentation detected (files exist in both locations):

```bash
# For each .lfj-*.json file found:
# 1. Identify authoritative source (usually ~/.hermes/scripts/ for global, or use newest file)
# 2. Symlink profile variant to authoritative location
PROFILES=~/.hermes/profiles/*/home/.hermes/scripts/
for statefile in .lfj-position-state .lfj-efficiency-trend .lfj-aae-state; do
  # If global exists but profile doesn't → create symlink
  if [ -f ~/.hermes/scripts/$statefile ] && [ ! -e $PROFILES/$statefile ]; then
    ln -s ~/.hermes/scripts/$statefile $PROFILES/$statefile
  fi
  # If both exist but differ → use newest, force-symlink
done
```

**Important:** After symlinks, **delete stale copies** to prevent future divergence.

### Phase 4 — Config Reconciliation
Search for hardcoded values that should be config-driven:

```bash
# Find hardcoded milestone amounts
grep -rn '\$[0-9]\+\.\?[0-9]*' 03-Strategies/scripts/ | grep -E 'd5|lp|milestone'

# Compare against config source
cat 00-HQ/config/defi-lp-config.env | grep -E 'MILESTONE|TIER|TARGET'
```

If found, **refactor script to read from config** (or update config to match agreed thresholds). Document the source-of-truth in script header comment.

---

## 📊 Discrepancy Thresholds & Actions

Before any vault update, run tolerance check:

| Metric | Tolerance | Action if Exceeded |
|--------|-----------|-------------------|
| Position value delta | > $0.50 | **Do NOT update vault** — resolve discrepancy first |
| Efficiency delta | > 5 percentage points | Log in Green Room, halt vault writes |
| IL percentage variance | Any (ground truth required) | Use `lp-position-reader.py` only; investigate oracle |
| Tier label mismatch | Any | Reconcile config source before publishing |

**Vault entry field rules:**
- `Balance:` ground truth only (Tier 1)
- `Efficiency:` ground truth only (Tier 1)
- `Action:` Tier 2 acceptable if annotated with source
- `Milestone Progress:` cite which script's tier logic used

If any field sourced from Tier 3 (`d5-milestone-summary.py`), add **inline note:**
```
Note: Narrative tier label from d5-milestone-summary.py; ground truth tier = X (lp-aae-signal-monitor.py)
```

---

## 🛡️ Prevention Checklist (Pre-Vault-Update)

**Execute this BEFORE any vault entry is written:**

- [ ] Run `lp-position-reader.py` → record Position, Efficiency, IL, Active Bin
- [ ] Run `d5-master-cron.py` → record Watchlist prices, Pool volume
- [ ] Cross-check: Position agrees within ±$0.50 AND ±5pp efficiency?
- [ ] Check state files: are all `.lfj-*.json` symlinked across profiles?
- [ ] Verify config source: milestone ladder matches agreed thresholds (`00-HQ/config/defi-lp-config.env`)
- [ ] If IL > 2%: add `🚨 Review` flag to vault entry, escalate to YoYo
- [ ] Document any variance > tolerance in Green Room incident log

**If any check fails → STOP → create Green Room handoff before proceeding.**

---

## 🧩 State File Management

### Profile Scatter Pattern

HERMES creates per-agent profile directories that each have independent `~/.hermes/scripts/` trees:

```
~/.hermes/
  scripts/                    # Global (YoYo's default hermes)
    .lfj-position-state.json
  profiles/
    yoyo/home/.hermes/scripts/   # Profile-isolated copy
      .lfj-position-state.json   ← often desynced
    dmob/home/.hermes/scripts/   # DMOB's isolated copy
      .lfj-position-state.json   ← diverges independently
```

**Problem:** Scripts running under different profiles read different state files → reporting divergence.

### Symlink Bridge Solution

Create **profile→global symlinks** so all agents read/write same state:

```bash
# In each profile directory:
cd ~/.hermes/profiles/yoyo/home/.hermes/scripts/
for f in ~/.hermes/scripts/.lfj-*.json; do
  [ -e "$(basename "$f")" ] && rm "$(basename "$f")"
  ln -s "$f" .
done
```

**Enforcement:** After any cron job modification, verify symlink integrity with:

```bash
# Verification script (save as scripts/verify-state-sync.py)
#!/usr/bin/env python3
import os, pathlib
global_dir = pathlib.Path.home() / '.hermes' / 'scripts'
profile_dir = pathlib.Path.home() / '.hermes' / 'profiles' / 'yoyo' / 'home' / '.hermes' / 'scripts'
for statefile in global_dir.glob('.lfj-*.json'):
  target = profile_dir / statefile.name
  if not target.exists():
    print(f"MISSING: {target}")
  elif not target.is_symlink():
    print(f"NOT_SYMLINK: {target}")
  elif os.readlink(target) != str(statefile):
    print(f"WRONG_TARGET: {target} -> {os.readlink(target)}")
print("State sync verification complete")
```

---

## 📁 Incident Documentation Template

When creating Green Room incident file, use structure:

```
# Incident: Script Discrepancy — <Brief Description>
**Date:** YYYY-MM-DD
**Detected by:** <Agent> during <monitoring run/context>
**Severity:** P0/P1/P2
**Scripts involved:** <list affected scripts>

---
## Symptom

| Script | Reported Value | Efficiency | Status |
|--------|----------------|------------|--------|
| `script-a.py` | $X | Y% | ❌ Under |
| `script-b.py` | $Z | W% | ⚠️ Over |
| `ground-truth.py` | $G | V% | ✅ Canonical |

## Root Cause

<1–3 sentence classification from known causes table>

## Resolution Protocol (as executed)

1. <Step 1 — what was done immediately>
2. <Step 2 — ground truth establishment>
3. <Step 3 — divergence explanation>

## Follow-up Actions

| Owner | Task | Deadline | Status |
|-------|------|----------|--------|

## Prevention

<Checks to run before next vault update>

---
*Documented in: skills-captures/<filename>.md*
```

**Store to:** `09-Green Room/skills-captures/<descriptive-name>.md`

---

## 🔄 Related Skills

- `strategies/cron-consolidation` — Overlap: cron consolidation often triggers this pattern by merging previously independent stateful jobs. Use this skill AFTER consolidation to audit state sync.
- `gentech/hermes-agent-health` — Related: agent offline issues can masquerade as data divergence. Rule out agent health first.
- `gentech/handoff-reporting` — Connects: handoff to DMOB (state file fixes) and YoYo (config reconciliation) when incident exceeds tolerance thresholds.

---

## 📚 Reference Cases

**May 3, 2026 incident (D5 Milestone monitoring):**
- Discovery: `d5-master-cron.py` ($138.92) vs `d5-milestone-summary.py` ($83.92) vs `lp-position-reader.py` ($135.82)
- Root cause: State files in both global and profile directories, unsynchronized
- Ground truth: `lp-position-reader.py` (on-chain decoded)
- Follow-ups assigned: DMOB (symlink state files), YoYo (reconcile milestone ladder config)
- Incident doc: `10-Archive/Memory-Backups/2026-05-03-11/gentech-skills-script-discrepancy-case-2026-05-03.md`
- Skills capture: `09-Green Room/skills-captures/d5-monitoring-script-discrepancy-resolution.md`

**Historical precedents:**
- `dmob-skills-d5-cron-consolidation-plan.md` — planned unified cron but state fragmentation not anticipated
- `gentech-skills-state-file-schemas.md` — documents which scripts read/write which state files (consult before modifying)

---

## 🚨 Escalation Triggers

Escalate to **Gentech** if:
- Discrepancy persists >4h after ground truth established
- State file corruption detected (JSON decode errors)
- >3 scripts affected simultaneously
- Vault entry already published with incorrect numbers

Escalate to **Jordan** if:
- DMOB unresponsive to state-fix handoff (>12h)
- Config reconciliation blocked by strategic disagreement
- Monitoring data used for strategy call that turns out incorrect

---

## 🧪 Testing Your Fix

After applying resolution:

```bash
# 1. Re-run all scripts, confirm convergence
python3 lp-position-reader.py | grep Position
python3 d5-master-cron.py | grep Position
python3 d5-milestone-summary.py | grep Position
# Values should agree within tolerance (balance exact, efficiency ±5pp)

# 2. Verify state file symlinks
find ~/.hermes/profiles -type l -name '.lfj-*.json' -exec readlink {} \;

# 3. Test vault entry generation produces correct Balance field
# (simulate vault entry template with ground truth output)

# 4. Document in next daily sync that resolution completed
```

---

## 📌 Key Principles (Non-Negotiable)

1. **Ground truth precedes action** — Never update vault based on single script when divergence detected
2. **State file unity** — All profiles must read same state files via symlinks
3. **Config single-source** — Milestone thresholds live in ONE place; all scripts read from it
4. **Vault balance accuracy** — Balance field is contractual; must match on-chain exactly
5. **Narrative vs data separation** — `d5-milestone-summary.py` is template engine, not data source

---

*Version:* 1.0  
*Last validated:* 2026-05-03 (IL spike incident)  
*Next review:* After Kite AI monitoring suite added (May 17 target)
