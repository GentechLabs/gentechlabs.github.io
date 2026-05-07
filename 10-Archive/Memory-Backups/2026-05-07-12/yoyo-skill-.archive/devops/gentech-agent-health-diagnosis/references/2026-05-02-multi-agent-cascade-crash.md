# Multi-Agent Simultaneous Crash Cascade — May 2, 2026

**Incident ID:** INC-20260502-0055  
**Detection:** Watchdog cron job (scheduled 01:05 UTC)  
**Agents affected:** Gentech, YoYo, DMOB, Desmond (all 4 Hermes gateways)  
**Status:** All agents restored automatically by systemd restart  

---

## Timeline (chronological)

| Time (UTC) | Agent | Event | Exit code | Recovery |
|------------|-------|-------|-----------|----------|
| 00:55:10 | Desmond | Stop signal received | — | — |
| 00:55:11 | Desmond | Process exited, status 1/FAILURE | 1 | Restarted at 00:55:11 |
| 00:55:12 | DMOB | Stop signal received | — | — |
| 00:55:15 | DMOB | Process exited, status 1/FAILURE | 1 | Restarted at 00:55:16 |
| 00:55:17 | Gentech | Stop signal received | — | — |
| 00:56:47 | Gentech | Stop timeout, SIGKILL sent (TimeoutStopSec exceeded) | 9/KILL | Restarted at 00:56:48 |
| 00:56:48 | YoYo | Stop signal received | — | — |
| 00:56:52 | YoYo | Process exited, status 1/FAILURE | 1 | Restarted at 00:56:53 |

**Total outage window:** 91 seconds (Gentech longest), other agents <5s each.

---

## Observations

1. **Cascade pattern** — All 4 services stopped within a 60-second window, suggesting a coordinated trigger rather than independent failures.
2. **Gentech timeout anomaly** — Gentech shutdown took 91 seconds (exceeded systemd `TimeoutStopSec`), requiring SIGKILL. This indicates a hung cleanup routine (likely kanban notifier I/O, SessionDB commit, or cron cache flush).
3. **Automatic recovery** — systemd user services self-restarted; all PIDs fresh at 00:56–00:57.
4. **Precursor activity (April 29)** — Ollama API 429 rate-limit errors and SessionDB marshal corruption warnings appeared 3 days earlier but resolved by May 1. No direct causal link established.

---

## Diagnostic findings

**System resources** (at incident time, from journalctl):
- Memory pressure: No OOM events detected (`dmesg` clean)
- Disk space: Root filesystem 82% used (37G free) — adequate
- Inodes: No exhaustion observed
- Network: No connectivity errors in system logs

**Process state** (post-recovery):
```
YOYO:  PID=923106 CPU=1.0% MEM=1.1%
DMOB:  PID=922890 CPU=0.3% MEM=0.7%
DESMOND: PID=922877 CPU=0.3% MEM=0.8%
GENTECH: PID=923094 CPU=0.6% MEM=1.0%
```
All nominal.

**Error log analysis:**
- No `InvalidToken`, `Refresh session revoked`, or provider auth errors
- No `marshal data too short` errors during May 2 incident window
- No kanban notifier I/O failures or SQLite `database or disk is full` warnings
- No concurrent cron job overload signals

---

## Hypothesized triggers (ranked by likelihood)

### 1. Coordinated restart signal (highest likelihood)
- **Evidence:** All gateways stopped within 60 seconds of each other, not randomly staggered.
- **Possible causes:**
  - Systemd user instance restart (e.g., `systemctl --user daemon-reexec` triggered by something)
  - Manual or scripted `hermes gateway stop --all` run inadvertently
  - Gateway watchdog health-check loop that decided all needed restart
- **How to verify:** Check `journalctl` for `systemd[797]: Stopping hermes-gateway` entries at the start of the cascade — already seen. Trace upstream to what requested the stop (was it a user command, cron, or systemd dependency restart?)

### 2. Kanban notifier I/O hang that propagated across profiles
- **Evidence:** Gentech required SIGKILL (90+ s stop timeout), suggesting a blocking I/O operation during shutdown (likely kanban notifier trying to write to SQLite or Telegram).
- **Mechanism:** All gateways share the same embedded cron executor thread. A deadlock in the kanban notifier (used by all agents) could cause the executor to hang, triggering coordinated stop/restart.
- **How to verify:** Check each `gateway.log` for `kanban notifier` errors in the 30 minutes prior to cascade. Look for `sqlite3.OperationalError: database is locked` or `disk I/O error`.

### 3. Hermes package update / bytecode invalidation race
- **Evidence:** Prior to incident (April 29), marshal bytecode errors occurred across multiple agents. While resolved, it demonstrates that shared installation changes can cascade.
- **Mechanism:** A background update (e.g., `pip install --upgrade hermes-agent`) or brain backup that modified files under `/usr/local/lib/hermes-agent` could have triggered process re-exec checks, causing gateways to restart.
- **How to verify:** Check `update.log` and `brain-backup.log` for timestamps around 00:50–00:55 UTC on May 2.

### 4. Ollama API exhaustion cascade (less likely)
- **Evidence:** April 29 had `OLLAMA_API_KEY exhausted (status=429)` and context summary failures. But these were 3 days earlier and not active on May 2.
- **Mechanism:** If context summarization is a blocking gating operation during gateway shutdown (e.g., must summarize session before exit), a 429 hang could delay shutdown past `TimeoutStopSec`.
- **Probability:** Low — not observed in current error logs.

---

## Monitoring correlation

The incident was detected by the scheduled Watchdog cron job running at 01:05 UTC, which performs active health verification (`ps aux` + recent transcript check). The job itself completed successfully, but its output revealed the cascade.

**Key detection logic that worked:**
```python
# 1. Verify all 4 gateways are in `ps aux`
# 2. Check systemd service status (showed previously-failed but now-restarted)
# 3. Scanned journalctl for recent failure entries (found 00:55–00:56 failures)
# 4. Confirmed current running state (all agents OK as of 01:05)
```

**What DIDN'T trigger automatic alert:** The gateways self-restarted within <2 minutes each, so systemd reported `active` by the time the watchdog ran. No paging alert would have fired unless we explicitly scan historical journal entries. The Watchdog's *report* contained the anomaly; a monitoring rule should be added:

```
IF (journalctl --since "10 min ago" contains "hermes-gateway-*.service: Failed")
THEN elevate to incident (even if services currently active)
```

---

## Recommendations

### Immediate
1. **Add Watchdog correlation rule** — Scan for recent `Failed` entries across all 4 gateway services, not just current process state.
2. **Check for manual stop commands** — Search audit trail (bash history, systemd user manager logs) for `hermes gateway stop` or `systemctl --user stop hermes-gateway-*` around 00:55 UTC.

### Short-term
3. **Instrument gateway stop duration** — Add explicit logging when `TimeoutStopSec` is approached. Currently only systemd logs the kill event; gateway process itself doesn't log "shutdown taking longer than X seconds."
4. **Increase `TimeoutStopSec`** for all gateways from default 90s to 180s to allow graceful kanban notifier flush during shutdown (if hang is transient).
5. **Verify cron executor state post-restart** — After any multi-agent restart, explicitly check `hermes cron list` and gateway logs for `Cron executor started` to ensure cron subsystem recovered.

### Long-term
6. **Implement health endpoint / readiness probe** — Each gateway should expose a simple health check (HTTP or file-based) that external watchdog can poll to detect "running but not executing" states.
7. **Add stop-sentinel logging** — Gateways should log `Received stop signal` and `Shutdown complete` with timestamps, so we can measure actual stop duration without relying on systemd kill logs.
8. **Cross-agent lock coordination** — Investigate whether per-agent Telegram locks (`/root/.local/state/hermes/gateway-locks/`) could create cross-contention during simultaneous shutdown/startup. Consider sequential restart with longer stagger (10s vs 4s) in automated recovery scripts.

---

## Related incidents

- **2026-04-29**: Ollama API 429 rate-limit cascade + SessionDB marshal corruption warnings (not same root cause, but shows multi-agent fragility)
- **2026-05-01**: Routine health check, all agents OK (incident-free day before cascade)

---

## Analysis status

- [x] Timeline reconstructed from journalctl
- [x] Exit codes and restart times verified
- [x] Resource pressure ruled out
- [x] Auth/Token issues ruled out
- [ ] Root cause hypothesis: **likely coordinated restart signal** (needs bash history / systemd user manager audit)
- [ ] Follow-up: check `update.log` and `brain-backup.log` for concurrent activity

