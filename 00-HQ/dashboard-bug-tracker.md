# 🐛 Dashboard Bug Tracker

> Every bug encountered, documented, and fixed across all Gentech dashboards.
> We're the QA team AND the dev team — if it broke, it goes here.

---

## Format

| # | Date | Dashboard | Severity | Bug Description | Root Cause | Fix Applied | Status |
|---|------|-----------|----------|-----------------|------------|-------------|--------|

**Severity Levels:**
- 🔴 **Critical** — Dashboard broken, data wrong, deploy failed
- 🟡 **Medium** — Visual glitch, stale data, minor UX issue
- 🟢 **Low** — Cosmetic, polish, nice-to-have

---

## Bugs Log

| # | Date | Dashboard | Severity | Bug Description | Root Cause | Fix Applied | Status |
|---|------|-----------|----------|-----------------|------------|-------------|--------|
| 1 | 2026-06-14 | Hub | 🔴 Critical | Hub showing stale DeFi values ($16.89) instead of live data ($44.74) | Browser cache + no cache buster on fetch | Added `?t=Date.now()` cache buster to `fetchLiveData` | ✅ Fixed |
| 2 | 2026-06-14 | DeFi | 🔴 Critical | CSS theme (AVAX red/black) not applying — green persisted | `applyTheme()` JS cascade overwriting CSS variables | Added `!important` locks on CSS variable declarations | ✅ Fixed |
| 3 | 2026-06-14 | DeFi | 🟡 Medium | Dashboard tab showed Agent Scout (deprecated) instead of Market Intelligence | Template not rebuilt after module swap | Rebuilt `defi-template.json` with new component mappings | ✅ Fixed |
| 4 | 2026-06-14 | DeFi | 🟡 Medium | Hub embedded tab missing milestone injection | Milestones hardcoded in standalone only | Injected milestone summary directly into `hub.html` DeFi tab | ✅ Fixed |
| 5 | 2026-06-14 | Cron | 🟡 Medium | Portfolio Health Check and Fed Event Reminder both firing at 12:00 UTC | No stagger on overlapping hourly jobs | Shifted Fed Event Reminder to 1pm ET (+1h offset) | ✅ Fixed |
| 6 | 2026-06-14 | Cron | 🟡 Medium | Cron Health Monitor and Context Snapshot colliding at 00/06/12/18 UTC | Interval jobs not offset from scheduled jobs | Applied +6 minute stagger to Context Snapshot | ✅ Fixed |
| 7 | 2026-06-14 | DeFi | 🔴 Critical | LP curve shape showed Convergent instead of Bidirectional after rebalance | `defi-data.json` shape field not updated | Updated shape to "bidirectional" with new bin depths | ✅ Fixed |
| 8 | 2026-06-14 | DeFi | 🟡 Medium | Deployed HTML files still showing old range (6.43–6.59) after update | Git push didn't trigger Pages rebuild / CDN cache | Re-pushed with updated commit, verified with cache-busted curl | ✅ Fixed |
| 9 | 2026-06-14 | DeFi | 🟡 Medium | `.lfj-aae-config.json` and `defi-master-cron.py` had stale range values | Config files not updated during dashboard rebalance | Updated all config files to 6.30–6.55 bidirectional | ✅ Fixed |
| 10 | 2026-06-14 | DeFi | 🟢 Low | No Fisher tier in milestone ladder | Milestone config only went up to Warlord | Added Fisher ($100/day) and Sovereign ($200/day) tiers | ✅ Fixed |

---

## Recurring Patterns (Watch For)

1. **Cache busting** — Every `fetch()` call needs `?t=Date.now()` or browser serves stale HTML
2. **CSS variable conflicts** — Dashboard engine's `applyTheme()` overrides custom CSS; always use `!important`
3. **Config sync** — When updating `defi-data.json`, also update `.lfj-aae-config.json`, `defi-master-cron.py`, and `defi-lp-config.env`
4. **GitHub Pages CDN** — Changes take 1-5 min to propagate; always verify with cache-busted URL
5. **Template mapping** — Component swaps require updating `*-template.json` AND the HTML file

---

## Open Bugs

_None currently. All 10 resolved._

---

*Last updated: 2026-06-14*
