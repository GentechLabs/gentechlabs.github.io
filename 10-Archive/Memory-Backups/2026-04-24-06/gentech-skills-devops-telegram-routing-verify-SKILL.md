---
name: telegram-routing-verify
description: Verify all Telegram groups in channel_directory.json are reachable and media-capable after restructure or agent restart.
category: devops
---

# Telegram Routing Verification

Verify that all agent Telegram groups are configured and receiving messages after restructure, downtime, or reinstallation.

## Trigger Conditions
- Agent comes back online after downtime
- Channel directory was modified or recreated
- Jordan reports messages not being received in a group
- Post-restructure recovery

## Steps

### 1. Read channel directory
```bash
cat /root/.hermes/channel_directory.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
groups = [c for c in data['platforms']['telegram'] if c.get('thread_id') is None]
for g in groups:
    print(f\"  {g['name']:30s} → {g['id']}\")
print(f'\nTotal groups: {len(groups)}')
"
```

### 2. Expected groups
| Group | Chat ID | Agent |
|-------|---------|-------|
| Gentech HQ | `-1003863540828` | Gentech (coordinator) |
| Gentech Strategies | `-1002916759037` | YoYo |
| Gentech Labs | `-1003872552815` | DMOB |
| Gentech Entertainment | **MISSING** | Desmond |

> ⚠️ **Known issue (Apr 2026):** Entertainment group was dropped during restructure. Jordan needs to provide chat ID to restore.

### 3. Send test messages to each group
Use `send_message` with target `telegram:<chat_id>` for each group found in step 1. Include:
- Agent name and role
- "Can you see this? ✅ or ❌"
- Timestamp

### 4. Check media capabilities
- **Text:** Always works if message delivery works
- **Images:** Use `image_generate` or send a file with `MEDIA:/path/to/file`
- **Voice:** Use `text_to_speech` — delivers as voice bubble
- **FAL image generation:** Currently broken via Nous proxy (model not enabled). Options:
  - Set `FAL_KEY` in `/root/.hermes/.env`
  - Enable model on Nous portal
  - Use `browser_vision` screenshots as fallback

### 5. Report results
Send summary to HQ (`telegram:-1003863540828`) with:
- Which groups received test messages (✅/❌)
- Media capability status
- Any missing groups to restore

## Pitfalls
- `send_message(action='list')` returns targets by NAME, not chat_id — use names like `telegram:Gentech Strategies`
- For chat_id targets, use format `telegram:-100XXXXXXXXXX`
- Topic-specific targets use `telegram:-100XXXXXXXXXX:thread_id`
- Missing groups in channel_directory means that agent CAN'T receive routed messages
- FAL image gen error: `"Nous Subscription gateway rejected model 'fal-ai/flux-2/klein/9b'"` — this is a provider config issue, not a routing issue
