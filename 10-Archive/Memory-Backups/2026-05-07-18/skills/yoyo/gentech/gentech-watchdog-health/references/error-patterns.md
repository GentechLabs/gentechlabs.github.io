# Hermes Error Pattern Reference

Quick regex lookup for log scanning during watchdog checks.

## Auth & Credential Failures

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| Nous token expired | `Refresh session has been revoked` | `AuthError: Refresh session has been revoked` | Run `hermes model` to re-auth |
| Nous refresh in progress | `Refresh already in progress` | `Primary provider auth failed: Refresh already in progress` | Wait 60s, retry |
| Invalid API key (generic) | `status.*401|Unauthorized` | `status_code: 401` | Rotate key in config |
| Missing provider credentials | `No .* credentials found` | `RuntimeError: No Anthropic credentials found` | Inject env vars or config |
| ElevenLabs 401 | `elevenlabs.*401|Invalid API key` | `ApiError: status_code: 401` | Rotate ElevenLabs key |

## Corruption & Data Errors

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| Bytecode truncation | `EOFError.*marshal data too short` | `EOFError: marshal data too short` | Delete `.pyc`, restart |
| SQLite malformed | `database disk image is malformed` | `sqlite3.OperationalError: database disk image is malformed` | Restore/recreate DB |
| SQLite locked | `database is locked` | `sqlite3.OperationalError: database is locked` | Check for lockfiles, restart |
| Disk full | `Errno 28` | `[Errno 28] No space left on device` | Clear disk space |

## Crashes & Instability

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| Gateway crash | `exit code 1` | `Process exited with code 1` | Check logs for root cause |
| SIGTERM received | `SIGTERM` | `Received SIGTERM, shutting down` | Check if manual kill or OOM |
| OOM killer | `Killed` | `Killed` (no traceback) | Add RAM or reduce memory usage |
| Graceful shutdown | `GracefulShutdown` | `GracefulShutdown requested` | Normal stop, not an error |

## Cron & Scheduler

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| Job failed (runtime) | `Job .* failed:` | `Job 'D5 Milestone' failed:` | Check job error details |
| Job skipped (past-due) | `Job .* skipped` | `Job skipped: already past_due` | Check scheduler clock |
| Dispatch error | `dispatch failed` | `Failed to dispatch job` | Check cron DB health |

## Network & Connections

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| Telegram disconnect | `ConnectionResetError|ConnectionError` | `ConnectionResetError` | Network flake, auto-reconnect |
| Telegram timeout | `telegram.*timeout|ReadTimeout` | `ReadTimeout` | Increase timeout or retry |
| Provider unavailable | `provider.*unavailable|fallback` | `Primary provider unavailable — trying fallback` | Check API status |
| Rate limit | `429|rate.?limit` | `HTTP 429 Too Many Requests` | Back off, add delay |

## File & System Errors

| Pattern | Regex | Example | Action |
|---------|-------|---------|--------|
| File not found | `FileNotFoundError` | `FileNotFoundError: [Errno 2]` | Check path, install missing file |
| Permission denied | `Permission denied` | `PermissionError: [Errno 13]` | Fix file permissions |
| YAML parse error | `mapping values are not allowed` | `yaml.parser.ParserError: mapping values` | Fix indentation in config.yaml |

## Bytecode Corruption Detection (Advanced)

In addition to log patterns, verify bytecode integrity:

```bash
# Find truncated .pyc files (< 50% of source .py size)
find /usr/local/lib/hermes-agent/agent/__pycache__ -name "*.pyc" -exec sh -c '
  src="${1%.cpython-311.pyc}.py"
  if [ -f "$src" ]; then
    pyc=$(stat -c%s "$1")
    py=$(stat -c%s "$src")
    if [ "$pyc" -lt $((py/2)) ]; then
      echo "CORRUPT: $1 ($pyc bytes) vs $src ($py bytes)"
    fi
  fi
' sh {} \;
```

## Colorized Log View (bash)

```bash
# Color-highlight critical errors when tailing logs
tail -f /root/.hermes/profiles/yoyo/logs/errors.log | perl -pe '
  s/(Refresh session has been revoked)/\e[31m$1\e[0m/g;
  s/(marshal data too short)/\e[33m$1\e[0m/g;
  s/(database disk image is malformed)/\e[35m$1\e[0m/g;
  s/(exit code 1)/\e[91m$1\e[0m/g;
'
```
