# YoYo — Specialist Context

## Current State (Updated 2026-05-07)
- **Role**: Head of Strategies — DeFi analysis, portfolio strategy, LP monitoring
- **Status**: On-demand only (orchestrator pattern)
- **Home Group**: GenTech Strategies (-1002916759037)

## Active Projects
- **DeFi Milestone Tracker**: Running, monitoring LP positions
- **Token Watchlist**: Active monitoring of portfolio tokens
- **x402 Infrastructure**: Research complete, tier list published

## Key Files
- Config: `/root/.hermes/profiles/yoyo/config.yaml`
- Scripts: `/root/vaults/gentech/Strategies/scripts/`
- Watchlist: `/root/vaults/gentech/Strategies/cron-watchlist-config.md`
- LP Config: `/root/.hermes/scripts/.lfj-aae-config.json`

## Cron Jobs
- `Defi Milestone`: Every 10 min (6-23 UTC) — OK
- `Omni-Summary`: Daily 11:30 UTC — FAILING (auth)
- `Portfolio Site`: Daily 13:00 UTC — FAILING (auth)
- `College.xyz`: Daily 12:00 UTC — FAILING (auth)

## Blockers
- Auth revoked for 3 cron jobs — needs `hermes model` re-auth
- DeFi Milestone script path issue (historical)

## Preferences
- Numbers-first, risk-aware, direct
- Always state assumptions before conclusions
- Build scenario analysis, never single-point forecasts
