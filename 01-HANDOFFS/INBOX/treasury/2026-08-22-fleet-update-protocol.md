# Fleet Hermes Update — New Protocol

**From:** Entertainment (Pixel)
**To:** All agents / groups
**Date:** 2026-08-22
**Status:** open

## What's needed
Adopt the **fleet-update** protocol so that when Hermes is updated, ALL group
gateways restart together — no agent gets left behind on old code.

## The problem (root cause)
All profiles share ONE Hermes install at `/usr/local/lib/hermes-agent`, so
`hermes update` updates the code once. But each profile's gateway is a SEPARATE
process that must be restarted to load the new code. On the last update, Pixel's
gateway never restarted — it stayed 9 commits behind while the code updated.

## The fix
A fleet-update script that updates the shared code ONCE, then restarts EVERY
profile gateway so the whole fleet picks up the update together.

```bash
# Canonical location (vault)
/root/vaults/gentech/00-System/agent-profiles/fleet_update.py

# Check mode (no changes) — shows versions + gateway state
python3 fleet_update.py --check

# Full update: update code + restart ALL gateways
python3 fleet_update.py

# Restart gateways only (skip code update)
python3 fleet_update.py --restart-only
```

## Context / files
- Script: `00-System/agent-profiles/fleet_update.py` (vault, canonical)
- Profiles covered: gentech, gentech-treasury, gizmo, pixel
- Related: `hermes-agent` skill (update workflow), `hermes-maintenance-scripts` (vault→runtime deploy pattern)

## Action for you
On your next wake-up, note that fleet updates are now coordinated via
`fleet_update.py`. When Jordan says "update Hermes," run the fleet script (or
`--restart-only` if only gateways need restarting) rather than updating just
your own profile.
