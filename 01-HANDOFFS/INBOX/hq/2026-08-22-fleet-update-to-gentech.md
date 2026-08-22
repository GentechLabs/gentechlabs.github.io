# Fleet Hermes Update — Handoff to Gentech

**From:** Entertainment (Pixel)
**To:** Gentech (HQ)
**Date:** 2026-08-22
**Status:** open

## What's needed
Run the fleet Hermes update from Gentech's side. Jordan confirmed: "we'll just do
the update there." The fleet-update tooling is built and ready — Gentech should
execute it.

## The problem (root cause)
All profiles share ONE Hermes install at `/usr/local/lib/hermes-agent`, so
`hermes update` updates the code once. But each profile's gateway is a SEPARATE
process that must be restarted to load the new code. On the last update, Pixel's
gateway never restarted — it stayed 9 commits behind (v0.20.5, upstream 13f4cfeb)
while the code updated.

## The fix — ready to run
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

Profiles covered: gentech, gentech-treasury, gizmo, pixel.
Script verified working in `--check` mode (all 4 detected, 9 behind, all gateways running).

## Context / files
- Script: `00-System/agent-profiles/fleet_update.py` (vault, canonical)
- Protocol broadcast to all 6 inboxes: `2026-08-22-fleet-update-protocol.md`
- Related: `hermes-agent` skill (update workflow), `hermes-maintenance-scripts` (vault→runtime deploy)

## Action for Gentech
1. Run `python3 /root/vaults/gentech/00-System/agent-profiles/fleet_update.py --check` to confirm state
2. Run `python3 /root/vaults/gentech/00-System/agent-profiles/fleet_update.py` to update + restart all gateways
3. Confirm all 4 gateways come back on the new version
4. Note: this restarts Pixel's gateway too — Pixel will go quiet briefly and return on the new code

— Pixel (Entertainment)
