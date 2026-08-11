# From HQ → Labs — GenTech Hub PWA Build (Aug 11)

**Source:** Jordan greenlight (Aug 11) + Treasury handoff `2026-08-11-pwa-stand-alone-decision.md`
**Status:** DECIDED + spec'd + template built. Ready to build.
**Build queue:** #55 (high, assigned labs)

## The decision
Unify all GenTech surfaces into **ONE installable PWA shell** ("GenTech Hub"), NOT separate PWAs, NOT one blob. Shared shell + distinct module screens. Makes "the autonomous agent economy in one installable app" tangible.

## Spec (authoritative)
`09-Green Room/specs/gentech-hub-pwa-architecture.md`

## Template (DONE — reusable, one-command)
`10-Labs/pwa-template/` — proven pattern from the Steward PWA:
- `manifest.json` (scope `/`, theme #8b5cf6, standalone)
- `sw.js` (cache-first shell, network-first `<surface>-state.json`)
- `index.html` (dark theme, Inter + JetBrains Mono, cards grid, **chat-bridge FAB** → `/bridge/`)
- `icons/` (192 + 512, shield design)
- `README.md` — one-command scaffold (sed fill placeholders → deploy to `/var/www/gentechlabs/<Surface>/`)

## Build order
1. **Hub home/launcher** at `/` (index.html + root manifest.json + root sw.js) — the shell that ties modules together
2. **Refactor surfaces into the shell** — Steward is DONE (template); add Arcade, Cookbook, Travel, Meta Ray-Ban
3. **Shared wallet + dept-routed bridge** at Hub level (`?dept=strategies|entertainment|finance`)

## Key details (from Treasury)
- Bridge: same-origin `/bridge/` nginx proxy (port 8765 NOT publicly exposed — must stay proxied). Pattern: `POST /bridge/api/session` → `POST /bridge/api/chat?dept=`
- State file pattern: each module reads `<surface>-state.json` refreshed by cron → live data, no backend
- Live surfaces to wrap: `/var/www/gentechlabs/Treasury/` (done), `/Gaming/`, `/hub/` (per-user family hub — leave intact), plus Cookbook/Travel/Ray-Ban to create

## Verify after build
```bash
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/index.html      # 200
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/manifest.json   # 200
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/sw.js           # 200
```
Plus each surface: `https://gentechlabs.net/<Surface>/index.html` → 200.

## Handoff protocol
Report back via `01-HANDOFFS/labs-to-gentech/` when the shell + first surface (Arcade or Cookbook) is live.
