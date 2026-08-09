# Agent Warfare — Item #8 SHIPPED (2026-08-08)

**Item:** Agent Warfare — Agent Archetypes/Classes (Sniper, Scout, Heavy, Medic, Engineer)
**Group:** entertainment
**Status:** ✅ SHIPPED by gentech (nightly build session)

## What shipped
- **`src/ai/archetypes.js`** — 5 combat role profiles (Sniper/Scout/Heavy/Medic/Engineer), each a stat profile + behavior flags. Unknown names fall back to baseline (never throw).
- **`src/ai/agent.js`** — archetype-driven health, speed, weapon range/damage/fire rate, mag size, reload, retreat threshold. Added `_support()` (medic heals wounded squadmates) + `_deploy()` (engineer deploys cover).
- **`src/ai/nav.js`** — `CoverMap.add()` for dynamic engineer-deployed cover.
- **`src/ai/index.js`** — balanced archetype mix across garrison squads.
- **`src/app/`** — MainMenu, CharacterSelect, MatchEnd state machine (menu flow).
- **`src/data/`** — 8 playable characters + 4 game modes (TDM, Domination, Duel, Practice).

## Verification
- `node src/ai/archetypes.test.mjs` → **PASS (0 failures)**
- `node --check` on all new files → OK
- `npm run build` → **✓ built in 4.54s**
- Deployed to `/var/www/arcade/cabinet/agent-warfare/`
- Origin + public URL both serve new content (content check, not just status)

## Committed
- `82b1957` pushed to `origin/main` (github.com/ProtoJay4789/agent-warfare)

## Next for entertainment
- **#9 Procedural Map Generation via text-to-cad** — still pending, Jordan TOP PRIORITY. Map gen pipeline (build123d → STEP → GLB → Three.js) is the natural next build.
- Character select + menu system is wired; gameplay tuning (Jordan: "must be crispy") is the ongoing focus.
