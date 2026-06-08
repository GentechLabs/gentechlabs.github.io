# Agent Architecture — Standalone Setup

**Updated:** April 14, 2026
**Status:** 🟢 Operational

## Architecture

Migrated from shared profiles to **standalone agents** — each runs independently.

### Directory Structure
```
/opt/hermes-agents/{name}/
├── HERMES_HOME/
├── auth.json
├── config/
└── systemd service
```

### Shared Codebase
- `/root/.hermes/hermes-agent/` — shared code, symlinked to each agent

## Services
| Agent | Service | Group | Role |
|-------|---------|-------|------|
| Gentech (default) | hermes-agent-default | Agency | Orchestration, planning, delegation |
| YoYo | hermes-agent-yoyo | Strategies | Research, DeFi, market analysis |
| Dmob | hermes-agent-dmob | Labs | Development, smart contracts, bounties |
| Desmond | hermes-agent-desmond | Entertainment | Content, social media, branding |

## Watchdog
- Cron job runs every 5 minutes
- Checks all 5 services (4 agents + workspace)
- Auto-restarts dead services
- Alerts Jordan via DM on persistent failures

## Auth
- Each agent has its own `auth.json` (device code flow)
- No more auth race conditions between profiles
- Tokens refreshed independently

## Cron Jobs by Agent
| Job | Agent | Schedule | Destination |
|-----|-------|----------|-------------|
| Crypto Watchlist | YoYo | Every 2h (11am-1am) | Strategies |
| Opportunity Scanner | Dmob | Mon & Thu 10am | Labs |
| Second Brain | Gentech | Daily 9pm | Agency |
| Daily Briefing | Gentech | Daily 10:30am | Agency |
| LLC Reminder | Gentech | 1st of month | Agency |
| Watchdog | Gentech | Every 5 min | DM Jordan |

## Known Issues
- **Syncthing folder mismatch** — "gentec" vs "gentech" spelling causing two separate sync folders
- **Bot kicked from some groups** — Crypto watchlist delivery failures on some runs
- **Daily Debrief paused** — Pending cross-agent communication capability

## Dashboard Development (Apr 14)
- **Departments tab** added to Hermes Workspace UI
- Shows Agent Reach channel groups with icons (Building2 icon)
- Part of broader Gentech-branded dashboard initiative
- Dark charcoal theme, red+cyan neon accents planned

## Tags
#infrastructure #agent:gentech #agent:dmob #status:active
