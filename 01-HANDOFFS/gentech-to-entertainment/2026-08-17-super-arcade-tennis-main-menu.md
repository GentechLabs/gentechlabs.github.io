# Handoff — Super Arcade Tennis Main Menu (#14) → Entertainment

**Date:** 2026-08-17
**From:** Gentech (nightly build)
**Status:** ✅ SHIPPED + verified live

## What shipped
The last open P0 from the arcade audit is closed. Super Arcade Tennis (`arcade.gentechlabs.net` root) no longer boots straight into play — it now opens on a proper main menu.

## Changes (all in `/var/www/arcade/index.html`, single-file Three.js)
1. **Title screen** — "SUPER ARCADE TENNIS" + "GenTech Labs · Agent Arcade" subtitle, gradient text on the court backdrop.
2. **Mode select** — two modes:
   - **Quick Match** (default) — first to 6.
   - **Tiebreak** — first to 10.
   - Mode sets `state.targetScore` (6 or 10), which now gates the win condition.
3. **▶ PLAY** button — starts the game. Also **Enter / Space** on the menu starts it (with preventDefault so it doesn't also trigger a serve).
4. **How to Play** overlay — goal, movement, swing/serve, chain power-shots (BTC/ETH/SOL), pause. Reached via "How to Play" → "← BACK".
5. Game boots into a **non-started state** — `state.started=false`, update loop early-returns to render the court behind the menu without running physics/AI. `togglePause` is gated behind `state.started` so Esc/P can't pause from the menu.

## Verification (all real)
- `node --check` on the extracted module: **SYNTAX OK**.
- Static check: all 22 `getElementById` ids referenced in JS resolve in the HTML — **none missing**.
- Both `data-mode` buttons present (`quick`, `tiebreak`).
- Live: `arcade.gentechlabs.net/` → **HTTP 200**, menu markers present on the served page.
- Queue `build_queue.json` **valid JSON**, #14 marked shipped 2026-08-17.

## Notes for Entertainment / Pixel
- Mobile: menu buttons are pointer-events:auto so they tap reliably; the How-to overlay + mode buttons are all touch-friendly.
- Restart (`▶ PLAY AGAIN` on game-over) now calls `startGame(state.mode)` so it preserves the selected mode.
- No further P0s remain in the arcade audit — cab #1 is feature-complete on the front end. The only outstanding arcade work is the x402 crypto-payment wiring (#1), which is Jordan-gated (needs wallet/funds).
