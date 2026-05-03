# Gentech "Chat not found" Telegram Errors (May 2026)

## Symptom

Gateway log entries:
```
2026-05-01 09:44:42,028 ERROR gateway.platforms.telegram: [Telegram] Failed to send Telegram message: Chat not found
Traceback (most recent call last):
  File "/usr/local/lib/hermes-agent/gateway/platforms/telegram.py", line 1028, in send
  File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 3118, in send_message
    return await super().send_message(
telegram.error.BadRequest: Chat not found
```

**Occurrences in Gentech gateway:**
- 2026-05-01 09:44:42 — first occurrence (preceded by channel directory disk I/O warnings)
- 2026-05-02 09:04:36 — recurrence (24h later)

**Not observed in:** Yoyo, DMOB, Desmond agents (they use different Telegram groups/chats).

## Diagnostic Checklist

1. **Verify bot still has access to target chat**
   - Target chat ID from config: `-1003863540828` (Gentech HQ group)
   - Check recent inbound logs: if inbound messages from that chat still arrive, bot *receives* but cannot *send* → send permission issue
   - In our case: inbound messages from `jordan` to `-1003863540828` processed at 11:58 → bot still in group

2. **Check bot role/permissions in group**
   - Bot must have **"Can send messages"** permission
   - If bot was promoted to admin and then demoted, it may have lost send rights
   - If group settings changed to restrict bots, message sends fail

3. **Confirm chat ID configuration**
   ```yaml
   # In config.yaml or platform config
   allowed_chat_ids:
     - -1003863540828  # Must match exactly
   ```
   - Rarely, groups migrate to new IDs; if group was recreated, ID changed

4. **Check for bot expulsion**
   - If bot was explicitly removed from group, all sends fail with `Chat not found`
   - No automatic re-join; requires manual re-invite

## Resolution Steps

### Step 1: Re-invite bot to group
1. Open Telegram, go to Gentech HQ group (`-1003863540828`)
2. Tap group info → Add member → search for `@GentechBot` (or actual bot username)
3. Add bot back to group
4. Grant "Send Messages" permission if prompted

### Step 2: Verify config matches
```bash
grep -r "allowed_chat_ids" /root/.hermes/profiles/gentech/
```
Ensure listed chat IDs include `-1003863540828`.

### Step 3: Restart gateway (to flush any cached bad state)
```bash
hermes -p gentech gateway restart
```

### Step 4: Send test message
Trigger a Gentech cron job or send `/start` to bot in group; confirm response arrives.

## Follow-up: Paused Cron Jobs

While investigating, found 2 paused Gentech cron jobs:
- `social-briefing` — state=paused, paused_by_system=false, paused_reason=None
- `social-monitor` — state=paused, paused_by_system=false, paused_reason=None

**Action:** Review these jobs' recent failure history and either fix root cause or unpause:
```bash
hermes cron list --profile gentech
hermes cron resume <ID>
```

## Prevention

- Add **chat access validator** to Gentech startup routine: attempt a `send_message(chat_id, "✓")` on boot; if fails, alert in Mess Hall
- Monitor `Chat not found` error rate; >0 in 24h → auto-create ticket
- Document bot username and group ID in vault: `03-Projects/Gentech/Telegram-Bot-Management.md`

## References

- Hermes Telegram platform: `/usr/local/lib/hermes-agent/gateway/platforms/telegram.py`
- Error class: `telegram.error.BadRequest` — raised when API returns 400 with `chat_not_found`

</content>