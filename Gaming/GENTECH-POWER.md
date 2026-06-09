---
title: GenTech Power — POE2 Build Guide System
created: 2026-06-09
status: active
tags: [POE2, build, gaming, GenTech Power]
---

# GenTech Power — POE2 Build Guide System

## What Is GenTech Power?

Shared build tracking system for GenTech team members playing POE2. Tracks skills, gear, ascendancy, and progression. Updated by agents based on player input.

## How It Works

1. **Player tells agent what changed** — "I chose Invoker ascendancy" or "I swapped supports on Thunderstorm"
2. **Agent updates the JSON** in `Gaming/poe2-[class].json`
3. **Dashboard updates** — `Gaming/poe2-dashboard.html` reflects current state
4. **Agent gives advice** — next upgrades, synergies, things to watch for

## Players

| Player | Class | Build | Status |
|--------|-------|-------|--------|
| Jordan | Monk | Lightning Invoker | Active |
| Vanito | TBD | TBD | Pending |

## Files

- `Gaming/poe2-monk.json` — Jordan's Monk build data
- `Gaming/poe2-warrior.json` — Vanito's build (when ready)
- `Gaming/poe2-dashboard.html` — Visual dashboard
- `Gaming/GENTECH-POWER.md` — This file

## Update Protocol

When a player says what changed:
1. Update the JSON file with new skill/ascendancy/gear
2. Update the dashboard if visual changes needed
3. Give 2-3 next steps for the build
4. Note any synergies with the new choice

## Command

Just tell the agent:
- "Update my build" + what changed
- "What should I do next?"
- "Check my build" — agent reviews current state and suggests upgrades
