# Gentech Agent State — 2026-04-19

## Status: ALL AGENTS ONLINE
- Timestamp: 2026-04-19 00:40 UTC (8:40 PM EST Apr 18)
- Model: qwen3.6-plus via opencode-go

## Agent Health (watchdog verified)
| Agent | Status | Last Active | Notes |
|-------|--------|-------------|-------|
| Gentech | ✓ Running | Now | Gateway PID active |
| YoYo | ✓ Running | recent | Cron sessions active |
| Dmob | ✓ Running | recent | Idle but healthy |
| Desmond | ✓ Running | recent | Cron sessions active |

## Model Switch Order (updated)
1. Morning 5:30 AM EST (09:30 UTC) → Nous Research (MiMo v2 Pro)
2. Evening 7:30 PM EST (23:30 UTC) → OpenCode + Qwen 3.6
3. Late 2:00 AM EST (06:00 UTC) → Ollama local (fallback, low power)

## Cron Jobs
- 30 active jobs
- "Second Brain" renamed to "The Brain" across all cron jobs
- evening-switch-ollama renamed to late-night-switch-ollama (runs 2:00 AM EST)
- All crons scheduled before 11pm EST quiet time

## Fixes Applied
1. Fixed hermes_cli/cron.py — repeat_info type guard
2. Created switch-to-ollama.sh script (was missing)
3. Updated crontab model switch times
4. Renamed "Second Brain" → "The Brain" in all cron jobs
5. Updated evening switch to OpenCode/Qwen 3.6, Ollama as last fallback

## Files Updated
- /root/.hermes/scripts/switch-to-ollama.sh (created)
- /root/.hermes/cron/jobs.json (cron renames + schedule changes)
- Crontab: model switch times updated
