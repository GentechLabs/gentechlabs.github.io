# Arcade Games Audit — 2026-08-15

> Compatibility audit of all GenTech Arcade games: mobile/desktop, performance,
> menus, pause, completeness, glitches. Source: live VPS files + local repos.
> **UPDATED 2026-08-16: P0 fixes shipped (3D lobby deployed + wired, Tennis mobile+pause, VKT pause).**

## Summary Table

| Game | Mobile | Desktop | Menu | Pause | Perf | Completeness | Verdict |
|------|--------|---------|------|-------|------|--------------|---------|
| **Super Arcade Tennis** (root) | ✅ Touch+SWING (Aug 16) | ✅ WASD+Space | ❌ none | ✅ Esc/P (Aug 16) | ✅ OK | 🟡 Playable, needs menu | **Fix: menu (remaining)** |
| **Agent Warfare** | ✅ Touch+Gamepad | ✅ Full | ✅ Full | ✅ Escape | ✅ quality tiers | ✅ Most complete | **Ship-ready** |
| **King's Gambit** | ⚠️ React, needs check | ✅ | ✅ | ⚠️ | ✅ | ✅ | **Verify mobile** |
| **Visual Kei Tap** | ✅ Touch+Mouse | ✅ Keys | ✅ Start/Results | ✅ Esc/P (Aug 16) | ✅ | ✅ | **Ship-ready** |
| **3D Lobby** | ⚠️ | ✅ | N/A | N/A | ✅ | ✅ DEPLOYED + real games (Aug 16) | **Live at /lobby/** |

---

## 1. Super Arcade Tennis (arcade.gentechlabs.net root)

**File:** `/var/www/arcade/index.html` (27.9KB, single file, Three.js 0.170 CDN)

### ✅ What works
- Desktop: WASD move, SPACE swing/serve, Q+SPACE chain power shots
- Chain power system (BTC/ETH/SOL coins) — polished
- AI opponent, score, game-over screen with restart
- Resize handler, pixelRatio capped at 2, shadow maps 1024 (perf OK)

### ❌ Issues
1. **NO mobile input at all** — only `keydown`/`keyup` keyboard listeners. No touch, no pointer, no gamepad. **Unplayable on phones/tablets.** This is the arcade ROOT — first thing visitors see.
2. **No main menu** — game boots straight into play. No title screen, no mode select, no instructions screen.
3. **No pause** — no Escape/P key handler. Single-player can't pause mid-rally.
4. **No touch controls** — even though it's the landing page.

### Fix priority: HIGH (it's the arcade root)

---

## 2. Agent Warfare (arcade.gentechlabs.net/cabinet/agent-warfare/)

**Source:** `/root/agent-warfare/` (Vite build, Three.js 0.180)

### ✅ What works — MOST COMPLETE GAME
- **Full menu system**: `App.js` state machine — MainMenu → CharacterSelect → Game → MatchEnd → MainMenu
- **Pause menu**: `PauseMenu` class, Escape key + gamepad Start (btn 9), quality settings
- **Mobile**: `TouchControls` (virtual joystick + touch look + action buttons), auto-detects touch devices
- **Gamepad**: full button/axis mapping
- **Perf**: quality tiers (`?q=ultra`), prewarm, graceful boot-failure message for mobile WebGL
- **5 archetypes** (Sniper/Scout/Heavy/Medic/Engineer), procedural maps (`?mapseed=NUM`)

### ⚠️ Notes
- Boot failure message says "connect a controller to your phone" — implies mobile WebGL may be heavy. Needs real-device test.
- 12MB cabinet dir — large. Consider code-splitting/lazy-loading for mobile.

### Verdict: **Ship-ready.** This is the flagship. Only real-device mobile perf test needed.

---

## 3. King's Gambit (arcade.gentechlabs.net/cabinet/kings-gambit/)

**File:** `/var/www/arcade/cabinet/kings-gambit/index.html` (1.3KB loader → Vite React build)

### ✅ What works
- Cinematic 3D chess, torch-lit castle hall, computer opponent + friend mode
- React app with engine.worker (chess AI off main thread — good perf)
- OG meta, favicon, robots.txt

### ⚠️ Needs verification
- **Mobile**: React app — need to confirm touch input + responsive layout. Not audited in depth (minified bundle).
- **Pause**: chess is turn-based so pause is less critical, but need to confirm menu/back exists.
- **Menu**: need to confirm there's a start/mode screen.

### Fix priority: MEDIUM — verify mobile + menu on real device.

---

## 4. Visual Kei Tap (arcade.gentechlabs.net/visual-kei-tap/)

**File:** `/var/www/arcade/visual-kei-tap/index.html` (17.3KB, single file)

### ✅ What works
- **Mobile**: `touchstart` (3-lane tap by x-position) + `mousedown` + keyboard (A/S/D)
- **Menu**: start screen (`#s`) with track select, results screen (`#r`) with score/accuracy
- **Perf**: single file, canvas, viewport-fit-cover, touch-action none — clean

### ❌ Issues
1. **No pause** — `pausedAt` variable exists but no Escape/pause key handler. Keydown only handles A/S/D during play. Can't pause mid-song.

### Fix priority: LOW-MEDIUM — add Escape pause.

---

## 5. 3D Lobby (NOT DEPLOYED — vault only)

**File:** `/root/vaults/gentech/10-Labs/gentech-arcade-3d-lobby/index.html` (621 lines)

### ❌ Critical issues
1. **NOT DEPLOYED** — `/lobby/` and `/3d-lobby/` return 200 but serve Super Arcade Tennis (nginx fallback). The lobby only exists in the vault.
2. **Placeholder games** — GAMES array = Poker, Blackjack, Connect Four, Tic-Tac-Toe, Backgammon, Pong. **NONE of these are the real games** (Tennis, Agent Warfare, King's Gambit, Visual Kei Tap).
3. **Join button is a mockup** — `gp-join` just shows `alert("Joining... x402 payment flow incoming")`. Doesn't link to any real game.
4. **ARC token economy is fictional** — entry fees, prize pots, leaderboard are hardcoded demo values.

### Fix priority: HIGH for the vision — this is the walkable lobby centerpiece. Must:
- Deploy to arcade root (or /lobby/)
- Replace GAMES array with the 4 real games + real URLs
- Wire gp-join to `window.location` of each real cabinet
- Add anime water/grass environment (Stylized Components)

---

## Consolidated Fix List (build order)

### P0 — Arcade root experience
1. **Deploy 3D lobby** to arcade root, wire the 4 real games to cabinets (replaces placeholder GAMES array) — **DONE 2026-08-16** (deployed to `/lobby/`, wired to real cabinets)
2. **Add mobile touch to Super Arcade Tennis** (it's the current root — unplayable on mobile) — **DONE 2026-08-16** (virtual joystick + SWING button)
3. **Add menu + pause to Super Arcade Tennis** — **pause DONE 2026-08-16**; menu still TODO

### P1 — Polish
4. **Add pause to Visual Kei Tap** (Escape key) — **DONE 2026-08-16**
5. **Verify King's Gambit mobile + menu** on real device — TODO
6. **Real-device mobile perf test on Agent Warfare** (12MB bundle) — TODO

### P2 — Vision
7. **Anime environment** (Stylized Components water/grass) into the lobby
8. **Agent spectator mode** — agents playing in the lobby
9. **Meta glasses pass** — bundle lobby for 600×600 display

---

## Files Audited
- `/var/www/arcade/index.html` (Tennis)
- `/var/www/arcade/cabinet/agent-warfare/` (Agent Warfare, source at `/root/agent-warfare/`)
- `/var/www/arcade/cabinet/kings-gambit/` (King's Gambit)
- `/var/www/arcade/visual-kei-tap/index.html` (Visual Kei Tap)
- `/root/vaults/gentech/10-Labs/gentech-arcade-3d-lobby/index.html` (3D Lobby)
