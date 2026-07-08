# DeFi LP Monitor — Consolidation Audit

**Date:** July 8, 2026
**Owner:** Gentech (VPS) — this is VPS-side infra
**Status:** Audit complete, configs documented

---

## Current State

| File | Location | Purpose |
|------|----------|---------|
| `defi-lp-config.env` | `HQ/config/` | Wallet + pool + position config |
| `.lfj-aae-config.json` | `./` (vault root) | AAE strategy config |
| `.lfj-aae-config.json` | `Strategies/scripts/` | Script-local copy |
| `.lfj-position-tracker.json` | `Strategies/scripts/` | Position tracking state |
| `defi-lp-consolidated.py` | `Strategies/scripts/` | Main monitor script (511 lines) |

## Data Flow

```
defi-lp-config.env ──► .lfj-aae-config.json ──► defi-lp-consolidated.py
                                                      │
                                                      ▼
                                              DexScreener API
                                                      │
                                                      ▼
                                              defi-data.json
                                              (GitHub Pages)
```

## What Needs Consolidation

1. **Config files:** 3 copies of `.lfj-aae-config.json` — should be 1 source of truth
2. **State file:** `.lfj-position-tracker.json` lives in `Strategies/scripts/` — should be in `HQ/config/`
3. **Script paths:** Hardcoded to `/root/ProtoJay4789.github.io/` — should use env vars
4. **Dashboard data:** `defi-data.json` path is VPS-specific

## Recommendation

This is **Gentech's domain** (VPS-side infra, cron jobs, DeFi ops). The consolidation is straightforward but needs VPS access to test. Hand off to Gentech with the plan:

1. Move all configs to `HQ/config/`
2. Single `.lfj-aae-config.json` source of truth
3. Update script to use env vars for paths
4. Test on VPS before deploying
