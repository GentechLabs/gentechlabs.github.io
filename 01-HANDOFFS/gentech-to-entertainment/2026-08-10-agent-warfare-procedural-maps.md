# Agent Warfare — Item #9 SHIPPED (2026-08-10)

**Item:** Agent Warfare — Procedural Map Generation
**Group:** entertainment
**Status:** ✅ SHIPPED by gentech (nightly build session)

## What shipped
- **`src/world/procedural.js`** — seed-driven procedural layout generator (xoshiro128** RNG). Produces a balanced west/east row of buildings + market set pieces (stalls, jerseys, sandbag walls) per seed.
- **`src/world/index.js`** — if the URL carries `?mapseed=NUM`, the static `BUILDINGS`/`SET_PIECES` layout is swapped for the generated one before any world construction (live-binding splice/assign), so all subsystems see the new data.
- **Bug fixes over the prior in-progress commit:**
  - **Street-face orientation inverted** — `streetSide: 1` (+X) was being placed on the EAST row (x>0). Matches `layout.js` convention now: streetSide 1 sits on the WEST row (x<0), streetSide 3 on the EAST row (x>0). Otherwise doors/shopfronts would face AWAY from the street.
  - **Kerb encroachment** — building width was up to 16 at centre ±12.5, poking facades into the street. Constrained width ≤ 12 so the street-side inner edge stays ≥ 6.5 (flush with the kerb line), matching the static rows.
- **`src/world/procedural.test.mjs`** — determinism, 12-seed distinctness, orientation + kerb invariants, set-piece presence.

## Verification
- `node src/world/procedural.test.mjs` → **PASS (0 failures)**
- `node src/ai/archetypes.test.mjs` → **PASS (0 failures)**
- `npm run build` → **✓ built**
- Browser boot check: `?mapseed=42/7/0` → **0 page errors** (procedural IIFE runs at import without throwing)
- Deployed to `/var/www/arcade/cabinet/agent-warfare/`; origin + public CDN both serve the chunk containing the procedural code (content check, not just status)

## Committed
- `cbf85a0` pushed to `origin/main` (github.com/ProtoJay4789/agent-warfare)

## How to use
- Any `?mapseed=NUM` yields a distinct deterministic map. Seed 0 = static layout (unchanged).
- Natural next: surface map selection in the menu UI, and/or wire the text-to-cad (build123d → STEP → GLB) pipeline for named maps (urban courtyard, warehouse, desert outpost).
