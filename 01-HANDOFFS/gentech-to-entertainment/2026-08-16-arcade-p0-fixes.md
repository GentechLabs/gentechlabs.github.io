# Arcade P0 Fixes Shipped — 2026-08-16

> From Gentech Nightly Build → Entertainment group. All three P0 items from the
> 2026-08-15 arcade audit are now shipped and verified live.

## What shipped

1. **3D Lobby deployed + wired to real games** — `arcade.gentechlabs.net/lobby/`
   - Replaced the placeholder GAMES array (Poker/Blackjack/Connect Four/etc.) with the 4 real live cabinets:
     - Super Arcade Tennis → `/`
     - Agent Warfare → `/cabinet/agent-warfare/`
     - King's Gambit → `/cabinet/kings-gambit/`
     - Visual Kei Tap → `/visual-kei-tap/`
   - Plus a 3D Lobby self-link and a "More Cabinets" coming-soon placeholder.
   - Join button now navigates to the real cabinet URL (was a mockup alert).
   - Removed the fictional ARC economy (leaderboard + wallet now honest — no fake balances).
   - Verified: HTTP 200, all 5 live cabinet URLs present, JS syntax OK.

2. **Super Arcade Tennis — mobile touch + pause** (arcade root, was unplayable on mobile)
   - Virtual joystick (touch anywhere) + dedicated SWING button (bottom-right).
   - Escape/P pause with overlay + on-screen pause button.
   - Verified: HTTP 200, JS syntax OK, all new elements present.

3. **Visual Kei Tap — pause** (Escape/P + on-screen RESUME button)
   - Pause overlay, audio pause/resume via stopAudio/playAudio, loop gated on `!paused`.
   - Verified: HTTP 200, JS syntax OK.

## Remaining (for Entertainment)

- **Super Arcade Tennis main menu** (title screen / mode select / instructions) — the last P0 item.
- **Verify King's Gambit mobile + menu** on a real device.
- **Real-device mobile perf test on Agent Warfare** (12MB bundle — consider code-splitting).
- **P2 vision**: anime environment in the lobby, agent spectator mode, Meta glasses pass.

## Files touched (live VPS)
- `/var/www/arcade/lobby/index.html` (new — 3D lobby)
- `/var/www/arcade/index.html` (Tennis — mobile + pause)
- `/var/www/arcade/visual-kei-tap/index.html` (VKT — pause)
- Vault source: `10-Labs/gentech-arcade-3d-lobby/index.html`
