---
title: State File Symlink Pattern for Multi-Profile Hermes Environments
updated: 2026-05-03
owner: DMOB (implementation) | YoYo (verification)
---

## Problem

When multiple Hermes agents (or profiles) run scripts that share state, each profile's home directory has its own `~/.hermes/scripts/` folder. If state files (`.lfj-*.json`, `.cmc-watchlist-state.json`) are not shared, scripts diverge and report different values for the same entity.

**Symptom**: `d5-master-cron.py` reports position $138.92 while `lp-position-reader.py` reports $135.82 for same pool at same time.

**Root cause**: Each script reads/write state in its own profile's `HOME_SCRIPTS_DIR`. No singleton state.

## Directory Layout

Hermes profile structure:
```
~/.hermes/profiles/
├── yoyo/
│   └── home/
│       └── .hermes/
│           └── scripts/
│               ├── .lfj-aae-state.json
│               └── .lfj-aae-config.json
├── dmob/
│   └── home/
│       └── .hermes/
│           └── scripts/
│               └── .lfj-aae-state.json   ← separate copy → divergence
└── desmond/
    └── home/
        └── .hermes/
            └── scripts/
```

**Canonical location** (pick ONE):
```
/root/.hermes/scripts/          ← system-wide shared (all profile symlinks point here)
# OR per-profile but symlinked to a shared dir:
/var/lib/gentech/hermes-state/  ← recommended for multi-agent
```

## Symlink Commands

**Option A — Centralize in `/root/.hermes/scripts/`** (simplest):
```bash
# As root, ensure the shared state file exists with correct permissions
touch /root/.hermes/scripts/.lfj-aae-state.json
chmod 600 /root/.hermes/scripts/.lfj-aae-state.json

# For each Hermes profile, replace its local copy with a symlink
for profile in yoyo dmob desmond; do
  local="/root/.hermes/profiles/${profile}/home/.hermes/scripts/.lfj-aae-state.json"
  if [ -f "$local" ]; then
    mv "$local" "${local}.bak-$(date +%s)"  # backup old file
  fi
  ln -s /root/.hermes/scripts/.lfj-aae-state.json "$local"
done

# Verify
for profile in yoyo dmob desmond; do
  ls -l "/root/.hermes/profiles/${profile}/home/.hermes/scripts/.lfj-aae-state.json"
done
```

**Option B — Shared directory `/var/lib/gentech/hermes-state/`** (clean separation):
```bash
mkdir -p /var/lib/gentech/hermes-state
chown root:root /var/lib/gentech/hermes-state
chmod 755 /var/lib/gentech/hermes-state

# Move state files there
mv /root/.hermes/scripts/.lfj-aae-state.json /var/lib/gentech/hermes-state/
mv /root/.hermes/scripts/.cmc-watchlist-state.json /var/lib/gentech/hermes-state/ 2>/dev/null || true

# Symlink back for backward compatibility
ln -s /var/lib/gentech/hermes-state/.lfj-aae-state.json /root/.hermes/scripts/.lfj-aae-state.json
ln -s /var/lib/gentech/hermes-state/.cmc-watchlist-state.json /root/.hermes/scripts/.cmc-watchlist-state.json 2>/dev/null || true

# Symlink for each profile
for profile in yoyo dmob desmond; do
  ln -sf /var/lib/gentech/hermes-state/.lfj-aae-state.json "/root/.hermes/profiles/${profile}/home/.hermes/scripts/.lfj-aae-state.json"
  ln -sf /var/lib/gentech/hermes-state/.cmc-watchlist-state.json "/root/.hermes/profiles/${profile}/home/.hermes/scripts/.cmc-watchlist-state.json" 2>/dev/null || true
done
```

## Post-Symlink Validation

Run this verification after symlinking (as each agent):
```bash
#!/bin/bash
# verify-state-symlinks.sh
SHARED="/root/.hermes/scripts/.lfj-aae-state.json"
for profile in yoyo dmob desmond; do
  PROFILE_LINK="/root/.hermes/profiles/${profile}/home/.hermes/scripts/.lfj-aae-state.json"
  if [ -L "$PROFILE_LINK" ]; then
    TARGET=$(readlink -f "$PROFILE_LINK")
    if [ "$TARGET" != "$SHARED" ]; then
      echo "❌ ${profile}: points to $TARGET (expected $SHARED)"
      exit 1
    else
      echo "✅ ${profile}: symlink correct"
    fi
  else
    echo "⚠️  ${profile}: not a symlink (regular file or missing)"
    exit 1
  fi
done
echo "✓ All profiles share same state file"
```

**Test after script writes**: Run `d5-master-cron.py` as two different profiles simultaneously, then verify both read the same `last_position_value` from the state file.

## Cron Integration

After symlinking, restart any cron jobs that depend on state to ensure they read from the shared location on next run:
```bash
# List Hermes cron jobs for this agent
hermes cron list | grep d5

# Graceful restart (wait for current run to finish)
hermes cron disable <job-id>
sleep 60
hermes cron enable <job-id>
```

## Rollback

If symlinks break:
```bash
# Remove symlink and restore backup
rm /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-state.json
cp /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-state.json.bak-* \
   /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-state.json
```

## Related

- Ground truth protocol: `references/ground-truth-protocol.md`
- Handoff task: `09-Green Room/active-handoffs/2026-05-02-d5-milestone-enhancement-dmob.md`
- Incident report: `08-Daily/2026-05-03.md` (Script Discrepancy Incident section)
