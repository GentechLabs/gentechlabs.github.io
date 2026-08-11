## From Treasury — PWA Stand-Alone Decision (Jordan → JinTech)

**Date:** Aug 11, 2026

### The decision Jordan wants to discuss with JinTech
> "Now that I know we can pretty much build these out as stand-alones and tie them to our website... Let's talk about making the other ones PWAs."

### What we proved (evidence, not theory)
The **Steward Command Center** is now a live, installable **PWA** — the proof-of-concept that stand-alone apps can be built and tied to the website. Jordan saw it working and wants to know if the **other GenTech surfaces** should get the same treatment.

### The recipe (reusable, proven today)
1. Build a self-contained HTML dashboard (dark theme, Inter + JetBrains Mono, purple/cyan, demo.gentechlabs.net look)
2. Add `manifest.json` (installable, standalone) + `sw.js` (offline cache) + app icons → **PWA installs to home screen like an app**
3. Serve it from `/var/www/gentechlabs/<Surface>/` → live at `gentechlabs.net/<Surface>/...`
4. (Optional) wire a web-bridge chat tab so it's **controllable from the site, not just Telegram**
5. Feed live data via a state producer + cron (heartbeat writes `steward-state.json`)

### Candidate surfaces to PWA-ify (JinTech's call on priority)
| Surface | Status | Notes |
|---------|--------|-------|
| **Treasury / Steward** | ✅ DONE | live at `gentechlabs.net/Treasury/` — the template |
| **Cookbook** | ⬜ candidate | Filipino recipes → Cincinnati subs |
| **Travel** | ⬜ candidate | flight research, Philippines trips |
| **Meta Ray-Ban** | ⬜ candidate | glasses integration |
| **Hub home** | ⬜ candidate | the PWA shell that ties it together |

### Key details for JinTech
- **Bridge fix landed:** chat tab now uses same-origin `/bridge/` nginx proxy (was broken `:8765`). This pattern makes any PWA controllable from the site.
- **State file pattern:** each PWA reads a `<surface>-state.json` refreshed by cron → live data without a backend.
- **Committed to:** hub repo `6cdb3c74` + vault.

### Open question
Does JinTech want to standardize this into a **PWA template/boilerplate** (so any future surface gets it in one command), or handle each surface ad-hoc? Jordan leaning toward template.

---

### 📝 Notes
- This is a **decision for HQ/CLI** — Jordan explicitly said "I got to talk to JinTech about that," so no build here until scoped.
- The Steward dashboard already ties in Cookbook/Travel/Ray-Ban as nav links; the PWA-ification of those surfaces is the follow-on.
- Tier toggle (Operator full-autonomy vs User recommend+confirm) baked into the Steward PWA — the multi-tier product story is ready to show.
