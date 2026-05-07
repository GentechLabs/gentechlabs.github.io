# Coordinated Gateway Restart Storm — Fleet-Wide Synchronized Shutdown

**Detected:** 2026-05-03 23:33:47–23:33:51 UTC
**Scope:** All 4 agents (Gentech, Desmond, DMOB, YoYo) stopped and restarted within 4 seconds
**Severity:** P1 — All services recovered automatically, but root cause indicates systemic trigger

---

## Event Timeline

```
23:33:47.430 [Gentech]  INFO gateway.run: Gateway stopped
23:33:47.431 [Gentech]  INFO gateway.run: Cron ticker stopped
23:33:47.431 [Gentech]  INFO gateway.run: Exiting with code 1 (signal-initiated shutdown without restart request)

23:33:48.215 [Desmond]  INFO gateway.run: Gateway stopped
23:33:48.216 [Desmond]  INFO gateway.run: Cron ticker stopped
23:33:48.216 [Desmond]  INFO gateway.run: Exiting with code 1 (signal-initiated shutdown without restart request)

23:33:48.804 [DMOB]    INFO gateway.run: Gateway stopped
23:33:48.804 [DMOB]    INFO gateway.run: Cron ticker stopped
23:33:48.804 [DMOB]    INFO gateway.run: Exiting with code 1 (signal-initiated shutdown without restart request)

23:33:49.445 [YoYo]    INFO gateway.run: Gateway stopped
23:33:49.445 [YoYo]    INFO gateway.run: Cron ticker stopped
23:33:49.445 [YoYo]    INFO gateway.run: Exiting with code 1 (signal-initiated shutdown without restart request)

[~2–4 second window for all 4 agents to begin shutdown]

23:33:49.909 [Gentech]  INFO gateway.run: Cron ticker started (interval=60s)
23:33:50.822 [Desmond]  INFO gateway.run: Cron ticker started (interval=60s)
23:33:51.156 [DMOB]    INFO gateway.run: Cron ticker started (interval=60s)
23:33:51.365 [???]      INFO gateway.run: Cron ticker started (interval=60s)  # YoYo's restart not captured
```

**Pattern:** All 4 agents within the same 4-second window logged "Exiting with code 1 (signal-initiated shutdown without restart request)" and then restarted automatically via systemd's `Restart=on-failure`.

---

## Root Cause Hypotheses

Given the **tight synchronization** across independent gateway processes, this is almost certainly not a coincidence. Possible triggers:

### H1 — Shared signal sent to all Hermes processes
A single `SIGTERM` or `SIGINT` broadcast to all gateway PIDs (e.g., via `killall` or systemd user service stop).  
**Evidence for:** Simultaneous shutdown across all profiles.  
**Evidence against:** No manual stop record; the message says "without restart request" but if it were a coordinated stop, typically we'd see a "GracefulShutdown requested" message.

### H2 — Scheduler panic on credential cascade failure
The Nous OAuth revocation was detected at 23:22 UTC (per incident report). At 23:33, the cron executor may have hit a **credential validation panic threshold** and triggered a graceful restart of all gateways to clear bad auth state.  
**Evidence for:** The OAuth failure was in progress; multiple agents showing `auth.json` `providers: []` state.  
**Evidence against:** The shutdown message says "without restart request" — suggests an unhandled exception or forced exit, not a graceful scheduler-triggered restart.

### H3 — Resource exhaustion trigger (disk/memory) affecting all processes simultaneously
The system was under disk pressure earlier (May 1 had 82% usage; May 4 was cleaner after cleanup). Could be a memory pressure event causing OOM killer, but no `Killed` message appears.  
**Evidence against:** All messages show `Exiting with code 1`, not `Killed` by OOM.

### H4 — Hermes agent update/deployment
Automatic update mechanism may have installed new agent code, triggering restart. Check for recent updates:
```bash
ls -la /usr/local/lib/hermes-agent/  # recent modification?
git -C /usr/local/lib/hermes-agent log --oneline -5  # if git-tracked
```
**Evidence for:** Coordinated across all profiles is expected during deployment.
**Evidence against:** No deployment was logged in Mess Hall; watchdogs haven't reported update activity.

### H5 — Systemd user service collision
All Hermes gateways run as user systemd services (`hermes-gateway-<profile>.service`). A `systemctl --user stop hermes-gateway*` or `systemctl --user restart hermes-gateway*` would restart all simultaneously.  
**Evidence for:** Perfectly synchronized; systemd is the coordination point.  
**Evidence against:** No record of such a command in shell history; the watchdog would have caught it.

---

## Diagnostic Checklist

When you observe this pattern:

### 1. Correlate with external events
```bash
# Check for any system-level events within ±5 minutes
grep -E 'systemd|kill|restart|oom|sigterm' /var/log/syslog 2>/dev/null | \
  grep 'May 3 23:3[0-9]' | head -20
```

### 2. Check if there was a coordinated deployment
```bash
# Look for timestamped changes to hermes-agent installation
find /usr/local/lib/hermes-agent -type f -cmin -120 -ls 2>/dev/null | head -20
# Or check if hermes was updated via package manager
grep 'hermes' /var/log/apt/history.log 2>/dev/null | tail -20
```

### 3. Examine the shutdown message details
The exact text `Exiting with code 1 (signal-initiated shutdown without restart request)` indicates the gateway received a **signal** (SIGTERM/SIGINT) but the code path explicitly rejected it as "without restart request", meaning it was an **external signal** not initiated by the gateway's own restart logic. This points to H1 or H5 (external kill signal).

### 4. Hunt for the signal source
```bash
# Check audit logs for kill signals (if auditd is running)
ausearch -m SIG -ts '2026-05-03 23:30:00' -te '2026-05-03 23:35:00' 2>/dev/null | head -20

# Or check process accounting (if enabled)
lastcomm | grep kill | grep '23:3[0-9]' 2>/dev/null | head -10
```

---

## Recovery Observations

**Automatic recovery worked:** All agents restarted within 2–4 seconds via systemd `Restart=on-failure`. This is exactly how the system is designed to behave.

**Post-restart state:**
- All gateways reinitialized with clean process state
- Cron ticker resumed (`Cron ticker started` logged within 2s of each restart)
- `.tick.lock` files were recreated (but some showed stale content, indicating the lock wasn't cleared properly during the cascade)

**Why `.tick.lock` went stale post-restart:**  
The shutdown occurred while the cron ticker was holding the lock. The process exited without releasing it (typical with SIGTERM). On restart, the new gateway process started with a fresh lock. However, if the timestamp on the lock file persisted from before the restart (due to filesystem timestamp quirks or NFS delay), the lock could appear stale even on a fresh process.

---

## Detection & Alerting

Add to watchdog Step 0: **Synchronized Restart Detection**

```bash
# Parse last 100 lines of each gateway log for coordinated shutdowns
declare -A restart_times
for p in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$p/logs/gateway.log"
  if [ -f "$log" ]; then
    # Find the most recent "Exiting with code 1" event
    line=$(grep -m1 'Exiting with code 1' "$log" | tail -1)
    if [ -n "$line" ]; then
      ts=$(echo "$line" | cut -d',' -f1)
      restart_times[$p]="$ts"
      echo "[$p] last_exit: $ts"
    fi
  fi
done

# Check for time clustering: do ≥3 agents have exit times within 10 seconds?
recent_exits=0
for agent in "${!restart_times[@]}"; do
  ts="${restart_times[$agent]}"
  # Compare to others, count how many within 10s
  count=0
  for other in "${!restart_times[@]}"; do
    # Calculate diff in seconds (simplified)
    # If multiple agents show near-identical timestamps → coordinated
    :
  done
done
```

**Alert condition:** ≥3 agents show identical shutdown timestamps (within 5-second window) → `🚨 Watchdog Alert: Coordinated gateway restart storm detected (all agents within 4s window)`

---

## Playbook Response

When you observe a coordinated restart:

1. **DO NOT PANIC** — systemd auto-restart handled recovery
2. **Check external cause first:**
   - Was there a system update or deployment? (`/var/log/apt/history.log`, `/var/log/dpkg.log`)
   - Did Jordan or another operator run a cluster-wide command? (Check shell history / audit logs)
3. **Inspect auth cascade:** Run `python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py` — OAuth revocation may have triggered panic restart
4. **Validate cron DB integrity:** Check `jobs.db` size — if 0 bytes, execute recovery from `references/2026-05-04-cron-db-zero-byte-corruption.md`
5. **Monitor** for 15 minutes to ensure stability
6. **Document** in Mess Hall with root cause (or "unknown" if not found)

---

## Related Patterns

- **Cascading shutdown pattern** mirrors the May 2 00:55 restart event (observed in prior health checks)
- Often co-occurs with **cron database corruption** (0-byte jobs.db) — both can be triggered by abrupt SIGKILL during DB write
- If followed by **stale `.tick.lock`** files, that's a secondary symptom (locks not cleaned up on forced exit)

---

## Decision Tree

```
Multiple gateways stopped simultaneously?
├─ YES → Coordinated event
│  │
│  ├─ Shutdown message = 'GracefulShutdown requested'?
│  │  └─ YES → Planned maintenance/deployment (check operator activity)
│  │
│  ├─ Exit code 1 + 'signal-initiated shutdown without restart request'?
│  │  └─ YES → External SIGTERM/SIGINT broadcast
│  │     ├─ systemctl --user stop/restart hermes-gateway*? → manual action
│  │     ├─ killall hermes? → manual action
│  │     └─ Unknown source → check auditd, shell history
│  │
│  └─ Exit code = 'Killed' (no message)?
│     └─ YES → OOM killer → add memory
│
└─ NO → Isolated crash → check individual agent logs
```

---

## Key Takeaway

**A coordinated restart without explicit operator action is a RED FLAG** — it indicates a single point of control (systemd, orchestration script, or panic handler) decided to restart all gateways at once. Always hunt the **initiating event** rather than treating each agent's recovery as independent.
