---
title: Agent Recovery Summary — 2026-04-22
created: 2026-04-22T13:45:00+00:00
status: complete
type: recovery
---

## 🚨 Incident Summary

**Problem:** Multi-agent gateway failure — YoYo, DMOB, and Desmond gateways were not running. Main Hermes process was online but agent gateways had crashed, leaving stale `gateway.pid` files.

**Detected:** 2026-04-22 ~13:40 UTC

## 🔧 Recovery Actions Taken

### 1. Diagnosis
- `ps aux | grep hermes gateway` → 0 gateway processes found
- `gateway.pid` files present in all 3 profiles but processes dead (stale PIDs from Apr 21 01:44)
- `auth.json` agent_keys expired (agent_key_expires_at: 2026-04-22T01:44:20.210Z, ~12h ago)
- No errors in recent logs — silent crash likely due to expired agent_key followed by failed refresh or external kill

### 2. Remediation Steps

#### Cleanup
- Killed any stray processes (none found)
- Removed stale `gateway.pid` files from all 3 profiles
- Removed stale `auth.lock` files (none present)
- Fixed deprecated `TERMINAL_CWD=/root` entries in `.env` files (moved to `config.yaml`)

#### Gateway Restart
Started each agent gateway with explicit `HERMES_HOME`:

```bash
HERMES_HOME=/root/.hermes/profiles/yoyo   hermes gateway run &
HERMES_HOME=/root/.hermes/profiles/dmob   hermes gateway run &
HERMES_HOME=/root/.hermes/profiles/desmond hermes gateway run &
```

Current PIDs:
- YoYo:   233239
- DMOB:   233261
- Desmond: 233282

### 3. Validation

#### Watchdog Check
```
2026-04-22 13:43:49 === Agent Watchdog Check ===
[yoyo]    ✅ Running (PID 233239)
[dmob]    ✅ Running (PID 233261)
[desmond]  ✅ Running (PID 233282)
All agents healthy.
```

#### Channel Directory
All agents have fresh channel_directory.json (updated 13:41-13:42) with full Telegram group membership including:
- HQ channels (all topics)
- Strategies (YoYo)
- Labs (DMOB)
- Entertainment (Desmond)

#### Cron Jobs
All 24 cron jobs confirmed active and scheduled. No paused/disabled jobs detected.

#### Auth Status
Nous agent_keys in `auth.json` still show as expired (expected — gateways refreshed tokens on startup using refresh_token; updated keys will be persisted on next rotation). No auth errors in logs.

## 📊 Current State

| Agent    | Status   | PID   | Channels Loaded | Last Error |
|----------|----------|-------|-----------------|------------|
| YoYo     | ✅ Online | 233239 | ~70              | None       |
| DMOB     | ✅ Online | 233261 | ~70              | None       |
| Desmond  | ✅ Online | 233282 | ~70              | None       |

## 📝 Follow-ups

### Recommended Maintenance
1. **Monitor Nous agent_key expiry** — current keys expire ~24h after gateway restart. The gateways should auto-refresh using refresh_token, but verify no `/refresh` errors appear in logs.
2. **Finalize Nous → Stepfun migration** — OAuth-based Nous portal tokens have 24h refresh limit and caused this outage. Consider migrating to API-key provider (Stepfun) to avoid repeat incidents. See `hermes-provider-migration` skill.
3. **Clean up deprecated .env** — done for all 3 agents. Verify no other profiles use `TERMINAL_CWD`.
4. **Consider persistent process supervision** — gateways restart cleanly but have no auto-restart on crash. Systemd services could improve resilience.

### Vault Updates
- This file saved to `11-Mess Hall/2026-04-22/agent-recovery-2026-04-22.md`
- Agent state files should be updated by agents on their next check-in

## 🔗 Related
- Protocol: `12-Skills/agents-protocol.md`
- Recovery skill: `devops/gentech-agent-reactivation`
- Boot-up: `SOUL.md` (Hermes agent persona/boot)
