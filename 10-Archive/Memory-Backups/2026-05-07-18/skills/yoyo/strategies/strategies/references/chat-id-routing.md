# Chat ID Routing Reference

**Last verified:** 2026-05-05

## Known Chat IDs

| Chat ID | Group | Purpose |
|---------|-------|---------|
| `-1003863540828` | Gentech HQ | Coordination, briefings, portfolio, job hunting |
| `-1002916759037` | Gentech Strategies | Investment work, DeFi monitoring, YoYo's home |

## How to Verify Unknown IDs

```bash
grep -r "TELEGRAM_HOME_CHANNEL" /root/.hermes/profiles/*/.env
```

Each profile's `.env` has `TELEGRAM_HOME_CHANNEL=<chat_id>` — that tells you which group is that agent's home.

## Routing Rules

- **HQ** (`-1003863540828`): Omni-Summary, Portfolio Site, College.xyz, general coordination
- **Strategies** (`-1002916759037`): Defi Milestone, LP monitoring, investment alerts
- **Labs**: Development work (DMOB's domain)
- **Entertainment**: Content work (Desmond's domain)

When creating cron jobs, always verify the `deliver` target matches the job's department.
