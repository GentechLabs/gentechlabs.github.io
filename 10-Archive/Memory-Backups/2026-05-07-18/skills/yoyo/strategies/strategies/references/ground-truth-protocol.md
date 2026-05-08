---
title: Ground Truth Protocol for Cross-Script LP Monitoring
updated: 2026-05-03
owner: YoYo (Strategies)
---

## Problem Statement

Multiple monitoring scripts track the same LP position but maintain independent state caches in different Hermes profile directories (e.g., `~/.hermes/scripts/` vs `~/.hermes/profiles/yoyo/home/.hermes/scripts/`). This causes divergent reported values for Balance, Efficiency, and APR at the same timestamp.

**Incident example (May 3, 2026)**:
| Script | Reported Position | Efficiency |
|--------|------------------|------------|
| `d5-milestone-summary.py` | $83.92 | 38.2% |
| `d5-master-cron.py` | $138.92 | 66.3% |
| `lp-position-reader.py` | $135.82 | 38.2% |

Root causes identified:
- `d5-master-cron.py` includes pending DCA injection not yet on-chain
- `d5-milestone-summary.py` uses simplified efficiency calc and different config range source
- State files not shared across Hermes profiles

## Ground Truth Hierarchy

1. **On-chain decoded balances** (`lp-position-reader.py`) — always authoritative for vault Balance, Efficiency, APR, Active Bin
2. **Watchlist/price aggregators** (`d5-master-cron.py`) — secondary source for CMC watchlist, pool volume, price deltas only
3. **Narrative/summary scripts** (`d5-milestone-summary.py`) — tertiary; use for templated report boilerplate only; ignore numeric fields

## Daily Verification Checklist

Run every morning before vault write:
```bash
# Step 1: Get ground truth
python3 lp-position-reader.py
# → Record: Balance, Efficiency, APR, Range, Active Bin

# Step 2: Check watchlist source for context
python3 d5-master-cron.py
# → Use for CMC alerts and volume narrative only

# Step 3: Validate summary script output
python3 d5-milestone-summary.py
# → Ignore its Balance/Efficiency numbers; use only milestone tier text
```

**Tolerance thresholds** (if exceeded, investigate):
- Balance discrepancy > $0.50
- Efficiency difference > 5 percentage points
- APR divergence > 2%

## State File Layout

All state files must reside in a **single shared directory** accessible to all Hermes profiles:

```
~/.hermes/profiles/yoyo/home/.hermes/scripts/
├── .lfj-aae-state.json           ← LP position state (ground truth cache)
├── .cmc-watchlist-state.json     ← CMC watchlist last prices
├── .d5-milestone-state.json      ← milestone tracking
└── .lfj-aae-config.json          ← config (read-only, versioned)
```

**Symlink requirement**: If scripts run under different Hermes profiles, ensure all `.lfj-*.json` files are symlinked to a common location. See `references/state-file-symlink-pattern.md`.

## Discrepancy Incident Response Template

When divergence detected, create `09-Green Room/active-handoffs/<date>-script-discrepancy-<owner>.md`:

```markdown
---
incident: Script State Divergence
date: <YYYY-MM-DD>
detected_by: <agent>
affected_scripts: [list]
---

### Symptom
<Describe what values differed and by how much>

### Ground Truth Determination
<Which script is authoritative and why>

### Root Cause
<Check: state paths, pending DCA inclusion, config mismatch, stale cache>

### Remediation Assignment
- Owner: <agent>
- Task: <specific fix>
- Deadline: <YYYY-MM-DD EOD>
```

## Prevention Rules

1. **Single source of truth**: All vault Balance fields must cite `lp-position-reader.py` output
2. **State singletons**: One state file per data domain; never duplicate
3. **Config-as-source**: Efficiency thresholds, milestone ladder, range boundaries read from config at runtime (no hardcoding)
4. **Weekly audit**: Run `diff` across all profile script directories to catch state duplication early

## Related

- Handoff: `09-Green Room/active-handoffs/2026-05-02-d5-milestone-enhancement-dmob.md`
- Daily sync: `08-Daily/2026-05-03.md` (Script Discrepancy Incident section)
- State symmetry: `references/state-file-symlink-pattern.md`
