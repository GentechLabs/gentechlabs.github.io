# KytyPS5 — Codebase Analysis & Contribution Plan
**Date:** Jul 15, 2026 | **Repo:** github.com/Nmzik/KytyPS5 | **Stars:** 854⭐ | **Latest:** v0.0.3

## ⚠️ Key Finding: Source Not Public

The GitHub repo contains **only binaries + documentation**. No C++/Vulkan source in any branch or tag. The actual emulator source is distributed inside the release ZIPs or kept private by the developer (Nmzik).

**Repo contents:**
- `README.md` — project docs
- `docs/screenshots/` — game screenshots (Disgaea 6, Cult of the Lamb, Silent Hill, etc.)
- `.github/ISSUE_TEMPLATE/` — issue templates
- `compatibility_db.json` (compat-db branch) — game compatibility status, currently 1 entry

**This means:** Direct code PRs are not possible. Our contributions must follow a different model.

## Release History

| Version | Date | Key Improvements |
|---------|------|------------------|
| v0.0.1 | Jun 9 | Initial release |
| v0.0.2 | Jul 3 | AJM audio emulation, AGC driver, shader recompiler, in-game for many titles |
| v0.0.3 WIP | Jul 11 | Virtual memory perf, SRT shader-binding, AMPR optimizations, GUI + compat DB |

## Open Issues (14 open, 4 closed)

### Quick-Win Opportunities (no source access needed):

| # | Title | Type | Action |
|---|-------|------|--------|
| #17 | Linux Support | Feature | Dev says "coming soon" — we can offer testing help |
| #12 | Teaming up with other emulators | Discussion | Engage with the community, offer collaboration |
| — | Compatibility DB | Data | Currently 1 entry — we can test games and submit PRs with results |

### Bug Reports (Forge testing required — needs Windows + GPU):

| # | Game | Issue |
|---|------|-------|
| #20 | [GAME BUG] | Unknown, opened 2 days ago |
| #16 | Astria Ascending | Needs testing |
| #15 | Hotline Miami | Needs testing |
| #14 | EA UFC 5 | Won't start |
| #11 | Dreaming Sarah | Graphical issue |
| #8 | GTA V | Needs testing |
| #7 | Neptunia ReVerse | Needs testing |
| #6 | Arkanoid Eternal Battle | Needs testing |
| #5 | Quake 2 | Needs testing |
| #4 | Silent Hill: The Short Message | Progress tracking |
| #3 | Void Terrarium | Progress tracking |
| #2 | Dreaming Sarah | Progress tracking |

## Contribution Strategy (Revised)

### Phase 1 — Relationship Building (Immediate, no Windows needed)
1. **Compatibility DB PRs** — test games, add results to `compatibility_db.json`
2. **Engage on issues** — help triage, ask good questions, show we're serious
3. **Star + watch** the repo, follow Nmzik's activity

### Phase 2 — Testing Pipeline (When Forge is on desktop)
1. Download v0.0.3 release
2. Test a curated set of games
3. File detailed bug reports with logs
4. Submit compatibility DB updates

### Phase 3 — Code Contribution (If source goes public)
1. Fork and build from source
2. Target: Linux port (issue #17), Vulkan fixes, UI improvements
3. Integrate with Emulation AI Companion stack

## Recommended First Move

**Submit a compatibility DB PR right now.** The DB has 1 entry. We can find test results from existing issues and add them. Quick, useful, zero Windows needed.
