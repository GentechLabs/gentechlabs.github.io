---
date: 2026-04-27
type: hermes-full-backup
backup-dir: /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215036
profiles: yoyo, dmob, desmond, gentech
main-cron-jobs: 23
yoyo-cron-jobs: ~28 (incl duplicates)
dmob-cron-jobs: ~10
desmond-cron-jobs: ~6
total-backup-size: 584K (configs only, runtime files excluded)
---

# Hermes Full Backup — 2026-04-27

Stored at `/root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215036/`

## Whats Inside

| Item | Status | Notes |
|------|--------|-------|
| `config.yaml` (main) | ✅ | current provider ollama-cloud, model kimi-k2.6 |
| `.env` (main) | ✅ | TELEGRAM_BOT_TOKEN, API keys |
| `auth.json` (main) | ✅ | OAuth tokens |
| `profiles/yoyo/` | ✅ | config, SOUL.md, .env, auth, channel_dir, cron |
| `profiles/dmob/` | ✅ | config, SOUL.md, .env, auth, channel_dir, cron |
| `profiles/desmond/` | ✅ | config, SOUL.md, .env, auth, channel_dir, cron |
| `profiles/gentech/` | ✅ | config, SOUL.md, .env, auth, channel_dir |
| `cron-export/` | ✅ | JSON exports of all cron jobs (main + per-profile) |
| `channel-mappings.txt` | ✅ | Telegram group ↔ agent mappings |
| `env-keys.txt` | ✅ | Variable names only for security |
| `skills-list.txt` | ✅ | Full installed skill list |
| `skills-dirs.txt` | ✅ | Git repo paths for each skill |
| **`agent-config-package/`** | ✅ | Post-reinstall configs with multi-model + queue protocol |

## What Was Excluded

- `state.db` (~600MB total) — recreatable via `hermes doctor`
- `sessions/` (~1GB) — transient conversation history
- `cron/output/` (~21MB) — old job execution logs
- `sandboxes/` — temp working dirs
- `audio_cache/` — voice scratch files

## Telegram Groups Mapped

| Agent | Primary Group | Model | Role |
|-------|---------------|-------|------|
| gentech | Gentech HQ (-1003863540828) | kimi-k2.6 | Coordinator |
| yoyo | Gentech Strategies (-1002916759037) | kimi-k2.6 | Investor |
| dmob | Gentech Labs (-1003872552815) | qwen3-coder-next | Dev/Auditor |
| desmond | Gentech Ent (-1003893562036) | kimi-k2.6 | Content |

## Main Cron Jobs (23)

1. **LP Unified Monitor** — every 10m, AVAX/USDC → Strategies group
2. **x-morning-briefing** — daily 07:00 → origin
3. **x-feed-monitor** — every 2h → origin
4. **Mess Hall Check-In** — daily 14:00 → HQ
5. **Brain Backup** — every 6h → origin
6. **x402 Tracker** — biweekly 1st & 15th
7. **Vault Manager** — nightly 23:00 → HQ
8. **Mess Hall Rotation** — daily 03:00 → local
9. **Morning Briefing** — Mon-Sat 04:30 → HQ
10. **Morning Briefing + Stars** — daily 06:30 → HQ
11. **Protocol Due Diligence** — Thu 06:00 → Strategies
12. **Weekly Opportunity Scanner** — Mon/Thu 06:00 → Labs
13. **Kite AI Hackathon Check** — daily 10:00 → Labs
14. **Security→Content Pipeline** — Tue/Fri 07:00 → Ent
15. **Gentech X Content** — daily 17:00 → Ent
16. **LayerZero DVN Monitor** — every 6h
17. **The Brain Daily** — daily 16:00
18. **Vault Maintenance** — Sun 22:30 → HQ
19. **LLC Reminder** — monthly 15th 05:00
20. **End of Shift Wrap-Up** — Thu-Sat 16:30
21. **Sunday Skill Update** — Sun 10:00 → HQ
22. **Agent Watchdog** — every 15m
23. **Hermes Agent Sync** — daily 06:00 → Labs

## Reinstall Checklist

- [ ] Kill all remaining hermes processes: `tmux kill-server; pkill -f "hermes gateway run"`
- [ ] Uninstall: `hermes uninstall` or `rm -rf ~/.hermes`
- [ ] Reinstall: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- [ ] Restore configs: `cp -r` from backup dir to `~/.hermes/`
- [ ] Copy `auth.json` into each profile
- [ ] Install skills: `hermes skills tap add ProtoJay4789/hermes-agent` + re-clone custom skills
- [ ] Set models: `hermes profile use <name>; hermes config set model.provider ollama-cloud; hermes config set model.default kimi-k2.6`
- [ ] Recreate cron jobs: use `hermes cron create` with exported JSON from `cron-export/`
- [ ] Start gateways: `tmux` + `HERMES_HOME=~/.hermes/profiles/<name> hermes gateway run`
- [ ] Verify: `hermes profile list`, `hermes cron list`, `hermes gateway status`

## Post-Restore Agent Config TODO

User requested before reinstall:
1. Set all agents → **kimi-k2.6** via ollama-cloud (except dmob keeps qwen3-coder-next)
2. **Message queuing**: no interrupt on new messages per agent
3. **Workflow enforcement**: HQ/Green Room/Mess Hall routing protocol in SOUL.md
4. Limit API queries per run (rate limits)
