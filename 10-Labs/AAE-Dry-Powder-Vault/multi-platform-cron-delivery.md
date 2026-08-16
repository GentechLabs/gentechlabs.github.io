# Agentic Treasury — Multi-Platform Cron Delivery (feature)

**Status:** Approved by Jordan — Aug 16, 2026
**Owner:** The Steward

## The feature
When a user provisions an Agentic Treasury, they pick their **delivery platform**
(Telegram / Discord / WhatsApp / Signal). The kit's cron reports (rail finder,
buy list, position watchdog, etc.) then route to that platform automatically.

This is a **onboarding differentiator**: "deploy your treasury, get your reports
wherever you live." Zero extra wiring for the user.

## Platform status (Hermes gateway)
| Platform | Status | What's needed |
|----------|--------|---------------|
| Telegram | ✅ LIVE | — |
| Discord | config block present | bot token |
| Slack | config block present | token |
| WhatsApp | kapso Cloud-API block present | activate / verify |
| Signal | not configured | setup |

Hermes gateway supports Telegram, Discord, Slack, WhatsApp, Signal, SMS, Email,
Mattermost, Matrix, Teams, LINE, and more. Cron `deliver:` is platform-agnostic.

## Implementation sketch
- `provision.sh` gains a `--deliver <platform>` flag.
- Cron jobs created with `deliver: <platform>:<chat_id>`.
- Mobile-safe + rich-text report layout applies on every platform (see
  `telegram-publishing` skill → `references/mobile-safe-cron-layout.md`).

## Next step
Wire Discord first (Jordan's likely second platform) — needs a bot token from
discord.dev pasted into `hermes gateway setup`.
