# 2026-05-03 — Mess Hall Context

## Flags Raised

🔴 **CRITICAL: Nous OAuth session revoked** — Data collection pipeline offline
- Token expired 18:28 UTC; refresh script `refresh_nous_oauth.py` cannot recover (returns `needs_reauth: true`)
- **Action:** DMOB ran `hermes model` to re-authenticate Nous provider (completed in GenTech Labs)
- Impact: Kite AI hackathon checks, LayerZero monitor, social monitors all failing with 401 errors
- Mitigation: **Silent mode implemented** — OAuth refresh cron now exits `0` when `needs_reauth=true` (expected state, not an alert). Only unexpected errors trigger Telegram notifications.
- Full incident log: `00-HQ/Operations/Infrastructure-Issues.md`

## Coordination Notes

- **Fix deployed:** All agent profile scripts (`gentech`, `yoyo`, `desmond`, `dmob`) updated to silent mode. Documentation updated in `00-HQ/03-Projects/Proactive-Nous-OAuth-Refresh.md`.
- No other blockers or urgent items at this time.
- Watchdog will verify recovery on next cycle; silent mode prevents noise on future expiry events.
