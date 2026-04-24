---
created: 2026-04-19
updated: 2026-04-20
tags: [agent-config, team, operational, governance]
---

# Agent Team Configuration

## Org Chart & Governance
Full org chart with reporting structure, accountability, and escalation paths:
→ `01-GenTech HQ/Org Chart.md`

## Team Roster

## Team Roster

| Agent | Telegram Bot | Speciality | Telegram Group |
|-------|-------------|------------|----------------|
| Gentech | Original | Orchestration, planning, QA | HQ (-1003863540828) |
| YoYo | YOYO | Research, analysis, due diligence | Strats (-1002916759037) |
| Dmob | DMOB | Solidity, smart contracts, debugging | Labs (-1003872552815) |
| Desmond | Desmond | Content, writing, social, narratives | Ent (-1003893562036) |

## Agent Groups (Telegram)
- **HQ**: -1003863540828 (Gentech, Jordan comms hub)
- **Strats**: -1002916759037 (YoYo — research, financial)
- **Labs**: -1003872552815 (Dmob — dev, opportunities)
- **Ent**: -1003893562036 (Desmond — content, social)
- All isolated at `/opt/hermes-agents/{name}`
- Shared code: `~/hermes-agent`
- Watchdog: 5min restart

## Agent Reach
- **Connected**: 8/16 channels
- **Cookie auth**: Twitter, XHS, Weibo, Reddit
- **Missing**: 小宇宙, 雪球, Douyin, LinkedIn

## Browser Automation
- Harness: `~/repos/browser-harness`
- Service: `chrome-harness.service` on `:9222`
- Adapter: `hermes_browser_adapter.py`

## Voice Assignments (ElevenLabs)
- Gentech: Ivan on Tech
- YoYo: Optimus
- Dmob: (default)
- Desmond: Steve Harvey

## Cron Routing
- 23:30 → Ollama (local models)
- 09:30 → Nous (cloud models)
- Cron → specialist groups per content type
- DM rule: emergencies only

## Provider Strategy (Confirmed Apr 2026)
- **Primary**: Nous Research sub → xiaomi/mimo-v2-pro (daily driver for all specialist agents)
- **Fallback 1**: OpenCode-go → qwen3.6-plus (auto-switch when Nous token expires)
- **Fallback 2**: Ollama local (nuclear option, overnight savings only)
- Gentech main gateway runs on OpenCode/go by default
- Auto-token-check cron every 6h + Telegram alert when reauth needed

## Desmond Content Cron
- ID: `b3cf562ffe66`
- Schedule: Daily 9PM UTC
- Reads HQ convos → drafts 2-3 X posts → saves to vault
- Location: `vault/01-GenTech HQ/X-Content/`
- Jordan reviews manually (no X API yet)
- Strategy + hackathon templates in vault

## Team Lead Protocol
1. Gentech monitors all handoffs — see [Agent Handoff Enforcement Protocol](~/.hermes/skills/devops/agent-handoff-enforcement/SKILL.md)
2. Confirm receiving agent picks up (ACK within 5 min)
3. Status check after completion
4. Agents must signal "clean/nothing-to-add"
5. Gentech nudges silent agents
6. Jordan gets one status line, not a chase
7. Escalation: 15 min no ACK → Jordan notified in HQ
8. Board maintenance: scan every 30 min for stale briefs

## Communication Rules
- DM: emergencies only
- Normal → HQ (-1003863540828)
- Cron → specialist groups
- Post-collab: debrief Mess Hall
- HQ = single comms hub
- Specialist groups = workshops only

## Kite Design
- 6-layer agent: Brain, Personality, Strategy, Enforcement, Execution, Memory
- Presets ≠ Locks — every layer editable after cloning
- Leaderboard = discoverability, users fork/remix like GitHub
- Enforcement respects CURRENT user's education tier
- Medium blog series planned:
  1. "6-Layer Agent Stack"
  2. "Constitutional AI for DeFi"
  3. "729 Agents — What Prints"
  4. "Agent Levels Up Like RPG"
  5. "Personality Problem in AI Trading"
  6. "Agent Economy"

## Gentech Entertainment
- YouTube podcast framework: `06-Content/Gentech Entertainment - Content Framework.md`
- Adult-oriented talk show: finances, geopolitics, trending topics
- Jordan personal brand + Gentech
- Uncensored, no-holds-barred
- LLC planned for podcast costs + liability
- Agents as co-hosts
