# Agent Profiles Backup

Synced from `~/.hermes/profiles/` — **NO secrets included**.

| Agent | Model | Purpose |
|-------|-------|---------|
| `yoyo` | kimi-k2.6 | Strategies — DeFi, LP, research, tokenomics |
| `dmob` | qwen3-coder-next | Labs — smart contracts, security, audits |
| `desmond` | kimi-k2.6 | Content — creative, media, outreach |
| `gentech` | kimi-k2.6 | HQ — orchestration, coordination |

## Files per Profile
- `SOUL.md` — Identity, domain rules, boot protocol
- `config.yaml` — Model, toolsets, gateway settings
- `memory.md` — Persistent agent memory
- `memories/` — Additional memory fragments
- `cron/jobs.json` — Scheduled tasks
- `skills-manifest.txt` — List of loaded skills

## Sync Procedure
Run from server:
```bash
cd /root/vaults/gentech/00-System/agent-profiles
for p in yoyo dmob desmond gentech; do
  cp ~/.hermes/profiles/$p/SOUL.md $p/SOUL.md
  cp ~/.hermes/profiles/$p/config.yaml $p/config.yaml
  cp ~/.hermes/profiles/$p/memory.md $p/memory.md 2>/dev/null
  [ -f ~/.hermes/profiles/$p/cron/jobs.json ] && cp ~/.hermes/profiles/$p/cron/jobs.json $p/cron/jobs.json
  ls ~/.hermes/profiles/$p/skills/ > $p/skills-manifest.txt
done
cd /root/vaults/gentech && git add . && git commit -m "profile sync $(date +%Y-%m-%d)" && git push
```
