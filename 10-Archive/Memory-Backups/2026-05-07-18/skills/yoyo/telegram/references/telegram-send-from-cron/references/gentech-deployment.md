# Gentech Telegram Deployment — Session Notes

**When:** 2026-05-03 — Daily Mess Hall agent check-in  
**Agent:** YoYo (Strategies)  
**Profile path:** `/root/.hermes/profiles/yoyo/`

## Token Location (Confirmed Working)

Active bot tokens are stored per-agent in their profile `.env`:

```
/root/.hermes/profiles/yoyo/.env        → TELEGRAM_BOT_TOKEN=<Yoyo's bot>
/root/.hermes/profiles/dmob/.env        → TELEGRAM_BOT_TOKEN=<DMOB's bot>
/root/.hermes/profiles/desmond/.env     → TELEGRAM_BOT_TOKEN=<Desmond's bot>
/root/.hermes/profiles/gentech/.env     → TELEGRAM_BOT_TOKEN=<HQ bot>
```

**NOT** in `/root/.hermes/.env` (that's the system hermes instance, not the active profile).

Verify with: `cat /root/.hermes/profiles/yoyo/.env | grep TELEGRAM_BOT_TOKEN`

## Cron Job Structure

Hermes cron jobs use this schema:

```json
{
  "jobs": [
    {
      "id": "<uuid>",
      "name": "Job Name",
      "prompt": "...",
      "deliver": "telegram:-100XXXXXX",
      ...
    }
  ]
}
```

The `jobs.json` lives at `/root/repos/hermes-brain/profiles/yoyo/cron/jobs.json` for this agent.

**Note:** The "Mess Hall — Agent Check-in" job ID is `3531ebe1d549` and delivers to `telegram:-1003863540828` (Gentech HQ), but when posting from the **Strategies** agent we should use the Strategies group `-1002916759037` as the destination.

## Chat ID Mapping (Gentech)

From `/root/.hermes/profiles/yoyo/channel_directory.json`:

| Name               | Chat ID           | Use for…                     |
|--------------------|-------------------|------------------------------|
| Gentech Strategies | `-1002916759037`  | YoYo, DMOB, Desmond reporting|
| Gentech HQ         | `-1003863540828`  | Central coordination         |
| Gentech Labs       | `-1003872552815`  | Creative builds & tech debt  |

## Verified curl Command (Works in Cron)

```bash
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=-1002916759037" \
  --data-urlencode "text=🤖 Daily Agent Check-In\n\nTeam — respond with..." \
  --data-urlencode "parse_mode=Markdown"
```

- Always use `--data-urlencode` for message content (handles emojis, newlines, dollars safely)
- No pipe-to-python due to security scan — pure curl is fine
- Response includes `message_id`, `chat.id`, `from.id` for audit trail

## Pitfalls Encountered

1. **Misreading jobs.json type** — First parse assumed `jobs` was dict keyed by ID but it's a list. Check with `type(data['jobs'])` before iterating.
2. **Wrong .env path** — `~/.hermes/.env` is the system-level hermes agent, not the per-profile active agent. For YoYo, use `/root/.hermes/profiles/yoyo/.env`.
3. **Vault backup divergence** — Backups in `/root/vaults/gentech/10-Archive/Hermes-Backups/` may contain stale tokens. Always read from `.env` files in `/root/.hermes/profiles/` for current tokens.
4. **channel_directory.json lookup** — Searching by human name (e.g. "Jordan") doesn't work; entries are by chat title only. Use fixed Chat ID from the directory.

## Quick-Start Template (YoYo → Strategies Group)

```bash
#!/bin/bash
TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' /root/.hermes/profiles/yoyo/.env | cut -d= -f2)
MSG="🤖 Strategies Stand-up\n\nPlease share:\n• Today's win\n• Current blocker\n• Tomorrow's plan"
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=-1002916759037" \
  --data-urlencode "text=${MSG}" \
  --data-urlencode "parse_mode=Markdown" > /dev/null
```

---

**Next session trigger:** Any task requiring YoYo to "post to Telegram from cron/background" should route through the `telegram-send-from-cron` skill and consult this reference for the Gentech-specific paths.
