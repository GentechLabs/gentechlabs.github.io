# GenTech Hub — Unified PWA Architecture Spec

**Status:** ✅ DECIDED (Jordan + JinTech, Aug 11, 2026)
**Decision:** Unify all GenTech surfaces into **ONE installable PWA shell** ("GenTech Hub") with each surface as a module/tab. NOT separate PWAs, NOT one blob.
**Proven template:** The Steward Command Center (`gentechlabs.net/Treasury/steward-dashboard.html`) — the working proof-of-concept.

---

## Why unify (the thesis)
Our thesis is the **autonomous agent economy**. Every surface is the same story told through a different lens:
- **Treasury / Steward** — agents settle and grow capital
- **Arcade** — agents play games (and will run them)
- **Cookbook** — agents do real-world kitchen tasks
- **Travel** — agents arrange trips
- **Meta Ray-Ban** — agents in wearable/ambient form

Separate PWAs fragment the story. One Hub makes "the agent economy in one installable app" tangible. One identity, one wallet, one chat bridge, one story.

## Architecture: shared shell + distinct modules

```
GenTech Hub  (ONE installable PWA)
│   index.html (launcher / home)
│   manifest.json      ← shared, scope "/"
│   sw.js              ← shared service worker
│   hub-state.json     ← shared state
│   /bridge/           ← same-origin nginx proxy to Hermes (chat)
│
├── /Treasury/   → Steward Command Center  (✅ LIVE — the template)
├── /Arcade/     → agent arcade
├── /Cookbook/   → Filipino recipes → Cincinnati subs
├── /Travel/     → flight research, Philippines trips
├── /rayban/     → Meta Ray-Ban glasses integration
```

**Rules:**
1. **One manifest.json** scoped to `/` — install once, all modules inside.
2. **One sw.js** — caches the shared shell + each module's shell; network-first for `<module>-state.json` (always fresh), cache-first for static shells.
3. **One chat bridge** — `/bridge/` nginx proxy → Hermes. Any module can talk to any department via `?dept=`.
4. **One wallet** — connect once at Hub level; modules read the shared wallet context.
5. **State file pattern** — each module reads `<surface>-state.json`, refreshed by a cron. Live data without a backend.
6. **Nav wiring** — each module already links to the others (Steward links Cookbook/Travel/Ray-Ban). The Hub home is the launcher that ties them together.

## The template (reusable, one command)
Standardize into a boilerplate so ANY future surface scaffolds in one command:
- `manifest.json` (name, short_name, icons, theme #8b5cf6, standalone)
- `sw.js` (offline cache + network-first state)
- `index.html` (dark theme, Inter + JetBrains Mono, purple/cyan — demo.gentechlabs.net look)
- `app-icons/` (192 + 512, shield design)
- `<surface>-state.json` (empty scaffold)
- bridge chat stub (FAB → `/bridge/api/session` → `/bridge/api/chat?dept=`)

## Build priority (JinTech recommendation)
1. **PWA boilerplate template** (the multiplier — every surface after this is fast)
2. **Hub home/launcher** (`index.html` at `/` — ties the modules together)
3. **Refactor existing surfaces into the shell** (Steward already done; add Arcade, Cookbook, Travel, Ray-Ban)
4. **Wire shared wallet + dept-routed bridge** at Hub level

## Files / locations
- Live surfaces: `/var/www/gentechlabs/<Surface>/` → `gentechlabs.net/<Surface>/`
- Hub root: `/var/www/gentechlabs/index.html` (+ manifest.json, sw.js at root)
- Hub repo: `gentechlabs.net` hub repo (same one that holds steward-dashboard.html)

## Handoff
Built by Labs per handoff protocol. JinTech scopes; Labs builds. Template first, then surfaces.
