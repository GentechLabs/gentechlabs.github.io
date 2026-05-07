# 2026-05-05: Gentech Telegram "Chat not found" Delivery Failure

**Watchdog**: Gentech (May 5, 2026 03:43 UTC)

## Symptom

Gentech agent gateway logs contain repeated errors:
```
ERROR gateway.platforms.telegram: [Telegram] Failed to send Telegram message: Chat not found
```

This occurs when the agent attempts to send messages to its configured `deliver` chat ID via Telegram.

## Diagnosis

**Error type**: Telegram HTTP 400 BadRequest with `chat not found` reason. This is **not** a rate limit, network, or auth problem — it's specifically a destination access failure.

**Confirmation** (manual check):
```bash
# Replace <BOT_TOKEN> and <CHAT_ID> from agent config/jobs
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getChat?chat_id=<CHAT_ID>"
# Expected failure output:
# {"ok":false,"error_code":400,"description":"Chat not found"}
```

## Root Causes (Likely)

1. **Bot not in target chat** — The Gentech bot was never added to the destination group/channel, or the invite link expired and was never used.
2. **Bot removed/kicked** — An admin removed the bot from the chat.
3. **Chat ID changed** — The chat migrated (e.g., group to supergroup) and the ID the bot has is stale.
4. **Privacy restrictions** — Chat has "Restrict saving content" enabled; bots cannot post.
5. **Wrong ID type** — The configured ID is a user ID (private chat) rather than a group/channel ID; bots can only message groups they're members of.

## Cross-Agent Comparison

Other agents (YoYo, DMOB, Desmond) did **not** show this error in the same audit window, indicating:
- Their Telegram bot tokens are different (each agent uses its own bot)
- Their configured destination chat IDs are accessible to their respective bots
- The problem is isolated to Gentech's bot+chat pairing, not a fleet-wide Telegram outage

## Recovery Steps

1. **Obtain the correct chat ID**:
   - From another agent that successfully posts to the intended chat, copy its `deliver` chat ID
   - Or ask a chat admin to forward a message from the chat and inspect `chat.id` via Telegram API
   - Or use the chat's invite link to get the ID (some bots can resolve)

2. **Verify bot membership**:
   ```bash
   curl -s "https://api.telegram.org/bot<GentechBotToken>/getChatMember?chat_id=<target_chat_id>&user_id=<GentechBotId>"
   # Should return status: "member" or "administrator"
   ```

3. **If bot not in chat**:
   - Generate a fresh invite link: Telegram Desktop → Chat → Invite → Create a never-expiring link
   - Add the bot as a member using that link
   - Grant appropriate permissions (Post messages if needed)

4. **Update Gentech's cron job deliver target**:
   Edit `/root/.hermes/cron/jobs.json` (or the specific agent job in Gentech's cron config) to set:
   ```json
   "deliver": "<correct_chat_id>"
   ```
   Then restart Gentech gateway to reload cron config.

5. **Test**:
   ```bash
   hermes send --profile gentech --chat <correct_chat_id> "Watchdog test: Telegram access restored"
   ```
   Check gateway.log for successful send (no error lines).

6. **Validate**: Wait for next scheduled cron job; verify output appears in the chat and no `Chat not found` errors appear in `errors.log`.

## Prevention

- Document all Telegram chat IDs in vault with: which bot(s) have access, invite link, date added
- Before registering a new cron job with Telegram delivery, do a `getChat` API test to confirm bot access
- Set up a quarterly bot membership audit (re-run `getChat` for all deliver targets)
- If using private groups, keep a permanent invite link in the vault with access instructions

## Related

- `agent-health-audit` pattern: **Telegram "Chat not found" Access Failure**
- Telegram platform docs: https://core.telegram.org/bots/api#getchat
