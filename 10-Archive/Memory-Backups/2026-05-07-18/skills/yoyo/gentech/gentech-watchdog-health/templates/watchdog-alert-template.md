# Watchdog Alert Template

**Usage:** Copy this template when filing a critical health alert to Gentech HQ or incident channel.

**Trigger condition:** Any agent with no Telegram response >60 min, cron executor deadlocked, auth revoked fleet-wide, or infrastructure corruption detected.

---

🚨 **Watchdog Alert:** [ONE-LINER SUMMARY]

**Time:** {{timestamp}} UTC  
**Agents affected:** [YoYo, DMOB, Desmond, Gentech — or list affected]  
**Severity:** [CRITICAL / HIGH / MEDIUM]

### What's Wrong
[Brief description of failure. Example: "All agents unresponsive; gateways running but not processing Telegram messages since 12:47 UTC."]

### Evidence
- **Last Telegram response:** {{last_response_time}} (idle {{minutes}} min)
- **Cron jobs:** {{num_overdue}}/{{total_jobs}} overdue with `last_run: null`
- **Auth status:** [Describe auth failures e.g. "Nous Portal token expired on May 1"]
- **Corruption:** [List any: bytecode (.pyc truncated), DB malformed, cron DB 0 bytes]
- **Crash cycles:** [Number of gateway crash/restart cycles observed]

### Root Cause (if known)
[Pre-filled from diagnostic. Example: "Nous Portal refresh session revoked; cron executor deadlock due to 0-byte jobs.db; shared bytecode cache corruption affecting all profiles."]

### Immediate Actions Required
1. **[ ]** Re-authenticate Nous Portal: `hermes model` for each profile (YoYo, DMOB, Desmond, Gentech)
2. **[ ]** Repair cron DB: Stop all gateways → `> /root/.hermes/cron/jobs.db` → restart
3. **[ ]** Purge bytecode: `find /usr/local/lib/hermes-agent -name "*.pyc" -delete`
4. **[ ]** [Additional agent-specific action, e.g. "Rotate ElevenLabs API key in DMOB config"]
5. **[ ]** Restart gateways and verify Telegram responses resume

### Monitoring Checklist
- [ ] `jobs.db` size > 0 bytes within 60 seconds of restart
- [ ] At least one cron job execution appears in `scheduler.log`
- [ ] `gateway.log` shows `Sending response` with current timestamps
- [ ] Auth error velocity in `errors.log` < 5 per 100 lines
- [ ] No new `SIGTERM` or `exit code 1` entries

### Related Sessions
[Session IDs from watchdog investigation, e.g.]
- `cron_9ecfada01952_20260502_210554` — Initial fleet health check
- `cron_9ecfada01952_20260502_220535` — Deep-dive diagnostics

---

**Filed by:** Gentech Watchdog (cron job)  
**Follow-up:** Verify recovery within 30 minutes; if not escalated to DMOB/Infrastructure.
