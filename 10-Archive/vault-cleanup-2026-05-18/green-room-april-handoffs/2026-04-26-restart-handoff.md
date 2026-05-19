---
date: 2026-04-26
type: restart-handoff
priority: critical
---

# 🔄 Agent Restart Handoff — 2026-04-26

## Why We Restarted
Gateway restart required to activate new model routing:
- **Primary**: OpenCode Go (kimi-k2.6) for gentech, yoyo, desmond
- **Backup**: Ollama Cloud (kimi-k2.6:cloud) fallback
- **DMOB**: Ollama Cloud (qwen2.5-coder:32b) primary, OpenCode fallback

## What Changed (Pre-Restart)

### Model Routing Fix
| Agent | Before (Broken) | After (Fixed) |
|-------|----------------|---------------|
| gentech | ollama-cloud | opencode-go → ollama fallback |
| yoyo | ollama-cloud | opencode-go → ollama fallback |
| desmond | ollama-cloud | opencode-go → ollama fallback |
| dmob | ollama-cloud | ollama-cloud qwen → opencode fallback |

**Root cause**: Apr 26 16:51 gateway restart reverted all configs to ollama-cloud. Vault had correct settings but live configs drifted.

### Other Pending Work
1. **HawkFi analysis** — Social channels deleted, site still live. Pending DMOB contract audit.
2. **Approval queue** — Migrated from `00-Inbox/` and `10-Inbox/` → `01-Agency/Approvals/`.
3. **OpenCode Go subscription** — User reports intermittent failures. Fix applied above may resolve.
4. **Kite AI hackathon** — Due May 11. Option B (Novel Track) locked. DMOB owns submission.

## Boot-Up Recovery Checklist
Each agent MUST run on startup:
1. `session_search` — last 3 sessions for context
2. Read `11-Mess Hall/status-2026-04-26.md` — latest status
3. Read this handoff file
4. Check `01-Agency/Approvals/` — any pending approvals for Jordan
5. Run `hermes --version` — verify software version
6. Report to HQ: "I'm back. Last: [summary]. Pending: [list]. Focus: [ask Jordan]"

## Files to Check Post-Restart
- `~/.hermes/profiles/{agent}/config.yaml` — verify model provider matches this handoff
- `00-Working-Memory.md` — any global state
- `08-Logs/2026-04-26.md` — today's full activity log
- `03-Strategies/cron-jobs.md` — cron status

## Do Not Lose
- LP monitoring cron is ACTIVE (4× daily)
- GitHub token needs rotation (critical security — Jordan action required)
- Kite AI deadline: May 11 (17 days)

---
*Written by YoYo pre-restart. Synced to GitHub commit 7ec529a.*
