# Hermes Provider Auth Error Signatures

## Nous Portal device_code Flow

### Symptom
```
RuntimeError: Hermes is not logged into Nous Portal. Run `hermes model` to re-authenticate.
```
or
```
Agent completed but produced empty response (model error, timeout, or misconfiguration)
```
combined with auth.json showing:
```json
"credentials": {
  "nous": {
    "last_status": null  // or missing
  }
}
```

### Root Cause
Nous Portal OAuth device_code token expired. The `hermes status` command may still report "logged in" because it reads a separate status flag, but the actual access token is no longer valid. `last_status: None` indicates the credential pool has no working token.

### Fix
Run `hermes model` to re-authenticate via device code flow. This regenerates a fresh token stored in `auth.json` and updates `last_status` to "ok".

### Verification
```bash
# Check credential pool status
cat ~/.hermes/profiles/*/auth.json | grep -A2 '"nous"'
# Expected: "last_status": "ok"

# Test actual model access
timeout 10 hermes chat -- "test" 2>&1 | head -5
# Should return a response, not empty
```

---

## Telegram Bad Gateway

### Symptom
```
WARNING gateway.platforms.telegram: [Telegram] Telegram network error, scheduling reconnect: Bad Gateway
```
followed by automatic reconnect attempts and eventual resumption:
```
INFO gateway.platforms.telegram: [Telegram] Telegram polling resumed after network error
```

### Root Cause
Transient MTProto API network failure — usually rate limiting, Telegram-side outage, or IP-level connectivity issue.

### Impact
- Outbound messages may be buffered and flushed after reconnection
- Inbound messages missed during disconnection window
- No persistent state corruption

### Detection
Check gateway.log for pattern:
```
<timestamp> WARNING ... Bad Gateway
<timestamp> INFO ... polling resumed after network error
```
If these occur within minutes of each other, it's transient. If reconnect fails after 10 attempts → persistent issue.

---

## Channel Directory I/O Exhaustion

### Symptom
```
WARNING gateway.channel_directory: Channel directory: failed to write: [Errno 28] No space left on device
```
repeated every 30 minutes (default cleanup interval).

### Root Cause
Disk inode or block exhaustion on the partition containing `~/.hermes/profiles/*/home/.hermes/channel_directory`.

### Impact
- Telegram message batching state cannot be persisted
- Message flush failures → lost outbound messages
- May cascade to gateway instability

### Fix
1. Check disk space: `df -h /` and `df -i /`
2. Clear old channel directory contents if safe
3. Increase disk capacity or relocate profile storage

---

## Empty response Cron Failures

### Symptom
Hermes cron list reports:
```
Last run:  2026-05-01T06:00:32.695615+00:00  error: Agent completed but produced empty response (model error, timeout, or misconfiguration)
```

### Root Cause Matrix
| Primary Cause | Evidence | Resolution |
|---------------|----------|------------|
| Expired model provider token | auth.json last_status = null/None | `hermes model` re-auth |
| Model name deprecated/404 | errors.log: `NotFoundError: Error code: 404` | Update model name in config.yaml |
| Provider rate-limited | openai/status 429 errors | Wait or switch provider |
| Gateway deadlocked | No 'Running job' log lines despite ticker | Restart ALL agent gateways simultaneously |

### Verification Chain
1. Check agent errors.log for `empty response` within last 24h
2. Check auth.json provider `last_status` value
3. Verify model exists (if OpenRouter: https://openrouter.ai/models)
4. Confirm cron ticker actually dispatched job (gateway.log: `Running job`)

---

## Dual-PID Process Pattern

### Observation
Each Hermes agent profile typically runs with exactly one gateway process. Finding **two** PIDs for the same profile (`pgrep -f 'hermes.*--profile yoyo'` returns two PIDs) indicates either:

**Normal case**: A recent, clean restart. The older PID will have shorter elapsed time (`ps -o pid,etime`) and exit quickly.

**Problem case**: A stuck restart loop where:
- Old process fails to exit cleanly
- New process spawns before old exits
- Both accumulate, indicating gateway start/stop thrashing

### Diagnosis
```bash
# For each agent, check elapsed times
ps -eo pid,etime,comm | grep hermes

# If two PIDs exist:
# - Older PID should be in Z (zombie) or S (sleeping EXITING) state
# - If both are S (sleeping) with significant elapsed time (>5min), investigate
```

### Common Causes
- Credential rejection during startup → immediate restart loop
- Port binding conflict (unlikely — single profile uses one port)
- Database lock contention (state.db locked by another process)
