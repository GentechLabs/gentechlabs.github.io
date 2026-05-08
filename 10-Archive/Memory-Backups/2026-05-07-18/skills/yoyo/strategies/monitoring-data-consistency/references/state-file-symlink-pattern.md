---
title: HERMES Profile State File Symlink Pattern
used_in: [monitoring-data-consistency, D5-Milestone-Tracker]
date: 2026-05-03
author: YoYo (Strategies)
type: reference
---

# State File Symlink Pattern — HERMES Profile Unification

## Problem

Multiple monitoring scripts each maintain state caches in HERMES profile directories. When profiles are isolated (`~/.hermes/profiles/yoyo/home/`, `~/.hermes/profiles/dmob/home/`), each profile's scripts read **different state files** → reporting divergence, even though they're observing the same on-chain position.

```
BEFORE (fragmented):
~/.hermes/scripts/.lfj-position-state.json           ← global (unused by profiles)
~/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-position-state.json   ← stale copy
~/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-position-state.json  ← stale copy
Result: d5-master-cron.py (Yoyo profile) reads different state than lp-aae-signal-monitor.py (Dmob profile)
```

## Directory Layout

```
~/.hermes/
  scripts/                        # Global script storage (default hermes)
    .lfj-position-state.json      # ← canonical state (single source of truth)
    .lfj-efficiency-trend.json
    .lfj-aae-state.json

  profiles/
    yoyo/
      home/
        .hermes/
          scripts/                # Profile-isolated (often stale)
            .lfj-position-state.json → should symlink to ../../../../scripts/
            .lfj-efficiency-trend.json → should symlink to ../../../../scripts/
    dmob/
      home/
        .hermes/
          scripts/
            .lfj-position-state.json → should symlink to ../../../../scripts/
```

**Path math:** Profile script dir = `$HERMES_HOME/home/.hermes/scripts/`  
Global script dir = `$HERMES_HOME/scripts/` (where `HERMES_HOME` is the Hermes installation root; for default install it's `~/.hermes`)

---

## Symlink Bridge Solution

Make **all profiles symlink to the global state directory.** Writes go to global; all profiles read same data.

### One-Time Setup (for each profile)

```bash
#!/usr/bin/env bash
# run as the agent user (yoyo, dmob, etc.)

PROFILE_SCRIPTS="$HOME/.hermes/profiles/$(whoami)/home/.hermes/scripts"
GLOBAL_SCRIPTS="$HOME/.hermes/scripts"

# Ensure directories exist
mkdir -p "$PROFILE_SCRIPTS"
mkdir -p "$GLOBAL_SCRIPTS"

# For each known state file
for statefile in .lfj-position-state .lfj-efficiency-trend .lfj-aae-state .d5-lp-state; do
  GLOBAL_FILE="$GLOBAL_SCRIPTS/$statefile"
  PROFILE_FILE="$PROFILE_SCRIPTS/$statefile"

  # If global file doesn't exist yet, create empty placeholder
  if [ ! -e "$GLOBAL_FILE" ]; then
    touch "$GLOBAL_FILE"
  fi

  # If profile file exists but is not a symlink → backup it
  if [ -e "$PROFILE_FILE" ] && [ ! -L "$PROFILE_FILE" ]; then
    mv "$PROFILE_FILE" "${PROFILE_FILE}.bak-$(date +%s)"
  fi

  # Create symlink (force if already exists as broken link)
  ln -sf "$GLOBAL_FILE" "$PROFILE_FILE"
done

echo "✓ State file symlinks established for $(whoami)"
echo "  Global dir: $GLOBAL_SCRIPTS"
echo "  Profile dir: $PROFILE_SCRIPTS"
```

### Verification

```bash
#!/usr/bin/env bash
# verify-state-sync.sh

PROFILE_SCRIPTS="$HOME/.hermes/profiles/$(whoami)/home/.hermes/scripts"
GLOBAL_SCRIPTS="$HOME/.hermes/scripts"

echo "Checking symlink integrity..."
issues=0

for statefile in .lfj-position-state .lfj-efficiency-trend .lfj-aae-state; do
  PROFILE_FILE="$PROFILE_SCRIPTS/$statefile"
  GLOBAL_FILE="$GLOBAL_SCRIPTS/$statefile"

  if [ ! -L "$PROFILE_FILE" ]; then
    echo "  ❌ $PROFILE_FILE: NOT A SYMLINK"
    ((issues++))
    continue
  fi

  TARGET=$(readlink "$PROFILE_FILE")
  if [ "$TARGET" != "$GLOBAL_FILE" ]; then
    echo "  ❌ $PROFILE_FILE → $TARGET (expected $GLOBAL_FILE)"
    ((issues++))
  else
    echo "  ✅ $statefile → $(basename "$TARGET")"
  fi
done

if [ $issues -eq 0 ]; then
  echo "✓ All state files properly symlinked"
else
  echo "❌ $issues issue(s) found — run fix-state-sync.sh"
  exit 1
fi
```

**Automation:** Add to `d5-master-cron.py` pre-flight check; abort if symlink integrity fails.

---

## Common Pitfalls

### Pitfall 1: Relative vs Absolute Symlink Paths
- **Wrong:** `ln -s ../../../../scripts/.lfj-position-state .` (relative path depends on cwd)
- **Right:** `ln -sf "$HOME/.hermes/scripts/.lfj-position-state" .` (absolute, resolved at runtime)

**Impact:** Relative symlinks break when accessed from different working directories (cron vs interactive shell).

### Pitfall 2: Orphaned Stale Files
- profile file exists as regular file (not symlink) → script writes to it → divergence
- **Fix:** Run verification script daily; auto-repair stale non-symlinks

### Pitfall 3: Permission Drift
- Global state file owned by `root:root 600`; profile user cannot read
- **Fix:** Ensure global state files are `644` or group-accessible by all agent users

```bash
chmod 644 ~/.hermes/scripts/.lfj-*.json
chown :hermes-agents ~/.hermes/scripts/.lfj-*.json  # if using shared group
```

### Pitfall 4: Concurrent Write Racing
- Multiple agents on different profiles write to same state file simultaneously → last-write-wins, lost updates
- **Mitigation:** Only **one agent** (profile owner) should write to state at a time; others read-only
- Use `flock` for write sections if concurrent writes unavoidable:

```python
import fcntl
with open(STATE_FILE, 'w') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    json.dump(state, f)
    f.flush()
    fcntl.flock(f, fcntl.LOCK_UN)
```

---

## Recovery Procedure

**If divergence is already detected:**

1. **Stop all monitoring scripts** to prevent further state mutation
2. **Backup all state files** (both global and profiles):
   ```bash
   tar czf ~/state-backup-$(date +%s).tar.gz ~/.hermes/scripts/ ~/.hermes/profiles/*/home/.hermes/scripts/
   ```
3. **Identify authoritative copy:** Usually the most recent file across all locations
   ```bash
   find ~/.hermes -name '.lfj-position-state.json' -exec stat -c '%Y %n' {} \; | sort -n | tail -1
   ```
4. **Replace all other copies** with symlinks to authoritative source
5. **Run verification script** — confirm all symlinks resolve correctly
6. **Restart monitoring** with ground truth script first (`lp-position-reader.py`)

---

## Monitoring Integration

Add pre-flight check to every cron job:

```python
#!/usr/bin/env python3
import subprocess, sys

def verify_state_sync():
  """Exit 1 if state files are not properly symlinked."""
  profile_dir = os.path.expanduser('~/.hermes/profiles/yoyo/home/.hermes/scripts')
  global_dir  = os.path.expanduser('~/.hermes/scripts')
  for sf in ['.lfj-position-state.json', '.lfj-efficiency-trend.json']:
    p = os.path.join(profile_dir, sf)
    if not os.path.islink(p):
      print(f"STATE SYNC ERROR: {p} is not a symlink")
      return False
  return True

if not verify_state_sync():
  print("❌ State files not synchronized — aborting")
  sys.exit(1)

# ... rest of script ...
```

**Cron guard** (wrap script):

```bash
#!/bin/bash
# d5-master-cron.sh — wrapper with state verification

STATE_OK=$(python3 /usr/local/bin/verify-state-sync.py)
if [ $? -ne 0 ]; then
  echo "$(date): STATE SYNC FAILURE — ABORTING" >> /var/log/hermes/d5-cron-error.log
  exit 1
fi

exec python3 /root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py
```

---

## References

- Incident case study: `09-Green Room/skills-captures/d5-monitoring-script-discrepancy-resolution.md`
- State file schema: `10-Archive/Memory-Backups/2026-05-03-11/gentech-skills-state-file-schemas.md`
- Script used for ground truth: `03-Strategies/scripts/lp-position-reader.py`
- Consolidated cron (d5-master-cron.py) state expectations: `03-Strategies/scripts/d5-master-cron.py`

---

*Maintained by:* YoYo (Strategies)  
*Last updated:* 2026-05-03 (state fragmentation incident)  
*Applies to:* D5 Milestone monitoring suite, future multi-script systems
