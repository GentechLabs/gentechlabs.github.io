# Gateway Crash Analysis — Interpreting `gateway.log` Exit Patterns

## Exit Code Taxonomy

| Exit Pattern | Meaning | Typical Root Cause |
|---|---|---|
| `Exiting with code 0` | Clean shutdown | Manual `hermes gateway stop` or graceful restart |
| `Exiting with code 1 (signal-initiated shutdown)` | Crash/unhandled exception | Missing API key, provider auth failure, uncaught Python exception |
| `Gateway stopped` (no exit line) | Force-killed by operator | `kill -9` or `systemctl stop` |
| Repeated boots within 60s | Restart loop | Persistent config error (missing credential, invalid model) |

## Traceback Reconstruction

When you see "Exiting with code 1", you MUST read 30–60 seconds of log *before* that line to find the actual exception.

**Command:**
```bash
# Show 50 lines before each crash exit
tac /root/.hermes/profiles/gentech/logs/gateway.log | grep -m1 -B50 "Exiting with code 1" | tail -60
```

**Look for:**
- `Traceback (most recent call last):` — Python exception chain start
- `RuntimeError:` — followed by credential gap message (see credential-gap-patterns.md)
- `ImportError` / `ModuleNotFoundError` — missing Python package
- `PermissionError` — file/network access blocked

## Common Crash Vectors

### Vector 1 — Provider Config Without Key
**Log signature:**
```
Traceback (most recent call last):
RuntimeError: Provider 'opencode-go' is set in config.yaml but no API key was found.
```

**Fix:** Add key to `.env` OR change provider to one with a valid key.

### Vector 2 — Telegram Network Instability (usually secondary)
**Log signature:**
```
WARNING gateway.platforms.telegram: [Telegram] Telegram network error, scheduling reconnect: Bad Gateway
```

**Note:** This rarely causes gateway exit by itself; it's a reconnection warning. If the gateway crashes *after* this pattern, look for the real cause 15–30 lines later.

### Vector 3 — Auxiliary Client Connection Storm
**Log signature (agent.log, not gateway.log):**
```
INFO agent.auxiliary_client: Auxiliary session_search: connection error on auto — falling back to nous
```

**Note:** These are INFO-level, not crashes. However, 5,000+ instances in 2 hours indicate the auxiliary client cannot reach its configured provider (wrong `AuxiliaryProvider` setting or network egress block).

## Recovery Verification Checklist

After applying a fix:

1. ✅ Gateway process is in `Ssl` state (running, supervised)
2. ✅ No "Exiting with code 1" entries in last 10 minutes of `gateway.log`
3. ✅ Boot count stable (no new "Starting Hermes Gateway" entries)
4. ✅ Error rate in `agent.log` drops below 5 errors per 100 lines
5. ✅ Telegram platform connects (look for `[Telegram] Telegram polling started`)

## Quick Diagnostic Script

```bash
#!/bin/bash
AGENT=$1
echo "=== $AGENT Crash Analysis ==="
echo "Gateway boots: $(grep -c 'Starting Hermes Gateway' /root/.hermes/profiles/$AGENT/logs/gateway.log 2>/dev/null || echo 0)"
echo "Exit code 1 count: $(grep -c 'Exiting with code 1' /root/.hermes/profiles/$AGENT/logs/gateway.log 2>/dev/null || echo 0)"
echo "Last crash traceback:"
tac /root/.hermes/profiles/$AGENT/logs/gateway.log | grep -m1 -B40 "Exiting with code 1" | tail -45
```

Save as `scripts/gateway-crash-analysis.sh` within the skill and invoke with `./scripts/gateway-crash-analysis.sh gentech`.
