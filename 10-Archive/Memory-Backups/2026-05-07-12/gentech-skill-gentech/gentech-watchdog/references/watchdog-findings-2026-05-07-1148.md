# Watchdog Findings — 2026-05-07 11:48 UTC

## Fleet Status

| Agent | Gateway | Cron Jobs | Issues |
|-------|---------|-----------|--------|
| Gentech | ✅ Running (mimo-v2.5, custom endpoint) | ✅ 30 active, most OK | 3 cron jobs failing (No LLM provider configured) |
| YoYo | ✅ Running | ✅ DCA monitor working | 2 cron jobs failing (Refresh session revoked) |
| DMOB | ✅ Running | ✅ LP monitor working | 1 stale error (May 3, Sunday Skill Update) |
| Desmond | ✅ Running | ✅ No errors | Clean |

## Changes from Previous Report (01:00 UTC)

### Improvements
- **Mess Hall — Daily Rotation**: was erroring, now OK (ran 03:02 UTC)
- **Mess Hall — Break 1**: was erroring, now OK (ran 06:02 UTC)
- **YoYo DCA monitor**: running correctly (Defi Milestone ran 11:40 UTC)
- **Omni-Summary Master Brief**: ran OK (11:32 UTC)

### Persistent Issues (unchanged)
- **YoYo**: "Portfolio Site — Daily Regeneration" and "College.xyz — Daily Internship Scan" failing with revoked auth. Both scheduled to run today (12:00, 13:00 UTC) — will likely fail again.
- **Gentech**: "The Brain — Daily" (16:00 UTC), "Gentech X Content Extractor" (17:00 UTC), "Security → Content Pipeline" (May 8) failing with No LLM provider configured.

### No New Issues Detected
- All gateway logs clean in last hour
- No new error types
- No process restarts or crashes
- Telegram connected for all agents

## Root Causes (unchanged from 01:00 report)
1. **Nous Portal OAuth refresh session revoked** — affects YoYo cron jobs that depend on Nous auth
2. **Cron daemon context lacks provider config** — custom endpoint (mimo-v2.5) works in gateway but not in cron subprocess context. Jobs need explicit model/provider pinning.
3. **Stale Mess Hall errors** — I/O operation on closed file (May 3), 401 API key invalid (May 3) — likely transient, some have recovered

## Decision
**STATUS:OK** — All agents healthy. No new issues. Known issues already documented in previous report.
