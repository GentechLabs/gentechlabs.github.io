---
created: 2026-04-19
tags: [infrastructure, vps, devops]
---

# VPS & Infrastructure Reference

## VPS Specs
- **Provider**: Hostinger KVM 4
- **Storage**: 200GB
- **RAM**: 16GB
- **IP**: [REDACTED — see secure vault]

## Services
- **Workspace**: `:3001` (password: [REDACTED — see secure vault])
- **Gateway**: `:8642`
- **Vault**: `~/Documents/Obsidian Vault`
  - Sync: `ob sync --continuous`

## Agent Workspaces
- `/opt/hermes-agents/gentech/`
- `/opt/hermes-agents/yoyo/`
- `/opt/hermes-agents/dmob/`
- `/opt/hermes-agents/desmond/`

## Cron Schedule
| Time | Task | Provider |
|------|------|----------|
| 09:30 | Nous models | Nous |
| 23:30 | Ollama models | Ollama |

## Workspace Password
- Password: [REDACTED — see secure vault]

## Common Paths
| Path | Purpose |
|------|---------|
| `~/hermes-agent/` | Shared agent code |
| `/opt/hermes-agents/{name}/` | Agent-specific configs |
| `~/Documents/Obsidian Vault/` | Knowledge vault |
| `~/repos/browser-harness/` | Browser automation |
| `~/.hermes/skills/` | Skills |
| `~/.hermes/cron/` | Cron jobs |

## Service Management
- Browser harness: `chrome-harness.service`
- Watchdog: 5min auto-restart
- Paperclip: replaced (historical issue)

## Telegram Infrastructure
- **Bot ID**: [REDACTED]
- **Users**: Jordan, Desmond, Dadrian [IDs REDACTED]
- **Groups**:
  - HQ (brainstorm/orchestration): [REDACTED]
  - Strategies (investing/DeFi): [REDACTED]
  - Labs (dev/learning): [REDACTED]
  - Entertainment (content): [REDACTED]
- Gateway runs as systemd user service

## Paperclip Dashboard
- URL: [REDACTED — see secure vault]
- Login: [REDACTED — see secure vault]
- API Base: [REDACTED]
- Agent ID: [REDACTED]
- Company ID: [REDACTED]
- Auth: Session cookie + Origin header required for mutations
- Login: `POST /api/auth/sign-in/email`
- Unpause agent: `UPDATE agents SET status='idle' WHERE id='...'`

### Paperclip Troubleshooting
- Stuck session: Kill hermes chat process AND child npm run start, then MUST restart gateway (`kill $(pgrep -f "hermes gateway run")` + start fresh) — gateway holds "Still working..." status in memory
- Skills: Auto-discovers `~/.hermes/skills/` (96 Hermes skills shown as "User-installed"). syncHermesSkills is no-op. 4 bundled Paperclip skills required.
- Skill: paperclip-hermes-sync

## Projects
### Avalanche Agent Economy (AAE)
- Avalanche social AI agent platform, solo dev
- Retro9000 grant ($75K) at `/tmp/retro9000-grant-outline.md`
- PentAGI: [REDACTED — see secure vault]
- Nous API 404 from Go client known issue
- VPS 48GB at 92%, warn at 95%, upgrade Hetzner CX41 when ready

### SUPERSTACK (solana.new)
- Installed 54 Claude Code skills to `~/.claude/skills/`
- Config at `~/.superstack/config.json`
- Needs Colosseum Copilot PAT (arena.colosseum.org/copilot)
- AI-Trader project ref: `~/repos/AI-Trader/`

### Arc Hackathon (Dmob-specific)
- Nanopayments: developers.circle.com/gateway/nanopayments
- x402 protocol, batched settlement, ERC-8004 agent reg, ERC-8183 jobs
- Key repo: circlefin/arc-escrow (AI-validated escrow on Arc)
- Circle GitHub: github.com/circlefin (81 repos)
- Registered as Gentech Labs
