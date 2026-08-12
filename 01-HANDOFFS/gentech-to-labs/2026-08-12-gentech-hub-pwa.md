# Gentech → Labs — 2026-08-12

## Shipped this session

### #55 GenTech Hub PWA — Hub launcher LIVE
- **What:** Built the installable Hub PWA shell at the web root.
- **Files deployed to `/var/www/gentechlabs/`:**
  - `hub-launcher.html` — the Hub home/launcher (the "one app" entry point)
  - `manifest.json` — shared manifest, scope `/`, standalone, theme `#8b5cf6`
  - `sw.js` — shared service worker (network-first for state/data JSON, cache-first for shells)
  - `icons/icon-192.png` + `icon-512.png` (copied from pwa-template)
- **Verified:** all 4 assets serve HTTP 200 on gentechlabs.net; manifest is valid JSON; launcher links Treasury/Steward, Arcade, Yield Rainbow, Vanito/KAGE, Arc x402, Hub Engine.
- **Launcher URL:** https://gentechlabs.net/hub-launcher.html
- **Not yet built (marked SOON in launcher):** Cookbook, Travel, Meta Ray-Ban — these surfaces don't exist yet as standalone pages. When built, update the launcher links.

## Next steps for Labs (per spec build order)
1. Refactor remaining surfaces into the shell (Steward already done; add Arcade, Yield Rainbow, Vanito as modules).
2. Wire shared wallet + dept-routed bridge at Hub level.
3. Consider making `/` (index.html) redirect to the launcher OR keep the AAE Builder landing page and add a prominent "Open Hub" button — Jordan's call.

## Group returns consumed
- **labs → gentech:** #29, #52, #19, #2, #30, #1, #6, #48, #49 — all already marked shipped in queue (verified). No new application needed.
- **forge → gentech:** #61, #59, #60, #66, #62, #65 — from Jul 24 session, not in current queue (ids 1-55). Already handled/archived.
