# Agent Crash Patterns — Observed Exit Codes

Recorded from 2026-05-04 systemd analysis across YoYo/DMOB/Desmond/Gentech gateways.

## Exit Code → Meaning + Action

| Exit Code | Systemd Status | Observed Behavior | Root Cause (likely) | Recovery |
|-----------|----------------|-------------------|---------------------|----------|
| `0` | `success` | Clean exit | Normal stop/restart | N/A |
| `1` / `FAILURE` | `failed` | Gateway crashed, auto-restarted | Unhandled exception, config error | Check `errors.log` + `gateway.log` |
| `75` / `TEMPFAIL` | `failed` | Temporary failure exit | Network timeout, API unreachable, resource exhausted | Transient — auto-recovered |
| `137` / `SIGKILL` | `timeout` | Killed after 60s stop timeout | Agent hung on shutdown (blocking I/O) | Restart, investigate stuck task |
| `143` / `SIGTERM` | `exited` | Graceful shutdown via signal | Normal stop command | N/A |

## Crash Sequence Analysis (May 3 23:30–23:35 UTC)

**Pattern:** All four agents failed in rapid succession (< 60s window).

```
23:30:07  hermes-gateway-gentech: exit(75/TEMPFAIL) → restart
23:30:08  hermes-gateway-dmob:    exit(75/TEMPFAIL) → restart
23:30:08  hermes-gateway-yoyo:    exit(75/TEMPFAIL) → restart
23:33:47  hermes-gateway-gentech: exit(1/FAILURE)   → restart
23:33:48  hermes-gateway-desmond:  exit(1/FAILURE)   → restart
23:33:49  hermes-gateway-dmob:     exit(1/FAILURE)   → restart
23:35:19  hermes-gateway-yoyo:     timeout(60s) → SIGKILL → restart
```

**Diagnostic path:**
1. Check `errors.log` on each agent immediately after crash — TTL ~1h before log rotation
2. Correlate with syslog: `grep "hermes.*fail\|hermes.*exit" /var/log/syslog`
3. Look for concurrent API outage alerts in other agents' logs

## Recovery Behavior

All agents auto-recovered via systemd `Restart=always` (default). Recovery time:
- DMOB/Desmond/Gentech: ~1–2s (fast restart)
- YoYo: ~40s due to 60s stop-timeout hit → SIGKILL → cold start

**Recommendation:** If YoYo repeatedly hits stop-timeout, investigate:
- Long-running web requests (OpenAI API hangs)
- Kanban job stuck in infinite loop
- Unresponded Telegram message flush

---

*Source: 2026-05-04 watchdog audit, /var/log/syslog, `systemctl --user status` output.*