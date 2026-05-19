# Watchdog Findings — 2026-05-09 0820 UTC

## Gateways
All four agents confirmed running (stable PIDs since May 07/08):
- YoYo: PID 427301
- DMOB: PID 426988
- Desmond: PID 426716
- Gentech: PID 442001

## Cron Job Status
Pre-existing errors unchanged:
- DMOB Sunday Skill Update Check: `error` (revoked session, since May 3)
- Mess Hall — Pre-Shift: `error` (HTTP 429 quota exhausted, since May 6)
- Weekly Skills Update Check: `error` (401 invalid API key, since May 3)
- Token Usage Weekly Audit: `last=None` (next scheduled: Sun May 10 15:00)

## Gateway Logs
No new errors in last hour for any agent.

## Cron Logs
No errors.

## Auth
- Nous Portal: Revoked (known, unchanged)

## Conclusion
No changes from previous run (0811). All error states documented and unchanged.
