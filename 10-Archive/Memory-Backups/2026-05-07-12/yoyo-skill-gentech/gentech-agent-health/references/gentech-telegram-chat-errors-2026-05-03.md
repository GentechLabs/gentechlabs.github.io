# Gentech Telegram "Chat not found" Incident — May 3, 2026

**Agent:** Gentech  
**Platform:** Telegram  
**Error:** `telegram.error.BadRequest: Chat not found`  
**Duration:** ~10 minutes (12:10 — 12:20)  
**Resolution:** Self-cleared after gateway restart at 12:24:30

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 12:10:03 | First "Chat not found" error logged (failed send to `-1003863540828`) |
| 12:20:06 | Second "Chat not found" error logged |
| 12:24:05 | Gateway disconnected from Telegram (manual/cron-triggered shutdown) |
| 12:24:30 | Gateway restarted, reconnected to Telegram |
| 12:37:33 | First successful send post-restart (message from jordan) |
| 12:47:39 | Second successful send post-restart (link share) — error resolved |

## Diagnosis

### Initial Hypothesis (Incorrect)
- **Bot expelled from group:** ruled out — inbound messages from `jordan` still arrived at 12:37
- **Chat ID changed:** ruled out — same chat ID `-1003863540828` used throughout
- **API key revoked:** ruled out — other agents (yoyo, dmob, desmond) sending to same group without errors

### Actual Root Cause
**Transient Telegram polling session desynchronization** during gateway restart sequence:

1. Gateway shutdown at 12:24:05 terminated the long-polling Telegram connection
2. Bot's `getUpdates` session was abruptly closed on Telegram's side
3. Upon reconnect at 12:24:31, Telegram accepted the connection but had not yet re-associated the bot's chat membership cache for all groups
4. First outbound send attempts within ~5 minutes of reconnect hit "Chat not found" because Telegram still believed the bot was not a member of that chat
5. Inbound message from `jordan` at 12:37 triggered a proper chat context refresh, after which outbound send succeeded

### Key Evidence

1. **No inbound errors:** Gateway continued receiving inbound messages from the same chat (`-1003863540828`) throughout — proving chat was accessible
2. **Errors stopped without intervention:** Two errors logged, then ~17 minutes of silence before successful send at 12:37
3. **No permission changes:** No config changes to `allowed_chat_ids` or bot rights during window
4. **Other agents unaffected:** Yoyo, DMOB, Desmond sending to same chat simultaneously with no errors — indicates issue isolated to Gentech's connection state

## Resolution

**Passive recovery:** No manual intervention required. Inbound message activity refreshed the bot's chat session cache, allowing outbound sends to succeed.

**Active prevention (for future restarts):**
- Add a post-startup warm-up routine that sends a low-priority `/status` or health-check message to primary chat
- Implement chat membership verification on boot: call `getChat` API to force refresh chat membership cache before processing outbound messages
- Stagger gateway restarts across agents to avoid simultaneous reconnection storms

## Lessons for Health Checks

1. **"Chat not found" ≠ always permanent** — check for recent gateway restarts within the last 5–10 minutes before concluding bot expulsion
2. **Correlate with inbound activity** — if inbound messages from same chat are arriving, the error is likely transient
3. **Look at other agents** — if only one agent affected, it's a connection-state issue; if fleet-wide, check bot token revocation
4. **Don't immediately re-invite bot** — wait 5–10 minutes for Telegram session to stabilize; unnecessary re-invites can trigger anti-spam

## Verification Checklist

When "Chat not found" appears in logs:

- [ ] Check gateway.log for recent restart timestamp (`Starting Hermes Gateway`)
- [ ] If restart < 10 minutes ago: mark as transient, watch for recovery
- [ ] Verify inbound messages from target chat are still arriving
- [ ] Check if other agents report same error (fleet-wide vs isolated)
- [ ] Look for successful `Sending response` entries after the error timestamps
- [ ] If no recovery after 15 minutes and bot still in group: manually re-invite or verify bot permissions

## References

- Incident log: `10-Archive/Memory-Backups/2026-05-03-11/gentech-agent-health-check-2026-05-03.md`
- Related skill: `gentech-agent-health` → Telegram troubleshooting section