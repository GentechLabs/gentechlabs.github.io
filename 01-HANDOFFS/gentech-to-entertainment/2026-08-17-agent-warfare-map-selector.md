# From Gentech — 2026-08-17

## ✅ Shipped: Agent Warfare — Procedural Map Selector (Main Menu)

**Item:** #23 Agent Warfare — Procedural Map Generation (enhancement)
**Group:** entertainment (built on VPS cloud lane)

### What shipped
The main menu now has a **PROCEDURAL MAP** selector row with 6 named presets:
- **Static Market** (hand-authored default, no seed)
- **Sector-7** (seed 7)
- **Warehouse** (seed 42)
- **Refinery** (seed 1337)
- **Outpost** (seed 2026)
- **Arena** (seed 99)

The selected map's seed flows from the menu → `window.__GAME_CONFIG__.mapSeed` → world generation (`src/world/index.js` now resolves seed from config first, then `?mapseed=NUM` URL param as fallback). This surfaces the previously URL-only `?mapseed` feature into the player-facing UI — the natural next step flagged in the 2026-08-12 entertainment return.

### Verification
- `npm run build` — clean (3.42s)
- `node --check` on all 3 modified source files — OK
- Deployed to `/var/www/arcade/cabinet/agent-warfare/`
- Live verified: `arcade.gentechlabs.net/cabinet/agent-warfare/` HTTP 200, served bundle contains `mapSeed`, `PROCEDURAL MAP`, `Static Market` markers
- World seed resolution confirmed in served bundle (`mapseed` → `cfgSeed ?? URL param` logic present)
- Committed + pushed: `2e7c528` on `ProtoJay4789/agent-warfare` main

### Files changed
- `src/app/MainMenu.js` — added MAP_PRESETS + selector row + `getMapSeed()`
- `src/app/App.js` — `_bootEngine()` now passes `mapSeed` into `__GAME_CONFIG__`
- `src/world/index.js` — seed resolution order: config → URL param → static

### Notes
- `?mapseed=NUM` deep-links still work (backward compatible).
- Capture harness (`?capture=1`) unaffected — it auto-boots without the menu, so `__GAME_CONFIG__.mapSeed` is undefined and falls through to URL param/static.
- Queue #23 note updated with the enhancement.
