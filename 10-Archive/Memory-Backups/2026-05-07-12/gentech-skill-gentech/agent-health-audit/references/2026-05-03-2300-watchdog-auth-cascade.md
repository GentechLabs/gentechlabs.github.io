---
date: 2026-05-03T23:10
auditor: Gentech Watchdog (scheduled cron run 9ecfada01952)
agents_checked: [yoyo, dmob, desmond, gentech]
severity: critical
keywords: ["oauth revocation cascade", "elevenlabs quota exhausted", "cron job failures", "gateway drain timeout", "systemd service dead", "telegram flood control"]
related_skills: ["agent-health-audit", "hermes-auth-incident-response"]
---

# May 3, 2026 23:10 — Watchdog Alert Run (Second Audit of Day)

## Executive Summary

**🚨 CRITICAL: Fleet-wide authentication collapse + infrastructure degradation**

All four agent gateways were technically running and Telegram-connected at time of check (23:11–23:12), but **three catastrophic systemic failures** were detected:

1. **Nous OAuth revoked** (P0) — All agents blocked from Nous API since ~22:10 UTC. Access token expired; refresh token rejected by server. `hermes model` re-auth required.
2. **ElevenLabs TTS quota exceeded** — All agents: 0 credits remaining (Yoyo: 36 quota_exceeded errors, DMOB: 38, Desmond: 36, Gentech: 28 in logs). Voice output completely non-functional.
3. **Master cron orchestration dead** — `hermes-gateway.service` inactive since 14:35. Agents running as standalone processes via `--replace`; no service supervision or automatic restart. All cron dispatch is intra-process (no central ticker).

**Active failures (13 cron jobs)**: YoYo Crypto Watchlist, Kite AI Hackathon check, social-monitor, weekly skills, LayerZero DVN, hackathon-bounty-monitor, plus 6 Mess Hall jobs (I/O closed file errors, auth failures).

**Additional instability**: Gateway drain timeouts observed at 23:05 across all agents; DMOB experiencing Telegram flood control.

---

## Verification Results (23:10–23:12 UTC)

### Process Liveness

All agents confirmed running:

```
PID 420628: YoYo — uptime 0h 6m
PID 420653: DMOB — uptime 0h 5m
PID 420654: Gentech — uptime 0h 5m
PID 420661: Desmond — uptime 0h 5m
```

Gateway logs showed recent Telegram activity on all four agents at 23:11–23:12, confirming responsiveness.

### Cron Job Failures Identified

From `hermes cron list` (13 active failures):

| Job Name | Error |
|---|---|
| YoYo — Crypto Watchlist + LP Monitor | `Hermes not logged into Nous Portal` |
| Kite AI Hackathon Submission Check | `401 API key invalid/blocked/out of funds` |
| Mess Hall — Daily Rotation | `Hermes not logged into Nous Portal` |
| Mess Hall — Break 1/2/3 | `ValueError: I/O operation on closed file` |
| Mess Hall — Pre-Shift / Post-Shift | `closed file` / `Refresh session revoked` |
| Weekly Skills Update Check | `401 API key invalid` |
| LayerZero DVN Monitor | `401 API key invalid` |
| social-briefing | `ValueError: I/O operation on closed file` |
| social-monitor | `Hermes not logged into Nous Portal` |
| hackathon-bounty-monitor | `401 API key invalid` |

**Note**: All jobs reported as `system` profile in `hermes cron list`, but the failures clearly map to specific agents (YoYo, Gentech, DMOB/Desmond). This indicates dispatcher state confusion due to master service failure.

### Authentication State

- **Gentech**: `auth.json` shows `providers.nous.expires_at = 2026-05-03T22:11:54Z` (expired). Refresh token present but server rejected with `relogin_required: true`.
- **Revocation alert files** present in vault:
  - `/root/vaults/gentech/00-HQ/Alerts/nous-oauth-revoked-alert-2026-05-03-2310.md` (P0, detected 23:10)
  - `/root/vaults/gentech/11-Mess Hall/2026/W18/nous-oauth-revoked-alert-2026-05-03-1849.md` (detected 18:49)

### TTS Quota Status

All four agents share the same ElevenLabs key (`ELEVENLABS_API_KEY=bb158b...8674`). Logs show `quota_exceeded` pattern:

```
Yoyo: 36 occurrences of quota_exceeded in errors.log
DMOB: 38
Desmond: 36
Gentech: 28
```

Quota account `121002` at 0 credits; required per-request credits range 35–1564 depending on text length.

### Infrastructure Degradation

- **hermes-gateway.service**: `inactive (dead)` since 14:35 UTC. ExecStart path mismatch known issue (`/root/.hermes/hermes-agent/venv/bin/python` vs `/usr/local/lib/hermes-agent/venv/bin/python`). Not stopping manually launched gateways, but means no supervision/auto-restart.
- **Gateway drain timeouts**: All four agents logged `WARNING gateway.run: Gateway drain timed out after 60.0s with 1 active agent(s); interrupting remaining work.` at ~23:05. Indicates forced shutdown during prior gateway restart cycle.
- **Telegram flood control**: DMOB gateway logged `Telegram flood control on send (attempt 1/3), retrying in 10.0s` at 23:10. Likely from rapid restart message burst.

---

## Timeline of Today's Incidents (May 3 cumulative)

| Time (UTC) | Event | Impact |
|---|---|---|
| 14:33–14:35 | hermes-gateway.service stopped (likely manual or crash) | Central cron supervision lost; agents continue only if manually started |
| 18:49 | First OAuth revocation detection (Mess Hall alert created) | Nous API calls begin failing fleet-wide |
| 22:11 | Gentech access token expires | All subsequent Hermes-Nous calls fail 401 |
| 22:52 | auth.json modified (likely refresh attempt) | Refresh token rejected (`relogin_required: true`) |
| 23:05 | Coordinated gateway restart (drain timeouts logged) | All agents restarted; still not re-authenticated |
| 23:10 | Watchdog run — full fleet audit | This alert issued |

---

## Root Causes

1. **OAuth session revocation** — Refresh token invalidated by Nous Portal. Cause unknown (manual revocation? security flag? token reuse?). Affects all agents using shared Nous credentials. Recovery requires interactive `hermes model` per profile.
2. **ElevenLabs quota exhaustion** — Account `121002` depleted. 0 credits remaining. Need upgrade or new API key.
3. **Master service misconfiguration** — `hermes-gateway.service` ExecStart path points to wrong Python venv. Service won't start automatically. Agents running with `--replace` bypass supervision.
4. **Cron job I/O errors** — `ValueError: I/O operation on closed file` in Mess Hall jobs suggests output stream mishandling during gateway drain/restart. Transient but blocks those job runs.
5. **Model support withdrawal compound failure** — Earlier in day (per previous audit), Gentech saw `Model stepfun/step-3.5-flash not supported`. This error may still be present in config even after re-auth, blocking cron jobs.

---

## Required Actions (Prioritized)

### P0 — Immediate (Auth & Model)

**All agents**: Run `hermes model` to re-authenticate to Nous Portal (interactive OAuth required). No automated recovery path.

**Gentech-specific**: After re-auth, verify configured model is supported. If `stepfun/step-3.5-flash` is still set, switch to a currently available Nous-model via `hermes model` or edit `config.yaml`.

### P1 — Today

1. **Rotate ElevenLabs API key** in all four agent `.env` files, or top up quota on account `121002`.
2. **Fix hermes-gateway.service** ExecStart path to `/usr/local/lib/hermes-agent/venv/bin/python`, then `systemctl --user daemon-reload && systemctl --user restart hermes-gateway.service` to restore supervision.
3. **Restart all gateways** after credential rotation to ensure env variables are loaded.

### P2 — This Week

1. **Investigate OAuth revocation cause** — Check Nous Portal for security events, token reuse, or rate-limit flags. Consider credential pool strategy to avoid single-point-of-failure.
2. **Add cron health monitoring** — Detect `last_run_at: null` vs `next_run_at` gaps proactively.
3. **Review Mess Hall cron output handling** — Prevent I/O closed file errors during gateway drains.

---

## Diagnostic Commands Used

```bash
# Process table + uptime
ps -eo pid,etimes,cmd | grep hermes_cli.main

# Gateway logs (last 5 entries)
for a in yoyo dmob desmond gentech; do
  tail -5 /root/.hermes/profiles/$a/logs/gateway.log
done

# Errors.log size and tail (TTS quota pattern)
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  wc -l /root/.hermes/profiles/$a/logs/errors.log
  grep -c "quota_exceeded" /root/.hermes/profiles/$a/logs/errors.log
done

# Hermes cron list and error extraction
hermes cron list | grep -B2 "error:"

# Systemd gateway service status
systemctl --user status hermes-gateway.service --no-pager --lines 20

# auth.json inspection
python3 -c "import json; d=json.load(open('/root/.hermes/profiles/gentech/auth.json')); print(json.dumps(d['providers']['nous'], indent=2))"

# ElevenLabs key presence (masked)
grep ELEVENLABS /root/.hermes/profiles/*/.env | head -4

# Recent session check (last 2h)
find /root/.local/state/tirith/sessions -name "*.json" -mmin -120 -ls
```

---

## Pattern Notes (New This Session)

### Pattern: Gateway Drain Timeout as Restart Symptom

When all agents log `Gateway drain timed out after 60.0s with 1 active agent(s)` within same time window (+/- 30s), this indicates a **coordinated gateway restart** (likely manual or crash-recovery). The drain timeout itself is not the root cause — it's the symptom of a prior shutdown signal.

**Correlate with**: Process uptime (all agents showing similar young PIDs), systemd service state transitions, and `Skipping .clean_shutdown marker` log entries.

### Pattern: Cron List Shows `system` Profile for Agent Jobs

With master `hermes-gateway.service` dead and agents running manually, `hermes cron list` may report agent jobs under `profile: system` rather than the actual agent profile. This is a **display artifact** of the broken dispatcher, not a misassignment.

**Do not migrate these jobs** — they are executing inside the correct agent's in-process cron. Verify execution via agent-specific cron output directories (`/root/.hermes/profiles/<agent>/cron/output/`) and session files.

### Pattern: Telegram Flood Control Following Restart Burst

After gateway restart, all agents may simultaneously push buffered Telegram messages, triggering `Flood control exceeded`. This is self-throttling; wait 10–60 seconds between retries. Avoid manual `send_message` during recovery window.

### Pattern: Quota Exceeded vs Invalid Key

Error `quota_exceeded` means key is valid but credits are zero. Error `Invalid API key` means key is wrong/rotated. Both return 401 but have different remediation:
- `quota_exceeded` → purchase/refill credits or switch to different account
- `Invalid API key` → rotate key in `.env`

Distinguish by reading error body `'status': 'quota_exceeded'` vs `'status': 'invalid_api_key'`.

---

## Vault Artifacts Created This Session

None. This was a read-only diagnostic run. All findings captured in this reference.

---

## Follow-up Required

- [ ] **Owner: DMOB** — Run `hermes model` on YoYo, DMOB, Desmond, Gentech (interactive OAuth flow)
- [ ] **Owner: DMOB/Gentech** — Switch Gentech model from `stepfun/step-3.5-flash` to supported alternative after re-auth
- [ ] **Owner: DMOB** — Top up ElevenLabs account `121002` or rotate key across all agents
- [ ] **Owner: DMOB** — Fix `hermes-gateway.service` ExecStart path and restart service for supervision
- [ ] **Owner: DMOB** — Restart all agent gateways post-credential updates
- [ ] **Owner: YoYo** — Investigate and fix Mess Hall cron I/O errors (output stream handling)
- [ ] **Owner: Gentech** — Next audit scheduled 2026-05-04 06:00 UTC (post-recovery validation)

---

## References

- [Earlier same-day audit](references/2026-05-03-fleet-health-audit.md) — 18:49 UTC run, initial revocation detection
- OAuth revocation recovery playbook: `00-HQ/Alerts/nous-oauth-revoked-alert-2026-05-03-2310.md`
- Mess Hall daily context: `11-Mess Hall/2026/W18/nous-oauth-revoked-alert-2026-05-03-1849.md`
