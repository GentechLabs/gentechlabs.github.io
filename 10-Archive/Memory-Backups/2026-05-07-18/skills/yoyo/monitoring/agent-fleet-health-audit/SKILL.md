---
name: agent-fleet-health-audit
description: Systematic multi-agent health check methodology for Hermes agent fleets. Detects crashes, resource exhaustion, API dependency failures, and silent degradation across concurrent gateway processes.
triggers:
  - health_check
  - fleet_audit
  - watchdog_investigation
  - multi_agent_anomaly
---

# Agent Fleet Health Audit

Systematic multi-agent health check methodology for Hermes agent fleets. Detects crashes, resource exhaustion, API dependency failures, and silent degradation across concurrent gateway processes.

## WHEN TO USE

Run routine health audits or investigate fleet-wide anomalies:
- Multiple agents reporting similar errors
- Unexpected behavior across agent group
- Post-outage validation
- Weekly health check scheduling

## QUICK START

```bash
# 1. Check systemd service status
systemctl --user status hermes-gateway-*.service --no-pager

# 2. Verify all processes running
ps aux | grep hermes | grep -v grep

# 3. Scan gateway logs for ERROR entries
for agent in yoyo dmob desmond gentech; do
    grep -i ERROR /root/.hermes/profiles/$agent/logs/gateway.log | tail -20
done

# 4. Check for recent crashes (last 24h)
grep -i "fail\|exit" /var/log/syslog | grep hermes | tail -20
```

## METHODOLOGY

### **Layer 1: Service Layer**
- systemd status: Active/running? Main PID? Memory/CPU?
- Process count: One python process per agent profile expected
- Zombie/orphan detection: Ensure no stranded processes

### **Layer 2: Time-Series Log Analysis**
- Gateway logs: Look for `cron ticker started/stopped`, inbound/outbound messages
- Error logs: Collect ERROR/EXCEPTION/TRACEBACK entries by agent
- Compare mtimes across agent logs to see who's active

### **Layer 3: Cron Execution Validation**
- Verify crontab entries exist: `crontab -l | grep agent-name`
- Check cron output files have content written at expected times
- Match CRON syslog entries with log file modification timestamps

### **Layer 4: API Dependency Health**
- Scan error logs for third-party service failures:
  - ElevenLabs: `quota_exceeded`, `status_code: 401`
  - OpenAI: `NotFoundError: 404`, `unknown provider`
  - Anthropic: `no Anthropic credentials found`
  - Telegram: `Flood control`, `Chat not found`
- Count frequency — persistent failures = service outage

### **Layer 5: Cross-Correlation**
- Did all agents crash simultaneously? → Shared dependency failure
- Are errors time-correlated? → Network/service outage window
- Is only one agent affected? → Profile-specific config issue

## RED FLAGS & MEANINGS

| Symptom | Likely Cause | Priority |
|---------|--------------|----------|
| `exit-code` + `status=75/TEMPFAIL` | Transient resource/network issue | Medium |
| `State 'stop-sigterm' timed out` | Agent hung on shutdown (often stuck web request) | High |
| `Failed with result 'timeout'` | SIGKILL after 60s grace period | High |
| `quota_exceeded` (ElevenLabs) | Billing/credits exhausted — TTS dead | Critical |
| `unknown provider 'openai'` | Auth/config drift, missing env vars | Medium |
| `kanban dispatcher: tick failed` | Stuck kanban job blocking tick loop | Medium |
| `Flood control exceeded` | Rate limit hit — backpressure working | Low |

## POST-AUDIT ACTIONS

1. **Immediate:** Restart failed services via `systemctl --user restart hermes-gateway-<agent>.service`
2. **API failures:** Check credentials in agent `.env` or keychain; verify service status dashboards
3. **Cron silence:** Verify file append permissions, disk space, script runtime < schedule interval
4. **Log aggregation:** Archive findings to `11-Mess Hall/` with date-stamped report

## FILES REFERENCED

- `references/agent-crash-patterns.md` — exit codes, failure modes observed in production
- `references/api-outage-cheatsheet.md` — known outage signatures for common providers
- `references/gateway-log-parser.md` — log format reference and grep recipes

---

*Skill shaped by 2026-05-04 watchdog audit: simultaneous gateway crashes + API cascades + YoYo cron silent failure.*