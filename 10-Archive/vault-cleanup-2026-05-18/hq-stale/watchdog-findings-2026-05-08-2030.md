# Watchdog Findings — 2026-05-08 2030 UTC

## Gateways
All four agents confirmed running (stable PIDs since May 07/08):
- YoYo: PID 427301
- DMOB: PID 426988
- Desmond: PID 426716
- Gentech: PID 442001

## Cron Job Status
Pre-existing errors unchanged:
- DMOB Sunday Skill Update Check: `Refresh session has been revoked` (since May 3)
- Mess Hall — Pre-Shift: `HTTP 429 quota exhausted` (since May 6)
- Weekly Skills Update Check: `401 invalid API key` (since May 3)
- Token Usage Weekly Audit: `last=None` (next scheduled: Sun May 10 15:00)

All other jobs across all four agents: OK.

## Gateway Logs
No errors in the last hour for any agent.

## Cron Logs
No errors for any agent.

## Changes from Previous Run (2020)
No changes. All state identical.
